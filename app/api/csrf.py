"""
CSRF Token API endpoints
Provides centralized CSRF token management for the application
"""

from flask import Blueprint, jsonify, request
from flask_login import login_required
from flask_wtf.csrf import generate_csrf
from datetime import datetime
import logging

csrf_bp = Blueprint('csrf_api', __name__, url_prefix='/api/v1')

logger = logging.getLogger(__name__)

@csrf_bp.route('/csrf-token', methods=['GET'])
def get_csrf_token():
    """
    Get CSRF token for authenticated and unauthenticated users
    Returns a fresh CSRF token that can be used in forms and AJAX requests
    """
    try:
        token = generate_csrf()
        
        # Log token generation for security monitoring
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        logger.info(f"CSRF token generated for IP: {client_ip}")
        
        return jsonify({
            'csrf_token': token,
            'timestamp': datetime.utcnow().isoformat(),
            'expires_in': 3600  # 1 hour in seconds
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to generate CSRF token: {str(e)}")
        return jsonify({
            'error': 'Unable to generate CSRF token',
            'message': 'Please refresh the page and try again'
        }), 500

@csrf_bp.route('/csrf-token/refresh', methods=['POST'])
@login_required  
def refresh_csrf_token():
    """
    Force refresh CSRF token for authenticated users
    Useful when the current token has expired or become invalid
    """
    try:
        # Generate a new token
        token = generate_csrf()
        
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        logger.info(f"CSRF token refreshed for authenticated user at IP: {client_ip}")
        
        return jsonify({
            'csrf_token': token,
            'timestamp': datetime.utcnow().isoformat(),
            'expires_in': 3600,
            'refreshed': True
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to refresh CSRF token: {str(e)}")
        return jsonify({
            'error': 'Unable to refresh CSRF token',
            'message': 'Please refresh the page and try again'
        }), 500

@csrf_bp.route('/csrf-token/validate', methods=['POST'])
def validate_csrf_token():
    """
    Validate CSRF token without performing any action
    Useful for checking token validity before making important requests
    """
    try:
        # Flask-WTF will automatically validate the CSRF token
        # If we reach this point, the token is valid
        return jsonify({
            'valid': True,
            'message': 'CSRF token is valid'
        }), 200
        
    except Exception as e:
        logger.warning(f"CSRF token validation failed: {str(e)}")
        return jsonify({
            'valid': False,
            'error': 'Invalid CSRF token',
            'message': 'Please refresh the page to get a new token'
        }), 400
