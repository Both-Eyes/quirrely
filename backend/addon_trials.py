#!/usr/bin/env python3
"""
QUIRRELY ADDON TRIAL SYSTEM v1.0
Manages 7-day free trials for Voice + Style addon.

Features:
- Start trial for eligible users
- Track trial status and expiration
- Convert trial to paid
- Email triggers for trial lifecycle

Expected Impact:
- +50% addon attach rate (8% → 12%)
- +$2,000/mo per 10K users
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from dependencies import get_current_user, CurrentUser
from feature_gate import FeatureGate, Addon, get_feature_gate
from conversion_events import get_conversion_tracker, ConversionEvent
from halo_bridge import get_halo_bridge

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v2/addons", tags=["addons"])


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

ADDON_TRIAL_CONFIG = {
    "voice_style": {
        "trial_days": 7,
        "price_monthly": 4.99,
        "price_annual": 49.99,
        "features": [
            "Full voice profile analysis",
            "Writing style breakdown",
            "Voice evolution tracking",
            "Personalized writing tips",
            "Author comparisons",
        ],
        "email_triggers": {
            "trial_started": True,
            "trial_day_3": True,
            "trial_day_6": True,
            "trial_expired": True,
        },
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# TRIAL STATUS
# ═══════════════════════════════════════════════════════════════════════════

class TrialStatus(str, Enum):
    """Addon trial status."""
    NOT_STARTED = "not_started"
    ACTIVE = "active"
    EXPIRING = "expiring"  # < 3 days left
    EXPIRED = "expired"
    CONVERTED = "converted"
    ALREADY_OWNED = "already_owned"


@dataclass
class AddonTrialInfo:
    """Information about a user's addon trial."""
    addon: str
    status: TrialStatus
    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    days_remaining: Optional[int] = None
    converted_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "addon": self.addon,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "days_remaining": self.days_remaining,
            "converted_at": self.converted_at.isoformat() if self.converted_at else None,
        }


# ═══════════════════════════════════════════════════════════════════════════
# TRIAL MANAGER
# ═══════════════════════════════════════════════════════════════════════════

