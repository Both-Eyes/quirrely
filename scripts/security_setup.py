#!/usr/bin/env python3
"""
LNCP Security Setup Script

Run this once to configure security for your installation.
It will generate all required secrets and provide configuration instructions.
"""

import os
import sys
import json
import getpass
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lncp.security.gateway import (
    setup_totp,
    setup_password,
    generate_master_key,
    SecurityGateway,
    CryptoUtils
)


def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_step(num, text):
    print(f"\n[{num}] {text}")
    print("-" * 40)


def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║              LNCP SECURITY SETUP v1.0.0                        ║
║                                                                ║
║  This script will configure fortress-level security for       ║
║  your LNCP installation.                                       ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    config = {}
    
    # Step 1: Generate Master Key
    print_step(1, "Generate Master Encryption Key")
    print("This key protects all encrypted data in the system.")
    
    result = generate_master_key()
    config['LNCP_MASTER_KEY'] = result['key']
    
    print(f"✓ Master key generated")
    print(f"  Key: {result['key'][:20]}...")
    
    # Step 2: Set Admin Password
    print_step(2, "Set Admin Password")
    print("Choose a strong password (min 16 characters recommended).")
    
    while True:
        password = getpass.getpass("Enter admin password: ")
        if len(password) < 8:
            print("Password too short. Minimum 8 characters.")
            continue
        
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Passwords don't match. Try again.")
            continue
        
        break
    
    result = setup_password(password)
    config['LNCP_ADMIN_PASSWORD_HASH'] = result['hash']
    
    print(f"✓ Password hash generated")
    
    # Step 3: Setup TOTP
    print_step(3, "Setup TOTP (Two-Factor Authentication)")
    
    try:
        import pyotp
        result = setup_totp()
        config['LNCP_TOTP_SECRET'] = result['secret']
        
        print(f"✓ TOTP secret generated")
        print(f"\n  Secret: {result['secret']}")
        print(f"\n  Scan this in your authenticator app or enter the secret manually.")
        print(f"\n  QR Code URI (for manual entry):")
        print(f"  {result['uri']}")
        
        # Verify TOTP works
        print("\n  Let's verify your authenticator is set up correctly.")
        code = input("  Enter the current 6-digit code from your app: ")
        
        totp = pyotp.TOTP(result['secret'])
        if totp.verify(code):
            print("  ✓ TOTP verified successfully!")
        else:
            print("  ✗ Invalid code. Make sure your authenticator is synced.")
            print("    You can still proceed, but verify TOTP works before production.")
    
    except ImportError:
        print("⚠ pyotp not installed. TOTP will be disabled.")
        print("  Install with: pip install pyotp")
        config['LNCP_TOTP_SECRET'] = ''
    
    # Step 4: Configure IP Whitelist
    print_step(4, "Configure IP Whitelist")
    print("Enter the IP addresses that should have access.")
    print("For Tailscale, these are your Tailscale IPs (e.g., 100.x.x.x)")
    print("Enter one IP per line, empty line when done:")
    
    ips = []
    while True:
        ip = input("  IP: ").strip()
        if not ip:
            break
        ips.append(ip)
    
    if ips:
        config['LNCP_ALLOWED_IPS'] = ','.join(ips)
        print(f"✓ {len(ips)} IP(s) whitelisted")
    else:
        print("⚠ No IPs whitelisted. All IPs will be allowed (not recommended for production).")
        config['LNCP_ALLOWED_IPS'] = ''
    
    # Step 5: Configure Alerts (Optional)
    print_step(5, "Configure Alert System (Optional)")
    
    setup_alerts = input("Set up SMS/Push alerts? (y/n): ").lower() == 'y'
    
    if setup_alerts:
        print("\nTwilio (for SMS):")
        config['TWILIO_SID'] = input("  Twilio Account SID (or empty to skip): ").strip()
        if config['TWILIO_SID']:
            config['TWILIO_TOKEN'] = input("  Twilio Auth Token: ").strip()
            config['TWILIO_PHONE'] = input("  Twilio Phone Number (+1...): ").strip()
            config['ADMIN_PHONE'] = input("  Your Phone Number (+1...): ").strip()
        
        print("\nPushover (for Push notifications):")
        config['PUSHOVER_TOKEN'] = input("  Pushover App Token (or empty to skip): ").strip()
        if config['PUSHOVER_TOKEN']:
            config['PUSHOVER_USER'] = input("  Pushover User Key: ").strip()
        
        print("\nEmail:")
        config['ADMIN_EMAIL'] = input("  Your Email (for alerts): ").strip()
    
    # Step 6: Generate Initial URL
    print_step(6, "Generate Initial Admin URL")
    
    # Initialize security system
    os.makedirs('data', exist_ok=True)
    
    # Set environment temporarily
    for key, value in config.items():
        if value:
            os.environ[key] = value
    
    gateway = SecurityGateway()
    token = gateway.rotate_url()
    
    print(f"✓ Initial URL token generated")
    print(f"\n  Your admin URL is:")
    print(f"  https://yoursite.com/gate/{token}")
    print(f"\n  ⚠ SAVE THIS URL - you'll need it to access the admin panel!")
    
    # Step 7: Generate Environment File
    print_step(7, "Generate Configuration")
    
    env_content = f"""# LNCP Security Configuration
# Generated: {datetime.now().isoformat()}
# 
# Add these to your environment or .env file
# KEEP THIS FILE SECURE - it contains all your secrets!

# Master encryption key
LNCP_MASTER_KEY='{config.get('LNCP_MASTER_KEY', '')}'

# Admin password hash (don't share this)
LNCP_ADMIN_PASSWORD_HASH='{config.get('LNCP_ADMIN_PASSWORD_HASH', '')}'

# TOTP secret (for authenticator app)
LNCP_TOTP_SECRET='{config.get('LNCP_TOTP_SECRET', '')}'

# IP whitelist (comma-separated Tailscale IPs)
LNCP_ALLOWED_IPS='{config.get('LNCP_ALLOWED_IPS', '')}'

# Twilio (SMS alerts)
TWILIO_SID='{config.get('TWILIO_SID', '')}'
TWILIO_TOKEN='{config.get('TWILIO_TOKEN', '')}'
TWILIO_PHONE='{config.get('TWILIO_PHONE', '')}'
ADMIN_PHONE='{config.get('ADMIN_PHONE', '')}'

# Pushover (Push alerts)
PUSHOVER_TOKEN='{config.get('PUSHOVER_TOKEN', '')}'
PUSHOVER_USER='{config.get('PUSHOVER_USER', '')}'

# Email
ADMIN_EMAIL='{config.get('ADMIN_EMAIL', '')}'

# Environment
LNCP_ENV='production'
"""
    
    env_path = '.env.security'
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    # Secure the file
    os.chmod(env_path, 0o600)
    
    print(f"✓ Configuration saved to {env_path}")
    print(f"  File permissions set to owner-only (600)")
    
    # Summary
    print_header("SETUP COMPLETE")
    
    print(f"""
Your LNCP system is now secured with:

  ✓ Encrypted rotating admin URL (24-hour rotation)
  ✓ Strong password authentication
  {'✓' if config.get('LNCP_TOTP_SECRET') else '✗'} TOTP two-factor authentication
  {'✓' if config.get('LNCP_ALLOWED_IPS') else '✗'} IP whitelist ({len(ips)} IPs)
  {'✓' if config.get('TWILIO_SID') else '✗'} SMS alerts
  {'✓' if config.get('PUSHOVER_TOKEN') else '✗'} Push notifications
  ✓ Immutable audit logging

NEXT STEPS:

1. Source the environment file:
   source {env_path}

2. For production, add these to your hosting platform's
   environment variables (Vercel, Railway, etc.)

3. Set up Tailscale if you haven't already:
   https://tailscale.com/download

4. Consider adding a YubiKey for hardware authentication

5. Test your setup:
   python3 lncp/security/gateway.py status

IMPORTANT:

- Your admin URL is: /gate/{token[:20]}...
- This URL changes every 24 hours
- Keep your .env.security file SECURE
- Never commit secrets to git

""")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
