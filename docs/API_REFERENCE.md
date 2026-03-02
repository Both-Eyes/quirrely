# LNCP v5.1.1 API Reference

## Core Engine API

### Tokens

```python
from lncp.engine.tokens import ALL_TOKENS, get_token, Token, TokenCategory

# Get all tokens
tokens = ALL_TOKENS  # List[Token], 50 items

# Get specific token
token = get_token("assertive")  # Token or None

# Token attributes
token.id          # str: unique identifier
token.name        # str: display name  
token.category    # TokenCategory enum
token.weight      # float: importance weight
token.description # str: explanation

# Categories
TokenCategory.STRUCTURE    # Document structure tokens
TokenCategory.COMPLEXITY   # Complexity tokens
TokenCategory.RHYTHM       # Rhythm and flow tokens
TokenCategory.PERSPECTIVE  # Point of view tokens
TokenCategory.TONE         # Emotional tone tokens
```

### Profiles

```python
from lncp.engine.profiles import ALL_PROFILES, get_profile, Profile

# Get all profiles
profiles = ALL_PROFILES  # List[Profile], 40 items

# Get specific profile
profile = get_profile("Confident Direct")  # Profile or None

# Profile attributes
profile.id           # str: unique identifier
profile.name         # str: display name
profile.description  # str: profile description
profile.token_weights # Dict[str, float]: token affinities
```

### Scoring

```python
from lncp.engine.scoring import analyze, AnalysisResult

# Analyze text
result = analyze("Your text here...")  # AnalysisResult

# Result attributes
result.tokens         # Dict[str, float]: detected tokens
result.matched_profile # Profile: best matching profile
result.all_matches    # List[Tuple[Profile, float]]: ranked matches
```

### Value

```python
from lncp.engine.value import calculate_token_value, calculate_system_value

# Calculate token value
value = calculate_token_value("assertive")  # float

# Calculate system value
total = calculate_system_value()  # float
```

---

## Meta Layer API

### Configuration

```python
from lncp.meta.config import get_config, Environment

config = get_config()

config.env                # Environment enum
config.is_production      # bool
config.is_development     # bool
config.simulation_mode    # bool
config.validate()         # List[str]: validation errors
```

### Events

```python
from lncp.meta.events import (
    EventBus, EventCollector, AppObserver,
    EventType, UserTier, AppEvent
)

# App-side: Emit events
bus = EventBus(events_dir="/path/to/events")

bus.session_started(visitor_id, session_id, 
                   utm_source="google", utm_medium="cpc")

bus.analysis_completed(visitor_id, user_id, UserTier.PRO,
                      text_length=500, token_count=15,
                      profile_id="p1", profile_name="Profile",
                      confidence=0.85, duration_ms=150)

bus.profile_viewed(visitor_id, user_id, UserTier.PRO,
                  profile_id="p1", profile_name="Profile",
                  view_duration_seconds=45.0)

bus.help_accessed(visitor_id, user_id, UserTier.FREE,
                 context="results_page", topic="understanding_scores")

bus.flush()  # Write to disk

# Meta-side: Collect events
collector = EventCollector(events_dir="/path/to/events")
events = collector.collect()  # List[AppEvent]
events = collector.collect_since(hours=24)

# Aggregate signals
observer = AppObserver(collector)
observer.aggregator.add_all(events)
signals = observer.get_current_signals(hours=24)

# Signal attributes
signals.total_events          # int
signals.sessions_started      # int
signals.sessions_with_utm     # int
signals.analyses_completed    # int
signals.profiles_viewed       # int
signals.results_exported      # int
signals.help_accessed         # int
signals.friction_rate         # float
signals.utm_attribution_rate  # float

# Health inputs for orchestrator
health = observer.get_health_inputs()  # Dict
```

### Activation

```python
from lncp.meta.activation import ActivationTracker, get_activation_tracker

tracker = get_activation_tracker()

# Process events
tracker.process_events(events)

# Get metrics
rate = tracker.get_activation_rate()  # float: 0-1
summary = tracker.get_summary()       # Dict
funnel = tracker.get_activation_funnel()  # Dict
health = tracker.get_health_inputs()  # Dict for orchestrator
```

### Lifecycle

