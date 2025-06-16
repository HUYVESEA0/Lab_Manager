"""
Base Service Class
=================

Base class cho tất cả services, cung cấp common functionality.
"""

from flask import current_app, jsonify
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from ..models import db
from ..utils import log_activity
from ..cache.cache_manager import invalidate_model_cache, invalidate_user_cache
from typing import Dict, Any, Optional, List, Union, Tuple
import logging

logger = logging.getLogger(__name__)

class ServiceError(Exception):
    """Custom exception cho service layer"""
    def __init__(self, message: str, code: int = 400, details: Optional[Dict] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

class BaseService:
    """
    Base service class cung cấp common functionality cho tất cả services
    """
    
    def __init__(self):
        self.db = db
        self.logger = logger
    
    def success_response(self, message: str, data: Optional[Dict] = None, code: int = 200) -> Tuple[Dict, int]:
        """Tạo response thành công chuẩn"""
        response = {
            'success': True,
            'message': message,
            'timestamp': self._get_timestamp()
        }
        if data:
            response['data'] = data
        return response, code
    
    def error_response(self, message: str, code: int = 400, details: Optional[Dict] = None) -> Tuple[Dict, int]:
        """Tạo response lỗi chuẩn"""
        response = {
            'success': False,
            'message': message,
            'timestamp': self._get_timestamp()
        }
        if details:
            response['details'] = details
        return response, code
    
    def validate_required_fields(self, data: Dict, required_fields: List[str]) -> bool:
        """Validate required fields trong data"""
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            raise ServiceError(
                f"Missing required fields: {', '.join(missing_fields)}",
                400,
                {'missing_fields': missing_fields}
            )
        return True
    
    def handle_database_error(self, error: Exception, operation: str = "database operation") -> Tuple[Dict, int]:
        """Xử lý database errors một cách nhất quán"""
        try:
            self.db.session.rollback()
        except:
            pass
        
        if isinstance(error, IntegrityError):
            if "UNIQUE constraint failed" in str(error) or "duplicate key" in str(error).lower():
                return self.error_response(
                    "Dữ liệu đã tồn tại trong hệ thống",
                    409,
                    {'error_type': 'duplicate_entry'}
                )
            else:
                return self.error_response(
                    "Vi phạm ràng buộc dữ liệu",
                    400,
                    {'error_type': 'constraint_violation'}
                )
        
        self.logger.error(f"Database error during {operation}: {str(error)}")
        return self.error_response(
            f"Lỗi cơ sở dữ liệu khi {operation}",
            500,
            {'error_type': 'database_error'}
        )
    
    def log_user_activity(self, user_id: int, action: str, details: str = "") -> None:
        """Log user activity"""
        try:
            log_activity(action, details, user_id)
        except Exception as e:
            self.logger.warning(f"Failed to log activity: {str(e)}")
    
    def invalidate_caches(self, cache_keys: Optional[List[str]] = None, user_id: Optional[int] = None) -> None:
        """Invalidate relevant caches"""
        try:
            if cache_keys:
                for key in cache_keys:
                    invalidate_model_cache(key)
            
            if user_id:
                invalidate_user_cache(user_id)
        except Exception as e:
            self.logger.warning(f"Failed to invalidate caches: {str(e)}")
    
    def paginate_query(self, query, page: int = 1, per_page: int = 20) -> Dict:
        """Paginate query results"""
        try:
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            return {
                'items': [item.to_dict() if hasattr(item, 'to_dict') else str(item) 
                         for item in pagination.items],
                'pagination': {
                    'page': pagination.page,
                    'per_page': pagination.per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_prev': pagination.has_prev,
                    'has_next': pagination.has_next,
                    'prev_num': pagination.prev_num,
                    'next_num': pagination.next_num
                }
            }
        except Exception as e:
            self.logger.error(f"Pagination error: {str(e)}")
            raise ServiceError("Lỗi phân trang dữ liệu", 500)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def safe_commit(self) -> bool:
        """Safely commit database changes"""
        try:
            self.db.session.commit()
            return True
        except Exception as e:
            self.db.session.rollback()
            self.logger.error(f"Commit failed: {str(e)}")
            raise ServiceError(f"Lỗi lưu dữ liệu: {str(e)}", 500)
    
    def create_model_instance(self, model_class, data: Dict, exclude_fields: Optional[List[str]] = None) -> Any:
        """Create model instance from data"""
        exclude_fields = exclude_fields or ['id', 'created_at', 'updated_at']
        
        # Filter out excluded fields
        filtered_data = {k: v for k, v in data.items() if k not in exclude_fields}
        
        try:
            instance = model_class(**filtered_data)
            return instance
        except TypeError as e:
            raise ServiceError(f"Invalid data for model {model_class.__name__}: {str(e)}", 400)
    
    def update_model_instance(self, instance, data: Dict, exclude_fields: Optional[List[str]] = None) -> Any:
        """Update model instance with data"""
        exclude_fields = exclude_fields or ['id', 'created_at', 'updated_at']
        
        for key, value in data.items():
            if key not in exclude_fields and hasattr(instance, key):
                setattr(instance, key, value)
        
        return instance
