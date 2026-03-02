#!/usr/bin/env python3
"""
QUIRRELY SUPER ADMIN API v1.0
System Pulse and Prescriptive Actions for Super Admins.

The Super Admin dashboard surfaces:
- Real-time system health from Master Test
- Prescriptive actions (opportunities, watches, risks)
- One-click refresh capability
- Historical comparison
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List
from fastapi import APIRouter, HTTPException, Depends, Header, BackgroundTasks
from pydantic import BaseModel

from master_test import (
    MasterTest,
    run_master_test,
    run_quick_test,
    BaselineExpectations,
    ActionSeverity,
)
from simulation_engine import SimulationConfig


# ═══════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════

router = APIRouter(prefix="/api/v2/super-admin", tags=["super-admin"])


# ═══════════════════════════════════════════════════════════════════════════
# IN-MEMORY CACHE (Replace with Redis/DB in production)
# ═══════════════════════════════════════════════════════════════════════════

_latest_test_results: Optional[Dict] = None
_test_history: List[Dict] = []
_is_running: bool = False


# ═══════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════

class RunTestRequest(BaseModel):
    quick: bool = False
    seed: Optional[int] = None


class SystemPulseResponse(BaseModel):
    overall_health: int
    health_breakdown: Dict[str, int]
    key_metrics: Dict[str, float]
    top_actions: List[Dict]
    last_updated: Optional[str]
    is_stale: bool


# ═══════════════════════════════════════════════════════════════════════════
# DEPENDENCIES
# ═══════════════════════════════════════════════════════════════════════════

def require_super_admin(authorization: Optional[str] = Header(None)) -> str:
    """Require super admin role."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # In production, check for super_admin role specifically
    # For now, just check for admin token
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization")
    
    return "super_admin"


# ═══════════════════════════════════════════════════════════════════════════
# SYSTEM PULSE ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/pulse")
async def get_system_pulse(admin: str = Depends(require_super_admin)):
    """
    Get the current system pulse.
    
    This is the primary endpoint for the Super Admin dashboard.
    Returns health scores, key metrics, and top prescriptive actions.
    """
    global _latest_test_results
    
    if not _latest_test_results:
        return {
            "overall_health": 0,
            "health_breakdown": {"conversion": 0, "value": 0, "retention": 0},
            "key_metrics": {},
            "top_actions": [],
            "last_updated": None,
            "is_stale": True,
            "message": "No test results available. Run a test to populate.",
        }
    
    pulse = _latest_test_results.get("system_pulse", {})
    meta = _latest_test_results.get("meta", {})
    
    # Check if results are stale (>24 hours old)
    last_run = meta.get("run_completed_at")
    is_stale = True
    if last_run:
        last_run_dt = datetime.fromisoformat(last_run)
        is_stale = datetime.utcnow() - last_run_dt > timedelta(hours=24)
    
    return {
        "overall_health": pulse.get("overall_health", 0),
        "health_breakdown": pulse.get("health_breakdown", {}),
        "key_metrics": pulse.get("key_metrics", {}),
        "top_actions": pulse.get("top_actions", []),
        "last_updated": last_run,
        "is_stale": is_stale,
    }


# ═══════════════════════════════════════════════════════════════════════════
# PRESCRIPTIVE ACTIONS ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/actions")
async def get_all_actions(admin: str = Depends(require_super_admin)):
    """Get all prescriptive actions from latest test."""
    global _latest_test_results
    
    if not _latest_test_results:
        return {"actions": [], "total": 0}
    
    actions = _latest_test_results.get("prescriptive_actions", {})
    
    return {
        "actions": actions.get("actions", []),
        "total": actions.get("total", 0),
        "by_severity": actions.get("by_severity", {}),
    }


@router.get("/actions/opportunities")
async def get_opportunities(admin: str = Depends(require_super_admin)):
    """Get opportunity actions only."""
    global _latest_test_results
    
    if not _latest_test_results:
        return {"actions": []}
    
    all_actions = _latest_test_results.get("prescriptive_actions", {}).get("actions", [])
    opportunities = [a for a in all_actions if a.get("severity") == "opportunity"]
    
    return {"actions": opportunities}


