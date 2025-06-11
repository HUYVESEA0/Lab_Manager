"""
Authentication API
==================

RESTful API endpoints for authentication operations.
"""

from flask import jsonify, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.api import api_bp
from app.models import NguoiDung as User, db
from app.utils import log_activity
from werkzeug.security import check_password_hash, generate_password_hash
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    """API endpoint for user login"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        # Try to find user by username or email
        user = User.query.filter(
            (User.ten_nguoi_dung == username) | (User.email == username)
        ).first()
        
        if user and check_password_hash(user.mat_khau_hash, password):
            if not user.is_active:
                return jsonify({'error': 'Account is disabled'}), 403
            
            login_user(user, remember=data.get('remember', False))
              # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Log activity
            log_activity('login', f'User {username} logged in via API', user)
            
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'ten_nguoi_dung': user.ten_nguoi_dung,
                    'email': user.email,
                    'vai_tro': user.vai_tro
                }
            })
        else:
            log_activity('login_failed', f'Failed login attempt for username: {username}')
            return jsonify({'error': 'Invalid username or password'}), 401
            
    except Exception as e:
        logger.error(f"Error during API login: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@api_bp.route('/auth/logout', methods=['POST'])
@login_required
def api_logout():
    """API endpoint for user logout"""
    try:
        user_id = current_user.id
        username = current_user.ten_nguoi_dung
        
        logout_user()
          # Log activity
        log_activity('logout', f'User {username} logged out via API', current_user)
        
        return jsonify({'message': 'Logout successful'})
        
    except Exception as e:
        logger.error(f"Error during API logout: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500

@api_bp.route('/auth/me', methods=['GET'])
@login_required
def get_current_user():
    """Get current authenticated user info"""
    try:        return jsonify({
            'user': {
                'id': current_user.id,
                'ten_nguoi_dung': current_user.ten_nguoi_dung,
                'email': current_user.email,
                'vai_tro': current_user.vai_tro,
                'is_active': current_user.is_active,
                'ngay_tao': current_user.ngay_tao.isoformat() if current_user.ngay_tao else None,
                'last_login': current_user.last_login.isoformat() if hasattr(current_user, 'last_login') and current_user.last_login else None
            }
        })
    except Exception as e:
        logger.error(f"Error fetching current user: {str(e)}")
        return jsonify({'error': 'Failed to fetch user info'}), 500

@api_bp.route('/auth/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    try:
        data = request.get_json()
        
        if not data or not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current password and new password are required'}), 400
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        # Verify current password
        if not check_password_hash(current_user.mat_khau_hash, current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Validate new password
        if len(new_password) < 6:
            return jsonify({'error': 'New password must be at least 6 characters long'}), 400
        
        # Update password
        current_user.mat_khau_hash = generate_password_hash(new_password)
        db.session.commit()
          # Log activity
        log_activity('password_change', f'User {current_user.ten_nguoi_dung} changed password via API', current_user)
        
        return jsonify({'message': 'Password changed successfully'})
        
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to change password'}), 500

@api_bp.route('/auth/session-check', methods=['GET'])
@login_required
def check_session():
    """Check if user session is still valid"""
    try:
        return jsonify({
            'valid': True,
            'user_id': current_user.id,
            'ten_nguoi_dung': current_user.ten_nguoi_dung,
            'vai_tro': current_user.vai_tro
        })
    except Exception as e:
        logger.error(f"Error checking session: {str(e)}")
        return jsonify({'valid': False, 'error': 'Session check failed'}), 500

@api_bp.route('/csrf-token', methods=['GET'])
def get_csrf_token():
    """Get CSRF token for frontend forms"""
    from flask_wtf.csrf import generate_csrf
    try:
        token = generate_csrf()
        return jsonify({
            'csrf_token': token,
            'message': 'CSRF token generated successfully'
        })
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate CSRF token',
            'details': str(e)
        }), 500
