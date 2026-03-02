#!/usr/bin/env python3
"""
LNCP MASTER VALIDATION TEST v5.1.1 (Final)
System-wide validation using verified API signatures.
"""

import sys
import os
import tempfile
from datetime import datetime, timedelta, timezone

sys.path.insert(0, '/mnt/user-data/outputs/lncp-web-app')

RESULTS = {"passed": 0, "failed": 0, "details": []}

def now():
    return datetime.now(timezone.utc)

def log_test(cat, name, passed, msg=""):
    RESULTS["passed" if passed else "failed"] += 1
    RESULTS["details"].append({"category": cat, "test": name, "passed": passed})
    color = "\033[92m" if passed else "\033[91m"
    print(f"  {color}{'✓' if passed else '✗'}\033[0m {name}" + (f" - {msg}" if msg else ""))


def test_core_engine():
    print("\n" + "═" * 70)
    print("1. CORE ENGINE")
    print("═" * 70)
    
    print("\n1.1 Tokens (50)")
    try:
        from lncp.engine.tokens import ALL_TOKENS, get_token, Token
        log_test("CORE", "Token count", len(ALL_TOKENS) == 50, f"{len(ALL_TOKENS)}")
        log_test("CORE", "Token lookup", get_token("assertive") is not None)
        log_test("CORE", "Token type", isinstance(get_token("assertive"), Token))
    except Exception as e:
        log_test("CORE", "Tokens", False, str(e)[:50])
    
    print("\n1.2 Profiles (40)")
    try:
        from lncp.engine.profiles import ALL_PROFILES, get_profile, Profile
        log_test("CORE", "Profile count", len(ALL_PROFILES) == 40, f"{len(ALL_PROFILES)}")
        log_test("CORE", "Profile lookup", get_profile("Assertive Open") is not None)
    except Exception as e:
        log_test("CORE", "Profiles", False, str(e)[:50])
    
    print("\n1.3 Scoring")
    try:
        from lncp.engine.scoring import analyze
        result = analyze("I believe we should move forward confidently.")
        log_test("CORE", "analyze()", result is not None)
        log_test("CORE", "Profile matched", result.profile is not None)
        log_test("CORE", "Confidence", 0 <= result.confidence <= 1, f"{result.confidence:.2f}")
    except Exception as e:
        log_test("CORE", "Scoring", False, str(e)[:50])
    
    print("\n1.4 Value")
    try:
        from lncp.engine.value import calculate_token_value, calculate_system_value
        val = calculate_token_value("assertive", usage_count=10)
        log_test("CORE", "Token value", val >= 0, f"{val:.2f}")
    except Exception as e:
        log_test("CORE", "Value", False, str(e)[:50])


def test_meta_foundation():
    print("\n" + "═" * 70)
    print("2. META FOUNDATION")
    print("═" * 70)
    
    print("\n2.1 Configuration")
    try:
        from lncp.meta.config import get_config, Environment
        config = get_config()
        log_test("META", "Config loaded", config is not None)
        log_test("META", "Environment", config.env in Environment)
        log_test("META", "Validation", len(config.validate()) == 0 or config.is_development)
    except Exception as e:
        log_test("META", "Config", False, str(e)[:50])
    
    print("\n2.2 Persistence")
    try:
        from lncp.meta.persistence import PersistenceManager
        with tempfile.TemporaryDirectory() as tmpdir:
            pm = PersistenceManager(tmpdir)
            pm.outcomes.save("k", {"v": 1})
            log_test("META", "SQLite save/load", pm.outcomes.load("k")["v"] == 1)
            pm.parameters.save("c", {"x": 2})
            log_test("META", "JSON save/load", pm.parameters.load("c")["x"] == 2)
            log_test("META", "Integrity", pm.check_integrity()["status"] == "ok")
            pm.close()
    except Exception as e:
        log_test("META", "Persistence", False, str(e)[:50])
    
    print("\n2.3 Health")
    try:
        from lncp.meta.health_score import get_health_calculator
        calc = get_health_calculator()
        log_test("META", "Health calculator", calc is not None)
        health = calc.get_system_health()
        log_test("META", "System health", health is not None)
    except Exception as e:
        log_test("META", "Health", False, str(e)[:50])


def test_meta_learning():
    print("\n" + "═" * 70)
    print("3. META LEARNING")
    print("═" * 70)
    
    try:
        from lncp.meta.outcome_tracker import OutcomeTracker
        log_test("LEARN", "OutcomeTracker", OutcomeTracker() is not None)
    except Exception as e:
        log_test("LEARN", "OutcomeTracker", False, str(e)[:50])
    
    try:
        from lncp.meta.prediction_logger import PredictionLogger
        log_test("LEARN", "PredictionLogger", PredictionLogger() is not None)
    except Exception as e:
        log_test("LEARN", "PredictionLogger", False, str(e)[:50])
    
    try:
        from lncp.meta.feedback_loop import FeedbackLoop
        log_test("LEARN", "FeedbackLoop", FeedbackLoop() is not None)
    except Exception as e:
        log_test("LEARN", "FeedbackLoop", False, str(e)[:50])


