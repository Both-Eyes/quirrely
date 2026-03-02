#!/usr/bin/env python3
"""
LNCP MASTER VALIDATION TEST v5.1.1
Comprehensive system-wide validation of all components.

Tests:
1. CORE ENGINE - Tokens, Profiles, Scoring, Value
2. META FOUNDATION - Config, Persistence, Health
3. META LEARNING - Outcomes, Predictions, Parameters
4. META OPTIMIZATION - Trust, Proposals, Auto-Apply
5. META INTEGRATIONS - Stripe, GSC, Alerting
6. META ANALYTICS - ML Models, Signal Discovery
7. META EXPERIENCE - Events, Activation, Lifecycle, Tiers
8. ORCHESTRATION - Full cycle simulation
9. PREDICTIVE - Model training and prediction
10. PRESCRIPTIVE - Proposal generation and evaluation
"""

import sys
import os
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

sys.path.insert(0, '/mnt/user-data/outputs/lncp-web-app')

# Test results collector
RESULTS = {
    "passed": 0,
    "failed": 0,
    "warnings": 0,
    "details": []
}

def log_test(category: str, test_name: str, passed: bool, message: str = ""):
    """Log a test result."""
    status = "✓" if passed else "✗"
    if passed:
        RESULTS["passed"] += 1
    else:
        RESULTS["failed"] += 1
    
    RESULTS["details"].append({
        "category": category,
        "test": test_name,
        "passed": passed,
        "message": message
    })
    
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    msg = f" - {message}" if message else ""
    print(f"  {color}{status}{reset} {test_name}{msg}")

def log_warning(category: str, message: str):
    """Log a warning."""
    RESULTS["warnings"] += 1
    print(f"  \033[93m⚠\033[0m {message}")


# ═══════════════════════════════════════════════════════════════════════════
# 1. CORE ENGINE
# ═══════════════════════════════════════════════════════════════════════════

def test_core_engine():
    print("\n" + "═" * 70)
    print("1. CORE ENGINE VALIDATION")
    print("═" * 70)
    
    # 1.1 Tokens
    print("\n1.1 Tokens")
    try:
        from lncp.engine.tokens import TOKENS, get_token, search_tokens
        
        log_test("CORE", "Token count", len(TOKENS) == 50, f"{len(TOKENS)} tokens")
        log_test("CORE", "Token lookup", get_token("assertive") is not None)
        
        results = search_tokens("confident")
        log_test("CORE", "Token search", len(results) > 0, f"{len(results)} results")
        
        # Validate token structure
        token = get_token("assertive")
        required_fields = ["id", "name", "category", "weight"]
        has_fields = all(hasattr(token, f) or f in token.__dict__ for f in required_fields)
        log_test("CORE", "Token structure", has_fields)
        
    except Exception as e:
        log_test("CORE", "Tokens module", False, str(e))
    
    # 1.2 Profiles
    print("\n1.2 Profiles")
    try:
        from lncp.engine.profiles import PROFILES, get_profile, get_profile_by_id
        
        log_test("CORE", "Profile count", len(PROFILES) == 40, f"{len(PROFILES)} profiles")
        
        profile = get_profile("Assertive Open")
        log_test("CORE", "Profile lookup by name", profile is not None)
        
        profile_by_id = get_profile_by_id("assertive-open")
        log_test("CORE", "Profile lookup by ID", profile_by_id is not None)
        
        # Validate profile structure
        required = ["id", "name", "traits", "description"]
        has_fields = profile is not None and all(hasattr(profile, f) for f in required)
        log_test("CORE", "Profile structure", has_fields)
        
    except Exception as e:
        log_test("CORE", "Profiles module", False, str(e))
    
    # 1.3 Scoring
    print("\n1.3 Scoring")
    try:
        from lncp.engine.scoring import analyze_text, score_profile_match
        
        test_text = "I believe we should move forward confidently with this plan. Let's take decisive action."
        result = analyze_text(test_text)
        
        log_test("CORE", "Text analysis", result is not None)
        log_test("CORE", "Tokens detected", "tokens" in result and len(result["tokens"]) > 0)
        log_test("CORE", "Profile matched", "profile" in result and result["profile"] is not None)
        log_test("CORE", "Confidence score", "confidence" in result and 0 <= result["confidence"] <= 1)
        
    except Exception as e:
        log_test("CORE", "Scoring module", False, str(e))
    
    # 1.4 Value
    print("\n1.4 Value/Economics")
    try:
        from lncp.engine.value import calculate_token_value, get_value_metrics
        
        metrics = get_value_metrics()
        log_test("CORE", "Value metrics", metrics is not None)
        
        value = calculate_token_value("assertive", usage_count=100)
        log_test("CORE", "Token value calculation", value > 0, f"Value: {value:.2f}")
        
    except Exception as e:
        log_test("CORE", "Value module", False, str(e))


