#!/usr/bin/env python3
"""
QUIRRELY SECURITY LOGGER v1.0
Structured security event logging and monitoring.

Features:
- Structured JSON logging for security events
- Real-time security alert detection
- Performance monitoring
- Log aggregation and analysis
- Automated threat response
"""

import os
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, asdict
import asyncio
from pathlib import Path

import structlog

# ═══════════════════════════════════════════════════════════════════════════
# SECURITY EVENT TYPES
# ═══════════════════════════════════════════════════════════════════════════

class SecurityEventType(Enum):
    """Security event types for categorization and alerting."""
    
    # Authentication Events
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    TOKEN_EXPIRED = "token_expired"
    TOKEN_INVALID = "token_invalid"
    PASSWORD_RESET = "password_reset"
    ACCOUNT_LOCKED = "account_locked"
    
    # Authorization Events
    ADMIN_ACCESS = "admin_access"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    RESOURCE_ACCESS_DENIED = "resource_access_denied"
    
    # Attack Detection
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    IP_BLOCKED = "ip_blocked"
    SQL_INJECTION_ATTEMPT = "sql_injection_attempt"
    XSS_ATTEMPT = "xss_attempt"
    CSRF_ATTEMPT = "csrf_attempt"
    BRUTE_FORCE_ATTEMPT = "brute_force_attempt"
    
    # System Security
    CONFIG_CHANGE = "config_change"
    SECRET_ACCESS = "secret_access"
    FILE_ACCESS_VIOLATION = "file_access_violation"
    SYSTEM_COMPROMISE = "system_compromise"
    
    # Network Security
    INVALID_ORIGIN = "invalid_origin"
    MALICIOUS_USER_AGENT = "malicious_user_agent"
    GEO_RESTRICTION_VIOLATION = "geo_restriction_violation"
    VPN_DETECTION = "vpn_detection"

