import os
import sys
import time
from dotenv import load_dotenv

# Import app sau khi load environment variables
from app import create_app

def run_system_checks():
    """Chạy các kiểm tra hệ thống trước khi khởi động ứng dụng"""
    print("🔍 Bắt đầu kiểm tra hệ thống...")
    
    # 1. Kiểm tra phiên bản Python
    print(f"✓ Python version: {sys.version}")
    if sys.version_info < (3, 8):
        print("❌ CẢNH BÁO: Python version < 3.8 có thể gây vấn đề")
    
    # 2. Kiểm tra các thư viện quan trọng
    required_packages = [
        'flask', 'flask_sqlalchemy', 'flask_login', 'flask_wtf', 
        'flask_socketio', 'werkzeug', 'sqlalchemy'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} imported successfully")
        except ImportError as e:
            print(f"❌ Lỗi import {package}: {e}")
            return False
    
    # 3. Kiểm tra biến môi trường quan trọng
    required_env_vars = ['SECRET_KEY', 'DATABASE_URL', 'FLASK_APP']
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Thiếu biến môi trường: {', '.join(missing_vars)}")
    else:
        print("✓ Tất cả biến môi trường quan trọng đã được cấu hình")
    
    # 4. Kiểm tra SECRET_KEY
    secret_key = os.getenv('SECRET_KEY')
    if secret_key:
        print(f"✓ SECRET_KEY is set: {secret_key[:10]}...")
        if len(secret_key) < 32:
            print("⚠️  CẢNH BÁO: SECRET_KEY quá ngắn, nên dài ít nhất 32 ký tự")
    
    return True

