import os
from .models import db, NguoiDung
from flask import current_app
from werkzeug.security import generate_password_hash

def init_sample_data():
    # Lấy thông tin từ biến môi trường
    admin_manager_username = os.getenv("SYSTEM_ADMIN_USERNAME", "HUYVIESEA")
    admin_manager_email = os.getenv("SYSTEM_ADMIN_EMAIL", "hhuy0847@gmail.com")
    admin_manager_password = os.getenv("SYSTEM_ADMIN_PASSWORD", "huyviesea@manager")

    admin_username = os.getenv("ADMIN_USERNAME", "ADMIN")
    admin_email = os.getenv("ADMIN_EMAIL", "hhuy08@gmail.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "huyviesea@admin")

    user_username = os.getenv("USER_USERNAME", "USER")
    user_email = os.getenv("USER_EMAIL", "hhuy084@gmail.com")
    user_password = os.getenv("USER_PASSWORD", "huyviesea@user")

    with current_app.app_context():
        # Tạo admin_manager nếu chưa có
        if not NguoiDung.query.filter_by(vai_tro="quan_tri_he_thong").first():
            u = NguoiDung(ten_nguoi_dung=admin_manager_username, email=admin_manager_email, vai_tro="quan_tri_he_thong")
            u.dat_mat_khau(admin_manager_password)
            db.session.add(u)
            print(f"Created SYSTEM_ADMIN: {admin_manager_email}")
        # Tạo admin nếu chưa có
        if not NguoiDung.query.filter_by(vai_tro="quan_tri_vien").first():
            u = NguoiDung(ten_nguoi_dung=admin_username, email=admin_email, vai_tro="quan_tri_vien")
            u.dat_mat_khau(admin_password)
            db.session.add(u)
            print(f"Created ADMIN: {admin_email}")
        # Tạo user thường nếu chưa có
        if not NguoiDung.query.filter_by(vai_tro="nguoi_dung").first():
            u = NguoiDung(ten_nguoi_dung=user_username, email=user_email, vai_tro="nguoi_dung")
            u.dat_mat_khau(user_password)
            db.session.add(u)
            print(f"Created USER: {user_email}")
        db.session.commit()
        print("Sample data loaded from .env!")
