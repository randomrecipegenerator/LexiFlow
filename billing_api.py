"""
LexiFlow Stripe Connect Billing Module.

Provides subscription management endpoints using Stripe Connect.
Handles checkout, customer portal, webhooks, and plan status.

Pricing Tiers (monthly recurring):
- Starter: $29  — AI Intake Suite, Basic Chronologies
- Professional: $99  — Standard + 250 docs/mo + Priority Processing
- Enterprise: $129  — Professional + Veritas Deposition™ + 500 docs/mo

Stripe Connect onboarding scheduled: Tuesday, June 23, 2026.
Test mode keys should be used for development until live keys are configured.
"""
import os
import json
import logging
import stripe
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session

from database import get_db
from models import Firm, User, Subscription
from auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["Billing & Subscriptions"])

# Separate router for webhooks (no prefix — mapped at /webhooks/stripe)
webhook_router = APIRouter(tags=["Stripe Webhooks"])

# --- Stripe Configuration ---
# Test keys are used until Stripe Connect onboarding (June 23).
# In production, these are set via environment variables.
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_test_placeholder")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# Price IDs — to be created in Stripe Dashboard after onboarding.
# Until then, the checkout endpoint uses test-mode price lookups.
PRICE_IDS = {
    "starter": os.getenv("STRIPE_PRICE_STARTER", "price_starter_monthly"),
    "professional": os.getenv("STRIPE_PRICE_PROFESSIONAL", "price_professional_monthly"),
    "enterprise": os.getenv("STRIPE_PRICE_ENTERPRISE", "price_enterprise_monthly"),
}

# Tier metadata for reference
PLANS = {
    "starter": {
        "name": "Starter",
        "amount": 2900,  # $29 in cents
        "description": "AI Intake Suite (Web/SMS AI, Voice AI, Basic Chronologies)",
        "features": [
            "AI Web Chat & SMS Intake",
            "Voice AI Agent",
            "Basic Medical Chronologies",
            "Lead Scoring & Qualification",
        ],
    },
    "professional": {
        "name": "Professional",
        "amount": 9900,  # $99 in cents
        "description": "Standard features + 250 documents/month + Priority AI Processing",
        "features": [
            "Everything in Starter",
            "250 Documents/Month Processing",
            "Priority AI Processing Queue",
            "Custom CRM Integration",
        ],
    },
    "enterprise": {
        "name": "Enterprise",
        "amount": 12900,  # $129 in cents
        "description": "Professional + Veritas Deposition™ + 500 documents/month + LexiFlow Strategist™",
        "features": [
            "Everything in Professional",
            "Veritas Deposition™ Suite",
            "LexiFlow Strategist™ AI Advice",
            "500 Documents/Month",
            "Enterprise CRM Sync (Clio, Filevine)",
        ],
    },
}

DOCUMENT_LIMITS = {
    "starter": 10,
    "professional": 250,
    "enterprise": 500,
}


def get_stripe() -> stripe.StripeObject:
    """Get a configured Stripe client. Uses test keys if live not configured."""
    stripe.api_key = STRIPE_SECRET_KEY
    return stripe


# --- Error responses ---
def _stripe_not_configured():
    raise HTTPException(
        status_code=503,
        detail="Stripe billing is not yet configured. "
               "Please complete Stripe Connect onboarding (scheduled June 23, 2026) "
               "and set STRIPE_SECRET_KEY in environment variables.",
    )


def _firm_required(firm: Optional[Firm]):
    if not firm:
        raise HTTPException(status_code=401, detail="Firm authentication required")


def _user_required(user: Optional[User]):
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")


# --- Endpoints ---


@router.get("/plans")
def list_plans():
    """
    GET /api/billing/plans
    Returns available subscription plans with pricing and features.
    No authentication required — used before checkout.
    """
    return {
        "plans": [
            {
                "id": tier,
                "name": info["name"],
                "amount": info["amount"],
                "amount_display": f"${info['amount'] // 100}.00",
                "interval": "month",
                "description": info["description"],
                "features": info["features"],
                "document_limit": DOCUMENT_LIMITS[tier],
                "price_id": PRICE_IDS.get(tier),
            }
            for tier, info in PLANS.items()
        ]
    }


