#!/usr/bin/env python3
"""
CSRF Integration Tests
Tests CSRF functionality in real browser-like scenarios
"""

import unittest
import sys
import os
import time
import threading

# Selenium imports with fallback handling
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Selenium not available: {e}")
    print("📝 Install with: pip install selenium webdriver-manager")
    SELENIUM_AVAILABLE = False
    
    # Create dummy classes to prevent import errors
    class Options:
        def add_argument(self, arg): pass
    class WebDriverException(Exception): pass
    class TimeoutException(Exception): pass

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import create_app
    from app.models import db
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

class CSRFIntegrationTest(unittest.TestCase):
    """Integration tests using Selenium for real browser testing"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test server and browser"""
        print("Setting up CSRF Integration Test environment...")
        
        # Start Flask app in test mode
        cls.app, cls.socketio = create_app()
        cls.app.config['TESTING'] = True
        cls.app.config['WTF_CSRF_ENABLED'] = True
        
        # Start server in background thread
        cls.server_thread = threading.Thread(
            target=lambda: cls.socketio.run(cls.app, port=5001, debug=False, use_reloader=False)
        )
        cls.server_thread.daemon = True
        cls.server_thread.start()
        
        # Wait for server to start
        time.sleep(2)
        
        # Set up Chrome driver
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Run in background
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            
            cls.driver = webdriver.Chrome(options=chrome_options)
            cls.driver.implicitly_wait(10)
            cls.base_url = "http://localhost:5001"
            
        except WebDriverException as e:
            print(f"Chrome driver not available: {e}")
            print("Skipping browser tests...")
            cls.driver = None
    
    @classmethod
    def tearDownClass(cls):
        """Clean up browser and server"""
        if hasattr(cls, 'driver') and cls.driver:
            cls.driver.quit()
    
    def setUp(self):
        """Set up individual test"""
        if not self.driver:
            self.skipTest("Chrome driver not available")
    
    def test_csrf_test_page_loads(self):
        """Test that CSRF test page loads correctly"""
        self.driver.get(f"{self.base_url}/csrf-test")
        
        # Wait for page to load
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "currentToken")))
        
        # Check page title
        self.assertIn("CSRF", self.driver.title)
        
        # Check that token field exists
        token_field = self.driver.find_element(By.ID, "currentToken")
        self.assertIsNotNone(token_field)
        
        print("✓ CSRF test page loads correctly")
    
    def test_csrf_token_display(self):
        """Test CSRF token is displayed on page"""
        self.driver.get(f"{self.base_url}/csrf-test")
        
        # Wait for token to be loaded
        wait = WebDriverWait(self.driver, 10)
        token_field = wait.until(EC.presence_of_element_located((By.ID, "currentToken")))
        
        # Check token is populated
        time.sleep(2)  # Wait for JavaScript to run
        token_value = token_field.get_attribute("value")
        
        self.assertNotEqual(token_value, "")
        self.assertNotEqual(token_value, "No token available")
        
        print(f"✓ CSRF token displayed: {token_value[:20]}...")
    
    def test_csrf_token_refresh(self):
        """Test CSRF token refresh functionality"""
        self.driver.get(f"{self.base_url}/csrf-test")
        
        # Wait for initial token
        wait = WebDriverWait(self.driver, 10)
        token_field = wait.until(EC.presence_of_element_located((By.ID, "currentToken")))
        time.sleep(2)
        
        initial_token = token_field.get_attribute("value")
        
        # Click refresh button
        refresh_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Refresh Token')]")
        refresh_button.click()
        
        # Wait for token to change
        time.sleep(3)
        new_token = token_field.get_attribute("value")
        
        self.assertNotEqual(initial_token, new_token)
        print(f"✓ CSRF token refreshed successfully")
    
    def test_form_submission_with_csrf(self):
        """Test form submission with CSRF token"""
        self.driver.get(f"{self.base_url}/csrf-test")
        
        # Wait for page to load
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "testForm")))
        
        # Fill form
        test_data_field = self.driver.find_element(By.ID, "testData")
        test_data_field.clear()
        test_data_field.send_keys("Integration test data")
        
        # Submit form
        submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
        submit_button.click()
        
        # Wait for results
        time.sleep(3)
        
        # Check test results area
        results_area = self.driver.find_element(By.ID, "testResults")
        results_text = results_area.text
        
        # Should contain some response
        self.assertNotEqual(results_text.strip(), "")
        print("✓ Form submission test completed")
    
    def test_api_requests(self):
        """Test API requests through browser"""
        self.driver.get(f"{self.base_url}/csrf-test")
        
        # Wait for page to load
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "testResults")))
        
        # Click API GET test
        get_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Test GET Request')]")
        get_button.click()
        
        time.sleep(2)
        
        # Click API POST test
        post_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Test POST Request')]")
        post_button.click()
        
        time.sleep(2)
        
        # Check results
        results_area = self.driver.find_element(By.ID, "testResults")
        results_text = results_area.text
        
        self.assertIn("Test", results_text)
        print("✓ API request tests completed")


class CSRFPerformanceTest(unittest.TestCase):
    """Performance tests for CSRF system"""
    
    def setUp(self):
        """Set up performance test"""
        self.app, self.socketio = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Clean up"""
        self.app_context.pop()
    
    def test_csrf_token_generation_performance(self):
        """Test CSRF token generation performance"""
        import time
        
        start_time = time.time()
        
        # Generate 100 tokens
        for _ in range(100):
            response = self.client.get('/api/v1/csrf-token')
            self.assertEqual(response.status_code, 200)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / 100
        
        print(f"✓ CSRF token generation: {avg_time*1000:.2f}ms average")
        self.assertLess(avg_time, 0.1)  # Should be less than 100ms per token
    
    def test_concurrent_csrf_requests(self):
        """Test concurrent CSRF token requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            start = time.time()
            response = self.client.get('/api/v1/csrf-token')
            end = time.time()
            results.append({
                'status': response.status_code,
                'time': end - start
            })
        
        # Create 10 concurrent threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Wait for all to complete
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # Check results
        successful = len([r for r in results if r['status'] == 200])
        avg_time = sum(r['time'] for r in results) / len(results)
        total_time = end_time - start_time
        
        print(f"✓ Concurrent CSRF requests: {successful}/10 successful")
        print(f"✓ Average response time: {avg_time*1000:.2f}ms")
        print(f"✓ Total time: {total_time:.2f}s")
        
        self.assertEqual(successful, 10)
        self.assertLess(total_time, 5)  # Should complete within 5 seconds


def run_integration_tests():
    """Run all integration tests"""
    print("=" * 70)
    print("CSRF INTEGRATION TESTS")
    print("=" * 70)
    
    # Check if Chrome driver is available
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        test_driver = webdriver.Chrome(options=chrome_options)
        test_driver.quit()
        browser_available = True
    except:
        browser_available = False
        print("⚠️  Chrome driver not available, skipping browser tests")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add performance tests (these don't need browser)
    suite.addTests(loader.loadTestsFromTestCase(CSRFPerformanceTest))
    
    # Add browser tests if available
    if browser_available:
        suite.addTests(loader.loadTestsFromTestCase(CSRFIntegrationTest))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
