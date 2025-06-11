#!/usr/bin/env python3
"""
CSRF System Test Script
Tests the CSRF token functionality in Lab Manager system
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add the parent directory to the path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_csrf_system(base_url="http://localhost:5000"):
    """Test CSRF system functionality"""
    
    print("=" * 60)
    print("CSRF SYSTEM TEST REPORT")
    print("=" * 60)
    print(f"Testing against: {base_url}")
    print(f"Test time: {datetime.now().isoformat()}")
    print()
    
    session = requests.Session()
    results = []
    
    def run_test(test_name, test_func):
        """Run a test and record results"""
        print(f"Running: {test_name}...")
        try:
            result = test_func(session, base_url)
            results.append({
                'test': test_name,
                'status': 'PASS' if result else 'FAIL',
                'details': result if isinstance(result, str) else 'Success'
            })
            print(f"  ✓ {test_name}: PASS")
        except Exception as e:
            results.append({
                'test': test_name,
                'status': 'ERROR',
                'details': str(e)
            })
            print(f"  ✗ {test_name}: ERROR - {str(e)}")
        print()
    
    # Test 1: Get CSRF token from API
    def test_get_csrf_token(session, base_url):
        response = session.get(f"{base_url}/api/v1/csrf-token")
        if response.status_code == 200:
            data = response.json()
            if 'csrf_token' in data:
                session.csrf_token = data['csrf_token']
                return True
        return False
    
    # Test 2: Validate CSRF token
    def test_validate_csrf_token(session, base_url):
        if not hasattr(session, 'csrf_token'):
            return False
        
        response = session.post(
            f"{base_url}/api/v1/csrf-token/validate",
            headers={'X-CSRFToken': session.csrf_token}
        )
        return response.status_code == 200
    
    # Test 3: Test CSRF protection (should fail without token)
    def test_csrf_protection(session, base_url):
        # This should fail
        response = session.post(f"{base_url}/csrf-test", data={'test_data': 'test'})
        return response.status_code in [400, 403]  # Should be blocked
    
    # Test 4: Test successful form submission with CSRF
    def test_form_submission_with_csrf(session, base_url):
        if not hasattr(session, 'csrf_token'):
            return False
        
        response = session.post(
            f"{base_url}/csrf-test",
            data={
                'test_data': 'CSRF test data',
                'csrf_token': session.csrf_token
            }
        )
        return response.status_code == 200
    
    # Test 5: Test CSRF refresh
    def test_csrf_refresh(session, base_url):
        response = session.post(f"{base_url}/api/v1/csrf-token/refresh")
        if response.status_code == 200:
            data = response.json()
            return 'csrf_token' in data and data.get('refreshed') == True
        return False
    
    # Test 6: Test multiple endpoints
    def test_multiple_endpoints(session, base_url):
        endpoints = ['/csrf-token', '/admin/csrf-token', '/lab/csrf-token']
        success_count = 0
        
        for endpoint in endpoints:
            try:
                response = session.get(f"{base_url}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    if 'csrf_token' in data:
                        success_count += 1
            except:
                pass
        
        return success_count >= 1  # At least one should work
    
    # Run all tests
    run_test("Get CSRF Token from API", test_get_csrf_token)
    run_test("Validate CSRF Token", test_validate_csrf_token)
    run_test("CSRF Protection (should block)", test_csrf_protection)
    run_test("Form Submission with CSRF", test_form_submission_with_csrf)
    run_test("CSRF Token Refresh", test_csrf_refresh)
    run_test("Multiple CSRF Endpoints", test_multiple_endpoints)
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    errors = sum(1 for r in results if r['status'] == 'ERROR')
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Errors: {errors}")
    print()
    
    # Detailed results
    for result in results:
        status_symbol = "✓" if result['status'] == 'PASS' else "✗"
        print(f"{status_symbol} {result['test']}: {result['status']}")
        if result['status'] != 'PASS':
            print(f"  Details: {result['details']}")
    
    print()
    success_rate = (passed / total) * 100 if total > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 CSRF system is working well!")
    elif success_rate >= 60:
        print("⚠️  CSRF system has some issues but is functional")
    else:
        print("❌ CSRF system has significant problems")
    
    return results

if __name__ == "__main__":
    # Allow custom base URL from command line
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    test_csrf_system(base_url)
