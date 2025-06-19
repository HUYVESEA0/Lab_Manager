"""
Enhanced Lab Sessions Management API
===================================

Extended RESTful API endpoints with advanced features for lab session management.
"""

from flask import jsonify, request, current_app, make_response, send_file, Response
from flask_login import login_required, current_user
from app.api import api_bp
from app.models import (
    CaThucHanh as LabSession, DangKyCa as Registration, VaoCa as Entry, 
    NguoiDung as User, MauCaThucHanh as SessionTemplate, TaiLieuCa as SessionFile,
    ThietBi as Equipment, DatThietBi as EquipmentBooking, DanhGiaCa as SessionRating,
    ThongBao as Notification, db
)
from app.decorators import admin_required
from app.utils import log_activity
from app.cache.cache_manager import cached_api, invalidate_user_cache, invalidate_model_cache
from app.cache.cached_queries import invalidate_session_caches, invalidate_activity_caches
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.expression import desc, and_, or_
from datetime import datetime, timedelta
import logging
import random
import string
import json
import csv
import io
# import openpyxl  # Optional - install if needed: pip install openpyxl
# from reportlab.pdfgen import canvas  # Optional - install if needed: pip install reportlab
# from reportlab.lib.pagesizes import letter, A4
import os

logger = logging.getLogger(__name__)

# Enhanced Lab Sessions Endpoints

