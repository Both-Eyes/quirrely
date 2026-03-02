# LNCP v5.1.1 Operations Runbook

## Quick Start

### Prerequisites
- Python 3.10+
- SQLite3
- Node.js 18+ (for frontend)

### Installation
```bash
cd lncp-web-app
pip install -r requirements.txt  # If exists
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Verify Installation
```bash
python3 -c "from lncp.engine.tokens import ALL_TOKENS; print(f'Tokens: {len(ALL_TOKENS)}')"
python3 -c "from lncp.meta.command_center import get_command_center; print('Command Center: OK')"
```

---

## Daily Operations

### Morning Health Check
```bash
# Run E2E2E validation
python3 lncp/meta/e2e2e_validator.py

# Expected output:
# Pass Rate: 100.0%
# 🚀 PRODUCTION READY
```

### Review Proposals
```python
from lncp.meta.command_center import get_command_center

cc = get_command_center()
for p in cc.proposals[:5]:
    print(f"[{p.priority_score}] {p.title}")
    print(f"    Domain: {p.domain.value}, Tier: {p.tier.value}")
    print(f"    Impact: UX +{p.impact.ux_percent}%, MRR +${p.impact.mrr_dollars}")
```

### Check Alerts
```python
from lncp.meta.command_center import get_command_center, Domain

cc = get_command_center()
for domain in cc.domains.values():
    for alert in domain.alerts:
        if alert.severity.value in ["critical", "warning"]:
            print(f"[{alert.severity.value.upper()}] {alert.title}")
```

### Review Metrics
```python
from lncp.meta.stripe_integration import ProductionRevenueObserver
from lncp.meta.gsc_integration import ProductionGSCObserver

# Revenue
revenue = ProductionRevenueObserver().get_metrics()
print(f"MRR: ${revenue['mrr']:,.0f}")
print(f"Churn: {revenue['churn_rate']:.1%}")

# Search
gsc = ProductionGSCObserver().get_site_metrics()
print(f"Impressions: {gsc.total_impressions:,}")
print(f"CTR: {gsc.avg_ctr:.2%}")
```

---

## Weekly Operations

### Full System Audit
```bash
# Run master test
python3 lncp/tests/master_validation_final.py

# Export system state
python3 -c "
from lncp.meta.command_center import get_command_center
import json
cc = get_command_center()
with open('weekly_state.json', 'w') as f:
    json.dump(cc.get_full_state(), f, indent=2)
print('State exported to weekly_state.json')
"
```

### Review Trust Scores
```python
from lncp.meta.trust_store import get_trust_store

store = get_trust_store()
summary = store.get_summary()
for action, data in summary.get('actions', {}).items():
    print(f"{action}: trust={data['trust_score']:.2f}, success={data['success_rate']:.1%}")
```

### Check Activation Funnel
```python
from lncp.meta.activation import get_activation_tracker

tracker = get_activation_tracker()
funnel = tracker.get_activation_funnel()
print(f"Signup → Analysis: {funnel.get('has_analysis_pct', 0):.1%}")
print(f"Analysis → View: {funnel.get('has_profile_view_pct', 0):.1%}")
print(f"View → Activated: {funnel.get('activated_pct', 0):.1%}")
```

### Review Lifecycle Distribution
```python
from lncp.meta.lifecycle import get_lifecycle_manager

manager = get_lifecycle_manager()
dist = manager.get_state_distribution()
for state, count in sorted(dist.items(), key=lambda x: -x[1]):
    print(f"{state.name}: {count}")
```

---

## Proposal Workflow

### 1. Review Pending Proposals
```python
from lncp.meta.command_center import get_command_center

cc = get_command_center()
pending = [p for p in cc.proposals if p.status.value == "pending"]
print(f"{len(pending)} proposals pending review")
```

### 2. Evaluate High-Priority Proposals
```python
for p in cc.proposals[:3]:
    print(f"\n{'='*50}")
    print(f"ID: {p.id}")
    print(f"Title: {p.title}")
    print(f"Priority: {p.priority_score}/100")
    print(f"Domain: {p.domain.value}")
    print(f"Tier: {p.tier.value}")
    print(f"Confidence: {p.confidence:.0%}")
    print(f"Trust: {p.trust_score:.2f}")
    print(f"Impact:")
    print(f"  UX: +{p.impact.ux_percent}%")
    print(f"  Health: +{p.impact.health_percent}%")
    print(f"  MRR: +${p.impact.mrr_dollars}")
    print(f"Evidence: {p.evidence}")
```

### 3. Approve Proposal
```python
result = cc.approve_proposal("prop_001", approved_by="your_name")
if result.get("success"):
    print(f"✓ Approved: {result['proposal']['title']}")
    print(f"  Injection tier: {result['injection_tier']}")
```

### 4. Reject Proposal
```python
result = cc.reject_proposal("prop_002", reason="Risk exceeds benefit")
print("Rejected and logged for learning")
```

### 5. Execute Immediate Injections
```python
# Only for approved immediate-tier proposals
results = cc.execute_immediate()
for r in results:
    print(f"Executed: {r['title']} - {r['status']}")
