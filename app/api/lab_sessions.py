"""
Lab Sessions Management API
==========================

RESTful API endpoints for lab session management operations.
"""

from flask import jsonify, request, current_app, make_response
from flask_login import login_required, current_user
from app.api import api_bp
from app.models import CaThucHanh as LabSession, DangKyCa as Registration, VaoCa as Entry, NguoiDung as User, db
from app.decorators import admin_required
from app.utils import log_activity
from app.cache.cache_manager import cached_api, invalidate_user_cache, invalidate_model_cache
from app.cache.cached_queries import invalidate_session_caches, invalidate_activity_caches
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import logging
import random
import string

logger = logging.getLogger(__name__)

@api_bp.route('/lab-sessions', methods=['GET'])
@login_required
@cached_api(timeout=180, key_prefix='api_lab_sessions_list')
def get_lab_sessions():
    """Get lab sessions with filters and caching"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        room = request.args.get('room')
        date_filter = request.args.get('date')
        available_only = request.args.get('available_only', False, type=bool)
        
        query = LabSession.query
        
        # Apply filters
        if status:
            if status == 'active':
                query = query.filter(LabSession.dang_hoat_dong == True)
            elif status == 'inactive':
                query = query.filter(LabSession.dang_hoat_dong == False)
        if room:
            query = query.filter(LabSession.dia_diem.like(f'%{room}%'))
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                query = query.filter(func.date(LabSession.gio_bat_dau) == filter_date)
            except ValueError:
                pass
        
        # Filter for available sessions (future sessions that are active)
        if available_only:
            now = datetime.now()
            query = query.filter(
                LabSession.dang_hoat_dong == True,
                LabSession.gio_bat_dau > now
            )
          # Order by start time
        query = query.order_by(LabSession.gio_bat_dau)
        sessions = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        return jsonify({
            'sessions': [{
                'id': session.id,
                'tieu_de': session.tieu_de,
                'mo_ta': session.mo_ta,
                'dia_diem': session.dia_diem,
                'gio_bat_dau': session.gio_bat_dau.isoformat(),
                'gio_ket_thuc': session.gio_ket_thuc.isoformat(),
                'ngay': session.ngay.isoformat(),
                'dang_hoat_dong': session.dang_hoat_dong,
                'nguoi_tao_ma': session.nguoi_tao_ma,
                'so_luong_toi_da': session.so_luong_toi_da,
                'so_dang_ky': len(session.dang_ky) if session.dang_ky else 0,
                'ngay_tao': session.ngay_tao.isoformat() if session.ngay_tao else None,
                'ma_xac_thuc': session.ma_xac_thuc,
                'co_the_dang_ky': session.co_the_dang_ky() if hasattr(session, 'co_the_dang_ky') else True,
                'dang_dien_ra': session.dang_dien_ra() if hasattr(session, 'dang_dien_ra') else False
            } for session in sessions.items],
            'pagination': {
                'page': sessions.page,
                'pages': sessions.pages,
                'per_page': sessions.per_page,
                'total': sessions.total,
                'has_next': sessions.has_next,
                'has_prev': sessions.has_prev
            }
        })
    except Exception as e:
        logger.error(f"Error fetching lab sessions: {str(e)}")
        return jsonify({'error': 'Failed to fetch lab sessions'}), 500

@api_bp.route('/lab-sessions/<int:session_id>', methods=['GET'])
@login_required
@cached_api(timeout=300, key_prefix='api_lab_session_detail')
def get_lab_session(session_id):
    """Get specific lab session by ID with caching"""
    try:
        session = LabSession.query.get_or_404(session_id)
        
        return jsonify({
            'id': session.id,
            'tieu_de': session.tieu_de,
            'dia_diem': session.dia_diem,
            'gio_bat_dau': session.gio_bat_dau.isoformat(),
            'gio_ket_thuc': session.gio_ket_thuc.isoformat(),
            'dang_hoat_dong': session.dang_hoat_dong,
            'nguoi_tao_ma': session.nguoi_tao_ma,
            'so_luong_toi_da': session.so_luong_toi_da,
            'dang_ky': [{
                'id': dk.id,
                'nguoi_dung_ma': dk.nguoi_dung_ma
            } for dk in session.dang_ky] if session.dang_ky else [],
            'ngay_tao': session.ngay_tao.isoformat() if session.ngay_tao else None
        })
    except Exception as e:
        logger.error(f"Error fetching lab session {session_id}: {str(e)}")
        return jsonify({'error': 'Lab session not found'}), 404


@api_bp.route('/lab-sessions/upcoming', methods=['GET'])
@login_required
def get_upcoming_sessions():
    """Get upcoming lab sessions"""
    try:
        limit = request.args.get('limit', 5, type=int)
        now = datetime.utcnow()
        
        sessions = LabSession.query.filter(
            LabSession.gio_bat_dau > now
        ).order_by(LabSession.gio_bat_dau).limit(limit).all()
        
        return jsonify({
            'upcoming_sessions': [{
                'id': session.id,
                'tieu_de': session.tieu_de,
                'dia_diem': session.dia_diem,
                'gio_bat_dau': session.gio_bat_dau.isoformat(),
                'so_dang_ky': len(session.dang_ky) if session.dang_ky else 0,
                'so_luong_toi_da': session.so_luong_toi_da
            } for session in sessions]
        })
    except Exception as e:
        logger.error(f"Error fetching upcoming sessions: {str(e)}")
        return jsonify({'error': 'Failed to fetch upcoming sessions'}), 500

@api_bp.route('/lab-sessions/register', methods=['POST'])
@login_required
def register_for_session():
    """Register current user for a lab session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        notes = data.get('notes', '')
        
        if not session_id:
            return jsonify({'error': 'Session ID is required'}), 400
        
        # Check if session exists and is available
        lab_session = LabSession.query.get_or_404(session_id)
        if not lab_session.co_the_dang_ky():
            return jsonify({'error': 'This session is not available for registration'}), 400
        
        # Check if user is already registered
        existing_registration = Registration.query.filter_by(
            nguoi_dung_ma=current_user.id,
            ca_thuc_hanh_ma=session_id
        ).first()
        
        if existing_registration:
            return jsonify({'error': 'You are already registered for this session'}), 400
          # Create registration
        registration = Registration(
            nguoi_dung_ma=current_user.id,
            ca_thuc_hanh_ma=session_id,
            ghi_chu=notes
        )
        
        db.session.add(registration)
        db.session.commit()
        
        # Invalidate related caches after registration
        invalidate_user_cache(current_user.id)
        invalidate_session_caches()
        invalidate_activity_caches()
        
        log_activity("Lab registration", f"Registered for lab session {lab_session.tieu_de}")
        
        return jsonify({
            'message': 'Registration successful',
            'registration_id': registration.id
        })
        
    except Exception as e:
        logger.error(f"Error registering for session: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to register for session'}), 500

@api_bp.route('/lab-sessions/<int:session_id>/verify', methods=['POST'])
@login_required
def verify_lab_session(session_id):
    """Verify attendance at a lab session with verification code"""
    try:
        data = request.get_json()
        verification_code = data.get('verification_code')
        
        if not verification_code:
            return jsonify({'error': 'Verification code is required'}), 400
        
        # Check if session exists
        lab_session = LabSession.query.get_or_404(session_id)
        
        # Check if user is registered for this session
        registration = Registration.query.filter_by(
            nguoi_dung_ma=current_user.id,
            ca_thuc_hanh_ma=session_id
        ).first()
        
        if not registration:
            return jsonify({'error': 'You are not registered for this session'}), 400
        
        # Check if session is currently running
        if not lab_session.dang_dien_ra():
            return jsonify({'error': 'This session is not currently running'}), 400
        
        # Check if user already has an entry
        existing_entry = Entry.query.filter_by(
            nguoi_dung_ma=current_user.id,
            ca_thuc_hanh_ma=session_id
        ).first()
        
        if existing_entry:
            return jsonify({
                'message': 'Already verified',
                'entry_id': existing_entry.id
            })
        
        # Verify the code
        if verification_code != lab_session.ma_xac_thuc:
            return jsonify({'error': 'Invalid verification code'}), 400
        
        # Create entry
        entry = Entry(
            nguoi_dung_ma=current_user.id,
            ca_thuc_hanh_ma=session_id
        )
        
        # Update registration status
        registration.trang_thai_tham_gia = "da_tham_gia"
        
        db.session.add(entry)
        db.session.commit()
        
        log_activity("Vào ca thực hành", f"Vào ca thực hành {lab_session.tieu_de}")
        
        return jsonify({
            'message': 'Verification successful',
            'entry_id': entry.id
        })
        
    except Exception as e:
        logger.error(f"Error verifying session: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to verify session'}), 500

@api_bp.route('/lab-sessions/entries/<int:entry_id>/submit', methods=['POST'])
@login_required
def submit_lab_result(entry_id):
    """Submit lab result and end session"""
    try:
        data = request.get_json()
        lab_result = data.get('lab_result')
        
        if not lab_result:
            return jsonify({'error': 'Lab result is required'}), 400
        
        # Find the entry
        entry = Entry.query.filter_by(
            id=entry_id,
            nguoi_dung_ma=current_user.id
        ).first_or_404()
        
        # Check if already submitted
        if entry.thoi_gian_ra:
            return jsonify({'error': 'Lab result already submitted'}), 400
        
        # Update entry
        entry.ket_qua = lab_result
        entry.thoi_gian_ra = datetime.now()
        
        db.session.commit()
        
        log_activity("Kết thúc ca thực hành", f"Hoàn thành ca thực hành {entry.ca_thuc_hanh.tieu_de}")
        
        return jsonify({
            'message': 'Lab result submitted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error submitting lab result: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to submit lab result'}), 500

@api_bp.route('/lab-sessions/my-sessions', methods=['GET'])
@login_required
def get_my_lab_sessions():
    """Get current user's registered lab sessions"""
    try:
        # Get registered sessions
        registered_sessions = db.session.query(LabSession).join(Registration).filter(
            Registration.nguoi_dung_ma == current_user.id
        ).order_by(LabSession.gio_bat_dau).all()
        
        # Get lab history (entries)
        lab_history = Entry.query.filter_by(
            nguoi_dung_ma=current_user.id
        ).order_by(Entry.thoi_gian_vao.desc()).all()
        
        return jsonify({
            'registered_sessions': [{
                'id': session.id,
                'tieu_de': session.tieu_de,
                'mo_ta': session.mo_ta,
                'dia_diem': session.dia_diem,
                'gio_bat_dau': session.gio_bat_dau.isoformat(),
                'gio_ket_thuc': session.gio_ket_thuc.isoformat(),
                'dang_hoat_dong': session.dang_hoat_dong,
                'co_the_dang_ky': session.co_the_dang_ky() if hasattr(session, 'co_the_dang_ky') else True,
                'dang_dien_ra': session.dang_dien_ra() if hasattr(session, 'dang_dien_ra') else False
            } for session in registered_sessions],
            'lab_history': [{
                'id': entry.id,
                'ca_thuc_hanh_ma': entry.ca_thuc_hanh_ma,
                'tieu_de': entry.ca_thuc_hanh.tieu_de,
                'dia_diem': entry.ca_thuc_hanh.dia_diem,
                'thoi_gian_vao': entry.thoi_gian_vao.isoformat(),
                'thoi_gian_ra': entry.thoi_gian_ra.isoformat() if entry.thoi_gian_ra else None,
                'ket_qua': entry.ket_qua
            } for entry in lab_history]
        })
        
    except Exception as e:
        logger.error(f"Error fetching user's lab sessions: {str(e)}")
        return jsonify({'error': 'Failed to fetch lab sessions'}), 500

@api_bp.route('/lab-sessions/entries/<int:entry_id>', methods=['GET'])
@login_required
def get_lab_entry(entry_id):
    """Get specific lab entry details"""
    try:
        entry = Entry.query.filter_by(
            id=entry_id,
            nguoi_dung_ma=current_user.id
        ).first_or_404()
        
        lab_session = entry.ca_thuc_hanh
        now = datetime.now()
        time_elapsed = now - entry.thoi_gian_vao
        time_remaining = lab_session.gio_ket_thuc - now if now < lab_session.gio_ket_thuc else timedelta(0)
        
        return jsonify({
            'id': entry.id,
            'ca_thuc_hanh': {
                'id': lab_session.id,
                'tieu_de': lab_session.tieu_de,
                'mo_ta': lab_session.mo_ta,
                'dia_diem': lab_session.dia_diem,
                'gio_bat_dau': lab_session.gio_bat_dau.isoformat(),
                'gio_ket_thuc': lab_session.gio_ket_thuc.isoformat()
            },
            'thoi_gian_vao': entry.thoi_gian_vao.isoformat(),
            'thoi_gian_ra': entry.thoi_gian_ra.isoformat() if entry.thoi_gian_ra else None,
            'ket_qua': entry.ket_qua,
            'time_elapsed_seconds': int(time_elapsed.total_seconds()),
            'time_remaining_seconds': int(time_remaining.total_seconds()) if time_remaining.total_seconds() > 0 else 0
        })
        
    except Exception as e:
        logger.error(f"Error fetching lab entry: {str(e)}")
        return jsonify({'error': 'Lab entry not found'}), 404

# Admin API endpoints
@api_bp.route('/lab-sessions/admin', methods=['POST'])
@login_required
@admin_required
def create_lab_session():
    """Create new lab session (Admin only)"""
    try:
        data = request.get_json()
        
        # Generate verification code if not provided
        verification_code = data.get('verification_code')
        if not verification_code:
            verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Parse dates and times
        date_str = data.get('date')
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        
        if not all([date_str, start_time_str, end_time_str]):
            return jsonify({'error': 'Date, start time, and end time are required'}), 400
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            start_time_obj = datetime.strptime(start_time_str, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time_str, '%H:%M').time()
        except ValueError as e:
            return jsonify({'error': f'Invalid date/time format: {str(e)}'}), 400
        
        start_datetime = datetime.combine(date_obj, start_time_obj)
        end_datetime = datetime.combine(date_obj, end_time_obj)
        
        # Create lab session
        lab_session = LabSession(
            tieu_de=data.get('tieu_de'),
            mo_ta=data.get('mo_ta'),
            ngay=date_obj,
            gio_bat_dau=start_datetime,
            gio_ket_thuc=end_datetime,
            dia_diem=data.get('dia_diem'),
            so_luong_toi_da=data.get('so_luong_toi_da', 20),
            dang_hoat_dong=data.get('dang_hoat_dong', True),
            ma_xac_thuc=verification_code,
            nguoi_tao_ma=current_user.id
        )
        
        db.session.add(lab_session)
        db.session.commit()
        
        log_activity("Tạo ca thực hành", f"Đã tạo ca thực hành: {lab_session.tieu_de}")
        
        return jsonify({
            'message': 'Lab session created successfully',
            'session_id': lab_session.id,
            'verification_code': verification_code
        })
        
    except Exception as e:
        logger.error(f"Error creating lab session: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create lab session'}), 500

@api_bp.route('/lab-sessions/<int:session_id>/attendees', methods=['GET'])
@login_required
@admin_required
def get_session_attendees(session_id):
    """Get attendees for a specific lab session (Admin only)"""
    try:
        lab_session = LabSession.query.get_or_404(session_id)
        
        # Get registrations
        registrations = db.session.query(Registration, User).join(User).filter(
            Registration.ca_thuc_hanh_ma == session_id
        ).order_by(User.ten_nguoi_dung).all()
        
        # Get entries (actual attendance)
        entries = db.session.query(Entry, User).join(User).filter(
            Entry.ca_thuc_hanh_ma == session_id
        ).order_by(Entry.thoi_gian_vao).all()
        
        return jsonify({
            'session': {
                'id': lab_session.id,
                'tieu_de': lab_session.tieu_de,
                'dia_diem': lab_session.dia_diem,
                'gio_bat_dau': lab_session.gio_bat_dau.isoformat(),
                'gio_ket_thuc': lab_session.gio_ket_thuc.isoformat()
            },
            'registrations': [{
                'id': reg.id,
                'user': {
                    'id': user.id,
                    'ten_nguoi_dung': user.ten_nguoi_dung,
                    'email': user.email
                },
                'ghi_chu': reg.ghi_chu,
                'trang_thai_tham_gia': reg.trang_thai_tham_gia
            } for reg, user in registrations],
            'entries': [{
                'id': entry.id,
                'user': {
                    'id': user.id,
                    'ten_nguoi_dung': user.ten_nguoi_dung,
                    'email': user.email
                },
                'thoi_gian_vao': entry.thoi_gian_vao.isoformat(),
                'thoi_gian_ra': entry.thoi_gian_ra.isoformat() if entry.thoi_gian_ra else None,
                'ket_qua': entry.ket_qua
            } for entry, user in entries]
        })
        
    except Exception as e:
        logger.error(f"Error fetching session attendees: {str(e)}")
        return jsonify({'error': 'Failed to fetch session attendees'}), 500

@api_bp.route('/lab-sessions/schedule/valid', methods=['GET'])
@login_required
@admin_required
def get_valid_sessions_for_schedule():
    """Get sessions that are valid for scheduling (Admin only)"""
    try:
        min_students = request.args.get('min_students', 5, type=int)
        
        # Sessions with enough registrations
        valid_sessions = db.session.query(
            LabSession, 
            func.count(Registration.id).label("student_count")
        ).join(Registration).group_by(LabSession.id).having(
            func.count(Registration.id) >= min_students
        ).order_by(LabSession.gio_bat_dau).all()
        
        # Sessions with insufficient registrations
        pending_sessions = db.session.query(
            LabSession, 
            func.count(Registration.id).label("student_count")
        ).join(Registration).group_by(LabSession.id).having(
            func.count(Registration.id) < min_students
        ).order_by(LabSession.gio_bat_dau).all()
        
        return jsonify({
            'valid_sessions': [{
                'session': {
                    'id': session.id,
                    'tieu_de': session.tieu_de,
                    'dia_diem': session.dia_diem,
                    'gio_bat_dau': session.gio_bat_dau.isoformat(),
                    'gio_ket_thuc': session.gio_ket_thuc.isoformat(),
                    'so_luong_toi_da': session.so_luong_toi_da
                },
                'student_count': count
            } for session, count in valid_sessions],
            'pending_sessions': [{
                'session': {
                    'id': session.id,
                    'tieu_de': session.tieu_de,
                    'dia_diem': session.dia_diem,
                    'gio_bat_dau': session.gio_bat_dau.isoformat(),
                    'gio_ket_thuc': session.gio_ket_thuc.isoformat(),
                    'so_luong_toi_da': session.so_luong_toi_da
                },
                'student_count': count
            } for session, count in pending_sessions]
        })
        
    except Exception as e:
        logger.error(f"Error fetching schedule sessions: {str(e)}")
        return jsonify({'error': 'Failed to fetch schedule sessions'}), 500

@api_bp.route('/lab-sessions/rooms/schedule', methods=['POST'])
@login_required
@admin_required
def schedule_lab_rooms():
    """Auto-schedule rooms for lab sessions (Admin only)"""
    try:
        # Get active sessions
        sessions = LabSession.query.filter_by(dang_hoat_dong=True).order_by(
            LabSession.gio_bat_dau
        ).all()
        
        # Available rooms
        rooms = ["Phòng 1", "Phòng 2", "Phòng 3", "Phòng 4", "Phòng 5", "Phòng 6"]
        
        # Generate schedule
        schedule = []
        for i, session in enumerate(sessions):
            room = rooms[i % len(rooms)]
            schedule.append({
                'session': {
                    'id': session.id,
                    'tieu_de': session.tieu_de,
                    'dia_diem': session.dia_diem,
                    'gio_bat_dau': session.gio_bat_dau.isoformat(),
                    'gio_ket_thuc': session.gio_ket_thuc.isoformat()
                },
                'assigned_room': room
            })
        
        log_activity("Lên lịch phòng thực hành", f"Đã lên lịch {len(schedule)} ca thực hành")
        
        return jsonify({
            'message': 'Room scheduling completed successfully',
            'schedule': schedule
        })
        
    except Exception as e:
        logger.error(f"Error scheduling rooms: {str(e)}")
        return jsonify({'error': 'Failed to schedule rooms'}), 500

@api_bp.route('/lab-sessions/stats', methods=['GET'])
@login_required
@admin_required
def get_lab_session_stats():
    """Get enhanced lab session statistics"""
    try:
        # Basic counts
        total_sessions = LabSession.query.count()
        active_sessions = LabSession.query.filter_by(dang_hoat_dong=True).count()
        
        # Today's sessions
        today = datetime.utcnow().date()
        today_sessions = LabSession.query.filter(
            func.date(LabSession.gio_bat_dau) == today
        ).count()
        
        # This week's sessions
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        week_sessions = LabSession.query.filter(
            func.date(LabSession.gio_bat_dau).between(week_start, week_end)
        ).count()
        
        # Total attendees from all entries
        from app.models import VaoCa as Entry
        total_attendees = Entry.query.count()
        
        # Upcoming sessions (next 7 days)
        next_week = today + timedelta(days=7)
        upcoming_sessions = LabSession.query.filter(
            func.date(LabSession.gio_bat_dau).between(today, next_week),
            LabSession.dang_hoat_dong == True
        ).count()
        
        # Room usage stats
        room_stats = db.session.query(
            LabSession.dia_diem,
            func.count(LabSession.id).label('count')
        ).group_by(LabSession.dia_diem).limit(10).all()
        
        # Monthly session trend (last 6 months)
        monthly_stats = []
        for i in range(6):
            month_start = (today.replace(day=1) - timedelta(days=i*30)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            count = LabSession.query.filter(
                func.date(LabSession.gio_bat_dau).between(month_start, month_end)
            ).count()
            
            monthly_stats.append({
                'month': month_start.strftime('%Y-%m'),
                'count': count
            })
        
        return jsonify({
            'total_sessions': total_sessions,
            'active_sessions': active_sessions,
            'inactive_sessions': total_sessions - active_sessions,
            'today_sessions': today_sessions,
            'week_sessions': week_sessions,
            'upcoming_sessions': upcoming_sessions,
            'total_attendees': total_attendees,
            'room_usage': [{'room': room, 'count': count} for room, count in room_stats],
            'monthly_trend': monthly_stats,
            'last_updated': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Error fetching lab session stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch lab session statistics'}), 500

@api_bp.route('/lab-sessions/bulk-action', methods=['POST'])
@login_required
@admin_required
def bulk_lab_session_action():
    """Perform bulk actions on lab sessions (Admin only)"""
    try:
        data = request.get_json()
        action = data.get('action')
        session_ids = data.get('session_ids', [])
        
        if not action or not session_ids:
            return jsonify({'error': 'Action and session_ids are required'}), 400
        
        sessions = LabSession.query.filter(LabSession.id.in_(session_ids)).all()
        
        if not sessions:
            return jsonify({'error': 'No sessions found with provided IDs'}), 404
        
        success_count = 0
        
        if action == 'activate':
            for session in sessions:
                session.dang_hoat_dong = True
                success_count += 1
            message = f'Successfully activated {success_count} sessions'
            
        elif action == 'deactivate':
            for session in sessions:
                session.dang_hoat_dong = False
                success_count += 1
            message = f'Successfully deactivated {success_count} sessions'
            
        elif action == 'delete':
            for session in sessions:
                # Delete related records first
                from app.models import DangKyCa as Registration, VaoCa as Entry
                Registration.query.filter_by(ca_thuc_hanh_ma=session.id).delete()
                Entry.query.filter_by(ca_thuc_hanh_ma=session.id).delete()
                db.session.delete(session)
                success_count += 1
            message = f'Successfully deleted {success_count} sessions'
            
        else:
            return jsonify({'error': 'Invalid action'}), 400
        
        db.session.commit()
        
        # Invalidate caches
        invalidate_session_caches()
        invalidate_activity_caches()
        
        log_activity(f"Bulk {action} sessions", f"{message} - IDs: {session_ids}")
        
        return jsonify({
            'message': message,
            'affected_count': success_count
        })
        
    except Exception as e:
        logger.error(f"Error performing bulk action: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to perform bulk action'}), 500

@api_bp.route('/lab-sessions/<int:session_id>/duplicate', methods=['POST'])
@login_required
@admin_required
def duplicate_lab_session(session_id):
    """Duplicate a lab session (Admin only)"""
    try:
        original_session = LabSession.query.get_or_404(session_id)
        
        # Create new session with same properties but different title and future date
        new_session = LabSession(
            tieu_de=f"{original_session.tieu_de} (Copy)",
            mo_ta=original_session.mo_ta,
            ngay=datetime.utcnow().date() + timedelta(days=7),  # Default to next week
            gio_bat_dau=original_session.gio_bat_dau + timedelta(days=7),
            gio_ket_thuc=original_session.gio_ket_thuc + timedelta(days=7),
            dia_diem=original_session.dia_diem,
            so_luong_toi_da=original_session.so_luong_toi_da,
            dang_hoat_dong=False,  # Start as inactive
            ma_xac_thuc=''.join(random.choices(string.ascii_uppercase + string.digits, k=6)),
            nguoi_tao_ma=current_user.id
        )
        
        db.session.add(new_session)
        db.session.commit()
        
        # Invalidate caches
        invalidate_session_caches()
        
        log_activity("Duplicate session", f"Duplicated session: {original_session.tieu_de}")
        
        return jsonify({
            'message': 'Session duplicated successfully',
            'new_session_id': new_session.id,
            'new_session': {
                'id': new_session.id,
                'tieu_de': new_session.tieu_de,
                'gio_bat_dau': new_session.gio_bat_dau.isoformat(),
                'gio_ket_thuc': new_session.gio_ket_thuc.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error duplicating session: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to duplicate session'}), 500

@api_bp.route('/lab-sessions/export', methods=['GET', 'POST'])
@login_required
@admin_required
def export_lab_sessions():
    """Export lab sessions to various formats (Admin only)"""
    try:
        if request.method == 'POST':
            # Export selected sessions
            data = request.get_json()
            session_ids = data.get('session_ids', [])
            format_type = data.get('format', 'excel')
            
            if session_ids:
                sessions = LabSession.query.filter(LabSession.id.in_(session_ids)).all()
            else:
                sessions = LabSession.query.all()
        else:
            # Export all sessions
            format_type = request.args.get('format', 'excel')
            sessions = LabSession.query.order_by(LabSession.gio_bat_dau.desc()).all()
        
        # Prepare data for export
        export_data = []
        for session in sessions:
            registration_count = len(session.dang_ky) if session.dang_ky else 0
            
            export_data.append({
                'ID': session.id,
                'Title': session.tieu_de,
                'Description': session.mo_ta or '',
                'Location': session.dia_diem,
                'Date': session.ngay.strftime('%Y-%m-%d'),
                'Start Time': session.gio_bat_dau.strftime('%H:%M'),
                'End Time': session.gio_ket_thuc.strftime('%H:%M'),
                'Max Students': session.so_luong_toi_da,
                'Registered': registration_count,
                'Available Spots': session.so_luong_toi_da - registration_count,
                'Status': 'Active' if session.dang_hoat_dong else 'Inactive',
                'Verification Code': session.ma_xac_thuc,
                'Created By': session.nguoi_tao_ma,
                'Created Date': session.ngay_tao.strftime('%Y-%m-%d %H:%M') if session.ngay_tao else ''
            })
        
        if format_type == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=export_data[0].keys() if export_data else [])
            writer.writeheader()
            writer.writerows(export_data)
            
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = 'attachment; filename=lab_sessions.csv'
            return response
            
        elif format_type == 'excel':
            try:
                import pandas as pd
                from io import BytesIO
                
                df = pd.DataFrame(export_data)
                output = BytesIO()
                
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Lab Sessions', index=False)
                    
                    # Get workbook and worksheet
                    workbook = writer.book
                    worksheet = writer.sheets['Lab Sessions']
                    
                    # Auto-adjust column widths
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
                
                output.seek(0)
                response = make_response(output.read())
                response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                response.headers['Content-Disposition'] = 'attachment; filename=lab_sessions.xlsx'
                return response
                
            except ImportError:
                return jsonify({'error': 'Excel export requires pandas and openpyxl packages'}), 500
                
        elif format_type == 'pdf':
            # For PDF export, you would need a PDF library like reportlab
            return jsonify({'error': 'PDF export not implemented yet'}), 501
            
        else:
            return jsonify({'error': 'Unsupported format'}), 400
            
    except Exception as e:
        logger.error(f"Error exporting sessions: {str(e)}")
        return jsonify({'error': 'Failed to export sessions'}), 500

@api_bp.route('/lab-sessions/<int:session_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_lab_session(session_id):
    """Delete a specific lab session (Admin only)"""
    try:
        session = LabSession.query.get_or_404(session_id)
        
        # Delete related records first
        from app.models import DangKyCa as Registration, VaoCa as Entry
        Registration.query.filter_by(ca_thuc_hanh_ma=session_id).delete()
        Entry.query.filter_by(ca_thuc_hanh_ma=session_id).delete()
        
        session_title = session.tieu_de
        db.session.delete(session)
        db.session.commit()
        
        # Invalidate caches
        invalidate_session_caches()
        invalidate_activity_caches()
        
        log_activity("Delete session", f"Deleted session: {session_title}")
        
        return jsonify({
            'message': 'Session deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to delete session'}), 500