```python
from lncp.meta.lifecycle import (
    UserLifecycleManager, get_lifecycle_manager,
    UserState, LifecycleState  # LifecycleState is alias
)

manager = get_lifecycle_manager()

# Process events
manager.process_events(events)

# Get state
state = manager.get_user_state(user_id)  # UserState enum

# Get distribution
dist = manager.get_state_distribution()  # Dict[UserState, int]

# Get rates
rates = manager.get_conversion_rates()  # Dict

# Health inputs
health = manager.get_health_inputs()  # Dict

# States
UserState.ANONYMOUS
UserState.SIGNED_UP
UserState.ONBOARDING
UserState.ACTIVATED
UserState.ENGAGED
UserState.RETAINED
UserState.BOUNCED
UserState.ABANDONED
UserState.DORMANT
UserState.AT_RISK
UserState.CHURNED
```

### Tier Context

```python
from lncp.meta.tier_context import (
    TierContextManager, get_tier_manager, TIER_TARGETS
)
from lncp.meta.events import UserTier

manager = get_tier_manager()

# Record outcomes
manager.record_action_outcome(
    action_type="meta_title_update",
    tier=UserTier.PRO,
    success=True,
    impact=0.12
)

# Get tier-specific trust
trust = manager.get_tier_trust("meta_title_update", UserTier.PRO)

# Evaluate proposal
eval_result = manager.evaluate_proposal_impact(
    expected_impacts={"activation_rate": 0.05},
    affected_tiers=[UserTier.FREE, UserTier.TRIAL]
)
# Returns: {"recommendation": "approve"|"review"|"reject", ...}

# Tier targets
TIER_TARGETS[UserTier.FREE]   # {"primary": "activation_rate", "target": 0.30}
TIER_TARGETS[UserTier.TRIAL]  # {"primary": "trial_conversion", "target": 0.25}
TIER_TARGETS[UserTier.PRO]    # {"primary": "retention_rate", "target": 0.95}
```

### Engine Feedback

```python
from lncp.meta.engine_feedback import (
    EngineFeedbackCollector, get_engine_feedback_collector
)

collector = get_engine_feedback_collector()

# Process events
collector.process_events(events)

# Get accuracy (inferred from user behavior)
accuracy = collector.get_overall_accuracy()  # float: 0-1

# Get summary
summary = collector.get_summary()  # Dict
```

### Trust Store

```python
from lncp.meta.trust_store import TrustStore, get_trust_store

store = get_trust_store()

# Record outcome
store.record_outcome("action_type", success=True, impact=0.15)

# Get trust score
score = store.get_trust_score("action_type")  # float: 0-1

# Check if auto-applicable
can_auto = store.can_auto_apply("action_type")  # bool
```

### Proposal System

```python
from lncp.meta.proposal_system import (
    ProposalManager, get_proposal_manager, Proposal
)

manager = get_proposal_manager()

# Create proposal
proposal = manager.create_proposal(
    action_type="meta_title_update",
    parameters={"new_title": "Better Title"},
    expected_impact=0.12,
    rationale="A/B test showed improvement"
)

# Get pending proposals
pending = manager.get_pending_proposals()  # List[Proposal]

# Approve/reject
manager.approve_proposal(proposal.id, approved_by="admin")
manager.reject_proposal(proposal.id, reason="Not aligned with goals")
```

### Command Center

```python
from lncp.meta.command_center import (
    CommandCenter, get_command_center,
    Domain, InjectionTier, ProposalStatus
)

cc = get_command_center()

# Get domain states
ux = cc.domains[Domain.USER_EXPERIENCE]
health = cc.domains[Domain.SYSTEM_HEALTH]
mrr = cc.domains[Domain.MRR_PERFORMANCE]

# Get proposals (sorted by priority)
for proposal in cc.proposals:
    print(f"[{proposal.priority_score}] {proposal.title}")
    print(f"  Tier: {proposal.tier.value}")
    print(f"  Impact: UX +{proposal.impact.ux_percent}%, MRR +${proposal.impact.mrr_dollars}")

# Approve proposal
result = cc.approve_proposal("prop_001", approved_by="admin")
# Returns: {"success": True, "proposal": {...}, "injection_tier": "immediate"}

# Reject proposal
cc.reject_proposal("prop_002", reason="Risk too high")

# Get injection queue
queue = cc.get_injection_queue()
# Returns: {"immediate": {...}, "24hour": {...}, "30day": {...}}

# Execute immediate injections
results = cc.execute_immediate()

# Get full state (JSON exportable)
state = cc.get_full_state()

# Get summary
summary = cc.get_summary()
```

### Integrations

