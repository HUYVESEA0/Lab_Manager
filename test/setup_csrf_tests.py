#!/usr/bin/env python3
"""
CSRF Test Environment Setup
Sets up the environment for running CSRF tests
"""

import sys
import os
import subprocess
import json

def check_python_version():
    """Check Python version"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.8+ required.")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing requirements...")
    
    # Check if requirements.txt exists
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], check=True, capture_output=True, text=True)
        
        print("✅ Requirements installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        print(f"Error output: {e.stderr}")
        return False

def install_test_dependencies():
    """Install additional test dependencies"""
    print("\n🧪 Installing test dependencies...")
    
    test_packages = [
        'selenium==4.15.2',
        'webdriver-manager==4.0.1', 
        'chromedriver-autoinstaller==0.6.4',
        'pytest==7.4.3',
        'pytest-cov==4.1.0',
        'requests==2.31.0',
        'beautifulsoup4==4.12.2'
    ]
    
    success_count = 0
    for package in test_packages:
        try:
            print(f"Installing {package}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], check=True, capture_output=True, text=True)
            
            print(f"✅ {package} installed successfully")
            success_count += 1
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Failed to install {package}: {e}")
            print(f"Error output: {e.stderr}")
    
    print(f"\n📊 Test dependencies: {success_count}/{len(test_packages)} installed successfully")
    return success_count >= len(test_packages) * 0.8  # 80% success rate

def setup_chrome_driver():
    """Setup Chrome driver for Selenium tests"""
    print("\n🌐 Setting up Chrome driver...")
    
    try:
        # First try webdriver-manager approach
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Test Chrome driver installation
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(service=service, options=options)
        driver.quit()
        
        print("✅ Chrome driver installed and working with webdriver-manager")
        return True
        
    except Exception as webdriver_error:
        print(f"⚠️  webdriver-manager failed: {webdriver_error}")
        
        # Fallback to chromedriver-autoinstaller
        try:
            import chromedriver_autoinstaller
            chromedriver_autoinstaller.install()
            
            # Test with basic Chrome options
            from selenium import webdriver
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            
            driver = webdriver.Chrome(options=options)
            driver.quit()
            
            print("✅ Chrome driver installed with chromedriver-autoinstaller")
            return True
            
        except Exception as auto_error:
            print(f"⚠️  chromedriver-autoinstaller failed: {auto_error}")
            print("📝 Manual setup required:")
            print("   1. Download Chrome driver from https://chromedriver.chromium.org/")
            print("   2. Add to PATH or place in project directory")
            print("   3. Ensure Chrome browser is installed")
            return False

def create_test_config():
    """Create test configuration file"""
    print("\n⚙️  Creating test configuration...")
    
    config = {
        "test_server": {
            "host": "localhost",
            "port": 5001,
            "url": "http://localhost:5001"
        },
        "csrf_endpoints": [
            "/api/v1/csrf-token",
            "/csrf-token",
            "/admin/csrf-token",
            "/lab/csrf-token"
        ],
        "test_data": {
            "valid_test_data": "CSRF test data",
            "invalid_token": "invalid-fake-token-12345"
        },
        "timeouts": {
            "request_timeout": 30,
            "page_load_timeout": 10
        },
        "browser_options": {
            "headless": True,
            "no_sandbox": True,
            "disable_gpu": True
        }
    }
    
    try:
        with open('test/csrf_test_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Test configuration created: test/csrf_test_config.json")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test config: {e}")
        return False

def verify_app_structure():
    """Verify application structure"""
    print("\n🏗️  Verifying application structure...")
    
    required_files = [
        'app/__init__.py',
        'app/models.py',
        'app/api/csrf.py',
        'app/templates/base.html',
        'app/templates/csrf_test.html',
        'app/templates/csrf_demo.html',
        'app/templates/api_integration_demo.html'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing {len(missing_files)} required files")
        return False
    
    print("✅ All required files present")
    return True

def create_test_runner_script():
    """Create convenient test runner script"""
    print("\n📜 Creating test runner script...")
    
    if os.name == 'nt':  # Windows
        script_content = """@echo off
echo Starting CSRF Test Suite...
python test/run_all_csrf_tests.py --html %*
echo.
echo Test completed. Check generated HTML report for details.
pause
"""
        script_file = 'run_csrf_tests.bat'
    else:  # Unix/Linux/Mac
        script_content = """#!/bin/bash
echo "Starting CSRF Test Suite..."
python3 test/run_all_csrf_tests.py --html "$@"
echo ""
echo "Test completed. Check generated HTML report for details."
"""
        script_file = 'run_csrf_tests.sh'
    
    try:
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        # Make executable on Unix systems
        if os.name != 'nt':
            os.chmod(script_file, 0o755)
        
        print(f"✅ Test runner script created: {script_file}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test runner script: {e}")
        return False

def main():
    """Main setup function"""
    print("🛡️  CSRF Test Environment Setup")
    print("=" * 50)
    
    success_count = 0
    total_steps = 7
    
    # Step 1: Check Python version
    if check_python_version():
        success_count += 1
    
    # Step 2: Install requirements
    if install_requirements():
        success_count += 1
    
    # Step 3: Install test dependencies
    install_test_dependencies()  # Optional
    success_count += 1
    
    # Step 4: Setup Chrome driver
    if setup_chrome_driver():
        success_count += 1
    else:
        success_count += 0.5  # Partial credit
    
    # Step 5: Create test directories
    os.makedirs('test', exist_ok=True)
    print("✅ Test directory created/verified")
    success_count += 1
    
    # Step 6: Create test config
    if create_test_config():
        success_count += 1
    
    # Step 7: Verify app structure
    if verify_app_structure():
        success_count += 1
    
    # Step 8: Create test runner script
    if create_test_runner_script():
        success_count += 1
    
    # Summary
    print(f"\n{'='*50}")
    print("SETUP SUMMARY")
    print(f"{'='*50}")
    
    success_rate = (success_count / total_steps) * 100
    print(f"Setup Progress: {success_count}/{total_steps} steps completed ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Start your Flask application: python run.py")
        print("2. Run CSRF tests: python test/run_all_csrf_tests.py --html")
        print("3. Or use the runner script created above")
        print("4. Check generated HTML report for detailed results")
        
        return True
    else:
        print("⚠️  Setup completed with some issues")
        print("Some features may not work correctly")
        print("Check error messages above and resolve issues")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
