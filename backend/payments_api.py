#!/usr/bin/env python3
"""
QUIRRELY PAYMENTS API v1.0
Stripe checkout, webhooks, and subscription management.

Features:
- Checkout session creation
- Subscription management
- Trial handling (7-day PRO, auto-unlock at 500 words)
- Payment failure grace period (2 days)
- No refunds policy
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, Header, Request
from pydantic import BaseModel
import stripe

from stripe_config import (
    STRIPE_SECRET_KEY,
    STRIPE_WEBHOOK_SECRET,
    Currency,
    ProductTier,
    DEFAULT_CURRENCY,
    PAYMENT_GRACE_PERIOD_DAYS,
    TRIAL_CONFIG,
    get_currency_for_country,
    get_stripe_price_id,
    get_price,
    get_all_prices_for_display,
    get_bundle_savings,
    REFUND_POLICY,
    TIER_FEATURES,
)


# ═══════════════════════════════════════════════════════════════════════════
# SETUP
# ═══════════════════════════════════════════════════════════════════════════

stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter(prefix="/api/v2/payments", tags=["payments"])


# ═══════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════

class CreateCheckoutRequest(BaseModel):
    tier: str  # "pro", "curator", "bundle"
    annual: bool = False
    currency: Optional[str] = None  # If not provided, detect from geo


class CheckoutResponse(BaseModel):
    checkout_url: str
    session_id: str


class SubscriptionResponse(BaseModel):
    tier: str
    status: str
    current_period_end: datetime
    cancel_at_period_end: bool
    currency: str
    amount: int
    interval: str


class PricingResponse(BaseModel):
    currency: str
    currency_symbol: str
    currency_flag: str
    pro: Dict[str, Any]
    curator: Dict[str, Any]
    bundle: Dict[str, Any]


class TrialStatusResponse(BaseModel):
    has_trialed: bool
    trial_active: bool
    trial_ends_at: Optional[datetime]
    can_start_trial: bool
    auto_trial_eligible: bool
    words_until_auto_trial: int


# ═══════════════════════════════════════════════════════════════════════════
# IN-MEMORY STORAGE (Replace with database in production)
# ═══════════════════════════════════════════════════════════════════════════

_subscriptions: Dict[str, Dict] = {}
_trials: Dict[str, Dict] = {}
_payment_failures: Dict[str, Dict] = {}


# ═══════════════════════════════════════════════════════════════════════════
# DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════

def get_current_user(authorization: Optional[str] = Header(None)) -> Optional[str]:
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        if len(token) > 10:
            return token[:36]
    return None


def require_auth(authorization: Optional[str] = Header(None)) -> str:
    user_id = get_current_user(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user_id


def get_user_country(request: Request) -> str:
    """Get country code from request headers."""
    return request.headers.get("CF-IPCountry", "CA")


# ═══════════════════════════════════════════════════════════════════════════
# PRICING ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/pricing", response_model=PricingResponse)
async def get_pricing(
    request: Request,
    currency: Optional[str] = None,
):
    """Get pricing in user's currency."""
    if currency:
        try:
            curr = Currency(currency.lower())
        except ValueError:
            curr = DEFAULT_CURRENCY
    else:
        country = get_user_country(request)
        curr = get_currency_for_country(country)
    
    prices = get_all_prices_for_display(curr)
    return PricingResponse(**prices)


@router.get("/pricing/all")
async def get_all_pricing():
    """Get pricing in all currencies (for currency selector)."""
    return {
        currency.value: get_all_prices_for_display(currency)
        for currency in Currency
    }


@router.get("/refund-policy")
async def get_refund_policy():
    """Get refund policy text."""
    return REFUND_POLICY


