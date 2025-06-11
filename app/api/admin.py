"""
Administrative Functions API
============================

RESTful API endpoints for administrative operations.
"""

from flask import jsonify, request, current_app
from flask_login import login_required, current_user
from app.api import api_bp
from app.models import NguoiDung as User, CaThucHanh as LabSession, NhatKyHoatDong as ActivityLog, db
from app.decorators import admin_required
from app.utils import log_activity
from sqlalchemy import func, desc, text
from datetime import datetime, timedelta
import logging
import psutil
import os

logger = logging.getLogger(__name__)

@api_bp.route('/admin/dashboard-stats', methods=['GET'])
@login_required
@admin_required
def get_dashboard_stats():
    """Get comprehensive dashboard statistics"""
    try:
        # User statistics
        total_users = User.query.count()
        active_users = User.query.filter_by(dang_hoat_dong=True).count()
        online_users = User.query.filter(
            User.last_login >= datetime.utcnow() - timedelta(minutes=30)
        ).count()
        
        # Lab session statistics
        total_sessions = LabSession.query.count()
        active_sessions = LabSession.query.filter_by(dang_hoat_dong=True).count()
        today_sessions = LabSession.query.filter(
            func.date(LabSession.gio_bat_dau) == datetime.utcnow().date()
        ).count()
        
        # System health
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_usage('/')
            
            system_health = {
                'cpu_usage': cpu_usage,
                'memory_usage': memory_info.percent,
                'disk_usage': disk_info.percent,
                'uptime': psutil.boot_time()
            }
        except Exception as e:
            logger.warning(f"Could not get system health: {str(e)}")
            system_health = {
                'cpu_usage': 0,
                'memory_usage': 0,
                'disk_usage': 0,
                'uptime': 0
            }
        
        # Recent activities
        recent_activities = ActivityLog.query.order_by(
            desc(ActivityLog.thoi_gian)
        ).limit(10).all()
        
        return jsonify({
            'users': {
                'total': total_users,
                'active': active_users,
                'online': online_users,
                'offline': total_users - online_users
            },
            'sessions': {
                'total': total_sessions,
                'active': active_sessions,
                'today': today_sessions,
                'inactive': total_sessions - active_sessions
            },
            'system': system_health,
            'recent_activities': [{
                'id': activity.id,
                'nguoi_dung_ma': activity.nguoi_dung_ma,
                'hanh_dong': activity.hanh_dong,
                'chi_tiet': activity.chi_tiet,
                'thoi_gian': activity.thoi_gian.isoformat(),
                'dia_chi_ip': activity.dia_chi_ip
            } for activity in recent_activities]
        })
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch dashboard statistics'}), 500

@api_bp.route('/admin/activities', methods=['GET'])
@login_required
@admin_required
def get_activities():
    """Get system activities with filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        action_filter = request.args.get('action')
        user_id = request.args.get('user_id', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        query = ActivityLog.query
        
        # Apply filters
        if action_filter:
            query = query.filter(ActivityLog.hanh_dong == action_filter)
        if user_id:
            query = query.filter(ActivityLog.nguoi_dung_ma == user_id)
        if date_from:
            try:
                from_date = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(ActivityLog.thoi_gian >= from_date)
            except ValueError:
                pass
        if date_to:
            try:
                to_date = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
                query = query.filter(ActivityLog.thoi_gian < to_date)
            except ValueError:
                pass
        
        # Order by timestamp (newest first)
        query = query.order_by(desc(ActivityLog.thoi_gian))
        
        activities = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'activities': [{
                'id': activity.id,
                'nguoi_dung_ma': activity.nguoi_dung_ma,
                'username': activity.user.ten_nguoi_dung if activity.user else 'System',
                'hanh_dong': activity.hanh_dong,
                'chi_tiet': activity.chi_tiet,
                'thoi_gian': activity.thoi_gian.isoformat(),
                'dia_chi_ip': activity.dia_chi_ip
            } for activity in activities.items],
            'pagination': {
                'page': activities.page,
                'pages': activities.pages,
                'per_page': activities.per_page,
                'total': activities.total,
                'has_next': activities.has_next,
                'has_prev': activities.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching activities: {str(e)}")
        return jsonify({'error': 'Failed to fetch activities'}), 500

@api_bp.route('/admin/system-maintenance', methods=['POST'])
@login_required
@admin_required
def system_maintenance():
    """Perform system maintenance tasks"""
    try:
        data = request.get_json()
        task = data.get('task') if data else None
        
        if not task:
            return jsonify({'error': 'Maintenance task not specified'}), 400
        
        results = {}
        
        if task == 'cleanup_logs':
            # Clean up old activity logs (older than 90 days)
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            deleted_count = ActivityLog.query.filter(
                ActivityLog.thoi_gian < cutoff_date
            ).delete()
            db.session.commit()
            results['deleted_logs'] = deleted_count
            
        elif task == 'update_stats':
            # Refresh database statistics
            db.session.execute(text('ANALYZE'))
            db.session.commit()
            results['stats_updated'] = True
            
        elif task == 'cleanup_sessions':
            # Clean up old completed sessions (older than 1 year)
            cutoff_date = datetime.utcnow() - timedelta(days=365)
            deleted_count = LabSession.query.filter(
                LabSession.dang_hoat_dong == False,
                LabSession.gio_ket_thuc < cutoff_date
            ).delete()
            db.session.commit()
            results['deleted_sessions'] = deleted_count
            
        else:
            return jsonify({'error': 'Unknown maintenance task'}), 400
        
        # Log maintenance activity
        log_activity(
            current_user.id,
            'system_maintenance',
            f'Performed maintenance task: {task}'
        )
        
        return jsonify({
            'message': f'Maintenance task "{task}" completed successfully',
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error during system maintenance: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Maintenance task failed'}), 500

@api_bp.route('/admin/reports/usage', methods=['GET'])
@login_required
@admin_required
def get_usage_report():
    """Get system usage report"""
    try:
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Daily login counts
        daily_logins = db.session.query(
            func.date(User.last_login).label('date'),
            func.count(User.id).label('logins')
        ).filter(
            User.last_login >= start_date
        ).group_by(func.date(User.last_login)).all()
        
        # Daily session counts
        daily_sessions = db.session.query(
            func.date(LabSession.gio_bat_dau).label('date'),
            func.count(LabSession.id).label('sessions')
        ).filter(
            LabSession.gio_bat_dau >= start_date
        ).group_by(func.date(LabSession.gio_bat_dau)).all()
        
        # Popular lab rooms
        room_usage = db.session.query(
            LabSession.dia_diem,
            func.count(LabSession.id).label('usage_count')
        ).filter(
            LabSession.gio_bat_dau >= start_date
        ).group_by(LabSession.dia_diem).order_by(
            desc(func.count(LabSession.id))
        ).limit(10).all()
        
        return jsonify({
            'period_days': days,
            'daily_logins': [
                {'date': str(date), 'count': count} 
                for date, count in daily_logins
            ],
            'daily_sessions': [
                {'date': str(date), 'count': count} 
                for date, count in daily_sessions
            ],
            'room_usage': [
                {'room': room, 'count': count} 
                for room, count in room_usage
            ]
        })
        
    except Exception as e:
        logger.error(f"Error generating usage report: {str(e)}")
        return jsonify({'error': 'Failed to generate usage report'}), 500
