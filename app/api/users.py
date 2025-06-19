"""
Users API
=========

RESTful API endpoints for user management operations with comprehensive caching.
"""

from flask import jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func
from app.api import api_bp
from app.models import NguoiDung as User, db
from app.decorators import admin_required
from app.cache.cache_manager import cached_api, invalidate_user_cache, invalidate_model_cache
from app.cache.cached_queries import get_total_users, invalidate_user_caches
from app.services.user_service import UserService
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@api_bp.route('/users/register', methods=['POST'])
def register_user():
    """Public endpoint for user registration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        user_service = UserService()
        result, status_code = user_service.create_user(data)
        
        if status_code == 200:
            return jsonify(result), 201
        else:
            return jsonify(result), status_code
            
    except Exception as e:
        logger.error(f"Error in user registration: {str(e)}")
        return jsonify({
            'success': False, 
            'message': 'Internal server error'
        }), 500

@api_bp.route('/users/create', methods=['POST'])
@login_required
@admin_required
def create_user_admin():
    """Admin endpoint for creating users with advanced options"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        user_service = UserService()
        result, status_code = user_service.create_user(data)
        
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in admin user creation: {str(e)}")
        return jsonify({
            'success': False, 
            'message': 'Internal server error'
        }), 500

@api_bp.route('/users/bulk-create', methods=['POST'])
@login_required
@admin_required
def bulk_create_users():
    """Bulk create multiple users"""
    try:
        data = request.get_json()
        if not data or 'users' not in data:
            return jsonify({'success': False, 'message': 'No users data provided'}), 400
        
        users_data = data['users']
        if not isinstance(users_data, list):
            return jsonify({'success': False, 'message': 'Users data must be a list'}), 400
        
        user_service = UserService()
        results = []
        success_count = 0
        error_count = 0
        
        for user_data in users_data:
            try:
                result, status_code = user_service.create_user(user_data)
                if status_code == 200:
                    success_count += 1
                    results.append({
                        'success': True,
                        'user': result.get('data', {}).get('user', {}),
                        'message': result.get('message', '')
                    })
                else:
                    error_count += 1
                    results.append({
                        'success': False,
                        'user_data': user_data,
                        'message': result.get('message', 'Unknown error')
                    })
            except Exception as e:
                error_count += 1
                results.append({
                    'success': False,
                    'user_data': user_data,
                    'message': str(e)
                })
        
        return jsonify({
            'success': True,
            'summary': {
                'total': len(users_data),
                'success': success_count,
                'errors': error_count
            },
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error in bulk user creation: {str(e)}")
        return jsonify({
            'success': False, 
            'message': 'Internal server error'
        }), 500

@api_bp.route('/users', methods=['GET'])
@login_required
@admin_required
@cached_api(timeout=300, key_prefix='api_users_list')
def get_users():
    """Get all users with pagination and caching"""
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
                'is_active': getattr(user, 'is_active', True),
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
@cached_api(timeout=600, key_prefix='api_user_detail')
def get_user(user_id):
    """Get user by ID with caching"""
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({
            'id': user.id,
            'ten_nguoi_dung': user.ten_nguoi_dung,
            'email': user.email,
            'vai_tro': user.vai_tro,
            'is_active': getattr(user, 'is_active', True),
            'ngay_tao': user.ngay_tao.isoformat() if user.ngay_tao else None
        })
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {str(e)}")
        return jsonify({'error': 'User not found'}), 404

@api_bp.route('/users/stats', methods=['GET'])
@login_required
@admin_required
@cached_api(timeout=300, key_prefix='api_user_stats')
def get_user_stats():
    """Get user statistics with caching"""
    try:
        total_users = get_total_users()  # Use cached query
        
        # Users by role - use direct query for now, can be optimized later
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
    """Toggle user active status with cache invalidation"""
    try:
        user = User.query.get_or_404(user_id)
        old_status = getattr(user, 'is_active', True)
        # Toggle status logic would go here when is_active field exists
        # user.is_active = not user.is_active
        db.session.commit()
        
        # Invalidate related caches
        invalidate_user_cache(user_id)
        invalidate_user_caches()
        
        return jsonify({
            'message': f'User status would be updated',
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Error toggling user status: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to update user status'}), 500

@api_bp.route('/users/check-username', methods=['POST'])
def check_username_availability():
    """Check if username is available"""
    try:
        data = request.get_json()
        if not data or 'username' not in data:
            return jsonify({'error': 'Username is required'}), 400
        
        username = data['username']
        user = User.query.filter_by(ten_nguoi_dung=username).first()
        
        return jsonify({
            'available': user is None,
            'username': username
        })
        
    except Exception as e:
        logger.error(f"Error checking username availability: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/users/check-email', methods=['POST'])
def check_email_availability():
    """Check if email is available"""
    try:
        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].lower().strip()
        user = User.query.filter_by(email=email).first()
        
        return jsonify({
            'available': user is None,
            'email': email
        })
        
    except Exception as e:
        logger.error(f"Error checking email availability: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
