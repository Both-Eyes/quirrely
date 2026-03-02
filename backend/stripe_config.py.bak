#!/usr/bin/env python3
"""
QUIRRELY STRIPE CONFIGURATION v1.0
Stripe setup, products, prices, and currency handling.

CURRENCIES: CAD, GBP, EUR, AUD (NEVER USD)
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "sk_test_...")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY", "pk_test_...")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "whsec_...")

# Grace period for failed payments (in days)
PAYMENT_GRACE_PERIOD_DAYS = 2


# ═══════════════════════════════════════════════════════════════════════════
# CURRENCIES (NEVER USD)
# ═══════════════════════════════════════════════════════════════════════════

class Currency(str, Enum):
    CAD = "cad"
    GBP = "gbp"
    EUR = "eur"
    AUD = "aud"
    NZD = "nzd"


CURRENCY_SYMBOLS = {
    Currency.CAD: "$",
    Currency.GBP: "£",
    Currency.EUR: "€",
    Currency.AUD: "$",
    Currency.NZD: "$",
}

CURRENCY_NAMES = {
    Currency.CAD: "Canadian Dollar",
    Currency.GBP: "British Pound",
    Currency.EUR: "Euro",
    Currency.AUD: "Australian Dollar",
    Currency.NZD: "New Zealand Dollar",
}

CURRENCY_FLAGS = {
    Currency.CAD: "🇨🇦",
    Currency.GBP: "🇬🇧",
    Currency.EUR: "🇪🇺",
    Currency.AUD: "🇦🇺",
    Currency.NZD: "🇳🇿",
}

# Default currency (Canada-first)
DEFAULT_CURRENCY = Currency.CAD

# Country to currency mapping
COUNTRY_TO_CURRENCY = {
    # CAD
    "CA": Currency.CAD,
    # GBP
    "GB": Currency.GBP,
    "UK": Currency.GBP,
    # EUR
    "AT": Currency.EUR, "BE": Currency.EUR, "CY": Currency.EUR,
    "EE": Currency.EUR, "FI": Currency.EUR, "FR": Currency.EUR,
    "DE": Currency.EUR, "GR": Currency.EUR, "IE": Currency.EUR,
    "IT": Currency.EUR, "LV": Currency.EUR, "LT": Currency.EUR,
    "LU": Currency.EUR, "MT": Currency.EUR, "NL": Currency.EUR,
    "PT": Currency.EUR, "SK": Currency.EUR, "SI": Currency.EUR,
    "ES": Currency.EUR,
    # AUD
    "AU": Currency.AUD,
    # NZD
    "NZ": Currency.NZD,
}


def get_currency_for_country(country_code: str) -> Currency:
    """Get currency for a country code. Defaults to CAD."""
    return COUNTRY_TO_CURRENCY.get(country_code.upper(), DEFAULT_CURRENCY)


# ═══════════════════════════════════════════════════════════════════════════
# PRODUCTS & TIERS
# ═══════════════════════════════════════════════════════════════════════════

class ProductTier(str, Enum):
    FREE = "free"
    TRIAL = "trial"
    PRO = "pro"
    READER = "reader"
    CURATOR = "curator"
    BUNDLE = "bundle"  # PRO + Curator


@dataclass
class PricePoint:
    """Price in a specific currency."""
    currency: Currency
    monthly_cents: int
    annual_cents: int
    
    @property
    def monthly_display(self) -> str:
        symbol = CURRENCY_SYMBOLS[self.currency]
        amount = self.monthly_cents / 100
        return f"{symbol}{amount:.2f}"
    
    @property
    def annual_display(self) -> str:
        symbol = CURRENCY_SYMBOLS[self.currency]
        amount = self.annual_cents / 100
        return f"{symbol}{amount:.2f}"
    
    @property
    def annual_monthly_equivalent(self) -> str:
        """Monthly equivalent when paying annually."""
        symbol = CURRENCY_SYMBOLS[self.currency]
        amount = (self.annual_cents / 12) / 100
        return f"{symbol}{amount:.2f}"
    
    @property
    def annual_savings_percent(self) -> int:
        """Percentage saved by paying annually."""
        monthly_total = self.monthly_cents * 12
        if monthly_total == 0:
            return 0
        return round((1 - (self.annual_cents / monthly_total)) * 100)


# ═══════════════════════════════════════════════════════════════════════════
# PRICING TABLES
# ═══════════════════════════════════════════════════════════════════════════

PRO_PRICES: Dict[Currency, PricePoint] = {
    Currency.CAD: PricePoint(Currency.CAD, 499, 5000),   # $4.99/mo, $50/yr
    Currency.GBP: PricePoint(Currency.GBP, 299, 3000),   # £2.99/mo, £30/yr
    Currency.EUR: PricePoint(Currency.EUR, 349, 3500),   # €3.49/mo, €35/yr
    Currency.AUD: PricePoint(Currency.AUD, 599, 6000),   # $5.99/mo, $60/yr
    Currency.NZD: PricePoint(Currency.NZD, 649, 6500),   # $6.49/mo, $65/yr
}

CURATOR_PRICES: Dict[Currency, PricePoint] = {
    Currency.CAD: PricePoint(Currency.CAD, 199, 2000),   # $1.99/mo, $20/yr
    Currency.GBP: PricePoint(Currency.GBP, 129, 1200),   # £1.29/mo, £12/yr
    Currency.EUR: PricePoint(Currency.EUR, 149, 1500),   # €1.49/mo, €15/yr
    Currency.AUD: PricePoint(Currency.AUD, 249, 2500),   # $2.49/mo, $25/yr
    Currency.NZD: PricePoint(Currency.NZD, 279, 2800),   # $2.79/mo, $28/yr
}

BUNDLE_PRICES: Dict[Currency, PricePoint] = {
    Currency.CAD: PricePoint(Currency.CAD, 599, 6000),   # $5.99/mo, $60/yr (save $0.99/mo)
    Currency.GBP: PricePoint(Currency.GBP, 379, 3800),   # £3.79/mo, £38/yr
    Currency.EUR: PricePoint(Currency.EUR, 449, 4500),   # €4.49/mo, €45/yr
    Currency.AUD: PricePoint(Currency.AUD, 749, 7500),   # $7.49/mo, $75/yr
    Currency.NZD: PricePoint(Currency.NZD, 799, 8000),   # $7.99/mo, $80/yr
}


def get_price(tier: ProductTier, currency: Currency) -> Optional[PricePoint]:
    """Get price for a tier in a specific currency."""
    if tier == ProductTier.PRO:
        return PRO_PRICES.get(currency)
    elif tier == ProductTier.CURATOR:
        return CURATOR_PRICES.get(currency)
    elif tier == ProductTier.BUNDLE:
        return BUNDLE_PRICES.get(currency)
    return None


def get_bundle_savings(currency: Currency) -> Dict[str, any]:
    """Calculate bundle savings compared to buying separately."""
    pro = PRO_PRICES.get(currency)
    curator = CURATOR_PRICES.get(currency)
    bundle = BUNDLE_PRICES.get(currency)
    
    if not all([pro, curator, bundle]):
        return {}
    
    separate_monthly = pro.monthly_cents + curator.monthly_cents
    bundle_monthly = bundle.monthly_cents
    monthly_savings = separate_monthly - bundle_monthly
    
    separate_annual = pro.annual_cents + curator.annual_cents
    bundle_annual = bundle.annual_cents
    annual_savings = separate_annual - bundle_annual
    
    symbol = CURRENCY_SYMBOLS[currency]
    
    return {
        "monthly_savings_cents": monthly_savings,
        "monthly_savings_display": f"{symbol}{monthly_savings / 100:.2f}",
        "annual_savings_cents": annual_savings,
        "annual_savings_display": f"{symbol}{annual_savings / 100:.2f}",
    }


# ═══════════════════════════════════════════════════════════════════════════
# STRIPE PRODUCT/PRICE IDS
# ═══════════════════════════════════════════════════════════════════════════

# These would be created in Stripe Dashboard or via API
# Format: {tier}_{currency}_{interval}

STRIPE_PRICE_IDS = {
    # PRO Monthly
    "pro_cad_monthly": "price_pro_cad_monthly",
    "pro_gbp_monthly": "price_pro_gbp_monthly",
    "pro_eur_monthly": "price_pro_eur_monthly",
    "pro_aud_monthly": "price_pro_aud_monthly",
    "pro_nzd_monthly": "price_pro_nzd_monthly",
    # PRO Annual
    "pro_cad_annual": "price_pro_cad_annual",
    "pro_gbp_annual": "price_pro_gbp_annual",
    "pro_eur_annual": "price_pro_eur_annual",
    "pro_aud_annual": "price_pro_aud_annual",
    "pro_nzd_annual": "price_pro_nzd_annual",
    # Curator Monthly
    "curator_cad_monthly": "price_curator_cad_monthly",
    "curator_gbp_monthly": "price_curator_gbp_monthly",
    "curator_eur_monthly": "price_curator_eur_monthly",
    "curator_aud_monthly": "price_curator_aud_monthly",
    "curator_nzd_monthly": "price_curator_nzd_monthly",
    # Curator Annual
    "curator_cad_annual": "price_curator_cad_annual",
    "curator_gbp_annual": "price_curator_gbp_annual",
    "curator_eur_annual": "price_curator_eur_annual",
    "curator_aud_annual": "price_curator_aud_annual",
    "curator_nzd_annual": "price_curator_nzd_annual",
    # Bundle Monthly
    "bundle_cad_monthly": "price_bundle_cad_monthly",
    "bundle_gbp_monthly": "price_bundle_gbp_monthly",
    "bundle_eur_monthly": "price_bundle_eur_monthly",
    "bundle_aud_monthly": "price_bundle_aud_monthly",
    "bundle_nzd_monthly": "price_bundle_nzd_monthly",
    # Bundle Annual
    "bundle_cad_annual": "price_bundle_cad_annual",
    "bundle_gbp_annual": "price_bundle_gbp_annual",
    "bundle_eur_annual": "price_bundle_eur_annual",
    "bundle_aud_annual": "price_bundle_aud_annual",
    "bundle_nzd_annual": "price_bundle_nzd_annual",
}


def get_stripe_price_id(tier: ProductTier, currency: Currency, annual: bool = False) -> Optional[str]:
    """Get Stripe price ID for a tier/currency/interval combination."""
    interval = "annual" if annual else "monthly"
    key = f"{tier.value}_{currency.value}_{interval}"
    return STRIPE_PRICE_IDS.get(key)


# ═══════════════════════════════════════════════════════════════════════════
# TRIAL CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

TRIAL_CONFIG = {
    # 7-day PRO trial (can be triggered manually or auto at 500 words)
    "pro_trial_days": 7,
    
    # Words needed to auto-unlock trial
    "auto_trial_word_threshold": 500,
    
    # Can only trial once
    "trial_once_per_user": True,
}


# ═══════════════════════════════════════════════════════════════════════════
# FEATURE FLAGS BY TIER
# ═══════════════════════════════════════════════════════════════════════════

TIER_FEATURES = {
    ProductTier.FREE: {
        "word_limit": 500,
        "analyses_per_day": 3,
        "history_days": 0,
        "voice_evolution": False,
        "featured_eligible": False,
        "authority_eligible": False,
    },
    ProductTier.TRIAL: {
        "word_limit": 10000,  # Full PRO access during trial
        "analyses_per_day": -1,  # Unlimited
        "history_days": 30,
        "voice_evolution": True,
        "featured_eligible": False,  # Can't submit during trial
        "authority_eligible": False,
    },
    ProductTier.PRO: {
        "word_limit": 10000,
        "analyses_per_day": -1,
        "history_days": -1,  # Unlimited
        "voice_evolution": True,
        "featured_eligible": True,
        "authority_eligible": True,
    },
    ProductTier.READER: {
        "posts_per_day": -1,
        "bookmarks_max": 10,
        "reading_taste": "basic",
        "featured_access": "limited",  # 1/day
    },
    ProductTier.CURATOR: {
        "posts_per_day": -1,
        "bookmarks_max": -1,
        "reading_taste": "full",
        "featured_access": "unlimited",
        "taste_vs_voice": True,
        "export_reading_list": True,
        "featured_curator_eligible": True,
        "authority_curator_eligible": True,
    },
    ProductTier.BUNDLE: {
        # Combines PRO + Curator features
        "word_limit": 10000,
        "analyses_per_day": -1,
        "history_days": -1,
        "voice_evolution": True,
        "featured_eligible": True,
        "authority_eligible": True,
        "posts_per_day": -1,
        "bookmarks_max": -1,
        "reading_taste": "full",
        "featured_access": "unlimited",
        "taste_vs_voice": True,
        "export_reading_list": True,
        "featured_curator_eligible": True,
        "authority_curator_eligible": True,
    },
}


def get_tier_features(tier: ProductTier) -> Dict:
    """Get feature flags for a tier."""
    return TIER_FEATURES.get(tier, TIER_FEATURES[ProductTier.FREE])


# ═══════════════════════════════════════════════════════════════════════════
# REFUND POLICY
# ═══════════════════════════════════════════════════════════════════════════

REFUND_POLICY = {
    "refunds_allowed": False,
    "policy_text": """
