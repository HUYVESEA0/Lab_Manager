"""
Cached Database Queries
======================

Centralized cached database query functions for optimal performance.
These functions provide caching for expensive database operations.
"""

from app.models import NguoiDung, CaThucHanh, NhatKyHoatDong, CaiDatHeThong, SinhVien, db
from app.cache.cache_manager import cached_query, invalidate_model_cache
from datetime import datetime, timedelta
from sqlalchemy import func, desc
import logging

logger = logging.getLogger(__name__)

# User-related cached queries
@cached_query(timeout=600, key_prefix="user_count")
def get_total_users():
    """Get total number of users (cached for 10 minutes)"""
    return NguoiDung.query.count()

@cached_query(timeout=300, key_prefix="active_users")
def get_active_users_count(hours=24):
    """Get count of users active in last N hours (cached for 5 minutes)"""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    return NguoiDung.query.filter(NguoiDung.last_seen >= cutoff).count()

@cached_query(timeout=900, key_prefix="users_by_role")
def get_users_by_role():
    """Get user count by role (cached for 15 minutes)"""
    result = db.session.query(
        NguoiDung.vai_tro,
        func.count(NguoiDung.id).label('count')
    ).group_by(NguoiDung.vai_tro).all()
    
    return {role: count for role, count in result}

@cached_query(timeout=1200, key_prefix="recent_users")
def get_recent_users(limit=10):
    """Get recently created users (cached for 20 minutes)"""
    users = NguoiDung.query.order_by(desc(NguoiDung.ngay_tao)).limit(limit).all()
    return [{
        'id': user.id,
        'ten_nguoi_dung': user.ten_nguoi_dung,
        'email': user.email,
        'vai_tro': user.vai_tro,
        'ngay_tao': user.ngay_tao.isoformat() if user.ngay_tao else None
    } for user in users]

# Lab session related cached queries
@cached_query(timeout=300, key_prefix="session_count")
def get_total_sessions():
    """Get total number of lab sessions (cached for 5 minutes)"""
    return CaThucHanh.query.count()

@cached_query(timeout=180, key_prefix="active_sessions")
def get_active_sessions_count():
    """Get count of currently active lab sessions (cached for 3 minutes)"""
    now = datetime.utcnow()
    return CaThucHanh.query.filter(
        CaThucHanh.gio_bat_dau <= now,
        CaThucHanh.gio_ket_thuc >= now
    ).count()

@cached_query(timeout=600, key_prefix="sessions_today")
def get_sessions_today():
    """Get lab sessions for today (cached for 10 minutes)"""
    today = datetime.utcnow().date()
    sessions = CaThucHanh.query.filter(
        func.date(CaThucHanh.gio_bat_dau) == today
    ).all()
    
    return [{
        'id': session.id,
        'tieu_de': session.tieu_de,
        'gio_bat_dau': session.gio_bat_dau.isoformat() if session.gio_bat_dau else None,
        'gio_ket_thuc': session.gio_ket_thuc.isoformat() if session.gio_ket_thuc else None,
        'trang_thai': getattr(session, 'trang_thai', 'unknown')
    } for session in sessions]

@cached_query(timeout=1800, key_prefix="sessions_by_status")
def get_sessions_by_status():
    """Get session count by status (cached for 30 minutes)"""
    # Assuming status logic based on time
    now = datetime.utcnow()
    
    upcoming = CaThucHanh.query.filter(CaThucHanh.gio_bat_dau > now).count()
    active = CaThucHanh.query.filter(
        CaThucHanh.gio_bat_dau <= now,
        CaThucHanh.gio_ket_thuc >= now
    ).count()
    completed = CaThucHanh.query.filter(CaThucHanh.gio_ket_thuc < now).count()
    
    return {
        'upcoming': upcoming,
        'active': active,
        'completed': completed,
        'total': upcoming + active + completed
    }

# Activity log cached queries
@cached_query(timeout=120, key_prefix="recent_activities")
def get_recent_activities(limit=20):
    """Get recent activity log entries (cached for 2 minutes)"""
    activities = NhatKyHoatDong.query.order_by(desc(NhatKyHoatDong.thoi_gian)).limit(limit).all()
    
    return [{
        'id': activity.id,
        'hanh_dong': activity.hanh_dong,
        'chi_tiet': activity.chi_tiet,
        'thoi_gian': activity.thoi_gian.isoformat() if activity.thoi_gian else None,
        'nguoi_dung_ma': activity.nguoi_dung_ma,
        'nguoi_dung_ten': activity.nguoi_dung.ten_nguoi_dung if activity.nguoi_dung else 'Unknown'
    } for activity in activities]

