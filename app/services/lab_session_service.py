"""
Lab Session Service
==================

Service để xử lý logic liên quan đến phòng thực hành.
"""

from .base_service import BaseService, ServiceError
from ..models import CaThucHanh, DangKyCa, VaoCa, NguoiDung, db
from ..cache.cached_queries import invalidate_session_caches
from sqlalchemy import or_, and_
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, date
import secrets
import string

class LabSessionService(BaseService):
    """Service xử lý logic phòng thực hành"""
    
    def __init__(self):
        super().__init__()
        self.model = CaThucHanh
    
    def create_session(self, data: Dict) -> Tuple[Dict, int]:
        """Tạo ca thực hành mới"""
        try:
            # Validate required fields
            required_fields = ['tieu_de', 'mo_ta', 'ngay', 'gio_bat_dau', 'gio_ket_thuc', 'dia_diem', 'so_luong_toi_da']
            self.validate_required_fields(data, required_fields)
            
            # Generate verification code if not provided
            if not data.get('ma_xac_thuc'):
                data['ma_xac_thuc'] = self._generate_verification_code()
            
            # Create session
            session_data = {
                'tieu_de': data['tieu_de'],
                'mo_ta': data['mo_ta'],
                'ngay': data['ngay'],
                'gio_bat_dau': data['gio_bat_dau'],
                'gio_ket_thuc': data['gio_ket_thuc'],
                'dia_diem': data['dia_diem'],
                'so_luong_toi_da': int(data['so_luong_toi_da']),
                'ma_xac_thuc': data['ma_xac_thuc'],
                'nguoi_tao_ma': data.get('nguoi_tao_ma', 1),
                'dang_hoat_dong': data.get('dang_hoat_dong', True)
            }
            
            session = self.create_model_instance(self.model, session_data)
            self.db.session.add(session)
            self.safe_commit()
            
            # Invalidate caches
            invalidate_session_caches()
            
            return self.success_response(
                "Tạo ca thực hành thành công",
                {
                    'session': {
                        'id': session.id,
                        'tieu_de': session.tieu_de,
                        'ma_xac_thuc': session.ma_xac_thuc
                    }
                }
            )
            
        except ServiceError:
            raise
        except Exception as e:
            return self.handle_database_error(e, "tạo ca thực hành")
    
    def get_session_by_id(self, session_id: int) -> Optional[CaThucHanh]:
        """Lấy ca thực hành theo ID"""
        try:
            return self.model.query.get(session_id)
        except Exception as e:
            self.logger.error(f"Error getting session by ID {session_id}: {str(e)}")
            return None
    
    def get_active_sessions(self, filters: Optional[Dict] = None) -> Tuple[Dict, int]:
        """Lấy danh sách ca thực hành đang hoạt động"""
        try:
            query = self.model.query.filter(self.model.dang_hoat_dong == True)
            
            if filters:
                if filters.get('date'):
                    query = query.filter(self.model.ngay == filters['date'])
                if filters.get('location'):
                    query = query.filter(self.model.dia_diem.like(f"%{filters['location']}%"))
            
            sessions = query.order_by(self.model.ngay.desc(), self.model.gio_bat_dau.asc()).all()
            
            session_list = []
            for session in sessions:
                session_list.append({
                    'id': session.id,
                    'tieu_de': session.tieu_de,
                    'mo_ta': session.mo_ta,
                    'ngay': session.ngay.isoformat() if session.ngay else None,
                    'gio_bat_dau': session.gio_bat_dau.isoformat() if session.gio_bat_dau else None,
                    'gio_ket_thuc': session.gio_ket_thuc.isoformat() if session.gio_ket_thuc else None,
                    'dia_diem': session.dia_diem,
                    'so_luong_toi_da': session.so_luong_toi_da,
                    'dang_hoat_dong': session.dang_hoat_dong
                })
            
            return self.success_response(
                "Lấy danh sách ca thực hành thành công",
                {'sessions': session_list}
            )
            
        except Exception as e:
            self.logger.error(f"Error getting active sessions: {str(e)}")
            return self.error_response("Lỗi lấy danh sách ca thực hành", 500)
    
    def register_for_session(self, user_id: int, session_id: int, notes: str = "") -> Tuple[Dict, int]:
        """Đăng ký tham gia ca thực hành"""
        try:
            # Check if session exists and is active
            session = self.get_session_by_id(session_id)
            if not session:
                raise ServiceError("Ca thực hành không tồn tại", 404)
            
            if not session.dang_hoat_dong:
                raise ServiceError("Ca thực hành không còn hoạt động", 400)
            
            # Check if user already registered
            existing_registration = DangKyCa.query.filter_by(
                nguoi_dung_ma=user_id,
                ca_thuc_hanh_ma=session_id
            ).first()
            
            if existing_registration:
                raise ServiceError("Bạn đã đăng ký ca thực hành này", 409)
            
            # Check capacity
            current_registrations = DangKyCa.query.filter_by(ca_thuc_hanh_ma=session_id).count()
            if current_registrations >= session.so_luong_toi_da:
                raise ServiceError("Ca thực hành đã đầy", 400)
            
            # Create registration
            registration = DangKyCa(
                nguoi_dung_ma=user_id,
                ca_thuc_hanh_ma=session_id,
                ghi_chu=notes
            )
            
            self.db.session.add(registration)
            self.safe_commit()
            
            # Log activity
            self.log_user_activity(user_id, "Đăng ký ca thực hành", f"Đăng ký ca {session.tieu_de}")
            
            return self.success_response("Đăng ký ca thực hành thành công")
            
        except ServiceError:
            raise
        except Exception as e:
            return self.handle_database_error(e, "đăng ký ca thực hành")
    
    def _generate_verification_code(self) -> str:
        """Tạo mã xác thực ngẫu nhiên"""
        return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