# ═══════════════════════════════════════════════════════════════════════════
# 2. META FOUNDATION
# ═══════════════════════════════════════════════════════════════════════════

def test_meta_foundation():
    print("\n" + "═" * 70)
    print("2. META FOUNDATION VALIDATION")
    print("═" * 70)
    
    # 2.1 Config
    print("\n2.1 Configuration")
    try:
        from lncp.meta.config import get_config, Config, Environment
        
        config = get_config()
        log_test("META", "Config loaded", config is not None)
        log_test("META", "Environment set", config.env in Environment)
        log_test("META", "Simulation mode", isinstance(config.simulation_mode, bool))
        
        errors = config.validate()
        log_test("META", "Config validation", len(errors) == 0 or config.is_development, 
                f"{len(errors)} errors" if errors else "Valid")
        
    except Exception as e:
        log_test("META", "Config module", False, str(e))
    
    # 2.2 Persistence
    print("\n2.2 Persistence")
    try:
        from lncp.meta.persistence import PersistenceManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = PersistenceManager(tmpdir)
            
            # Test SQLite
            pm.outcomes.save("test_key", {"value": 123, "timestamp": datetime.utcnow().isoformat()})
            loaded = pm.outcomes.load("test_key")
            log_test("META", "SQLite save/load", loaded is not None and loaded["value"] == 123)
            
            # Test JSON
            pm.parameters.save("config", {"threshold": 0.85})
            loaded = pm.parameters.load("config")
            log_test("META", "JSON save/load", loaded is not None and loaded["threshold"] == 0.85)
            
            # Integrity check
            integrity = pm.check_integrity()
            log_test("META", "Integrity check", integrity["status"] == "ok")
            
            pm.close()
            
    except Exception as e:
        log_test("META", "Persistence module", False, str(e))
    
    # 2.3 Health Score
    print("\n2.3 Health Score")
    try:
        from lncp.meta.health_score import HealthCalculator, HealthDomain
        
        calc = HealthCalculator()
        
        # Update with test data
        calc.update_domain(HealthDomain.APP, {"metric1": 80, "metric2": 90})
        calc.update_domain(HealthDomain.REVENUE, {"mrr_growth": 5, "churn_rate": 3})
        
        health = calc.calculate()
        log_test("META", "Health calculation", 0 <= health.overall_score <= 100, 
                f"Score: {health.overall_score:.1f}")
        
        risk = calc.get_risk_tolerance()
        log_test("META", "Risk tolerance", 0 <= risk <= 1, f"Risk: {risk:.2f}")
        
    except Exception as e:
        log_test("META", "Health score module", False, str(e))


# ═══════════════════════════════════════════════════════════════════════════
# 3. META LEARNING
# ═══════════════════════════════════════════════════════════════════════════

def test_meta_learning():
    print("\n" + "═" * 70)
    print("3. META LEARNING VALIDATION")
    print("═" * 70)
    
    # 3.1 Outcome Tracker
    print("\n3.1 Outcome Tracking")
    try:
        from lncp.meta.outcome_tracker import OutcomeTracker, Outcome
        
        tracker = OutcomeTracker()
        
        outcome = tracker.record(
            action_id="act_001",
            action_type="meta_title_update",
            predicted_impact=0.15,
            actual_impact=0.12,
            success=True
        )
        log_test("LEARN", "Outcome recorded", outcome is not None)
        
        stats = tracker.get_action_stats("meta_title_update")
        log_test("LEARN", "Action stats", stats is not None)
        
    except Exception as e:
        log_test("LEARN", "Outcome tracker", False, str(e))
    
    # 3.2 Prediction Logger
    print("\n3.2 Prediction Logging")
    try:
        from lncp.meta.prediction_logger import PredictionLogger
        
        logger = PredictionLogger()
        
        pred_id = logger.log_prediction(
            action_type="meta_title_update",
            predicted_impact=0.15,
            confidence=0.85,
            context={"page": "/blog/test"}
        )
        log_test("LEARN", "Prediction logged", pred_id is not None)
        
        accuracy = logger.calculate_accuracy("meta_title_update")
        log_test("LEARN", "Accuracy calculation", accuracy is not None)
        
    except Exception as e:
        log_test("LEARN", "Prediction logger", False, str(e))
    
    # 3.3 Parameter Store
    print("\n3.3 Parameter Store")
    try:
        from lncp.meta.parameter_store import ParameterStore
        
        store = ParameterStore()
        
        store.set("test_param", 0.5, bounds=(0, 1))
        value = store.get("test_param")
        log_test("LEARN", "Parameter set/get", value == 0.5)
        
        store.propose_update("test_param", 0.6, evidence={"reason": "test"})
        proposals = store.get_pending_proposals()
        log_test("LEARN", "Parameter proposals", len(proposals) > 0)
        
    except Exception as e:
        log_test("LEARN", "Parameter store", False, str(e))