Quirrely subscriptions are non-refundable. By subscribing, you agree that:

• All payments are final and non-refundable
• You may cancel at any time, but no refunds will be issued
• Cancelled subscriptions remain active until the end of the billing period
• Annual subscriptions are charged in full and are not pro-rated

If you have questions, contact support@quirrely.com before subscribing.
""".strip(),
}


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def get_all_prices_for_display(currency: Currency) -> Dict:
    """Get all prices formatted for display in a specific currency."""
    pro = PRO_PRICES.get(currency)
    curator = CURATOR_PRICES.get(currency)
    bundle = BUNDLE_PRICES.get(currency)
    savings = get_bundle_savings(currency)
    
    return {
        "currency": currency.value,
        "currency_symbol": CURRENCY_SYMBOLS[currency],
        "currency_name": CURRENCY_NAMES[currency],
        "currency_flag": CURRENCY_FLAGS[currency],
        "pro": {
            "monthly": pro.monthly_display if pro else None,
            "annual": pro.annual_display if pro else None,
            "annual_monthly": pro.annual_monthly_equivalent if pro else None,
            "annual_savings_percent": pro.annual_savings_percent if pro else 0,
        },
        "curator": {
            "monthly": curator.monthly_display if curator else None,
            "annual": curator.annual_display if curator else None,
            "annual_monthly": curator.annual_monthly_equivalent if curator else None,
            "annual_savings_percent": curator.annual_savings_percent if curator else 0,
        },
        "bundle": {
            "monthly": bundle.monthly_display if bundle else None,
            "annual": bundle.annual_display if bundle else None,
            "annual_monthly": bundle.annual_monthly_equivalent if bundle else None,
            "annual_savings_percent": bundle.annual_savings_percent if bundle else 0,
            "monthly_savings": savings.get("monthly_savings_display"),
            "annual_savings": savings.get("annual_savings_display"),
        },
    }


# ═══════════════════════════════════════════════════════════════════════════
# STRIPE SETUP SCRIPT (Run once to create products/prices)
# ═══════════════════════════════════════════════════════════════════════════

def create_stripe_products_and_prices():
    """
    Create all Stripe products and prices.
    Run this once during initial setup.
    
    Returns dict of created price IDs to update STRIPE_PRICE_IDS.
    """
    import stripe
    stripe.api_key = STRIPE_SECRET_KEY
    
    created_prices = {}
    
    # Create Products
    products = {
        "pro": stripe.Product.create(
            name="Quirrely PRO",
            description="Full writing analysis with 10,000 words/day, voice evolution, and Featured Writer eligibility.",
        ),
        "curator": stripe.Product.create(
            name="Quirrely Curator",
            description="Full reading taste analysis, unlimited bookmarks, and Featured Curator eligibility.",
        ),
        "bundle": stripe.Product.create(
            name="Quirrely PRO + Curator",
            description="Complete Quirrely experience: writing analysis, reading taste, and both Featured paths.",
        ),
    }
    
    # Create Prices for each product/currency/interval
    for tier_name, product in products.items():
        if tier_name == "pro":
            prices = PRO_PRICES
        elif tier_name == "curator":
            prices = CURATOR_PRICES
        else:
            prices = BUNDLE_PRICES
        
        for currency, price_point in prices.items():
            # Monthly
            monthly_price = stripe.Price.create(
                product=product.id,
                unit_amount=price_point.monthly_cents,
                currency=currency.value,
                recurring={"interval": "month"},
            )
            key = f"{tier_name}_{currency.value}_monthly"
            created_prices[key] = monthly_price.id
            
            # Annual
            annual_price = stripe.Price.create(
                product=product.id,
                unit_amount=price_point.annual_cents,
                currency=currency.value,
                recurring={"interval": "year"},
            )
            key = f"{tier_name}_{currency.value}_annual"
            created_prices[key] = annual_price.id
    
    return created_prices


if __name__ == "__main__":
    # Display pricing table
    print("QUIRRELY PRICING\n")
    for currency in Currency:
        prices = get_all_prices_for_display(currency)
        print(f"{CURRENCY_FLAGS[currency]} {currency.value.upper()}")
        print(f"  PRO: {prices['pro']['monthly']}/mo or {prices['pro']['annual']}/yr ({prices['pro']['annual_savings_percent']}% off)")
        print(f"  Curator: {prices['curator']['monthly']}/mo or {prices['curator']['annual']}/yr")
        print(f"  Bundle: {prices['bundle']['monthly']}/mo (save {prices['bundle']['monthly_savings']}/mo)")
        print()