class SecurityEventSeverity(Enum):
    """Event severity levels for prioritization."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# ═══════════════════════════════════════════════════════════════════════════
# SECURITY EVENT DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SecurityEvent:
    """Structured security event data."""
    
    # Core identification
    event_type: SecurityEventType
    severity: SecurityEventSeverity
    timestamp: datetime
    event_id: str
    
    # Request context
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_path: Optional[str] = None
    request_method: Optional[str] = None
    
    # Event details
    message: str = ""
    additional_data: Optional[Dict[str, Any]] = None
    
    # Geo and network info
    country_code: Optional[str] = None
    city: Optional[str] = None
    asn: Optional[str] = None
    
    # Detection info
    detection_rule: Optional[str] = None
    confidence_score: float = 1.0
    false_positive: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["event_type"] = self.event_type.value
        data["severity"] = self.severity.value
        data["timestamp"] = self.timestamp.isoformat()
        return data

# ═══════════════════════════════════════════════════════════════════════════
# SECURITY LOGGER CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SecurityLoggerConfig:
    """Security logger configuration."""
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/var/log/quirrely/security.log"
    LOG_ROTATION_SIZE: int = 100 * 1024 * 1024  # 100MB
    LOG_RETENTION_DAYS: int = 90
    
    # Real-time alerting
    ENABLE_REALTIME_ALERTS: bool = True
    ALERT_THRESHOLD_WINDOW: int = 300  # 5 minutes
    CRITICAL_ALERT_THRESHOLD: int = 1
    HIGH_ALERT_THRESHOLD: int = 5
    MEDIUM_ALERT_THRESHOLD: int = 20
    
    # Performance settings
    ASYNC_LOGGING: bool = True
    BUFFER_SIZE: int = 1000
    FLUSH_INTERVAL: int = 5
    
    # Export settings
    EXPORT_TO_SIEM: bool = False
    SIEM_ENDPOINT: Optional[str] = None
    
    def __post_init__(self):
        """Initialize from environment variables."""
        self.LOG_LEVEL = os.environ.get("SECURITY_LOG_LEVEL", self.LOG_LEVEL)
        self.LOG_FILE = os.environ.get("SECURITY_LOG_FILE", self.LOG_FILE)
        self.ENABLE_REALTIME_ALERTS = os.environ.get("ENABLE_SECURITY_ALERTS", "true").lower() == "true"
        self.EXPORT_TO_SIEM = os.environ.get("EXPORT_TO_SIEM", "false").lower() == "true"
        self.SIEM_ENDPOINT = os.environ.get("SIEM_ENDPOINT")

# ═══════════════════════════════════════════════════════════════════════════
# THREAT DETECTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class ThreatDetectionEngine:
    """Real-time threat detection and alerting."""
    
    def __init__(self):
        self.event_history: List[SecurityEvent] = []
        self.ip_reputation: Dict[str, float] = {}
        self.user_risk_scores: Dict[str, float] = {}
        self.alert_cooldowns: Dict[str, datetime] = {}
    
    def analyze_event(self, event: SecurityEvent) -> Dict[str, Any]:
        """
        Analyze security event for threats and patterns.
        
        Returns:
            Analysis results with threat indicators
        """
        analysis = {
            "threat_detected": False,
            "threat_type": None,
            "risk_score": 0.0,
            "recommended_action": "monitor",
            "patterns_detected": []
        }
        
        # Check for brute force attacks
        if event.event_type == SecurityEventType.AUTH_FAILURE:
            brute_force_score = self._detect_brute_force(event)
            if brute_force_score > 0.7:
                analysis.update({
                    "threat_detected": True,
                    "threat_type": "brute_force",
                    "risk_score": brute_force_score,
                    "recommended_action": "block_ip",
                    "patterns_detected": ["repeated_auth_failures"]
                })
        
        # Check for suspicious IP behavior
        if event.ip_address:
            ip_risk = self._analyze_ip_reputation(event.ip_address)
            if ip_risk > 0.8:
                analysis["patterns_detected"].append("suspicious_ip")
                analysis["risk_score"] = max(analysis["risk_score"], ip_risk)
        
        # Check for privilege escalation attempts
        if event.event_type == SecurityEventType.UNAUTHORIZED_ACCESS:
            if event.additional_data and "admin" in str(event.additional_data).lower():
                analysis.update({
                    "threat_detected": True,
                    "threat_type": "privilege_escalation",
                    "risk_score": 0.9,
                    "recommended_action": "investigate",
                    "patterns_detected": ["admin_access_attempt"]
                })
        
        # Update event history for pattern detection
        self._update_event_history(event)
        
        return analysis
    
    def _detect_brute_force(self, event: SecurityEvent) -> float:
        """Detect brute force attacks based on failure patterns."""
        if not event.ip_address:
            return 0.0
        
        # Count failures from same IP in last 10 minutes
        cutoff = datetime.utcnow() - timedelta(minutes=10)
        failures = [
            e for e in self.event_history
            if (e.ip_address == event.ip_address and
                e.event_type == SecurityEventType.AUTH_FAILURE and
                e.timestamp > cutoff)
        ]
        
        # Risk score based on failure count
        failure_count = len(failures) + 1  # +1 for current event
        if failure_count >= 10:
            return 1.0
        elif failure_count >= 5:
            return 0.8
        elif failure_count >= 3:
            return 0.5
        else:
            return failure_count * 0.1
    
    def _analyze_ip_reputation(self, ip_address: str) -> float:
        """Analyze IP reputation and risk score."""
        # Simple reputation system - in production, integrate with threat intel
        if ip_address in self.ip_reputation:
            return self.ip_reputation[ip_address]
        
        # Basic heuristics
        risk_score = 0.0
        
        # Check for suspicious patterns
        recent_events = [
            e for e in self.event_history
            if (e.ip_address == ip_address and
                e.timestamp > datetime.utcnow() - timedelta(hours=24))
        ]
        
        # High volume of events from single IP
        if len(recent_events) > 100:
            risk_score += 0.3
        
        # Multiple event types (reconnaissance)
        event_types = set(e.event_type for e in recent_events)
        if len(event_types) > 5:
            risk_score += 0.2
        
        # Attack events
        attack_events = [
            e for e in recent_events
            if e.event_type in [
                SecurityEventType.SQL_INJECTION_ATTEMPT,
                SecurityEventType.XSS_ATTEMPT,
                SecurityEventType.BRUTE_FORCE_ATTEMPT
            ]
        ]
        if attack_events:
            risk_score += 0.5
        
        self.ip_reputation[ip_address] = min(risk_score, 1.0)
        return self.ip_reputation[ip_address]
    
    def _update_event_history(self, event: SecurityEvent):
        """Update event history for pattern analysis."""
        self.event_history.append(event)
        
        # Keep only recent events to prevent memory bloat
        cutoff = datetime.utcnow() - timedelta(hours=24)
        self.event_history = [
            e for e in self.event_history
            if e.timestamp > cutoff
        ]
    
    def should_alert(self, event: SecurityEvent, analysis: Dict[str, Any]) -> bool:
        """Determine if an alert should be sent for this event."""
        # Check cooldowns to prevent alert spam
        alert_key = f"{event.event_type.value}:{event.ip_address or 'unknown'}"
        cooldown_until = self.alert_cooldowns.get(alert_key)
        
        if cooldown_until and datetime.utcnow() < cooldown_until:
            return False
        
        # Alert criteria
        should_alert = (
            event.severity == SecurityEventSeverity.CRITICAL or
            analysis.get("threat_detected", False) or
            analysis.get("risk_score", 0) > 0.8
        )
        
        if should_alert:
            # Set cooldown (5 minutes for most events, 1 hour for high-risk IPs)
            cooldown_duration = 3600 if analysis.get("risk_score", 0) > 0.9 else 300
            self.alert_cooldowns[alert_key] = datetime.utcnow() + timedelta(seconds=cooldown_duration)
        
        return should_alert

# ═══════════════════════════════════════════════════════════════════════════
# SECURITY LOGGER
# ═══════════════════════════════════════════════════════════════════════════

class SecurityLogger:
    """Centralized security event logger with threat detection."""
    
    def __init__(self):
        self.config = SecurityLoggerConfig()
        self.threat_engine = ThreatDetectionEngine()
        self.event_buffer: List[SecurityEvent] = []
        self._setup_logging()
        
        # Start async processing if enabled
        if self.config.ASYNC_LOGGING:
            self._processing_task = asyncio.create_task(self._process_events())
    
    def _setup_logging(self):
        """Configure structured logging."""
        # Ensure log directory exists
        log_dir = Path(self.config.LOG_FILE).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # Configure file handler
        self.logger = structlog.get_logger("security")
        
        # Configure standard library logger for file output
        stdlib_logger = logging.getLogger("security")
        stdlib_logger.setLevel(getattr(logging, self.config.LOG_LEVEL))
        
        # File handler with rotation
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            self.config.LOG_FILE,
            maxBytes=self.config.LOG_ROTATION_SIZE,
            backupCount=5
        )
        file_handler.setLevel(getattr(logging, self.config.LOG_LEVEL))
        
        # JSON formatter
        formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(formatter)
        
        stdlib_logger.addHandler(file_handler)
    
    def log_event(
        self,
        event_type: SecurityEventType,
        severity: SecurityEventSeverity,
        message: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_path: Optional[str] = None,
        request_method: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Log a security event with automatic threat analysis.
        
        Args:
            event_type: Type of security event
            severity: Event severity level
            message: Human-readable event description
            user_id: User identifier (if applicable)
            session_id: Session identifier (if applicable)
            ip_address: Client IP address
            user_agent: Client user agent
            request_path: HTTP request path
            request_method: HTTP request method
            additional_data: Additional event data
            **kwargs: Additional event attributes
        """
        # Create security event
        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            timestamp=datetime.utcnow(),
            event_id=self._generate_event_id(),
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_path=request_path,
            request_method=request_method,
            message=message,
            additional_data=additional_data or {}
        )
        
        # Add any additional attributes
        for key, value in kwargs.items():
            if hasattr(event, key):
                setattr(event, key, value)
        
        # Perform threat analysis
        analysis = self.threat_engine.analyze_event(event)
        
        # Update event with analysis results
        event.additional_data.update({
            "threat_analysis": analysis
        })
        
        # Log the event
        self._write_event(event)
        
        # Handle real-time alerting
        if (self.config.ENABLE_REALTIME_ALERTS and 
            self.threat_engine.should_alert(event, analysis)):
            self._send_alert(event, analysis)
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        timestamp = datetime.utcnow().isoformat()
        return hashlib.sha256(f"{timestamp}:{os.urandom(16).hex()}".encode()).hexdigest()[:16]
    
    def _write_event(self, event: SecurityEvent):
        """Write event to log."""
        if self.config.ASYNC_LOGGING:
            # Add to buffer for async processing
            self.event_buffer.append(event)
            
            # Flush if buffer is full
            if len(self.event_buffer) >= self.config.BUFFER_SIZE:
                asyncio.create_task(self._flush_buffer())
        else:
            # Write immediately
            self._write_event_sync(event)
    
    def _write_event_sync(self, event: SecurityEvent):
        """Synchronously write event to log."""
        event_data = event.to_dict()
        
        # Determine log level
        if event.severity == SecurityEventSeverity.CRITICAL:
            self.logger.critical("Security event", **event_data)
        elif event.severity == SecurityEventSeverity.HIGH:
            self.logger.error("Security event", **event_data)
        elif event.severity == SecurityEventSeverity.MEDIUM:
            self.logger.warning("Security event", **event_data)
        else:
            self.logger.info("Security event", **event_data)
    
    async def _process_events(self):
        """Async event processing loop."""
        while True:
            try:
                if self.event_buffer:
                    await self._flush_buffer()
                await asyncio.sleep(self.config.FLUSH_INTERVAL)
            except Exception as e:
                print(f"Error in security logger processing: {e}")
                await asyncio.sleep(5)
    
    async def _flush_buffer(self):
        """Flush buffered events to log."""
        events_to_flush = self.event_buffer.copy()
        self.event_buffer.clear()
        
        for event in events_to_flush:
            self._write_event_sync(event)
    
    def _send_alert(self, event: SecurityEvent, analysis: Dict[str, Any]):
        """Send real-time security alert."""
        alert_data = {
            "alert_type": "security_event",
            "severity": event.severity.value,
            "event_type": event.event_type.value,
            "timestamp": event.timestamp.isoformat(),
            "message": event.message,
            "ip_address": event.ip_address,
            "user_id": event.user_id,
            "threat_analysis": analysis
        }
        
        # In production, send to alerting system (Slack, PagerDuty, etc.)
        print(f"🚨 SECURITY ALERT: {json.dumps(alert_data, indent=2)}")
    
    def get_recent_events(
        self, 
        hours: int = 24, 
        event_types: Optional[List[SecurityEventType]] = None,
        min_severity: SecurityEventSeverity = SecurityEventSeverity.LOW
    ) -> List[Dict[str, Any]]:
        """Get recent security events from threat engine history."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        events = [
            event for event in self.threat_engine.event_history
            if (event.timestamp > cutoff and
                event.severity.value >= min_severity.value and
                (not event_types or event.event_type in event_types))
        ]
        
        return [event.to_dict() for event in events]
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get security statistics and metrics."""
        recent_events = self.threat_engine.event_history
        
        # Count events by type and severity
        event_counts = {}
        severity_counts = {}
        
        for event in recent_events:
            event_counts[event.event_type.value] = event_counts.get(event.event_type.value, 0) + 1
            severity_counts[event.severity.value] = severity_counts.get(event.severity.value, 0) + 1
        
        return {
            "total_events_24h": len(recent_events),
            "events_by_type": event_counts,
            "events_by_severity": severity_counts,
            "unique_ips": len(set(e.ip_address for e in recent_events if e.ip_address)),
            "high_risk_ips": len([ip for ip, score in self.threat_engine.ip_reputation.items() if score > 0.7]),
            "buffer_size": len(self.event_buffer),
            "config": {
                "async_logging": self.config.ASYNC_LOGGING,
                "realtime_alerts": self.config.ENABLE_REALTIME_ALERTS,
                "log_file": self.config.LOG_FILE
            }
        }