```python
# Stripe
from lncp.meta.stripe_integration import ProductionRevenueObserver

observer = ProductionRevenueObserver()
metrics = observer.get_metrics()
# {"mrr": 16170.0, "churn_rate": 0.028, "ltv": 890, ...}

# GSC
from lncp.meta.gsc_integration import ProductionGSCObserver

observer = ProductionGSCObserver()
metrics = observer.get_site_metrics()
# metrics.total_impressions, metrics.total_clicks, metrics.avg_ctr, ...

# Alerting
from lncp.meta.benchmarks_alerting import AlertManager, AlertLevel

manager = AlertManager()
alert = manager.create_alert(
    level=AlertLevel.WARNING,
    title="Trial Conversion Low",
    message="18% vs 25% target",
    source="mrr_observer"
)
```

---

## Validation API

### E2E2E Validator

```python
from lncp.meta.e2e2e_validator import E2E2EValidator, run_e2e2e_validation

# Quick run
results = run_e2e2e_validation()
print(f"Pass rate: {results['summary']['pass_rate']}%")
print(f"Can deploy: {results['can_deploy']}")

# Detailed run
validator = E2E2EValidator()
results = validator.run()

# Results structure
results = {
    "version": "5.1.1",
    "timestamp": "2026-02-15T...",
    "summary": {
        "total": 44,
        "passed": 44,
        "failed": 0,
        "pass_rate": 100.0,
        "critical_failed": 0,
        "required_failed": 0
    },
    "phases": {
        "Core Engine": True,
        "Event Pipeline": True,
        ...
    },
    "can_deploy": True,
    "status": "🚀 PRODUCTION READY",
    "results": [...]
}
```

---

## Event Types Reference

```python
from lncp.meta.events import EventType

# Onboarding
EventType.SESSION_STARTED
EventType.ACCOUNT_CREATED
EventType.ONBOARDING_STARTED
EventType.ONBOARDING_STEP
EventType.ONBOARDING_COMPLETED

# Analysis
EventType.ANALYSIS_STARTED
EventType.ANALYSIS_COMPLETED
EventType.PROFILE_VIEWED
EventType.RESULT_EXPORTED
EventType.RESULT_SHARED

# Engagement
EventType.TOKEN_EXPANDED
EventType.COMPARISON_VIEWED
EventType.WRITING_SAMPLE_SUBMITTED
EventType.RECOMMENDATION_CLICKED
EventType.RESOURCE_ACCESSED

# Account
EventType.TRIAL_STARTED
EventType.SUBSCRIPTION_STARTED
EventType.SUBSCRIPTION_CANCELLED
EventType.TIER_UPGRADED
EventType.TIER_DOWNGRADED

# Feedback
EventType.PROFILE_ACCEPTED
EventType.PROFILE_SWITCHED
EventType.FEEDBACK_SUBMITTED
EventType.RATING_GIVEN
EventType.SUGGESTION_MADE
EventType.BUG_REPORTED
EventType.FEATURE_REQUESTED

# Friction (v5.1.1)
EventType.HELP_ACCESSED
EventType.SUPPORT_CONTACTED
EventType.ERROR_ENCOUNTERED
EventType.FLOW_ABANDONED

# System
EventType.SESSION_ENDED
EventType.PAGE_VIEWED
EventType.FEATURE_USED
EventType.EXPERIMENT_ASSIGNED
```

---

## User Tiers

```python
from lncp.meta.events import UserTier

UserTier.ANONYMOUS   # No account
UserTier.FREE        # Free tier
UserTier.TRIAL       # Trial period
UserTier.PRO         # Paid subscription
UserTier.ENTERPRISE  # Enterprise customer
```

---

## Enums Reference

```python
# Domains
from lncp.meta.command_center import Domain
Domain.USER_EXPERIENCE
Domain.SYSTEM_HEALTH
Domain.MRR_PERFORMANCE

# Injection Tiers
from lncp.meta.command_center import InjectionTier
InjectionTier.IMMEDIATE  # < 1 hour
InjectionTier.HOUR_24    # Next deploy
InjectionTier.DAY_30     # Next sprint

# Proposal Status
from lncp.meta.command_center import ProposalStatus
ProposalStatus.PENDING
ProposalStatus.APPROVED
ProposalStatus.REJECTED
ProposalStatus.DEFERRED
ProposalStatus.APPLIED

# Alert Levels
from lncp.meta.benchmarks_alerting import AlertLevel
AlertLevel.INFO
AlertLevel.WARNING
AlertLevel.CRITICAL

# Environments
from lncp.meta.config import Environment
Environment.DEVELOPMENT
Environment.STAGING
Environment.PRODUCTION
```
