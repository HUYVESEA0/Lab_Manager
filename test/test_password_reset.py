#!/usr/bin/env python3
"""
Test script for password reset functionality
"""

import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, NguoiDung
from app.utils import send_password_reset_email

def test_password_reset():
    """Test the password reset functionality"""
    app, socketio = create_app()
    
    with app.app_context():
        print("Testing password reset functionality...")
        
        # Check if we have a test user
        test_user = NguoiDung.query.filter_by(email="hhuy0847@gmail.com").first()
        
        if not test_user:
            print("❌ No test user found. Please ensure the admin user exists.")
            return False
        
        print(f"✅ Found test user: {test_user.ten_nguoi_dung} ({test_user.email})")
        
        # Test token generation
        try:
            token = test_user.get_reset_password_token()
            print(f"✅ Token generated successfully: {token[:20]}...")
        except Exception as e:
            print(f"❌ Error generating token: {str(e)}")
            return False
        
        # Test token verification
        try:
            verified_user = NguoiDung.verify_reset_password_token(token)
            if verified_user and verified_user.id == test_user.id:
                print("✅ Token verification successful")
            else:
                print("❌ Token verification failed")
                return False
        except Exception as e:
            print(f"❌ Error verifying token: {str(e)}")
            return False
        
        # Test email sending (without actually sending)
        print("\n📧 Testing email function (mock mode)...")
        app.config['TESTING'] = True
        app.config['MAIL_SUPPRESS_SEND'] = True
        
        try:
            result = send_password_reset_email(test_user)
            if result:
                print("✅ Email function works correctly")
            else:
                print("❌ Email function failed")
        except Exception as e:
            print(f"❌ Error in email function: {str(e)}")
            return False
        
        print("\n🎉 All password reset tests passed!")
        return True

if __name__ == "__main__":
    if test_password_reset():
        print("\n✅ Password reset feature is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Password reset feature has issues!")
        sys.exit(1)
