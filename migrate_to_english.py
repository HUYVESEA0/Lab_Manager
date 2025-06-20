#!/usr/bin/env python3
"""
Database Migration Script: Vietnamese to English
Migrates Lab Manager database from Vietnamese naming to English naming
"""

import sqlite3
import os
import shutil
from datetime import datetime
import json

def backup_database(db_path):
    """Create a backup of the current database"""
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(db_path, backup_path)
    print(f"✅ Database backed up to: {backup_path}")
    return backup_path

def create_english_schema(cursor):
    """Create new English schema tables"""
    
    # Users table (replaces nguoi_dung)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(80) UNIQUE NOT NULL,
            email VARCHAR(120) UNIQUE NOT NULL,
            password_hash VARCHAR(256),
            role VARCHAR(20) DEFAULT 'user',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
            bio TEXT,
            is_verified BOOLEAN DEFAULT 0,
            verification_token VARCHAR(100),
            verification_token_expiry INTEGER,
            active BOOLEAN DEFAULT 1,
            failed_login_attempts INTEGER DEFAULT 0,
            last_failed_login DATETIME,
            account_locked_until DATETIME,
            reset_token VARCHAR(100),
            reset_token_expiry INTEGER
        )
    ''')
    
    # Lab Sessions table (replaces ca_thuc_hanh)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lab_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            session_date DATE NOT NULL,
            start_time DATETIME NOT NULL,
            end_time DATETIME NOT NULL,
            location VARCHAR(100) NOT NULL,
            max_participants INTEGER NOT NULL DEFAULT 30,
            is_active BOOLEAN DEFAULT 1,
            verification_code VARCHAR(10) NOT NULL,
            created_by INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            tags TEXT,
            cover_image VARCHAR(255),
            difficulty_level VARCHAR(20) DEFAULT 'medium',
            required_equipment TEXT,
            allow_late_registration BOOLEAN DEFAULT 0,
            auto_approve BOOLEAN DEFAULT 1,
            notification_minutes INTEGER DEFAULT 60,
            status VARCHAR(20) DEFAULT 'scheduled',
            max_score INTEGER DEFAULT 100,
            time_limit_minutes INTEGER,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Session Registrations (replaces dang_ky_ca)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS session_registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lab_session_id INTEGER NOT NULL,
            notes TEXT,
            status VARCHAR(20) DEFAULT 'registered',
            registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            priority INTEGER DEFAULT 0,
            is_confirmed BOOLEAN DEFAULT 1,
            confirmed_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (lab_session_id) REFERENCES lab_sessions (id)
        )
    ''')
    
    # Session Entries (replaces vao_ca)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS session_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            lab_session_id INTEGER NOT NULL,
            entry_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            exit_time DATETIME,
            results TEXT,
            score INTEGER,
            teacher_comment TEXT,
            submitted_files VARCHAR(500),
            submission_status VARCHAR(20) DEFAULT 'not_submitted',
            submitted_at DATETIME,
            seat_assignment VARCHAR(20),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (lab_session_id) REFERENCES lab_sessions (id)
        )
    ''')
    
    # System Settings (replaces cai_dat_he_thong)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key VARCHAR(64) UNIQUE NOT NULL,
            value TEXT,
            data_type VARCHAR(16) DEFAULT 'string',
            description VARCHAR(256),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Activity Logs (replaces nhat_ky_hoat_dong)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action VARCHAR(128) NOT NULL,
            details TEXT,
            ip_address VARCHAR(45),
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Courses (replaces khoa_hoc)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(100) NOT NULL,
            description TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Lessons (replaces bai_hoc)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(100) NOT NULL,
            content TEXT NOT NULL,
            course_id INTEGER NOT NULL,
            FOREIGN KEY (course_id) REFERENCES courses (id)
        )
    ''')
    
    # Enrollments (replaces ghi_danh)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            enrolled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (course_id) REFERENCES courses (id)
        )
    ''')
    
    print("✅ English schema tables created")

def migrate_role_names(role):
    """Convert Vietnamese role names to English"""
    role_mapping = {
        "quan_tri_he_thong": "system_admin",
        "quan_tri_vien": "admin",
        "nguoi_dung": "user"
    }
    return role_mapping.get(role, "user")

def migrate_status_names(status):
    """Convert Vietnamese status names to English"""
    status_mapping = {
        "da_dang_ky": "registered",
        "da_tham_gia": "attended",
        "vang_mat": "absent",
        "huy_bo": "cancelled",
        "dang_cho": "pending"
    }
    return status_mapping.get(status, status)

def migrate_data(cursor):
    """Migrate data from Vietnamese tables to English tables"""
    
    # Check if old tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    # Migrate Users (nguoi_dung -> users)
    if 'nguoi_dung' in existing_tables:
        cursor.execute('''
            INSERT INTO users (
                id, username, email, password_hash, role, created_at, 
                last_seen, bio, is_verified, verification_token, 
                verification_token_expiry, active, failed_login_attempts,
                last_failed_login, account_locked_until, reset_token, reset_token_expiry
            )
            SELECT 
                id, ten_nguoi_dung, email, mat_khau_hash, ?, ngay_tao,
                last_seen, bio, is_verified, verification_token,
                verification_token_expiry, active, failed_login_attempts,
                last_failed_login, account_locked_until, reset_token, reset_token_expiry
            FROM nguoi_dung
        ''', (migrate_role_names,))
        
        # Update roles
        cursor.execute("SELECT id, vai_tro FROM nguoi_dung")
        for user_id, role in cursor.fetchall():
            new_role = migrate_role_names(role)
            cursor.execute("UPDATE users SET role = ? WHERE id = ?", (new_role, user_id))
        
        print("✅ Users migrated")
    
    # Migrate Lab Sessions (ca_thuc_hanh -> lab_sessions)
    if 'ca_thuc_hanh' in existing_tables:
        cursor.execute('''
            INSERT INTO lab_sessions (
                id, title, description, session_date, start_time, end_time,
                location, max_participants, is_active, verification_code,
                created_by, created_at, tags, cover_image, difficulty_level,
                allow_late_registration, auto_approve, notification_minutes,
                status, max_score, time_limit_minutes
            )
            SELECT 
                id, tieu_de, mo_ta, ngay, gio_bat_dau, gio_ket_thuc,
                dia_diem, so_luong_toi_da, dang_hoat_dong, ma_xac_thuc,
                nguoi_tao_ma, ngay_tao, tags, anh_bia, 
                CASE muc_do_kho 
                    WHEN 'de' THEN 'easy'
                    WHEN 'trung_binh' THEN 'medium' 
                    WHEN 'kho' THEN 'hard'
                    ELSE 'medium'
                END,
                cho_phep_dang_ky_tre, tu_dong_xac_nhan, thong_bao_truoc,
                trang_thai, diem_so_toi_da, thoi_gian_lam_bai
            FROM ca_thuc_hanh
        ''')
        print("✅ Lab Sessions migrated")
    
    # Migrate Session Registrations (dang_ky_ca -> session_registrations)
    if 'dang_ky_ca' in existing_tables:
        cursor.execute('''
            INSERT INTO session_registrations (
                id, user_id, lab_session_id, notes, status, registered_at,
                priority, is_confirmed, confirmed_at
            )
            SELECT 
                id, nguoi_dung_ma, ca_thuc_hanh_ma, ghi_chu, ?, ngay_dang_ky,
                uu_tien, da_xac_nhan, ngay_xac_nhan
            FROM dang_ky_ca
        ''', (migrate_status_names,))
        
        # Update status values
        cursor.execute("SELECT id, trang_thai_tham_gia FROM dang_ky_ca")
        for reg_id, status in cursor.fetchall():
            new_status = migrate_status_names(status)
            cursor.execute("UPDATE session_registrations SET status = ? WHERE id = ?", (new_status, reg_id))
        
        print("✅ Session Registrations migrated")
    
    # Migrate Session Entries (vao_ca -> session_entries)
    if 'vao_ca' in existing_tables:
        cursor.execute('''
            INSERT INTO session_entries (
                id, user_id, lab_session_id, entry_time, exit_time, results,
                score, teacher_comment, submitted_files, submission_status,
                submitted_at, seat_assignment
            )
            SELECT 
                id, nguoi_dung_ma, ca_thuc_hanh_ma, thoi_gian_vao, thoi_gian_ra, ket_qua,
                diem_so, nhan_xet_gv, tep_nop_bai, trang_thai_nop,
                thoi_gian_nop, vi_tri_ngoi
            FROM vao_ca
        ''')
        print("✅ Session Entries migrated")
    
    # Migrate System Settings (cai_dat_he_thong -> system_settings)
    if 'cai_dat_he_thong' in existing_tables:
        cursor.execute('''
            INSERT INTO system_settings (
                id, key, value, data_type, description, created_at, updated_at
            )
            SELECT 
                id, khoa, gia_tri, kieu, mo_ta, ngay_tao, ngay_cap_nhat
            FROM cai_dat_he_thong
        ''')
        print("✅ System Settings migrated")
    
    # Migrate Activity Logs (nhat_ky_hoat_dong -> activity_logs)
    if 'nhat_ky_hoat_dong' in existing_tables:
        cursor.execute('''
            INSERT INTO activity_logs (
                id, user_id, action, details, ip_address, timestamp
            )
            SELECT 
                id, nguoi_dung_ma, hanh_dong, chi_tiet, dia_chi_ip, thoi_gian
            FROM nhat_ky_hoat_dong
        ''')
        print("✅ Activity Logs migrated")
    
    # Migrate Courses (khoa_hoc -> courses)
    if 'khoa_hoc' in existing_tables:
        cursor.execute('''
            INSERT INTO courses (id, title, description, created_at)
            SELECT id, tieu_de, mo_ta, ngay_tao
            FROM khoa_hoc
        ''')
        print("✅ Courses migrated")
    
    # Migrate Lessons (bai_hoc -> lessons)
    if 'bai_hoc' in existing_tables:
        cursor.execute('''
            INSERT INTO lessons (id, title, content, course_id)
            SELECT id, tieu_de, noi_dung, khoa_hoc_ma
            FROM bai_hoc
        ''')
        print("✅ Lessons migrated")
    
    # Migrate Enrollments (ghi_danh -> enrollments)
    if 'ghi_danh' in existing_tables:
        cursor.execute('''
            INSERT INTO enrollments (id, user_id, course_id, enrolled_at)
            SELECT id, nguoi_dung_ma, khoa_hoc_ma, ngay_ghi_danh
            FROM ghi_danh
        ''')
        print("✅ Enrollments migrated")

def create_indexes(cursor):
    """Create performance indexes"""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
        "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
        "CREATE INDEX IF NOT EXISTS idx_lab_sessions_date ON lab_sessions(session_date)",
        "CREATE INDEX IF NOT EXISTS idx_lab_sessions_status ON lab_sessions(status)",
        "CREATE INDEX IF NOT EXISTS idx_session_registrations_user ON session_registrations(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_session_entries_user ON session_entries(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_activity_logs_user ON activity_logs(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_activity_logs_timestamp ON activity_logs(timestamp)"
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    print("✅ Performance indexes created")

def drop_old_tables(cursor):
    """Drop old Vietnamese tables after successful migration"""
    old_tables = [
        'nguoi_dung', 'ca_thuc_hanh', 'dang_ky_ca', 'vao_ca',
        'cai_dat_he_thong', 'nhat_ky_hoat_dong', 'khoa_hoc', 
        'bai_hoc', 'ghi_danh', 'sinh_vien'
    ]
    
    for table in old_tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"✅ Dropped old table: {table}")
        except Exception as e:
            print(f"⚠️  Warning: Could not drop table {table}: {e}")

def main():
    """Main migration function"""
    db_path = "instance/app.db"
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please make sure the app.db file exists.")
        return False
    
    # Create backup
    backup_path = backup_database(db_path)
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Starting database migration...")
        
        # Create new English schema
        create_english_schema(cursor)
        
        # Migrate data
        migrate_data(cursor)
        
        # Create indexes
        create_indexes(cursor)
        
        # Commit changes
        conn.commit()
        
        print("\n✅ Migration completed successfully!")
        print("📝 Summary:")
        print("   - Database backed up")
        print("   - English schema created")
        print("   - Data migrated to new tables")
        print("   - Performance indexes created")
        
        # Ask if user wants to drop old tables
        drop_old = input("\n🗑️  Do you want to drop old Vietnamese tables? (y/N): ").lower().strip()
        if drop_old in ['y', 'yes']:
            drop_old_tables(cursor)
            conn.commit()
            print("✅ Old tables removed")
        else:
            print("ℹ️  Old tables preserved for safety")
        
        conn.close()
        
        print(f"\n🎉 Migration completed! Backup saved at: {backup_path}")
        print("⚠️  Please test the application thoroughly before removing the backup.")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print(f"🔄 Restoring backup from: {backup_path}")
        shutil.copy2(backup_path, db_path)
        print("✅ Database restored from backup")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
