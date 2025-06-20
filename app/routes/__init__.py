from .admin.admin_main import admin_bp
from .user.user_main import user_bp
from .auth import auth_bp
from .lab import lab_bp
from .search import search_bp
from .system_admin.system_admin import system_admin_bp

# Đăng ký tất cả blueprints theo thứ tự ưu tiên
__all__ = [
    'system_admin_bp',  # Quyền cao nhất
    'admin_bp',         # Quyền admin 
    'user_bp',          # Quyền user cơ bản
    'auth_bp',
    'lab_bp', 
    'search_bp'
]
