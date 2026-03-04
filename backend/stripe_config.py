#!/usr/bin/env python3
"""
QUIRRELY STRIPE CONFIGURATION v2.0
TIERS: Free > Pro ($2.99)
CURRENCIES: CAD, USD, GBP, AUD, NZD
"""
import os
from typing import Dict, Optional
from enum import Enum

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
PAYMENT_GRACE_PERIOD_DAYS = 2

class Currency(str, Enum):
    CAD = "cad"
    GBP = "gbp"
    AUD = "aud"
    NZD = "nzd"
    USD = "usd"

CURRENCY_SYMBOLS = {Currency.CAD: "$", Currency.GBP: chr(163), Currency.AUD: "$", Currency.NZD: "$", Currency.USD: "$"}
CURRENCY_FLAGS = {Currency.CAD: "CA", Currency.GBP: "GB", Currency.AUD: "AU", Currency.NZD: "NZ", Currency.USD: "US"}
DEFAULT_CURRENCY = Currency.CAD
COUNTRY_TO_CURRENCY = {"CA": Currency.CAD, "GB": Currency.GBP, "UK": Currency.GBP, "AU": Currency.AUD, "NZ": Currency.NZD, "US": Currency.USD}

def get_currency_for_country(country_code):
    return COUNTRY_TO_CURRENCY.get(country_code.upper(), DEFAULT_CURRENCY)

class ProductTier(str, Enum):
    FREE = "free"
    TRIAL = "trial"
    PRO = "pro"

STRIPE_PRICE_IDS = {
    "pro_monthly": os.environ.get("STRIPE_PRICE_PRO_MONTHLY", ""),
    "pro_annual": os.environ.get("STRIPE_PRICE_PRO_ANNUAL", ""),
}

def get_stripe_price_id(tier, currency=None, annual=False):
    if isinstance(tier, ProductTier):
        tier = tier.value
    interval = "annual" if annual else "monthly"
    return STRIPE_PRICE_IDS.get(f"{tier}_{interval}")

PRICING = {
    Currency.CAD: {
        ProductTier.PRO: {"monthly": 2.99, "annual": 29.99},
    },
    Currency.GBP: {
        ProductTier.PRO: {"monthly": 1.99, "annual": 20.99},
    },
    Currency.AUD: {
        ProductTier.PRO: {"monthly": 4.99, "annual": 29.99},
    },
    Currency.NZD: {
        ProductTier.PRO: {"monthly": 3.99, "annual": 39.99},
    },
    Currency.USD: {
        ProductTier.PRO: {"monthly": 2.99, "annual": 29.99},
    },
}

def get_pricing_display(tier, currency=Currency.CAD):
    currency_prices = PRICING.get(currency, PRICING[Currency.CAD])
    p = currency_prices.get(tier, {})
    monthly = p.get("monthly", 0)
    annual = p.get("annual", 0)
    return {
        "monthly": monthly,
        "annual": annual,
        "annual_monthly_equivalent": round(annual / 12, 2) if annual else 0,
        "annual_savings_percent": round((1 - annual / (monthly * 12)) * 100) if monthly else 0,
    }

TIER_FEATURES = {
    ProductTier.FREE: {"analyses_per_month": 3, "phases": [1,2,3], "stretch_access": False, "featured_profile": False, "blog_submission": False, "story_mode": False, "leaderboard": False, "achievements": False, "advanced_analytics": False},
    ProductTier.TRIAL: {"analyses_per_month": 100, "phases": [1,2,3], "stretch_access": True, "featured_profile": False, "blog_submission": False, "story_mode": False, "leaderboard": False, "achievements": False, "advanced_analytics": False},
    ProductTier.PRO: {"analyses_per_month": 100, "phases": [1,2,3], "stretch_access": True, "featured_profile": True, "blog_submission": True, "story_mode": False, "leaderboard": False, "achievements": False, "advanced_analytics": False},
}

def get_tier_features(tier):
    return TIER_FEATURES.get(tier, TIER_FEATURES[ProductTier.FREE])

TRIAL_CONFIG = {"pro_trial_days": 7, "auto_trial_word_threshold": 500, "trial_once_per_user": True}

REFUND_POLICY = {"refunds_allowed": False, "policy_text": "Quirrely subscriptions are non-refundable. You may cancel at any time but no refunds will be issued. Cancelled subscriptions remain active until the end of the billing period."}