# ═══════════════════════════════════════════════════════════════════════════
# CHECKOUT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout_session(
    request_body: CreateCheckoutRequest,
    request: Request,
    user_id: str = Depends(require_auth),
):
    """Create Stripe checkout session."""
    # Determine currency
    if request_body.currency:
        try:
            currency = Currency(request_body.currency.lower())
        except ValueError:
            currency = DEFAULT_CURRENCY
    else:
        country = get_user_country(request)
        currency = get_currency_for_country(country)
    
    # Get tier
    try:
        tier = ProductTier(request_body.tier.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {request_body.tier}")
    
    if tier not in [ProductTier.PRO, ProductTier.CURATOR, ProductTier.BUNDLE]:
        raise HTTPException(status_code=400, detail="Only PRO, Curator, or Bundle can be purchased")
    
    # Get Stripe price ID
    price_id = get_stripe_price_id(tier, currency, request_body.annual)
    if not price_id:
        raise HTTPException(status_code=400, detail="Price not found for this combination")
    
    # Create checkout session
    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=f"https://quirrely.com/welcome?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url="https://quirrely.com/pricing?cancelled=true",
            client_reference_id=user_id,
            customer_email=None,  # Would get from user profile
            metadata={
                "user_id": user_id,
                "tier": tier.value,
                "currency": currency.value,
                "annual": str(request_body.annual),
            },
            subscription_data={
                "metadata": {
                    "user_id": user_id,
                    "tier": tier.value,
                },
            },
        )
        
        return CheckoutResponse(
            checkout_url=session.url,
            session_id=session.id,
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/checkout/{session_id}/status")
async def get_checkout_status(session_id: str):
    """Check status of a checkout session."""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        return {
            "status": session.status,
            "payment_status": session.payment_status,
            "customer": session.customer,
            "subscription": session.subscription,
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=404, detail="Session not found")


# ═══════════════════════════════════════════════════════════════════════════
# SUBSCRIPTION MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/subscription", response_model=Optional[SubscriptionResponse])
async def get_subscription(user_id: str = Depends(require_auth)):
    """Get current user's subscription."""
    sub = _subscriptions.get(user_id)
    if not sub:
        return None
    
    return SubscriptionResponse(**sub)


@router.post("/subscription/cancel")
async def cancel_subscription(user_id: str = Depends(require_auth)):
    """Cancel subscription at end of billing period."""
    sub = _subscriptions.get(user_id)
    if not sub:
        raise HTTPException(status_code=404, detail="No active subscription")
    
    try:
        stripe.Subscription.modify(
            sub["stripe_subscription_id"],
            cancel_at_period_end=True,
        )
        
        sub["cancel_at_period_end"] = True
        _subscriptions[user_id] = sub
        
        return {
            "success": True,
            "message": "Subscription will cancel at end of billing period",
            "cancels_at": sub["current_period_end"],
        }
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscription/reactivate")
async def reactivate_subscription(user_id: str = Depends(require_auth)):
    """Reactivate a cancelled subscription before it ends."""
    sub = _subscriptions.get(user_id)
    if not sub:
        raise HTTPException(status_code=404, detail="No subscription found")
    
    if not sub.get("cancel_at_period_end"):
        raise HTTPException(status_code=400, detail="Subscription is not cancelled")
    
    try:
        stripe.Subscription.modify(
            sub["stripe_subscription_id"],
            cancel_at_period_end=False,
        )
        
        sub["cancel_at_period_end"] = False
        _subscriptions[user_id] = sub
        
        return {"success": True, "message": "Subscription reactivated"}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscription/change")
async def change_subscription(
    new_tier: str,
    annual: bool = False,
    user_id: str = Depends(require_auth),
):
    """Change subscription tier (upgrade/downgrade)."""
    sub = _subscriptions.get(user_id)
    if not sub:
        raise HTTPException(status_code=404, detail="No active subscription")
    
    try:
        new_tier_enum = ProductTier(new_tier.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid tier: {new_tier}")
    
    currency = Currency(sub["currency"])
    new_price_id = get_stripe_price_id(new_tier_enum, currency, annual)
    
    if not new_price_id:
        raise HTTPException(status_code=400, detail="Price not found")
    
    try:
        # Get current subscription from Stripe
        stripe_sub = stripe.Subscription.retrieve(sub["stripe_subscription_id"])
        
        # Update subscription
        stripe.Subscription.modify(
            sub["stripe_subscription_id"],
            items=[{
                "id": stripe_sub["items"]["data"][0].id,
                "price": new_price_id,
            }],
            proration_behavior="create_prorations",
        )
        
        # Update local record
        price = get_price(new_tier_enum, currency)
        sub["tier"] = new_tier_enum.value
        sub["amount"] = price.annual_cents if annual else price.monthly_cents
        sub["interval"] = "year" if annual else "month"
        _subscriptions[user_id] = sub
        
        return {"success": True, "message": f"Subscription changed to {new_tier}"}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════
# TRIAL MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/trial/status", response_model=TrialStatusResponse)
async def get_trial_status(
    user_id: str = Depends(require_auth),
):
    """Get trial status for user."""
    trial = _trials.get(user_id, {})
    
    has_trialed = trial.get("has_trialed", False)
    trial_active = False
    trial_ends_at = None
    
    if trial.get("trial_ends_at"):
        trial_ends_at = trial["trial_ends_at"]
        trial_active = datetime.utcnow() < trial_ends_at
    
    # Check if auto-trial eligible (would need word count from milestone tracker)
    words_written = 0  # Would get from milestone tracker
    auto_trial_eligible = words_written >= TRIAL_CONFIG["auto_trial_word_threshold"]
    words_until_auto_trial = max(0, TRIAL_CONFIG["auto_trial_word_threshold"] - words_written)
    
    can_start_trial = not has_trialed and not trial_active
    
    return TrialStatusResponse(
        has_trialed=has_trialed,
        trial_active=trial_active,
        trial_ends_at=trial_ends_at,
        can_start_trial=can_start_trial,
        auto_trial_eligible=auto_trial_eligible,
        words_until_auto_trial=words_until_auto_trial,
    )


@router.post("/trial/start")
async def start_trial(user_id: str = Depends(require_auth)):
    """Start 7-day PRO trial."""
    trial = _trials.get(user_id, {})
    
    if trial.get("has_trialed") and TRIAL_CONFIG["trial_once_per_user"]:
        raise HTTPException(status_code=400, detail="Trial already used")
    
    # Check if already subscribed
    if user_id in _subscriptions:
        raise HTTPException(status_code=400, detail="Already subscribed")
    
    trial_ends = datetime.utcnow() + timedelta(days=TRIAL_CONFIG["pro_trial_days"])
    
    _trials[user_id] = {
        "has_trialed": True,
        "trial_started_at": datetime.utcnow(),
        "trial_ends_at": trial_ends,
        "trial_type": "pro",
    }
    
    return {
        "success": True,
        "message": f"PRO trial started! Expires in {TRIAL_CONFIG['pro_trial_days']} days.",
        "trial_ends_at": trial_ends,
    }


def check_auto_trial_unlock(user_id: str, lifetime_words: int) -> Optional[Dict]:
    """
    Check if user should auto-unlock trial based on word count.
    Called from milestone tracker when words are recorded.
    """
    if lifetime_words < TRIAL_CONFIG["auto_trial_word_threshold"]:
        return None
    
    trial = _trials.get(user_id, {})
    
    if trial.get("has_trialed") and TRIAL_CONFIG["trial_once_per_user"]:
        return None
    
    if user_id in _subscriptions:
        return None
    
    # Auto-start trial
    trial_ends = datetime.utcnow() + timedelta(days=TRIAL_CONFIG["pro_trial_days"])
    
    _trials[user_id] = {
        "has_trialed": True,
        "trial_started_at": datetime.utcnow(),
        "trial_ends_at": trial_ends,
        "trial_type": "pro",
        "auto_unlocked": True,
        "unlocked_at_words": lifetime_words,
    }
    
    return {
        "trial_started": True,
        "trial_ends_at": trial_ends,
        "reason": f"Auto-unlocked at {lifetime_words} words",
    }


# ═══════════════════════════════════════════════════════════════════════════
# TIER STATUS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/tier")
async def get_current_tier(user_id: str = Depends(require_auth)):
    """Get user's current tier and features."""
    # Check subscription
    sub = _subscriptions.get(user_id)
    if sub and sub.get("status") == "active":
        tier = ProductTier(sub["tier"])
        return {
            "tier": tier.value,
            "source": "subscription",
            "features": TIER_FEATURES.get(tier, {}),
            "subscription": sub,
        }
    
    # Check trial
    trial = _trials.get(user_id, {})
    if trial.get("trial_ends_at"):
        if datetime.utcnow() < trial["trial_ends_at"]:
            return {
                "tier": ProductTier.TRIAL.value,
                "source": "trial",
                "features": TIER_FEATURES.get(ProductTier.TRIAL, {}),
                "trial_ends_at": trial["trial_ends_at"],
            }
    
    # Check grace period for failed payments
    failure = _payment_failures.get(user_id)
    if failure:
        grace_ends = failure["failed_at"] + timedelta(days=PAYMENT_GRACE_PERIOD_DAYS)
        if datetime.utcnow() < grace_ends:
            tier = ProductTier(failure["tier"])
            return {
                "tier": tier.value,
                "source": "grace_period",
                "features": TIER_FEATURES.get(tier, {}),
                "grace_ends_at": grace_ends,
                "payment_failed": True,
            }
    
    # Default to FREE
    return {
        "tier": ProductTier.FREE.value,
        "source": "default",
        "features": TIER_FEATURES.get(ProductTier.FREE, {}),
    }


# ═══════════════════════════════════════════════════════════════════════════
# STRIPE WEBHOOKS
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events."""
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle events
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        await handle_checkout_completed(session)
    
    elif event["type"] == "customer.subscription.updated":
        subscription = event["data"]["object"]
        await handle_subscription_updated(subscription)
    
    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        await handle_subscription_deleted(subscription)
    
    elif event["type"] == "invoice.payment_failed":
        invoice = event["data"]["object"]
        await handle_payment_failed(invoice)
    
    elif event["type"] == "invoice.payment_succeeded":
        invoice = event["data"]["object"]
        await handle_payment_succeeded(invoice)
    
    return {"received": True}


async def handle_checkout_completed(session: Dict):
    """Handle successful checkout."""
    user_id = session.get("client_reference_id") or session.get("metadata", {}).get("user_id")
    if not user_id:
        return
    
    subscription_id = session.get("subscription")
    if not subscription_id:
        return
    
    # Fetch full subscription
    stripe_sub = stripe.Subscription.retrieve(subscription_id)
    
    tier = stripe_sub.get("metadata", {}).get("tier", "pro")
    
    _subscriptions[user_id] = {
        "stripe_subscription_id": subscription_id,
        "stripe_customer_id": session.get("customer"),
        "tier": tier,
        "status": stripe_sub["status"],
        "current_period_end": datetime.fromtimestamp(stripe_sub["current_period_end"]),
        "cancel_at_period_end": stripe_sub["cancel_at_period_end"],
        "currency": stripe_sub["currency"],
        "amount": stripe_sub["items"]["data"][0]["price"]["unit_amount"],
        "interval": stripe_sub["items"]["data"][0]["price"]["recurring"]["interval"],
    }
    
    # Clear any trial
    if user_id in _trials:
        _trials[user_id]["converted_to_paid"] = True


async def handle_subscription_updated(subscription: Dict):
    """Handle subscription updates."""
    user_id = subscription.get("metadata", {}).get("user_id")
    if not user_id or user_id not in _subscriptions:
        return
    
    _subscriptions[user_id].update({
        "status": subscription["status"],
        "current_period_end": datetime.fromtimestamp(subscription["current_period_end"]),
        "cancel_at_period_end": subscription["cancel_at_period_end"],
    })


async def handle_subscription_deleted(subscription: Dict):
    """Handle subscription cancellation/deletion."""
    user_id = subscription.get("metadata", {}).get("user_id")
    if not user_id:
        return
    
    if user_id in _subscriptions:
        _subscriptions[user_id]["status"] = "cancelled"


async def handle_payment_failed(invoice: Dict):
    """Handle failed payment - start grace period."""
    subscription_id = invoice.get("subscription")
    if not subscription_id:
        return
    
    # Find user by subscription
    for user_id, sub in _subscriptions.items():
        if sub.get("stripe_subscription_id") == subscription_id:
            _payment_failures[user_id] = {
                "failed_at": datetime.utcnow(),
                "tier": sub["tier"],
                "invoice_id": invoice["id"],
            }
            break


async def handle_payment_succeeded(invoice: Dict):
    """Handle successful payment - clear any grace period."""
    subscription_id = invoice.get("subscription")
    if not subscription_id:
        return
    
    # Find and clear failure record
    for user_id, sub in _subscriptions.items():
        if sub.get("stripe_subscription_id") == subscription_id:
            if user_id in _payment_failures:
                del _payment_failures[user_id]
            break


# ═══════════════════════════════════════════════════════════════════════════
# BILLING PORTAL
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/billing-portal")
async def create_billing_portal_session(user_id: str = Depends(require_auth)):
    """Create Stripe billing portal session for subscription management."""
    sub = _subscriptions.get(user_id)
    if not sub:
        raise HTTPException(status_code=404, detail="No subscription found")
    
    try:
        session = stripe.billing_portal.Session.create(
            customer=sub["stripe_customer_id"],
            return_url="https://quirrely.com/settings",
        )
        return {"url": session.url}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=500, detail=str(e))
