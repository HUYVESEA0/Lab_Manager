#!/usr/bin/env python3
"""
Database Management Script for Lab Manager
==========================================

Script này cung cấp các công cụ để quản lý cơ sở dữ liệu của hệ thống Lab Manager.

Usage:
    python db_manager.py init          # Khởi tạo database
    python db_manager.py seed          # Tạo dữ liệu mẫu
    python db_manager.py backup        # Sao lưu database
    python db_manager.py restore <file> # Khôi phục database
    python db_manager.py reset         # Reset database (xóa tất cả)
    python db_manager.py status        # Kiểm tra trạng thái
    python db_manager.py migrate       # Chạy migration
    python db_manager.py upgrade       # Upgrade schema
"""

import os
import sys
import shutil
import sqlite3
from datetime import datetime, timedelta
import click
from flask import Flask
from flask.cli import with_appcontext

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, NguoiDung, CaiDatHeThong, CaThucHanh, DangKyCa, VaoCa, NhatKyHoatDong
from app.models import KhoaHoc, BaiHoc, GhiDanh, ThietBi, DatThietBi, TaiLieuCa, MauCaThucHanh
from app.models import DanhGiaCa, ThongBao, SinhVien
from werkzeug.security import generate_password_hash
import secrets
import random
import json

def create_sample_data():
    """Tạo dữ liệu mẫu cho hệ thống"""
    
    # Tạo người dùng mẫu
    users_data = [
        {
            'ten_nguoi_dung': 'HUYVIESEA',
            'email': 'hhuy0847@gmail.com',
            'vai_tro': 'quan_tri_he_thong',
            'password': 'huyviesea@manager'
        },
        {
            'ten_nguoi_dung': 'ADMIN',
            'email': 'admin@labmanager.com',
            'vai_tro': 'quan_tri_vien',
            'password': 'huyviesea@admin'
        },
        {
            'ten_nguoi_dung': 'USER',
            'email': 'user@labmanager.com',
            'vai_tro': 'nguoi_dung',
            'password': 'huyviesea@nguoidung'
        },
        {
            'ten_nguoi_dung': 'giaovien01',
            'email': 'teacher01@labmanager.com',
            'vai_tro': 'quan_tri_vien',
            'password': 'teacher123'
        },
        {
            'ten_nguoi_dung': 'sinhvien01',
            'email': 'student01@labmanager.com',
            'vai_tro': 'nguoi_dung',
            'password': 'student123'
        },
        {
            'ten_nguoi_dung': 'sinhvien02',
            'email': 'student02@labmanager.com',
            'vai_tro': 'nguoi_dung',
            'password': 'student123'
        }
    ]
    
    print("Tạo người dùng mẫu...")
    created_users = []
    for user_data in users_data:
        # Kiểm tra xem user đã tồn tại chưa
        existing_user = NguoiDung.query.filter_by(email=user_data['email']).first()
        if not existing_user:
            user = NguoiDung(
                ten_nguoi_dung=user_data['ten_nguoi_dung'],
                email=user_data['email'],
                vai_tro=user_data['vai_tro']
            )
            user.dat_mat_khau(user_data['password'])
            user.is_verified = True
            user.active = True
            db.session.add(user)
            created_users.append(user)
            print(f"  + Tạo {user.ten_nguoi_dung} ({user.vai_tro})")
        else:
            created_users.append(existing_user)
            print(f"  - {existing_user.ten_nguoi_dung} đã tồn tại")
    
    db.session.commit()
    
    # Tạo cài đặt hệ thống
    print("Tạo cài đặt hệ thống...")
    settings_data = [
        ('app_name', 'Lab Manager System', 'string', 'Tên ứng dụng'),
        ('app_description', 'Hệ thống quản lý phòng thực hành', 'string', 'Mô tả ứng dụng'),
        ('enable_registration', 'true', 'boolean', 'Cho phép đăng ký tài khoản mới'),
        ('enable_password_reset', 'true', 'boolean', 'Cho phép đặt lại mật khẩu'),
        ('items_per_page', '25', 'integer', 'Số item trên mỗi trang'),
        ('session_timeout', '1800', 'integer', 'Thời gian timeout session (giây)'),
        ('max_file_size', '10485760', 'integer', 'Kích thước file tối đa (bytes)'),
        ('allowed_file_types', 'pdf,doc,docx,ppt,pptx,zip', 'string', 'Các loại file được phép'),
        ('lab_session_reminder', '60', 'integer', 'Thời gian nhắc nhở trước ca thực hành (phút)'),
        ('auto_approve_registration', 'true', 'boolean', 'Tự động duyệt đăng ký ca thực hành')
    ]
    
    for khoa, gia_tri, kieu, mo_ta in settings_data:
        existing_setting = CaiDatHeThong.query.filter_by(khoa=khoa).first()
        if not existing_setting:
            CaiDatHeThong.dat_gia_tri(khoa, gia_tri, kieu, mo_ta)
            print(f"  + Tạo cài đặt: {khoa}")
        else:
            print(f"  - Cài đặt {khoa} đã tồn tại")
    
    # Tạo thiết bị mẫu
    print("Tạo thiết bị mẫu...")
    equipment_data = [
        ('Máy tính', 'Desktop computer cho thực hành', 30, 'available', 'Phòng A101'),
        ('Laptop', 'Laptop cho thực hành di động', 15, 'available', 'Phòng A102'),
        ('Projector', 'Máy chiếu', 5, 'available', 'Kho thiết bị'),
        ('Arduino UNO', 'Vi điều khiển Arduino', 50, 'available', 'Phòng B201'),
        ('Raspberry Pi', 'Mini computer Raspberry Pi', 20, 'available', 'Phòng B202'),
        ('Breadboard', 'Bo mạch thử nghiệm', 100, 'available', 'Kho linh kiện'),
        ('Multimeter', 'Đồng hồ vạn năng', 25, 'available', 'Phòng B201'),
        ('Oscilloscope', 'Máy hiện sóng', 10, 'available', 'Phòng B202')
    ]
    
    for ten, mo_ta, so_luong, trang_thai, vi_tri in equipment_data:
        existing_equipment = ThietBi.query.filter_by(ten_thiet_bi=ten).first()
        if not existing_equipment:
            equipment = ThietBi(
                ten_thiet_bi=ten,
                mo_ta=mo_ta,
                so_luong_co_san=so_luong,
                trang_thai=trang_thai,
                vi_tri=vi_tri
            )
            db.session.add(equipment)
            print(f"  + Tạo thiết bị: {ten}")
        else:
            print(f"  - Thiết bị {ten} đã tồn tại")
    
    db.session.commit()
    
    # Tạo khóa học mẫu
    print("Tạo khóa học mẫu...")
    courses_data = [
        ('Lập trình Python cơ bản', 'Khóa học lập trình Python cho người mới bắt đầu'),
        ('Phát triển Web với Flask', 'Học cách xây dựng ứng dụng web với Flask framework'),
        ('Arduino và IoT', 'Thực hành với vi điều khiển Arduino và Internet of Things'),
        ('Machine Learning cơ bản', 'Giới thiệu về Machine Learning và các thuật toán cơ bản'),
        ('Database Design', 'Thiết kế và quản lý cơ sở dữ liệu')
    ]
    
    created_courses = []
    for tieu_de, mo_ta in courses_data:
        existing_course = KhoaHoc.query.filter_by(tieu_de=tieu_de).first()
        if not existing_course:
            course = KhoaHoc(tieu_de=tieu_de, mo_ta=mo_ta)
            db.session.add(course)
            created_courses.append(course)
            print(f"  + Tạo khóa học: {tieu_de}")
        else:
            created_courses.append(existing_course)
            print(f"  - Khóa học {tieu_de} đã tồn tại")
    
    db.session.commit()
    
    # Tạo ca thực hành mẫu
    print("Tạo ca thực hành mẫu...")
    admin_user = next((u for u in created_users if u.vai_tro == 'quan_tri_vien'), created_users[0])
    
    sessions_data = [
        {
            'tieu_de': 'Python Basics - Variables and Data Types',
            'mo_ta': 'Học về biến và kiểu dữ liệu trong Python',
            'days_from_now': 7,
            'duration_hours': 2,
            'dia_diem': 'Phòng A101',
            'so_luong_toi_da': 25,
            'muc_do_kho': 'de',
            'tags': ['python', 'basics', 'programming']
        },
        {
            'tieu_de': 'Flask Web Development - Routing',
            'mo_ta': 'Tìm hiểu về routing trong Flask framework',
            'days_from_now': 10,
            'duration_hours': 3,
            'dia_diem': 'Phòng A102',
            'so_luong_toi_da': 20,
            'muc_do_kho': 'trung_binh',
            'tags': ['flask', 'web', 'routing']
        },
        {
            'tieu_de': 'Arduino LED Control',
            'mo_ta': 'Điều khiển LED với Arduino UNO',
            'days_from_now': 14,
            'duration_hours': 2,
            'dia_diem': 'Phòng B201',
            'so_luong_toi_da': 15,
            'muc_do_kho': 'de',
            'tags': ['arduino', 'led', 'electronics']
        },
        {
            'tieu_de': 'Machine Learning with Scikit-learn',
            'mo_ta': 'Thực hành ML với thư viện Scikit-learn',
            'days_from_now': 21,
            'duration_hours': 4,
            'dia_diem': 'Phòng A103',
            'so_luong_toi_da': 30,
            'muc_do_kho': 'kho',
            'tags': ['ml', 'scikit-learn', 'data-science']
        }
    ]
    
    for session_data in sessions_data:
        start_time = datetime.now() + timedelta(days=session_data['days_from_now'])
        end_time = start_time + timedelta(hours=session_data['duration_hours'])
        
        existing_session = CaThucHanh.query.filter_by(tieu_de=session_data['tieu_de']).first()
        if not existing_session:
            session = CaThucHanh(
                tieu_de=session_data['tieu_de'],
                mo_ta=session_data['mo_ta'],
                ngay=start_time.date(),
                gio_bat_dau=start_time,
                gio_ket_thuc=end_time,
                dia_diem=session_data['dia_diem'],
                so_luong_toi_da=session_data['so_luong_toi_da'],
                dang_hoat_dong=True,
                ma_xac_thuc=f"LAB{random.randint(1000, 9999)}",
                nguoi_tao_ma=admin_user.id,
                muc_do_kho=session_data['muc_do_kho'],
                trang_thai='scheduled'
            )
            session.set_tags(session_data['tags'])
            db.session.add(session)
            print(f"  + Tạo ca thực hành: {session.tieu_de}")
        else:
            print(f"  - Ca thực hành {session_data['tieu_de']} đã tồn tại")
    
    db.session.commit()
    
    # Tạo đăng ký mẫu
    print("Tạo đăng ký mẫu...")
    student_users = [u for u in created_users if u.vai_tro == 'nguoi_dung']
    lab_sessions = CaThucHanh.query.limit(3).all()
    
    for session in lab_sessions:
        for student in student_users[:2]:  # Chỉ đăng ký 2 sinh viên đầu tiên
            existing_registration = DangKyCa.query.filter_by(
                nguoi_dung_ma=student.id,
                ca_thuc_hanh_ma=session.id
            ).first()
            
            if not existing_registration:
                registration = DangKyCa(
                    nguoi_dung_ma=student.id,
                    ca_thuc_hanh_ma=session.id,
                    ghi_chu=f"Đăng ký tham gia ca {session.tieu_de}",
                    trang_thai_tham_gia='da_dang_ky',
                    da_xac_nhan=True
                )
                db.session.add(registration)
                print(f"  + Đăng ký {student.ten_nguoi_dung} vào ca {session.tieu_de}")
    
    db.session.commit()
    
    # Tạo hoạt động mẫu
    print("Tạo nhật ký hoạt động mẫu...")
    activities = [
        ('Đăng nhập hệ thống', 'Người dùng đăng nhập thành công'),
        ('Tạo ca thực hành', 'Tạo ca thực hành mới'),
        ('Đăng ký ca thực hành', 'Đăng ký tham gia ca thực hành'),
        ('Cập nhật hồ sơ', 'Cập nhật thông tin hồ sơ cá nhân'),
        ('Xem báo cáo', 'Truy cập trang báo cáo hệ thống')
    ]
    
    for user in created_users:
        for i, (action, detail) in enumerate(activities):
            if random.choice([True, False]):  # Random tạo activity
                activity = NhatKyHoatDong(
                    nguoi_dung_ma=user.id,
                    hanh_dong=action,
                    chi_tiet=detail,
                    dia_chi_ip='127.0.0.1',
                    thoi_gian=datetime.now() - timedelta(hours=i+1)
                )
                db.session.add(activity)
    
    db.session.commit()
    print("Hoàn thành tạo dữ liệu mẫu!")

