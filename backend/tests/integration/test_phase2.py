#!/usr/bin/env python3
"""
PHASE 2 INTEGRATION TESTS
Validates all Phase 2 components work together.

Components tested:
1. Country gate middleware
2. httpOnly cookie authentication
3. Meta events pipeline
4. Feature flag API
5. Authority Meta bridge
6. HALO bridge

Run with: pytest backend/tests/integration/test_phase2.py -v
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from fastapi import FastAPI
from fastapi.testclient import TestClient


# ═══════════════════════════════════════════════════════════════════════════
# TEST FIXTURES
# ═══════════════════════════════════════════════════════════════════════════

@pytest.fixture
def app():
    """Create test FastAPI app."""
    from fastapi import FastAPI
    app = FastAPI()
    
    # Add middleware
    from middleware.country_gate import CountryGateMiddleware
    app.add_middleware(CountryGateMiddleware)
    
    # Add routers
    from features_api import router as features_router
    from meta_events_api import router as events_router
    
    app.include_router(features_router)
    app.include_router(events_router)
    
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_user():
    """Create mock user."""
    return {
        "id": "user_test123",
        "email": "test@example.com",
        "name": "Test User",
        "tier": "pro",
        "addons": ["voice_style"],
        "country": "CA",
    }


# ═══════════════════════════════════════════════════════════════════════════
# COUNTRY GATE TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestCountryGate:
    """Test country enforcement middleware."""
    
    def test_allowed_country_passes(self):
        """CA, GB, AU, NZ should be allowed."""
        from middleware.country_gate import CountryGate
        
        gate = CountryGate()
        
        # Mock GeoIP to return allowed countries
        with patch.object(gate.geoip, 'lookup') as mock_lookup:
            for country in ['CA', 'GB', 'AU', 'NZ']:
                mock_lookup.return_value = (country, f"Country {country}")
                result = gate.check('1.2.3.4')
                
                assert result.allowed, f"{country} should be allowed"
                assert result.country_code == country
    
    def test_blocked_country_rejected(self):
        """US should be blocked."""
        from middleware.country_gate import CountryGate
        
        gate = CountryGate()
        
        with patch.object(gate.geoip, 'lookup') as mock_lookup:
            mock_lookup.return_value = ('US', 'United States')
            result = gate.check('1.2.3.4')
            
            assert not result.allowed
            assert result.country_code == 'US'
            assert result.reason == 'country_blocked'
    
    def test_local_ip_bypasses(self):
        """Local IPs should bypass country check."""
        from middleware.country_gate import CountryGate
        
        gate = CountryGate()
        
        for ip in ['127.0.0.1', '::1', '192.168.1.1', '10.0.0.1']:
            result = gate.check(ip)
            assert result.allowed, f"{ip} should bypass"
    
    def test_health_endpoint_skipped(self):
        """Health check endpoints should be skipped."""
        from middleware.country_gate import CountryGate
        
        gate = CountryGate()
        
        for path in ['/health', '/healthz', '/api/health']:
            result = gate.check('1.2.3.4', path=path)
            assert result.allowed
            assert result.reason == 'path_skipped'


# ═══════════════════════════════════════════════════════════════════════════
# AUTH COOKIE TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestAuthCookies:
    """Test httpOnly cookie authentication."""
    
    def test_create_access_token(self):
        """Access token should contain user claims."""
        from auth_middleware import create_access_token, decode_token
        
        token = create_access_token(
            user_id="user_123",
            email="test@example.com",
            tier="pro",
            addons=["voice_style"],
        )
        
        payload = decode_token(token)
        
        assert payload is not None
        assert payload["sub"] == "user_123"
        assert payload["email"] == "test@example.com"
        assert payload["tier"] == "pro"
        assert payload["addons"] == ["voice_style"]
        assert payload["type"] == "access"
    
    def test_create_refresh_token(self):
        """Refresh token should contain minimal claims."""
        from auth_middleware import create_refresh_token, decode_token
        
        token = create_refresh_token(user_id="user_123")
        
        payload = decode_token(token)
        
        assert payload is not None
        assert payload["sub"] == "user_123"
        assert payload["type"] == "refresh"
        assert "email" not in payload  # Minimal claims
    
    def test_expired_token_returns_none(self):
        """Expired token should return None on decode."""
        from auth_middleware import decode_token, config
        import jwt
        
        # Create expired token
        payload = {
            "sub": "user_123",
            "type": "access",
            "exp": datetime.utcnow() - timedelta(hours=1),
        }
        token = jwt.encode(payload, config.JWT_SECRET, algorithm="HS256")
        
        result = decode_token(token)
        assert result is None
    
    def test_invalid_token_returns_none(self):
        """Invalid token should return None on decode."""
        from auth_middleware import decode_token
        
        result = decode_token("invalid.token.here")
        assert result is None
    
    def test_set_auth_cookies(self):
        """Cookies should be set on response."""
        from auth_middleware import set_auth_cookies, config
        from fastapi import Response
        
        response = Response()
        
        access, refresh = set_auth_cookies(
            response=response,
            user_id="user_123",
            email="test@example.com",
            tier="pro",
            addons=["voice_style"],
        )
        
        assert access is not None
        assert refresh is not None
        
        # Check cookies were set
        cookies = response.headers.getlist("set-cookie")
        assert len(cookies) == 2
        
        # Verify httpOnly flag
        for cookie in cookies:
            assert "httponly" in cookie.lower()


# ═══════════════════════════════════════════════════════════════════════════
# META EVENTS TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestMetaEvents:
    """Test Meta events pipeline."""
    
    def test_event_store_add(self):
        """Events should be stored correctly."""
        from meta_events_api import EventStore, MetaEventData
        
        store = EventStore()
        
        event = MetaEventData(
            event="page_view",
            data={"page": "/dashboard"},
            timestamp=1708012800000,
            sessionId="sess_123",
            userId="user_123",
            page="/dashboard",
            userAgent="Mozilla/5.0",
            referrer="",
        )
        
        store.add_event(event)
        
        assert len(store.events) == 1
        assert store.events_by_type["page_view"] == 1
        assert "sess_123" in store.sessions
        assert "user_123" in store.users
    
    def test_event_store_stats(self):
        """Stats should reflect stored events."""
        from meta_events_api import EventStore, MetaEventData
        
        store = EventStore()
        
        # Add multiple events
        for i in range(5):
            store.add_event(MetaEventData(
                event="page_view",
                data={},
                timestamp=1708012800000 + i,
                sessionId=f"sess_{i}",
                userId=f"user_{i % 2}",  # 2 unique users
                page="/test",
                userAgent="",
                referrer="",
            ))
        
        stats = store.get_stats()
        
        assert stats.total_events == 5
        assert stats.unique_sessions == 5
        assert stats.unique_users == 2
        assert stats.events_by_type["page_view"] == 5
    
    def test_event_store_max_size(self):
        """Store should trim old events."""
        from meta_events_api import EventStore, MetaEventData
        
        store = EventStore(max_events=10)
        
        # Add more than max
        for i in range(15):
            store.add_event(MetaEventData(
                event="test",
                data={},
                timestamp=i,
                sessionId=f"sess_{i}",
                page="",
                userAgent="",
                referrer="",
            ))
        
        assert len(store.events) == 10


# ═══════════════════════════════════════════════════════════════════════════
# FEATURE FLAG TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestFeatureFlags:
    """Test feature flag system."""
    
    def test_free_user_features(self):
        """Free user should have limited features."""
        from feature_gate import FeatureGate, Tier
        
        gate = FeatureGate()
        gate.set_user_tier("free_user", Tier.FREE)
        
        # Free should have basic
        result = gate.can_access("basic_analysis", "free_user")
        assert result.allowed
        
        # Free should NOT have save_results
        result = gate.can_access("save_results", "free_user")
        assert not result.allowed
    
    def test_pro_user_features(self):
        """Pro user should have pro features."""
        from feature_gate import FeatureGate, Tier
        
        gate = FeatureGate()
        gate.set_user_tier("pro_user", Tier.PRO)
        
        # Pro should have analytics
        result = gate.can_access("analytics", "pro_user")
        assert result.allowed
        
        # Pro should NOT have voice_profile (needs addon)
        result = gate.can_access("voice_profile", "pro_user")
        assert not result.allowed
    
    def test_addon_grants_access(self):
        """Addon should grant access to addon features."""
        from feature_gate import FeatureGate, Tier, Addon
        
        gate = FeatureGate()
        gate.set_user_tier("addon_user", Tier.FREE)
        gate.add_addon("addon_user", Addon.VOICE_STYLE)
        
        # Should have voice_profile with addon
        result = gate.can_access("voice_profile", "addon_user")
        assert result.allowed
    
    def test_daily_limits(self):
        """Daily limits should be enforced."""
        from feature_gate import FeatureGate, Tier
        
        gate = FeatureGate()
        gate.set_user_tier("limited_user", Tier.FREE)
        
        limits = gate.check_daily_limit("limited_user")
        
        assert limits["limit"] == 5  # Free tier limit
        assert limits["used"] == 0
        assert limits["remaining"] == 5


# ═══════════════════════════════════════════════════════════════════════════
# HALO BRIDGE TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestHALOBridge:
    """Test HALO bridge."""
    
    @pytest.mark.asyncio
    async def test_voice_analysis_event(self):
        """Voice analysis events should be queued."""
        from halo_bridge import get_halo_bridge, HALOEventType
        
        bridge = get_halo_bridge()
        
        # Without Meta, events should be queued
        result = await bridge.observe_voice_analysis_completed(
            user_id="user_123",
            profile_type="assertive",
            confidence=0.87,
            tokens=["Directness", "Confidence"],
            word_count=1250,
            analysis_duration_ms=2500,
        )
        
        # Event should be queued (Meta not available in test)
        stats = bridge.get_stats()
        assert stats["queue_size"] >= 1
    
    @pytest.mark.asyncio
    async def test_session_events(self):
        """Session events should be recorded."""
        from halo_bridge import get_halo_bridge
        
        bridge = get_halo_bridge()
        
        await bridge.observe_session_started(
            user_id="user_123",
            session_id="sess_123",
            tier="pro",
            country="CA",
        )
        
        # Should not throw
        assert True
    
    def test_event_types(self):
        """All event types should be defined."""
        from halo_bridge import HALOEventType
        
        # Voice events
        assert HALOEventType.VOICE_ANALYSIS_STARTED
        assert HALOEventType.VOICE_ANALYSIS_COMPLETED
        
        # User events
        assert HALOEventType.USER_SESSION_STARTED
        assert HALOEventType.USER_FEATURE_USED
        
        # Conversion events
        assert HALOEventType.TRIAL_STARTED
        assert HALOEventType.SUBSCRIPTION_CREATED


# ═══════════════════════════════════════════════════════════════════════════
# AUTHORITY META TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestAuthorityMeta:
    """Test Authority Meta bridge."""
    
    @pytest.mark.asyncio
    async def test_fallback_score(self):
        """Fallback score should be calculated from tier."""
        from authority_meta_api import MetaAuthorityBridge
        from dependencies import CurrentUser
        from feature_gate import Tier
        
        bridge = MetaAuthorityBridge()
        
        user = CurrentUser(
            id="user_123",
            email="test@example.com",
            name="Test",
            tier=Tier.PRO,
            addons=[],
        )
        
        result = await bridge.get_authority_score(user)
        
        assert result.score == 35.0  # Pro tier base score
        assert result.tier == "pro"
        assert result.level == "Established"
    
    def test_score_to_level(self):
        """Scores should map to correct levels."""
        from authority_meta_api import MetaAuthorityBridge
        
        bridge = MetaAuthorityBridge()
        
        assert bridge._score_to_level(98) == "Legendary"
        assert bridge._score_to_level(88) == "Authority"
        assert bridge._score_to_level(72) == "Featured"
        assert bridge._score_to_level(55) == "Established"
        assert bridge._score_to_level(30) == "Rising"
        assert bridge._score_to_level(10) == "Newcomer"


# ═══════════════════════════════════════════════════════════════════════════
# INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestEndToEnd:
    """End-to-end integration tests."""
    
    def test_auth_flow_with_features(self):
        """Complete auth flow should work with feature checks."""
        from auth_middleware import (
            create_access_token,
            decode_token,
            set_auth_cookies,
        )
        from feature_gate import FeatureGate, Tier
        
        # 1. Create user
        gate = FeatureGate()
        gate.set_user_tier("e2e_user", Tier.PRO)
        
        # 2. Create token
        token = create_access_token(
            user_id="e2e_user",
            email="e2e@test.com",
            tier="pro",
            addons=[],
        )
        
        # 3. Decode token
        payload = decode_token(token)
        assert payload["sub"] == "e2e_user"
        
        # 4. Check features
        result = gate.can_access("analytics", "e2e_user")
        assert result.allowed
    
    def test_country_to_features_flow(self):
        """Country check + feature check should work together."""
        from middleware.country_gate import CountryGate
        from feature_gate import FeatureGate, Tier
        
        country_gate = CountryGate()
        feature_gate = FeatureGate()
        
        # 1. Check country (mock CA)
        with patch.object(country_gate.geoip, 'lookup') as mock:
            mock.return_value = ('CA', 'Canada')
            country_result = country_gate.check('1.2.3.4')
        
        assert country_result.allowed
        
        # 2. Create user from that country
        feature_gate.set_user_tier("ca_user", Tier.PRO)
        
        # 3. Check features
        feature_result = feature_gate.can_access("analytics", "ca_user")
        assert feature_result.allowed


# ═══════════════════════════════════════════════════════════════════════════
# RUN TESTS
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