@router.post("/create-checkout")
async def create_checkout_session(
    request: Request,
    price_id: Optional[str] = None,
    plan: Optional[str] = None,
    success_url: Optional[str] = None,
    cancel_url: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    POST /api/billing/create-checkout
    Creates a Stripe Checkout Session for subscription purchase.
    
    Accepts either a Stripe price_id OR a plan name (standard/professional/enterprise).
    If plan is provided, the price ID is looked up from configuration.
    
    Requires authentication. The firm associated with the user is billed.
    """
    _user_required(user)
    firm = db.query(Firm).filter(Firm.id == user.firm_id).first()
    _firm_required(firm)

    # Resolve price_id
    resolved_price_id = price_id
    if not resolved_price_id and plan:
        resolved_price_id = PRICE_IDS.get(plan.lower())
    if not resolved_price_id:
        raise HTTPException(
            status_code=400,
            detail="Either 'price_id' (Stripe Price ID) or 'plan' (starter/professional/enterprise) is required.",
        )

    # If Stripe isn't configured yet, return a simulated checkout URL for testing
    if STRIPE_SECRET_KEY.startswith("sk_test_placeholder"):
        # Simulated response for pre-onboarding development
        logger.info(f"Stripe not configured — returning simulated checkout URL for firm {firm.id}, plan={plan or price_id}")
        return {
            "status": "simulated",
            "url": f"{FRONTEND_URL}/billing/simulated-checkout?firm_id={firm.id}&plan={plan or 'starter'}",
            "session_id": f"cs_sim_{firm.id}_{datetime.utcnow().timestamp()}",
            "message": "Stripe Connect onboarding is scheduled for June 23, 2026. "
                       "This is a simulated checkout for development purposes.",
        }

    try:
        stripe_instance = get_stripe()

        # Ensure the customer exists in Stripe
        customer_id = firm.stripe_customer_id
        if not customer_id:
            customer = stripe_instance.Customer.create(
                email=user.email,
                name=firm.name,
                metadata={"firm_id": str(firm.id), "firm_slug": firm.slug},
            )
            customer_id = customer.id
            firm.stripe_customer_id = customer_id
            db.commit()

        base_url = str(request.base_url).rstrip("/")
        session = stripe_instance.checkout.Session.create(
            customer=customer_id,
            mode="subscription",
            line_items=[{"price": resolved_price_id, "quantity": 1}],
            success_url=success_url or f"{base_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=cancel_url or f"{base_url}/billing/cancel",
            metadata={
                "firm_id": str(firm.id),
                "firm_slug": firm.slug,
            },
            subscription_data={
                "metadata": {
                    "firm_id": str(firm.id),
                    "firm_slug": firm.slug,
                },
            },
        )

        return {"status": "success", "url": session.url, "session_id": session.id}

    except stripe.error.StripeError as e:
        logger.error(f"Stripe checkout error: {e}")
        raise HTTPException(status_code=502, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        logger.error(f"Checkout session creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create checkout session: {str(e)}")


@router.post("/create-portal-session")
async def create_portal_session(
    return_url: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    POST /api/billing/create-portal-session
    Creates a Stripe Customer Portal session for subscription management
    (upgrade, downgrade, cancel, update payment method).
    
    Requires authentication.
    """
    _user_required(user)
    firm = db.query(Firm).filter(Firm.id == user.firm_id).first()
    _firm_required(firm)

    if not firm.stripe_customer_id:
        raise HTTPException(
            status_code=400,
            detail="No Stripe customer record found. Please subscribe to a plan first.",
        )

    if STRIPE_SECRET_KEY.startswith("sk_test_placeholder"):
        return {
            "status": "simulated",
            "url": f"{FRONTEND_URL}/billing/simulated-portal?firm_id={firm.id}",
            "message": "Stripe Customer Portal is not available until Stripe Connect onboarding completes (June 23, 2026).",
        }

    try:
        stripe_instance = get_stripe()
        portal_session = stripe_instance.billing_portal.Session.create(
            customer=firm.stripe_customer_id,
            return_url=return_url or f"{FRONTEND_URL}/dashboard",
        )

        return {"status": "success", "url": portal_session.url}

    except stripe.error.StripeError as e:
        logger.error(f"Stripe portal error: {e}")
        raise HTTPException(status_code=502, detail=f"Stripe error: {str(e)}")
    except Exception as e:
        logger.error(f"Portal session creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create portal session: {str(e)}")


@webhook_router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    POST /api/webhooks/stripe
    Stripe webhook handler for subscription lifecycle events.
    
    Processes the following events:
    - checkout.session.completed → Activate subscription
    - invoice.paid → Reset billing period
    - invoice.payment_failed → Flag account
    - customer.subscription.updated → Sync plan changes
    - customer.subscription.deleted → Downgrade
    
    This endpoint receives raw POST data from Stripe with a Stripe-Signature header.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if STRIPE_SECRET_KEY.startswith("sk_test_placeholder"):
        logger.info("Stripe webhook received but Stripe is not configured — returning 200 OK for development")
        return {"status": "ignored", "message": "Stripe not configured"}

    try:
        stripe_instance = get_stripe()
        event = stripe_instance.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid Stripe webhook payload: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid Stripe webhook signature: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    event_type = event.get("type")
    data_object = event.get("data", {}).get("object", {})

    logger.info(f"Stripe webhook received: {event_type} (id={data_object.get('id')})")

    try:
        if event_type == "checkout.session.completed":
            await _handle_checkout_completed(data_object, db)
        elif event_type == "invoice.paid":
            await _handle_invoice_paid(data_object, db)
        elif event_type == "invoice.payment_failed":
            await _handle_payment_failed(data_object, db)
        elif event_type == "customer.subscription.updated":
            await _handle_subscription_updated(data_object, db)
        elif event_type == "customer.subscription.deleted":
            await _handle_subscription_deleted(data_object, db)
        else:
            logger.info(f"Unhandled Stripe event type: {event_type}")
    except Exception as e:
        logger.error(f"Error processing Stripe webhook {event_type}: {e}")
        # Return 200 to acknowledge receipt even on processing errors

    return {"status": "received", "event": event_type}


async def _handle_checkout_completed(session_data: dict, db: Session):
    """Process checkout.session.completed — activate firm subscription."""
    metadata = session_data.get("metadata", {})
    firm_id = metadata.get("firm_id")
    if not firm_id:
        logger.warning("Checkout completed without firm_id in metadata")
        return

    firm = db.query(Firm).filter(Firm.id == int(firm_id)).first()
    if not firm:
        logger.warning(f"Firm {firm_id} not found for checkout completion")
        return

    customer_id = session_data.get("customer")
    subscription_id = session_data.get("subscription")

    # Map the Stripe subscription to the firm
    firm.stripe_customer_id = customer_id
    firm.stripe_subscription_id = subscription_id
    firm.plan_status = "active"

    # Determine tier from the subscription line items
    # Fall back to starter if we can't detect
    tier = "starter"
    line_items = session_data.get("line_items", {}).get("data", [])
    if line_items:
        price_id = line_items[0].get("price", {}).get("id", "")
        reverse_map = {v: k for k, v in PRICE_IDS.items()}
        tier = reverse_map.get(price_id, "starter")
    else:
        # Try to infer from metadata
        tier = metadata.get("plan", "starter")

    firm.billing_tier = tier

    # Create local subscription record
    sub = Subscription(
        firm_id=firm.id,
        stripe_subscription_id=subscription_id,
        stripe_customer_id=customer_id,
        status="active",
        plan_tier=tier,
        current_period_start=datetime.utcnow(),
    )
    db.add(sub)
    db.commit()

    logger.info(f"Firm {firm.id} ({firm.name}) subscription activated: {tier}")


async def _handle_invoice_paid(invoice_data: dict, db: Session):
    """Process invoice.paid — reset billing period."""
    subscription_id = invoice_data.get("subscription")
    if not subscription_id:
        return

    sub = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_id
    ).first()
    if not sub:
        return

    period_end = invoice_data.get("period_end")
    if period_end:
        sub.current_period_end = datetime.fromtimestamp(period_end)
    sub.status = "active"
    db.commit()

    # Also update the firm's billing period
    firm = db.query(Firm).filter(Firm.id == sub.firm_id).first()
    if firm:
        firm.billing_period_start = datetime.utcnow()
        firm.plan_status = "active"
        db.commit()


