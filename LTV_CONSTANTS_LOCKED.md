# SENTENSE — LOCKED LTV CONSTANTS

**Locked:** 2026-02-10  
**Discount Rate:** 10% annual

---

## 🔒 LOCKED VALUES

| Segment | LTV (Discounted) |
|---------|------------------|
| Monthly | **$27.61** |
| Annual | **$85.71** |
| **Blended** | **$58.29** |

---

## Derivation

### Monthly Subscribers (47.2% of mix)

```
Price:    $2.99/mo
Churn:    10%/mo
Discount: 0.83%/mo (10% annual ÷ 12)

LTV = Price / (Churn + Discount)
    = $2.99 / (0.10 + 0.0083)
    = $2.99 / 0.1083
    = $27.61
```

### Annual Subscribers (52.8% of mix)

```
Price:    $30/yr
Churn:    25%/yr (75% renewal)
Discount: 10%/yr

LTV = Price / (Churn + Discount)
    = $30 / (0.25 + 0.10)
    = $30 / 0.35
    = $85.71
```

### Blended LTV

```
= (Monthly % × Monthly LTV) + (Annual % × Annual LTV)
= (0.472 × $27.61) + (0.528 × $85.71)
= $13.03 + $45.25
= $58.29
```

---

## Use in Simulations

All future funnel simulations must use:

```javascript
const LTV = {
  MONTHLY: 27.61,
  ANNUAL: 85.71,
  BLENDED: 58.29
};
```

---

## Comparison: Discounted vs Undiscounted

| Segment | Undiscounted | Discounted | Difference |
|---------|--------------|------------|------------|
| Monthly | $29.90 | $27.61 | -8% |
| Annual | $120.00 | $85.71 | -29% |
| Blended | $77.47 | $58.29 | -25% |

Discounting reduces blended LTV by 25%, giving more conservative projections.

---

*Locked: 2026-02-10*
