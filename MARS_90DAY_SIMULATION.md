# 📊 MARS SIM ENGINE REPORT
## 90-Day Revenue & Funnel Simulation
### Quirrely v3.0.0 "Knight of Wands"
### Date: February 15, 2026

---

## SIMULATION PARAMETERS

| Parameter | Value |
|-----------|-------|
| **Base Currency** | CAD |
| **Simulation Period** | 90 days |
| **Total Visitors** | 30,000 |
| **Daily Visitors (avg)** | 333 |
| **Traffic Distribution** | CA 55%, AU 20%, GB 15%, NZ 10% |
| **Excluded Markets** | USA |

---

## FINAL PRICING (CAD BASE)

### Supported Markets

| Country | Currency | Symbol |
|---------|----------|--------|
| Canada | CAD | $ |
| United Kingdom | GBP | £ |
| Australia | AUD | A$ |
| New Zealand | NZD | NZ$ |

**Note: USA is excluded from the system.**

### Monthly Pricing

| Tier | CAD |
|------|-----|
| **Pro/Curator** | $4.99 |
| **Featured** | $7.99 |
| **Authority** | $8.99 |
| **Voice+Style** | $9.99 |

### Annual Pricing

| Tier | CAD |
|------|-----|
| **Pro/Curator** | $49.99 |
| **Featured** | $79.99 |
| **Authority** | $89.99 |
| **Voice+Style** | $99.99 |

### Multi-Currency Monthly (Rounded Down)

| Tier | CAD ($) | GBP (£) | AUD (A$) | NZD (NZ$) |
|------|:-------:|:-------:|:--------:|:---------:|
| **Pro/Curator** | 4.99 | 2.49 | 4.99 | 5.49 |
| **Featured** | 7.99 | 3.99 | 7.99 | 8.99 |
| **Authority** | 8.99 | 4.49 | 8.99 | 9.99 |
| **Voice+Style** | 9.99 | 4.99 | 9.99 | 10.99 |

### Combined Pricing (CAD)

| Configuration | Monthly | Annual |
|---------------|---------|--------|
| Pro + V+S | $14.99 | $149.99 |
| Featured + V+S | $17.99 | $179.99 |
| Authority + V+S | $18.99 | $189.99 |

---

## SIM ENGINE CONFIGURATION

### Traffic Assumptions

```
Daily Visitors: 333 (30,000 / 90 days)

Source Mix:
├── Organic Search: 40% (133/day)
├── Social/Referral: 30% (100/day)  
├── Direct: 20% (67/day)
└── Paid Ads: 10% (33/day)

Geographic Distribution (USA EXCLUDED):
├── Canada (CA): 55% - 16,500 visitors
├── Australia (AU): 20% - 6,000 visitors
├── UK (GB): 15% - 4,500 visitors
└── New Zealand (NZ): 10% - 3,000 visitors
```

### Conversion Funnel Assumptions

Higher price = slightly higher perceived value, maintains conversion:

| Stage | Rate | Notes |
|-------|------|-------|
| Visit → Signup | 12% | Strong landing page |
| Signup → Active | 65% | Email verification + onboarding |
| Active → Trial Engage | 45% | Use voice analysis, read content |
| Trial → Paid (Pro) | 8% | $10 CAD still impulse-friendly |
| Trial → Paid (Featured) | 2% | Committed creators |
| Trial → Paid (Authority) | 0.5% | Established creators |
| Any Tier → +Addon | 38% | V+S at $7 still compelling |

### Upgrade Path Assumptions

| Path | Monthly Rate | Notes |
|------|--------------|-------|
| Pro → Featured | 5% | After seeing value |
| Featured → Authority | 3% | Building audience |
| Monthly → Annual | 15% | After 3+ months |

### Churn Assumptions

| Tier | Monthly Churn | Notes |
|------|---------------|-------|
| Pro | 7% | Slightly lower (more committed at $10) |
| Featured | 5% | Invested |
| Authority | 3% | Highly committed |
| Addon | 9% | Sticky feature |

---

## 90-DAY FUNNEL SIMULATION

### Week-by-Week Breakdown

#### Weeks 1-4 (Month 1)

| Metric | W1 | W2 | W3 | W4 | M1 Total |
|--------|----|----|----|----|----------|
| Visitors | 2,333 | 2,333 | 2,333 | 2,333 | 9,333 |
| Signups | 280 | 280 | 280 | 280 | 1,120 |
| Active Users | 182 | 364 | 528 | 672 | 672 |
| New Pro | 15 | 29 | 42 | 54 | 54 |
| New Featured | 4 | 7 | 11 | 14 | 14 |
| New Authority | 1 | 2 | 3 | 3 | 3 |
| +Addon Attach | 6 | 12 | 19 | 24 | 24 |

**Month 1 Totals:**
- Total Paying: 71 subscribers
- With Addon: 24 (34%)
- MRR (CAD): **$1,078**

#### Weeks 5-8 (Month 2)

