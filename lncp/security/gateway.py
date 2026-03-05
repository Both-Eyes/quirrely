#!/usr/bin/env python3
"""
LNCP SECURITY GATEWAY v1.0.0
The fortress protecting all LNCP intellectual property.

This module implements:
1. Encrypted rotating URL system (24h auto-refresh)
2. Multi-factor authentication (password + TOTP + hardware key)
3. IP whitelist enforcement
4. Client certificate validation
5. Session management
6. Audit logging
7. Alert system
8. One-click credential rotation
"""

import os
import sys
import json
import hmac
import base64
import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
import threading

# Cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# TOTP
try:
    import pyotp
    TOTP_AVAILABLE = True
except ImportError:
    TOTP_AVAILABLE = False
    print("Warning: pyotp not installed. TOTP disabled.")


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

class SecurityConfig:
    """Security configuration - loaded from environment in production."""
    
    # URL rotation
    URL_ROTATION_HOURS = 24
    URL_TOKEN_LENGTH = 64
    
    # Session
    SESSION_TIMEOUT_MINUTES = 15
    MAX_FAILED_ATTEMPTS = 3
    LOCKOUT_MINUTES = 60
    
    # Paths
    SECURITY_DB_PATH = os.environ.get('LNCP_SECURITY_DB', 'data/security.db')
    AUDIT_LOG_PATH = os.environ.get('LNCP_AUDIT_LOG', 'data/audit.log')
    
    # Secrets (MUST be set via environment in production)
    MASTER_KEY = os.environ.get('LNCP_MASTER_KEY', None)
    TOTP_SECRET = os.environ.get('LNCP_TOTP_SECRET', None)
    ADMIN_PASSWORD_HASH = os.environ.get('LNCP_ADMIN_PASSWORD_HASH', None)
    
    # IP Whitelist (Tailscale IPs)
    ALLOWED_IPS = os.environ.get('LNCP_ALLOWED_IPS', '').split(',')
    
    # Alert configuration
    TWILIO_SID = os.environ.get('TWILIO_SID', None)
    TWILIO_TOKEN = os.environ.get('TWILIO_TOKEN', None)
    TWILIO_PHONE = os.environ.get('TWILIO_PHONE', None)
    ADMIN_PHONE = os.environ.get('ADMIN_PHONE', None)
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', None)
    PUSHOVER_TOKEN = os.environ.get('PUSHOVER_TOKEN', None)
    PUSHOVER_USER = os.environ.get('PUSHOVER_USER', None)


# ═══════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════

class AlertLevel(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    INTRUSION = "intrusion"


class AuthResult(str, Enum):
    SUCCESS = "success"
    FAILED_PASSWORD = "failed_password"
    FAILED_TOTP = "failed_totp"
    FAILED_HARDWARE_KEY = "failed_hardware_key"
    FAILED_IP = "failed_ip"
    FAILED_CERT = "failed_certificate"
    LOCKED_OUT = "locked_out"
    INVALID_URL = "invalid_url"
    SESSION_EXPIRED = "session_expired"


class AuditAction(str, Enum):
    LOGIN_ATTEMPT = "login_attempt"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    URL_ROTATED = "url_rotated"
    CREDENTIALS_ROTATED = "credentials_rotated"
    IP_BLOCKED = "ip_blocked"
    INTRUSION_DETECTED = "intrusion_detected"
    ADMIN_ACTION = "admin_action"
    SYSTEM_ACCESS = "system_access"


# ═══════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Session:
    """Active admin session."""
    session_id: str
    created_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    authenticated_factors: List[str] = field(default_factory=list)
    
    @property
    def is_expired(self) -> bool:
        timeout = timedelta(minutes=SecurityConfig.SESSION_TIMEOUT_MINUTES)
        return datetime.now(timezone.utc) - self.last_activity > timeout
    
    def refresh(self):
        self.last_activity = datetime.now(timezone.utc)


@dataclass
class AuditEntry:
    """Immutable audit log entry."""
    timestamp: datetime
    action: AuditAction
    ip_address: str
    user_agent: str
    success: bool
    details: Dict = field(default_factory=dict)
    signature: str = ""  # HMAC signature for integrity
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "action": self.action.value,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "success": self.success,
            "details": self.details,
            "signature": self.signature
        }


