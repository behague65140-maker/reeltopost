"""
Serveur webhook Stripe — FastAPI (port 8502)
Ecoute les evenements Stripe et met a jour les plans utilisateurs.
"""

import os
import stripe
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from database import get_or_create_user, set_plan, init_db

load_dotenv()
init_db()

app = FastAPI(title="Content Kit — Webhook Stripe")

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

# Correspondance price_id -> plan interne
PRICE_TO_PLAN: dict[str, str] = {
    os.environ.get("STRIPE_PRICE_PRO", ""):    "pro",
    os.environ.get("STRIPE_PRICE_AGENCY", ""): "agency",
}


def _email_from_session(session: dict) -> str | None:
    return (
        session.get("customer_email")
        or (session.get("customer_details") or {}).get("email")
    )


def _plan_from_session(session: dict) -> str:
    """Retrouve le plan via les line items ou les metadata."""
    # 1. Metadata explicite (recommande)
    if session.get("metadata", {}).get("plan"):
        return session["metadata"]["plan"]
    # 2. Price ID dans les line items
    items = (session.get("line_items") or {}).get("data", [])
    for item in items:
        price_id = (item.get("price") or {}).get("id", "")
        if price_id in PRICE_TO_PLAN:
            return PRICE_TO_PLAN[price_id]
    return "pro"  # fallback


@app.get("/")
def health():
    return {"status": "ok", "service": "Content Kit Webhook"}


@app.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("stripe-signature", "")

    # Verification de la signature Stripe
    if WEBHOOK_SECRET:
        try:
            event = stripe.Webhook.construct_event(payload, sig, WEBHOOK_SECRET)
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")
    else:
        # Mode dev sans secret (ne pas utiliser en production)
        import json
        event = json.loads(payload)

    etype = event["type"]
    data  = event["data"]["object"]

    # --- Paiement reussi (one-time ou premiere echeance) ---
    if etype == "checkout.session.completed":
        email = _email_from_session(data)
        plan  = _plan_from_session(data)
        if email:
            get_or_create_user(email)
            set_plan(email, plan)
            print(f"[webhook] UPGRADE {email} -> {plan}")

    # --- Renouvellement d'abonnement ---
    elif etype == "invoice.payment_succeeded":
        sub_id = data.get("subscription")
        if sub_id:
            sub = stripe.Subscription.retrieve(sub_id)
            customer = stripe.Customer.retrieve(sub["customer"])
            email = customer.get("email")
            price_id = sub["items"]["data"][0]["price"]["id"]
            plan = PRICE_TO_PLAN.get(price_id, "pro")
            if email:
                set_plan(email, plan)
                print(f"[webhook] RENOUVELLEMENT {email} -> {plan}")

    # --- Abonnement annule ou paiement echoue ---
    elif etype in ("customer.subscription.deleted", "invoice.payment_failed"):
        customer_id = data.get("customer")
        if customer_id:
            customer = stripe.Customer.retrieve(customer_id)
            email = customer.get("email")
            if email:
                set_plan(email, "free")
                print(f"[webhook] DOWNGRADE {email} -> free")

    return {"status": "ok"}
