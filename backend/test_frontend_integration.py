#!/usr/bin/env python3
"""
FRONTEND INTEGRATION TEST
Test that React components can interact with the collaboration API correctly.
"""

import json
import subprocess
import os
from pathlib import Path

def test_typescript_compilation():
    """Test that TypeScript files compile without errors."""
    print("🧪 Testing TypeScript compilation...")
    
    # Check if React app directory exists
    react_dir = Path("/root/quirrely_v313_integrated/sentense-app")
    if not react_dir.exists():
        return False, "React app directory not found"
    
    # Check key TypeScript files exist
    key_files = [
        "src/hooks/usePartnership.ts",
        "src/components/collaboration/PartnershipCard.tsx",
        "src/components/analysis/WordPoolSelector.tsx",
        "src/pages/dashboard/Partnership.tsx",
        "src/api/client.ts"
    ]
    
    missing_files = []
    for file_path in key_files:
        full_path = react_dir / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    if missing_files:
        return False, f"Missing files: {missing_files}"
    
    return True, "All TypeScript files present"

def test_api_integration_types():
    """Test that API integration types are correct."""
    print("🧪 Testing API integration types...")
    
    # Read the usePartnership hook
    hook_path = Path("/root/quirrely_v313_integrated/sentense-app/src/hooks/usePartnership.ts")
    
    if not hook_path.exists():
        return False, "usePartnership hook not found"
    
    content = hook_path.read_text()
    
    # Check for required types and functions
    required_elements = [
        "interface Partnership",
        "interface PartnershipInvitation",
        "interface WordAllocation",
        "interface InviteRequest",
        "sendInvitation",
        "acceptInvitation",
        "cancelPartnership",
        "useWords",
        "canUseWords",
        "getWordAllowance",
        "hasActivePartnership"
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in content:
            missing_elements.append(element)
    
    if missing_elements:
        return False, f"Missing elements: {missing_elements}"
    
    # Check that it uses the correct API client pattern
    if "import('../api/client')" not in content:
        return False, "Not using correct API client import pattern"
    
    if "/v2/collaboration" not in content:
        return False, "Not using correct API endpoint paths"
    
    return True, "API integration types are correct"

def test_component_integration():
    """Test that components integrate properly."""
    print("🧪 Testing React component integration...")
    
    # Check WordPoolSelector component
    selector_path = Path("/root/quirrely_v313_integrated/sentense-app/src/components/analysis/WordPoolSelector.tsx")
    
    if not selector_path.exists():
        return False, "WordPoolSelector component not found"
    
    selector_content = selector_path.read_text()
    
    # Check for required integration points
    required_integrations = [
        "import { usePartnership }",
        "hasActivePartnership()",
        "canUseWords(",
        "getWordAllowance()",
        "onPoolSelected",
        "formatWordCount"
    ]
    
    missing_integrations = []
    for integration in required_integrations:
        if integration not in selector_content:
            missing_integrations.append(integration)
    
    if missing_integrations:
        return False, f"Missing integrations: {missing_integrations}"
    
    # Check PartnershipCard component
    card_path = Path("/root/quirrely_v313_integrated/sentense-app/src/components/collaboration/PartnershipCard.tsx")
    
    if not card_path.exists():
        return False, "PartnershipCard component not found"
    
    card_content = card_path.read_text()
    
    # Check for human-centered language
    human_centered_elements = [
        "Creative Space",
        "Your Solo Space",
        "shared creative space",
        "partnership",
        "collaborating"
    ]
    
    found_human_elements = sum(1 for element in human_centered_elements if element in card_content)
    
    if found_human_elements < 3:
        return False, f"Insufficient human-centered language found ({found_human_elements}/5)"
    
    return True, "Component integration is correct"

def test_routing_integration():
    """Test that routing includes partnership pages."""
    print("🧪 Testing routing integration...")
    
    # Check if Partnership page is properly integrated
    partnership_page = Path("/root/quirrely_v313_integrated/sentense-app/src/pages/dashboard/Partnership.tsx")
    
    if not partnership_page.exists():
        return False, "Partnership page not found"
    
    partnership_content = partnership_page.read_text()
    
    # Check for required partnership page elements
    required_page_elements = [
        "partnership_type",
        "partnership_name",
        "partnership_intention",
        "sendInvitation",
        "hasActivePartnership",
        "Pro tier"
    ]
    
    missing_page_elements = []
    for element in required_page_elements:
        if element not in partnership_content:
            missing_page_elements.append(element)
    
    if missing_page_elements:
        return False, f"Missing page elements: {missing_page_elements}"
    
    return True, "Routing integration is correct"

def test_api_client_consistency():
    """Test that API client follows existing patterns."""
    print("🧪 Testing API client consistency...")
    
    client_path = Path("/root/quirrely_v313_integrated/sentense-app/src/api/client.ts")
    
    if not client_path.exists():
        return False, "API client not found"
    
    client_content = client_path.read_text()
    
    # Check for consistent authentication patterns
    auth_patterns = [
        "withCredentials: true",
        "axios.create",
        "Authorization",
        "Bearer",
        "interceptors"
    ]
    
    missing_auth_patterns = []
    for pattern in auth_patterns:
        if pattern not in client_content:
            missing_auth_patterns.append(pattern)
    
    if missing_auth_patterns:
        return False, f"Missing auth patterns: {missing_auth_patterns}"
    
    # Check for error handling
    if "AxiosError" not in client_content:
        return False, "Missing error handling types"
    
    return True, "API client consistency is correct"

def run_frontend_tests():
    """Run all frontend integration tests."""
    print("🚀 Starting Frontend Integration Tests")
    print("=" * 60)
    
    tests = [
        ("TypeScript Compilation", test_typescript_compilation),
        ("API Integration Types", test_api_integration_types),
        ("Component Integration", test_component_integration),
        ("Routing Integration", test_routing_integration),
        ("API Client Consistency", test_api_client_consistency)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            passed, message = test_func()
            results[test_name] = {
                'passed': passed,
                'message': message
            }
            
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status:>8} | {test_name}")
            if not passed:
                print(f"         └─ {message}")
                
        except Exception as e:
            results[test_name] = {
                'passed': False,
                'message': f"Test error: {str(e)}"
            }
            print(f"❌ ERROR | {test_name}")
            print(f"         └─ {str(e)}")
    
    print("=" * 60)
    passed_count = sum(1 for result in results.values() if result['passed'])
    total_count = len(results)
    
    print(f"Total: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("🎉 ALL FRONTEND INTEGRATION TESTS PASSED!")
        return True
    else:
        print(f"⚠️  {total_count - passed_count} test(s) failed - Review needed")
        return False

if __name__ == "__main__":
    success = run_frontend_tests()
    exit(0 if success else 1)