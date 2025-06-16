"""
CSRF Middleware for Lab Manager
Provides automatic CSRF token handling and validation
"""

from flask import request, session, g, current_app, jsonify
from flask_wtf.csrf import generate_csrf, validate_csrf
from werkzeug.exceptions import BadRequest
import logging

logger = logging.getLogger(__name__)

class CSRFMiddleware:
    """
    Middleware to handle CSRF token validation and refresh automatically
    """
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Store reference to app for logging
        self.app = app
    
    def before_request(self):
        """
        Process request before it reaches the route
        - Generate CSRF token if needed
        - Validate CSRF token for protected routes
        """
        # Skip CSRF for certain routes
        if self._should_skip_csrf():
            return
        
        # Ensure we have a CSRF token available
        if not hasattr(g, 'csrf_token'):
            g.csrf_token = generate_csrf()
        
        # For non-GET requests, validate CSRF token
        if request.method != 'GET':
            self._validate_csrf_token()
    
    def after_request(self, response):
        """
        Process response after route execution
        - Add CSRF token to response headers for AJAX requests
        """
        # Add CSRF token to response header for easy access
        if hasattr(g, 'csrf_token'):
            response.headers['X-CSRF-Token'] = g.csrf_token
        
        return response
    
    def _should_skip_csrf(self):
        """
        Determine if CSRF protection should be skipped for this request
        """
        # Skip for API routes (they use different authentication)
        if request.path.startswith('/api/'):
            return True
        
        # Skip for static files
        if request.path.startswith('/static/'):
            return True
        
        # Skip for health check endpoints
        if request.path in ['/health', '/ping', '/status']:
            return True
        
        # Skip for GET requests (CSRF only needed for state-changing operations)
        if request.method == 'GET':
            return True
        
        # Skip if CSRF is explicitly disabled for this route
        endpoint = request.endpoint
        if endpoint and hasattr(current_app.view_functions.get(endpoint), '_csrf_exempt'):
            return True
        
        return False
    
    def _validate_csrf_token(self):
        """
        Validate CSRF token from request
        """
        try:
            # Get token from various sources
            token = self._get_csrf_token_from_request()
            
            if not token:
                self._handle_csrf_error("CSRF token missing")
                return
            
            # Validate the token
            validate_csrf(token)
            
        except Exception as e:
            self._handle_csrf_error(f"CSRF validation failed: {str(e)}")
    
    def _get_csrf_token_from_request(self):
        """
        Extract CSRF token from request in order of preference:
        1. X-CSRFToken header (for AJAX requests)
        2. csrf_token form field
        3. X-CSRF-Token header (alternative)
        """
        # Check headers first (preferred for AJAX)
        token = request.headers.get('X-CSRFToken')
        if token:
            return token
        
        token = request.headers.get('X-CSRF-Token')
        if token:
            return token
        
        # Check form data
        token = request.form.get('csrf_token')
        if token:
            return token
        
        # Check JSON data
        if request.is_json:
            json_data = request.get_json(silent=True)
            if json_data and 'csrf_token' in json_data:
                return json_data['csrf_token']
        
        return None
    
    def _handle_csrf_error(self, error_message):
        """
        Handle CSRF validation errors
        """
        logger.warning(f"CSRF Error: {error_message} - IP: {request.remote_addr}, Path: {request.path}")
        
        # For AJAX requests, return JSON error
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
            response = jsonify({
                'error': 'CSRF token validation failed',
                'message': 'Please refresh the page and try again',
                'code': 'CSRF_ERROR'
            })
            response.status_code = 403
            return response
        
        # For regular requests, raise BadRequest
        raise BadRequest("CSRF token validation failed. Please refresh the page and try again.")

def csrf_exempt(f):
    """
    Decorator to exempt a route from CSRF protection
    Usage: @csrf_exempt
    """
    f._csrf_exempt = True
    return f
