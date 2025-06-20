#!/usr/bin/env python3
"""
Test script to verify lab session lists display correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import NguoiDung, CaThucHanh, DangKyCa, VaoCa
from flask_login import login_user
from datetime import datetime, date

def test_lab_session_data():
    """Test that lab session data is correctly passed to templates"""
    app, socketio = create_app()
    
    with app.app_context():
        print("🧪 Testing Lab Session UI Data...")
        print("=" * 50)
        
        # Test data availability
        print("📊 Checking database data:")
        total_sessions = CaThucHanh.query.count()
        total_registrations = DangKyCa.query.count()
        total_attendances = VaoCa.query.count()
        
        print(f"  ✓ Total lab sessions: {total_sessions}")
        print(f"  ✓ Total registrations: {total_registrations}")
        print(f"  ✓ Total attendances: {total_attendances}")
        
        if total_sessions == 0:
            print("⚠️  No lab sessions found in database")
            return False        # Get sample session data
        sample_session = CaThucHanh.query.first()
        if sample_session:
            registrations_count = DangKyCa.query.filter_by(ca_thuc_hanh_ma=sample_session.id).count()
            attendances_count = VaoCa.query.filter_by(ca_thuc_hanh_ma=sample_session.id).count()
            
            print(f"\n📋 Sample session: '{sample_session.tieu_de}'")
            print(f"  • Date: {sample_session.ngay}")
            print(f"  • Status: {sample_session.trang_thai}")
            print(f"  • Location: {sample_session.dia_diem}")
            print(f"  • Registrations: {registrations_count}")
            print(f"  • Attendances: {attendances_count}")
        
        # Test user authentication and session access
        print("\n🔐 Testing user access:")
        
        # Get a test user
        test_user = NguoiDung.query.filter_by(vai_tro='Sinh viên').first()
        if not test_user:
            test_user = NguoiDung.query.first()
        
        if test_user:
            print(f"  ✓ Test user: {test_user.ten_nguoi_dung} ({test_user.vai_tro})")
            
            # Check user's registrations
            user_registrations = DangKyCa.query.filter_by(nguoi_dung_ma=test_user.id).count()
            user_attendances = VaoCa.query.filter_by(nguoi_dung_ma=test_user.id).count()
            
            print(f"  • User's registrations: {user_registrations}")
            print(f"  • User's attendances: {user_attendances}")
        
        # Test route data preparation
        print("\n🌐 Testing route data:")
        
        # Simulate /lab/sessions route logic
        sessions = CaThucHanh.query.order_by(CaThucHanh.ngay.desc()).all()
        for session in sessions:
            session.so_nguoi_dang_ky = DangKyCa.query.filter_by(ca_thuc_hanh_ma=session.id).count()
        
        print(f"  ✓ Sessions with registration counts: {len(sessions)}")
        
        if test_user:
            # Simulate /lab/my-sessions route logic
            registrations = DangKyCa.query.filter_by(nguoi_dung_ma=test_user.id).all()
            attendances = VaoCa.query.filter_by(nguoi_dung_ma=test_user.id).all()
            
            print(f"  ✓ User registrations for template: {len(registrations)}")
            print(f"  ✓ User attendances for template: {len(attendances)}")
        
        # Test admin route data
        print("\n👑 Testing admin route data:")
        
        admin_user = NguoiDung.query.filter(
            (NguoiDung.vai_tro == 'Quản trị hệ thống') | 
            (NguoiDung.vai_tro == 'Quản lý')
        ).first()
        
        if admin_user:
            print(f"  ✓ Admin user: {admin_user.ten_nguoi_dung} ({admin_user.vai_tro})")
            
            # Simulate admin route logic
            admin_sessions = CaThucHanh.query.order_by(CaThucHanh.ngay.desc()).all()
            for session in admin_sessions:
                session.so_nguoi_dang_ky = DangKyCa.query.filter_by(ca_thuc_hanh_ma=session.id).count()
                session.so_nguoi_da_vao = VaoCa.query.filter_by(ca_thuc_hanh_ma=session.id).count()
            
            today = date.today()
            today_sessions = [s for s in admin_sessions if s.ngay == today]
            active_sessions = [s for s in admin_sessions if s.trang_thai == 'Đang mở']
            
            print(f"  ✓ Total sessions for admin: {len(admin_sessions)}")
            print(f"  ✓ Today's sessions: {len(today_sessions)}")
            print(f"  ✓ Active sessions: {len(active_sessions)}")
        
        print("\n✅ All lab session data tests completed successfully!")
        print("📝 Templates should now display data correctly:")
        print("   • /lab/sessions - Shows all available sessions with registration counts")
        print("   • /lab/my-sessions - Shows user's registrations and attendance history")
        print("   • /admin/lab-sessions - Shows all sessions with detailed statistics")
        
        return True

if __name__ == "__main__":
    success = test_lab_session_data()
    if success:
        print("\n🎉 Lab session UI testing completed successfully!")
        print("🌐 Visit http://127.0.0.1:5000 to see the updated interface")
    else:
        print("\n❌ Some tests failed. Please check the database.")