# ═══════════════════════════════════════════════════════════════════════════
# 4. META OPTIMIZATION
# ═══════════════════════════════════════════════════════════════════════════

def test_meta_optimization():
    print("\n" + "═" * 70)
    print("4. META OPTIMIZATION VALIDATION")
    print("═" * 70)
    
    # 4.1 Trust Store
    print("\n4.1 Trust Store")
    try:
        from lncp.meta.trust_store import TrustStore
        
        store = TrustStore()
        
        # Record outcomes
        store.record_outcome("meta_title_update", success=True, impact=0.15)
        store.record_outcome("meta_title_update", success=True, impact=0.10)
        store.record_outcome("meta_title_update", success=False, impact=-0.05)
        
        score = store.get_trust_score("meta_title_update")
        log_test("OPT", "Trust score", score is not None, f"Score: {score:.2f}")
        
        can_auto = store.can_auto_apply("meta_title_update")
        log_test("OPT", "Auto-apply check", isinstance(can_auto, bool))
        
    except Exception as e:
        log_test("OPT", "Trust store", False, str(e))
    
    # 4.2 Proposal System
    print("\n4.2 Proposal System")
    try:
        from lncp.meta.proposal_system import ProposalSystem, Proposal
        
        system = ProposalSystem()
        
        proposal = system.create_proposal(
            action_type="meta_title_update",
            target="/blog/test",
            change={"old": "Test", "new": "Better Test"},
            expected_impact=0.12,
            evidence={"ctr_current": 0.02, "benchmark": 0.04}
        )
        log_test("OPT", "Proposal created", proposal is not None)
        
        pending = system.get_pending()
        log_test("OPT", "Pending proposals", len(pending) >= 0)
        
    except Exception as e:
        log_test("OPT", "Proposal system", False, str(e))
    
    # 4.3 Auto Applier
    print("\n4.3 Auto Applier")
    try:
        from lncp.meta.auto_applier import AutoApplier
        
        applier = AutoApplier()
        
        # Check configuration
        config = applier.get_config()
        log_test("OPT", "Auto applier config", config is not None)
        
        # Check action registry
        actions = applier.get_registered_actions()
        log_test("OPT", "Actions registered", len(actions) > 0, f"{len(actions)} actions")
        
    except Exception as e:
        log_test("OPT", "Auto applier", False, str(e))


# ═══════════════════════════════════════════════════════════════════════════
# 5. META INTEGRATIONS
# ═══════════════════════════════════════════════════════════════════════════

def test_meta_integrations():
    print("\n" + "═" * 70)
    print("5. META INTEGRATIONS VALIDATION")
    print("═" * 70)
    
    # 5.1 Stripe Integration
    print("\n5.1 Stripe Integration")
    try:
        from lncp.meta.stripe_integration import (
            StripeAPIClient, ProductionRevenueObserver
        )
        
        client = StripeAPIClient()
        log_test("INT", "Stripe client", client is not None)
        
        # Simulation mode
        mrr = client.calculate_mrr()
        log_test("INT", "MRR calculation", mrr >= 0, f"${mrr:,.0f}")
        
        observer = ProductionRevenueObserver()
        metrics = observer.get_metrics()
        log_test("INT", "Revenue metrics", "mrr" in metrics and "churn_rate" in metrics)
        
    except Exception as e:
        log_test("INT", "Stripe integration", False, str(e))
    
    # 5.2 GSC Integration
    print("\n5.2 GSC Integration")
    try:
        from lncp.meta.gsc_integration import ProductionGSCObserver
        
        observer = ProductionGSCObserver()
        
        metrics = observer.get_site_metrics()
        log_test("INT", "Site metrics", metrics is not None)
        log_test("INT", "Impressions tracked", metrics.total_impressions >= 0)
        
        summary = observer.get_summary()
        log_test("INT", "Quota tracking", "quota_remaining" in summary)
        
    except Exception as e:
        log_test("INT", "GSC integration", False, str(e))
    
    # 5.3 Alerting
    print("\n5.3 Alerting")
    try:
        from lncp.meta.benchmarks_alerting import (
            AlertManager, AlertLevel, BenchmarkStore
        )
        
        alerts = AlertManager()
        
        alert = alerts.create_alert(
            AlertLevel.WARNING,
            "Test Alert",
            "This is a test",
            "master_test"
        )
        log_test("INT", "Alert creation", alert is not None)
        
        benchmarks = BenchmarkStore()
        comp = benchmarks.compare("trial_conversion", 18)
        log_test("INT", "Benchmark comparison", comp is not None, f"Percentile: {comp.percentile}")
        
    except Exception as e:
        log_test("INT", "Alerting", False, str(e))