@router.get("/actions/watches")
async def get_watches(admin: str = Depends(require_super_admin)):
    """Get watch actions only."""
    global _latest_test_results
    
    if not _latest_test_results:
        return {"actions": []}
    
    all_actions = _latest_test_results.get("prescriptive_actions", {}).get("actions", [])
    watches = [a for a in all_actions if a.get("severity") == "watch"]
    
    return {"actions": watches}


@router.get("/actions/risks")
async def get_risks(admin: str = Depends(require_super_admin)):
    """Get risk actions only."""
    global _latest_test_results
    
    if not _latest_test_results:
        return {"actions": []}
    
    all_actions = _latest_test_results.get("prescriptive_actions", {}).get("actions", [])
    risks = [a for a in all_actions if a.get("severity") == "risk"]
    
    return {"actions": risks}


# ═══════════════════════════════════════════════════════════════════════════
# TEST EXECUTION ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.post("/run-test")
async def run_test(
    request: RunTestRequest,
    background_tasks: BackgroundTasks,
    admin: str = Depends(require_super_admin),
):
    """
    Run a new Master Test.
    
    Options:
    - quick: Run faster test with fewer users (500 users, 30 days)
    - seed: Set random seed for reproducibility
    """
    global _is_running
    
    if _is_running:
        return {
            "status": "already_running",
            "message": "A test is already in progress. Please wait.",
        }
    
    # Run in background
    background_tasks.add_task(_run_test_background, request.quick, request.seed)
    
    return {
        "status": "started",
        "message": "Test started. Check /pulse for results.",
        "estimated_duration_seconds": 5 if request.quick else 30,
    }


async def _run_test_background(quick: bool, seed: Optional[int]):
    """Background task to run the test."""
    global _latest_test_results, _test_history, _is_running
    
    _is_running = True
    
    try:
        if quick:
            results = run_quick_test()
        else:
            results = run_master_test(seed=seed)
        
        # Store in history
        if _latest_test_results:
            _test_history.append(_latest_test_results)
            # Keep last 10 runs
            if len(_test_history) > 10:
                _test_history = _test_history[-10:]
        
        _latest_test_results = results
        
    finally:
        _is_running = False


@router.get("/test-status")
async def get_test_status(admin: str = Depends(require_super_admin)):
    """Get current test status."""
    global _is_running, _latest_test_results
    
    return {
        "is_running": _is_running,
        "has_results": _latest_test_results is not None,
        "last_run": _latest_test_results.get("meta", {}).get("run_completed_at") if _latest_test_results else None,
    }


# ═══════════════════════════════════════════════════════════════════════════
# DETAILED RESULTS ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/results")
async def get_full_results(admin: str = Depends(require_super_admin)):
    """Get full test results."""
    global _latest_test_results
    
    if not _latest_test_results:
        raise HTTPException(status_code=404, detail="No test results available")
    
    return _latest_test_results


@router.get("/results/funnel")
async def get_funnel_results(admin: str = Depends(require_super_admin)):
    """Get funnel conversion rates."""
    global _latest_test_results
    
    if not _latest_test_results:
        return {"funnel_rates": {}}
    
    sim_results = _latest_test_results.get("simulation_results", {})
    
    return {
        "funnel_rates": sim_results.get("funnel_rates", {}),
        "stage_distribution": sim_results.get("stage_distribution", {}),
    }


@router.get("/results/countries")
async def get_country_results(admin: str = Depends(require_super_admin)):
    """Get results by country."""
    global _latest_test_results
    
    if not _latest_test_results:
        return {"country_stats": {}}
    
    sim_results = _latest_test_results.get("simulation_results", {})
    
    return {
        "country_stats": sim_results.get("country_stats", {}),
    }


@router.get("/results/tokens")
async def get_token_results(admin: str = Depends(require_super_admin)):
    """Get token generation distribution."""
    global _latest_test_results
    
    if not _latest_test_results:
        return {"generation_distribution": {}, "value_metrics": {}}
    
    sim_results = _latest_test_results.get("simulation_results", {})
    
    return {
        "generation_distribution": sim_results.get("generation_distribution", {}),
        "value_metrics": sim_results.get("value_metrics", {}),
    }


