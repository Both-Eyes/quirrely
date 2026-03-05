#!/usr/bin/env python3
"""
COLLABORATION SYSTEM TEST SUITE
Complete test suite for collaboration system including all components.
Run this before deployment to ensure everything works correctly.
"""

import asyncio
import subprocess
import sys
import os
from pathlib import Path
from typing import List, Dict, Any

class CollaborationTestSuite:
    def __init__(self):
        self.root_dir = Path("/root/quirrely_v313_integrated")
        self.backend_dir = self.root_dir / "backend"
        self.results: Dict[str, Dict] = {}
        
    def run_test_file(self, test_file: Path, description: str) -> tuple[bool, str]:
        """Run a test file and return success status and output."""
        try:
            print(f"  Running {test_file.name}...")
            
            # Change to backend directory and run test
            process = subprocess.run(
                [sys.executable, str(test_file)],
                cwd=self.backend_dir,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            if process.returncode == 0:
                return True, process.stdout
            else:
                return False, f"Exit code {process.returncode}:\n{process.stderr}\n{process.stdout}"
                
        except subprocess.TimeoutExpired:
            return False, "Test timed out after 2 minutes"
        except Exception as e:
            return False, f"Test execution error: {e}"
    
    def test_collaboration_core_functionality(self) -> bool:
        """Test core collaboration functionality."""
        print("🧪 Testing Core Collaboration Functionality...")
        
        test_file = self.backend_dir / "test_collaboration_e2e.py"
        if not test_file.exists():
            print("  ❌ E2E test file not found")
            self.results['core_functionality'] = {'passed': False, 'error': 'Test file missing'}
            return False
            
        passed, output = self.run_test_file(test_file, "End-to-end collaboration testing")
        
        self.results['core_functionality'] = {
            'passed': passed,
            'output': output
        }
        
        if passed:
            print("  ✅ Core functionality tests passed")
        else:
            print("  ❌ Core functionality tests failed")
            print(f"     {output[:200]}...")
            
        return passed
    
    def test_cancellation_rate_limiting(self) -> bool:
        """Test cancellation rate limiting system."""
        print("🧪 Testing Cancellation Rate Limiting...")
        
        test_file = self.backend_dir / "test_cancellation_rate_limiting.py"
        if not test_file.exists():
            print("  ❌ Rate limiting test file not found")
            self.results['rate_limiting'] = {'passed': False, 'error': 'Test file missing'}
            return False
            
        passed, output = self.run_test_file(test_file, "Rate limiting functionality")
        
        self.results['rate_limiting'] = {
            'passed': passed,
            'output': output
        }
        
        if passed:
            print("  ✅ Rate limiting tests passed")
        else:
            print("  ❌ Rate limiting tests failed")
            print(f"     {output[:200]}...")
            
        return passed
    
    def test_cancellation_e2e(self) -> bool:
        """Test cancellation end-to-end integration."""
        print("🧪 Testing Cancellation E2E Integration...")
        
        test_file = self.backend_dir / "test_cancellation_e2e.py"
        if not test_file.exists():
            print("  ❌ Cancellation E2E test file not found")
            self.results['cancellation_e2e'] = {'passed': False, 'error': 'Test file missing'}
            return False
            
        passed, output = self.run_test_file(test_file, "Cancellation end-to-end integration")
        
        self.results['cancellation_e2e'] = {
            'passed': passed,
            'output': output
        }
        
        if passed:
            print("  ✅ Cancellation E2E tests passed")
        else:
            print("  ❌ Cancellation E2E tests failed")
            print(f"     {output[:200]}...")
            
        return passed
    
    def test_frontend_integration(self) -> bool:
        """Test frontend integration."""
        print("🧪 Testing Frontend Integration...")
        
        test_file = self.backend_dir / "test_frontend_integration.py"
        if not test_file.exists():
            print("  ❌ Frontend integration test file not found")
            self.results['frontend_integration'] = {'passed': False, 'error': 'Test file missing'}
            return False
            
        passed, output = self.run_test_file(test_file, "Frontend integration testing")
        
        self.results['frontend_integration'] = {
            'passed': passed,
            'output': output
        }
        
        if passed:
            print("  ✅ Frontend integration tests passed")
        else:
            print("  ❌ Frontend integration tests failed")
            print(f"     {output[:200]}...")
            
        return passed
    
    def test_production_readiness(self) -> bool:
        """Test production readiness."""
        print("🧪 Testing Production Readiness...")
        
        test_file = self.backend_dir / "test_production_readiness.py"
        if not test_file.exists():
            print("  ❌ Production readiness test file not found")
            self.results['production_readiness'] = {'passed': False, 'error': 'Test file missing'}
            return False
            
        passed, output = self.run_test_file(test_file, "Production readiness validation")
        
        self.results['production_readiness'] = {
            'passed': passed,
            'output': output
        }
        
        if passed:
            print("  ✅ Production readiness tests passed")
        else:
            print("  ❌ Production readiness tests failed")
            print(f"     {output[:200]}...")
            
        return passed
    
    def test_file_existence(self) -> bool:
        """Test that all required files exist."""
        print("🧪 Testing Required Files Existence...")
        
        required_files = [
            # Database
            "migrations/001_add_collaboration_tables.sql",
            "migrations/002_add_cancellation_rate_limiting.sql",
            "collaboration_service.py",
            "collaboration_api.py",
            "email_templates.py",
            "main_with_collaboration.py",
            
            # Frontend
            "../sentense-app/src/hooks/usePartnership.ts",
            "../sentense-app/src/components/collaboration/PartnershipCard.tsx",
            "../sentense-app/src/components/analysis/WordPoolSelector.tsx",
            "../sentense-app/src/pages/dashboard/Partnership.tsx",
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.backend_dir / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            print("  ❌ Missing required files:")
            for file in missing_files:
                print(f"     - {file}")
            self.results['file_existence'] = {
                'passed': False,
                'missing_files': missing_files
            }
            return False
        else:
            print("  ✅ All required files exist")
            self.results['file_existence'] = {'passed': True}
            return True
    
    def test_qstats_integration(self) -> bool:
        """Test qstats collaboration metrics integration."""
        print("🧪 Testing QStats Integration...")
        
        try:
            # Test collaboration metrics display
            process = subprocess.run(
                [sys.executable, "../scripts/qstats_demo", "collaboration"],
                cwd=self.backend_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if process.returncode == 0 and "Writing Partnership Metrics" in process.stdout:
                print("  ✅ QStats collaboration metrics working")
                self.results['qstats_integration'] = {'passed': True}
                return True
            else:
                print("  ❌ QStats collaboration metrics failed")
                print(f"     {process.stderr[:200] if process.stderr else process.stdout[:200]}...")
                self.results['qstats_integration'] = {
                    'passed': False,
                    'error': process.stderr or process.stdout
                }
                return False
                
        except Exception as e:
            print(f"  ❌ QStats test error: {e}")
            self.results['qstats_integration'] = {'passed': False, 'error': str(e)}
            return False
    
    def run_complete_suite(self) -> bool:
        """Run the complete test suite."""
        print("🚀 COLLABORATION SYSTEM TEST SUITE")
        print("=" * 60)
        print("Running comprehensive tests before deployment...")
        print()
        
        # Define test functions
        tests = [
            ("Required Files", self.test_file_existence),
            ("Core Functionality", self.test_collaboration_core_functionality),
            ("Rate Limiting", self.test_cancellation_rate_limiting),
            ("Cancellation E2E", self.test_cancellation_e2e),
            ("Frontend Integration", self.test_frontend_integration),
            ("Production Readiness", self.test_production_readiness),
            ("QStats Integration", self.test_qstats_integration),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        # Run each test
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 40)
            
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                print(f"  ❌ Test execution error: {e}")
                self.results[test_name] = {'passed': False, 'error': str(e)}
        
        # Print final results
        print("\n" + "=" * 60)
        print("📊 TEST SUITE RESULTS")
        print("=" * 60)
        
        for test_name, result in self.results.items():
            status = "✅ PASS" if result.get('passed', False) else "❌ FAIL"
            print(f"{status:>8} | {test_name}")
            if not result.get('passed', False) and 'error' in result:
                print(f"         └─ {result['error'][:100]}...")
        
        print("-" * 60)
        print(f"Total: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("\n🎉 🎉 🎉  ALL TESTS PASSED!  🎉 🎉 🎉")
            print("\n✅ Collaboration system is ready for deployment")
            print("✅ All components tested and verified")
            print("✅ Rate limiting working correctly")
            print("✅ Frontend integration complete")
            print("✅ Production readiness confirmed")
            print("✅ QStats metrics integrated")
            print("\n🚀 READY FOR GITHUB TEST ENVIRONMENT!")
            return True
        else:
            print(f"\n⚠️  {total_tests - passed_tests} test(s) failed")
            print("   Please fix failing tests before deployment")
            print("\n❌ NOT READY FOR DEPLOYMENT")
            return False


def main():
    """Run the collaboration test suite."""
    test_suite = CollaborationTestSuite()
    success = test_suite.run_complete_suite()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)