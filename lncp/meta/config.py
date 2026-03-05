#!/usr/bin/env python3
"""
LNCP META: CONFIGURATION v5.0
Centralized configuration with validation and sensible defaults.

Usage:
    from lncp.meta.config import get_config, Config
    
    config = get_config()
    print(config.stripe_api_key)
    print(config.is_production)

Environment Loading:
    1. Loads from .env.lncp if exists
    2. Falls back to environment variables
    3. Uses defaults for development
"""

import os
from dataclasses import dataclass, field
from typing import Optional, List
from pathlib import Path
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
# ENVIRONMENT
# ═══════════════════════════════════════════════════════════════════════════

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Config:
    """
    LNCP Meta configuration.
    
    All settings with validation and defaults.
    """
    
    # ─────────────────────────────────────────────────────────────────────
    # ENVIRONMENT
    # ─────────────────────────────────────────────────────────────────────
    
    env: Environment = Environment.DEVELOPMENT
    simulation_mode: bool = True  # Safe default
    
    # ─────────────────────────────────────────────────────────────────────
    # PERSISTENCE
    # ─────────────────────────────────────────────────────────────────────
    
    data_dir: str = "./data"
    backup_dir: Optional[str] = None  # Defaults to data_dir/backups
    
    # ─────────────────────────────────────────────────────────────────────
    # STRIPE
    # ─────────────────────────────────────────────────────────────────────
    
    stripe_api_key: str = ""
    stripe_webhook_secret: str = ""
    
    # ─────────────────────────────────────────────────────────────────────
    # GOOGLE SEARCH CONSOLE
    # ─────────────────────────────────────────────────────────────────────
    
    gsc_credentials_path: str = ""
    gsc_site_url: str = ""
    
    # ─────────────────────────────────────────────────────────────────────
    # ALERTING
    # ─────────────────────────────────────────────────────────────────────
    
    slack_webhook_url: str = ""
    alert_email: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    
    # ─────────────────────────────────────────────────────────────────────
    # ADMIN
    # ─────────────────────────────────────────────────────────────────────
    
    admin_api_key: str = ""
    
    # ─────────────────────────────────────────────────────────────────────
    # FEATURE FLAGS
    # ─────────────────────────────────────────────────────────────────────
    
    enable_ml: bool = True
    enable_auto_apply: bool = False  # Safe default
    enable_webhooks: bool = True
    max_auto_per_cycle: int = 10
    
    # ─────────────────────────────────────────────────────────────────────
    # DERIVED PROPERTIES
    # ─────────────────────────────────────────────────────────────────────
    
    @property
    def is_production(self) -> bool:
        return self.env == Environment.PRODUCTION
    
    @property
    def is_development(self) -> bool:
        return self.env == Environment.DEVELOPMENT
    
    @property
    def stripe_configured(self) -> bool:
        return bool(self.stripe_api_key) and not self.simulation_mode
    
    @property
    def gsc_configured(self) -> bool:
        return bool(self.gsc_credentials_path) and os.path.exists(self.gsc_credentials_path)
    
    @property
    def slack_configured(self) -> bool:
        return bool(self.slack_webhook_url)
    
    @property
    def email_configured(self) -> bool:
        return bool(self.alert_email) and bool(self.smtp_host)
    
    @property
    def effective_backup_dir(self) -> str:
        return self.backup_dir or os.path.join(self.data_dir, "backups")
    
    # ─────────────────────────────────────────────────────────────────────
    # VALIDATION
    # ─────────────────────────────────────────────────────────────────────
    
    def validate(self) -> List[str]:
        """
        Validate configuration.
        
        Returns list of validation errors (empty if valid).
        """
        errors = []
        
        # Production requires real credentials
        if self.is_production and not self.simulation_mode:
            if not self.stripe_api_key:
                errors.append("STRIPE_API_KEY required for production")
            if not self.stripe_api_key.startswith("sk_live_"):
                errors.append("STRIPE_API_KEY should be live key for production")
            if not self.gsc_credentials_path:
                errors.append("GSC_CREDENTIALS_PATH required for production")
            if not self.gsc_site_url:
                errors.append("GSC_SITE_URL required for production")
        
        # Data directory must be writable
        if not os.access(os.path.dirname(self.data_dir) or ".", os.W_OK):
            errors.append(f"Data directory not writable: {self.data_dir}")
        
        # Validate limits
        if self.max_auto_per_cycle < 0 or self.max_auto_per_cycle > 100:
            errors.append("MAX_AUTO_PER_CYCLE must be between 0 and 100")
        
        return errors
    
    def validate_or_raise(self):
        """Validate and raise if invalid."""
        errors = self.validate()
        if errors:
            raise ConfigurationError("\n".join(errors))
    
    # ─────────────────────────────────────────────────────────────────────
    # DISPLAY
    # ─────────────────────────────────────────────────────────────────────
    
    def to_dict(self, mask_secrets: bool = True) -> dict:
        """Convert to dict, optionally masking secrets."""
        def mask(value: str) -> str:
            if not value or not mask_secrets:
                return value
            if len(value) <= 8:
                return "****"
            return value[:4] + "****" + value[-4:]
        
        return {
            "env": self.env.value,
            "simulation_mode": self.simulation_mode,
            "data_dir": self.data_dir,
            "stripe_api_key": mask(self.stripe_api_key),
            "stripe_configured": self.stripe_configured,
            "gsc_credentials_path": self.gsc_credentials_path,
            "gsc_configured": self.gsc_configured,
            "slack_configured": self.slack_configured,
            "email_configured": self.email_configured,
            "enable_ml": self.enable_ml,
            "enable_auto_apply": self.enable_auto_apply,
            "max_auto_per_cycle": self.max_auto_per_cycle,
        }
    
    def print_status(self):
        """Print configuration status."""
        print("=" * 60)
        print("LNCP META CONFIGURATION STATUS")
        print("=" * 60)
        print(f"Environment:      {self.env.value}")
        print(f"Simulation Mode:  {self.simulation_mode}")
        print(f"Data Directory:   {self.data_dir}")
        print("-" * 60)
        print("INTEGRATIONS:")
        print(f"  Stripe:         {'✓ Configured' if self.stripe_configured else '✗ Not configured'}")
        print(f"  GSC:            {'✓ Configured' if self.gsc_configured else '✗ Not configured'}")
        print(f"  Slack:          {'✓ Configured' if self.slack_configured else '✗ Not configured'}")
        print(f"  Email:          {'✓ Configured' if self.email_configured else '✗ Not configured'}")
        print("-" * 60)
        print("FEATURES:")
        print(f"  ML Models:      {'Enabled' if self.enable_ml else 'Disabled'}")
        print(f"  Auto-Apply:     {'Enabled' if self.enable_auto_apply else 'Disabled'}")
        print(f"  Max Per Cycle:  {self.max_auto_per_cycle}")
        print("=" * 60)


