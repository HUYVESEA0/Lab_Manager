#!/usr/bin/env python3
from app import create_app
from app.models import db, DangKyCa, VaoCa, ThongBao

app, socketio = create_app()
ctx = app.app_context()
ctx.push()

print("=== UPDATING DATABASE SCHEMA ===")

# Drop and recreate tables with missing columns
try:
    print("Dropping problematic tables...")
    db.engine.execute("DROP TABLE IF EXISTS thong_bao")
    print("✅ Dropped thong_bao table")
    
    # We can't safely drop dang_ky_ca and vao_ca since they have data
    # Instead, we'll add the missing columns manually
    try:
        db.engine.execute("ALTER TABLE dang_ky_ca ADD COLUMN uu_tien INTEGER DEFAULT 0")
        print("✅ Added uu_tien column to dang_ky_ca")
    except Exception as e:
        print(f"uu_tien column might already exist: {e}")
    
    try:
        db.engine.execute("ALTER TABLE dang_ky_ca ADD COLUMN da_xac_nhan BOOLEAN DEFAULT 1")
        print("✅ Added da_xac_nhan column to dang_ky_ca")
    except Exception as e:
        print(f"da_xac_nhan column might already exist: {e}")
        
    try:
        db.engine.execute("ALTER TABLE dang_ky_ca ADD COLUMN ngay_xac_nhan DATETIME")
        print("✅ Added ngay_xac_nhan column to dang_ky_ca")
    except Exception as e:
        print(f"ngay_xac_nhan column might already exist: {e}")
    
    # Add missing columns to vao_ca
    try:
        db.engine.execute("ALTER TABLE vao_ca ADD COLUMN diem_so FLOAT")
        print("✅ Added diem_so column to vao_ca")
    except Exception as e:
        print(f"diem_so column might already exist: {e}")
        
    try:
        db.engine.execute("ALTER TABLE vao_ca ADD COLUMN nhan_xet_gv TEXT")
        print("✅ Added nhan_xet_gv column to vao_ca")
    except Exception as e:
        print(f"nhan_xet_gv column might already exist: {e}")
        
    try:
        db.engine.execute("ALTER TABLE vao_ca ADD COLUMN tep_nop_bai VARCHAR(500)")
        print("✅ Added tep_nop_bai column to vao_ca")
    except Exception as e:
        print(f"tep_nop_bai column might already exist: {e}")
        
    try:
        db.engine.execute("ALTER TABLE vao_ca ADD COLUMN trang_thai_nop VARCHAR(50) DEFAULT 'chua_nop'")
        print("✅ Added trang_thai_nop column to vao_ca")
    except Exception as e:
        print(f"trang_thai_nop column might already exist: {e}")
        
    try:
        db.engine.execute("ALTER TABLE vao_ca ADD COLUMN thoi_gian_nop DATETIME")
        print("✅ Added thoi_gian_nop column to vao_ca")
    except Exception as e:
        print(f"thoi_gian_nop column might already exist: {e}")
        
    try:
        db.engine.execute("ALTER TABLE vao_ca ADD COLUMN vi_tri_ngoi VARCHAR(50)")
        print("✅ Added vi_tri_ngoi column to vao_ca")
    except Exception as e:
        print(f"vi_tri_ngoi column might already exist: {e}")

    # Recreate missing tables
    print("Creating missing tables...")
    db.create_all()
    print("✅ Database schema updated successfully")
    
    # Create some sample notifications
    from datetime import datetime
    from app.models import NguoiDung
    
    users = NguoiDung.query.all()
    if users and not ThongBao.query.first():
        print("Creating sample notifications...")
        for user in users:
            # Welcome notification
            welcome_notif = ThongBao(
                nguoi_nhan=user.id,
                tieu_de="Chào mừng đến với Lab Manager",
                noi_dung="Hệ thống quản lý phòng thực hành đã sẵn sàng. Bạn có thể đăng ký các ca thực hành và theo dõi tiến độ học tập.",
                loai="info",
                lien_ket="/lab/sessions"
            )
            db.session.add(welcome_notif)
            
            # System update notification
            update_notif = ThongBao(
                nguoi_nhan=user.id,
                tieu_de="Cập nhật hệ thống",
                noi_dung="Hệ thống đã được cập nhật với các tính năng mới: thông báo thời gian thực, quản lý ca thực hành nâng cao.",
                loai="success",
                lien_ket="/user/dashboard"
            )
            db.session.add(update_notif)
        
        db.session.commit()
        print("✅ Created sample notifications")

except Exception as e:
    print(f"❌ Error updating schema: {e}")

print("=== DATABASE UPDATE COMPLETE ===")