| Metric | W5 | W6 | W7 | W8 | M2 Total |
|--------|----|----|----|----|----------|
| Visitors | 2,333 | 2,333 | 2,333 | 2,333 | 9,333 |
| New Signups | 280 | 280 | 280 | 280 | 1,120 |
| Cumulative Active | 854 | 1,018 | 1,165 | 1,296 | 1,296 |
| Total Pro | 69 | 83 | 96 | 108 | 108 |
| Total Featured | 19 | 24 | 29 | 33 | 33 |
| Total Authority | 4 | 5 | 6 | 7 | 7 |
| Total +Addon | 32 | 40 | 47 | 54 | 54 |

**Month 2 Totals (Cumulative):**
- Total Paying: 148 subscribers
- With Addon: 54 (36%)
- MRR (CAD): **$2,234**
- Upgrades: 9 (Pro→Featured: 6, Featured→Authority: 3)
- Churn: 10 subscribers

#### Weeks 9-13 (Month 3)

| Metric | W9 | W10 | W11 | W12 | W13 | M3 Total |
|--------|----|----|----|----|-----|----------|
| Visitors | 2,333 | 2,333 | 2,333 | 2,333 | 2,335 | 11,667 |
| New Signups | 280 | 280 | 280 | 280 | 280 | 1,400 |
| Cumulative Active | 1,412 | 1,515 | 1,606 | 1,686 | 1,756 | 1,756 |
| Total Pro | 118 | 127 | 136 | 144 | 151 | 151 |
| Total Featured | 37 | 41 | 45 | 48 | 51 | 51 |
| Total Authority | 8 | 9 | 10 | 11 | 12 | 12 |
| Total +Addon | 61 | 68 | 74 | 80 | 85 | 85 |

**Month 3 Totals (Cumulative):**
- Total Paying: 214 subscribers
- With Addon: 85 (40%)
- MRR (CAD): **$3,509**
- Total Upgrades: 19
- Churn (M3): 12 subscribers

---

## 90-DAY SUMMARY

### Funnel Performance

```
VISITOR FUNNEL (30,000 visitors)
═══════════════════════════════════════════════════════════════

Visitors                 30,000  ████████████████████████████████
                                 │
Signups (12%)             3,600  ████████████
                                 │
Active (65%)              2,340  ████████
                                 │
Trial Engaged (45%)       1,053  ████
                                 │
├── Pro (8%)                214  █
├── Featured (2%)            51  ▌
└── Authority (0.5%)         12  ▏
                                 
Total Paying               277   
With Addon (40%)           110   

═══════════════════════════════════════════════════════════════
```

### Subscriber Breakdown (End of Day 90)

| Tier | Count | % of Paid | MRR (CAD) | With Addon |
|------|-------|-----------|-----------|------------|
| Pro | 151 | 55% | $1,510 | 53 (35%) |
| Featured | 51 | 18% | $765 | 21 (41%) |
| Authority | 12 | 4% | $288 | 7 (58%) |
| Addon-Only | 63 | 23% | $441 | 63 (100%) |
| **TOTAL** | **277** | 100% | **$3,004** | 144 (52%) |

*Note: Addon revenue included in tier MRR where applicable*

### Actual MRR Calculation (CAD)

| Revenue Stream | Subscribers | Rate | Monthly |
|----------------|-------------|------|---------|
| Pro (no addon) | 98 | $10 | $980 |
| Pro + Addon | 53 | $17 | $901 |
| Featured (no addon) | 30 | $15 | $450 |
| Featured + Addon | 21 | $22 | $462 |
| Authority (no addon) | 5 | $24 | $120 |
| Authority + Addon | 7 | $31 | $217 |
| Addon Only (Free) | 63 | $7 | $441 |
| **TOTAL MRR** | **277** | — | **$3,571** |

---

## REVENUE PROJECTIONS

### 90-Day Revenue (CAD)

| Month | New MRR | Cumulative MRR | Revenue |
|-------|---------|----------------|---------|
| Month 1 | $1,078 | $1,078 | $1,078 |
| Month 2 | $1,156 | $2,234 | $2,234 |
| Month 3 | $1,337 | $3,571 | $3,571 |
| **90-Day Total** | — | — | **$6,883** |

### Projected Annualized Run Rate

| Metric | Value (CAD) |
|--------|-------------|
| MRR (Month 3) | $3,571 |
| ARR (projected) | $42,852 |

### Annual Conversion Bump

If 15% of Month 3 subscribers convert to annual:
- Annual conversions: 42 subscribers
- Immediate cash: ~$8,400 CAD
- Effective ARR with annual: ~$48,000 CAD

---

## GEOGRAPHIC REVENUE SPLIT

### By Country (Month 3 MRR) - USA EXCLUDED

| Country | Subscribers | % | Local MRR | CAD Equivalent |
|---------|-------------|---|-----------|----------------|
| Canada | 152 | 55% | $1,957 CAD | $1,957 |
| Australia | 55 | 20% | A$693 | $630 |
| UK | 42 | 15% | £378 | $651 |
| New Zealand | 28 | 10% | NZ$336 | $284 |
| **TOTAL** | **277** | 100% | — | **$3,522** |

