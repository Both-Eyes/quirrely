# PHASE 1: PRICING & PAYMENTS IMPLEMENTATION
## Quirrely Payment System

**Date:** February 12, 2026  
**Status:** ✅ IMPLEMENTED

---

## Decisions Made

| Decision | Choice |
|----------|--------|
| **Processor** | Stripe |
| **Subscription** | Monthly + Annual (discount) |
| **Trial** | All options (FREE is trial + 7-day PRO trial + auto-unlock at 500 words) |
| **Bundle** | $5.99 CAD/mo (save $0.99/mo) |
| **Grace Period** | 2 days retry, keep access |
| **Refunds** | No refunds, clear terms |
| **Currency** | CAD/GBP/EUR/AUD/NZD — **NEVER USD** |
| **Default** | CAD (Canada-first) |
| **Fallback** | User chooses via currency selector |

---

## Supported Currencies

| Currency | Flag | Symbol | Markets |
|----------|------|--------|---------|
| 🇨🇦 CAD | Canadian Dollar | $ | Canada (default) |
| 🇬🇧 GBP | British Pound | £ | UK |
| 🇪🇺 EUR | Euro | € | Eurozone (19 countries) |
| 🇦🇺 AUD | Australian Dollar | $ | Australia |
| 🇳🇿 NZD | New Zealand Dollar | $ | New Zealand |

---

## Pricing Structure

### PRO (Writer)

| Currency | Monthly | Annual | Savings |
|----------|---------|--------|---------|
| 🇨🇦 CAD | $4.99 | $50 | ~17% |
| 🇬🇧 GBP | £2.99 | £30 | ~16% |
| 🇪🇺 EUR | €3.49 | €35 | ~16% |
| 🇦🇺 AUD | $5.99 | $60 | ~17% |
| 🇳🇿 NZD | $6.49 | $65 | ~17% |

### Curator (Reader)

| Currency | Monthly | Annual | Savings |
|----------|---------|--------|---------|
| 🇨🇦 CAD | $1.99 | $20 | ~16% |
| 🇬🇧 GBP | £1.29 | £12 | ~22% |
| 🇪🇺 EUR | €1.49 | €15 | ~16% |
| 🇦🇺 AUD | $2.49 | $25 | ~16% |
| 🇳🇿 NZD | $2.79 | $28 | ~16% |

### Bundle (PRO + Curator)

| Currency | Monthly | Annual | Monthly Savings |
|----------|---------|--------|-----------------|
| 🇨🇦 CAD | $5.99 | $60 | $0.99/mo |
| 🇬🇧 GBP | £3.79 | £38 | £0.49/mo |
| 🇪🇺 EUR | €4.49 | €45 | €0.49/mo |
| 🇦🇺 AUD | $7.49 | $75 | $0.99/mo |
| 🇳🇿 NZD | $7.99 | $80 | $1.29/mo |

---

## Trial System

| Trigger | Trial Type | Duration |
|---------|------------|----------|
| User clicks "Start Trial" | Manual | 7 days PRO |
| User writes 500 words | Auto-unlock | 7 days PRO |
| Promo code | Code-based | Varies |
| Referral | Referral | 7 days PRO |

**Rules:**
- One trial per user (ever)
- Full PRO access during trial
- Can't submit Featured piece during trial
- Trial converts to FREE if not upgraded

---

## Payment Failure Handling

| Day | Status | Access |
|-----|--------|--------|
| 0 | Payment fails | Full access (grace period starts) |
| 1 | Retry attempt | Full access |
| 2 | Final retry | Full access ends at midnight |
| 3+ | Subscription cancelled | Downgrades to FREE |

---

## Refund Policy

**No refunds. Clear terms.**

> Quirrely subscriptions are non-refundable. By subscribing, you agree that:
> - All payments are final and non-refundable
> - You may cancel at any time, but no refunds will be issued
> - Cancelled subscriptions remain active until the end of the billing period
> - Annual subscriptions are charged in full and are not pro-rated

---

## Files Created

### Backend

| File | Purpose |
|------|---------|
| `stripe_config.py` | Stripe setup, products, prices, currencies |
| `payments_api.py` | Checkout, webhooks, subscription management |
| `schema_payments.sql` | Subscriptions, trials, payment history |

### Frontend

| File | Purpose |
|------|---------|
| `pricing-components.js` | Pricing cards, currency selector, trial banner |

---

## API Endpoints

### Pricing

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v2/payments/pricing` | Get pricing in user's currency |
| GET | `/api/v2/payments/pricing/all` | Get all currencies |
| GET | `/api/v2/payments/refund-policy` | Get refund policy |

### Checkout

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v2/payments/checkout` | Create checkout session |
| GET | `/api/v2/payments/checkout/{id}/status` | Check checkout status |

### Subscription

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v2/payments/subscription` | Get current subscription |
| POST | `/api/v2/payments/subscription/cancel` | Cancel at period end |
| POST | `/api/v2/payments/subscription/reactivate` | Reactivate cancelled |
| POST | `/api/v2/payments/subscription/change` | Upgrade/downgrade |

### Trial

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v2/payments/trial/status` | Get trial status |
| POST | `/api/v2/payments/trial/start` | Start 7-day trial |

### Billing

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v2/payments/tier` | Get current tier + features |
| POST | `/api/v2/payments/billing-portal` | Stripe billing portal |
| POST | `/api/v2/payments/webhook` | Stripe webhooks |

---

## Frontend Components

| Component | Purpose |
|-----------|---------|
| `<currency-selector>` | Currency picker (5 options) |
| `<pricing-card>` | Individual tier card |
| `<pricing-page>` | Full pricing page |
| `<trial-banner>` | Trial status/unlock banner |
| `<subscription-status>` | Current subscription display |

---

## Database Tables

| Table | Purpose |
|-------|---------|
| `subscriptions` | Active subscriptions |
| `trials` | Trial history |
| `payment_history` | All payments |
| `stripe_events` | Webhook audit log |

---

## Stripe Products to Create

Run `create_stripe_products_and_prices()` in `stripe_config.py` to create:

- **3 Products:** PRO, Curator, Bundle
- **30 Prices:** 3 tiers × 5 currencies × 2 intervals

---

## Excluded (by design)

- ❌ USD (never)
- ❌ Refunds (policy)
- ❌ Free trials for existing subscribers
- ❌ Multiple active subscriptions per user

---

## Phase 1 Complete ✅

Ready for **Phase 2: Authentication & User Management**