@api_bp.route('/lab-sessions/enhanced', methods=['GET'])
@login_required
@cached_api(timeout=180, key_prefix='api_lab_sessions_enhanced')
def get_enhanced_lab_sessions():
    """Get lab sessions with enhanced features and analytics"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        status = request.args.get('status')
        room = request.args.get('room')
        date_filter = request.args.get('date')
        tag_filter = request.args.get('tags')
        difficulty = request.args.get('difficulty')
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'gio_bat_dau')
        sort_order = request.args.get('sort_order', 'asc')
        
        query = LabSession.query
        
        # Apply search filter
        if search:
            search_filter = or_(
                LabSession.tieu_de.contains(search),
                LabSession.mo_ta.contains(search),
                LabSession.dia_diem.contains(search)
            )
            query = query.filter(search_filter)
        
        # Apply status filter
        if status:
            if status == 'active':
                query = query.filter(LabSession.dang_hoat_dong == True)
            elif status == 'inactive':
                query = query.filter(LabSession.dang_hoat_dong == False)
            elif status == 'upcoming':
                query = query.filter(
                    LabSession.gio_bat_dau > datetime.now(),
                    LabSession.trang_thai == 'scheduled'
                )
            elif status == 'ongoing':
                query = query.filter(LabSession.trang_thai == 'ongoing')
            elif status == 'completed':
                query = query.filter(LabSession.trang_thai == 'completed')
        
        # Apply room filter
        if room:
            query = query.filter(LabSession.dia_diem.like(f'%{room}%'))
        
        # Apply date filter
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                query = query.filter(func.date(LabSession.gio_bat_dau) == filter_date)
            except ValueError:
                pass
        
        # Apply difficulty filter
        if difficulty:
            query = query.filter(LabSession.muc_do_kho == difficulty)
        # Apply tag filter
        if tag_filter:
            tags = tag_filter.split(',')
            for tag in tags:
                # Assuming tags are stored in a column, replace 'tags' with the actual column name
                # If tags are stored as JSON or text, use the appropriate column
                query = query.filter(LabSession.tags_column.like(f'%{tag.strip()}%'))
                # Alternative: if tags is a text field, use:
                # query = query.filter(LabSession.tags_text.like(f'%{tag.strip()}%'))
        
        # Apply sorting
        if sort_order == 'desc':
            query = query.order_by(desc(getattr(LabSession, sort_by, LabSession.gio_bat_dau)))
        else:
            query = query.order_by(getattr(LabSession, sort_by, LabSession.gio_bat_dau))
        
        sessions = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Get enhanced session data
        enhanced_sessions = []
        for session in sessions.items:
            # Get registration count
            registration_count = len(session.dang_ky)
            
            # Get completion rate
            completion_rate = session.get_completion_rate()
            
            # Get average rating
            ratings = [r.diem_danh_gia for r in session.danh_gia]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            
            # Check user registration status
            user_registered = False
            if current_user.is_authenticated:
                user_registered = any(r.nguoi_dung_ma == current_user.id for r in session.dang_ky)
            
            enhanced_sessions.append({
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
                'so_dang_ky': registration_count,
                'ngay_tao': session.ngay_tao.isoformat() if session.ngay_tao else None,
                'ma_xac_thuc': session.ma_xac_thuc if current_user.is_admin() else None,
                'co_the_dang_ky': session.co_the_dang_ky(),
                'dang_dien_ra': session.dang_dien_ra(),
                'tags': session.get_tags(),
                'muc_do_kho': session.muc_do_kho,
                'yeu_cau_thiet_bi': session.get_equipment(),
                'trang_thai': session.trang_thai,
                'completion_rate': completion_rate,
                'avg_rating': round(avg_rating, 1),
                'rating_count': len(ratings),
                'user_registered': user_registered,
                'anh_bia': session.anh_bia,
                'cho_phep_dang_ky_tre': session.cho_phep_dang_ky_tre,
                'diem_so_toi_da': session.diem_so_toi_da,
                'thoi_gian_lam_bai': session.thoi_gian_lam_bai
            })
        
        return jsonify({
            'sessions': enhanced_sessions,
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
        logger.error(f"Error fetching enhanced lab sessions: {str(e)}")
        return jsonify({'error': 'Failed to fetch lab sessions'}), 500

@api_bp.route('/lab-sessions/analytics', methods=['GET'])
@login_required
@admin_required
def get_lab_sessions_analytics():
    """Get comprehensive analytics for lab sessions"""
    try:
        # Time range filter
        days = request.args.get('days', 30, type=int)
        start_date = datetime.now() - timedelta(days=days)
        
        # Basic statistics
        total_sessions = LabSession.query.count()
        active_sessions = LabSession.query.filter(LabSession.dang_hoat_dong == True).count()
        upcoming_sessions = LabSession.query.filter(
            LabSession.gio_bat_dau > datetime.now(),
            LabSession.trang_thai == 'scheduled'
        ).count()
        completed_sessions = LabSession.query.filter(
            LabSession.trang_thai == 'completed'
        ).count()
        
        # Registration statistics
        total_registrations = Registration.query.join(LabSession).filter(
            LabSession.gio_bat_dau >= start_date
        ).count()
        
        total_attendees = Entry.query.join(LabSession).filter(
            LabSession.gio_bat_dau >= start_date
        ).count()
        
        # Completion rate
        completion_rate = (total_attendees / total_registrations * 100) if total_registrations > 0 else 0
        
        # Popular rooms
        room_stats = db.session.query(
            LabSession.dia_diem,
            func.count(LabSession.id).label('session_count')
        ).filter(
            LabSession.gio_bat_dau >= start_date
        ).group_by(LabSession.dia_diem).order_by(desc('session_count')).limit(5).all()
        
        # Daily session trends
        daily_stats = db.session.query(
            func.date(LabSession.gio_bat_dau).label('date'),
            func.count(LabSession.id).label('sessions'),
            func.sum(func.cast(LabSession.so_luong_toi_da, db.Integer)).label('capacity'),
            func.count(Registration.id).label('registrations')
        ).outerjoin(Registration).filter(
            LabSession.gio_bat_dau >= start_date
        ).group_by(func.date(LabSession.gio_bat_dau)).order_by('date').all()
        
        # Equipment usage
        equipment_stats = db.session.query(
            Equipment.ten_thiet_bi,
            func.count(EquipmentBooking.id).label('usage_count')
        ).join(EquipmentBooking).join(LabSession).filter(
            LabSession.gio_bat_dau >= start_date
        ).group_by(Equipment.ten_thiet_bi).order_by(desc('usage_count')).limit(10).all()
        
        # Average ratings
        avg_rating = db.session.query(
            func.avg(SessionRating.diem_danh_gia)
        ).join(LabSession).filter(
            LabSession.gio_bat_dau >= start_date
        ).scalar() or 0
        
        return jsonify({
            'overview': {
                'total_sessions': total_sessions,
                'active_sessions': active_sessions,
                'upcoming_sessions': upcoming_sessions,
                'completed_sessions': completed_sessions,
                'total_registrations': total_registrations,
                'total_attendees': total_attendees,
                'completion_rate': round(completion_rate, 1),
                'avg_rating': round(avg_rating, 1)
            },
            'room_stats': [
                {'room': room, 'count': count} for room, count in room_stats
            ],
            'daily_trends': [
                {
                    'date': date.isoformat() if date else None,
                    'sessions': sessions or 0,
                    'capacity': capacity or 0,
                    'registrations': registrations or 0
                } for date, sessions, capacity, registrations in daily_stats
            ],
            'equipment_usage': [
                {'equipment': equipment, 'usage': usage} for equipment, usage in equipment_stats
            ]
        })
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        return jsonify({'error': 'Failed to fetch analytics'}), 500

@api_bp.route('/lab-sessions/templates', methods=['GET'])
@login_required
@admin_required
def get_session_templates():
    """Get lab session templates"""
    try:
        templates = SessionTemplate.query.filter(SessionTemplate.kich_hoat == True).all()
        
        return jsonify({
            'templates': [{
                'id': template.id,
                'ten_mau': template.ten_mau,
                'mo_ta': template.mo_ta,
                'tieu_de_mac_dinh': template.tieu_de_mac_dinh,
                'mo_ta_mac_dinh': template.mo_ta_mac_dinh,
                'thoi_gian_thuc_hien': template.thoi_gian_thuc_hien,
                'so_luong_toi_da_mac_dinh': template.so_luong_toi_da_mac_dinh,
                'tags_mac_dinh': json.loads(template.tags_mac_dinh) if template.tags_mac_dinh else [],
                'yeu_cau_thiet_bi_mac_dinh': json.loads(template.yeu_cau_thiet_bi_mac_dinh) if template.yeu_cau_thiet_bi_mac_dinh else [],
                'muc_do_kho': template.muc_do_kho,
                'diem_so_toi_da': template.diem_so_toi_da
            } for template in templates]
        })
    except Exception as e:
        logger.error(f"Error fetching templates: {str(e)}")
        return jsonify({'error': 'Failed to fetch templates'}), 500

@api_bp.route('/lab-sessions/templates', methods=['POST'])
@login_required
@admin_required
def create_session_template():
    """Create a new session template"""
    try:
        data = request.get_json()
        
        template = SessionTemplate(
            ten_mau=data.get('ten_mau'),
            mo_ta=data.get('mo_ta', ''),
            tieu_de_mac_dinh=data.get('tieu_de_mac_dinh'),
            mo_ta_mac_dinh=data.get('mo_ta_mac_dinh'),
            thoi_gian_thuc_hien=data.get('thoi_gian_thuc_hien', 120),
            so_luong_toi_da_mac_dinh=data.get('so_luong_toi_da_mac_dinh', 20),
            tags_mac_dinh=json.dumps(data.get('tags_mac_dinh', [])),
            yeu_cau_thiet_bi_mac_dinh=json.dumps(data.get('yeu_cau_thiet_bi_mac_dinh', [])),
            muc_do_kho=data.get('muc_do_kho', 'trung_binh'),
            diem_so_toi_da=data.get('diem_so_toi_da', 100),
            nguoi_tao_ma=current_user.id
        )
        
        db.session.add(template)
        db.session.commit()
        
        log_activity("Template created", f"Created session template: {template.ten_mau}")
        
        return jsonify({
            'message': 'Template created successfully',
            'template_id': template.id
        }), 201
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        return jsonify({'error': 'Failed to create template'}), 500

@api_bp.route('/lab-sessions/bulk-actions', methods=['POST'])
@login_required
@admin_required
def bulk_session_actions():
    """Perform bulk actions on lab sessions"""
    try:
        data = request.get_json()
        action = data.get('action')
        session_ids = data.get('session_ids', [])
        
        if not session_ids:
            return jsonify({'error': 'No sessions selected'}), 400
        
        sessions = LabSession.query.filter(LabSession.id.in_(session_ids)).all()
        
        if action == 'activate':
            for session in sessions:
                session.dang_hoat_dong = True
            message = f"Activated {len(sessions)} sessions"
            
        elif action == 'deactivate':
            for session in sessions:
                session.dang_hoat_dong = False
            message = f"Deactivated {len(sessions)} sessions"
            
        elif action == 'delete':
            for session in sessions:
                db.session.delete(session)
            message = f"Deleted {len(sessions)} sessions"
            
        elif action == 'duplicate':
            duplicated_count = 0
            for session in sessions:
                new_session = LabSession(
                    tieu_de=f"{session.tieu_de} (Copy)",
                    mo_ta=session.mo_ta,
                    ngay=session.ngay,
                    gio_bat_dau=session.gio_bat_dau + timedelta(days=7),
                    gio_ket_thuc=session.gio_ket_thuc + timedelta(days=7),
                    dia_diem=session.dia_diem,
                    so_luong_toi_da=session.so_luong_toi_da,
                    ma_xac_thuc=''.join(random.choices(string.ascii_uppercase + string.digits, k=6)),
                    nguoi_tao_ma=current_user.id,
                    tags=session.tags,
                    muc_do_kho=session.muc_do_kho,
                    yeu_cau_thiet_bi=session.yeu_cau_thiet_bi
                )
                db.session.add(new_session)
                duplicated_count += 1
            message = f"Duplicated {duplicated_count} sessions"
            
        else:
            return jsonify({'error': 'Invalid action'}), 400        
        db.session.commit()
        invalidate_session_caches()
        
        log_activity("Bulk action", f"{action} performed on {len(sessions)} sessions")
        return jsonify({'message': message})
    except Exception as e:
        logger.error(f"Error performing bulk action: {str(e)}")
        return jsonify({'error': 'Failed to perform bulk action'}), 500

@api_bp.route('/lab-sessions/enhanced/export', methods=['POST'])
@login_required
@admin_required
def export_enhanced_lab_sessions():
    """Export lab sessions data"""
    try:
        data = request.get_json()
        format_type = data.get('format', 'excel')  # excel, csv, pdf
        session_ids = data.get('session_ids', [])
        include_attendees = data.get('include_attendees', False)
        
        query = LabSession.query
        if session_ids:
            query = query.filter(LabSession.id.in_(session_ids))
        sessions = query.order_by(LabSession.gio_bat_dau).all()
        
        if format_type == 'csv':
            return export_to_csv(sessions, include_attendees)
        else:
            return jsonify({'error': 'Only CSV export is currently supported'}), 400
            
    except Exception as e:
        logger.error(f"Error exporting sessions: {str(e)}")
        return jsonify({'error': 'Failed to export sessions'}), 500

def export_to_csv(sessions, include_attendees):
    """Export sessions to CSV format"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    headers = ['ID', 'Title', 'Description', 'Date', 'Start Time', 'End Time', 
               'Location', 'Max Students', 'Registered', 'Status', 'Difficulty']
    if include_attendees:
        headers.extend(['Attendees', 'Completion Rate'])
    
    writer.writerow(headers)
    
    # Data
    for session in sessions:
        row = [
            session.id,
            session.tieu_de,
            session.mo_ta,
            session.ngay.strftime('%Y-%m-%d'),
            session.gio_bat_dau.strftime('%H:%M'),
            session.gio_ket_thuc.strftime('%H:%M'),
            session.dia_diem,
            session.so_luong_toi_da,
            len(session.dang_ky),
            session.trang_thai,
            session.muc_do_kho
        ]
        
        if include_attendees:
            attendees = len([e for e in session.vao_ca if e.thoi_gian_ra])
            completion_rate = session.get_completion_rate()
            row.extend([attendees, f"{completion_rate:.1f}%"])
        
        writer.writerow(row)
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=lab_sessions.csv'}
    )

