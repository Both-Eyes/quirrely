#!/usr/bin/env python3
"""
LNCP Admin API v1.0
Backend API for the admin dashboard.

Endpoints:
- GET  /api/admin/queue      - Get pending review queue
- POST /api/admin/approve    - Approve an action
- POST /api/admin/reject     - Reject an action
- POST /api/admin/run-cycle  - Run optimization cycle
- GET  /api/admin/status     - Get system status
- GET  /api/admin/experiments - Get A/B experiments
- GET  /api/admin/insights   - Get recent insights

This provides the API layer for the admin UI.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any
import sys
import json

# Add LNCP to path
sys.path.insert(0, '/mnt/user-data/outputs/lncp-web-app')

from lncp.meta import (
    get_unified_orchestrator,
    UnifiedMode,
    Domain,
)
from lncp.meta.blog import (
    get_experiment_manager,
    get_blog_tracker,
    get_cta_tracker,
    get_blog_feedback_loop,
)


# ═══════════════════════════════════════════════════════════════════════════
# ADMIN API HANDLERS
# ═══════════════════════════════════════════════════════════════════════════

class AdminAPI:
    """
    Admin API for the LNCP dashboard.
    """
    
    def __init__(self):
        self.orchestrator = get_unified_orchestrator()
        self.experiments = get_experiment_manager()
        self.blog_tracker = get_blog_tracker()
        self.cta_tracker = get_cta_tracker()
        self.feedback = get_blog_feedback_loop()
    
    # ─────────────────────────────────────────────────────────────────────
    # QUEUE ENDPOINTS
    # ─────────────────────────────────────────────────────────────────────
    
    def get_queue(self) -> Dict:
        """Get the current review queue."""
        queue = self.orchestrator.get_review_queue()
        
        # Get stats
        status = self.orchestrator.get_status()
        last_cycle = status.get("last_cycle", {})
        
        # Get insights from last cycle
        insights = self.orchestrator.get_insights(limit=5)
        
        return {
            "success": True,
            "actions": queue,
            "insights": insights,
            "stats": {
                "pending": len(queue),
                "applied": last_cycle.get("combined", {}).get("total_applied", 0) if last_cycle else 0,
                "health": last_cycle.get("app", {}).get("health", 0) if last_cycle else 0,
                "experiments": len(self.experiments.get_running_experiments()),
            },
        }
    
    def approve_action(self, action_id: str) -> Dict:
        """Approve an action from the review queue."""
        success = self.orchestrator.approve_action(action_id)
        
        return {
            "success": success,
            "action_id": action_id,
            "message": "Action approved and queued for execution" if success else "Action not found",
        }
    
    def reject_action(self, action_id: str, reason: str = "") -> Dict:
        """Reject an action from the review queue."""
        success = self.orchestrator.reject_action(action_id, reason)
        
        return {
            "success": success,
            "action_id": action_id,
            "message": "Action rejected" if success else "Action not found",
        }
    
    def bulk_approve(self, action_ids: List[str]) -> Dict:
        """Approve multiple actions."""
        results = []
        for action_id in action_ids:
            success = self.orchestrator.approve_action(action_id)
            results.append({"action_id": action_id, "success": success})
        
        return {
            "success": True,
            "results": results,
            "approved_count": sum(1 for r in results if r["success"]),
        }
    
    def bulk_reject(self, action_ids: List[str], reason: str = "") -> Dict:
        """Reject multiple actions."""
        results = []
        for action_id in action_ids:
            success = self.orchestrator.reject_action(action_id, reason)
            results.append({"action_id": action_id, "success": success})
        
        return {
            "success": True,
            "results": results,
            "rejected_count": sum(1 for r in results if r["success"]),
        }
    
    # ─────────────────────────────────────────────────────────────────────
    # CYCLE ENDPOINTS
    # ─────────────────────────────────────────────────────────────────────
    
    def run_cycle(self, domains: str = "all") -> Dict:
        """Run an optimization cycle."""
        domain_map = {
            "all": Domain.ALL,
            "app": Domain.APP,
            "blog": Domain.BLOG,
        }
        domain = domain_map.get(domains.lower(), Domain.ALL)
        
        try:
            result = self.orchestrator.run_cycle(force=True, domains=domain)
            
            return {
                "success": True,
                "cycle_id": result.cycle_id,
                "duration_seconds": (result.completed_at - result.started_at).total_seconds(),
                "app": {
                    "health": result.app_health,
                    "actions": result.app_actions_total,
                    "auto_apply": result.app_auto_apply,
                    "human_review": result.app_human_review,
                },
                "blog": {
                    "pages_tracked": result.blog_pages_tracked,
                    "experiments": result.blog_experiments_running,
                    "actions": result.blog_actions_total,
                    "auto_apply": result.blog_auto_apply,
                    "human_review": result.blog_human_review,
                },
                "insights": result.insights,
                "pending_review": len(result.pending_review),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    # ─────────────────────────────────────────────────────────────────────
    # STATUS ENDPOINTS
    # ─────────────────────────────────────────────────────────────────────
    
    def get_status(self) -> Dict:
        """Get overall system status."""
        status = self.orchestrator.get_status()
        
        # Add more details
        blog_summary = self.blog_tracker.get_summary()
        cta_summary = self.cta_tracker.get_summary()
        exp_summary = self.experiments.get_summary()
        
        return {
            "success": True,
            "orchestrator": status,
            "blog": {
                "pages_tracked": blog_summary.get("unique_pages", 0),
                "total_views": blog_summary.get("total_views", 0),
                "cta_clicks": blog_summary.get("total_cta_clicks", 0),
                "signups": blog_summary.get("total_signups", 0),
            },
            "cta": {
                "total_impressions": cta_summary.get("total_impressions", 0),
                "total_clicks": cta_summary.get("total_clicks", 0),
                "overall_click_rate": cta_summary.get("overall_click_rate", 0),
            },
            "experiments": exp_summary,
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    # ─────────────────────────────────────────────────────────────────────
    # EXPERIMENT ENDPOINTS
    # ─────────────────────────────────────────────────────────────────────
    
    def get_experiments(self, status: str = None) -> Dict:
        """Get A/B experiments."""
        if status == "running":
            experiments = self.experiments.get_running_experiments()
        elif status == "concluded":
            experiments = self.experiments.get_concluded_experiments()
        else:
            experiments = list(self.experiments.experiments.values())
        
        return {
            "success": True,
            "experiments": [exp.to_dict() for exp in experiments],
            "summary": self.experiments.get_summary(),
        }
    
    def conclude_experiment(self, experiment_id: str) -> Dict:
        """Manually conclude an experiment."""
        result = self.experiments.conclude_experiment(experiment_id)
        
        if result:
            return {
                "success": True,
                "experiment_id": experiment_id,
                "result": result.value,
            }
        else:
            return {
                "success": False,
                "error": "Cannot conclude experiment yet",
            }
    
    # ─────────────────────────────────────────────────────────────────────
    # INSIGHTS ENDPOINTS
    # ─────────────────────────────────────────────────────────────────────
    
    def get_insights(self, limit: int = 10) -> Dict:
        """Get recent insights."""
        insights = self.orchestrator.get_insights(limit=limit)
        
        # Also get feedback loop insights
        feedback_result = self.feedback.run_cycle()
        feedback_insights = feedback_result.get("insights", [])
        
        all_insights = insights + [{"domain": "feedback", **i} for i in feedback_insights]
        
        return {
            "success": True,
            "insights": all_insights[:limit],
            "total": len(all_insights),
        }
    
    # ─────────────────────────────────────────────────────────────────────
    # ANALYTICS ENDPOINTS
    # ─────────────────────────────────────────────────────────────────────
    
    def get_blog_analytics(self) -> Dict:
        """Get blog analytics."""
        summary = self.blog_tracker.get_summary()
        top_pages = self.blog_tracker.get_top_pages(limit=10)
        underperforming = self.blog_tracker.get_underperforming_pages(limit=5)
        
        return {
            "success": True,
            "summary": summary,
            "top_pages": [
                {
                    "url": p.page_url,
                    "views": p.total_views,
                    "cta_click_rate": p.cta_click_rate,
                    "performance_score": p.performance_score,
                    "tier": p.tier,
                }
                for p in top_pages
            ],
            "underperforming": [
                {
                    "url": p.page_url,
                    "views": p.total_views,
                    "performance_score": p.performance_score,
                    "tier": p.tier,
                }
                for p in underperforming
            ],
        }
    
    def get_cta_analytics(self) -> Dict:
        """Get CTA analytics."""
        summary = self.cta_tracker.get_summary()
        comparison = self.cta_tracker.get_variant_comparison()
        recommendations = self.cta_tracker.get_recommendations()
        
        return {
            "success": True,
            "summary": summary,
            "variant_comparison": comparison,
            "recommendations": recommendations,
        }


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_admin_api: Optional[AdminAPI] = None

def get_admin_api() -> AdminAPI:
    global _admin_api
    if _admin_api is None:
        _admin_api = AdminAPI()
    return _admin_api


# ═══════════════════════════════════════════════════════════════════════════
# REQUEST HANDLERS (for Flask/FastAPI integration)
# ═══════════════════════════════════════════════════════════════════════════

def handle_get_queue() -> Dict:
    return get_admin_api().get_queue()

def handle_approve(request_body: Dict) -> Dict:
    action_id = request_body.get("action_id")
    if not action_id:
        return {"success": False, "error": "action_id required"}
    return get_admin_api().approve_action(action_id)

def handle_reject(request_body: Dict) -> Dict:
    action_id = request_body.get("action_id")
    reason = request_body.get("reason", "")
    if not action_id:
        return {"success": False, "error": "action_id required"}
    return get_admin_api().reject_action(action_id, reason)

def handle_run_cycle(request_body: Dict) -> Dict:
    domains = request_body.get("domains", "all")
    return get_admin_api().run_cycle(domains)

def handle_get_status() -> Dict:
    return get_admin_api().get_status()

def handle_get_experiments(params: Dict) -> Dict:
    status = params.get("status")
    return get_admin_api().get_experiments(status)

def handle_get_insights(params: Dict) -> Dict:
    limit = int(params.get("limit", 10))
    return get_admin_api().get_insights(limit)

def handle_get_blog_analytics() -> Dict:
    return get_admin_api().get_blog_analytics()

def handle_get_cta_analytics() -> Dict:
    return get_admin_api().get_cta_analytics()


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "AdminAPI",
    "get_admin_api",
    "handle_get_queue",
    "handle_approve",
    "handle_reject",
    "handle_run_cycle",
    "handle_get_status",
    "handle_get_experiments",
    "handle_get_insights",
    "handle_get_blog_analytics",
    "handle_get_cta_analytics",
]
