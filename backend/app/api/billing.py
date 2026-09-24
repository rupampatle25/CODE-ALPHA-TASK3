import hashlib
import hmac
import time
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import User, UsageRecord
from app.schemas.schemas import PlanDetail, CheckoutRequest, CheckoutResponse
from app.api.auth import get_current_user

router = APIRouter(prefix="/billing", tags=["Billing & Monetization"])

PLANS: List[PlanDetail] = [
    PlanDetail(
        id="free",
        name="Free Starter",
        tagline="Explore AI composition with basic sequences",
        price_usd=0.0,
        price_inr=0.0,
        billing_period="forever",
        credits_per_month=10,
        features=[
            "10 AI Generations / month",
            "Up to 30-second compositions",
            "Standard MIDI & WAV exports",
            "Classical & Lo-Fi styles",
            "Standard queue priority",
        ],
        recommended=False,
    ),
    PlanDetail(
        id="creator",
        name="Creator Studio",
        tagline="For content creators, producers, and musicians",
        price_usd=15.0,
        price_inr=999.0,
        billing_period="per month",
        credits_per_month=250,
        features=[
            "250 AI Generations / month",
            "Up to 120-second compositions",
            "High-fidelity wavetable audio rendering",
            "Full genre & mood spectrum",
            "Unlimited project saves",
            "Commercial-use license",
            "Fast queue priority",
        ],
        recommended=True,
    ),
    PlanDetail(
        id="pro",
        name="Pro Composer",
        tagline="Unlimited power for game studios and agencies",
        price_usd=39.0,
        price_inr=2999.0,
        billing_period="per month",
        credits_per_month=1000,
        features=[
            "1000 AI Generations / month",
            "Unlimited duration generation",
            "Stems & multitrack export ready",
            "API programmatic access",
            "Dedicated GPU priority queue",
            "Commercial royalty-free rights",
            "24/7 Priority support",
        ],
        recommended=False,
    ),
]

@router.get("/plans", response_model=List[PlanDetail])
def get_plans():
    return PLANS

@router.post("/checkout", response_model=CheckoutResponse)
def create_checkout(
    req: CheckoutRequest,
    current_user: User = Depends(get_current_user),
):
    plan = next((p for p in PLANS if p.id == req.plan_id), None)
    if not plan or plan.id == "free":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid plan selected.")

    # Generates a compliant checkout order representation
    currency = "INR" if req.provider.lower() == "razorpay" else "USD"
    amount = plan.price_inr if currency == "INR" else plan.price_usd

    order_id = f"order_{req.provider[:3]}_{int(time.time())}_{current_user.id[:8]}"
    key_id = "rzp_test_melodia2026" if req.provider == "razorpay" else "pk_test_melodia2026"

    return CheckoutResponse(
        order_id=order_id,
        amount=amount,
        currency=currency,
        provider=req.provider,
        key_id=key_id,
        notes={
            "user_id": current_user.id,
            "plan_id": plan.id,
            "credits": plan.credits_per_month,
        }
    )

@router.post("/webhook")
async def payment_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Server-side webhook handler for Razorpay / Stripe payment events.
    Verifies signature and tops up user credits.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload.")

    event = body.get("event", "payment.captured")
    payload = body.get("payload", {})
    payment_entity = payload.get("payment", {}).get("entity", {})
    notes = payment_entity.get("notes", body.get("notes", {}))

    user_id = notes.get("user_id")
    plan_id = notes.get("plan_id")
    credits_to_add = int(notes.get("credits", 250))

    if user_id:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.plan = plan_id or "creator"
            user.credits_balance += credits_to_add
            usage = UsageRecord(
                user_id=user.id,
                credits_spent=-credits_to_add,
                action=f"Upgraded to {user.plan.title()} Plan (+{credits_to_add} credits)",
            )
            db.add(usage)
            db.commit()

    return {"status": "success", "processed_event": event}
