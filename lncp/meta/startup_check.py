#!/usr/bin/env python3
"""
LNCP META: STARTUP CHECK
Run this before starting Meta to validate configuration and dependencies.

Usage:
    python -m lncp.meta.startup_check
    
    # Or directly:
    python lncp/meta/startup_check.py

Exit codes:
    0 - All checks passed
    1 - Configuration errors
    2 - Dependency errors
    3 - Connection errors
"""

import sys
import os

# Ensure package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def print_header(text: str):
    print(f"\n{'─' * 60}")
    print(f"  {text}")
    print(f"{'─' * 60}")


def print_check(name: str, passed: bool, message: str = ""):
    status = "✓" if passed else "✗"
    color_start = "\033[92m" if passed else "\033[91m"
    color_end = "\033[0m"
    msg = f" - {message}" if message else ""
    print(f"  {color_start}{status}{color_end} {name}{msg}")


def check_configuration() -> bool:
    """Check configuration validity."""
    print_header("CONFIGURATION")
    
    try:
        from lncp.meta.config import get_config
        config = get_config()
        
        print_check("Config loaded", True)
        print_check(f"Environment: {config.env.value}", True)
        print_check(f"Simulation mode: {config.simulation_mode}", True)
        
        # Validate
        errors = config.validate()
        if errors:
            print_check("Validation", False, f"{len(errors)} errors")
            for error in errors:
                print(f"      └─ {error}")
            return False
        
        print_check("Validation passed", True)
        return True
        
    except Exception as e:
        print_check("Config load failed", False, str(e))
        return False


def check_persistence() -> bool:
    """Check persistence layer."""
    print_header("PERSISTENCE")
    
    try:
        from lncp.meta.config import get_config
        from lncp.meta.persistence import PersistenceManager
        
        config = get_config()
        
        # Check data directory
        data_dir = config.data_dir
        if os.path.exists(data_dir):
            print_check(f"Data directory exists: {data_dir}", True)
        else:
            # Try to create
            try:
                os.makedirs(data_dir, exist_ok=True)
                print_check(f"Data directory created: {data_dir}", True)
            except Exception as e:
                print_check(f"Data directory: {data_dir}", False, str(e))
                return False
        
        # Check write access
        test_file = os.path.join(data_dir, ".write_test")
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            print_check("Write access", True)
        except Exception as e:
            print_check("Write access", False, str(e))
            return False
        
        # Initialize persistence
        try:
            pm = PersistenceManager(data_dir)
            integrity = pm.check_integrity()
            pm.close()
            
            if integrity["status"] == "ok":
                print_check("Database integrity", True)
            else:
                print_check("Database integrity", False, str(integrity["issues"]))
                return False
        except Exception as e:
            print_check("Persistence initialization", False, str(e))
            return False
        
        return True
        
    except ImportError as e:
        print_check("Import persistence module", False, str(e))
        return False


def check_stripe() -> bool:
    """Check Stripe configuration."""
    print_header("STRIPE INTEGRATION")
    
    try:
        from lncp.meta.config import get_config
        from lncp.meta.stripe_integration import StripeAPIClient
        
        config = get_config()
        
        if config.simulation_mode:
            print_check("Simulation mode", True, "Using simulated data")
            return True
        
        if not config.stripe_api_key:
            print_check("API key", False, "STRIPE_API_KEY not set")
            return False
        
        # Check key format
        if config.stripe_api_key.startswith("sk_test_"):
            print_check("API key format", True, "Test key")
        elif config.stripe_api_key.startswith("sk_live_"):
            print_check("API key format", True, "Live key")
        else:
            print_check("API key format", False, "Invalid key format")
            return False
        
        # Try to connect
        client = StripeAPIClient(config.stripe_api_key)
        if client.is_configured:
            print_check("Stripe library", True)
            # Could add a test API call here
        else:
            print_check("Stripe library", False, "stripe package not installed")
            return False
        
        return True
        
    except Exception as e:
        print_check("Stripe check", False, str(e))
        return False


def check_gsc() -> bool:
    """Check Google Search Console configuration."""
    print_header("GOOGLE SEARCH CONSOLE")
    
    try:
        from lncp.meta.config import get_config
        
        config = get_config()
        
        if config.simulation_mode:
            print_check("Simulation mode", True, "Using simulated data")
            return True
        
        if not config.gsc_credentials_path:
            print_check("Credentials path", False, "GSC_CREDENTIALS_PATH not set")
            return False
        
        if not os.path.exists(config.gsc_credentials_path):
            print_check("Credentials file", False, f"File not found: {config.gsc_credentials_path}")
            return False
        
        print_check("Credentials file exists", True)
        
        if not config.gsc_site_url:
            print_check("Site URL", False, "GSC_SITE_URL not set")
            return False
        
        print_check(f"Site URL: {config.gsc_site_url}", True)
        
        return True
        
    except Exception as e:
        print_check("GSC check", False, str(e))
        return False


def check_alerting() -> bool:
    """Check alerting configuration."""
    print_header("ALERTING")
    
    try:
        from lncp.meta.config import get_config
        
        config = get_config()
        
        if config.slack_configured:
            print_check("Slack webhook", True, "Configured")
        else:
            print_check("Slack webhook", False, "Not configured (optional)")
        
        if config.email_configured:
            print_check("Email alerts", True, f"→ {config.alert_email}")
        else:
            print_check("Email alerts", False, "Not configured (optional)")
        
        # Alerting is optional, so always return True
        return True
        
    except Exception as e:
        print_check("Alerting check", False, str(e))
        return True  # Non-critical


def check_ml() -> bool:
    """Check ML models."""
    print_header("ML MODELS")
    
    try:
        from lncp.meta.config import get_config
        from lncp.meta.ml_models import ModelManager
        
        config = get_config()
        
        if not config.enable_ml:
            print_check("ML disabled", True, "Skipping")
            return True
        
        # Initialize model manager
        mm = ModelManager()
        print_check("Model manager", True)
        
        summary = mm.get_summary()
        print_check(f"Success predictor: {'trained' if summary['success_trained'] else 'untrained'}", True)
        print_check(f"Impact predictor: {'trained' if summary['impact_trained'] else 'untrained'}", True)
        
        return True
        
    except Exception as e:
        print_check("ML check", False, str(e))
        return False


def main():
    """Run all startup checks."""
    print("\n" + "=" * 60)
    print("  LNCP META v5.0 STARTUP CHECK")
    print("=" * 60)
    
    all_passed = True
    
    # Configuration (required)
    if not check_configuration():
        all_passed = False
        print("\n❌ Configuration check failed. Fix errors before starting.")
        sys.exit(1)
    
    # Persistence (required)
    if not check_persistence():
        all_passed = False
        print("\n❌ Persistence check failed. Fix errors before starting.")
        sys.exit(2)
    
    # External integrations (warnings only in simulation mode)
    check_stripe()
    check_gsc()
    
    # Optional checks
    check_alerting()
    check_ml()
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("  ✓ ALL REQUIRED CHECKS PASSED")
        print("=" * 60)
        print("\nLNCP Meta is ready to start.")
        sys.exit(0)
    else:
        print("  ✗ SOME CHECKS FAILED")
        print("=" * 60)
        print("\nFix the errors above before starting.")
        sys.exit(1)


if __name__ == "__main__":
    main()
