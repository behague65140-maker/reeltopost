"""
ReelToPost — Interface web Streamlit
"""

import os
import io
import re
import zipfile
import streamlit as st
import anthropic
from dotenv import load_dotenv

from database import (
    init_db, get_or_create_user, increment_usage, kits_remaining, PLANS,
    list_all_users, set_plan, delete_user, reset_usage, export_emails_csv,
)
from content_kit import (
    extract_video_id,
    get_transcript,
    get_system_prompt,
    CONTENT_TASKS,
    OUTPUT_LANGUAGES,
    IpBlocked,
)
from youtube_transcript_api import NoTranscriptFound, TranscriptsDisabled
from auth_google import get_auth_url, exchange_code, google_configured
from i18n import t, SITE_LANGUAGES

load_dotenv()

# Streamlit Cloud injecte les secrets dans st.secrets — on les recopie dans os.environ
try:
    for k, v in st.secrets.items():
        if k not in os.environ:
            os.environ[k] = str(v)
except Exception:
    pass

init_db()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ReelToPost",
    page_icon="🎬",
    layout="wide",
)

api_key = os.environ.get("ANTHROPIC_API_KEY", "")
if not api_key:
    st.error("Clé API Anthropic manquante dans le fichier `.env`.")
    st.stop()


# ---------------------------------------------------------------------------
# CSS — cartes pricing
# ---------------------------------------------------------------------------
st.markdown("""
<style>
.plan-card {
    border: 1px solid #333;
    border-radius: 12px;
    padding: 28px 24px;
    text-align: center;
    height: 100%;
}
.plan-card.popular {
    border: 2px solid #ff4b4b;
}
.plan-price {
    font-size: 2.4rem;
    font-weight: 700;
    margin: 8px 0;
}
.plan-sub {
    color: #888;
    font-size: 0.85rem;
    margin-bottom: 20px;
}
.plan-feature {
    text-align: left;
    margin: 6px 0;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "main"
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_picture" not in st.session_state:
    st.session_state.user_picture = None
if "site_lang" not in st.session_state:
    st.session_state.site_lang = "fr"
if "_oauth_flow" not in st.session_state:
    st.session_state._oauth_flow = None

# ---------------------------------------------------------------------------
# Callback OAuth Google — intercepté avant tout rendu
# ---------------------------------------------------------------------------
_params = st.query_params
if "code" in _params and st.session_state.user is None:
    with st.spinner("Connexion avec Google…"):
        try:
            flow = st.session_state._oauth_flow
            if flow is None:
                # Flow perdu (ex: rechargement de page) — on recrée un flow minimal
                from auth_google import get_auth_url as _gau
                _, flow = _gau()
            email, name, picture = exchange_code(_params["code"], flow)
            st.session_state._oauth_flow = None
            st.session_state.user = get_or_create_user(email, name=name, picture=picture, provider="google")
            st.session_state.user_name = name
            st.session_state.user_picture = picture
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Erreur d'authentification Google : {e}")
            st.session_state._oauth_flow = None
            st.query_params.clear()


# ---------------------------------------------------------------------------
# Page : Login dédiée
# ---------------------------------------------------------------------------
def page_login():
    st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0d0d1a 0%, #111827 50%, #0d1a2e 100%); }
.login-wrap {
    max-width: 460px;
    margin: 6vh auto 0;
    text-align: center;
}
.login-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 24px;
    padding: 3rem 2.5rem 2.5rem;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 40px rgba(0,0,0,0.5);
    margin-top: 2rem;
}
.login-logo {
    font-size: 3rem;
    margin-bottom: 0.5rem;
}
.login-title {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 30%, #a78bfa 70%, #60a5fa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.4rem;
}
.login-sub {
    color: #94a3b8;
    font-size: 0.95rem;
    margin-bottom: 2rem;
}
.google-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    width: 100%;
    padding: 14px 24px;
    background: #fff;
    color: #1f1f1f;
    border: none;
    border-radius: 12px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
    transition: box-shadow 0.2s;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.google-btn:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.4); }
.divider-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 1.5rem 0;
    color: #4b5563;
    font-size: 0.85rem;
}
.divider-row::before, .divider-row::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.1);
}
.login-features {
    display: flex;
    justify-content: center;
    gap: 20px;
    flex-wrap: wrap;
    margin-top: 2rem;
}
.login-feat {
    color: #94a3b8;
    font-size: 0.82rem;
    display: flex;
    align-items: center;
    gap: 6px;
}
.policy-link {
    color: #6b7280;
    font-size: 0.8rem;
    margin-top: 1.5rem;
    text-decoration: none;
}
</style>

<!-- Orbes fond -->
<div style="position:fixed;width:400px;height:400px;background:#7c3aed;border-radius:50%;filter:blur(80px);opacity:0.1;top:-100px;left:-100px;pointer-events:none;"></div>
<div style="position:fixed;width:350px;height:350px;background:#1d4ed8;border-radius:50%;filter:blur(80px);opacity:0.1;bottom:-80px;right:-80px;pointer-events:none;"></div>

<div class="login-wrap">
    <div class="login-logo">🎬</div>
    <div class="login-title">ReelToPost</div>
    <div class="login-sub">LOGIN_SUB</div>
    <div class="login-card">
""".replace("LOGIN_SUB", t("login_sub")), unsafe_allow_html=True)

    if google_configured():
        auth_url, flow = get_auth_url()
        st.session_state._oauth_flow = flow
        st.markdown(f"""
<a href="{auth_url}" class="google-btn">
    <svg width="20" height="20" viewBox="0 0 48 48">
        <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
        <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
        <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
        <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.18 1.48-4.97 2.36-8.16 2.36-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
    </svg>
    {t("login_google")}
</a>
""", unsafe_allow_html=True)
    else:
        st.warning(t("login_google_missing"))

    st.markdown(f"""
        <div class="login-features">
            <span class="login-feat">{t("login_feat_free")}</span>
            <span class="login-feat">{t("login_feat_secure")}</span>
            <span class="login-feat">{t("login_feat_instant")}</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        if st.button("📜 Politique d'utilisation", use_container_width=True):
            st.session_state.page = "policy"
            st.rerun()


# ---------------------------------------------------------------------------
# Page : Politique d'utilisation
# ---------------------------------------------------------------------------
def page_policy():
    with st.sidebar:
        st.markdown("## 🎬 ReelToPost")
        st.divider()
        if st.button(t("back_to_app"), use_container_width=True):
            st.session_state.page = "main"
            st.rerun()

    st.title(t("policy_title"))
    st.caption(t("policy_updated"))
    st.markdown(t("policy_body"))

    st.divider()
    if st.button(t("back_to_app"), use_container_width=True, type="primary"):
        st.session_state.page = "main"
        st.rerun()


# ---------------------------------------------------------------------------
# Page : Admin
# ---------------------------------------------------------------------------
def page_admin():
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "").lower()

    st.title(t("admin_title"))
    st.caption(t("admin_caption"))

    users = list_all_users()
    total = len(users)
    paying = sum(1 for u in users if u["plan"] != "free")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(t("admin_total"), total)
    col2.metric(t("admin_paying"), paying)
    col3.metric(t("admin_conversion"), f"{paying/total*100:.0f}%" if total else "—")
    google_users = sum(1 for u in users if u.get("login_provider") == "google")
    col4.metric(t("admin_google"), google_users)

    col_search, col_export = st.columns([3, 1])
    with col_export:
        csv_data = export_emails_csv()
        st.download_button(
            label=t("admin_export_csv"),
            data=csv_data.encode("utf-8"),
            file_name="reeltopost-emails.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.divider()

    with col_search:
        search = st.text_input(t("admin_search"), placeholder="user@example.com")
    filtered = [u for u in users if search.lower() in u["email"]] if search else users

    st.subheader(t("admin_users_count", n=len(filtered)))

    for u in filtered:
        provider_icon = "🔵" if u.get("login_provider") == "google" else "📧"
        name_display = f" ({u['name']})" if u.get("name") else ""
        with st.expander(f"{provider_icon} {u['email']}{name_display}  —  {PLANS[u['plan']]['label']}  |  {u['kits_used']} kits"):
            col_plan, col_reset, col_del = st.columns([2, 1, 1])

            with col_plan:
                new_plan = st.selectbox(
                    "Plan",
                    options=list(PLANS.keys()),
                    index=list(PLANS.keys()).index(u["plan"]),
                    format_func=lambda k: PLANS[k]["label"],
                    key=f"plan_{u['email']}",
                )
                if st.button(t("admin_apply"), key=f"apply_{u['email']}", type="primary"):
                    set_plan(u["email"], new_plan)
                    st.success(t("admin_plan_updated", plan=PLANS[new_plan]["label"]))
                    st.rerun()

            with col_reset:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(t("admin_reset_quota"), key=f"reset_{u['email']}"):
                    reset_usage(u["email"])
                    st.success(t("admin_quota_reset"))
                    st.rerun()

            with col_del:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button(t("admin_delete"), key=f"del_{u['email']}"):
                    delete_user(u["email"])
                    st.warning(t("admin_deleted", email=u["email"]))
                    st.rerun()

    st.divider()
    if st.button(t("admin_back")):
        st.session_state.is_admin = False
        st.rerun()


# ---------------------------------------------------------------------------
# Page : Application principale (page d'accueil)
# ---------------------------------------------------------------------------
def page_main():
    user = st.session_state.user
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "").lower()

    # --- Sidebar ---
    with st.sidebar:
        st.markdown("## 🎬 ReelToPost")
        st.divider()

        if user is None:
            if st.button(t("login_btn"), use_container_width=True, type="primary"):
                st.session_state.page = "login"
                st.rerun()
        else:
            plan_info = PLANS[user["plan"]]
            remaining = kits_remaining(user)

            if st.session_state.user_picture:
                st.markdown(
                    f'<img src="{st.session_state.user_picture}" '
                    f'style="width:48px;height:48px;border-radius:50%;margin-bottom:6px;">',
                    unsafe_allow_html=True,
                )
            display_name = st.session_state.user_name or user["email"].split("@")[0]
            st.markdown(f"**{display_name}**")
            st.caption(user["email"])
            st.caption(t("plan_label", plan=plan_info["label"]))

            if remaining is None:
                st.success(t("kits_unlimited"))
            elif remaining <= 1:
                st.error(t("kits_remaining_1", n=remaining))
            else:
                st.info(t("kits_remaining_n", n=remaining))

            if user["plan"] != "agency":
                st.link_button(t("upgrade_btn"), PLANS["pro"]["stripe_link"] or "#", use_container_width=True)

            if user["email"] == ADMIN_EMAIL:
                if st.button(t("admin_btn"), key="go_admin", use_container_width=True):
                    st.session_state.is_admin = True
                    st.rerun()

            if st.button(t("logout_btn"), use_container_width=True):
                st.session_state.user = None
                st.session_state.user_name = None
                st.session_state.user_picture = None
                st.rerun()

            st.divider()
            st.markdown(f"**{t('content_to_generate')}**")

        # Formats autorisés selon le plan
        FREE_KEYS = {"article_blog", "newsletter", "posts_x"}
        is_free = (user is None) or (user and user["plan"] == "free")

        task_selection = {}
        for task in CONTENT_TASKS:
            allowed = (not is_free) or (task["key"] in FREE_KEYS)
            if allowed:
                task_selection[task["key"]] = st.checkbox(task["label"], value=True)
            else:
                st.checkbox(
                    f"{task['label']} 🔒",
                    value=False,
                    disabled=True,
                    help="Pro / Agence uniquement",
                )

        if is_free:
            st.caption("🔒 3 formats sur 6 — [Passer au Pro]({})" .format(PLANS["pro"]["stripe_link"] or "#"))

        st.divider()
        st.markdown(f"**{t('output_language')}**")
        output_lang = st.selectbox(
            "output_lang",
            options=OUTPUT_LANGUAGES,
            index=0,
            label_visibility="collapsed",
        )

        st.divider()
        st.markdown(f"**{t('site_language')}**")
        lang_options = list(SITE_LANGUAGES.keys())
        lang_labels = list(SITE_LANGUAGES.values())
        current_idx = lang_options.index(st.session_state.site_lang)
        chosen = st.selectbox(
            "site_lang_select",
            options=lang_options,
            index=current_idx,
            format_func=lambda k: SITE_LANGUAGES[k],
            label_visibility="collapsed",
        )
        if chosen != st.session_state.site_lang:
            st.session_state.site_lang = chosen
            st.rerun()

    # --- Fond animé + Hero ---
    st.markdown("""
<style>
/* Fond dégradé animé */
.stApp {
    background: linear-gradient(135deg, #0d0d1a 0%, #111827 50%, #0d1a2e 100%);
    min-height: 100vh;
}

/* Particules flottantes */
.particle {
    position: fixed;
    pointer-events: none;
    z-index: 0;
    animation: floatUp linear infinite;
    opacity: 0;
    user-select: none;
}

@keyframes floatUp {
    0%   { transform: translateY(105vh) rotate(0deg) scale(0.8); opacity: 0; }
    5%   { opacity: 0.18; }
    90%  { opacity: 0.18; }
    100% { transform: translateY(-10vh) rotate(540deg) scale(1.1); opacity: 0; }
}

/* Orbes lumineux en arrière-plan */
.orb {
    position: fixed;
    border-radius: 50%;
    filter: blur(80px);
    pointer-events: none;
    z-index: 0;
    animation: pulse ease-in-out infinite alternate;
}
@keyframes pulse {
    0%   { transform: scale(1);    opacity: 0.07; }
    100% { transform: scale(1.25); opacity: 0.13; }
}

/* Section hero */
.hero {
    position: relative;
    z-index: 1;
    text-align: center;
    padding: 3.5rem 1rem 2rem;
}
.hero-badge {
    display: inline-block;
    background: rgba(255,75,75,0.15);
    border: 1px solid rgba(255,75,75,0.4);
    color: #ff6b6b;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 4px 14px;
    border-radius: 20px;
    margin-bottom: 1.2rem;
}
.hero-title {
    font-size: clamp(2.2rem, 5vw, 3.8rem);
    font-weight: 800;
    line-height: 1.15;
    margin: 0 0 1rem;
    background: linear-gradient(135deg, #ffffff 30%, #a78bfa 70%, #60a5fa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-sub {
    font-size: 1.1rem;
    color: #94a3b8;
    max-width: 540px;
    margin: 0 auto 2.5rem;
    line-height: 1.6;
}

/* Carte input */
.input-card {
    position: relative;
    z-index: 1;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 2rem 2rem 1.5rem;
    backdrop-filter: blur(12px);
    max-width: 720px;
    margin: 0 auto 2rem;
    box-shadow: 0 8px 40px rgba(0,0,0,0.4);
}

/* Badges features */
.features-row {
    position: relative;
    z-index: 1;
    display: flex;
    justify-content: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 2.5rem;
}
.feature-badge {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 30px;
    padding: 6px 16px;
    font-size: 0.82rem;
    color: #94a3b8;
}
</style>

<!-- Orbes -->
<div class="orb" style="width:500px;height:500px;background:#7c3aed;top:-150px;left:-100px;animation-duration:7s;"></div>
<div class="orb" style="width:400px;height:400px;background:#1d4ed8;bottom:-100px;right:-80px;animation-duration:9s;animation-delay:-3s;"></div>
<div class="orb" style="width:300px;height:300px;background:#db2777;top:40%;left:55%;animation-duration:11s;animation-delay:-5s;"></div>

<!-- Particules flottantes -->
<div class="particle" style="left:5%;font-size:1.6rem;animation-duration:14s;animation-delay:0s;">🎬</div>
<div class="particle" style="left:12%;font-size:1.2rem;animation-duration:18s;animation-delay:-4s;">📝</div>
<div class="particle" style="left:20%;font-size:1.4rem;animation-duration:12s;animation-delay:-8s;">🎵</div>
<div class="particle" style="left:28%;font-size:1.1rem;animation-duration:20s;animation-delay:-2s;">📱</div>
<div class="particle" style="left:36%;font-size:1.5rem;animation-duration:15s;animation-delay:-10s;">✍️</div>
<div class="particle" style="left:44%;font-size:1.2rem;animation-duration:17s;animation-delay:-6s;">📊</div>
<div class="particle" style="left:52%;font-size:1.4rem;animation-duration:13s;animation-delay:-1s;">🎯</div>
<div class="particle" style="left:60%;font-size:1.1rem;animation-duration:19s;animation-delay:-7s;">💡</div>
<div class="particle" style="left:68%;font-size:1.5rem;animation-duration:16s;animation-delay:-3s;">🚀</div>
<div class="particle" style="left:76%;font-size:1.2rem;animation-duration:11s;animation-delay:-9s;">📸</div>
<div class="particle" style="left:84%;font-size:1.4rem;animation-duration:22s;animation-delay:-5s;">🎤</div>
<div class="particle" style="left:92%;font-size:1.1rem;animation-duration:14s;animation-delay:-12s;">📰</div>
<div class="particle" style="left:8%;font-size:1.0rem;animation-duration:25s;animation-delay:-15s;">⚡</div>
<div class="particle" style="left:33%;font-size:1.3rem;animation-duration:21s;animation-delay:-11s;">🌟</div>
<div class="particle" style="left:70%;font-size:1.0rem;animation-duration:18s;animation-delay:-13s;">🎨</div>
<div class="particle" style="left:88%;font-size:1.3rem;animation-duration:16s;animation-delay:-2s;">📣</div>

<!-- Hero -->
<div class="hero">
    <div class="hero-badge">HERO_BADGE</div>
    <div class="hero-title">HERO_TITLE</div>
    <div class="hero-sub">HERO_SUB</div>
</div>

<!-- Badges features -->
<div class="features-row">
    <span class="feature-badge">📝 Article de blog</span>
    <span class="feature-badge">💼 Post LinkedIn</span>
    <span class="feature-badge">🐦 Fil Twitter/X</span>
    <span class="feature-badge">📧 Newsletter</span>
    <span class="feature-badge">📊 Résumé exécutif</span>
    <span class="feature-badge">🔑 Notes clés</span>
</div>

<div class="input-card">
""".replace("HERO_BADGE", t("hero_badge"))
   .replace("HERO_TITLE", t("hero_title"))
   .replace("HERO_SUB", t("hero_sub")), unsafe_allow_html=True)

    # JS patch — copier-coller dans l'iframe
    st.markdown("""
<script>
(function enablePaste() {
    function patch() {
        const input = document.querySelector(
            'input[placeholder="https://www.youtube.com/watch?v=..."]'
        );
        if (!input || input.dataset.pastePatch) return;
        input.dataset.pastePatch = "1";
        input.addEventListener("paste", function (e) {
            const text = (e.clipboardData || window.clipboardData).getData("text");
            if (!text) return;
            e.preventDefault();
            e.stopPropagation();
            const setter = Object.getOwnPropertyDescriptor(
                window.HTMLInputElement.prototype, "value"
            ).set;
            setter.call(input, text.trim());
            input.dispatchEvent(new Event("input", { bubbles: true }));
        });
    }
    const id = setInterval(function () {
        patch();
        if (document.querySelector(
            'input[placeholder="https://www.youtube.com/watch?v=..."][data-paste-patch="1"]'
        )) clearInterval(id);
    }, 300);
})();
</script>
""", unsafe_allow_html=True)

    url = st.text_input(
        t("url_label"),
        placeholder=t("url_placeholder"),
    )

    # Quota dépassé
    if user is not None and kits_remaining(user) == 0:
        st.markdown("</div>", unsafe_allow_html=True)
        st.warning(t("quota_reached"))
        col_pro, col_agency = st.columns(2)
        with col_pro:
            if PLANS["pro"]["stripe_link"]:
                st.link_button(t("upgrade_pro"), PLANS["pro"]["stripe_link"], type="primary", use_container_width=True)
        with col_agency:
            if PLANS["agency"]["stripe_link"]:
                st.link_button(t("upgrade_agency"), PLANS["agency"]["stripe_link"], use_container_width=True)
        st.stop()

    generate_disabled = user is None
    generate_btn = st.button(
        t("generate_btn"),
        type="primary",
        use_container_width=True,
        disabled=generate_disabled,
    )

    if user is None:
        st.info(t("login_hint"))

    st.markdown("</div>", unsafe_allow_html=True)

    # --- Génération ---
    if generate_btn:
        if not url:
            st.error(t("enter_url"))
            st.stop()

        try:
            video_id = extract_video_id(url)
        except ValueError:
            st.error(t("invalid_url"))
            st.stop()

        with st.status(t("getting_transcript"), expanded=False) as status:
            try:
                transcript, timestamps = get_transcript(video_id, target_lang=output_lang)
                status.update(
                    label=t("transcript_ok", n=len(transcript.split())),
                    state="complete",
                )
            except TranscriptsDisabled:
                status.update(label=t("transcript_disabled"), state="error")
                st.stop()
            except NoTranscriptFound:
                status.update(label=t("transcript_not_found"), state="error")
                st.stop()
            except IpBlocked:
                status.update(label=t("transcript_ip_blocked"), state="error")
                st.error(t("transcript_ip_msg"))
                st.stop()
            except Exception as e:
                status.update(label=t("transcript_error", e=e), state="error")
                st.stop()

        transcript_ts = "\n".join(
            f"[{e['timestamp']}] {e['text']}" for e in timestamps
        )
        client = anthropic.Anthropic(api_key=api_key)
        system_prompt = get_system_prompt(output_lang)
        FREE_KEYS = {"article_blog", "newsletter", "posts_x"}
        selected_tasks = [
            task for task in CONTENT_TASKS
            if task_selection.get(task["key"])
            and (user["plan"] != "free" or task["key"] in FREE_KEYS)
        ]

        if not selected_tasks:
            st.warning(t("select_content"))
            st.stop()

        increment_usage(user["email"])
        st.session_state.user = get_or_create_user(user["email"])

        st.divider()
        st.subheader(t("kit_generated"))

        tabs = st.tabs([t["label"] for t in selected_tasks])
        generated = {}

        for tab, task in zip(tabs, selected_tasks):
            with tab:
                prompt = task["prompt_template"].format(
                    transcript=transcript[:40000],
                    transcript_ts=transcript_ts[:50000],
                    video_url=url,
                )
                try:
                    with client.messages.stream(
                        model="claude-opus-4-6",
                        max_tokens=4096,
                        system=system_prompt,
                        messages=[{"role": "user", "content": prompt}],
                    ) as stream:
                        content = st.empty().write_stream(
                            chunk for chunk in stream.text_stream
                        )
                    generated[task["key"]] = {"content": content, "filename": task["filename"]}
                    st.download_button(
                        label=f"⬇️ {task['filename']}",
                        data=content.encode("utf-8"),
                        file_name=task["filename"],
                        mime="text/markdown",
                        key=f"dl_{task['key']}",
                    )
                except anthropic.APIError as e:
                    st.error(t("api_error", e=e))

        # ZIP — Pro et Agence uniquement
        if generated:
            st.divider()
            if user["plan"] in ("pro", "agency"):
                buf = io.BytesIO()
                with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                    for data in generated.values():
                        zf.writestr(data["filename"], data["content"])
                buf.seek(0)
                st.download_button(
                    label=t("download_zip"),
                    data=buf,
                    file_name="content-kit.zip",
                    mime="application/zip",
                    type="primary",
                    use_container_width=True,
                )
            else:
                st.info(t("zip_pro_only"))
                if PLANS["pro"]["stripe_link"]:
                    st.link_button(t("upgrade_pro_link"), PLANS["pro"]["stripe_link"], type="primary")

    # --- Pricing (en bas, repliable) ---
    st.divider()
    col_how, col_pricing_toggle, col_policy = st.columns([1, 2, 1])
    with col_how:
        if st.button(t("how_it_works"), use_container_width=True):
            st.session_state.page = "how_it_works"
            st.rerun()
    with col_policy:
        if st.button(t("policy"), use_container_width=True):
            st.session_state.page = "policy"
            st.rerun()

    with st.expander(t("see_plans")):
        col_free, col_pro, col_agency = st.columns(3)

        with col_free:
            st.markdown("""
<div class="plan-card">
<h3>Gratuit</h3>
<div class="plan-price">0€</div>
<div class="plan-sub">pour toujours</div>
<div class="plan-feature">✅ 3 kits / mois</div>
<div class="plan-feature">✅ 3 formats (Blog, Newsletter, X)</div>
<div class="plan-feature">✅ Téléchargement Markdown</div>
<div class="plan-feature">❌ Export ZIP</div>
<div class="plan-feature">❌ Support prioritaire</div>
</div>
""", unsafe_allow_html=True)

        with col_pro:
            st.markdown("""
<div class="plan-card popular">
<span style="background:#ff4b4b;color:white;padding:2px 10px;border-radius:20px;font-size:0.75rem;">⭐ POPULAIRE</span>
<h3>Pro</h3>
<div class="plan-price">19€</div>
<div class="plan-sub">/ mois</div>
<div class="plan-feature">✅ 50 kits / mois</div>
<div class="plan-feature">✅ 6 formats de contenu</div>
<div class="plan-feature">✅ Téléchargement Markdown</div>
<div class="plan-feature">✅ Export ZIP</div>
<div class="plan-feature">❌ Support prioritaire</div>
</div>
""", unsafe_allow_html=True)
            if PLANS["pro"]["stripe_link"]:
                st.link_button("S'abonner →", PLANS["pro"]["stripe_link"], use_container_width=True, type="primary")

        with col_agency:
            st.markdown("""
<div class="plan-card">
<h3>Agence</h3>
<div class="plan-price">79€</div>
<div class="plan-sub">/ mois</div>
<div class="plan-feature">✅ Kits illimités</div>
<div class="plan-feature">✅ 6 formats de contenu</div>
<div class="plan-feature">✅ Téléchargement Markdown</div>
<div class="plan-feature">✅ Export ZIP</div>
<div class="plan-feature">✅ Support prioritaire</div>
</div>
""", unsafe_allow_html=True)
            if PLANS["agency"]["stripe_link"]:
                st.link_button("S'abonner →", PLANS["agency"]["stripe_link"], use_container_width=True)


# ---------------------------------------------------------------------------
# Page : Comment ça marche
# ---------------------------------------------------------------------------
def page_how_it_works():
    with st.sidebar:
        st.markdown("## 🎬 ReelToPost")
        st.divider()
        if st.button(t("back_to_app"), use_container_width=True, type="primary"):
            st.session_state.page = "main"
            st.rerun()

    st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0d0d1a 0%, #111827 50%, #0d1a2e 100%); }
.how-hero { text-align:center; padding: 3rem 1rem 2rem; }
.how-title {
    font-size: clamp(2rem, 4vw, 3rem);
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 30%, #a78bfa 70%, #60a5fa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
}
.how-sub { color: #94a3b8; font-size: 1rem; margin-bottom: 2.5rem; }
.steps-row {
    display: flex;
    gap: 1.5rem;
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: 3rem;
}
.step-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 1.8rem 1.5rem;
    text-align: center;
    width: 200px;
    position: relative;
}
.step-number {
    width: 36px; height: 36px;
    border-radius: 50%;
    background: linear-gradient(135deg, #7c3aed, #3b82f6);
    color: white;
    font-weight: 700;
    font-size: 1rem;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 1rem;
}
.step-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.step-label { color: #e2e8f0; font-weight: 600; font-size: 0.95rem; }
.step-desc { color: #94a3b8; font-size: 0.82rem; margin-top: 0.4rem; }
.arrow { color: #4b5563; font-size: 1.5rem; align-self: center; }
.demo-section {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 2rem;
    margin-bottom: 2rem;
}
.demo-label {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(124,58,237,0.2);
    border: 1px solid rgba(124,58,237,0.4);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.8rem;
    color: #a78bfa;
    font-weight: 600;
    margin-bottom: 1rem;
}
.video-ref {
    background: rgba(255,75,75,0.08);
    border: 1px solid rgba(255,75,75,0.2);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 1.5rem;
    color: #fca5a5;
    font-size: 0.9rem;
}
</style>

<div class="how-hero">
    <div class="how-title">HIW_TITLE</div>
    <div class="how-sub">HIW_SUB</div>
</div>

<div class="steps-row">
    <div class="step-card">
        <div class="step-number">1</div>
        <div class="step-icon">🔗</div>
        <div class="step-label">HIW_S1L</div>
        <div class="step-desc">HIW_S1D</div>
    </div>
    <div class="arrow">→</div>
    <div class="step-card">
        <div class="step-number">2</div>
        <div class="step-icon">🤖</div>
        <div class="step-label">HIW_S2L</div>
        <div class="step-desc">HIW_S2D</div>
    </div>
    <div class="arrow">→</div>
    <div class="step-card">
        <div class="step-number">3</div>
        <div class="step-icon">📦</div>
        <div class="step-label">HIW_S3L</div>
        <div class="step-desc">HIW_S3D</div>
    </div>
</div>
""".replace("HIW_TITLE", t("hiw_title"))
   .replace("HIW_SUB",   t("hiw_sub"))
   .replace("HIW_S1L",   t("hiw_step1_label"))
   .replace("HIW_S1D",   t("hiw_step1_desc"))
   .replace("HIW_S2L",   t("hiw_step2_label"))
   .replace("HIW_S2D",   t("hiw_step2_desc"))
   .replace("HIW_S3L",   t("hiw_step3_label"))
   .replace("HIW_S3D",   t("hiw_step3_desc")), unsafe_allow_html=True)

    # --- Vidéo source fictive ---
    st.markdown("""
<div class="demo-section">
<div class="demo-label">DEMO_LABEL</div>
<div class="video-ref">
    ▶️ &nbsp; <strong>Comment construire une audience en partant de zéro</strong>
    &nbsp;•&nbsp; 18 min &nbsp;•&nbsp; 4 200 vues
</div>
""".replace("DEMO_LABEL", t("hiw_demo_label")), unsafe_allow_html=True)
    st.markdown(t("hiw_demo_note"))
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Exemples générés ---
    tab_blog, tab_linkedin, tab_twitter, tab_newsletter, tab_resume, tab_notes = st.tabs([
        "📝 Article de blog",
        "💼 LinkedIn",
        "🐦 Twitter/X",
        "📧 Newsletter",
        "📊 Résumé exécutif",
        "🔑 Notes clés",
    ])

    with tab_blog:
        st.markdown("""
# META-TITRE : Comment construire une audience de 0 à 10 000 abonnés en 90 jours

> **META-DESC** : Découvrez la méthode étape par étape pour créer une audience engagée depuis zéro, sans budget publicitaire et sans algorithme magique.

# De 0 à 10 000 abonnés : la méthode qui change tout

Tu publies depuis des mois, mais personne ne regarde ? Tu n'es pas seul. **97% des créateurs abandonnent avant d'atteindre leurs 1 000 premiers abonnés.** Pourtant, il existe une méthode simple — et contre-intuitive — pour inverser la tendance.

## 1. Arrête de créer pour tout le monde

La première erreur des débutants : vouloir plaire à tout le monde. Le résultat ? Un contenu fade que personne ne partage.

> "Si ton contenu convient à tout le monde, il n'est parfait pour personne." — Alex Hormozi

Choisis **un avatar ultra-précis** : Marie, 34 ans, responsable marketing dans une PME, qui manque de temps mais veut progresser sur LinkedIn. Parle à Marie. Seulement à Marie.

## 2. La règle des 80/20 appliquée au contenu

80% de ton contenu doit être de la **valeur pure** (tutoriels, conseils, erreurs à éviter). 20% seulement peut être promotionnel. La plupart des créateurs font l'inverse — et se demandent pourquoi leur audience ne grandit pas.

**Exemple concret :** Au lieu de poster "Achète ma formation", poste "Les 5 erreurs que j'ai faites avant de gagner mon premier euro en ligne". L'un repousse, l'autre attire.

## 3. La cohérence bat le talent

Publier un chef-d'œuvre une fois par mois ne vaut pas publier quelque chose de correct chaque semaine. L'algorithme récompense la **régularité**. Ton audience récompense la **fiabilité**.

**Plan d'action sur 90 jours :**
- Semaines 1-4 : définir ta niche et publier 3x/semaine
- Semaines 5-8 : analyser tes 3 meilleurs posts et doubler la mise
- Semaines 9-12 : collaborer avec 2 créateurs de ta niche

## Conclusion

Construire une audience n'est pas une question de chance ou de talent. C'est une question de **méthode et de persévérance**. Commence aujourd'hui avec ces 3 principes, et reviens dans 90 jours me dire où tu en es.

👉 **Prêt à passer à l'action ?** Télécharge le kit de contenu complet avec ReelToPost.
""")

    with tab_linkedin:
        st.markdown("""
---
## 📌 POST 1 — STORYTELLING

Il y a 6 mois, je publiais dans le vide.

0 commentaires. 3 likes (dont ma mère et deux bots).

J'avais pourtant suivi tous les "tips de croissance" : hashtags, heures de publication optimales, threads viraux…

Rien.

Ce qui a tout changé ? J'ai arrêté d'écrire pour "les gens" et j'ai commencé à écrire pour **une seule personne**.

Sophie, 31 ans, manager épuisée qui veut créer du contenu mais ne sait pas par où commencer.

Depuis que j'écris pour Sophie — et seulement pour elle — mon engagement a triplé.

Parce que Sophie se reconnaît. Elle partage. Et ses connexions ressemblent à Sophie.

La leçon ? **La précision bat la portée.**

Et toi, tu écris pour qui ?

#PersonalBranding #ContentStrategy #LinkedIn #Croissance #Marketing

---
## 📌 POST 2 — LISTE

7 erreurs qui tuent ta croissance sur LinkedIn (et comment les éviter) :

1. **Publier sans consistance** → L'algorithme oublie ceux qui disparaissent
2. **Parler de soi à 80%** → Personne ne s'intéresse à toi avant de te connaître
3. **Ignorer les commentaires** → L'engagement appelle l'engagement
4. **Copier les gros comptes** → Ton authenticité est ton avantage compétitif
5. **Négliger le hook** → Tu as 1,5 secondes pour retenir l'attention
6. **Poster sans stratégie** → Chaque post doit servir un objectif précis
7. **Abandonner trop tôt** → La plupart lâchent à 3 semaines du décollage

Lequel te reconnaîs-tu le plus ?

#LinkedIn #GrowthHacking #ContentCreator #Stratégie #Tips

---
## 📌 POST 3 — CONTRARIAN

Opinion impopulaire : **la qualité de ton contenu n'a aucune importance.**

(Attends, ne pars pas encore.)

J'ai vu des posts mal écrits, avec des fautes, sans visuels… exploser à 200 000 vues.

Et des chefs-d'œuvre graphiques mourir à 47 impressions.

Ce qui compte vraiment : **la résonance émotionnelle.**

Est-ce que ton lecteur se dit "c'est EXACTEMENT ce que je vis" en lisant ta première ligne ?

Si oui, il lit. Il like. Il partage.

La perfection sans résonance = silence.
L'imparfait avec résonance = viralité.

Vous êtes d'accord ou pas ?

#ContentMarketing #Authenticité #LinkedIn #PersonalBranding
""")

    with tab_twitter:
        st.markdown("""
---
**[1] CONSEIL ACTIONNABLE**
Ton audience ne grossit pas parce que tu crées pour tout le monde.
Choisis 1 personne. Écris pour elle. Seulement elle.
La précision bat la portée. Toujours.
#Audience #ContentCreator

---
**[2] FAIT SURPRENANT**
97% des créateurs abandonnent avant d'atteindre 1 000 abonnés.
La raison n°1 ? Ils mesurent leurs résultats trop tôt.
La croissance est exponentielle. Pas linéaire.
#Growth #Patience

---
**[3] THREAD STARTER**
J'ai interviewé 50 créateurs qui ont atteint 10k abonnés en moins d'un an.
Voici les 6 choses qu'ils ont TOUS faites 🧵

---
**[4] OPINION FORTE**
Les "heures optimales de publication" sont une distraction.
Ce qui compte : publier régulièrement et répondre à TOUS tes commentaires.
L'algorithme récompense l'engagement, pas le timing.
#ContentStrategy

---
**[5] MYTHE VS RÉALITÉ**
Mythe : il faut des milliers d'abonnés pour monétiser.
Réalité : 500 vrais fans suffisent pour vivre de son contenu.
La taille ne compte pas. La qualité de la relation oui.
#CreatorEconomy

---
**[6] BEFORE/AFTER**
Avant : je publiais 1x/semaine un contenu "parfait" → 0 croissance
Après : je publie 4x/semaine du contenu "assez bien" → +300 abonnés/mois
La régularité bat la perfection. À chaque fois.

---
**[7] QUESTION**
Tu as du mal à trouver des idées de contenu ?
Lis les commentaires sous les posts de tes concurrents.
Tes prochains 30 sujets sont là. Gratuits.
#ContentIdeas #Hack

---
**[8] CITATION**
"Publie ton premier brouillon. Améliore-le demain. Ne l'attends jamais parfait."
— Ce que j'aurais aimé entendre il y a 2 ans.
#Créativité

---
**[9] CONTRARIAN**
Arrête d'essayer de "pirater l'algorithme".
Les créateurs qui durent font une seule chose : ils aident vraiment les gens.
L'algorithme suit l'engagement. L'engagement suit la valeur.
#Authenticité

---
**[10] ACTIONNABLE**
Défi 7 jours : publie quelque chose chaque jour cette semaine.
Pas parfait. Juste honnête.
Reviens me dire ce qui s'est passé.
#Challenge #Audience
""")

    with tab_newsletter:
        st.markdown("""
**OBJET :** Ce que j'aurais aimé savoir avant de créer du contenu 🎯
**PRE-HEADER :** 3 leçons contre-intuitives qui changent tout

---

Salut {prénom} 👋

Je vais être direct avec toi aujourd'hui.

Ça fait maintenant 6 mois que je décortique la croissance des créateurs de contenu — ceux qui passent de 0 à 10 000 abonnés, et ceux qui abandonnent à 200.

Et j'ai trouvé quelque chose d'inattendu.

**Les créateurs qui réussissent ne sont pas les meilleurs.** Ils ne sont pas les plus talentueux, ni ceux qui passent le plus de temps à créer.

Ils font juste 3 choses différemment :

**1/ Ils définissent leur audience avec une précision chirurgicale**
Pas "les entrepreneurs". Mais "les freelances de 25-35 ans qui veulent quitter leur CDI mais ont peur de sauter le pas". Plus c'est précis, plus ça résonne.

**2/ Ils traitent leur contenu comme un produit**
Chaque post a un objectif. Chaque série a une logique. Rien n'est publié au hasard. Ils testent, mesurent, itèrent.

**3/ Ils jouent le long terme dès le premier jour**
Ils ne publient pas pour aller viral. Ils publient pour construire la confiance. Un post à la fois.

La bonne nouvelle ? Ces 3 choses s'apprennent.

À très vite,
**[Ton prénom]**

*P.S. — Si tu veux voir comment ReelToPost peut transformer tes vidéos en ce type de contenu automatiquement, [essaie gratuitement ici →]*
""")

    with tab_resume:
        st.markdown("""
# Résumé Exécutif : Construire une audience de 0 à 10 000 abonnés
**Lecture** : 2 min

---

## 10 Points Clés

1. **Niche précise** — Cibler une personne ultra-spécifique est plus efficace que viser large ; la précision crée la résonance.

2. **Règle 80/20** — 80% de valeur pure, 20% de promotion. Inverser ce ratio tue la croissance.

3. **Régularité > qualité** — Publier correctement 4x/semaine surpasse publier parfaitement 1x/semaine.

4. **Le hook est tout** — Les 1,5 premières secondes décident si le post est lu. Investir sur la première ligne.

5. **Engagement symétrique** — Répondre à chaque commentaire multiplie la portée organique par 2 à 3.

6. **Collaboration ciblée** — S'associer avec 2-3 créateurs de sa niche accélère la croissance de 40%.

7. **Analyse hebdomadaire** — Identifier ses 3 meilleurs posts et "doubler la mise" sur ces formats.

8. **Pas d'algorithme magique** — La valeur génère l'engagement, l'engagement génère la portée.

9. **Plan 90 jours** — Semaines 1-4 : niche + cadence / 5-8 : analyse + optimisation / 9-12 : collaborations.

10. **Persévérance** — 97% abandonnent avant le décollage. La croissance est exponentielle, pas linéaire.

---
## À retenir
> *La croissance d'une audience n'est pas une question de talent mais de méthode : cibler précisément, créer régulièrement, et jouer le long terme.*
""")

    with tab_notes:
        st.markdown("""
# Notes Clés — Construire une audience de 0 à 10 000 abonnés

---

## Citations & Moments Importants

### L'importance de la niche
> "Si ton contenu convient à tout le monde, il n'est parfait pour personne."
[02:14] — *Introduction au concept d'avatar client ultra-précis*

### Le chiffre qui surprend
> "97% des créateurs abandonnent avant d'atteindre leurs 1 000 premiers abonnés."
[04:38] — *Explication de la courbe de croissance exponentielle vs perception linéaire*

### La règle des 80/20
> "Quatre posts de valeur pour un post promotionnel. Pas l'inverse."
[06:55] — *Démonstration avec exemples de posts à fort vs faible engagement*

### La régularité avant tout
> "Un post correct publié chaque jour vaut mieux qu'un chef-d'œuvre publié chaque mois."
[09:12] — *Comparaison de deux stratégies sur 90 jours*

### L'engagement comme levier
> "Répondre à chaque commentaire dans les 30 premières minutes triple la portée."
[11:30] — *Mécanisme de l'algorithme LinkedIn expliqué simplement*

### La collaboration stratégique
> "Deux créateurs qui se taguent mutuellement une fois par semaine croissent 40% plus vite."
[13:47] — *Cas pratique avec résultats chiffrés*

### Le plan 90 jours
> "Pas besoin d'être parfait dès le départ. Il suffit d'être présent et d'améliorer en continu."
[15:20] — *Présentation du framework en 3 phases*

### La conclusion
> "La question n'est pas 'Est-ce que je suis doué ?' mais 'Est-ce que je suis régulier ?'"
[17:05] — *Message final adressé aux débutants*

---

## Concepts & Termes Clés

| Terme | Définition brève |
|-------|-----------------|
| Avatar client | Persona ultra-précis représentant le lecteur idéal |
| Règle 80/20 | 80% valeur, 20% promo dans la stratégie de contenu |
| Hook | Première phrase/ligne conçue pour stopper le scroll |
| Portée organique | Visibilité obtenue sans publicité payante |
| Croissance exponentielle | Croissance lente au début, puis accélération brutale |
| Créator Economy | Écosystème économique autour des créateurs de contenu |
""")

    # CTA final
    st.divider()
    st.markdown(f"""
<div style="text-align:center;padding:2rem 0;">
    <div style="font-size:1.5rem;font-weight:700;color:#e2e8f0;margin-bottom:0.5rem;">
        {t("hiw_cta_title")}
    </div>
    <div style="color:#94a3b8;margin-bottom:1.5rem;">
        {t("hiw_cta_sub")}
    </div>
</div>
""", unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        if st.button(t("hiw_cta_btn"), type="primary", use_container_width=True):
            st.session_state.page = "main"
            st.rerun()


# ---------------------------------------------------------------------------
# Routeur
# ---------------------------------------------------------------------------
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "").lower()
user = st.session_state.get("user")

if st.session_state.get("is_admin") and user and user["email"] == ADMIN_EMAIL:
    page_admin()
elif st.session_state.page == "policy":
    page_policy()
elif st.session_state.page == "login":
    page_login()
elif st.session_state.page == "how_it_works":
    page_how_it_works()
else:
    page_main()