async def _handle_payment_failed(invoice_data: dict, db: Session):
    """Process invoice.payment_failed — flag the firm account."""
    subscription_id = invoice_data.get("subscription")
    if not subscription_id:
        return

    sub = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_id
    ).first()
    if not sub:
        return

    sub.status = "past_due"
    db.commit()

    firm = db.query(Firm).filter(Firm.id == sub.firm_id).first()
    if firm:
        firm.plan_status = "past_due"
        db.commit()

    logger.warning(f"Payment failed for firm {sub.firm_id}")


async def _handle_subscription_updated(subscription_data: dict, db: Session):
    """Process customer.subscription.updated — sync plan changes."""
    subscription_id = subscription_data.get("id")
    if not subscription_id:
        return

    sub = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_id
    ).first()
    if not sub:
        return

    status = subscription_data.get("status", sub.status)
    cancel_at_period_end = subscription_data.get("cancel_at_period_end", False)
    current_period_end = subscription_data.get("current_period_end")
    items = subscription_data.get("items", {}).get("data", [])

    sub.status = status
    sub.cancel_at_period_end = cancel_at_period_end
    if current_period_end:
        sub.current_period_end = datetime.fromtimestamp(current_period_end)

    # Detect tier from items
    if items:
        price_id = items[0].get("price", {}).get("id", "")
        reverse_map = {v: k for k, v in PRICE_IDS.items()}
        detected_tier = reverse_map.get(price_id)
        if detected_tier:
            sub.plan_tier = detected_tier

    sub.updated_at = datetime.utcnow()
    db.commit()

    # Sync firm-level fields
    firm = db.query(Firm).filter(Firm.id == sub.firm_id).first()
    if firm:
        firm.billing_tier = sub.plan_tier
        firm.plan_status = status
        db.commit()


