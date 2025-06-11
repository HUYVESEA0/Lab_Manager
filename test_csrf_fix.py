#!/usr/bin/env python3
"""
Quick Test - CSRF Configuration Fix
Tests that the CSRF issue has been resolved
"""

import os
import sys
from dotenv import load_dotenv

def test_environment_loading():
    """Test environment variable loading"""
    print("🔧 Testing environment variable loading...")
    
    # Load environment variables
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✅ .env file found and loaded: {env_path}")
    else:
        print("❌ .env file not found")
        return False
    
    # Check SECRET_KEY
    secret_key = os.getenv('SECRET_KEY')
    if secret_key and len(secret_key) > 10:
        print(f"✅ SECRET_KEY loaded: {secret_key[:20]}...")
        return True
    else:
        print("❌ SECRET_KEY not found or too short")
        return False

def test_config_class():
    """Test configuration class"""
    print("\n⚙️  Testing configuration class...")
    
    try:
        from config import Config
        
        if hasattr(Config, 'SECRET_KEY') and Config.SECRET_KEY:
            print(f"✅ Config.SECRET_KEY: {Config.SECRET_KEY[:20]}...")
        else:
            print("❌ Config.SECRET_KEY not found")
            return False
            
        if hasattr(Config, 'WTF_CSRF_ENABLED'):
            print(f"✅ Config.WTF_CSRF_ENABLED: {Config.WTF_CSRF_ENABLED}")
        else:
            print("❌ Config.WTF_CSRF_ENABLED not found")
            
        return True
        
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False

def test_app_creation():
    """Test Flask app creation"""
    print("\n🚀 Testing Flask app creation...")
    
    try:
        from run import app
        
        if app:
            print("✅ Flask app created successfully")
        else:
            print("❌ Flask app creation failed")
            return False
            
        # Check app config
        secret_key = app.config.get('SECRET_KEY')
        if secret_key and len(secret_key) > 10:
            print(f"✅ App SECRET_KEY configured: {secret_key[:20]}...")
        else:
            print("❌ App SECRET_KEY not configured properly")
            return False
            
        csrf_enabled = app.config.get('WTF_CSRF_ENABLED')
        print(f"✅ App CSRF protection: {'Enabled' if csrf_enabled else 'Disabled'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating app: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_csrf_forms():
    """Test CSRF form creation"""
    print("\n📝 Testing CSRF form creation...")
    
    try:
        from app.forms import LoginForm
        
        # This will only work in app context
        from run import app
        with app.app_context():
            form = LoginForm()
            if hasattr(form, 'csrf_token'):
                print("✅ LoginForm with CSRF token created successfully")
                return True
            else:
                print("❌ LoginForm CSRF token not found")
                return False
                
    except Exception as e:
        print(f"❌ Error creating form: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("CSRF CONFIGURATION FIX - VERIFICATION TEST")
    print("=" * 60)
    
    tests = [
        ("Environment Loading", test_environment_loading),
        ("Configuration Class", test_config_class),
        ("Flask App Creation", test_app_creation),
        ("CSRF Forms", test_csrf_forms),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! CSRF issue has been resolved.")
        print("\n💡 You can now run the application with:")
        print("   python run.py")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
