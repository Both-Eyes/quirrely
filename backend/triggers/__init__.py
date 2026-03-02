"""
QUIRRELY TRIGGER SYSTEM
Event-driven conversion triggers.
"""

from .trigger_engine import (
    TriggerType,
    ActionType,
    TriggerAction,
    TriggerDefinition,
    TriggerEvent,
    FiredTrigger,
    TriggerEngine,
    get_trigger_engine,
    fire_trigger_event,
    TRIGGER_DEFINITIONS,
)

__all__ = [
    'TriggerType',
    'ActionType',
    'TriggerAction',
    'TriggerDefinition',
    'TriggerEvent',
    'FiredTrigger',
    'TriggerEngine',
    'get_trigger_engine',
    'fire_trigger_event',
    'TRIGGER_DEFINITIONS',
]