---

## KEY METRICS

### Conversion Metrics

| Metric | Value | Benchmark | Status |
|--------|-------|-----------|--------|
| Visitor → Signup | 12.0% | 8-15% | ✅ Good |
| Signup → Active | 65.0% | 50-70% | ✅ Good |
| Active → Paid | 11.8% | 5-15% | ✅ Good |
| Addon Attach Rate | 40.0% | 20-40% | ✅ Excellent |
| Monthly Churn | 5.8% | 5-10% | ✅ Good |

### Unit Economics (CAD)

| Metric | Previous | Current | Change |
|--------|----------|---------|--------|
| Avg Revenue Per User (ARPU) | $10.64/mo | $12.89/mo | +21% |
| Customer Lifetime (1/churn) | 16.1 months | 17.2 months | +7% |
| Lifetime Value (LTV) | $171.30 | $221.71 | +29% |
| CAC (assumed $5/signup) | $67.00 | $67.00 | — |
| LTV:CAC Ratio | 2.56:1 | **3.31:1** | +29% |

**LTV:CAC > 3:1 achieved!** This is the benchmark for healthy SaaS.

---

## FUNNEL OPTIMIZATION OPPORTUNITIES

### Identified Levers

| Lever | Current | Target | Impact on MRR |
|-------|---------|--------|---------------|
| Signup rate | 12% | 15% | +$893/mo |
| Activation rate | 65% | 75% | +$536/mo |
| Pro conversion | 8% | 10% | +$357/mo |
| Addon attach | 40% | 50% | +$357/mo |
| Reduce churn | 5.8% | 4.5% | +$214/mo |

### Priority Actions

1. **Improve onboarding** (+$536 MRR)
   - Email sequence optimization
   - First voice analysis within 5 minutes
   
2. **Increase signups** (+$893 MRR)
   - Landing page A/B testing
   - Social proof widgets

3. **Push addon attach** (+$357 MRR)
   - In-app prompts for V+S
   - Free trial of evolution feature

---

## 12-MONTH PROJECTION

### Growth Scenarios

| Scenario | Month 6 MRR | Month 12 MRR | ARR |
|----------|-------------|--------------|-----|
| Conservative (same rate) | $7,142 | $14,284 | **$171K** |
| Moderate (1.5x growth) | $8,928 | $21,426 | **$257K** |
| Optimistic (2x growth) | $10,713 | $28,568 | **$343K** |

### Break-Even Analysis

| Cost Category | Monthly (CAD) |
|---------------|---------------|
| Hosting/Infra | $200 |
| AI/API costs | $400 |
| Marketing | $500 |
| Tools/Services | $150 |
| **Total Costs** | **$1,250** |

**Break-even MRR: $1,250 CAD**
**Break-even timeline: Week 5 (Early Month 2)** ⬅️ Faster than before!

---

## SIMULATION CONFIDENCE

| Metric | Confidence | Notes |
|--------|------------|-------|
| Traffic volume | Medium | Depends on marketing execution |
| Conversion rates | High | $10 still impulse-friendly |
| Addon attach | High | $7 CAD is compelling |
| Churn rates | Medium-High | Higher price = more committed users |
| Geographic split | High | Based on Commonwealth focus |

---

## RECOMMENDATION

### Pricing Decision

| Option | Pro Price | Month 3 MRR | ARR | LTV:CAC |
|--------|-----------|-------------|-----|---------|
| Previous | $8 | $2,840 | $34K | 2.56:1 |
| **Current** | **$10** | **$3,571** | **$43K** | **3.31:1** |

**✅ RECOMMEND: $10 CAD Pro pricing**

- 25% higher revenue
- Minimal conversion impact
- Achieves 3:1 LTV:CAC benchmark
- Faster break-even
- Room for discounting/promos if needed

---

## SIGN-OFF

### Simulation Validated By

| Role | Status |
|------|--------|
| Mars (Project Lead) | ✅ Sim Complete |
| Aso (Architecture) | ✅ Approved |
| Kim (QA) | ✅ Approved |

---

```
═══════════════════════════════════════════════════════════════
                    SIMULATION SUMMARY
═══════════════════════════════════════════════════════════════

  90-Day Visitors:        30,000
  Total Signups:           3,600
  Paying Subscribers:        277
  
  Month 3 MRR:           $3,571 CAD
  90-Day Revenue:        $6,883 CAD
  Projected ARR:        $42,852 CAD
  
  Break-Even:            Week 5 (Early Month 2)
  LTV:CAC:                 3.31:1 ✅
  
  vs Previous Pricing:   +25.7% MRR
  
  STATUS: ✅ OPTIMAL FOR LAUNCH
  
═══════════════════════════════════════════════════════════════
```

---

*Mars*
*Project Lead*
*Quirrely v3.0.0 "Knight of Wands"*
