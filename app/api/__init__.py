"""
Lab Manager API Module
======================

RESTful API endpoints for Lab Manager system.
Provides clean separation between web routes and API routes.

API Versioning:
- v1: Current stable API version

Modules:
- system: System monitoring and health endpoints
- users: User management API
- lab_sessions: Lab session management API  
- auth: Authentication endpoints
- admin: Administrative functions API
"""

from flask import Blueprint
from flask_wtf.csrf import CSRFProtect

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Disable CSRF for all routes in this blueprint
@api_bp.before_request
def disable_csrf():
    """Disable CSRF protection for API routes"""
    pass

# Import API routes - Order matters for proper registration
from . import system
from . import users
from . import lab_sessions
from . import lab_sessions_enhanced  # Enhanced lab sessions API
from . import auth
from . import admin
from . import csrf

__version__ = '1.0.0'