```

---

## Injection Tiers

### 🟢 Immediate (< 1 hour)
- Low risk changes
- Examples: CTA color, copy tweaks, threshold adjustments
- Process: Approve → Execute immediately

### 🟡 24-Hour (Next deploy)
- Medium risk changes
- Examples: A/B test variants, reminder frequency
- Process: Approve → Queue → Deploy with next release

### 🔴 30-Day (Next sprint)
- High risk changes
- Examples: Scoring weights, new profiles, major features
- Process: Approve → Full review → Sprint planning → Testing → Deploy

---

## Troubleshooting

### E2E2E Validation Fails

**Symptom:** Critical failures in validation
```
Critical failures: 1  (must be 0 to deploy)
```

**Steps:**
1. Check which phase failed
2. Run individual phase test
3. Check logs for specific error
4. Fix and re-validate

```python
from lncp.meta.e2e2e_validator import E2E2EValidator

v = E2E2EValidator()
v.validate_core_engine()      # Run individual phase
v.validate_event_pipeline()
v.validate_command_center()
```

### Events Not Collecting

**Symptom:** `collector.collect()` returns empty list

**Steps:**
1. Check events directory exists
2. Verify EventBus flushed
3. Check file permissions

```python
import os
from lncp.meta.events import EventBus, EventCollector

# Check directory
events_dir = "/path/to/events"
print(f"Directory exists: {os.path.exists(events_dir)}")
print(f"Files: {os.listdir(events_dir)}")

# Force flush
bus = EventBus(events_dir=events_dir)
bus.flush()
```

### Command Center Not Loading Proposals

**Symptom:** `cc.proposals` is empty

**Steps:**
1. Re-initialize command center
2. Check domain states

```python
from lncp.meta.command_center import CommandCenter

# Create fresh instance
cc = CommandCenter()
print(f"Domains: {len(cc.domains)}")
print(f"Proposals: {len(cc.proposals)}")
```

### Database Errors

**Symptom:** SQLite errors

**Steps:**
1. Check database files exist
2. Verify integrity
3. Backup and recreate if needed

```python
from lncp.meta.persistence import PersistenceManager

pm = PersistenceManager("/path/to/data")
integrity = pm.check_integrity()
print(f"Status: {integrity['status']}")
```

---

## Monitoring

### Key Metrics to Watch

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| E2E2E Pass Rate | 100% | < 95% |
| Activation Rate | 30%+ | < 25% |
| Trial Conversion | 25%+ | < 20% |
| Churn Rate | < 3% | > 4% |
| Engine Accuracy | 85%+ | < 80% |
| Auto-Apply Rate | 30%+ | < 20% |

### Health Check Script
```python
#!/usr/bin/env python3
"""Daily health check script"""

from lncp.meta.command_center import get_command_center
from lncp.meta.stripe_integration import ProductionRevenueObserver
from lncp.meta.activation import get_activation_tracker

def health_check():
    print("=" * 50)
    print("LNCP HEALTH CHECK")
    print("=" * 50)
    
    # Command Center
    cc = get_command_center()
    summary = cc.get_summary()
    print(f"\nCommand Center: {summary['status']}")
    print(f"  Alerts: {summary['alerts']['critical']} critical, {summary['alerts']['warning']} warning")
    print(f"  Proposals: {summary['proposals']['pending']} pending")
    
    # Revenue
    revenue = ProductionRevenueObserver().get_metrics()
    print(f"\nRevenue:")
    print(f"  MRR: ${revenue['mrr']:,.0f}")
    print(f"  Churn: {revenue['churn_rate']:.1%}")
    
    # Activation
    tracker = get_activation_tracker()
    rate = tracker.get_activation_rate()
    print(f"\nActivation:")
    print(f"  Rate: {rate:.1%}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    health_check()
```

---

## Backup & Recovery

### Daily Backup
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups/lncp/$DATE"
mkdir -p $BACKUP_DIR

# Database files
cp data/*.db $BACKUP_DIR/

# System state
python3 -c "
from lncp.meta.command_center import get_command_center
import json
cc = get_command_center()
with open('$BACKUP_DIR/system_state.json', 'w') as f:
    json.dump(cc.get_full_state(), f, indent=2)
"

echo "Backup complete: $BACKUP_DIR"
```

### Recovery
```bash
# Restore databases
cp /backups/lncp/YYYYMMDD/*.db data/

# Verify
python3 lncp/meta/e2e2e_validator.py
```

---

## Emergency Procedures

### System Degradation
1. Run E2E2E validation to identify failing component
2. Check recent changes in audit trail
3. Rollback if needed
4. Notify stakeholders

### Critical Alert
1. Acknowledge alert in Command Center
2. Assess impact and urgency
3. Create incident ticket
4. Execute mitigation
5. Post-mortem

### Complete System Failure
1. Stop all services
2. Restore from last known good backup
3. Run E2E2E validation
4. Restart services one by one
5. Monitor closely for 24 hours

---

## Contacts

| Role | Contact |
|------|---------|
| System Owner | [Your contact] |
| On-Call | [Rotation schedule] |
| Escalation | [Management contact] |
