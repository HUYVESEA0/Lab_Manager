#!/usr/bin/env python3
"""
Data Export/Import Script for Lab Manager
=========================================

Script này cho phép xuất và nhập dữ liệu từ/vào database.

Usage:
    python data_manager.py export --format json --output data.json
    python data_manager.py export --format csv --output data/
    python data_manager.py import --format json --input data.json
    python data_manager.py export-users --output users.csv
    python data_manager.py import-users --input users.csv
"""

import os
import sys
import json
import csv
from datetime import datetime
import click
from flask.cli import with_appcontext

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, NguoiDung, CaThucHanh, DangKyCa, VaoCa, CaiDatHeThong
from app.models import NhatKyHoatDong, KhoaHoc, BaiHoc, ThietBi, ThongBao

def serialize_datetime(obj):
    """JSON serializer cho datetime objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

def export_to_json(output_file):
    """Xuất toàn bộ dữ liệu ra JSON"""
    print(f"Xuất dữ liệu ra {output_file}...")
    
    data = {
        'export_info': {
            'timestamp': datetime.now().isoformat(),
            'version': '1.0',
            'app': 'Lab Manager'
        },
        'users': [],
        'lab_sessions': [],
        'registrations': [],
        'attendances': [],
        'settings': [],
        'activities': [],
        'courses': [],
        'equipment': [],
        'notifications': []
    }
    
    # Xuất người dùng (loại bỏ mật khẩu)
    for user in NguoiDung.query.all():
        user_data = {
            'id': user.id,
            'ten_nguoi_dung': user.ten_nguoi_dung,
            'email': user.email,
            'vai_tro': user.vai_tro,
            'ngay_tao': user.ngay_tao.isoformat() if user.ngay_tao else None,
            'last_seen': user.last_seen.isoformat() if user.last_seen else None,
            'bio': user.bio,
            'is_verified': user.is_verified,
            'active': user.active
        }
        data['users'].append(user_data)
    
    # Xuất ca thực hành
    for session in CaThucHanh.query.all():
        session_data = {
            'id': session.id,
            'tieu_de': session.tieu_de,
            'mo_ta': session.mo_ta,
            'ngay': session.ngay.isoformat() if session.ngay else None,
            'gio_bat_dau': session.gio_bat_dau.isoformat() if session.gio_bat_dau else None,
            'gio_ket_thuc': session.gio_ket_thuc.isoformat() if session.gio_ket_thuc else None,
            'dia_diem': session.dia_diem,
            'so_luong_toi_da': session.so_luong_toi_da,
            'dang_hoat_dong': session.dang_hoat_dong,
            'ma_xac_thuc': session.ma_xac_thuc,
            'nguoi_tao_ma': session.nguoi_tao_ma,
            'muc_do_kho': session.muc_do_kho,
            'trang_thai': session.trang_thai,
            'tags': session.get_tags(),
            'yeu_cau_thiet_bi': session.get_equipment()
        }
        data['lab_sessions'].append(session_data)
    
    # Xuất đăng ký
    for reg in DangKyCa.query.all():
        reg_data = {
            'id': reg.id,
            'nguoi_dung_ma': reg.nguoi_dung_ma,
            'ca_thuc_hanh_ma': reg.ca_thuc_hanh_ma,
            'ghi_chu': reg.ghi_chu,
            'trang_thai_tham_gia': reg.trang_thai_tham_gia,
            'ngay_dang_ky': reg.ngay_dang_ky.isoformat() if reg.ngay_dang_ky else None,
            'da_xac_nhan': reg.da_xac_nhan
        }
        data['registrations'].append(reg_data)
    
    # Xuất tham dự
    for attendance in VaoCa.query.all():
        attendance_data = {
            'id': attendance.id,
            'nguoi_dung_ma': attendance.nguoi_dung_ma,
            'ca_thuc_hanh_ma': attendance.ca_thuc_hanh_ma,
            'thoi_gian_vao': attendance.thoi_gian_vao.isoformat() if attendance.thoi_gian_vao else None,
            'thoi_gian_ra': attendance.thoi_gian_ra.isoformat() if attendance.thoi_gian_ra else None,
            'ket_qua': attendance.ket_qua,
            'diem_so': attendance.diem_so,
            'trang_thai_nop': attendance.trang_thai_nop
        }
        data['attendances'].append(attendance_data)
    
    # Xuất cài đặt
    for setting in CaiDatHeThong.query.all():
        setting_data = {
            'id': setting.id,
            'khoa': setting.khoa,
            'gia_tri': setting.gia_tri,
            'kieu': setting.kieu,
            'mo_ta': setting.mo_ta
        }
        data['settings'].append(setting_data)
    
    # Xuất hoạt động (chỉ 1000 records gần nhất)
    for activity in NhatKyHoatDong.query.order_by(NhatKyHoatDong.thoi_gian.desc()).limit(1000):
        activity_data = {
            'id': activity.id,
            'nguoi_dung_ma': activity.nguoi_dung_ma,
            'hanh_dong': activity.hanh_dong,
            'chi_tiet': activity.chi_tiet,
            'dia_chi_ip': activity.dia_chi_ip,
            'thoi_gian': activity.thoi_gian.isoformat() if activity.thoi_gian else None
        }
        data['activities'].append(activity_data)
    
    # Xuất khóa học
    for course in KhoaHoc.query.all():
        course_data = {
            'id': course.id,
            'tieu_de': course.tieu_de,
            'mo_ta': course.mo_ta,
            'ngay_tao': course.ngay_tao.isoformat() if course.ngay_tao else None
        }
        data['courses'].append(course_data)
    
    # Xuất thiết bị
    for equipment in ThietBi.query.all():
        equipment_data = {
            'id': equipment.id,
            'ten_thiet_bi': equipment.ten_thiet_bi,
            'mo_ta': equipment.mo_ta,
            'so_luong_co_san': equipment.so_luong_co_san,
            'trang_thai': equipment.trang_thai,
            'vi_tri': equipment.vi_tri,
            'ghi_chu': equipment.ghi_chu
        }
        data['equipment'].append(equipment_data)
    
    # Xuất thông báo (chỉ 500 records gần nhất)
    for notification in ThongBao.query.order_by(ThongBao.ngay_tao.desc()).limit(500):
        notification_data = {
            'id': notification.id,
            'nguoi_nhan': notification.nguoi_nhan,
            'tieu_de': notification.tieu_de,
            'noi_dung': notification.noi_dung,
            'loai': notification.loai,
            'da_doc': notification.da_doc,
            'ngay_tao': notification.ngay_tao.isoformat() if notification.ngay_tao else None
        }
        data['notifications'].append(notification_data)
    
    # Ghi file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=serialize_datetime)
    
    print(f"✅ Đã xuất {len(data['users'])} users, {len(data['lab_sessions'])} sessions, {len(data['registrations'])} registrations")

def export_to_csv(output_dir):
    """Xuất dữ liệu ra các file CSV"""
    print(f"Xuất dữ liệu CSV vào thư mục {output_dir}...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Xuất người dùng
    users_file = os.path.join(output_dir, 'users.csv')
    with open(users_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Tên người dùng', 'Email', 'Vai trò', 'Ngày tạo', 'Trạng thái', 'Đã xác thực'])
        
        for user in NguoiDung.query.all():
            writer.writerow([
                user.id,
                user.ten_nguoi_dung,
                user.email,
                user.vai_tro,
                user.ngay_tao.strftime('%Y-%m-%d %H:%M:%S') if user.ngay_tao else '',
                'Active' if user.active else 'Inactive',
                'Yes' if user.is_verified else 'No'
            ])
    
    # Xuất ca thực hành
    sessions_file = os.path.join(output_dir, 'lab_sessions.csv')
    with open(sessions_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Tiêu đề', 'Mô tả', 'Ngày', 'Giờ bắt đầu', 'Giờ kết thúc', 'Địa điểm', 'Sức chứa', 'Trạng thái', 'Mức độ khó'])
        
        for session in CaThucHanh.query.all():
            writer.writerow([
                session.id,
                session.tieu_de,
                session.mo_ta,
                session.ngay.strftime('%Y-%m-%d') if session.ngay else '',
                session.gio_bat_dau.strftime('%H:%M') if session.gio_bat_dau else '',
                session.gio_ket_thuc.strftime('%H:%M') if session.gio_ket_thuc else '',
                session.dia_diem,
                session.so_luong_toi_da,
                session.trang_thai,
                session.muc_do_kho
            ])
    
    # Xuất đăng ký
    registrations_file = os.path.join(output_dir, 'registrations.csv')
    with open(registrations_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'User ID', 'Session ID', 'Ngày đăng ký', 'Trạng thái', 'Ghi chú'])
        
        for reg in DangKyCa.query.all():
            writer.writerow([
                reg.id,
                reg.nguoi_dung_ma,
                reg.ca_thuc_hanh_ma,
                reg.ngay_dang_ky.strftime('%Y-%m-%d %H:%M:%S') if reg.ngay_dang_ky else '',
                reg.trang_thai_tham_gia,
                reg.ghi_chu or ''
            ])
    
    print(f"✅ Đã xuất CSV files vào {output_dir}")

def import_from_json(input_file):
    """Nhập dữ liệu từ JSON file"""
    print(f"Nhập dữ liệu từ {input_file}...")
    
    if not os.path.exists(input_file):
        print(f"❌ Không tìm thấy file: {input_file}")
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📦 File xuất từ: {data.get('export_info', {}).get('timestamp', 'Unknown')}")
    
    # Clear existing data nếu người dùng xác nhận
    if click.confirm('⚠️  Xóa dữ liệu hiện tại trước khi import?'):
        print("Xóa dữ liệu hiện tại...")
        db.session.execute('DELETE FROM vao_ca')
        db.session.execute('DELETE FROM dang_ky_ca')
        db.session.execute('DELETE FROM ca_thuc_hanh')
        db.session.execute('DELETE FROM nhat_ky_hoat_dong')
        db.session.execute('DELETE FROM thong_bao')
        db.session.execute('DELETE FROM ghi_danh')
        db.session.execute('DELETE FROM bai_hoc')
        db.session.execute('DELETE FROM khoa_hoc')
        db.session.execute('DELETE FROM thiet_bi')
        db.session.execute('DELETE FROM nguoi_dung')
        db.session.commit()
    
    # Import users
    print("Nhập người dùng...")
    for user_data in data.get('users', []):
        existing_user = NguoiDung.query.filter_by(email=user_data['email']).first()
        if not existing_user:
            user = NguoiDung(
                ten_nguoi_dung=user_data['ten_nguoi_dung'],
                email=user_data['email'],
                vai_tro=user_data['vai_tro']
            )
            user.dat_mat_khau('temp123')  # Temporary password
            user.is_verified = user_data.get('is_verified', False)
            user.active = user_data.get('active', True)
            user.bio = user_data.get('bio')
            
            if user_data.get('ngay_tao'):
                user.ngay_tao = datetime.fromisoformat(user_data['ngay_tao'])
            
            db.session.add(user)
    
    db.session.commit()
    print(f"✅ Đã nhập {len(data.get('users', []))} người dùng")
    
    # Import settings
    print("Nhập cài đặt hệ thống...")
    for setting_data in data.get('settings', []):
        existing_setting = CaiDatHeThong.query.filter_by(khoa=setting_data['khoa']).first()
        if not existing_setting:
            CaiDatHeThong.dat_gia_tri(
                setting_data['khoa'],
                setting_data['gia_tri'],
                setting_data.get('kieu', 'string'),
                setting_data.get('mo_ta', '')
            )
    
    print(f"✅ Đã nhập {len(data.get('settings', []))} cài đặt")
    
    # Import courses
    print("Nhập khóa học...")
    for course_data in data.get('courses', []):
        course = KhoaHoc(
            tieu_de=course_data['tieu_de'],
            mo_ta=course_data['mo_ta']
        )
        if course_data.get('ngay_tao'):
            course.ngay_tao = datetime.fromisoformat(course_data['ngay_tao'])
        db.session.add(course)
    
    db.session.commit()
    print(f"✅ Đã nhập {len(data.get('courses', []))} khóa học")
    
    # Import equipment
    print("Nhập thiết bị...")
    for equipment_data in data.get('equipment', []):
        equipment = ThietBi(
            ten_thiet_bi=equipment_data['ten_thiet_bi'],
            mo_ta=equipment_data['mo_ta'],
            so_luong_co_san=equipment_data['so_luong_co_san'],
            trang_thai=equipment_data['trang_thai'],
            vi_tri=equipment_data['vi_tri'],
            ghi_chu=equipment_data['ghi_chu']
        )
        db.session.add(equipment)
    
    db.session.commit()
    print(f"✅ Đã nhập {len(data.get('equipment', []))} thiết bị")
    
    print("🎉 Import hoàn thành!")

@click.group()
def cli():
    """Lab Manager Data Export/Import Tool"""
    pass

@cli.command()
@click.option('--format', 'export_format', type=click.Choice(['json', 'csv']), default='json', help='Export format')
@click.option('--output', help='Output file/directory')
@with_appcontext
def export(export_format, output):
    """Xuất dữ liệu"""
    if export_format == 'json':
        output_file = output or f"lab_manager_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        export_to_json(output_file)
    elif export_format == 'csv':
        output_dir = output or f"lab_manager_csv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        export_to_csv(output_dir)

@cli.command()
@click.option('--format', 'import_format', type=click.Choice(['json']), default='json', help='Import format')
@click.option('--input', help='Input file')
@with_appcontext
def import_data(import_format, input):
    """Nhập dữ liệu"""
    if import_format == 'json':
        input_file = input or click.prompt('Đường dẫn file JSON')
        import_from_json(input_file)

@cli.command()
@click.option('--output', help='Output CSV file', default='users_export.csv')
@with_appcontext
def export_users(output):
    """Xuất danh sách người dùng ra CSV"""
    print(f"Xuất danh sách người dùng ra {output}...")
    
    with open(output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'ID', 'Tên đăng nhập', 'Email', 'Vai trò', 'Ngày tạo', 
            'Lần truy cập cuối', 'Trạng thái', 'Đã xác thực', 'Bio'
        ])
        
        for user in NguoiDung.query.order_by(NguoiDung.ngay_tao.desc()).all():
            writer.writerow([
                user.id,
                user.ten_nguoi_dung,
                user.email,
                user.vai_tro,
                user.ngay_tao.strftime('%Y-%m-%d %H:%M:%S') if user.ngay_tao else '',
                user.last_seen.strftime('%Y-%m-%d %H:%M:%S') if user.last_seen else '',
                'Active' if user.active else 'Inactive',
                'Yes' if user.is_verified else 'No',
                user.bio or ''
            ])
    
    print(f"✅ Đã xuất {NguoiDung.query.count()} người dùng ra {output}")

@cli.command()
@click.option('--input', help='Input CSV file')
@with_appcontext
def import_users(input):
    """Nhập danh sách người dùng từ CSV"""
    input_file = input or click.prompt('Đường dẫn file CSV')
    
    if not os.path.exists(input_file):
        print(f"❌ Không tìm thấy file: {input_file}")
        return
    
    print(f"Nhập người dùng từ {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        
        for row in reader:
            # Kiểm tra user đã tồn tại
            existing_user = NguoiDung.query.filter(
                (NguoiDung.ten_nguoi_dung == row['Tên đăng nhập']) |
                (NguoiDung.email == row['Email'])
            ).first()
            
            if existing_user:
                print(f"⚠️  User {row['Email']} đã tồn tại, bỏ qua")
                continue
            
            # Tạo user mới
            user = NguoiDung(
                ten_nguoi_dung=row['Tên đăng nhập'],
                email=row['Email'],
                vai_tro=row.get('Vai trò', 'nguoi_dung')
            )
            user.dat_mat_khau('123456')  # Default password
            user.is_verified = row.get('Đã xác thực', 'No').lower() == 'yes'
            user.active = row.get('Trạng thái', 'Active').lower() == 'active'
            user.bio = row.get('Bio', '')
            
            db.session.add(user)
            count += 1
        
        db.session.commit()
        print(f"✅ Đã nhập {count} người dùng mới")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        cli()
