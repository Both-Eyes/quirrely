#!/usr/bin/env python3
"""
QUIRRELY TRIGGER ENGINE v1.0
Event-driven conversion triggers.

Triggers automated actions based on user behavior:
- Trial expiration reminders
- Usage limit warnings  
- Engagement milestones
- Churn prevention

Expected Impact:
- +5% trial conversion (from reminders)
- +3% paid conversion (from limit triggers)
- -2% churn (from engagement triggers)
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# TRIGGER TYPES
# ═══════════════════════════════════════════════════════════════════════════

class TriggerType(str, Enum):
    """Types of triggers."""
    TRIAL_EXPIRING_3_DAYS = "trial.expiring.3_days"
    TRIAL_EXPIRING_1_DAY = "trial.expiring.1_day"
    TRIAL_EXPIRED = "trial.expired"
    USAGE_LIMIT_80_PERCENT = "usage.limit.80_percent"
    USAGE_LIMIT_REACHED = "usage.limit.reached"
    FIFTH_ANALYSIS = "usage.analysis.fifth"
    MILESTONE_REACHED = "engagement.milestone"
    STREAK_ACHIEVED = "engagement.streak"
    HIGH_ENGAGEMENT_SESSION = "engagement.session.high"
    INACTIVE_7_DAYS = "churn.inactive.7_days"
    INACTIVE_14_DAYS = "churn.inactive.14_days"
    CHURN_RISK_DETECTED = "churn.risk.detected"
    FEATURE_BLOCKED_3_TIMES = "upsell.feature.blocked_3"
    ADDON_INTEREST_SIGNAL = "upsell.addon.interest"
    AUTHORITY_ELIGIBLE = "upsell.authority.eligible"


class ActionType(str, Enum):
    """Types of actions."""
    SEND_EMAIL = "email"
    SHOW_IN_APP = "in_app"
    SEND_PUSH = "push"
    LOG_EVENT = "log"
    CALL_WEBHOOK = "webhook"


# ═══════════════════════════════════════════════════════════════════════════
# TRIGGER DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class TriggerAction:
    """Action to perform when trigger fires."""
    type: ActionType
    template: str
    data: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5


@dataclass
class TriggerDefinition:
    """Definition of a trigger."""
    id: TriggerType
    name: str
    description: str
    actions: List[TriggerAction]
    cooldown_hours: int = 24
    enabled: bool = True


TRIGGER_DEFINITIONS: Dict[TriggerType, TriggerDefinition] = {
    TriggerType.TRIAL_EXPIRING_3_DAYS: TriggerDefinition(
        id=TriggerType.TRIAL_EXPIRING_3_DAYS,
        name="Trial Expiring - 3 Days",
        description="User's trial expires in 3 days",
        actions=[
            TriggerAction(ActionType.SEND_EMAIL, "trial_expiring_3_days", {"subject": "Your Quirrely trial ends in 3 days"}, 8),
            TriggerAction(ActionType.SHOW_IN_APP, "trial_expiring_banner", {"dismissible": True}, 7),
        ],
        cooldown_hours=72,
    ),
    TriggerType.TRIAL_EXPIRING_1_DAY: TriggerDefinition(
        id=TriggerType.TRIAL_EXPIRING_1_DAY,
        name="Trial Expiring - 1 Day",
        description="User's trial expires tomorrow",
        actions=[
            TriggerAction(ActionType.SEND_EMAIL, "trial_expiring_1_day", {"subject": "Last day of your Quirrely trial!"}, 9),
            TriggerAction(ActionType.SHOW_IN_APP, "trial_expiring_modal", {"dismissible": False}, 9),
        ],
        cooldown_hours=24,
    ),
    TriggerType.USAGE_LIMIT_80_PERCENT: TriggerDefinition(
        id=TriggerType.USAGE_LIMIT_80_PERCENT,
        name="Usage at 80%",
        description="User has used 80% of daily analyses",
        actions=[
            TriggerAction(ActionType.SHOW_IN_APP, "usage_warning", {"level": "warning"}, 6),
        ],
        cooldown_hours=24,
    ),
    TriggerType.USAGE_LIMIT_REACHED: TriggerDefinition(
        id=TriggerType.USAGE_LIMIT_REACHED,
        name="Usage Limit Reached",
        description="User has reached daily analysis limit",
        actions=[
            TriggerAction(ActionType.SHOW_IN_APP, "usage_limit_modal", {"show_upgrade": True}, 8),
            TriggerAction(ActionType.LOG_EVENT, "limit_reached", {}, 5),
        ],
        cooldown_hours=24,
    ),
    TriggerType.FIFTH_ANALYSIS: TriggerDefinition(
        id=TriggerType.FIFTH_ANALYSIS,
        name="Fifth Analysis",
        description="User completed their 5th analysis",
        actions=[
            TriggerAction(ActionType.SHOW_IN_APP, "power_user_prompt", {"message": "You're getting great insights!"}, 6),
        ],
        cooldown_hours=0,
    ),
    TriggerType.MILESTONE_REACHED: TriggerDefinition(
        id=TriggerType.MILESTONE_REACHED,
        name="Milestone Reached",
        description="User reached a milestone",
        actions=[
            TriggerAction(ActionType.SHOW_IN_APP, "milestone_celebration", {"confetti": True}, 7),
        ],
        cooldown_hours=1,
    ),
    TriggerType.INACTIVE_7_DAYS: TriggerDefinition(
        id=TriggerType.INACTIVE_7_DAYS,
        name="Inactive 7 Days",
        description="User hasn't logged in for 7 days",
        actions=[
            TriggerAction(ActionType.SEND_EMAIL, "we_miss_you", {"subject": "We miss you at Quirrely!"}, 6),
        ],
        cooldown_hours=168,
    ),
    TriggerType.ADDON_INTEREST_SIGNAL: TriggerDefinition(
        id=TriggerType.ADDON_INTEREST_SIGNAL,
        name="Addon Interest Signal",
        description="User showing interest in addon features",
        actions=[
            TriggerAction(ActionType.SHOW_IN_APP, "addon_trial_offer", {"addon": "voice_style"}, 7),
        ],
        cooldown_hours=72,
    ),
}


# ═══════════════════════════════════════════════════════════════════════════
# TRIGGER ENGINE
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class TriggerEvent:
    """Event that may fire triggers."""
    user_id: str
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FiredTrigger:
    """Record of a fired trigger."""
    trigger_id: TriggerType
    user_id: str
    actions_executed: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)


class TriggerEngine:
    """Processes events and fires appropriate triggers."""
    
    def __init__(self):
        self._definitions = TRIGGER_DEFINITIONS
        self._fired: List[FiredTrigger] = []
        self._cooldowns: Dict[str, datetime] = {}
    
    def _get_cooldown_key(self, user_id: str, trigger_id: TriggerType) -> str:
        return f"{user_id}:{trigger_id.value}"
    
    def _is_on_cooldown(self, user_id: str, trigger: TriggerDefinition) -> bool:
        if trigger.cooldown_hours == 0:
            return False
        key = self._get_cooldown_key(user_id, trigger.id)
        last_fired = self._cooldowns.get(key)
        if not last_fired:
            return False
        return datetime.utcnow() < last_fired + timedelta(hours=trigger.cooldown_hours)
    
    def _set_cooldown(self, user_id: str, trigger: TriggerDefinition):
        key = self._get_cooldown_key(user_id, trigger.id)
        self._cooldowns[key] = datetime.utcnow()
    
    def _evaluate_condition(self, trigger: TriggerDefinition, event: TriggerEvent) -> bool:
        patterns = {
            TriggerType.TRIAL_EXPIRING_3_DAYS: lambda e: e.event_type == "trial.check" and e.data.get("days_remaining") == 3,
            TriggerType.TRIAL_EXPIRING_1_DAY: lambda e: e.event_type == "trial.check" and e.data.get("days_remaining") == 1,
            TriggerType.USAGE_LIMIT_80_PERCENT: lambda e: e.event_type == "usage.check" and 80 <= e.data.get("percent", 0) < 100,
            TriggerType.USAGE_LIMIT_REACHED: lambda e: e.event_type == "usage.limit_reached",
            TriggerType.FIFTH_ANALYSIS: lambda e: e.event_type == "analysis.completed" and e.data.get("total_analyses") == 5,
            TriggerType.MILESTONE_REACHED: lambda e: e.event_type == "milestone.achieved",
            TriggerType.INACTIVE_7_DAYS: lambda e: e.event_type == "user.inactive_check" and e.data.get("days") == 7,
            TriggerType.ADDON_INTEREST_SIGNAL: lambda e: e.event_type == "addon.interest_signal",
        }
        evaluator = patterns.get(trigger.id)
        return evaluator(event) if evaluator else False
    
    async def process_event(self, event: TriggerEvent) -> List[FiredTrigger]:
        """Process an event and fire matching triggers."""
        fired = []
        for trigger_id, trigger in self._definitions.items():
            if not trigger.enabled:
                continue
            if self._is_on_cooldown(event.user_id, trigger):
                continue
            if self._evaluate_condition(trigger, event):
                result = await self._fire_trigger(trigger, event.user_id, event.data)
                if result:
                    fired.append(result)
        return fired
    
    async def _fire_trigger(self, trigger: TriggerDefinition, user_id: str, context: Dict) -> Optional[FiredTrigger]:
        actions_executed = []
        for action in sorted(trigger.actions, key=lambda a: -a.priority):
            logger.info(f"Executing {action.type.value}: {action.template} for {user_id}")
            actions_executed.append(action.template)
        
        if actions_executed:
            self._set_cooldown(user_id, trigger)
            fired = FiredTrigger(trigger.id, user_id, actions_executed)
            self._fired.append(fired)
            logger.info(f"Trigger fired: {trigger.id} for {user_id}")
            return fired
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        by_trigger = {}
        for f in self._fired:
            by_trigger[f.trigger_id.value] = by_trigger.get(f.trigger_id.value, 0) + 1
        return {"total_fired": len(self._fired), "by_trigger": by_trigger, "active_cooldowns": len(self._cooldowns)}


_engine: Optional[TriggerEngine] = None

def get_trigger_engine() -> TriggerEngine:
    global _engine
    if _engine is None:
        _engine = TriggerEngine()
    return _engine


async def fire_trigger_event(user_id: str, event_type: str, data: Dict[str, Any] = None) -> List[FiredTrigger]:
    """Helper to fire trigger events from other modules."""
    engine = get_trigger_engine()
    event = TriggerEvent(user_id=user_id, event_type=event_type, data=data or {})
    return await engine.process_event(event)


if __name__ == "__main__":
    print("Trigger Engine loaded")
    print(f"Registered triggers: {len(TRIGGER_DEFINITIONS)}")
