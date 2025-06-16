"""
Service Layer Module
===================

Service layer để tách biệt business logic khỏi routes và API endpoints.
Giảm duplication và tăng khả năng tái sử dụng code.

Services:
- BaseService: Base class cho tất cả services
- UserService: Xử lý logic người dùng
- LabSessionService: Xử lý logic phòng thực hành
- AdminService: Xử lý logic quản trị
- AuthService: Xử lý logic xác thực
"""

from .base_service import BaseService
from .user_service import UserService
from .lab_session_service import LabSessionService
from .admin_service import AdminService
from .auth_service import AuthService

__all__ = [
    'BaseService',
    'UserService', 
    'LabSessionService',
    'AdminService',
    'AuthService'
]