def test_meta_optimization():
    print("\n" + "═" * 70)
    print("4. META OPTIMIZATION")
    print("═" * 70)
    
    try:
        from lncp.meta.trust_store import get_trust_store
        log_test("OPT", "TrustStore", get_trust_store() is not None)
    except Exception as e:
        log_test("OPT", "TrustStore", False, str(e)[:50])
    
    try:
        from lncp.meta.proposal_system import get_proposal_manager
        log_test("OPT", "ProposalManager", get_proposal_manager() is not None)
    except Exception as e:
        log_test("OPT", "ProposalManager", False, str(e)[:50])
    
    try:
        from lncp.meta.auto_applier import AutoApplier
        log_test("OPT", "AutoApplier", AutoApplier() is not None)
    except Exception as e:
        log_test("OPT", "AutoApplier", False, str(e)[:50])


def test_meta_integrations():
    print("\n" + "═" * 70)
    print("5. META INTEGRATIONS")
    print("═" * 70)
    
    print("\n5.1 Stripe")
    try:
        from lncp.meta.stripe_integration import StripeAPIClient, ProductionRevenueObserver
        mrr = StripeAPIClient().calculate_mrr()
        log_test("INT", "Stripe MRR", mrr >= 0, f"${mrr:,.0f}")
        m = ProductionRevenueObserver().get_metrics()
        log_test("INT", "Revenue metrics", "mrr" in m and "churn_rate" in m)
    except Exception as e:
        log_test("INT", "Stripe", False, str(e)[:50])
    
    print("\n5.2 GSC")
    try:
        from lncp.meta.gsc_integration import ProductionGSCObserver
        obs = ProductionGSCObserver()
        m = obs.get_site_metrics()
        log_test("INT", "GSC metrics", m.total_impressions >= 0, f"{m.total_impressions:,}")
        log_test("INT", "GSC quota", "quota_remaining" in obs.get_summary())
    except Exception as e:
        log_test("INT", "GSC", False, str(e)[:50])
    
    print("\n5.3 Alerting & Benchmarks")
    try:
        from lncp.meta.benchmarks_alerting import AlertManager, AlertLevel, BenchmarkStore
        a = AlertManager().create_alert(AlertLevel.INFO, "Test", "Msg", "test")
        log_test("INT", "Alert creation", a is not None)
        c = BenchmarkStore().compare("trial_conversion", 18)
        log_test("INT", "Benchmarks", c is not None)
    except Exception as e:
        log_test("INT", "Alerting", False, str(e)[:50])


def test_meta_analytics():
    print("\n" + "═" * 70)
    print("6. META ANALYTICS (PREDICTIVE)")
    print("═" * 70)
    
    try:
        from lncp.meta.ml_models import ModelManager, SignalAnalyzer
        mm = ModelManager()
        mm.train_all(
            [{"features": {"c": 0.9}, "success": 1}, {"features": {"c": 0.3}, "success": 0}],
            [{"features": {"c": 0.9}, "impact": 10}, {"features": {"c": 0.3}, "impact": 2}]
        )
        preds = mm.predict_action({"c": 0.8})
        log_test("PRED", "Success prediction", 0 <= preds["success"].prediction <= 1)
        log_test("PRED", "Impact prediction", preds["impact"].prediction >= 0)
        
        sa = SignalAnalyzer()
        corr = sa.analyze_correlations([{"a": 1, "s": 1}, {"a": 0, "s": 0}], "s")
        log_test("PRED", "Signal analysis", isinstance(corr, dict))
    except Exception as e:
        log_test("PRED", "ML Models", False, str(e)[:50])