def test_app_creation():
    """Kiểm tra việc tạo ứng dụng Flask"""
    print("\n🔧 Kiểm tra tạo ứng dụng...")
    
    try:
        from app import create_app
        app, socketio = create_app()
        print("✓ Ứng dụng Flask được tạo thành công")
        
        # Kiểm tra cơ sở dữ liệu
        with app.app_context():
            from app.models import db, NguoiDung, CaiDatHeThong
            
            # Tạo bảng nếu chưa có
            db.create_all()
            print("✓ Cơ sở dữ liệu được khởi tạo thành công")
            
            # Kiểm tra kết nối database
            try:
                user_count = NguoiDung.query.count()
                print(f"✓ Kết nối database OK - Có {user_count} người dùng")
            except Exception as e:
                print(f"⚠️  Cảnh báo database: {e}")
              # Kiểm tra các route chính
            routes = [route.rule for route in app.url_map.iter_rules()]
            important_routes = {
                '/': 'Trang chủ',
                '/auth/login': 'Đăng nhập', 
                '/auth/register': 'Đăng ký',
                '/admin/': 'Admin dashboard',
                '/user/dashboard': 'User dashboard'
            }
            
            print("📋 Kiểm tra các route quan trọng:")
            for route, description in important_routes.items():
                found = any(r == route or r.startswith(route) for r in routes)
                if found:
                    print(f"  ✓ {description} ({route})")
                else:
                    # Kiểm tra pattern match linh hoạt hơn
                    pattern_found = False
                    if 'login' in route:
                        pattern_found = any('login' in r for r in routes)
                    elif 'register' in route:
                        pattern_found = any('register' in r for r in routes)
                    elif 'dashboard' in route:
                        pattern_found = any('dashboard' in r for r in routes)
                    elif route == '/admin/':
                        pattern_found = any(r.startswith('/admin') for r in routes)
                    
                    if pattern_found:
                        print(f"  ✓ {description} (pattern found)")
                    else:
                        print(f"  ⚠️  {description} không tìm thấy")
        
        return app, socketio
        
    except Exception as e:
        print(f"❌ Lỗi tạo ứng dụng: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def check_database_health():
    """Kiểm tra tình trạng cơ sở dữ liệu"""
    print("\n💾 Kiểm tra tình trạng cơ sở dữ liệu...")
    
    try:
        from app import create_app
        from app.models import db, NguoiDung, CaiDatHeThong, CaThucHanh
        
        app, _ = create_app()
        with app.app_context():
            # Kiểm tra các bảng chính
            tables_to_check = [
                ('nguoi_dung', NguoiDung),
                ('cai_dat_he_thong', CaiDatHeThong),
                ('ca_thuc_hanh', CaThucHanh)
            ]
            
            for table_name, model in tables_to_check:
                try:
                    count = model.query.count()
                    print(f"✓ Bảng {table_name}: {count} bản ghi")
                except Exception as e:
                    print(f"⚠️  Bảng {table_name}: {e}")
            
            # Kiểm tra admin user
            admin_users = NguoiDung.query.filter_by(vai_tro='quan_tri_he_thong').count()
            if admin_users > 0:
                print(f"✓ Có {admin_users} quản trị hệ thống")
            else:
                print("⚠️  Chưa có quản trị hệ thống nào")
                
    except Exception as e:
        print(f"❌ Lỗi kiểm tra database: {e}")

def check_critical_services():
    """Kiểm tra các service quan trọng"""
    print("\n⚙️  Kiểm tra các service quan trọng...")
    
    try:
        # Kiểm tra UserService
        from app.services.user_service import UserService
        user_service = UserService()
        print("✓ UserService khởi tạo thành công")
        
        # Kiểm tra Cache
        from flask import current_app
        from app import create_app
        app, _ = create_app()
        with app.app_context():
            from app.cache.cache_manager import get_cache_manager
            cache_manager = get_cache_manager()
            print("✓ Cache Manager khởi tạo thành công")
            
        # Kiểm tra Utils
        from app.utils import log_activity
        print("✓ Utils functions loaded successfully")
        
        # Kiểm tra Forms
        from app.forms import LoginForm, RegistrationForm
        print("✓ Forms loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi kiểm tra services: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_static_files():
    """Kiểm tra các file static quan trọng"""
    print("\n🎨 Kiểm tra file static...")
    
    static_files = [
        'app/static/css/base.css',
        'app/static/js/lab_sessions.js',
        'app/templates/base.html',
        'app/templates/auth/log_regis.html'
    ]
    
    for file_path in static_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"⚠️  {file_path} không tìm thấy")

def check_file_permissions():
    """Kiểm tra quyền truy cập file quan trọng"""
    print("\n🔐 Kiểm tra quyền truy cập file...")
    
    important_files = [
        'config.py',
        'app/__init__.py',
        'app/models.py',
        'requirements.txt'
    ]
    
    for file_path in important_files:
        if os.path.exists(file_path):
            if os.access(file_path, os.R_OK):
                print(f"✓ {file_path} - có quyền đọc")
            else:
                print(f"❌ {file_path} - không có quyền đọc")
        else:
            print(f"⚠️  {file_path} - file không tồn tại")
    
    # Kiểm tra thư mục instance
    instance_dir = 'instance'
    if os.path.exists(instance_dir):
        if os.access(instance_dir, os.W_OK):
            print(f"✓ {instance_dir}/ - có quyền ghi")
        else:
            print(f"❌ {instance_dir}/ - không có quyền ghi")
    else:
        print(f"⚠️  {instance_dir}/ - thư mục không tồn tại")

def perform_basic_functionality_test():
    """Thực hiện test cơ bản các chức năng"""
    print("\n🧪 Test chức năng cơ bản...")
    
    try:
        from app import create_app
        from app.models import NguoiDung, CaiDatHeThong
        
        app, _ = create_app()
        with app.app_context():
            # Test query cơ bản
            total_users = NguoiDung.query.count()
            print(f"✓ Query users: {total_users} người dùng")
            
            # Test setting system
            app_name = CaiDatHeThong.lay_gia_tri("app_name", "Lab Manager")
            print(f"✓ System settings: App name = {app_name}")
            
            # Test create user service
            from app.services.user_service import UserService
            user_service = UserService()
            
            # Test email validation
            valid_email = user_service._validate_email("test@example.com")
            invalid_email = user_service._validate_email("invalid-email")
            
            if valid_email and not invalid_email:
                print("✓ Email validation hoạt động đúng")
            else:
                print("⚠️  Email validation có vấn đề")
                
        return True
        
    except Exception as e:
        print(f"❌ Lỗi test chức năng: {e}")
        return False

# Load environment variables first, before importing anything else
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
elif os.path.exists('.env'):
    load_dotenv()

# Create Flask app instance for Flask CLI compatibility
# This makes the app available at module level for 'flask run'
app, socketio = create_app()

# Application factory function for Flask CLI
def create_app_factory():
    """Factory function for Flask CLI"""
    return create_app()[0]  # Return only the Flask app, not socketio

if __name__ == "__main__":
    print("🚀 Lab Manager - Khởi động ứng dụng")
    print("=" * 50)
    
    # Chạy tất cả các kiểm tra hệ thống
    if not run_system_checks():
        print("❌ Kiểm tra hệ thống thất bại. Dừng khởi động.")
        sys.exit(1)
    
    # Kiểm tra quyền truy cập file
    check_file_permissions()
    
    # Tạo ứng dụng và kiểm tra
    app, socketio = test_app_creation()
    if not app or not socketio:
        print("❌ Không thể tạo ứng dụng. Dừng khởi động.")
        sys.exit(1)
    
    # Kiểm tra tình trạng database
    check_database_health()
    
    # Kiểm tra các service quan trọng
    if not check_critical_services():
        print("❌ Một số service quan trọng có vấn đề. Vẫn tiếp tục khởi động...")
    
    # Kiểm tra file static
    check_static_files()
    
    # Test chức năng cơ bản
    if not perform_basic_functionality_test():
        print("❌ Test chức năng cơ bản thất bại. Vẫn tiếp tục khởi động...")
    
    print("\n" + "=" * 50)
    print("✅ Tất cả kiểm tra đều hoàn thành!")
    print(f"🌐 Ứng dụng sẽ chạy tại: http://127.0.0.1:5000")
    print("📝 Nhấn Ctrl+C để dừng server")
    print("=" * 50)
    
    # Khởi động server
    try:
        socketio.run(app, debug=True, host='127.0.0.1', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server đã được dừng bởi người dùng")
    except Exception as e:
        print(f"\n❌ Lỗi khởi động server: {e}")
        sys.exit(1)
