#!/usr/bin/env python3
"""
LNCP META E2E VALIDATION v5.1.0
Comprehensive end-to-end test for Knight of Wands v3.1.1 + Blog/SEO Integration.

Tests:
- Meta Orchestrator v5.1.0 integration
- All v3.1.1 observers (Achievement, Retention, Bundle, Progressive)
- v5.1 Blog Observer
- Event schema (151 events)
- Action domains (19 domains)
- Health calculations
- Optimization suggestions
"""

import sys
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

# Test results tracking
@dataclass
class TestResult:
    category: str
    test_name: str
    passed: bool
    message: str = ""

results: List[TestResult] = []

def test(category: str, name: str, condition: bool, message: str = ""):
    """Record a test result."""
    results.append(TestResult(category, name, condition, message))
    status = "✅" if condition else "❌"
    print(f"  {status} {name}")
    if not condition and message:
        print(f"     → {message}")

def run_tests():
    """Run all E2E tests."""
    print("="*70)
    print("KNIGHT OF WANDS v3.1.1 + v5.1 E2E VALIDATION")
    print("="*70)
    print()
    
    # ═══════════════════════════════════════════════════════════════════
    # 1. VERSION & IMPORTS
    # ═══════════════════════════════════════════════════════════════════
    print("1. VERSION & IMPORTS")
    print("-"*40)
    
    try:
        from lncp.meta import __version__, __release__
        test("imports", "Meta version is 5.1.0-G2M", __version__ == "5.1.0-G2M", f"Got {__version__}")
        test("imports", "Meta release is G2M", __release__ == "G2M", f"Got {__release__}")
    except Exception as e:
        test("imports", "Meta version import", False, str(e))
    
    # v3.1.1 observers
    try:
        from lncp.meta import get_achievement_observer, AchievementObserver
        obs = get_achievement_observer()
        test("imports", "Achievement Observer", isinstance(obs, AchievementObserver))
    except Exception as e:
        test("imports", "Achievement Observer", False, str(e))
    
    try:
        from lncp.meta import get_retention_observer, RetentionObserver
        obs = get_retention_observer()
        test("imports", "Retention Observer", isinstance(obs, RetentionObserver))
    except Exception as e:
        test("imports", "Retention Observer", False, str(e))
    
    try:
        from lncp.meta import get_bundle_tracker, BundleTracker
        tracker = get_bundle_tracker()
        test("imports", "Bundle Tracker", isinstance(tracker, BundleTracker))
    except Exception as e:
        test("imports", "Bundle Tracker", False, str(e))
    
    try:
        from lncp.meta import get_progressive_tracker, ProgressiveTracker
        tracker = get_progressive_tracker()
        test("imports", "Progressive Tracker", isinstance(tracker, ProgressiveTracker))
    except Exception as e:
        test("imports", "Progressive Tracker", False, str(e))
    
    # v5.1 Blog Observer
    try:
        from lncp.meta import get_blog_observer, BlogObserver
        obs = get_blog_observer()
        test("imports", "Blog Observer (v5.1)", isinstance(obs, BlogObserver))
    except Exception as e:
        test("imports", "Blog Observer (v5.1)", False, str(e))
    
    print()
    
    # ═══════════════════════════════════════════════════════════════════
    # 2. EVENT SCHEMA
    # ═══════════════════════════════════════════════════════════════════
    print("2. EVENT SCHEMA")
    print("-"*40)
    
    try:
        from lncp.meta.events.schema import EventType
        events = list(EventType)
        test("schema", f"Event count ≥ 150", len(events) >= 150, f"Got {len(events)}")
        
        # Check v3.1.1 events
        v311_prefixes = ['achievement.', 'progressive.', 'bundle.', 'retention.', 
                         'annual.', 'notification.', 'social.', 'tier.', 'hook.', 'cta.', 'geo.']
        v311_events = [e for e in events if any(e.value.startswith(p) for p in v311_prefixes)]
        test("schema", f"v3.1.1 events ≥ 75", len(v311_events) >= 75, f"Got {len(v311_events)}")
        
        # Check v5.1 blog/SEO events
        v51_prefixes = ['blog.', 'seo.', 'content.']
        v51_events = [e for e in events if any(e.value.startswith(p) for p in v51_prefixes)]
        test("schema", f"v5.1 blog/SEO events ≥ 20", len(v51_events) >= 20, f"Got {len(v51_events)}")
        
        # Specific blog events
        blog_events = ['blog.page_viewed', 'blog.cta_clicked', 'blog.scroll_depth']
        for be in blog_events:
            found = any(e.value == be for e in events)
            test("schema", f"Event: {be}", found)
        
        # Specific SEO events
        seo_events = ['seo.impression', 'seo.click', 'seo.position_changed']
        for se in seo_events:
            found = any(e.value == se for e in events)
            test("schema", f"Event: {se}", found)
            
    except Exception as e:
        test("schema", "Event schema loading", False, str(e))
    
    print()
    
    # ═══════════════════════════════════════════════════════════════════
    # 3. ACTION DOMAINS
    # ═══════════════════════════════════════════════════════════════════
    print("3. ACTION DOMAINS")
    print("-"*40)
    
    try:
        from lncp.meta.action_classifier import ActionDomain
        domains = [d.value for d in ActionDomain]
        test("domains", f"Total domains ≥ 19", len(domains) >= 19, f"Got {len(domains)}")
        
        # v3.1.1 domains
        v311_domains = ['gamification', 'progressive', 'bundling', 'retention', 
                        'notification', 'social_proof', 'tier_pricing']
        for d in v311_domains:
            test("domains", f"v3.1.1 domain: {d}", d in domains)
        
        # v5.1 SEO domains
        v51_domains = ['seo', 'seo_content', 'seo_technical']
        for d in v51_domains:
            test("domains", f"v5.1 domain: {d}", d in domains)
            
    except Exception as e:
        test("domains", "Action domains loading", False, str(e))
    
    print()
    
    # ═══════════════════════════════════════════════════════════════════
    # 4. META ORCHESTRATOR v5.1
    # ═══════════════════════════════════════════════════════════════════
    print("4. META ORCHESTRATOR v5.1")
    print("-"*40)
    
    try:
        from lncp.meta.meta_orchestrator import MetaOrchestrator, get_meta_orchestrator
        orch = get_meta_orchestrator()
        
        test("orchestrator", "Version is 5.1.0-G2M", orch.VERSION == "5.1.0-G2M", f"Got {orch.VERSION}")
        test("orchestrator", "Release is G2M", orch.RELEASE == "G2M", f"Got {getattr(orch, 'RELEASE', 'missing')}")
        
        # Check all observers attached
        test("orchestrator", "Achievement observer attached", orch.achievement_observer is not None)
        test("orchestrator", "Retention observer attached", orch.retention_observer is not None)
        test("orchestrator", "Bundle tracker attached", orch.bundle_tracker is not None)
        test("orchestrator", "Progressive tracker attached", orch.progressive_tracker is not None)
        test("orchestrator", "Blog observer attached (v5.1)", orch.blog_observer is not None)
        
        # Test methods exist
        test("orchestrator", "get_v311_health() exists", hasattr(orch, 'get_v311_health'))
        test("orchestrator", "get_v311_summary() exists", hasattr(orch, 'get_v311_summary'))
        test("orchestrator", "get_seo_health() exists (v5.1)", hasattr(orch, 'get_seo_health'))
        
        # Test method execution
        v311_health = orch.get_v311_health()
        test("orchestrator", "get_v311_health() returns dict", isinstance(v311_health, dict))
        test("orchestrator", "v311_health has achievement", "achievement" in v311_health)
        test("orchestrator", "v311_health has retention", "retention" in v311_health)
        test("orchestrator", "v311_health has bundle", "bundle" in v311_health)
        test("orchestrator", "v311_health has progressive", "progressive" in v311_health)
        
        seo_health = orch.get_seo_health()
        test("orchestrator", "get_seo_health() returns dict", isinstance(seo_health, dict))
        test("orchestrator", "seo_health has overall_score", "overall_score" in seo_health)
        test("orchestrator", "seo_health has impressions", "impressions" in seo_health)
        test("orchestrator", "seo_health has pages", "pages" in seo_health)
        
        summary = orch.get_v311_summary()
        test("orchestrator", "get_v311_summary() returns dict", isinstance(summary, dict))
        test("orchestrator", "summary has seo (v5.1)", "seo" in summary)
        test("orchestrator", "summary version is 3.1.1", summary.get("version") == "3.1.1")
        test("orchestrator", "orchestrator_version is 5.1.0-G2M", summary.get("orchestrator_version") == "5.1.0-G2M")
        
        # Test status
        status = orch.get_status()
        test("orchestrator", "status has seo metrics", "seo" in status)
        
    except Exception as e:
        test("orchestrator", "Meta orchestrator initialization", False, str(e))
    
    print()
    
    # ═══════════════════════════════════════════════════════════════════
    # 5. BLOG OBSERVER FUNCTIONALITY
    # ═══════════════════════════════════════════════════════════════════
    print("5. BLOG OBSERVER FUNCTIONALITY")
    print("-"*40)
    
    try:
        from lncp.meta.blog_observer import BlogObserver, get_blog_observer
        blog_obs = get_blog_observer()
        
        # Test GSC data ingestion
        blog_obs.ingest_gsc_data(
            page_url="/blog/how-to-find-your-voice",
            impressions=5000,
            clicks=150,
            ctr=0.03,
            position=8.5,
            date_str="2026-02-16",
            queries=[
                {"query": "writing voice", "impressions": 1000, "clicks": 30, "ctr": 0.03, "position": 7.2},
                {"query": "find writing style", "impressions": 800, "clicks": 25, "ctr": 0.031, "position": 9.1},
            ]
        )
        test("blog_observer", "GSC data ingestion", len(blog_obs._pages) > 0)
        
        # Test page view tracking
        blog_obs.track_page_view(
            page_url="/blog/how-to-find-your-voice",
            session_id="sess_001",
            user_id="user_001",
            referrer="google",
            device="desktop"
        )
        test("blog_observer", "Page view tracking", len(blog_obs._page_view_events) > 0)
        
        # Test CTA tracking
        blog_obs.track_cta_event(
            page_url="/blog/how-to-find-your-voice",
            cta_id="cta_analyze",
            event_type="click",
            session_id="sess_001"
        )
        test("blog_observer", "CTA event tracking", len(blog_obs._cta_events) > 0)
        
        # Test content registration
        blog_obs.register_content(
            page_url="/blog/how-to-find-your-voice",
            publish_date=datetime.utcnow() - timedelta(days=60),
            last_updated=datetime.utcnow() - timedelta(days=30),
            word_count=2500
        )
        test("blog_observer", "Content registration", len(blog_obs._content_registry) > 0)
        
        # Test health calculation
        health = blog_obs.get_health()
        test("blog_observer", "Health calculation", health is not None)
        test("blog_observer", "Health has overall_score", hasattr(health, 'overall_score'))
        test("blog_observer", "Health has total_impressions", hasattr(health, 'total_impressions'))
        test("blog_observer", "Health has pages_performing", hasattr(health, 'pages_performing'))
        
        # Test optimization suggestions
        suggestions = blog_obs.suggest_optimizations()
        test("blog_observer", "Optimization suggestions generated", isinstance(suggestions, list))
        
        # Test keyword opportunity detection
        opportunities = blog_obs.detect_keyword_opportunities()
        test("blog_observer", "Keyword opportunities detected", isinstance(opportunities, list))
        
    except Exception as e:
        test("blog_observer", "Blog observer functionality", False, str(e))
    
    print()
    
    # ═══════════════════════════════════════════════════════════════════
    # 6. v3.1.1 OBSERVER FUNCTIONALITY
    # ═══════════════════════════════════════════════════════════════════
    print("6. v3.1.1 OBSERVER FUNCTIONALITY")
    print("-"*40)
    
    # Achievement Observer
    try:
        from lncp.meta.achievement_observer import get_achievement_observer
        ach_obs = get_achievement_observer()
        
        ach_obs.track_badge_earned("user_001", "first_week", 100, 7.0)
        ach_obs.track_xp_gained("user_001", 100, "badge", "first_week")
        ach_obs.track_streak_event("user_001", "continued", 5, 50)
        
        health = ach_obs.get_health()
        test("observers", "Achievement health calculated", health is not None)
        
        suggestions = ach_obs.suggest_optimizations()
        test("observers", "Achievement suggestions generated", isinstance(suggestions, list))
        
    except Exception as e:
        test("observers", "Achievement observer", False, str(e))
    
    # Retention Observer
    try:
        from lncp.meta.retention_observer import get_retention_observer, ChurnIntent, InterventionType, InterventionOutcome
        ret_obs = get_retention_observer()
        
        ret_obs.track_churn_intent("user_002", ChurnIntent.CANCEL_CLICKED, 4.99, "pro", 45)
        int_id = ret_obs.track_intervention_shown("user_002", InterventionType.PAUSE_OFFER, 4.99)
        ret_obs.track_intervention_outcome(int_id, InterventionOutcome.ACCEPTED, 4.99, 5.2)
        
        health = ret_obs.get_health()
        test("observers", "Retention health calculated", health is not None)
        
        suggestions = ret_obs.suggest_optimizations()
        test("observers", "Retention suggestions generated", isinstance(suggestions, list))
        
    except Exception as e:
        test("observers", "Retention observer", False, str(e))
    
    # Bundle Tracker
    try:
        from lncp.meta.bundle_tracker import get_bundle_tracker
        bundle = get_bundle_tracker()
        
        bundle.track_bundle_section_viewed("user_003", ["pro_vs"], "free", "CA")
        bundle.track_bundle_purchased("user_003", "pro_vs", 12.99, 1.99, "CAD", "monthly")
        
        health = bundle.get_health()
        test("observers", "Bundle health calculated", health is not None)
        
        suggestions = bundle.suggest_optimizations()
        test("observers", "Bundle suggestions generated", isinstance(suggestions, list))
        
    except Exception as e:
        test("observers", "Bundle tracker", False, str(e))
    
    # Progressive Tracker
    try:
        from lncp.meta.progressive_tracker import get_progressive_tracker
        prog = get_progressive_tracker()
        
        prog.track_user_started("user_004", "CA", None)
        prog.track_day_reached("user_004", 3)
        prog.track_feature_unlocked("user_004", "day3_voice_profile", 3)
        
        health = prog.get_health()
        test("observers", "Progressive health calculated", health is not None)
        
        suggestions = prog.suggest_optimizations()
        test("observers", "Progressive suggestions generated", isinstance(suggestions, list))
        
    except Exception as e:
        test("observers", "Progressive tracker", False, str(e))
    
    print()
    
    # ═══════════════════════════════════════════════════════════════════
    # 7. INTEGRATION TEST
    # ═══════════════════════════════════════════════════════════════════
    print("7. INTEGRATION TEST")
    print("-"*40)
    
    try:
        from lncp.meta.meta_orchestrator import get_meta_orchestrator, MetaMode
        orch = get_meta_orchestrator()
        orch.set_mode(MetaMode.LEARN_ONLY)
        
        # Run a cycle
        result = orch.run_cycle()
        test("integration", "Cycle completed", result is not None)
        test("integration", "Cycle has errors list", hasattr(result, 'errors'))
        
        # Check final status
        status = orch.get_status()
        test("integration", "Status version correct", status.get("version") == "5.1.0-G2M")
        test("integration", "Status has v311 metrics", "v311" in status)
        test("integration", "Status has seo metrics", "seo" in status)
        
        # Check full summary
        summary = orch.get_v311_summary()
        test("integration", "Summary includes SEO", "seo" in summary)
        test("integration", "Summary orchestrator version", summary.get("orchestrator_version") == "5.1.0-G2M")
        
    except Exception as e:
        test("integration", "Integration test", False, str(e))
    
    print()
    
    # ═══════════════════════════════════════════════════════════════════
    # SUMMARY
    # ═══════════════════════════════════════════════════════════════════
    print("="*70)
    print("E2E VALIDATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    total = len(results)
    
    print()
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pass Rate: {passed/total*100:.1f}%")
    print()
    
    # Summary by category
    categories = {}
    for r in results:
        if r.category not in categories:
            categories[r.category] = {"passed": 0, "failed": 0}
        if r.passed:
            categories[r.category]["passed"] += 1
        else:
            categories[r.category]["failed"] += 1
    
    print("By Category:")
    for cat, stats in categories.items():
        total_cat = stats["passed"] + stats["failed"]
        status = "✅" if stats["failed"] == 0 else "❌"
        print(f"  {status} {cat}: {stats['passed']}/{total_cat}")
    
    print()
    
    # Failed tests
    failed_tests = [r for r in results if not r.passed]
    if failed_tests:
        print("Failed Tests:")
        for r in failed_tests:
            print(f"  ❌ [{r.category}] {r.test_name}")
            if r.message:
                print(f"     → {r.message}")
    
    print()
    print("="*70)
    
    # Return results for JSON export
    return {
        "version": "5.1.0",
        "timestamp": datetime.utcnow().isoformat(),
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": passed/total*100,
        "categories": categories,
        "results": [
            {
                "category": r.category,
                "test": r.test_name,
                "passed": r.passed,
                "message": r.message
            }
            for r in results
        ]
    }


if __name__ == "__main__":
    sys.path.insert(0, ".")
    
    report = run_tests()
    
    # Save JSON report
    with open("e2e_validation_report_v5.1.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"Report saved to e2e_validation_report_v5.1.json")
    
    # Exit with appropriate code
    sys.exit(0 if report["failed"] == 0 else 1)