@cached_query(timeout=900, key_prefix="activities_today")
def get_activities_today():
    """Get activity count for today (cached for 15 minutes)"""
    today = datetime.utcnow().date()
    return NhatKyHoatDong.query.filter(
        func.date(NhatKyHoatDong.thoi_gian) == today
    ).count()

@cached_query(timeout=1800, key_prefix="activities_by_type")
def get_activities_by_type(days=7):
    """Get activity count by type for last N days (cached for 30 minutes)"""
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    result = db.session.query(
        NhatKyHoatDong.hanh_dong,
        func.count(NhatKyHoatDong.id).label('count')
    ).filter(
        NhatKyHoatDong.thoi_gian >= cutoff
    ).group_by(NhatKyHoatDong.hanh_dong).all()
    
    return {activity_type: count for activity_type, count in result}

# System settings cached queries
@cached_query(timeout=3600, key_prefix="system_settings")
def get_system_settings():
    """Get all system settings (cached for 1 hour)"""
    settings = CaiDatHeThong.query.all()
    return {setting.khoa: setting.gia_tri for setting in settings}

@cached_query(timeout=3600, key_prefix="system_setting")
def get_system_setting(key, default=None):
    """Get specific system setting (cached for 1 hour)"""
    setting = CaiDatHeThong.query.filter_by(khoa=key).first()
    return setting.value if setting else default

# Student related cached queries
@cached_query(timeout=600, key_prefix="student_count")
def get_total_students():
    """Get total number of students (cached for 10 minutes)"""
    return SinhVien.query.count()

@cached_query(timeout=900, key_prefix="students_by_class")
def get_students_by_class():
    """Get student count by class (cached for 15 minutes)"""
    result = db.session.query(
        SinhVien.lop,
        func.count(SinhVien.id).label('count')
    ).group_by(SinhVien.lop).all()
    
    return {class_name or 'Unassigned': count for class_name, count in result}

# Dashboard statistics cached queries
@cached_query(timeout=300, key_prefix="dashboard_stats")
def get_dashboard_statistics():
    """Get comprehensive dashboard statistics (cached for 5 minutes)"""
    return {
        'users': {
            'total': get_total_users(),
            'active_today': get_active_users_count(24),
            'by_role': get_users_by_role()
        },
        'sessions': {
            'total': get_total_sessions(),
            'active_now': get_active_sessions_count(),
            'today': len(get_sessions_today()),
            'by_status': get_sessions_by_status()
        },
        'activities': {
            'today': get_activities_today(),
            'recent_count': len(get_recent_activities(10)),
            'by_type': get_activities_by_type(7)
        },
        'students': {
            'total': get_total_students(),
            'by_class': get_students_by_class()
        },
        'timestamp': datetime.utcnow().isoformat()
    }

# Cache invalidation helpers
def invalidate_user_caches():
    """Invalidate all user-related caches"""
    patterns = [
        "user_count*",
        "active_users*", 
        "users_by_role*",
        "recent_users*",
        "dashboard_stats*"
    ]
    for pattern in patterns:
        invalidate_model_cache(pattern)

def invalidate_session_caches():
    """Invalidate all session-related caches"""
    patterns = [
        "session_count*",
        "active_sessions*",
        "sessions_today*",
        "sessions_by_status*",
        "dashboard_stats*"
    ]
    for pattern in patterns:
        invalidate_model_cache(pattern)

def invalidate_activity_caches():
    """Invalidate all activity-related caches"""
    patterns = [
        "recent_activities*",
        "activities_today*",
        "activities_by_type*",
        "dashboard_stats*"
    ]
    for pattern in patterns:
        invalidate_model_cache(pattern)

def invalidate_student_caches():
    """Invalidate all student-related caches"""
    patterns = [
        "student_count*",
        "students_by_class*",
        "dashboard_stats*"
    ]
    for pattern in patterns:
        invalidate_model_cache(pattern)

def invalidate_system_caches():
    """Invalidate all system-related caches"""
    patterns = [
        "system_settings*",
        "system_setting*"
    ]
    for pattern in patterns:
        invalidate_model_cache(pattern)
