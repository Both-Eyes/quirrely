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
        
        # Phase 2 agents
        from backend.agents.retention_predictor import RetentionPredictionAgent
        print("✅ Retention Prediction Agent imported successfully")
        
        from backend.agents.ab_test_analyzer import ABTestAnalysisAgent
        print("✅ A/B Test Analysis Agent imported successfully")
        
        from backend.agents.content_optimizer import ContentOptimizationAgent
        print("✅ Content Optimization Agent imported successfully")
        
        # Phase 3 agents
        from backend.agents.partnership_intelligence import PartnershipIntelligenceAgent
        print("✅ Partnership Intelligence Agent imported successfully")
        
        from backend.agents.pricing_optimization import PricingOptimizationAgent
        print("✅ Pricing Optimization Agent imported successfully")
        
        from backend.agents.revenue_forecasting import RevenueForecastingAgent
        print("✅ Revenue Forecasting Agent imported successfully")
        
        from backend.agents.scheduler import BatchAgentScheduler
        print("✅ Batch Agent Scheduler imported successfully")
        
        print("\n🎉 All Phase 1, 2 & 3 agents imported successfully!")
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
        
        # Test agent creation - Phase 1
        from backend.agents.conversion_optimizer import ConversionOptimizationAgent
        from backend.agents.lncp_pattern_discovery import LNCPPatternDiscoveryAgent
        from backend.agents.usage_pattern_analyzer import UsagePatternAnalyzer
        
        conv_agent = ConversionOptimizationAgent(mock_db)
        print(f"✅ Conversion Optimizer created: {conv_agent.name}")
        
        lncp_agent = LNCPPatternDiscoveryAgent(mock_db)
        print(f"✅ LNCP Pattern Discovery created: {lncp_agent.name}")
        
        usage_agent = UsagePatternAnalyzer(mock_db)
        print(f"✅ Usage Pattern Analyzer created: {usage_agent.name}")
        
        # Test agent creation - Phase 2
        from backend.agents.retention_predictor import RetentionPredictionAgent
        from backend.agents.ab_test_analyzer import ABTestAnalysisAgent
        from backend.agents.content_optimizer import ContentOptimizationAgent
        
        retention_agent = RetentionPredictionAgent(mock_db)
        print(f"✅ Retention Predictor created: {retention_agent.name}")
        
        ab_test_agent = ABTestAnalysisAgent(mock_db)
        print(f"✅ A/B Test Analyzer created: {ab_test_agent.name}")
        
        content_agent = ContentOptimizationAgent(mock_db)
        print(f"✅ Content Optimizer created: {content_agent.name}")
        
        # Test agent creation - Phase 3
        from backend.agents.partnership_intelligence import PartnershipIntelligenceAgent
        from backend.agents.pricing_optimization import PricingOptimizationAgent
        from backend.agents.revenue_forecasting import RevenueForecastingAgent
        
        partnership_agent = PartnershipIntelligenceAgent(mock_db)
        print(f"✅ Partnership Intelligence created: {partnership_agent.name}")
        
        pricing_agent = PricingOptimizationAgent(mock_db)
        print(f"✅ Pricing Optimizer created: {pricing_agent.name}")
        
        revenue_agent = RevenueForecastingAgent(mock_db)
        print(f"✅ Revenue Forecasting created: {revenue_agent.name}")
        
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
        from backend.agents.retention_predictor import RetentionPredictionAgent
        from backend.agents.ab_test_analyzer import ABTestAnalysisAgent
        from backend.agents.content_optimizer import ContentOptimizationAgent
        from backend.agents.partnership_intelligence import PartnershipIntelligenceAgent
        from backend.agents.pricing_optimization import PricingOptimizationAgent
        from backend.agents.revenue_forecasting import RevenueForecastingAgent
        
        # Mock database for config testing
        class MockDBPool:
            pass
        
        agents = [
            # Phase 1 agents
            ConversionOptimizationAgent(MockDBPool()),
            LNCPPatternDiscoveryAgent(MockDBPool()),
            UsagePatternAnalyzer(MockDBPool()),
            # Phase 2 agents
            RetentionPredictionAgent(MockDBPool()),
            ABTestAnalysisAgent(MockDBPool()),
            ContentOptimizationAgent(MockDBPool()),
            # Phase 3 agents
            PartnershipIntelligenceAgent(MockDBPool()),
            PricingOptimizationAgent(MockDBPool()),
            RevenueForecastingAgent(MockDBPool())
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
    
    print("🤖 QUIRRELY BATCH AGENTS - PHASE 1, 2 & 3 TESTING")
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
        print("🎉 ALL TESTS PASSED - Phase 1, 2 & 3 agents ready for deployment!")
        print("\nNext Steps:")
        print("1. Run: ./scripts/setup_agent_cron.sh")
        print("2. Monitor: ./scripts/qstats_demo agents")
        print("3. Test Phase 1: python3 backend/agents/scheduler.py run conversion_optimizer")
        print("4. Test Phase 2: python3 backend/agents/scheduler.py run retention_predictor")
        print("5. Test Phase 3: python3 backend/agents/scheduler.py run partnership_intelligence")
        return 0
    else:
        print("❌ Some tests failed - please review and fix issues")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)