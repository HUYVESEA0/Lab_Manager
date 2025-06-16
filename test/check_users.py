#!/usr/bin/env python3
"""
Script to check existing users in the database
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models import db, NguoiDung

def check_users():
    app, socketio = create_app()
    with app.app_context():
        users = NguoiDung.query.all()
        if users:
            print("Existing users:")
            for user in users:
                print(f"- Username: {user.ten_nguoi_dung}, Email: {user.email}, Role: {user.vai_tro}")
        else:
            print("No users found in database")
            # Create a sample user for testing
            sample_user = NguoiDung(
                ten_nguoi_dung="testuser",
                email="test@example.com",
                vai_tro="nguoi_dung"
            )
            sample_user.dat_mat_khau("password123")
            db.session.add(sample_user)
            db.session.commit()
            print("Created sample user: testuser / password123")

if __name__ == "__main__":
    check_users()
