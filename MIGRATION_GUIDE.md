# Database Migration: Vietnamese to English

## Overview

This migration converts the Lab Manager database from Vietnamese naming conventions to English naming conventions, making the codebase more internationally accessible and maintainable.

## Changes Made

### Table Name Mapping

| Vietnamese Table | English Table | Description |
|------------------|---------------|-------------|
| `nguoi_dung` | `users` | User accounts and authentication |
| `ca_thuc_hanh` | `lab_sessions` | Laboratory sessions management |
| `dang_ky_ca` | `session_registrations` | User registrations for lab sessions |
| `vao_ca` | `session_entries` | Session entry/exit tracking |
| `cai_dat_he_thong` | `system_settings` | System configuration settings |
| `nhat_ky_hoat_dong` | `activity_logs` | System activity logging |
| `khoa_hoc` | `courses` | Course management |
| `bai_hoc` | `lessons` | Individual lessons within courses |
| `ghi_danh` | `enrollments` | Course enrollment tracking |

### Field Name Mapping

#### Users Table
| Vietnamese Field | English Field | Type | Description |
|------------------|---------------|------|-------------|
| `ten_nguoi_dung` | `username` | VARCHAR(80) | User login name |
| `mat_khau_hash` | `password_hash` | VARCHAR(256) | Hashed password |
| `vai_tro` | `role` | VARCHAR(20) | User role (user, admin, system_admin) |
| `ngay_tao` | `created_at` | DATETIME | Account creation date |

#### Lab Sessions Table
| Vietnamese Field | English Field | Type | Description |
|------------------|---------------|------|-------------|
| `tieu_de` | `title` | VARCHAR(100) | Session title |
| `mo_ta` | `description` | TEXT | Session description |
| `ngay` | `session_date` | DATE | Session date |
| `gio_bat_dau` | `start_time` | DATETIME | Session start time |
| `gio_ket_thuc` | `end_time` | DATETIME | Session end time |
| `dia_diem` | `location` | VARCHAR(100) | Session location |
| `so_luong_toi_da` | `max_participants` | INTEGER | Maximum participants |
| `dang_hoat_dong` | `is_active` | BOOLEAN | Active status |
| `ma_xac_thuc` | `verification_code` | VARCHAR(10) | Entry verification code |
| `nguoi_tao_ma` | `created_by` | INTEGER | Creator user ID |
| `anh_bia` | `cover_image` | VARCHAR(255) | Session cover image |
| `muc_do_kho` | `difficulty_level` | VARCHAR(20) | Difficulty (easy, medium, hard) |
| `yeu_cau_thiet_bi` | `required_equipment` | TEXT | Required equipment (JSON) |
| `cho_phep_dang_ky_tre` | `allow_late_registration` | BOOLEAN | Allow late registration |
| `tu_dong_xac_nhan` | `auto_approve` | BOOLEAN | Auto-approve registrations |
| `thong_bao_truoc` | `notification_minutes` | INTEGER | Notification timing |
| `trang_thai` | `status` | VARCHAR(20) | Session status |
| `diem_so_toi_da` | `max_score` | INTEGER | Maximum score |
| `thoi_gian_lam_bai` | `time_limit_minutes` | INTEGER | Time limit in minutes |

### Role Value Mapping

| Vietnamese Role | English Role | Description |
|-----------------|--------------|-------------|
| `quan_tri_he_thong` | `system_admin` | System Administrator (Level 3) |
| `quan_tri_vien` | `admin` | Administrator (Level 2) |
| `nguoi_dung` | `user` | Regular User (Level 1) |

### Status Value Mapping

| Vietnamese Status | English Status | Description |
|-------------------|----------------|-------------|
| `da_dang_ky` | `registered` | Successfully registered |
| `da_tham_gia` | `attended` | Attended session |
| `vang_mat` | `absent` | Absent from session |
| `huy_bo` | `cancelled` | Registration cancelled |
| `dang_cho` | `pending` | Pending approval |

## Removed Fields

The following fields were identified as unnecessary and removed during migration:

### From Lab Sessions (`ca_thuc_hanh`)
- `yeu_cau_truoc` - Prerequisites (redundant with description)
- `ket_qua_mong_doi` - Expected outcomes (redundant with description)
- `ghi_chu_nang_cao` - Advanced notes (consolidated into `internal_notes`)
- `thoi_gian_dong_dang_ky` - Registration closing time (calculated based on session start time)

### From Equipment Tables
- `phong_thuc_hanh` - Lab room (consolidated into main `location` field)
- `ghi_chu` - Generic notes field (replaced with specific purpose fields)

### From Session Materials
- `kich_thuoc` - File size field (automatically calculated)
- `loai_file` - File type (automatically detected from extension)

## New Enhanced Features

### Session Templates
- Reusable templates for quick session creation
- Default settings and configurations
- Template management and version control

### Equipment Management
- Comprehensive equipment tracking
- Booking and reservation system
- Availability status management

### Enhanced Notifications
- Rich notification system with types
- Read/unread status tracking
- Targeted notifications by user role

### Session Ratings
- Student feedback collection
- 5-star rating system
- Comment and review management

## Migration Process

1. **Backup Creation**: Automatic backup of existing database
2. **Schema Creation**: Create new English table structure
3. **Data Migration**: Transfer data with field mapping and value conversion
4. **Index Creation**: Add performance indexes
5. **Validation**: Verify data integrity
6. **Cleanup**: Optional removal of old Vietnamese tables

## Files Updated

### Core Files
- `app/models_english.py` - New English model definitions
- `migrate_to_english.py` - Migration script
- `README.md` - Updated documentation with English schema

### Migration Benefits

1. **International Accessibility**: English naming makes the codebase accessible to international developers
2. **Code Clarity**: Clear, descriptive field names improve code readability
3. **Maintenance**: Easier maintenance and debugging with standard naming conventions
4. **Documentation**: Better alignment with English documentation and comments
5. **Collaboration**: Facilitates collaboration with international teams
6. **Performance**: Optimized database structure with proper indexing

## Post-Migration Steps

1. **Update Application Code**: Modify application code to use new English model classes
2. **Update Templates**: Update HTML templates to use new field names
3. **Test Thoroughly**: Comprehensive testing of all functionality
4. **Update Documentation**: Ensure all documentation reflects new structure
5. **Deploy Gradually**: Consider staged deployment for production systems

## Rollback Plan

If issues arise after migration:

1. The migration script creates automatic backups
2. Restore from backup: `cp app.db.backup_YYYYMMDD_HHMMSS instance/app.db`
3. Restart application with original models
4. Investigate and fix issues before re-attempting migration

## Support

For issues with the migration process:

1. Check the backup file exists and is accessible
2. Verify database permissions and file system access
3. Review migration logs for specific error messages
4. Test migration on a copy of the database first
5. Consider manual data verification after migration

---

**Note**: This migration maintains all existing functionality while providing a cleaner, more maintainable database structure with English naming conventions.