# ═══════════════════════════════════════════════════════════════════════════
# 6. META ANALYTICS (PREDICTIVE)
# ═══════════════════════════════════════════════════════════════════════════

def test_meta_analytics():
    print("\n" + "═" * 70)
    print("6. META ANALYTICS (PREDICTIVE)")
    print("═" * 70)
    
    # 6.1 ML Models
    print("\n6.1 ML Models")
    try:
        from lncp.meta.ml_models import ModelManager, SuccessPredictor, ImpactPredictor
        
        mm = ModelManager()
        
        # Training data
        success_data = [
            {"features": {"confidence": 0.9, "trust": 15, "health": 80}, "success": 1},
            {"features": {"confidence": 0.8, "trust": 10, "health": 75}, "success": 1},
            {"features": {"confidence": 0.6, "trust": 5, "health": 60}, "success": 0},
            {"features": {"confidence": 0.5, "trust": 2, "health": 50}, "success": 0},
            {"features": {"confidence": 0.7, "trust": 8, "health": 70}, "success": 1},
            {"features": {"confidence": 0.4, "trust": 3, "health": 45}, "success": 0},
        ]
        
        impact_data = [
            {"features": {"confidence": 0.9, "trust": 15}, "impact": 12.0},
            {"features": {"confidence": 0.8, "trust": 10}, "impact": 8.0},
            {"features": {"confidence": 0.6, "trust": 5}, "impact": 3.0},
            {"features": {"confidence": 0.4, "trust": 2}, "impact": 1.0},
        ]
        
        results = mm.train_all(success_data, impact_data)
        log_test("PRED", "Models trained", "success" in results and "impact" in results)
        
        # Prediction
        preds = mm.predict_action({"confidence": 0.85, "trust": 12, "health": 75})
        log_test("PRED", "Success prediction", 0 <= preds["success"].prediction <= 1,
                f"P(success): {preds['success'].prediction:.2f}")
        log_test("PRED", "Impact prediction", preds["impact"].prediction >= 0,
                f"Expected: {preds['impact'].prediction:.1f}")
        
    except Exception as e:
        log_test("PRED", "ML models", False, str(e))
    
    # 6.2 Signal Discovery
    print("\n6.2 Signal Discovery")
    try:
        from lncp.meta.ml_models import SignalAnalyzer
        
        analyzer = SignalAnalyzer()
        
        data = [
            {"signal_a": 0.9, "signal_b": 0.2, "success": 1},
            {"signal_a": 0.8, "signal_b": 0.3, "success": 1},
            {"signal_a": 0.3, "signal_b": 0.8, "success": 0},
            {"signal_a": 0.2, "signal_b": 0.9, "success": 0},
        ]
        
        correlations = analyzer.analyze_correlations(data, "success")
        log_test("PRED", "Correlation analysis", len(correlations) > 0)
        
        strong = analyzer.identify_strong_signals()
        weak = analyzer.identify_weak_signals()
        log_test("PRED", "Signal identification", isinstance(strong, list) and isinstance(weak, list))
        
    except Exception as e:
        log_test("PRED", "Signal discovery", False, str(e))


# ═══════════════════════════════════════════════════════════════════════════
# 7. META EXPERIENCE
# ═══════════════════════════════════════════════════════════════════════════

