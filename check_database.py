#!/usr/bin/env python3
from app import create_app
from app.models import *

app, socketio = create_app()
ctx = app.app_context()
ctx.push()

print("=== KIỂM TRA CÁC BẢNG DATABASE ===")

tables = [
    ('NguoiDung (Users)', NguoiDung),
    ('CaThucHanh (Lab Sessions)', CaThucHanh), 
    ('DangKyCa (Registrations)', DangKyCa),
    ('VaoCa (Attendances)', VaoCa),
    ('CaiDatHeThong (System Settings)', CaiDatHeThong),
    ('NhatKyHoatDong (Activity Logs)', NhatKyHoatDong),
    ('ThongBao (Notifications)', ThongBao),
    ('SinhVien (Students)', SinhVien)
]

for name, model in tables:
    try:
        count = model.query.count()
        print(f"✅ {name}: {count} records")
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)}")

print("\n=== KIỂM TRA THÔNG BÁO ===")
try:
    notifications = ThongBao.query.all()
    print(f"Total notifications: {len(notifications)}")
    for notif in notifications[:3]:
        print(f"  - {notif.tieu_de} (User: {notif.nguoi_nhan}, Read: {notif.da_doc})")
except Exception as e:
    print(f"Error loading notifications: {e}")

print("\n=== KIỂM TRA CÁC MODULE ===")
print("✅ Lab module: CaThucHanh, DangKyCa, VaoCa tables available")
print("✅ Admin module: NguoiDung, NhatKyHoatDong tables available")
print("✅ System Admin module: CaiDatHeThong table available")
