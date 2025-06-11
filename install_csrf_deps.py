#!/usr/bin/env python3
"""
Install CSRF Test Dependencies
Quick installer for all testing dependencies
"""

import sys
import subprocess
import os

def run_pip_install(packages, description="packages"):
    """Install packages with pip"""
    print(f"\n📦 Installing {description}...")
    
    if isinstance(packages, str):
        packages = [packages]
    
    success_count = 0
    for package in packages:
        try:
            print(f"  Installing {package}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', package, '--upgrade'
            ], check=True, capture_output=True, text=True)
            
            print(f"  ✅ {package}")
            success_count += 1
            
        except subprocess.CalledProcessError as e:
            print(f"  ❌ {package} failed: {e}")
            if e.stderr:
                print(f"     Error: {e.stderr.strip()}")
    
    return success_count, len(packages)

def check_and_upgrade_pip():
    """Check and upgrade pip"""
    print("🔄 Checking pip version...")
    
    try:
        # Upgrade pip first
        subprocess.run([
            sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'
        ], check=True, capture_output=True, text=True)
        
        print("✅ pip upgraded successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Could not upgrade pip: {e}")
        return False

def install_base_requirements():
    """Install base requirements from requirements.txt"""
    print("\n📋 Installing base requirements...")
    
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], check=True, capture_output=True, text=True)
        
        print("✅ Base requirements installed")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install base requirements: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def install_testing_packages():
    """Install testing-specific packages"""
    testing_packages = [
        'pytest==7.4.3',
        'pytest-cov==4.1.0', 
        'pytest-mock==3.12.0',
        'requests==2.31.0'
    ]
    
    return run_pip_install(testing_packages, "testing packages")

def install_selenium_packages():
    """Install Selenium and WebDriver packages"""
    selenium_packages = [
        'selenium==4.15.2',
        'webdriver-manager==4.0.1',
        'chromedriver-autoinstaller==0.6.4'
    ]
    
    return run_pip_install(selenium_packages, "Selenium packages")

def install_optional_packages():
    """Install optional testing packages"""
    optional_packages = [
        'beautifulsoup4==4.12.2',
        'lxml==4.9.3',
        'coverage==7.3.2'
    ]
    
    return run_pip_install(optional_packages, "optional packages")

def verify_installation():
    """Verify key packages are installed correctly"""
    print("\n🔍 Verifying installation...")
    
    key_packages = [
        ('flask', 'Flask web framework'),
        ('selenium', 'Selenium WebDriver'),
        ('pytest', 'Testing framework'),
        ('requests', 'HTTP library')
    ]
    
    all_good = True
    for package, description in key_packages:
        try:
            __import__(package)
            print(f"✅ {package}: {description}")
        except ImportError:
            print(f"❌ {package}: {description} - NOT INSTALLED")
            all_good = False
    
    return all_good

def test_selenium_setup():
    """Test Selenium Chrome setup"""
    print("\n🌐 Testing Selenium Chrome setup...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        # Try with webdriver-manager first
        try:
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            service = Service(ChromeDriverManager().install())
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(service=service, options=options)
            driver.get("data:text/html,<html><body><h1>Test</h1></body></html>")
            title = driver.title
            driver.quit()
            
            print("✅ Selenium with webdriver-manager working")
            return True
            
        except Exception as wm_error:
            print(f"⚠️  webdriver-manager failed: {wm_error}")
            
            # Fallback to chromedriver-autoinstaller
            try:
                import chromedriver_autoinstaller
                chromedriver_autoinstaller.install()
                
                options = Options()
                options.add_argument("--headless")
                driver = webdriver.Chrome(options=options)
                driver.get("data:text/html,<html><body><h1>Test</h1></body></html>")
                driver.quit()
                
                print("✅ Selenium with chromedriver-autoinstaller working")
                return True
                
            except Exception as ca_error:
                print(f"❌ chromedriver-autoinstaller failed: {ca_error}")
                return False
        
    except ImportError as e:
        print(f"❌ Selenium not available: {e}")
        return False

def main():
    """Main installation function"""
    print("🛡️  CSRF Test Dependencies Installer")
    print("=" * 50)
    
    success_counts = []
    
    # Step 1: Upgrade pip
    if check_and_upgrade_pip():
        success_counts.append(1)
    else:
        success_counts.append(0)
    
    # Step 2: Install base requirements
    if install_base_requirements():
        success_counts.append(1)
    else:
        success_counts.append(0)
    
    # Step 3: Install testing packages
    testing_success, testing_total = install_testing_packages()
    success_counts.append(testing_success / testing_total if testing_total > 0 else 0)
    
    # Step 4: Install Selenium packages
    selenium_success, selenium_total = install_selenium_packages()
    success_counts.append(selenium_success / selenium_total if selenium_total > 0 else 0)
    
    # Step 5: Install optional packages
    optional_success, optional_total = install_optional_packages()
    success_counts.append(optional_success / optional_total if optional_total > 0 else 0)
    
    # Step 6: Verify installation
    if verify_installation():
        success_counts.append(1)
    else:
        success_counts.append(0)
    
    # Step 7: Test Selenium
    if test_selenium_setup():
        success_counts.append(1)
    else:
        success_counts.append(0.5)  # Partial credit
    
    # Summary
    print(f"\n{'='*50}")
    print("INSTALLATION SUMMARY")
    print(f"{'='*50}")
    
    total_score = sum(success_counts)
    max_score = len(success_counts)
    success_rate = (total_score / max_score) * 100
    
    print(f"Overall Success Rate: {success_rate:.1f}%")
    print(f"Score: {total_score:.1f}/{max_score}")
    
    if success_rate >= 80:
        print("🎉 Installation completed successfully!")
        print("\n📋 Next steps:")
        print("1. Run tests: python test/run_all_csrf_tests.py --html")
        print("2. Or run individual tests:")
        print("   - python test/csrf_unit_tests.py")
        print("   - python test/csrf_integration_tests.py")
        print("3. Access demo pages after starting the app:")
        print("   - /csrf-demo")
        print("   - /api-integration-demo")
        
    elif success_rate >= 60:
        print("⚠️  Installation mostly successful with some issues")
        print("Some features may not work correctly")
        print("Check error messages above")
        
    else:
        print("❌ Installation had significant problems")
        print("Please review error messages and install missing packages manually")
    
    print(f"\n📝 Manual installation commands if needed:")
    print("pip install selenium webdriver-manager chromedriver-autoinstaller")
    print("pip install pytest pytest-cov requests beautifulsoup4")
    
    return success_rate >= 60

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