class AddonTrialManager:
    """
    Manages addon trials.
    
    In production, this would use a database. For now, uses in-memory storage.
    """
    
    def __init__(self):
        self._trials: Dict[str, Dict[str, Any]] = {}  # user_id -> trial data
        self._conversion_tracker = get_conversion_tracker()
        self._halo = get_halo_bridge()
        self._gate = get_feature_gate()
    
    def _get_trial_key(self, user_id: str, addon: str) -> str:
        return f"{user_id}:{addon}"
    
    def get_trial_status(self, user_id: str, addon: str = "voice_style") -> AddonTrialInfo:
        """Get trial status for a user and addon."""
        key = self._get_trial_key(user_id, addon)
        
        # Check if user already owns addon
        user_tier = self._gate.get_user_tier(user_id)
        if addon in user_tier.addons:
            return AddonTrialInfo(
                addon=addon,
                status=TrialStatus.ALREADY_OWNED,
            )
        
        # Check for active/expired trial
        if key in self._trials:
            trial = self._trials[key]
            started_at = trial["started_at"]
            expires_at = trial["expires_at"]
            converted_at = trial.get("converted_at")
            
            if converted_at:
                return AddonTrialInfo(
                    addon=addon,
                    status=TrialStatus.CONVERTED,
                    started_at=started_at,
                    expires_at=expires_at,
                    converted_at=converted_at,
                )
            
            now = datetime.utcnow()
            if now >= expires_at:
                return AddonTrialInfo(
                    addon=addon,
                    status=TrialStatus.EXPIRED,
                    started_at=started_at,
                    expires_at=expires_at,
                    days_remaining=0,
                )
            
            days_remaining = (expires_at - now).days
            status = TrialStatus.EXPIRING if days_remaining <= 3 else TrialStatus.ACTIVE
            
            return AddonTrialInfo(
                addon=addon,
                status=status,
                started_at=started_at,
                expires_at=expires_at,
                days_remaining=days_remaining,
            )
        
        return AddonTrialInfo(
            addon=addon,
            status=TrialStatus.NOT_STARTED,
        )
    
    async def start_trial(
        self,
        user_id: str,
        addon: str = "voice_style",
    ) -> AddonTrialInfo:
        """Start a trial for a user."""
        key = self._get_trial_key(user_id, addon)
        config = ADDON_TRIAL_CONFIG.get(addon, {})
        
        # Check eligibility
        current_status = self.get_trial_status(user_id, addon)
        
        if current_status.status == TrialStatus.ALREADY_OWNED:
            raise ValueError("User already owns this addon")
        
        if current_status.status in (TrialStatus.ACTIVE, TrialStatus.EXPIRING):
            raise ValueError("User already has an active trial")
        
        if current_status.status == TrialStatus.EXPIRED:
            raise ValueError("User's trial has already expired")
        
        if current_status.status == TrialStatus.CONVERTED:
            raise ValueError("User has already converted")
        
        # Start trial
        now = datetime.utcnow()
        trial_days = config.get("trial_days", 7)
        expires_at = now + timedelta(days=trial_days)
        
        self._trials[key] = {
            "user_id": user_id,
            "addon": addon,
            "started_at": now,
            "expires_at": expires_at,
        }
        
        # Grant temporary addon access
        self._gate.add_addon(user_id, Addon.VOICE_STYLE)
        
        # Track conversion event
        await self._conversion_tracker.track_addon_purchase(
            user_id=user_id,
            addon=f"{addon}_trial",
            revenue=0,
        )
        
        # Track in HALO
        await self._halo.observe_conversion(
            user_id=user_id,
            conversion_type="addon_trial_started",
            details={"addon": addon, "trial_days": trial_days},
        )
        
        logger.info(f"Started {addon} trial for user {user_id}")
        
        return AddonTrialInfo(
            addon=addon,
            status=TrialStatus.ACTIVE,
            started_at=now,
            expires_at=expires_at,
            days_remaining=trial_days,
        )
    
    async def convert_trial(
        self,
        user_id: str,
        addon: str = "voice_style",
        plan: str = "monthly",
    ) -> AddonTrialInfo:
        """Convert trial to paid subscription."""
        key = self._get_trial_key(user_id, addon)
        config = ADDON_TRIAL_CONFIG.get(addon, {})
        
        # Check trial exists
        if key not in self._trials:
            raise ValueError("No trial found")
        
        trial = self._trials[key]
        
        # Check not already converted
        if trial.get("converted_at"):
            raise ValueError("Trial already converted")
        
        # Record conversion
        now = datetime.utcnow()
        trial["converted_at"] = now
        
        # Get revenue
        revenue = config.get("price_monthly", 4.99) if plan == "monthly" else config.get("price_annual", 49.99)
        
        # Track conversion
        await self._conversion_tracker.track_addon_purchase(
            user_id=user_id,
            addon=addon,
            revenue=revenue,
        )
        
        # Track in HALO
        await self._halo.observe_conversion(
            user_id=user_id,
            conversion_type="addon_purchased",
            details={"addon": addon, "plan": plan, "revenue": revenue, "from_trial": True},
        )
        
        logger.info(f"Converted {addon} trial for user {user_id} to {plan}")
        
        return AddonTrialInfo(
            addon=addon,
            status=TrialStatus.CONVERTED,
            started_at=trial["started_at"],
            expires_at=trial["expires_at"],
            converted_at=now,
        )
    
    async def expire_trial(self, user_id: str, addon: str = "voice_style") -> bool:
        """Expire a trial (called by cron/background job)."""
        key = self._get_trial_key(user_id, addon)
        
        if key not in self._trials:
            return False
        
        trial = self._trials[key]
        
        # Don't expire if converted
        if trial.get("converted_at"):
            return False
        
        # Remove addon access
        # Note: In production, this would be handled differently
        # For now, we leave the trial data for analytics
        
        # Track in HALO
        await self._halo.observe_conversion(
            user_id=user_id,
            conversion_type="addon_trial_expired",
            details={"addon": addon},
        )
        
        logger.info(f"Expired {addon} trial for user {user_id}")
        return True
    
    def get_trials_expiring_soon(self, days: int = 3) -> List[Dict[str, Any]]:
        """Get trials expiring within N days."""
        now = datetime.utcnow()
        cutoff = now + timedelta(days=days)
        
        expiring = []
        for key, trial in self._trials.items():
            if trial.get("converted_at"):
                continue
            
            expires_at = trial["expires_at"]
            if now < expires_at <= cutoff:
                expiring.append({
                    **trial,
                    "days_remaining": (expires_at - now).days,
                })
        
        return expiring
    
    def get_stats(self) -> Dict[str, Any]:
        """Get trial statistics."""
        total = len(self._trials)
        active = 0
        converted = 0
        expired = 0
        
        now = datetime.utcnow()
        
        for trial in self._trials.values():
            if trial.get("converted_at"):
                converted += 1
            elif trial["expires_at"] <= now:
                expired += 1
            else:
                active += 1
        
        conversion_rate = (converted / total * 100) if total > 0 else 0
        
        return {
            "total_trials": total,
            "active": active,
            "converted": converted,
            "expired": expired,
            "conversion_rate": round(conversion_rate, 2),
        }