@click.group()
def cli():
    """Lab Manager Database Manager"""
    pass

@cli.command()
@with_appcontext
def init():
    """Khởi tạo database"""
    print("Khởi tạo database...")
    db.create_all()
    print("Database đã được khởi tạo!")

@cli.command()
@with_appcontext
def seed():
    """Tạo dữ liệu mẫu"""
    print("Tạo dữ liệu mẫu...")
    create_sample_data()
    print("Dữ liệu mẫu đã được tạo!")

@cli.command()
@with_appcontext
def reset():
    """Reset database (xóa tất cả dữ liệu)"""
    if click.confirm('Bạn có chắc chắn muốn xóa tất cả dữ liệu?'):
        print("Đang reset database...")
        db.drop_all()
        db.create_all()
        print("Database đã được reset!")

@cli.command()
@click.argument('backup_file')
@with_appcontext
def backup(backup_file):
    """Sao lưu database"""
    print(f"Sao lưu database vào {backup_file}...")
    
    if not backup_file.endswith('.db'):
        backup_file += '.db'
    
    # Chỉ hỗ trợ SQLite backup
    source_db = 'instance/app.db'
    if os.path.exists(source_db):
        shutil.copy2(source_db, backup_file)
        print(f"Đã sao lưu database vào {backup_file}")
    else:
        print(f"Không tìm thấy database tại {source_db}")