async def _handle_subscription_deleted(subscription_data: dict, db: Session):
    """Process customer.subscription.deleted — downgrade firm."""
    subscription_id = subscription_data.get("id")
    if not subscription_id:
        return

    sub = db.query(Subscription).filter(
        Subscription.stripe_subscription_id == subscription_id
    ).first()
    if not sub:
        return

    sub.status = "canceled"
    sub.updated_at = datetime.utcnow()
    db.commit()

    firm = db.query(Firm).filter(Firm.id == sub.firm_id).first()
    if firm:
        firm.plan_status = "canceled"
        firm.stripe_subscription_id = None
        firm.billing_tier = "starter"
        db.commit()

    logger.info(f"Subscription canceled for firm {sub.firm_id}")


@router.get("/status")
def get_billing_status(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    GET /api/billing/status
    Returns the current firm's billing plan, usage, and subscription details.
    
    Requires authentication.
    """
    _user_required(user)
    firm = db.query(Firm).filter(Firm.id == user.firm_id).first()
    _firm_required(firm)

    # Get active subscription
    subscription = db.query(Subscription).filter(
        Subscription.firm_id == firm.id,
        Subscription.status.in_(["active", "trialing", "past_due"]),
    ).order_by(Subscription.created_at.desc()).first()

    # Calculate current usage for the billing period
    from models import Usage
    usage_entries = db.query(Usage).filter(
        Usage.firm_id == firm.id,
        Usage.timestamp >= (firm.billing_period_start or datetime.utcnow()),
    ).all()

    usage_by_type = {}
    for entry in usage_entries:
        usage_by_type[entry.usage_type] = usage_by_type.get(entry.usage_type, 0) + entry.quantity

    doc_limit = DOCUMENT_LIMITS.get(firm.billing_tier, 50)
    docs_used = usage_by_type.get("document_analysis", 0)

    return {
        "plan": {
            "tier": firm.billing_tier,
            "status": firm.plan_status,
            "billing_period_start": firm.billing_period_start.isoformat() if firm.billing_period_start else None,
            "trial_expires_at": firm.trial_expires_at.isoformat() if firm.trial_expires_at else None,
        },
        "subscription": {
            "stripe_customer_id": firm.stripe_customer_id,
            "stripe_subscription_id": firm.stripe_subscription_id,
            "status": subscription.status if subscription else None,
            "plan_tier": subscription.plan_tier if subscription else None,
            "current_period_start": subscription.current_period_start.isoformat() if subscription and subscription.current_period_start else None,
            "current_period_end": subscription.current_period_end.isoformat() if subscription and subscription.current_period_end else None,
            "cancel_at_period_end": subscription.cancel_at_period_end if subscription else False,
        } if subscription else None,
        "usage": {
            "documents_processed": int(docs_used),
            "document_limit": doc_limit,
            "documents_remaining": max(0, doc_limit - int(docs_used)),
            "by_type": {k: int(v) for k, v in usage_by_type.items()},
        },
        "stripe_configured": not STRIPE_SECRET_KEY.startswith("sk_test_placeholder"),
        "publishable_key": STRIPE_PUBLISHABLE_KEY if not STRIPE_PUBLISHABLE_KEY.startswith("pk_test_placeholder") else None,
    }


@router.post("/simulate-activation")
def simulate_subscription_activation(
    plan: str = "starter",
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    POST /api/billing/simulate-activation
    DEVELOPMENT ONLY: Simulates a subscription activation without Stripe.
    Useful for testing before Stripe Connect onboarding (June 23).
    
    Requires authentication.
    """
    _user_required(user)
    firm = db.query(Firm).filter(Firm.id == user.firm_id).first()
    _firm_required(firm)

    if plan not in PLANS:
        raise HTTPException(status_code=400, detail=f"Invalid plan. Choose from: {', '.join(PLANS.keys())}")

    # Activate the firm
    firm.plan_status = "active"
    firm.billing_tier = plan
    firm.billing_period_start = datetime.utcnow()

    # Create a local subscription record
    sub = Subscription(
        firm_id=firm.id,
        stripe_subscription_id=f"sub_sim_{firm.id}_{int(datetime.utcnow().timestamp())}",
        stripe_customer_id=f"cus_sim_{firm.id}",
        status="active",
        plan_tier=plan,
        current_period_start=datetime.utcnow(),
    )
    db.add(sub)
    db.commit()

    logger.info(f"Simulated subscription activation: firm={firm.id}, plan={plan}")

    return {
        "status": "success",
        "message": f"Subscription simulated: {plan} tier activated for {firm.name}",
        "plan": plan,
        "valid_until": sub.current_period_start.isoformat() if sub.current_period_start else None,
    }


@router.post("/simulate-cancel")
def simulate_subscription_cancellation(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    POST /api/billing/simulate-cancel
    DEVELOPMENT ONLY: Simulates subscription cancellation without Stripe.
    """
    _user_required(user)
    firm = db.query(Firm).filter(Firm.id == user.firm_id).first()
    _firm_required(firm)

    sub = db.query(Subscription).filter(
        Subscription.firm_id == firm.id,
        Subscription.status.in_(["active", "trialing"]),
    ).first()

    if sub:
        sub.status = "canceled"
        sub.cancel_at_period_end = True
        sub.updated_at = datetime.utcnow()

    firm.plan_status = "canceled"
    firm.stripe_subscription_id = None
    db.commit()

    return {"status": "success", "message": "Subscription canceled (simulated)"}