@router.get("/results/entry")
async def get_entry_results(admin: str = Depends(require_super_admin)):
    """Get direct vs .com entry results."""
    global _latest_test_results
    
    if not _latest_test_results:
        return {"entry_stats": {}}
    
    sim_results = _latest_test_results.get("simulation_results", {})
    
    return {
        "entry_stats": sim_results.get("entry_stats", {}),
    }


# ═══════════════════════════════════════════════════════════════════════════
# HISTORY ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/history")
async def get_test_history(admin: str = Depends(require_super_admin)):
    """Get history of test runs."""
    global _test_history
    
    return {
        "runs": [
            {
                "run_at": r.get("meta", {}).get("run_completed_at"),
                "overall_health": r.get("system_pulse", {}).get("overall_health"),
                "total_actions": r.get("prescriptive_actions", {}).get("total"),
            }
            for r in _test_history
        ],
        "count": len(_test_history),
    }


@router.get("/history/compare")
async def compare_to_previous(admin: str = Depends(require_super_admin)):
    """Compare current results to previous run."""
    global _latest_test_results, _test_history
    
    if not _latest_test_results:
        raise HTTPException(status_code=404, detail="No current results")
    
    if not _test_history:
        return {"comparison": None, "message": "No previous run to compare"}
    
    previous = _test_history[-1]
    current = _latest_test_results
    
    current_pulse = current.get("system_pulse", {})
    previous_pulse = previous.get("system_pulse", {})
    
    return {
        "comparison": {
            "health_delta": current_pulse.get("overall_health", 0) - previous_pulse.get("overall_health", 0),
            "conversion_delta": (
                current_pulse.get("health_breakdown", {}).get("conversion", 0) -
                previous_pulse.get("health_breakdown", {}).get("conversion", 0)
            ),
            "value_delta": (
                current_pulse.get("key_metrics", {}).get("avg_value", 0) -
                previous_pulse.get("key_metrics", {}).get("avg_value", 0)
            ),
            "actions_delta": (
                current.get("prescriptive_actions", {}).get("total", 0) -
                previous.get("prescriptive_actions", {}).get("total", 0)
            ),
        },
        "current_run": current.get("meta", {}).get("run_completed_at"),
        "previous_run": previous.get("meta", {}).get("run_completed_at"),
    }


# ═══════════════════════════════════════════════════════════════════════════
# SCENARIO TESTING
# ═══════════════════════════════════════════════════════════════════════════

class ScenarioRequest(BaseModel):
    name: str
    trial_convert_rate: Optional[float] = None
    signup_rate: Optional[float] = None
    churn_rate: Optional[float] = None


@router.post("/scenario")
async def run_scenario(
    request: ScenarioRequest,
    background_tasks: BackgroundTasks,
    admin: str = Depends(require_super_admin),
):
    """
    Run a what-if scenario test.
    
    Example: What if trial conversion increased to 35%?
    """
    overrides = {}
    
    if request.trial_convert_rate is not None:
        overrides["trial_convert_rate"] = request.trial_convert_rate
    
    if request.signup_rate is not None:
        overrides["signup_rate"] = request.signup_rate
    
    if request.churn_rate is not None:
        overrides["base_churn_rate"] = request.churn_rate
    
    # Run synchronously for scenarios (they're quick)
    config = SimulationConfig(
        total_users=1000,  # Smaller for scenarios
        simulation_days=30,
        seed=42,
    )
    
    for key, value in overrides.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    test = MasterTest(config=config)
    results = test.run()
    results["scenario_name"] = request.name
    results["scenario_overrides"] = overrides
    
    return {
        "scenario_name": request.name,
        "overrides": overrides,
        "system_pulse": results.get("system_pulse", {}),
        "comparison_to_baseline": {
            "health_delta": results.get("system_pulse", {}).get("overall_health", 0) - 70,  # Assume 70 baseline
        },
    }