def test_meta_experience():
    print("\n" + "═" * 70)
    print("7. META EXPERIENCE")
    print("═" * 70)
    
    print("\n7.1 Events")
    try:
        from lncp.meta.events import EventBus, EventCollector, AppObserver, UserTier
        with tempfile.TemporaryDirectory() as tmpdir:
            bus = EventBus(events_dir=tmpdir)
            bus.session_started("v", "s", utm_source="google")
            bus.analysis_completed("v", "u", UserTier.PRO, 100, 5, "p", "P", 0.9, 50)
            bus.help_accessed("v", "u", UserTier.PRO, "ctx", "topic")
            bus.flush()
            events = EventCollector(events_dir=tmpdir).collect()
            log_test("EXP", "Event emission", len(events) == 3, f"{len(events)} events")
            obs = AppObserver()
            obs.aggregator.add_all(events)
            sig = obs.get_current_signals(1)
            log_test("EXP", "Signals", sig.total_events > 0)
            log_test("EXP", "Friction tracking", hasattr(sig, "friction_rate"))
            log_test("EXP", "UTM attribution", hasattr(sig, "sessions_with_utm"))
    except Exception as e:
        log_test("EXP", "Events", False, str(e)[:50])
    
    print("\n7.2 Activation")
    try:
        from lncp.meta.activation import ActivationTracker
        from lncp.meta.events import EventType, AppEvent, UserTier
        t = ActivationTracker()
        events = [
            AppEvent("e1", EventType.ACCOUNT_CREATED, now()-timedelta(hours=2), "v", "u", UserTier.FREE, payload={}),
            AppEvent("e2", EventType.ANALYSIS_COMPLETED, now()-timedelta(hours=1), "v", "u", UserTier.FREE, payload={"text_length": 100}),
            AppEvent("e3", EventType.PROFILE_VIEWED, now()-timedelta(minutes=30), "v", "u", UserTier.FREE, payload={"view_duration_seconds": 45}),
        ]
        t.process_events(events)
        log_test("EXP", "Activation rate", t.get_activation_rate() >= 0)
        log_test("EXP", "Activation summary", "activated" in t.get_summary())
    except Exception as e:
        log_test("EXP", "Activation", False, str(e)[:50])
    
    print("\n7.3 Lifecycle")
    try:
        from lncp.meta.lifecycle import UserLifecycleManager
        m = UserLifecycleManager()
        log_test("EXP", "Lifecycle manager", m is not None)
        log_test("EXP", "State distribution", isinstance(m.get_state_distribution(), dict))
    except Exception as e:
        log_test("EXP", "Lifecycle", False, str(e)[:50])
    
    print("\n7.4 Tier Context")
    try:
        from lncp.meta.tier_context import TierContextManager
        from lncp.meta.events import UserTier
        m = TierContextManager()
        m.record_action_outcome("test", UserTier.PRO, True, 0.1)
        log_test("EXP", "Tier trust", m.get_tier_trust("test", UserTier.PRO) >= 0)
        e = m.evaluate_proposal_impact({"x": 0.1}, [UserTier.PRO])
        log_test("EXP", "Proposal eval", "recommendation" in e)
    except Exception as e:
        log_test("EXP", "Tier context", False, str(e)[:50])
    
    print("\n7.5 Engine Feedback")
    try:
        from lncp.meta.engine_feedback import EngineFeedbackCollector
        c = EngineFeedbackCollector()
        log_test("EXP", "Engine accuracy", 0 <= c.get_overall_accuracy() <= 1)
        log_test("EXP", "Feedback summary", isinstance(c.get_summary(), dict))
    except Exception as e:
        log_test("EXP", "Engine feedback", False, str(e)[:50])


def test_orchestration():
    print("\n" + "═" * 70)
    print("8. ORCHESTRATION")
    print("═" * 70)
    
    try:
        from lncp.meta.meta_orchestrator import MetaOrchestrator
        o = MetaOrchestrator()
        log_test("ORCH", "MetaOrchestrator", o is not None)
        log_test("ORCH", "Status", o.get_status() is not None)
    except Exception as e:
        log_test("ORCH", "MetaOrchestrator", False, str(e)[:50])
    
    try:
        from lncp.meta.unified_orchestrator import UnifiedOrchestrator
        log_test("ORCH", "UnifiedOrchestrator", UnifiedOrchestrator() is not None)
    except Exception as e:
        log_test("ORCH", "UnifiedOrchestrator", False, str(e)[:50])
    
    try:
        from lncp.meta.config_store import ConfigStore
        log_test("ORCH", "ConfigStore", ConfigStore() is not None)
    except Exception as e:
        log_test("ORCH", "ConfigStore", False, str(e)[:50])


def test_blog():
    print("\n" + "═" * 70)
    print("9. BLOG OPTIMIZATION")
    print("═" * 70)
    
    try:
        from lncp.meta.blog.ab_testing import BlogExperimentManager, get_experiment_manager
        log_test("BLOG", "A/B Testing", get_experiment_manager() is not None)
    except Exception as e:
        log_test("BLOG", "A/B Testing", False, str(e)[:50])
    
    try:
        from lncp.meta.blog.classifier import BlogActionClassifier
        log_test("BLOG", "Classifier", BlogActionClassifier() is not None)
    except Exception as e:
        log_test("BLOG", "Classifier", False, str(e)[:50])
    
    try:
        from lncp.meta.blog.cta_tracker import CTATracker
        log_test("BLOG", "CTA Tracker", CTATracker() is not None)
    except Exception as e:
        log_test("BLOG", "CTA Tracker", False, str(e)[:50])
    
    try:
        from lncp.meta.blog.feedback import BlogFeedbackLoop
        log_test("BLOG", "Feedback Loop", BlogFeedbackLoop() is not None)
    except Exception as e:
        log_test("BLOG", "Feedback Loop", False, str(e)[:50])


