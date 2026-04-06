#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Content Kit Generator
Genere un kit de contenu complet a partir d'une video YouTube via Claude AI.
"""

import os
import sys
import re
from pathlib import Path

# Fix Windows terminal encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import anthropic

try:
    from youtube_transcript_api import (
        YouTubeTranscriptApi,
        NoTranscriptFound,
        TranscriptsDisabled,
    )
    try:
        from youtube_transcript_api import IpBlocked
    except ImportError:
        IpBlocked = Exception  # fallback pour anciennes versions
except ImportError:
    print("Erreur : youtube-transcript-api non installe.")
    print("Lancez : python -m pip install youtube-transcript-api")
    sys.exit(1)


def extract_video_id(url: str) -> str:
    patterns = [
        r"(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})",
        r"(?:embed/)([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Impossible d'extraire l'ID video depuis : {url}")


# Correspondance nom affiché → codes de langue YouTube
LANG_CODES = {
    "Français":   ["fr", "fr-FR"],
    "English":    ["en", "en-US", "en-GB"],
    "Español":    ["es", "es-ES", "es-419"],
    "Deutsch":    ["de", "de-DE"],
    "Italiano":   ["it", "it-IT"],
    "Português":  ["pt", "pt-BR", "pt-PT"],
    "العربية":    ["ar"],
    "中文":       ["zh", "zh-Hans", "zh-TW"],
}

OUTPUT_LANGUAGES = list(LANG_CODES.keys())


def _get_transcript_assemblyai(video_id: str, assemblyai_key: str) -> tuple:
    """Télécharge l'audio YouTube et le transcrit via AssemblyAI."""
    import yt_dlp
    import assemblyai as aai

    import tempfile

    video_url = f"https://www.youtube.com/watch?v={video_id}"
    scraper_api_key = os.environ.get("SCRAPER_API_KEY", "")

    # Télécharge l'audio dans un fichier temporaire
    tmp_path = tempfile.mktemp(suffix=".mp4")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": tmp_path,
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
    }
    if scraper_api_key:
        ydl_opts["proxy"] = f"http://scraperapi:{scraper_api_key}@proxy-server.scraperapi.com:8001"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

    # Cherche le fichier téléchargé (yt-dlp peut changer l'extension)
    import glob
    candidates = glob.glob(tmp_path + "*") or glob.glob(tmp_path.replace(".mp4", "") + "*")
    audio_file = candidates[0] if candidates else tmp_path

    # Transcrit avec AssemblyAI en envoyant le fichier directement
    try:
        aai.settings.api_key = assemblyai_key
        config = aai.TranscriptionConfig(speech_models=["universal-2"])
        transcriber = aai.Transcriber(config=config)
        transcript = transcriber.transcribe(audio_file)
    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)

    if transcript.status == aai.TranscriptStatus.error:
        raise Exception(f"Erreur transcription : {transcript.error}")

    text = transcript.text or ""
    timestamps = []
    if hasattr(transcript, "words") and transcript.words:
        for w in transcript.words:
            start = w.start / 1000
            minutes, seconds = int(start // 60), int(start % 60)
            timestamps.append({"timestamp": f"{minutes:02d}:{seconds:02d}", "text": w.text})

    return text, timestamps


def _get_transcript_scraperapi(video_id: str, api_key: str, target_lang: str = "Français") -> tuple:
    """Récupère la transcription via ScraperAPI pour contourner le blocage YouTube."""
    import re as _re
    import json as _json
    import requests as _requests
    from xml.etree import ElementTree

    target_codes = LANG_CODES.get(target_lang, ["fr"])
    preferred = target_codes + ["fr", "en"]

    # 1. Récupère la page YouTube via ScraperAPI
    yt_url = f"https://www.youtube.com/watch?v={video_id}"
    resp = _requests.get(
        "https://api.scraperapi.com/",
        params={"api_key": api_key, "url": yt_url},
        timeout=30,
    )
    resp.raise_for_status()

    # 2. Extrait les pistes de sous-titres via ytInitialPlayerResponse
    tracks = []
    # Méthode 1 : ytInitialPlayerResponse complet
    m = _re.search(r'ytInitialPlayerResponse\s*=\s*(\{.+?\})\s*;', resp.text, _re.DOTALL)
    if m:
        try:
            pr = _json.loads(m.group(1))
            tracks = (pr.get("captions", {})
                        .get("playerCaptionsTracklistRenderer", {})
                        .get("captionTracks", []))
        except Exception:
            tracks = []

    # Méthode 2 : regex directe sur captionTracks
    if not tracks:
        m2 = _re.search(r'"captionTracks":(\[.*?\])', resp.text)
        if m2:
            try:
                tracks = _json.loads(m2.group(1))
            except Exception:
                tracks = []

    if not tracks:
        raise NoTranscriptFound(video_id, [], [])

    # 3. Choisit la meilleure piste
    track_url = None
    for code in preferred:
        for track in tracks:
            if track.get("languageCode", "").startswith(code):
                track_url = track["baseUrl"]
                break
        if track_url:
            break
    if not track_url:
        track_url = tracks[0]["baseUrl"]

    # 4. Télécharge le XML de la transcription directement (pas de blocage IP sur cet endpoint)
    xml_resp = _requests.get(track_url + "&fmt=xml", timeout=30, headers={"Accept-Language": "fr-FR,fr;q=0.9"})
    if xml_resp.status_code != 200 or not xml_resp.content.strip():
        # Fallback via ScraperAPI
        xml_resp = _requests.get(
            "https://api.scraperapi.com/",
            params={"api_key": api_key, "url": track_url},
            timeout=30,
        )
    xml_resp.raise_for_status()

    content = xml_resp.content.strip()
    if not content:
        raise NoTranscriptFound(video_id, [], [])

    # 5. Parse le XML
    root = ElementTree.fromstring(content)
    texts, timestamps = [], []
    for elem in root.findall("text"):
        start = float(elem.get("start", 0))
        text = _re.sub(r"<[^>]+>", "", elem.text or "").strip()
        if not text:
            continue
        minutes, seconds = int(start // 60), int(start % 60)
        texts.append(text)
        timestamps.append({"timestamp": f"{minutes:02d}:{seconds:02d}", "text": text})

    if not texts:
        raise NoTranscriptFound(video_id, [], [])

    return " ".join(texts), timestamps


def get_transcript(video_id: str, target_lang: str = "Français") -> tuple:
    # Priorité 1 : AssemblyAI (transcription IA de l'audio)
    assemblyai_key = os.environ.get("ASSEMBLYAI_API_KEY", "")
    if assemblyai_key:
        return _get_transcript_assemblyai(video_id, assemblyai_key)

    # Priorité 2 : ScraperAPI (sous-titres YouTube via proxy)
    scraper_api_key = os.environ.get("SCRAPER_API_KEY", "")
    if scraper_api_key:
        return _get_transcript_scraperapi(video_id, scraper_api_key, target_lang)

    # Priorité 3 : API YouTube directe (fonctionne en local)
    api = YouTubeTranscriptApi()
    transcript_list = api.list(video_id)

    transcript = None
    # Priorité : langue cible > français > anglais > tout
    target_codes = LANG_CODES.get(target_lang, ["fr"])
    preferred_langs = target_codes + ["fr", "fr-FR", "en", "en-US", "en-GB"]
    try:
        transcript = transcript_list.find_transcript(preferred_langs)
    except NoTranscriptFound:
        # Prend la première transcription disponible (sera traduite par Claude)
        for t in transcript_list:
            transcript = t
            break

    if transcript is None:
        raise NoTranscriptFound(video_id, [], [])

    fetched = transcript.fetch()

    full_text_parts = []
    timestamps = []
    for entry in fetched:
        # v1.x retourne des objets FetchedTranscriptSnippet, v0.x des dicts
        start = entry.start if hasattr(entry, "start") else entry["start"]
        text = (entry.text if hasattr(entry, "text") else entry["text"])
        text = text.replace("\n", " ").strip()
        minutes = int(start // 60)
        seconds = int(start % 60)
        ts = f"{minutes:02d}:{seconds:02d}"
        full_text_parts.append(text)
        timestamps.append({"timestamp": ts, "text": text})

    return " ".join(full_text_parts), timestamps


def get_system_prompt(language: str = "Français") -> str:
    return (
        "Tu es un expert en strategie de contenu digital et en marketing. "
        "Tu crees du contenu de haute qualite, engageant et adapte a chaque plateforme. "
        f"IMPORTANT : Tout le contenu genere doit etre EXCLUSIVEMENT en {language}. "
        "Si la transcription est dans une autre langue, traduis et adapte le contenu. "
        "Suis scrupuleusement les instructions de format donnees."
    )

# Compatibilité avec l'ancienne constante
SYSTEM_PROMPT = get_system_prompt()

CONTENT_TASKS = [
    {
        "key": "article_blog",
        "filename": "article-blog.md",
        "label": "Article de blog (800 mots, SEO)",
        "prompt_template": (
            "Cree un article de blog complet et optimise SEO d'environ 800 mots "
            "a partir de cette transcription.\n\n"
            "Structure obligatoire :\n"
            "1. Meta-titre SEO (60 car. max) -- prefixe avec `# META-TITRE : `\n"
            "2. Meta-description SEO (160 car. max) -- prefixe avec `> **META-DESC** : `\n"
            "3. Titre H1 accrocheur\n"
            "4. Introduction avec hook fort (2-3 phrases)\n"
            "5. Corps de l'article avec titres H2/H3, exemples concrets\n"
            "6. Conclusion avec call-to-action clair\n\n"
            "Format : Markdown.\n\n"
            "---\nTRANSCRIPTION :\n{transcript}"
        ),
    },
    {
        "key": "posts_linkedin",
        "filename": "posts-linkedin.md",
        "label": "3 Posts LinkedIn (storytelling / liste / contrarian)",
        "prompt_template": (
            "Cree 3 posts LinkedIn distincts a partir de cette transcription.\n\n"
            "---\n## POST 1 -- STORYTELLING\n"
            "Raconte une histoire ou anecdote tiree du contenu.\n"
            "- Hook puissant des la 1ere ligne\n"
            "- 200-300 mots\n"
            "- 1 question d'engagement en fin\n"
            "- 5-8 hashtags\n\n"
            "---\n## POST 2 -- LISTE\n"
            "Format 'X choses que j'ai appris / X erreurs a eviter'\n"
            "- Numeros ou emojis par item\n"
            "- 200-250 mots\n"
            "- CTA concret\n"
            "- 5-8 hashtags\n\n"
            "---\n## POST 3 -- CONTRARIAN\n"
            "Opinion provocatrice ou point de vue contre-intuitif sur le sujet.\n"
            "- Affirmation audacieuse en 1ere ligne\n"
            "- Argumentation solide\n"
            "- Invite au debat en conclusion\n"
            "- 5-8 hashtags\n\n"
            "---\nTRANSCRIPTION :\n{transcript}"
        ),
    },
    {
        "key": "posts_x",
        "filename": "posts-x.md",
        "label": "10 Posts X / Twitter",
        "prompt_template": (
            "Cree 10 posts X (Twitter) percutants a partir de cette transcription.\n\n"
            "Chaque post : max 280 caracteres, hook immediat, 1-3 hashtags.\n"
            "Utilise des angles varies : conseil actionnable, fait surprenant, "
            "citation, question, thread starter, opinion forte, before/after, "
            "mythe vs realite...\n\n"
            "Format :\n---\n**[N] [ANGLE]**\n[contenu du post]\n---\n\n"
            "TRANSCRIPTION :\n{transcript}"
        ),
    },
    {
        "key": "newsletter",
        "filename": "newsletter.md",
        "label": "Newsletter email",
        "prompt_template": (
            "Cree un email newsletter complet a partir de cette transcription.\n\n"
            "Structure :\n"
            "OBJET : [accrocheur, max 60 car.]\n"
            "PRE-HEADER : [complete l'objet, max 90 car.]\n\n"
            "Corps (300-500 mots) :\n"
            "- Salutation chaleureuse\n"
            "- Accroche personnelle\n"
            "- Resume des insights cles sous forme narrative\n"
            "- 1-2 CTA clairs et naturels\n"
            "- Signature friendly\n\n"
            "Ton : conversationnel, bienveillant, comme un email d'un ami expert.\n\n"
            "---\nTRANSCRIPTION :\n{transcript}"
        ),
    },
    {
        "key": "resume_executif",
        "filename": "resume-executif.md",
        "label": "Resume executif (10 bullet points, 2 min)",
        "prompt_template": (
            "Cree un resume executif en 10 bullet points a partir de cette transcription.\n"
            "Objectif : briefer quelqu'un en moins de 2 minutes.\n\n"
            "Format :\n"
            "# Resume Executif : [Titre du sujet]\n"
            "**Lecture** : 2 min | **Source** : {video_url}\n\n"
            "---\n\n## 10 Points Cles\n\n"
            "1. **[Theme court]** -- [1-2 phrases actionnables, concretes]\n"
            "2. **[Theme court]** -- [1-2 phrases actionnables, concretes]\n"
            "... (jusqu'a 10)\n\n"
            "---\n## A retenir\n"
            "> [La lecon centrale en une phrase memorable]\n\n"
            "---\nTRANSCRIPTION :\n{transcript}"
        ),
    },
    {
        "key": "notes_cles",
        "filename": "notes-cles.md",
        "label": "Notes cles + citations + timestamps",
        "prompt_template": (
            "Cree une fiche de notes detaillee avec les citations cles et leurs timestamps.\n\n"
            "Format :\n"
            "# Notes Cles -- [Titre du sujet]\n"
            "**Source** : {video_url}\n\n"
            "---\n\n## Citations & Moments Importants\n\n"
            "### [Theme 1]\n"
            "> \"[Citation directe ou paraphrase fidele]\"\n"
            "[MM:SS] -- *[Contexte en 1 phrase]*\n\n"
            "### [Theme 2]\n"
            "> \"[Citation directe ou paraphrase fidele]\"\n"
            "[MM:SS] -- *[Contexte en 1 phrase]*\n\n"
            "[8 a 12 moments cles minimum]\n\n"
            "---\n\n## Concepts & Termes Cles\n"
            "| Terme | Definition breve |\n"
            "|-------|------------------|\n"
            "| ... | ... |\n\n"
            "---\nTRANSCRIPTION AVEC TIMESTAMPS :\n{transcript_ts}"
        ),
    },
]


def generate_piece(
    client: anthropic.Anthropic,
    task: dict,
    transcript: str,
    transcript_ts: str,
    video_url: str,
) -> str:
    prompt = task["prompt_template"].format(
        transcript=transcript[:40000],
        transcript_ts=transcript_ts[:50000],
        video_url=video_url,
    )

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        content = ""
        for text in stream.text_stream:
            print(text, end="", flush=True)
            content += text
    return content


def main():
    print("\n" + "=" * 55)
    print("  YouTube Content Kit Generator")
    print("=" * 55)

    # Recuperer l'URL
    if len(sys.argv) > 1:
        video_url = sys.argv[1].strip()
    else:
        video_url = input("\nURL de la video YouTube : ").strip()

    if not video_url:
        print("Erreur : URL manquante.")
        sys.exit(1)

    # Extraire l'ID
    try:
        video_id = extract_video_id(video_url)
    except ValueError as e:
        print(f"Erreur : {e}")
        sys.exit(1)

    print(f"\n>> Video ID : {video_id}")

    # Recuperer la transcription
    print(">> Recuperation de la transcription...", end=" ", flush=True)
    try:
        transcript, timestamps = get_transcript(video_id)
    except TranscriptsDisabled:
        print("\nErreur : Les sous-titres sont desactives pour cette video.")
        sys.exit(1)
    except NoTranscriptFound:
        print("\nErreur : Aucune transcription trouvee.")
        sys.exit(1)
    except IpBlocked:
        print("\nErreur : YouTube bloque les requetes depuis cette IP (environnement cloud).")
        print("Solution : Lance le script directement depuis ton ordinateur.")
        sys.exit(1)
    except Exception as e:
        print(f"\nErreur : {e}")
        sys.exit(1)

    word_count = len(transcript.split())
    print(f"OK ({word_count} mots, {len(timestamps)} segments)")

    # Formatter la version avec timestamps
    transcript_ts = "\n".join(
        f"[{e['timestamp']}] {e['text']}" for e in timestamps
    )

    # Client Anthropic
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("\nErreur : ANTHROPIC_API_KEY non definie dans les variables d'environnement.")
        sys.exit(1)
    client = anthropic.Anthropic(api_key=api_key)

    # Repertoire de sortie
    output_dir = Path("content-kit")
    output_dir.mkdir(exist_ok=True)

    # Generer chaque piece de contenu
    total = len(CONTENT_TASKS)
    results = {}

    for i, task in enumerate(CONTENT_TASKS, 1):
        print(f"\n{'-' * 55}")
        print(f"[{i}/{total}] {task['label']}")
        print("-" * 55)

        try:
            content = generate_piece(
                client, task, transcript, transcript_ts, video_url
            )
            results[task["key"]] = content

            # Sauvegarder immediatement
            filepath = output_dir / task["filename"]
            filepath.write_text(content, encoding="utf-8")
            print(f"\n\n>> Sauvegarde : {filepath}")

        except anthropic.APIError as e:
            print(f"\nErreur API : {e}")
            continue

    # Resume final
    print(f"\n{'=' * 55}")
    print("Kit de contenu genere avec succes !")
    print(f"Dossier : {output_dir.resolve()}\n")
    for task in CONTENT_TASKS:
        if task["key"] in results:
            fp = output_dir / task["filename"]
            size = fp.stat().st_size
            print(f"  [OK] {task['filename']}  ({size:,} octets)")
    print()


if __name__ == "__main__":
    main()