@cli.command()
@click.argument('backup_file')
@with_appcontext
def restore(backup_file):
    """Khôi phục database từ backup"""
    if not os.path.exists(backup_file):
        print(f"Không tìm thấy file backup: {backup_file}")
        return
    
    if click.confirm(f'Khôi phục database từ {backup_file}? (Dữ liệu hiện tại sẽ bị mất)'):
        print(f"Khôi phục database từ {backup_file}...")
        target_db = 'instance/app.db'
        
        # Backup current db first
        if os.path.exists(target_db):
            backup_current = f"{target_db}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(target_db, backup_current)
            print(f"Đã backup database hiện tại vào {backup_current}")
        
        shutil.copy2(backup_file, target_db)
        print("Database đã được khôi phục!")

@cli.command()
@with_appcontext
def status():
    """Kiểm tra trạng thái database"""
    print("=== TRẠNG THÁI DATABASE ===")
    
    try:
        # Kiểm tra kết nối
        db.session.execute('SELECT 1').fetchone()
        print("✅ Kết nối database: OK")
        
        # Đếm số lượng records
        tables = [
            ('Người dùng', NguoiDung),
            ('Ca thực hành', CaThucHanh),
            ('Đăng ký ca', DangKyCa),
            ('Tham dự ca', VaoCa),
            ('Nhật ký hoạt động', NhatKyHoatDong),
            ('Cài đặt hệ thống', CaiDatHeThong),
            ('Khóa học', KhoaHoc),
            ('Thiết bị', ThietBi),
            ('Thông báo', ThongBao)
        ]
        
        print("\n📊 THỐNG KÊ DỮ LIỆU:")
        for table_name, model in tables:
            try:
                count = model.query.count()
                print(f"  {table_name}: {count} records")
            except Exception as e:
                print(f"  {table_name}: Lỗi - {str(e)}")
        
        # Kiểm tra người dùng admin
        print("\n👥 NGƯỜI DÙNG QUẢN TRỊ:")
        admins = NguoiDung.query.filter(NguoiDung.vai_tro.in_(['quan_tri_vien', 'quan_tri_he_thong'])).all()
        for admin in admins:
            print(f"  {admin.ten_nguoi_dung} ({admin.email}) - {admin.vai_tro}")
        
        # Kiểm tra ca thực hành sắp tới
        print("\n🧪 CA THỰC HÀNH SẮP TỚI:")
        upcoming_sessions = CaThucHanh.query.filter(
            CaThucHanh.gio_bat_dau > datetime.now()
        ).order_by(CaThucHanh.gio_bat_dau).limit(5).all()
        
        for session in upcoming_sessions:
            print(f"  {session.tieu_de} - {session.gio_bat_dau.strftime('%d/%m/%Y %H:%M')}")
        
    except Exception as e:
        print(f"❌ Lỗi kết nối database: {str(e)}")

