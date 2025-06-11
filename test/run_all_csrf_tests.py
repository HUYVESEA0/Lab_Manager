#!/usr/bin/env python3
"""
Comprehensive CSRF Test Suite Runner
Runs all CSRF tests and generates detailed reports
"""

import sys
import os
import subprocess
import json
import time
from datetime import datetime
import argparse

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_command(command, description):
    """Run a command and capture output"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Exit Code: {result.returncode}")
        print(f"Duration: {duration:.2f} seconds")
        
        if result.stdout:
            print(f"\nSTDOUT:\n{result.stdout}")
        
        if result.stderr:
            print(f"\nSTDERR:\n{result.stderr}")
        
        return {
            'command': command,
            'description': description,
            'exit_code': result.returncode,
            'duration': duration,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0
        }
        
    except subprocess.TimeoutExpired:
        print(f"❌ Command timed out after 5 minutes")
        return {
            'command': command,
            'description': description,
            'exit_code': -1,
            'duration': 300,
            'stdout': '',
            'stderr': 'Command timed out',
            'success': False
        }
    except Exception as e:
        print(f"❌ Error running command: {str(e)}")
        return {
            'command': command,
            'description': description,
            'exit_code': -1,
            'duration': 0,
            'stdout': '',
            'stderr': str(e),
            'success': False
        }

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    dependencies = []
    
    # Check Python modules
    python_modules = [
        ('flask', 'Flask web framework'),
        ('flask_wtf', 'Flask-WTF for CSRF protection'),
        ('requests', 'HTTP library for testing'),
        ('selenium', 'Browser automation (optional)'),
    ]
    
    for module, description in python_modules:
        try:
            __import__(module)
            dependencies.append({
                'name': module,
                'description': description,
                'available': True,
                'type': 'python'
            })
            print(f"✅ {module}: Available")
        except ImportError:
            dependencies.append({
                'name': module,
                'description': description,
                'available': False,
                'type': 'python'
            })
            print(f"❌ {module}: Not available")
      # Check Chrome driver for Selenium tests
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Try with webdriver-manager first
        try:
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except:
            # Fallback to default Chrome driver
            driver = webdriver.Chrome(options=chrome_options)
        
        driver.quit()
        
        dependencies.append({
            'name': 'chromedriver',
            'description': 'Chrome WebDriver for browser tests',
            'available': True,
            'type': 'system'
        })
        print("✅ Chrome WebDriver: Available")
    except Exception as e:
        dependencies.append({
            'name': 'chromedriver',
            'description': 'Chrome WebDriver for browser tests',
            'available': False,
            'type': 'system'
        })
        print(f"❌ Chrome WebDriver: Not available - {str(e)}")
        print("   💡 Install with: python install_csrf_deps.py")
    
    return dependencies

def run_all_tests(server_url="http://localhost:5000", verbose=False):
    """Run all CSRF tests"""
    
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'server_url': server_url,
        'dependencies': check_dependencies(),
        'tests': []
    }
    
    # Define test commands
    test_commands = [
        {
            'command': f'python test/csrf_unit_tests.py',
            'description': 'CSRF Unit Tests',
            'required': True
        },
        {
            'command': f'python test/csrf_system_test.py {server_url}',
            'description': 'CSRF System Integration Tests',
            'required': True
        },
        {
            'command': f'python test/csrf_integration_tests.py',
            'description': 'CSRF Browser Integration Tests',
            'required': False  # Optional because requires Chrome driver
        }
    ]
    
    print(f"\n🚀 Starting comprehensive CSRF test suite")
    print(f"Server URL: {server_url}")
    print(f"Test time: {test_results['timestamp']}")
    
    # Run each test
    for test_config in test_commands:
        result = run_command(test_config['command'], test_config['description'])
        result['required'] = test_config['required']
        test_results['tests'].append(result)
    
    # Generate summary
    print(f"\n{'='*80}")
    print("COMPREHENSIVE TEST SUITE SUMMARY")
    print(f"{'='*80}")
    
    total_tests = len(test_results['tests'])
    successful_tests = sum(1 for test in test_results['tests'] if test['success'])
    failed_tests = total_tests - successful_tests
    required_tests = sum(1 for test in test_results['tests'] if test['required'])
    successful_required = sum(1 for test in test_results['tests'] if test['required'] and test['success'])
    
    print(f"Total Tests Run: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Required Tests: {required_tests}")
    print(f"Required Successful: {successful_required}")
    
    # Test details
    print(f"\nDETAILED RESULTS:")
    for i, test in enumerate(test_results['tests'], 1):
        status_symbol = "✅" if test['success'] else "❌"
        required_text = " (REQUIRED)" if test['required'] else " (OPTIONAL)"
        print(f"{i}. {status_symbol} {test['description']}{required_text}")
        print(f"   Duration: {test['duration']:.2f}s, Exit Code: {test['exit_code']}")
        
        if not test['success'] and verbose:
            print(f"   Error: {test['stderr']}")
    
    # Overall status
    overall_success = successful_required == required_tests
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    required_success_rate = (successful_required / required_tests * 100) if required_tests > 0 else 0
    
    print(f"\nOVERALL STATUS:")
    print(f"Success Rate: {success_rate:.1f}% ({successful_tests}/{total_tests})")
    print(f"Required Success Rate: {required_success_rate:.1f}% ({successful_required}/{required_tests})")
    
    if overall_success:
        print("🎉 All required tests passed! CSRF system is working correctly.")
        test_results['overall_status'] = 'PASS'
    else:
        print("❌ Some required tests failed. CSRF system has issues.")
        test_results['overall_status'] = 'FAIL'
    
    # Dependency status
    print(f"\nDEPENDENCY STATUS:")
    for dep in test_results['dependencies']:
        status = "✅" if dep['available'] else "❌"
        print(f"{status} {dep['name']}: {dep['description']}")
    
    # Save detailed results
    results_file = f"csrf-test-results-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    
    try:
        with open(results_file, 'w') as f:
            json.dump(test_results, f, indent=2)
        print(f"\n📄 Detailed results saved to: {results_file}")
    except Exception as e:
        print(f"\n⚠️  Could not save results file: {str(e)}")
    
    return test_results

def generate_html_report(test_results):
    """Generate an HTML report"""
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CSRF Test Results</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
            .summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 20px; }
            .stat-card { background: white; border: 1px solid #dee2e6; padding: 15px; border-radius: 5px; text-align: center; }
            .stat-number { font-size: 2em; font-weight: bold; color: #007bff; }
            .test-item { background: white; border: 1px solid #dee2e6; margin: 10px 0; padding: 15px; border-radius: 5px; }
            .test-success { border-left: 4px solid #28a745; }
            .test-failed { border-left: 4px solid #dc3545; }
            .test-optional { opacity: 0.8; }
            .dependency-list { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
            .dependency-item { padding: 10px; border: 1px solid #dee2e6; border-radius: 3px; }
            .available { background: #d4edda; }
            .unavailable { background: #f8d7da; }
            pre { background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🛡️ CSRF System Test Results</h1>
            <p><strong>Test Time:</strong> {timestamp}</p>
            <p><strong>Server URL:</strong> {server_url}</p>
            <p><strong>Overall Status:</strong> 
                <span style="color: {status_color}; font-weight: bold;">{overall_status}</span>
            </p>
        </div>
        
        <div class="summary">
            <div class="stat-card">
                <div class="stat-number">{total_tests}</div>
                <div>Total Tests</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: #28a745;">{successful_tests}</div>
                <div>Successful</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" style="color: #dc3545;">{failed_tests}</div>
                <div>Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{success_rate:.1f}%</div>
                <div>Success Rate</div>
            </div>
        </div>
        
        <h2>Test Results</h2>
        {test_results_html}
        
        <h2>Dependencies</h2>
        <div class="dependency-list">
            {dependencies_html}
        </div>
    </body>
    </html>
    """
    
    # Calculate statistics
    total_tests = len(test_results['tests'])
    successful_tests = sum(1 for test in test_results['tests'] if test['success'])
    failed_tests = total_tests - successful_tests
    success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
    
    # Generate test results HTML
    test_results_html = ""
    for test in test_results['tests']:
        status_class = "test-success" if test['success'] else "test-failed"
        if not test['required']:
            status_class += " test-optional"
        
        status_symbol = "✅" if test['success'] else "❌"
        required_text = " (REQUIRED)" if test['required'] else " (OPTIONAL)"
        
        test_results_html += f"""
        <div class="test-item {status_class}">
            <h3>{status_symbol} {test['description']}{required_text}</h3>
            <p><strong>Command:</strong> <code>{test['command']}</code></p>
            <p><strong>Duration:</strong> {test['duration']:.2f}s | 
               <strong>Exit Code:</strong> {test['exit_code']}</p>
            {f'<pre>{test["stderr"]}</pre>' if test['stderr'] and not test['success'] else ''}
        </div>
        """
    
    # Generate dependencies HTML
    dependencies_html = ""
    for dep in test_results['dependencies']:
        status_class = "available" if dep['available'] else "unavailable"
        status_symbol = "✅" if dep['available'] else "❌"
        
        dependencies_html += f"""
        <div class="dependency-item {status_class}">
            <strong>{status_symbol} {dep['name']}</strong><br>
            <small>{dep['description']}</small>
        </div>
        """
    
    # Fill template
    html_content = html_template.format(
        timestamp=test_results['timestamp'],
        server_url=test_results['server_url'],
        overall_status=test_results['overall_status'],
        status_color="#28a745" if test_results['overall_status'] == 'PASS' else "#dc3545",
        total_tests=total_tests,
        successful_tests=successful_tests,
        failed_tests=failed_tests,
        success_rate=success_rate,
        test_results_html=test_results_html,
        dependencies_html=dependencies_html
    )
    
    # Save HTML report
    html_file = f"csrf-test-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.html"
    
    try:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"📊 HTML report generated: {html_file}")
        return html_file
    except Exception as e:
        print(f"⚠️  Could not generate HTML report: {str(e)}")
        return None

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Run comprehensive CSRF test suite')
    parser.add_argument('--server', default='http://localhost:5000', 
                       help='Server URL to test against (default: http://localhost:5000)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--html', action='store_true',
                       help='Generate HTML report')
    
    args = parser.parse_args()
    
    print("🛡️  CSRF Test Suite Runner")
    print("=" * 50)
    
    # Run tests
    results = run_all_tests(args.server, args.verbose)
    
    # Generate HTML report if requested
    if args.html:
        generate_html_report(results)
    
    # Exit with appropriate code
    sys.exit(0 if results['overall_status'] == 'PASS' else 1)

if __name__ == "__main__":
    main()