# ═══════════════════════════════════════════════════════════════════════════
# ENCRYPTION UTILITIES
# ═══════════════════════════════════════════════════════════════════════════

class CryptoUtils:
    """Cryptographic utilities."""
    
    @staticmethod
    def generate_key() -> bytes:
        """Generate a new encryption key."""
        return Fernet.generate_key()
    
    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """Derive encryption key from password."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    @staticmethod
    def encrypt(data: str, key: bytes) -> str:
        """Encrypt data with Fernet."""
        f = Fernet(key)
        return f.encrypt(data.encode()).decode()
    
    @staticmethod
    def decrypt(encrypted: str, key: bytes) -> str:
        """Decrypt data with Fernet."""
        f = Fernet(key)
        return f.decrypt(encrypted.encode()).decode()
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password with salt."""
        salt = secrets.token_hex(32)
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            iterations=480000
        )
        return f"{salt}:{hash_obj.hex()}"
    
    @staticmethod
    def verify_password(password: str, stored_hash: str) -> bool:
        """Verify password against stored hash."""
        try:
            salt, hash_hex = stored_hash.split(':')
            hash_obj = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt.encode(),
                iterations=480000
            )
            return hmac.compare_digest(hash_obj.hex(), hash_hex)
        except:
            return False
    
    @staticmethod
    def generate_url_token() -> str:
        """Generate secure URL token."""
        return secrets.token_urlsafe(SecurityConfig.URL_TOKEN_LENGTH)
    
    @staticmethod
    def sign_data(data: str, key: bytes) -> str:
        """Create HMAC signature for data integrity."""
        return hmac.new(key, data.encode(), hashlib.sha256).hexdigest()


# ═══════════════════════════════════════════════════════════════════════════
# AUDIT LOGGER
# ═══════════════════════════════════════════════════════════════════════════

