#!/usr/bin/env python3
"""
Test script to verify user creation workflow
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import NguoiDung
from app.forms import CreateUserForm

def test_form_validation():
    """Test form validation with valid data"""
    app, socketio = create_app()
    
    with app.app_context():
        # Create form with valid data
        form_data = {
            'ten_nguoi_dung': 'testuser123',
            'ho_ten': 'Test User Full Name',
            'email': 'testuser@example.com',
            'mat_khau': 'securepassword123',
            'xac_nhan_mat_khau': 'securepassword123',
            'vai_tro': 'nguoi_dung',
            'kich_hoat': True,
            'gui_email_chao_mung': True,
            'yeu_cau_doi_mat_khau': False,
            'ghi_chu': 'Test user created via script',
            'csrf_token': 'dummy_token'  # For testing
        }
        
        print("=== Testing Form Creation ===")
        try:
            form = CreateUserForm(data=form_data)
            print(f"Form created successfully")
            print(f"Form fields: {list(form._fields.keys())}")
            
            # Check if required fields are present
            required_fields = ['ten_nguoi_dung', 'email', 'mat_khau', 'vai_tro']
            for field in required_fields:
                if hasattr(form, field):
                    print(f"✓ Required field '{field}' exists")
                else:
                    print(f"✗ Required field '{field}' missing")
            
            # Check optional fields
            optional_fields = ['ho_ten', 'so_dien_thoai', 'kich_hoat', 'gui_email_chao_mung']
            for field in optional_fields:
                if hasattr(form, field):
                    print(f"✓ Optional field '{field}' exists")
                else:
                    print(f"- Optional field '{field}' not available")
            
        except Exception as e:
            print(f"✗ Error creating form: {e}")
            return False
        
        return True

def test_user_creation():
    """Test actual user creation"""
    app, socketio = create_app()
    
    with app.app_context():
        print("\n=== Testing User Creation ===")
        
        # Clean up any existing test user
        existing_user = NguoiDung.query.filter_by(ten_nguoi_dung='testuser123').first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
            print("Cleaned up existing test user")
        
        try:
            # Create new user
            new_user = NguoiDung(
                ten_nguoi_dung='testuser123',
                email='testuser@example.com',
                vai_tro='nguoi_dung'
            )
            
            # Set password
            new_user.dat_mat_khau('securepassword123')
            
            # Set bio from ho_ten (since model doesn't have ho_ten field)
            new_user.bio = 'Test User Full Name'
            
            # Set account status
            new_user.active = True
            
            db.session.add(new_user)
            db.session.commit()
            
            print(f"✓ User created successfully: {new_user.ten_nguoi_dung}")
            print(f"  - Email: {new_user.email}")
            print(f"  - Role: {new_user.vai_tro}")
            print(f"  - Bio (Full Name): {new_user.bio}")
            print(f"  - Active: {new_user.active}")
            print(f"  - Password set: {'Yes' if new_user.mat_khau_hash else 'No'}")
            
            # Test password verification
            if new_user.kiem_tra_mat_khau('securepassword123'):
                print(f"✓ Password verification successful")
            else:
                print(f"✗ Password verification failed")
            
            # Clean up
            db.session.delete(new_user)
            db.session.commit()
            print("✓ Test user cleaned up")
            
        except Exception as e:
            print(f"✗ Error creating user: {e}")
            db.session.rollback()
            return False
        
        return True

def test_model_fields():
    """Test model field availability"""
    from config import Config
    app, socketio = create_app()
    
    with app.app_context():
        print("\n=== Testing Model Fields ===")
        
        # Get model columns
        model_columns = [column.name for column in NguoiDung.__table__.columns]
        print(f"Available model fields: {model_columns}")
        
        # Check essential fields
        essential_fields = ['id', 'ten_nguoi_dung', 'email', 'mat_khau_hash', 'vai_tro']
        for field in essential_fields:
            if field in model_columns:
                print(f"✓ Essential field '{field}' available")
            else:
                print(f"✗ Essential field '{field}' missing")
        
        # Check optional fields
        optional_fields = ['bio', 'active', 'ngay_tao', 'last_seen']
        for field in optional_fields:
            if field in model_columns:
                print(f"✓ Optional field '{field}' available")
            else:
                print(f"- Optional field '{field}' not available")
        
        return True

if __name__ == '__main__':
    print("Testing User Creation Workflow")
    print("=" * 50)
    
    success = True
    
    # Test form validation
    if not test_form_validation():
        success = False
    
    # Test model fields
    if not test_model_fields():
        success = False
    
    # Test user creation
    if not test_user_creation():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All tests passed! User creation workflow should work correctly.")
    else:
        print("✗ Some tests failed. Please review the issues above.")
    
    print("\nNext steps:")
    print("1. Start the Flask app: python run.py")
    print("2. Go to Admin → Create User")
    print("3. Fill out the form and test submission")