class ConfigurationError(Exception):
    """Configuration validation error."""
    pass


# ═══════════════════════════════════════════════════════════════════════════
# LOADING
# ═══════════════════════════════════════════════════════════════════════════

def _load_env_file(path: str) -> dict:
    """Load environment variables from a file."""
    env_vars = {}
    if not os.path.exists(path):
        return env_vars
    
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip().strip('"\'')
    
    return env_vars


def _get_env(key: str, default: str = "", env_overrides: dict = None) -> str:
    """Get environment variable with optional override dict."""
    if env_overrides and key in env_overrides:
        return env_overrides[key]
    return os.environ.get(key, default)


def _get_bool(key: str, default: bool = False, env_overrides: dict = None) -> bool:
    """Get boolean environment variable."""
    value = _get_env(key, "", env_overrides)
    if not value:
        return default
    return value.lower() in ("true", "1", "yes", "on")


def _get_int(key: str, default: int = 0, env_overrides: dict = None) -> int:
    """Get integer environment variable."""
    value = _get_env(key, "", env_overrides)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def load_config(env_file: str = None) -> Config:
    """
    Load configuration from environment.
    
    Args:
        env_file: Optional path to .env file
    
    Returns:
        Config object
    """
    # Try to load .env file
    env_overrides = {}
    
    # Check common locations
    env_paths = [
        env_file,
        ".env.lncp",
        "lncp/.env.lncp",
        os.path.expanduser("~/.lncp/.env"),
        "/etc/lncp/.env",
    ]
    
    for path in env_paths:
        if path and os.path.exists(path):
            env_overrides = _load_env_file(path)
            break
    
    # Determine environment
    env_str = _get_env("LNCP_ENV", "development", env_overrides)
    try:
        env = Environment(env_str)
    except ValueError:
        env = Environment.DEVELOPMENT
    
    # Determine data directory
    if env == Environment.PRODUCTION:
        default_data_dir = "/var/lib/lncp"
    else:
        default_data_dir = "./data"
    
    # Build config
    config = Config(
        env=env,
        simulation_mode=_get_bool("LNCP_SIMULATION_MODE", env != Environment.PRODUCTION, env_overrides),
        
        # Persistence
        data_dir=_get_env("LNCP_DATA_DIR", default_data_dir, env_overrides),
        backup_dir=_get_env("LNCP_BACKUP_DIR", "", env_overrides) or None,
        
        # Stripe
        stripe_api_key=_get_env("STRIPE_API_KEY", "", env_overrides),
        stripe_webhook_secret=_get_env("STRIPE_WEBHOOK_SECRET", "", env_overrides),
        
        # GSC
        gsc_credentials_path=_get_env("GSC_CREDENTIALS_PATH", "", env_overrides),
        gsc_site_url=_get_env("GSC_SITE_URL", "", env_overrides),
        
        # Alerting
        slack_webhook_url=_get_env("LNCP_SLACK_WEBHOOK", "", env_overrides),
        alert_email=_get_env("LNCP_ALERT_EMAIL", "", env_overrides),
        smtp_host=_get_env("SMTP_HOST", "", env_overrides),
        smtp_port=_get_int("SMTP_PORT", 587, env_overrides),
        
        # Admin
        admin_api_key=_get_env("LNCP_ADMIN_API_KEY", "", env_overrides),
        
        # Features
        enable_ml=_get_bool("LNCP_ENABLE_ML", True, env_overrides),
        enable_auto_apply=_get_bool("LNCP_ENABLE_AUTO_APPLY", False, env_overrides),
        enable_webhooks=_get_bool("LNCP_ENABLE_WEBHOOKS", True, env_overrides),
        max_auto_per_cycle=_get_int("LNCP_MAX_AUTO_PER_CYCLE", 10, env_overrides),
    )
    
    return config


# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL INSTANCE
# ═══════════════════════════════════════════════════════════════════════════

_config: Optional[Config] = None

def get_config() -> Config:
    """Get the global configuration."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config(env_file: str = None) -> Config:
    """Reload configuration."""
    global _config
    _config = load_config(env_file)
    return _config


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """CLI entry point for config validation."""
    import sys
    
    config = get_config()
    config.print_status()
    
    errors = config.validate()
    if errors:
        print("\n⚠️  VALIDATION ERRORS:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("\n✓ Configuration valid")
        sys.exit(0)


if __name__ == "__main__":
    main()


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "Environment",
    "Config",
    "ConfigurationError",
    "load_config",
    "get_config",
    "reload_config",
]
