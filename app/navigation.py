"""
Navigation helper để quản lý menu theo quyền hạn
"""
from flask_login import current_user

class NavigationManager:
    """Quản lý navigation menu theo phân quyền kế thừa"""
    
    @staticmethod
    def get_user_menu():
        """Menu cơ bản cho tất cả user đã đăng nhập"""
        return [
            {'name': 'Dashboard', 'url': 'user.dashboard', 'icon': 'fas fa-tachometer-alt'},
            {'name': 'Hồ sơ', 'url': 'user.profile', 'icon': 'fas fa-user'},
            {'name': 'Cài đặt', 'url': 'user.settings', 'icon': 'fas fa-cog'},
            {'name': 'Ca thực hành', 'url': 'lab.my_lab_sessions', 'icon': 'fas fa-flask'},
        ]
    
    @staticmethod
    def get_admin_menu():
        """Menu admin kế thừa từ user menu và thêm quyền admin"""
        menu = NavigationManager.get_user_menu()
        admin_items = [
            {'name': 'Quản lý người dùng', 'url': 'admin.users', 'icon': 'fas fa-users'},
            {'name': 'Quản lý ca thực hành', 'url': 'admin.lab_sessions', 'icon': 'fas fa-calendar-alt'},
            {'name': 'Báo cáo', 'url': 'admin.reports', 'icon': 'fas fa-chart-bar'},
            {'name': 'Admin Dashboard', 'url': 'admin.admin_dashboard', 'icon': 'fas fa-tachometer-alt'},
        ]
        return menu + admin_items
    
    @staticmethod  
    def get_system_admin_menu():
        """Menu system admin kế thừa từ admin menu và thêm quyền system admin"""
        menu = NavigationManager.get_admin_menu()
        system_admin_items = [
            {'name': 'Cấu hình hệ thống', 'url': 'system_admin.system_config', 'icon': 'fas fa-server'},
            {'name': 'Quản lý CSDL', 'url': 'system_admin.database_management', 'icon': 'fas fa-database'},
            {'name': 'Giám sát hệ thống', 'url': 'system_admin.system_monitoring', 'icon': 'fas fa-chart-line'},
            {'name': 'Sao lưu & Phục hồi', 'url': 'system_admin.backup_restore', 'icon': 'fas fa-save'},
            {'name': 'System Dashboard', 'url': 'system_admin.system_dashboard', 'icon': 'fas fa-crown'},
        ]
        return menu + system_admin_items
    
    @staticmethod
    def get_current_user_menu():
        """Lấy menu phù hợp với quyền hạn của user hiện tại"""
        if not current_user.is_authenticated:
            return []
        
        if hasattr(current_user, 'is_system_admin') and current_user.is_system_admin():
            return NavigationManager.get_system_admin_menu()
        elif hasattr(current_user, 'is_admin') and current_user.is_admin():
            return NavigationManager.get_admin_menu()
        else:
            return NavigationManager.get_user_menu()
    
    @staticmethod
    def get_breadcrumb(endpoint):
        """Tạo breadcrumb navigation"""
        breadcrumbs = []
        
        if endpoint.startswith('system_admin'):
            breadcrumbs = [
                {'name': 'Home', 'url': 'index'},
                {'name': 'System Admin', 'url': 'system_admin.system_dashboard'}
            ]
        elif endpoint.startswith('admin'):
            breadcrumbs = [
                {'name': 'Home', 'url': 'index'},
                {'name': 'Admin', 'url': 'admin.admin_dashboard'}
            ]
        elif endpoint.startswith('user'):
            breadcrumbs = [
                {'name': 'Home', 'url': 'index'},
                {'name': 'User', 'url': 'user.dashboard'}
            ]
        
        return breadcrumbs
