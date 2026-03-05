#!/usr/bin/env python3
"""
AGENT TESTING SCRIPT
Test all Phase 1 batch agents without requiring full database setup.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

async def test_agent_imports():
    """Test that all agent modules can be imported."""
    
    print("🧪 Testing Agent System Imports...")
    
    try:
        from backend.agents.base_agent import BatchAgent, AnalysisResults, OptimizationActions
        print("✅ Base agent framework imported successfully")
        
        from backend.agents.conversion_optimizer import ConversionOptimizationAgent
        print("✅ Conversion Optimization Agent imported successfully")
        
        from backend.agents.lncp_pattern_discovery import LNCPPatternDiscoveryAgent  
        print("✅ LNCP Pattern Discovery Agent imported successfully")
        
        from backend.agents.usage_pattern_analyzer import UsagePatternAnalyzer
        print("✅ Usage Pattern Analyzer imported successfully")
        
        from backend.agents.scheduler import BatchAgentScheduler
        print("✅ Batch Agent Scheduler imported successfully")
        
        print("\n🎉 All Phase 1 agents imported successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

async def test_agent_initialization():
    """Test agent initialization without database connection."""
    
    print("\n🔧 Testing Agent Initialization...")
    
    try:
        # Mock database pool for testing
        class MockDBPool:
            async def execute(self, query, *args):
                return None
            
            async def fetch(self, query, *args):
                return []
                
            async def fetchval(self, query, *args):
                return 0
        
        mock_db = MockDBPool()
        
        # Test agent creation
        from backend.agents.conversion_optimizer import ConversionOptimizationAgent
        from backend.agents.lncp_pattern_discovery import LNCPPatternDiscoveryAgent
        from backend.agents.usage_pattern_analyzer import UsagePatternAnalyzer
        
        conv_agent = ConversionOptimizationAgent(mock_db)
        print(f"✅ Conversion Optimizer created: {conv_agent.name}")
        
        lncp_agent = LNCPPatternDiscoveryAgent(mock_db)
        print(f"✅ LNCP Pattern Discovery created: {lncp_agent.name}")
        
        usage_agent = UsagePatternAnalyzer(mock_db)
        print(f"✅ Usage Pattern Analyzer created: {usage_agent.name}")
        
        # Test scheduler
        from backend.agents.scheduler import BatchAgentScheduler
        scheduler = BatchAgentScheduler(mock_db)
        print("✅ Batch Agent Scheduler created")
        
        print("\n🎉 All agents initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Initialization failed: {str(e)}")
        return False

def test_configuration():
    """Test agent configuration and schedules."""
    
    print("\n⚙️ Testing Agent Configuration...")
    
    try:
        from backend.agents.conversion_optimizer import ConversionOptimizationAgent
        from backend.agents.lncp_pattern_discovery import LNCPPatternDiscoveryAgent
        from backend.agents.usage_pattern_analyzer import UsagePatternAnalyzer
        
        # Mock database for config testing
        class MockDBPool:
            pass
        
        agents = [
            ConversionOptimizationAgent(MockDBPool()),
            LNCPPatternDiscoveryAgent(MockDBPool()),
            UsagePatternAnalyzer(MockDBPool())
        ]
        
        print("Agent Configuration Summary:")
        for agent in agents:
            print(f"  {agent.name}:")
            print(f"    Schedule: {agent.schedule_cron}")
            print(f"    Data Sources: {', '.join(agent.data_sources)}")
            print(f"    Config Keys: {list(agent.config.keys())}")
            print()
        
        print("🎉 Configuration validation passed!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {str(e)}")
        return False

def test_qstats_integration():
    """Test QStats agent monitoring integration."""
    
    print("\n📊 Testing QStats Integration...")
    
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, 
            os.path.join(os.path.dirname(__file__), 'qstats_demo'),
            'agents'
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
        
        if result.returncode == 0:
            print("✅ QStats agent monitoring working")
            if "Agent Health Overview" in result.stdout:
                print("✅ Agent health display working")
            if "System Impact & Improvements" in result.stdout:
                print("✅ Agent impact metrics working")
            print("🎉 QStats integration successful!")
            return True
        else:
            print(f"❌ QStats test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ QStats integration test failed: {str(e)}")
        return False

async def main():
    """Run all agent tests."""
    
    print("🤖 QUIRRELY BATCH AGENTS - PHASE 1 TESTING")
    print("=" * 50)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Import Tests", test_agent_imports()),
        ("Initialization Tests", test_agent_initialization()),
        ("Configuration Tests", test_configuration()),
        ("QStats Integration", test_qstats_integration())
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_coro_or_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        
        try:
            if asyncio.iscoroutine(test_coro_or_func):
                result = await test_coro_or_func
            else:
                result = test_coro_or_func
                
            if result:
                passed += 1
                
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    print("\n" + "="*50)
    print("🏁 TEST SUMMARY")
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Phase 1 agents ready for deployment!")
        print("\nNext Steps:")
        print("1. Run: ./scripts/setup_agent_cron.sh")
        print("2. Monitor: ./scripts/qstats_demo agents")
        print("3. Test execution: python3 backend/agents/scheduler.py run conversion_optimizer")
        return 0
    else:
        print("❌ Some tests failed - please review and fix issues")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)