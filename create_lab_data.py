#!/usr/bin/env python3
from app import create_app
from app.models import *
from datetime import datetime, timedelta, time, date
import random
import string

app, socketio = create_app()
ctx = app.app_context()
ctx.push()

print("=== KIỂM TRA VÀ THÊM DỮ LIỆU CA THỰC HÀNH ===")

# Check existing data
ca_list = CaThucHanh.query.all()
print(f"Số ca thực hành hiện tại: {len(ca_list)}")

for ca in ca_list:
    print(f"  - {ca.tieu_de} | {ca.ngay} | {ca.gio_bat_dau} - {ca.gio_ket_thuc}")

# Check registrations
dang_ky_list = DangKyCa.query.all()
print(f"\nSố đăng ký ca: {len(dang_ky_list)}")

# Check attendances  
vao_ca_list = VaoCa.query.all()
print(f"Số lượt tham gia: {len(vao_ca_list)}")

print("\n=== THÊM DỮ LIỆU MẪU CA THỰC HÀNH ===")

# Create sample lab sessions if none exist
if len(ca_list) == 0:
    print("Đang tạo dữ liệu mẫu ca thực hành...")
    
    # Get today and future dates
    today = date.today()
    
    sample_sessions = [
        {
            "tieu_de": "Lab 1: Cài đặt môi trường Python",
            "mo_ta": "Hướng dẫn cài đặt và cấu hình môi trường phát triển Python cơ bản",
            "ngay": today + timedelta(days=1),
            "gio_bat_dau": time(9, 0),
            "gio_ket_thuc": time(11, 0),
            "so_cho_toi_da": 30,
            "phong": "Lab A1"
        },
        {
            "tieu_de": "Lab 2: Flask Web Framework",
            "mo_ta": "Xây dựng ứng dụng web đầu tiên với Flask framework",
            "ngay": today + timedelta(days=2),
            "gio_bat_dau": time(14, 0),
            "gio_ket_thuc": time(16, 0),
            "so_cho_toi_da": 25,
            "phong": "Lab B2"
        },
        {
            "tieu_de": "Lab 3: Database với SQLAlchemy",
            "mo_ta": "Tìm hiểu và thực hành với cơ sở dữ liệu SQLAlchemy",
            "ngay": today + timedelta(days=3),
            "gio_bat_dau": time(10, 0),
            "gio_ket_thuc": time(12, 0),
            "so_cho_toi_da": 20,
            "phong": "Lab C3"
        },
        {
            "tieu_de": "Lab 4: Authentication & Authorization",
            "mo_ta": "Xây dựng hệ thống đăng nhập và phân quyền người dùng",
            "ngay": today + timedelta(days=5),
            "gio_bat_dau": time(13, 0),
            "gio_ket_thuc": time(15, 0),
            "so_cho_toi_da": 25,
            "phong": "Lab A2"
        },
        {
            "tieu_de": "Lab 5: RESTful API Development",
            "mo_ta": "Phát triển API RESTful với Flask và testing",
            "ngay": today + timedelta(days=7),
            "gio_bat_dau": time(9, 30),
            "gio_ket_thuc": time(11, 30),
            "so_cho_toi_da": 30,
            "phong": "Lab B1"
        }
    ]
    
    for session_data in sample_sessions:
        # Generate verification code
        ma_xac_thuc = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Create datetime objects
        ngay_obj = session_data["ngay"]
        gio_bat_dau_obj = datetime.combine(ngay_obj, session_data["gio_bat_dau"])
        gio_ket_thuc_obj = datetime.combine(ngay_obj, session_data["gio_ket_thuc"])
        
        ca_moi = CaThucHanh(
            tieu_de=session_data["tieu_de"],
            mo_ta=session_data["mo_ta"],
            ngay=ngay_obj,
            gio_bat_dau=gio_bat_dau_obj,
            gio_ket_thuc=gio_ket_thuc_obj,
            so_cho_toi_da=session_data["so_cho_toi_da"],
            phong=session_data["phong"],
            ma_xac_thuc=ma_xac_thuc,
            trang_thai="sap_dien_ra"
        )
        
        db.session.add(ca_moi)
        print(f"✅ Tạo ca: {session_data['tieu_de']} - {ma_xac_thuc}")
    
    db.session.commit()
    print(f"✅ Đã tạo {len(sample_sessions)} ca thực hành mẫu")
    
else:
    print("Đã có dữ liệu ca thực hành, không cần tạo mẫu")

print("\n=== THÊM ĐĂNG KÝ MẪU ===")

# Get users for sample registrations
users = NguoiDung.query.all()
sessions = CaThucHanh.query.all()

if len(users) > 0 and len(sessions) > 0:
    # Create some sample registrations
    for i, user in enumerate(users):
        # Register each user for 2-3 random sessions
        user_sessions = random.sample(sessions, min(3, len(sessions)))
        
        for session in user_sessions:
            # Check if registration already exists
            existing = DangKyCa.query.filter_by(
                nguoi_dung_ma=user.id,
                ca_thuc_hanh_ma=session.id
            ).first()
            
            if not existing:
                dang_ky = DangKyCa(
                    nguoi_dung_ma=user.id,
                    ca_thuc_hanh_ma=session.id,
                    ghi_chu=f"Đăng ký từ user {user.ten_nguoi_dung}",
                    trang_thai_tham_gia="da_dang_ky",
                    uu_tien=random.randint(1, 3),
                    da_xac_nhan=True,
                    ngay_xac_nhan=datetime.utcnow()
                )
                db.session.add(dang_ky)
                print(f"✅ Đăng ký: {user.ten_nguoi_dung} -> {session.tieu_de}")
    
    db.session.commit()
    print("✅ Đã tạo đăng ký mẫu")

print("\n=== KIỂM TRA KẾT QUẢ ===")
final_sessions = CaThucHanh.query.all()
final_registrations = DangKyCa.query.all()

print(f"Tổng số ca thực hành: {len(final_sessions)}")
print(f"Tổng số đăng ký: {len(final_registrations)}")

print("\nDanh sách ca thực hành:")
for ca in final_sessions:
    registrations_count = DangKyCa.query.filter_by(ca_thuc_hanh_ma=ca.id).count()
    print(f"  - {ca.tieu_de} ({ca.ngay}) - {registrations_count} đăng ký")

print("\n✅ HOÀN TẤT THIẾT LẬP DỮ LIỆU CA THỰC HÀNH")
