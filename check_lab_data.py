#!/usr/bin/env python3
from app import create_app
from app.models import *

app, socketio = create_app()
ctx = app.app_context()
ctx.push()

print("=== KIỂM TRA DỮ LIỆU CA THỰC HÀNH ===")

sessions = CaThucHanh.query.all()
print(f"Tổng số ca thực hành: {len(sessions)}")

for session in sessions[:3]:
    print(f"- {session.tieu_de} | Ngày: {session.ngay} | Giờ: {session.gio_bat_dau} - {session.gio_ket_thuc}")

print("\n=== KIỂM TRA ĐĂNG KÝ CA ===")
registrations = DangKyCa.query.all()
print(f"Tổng số đăng ký: {len(registrations)}")

if len(registrations) == 0:
    print("⚠️ Không có đăng ký nào - Tạo dữ liệu mẫu...")
    
    # Tạo một số đăng ký mẫu
    if len(sessions) > 0 and NguoiDung.query.count() > 0:
        user = NguoiDung.query.first()
        for i, session in enumerate(sessions[:3]):
            registration = DangKyCa(
                nguoi_dung_ma=user.id,
                ca_thuc_hanh_ma=session.id,
                ghi_chu=f"Đăng ký mẫu {i+1}",
                trang_thai_tham_gia="da_dang_ky"
            )
            db.session.add(registration)
        
        db.session.commit()
        print(f"✅ Đã tạo {min(3, len(sessions))} đăng ký mẫu")
else:
    for reg in registrations:
        user = NguoiDung.query.get(reg.nguoi_dung_ma)
        session = CaThucHanh.query.get(reg.ca_thuc_hanh_ma)
        print(f"- {user.ten_nguoi_dung} đăng ký {session.tieu_de}")

print("\n=== KIỂM TRA LAI AFTER UPDATE ===")
registrations = DangKyCa.query.all()
print(f"Tổng số đăng ký sau update: {len(registrations)}")
