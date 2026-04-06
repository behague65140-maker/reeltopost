"""
Traductions de l'interface — ReelToPost
"""

TRANSLATIONS = {
    "fr": {
        "lang_name": "Français",
        "flag": "🇫🇷",
        # Sidebar
        "login_btn": "🔐 Se connecter avec Google",
        "logout_btn": "Se déconnecter",
        "upgrade_btn": "⬆️ Upgrader mon plan",
        "admin_btn": "🛠️ Admin",
        "content_to_generate": "📋 Contenu à générer",
        "output_language": "🌍 Langue du contenu généré",
        "site_language": "🗣️ Langue du site",
        "kits_unlimited": "∞ kits illimités",
        "kits_remaining_1": "{n} kit restant ce mois",
        "kits_remaining_n": "{n} kits restants ce mois",
        "plan_label": "Plan : {plan}",
        # Navigation commune
        "back_to_app": "← Retour à l'application",
        # Page principale
        "hero_badge": "✨ Propulsé par Claude AI",
        "hero_title": "Transforme tes vidéos<br>en contenu viral",
        "hero_sub": "Colle l'URL d'une vidéo YouTube et génère en quelques secondes un blog, LinkedIn, Twitter, newsletter et plus encore.",
        "url_label": "🔗 URL de la vidéo YouTube",
        "url_placeholder": "https://www.youtube.com/watch?v=...",
        "generate_btn": "🚀 Générer le kit de contenu",
        "login_hint": "👈 Connecte-toi avec Google pour générer ton kit.",
        "quota_reached": "Quota mensuel atteint. Passe à un plan supérieur pour continuer.",
        "upgrade_pro": "🚀 Passer au Pro (19€/mois)",
        "upgrade_agency": "🏢 Passer Agence (79€/mois)",
        "getting_transcript": "📝 Récupération de la transcription…",
        "transcript_ok": "✅ Transcription récupérée ({n} mots)",
        "transcript_disabled": "❌ Sous-titres désactivés",
        "transcript_not_found": "❌ Aucune transcription trouvée",
        "transcript_ip_blocked": "❌ IP bloquée par YouTube",
        "transcript_ip_msg": "Lance l'app depuis ton réseau personnel.",
        "transcript_error": "❌ Erreur : {e}",
        "select_content": "Sélectionnez au moins un type de contenu.",
        "kit_generated": "📦 Kit de contenu généré",
        "download_zip": "📦 Télécharger tout (ZIP)",
        "zip_pro_only": "💡 L'export ZIP est disponible à partir du plan **Pro** (19€/mois).",
        "upgrade_pro_link": "Passer au Pro →",
        "how_it_works": "💡 Comment ça marche ?",
        "policy": "📜 Politique d'utilisation",
        "see_plans": "💎 Voir les plans tarifaires",
        "enter_url": "Veuillez entrer une URL YouTube.",
        "invalid_url": "URL YouTube invalide.",
        "api_error": "Erreur API : {e}",
        # Login
        "login_sub": "Transforme tes vidéos YouTube en contenu viral",
        "login_google": "Continuer avec Google",
        "login_google_missing": "Google OAuth non configuré. Renseigne `GOOGLE_CLIENT_ID` et `GOOGLE_CLIENT_SECRET` dans le `.env`.",
        "login_feat_free": "✅ Gratuit pour commencer",
        "login_feat_secure": "🔒 Connexion sécurisée",
        "login_feat_instant": "⚡ Accès immédiat",
        # Plans
        "plan_free": "Gratuit",
        "plan_pro": "Pro",
        "plan_agency": "Agence",
        "per_month": "/ mois",
        "forever": "pour toujours",
        "unlimited_kits": "Kits illimités",
        # Comment ça marche
        "hiw_title": "Comment ça marche ?",
        "hiw_sub": "3 étapes, quelques secondes, un kit complet.",
        "hiw_step1_label": "Colle l'URL",
        "hiw_step1_desc": "N'importe quelle vidéo YouTube avec sous-titres",
        "hiw_step2_label": "L'IA analyse",
        "hiw_step2_desc": "Claude extrait la transcription et génère le contenu",
        "hiw_step3_label": "Tu télécharges",
        "hiw_step3_desc": "6 formats prêts à publier, en Markdown ou ZIP",
        "hiw_demo_label": "🎬 Vidéo source (exemple)",
        "hiw_demo_note": "Ce contenu ci-dessous a été **entièrement généré par ReelToPost** à partir de cette vidéo.",
        "hiw_cta_title": "Prêt à générer ton propre kit ?",
        "hiw_cta_sub": "Connecte-toi et colle l'URL de ta vidéo. C'est tout.",
        "hiw_cta_btn": "🚀 Essayer maintenant — c'est gratuit",
        # Politique d'utilisation
        "policy_title": "📜 Politique d'utilisation",
        "policy_updated": "Dernière mise à jour : avril 2025",
        "policy_body": """
## 1. Objet du service

ReelToPost est un outil en ligne qui génère automatiquement du contenu marketing (articles de blog, posts LinkedIn, fils Twitter, newsletters, résumés, notes clés) à partir de la transcription d'une vidéo YouTube, en utilisant l'intelligence artificielle Claude d'Anthropic.

---

## 2. Conditions d'accès

- L'accès au service nécessite un compte Google valide.
- Tu es responsable de l'exactitude des informations fournies.

---

## 3. Utilisation acceptable

En utilisant ce service, tu t'engages à :

- **Ne soumettre que des vidéos YouTube dont tu détiens les droits** ou pour lesquelles tu disposes d'une autorisation de traitement du contenu.
- Ne pas utiliser le service pour générer du contenu trompeur, diffamatoire, haineux, illégal ou violant les droits de tiers.
- Ne pas tenter de contourner les limites de quota par la création de multiples comptes.
- Ne pas automatiser les requêtes de manière abusive (scraping, bots).

---

## 4. Contenu généré par IA

- Le contenu produit est généré par l'IA Claude d'Anthropic et peut contenir des imprécisions.
- **Tu es seul responsable** de la vérification, de la correction et de l'utilisation du contenu avant toute publication.
- Le service ne garantit pas l'exactitude, l'exhaustivité ou l'adéquation du contenu généré à un usage particulier.

---

## 5. Propriété intellectuelle

- Le contenu des vidéos YouTube traitées reste la propriété de leurs auteurs respectifs.
- Le contenu généré à partir de ta vidéo t'appartient. Tu peux l'utiliser, le modifier et le publier librement.
- Tu n'es pas autorisé à revendre l'accès au service ou à proposer des services concurrents basés sur cette plateforme.

---

## 6. Données personnelles

- Nous collectons uniquement ton **adresse email**, ton **nom** (via Google) et le **nombre de kits générés** ce mois-ci.
- Ces données sont stockées de façon sécurisée et ne sont jamais revendues ni partagées avec des tiers.
- Tu peux demander la suppression de ton compte à tout moment en contactant l'administrateur.

---

## 7. Limites de responsabilité

Le service est fourni **"en l'état"**, sans garantie d'aucune sorte. Nous ne pouvons être tenus responsables :

- Des interruptions de service (maintenance, pannes API).
- Des blocages d'IP par YouTube sur les transcriptions.
- D'une perte de données liée à un redéploiement (base de données locale).
- De tout préjudice indirect lié à l'utilisation du contenu généré.

---

## 8. Modifications

Nous nous réservons le droit de modifier cette politique à tout moment. Les changements significatifs seront communiqués via l'interface de l'application.

---

## 9. Contact

Pour toute question relative à cette politique ou à la gestion de ton compte, contacte l'administrateur depuis l'interface admin ou par email.
""",
        # Admin
        "admin_title": "🛠️ Panneau Admin",
        "admin_caption": "Gestion des utilisateurs et des abonnements.",
        "admin_total": "Utilisateurs total",
        "admin_paying": "Abonnés payants",
        "admin_conversion": "Taux conversion",
        "admin_google": "Via Google",
        "admin_export_csv": "📥 Exporter CSV",
        "admin_search": "Rechercher un email",
        "admin_users_count": "{n} utilisateur(s)",
        "admin_apply": "Appliquer",
        "admin_plan_updated": "Plan mis à jour : {plan}",
        "admin_reset_quota": "Reset quota",
        "admin_quota_reset": "Quota réinitialisé.",
        "admin_delete": "🗑️ Supprimer",
        "admin_deleted": "{email} supprimé.",
        "admin_back": "← Retour à l'app",
    },
    "en": {
        "lang_name": "English",
        "flag": "🇬🇧",
        "login_btn": "🔐 Sign in with Google",
        "logout_btn": "Sign out",
        "upgrade_btn": "⬆️ Upgrade plan",
        "admin_btn": "🛠️ Admin",
        "content_to_generate": "📋 Content to generate",
        "output_language": "🌍 Content language",
        "site_language": "🗣️ Site language",
        "kits_unlimited": "∞ unlimited kits",
        "kits_remaining_1": "{n} kit left this month",
        "kits_remaining_n": "{n} kits left this month",
        "plan_label": "Plan: {plan}",
        "back_to_app": "← Back to app",
        "hero_badge": "✨ Powered by Claude AI",
        "hero_title": "Turn your videos<br>into viral content",
        "hero_sub": "Paste a YouTube URL and generate a blog, LinkedIn post, Twitter thread, newsletter and more in seconds.",
        "url_label": "🔗 YouTube video URL",
        "url_placeholder": "https://www.youtube.com/watch?v=...",
        "generate_btn": "🚀 Generate content kit",
        "login_hint": "👈 Sign in with Google to generate your kit.",
        "quota_reached": "Monthly quota reached. Upgrade to continue.",
        "upgrade_pro": "🚀 Go Pro (€19/month)",
        "upgrade_agency": "🏢 Go Agency (€79/month)",
        "getting_transcript": "📝 Fetching transcript…",
        "transcript_ok": "✅ Transcript retrieved ({n} words)",
        "transcript_disabled": "❌ Subtitles disabled",
        "transcript_not_found": "❌ No transcript found",
        "transcript_ip_blocked": "❌ IP blocked by YouTube",
        "transcript_ip_msg": "Run the app from your personal network.",
        "transcript_error": "❌ Error: {e}",
        "select_content": "Please select at least one content type.",
        "kit_generated": "📦 Generated content kit",
        "download_zip": "📦 Download all (ZIP)",
        "zip_pro_only": "💡 ZIP export is available on the **Pro** plan (€19/month).",
        "upgrade_pro_link": "Go Pro →",
        "how_it_works": "💡 How it works?",
        "policy": "📜 Usage policy",
        "see_plans": "💎 See pricing plans",
        "enter_url": "Please enter a YouTube URL.",
        "invalid_url": "Invalid YouTube URL.",
        "api_error": "API error: {e}",
        "login_sub": "Turn your YouTube videos into viral content",
        "login_google": "Continue with Google",
        "login_google_missing": "Google OAuth not configured. Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`.",
        "login_feat_free": "✅ Free to start",
        "login_feat_secure": "🔒 Secure login",
        "login_feat_instant": "⚡ Instant access",
        "plan_free": "Free",
        "plan_pro": "Pro",
        "plan_agency": "Agency",
        "per_month": "/ month",
        "forever": "forever",
        "unlimited_kits": "Unlimited kits",
        "hiw_title": "How does it work?",
        "hiw_sub": "3 steps, a few seconds, a complete kit.",
        "hiw_step1_label": "Paste the URL",
        "hiw_step1_desc": "Any YouTube video with subtitles",
        "hiw_step2_label": "AI analyses",
        "hiw_step2_desc": "Claude extracts the transcript and generates content",
        "hiw_step3_label": "You download",
        "hiw_step3_desc": "6 ready-to-publish formats, in Markdown or ZIP",
        "hiw_demo_label": "🎬 Source video (example)",
        "hiw_demo_note": "The content below was **entirely generated by ReelToPost** from this video.",
        "hiw_cta_title": "Ready to generate your own kit?",
        "hiw_cta_sub": "Sign in and paste your video URL. That's it.",
        "hiw_cta_btn": "🚀 Try it now — it's free",
        "policy_title": "📜 Usage Policy",
        "policy_updated": "Last updated: April 2025",
        "policy_body": """
## 1. About the service

ReelToPost is an online tool that automatically generates marketing content (blog articles, LinkedIn posts, Twitter threads, newsletters, summaries, key notes) from a YouTube video transcript, using Anthropic's Claude AI.

---

## 2. Access conditions

- Access to the service requires a valid Google account.
- You are responsible for the accuracy of the information provided.

---

## 3. Acceptable use

By using this service, you agree to:

- **Only submit YouTube videos you own or have permission** to process.
- Not use the service to generate misleading, defamatory, hateful, illegal content or content that violates third-party rights.
- Not attempt to circumvent quota limits by creating multiple accounts.
- Not automate requests abusively (scraping, bots).

---

## 4. AI-generated content

- Content is generated by Anthropic's Claude AI and may contain inaccuracies.
- **You are solely responsible** for verifying, correcting and using content before publication.
- The service does not guarantee the accuracy, completeness or suitability of generated content for any particular purpose.

---

## 5. Intellectual property

- The content of processed YouTube videos remains the property of their respective authors.
- Content generated from your video belongs to you. You may use, modify and publish it freely.
- You are not authorised to resell access to the service or to offer competing services based on this platform.

---

## 6. Personal data

- We only collect your **email address**, your **name** (via Google) and the **number of kits generated** this month.
- This data is stored securely and is never sold or shared with third parties.
- You can request deletion of your account at any time by contacting the administrator.

---

## 7. Limitation of liability

The service is provided **"as is"**, without warranty of any kind. We cannot be held liable for:

- Service interruptions (maintenance, API outages).
- IP blocks by YouTube on transcriptions.
- Data loss related to redeployment (local database).
- Any indirect damage related to the use of generated content.

---

## 8. Changes

We reserve the right to modify this policy at any time. Significant changes will be communicated via the application interface.

---

## 9. Contact

For any questions regarding this policy or account management, contact the administrator from the admin interface or by email.
""",
        "admin_title": "🛠️ Admin Panel",
        "admin_caption": "User and subscription management.",
        "admin_total": "Total users",
        "admin_paying": "Paying subscribers",
        "admin_conversion": "Conversion rate",
        "admin_google": "Via Google",
        "admin_export_csv": "📥 Export CSV",
        "admin_search": "Search by email",
        "admin_users_count": "{n} user(s)",
        "admin_apply": "Apply",
        "admin_plan_updated": "Plan updated: {plan}",
        "admin_reset_quota": "Reset quota",
        "admin_quota_reset": "Quota reset.",
        "admin_delete": "🗑️ Delete",
        "admin_deleted": "{email} deleted.",
        "admin_back": "← Back to app",
    },
    "es": {
        "lang_name": "Español",
        "flag": "🇪🇸",
        "login_btn": "🔐 Iniciar sesión con Google",
        "logout_btn": "Cerrar sesión",
        "upgrade_btn": "⬆️ Mejorar plan",
        "admin_btn": "🛠️ Admin",
        "content_to_generate": "📋 Contenido a generar",
        "output_language": "🌍 Idioma del contenido",
        "site_language": "🗣️ Idioma del sitio",
        "kits_unlimited": "∞ kits ilimitados",
        "kits_remaining_1": "{n} kit restante este mes",
        "kits_remaining_n": "{n} kits restantes este mes",
        "plan_label": "Plan: {plan}",
        "back_to_app": "← Volver a la aplicación",
        "hero_badge": "✨ Impulsado por Claude AI",
        "hero_title": "Convierte tus vídeos<br>en contenido viral",
        "hero_sub": "Pega la URL de un vídeo de YouTube y genera un blog, LinkedIn, Twitter, newsletter y más en segundos.",
        "url_label": "🔗 URL del vídeo de YouTube",
        "url_placeholder": "https://www.youtube.com/watch?v=...",
        "generate_btn": "🚀 Generar kit de contenido",
        "login_hint": "👈 Inicia sesión con Google para generar tu kit.",
        "quota_reached": "Cuota mensual alcanzada. Mejora tu plan para continuar.",
        "upgrade_pro": "🚀 Ir al Pro (19€/mes)",
        "upgrade_agency": "🏢 Ir a Agencia (79€/mes)",
        "getting_transcript": "📝 Obteniendo transcripción…",
        "transcript_ok": "✅ Transcripción obtenida ({n} palabras)",
        "transcript_disabled": "❌ Subtítulos desactivados",
        "transcript_not_found": "❌ No se encontró transcripción",
        "transcript_ip_blocked": "❌ IP bloqueada por YouTube",
        "transcript_ip_msg": "Ejecuta la app desde tu red personal.",
        "transcript_error": "❌ Error: {e}",
        "select_content": "Selecciona al menos un tipo de contenido.",
        "kit_generated": "📦 Kit de contenido generado",
        "download_zip": "📦 Descargar todo (ZIP)",
        "zip_pro_only": "💡 La exportación ZIP está disponible en el plan **Pro** (19€/mes).",
        "upgrade_pro_link": "Ir al Pro →",
        "how_it_works": "💡 ¿Cómo funciona?",
        "policy": "📜 Política de uso",
        "see_plans": "💎 Ver planes",
        "enter_url": "Por favor introduce una URL de YouTube.",
        "invalid_url": "URL de YouTube no válida.",
        "api_error": "Error de API: {e}",
        "login_sub": "Convierte tus vídeos de YouTube en contenido viral",
        "login_google": "Continuar con Google",
        "login_google_missing": "Google OAuth no configurado. Configura `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET` en `.env`.",
        "login_feat_free": "✅ Gratis para empezar",
        "login_feat_secure": "🔒 Conexión segura",
        "login_feat_instant": "⚡ Acceso inmediato",
        "plan_free": "Gratis",
        "plan_pro": "Pro",
        "plan_agency": "Agencia",
        "per_month": "/ mes",
        "forever": "para siempre",
        "unlimited_kits": "Kits ilimitados",
        "hiw_title": "¿Cómo funciona?",
        "hiw_sub": "3 pasos, unos segundos, un kit completo.",
        "hiw_step1_label": "Pega la URL",
        "hiw_step1_desc": "Cualquier vídeo de YouTube con subtítulos",
        "hiw_step2_label": "La IA analiza",
        "hiw_step2_desc": "Claude extrae la transcripción y genera el contenido",
        "hiw_step3_label": "Descargas",
        "hiw_step3_desc": "6 formatos listos para publicar, en Markdown o ZIP",
        "hiw_demo_label": "🎬 Vídeo fuente (ejemplo)",
        "hiw_demo_note": "El contenido de abajo fue **generado íntegramente por ReelToPost** a partir de este vídeo.",
        "hiw_cta_title": "¿Listo para generar tu propio kit?",
        "hiw_cta_sub": "Inicia sesión y pega la URL de tu vídeo. Eso es todo.",
        "hiw_cta_btn": "🚀 Probar ahora — es gratis",
        "policy_title": "📜 Política de uso",
        "policy_updated": "Última actualización: abril 2025",
        "policy_body": """
## 1. Objeto del servicio

ReelToPost es una herramienta en línea que genera automáticamente contenido de marketing (artículos de blog, publicaciones de LinkedIn, hilos de Twitter, newsletters, resúmenes, notas clave) a partir de la transcripción de un vídeo de YouTube, utilizando la IA Claude de Anthropic.

---

## 2. Condiciones de acceso

- El acceso al servicio requiere una cuenta de Google válida.
- Eres responsable de la exactitud de la información proporcionada.

---

## 3. Uso aceptable

Al utilizar este servicio, te comprometes a:

- **Solo enviar vídeos de YouTube de los que seas propietario** o para los que tengas permiso de procesamiento.
- No utilizar el servicio para generar contenido engañoso, difamatorio, odioso, ilegal o que viole derechos de terceros.
- No intentar eludir los límites de cuota creando múltiples cuentas.
- No automatizar solicitudes de forma abusiva (scraping, bots).

---

## 4. Contenido generado por IA

- El contenido es generado por la IA Claude de Anthropic y puede contener inexactitudes.
- **Eres el único responsable** de verificar, corregir y utilizar el contenido antes de publicarlo.
- El servicio no garantiza la exactitud, integridad o idoneidad del contenido generado para ningún propósito particular.

---

## 5. Propiedad intelectual

- El contenido de los vídeos de YouTube procesados sigue siendo propiedad de sus autores respectivos.
- El contenido generado a partir de tu vídeo te pertenece. Puedes usarlo, modificarlo y publicarlo libremente.
- No estás autorizado a revender el acceso al servicio ni a ofrecer servicios competidores basados en esta plataforma.

---

## 6. Datos personales

- Solo recopilamos tu **dirección de correo electrónico**, tu **nombre** (a través de Google) y el **número de kits generados** este mes.
- Estos datos se almacenan de forma segura y nunca se venden ni comparten con terceros.
- Puedes solicitar la eliminación de tu cuenta en cualquier momento contactando al administrador.

---

## 7. Limitación de responsabilidad

El servicio se proporciona **"tal cual"**, sin garantía de ningún tipo. No podemos ser responsables de:

- Interrupciones del servicio (mantenimiento, fallos de la API).
- Bloqueos de IP por YouTube en las transcripciones.
- Pérdida de datos relacionada con el redespliegue (base de datos local).
- Cualquier daño indirecto relacionado con el uso del contenido generado.

---

## 8. Modificaciones

Nos reservamos el derecho de modificar esta política en cualquier momento. Los cambios significativos se comunicarán a través de la interfaz de la aplicación.

---

## 9. Contacto

Para cualquier pregunta relacionada con esta política o la gestión de tu cuenta, contacta al administrador desde la interfaz de administración o por correo electrónico.
""",
        "admin_title": "🛠️ Panel de administración",
        "admin_caption": "Gestión de usuarios y suscripciones.",
        "admin_total": "Usuarios totales",
        "admin_paying": "Suscriptores de pago",
        "admin_conversion": "Tasa de conversión",
        "admin_google": "Vía Google",
        "admin_export_csv": "📥 Exportar CSV",
        "admin_search": "Buscar por email",
        "admin_users_count": "{n} usuario(s)",
        "admin_apply": "Aplicar",
        "admin_plan_updated": "Plan actualizado: {plan}",
        "admin_reset_quota": "Reiniciar cuota",
        "admin_quota_reset": "Cuota reiniciada.",
        "admin_delete": "🗑️ Eliminar",
        "admin_deleted": "{email} eliminado.",
        "admin_back": "← Volver a la app",
    },
}

SITE_LANGUAGES = {code: f"{v['flag']} {v['lang_name']}" for code, v in TRANSLATIONS.items()}


def t(key: str, **kwargs) -> str:
    """Retourne la traduction de la clé pour la langue active."""
    import streamlit as st
    lang = st.session_state.get("site_lang", "fr")
    text = TRANSLATIONS.get(lang, TRANSLATIONS["fr"]).get(key, TRANSLATIONS["fr"].get(key, key))
    return text.format(**kwargs) if kwargs else text
