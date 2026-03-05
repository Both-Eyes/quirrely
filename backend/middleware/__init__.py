"""
LNCP Backend Middleware
"""

from .country_gate import (
    CountryGate,
    CountryGateConfig,
    CountryGateMiddleware,
    CountryCheckResult,
    get_country_gate,
    require_allowed_country,
    add_allowed_country,
    remove_allowed_country,
    add_blocked_country,
    set_enforcement_enabled,
    get_enforcement_status,
)

__all__ = [
    'CountryGate',
    'CountryGateConfig',
    'CountryGateMiddleware',
    'CountryCheckResult',
    'get_country_gate',
    'require_allowed_country',
    'add_allowed_country',
    'remove_allowed_country',
    'add_blocked_country',
    'set_enforcement_enabled',
    'get_enforcement_status',
]
