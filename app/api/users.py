"""
Users API
=========

RESTful API endpoints for user management operations.
"""

from flask import jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func
from app.api import api_bp
from app.models import NguoiDung as User, db
from app.decorators import admin_required
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@api_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    """Get all users with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        users = User.query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'users': [{
                'id': user.id,
                'ten_nguoi_dung': user.ten_nguoi_dung,
                'email': user.email,
                'vai_tro': user.vai_tro,
                'is_active': user.is_active,
                'ngay_tao': user.ngay_tao.isoformat() if user.ngay_tao else None
            } for user in users.items],
            'pagination': {
                'page': users.page,
                'pages': users.pages,
                'per_page': users.per_page,
                'total': users.total,
                'has_next': users.has_next,
                'has_prev': users.has_prev
            }
        })
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        return jsonify({'error': 'Failed to fetch users'}), 500

@api_bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def get_user(user_id):
    """Get user by ID"""
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({
            'id': user.id,
            'ten_nguoi_dung': user.ten_nguoi_dung,
            'email': user.email,
            'vai_tro': user.vai_tro,
            'is_active': user.is_active,
            'ngay_tao': user.ngay_tao.isoformat() if user.ngay_tao else None
        })
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {str(e)}")
        return jsonify({'error': 'User not found'}), 404

@api_bp.route('/users/stats', methods=['GET'])
@login_required
@admin_required
def get_user_stats():
    """Get user statistics"""
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        
        # Users by role
        role_stats = db.session.query(
            User.vai_tro,
            func.count(User.id).label('count')
        ).group_by(User.vai_tro).all()
        
        # Recent registrations (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_users = User.query.filter(
            User.ngay_tao >= thirty_days_ago
        ).count()
        
        return jsonify({
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'recent_registrations': recent_users,
            'roles': {role: count for role, count in role_stats}
        })
    except Exception as e:
        logger.error(f"Error fetching user stats: {str(e)}")
        return jsonify({'error': 'Failed to fetch user statistics'}), 500

@api_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    try:
        user = User.query.get_or_404(user_id)
        user.is_active = not user.is_active
        db.session.commit()
        
        return jsonify({
            'message': f'User status updated to {"active" if user.is_active else "inactive"}',
            'is_active': user.is_active
        })
    except Exception as e:
        logger.error(f"Error toggling user status: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update user status'}), 500