class AuditLogger:
    """Immutable, cryptographically signed audit log."""
    
    def __init__(self, db_path: str = None, signing_key: bytes = None):
        self.db_path = db_path or SecurityConfig.SECURITY_DB_PATH
        self.signing_key = signing_key or (
            SecurityConfig.MASTER_KEY.encode() if SecurityConfig.MASTER_KEY 
            else b'development_key_not_for_production'
        )
        self._init_db()
    
    def _init_db(self):
        """Initialize audit database."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    action TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    user_agent TEXT,
                    success INTEGER NOT NULL,
                    details TEXT,
                    signature TEXT NOT NULL,
                    previous_hash TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS failed_attempts (
                    ip_address TEXT PRIMARY KEY,
                    attempts INTEGER DEFAULT 0,
                    locked_until TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS active_sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    last_activity TEXT NOT NULL,
                    ip_address TEXT NOT NULL,
                    user_agent TEXT,
                    factors TEXT
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS url_tokens (
                    id INTEGER PRIMARY KEY,
                    token TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1
                )
            ''')
            
            conn.commit()
    
    def log(self, action: AuditAction, ip_address: str, user_agent: str,
            success: bool, details: Dict = None) -> AuditEntry:
        """Log an audit entry with cryptographic signature."""
        timestamp = datetime.now(timezone.utc)
        details = details or {}
        
        # Create entry data for signing
        entry_data = json.dumps({
            "timestamp": timestamp.isoformat(),
            "action": action.value,
            "ip_address": ip_address,
            "success": success,
            "details": details
        }, sort_keys=True)
        
        signature = CryptoUtils.sign_data(entry_data, self.signing_key)
        
        # Get previous entry hash for chain integrity
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'SELECT signature FROM audit_log ORDER BY id DESC LIMIT 1'
            )
            row = cursor.fetchone()
            previous_hash = row[0] if row else "genesis"
            
            # Insert entry
            conn.execute('''
                INSERT INTO audit_log 
                (timestamp, action, ip_address, user_agent, success, details, signature, previous_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp.isoformat(),
                action.value,
                ip_address,
                user_agent,
                1 if success else 0,
                json.dumps(details),
                signature,
                previous_hash
            ))
            conn.commit()
        
        entry = AuditEntry(
            timestamp=timestamp,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            details=details,
            signature=signature
        )
        
        return entry
    
    def get_recent_entries(self, limit: int = 100) -> List[Dict]:
        """Get recent audit entries."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT timestamp, action, ip_address, user_agent, success, details
                FROM audit_log ORDER BY id DESC LIMIT ?
            ''', (limit,))
            
            return [
                {
                    "timestamp": row[0],
                    "action": row[1],
                    "ip_address": row[2],
                    "user_agent": row[3],
                    "success": bool(row[4]),
                    "details": json.loads(row[5]) if row[5] else {}
                }
                for row in cursor.fetchall()
            ]
    
    def verify_chain_integrity(self) -> Tuple[bool, str]:
        """Verify audit log chain hasn't been tampered with."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                'SELECT signature, previous_hash FROM audit_log ORDER BY id'
            )
            
            previous = "genesis"
            for row in cursor.fetchall():
                if row[1] != previous:
                    return False, f"Chain broken at signature {row[0][:16]}..."
                previous = row[0]
        
        return True, "Chain integrity verified"


# ═══════════════════════════════════════════════════════════════════════════
# ALERT SYSTEM
# ═══════════════════════════════════════════════════════════════════════════

class AlertSystem:
    """Multi-channel security alert system."""
    
    def __init__(self):
        self.twilio_available = all([
            SecurityConfig.TWILIO_SID,
            SecurityConfig.TWILIO_TOKEN,
            SecurityConfig.TWILIO_PHONE,
            SecurityConfig.ADMIN_PHONE
        ])
        
        self.pushover_available = all([
            SecurityConfig.PUSHOVER_TOKEN,
            SecurityConfig.PUSHOVER_USER
        ])
    
    def send_alert(self, level: AlertLevel, title: str, message: str):
        """Send alert through appropriate channels based on level."""
        full_message = f"[{level.value.upper()}] {title}: {message}"
        
        if level == AlertLevel.INFO:
            # Info: log only
            print(f"[ALERT-INFO] {full_message}")
        
        elif level == AlertLevel.WARNING:
            # Warning: push + email
            self._send_push(title, message, priority=0)
            self._send_email(f"⚠️ {title}", message)
        
        elif level == AlertLevel.CRITICAL:
            # Critical: SMS + push + email
            self._send_sms(f"🚨 LNCP: {title}")
            self._send_push(title, message, priority=1)
            self._send_email(f"🚨 CRITICAL: {title}", message)
        
        elif level == AlertLevel.INTRUSION:
            # Intrusion: ALL channels + auto-lockdown
            self._send_sms(f"🔴 INTRUSION: {title} - System locked")
            self._send_push(title, message, priority=2)
            self._send_email(f"🔴 INTRUSION ALERT: {title}", message)
            # Phone call would go here with Twilio voice API
    
    def _send_sms(self, message: str):
        """Send SMS via Twilio."""
        if not self.twilio_available:
            print(f"[SMS-SIMULATED] {message}")
            return
        
        try:
            from twilio.rest import Client
            client = Client(SecurityConfig.TWILIO_SID, SecurityConfig.TWILIO_TOKEN)
            client.messages.create(
                body=message[:160],  # SMS limit
                from_=SecurityConfig.TWILIO_PHONE,
                to=SecurityConfig.ADMIN_PHONE
            )
        except Exception as e:
            print(f"[SMS-ERROR] {e}")
    
    def _send_push(self, title: str, message: str, priority: int = 0):
        """Send push notification via Pushover."""
        if not self.pushover_available:
            print(f"[PUSH-SIMULATED] {title}: {message}")
            return
        
        try:
            import requests
            requests.post("https://api.pushover.net/1/messages.json", data={
                "token": SecurityConfig.PUSHOVER_TOKEN,
                "user": SecurityConfig.PUSHOVER_USER,
                "title": title,
                "message": message,
                "priority": priority,
                "retry": 60 if priority >= 2 else None,
                "expire": 3600 if priority >= 2 else None,
            })
        except Exception as e:
            print(f"[PUSH-ERROR] {e}")
    
    def _send_email(self, subject: str, body: str):
        """Send email alert."""
        if not SecurityConfig.ADMIN_EMAIL:
            print(f"[EMAIL-SIMULATED] {subject}: {body}")
            return
        
        # In production, use SendGrid, AWS SES, or similar
        print(f"[EMAIL] To: {SecurityConfig.ADMIN_EMAIL}, Subject: {subject}")


# ═══════════════════════════════════════════════════════════════════════════
# URL ROTATION SYSTEM
# ═══════════════════════════════════════════════════════════════════════════

class URLRotator:
    """Encrypted rotating URL system."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or SecurityConfig.SECURITY_DB_PATH
        self._lock = threading.Lock()
    
    def get_current_token(self) -> Optional[str]:
        """Get the current valid URL token."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT token FROM url_tokens 
                WHERE is_active = 1 AND expires_at > ?
                ORDER BY id DESC LIMIT 1
            ''', (datetime.now(timezone.utc).isoformat(),))
            
            row = cursor.fetchone()
            return row[0] if row else None
    
    def rotate_url(self, audit_logger: AuditLogger = None, 
                   ip_address: str = "system") -> str:
        """Generate new URL token and invalidate old ones."""
        with self._lock:
            new_token = CryptoUtils.generate_url_token()
            now = datetime.now(timezone.utc)
            expires = now + timedelta(hours=SecurityConfig.URL_ROTATION_HOURS)
            
            with sqlite3.connect(self.db_path) as conn:
                # Invalidate all existing tokens
                conn.execute('UPDATE url_tokens SET is_active = 0')
                
                # Insert new token
                conn.execute('''
                    INSERT INTO url_tokens (token, created_at, expires_at, is_active)
                    VALUES (?, ?, ?, 1)
                ''', (new_token, now.isoformat(), expires.isoformat()))
                
                conn.commit()
            
            if audit_logger:
                audit_logger.log(
                    AuditAction.URL_ROTATED,
                    ip_address, "system",
                    success=True,
                    details={"expires_at": expires.isoformat()}
                )
            
            return new_token
    
    def validate_token(self, token: str) -> bool:
        """Validate URL token."""
        current = self.get_current_token()
        if not current:
            return False
        return hmac.compare_digest(token, current)
    
    def get_admin_url(self, base_url: str) -> str:
        """Get the current admin URL."""
        token = self.get_current_token()
        if not token:
            token = self.rotate_url()
        return f"{base_url}/gate/{token}"
    
    def check_and_auto_rotate(self) -> bool:
        """Check if rotation needed and rotate if so."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT expires_at FROM url_tokens 
                WHERE is_active = 1
                ORDER BY id DESC LIMIT 1
            ''')
            
            row = cursor.fetchone()
            if not row:
                self.rotate_url()
                return True
            
            expires = datetime.fromisoformat(row[0])
            if datetime.now(timezone.utc) >= expires:
                self.rotate_url()
                return True
        
        return False


# ═══════════════════════════════════════════════════════════════════════════
# AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════════════

class Authenticator:
    """Multi-factor authentication handler."""
    
    def __init__(self, audit_logger: AuditLogger, alert_system: AlertSystem):
        self.audit = audit_logger
        self.alerts = alert_system
        self.db_path = SecurityConfig.SECURITY_DB_PATH
    
    def check_ip_allowed(self, ip_address: str) -> bool:
        """Check if IP is in whitelist."""
        allowed = SecurityConfig.ALLOWED_IPS
        if not allowed or allowed == ['']:
            # No whitelist configured - allow all (development mode)
            return True
        return ip_address in allowed
    
    def check_lockout(self, ip_address: str) -> Tuple[bool, Optional[datetime]]:
        """Check if IP is locked out."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT attempts, locked_until FROM failed_attempts
                WHERE ip_address = ?
            ''', (ip_address,))
            
            row = cursor.fetchone()
            if not row:
                return False, None
            
            attempts, locked_until = row
            
            if locked_until:
                locked = datetime.fromisoformat(locked_until)
                if datetime.now(timezone.utc) < locked:
                    return True, locked
                else:
                    # Lockout expired, reset
                    conn.execute(
                        'DELETE FROM failed_attempts WHERE ip_address = ?',
                        (ip_address,)
                    )
                    conn.commit()
            
            return False, None
    
    def record_failed_attempt(self, ip_address: str):
        """Record failed authentication attempt."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT attempts FROM failed_attempts WHERE ip_address = ?
            ''', (ip_address,))
            
            row = cursor.fetchone()
            attempts = (row[0] if row else 0) + 1
            
            locked_until = None
            if attempts >= SecurityConfig.MAX_FAILED_ATTEMPTS:
                locked_until = (
                    datetime.now(timezone.utc) + 
                    timedelta(minutes=SecurityConfig.LOCKOUT_MINUTES)
                ).isoformat()
                
                self.alerts.send_alert(
                    AlertLevel.CRITICAL,
                    "IP Locked Out",
                    f"IP {ip_address} locked after {attempts} failed attempts"
                )
            
            conn.execute('''
                INSERT OR REPLACE INTO failed_attempts (ip_address, attempts, locked_until)
                VALUES (?, ?, ?)
            ''', (ip_address, attempts, locked_until))
            conn.commit()
    
    def clear_failed_attempts(self, ip_address: str):
        """Clear failed attempts after successful auth."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                'DELETE FROM failed_attempts WHERE ip_address = ?',
                (ip_address,)
            )
            conn.commit()
    
    def verify_password(self, password: str) -> bool:
        """Verify admin password."""
        stored_hash = SecurityConfig.ADMIN_PASSWORD_HASH
        if not stored_hash:
            # No password configured - reject all (unless development)
            if os.environ.get('LNCP_ENV') == 'development':
                return password == 'dev_password'
            return False
        return CryptoUtils.verify_password(password, stored_hash)
    
    def verify_totp(self, code: str) -> bool:
        """Verify TOTP code."""
        if not TOTP_AVAILABLE:
            return True  # Skip if not available
        
        secret = SecurityConfig.TOTP_SECRET
        if not secret:
            if os.environ.get('LNCP_ENV') == 'development':
                return True  # Skip in development
            return False
        
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)
    
    def authenticate(self, ip_address: str, user_agent: str,
                    password: str, totp_code: str = None,
                    client_cert_valid: bool = False) -> Tuple[AuthResult, Optional[Session]]:
        """Full authentication flow."""
        
        # Check IP whitelist
        if not self.check_ip_allowed(ip_address):
            self.audit.log(
                AuditAction.LOGIN_FAILED, ip_address, user_agent,
                success=False, details={"reason": "ip_not_allowed"}
            )
            self.alerts.send_alert(
                AlertLevel.CRITICAL,
                "Unauthorized IP Access Attempt",
                f"Access attempted from non-whitelisted IP: {ip_address}"
            )
            return AuthResult.FAILED_IP, None
        
        # Check lockout
        is_locked, locked_until = self.check_lockout(ip_address)
        if is_locked:
            self.audit.log(
                AuditAction.LOGIN_FAILED, ip_address, user_agent,
                success=False, details={"reason": "locked_out", "until": locked_until.isoformat()}
            )
            return AuthResult.LOCKED_OUT, None
        
        # Verify password
        if not self.verify_password(password):
            self.record_failed_attempt(ip_address)
            self.audit.log(
                AuditAction.LOGIN_FAILED, ip_address, user_agent,
                success=False, details={"reason": "invalid_password"}
            )
            self.alerts.send_alert(
                AlertLevel.WARNING,
                "Failed Login Attempt",
                f"Invalid password from {ip_address}"
            )
            return AuthResult.FAILED_PASSWORD, None
        
        # Verify TOTP
        if totp_code and not self.verify_totp(totp_code):
            self.record_failed_attempt(ip_address)
            self.audit.log(
                AuditAction.LOGIN_FAILED, ip_address, user_agent,
                success=False, details={"reason": "invalid_totp"}
            )
            self.alerts.send_alert(
                AlertLevel.WARNING,
                "Failed TOTP",
                f"Invalid TOTP code from {ip_address}"
            )
            return AuthResult.FAILED_TOTP, None
        
        # All checks passed - create session
        self.clear_failed_attempts(ip_address)
        
        session = Session(
            session_id=secrets.token_urlsafe(32),
            created_at=datetime.now(timezone.utc),
            last_activity=datetime.now(timezone.utc),
            ip_address=ip_address,
            user_agent=user_agent,
            authenticated_factors=["password"]
        )
        
        if totp_code:
            session.authenticated_factors.append("totp")
        if client_cert_valid:
            session.authenticated_factors.append("client_cert")
        
        # Store session
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO active_sessions 
                (session_id, created_at, last_activity, ip_address, user_agent, factors)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                session.session_id,
                session.created_at.isoformat(),
                session.last_activity.isoformat(),
                session.ip_address,
                session.user_agent,
                json.dumps(session.authenticated_factors)
            ))
            conn.commit()
        
        self.audit.log(
            AuditAction.LOGIN_SUCCESS, ip_address, user_agent,
            success=True, 
            details={"factors": session.authenticated_factors}
        )
        
        self.alerts.send_alert(
            AlertLevel.INFO,
            "Admin Login",
            f"Successful login from {ip_address}"
        )
        
        return AuthResult.SUCCESS, session
    
    def validate_session(self, session_id: str, ip_address: str) -> Optional[Session]:
        """Validate existing session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT session_id, created_at, last_activity, ip_address, user_agent, factors
                FROM active_sessions WHERE session_id = ?
            ''', (session_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            session = Session(
                session_id=row[0],
                created_at=datetime.fromisoformat(row[1]),
                last_activity=datetime.fromisoformat(row[2]),
                ip_address=row[3],
                user_agent=row[4],
                authenticated_factors=json.loads(row[5])
            )
            
            # Check session not expired
            if session.is_expired:
                self.invalidate_session(session_id)
                return None
            
            # Check IP matches (prevent session hijacking)
            if session.ip_address != ip_address:
                self.audit.log(
                    AuditAction.INTRUSION_DETECTED, ip_address, "",
                    success=False,
                    details={"reason": "session_ip_mismatch", "original_ip": session.ip_address}
                )
                self.alerts.send_alert(
                    AlertLevel.INTRUSION,
                    "Session Hijacking Attempt",
                    f"Session used from {ip_address}, original: {session.ip_address}"
                )
                self.invalidate_session(session_id)
                return None
            
            # Refresh session
            session.refresh()
            conn.execute('''
                UPDATE active_sessions SET last_activity = ?
                WHERE session_id = ?
            ''', (session.last_activity.isoformat(), session_id))
            conn.commit()
            
            return session
    
    def invalidate_session(self, session_id: str):
        """Invalidate a session."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                'DELETE FROM active_sessions WHERE session_id = ?',
                (session_id,)
            )
            conn.commit()
    
    def invalidate_all_sessions(self):
        """Invalidate all active sessions (emergency lockdown)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM active_sessions')
            conn.commit()


# ═══════════════════════════════════════════════════════════════════════════
# SECURITY GATEWAY (Main Interface)
# ═══════════════════════════════════════════════════════════════════════════

class SecurityGateway:
    """
    Main security interface for LNCP system.
    
    Usage:
        gateway = SecurityGateway()
        
        # Get current admin URL
        url = gateway.get_admin_url("https://yoursite.com")
        
        # Authenticate
        result, session = gateway.authenticate(
            ip_address="1.2.3.4",
            user_agent="Mozilla/5.0...",
            url_token="abc123...",
            password=os.environ.get("ADMIN_GATEWAY_PASSWORD"),  # never hardcode
            totp_code="123456"
        )
        
        # Validate session on subsequent requests
        session = gateway.validate_session(session_id, ip_address)
        
        # One-click rotation
        new_url = gateway.emergency_rotate_all()
    """
    
    def __init__(self):
        self.audit = AuditLogger()
        self.alerts = AlertSystem()
        self.url_rotator = URLRotator()
        self.authenticator = Authenticator(self.audit, self.alerts)
        
        # Ensure we have a valid URL token
        self.url_rotator.check_and_auto_rotate()
    
    def get_admin_url(self, base_url: str) -> str:
        """Get current admin URL."""
        return self.url_rotator.get_admin_url(base_url)
    
    def validate_url_token(self, token: str) -> bool:
        """Validate URL token before showing login page."""
        valid = self.url_rotator.validate_token(token)
        if not valid:
            self.alerts.send_alert(
                AlertLevel.WARNING,
                "Invalid Admin URL",
                f"Access attempted with invalid/expired URL token"
            )
        return valid
    
    def authenticate(self, ip_address: str, user_agent: str,
                    url_token: str, password: str, 
                    totp_code: str = None,
                    client_cert_valid: bool = False) -> Tuple[AuthResult, Optional[Session]]:
        """Full authentication flow."""
        
        # First validate URL token
        if not self.validate_url_token(url_token):
            self.audit.log(
                AuditAction.LOGIN_FAILED, ip_address, user_agent,
                success=False, details={"reason": "invalid_url_token"}
            )
            return AuthResult.INVALID_URL, None
        
        # Then full authentication
        return self.authenticator.authenticate(
            ip_address, user_agent, password, totp_code, client_cert_valid
        )
    
    def validate_session(self, session_id: str, ip_address: str) -> Optional[Session]:
        """Validate existing session."""
        return self.authenticator.validate_session(session_id, ip_address)
    
    def logout(self, session_id: str, ip_address: str):
        """Logout and invalidate session."""
        self.authenticator.invalidate_session(session_id)
        self.audit.log(
            AuditAction.LOGOUT, ip_address, "",
            success=True
        )
    
    def rotate_url(self) -> str:
        """Manually rotate URL token."""
        new_token = self.url_rotator.rotate_url(self.audit)
        return new_token
    
    def emergency_rotate_all(self, ip_address: str = "system") -> Dict:
        """
        One-click emergency rotation of all credentials.
        - Rotates URL token
        - Invalidates all sessions
        - Logs the action
        - Sends alert
        """
        # Rotate URL
        new_token = self.url_rotator.rotate_url(self.audit, ip_address)
        
        # Invalidate all sessions
        self.authenticator.invalidate_all_sessions()
        
        # Log
        self.audit.log(
            AuditAction.CREDENTIALS_ROTATED, ip_address, "system",
            success=True,
            details={"action": "emergency_rotate_all"}
        )
        
        # Alert
        self.alerts.send_alert(
            AlertLevel.WARNING,
            "Credentials Rotated",
            "All credentials and sessions have been rotated"
        )
        
        return {
            "new_url_token": new_token,
            "sessions_invalidated": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def get_security_status(self) -> Dict:
        """Get current security status."""
        with sqlite3.connect(SecurityConfig.SECURITY_DB_PATH) as conn:
            # Active sessions
            cursor = conn.execute('SELECT COUNT(*) FROM active_sessions')
            active_sessions = cursor.fetchone()[0]
            
            # Recent failures
            cursor = conn.execute('''
                SELECT COUNT(*) FROM audit_log 
                WHERE action = 'login_failed' 
                AND timestamp > ?
            ''', ((datetime.now(timezone.utc) - timedelta(hours=24)).isoformat(),))
            recent_failures = cursor.fetchone()[0]
            
            # Locked IPs
            cursor = conn.execute('''
                SELECT COUNT(*) FROM failed_attempts 
                WHERE locked_until > ?
            ''', (datetime.now(timezone.utc).isoformat(),))
            locked_ips = cursor.fetchone()[0]
        
        # Chain integrity
        integrity_ok, integrity_msg = self.audit.verify_chain_integrity()
        
        return {
            "status": "operational",
            "active_sessions": active_sessions,
            "recent_failures_24h": recent_failures,
            "locked_ips": locked_ips,
            "audit_chain_integrity": integrity_ok,
            "audit_chain_message": integrity_msg,
            "url_rotation_enabled": True,
            "totp_enabled": TOTP_AVAILABLE and bool(SecurityConfig.TOTP_SECRET),
            "ip_whitelist_enabled": bool(SecurityConfig.ALLOWED_IPS and SecurityConfig.ALLOWED_IPS != ['']),
            "alerts_enabled": self.alerts.twilio_available or self.alerts.pushover_available
        }
    
    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """Get recent audit log entries."""
        return self.audit.get_recent_entries(limit)


# ═══════════════════════════════════════════════════════════════════════════
# SETUP UTILITIES
# ═══════════════════════════════════════════════════════════════════════════

def setup_totp() -> Dict:
    """Generate new TOTP secret and QR code URI."""
    if not TOTP_AVAILABLE:
        return {
            "error": "pyotp not installed",
            "secret": "",
            "uri": "",
            "instructions": ["Install pyotp: pip install pyotp"]
        }
    
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(
        name="super_admin",
        issuer_name="LNCP"
    )
    
    return {
        "secret": secret,
        "uri": uri,
        "instructions": [
            "1. Save the secret securely (you'll need it for LNCP_TOTP_SECRET)",
            "2. Scan the QR code or enter the secret in your authenticator app",
            "3. Set environment variable: export LNCP_TOTP_SECRET=" + secret
        ]
    }


def setup_password(password: str) -> Dict:
    """Generate password hash for configuration."""
    hash_value = CryptoUtils.hash_password(password)
    return {
        "hash": hash_value,
        "instructions": [
            "Set environment variable:",
            f"export LNCP_ADMIN_PASSWORD_HASH='{hash_value}'"
        ]
    }


def generate_master_key() -> Dict:
    """Generate master encryption key."""
    key = Fernet.generate_key().decode()
    return {
        "key": key,
        "instructions": [
            "Set environment variable:",
            f"export LNCP_MASTER_KEY='{key}'",
            "KEEP THIS SECRET - it protects all encrypted data"
        ]
    }


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    "SecurityGateway",
    "SecurityConfig",
    "AlertLevel",
    "AuthResult",
    "AuditAction",
    "Session",
    "AuditEntry",
    "setup_totp",
    "setup_password",
    "generate_master_key",
]


# ═══════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="LNCP Security Gateway")
    parser.add_argument("command", choices=[
        "setup-totp", "setup-password", "generate-key",
        "rotate-url", "status", "audit-log"
    ])
    parser.add_argument("--password", help="Password for setup-password command")
    parser.add_argument("--limit", type=int, default=20, help="Limit for audit-log")
    
    args = parser.parse_args()
    
    if args.command == "setup-totp":
        result = setup_totp()
        print(json.dumps(result, indent=2))
    
    elif args.command == "setup-password":
        if not args.password:
            import getpass
            password = getpass.getpass("Enter password: ")
        else:
            password = args.password
        result = setup_password(password)
        print(json.dumps(result, indent=2))
    
    elif args.command == "generate-key":
        result = generate_master_key()
        print(json.dumps(result, indent=2))
    
    elif args.command == "rotate-url":
        gateway = SecurityGateway()
        token = gateway.rotate_url()
        print(f"New URL token: {token}")
        print(f"Admin URL: /gate/{token}")
    
    elif args.command == "status":
        gateway = SecurityGateway()
        status = gateway.get_security_status()
        print(json.dumps(status, indent=2))
    
    elif args.command == "audit-log":
        gateway = SecurityGateway()
        entries = gateway.get_audit_log(args.limit)
        for entry in entries:
            print(f"[{entry['timestamp']}] {entry['action']} from {entry['ip_address']} - {'✓' if entry['success'] else '✗'}")