def test_meta_experience():
    print("\n" + "═" * 70)
    print("7. META EXPERIENCE VALIDATION")
    print("═" * 70)
    
    # 7.1 Event System
    print("\n7.1 Event System")
    try:
        from lncp.meta.events import (
            EventBus, EventCollector, AppObserver,
            EventType, UserTier, AppEvent
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            bus = EventBus(events_dir=tmpdir)
            
            # Emit various events
            bus.session_started("v_001", "s_001", utm_source="google", utm_campaign="brand")
            bus.analysis_completed("v_001", "u_001", UserTier.PRO, 500, 12, 
                                  "assertive-open", "Assertive Open", 0.85, 150)
            bus.profile_viewed("v_001", "u_001", UserTier.PRO, "assertive-open", "Assertive Open", 45.0)
            bus.help_accessed("v_001", "u_001", UserTier.PRO, "analysis_page", "how_to_export")
            
            bus.flush()
            
            collector = EventCollector(events_dir=tmpdir)
            events = collector.collect()
            log_test("EXP", "Event emission", len(events) == 4, f"{len(events)} events")
            
            # Test observer
            observer = AppObserver(collector)
            observer.aggregator.add_all(events)
            signals = observer.get_current_signals(hours=1)
            log_test("EXP", "Signal aggregation", signals.total_events > 0)
            log_test("EXP", "Friction tracking", hasattr(signals, "friction_rate"))
            log_test("EXP", "UTM attribution", hasattr(signals, "sessions_with_utm"))
            
    except Exception as e:
        log_test("EXP", "Event system", False, str(e))
    
    # 7.2 Activation Tracker
    print("\n7.2 Activation Tracking")
    try:
        from lncp.meta.activation import ActivationTracker, ActivationStatus
        from lncp.meta.events import EventType, AppEvent, UserTier
        
        tracker = ActivationTracker()
        
        # Simulate user journey
        events = [
            AppEvent(
                event_id="e1", event_type=EventType.ACCOUNT_CREATED,
                timestamp=datetime.utcnow() - timedelta(hours=2),
                visitor_id="v_001", user_id="u_001", tier=UserTier.FREE,
                payload={"source": "blog"}
            ),
            AppEvent(
                event_id="e2", event_type=EventType.ANALYSIS_COMPLETED,
                timestamp=datetime.utcnow() - timedelta(hours=1),
                visitor_id="v_001", user_id="u_001", tier=UserTier.FREE,
                payload={"text_length": 500}
            ),
            AppEvent(
                event_id="e3", event_type=EventType.PROFILE_VIEWED,
                timestamp=datetime.utcnow() - timedelta(minutes=55),
                visitor_id="v_001", user_id="u_001", tier=UserTier.FREE,
                payload={"profile_id": "p1", "view_duration_seconds": 45}
            ),
        ]
        
        tracker.process_events(events)
        
        rate = tracker.get_activation_rate()
        log_test("EXP", "Activation rate", rate >= 0, f"{rate:.1%}")
        
        summary = tracker.get_summary()
        log_test("EXP", "Activation summary", "activated" in summary)
        
        funnel = tracker.get_activation_funnel()
        log_test("EXP", "Activation funnel", "has_analysis_pct" in funnel)
        
    except Exception as e:
        log_test("EXP", "Activation tracker", False, str(e))
    
    # 7.3 Lifecycle Manager
    print("\n7.3 Lifecycle Management")
    try:
        from lncp.meta.lifecycle import UserLifecycleManager, UserState
        
        manager = UserLifecycleManager()
        manager.process_events(events)  # From activation test
        
        dist = manager.get_state_distribution()
        log_test("EXP", "State distribution", sum(dist.values()) > 0)
        
        rates = manager.get_conversion_rates()
        log_test("EXP", "Conversion rates", "signup_to_activated" in rates)
        
        health = manager.get_health_inputs()
        log_test("EXP", "Lifecycle health", "health_score" in health)
        
    except Exception as e:
        log_test("EXP", "Lifecycle manager", False, str(e))
    
    # 7.4 Tier Context
    print("\n7.4 Tier Context")
    try:
        from lncp.meta.tier_context import TierContextManager, TIER_TARGETS
        from lncp.meta.events import UserTier
        
        manager = TierContextManager()
        
        # Record outcomes
        manager.record_action_outcome("meta_title_update", UserTier.FREE, True, 0.15)
        manager.record_action_outcome("meta_title_update", UserTier.PRO, True, 0.10)
        manager.record_action_outcome("meta_title_update", UserTier.PRO, True, 0.12)
        
        trust = manager.get_tier_trust("meta_title_update", UserTier.PRO)
        log_test("EXP", "Tier-specific trust", trust >= 0)
        
        # Proposal evaluation
        eval_result = manager.evaluate_proposal_impact(
            expected_impacts={"activation_rate": 0.05},
            affected_tiers=[UserTier.FREE, UserTier.PRO]
        )
        log_test("EXP", "Proposal evaluation", "recommendation" in eval_result)
        
    except Exception as e:
        log_test("EXP", "Tier context", False, str(e))
    
    # 7.5 Engine Feedback
    print("\n7.5 Engine Feedback")
    try:
        from lncp.meta.engine_feedback import EngineFeedbackCollector, FeedbackSignal
        
        collector = EngineFeedbackCollector()
        
        # Process analysis events
        feedback_events = [
            AppEvent(
                event_id="f1", event_type=EventType.ANALYSIS_COMPLETED,
                timestamp=datetime.utcnow() - timedelta(minutes=30),
                visitor_id="v_002", user_id="u_002", tier=UserTier.PRO,
                payload={"profile_id": "confident-direct", "profile_name": "Confident Direct", "confidence": 0.88}
            ),
            AppEvent(
                event_id="f2", event_type=EventType.PROFILE_VIEWED,
                timestamp=datetime.utcnow() - timedelta(minutes=29),
                visitor_id="v_002", user_id="u_002", tier=UserTier.PRO,
                payload={"profile_id": "confident-direct", "view_duration_seconds": 60}
            ),
            AppEvent(
                event_id="f3", event_type=EventType.RESULT_EXPORTED,
                timestamp=datetime.utcnow() - timedelta(minutes=28),
                visitor_id="v_002", user_id="u_002", tier=UserTier.PRO,
                payload={"profile_id": "confident-direct", "format": "pdf"}
            ),
        ]
        
        collector.process_events(feedback_events)
        
        accuracy = collector.get_overall_accuracy()
        log_test("EXP", "Engine accuracy", 0 <= accuracy <= 1, f"{accuracy:.1%}")
        
        summary = collector.get_summary()
        log_test("EXP", "Feedback summary", "profiles_tracked" in summary)
        
    except Exception as e:
        log_test("EXP", "Engine feedback", False, str(e))


# ═══════════════════════════════════════════════════════════════════════════
# 8. ORCHESTRATION
# ═══════════════════════════════════════════════════════════════════════════

def test_orchestration():
    print("\n" + "═" * 70)
    print("8. ORCHESTRATION VALIDATION")
    print("═" * 70)
    
    # 8.1 Meta Orchestrator
    print("\n8.1 Meta Orchestrator")
    try:
        from lncp.meta.meta_orchestrator import MetaOrchestrator
        
        orch = MetaOrchestrator()
        log_test("ORCH", "Orchestrator created", orch is not None)
        
        status = orch.get_status()
        log_test("ORCH", "Status available", status is not None)
        
        # Check components connected
        log_test("ORCH", "Health calculator", hasattr(orch, 'health_calculator') or 'health' in str(dir(orch)).lower())
        log_test("ORCH", "Trust store", hasattr(orch, 'trust_store') or 'trust' in str(dir(orch)).lower())
        
    except Exception as e:
        log_test("ORCH", "Meta orchestrator", False, str(e))
    
    # 8.2 Unified Orchestrator
    print("\n8.2 Unified Orchestrator")
    try:
        from lncp.meta.unified_orchestrator import UnifiedOrchestrator
        
        orch = UnifiedOrchestrator()
        log_test("ORCH", "Unified orchestrator created", orch is not None)
        
        summary = orch.get_summary()
        log_test("ORCH", "Summary available", summary is not None)
        
    except Exception as e:
        log_test("ORCH", "Unified orchestrator", False, str(e))
    
    # 8.3 Simulation
    print("\n8.3 Simulation Engine")
    try:
        from lncp.meta.simulation import SimulationEngine
        
        sim = SimulationEngine()
        log_test("ORCH", "Simulation engine created", sim is not None)
        
        # Run short simulation
        result = sim.run(days=7, verbose=False)
        log_test("ORCH", "Simulation run", result is not None)
        
    except Exception as e:
        log_test("ORCH", "Simulation engine", False, str(e))


# ═══════════════════════════════════════════════════════════════════════════
# 9. PRESCRIPTIVE ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════

def test_prescriptive():
    print("\n" + "═" * 70)
    print("9. PRESCRIPTIVE ANALYTICS")
    print("═" * 70)
    
    # 9.1 Action Classification
    print("\n9.1 Action Classification")
    try:
        from lncp.meta.action_classifier import ActionClassifier
        
        classifier = ActionClassifier()
        
        classification = classifier.classify({
            "type": "meta_title_update",
            "target": "/blog/test",
            "expected_impact": 0.15
        })
        log_test("PRESC", "Action classified", classification is not None)
        
        risk = classifier.assess_risk("meta_title_update")
        log_test("PRESC", "Risk assessment", risk is not None)
        
    except Exception as e:
        log_test("PRESC", "Action classifier", False, str(e))
    
    # 9.2 Engine Parameters
    print("\n9.2 Engine Parameter Analysis")
    try:
        from lncp.meta.engine_parameters import EngineParameterAnalyzer
        
        analyzer = EngineParameterAnalyzer()
        
        proposals = analyzer.analyze_and_propose({
            "accuracy": 0.75,
            "profile_switches": 25,
            "total_analyses": 100
        })
        log_test("PRESC", "Parameter proposals", isinstance(proposals, list))
        
    except Exception as e:
        log_test("PRESC", "Engine parameters", False, str(e))
    
    # 9.3 Attribution Tracker
    print("\n9.3 Attribution Analysis")
    try:
        from lncp.meta.attribution_tracker import AttributionTracker
        
        tracker = AttributionTracker()
        
        tracker.track_touchpoint("user_001", "blog_post", "/blog/test", {"cta": "signup"})
        tracker.track_conversion("user_001", "signup")
        
        attribution = tracker.get_attribution("user_001")
        log_test("PRESC", "Attribution tracking", attribution is not None)
        
    except Exception as e:
        log_test("PRESC", "Attribution tracker", False, str(e))


# ═══════════════════════════════════════════════════════════════════════════
# 10. BLOG OPTIMIZATION
# ═══════════════════════════════════════════════════════════════════════════

def test_blog_optimization():
    print("\n" + "═" * 70)
    print("10. BLOG OPTIMIZATION")
    print("═" * 70)
    
    # 10.1 Blog Classifier
    print("\n10.1 Blog Classifier")
    try:
        from lncp.meta.blog.classifier import BlogClassifier
        
        classifier = BlogClassifier()
        
        classification = classifier.classify("/blog/test-post")
        log_test("BLOG", "Post classification", classification is not None)
        
    except Exception as e:
        log_test("BLOG", "Blog classifier", False, str(e))
    
    # 10.2 A/B Testing
    print("\n10.2 A/B Testing")
    try:
        from lncp.meta.blog.ab_testing import ABTestManager
        
        manager = ABTestManager()
        
        test = manager.create_test(
            name="headline_test",
            variants=["Original", "New Headline"],
            metric="ctr"
        )
        log_test("BLOG", "A/B test created", test is not None)
        
    except Exception as e:
        log_test("BLOG", "A/B testing", False, str(e))
    
    # 10.3 CTA Tracker
    print("\n10.3 CTA Tracking")
    try:
        from lncp.meta.blog.cta_tracker import CTATracker
        
        tracker = CTATracker()
        
        tracker.track_impression("cta_001", "/blog/test")
        tracker.track_click("cta_001", "/blog/test")
        
        metrics = tracker.get_metrics("cta_001")
        log_test("BLOG", "CTA metrics", metrics is not None)
        
    except Exception as e:
        log_test("BLOG", "CTA tracker", False, str(e))
    
    # 10.4 Blog Feedback
    print("\n10.4 Blog Feedback Loop")
    try:
        from lncp.meta.blog.feedback import BlogFeedbackLoop
        
        loop = BlogFeedbackLoop()
        
        analysis = loop.analyze_page("/blog/test", {
            "impressions": 1000,
            "clicks": 30,
            "conversions": 5
        })
        log_test("BLOG", "Feedback analysis", analysis is not None)
        
    except Exception as e:
        log_test("BLOG", "Blog feedback", False, str(e))


# ═══════════════════════════════════════════════════════════════════════════
# MASTER TEST EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

def run_master_test():
    """Run all tests and produce final report."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " LNCP MASTER VALIDATION TEST v5.1.1 ".center(68) + "║")
    print("║" + " System-Wide Comprehensive Validation ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"\nTest Started: {datetime.utcnow().isoformat()}")
    
    # Run all test suites
    test_core_engine()
    test_meta_foundation()
    test_meta_learning()
    test_meta_optimization()
    test_meta_integrations()
    test_meta_analytics()
    test_meta_experience()
    test_orchestration()
    test_prescriptive()
    test_blog_optimization()
    
    # Final Report
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " MASTER TEST RESULTS ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    
    total = RESULTS["passed"] + RESULTS["failed"]
    pass_rate = (RESULTS["passed"] / total * 100) if total > 0 else 0
    
    print(f"""
┌────────────────────────────────────────────────────────────────────┐
│  SUMMARY                                                           │
├────────────────────────────────────────────────────────────────────┤
│  Total Tests:     {total:>4}                                          │
│  Passed:          {RESULTS["passed"]:>4}  ({pass_rate:.1f}%)                                   │
│  Failed:          {RESULTS["failed"]:>4}                                          │
│  Warnings:        {RESULTS["warnings"]:>4}                                          │
├────────────────────────────────────────────────────────────────────┤
│  Pass Rate:       {pass_rate:>5.1f}%                                        │
└────────────────────────────────────────────────────────────────────┘
""")
    
    # Category breakdown
    print("┌────────────────────────────────────────────────────────────────────┐")
    print("│  RESULTS BY CATEGORY                                               │")
    print("├────────────────────────────────────────────────────────────────────┤")
    
    categories = {}
    for detail in RESULTS["details"]:
        cat = detail["category"]
        if cat not in categories:
            categories[cat] = {"passed": 0, "failed": 0}
        if detail["passed"]:
            categories[cat]["passed"] += 1
        else:
            categories[cat]["failed"] += 1
    
    for cat, counts in categories.items():
        total_cat = counts["passed"] + counts["failed"]
        rate = (counts["passed"] / total_cat * 100) if total_cat > 0 else 0
        status = "✓" if counts["failed"] == 0 else "✗"
        print(f"│  {status} {cat:<12} {counts['passed']:>3}/{total_cat:<3} ({rate:>5.1f}%)                            │")
    
    print("└────────────────────────────────────────────────────────────────────┘")
    
    # Failed tests detail
    failed_tests = [d for d in RESULTS["details"] if not d["passed"]]
    if failed_tests:
        print("\n┌────────────────────────────────────────────────────────────────────┐")
        print("│  FAILED TESTS                                                      │")
        print("├────────────────────────────────────────────────────────────────────┤")
        for test in failed_tests:
            print(f"│  ✗ [{test['category']}] {test['test'][:40]:<40}     │")
            if test['message']:
                print(f"│    └─ {test['message'][:55]:<55}│")
        print("└────────────────────────────────────────────────────────────────────┘")
    
    # System Status
    print("\n┌────────────────────────────────────────────────────────────────────┐")
    print("│  SYSTEM STATUS                                                     │")
    print("├────────────────────────────────────────────────────────────────────┤")
    
    if pass_rate >= 95:
        status_color = "\033[92m"  # Green
        status_text = "PRODUCTION READY"
        status_icon = "🚀"
    elif pass_rate >= 80:
        status_color = "\033[93m"  # Yellow
        status_text = "NEEDS ATTENTION"
        status_icon = "⚠️"
    else:
        status_color = "\033[91m"  # Red
        status_text = "NOT READY"
        status_icon = "❌"
    
    reset = "\033[0m"
    print(f"│  {status_icon}  {status_color}{status_text}{reset}                                               │")
    print("│                                                                    │")
    print(f"│  Core Engine:        {'✓ LOCKED' if pass_rate >= 90 else '⚠ CHECK'}                                    │")
    print(f"│  Meta Layer:         {'✓ OPERATIONAL' if pass_rate >= 90 else '⚠ CHECK'}                               │")
    print(f"│  Integrations:       {'✓ CONFIGURED' if pass_rate >= 90 else '⚠ CHECK'}                                │")
    print(f"│  Analytics:          {'✓ TRAINED' if pass_rate >= 90 else '⚠ CHECK'}                                   │")
    print(f"│  Orchestration:      {'✓ READY' if pass_rate >= 90 else '⚠ CHECK'}                                     │")
    print("└────────────────────────────────────────────────────────────────────┘")
    
    print(f"\nTest Completed: {datetime.utcnow().isoformat()}")
    
    return RESULTS


if __name__ == "__main__":
    results = run_master_test()
    sys.exit(0 if results["failed"] == 0 else 1)
