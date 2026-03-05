#!/usr/bin/env python3
"""
QSTATS Integration Test
Validates the qstats command integrates properly with security features.
"""

import sys
import os
import subprocess
import json
from pathlib import Path

# Add backend to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_qstats_help():
    """Test qstats help functionality."""
    print("Testing qstats help...")
    
    qstats_path = Path(__file__).parent.parent / "scripts" / "qstats"
    
    try:
        result = subprocess.run(
            [str(qstats_path), "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 0
        assert "QUIRRELY STATS" in result.stdout
        assert "security" in result.stdout
        assert "users" in result.stdout
        assert "features" in result.stdout
        print("✅ qstats help test passed")
        
    except subprocess.TimeoutExpired:
        print("❌ qstats help test timed out")
        return False
    except Exception as e:
        print(f"❌ qstats help test failed: {e}")
        return False
    
    return True

def test_qstats_import():
    """Test qstats can be imported and basic classes work."""
    print("Testing qstats imports...")
    
    try:
        # Add scripts to path
        scripts_path = str(Path(__file__).parent.parent / "scripts")
        if scripts_path not in sys.path:
            sys.path.insert(0, scripts_path)
        
        # Import qstats module
        from qstats import QuirrellyStat, SecurityMetrics, UserMetrics, FeatureMetrics
        
        # Test basic class instantiation
        qstats = QuirrellyStat()
        assert hasattr(qstats, 'collect_security_metrics')
        assert hasattr(qstats, 'collect_user_metrics')
        assert hasattr(qstats, 'collect_feature_metrics')
        
        # Test metric classes
        security_metrics = SecurityMetrics()
        assert hasattr(security_metrics, 'security_score')
        assert security_metrics.security_score == 100.0
        
        user_metrics = UserMetrics()
        assert hasattr(user_metrics, 'total_users')
        assert user_metrics.total_users == 0
        
        feature_metrics = FeatureMetrics()
        assert hasattr(feature_metrics, 'total_checks')
        assert feature_metrics.total_checks == 0
        
        print("✅ qstats import test passed")
        return True
        
    except ImportError as e:
        print(f"❌ qstats import test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ qstats import test failed: {e}")
        return False

def test_qstats_security_integration():
    """Test qstats integrates with our security modules."""
    print("Testing qstats security integration...")
    
    try:
        # Add scripts to path
        scripts_path = str(Path(__file__).parent.parent / "scripts")
        if scripts_path not in sys.path:
            sys.path.insert(0, scripts_path)
        
        from qstats import QuirrellyStat, SecurityMetrics
        from unittest.mock import Mock, patch
        
        qstats = QuirrellyStat()
        
        # Mock database and Redis connections
        with patch.object(qstats, 'db_conn') as mock_db, \
             patch.object(qstats, 'redis_conn') as mock_redis:
            
            # Mock database cursor
            mock_cursor = Mock()
            mock_db.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = (10, 2, 1, 5, 1)  # Mock security data
            mock_cursor.fetchall.return_value = [('injection_attempt', 1), ('brute_force', 1)]
            
            # Mock Redis
            mock_redis.keys.side_effect = [
                ['ws:conn1'],  # WebSocket connections
                ['session:1', 'session:2'],  # Active sessions
            ]
            
            # Test security metrics collection
            metrics = qstats.collect_security_metrics()
            
            assert isinstance(metrics, SecurityMetrics)
            assert metrics.total_events == 10
            assert metrics.threat_events == 2
            assert metrics.websocket_connections == 1
            assert metrics.active_sessions == 2
            
        print("✅ qstats security integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ qstats security integration test failed: {e}")
        return False

def test_qstats_json_output():
    """Test qstats JSON output for automation."""
    print("Testing qstats JSON output...")
    
    try:
        scripts_path = str(Path(__file__).parent.parent / "scripts")
        if scripts_path not in sys.path:
            sys.path.insert(0, scripts_path)
        
        from qstats import QuirrellyStat, SecurityMetrics, UserMetrics, FeatureMetrics, SystemMetrics, EventMetrics
        from unittest.mock import patch
        import json
        
        qstats = QuirrellyStat()
        
        # Create test metrics
        security = SecurityMetrics(total_events=100, security_score=85.0)
        users = UserMetrics(total_users=1000, new_signups_today=5)
        features = FeatureMetrics(total_checks=500, allowed_accesses=450)
        system = SystemMetrics(database_connections=10)
        events = EventMetrics(total_events=200, events_today=50)
        
        # Capture JSON output
        with patch('builtins.print') as mock_print:
            qstats.display_json(security, users, features, system, events)
            
            # Verify JSON was printed
            assert mock_print.called
            json_output = mock_print.call_args[0][0]
            
            # Parse and validate JSON
            data = json.loads(json_output)
            assert 'timestamp' in data
            assert 'security' in data
            assert 'users' in data
            assert 'features' in data
            assert 'system' in data
            assert 'events' in data
            
            # Validate specific values
            assert data['security']['total_events'] == 100
            assert data['security']['security_score'] == 85.0
            assert data['users']['total_users'] == 1000
            assert data['features']['total_checks'] == 500
        
        print("✅ qstats JSON output test passed")
        return True
        
    except Exception as e:
        print(f"❌ qstats JSON output test failed: {e}")
        return False

def main():
    """Run all qstats integration tests."""
    print("=" * 60)
    print("QSTATS INTEGRATION TESTS")
    print("=" * 60)
    print()
    
    tests = [
        test_qstats_help,
        test_qstats_import,
        test_qstats_security_integration,
        test_qstats_json_output,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed with exception: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("✅ All qstats integration tests passed!")
        return 0
    else:
        print("❌ Some qstats integration tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())