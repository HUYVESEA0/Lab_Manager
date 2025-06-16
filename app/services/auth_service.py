"""
Authentication Service
=====================

Service để xử lý logic xác thực và phân quyền.
"""

from .base_service import BaseService, ServiceError
from ..models import NguoiDung, db
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user
from typing import Dict, Any, Optional, Tuple
import secrets
import time

class AuthService(BaseService):
    """Service xử lý logic xác thực"""
    
    def __init__(self):
        super().__init__()
    
    def authenticate_user(self, email: str, password: str, remember_me: bool = False) -> Tuple[Dict, int]:
        """Xác thực người dùng"""
        try:
            # Find user by email
            user = NguoiDung.query.filter_by(email=email.lower().strip()).first()
            if not user:
                raise ServiceError("Email không tồn tại trong hệ thống", 401)
            
            # Check password
            if not user.kiem_tra_mat_khau(password):
                raise ServiceError("Mật khẩu không chính xác", 401)
            
            # Login user
            login_user(user, remember=remember_me)
            
            # Log activity
            self.log_user_activity(user.id, "Đăng nhập", f"Đăng nhập thành công từ IP")
            
            return self.success_response(
                "Đăng nhập thành công",
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
            return self.handle_database_error(e, "xác thực người dùng")
    
    def logout_user(self, user_id: int) -> Tuple[Dict, int]:
        """Đăng xuất người dùng"""
        try:
            # Log activity before logout
            self.log_user_activity(user_id, "Đăng xuất", "Người dùng đăng xuất")
            
            # Logout
            logout_user()
            
            return self.success_response("Đăng xuất thành công")
            
        except Exception as e:
            self.logger.error(f"Error during logout: {str(e)}")
            return self.error_response("Lỗi khi đăng xuất", 500)
    
    def register_user(self, data: Dict) -> Tuple[Dict, int]:
        """Đăng ký người dùng mới"""
        try:
            # Validate required fields
            required_fields = ['ten_nguoi_dung', 'email', 'password']
            self.validate_required_fields(data, required_fields)
            
            # Check if user exists
            if NguoiDung.query.filter_by(email=data['email'].lower().strip()).first():
                raise ServiceError("Email đã được đăng ký", 409)
            
            if NguoiDung.query.filter_by(ten_nguoi_dung=data['ten_nguoi_dung']).first():
                raise ServiceError("Tên người dùng đã tồn tại", 409)
            
            # Create user
            user = NguoiDung(
                ten_nguoi_dung=data['ten_nguoi_dung'],
                email=data['email'].lower().strip(),
                vai_tro='nguoi_dung'
            )
            user.dat_mat_khau(data['password'])
            
            self.db.session.add(user)
            self.safe_commit()
            
            # Log activity
            self.log_user_activity(user.id, "Đăng ký tài khoản", f"Tạo tài khoản mới {user.ten_nguoi_dung}")
            
            return self.success_response(
                "Đăng ký thành công",
                {
                    'user': {
                        'id': user.id,
                        'ten_nguoi_dung': user.ten_nguoi_dung,
                        'email': user.email
                    }
                }
            )
            
        except ServiceError:
            raise
        except Exception as e:
            return self.handle_database_error(e, "đăng ký người dùng")
    
    def generate_password_reset_token(self, email: str) -> Tuple[Dict, int]:
        """Tạo token đặt lại mật khẩu"""
        try:
            user = NguoiDung.query.filter_by(email=email.lower().strip()).first()
            if not user:
                # Don't reveal if email exists for security
                return self.success_response("Nếu email tồn tại, link đặt lại mật khẩu đã được gửi")
            
            # Generate token
            token = user.tao_reset_token()
            self.safe_commit()
            
            # Log activity
            self.log_user_activity(user.id, "Yêu cầu đặt lại mật khẩu", "Tạo token đặt lại mật khẩu")
            
            return self.success_response(
                "Token đặt lại mật khẩu đã được tạo",
                {'token': token}
            )
            
        except Exception as e:
            return self.handle_database_error(e, "tạo token đặt lại mật khẩu")
    
    def reset_password_with_token(self, token: str, new_password: str) -> Tuple[Dict, int]:
        """Đặt lại mật khẩu với token"""
        try:
            user = NguoiDung.verify_reset_password_token(token)
            if not user:
                raise ServiceError("Token không hợp lệ hoặc đã hết hạn", 400)
            
            # Validate password
            if len(new_password) < 6:
                raise ServiceError("Mật khẩu phải có ít nhất 6 ký tự", 400)
            
            # Update password
            user.dat_mat_khau(new_password)
            user.xoa_reset_token()
            self.safe_commit()
            
            # Log activity
            self.log_user_activity(user.id, "Đặt lại mật khẩu", "Mật khẩu đã được đặt lại thành công")
            
            return self.success_response("Mật khẩu đã được đặt lại thành công")
            
        except ServiceError:
            raise
        except Exception as e:
            return self.handle_database_error(e, "đặt lại mật khẩu")
    
    def check_user_permissions(self, user_id: int, required_role: str) -> bool:
        """Kiểm tra quyền của người dùng"""
        try:
            user = NguoiDung.query.get(user_id)
            if not user:
                return False
            
            role_hierarchy = {
                'nguoi_dung': 1,
                'quan_tri_vien': 2,
                'quan_tri_he_thong': 3
            }
            
            user_level = role_hierarchy.get(user.vai_tro, 0)
            required_level = role_hierarchy.get(required_role, 999)
            
            return user_level >= required_level
            
        except Exception as e:
            self.logger.error(f"Error checking user permissions: {str(e)}")
            return False