# Equipment Management Endpoints

@api_bp.route('/equipment', methods=['GET'])
@login_required
@admin_required
def get_equipment():
    """Get all equipment"""
    try:
        equipment = Equipment.query.all()
        return jsonify({
            'equipment': [{
                'id': eq.id,
                'ten_thiet_bi': eq.ten_thiet_bi,
                'mo_ta': eq.mo_ta,
                'so_luong_co_san': eq.so_luong_co_san,
                'trang_thai': eq.trang_thai,
                'vi_tri': eq.vi_tri,
                'ghi_chu': eq.ghi_chu
            } for eq in equipment]
        })
    except Exception as e:
        logger.error(f"Error fetching equipment: {str(e)}")
        return jsonify({'error': 'Failed to fetch equipment'}), 500

@api_bp.route('/equipment', methods=['POST'])
@login_required
@admin_required
def create_equipment():
    """Create new equipment"""
    try:
        data = request.get_json()
        
        equipment = Equipment(
            ten_thiet_bi=data.get('ten_thiet_bi'),
            mo_ta=data.get('mo_ta', ''),
            so_luong_co_san=data.get('so_luong_co_san', 1),
            trang_thai=data.get('trang_thai', 'available'),
            vi_tri=data.get('vi_tri', ''),
            ghi_chu=data.get('ghi_chu', '')
        )
        
        db.session.add(equipment)
        db.session.commit()
        
        log_activity("Equipment created", f"Created equipment: {equipment.ten_thiet_bi}")
        
        return jsonify({
            'message': 'Equipment created successfully',
            'equipment_id': equipment.id
        }), 201
    except Exception as e:
        logger.error(f"Error creating equipment: {str(e)}")
        return jsonify({'error': 'Failed to create equipment'}), 500

# Notification Endpoints

@api_bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    """Get user notifications"""
    try:
        notifications = Notification.query.filter(
            Notification.nguoi_nhan == current_user.id
        ).order_by(desc(Notification.ngay_tao)).limit(50).all()
        
        return jsonify({
            'notifications': [{
                'id': notif.id,
                'tieu_de': notif.tieu_de,
                'noi_dung': notif.noi_dung,
                'loai': notif.loai,
                'lien_ket': notif.lien_ket,
                'da_doc': notif.da_doc,
                'ngay_tao': notif.ngay_tao.isoformat()
            } for notif in notifications]
        })
    except Exception as e:
        logger.error(f"Error fetching notifications: {str(e)}")
        return jsonify({'error': 'Failed to fetch notifications'}), 500

@api_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    try:
        notification = Notification.query.filter(
            Notification.id == notification_id,
            Notification.nguoi_nhan == current_user.id
        ).first_or_404()
        
        notification.da_doc = True
        notification.ngay_doc = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Notification marked as read'})
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        return jsonify({'error': 'Failed to mark notification as read'}), 500
