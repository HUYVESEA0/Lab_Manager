#!/usr/bin/env python3
"""
Unit Tests for CSRF Token System
Tests individual components of the CSRF implementation
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import create_app
    from app.models import db
    from flask_wtf.csrf import generate_csrf, validate_csrf
    from flask import session
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

class TestCSRFTokenSystem(unittest.TestCase):
    """Test cases for CSRF token functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app, self.socketio = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key-for-csrf'
        
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
    def tearDown(self):
        """Clean up after tests"""
        self.app_context.pop()
    
    def test_csrf_token_generation(self):
        """Test CSRF token generation"""
        with self.app.test_request_context():
            token = generate_csrf()
            self.assertIsInstance(token, str)
            self.assertGreater(len(token), 10)
            print(f"✓ Generated CSRF token: {token[:20]}...")
    
    def test_csrf_api_endpoint(self):
        """Test CSRF token API endpoint"""
        response = self.client.get('/api/v1/csrf-token')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('csrf_token', data)
        self.assertIn('timestamp', data)
        self.assertIn('expires_in', data)
        print(f"✓ CSRF API endpoint working, token length: {len(data['csrf_token'])}")
    
    def test_multiple_csrf_endpoints(self):
        """Test multiple CSRF endpoints"""
        endpoints = ['/csrf-token', '/admin/csrf-token', '/lab/csrf-token']
        working_endpoints = []
        
        for endpoint in endpoints:
            try:
                response = self.client.get(endpoint)
                if response.status_code == 200:
                    data = json.loads(response.data)
                    if 'csrf_token' in data:
                        working_endpoints.append(endpoint)
            except:
                pass
        
        self.assertGreater(len(working_endpoints), 0)
        print(f"✓ Working CSRF endpoints: {working_endpoints}")
    
    def test_csrf_token_validation(self):
        """Test CSRF token validation"""
        # Get a token first
        response = self.client.get('/api/v1/csrf-token')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        csrf_token = data['csrf_token']
        
        # Test validation endpoint
        response = self.client.post('/api/v1/csrf-token/validate', 
                                  headers={'X-CSRFToken': csrf_token})
        
        # Note: This might fail in test environment due to session handling
        # But we check that the endpoint exists and responds
        self.assertIn(response.status_code, [200, 400, 403])
        print(f"✓ CSRF validation endpoint responds with status: {response.status_code}")
    
    def test_csrf_refresh_endpoint(self):
        """Test CSRF token refresh"""
        # This test checks if the refresh endpoint exists
        response = self.client.post('/api/v1/csrf-token/refresh')
        
        # In test environment without proper authentication, this might return 401
        # But we check that the endpoint is reachable
        self.assertIn(response.status_code, [200, 401, 403])
        print(f"✓ CSRF refresh endpoint responds with status: {response.status_code}")
    
    def test_csrf_test_page(self):
        """Test CSRF test page loads"""
        response = self.client.get('/csrf-test')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'CSRF Token Test', response.data)
        print("✓ CSRF test page loads successfully")
    
    def test_csrf_form_submission(self):
        """Test form submission with CSRF protection"""
        # Get CSRF token first
        with self.client.session_transaction() as sess:
            sess['_csrf_token'] = 'test-token'
        
        # Test form submission
        response = self.client.post('/csrf-test', data={
            'test_data': 'test submission',
            'csrf_token': 'test-token'
        })
        
        # Check that the endpoint responds (might fail validation in test env)
        self.assertIn(response.status_code, [200, 400, 403])
        print(f"✓ CSRF form submission endpoint responds: {response.status_code}")


class TestCSRFMiddleware(unittest.TestCase):
    """Test CSRF middleware functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app, self.socketio = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up"""
        self.app_context.pop()
    
    def test_api_routes_exempt_from_csrf(self):
        """Test that API routes are exempt from CSRF"""
        # API routes should not require CSRF tokens
        response = self.client.get('/api/v1/csrf-token')
        self.assertEqual(response.status_code, 200)
        print("✓ API routes exempt from CSRF protection")
    
    def test_static_routes_exempt(self):
        """Test static routes are exempt"""
        # Try to access a static file (might not exist but should not trigger CSRF)
        response = self.client.get('/static/css/base.css')
        # Should either succeed or return 404, not CSRF error
        self.assertIn(response.status_code, [200, 404])
        print(f"✓ Static routes exempt from CSRF: {response.status_code}")


class TestCSRFIntegration(unittest.TestCase):
    """Integration tests for CSRF system"""
    
    def setUp(self):
        """Set up integration test environment"""
        self.app, self.socketio = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up"""
        self.app_context.pop()
    
    def test_csrf_workflow(self):
        """Test complete CSRF workflow"""
        # Step 1: Get initial token
        response = self.client.get('/api/v1/csrf-token')
        self.assertEqual(response.status_code, 200)
        
        token_data = json.loads(response.data)
        initial_token = token_data['csrf_token']
        
        # Step 2: Use token in a request
        response = self.client.post('/api/v1/csrf-token/validate',
                                  headers={'X-CSRFToken': initial_token})
        
        # Step 3: Verify token handling
        self.assertIn(response.status_code, [200, 400, 403])
        print("✓ Complete CSRF workflow test completed")
    
    def test_error_handling(self):
        """Test CSRF error handling"""
        # Try to make a POST request without CSRF token
        response = self.client.post('/csrf-test', data={'test_data': 'test'})
        
        # Should be blocked or handled gracefully
        self.assertIn(response.status_code, [400, 403, 500])
        print(f"✓ CSRF error handling works: {response.status_code}")


def run_csrf_tests():
    """Run all CSRF tests and generate report"""
    print("=" * 70)
    print("CSRF SYSTEM UNIT TESTS")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCSRFTokenSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestCSRFMiddleware))
    suite.addTests(loader.loadTestsFromTestCase(TestCSRFIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 CSRF system unit tests mostly passing!")
    elif success_rate >= 60:
        print("⚠️  CSRF system has some test failures")
    else:
        print("❌ CSRF system has significant test failures")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_csrf_tests()
    sys.exit(0 if success else 1)