@cli.command()
@with_appcontext
def migrate():
    """Chạy database migration"""
    print("Chạy database migration...")
    try:
        from flask_migrate import upgrade
        upgrade()
        print("Migration completed!")
    except ImportError:
        print("Flask-Migrate không được cài đặt. Chạy: pip install Flask-Migrate")
    except Exception as e:
        print(f"Lỗi migration: {str(e)}")

@cli.command() 
@with_appcontext
def create_admin():
    """Tạo tài khoản admin mới"""
    print("Tạo tài khoản admin mới...")
    
    username = click.prompt('Tên đăng nhập')
    email = click.prompt('Email')
    password = click.prompt('Mật khẩu', hide_input=True)
    role = click.prompt('Vai trò (quan_tri_vien/quan_tri_he_thong)', 
                       default='quan_tri_vien')
    
    # Kiểm tra user đã tồn tại
    existing_user = NguoiDung.query.filter(
        (NguoiDung.ten_nguoi_dung == username) | (NguoiDung.email == email)
    ).first()
    
    if existing_user:
        print("❌ Tên đăng nhập hoặc email đã tồn tại!")
        return
    
    # Tạo user mới
    user = NguoiDung(
        ten_nguoi_dung=username,
        email=email,
        vai_tro=role
    )
    user.dat_mat_khau(password)
    user.is_verified = True
    user.active = True
    
    db.session.add(user)
    db.session.commit()
    
    print(f"✅ Đã tạo tài khoản admin: {username} ({email})")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        cli()
