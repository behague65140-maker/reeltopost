"""
Google OAuth 2.0 — helpers pour ReelToPost (sans PKCE)
"""

import os
import urllib.parse
import requests as http_requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


def get_auth_url() -> tuple[str, object]:
    """Retourne (auth_url, None) — pas de flow à conserver (pas de PKCE)."""
    params = {
        "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
        "redirect_uri": os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:8501"),
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "select_account",
    }
    auth_url = "https://accounts.google.com/o/oauth2/auth?" + urllib.parse.urlencode(params)
    return auth_url, None


def exchange_code(code: str, flow=None) -> tuple[str, str, str]:
    """
    Échange le code OAuth contre les infos utilisateur (sans PKCE).
    Retourne (email, name, picture_url).
    """
    token_resp = http_requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": code,
            "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
            "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET", ""),
            "redirect_uri": os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:8501"),
            "grant_type": "authorization_code",
        },
    )
    token_resp.raise_for_status()
    token_data = token_resp.json()

    id_info = id_token.verify_oauth2_token(
        token_data["id_token"],
        google_requests.Request(),
        os.environ.get("GOOGLE_CLIENT_ID", ""),
        clock_skew_in_seconds=10,
    )

    email = id_info.get("email", "")
    name = id_info.get("name", email.split("@")[0])
    picture = id_info.get("picture", "")
    return email, name, picture


def google_configured() -> bool:
    """Vérifie que les clés Google sont bien renseignées."""
    return bool(
        os.environ.get("GOOGLE_CLIENT_ID")
        and os.environ.get("GOOGLE_CLIENT_SECRET")
    )