def test_prescriptive():
    print("\n" + "═" * 70)
    print("10. PRESCRIPTIVE ANALYTICS")
    print("═" * 70)
    
    try:
        from lncp.meta.action_classifier import ActionClassifier
        log_test("PRESC", "ActionClassifier", ActionClassifier() is not None)
    except Exception as e:
        log_test("PRESC", "ActionClassifier", False, str(e)[:50])
    
    try:
        from lncp.meta.engine_parameters import EngineParameterAnalyzer
        log_test("PRESC", "EngineParameterAnalyzer", EngineParameterAnalyzer() is not None)
    except Exception as e:
        log_test("PRESC", "EngineParameterAnalyzer", False, str(e)[:50])
    
    try:
        from lncp.meta.attribution_tracker import AttributionTracker
        log_test("PRESC", "AttributionTracker", AttributionTracker() is not None)
    except Exception as e:
        log_test("PRESC", "AttributionTracker", False, str(e)[:50])


def test_command_center():
    print("\n" + "═" * 70)
    print("11. COMMAND CENTER")
    print("═" * 70)
    
    try:
        from lncp.meta.command_center import (
            CommandCenter, Domain, AlertSeverity, InjectionTier,
            ProposalStatus, get_command_center
        )
        cc = get_command_center()
        log_test("CMD", "Command Center", cc is not None)
        log_test("CMD", "Domains loaded", len(cc.domains) == 3, f"{len(cc.domains)} domains")
        log_test("CMD", "Proposals generated", len(cc.proposals) > 0, f"{len(cc.proposals)} proposals")
        
        # Check priority sorting
        priorities = [p.priority_score for p in cc.proposals]
        is_sorted = priorities == sorted(priorities, reverse=True)
        log_test("CMD", "Priority sorting", is_sorted)
        
        # Check injection queue
        queue = cc.get_injection_queue()
        log_test("CMD", "Injection queue", "immediate" in queue and "24hour" in queue)
        
        # Check state export
        state = cc.get_full_state()
        log_test("CMD", "State export", state["version"] == "5.1.1")
        log_test("CMD", "Audit trail", "audit_trail" in state)
        
        # Check summary
        summary = cc.get_summary()
        log_test("CMD", "Dashboard summary", summary["status"] == "OPERATIONAL")
        
    except Exception as e:
        log_test("CMD", "Command Center", False, str(e)[:50])


def run_master_test():
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " LNCP MASTER VALIDATION TEST v5.1.1 ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"\nTimestamp: {now().isoformat()}")
    
    test_core_engine()
    test_meta_foundation()
    test_meta_learning()
    test_meta_optimization()
    test_meta_integrations()
    test_meta_analytics()
    test_meta_experience()
    test_orchestration()
    test_blog()
    test_prescriptive()
    test_command_center()
    
    total = RESULTS["passed"] + RESULTS["failed"]
    rate = (RESULTS["passed"] / total * 100) if total > 0 else 0
    
    print("\n" + "═" * 70)
    print("RESULTS")
    print("═" * 70)
    print(f"\n  Total:  {total}")
    print(f"  Passed: {RESULTS['passed']} ({rate:.1f}%)")
    print(f"  Failed: {RESULTS['failed']}")
    
    cats = {}
    for d in RESULTS["details"]:
        c = d["category"]
        if c not in cats:
            cats[c] = [0, 0]
        cats[c][0 if d["passed"] else 1] += 1
    
    print("\n  By Category:")
    for c, (p, f) in cats.items():
        t = p + f
        r = (p / t * 100) if t > 0 else 0
        s = "✓" if f == 0 else "✗"
        print(f"    {s} {c:<8} {p}/{t} ({r:.0f}%)")
    
    if rate >= 95:
        status = "🚀 PRODUCTION READY"
    elif rate >= 85:
        status = "✅ READY (minor issues)"
    else:
        status = "❌ NOT READY"
    
    print(f"\n  STATUS: {status}")
    print("═" * 70)
    
    return RESULTS

if __name__ == "__main__":
    results = run_master_test()
    sys.exit(0 if results["failed"] == 0 else 1)
