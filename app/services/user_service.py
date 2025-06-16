"""
User Service
===========

Service để xử lý logic liên quan đến người dùng.
Tách biệt business logic khỏi routes và API endpoints.
"""

from flask_login import current_user
from werkzeug.security import check_password_hash, generate_password_hash
from .base_service import BaseService, ServiceError
from ..models import NguoiDung, db
from ..cache.cached_queries import invalidate_user_caches
from sqlalchemy import or_
from typing import Dict, Any, Optional, List, Tuple, Union
import re

class UserService(BaseService):
    """Service xử lý logic người dùng"""
    
    def __init__(self):
        super().__init__()
        self.model = NguoiDung
    
    def get_user_by_id(self, user_id: int) -> Optional[NguoiDung]:
        """Lấy user theo ID"""
        try:
            return self.model.query.get(user_id)
        except Exception as e:
            self.logger.error(f"Error getting user by ID {user_id}: {str(e)}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[NguoiDung]:
        """Lấy user theo email"""
        try:
            return self.model.query.filter_by(email=email).first()
        except Exception as e:
            self.logger.error(f"Error getting user by email {email}: {str(e)}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[NguoiDung]:
        """Lấy user theo username"""
        try:
            return self.model.query.filter_by(ten_nguoi_dung=username).first()
        except Exception as e:
            self.logger.error(f"Error getting user by username {username}: {str(e)}")
            return None
    
    def create_user(self, data: Dict) -> Tuple[Dict, int]:
        """Tạo user mới"""
        try:
            # Validate required fields
            required_fields = ['ten_nguoi_dung', 'email', 'mat_khau']
            self.validate_required_fields(data, required_fields)
            
            # Validate email format
            if not self._validate_email(data['email']):
                raise ServiceError("Email không hợp lệ", 400)
            
            # Check for existing user
            if self.get_user_by_email(data['email']):
                raise ServiceError("Email đã tồn tại", 409)
            
            if self.get_user_by_username(data['ten_nguoi_dung']):
                raise ServiceError("Tên người dùng đã tồn tại", 409)
            
            # Create user
            user_data = {
                'ten_nguoi_dung': data['ten_nguoi_dung'],
                'email': data['email'],
                'vai_tro': data.get('vai_tro', 'nguoi_dung'),
                'bio': data.get('bio', '')
            }
            
            user = self.create_model_instance(self.model, user_data)
            user.dat_mat_khau(data['mat_khau'])
            
            self.db.session.add(user)
            self.safe_commit()
            
            # Log activity and invalidate caches
            self.log_user_activity(user.id, "Tạo tài khoản", f"Tạo tài khoản {user.ten_nguoi_dung}")
            self.invalidate_caches(['users', 'user_stats'])
            invalidate_user_caches()
            
            return self.success_response(
                "Tạo người dùng thành công",
                {
                    'user': {
                        'id': user.id,
                        'ten_nguoi_dung': user.ten_nguoi_dung,
                        'email': user.email,
                        'vai_tro': user.vai_tro
                    }
                }
            )
            
        except ServiceError:
            raise
        except Exception as e:
            return self.handle_database_error(e, "tạo người dùng")
    
    def update_user_profile(self, user_id: int, data: Dict) -> Tuple[Dict, int]:
        """Cập nhật profile user"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise ServiceError("Người dùng không tồn tại", 404)
            
            # Check email uniqueness if changed
            if 'email' in data and data['email'] != user.email:
                if self.get_user_by_email(data['email']):
                    raise ServiceError("Email đã tồn tại", 409)
                
                if not self._validate_email(data['email']):
                    raise ServiceError("Email không hợp lệ", 400)
            
            # Check username uniqueness if changed
            if 'ten_nguoi_dung' in data and data['ten_nguoi_dung'] != user.ten_nguoi_dung:
                if self.get_user_by_username(data['ten_nguoi_dung']):
                    raise ServiceError("Tên người dùng đã tồn tại", 409)
            
            # Update user
            allowed_fields = ['ten_nguoi_dung', 'email', 'bio']
            update_data = {k: v for k, v in data.items() if k in allowed_fields}
            
            self.update_model_instance(user, update_data)
            self.safe_commit()
            
            # Log activity and invalidate caches
            self.log_user_activity(user_id, "Cập nhật hồ sơ", "Cập nhật thông tin hồ sơ cá nhân")
            self.invalidate_caches(user_id=user_id)
            
            return self.success_response(
                "Cập nhật hồ sơ thành công",
                {
                    'user': {
                        'id': user.id,
                        'ten_nguoi_dung': user.ten_nguoi_dung,
                        'email': user.email,
                        'bio': getattr(user, 'bio', '')
                    }
                }
            )
            
        except ServiceError:
            raise
        except Exception as e:
            return self.handle_database_error(e, "cập nhật hồ sơ")
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> Tuple[Dict, int]:
        """Đổi mật khẩu"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                raise ServiceError("Người dùng không tồn tại", 404)
            
            # Verify current password
            if not user.kiem_tra_mat_khau(current_password):
                raise ServiceError("Mật khẩu hiện tại không đúng", 400)
            
            # Validate new password
            if len(new_password) < 6:
                raise ServiceError("Mật khẩu mới phải có ít nhất 6 ký tự", 400)
            
            # Update password
            user.dat_mat_khau(new_password)
            self.safe_commit()
            
            # Log activity
            self.log_user_activity(user_id, "Đổi mật khẩu", "Đã thay đổi mật khẩu")
            
            return self.success_response("Đổi mật khẩu thành công")
            
        except ServiceError:
            raise
        except Exception as e:
            return self.handle_database_error(e, "đổi mật khẩu")
    
    def get_user_statistics(self, user_id: int) -> Tuple[Dict, int]:
        """Lấy thống kê user"""
        try:
            from ..models import DangKyCa, VaoCa, CaThucHanh
            from datetime import datetime
            
            user = self.get_user_by_id(user_id)
            if not user:
                raise ServiceError("Người dùng không tồn tại", 404)
            
            # Calculate statistics
            total_sessions = DangKyCa.query.filter_by(nguoi_dung_ma=user_id).count()
            completed_sessions = VaoCa.query.filter_by(nguoi_dung_ma=user_id)\
                                          .filter(VaoCa.thoi_gian_ra.isnot(None)).count()
            
            # Calculate total hours
            total_hours = 0
            lab_entries = VaoCa.query.filter_by(nguoi_dung_ma=user_id)\
                                   .filter(VaoCa.thoi_gian_ra.isnot(None)).all()
            for entry in lab_entries:
                if entry.thoi_gian_vao and entry.thoi_gian_ra:
                    duration = entry.thoi_gian_ra - entry.thoi_gian_vao
                    total_hours += duration.total_seconds() / 3600
            
            # Days since joined
            days_since_joined = 0
            if hasattr(user, 'ngay_tao') and user.ngay_tao:
                days_since_joined = (datetime.utcnow() - user.ngay_tao).days
            
            return self.success_response(
                "Lấy thống kê thành công",
                {
                    'statistics': {
                        'total_sessions': total_sessions,
                        'completed_sessions': completed_sessions,
                        'total_hours': round(total_hours, 1),
                        'days_since_joined': days_since_joined
                    }
                }
            )
            
        except ServiceError:
            raise
        except Exception as e:
            self.logger.error(f"Error getting user statistics: {str(e)}")
            return self.error_response("Lỗi lấy thống kê người dùng", 500)
    
    def get_users_list(self, page: int = 1, per_page: int = 20, filters: Optional[Dict] = None) -> Tuple[Dict, int]:
        """Lấy danh sách users với pagination"""
        try:
            query = NguoiDung.query
            
            # Apply filters
            if filters:
                if filters.get('vai_tro'):
                    query = query.filter(NguoiDung.vai_tro == filters['vai_tro'])
                
                if filters.get('search'):
                    search_term = f"%{filters['search']}%"
                    query = query.filter(
                        or_(
                            NguoiDung.ten_nguoi_dung.like(search_term),  # type: ignore
                            NguoiDung.email.like(search_term)  # type: ignore
                        )
                    )
            
            # Order by creation date
            query = query.order_by(NguoiDung.ngay_tao.desc())
            
            # Paginate
            result = self.paginate_query(query, page, per_page)
            
            return self.success_response(
                "Lấy danh sách người dùng thành công",
                result
            )
            
        except Exception as e:
            self.logger.error(f"Error getting users list: {str(e)}")
            return self.error_response("Lỗi lấy danh sách người dùng", 500)
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