# Singleton manager
_trial_manager: Optional[AddonTrialManager] = None

def get_trial_manager() -> AddonTrialManager:
    """Get or create trial manager."""
    global _trial_manager
    if _trial_manager is None:
        _trial_manager = AddonTrialManager()
    return _trial_manager


# ═══════════════════════════════════════════════════════════════════════════
# API MODELS
# ═══════════════════════════════════════════════════════════════════════════

class TrialStatusResponse(BaseModel):
    """Trial status response."""
    addon: str
    status: str
    started_at: Optional[str] = None
    expires_at: Optional[str] = None
    days_remaining: Optional[int] = None
    features: List[str] = []
    price: Dict[str, float] = {}


class StartTrialRequest(BaseModel):
    """Start trial request."""
    addon: str = "voice_style"


class ConvertTrialRequest(BaseModel):
    """Convert trial request."""
    addon: str = "voice_style"
    plan: str = "monthly"


# ═══════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/trial/status")
async def get_addon_trial_status(
    addon: str = "voice_style",
    user: CurrentUser = Depends(get_current_user),
    manager: AddonTrialManager = Depends(get_trial_manager),
):
    """Get trial status for an addon."""
    trial_info = manager.get_trial_status(user.id, addon)
    config = ADDON_TRIAL_CONFIG.get(addon, {})
    
    return TrialStatusResponse(
        addon=addon,
        status=trial_info.status.value,
        started_at=trial_info.started_at.isoformat() if trial_info.started_at else None,
        expires_at=trial_info.expires_at.isoformat() if trial_info.expires_at else None,
        days_remaining=trial_info.days_remaining,
        features=config.get("features", []),
        price={
            "monthly": config.get("price_monthly", 4.99),
            "annual": config.get("price_annual", 49.99),
        },
    )


@router.post("/trial/start")
async def start_addon_trial(
    request: StartTrialRequest,
    background_tasks: BackgroundTasks,
    user: CurrentUser = Depends(get_current_user),
    manager: AddonTrialManager = Depends(get_trial_manager),
):
    """Start a trial for an addon."""
    try:
        trial_info = await manager.start_trial(user.id, request.addon)
        
        return {
            "status": "success",
            "message": "Trial started successfully",
            "trial": trial_info.to_dict(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid request")


@router.post("/trial/convert")
async def convert_addon_trial(
    request: ConvertTrialRequest,
    background_tasks: BackgroundTasks,
    user: CurrentUser = Depends(get_current_user),
    manager: AddonTrialManager = Depends(get_trial_manager),
):
    """Convert trial to paid subscription."""
    try:
        trial_info = await manager.convert_trial(user.id, request.addon, request.plan)
        
        return {
            "status": "success",
            "message": "Trial converted successfully",
            "trial": trial_info.to_dict(),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid request")


@router.get("/trial/stats")
async def get_trial_stats(
    manager: AddonTrialManager = Depends(get_trial_manager),
):
    """Get trial statistics (admin endpoint)."""
    return manager.get_stats()


@router.get("/trial/expiring")
async def get_expiring_trials(
    days: int = 3,
    manager: AddonTrialManager = Depends(get_trial_manager),
):
    """Get trials expiring soon (admin endpoint)."""
    return {
        "days": days,
        "trials": manager.get_trials_expiring_soon(days),
    }


# ═══════════════════════════════════════════════════════════════════════════
# MODULE INIT
# ═══════════════════════════════════════════════════════════════════════════

def init_addon_trials(app):
    """Initialize addon trials routes."""
    app.include_router(router)
    logger.info("Addon trials API initialized")


if __name__ == "__main__":
    print("Addon Trial System loaded")
    print(f"Configured addons: {list(ADDON_TRIAL_CONFIG.keys())}")
