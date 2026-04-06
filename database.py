"""
Gestion des utilisateurs et de l'usage — SQLite
"""

import sqlite3
from pathlib import Path
from datetime import date

DB_PATH = Path(__file__).parent / ".claude" / "users.db"

PLANS = {
    "free": {
        "label": "Gratuit",
        "price": 0,
        "kits_per_month": 3,
        "stripe_link": None,
    },
    "pro": {
        "label": "Pro",
        "price": 19,
        "kits_per_month": 50,
        "stripe_link": "https://buy.stripe.com/REMPLACE_PRO",
    },
    "agency": {
        "label": "Agence",
        "price": 79,
        "kits_per_month": None,          # None = illimité
        "stripe_link": "https://buy.stripe.com/REMPLACE_AGENCE",
    },
}


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email            TEXT PRIMARY KEY,
                plan             TEXT    DEFAULT 'free',
                kits_used        INTEGER DEFAULT 0,
                billing_month    TEXT    DEFAULT '',
                created_at       TEXT    DEFAULT CURRENT_TIMESTAMP,
                name             TEXT    DEFAULT '',
                picture          TEXT    DEFAULT '',
                login_provider   TEXT    DEFAULT 'email',
                last_login       TEXT    DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Migration : ajoute les colonnes si la table existait déjà
        existing = {r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()}
        for col, definition in [
            ("name",           "TEXT DEFAULT ''"),
            ("picture",        "TEXT DEFAULT ''"),
            ("login_provider", "TEXT DEFAULT 'email'"),
            ("last_login",     "TEXT DEFAULT ''"),
        ]:
            if col not in existing:
                conn.execute(f"ALTER TABLE users ADD COLUMN {col} {definition}")


def _current_month() -> str:
    return date.today().strftime("%Y-%m")


def get_or_create_user(
    email: str,
    name: str = "",
    picture: str = "",
    provider: str = "email",
) -> dict:
    email = email.lower().strip()
    month = _current_month()
    with _conn() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()

        if row is None:
            conn.execute(
                "INSERT INTO users "
                "(email, plan, kits_used, billing_month, name, picture, login_provider, last_login) "
                "VALUES (?, 'free', 0, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
                (email, month, name, picture, provider),
            )
            return {
                "email": email, "plan": "free", "kits_used": 0,
                "name": name, "picture": picture, "login_provider": provider,
            }

        user = dict(row)
        # Mise à jour des infos de profil + last_login à chaque connexion
        updates = {"last_login": "CURRENT_TIMESTAMP"}
        params = []
        if name:
            updates["name"] = "?"
            params.append(name)
        if picture:
            updates["picture"] = "?"
            params.append(picture)
        if provider != "email":
            updates["login_provider"] = "?"
            params.append(provider)

        set_clause = ", ".join(
            f"{k} = {v}" for k, v in updates.items()
        )
        conn.execute(
            f"UPDATE users SET {set_clause} WHERE email = ?",
            params + [email],
        )

        # Réinitialise le compteur chaque nouveau mois
        if user["billing_month"] != month:
            conn.execute(
                "UPDATE users SET kits_used = 0, billing_month = ? WHERE email = ?",
                (month, email),
            )
            user["kits_used"] = 0
        return user


def increment_usage(email: str) -> None:
    with _conn() as conn:
        conn.execute(
            "UPDATE users SET kits_used = kits_used + 1 WHERE email = ?",
            (email.lower(),),
        )


def set_plan(email: str, plan: str) -> None:
    """Appelé par le webhook Stripe ou manuellement."""
    with _conn() as conn:
        conn.execute(
            "UPDATE users SET plan = ? WHERE email = ?",
            (plan, email.lower()),
        )


def list_all_users() -> list[dict]:
    """Retourne tous les utilisateurs — usage admin."""
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM users ORDER BY created_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def delete_user(email: str) -> None:
    with _conn() as conn:
        conn.execute("DELETE FROM users WHERE email = ?", (email.lower(),))


def reset_usage(email: str) -> None:
    with _conn() as conn:
        conn.execute(
            "UPDATE users SET kits_used = 0 WHERE email = ?", (email.lower(),)
        )


def export_emails_csv() -> str:
    """Exporte tous les emails inscrits en CSV."""
    import csv, io
    with _conn() as conn:
        rows = conn.execute(
            "SELECT email, name, plan, login_provider, kits_used, created_at, last_login "
            "FROM users ORDER BY created_at DESC"
        ).fetchall()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["Email", "Nom", "Plan", "Méthode", "Kits utilisés", "Inscrit le", "Dernière connexion"])
    for r in rows:
        writer.writerow(list(r))
    return buf.getvalue()


def kits_remaining(user: dict) -> int | None:
    """Retourne le nombre de kits restants, ou None si illimité."""
    plan = PLANS[user["plan"]]
    limit = plan["kits_per_month"]
    if limit is None:
        return None
    return max(0, limit - user["kits_used"])