# ═══════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

# Global security logger instance
security_logger = SecurityLogger()

def log_auth_success(user_id: str, ip_address: str, **kwargs):
    """Log successful authentication."""
    security_logger.log_event(
        SecurityEventType.AUTH_SUCCESS,
        SecurityEventSeverity.LOW,
        f"User {user_id} authenticated successfully",
        user_id=user_id,
        ip_address=ip_address,
        **kwargs
    )

def log_auth_failure(ip_address: str, reason: str, **kwargs):
    """Log authentication failure."""
    security_logger.log_event(
        SecurityEventType.AUTH_FAILURE,
        SecurityEventSeverity.MEDIUM,
        f"Authentication failed: {reason}",
        ip_address=ip_address,
        additional_data={"failure_reason": reason},
        **kwargs
    )

def log_admin_access(user_id: str, ip_address: str, action: str, **kwargs):
    """Log admin access attempt."""
    security_logger.log_event(
        SecurityEventType.ADMIN_ACCESS,
        SecurityEventSeverity.HIGH,
        f"Admin access: {action}",
        user_id=user_id,
        ip_address=ip_address,
        additional_data={"admin_action": action},
        **kwargs
    )

def log_suspicious_activity(description: str, ip_address: str = None, **kwargs):
    """Log suspicious activity."""
    security_logger.log_event(
        SecurityEventType.SUSPICIOUS_ACTIVITY,
        SecurityEventSeverity.HIGH,
        f"Suspicious activity detected: {description}",
        ip_address=ip_address,
        **kwargs
    )

def log_attack_attempt(attack_type: str, ip_address: str, details: Dict[str, Any] = None, **kwargs):
    """Log attack attempt."""
    event_type_map = {
        "sql_injection": SecurityEventType.SQL_INJECTION_ATTEMPT,
        "xss": SecurityEventType.XSS_ATTEMPT,
        "csrf": SecurityEventType.CSRF_ATTEMPT,
        "brute_force": SecurityEventType.BRUTE_FORCE_ATTEMPT
    }
    
    event_type = event_type_map.get(attack_type, SecurityEventType.SUSPICIOUS_ACTIVITY)
    
    security_logger.log_event(
        event_type,
        SecurityEventSeverity.CRITICAL,
        f"{attack_type.upper()} attack attempt detected",
        ip_address=ip_address,
        additional_data=details or {},
        **kwargs
    )

# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    'SecurityEventType',
    'SecurityEventSeverity', 
    'SecurityEvent',
    'SecurityLogger',
    'ThreatDetectionEngine',
    'security_logger',
    'log_auth_success',
    'log_auth_failure',
    'log_admin_access',
    'log_suspicious_activity',
    'log_attack_attempt'
]