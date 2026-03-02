#!/usr/bin/env python3
"""
LNCP META: EVENTS PACKAGE v5.1
Full-stack event instrumentation for user experience observation.
"""

from .schema import (
    UserTier,
    EventCategory,
    EventType,
    AppEvent,
    OnboardingStepPayload,
    AnalysisPayload,
    ProfileViewPayload,
    ProfileSwitchPayload,
    SessionPayload,
    AccountPayload,
    validate_event,
)

from .bus import (
    EventBus,
    get_event_bus,
)

from .collector import (
    EventCollector,
    EventAggregator,
    get_event_collector,
)

from .app_observer import (
    AppSignals,
    AppObserver,
    get_app_observer,
)

__all__ = [
    # Schema
    "UserTier",
    "EventCategory", 
    "EventType",
    "AppEvent",
    "OnboardingStepPayload",
    "AnalysisPayload",
    "ProfileViewPayload",
    "ProfileSwitchPayload",
    "SessionPayload",
    "AccountPayload",
    "validate_event",
    
    # Bus (App-side)
    "EventBus",
    "get_event_bus",
    
    # Collector (Meta-side)
    "EventCollector",
    "EventAggregator",
    "get_event_collector",
    
    # Observer
    "AppSignals",
    "AppObserver",
    "get_app_observer",
]
