"""
Admin Service
=============

Service để xử lý logic quản trị hệ thống.
"""

from .base_service import BaseService, ServiceError
from ..models import NguoiDung, CaThucHanh, DangKyCa, NhatKyHoatDong, CaiDatHeThong, db
from ..cache.cached_queries import invalidate_user_caches, invalidate_session_caches, invalidate_activity_caches
from sqlalchemy import func, desc
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta

class AdminService(BaseService):
    """Service xử lý logic quản trị hệ thống"""
    
    def __init__(self):
        super().__init__()
    
    def get_dashboard_stats(self) -> Tuple[Dict, int]:
        """Lấy thống kê cho dashboard admin"""
        try:
            # Basic counts
            total_users = NguoiDung.query.count()
            total_sessions = CaThucHanh.query.count()
            active_sessions = CaThucHanh.query.filter_by(dang_hoat_dong=True).count()
            total_registrations = DangKyCa.query.count()
            
            # Recent activity
            recent_activities = NhatKyHoatDong.query.order_by(desc(NhatKyHoatDong.thoi_gian)).limit(10).all()
            activity_list = []
            for activity in recent_activities:
                activity_list.append({
                    'id': activity.id,
                    'action': activity.hanh_dong,
                    'details': activity.chi_tiet,
                    'timestamp': activity.thoi_gian.isoformat() if activity.thoi_gian else None,
                    'user': activity.nguoi_dung.ten_nguoi_dung if activity.nguoi_dung else 'System'
                })
            
            # User roles distribution
            user_roles = db.session.query(
                NguoiDung.vai_tro,
                func.count(NguoiDung.id).label('count')
            ).group_by(NguoiDung.vai_tro).all()
            
            roles_stats = {}
            for role, count in user_roles:
                roles_stats[role] = count
            
            return self.success_response(
                "Lấy thống kê dashboard thành công",
                {
                    'stats': {
                        'total_users': total_users,
                        'total_sessions': total_sessions,
                        'active_sessions': active_sessions,
                        'total_registrations': total_registrations,
                        'user_roles': roles_stats
                    },
                    'recent_activities': activity_list
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error getting dashboard stats: {str(e)}")
            return self.error_response("Lỗi lấy thống kê dashboard", 500)
    
    def manage_user_role(self, user_id: int, new_role: str, admin_id: int) -> Tuple[Dict, int]:
        """Thay đổi vai trò người dùng"""
        try:
            # Validate role
            valid_roles = ['nguoi_dung', 'quan_tri_vien', 'quan_tri_he_thong']
            if new_role not in valid_roles:
                raise ServiceError("Vai trò không hợp lệ", 400)
            
            user = NguoiDung.query.get(user_id)
            if not user:
                raise ServiceError("Người dùng không tồn tại", 404)
            
            old_role = user.vai_tro
            user.vai_tro = new_role
            self.safe_commit()
            
            # Log activity
            self.log_user_activity(
                admin_id, 
                "Thay đổi vai trò người dùng", 
                f"Thay đổi vai trò của {user.ten_nguoi_dung} từ {old_role} thành {new_role}"
            )
            
            # Invalidate caches
            invalidate_user_caches()
            
            return self.success_response(f"Đã thay đổi vai trò người dùng thành {new_role}")
            
        except ServiceError:
            raise
        except Exception as e:
            return self.handle_database_error(e, "thay đổi vai trò người dùng")
    
    def delete_user(self, user_id: int, admin_id: int) -> Tuple[Dict, int]:
        """Xóa người dùng"""
        try:
            user = NguoiDung.query.get(user_id)
            if not user:
                raise ServiceError("Người dùng không tồn tại", 404)
            
            # Prevent deleting system admin
            if user.vai_tro == 'quan_tri_he_thong':
                raise ServiceError("Không thể xóa quản trị hệ thống", 403)
            
            username = user.ten_nguoi_dung
            self.db.session.delete(user)
            self.safe_commit()
            
            # Log activity
            self.log_user_activity(admin_id, "Xóa người dùng", f"Đã xóa người dùng {username}")
            
            # Invalidate caches
            invalidate_user_caches()
            
            return self.success_response(f"Đã xóa người dùng {username}")
            
        except ServiceError:
            raise
        except Exception as e:
            return self.handle_database_error(e, "xóa người dùng")
    
    def get_system_settings(self) -> Tuple[Dict, int]:
        """Lấy cài đặt hệ thống"""
        try:
            settings = CaiDatHeThong.query.all()
            settings_dict = {}
            
            for setting in settings:
                if setting.kieu == 'boolean':
                    settings_dict[setting.khoa] = setting.gia_tri.lower() in ('true', '1', 'yes')
                elif setting.kieu == 'integer':
                    settings_dict[setting.khoa] = int(setting.gia_tri) if setting.gia_tri else 0
                elif setting.kieu == 'float':
                    settings_dict[setting.khoa] = float(setting.gia_tri) if setting.gia_tri else 0.0
                else:
                    settings_dict[setting.khoa] = setting.gia_tri
            
            return self.success_response(
                "Lấy cài đặt hệ thống thành công",
                {'settings': settings_dict}
            )
            
        except Exception as e:
            self.logger.error(f"Error getting system settings: {str(e)}")
            return self.error_response("Lỗi lấy cài đặt hệ thống", 500)
    
    def update_system_setting(self, key: str, value: Any, admin_id: int) -> Tuple[Dict, int]:
        """Cập nhật cài đặt hệ thống"""
        try:
            # Determine value type
            value_type = "string"
            if isinstance(value, bool):
                value_type = "boolean"
            elif isinstance(value, int):
                value_type = "integer"
            elif isinstance(value, float):
                value_type = "float"
            
            CaiDatHeThong.dat_gia_tri(key, value, value_type)
            
            # Log activity
            self.log_user_activity(admin_id, "Cập nhật cài đặt hệ thống", f"Cập nhật {key} = {value}")
            
            return self.success_response(f"Đã cập nhật cài đặt {key}")
            
        except Exception as e:
            return self.handle_database_error(e, "cập nhật cài đặt hệ thống")
