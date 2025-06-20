#!/usr/bin/env python3
"""
Code Update Script: Convert Vietnamese imports to English
Updates Python files to use new English model names
"""

import os
import re
import shutil
from datetime import datetime

# Mapping of old Vietnamese names to new English names
MODEL_MAPPING = {
    # Models
    'NguoiDung': 'User',
    'CaThucHanh': 'LabSession', 
    'DangKyCa': 'SessionRegistration',
    'VaoCa': 'SessionEntry',
    'CaiDatHeThong': 'SystemSetting',
    'NhatKyHoatDong': 'ActivityLog',
    'KhoaHoc': 'Course',
    'BaiHoc': 'Lesson',
    'GhiDanh': 'Enrollment',
    'SinhVien': 'Student',  # if still used
    
    # New enhanced models
    'MauCaThucHanh': 'SessionTemplate',
    'TaiLieuCa': 'SessionMaterial',
    'ThietBi': 'Equipment',
    'DatThietBi': 'EquipmentBooking',
    'DanhGiaCa': 'SessionRating',
    'ThongBao': 'Notification'
}

# Field name mappings for common fields
FIELD_MAPPING = {
    # User fields
    'ten_nguoi_dung': 'username',
    'mat_khau_hash': 'password_hash',
    'vai_tro': 'role',
    'ngay_tao': 'created_at',
    
    # Lab session fields
    'tieu_de': 'title',
    'mo_ta': 'description',
    'ngay': 'session_date',
    'gio_bat_dau': 'start_time',
    'gio_ket_thuc': 'end_time',
    'dia_diem': 'location',
    'so_luong_toi_da': 'max_participants',
    'dang_hoat_dong': 'is_active',
    'ma_xac_thuc': 'verification_code',
    'nguoi_tao_ma': 'created_by',
    'anh_bia': 'cover_image',
    'muc_do_kho': 'difficulty_level',
    
    # Common fields
    'nguoi_dung_ma': 'user_id',
    'ca_thuc_hanh_ma': 'lab_session_id',
    'thoi_gian': 'timestamp',
    'hanh_dong': 'action',
    'chi_tiet': 'details',
    'dia_chi_ip': 'ip_address'
}

# Role value mappings
ROLE_MAPPING = {
    'quan_tri_he_thong': 'system_admin',
    'quan_tri_vien': 'admin', 
    'nguoi_dung': 'user'
}

def backup_file(file_path):
    """Create backup of file before modification"""
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    return backup_path

def update_imports(content):
    """Update import statements to use English models"""
    # Update model imports
    for old_name, new_name in MODEL_MAPPING.items():
        # Replace in import statements
        content = re.sub(
            rf'\bfrom\s+app\.models\s+import\s+([^,\n]*?)({old_name})([^,\n]*?)(?=\n|$)',
            rf'from app.models_english import \1{new_name}\3',
            content
        )
        
        # Replace standalone imports
        content = re.sub(
            rf'\bimport\s+.*{old_name}.*',
            lambda m: m.group(0).replace(old_name, new_name),
            content
        )
    
    # Update models import to models_english
    content = re.sub(
        r'from\s+app\.models\s+import',
        'from app.models_english import',
        content
    )
    
    return content

def update_model_references(content):
    """Update model class references in code"""
    for old_name, new_name in MODEL_MAPPING.items():
        # Replace class instantiations
        content = re.sub(rf'\b{old_name}\(', f'{new_name}(', content)
        
        # Replace class references
        content = re.sub(rf'\b{old_name}\.', f'{new_name}.', content)
        
        # Replace in type hints
        content = re.sub(rf':\s*{old_name}\b', f': {new_name}', content)
    
    return content

def update_field_references(content):
    """Update field name references"""
    for old_field, new_field in FIELD_MAPPING.items():
        # Replace field access patterns
        content = re.sub(rf'\.{old_field}\b', f'.{new_field}', content)
        
        # Replace in filter_by and other query methods
        content = re.sub(rf'{old_field}=', f'{new_field}=', content)
        
        # Replace in form field names
        content = re.sub(rf'["\'{old_field}["\']', f'"{new_field}"', content)
    
    return content

def update_role_values(content):
    """Update role values to English"""
    for old_role, new_role in ROLE_MAPPING.items():
        content = re.sub(rf'["\'{old_role}["\']', f'"{new_role}"', content)
    
    return content

def update_table_names(content):
    """Update table name references in raw SQL"""
    table_mapping = {
        'nguoi_dung': 'users',
        'ca_thuc_hanh': 'lab_sessions',
        'dang_ky_ca': 'session_registrations',
        'vao_ca': 'session_entries',
        'cai_dat_he_thong': 'system_settings',
        'nhat_ky_hoat_dong': 'activity_logs',
        'khoa_hoc': 'courses',
        'bai_hoc': 'lessons',
        'ghi_danh': 'enrollments'
    }
    
    for old_table, new_table in table_mapping.items():
        content = re.sub(rf'\b{old_table}\b', new_table, content)
    
    return content

def process_file(file_path):
    """Process a single Python file"""
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all transformations
        content = update_imports(content)
        content = update_model_references(content)
        content = update_field_references(content)
        content = update_role_values(content)
        content = update_table_names(content)
        
        # Only write if content changed
        if content != original_content:
            # Create backup
            backup_path = backup_file(file_path)
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Updated: {file_path}")
            print(f"   Backup: {backup_path}")
            return True
        else:
            print(f"ℹ️  No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def find_python_files(directory):
    """Find all Python files in directory and subdirectories"""
    python_files = []
    
    for root, dirs, files in os.walk(directory):
        # Skip certain directories
        skip_dirs = ['.git', '__pycache__', '.venv', 'venv', 'migrations', 'instance']
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def main():
    """Main function to update all Python files"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    print("🔄 Starting code migration to English models...")
    print(f"📁 Project root: {project_root}")
    
    # Find all Python files
    python_files = find_python_files(project_root)
    
    if not python_files:
        print("❌ No Python files found!")
        return False
    
    print(f"📄 Found {len(python_files)} Python files")
    
    # Ask for confirmation
    proceed = input("\n🤔 Do you want to proceed with updating all files? (y/N): ").lower().strip()
    if proceed not in ['y', 'yes']:
        print("❌ Operation cancelled")
        return False
    
    # Process each file
    updated_count = 0
    error_count = 0
    
    for file_path in python_files:
        try:
            if process_file(file_path):
                updated_count += 1
        except Exception as e:
            print(f"❌ Failed to process {file_path}: {e}")
            error_count += 1
    
    # Summary
    print(f"\n📊 Migration Summary:")
    print(f"   📄 Total files processed: {len(python_files)}")
    print(f"   ✅ Files updated: {updated_count}")
    print(f"   ℹ️  Files unchanged: {len(python_files) - updated_count - error_count}")
    print(f"   ❌ Errors: {error_count}")
    
    if updated_count > 0:
        print(f"\n🎉 Code migration completed!")
        print(f"⚠️  Please test your application thoroughly:")
        print(f"   1. Run all tests")
        print(f"   2. Check for any remaining Vietnamese references")
        print(f"   3. Update any custom SQL queries manually")
        print(f"   4. Verify all functionality works correctly")
    
    return error_count == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
