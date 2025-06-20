"""
Base routes cho hệ thống phân quyền kế thừa
System Admin > Admin > User
"""
from flask import Blueprint
from flask_login import login_required
from ..decorators import user_required, admin_required, system_admin_required

class UserRouteMixin:
    """Mixin cho user routes cơ bản"""
    
    def register_user_routes(self, bp):
        """Đăng ký các route cơ bản cho user"""
        
        @bp.route('/profile')
        @login_required
        @user_required
        def profile():
            return self.get_profile()
        
        @bp.route('/settings')
        @login_required
        @user_required  
        def settings():
            return self.get_settings()
    
    def get_profile(self):
        """Override this in implementation"""
        raise NotImplementedError
    
    def get_settings(self):
        """Override this in implementation"""
        raise NotImplementedError

class AdminRouteMixin(UserRouteMixin):
    """Mixin cho admin routes, kế thừa user routes"""
    
    def register_admin_routes(self, bp):
        """Đăng ký các route admin"""
        # Kế thừa user routes
        self.register_user_routes(bp)
        
        @bp.route('/users')
        @login_required
        @admin_required
        def manage_users():
            return self.get_user_management()
        
        @bp.route('/reports')
        @login_required
        @admin_required
        def reports():
            return self.get_reports()
        
        @bp.route('/lab-sessions')
        @login_required
        @admin_required
        def manage_lab_sessions():
            return self.get_lab_session_management()
    
    def get_user_management(self):
        """Override this in implementation"""
        raise NotImplementedError
    
    def get_reports(self):
        """Override this in implementation"""
        raise NotImplementedError
    
    def get_lab_session_management(self):
        """Override this in implementation"""
        raise NotImplementedError

class SystemAdminRouteMixin(AdminRouteMixin):
    """Mixin cho system admin routes, kế thừa admin routes"""
    
    def register_system_admin_routes(self, bp):
        """Đăng ký các route system admin"""
        # Kế thừa admin routes (và user routes)
        self.register_admin_routes(bp)
        
        @bp.route('/system-config')
        @login_required
        @system_admin_required
        def system_config():
            return self.get_system_config()
        
        @bp.route('/database-management')
        @login_required
        @system_admin_required
        def database_management():
            return self.get_database_management()
        
        @bp.route('/system-monitoring')
        @login_required
        @system_admin_required
        def system_monitoring():
            return self.get_system_monitoring()
        
        @bp.route('/backup-restore')
        @login_required
        @system_admin_required
        def backup_restore():
            return self.get_backup_restore()
    
    def get_system_config(self):
        """Override this in implementation"""
        raise NotImplementedError
    
    def get_database_management(self):
        """Override this in implementation"""
        raise NotImplementedError
    
    def get_system_monitoring(self):
        """Override this in implementation"""
        raise NotImplementedError
    
    def get_backup_restore(self):
        """Override this in implementation"""
        raise NotImplementedError
