"""
Google OAuth 2.0 — helpers pour ReelToPost
"""

import os
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


def _client_config() -> dict:
    return {
        "web": {
            "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
            "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET", ""),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:8501")],
        }
    }


def get_auth_url() -> tuple[str, object]:
    """Retourne (auth_url, flow) — le flow doit être conservé pour exchange_code."""
    os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

    flow = Flow.from_client_config(
        _client_config(),
        scopes=SCOPES,
        redirect_uri=os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:8501"),
    )
    auth_url, _ = flow.authorization_url(
        prompt="select_account",
        access_type="offline",
    )
    return auth_url, flow


def exchange_code(code: str, flow) -> tuple[str, str, str]:
    """
    Échange le code OAuth contre les infos utilisateur.
    Retourne (email, name, picture_url).
    Le flow doit être celui retourné par get_auth_url().
    """
    os.environ.setdefault("OAUTHLIB_INSECURE_TRANSPORT", "1")

    flow.fetch_token(code=code)
    credentials = flow.credentials

    id_info = id_token.verify_oauth2_token(
        credentials.id_token,
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
