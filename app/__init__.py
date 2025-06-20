from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO, join_room, leave_room
from flask_mail import Mail
from .models import db, khoi_tao_ung_dung as models_khoi_tao_ung_dung
from .session_handler import SessionHandler
from .decorators import *
from .utils import *
from datetime import datetime
import os

# Global SocketIO instance
socketio = None

def create_app():
    global socketio
    app = Flask(__name__)
    
    # Load environment variables from .env if present
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        from dotenv import load_dotenv
        load_dotenv(env_path)
    elif os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
          # Load config class based on FLASK_DEBUG (replacing deprecated FLASK_ENV)
    debug_mode = os.getenv("FLASK_DEBUG", "1").lower() in ['1', 'true', 'yes', 'on']
    env = "development" if debug_mode else "production"
    from config import config
    app.config.from_object(config.get(env, config["default"]))
    
    # Debug: Print SECRET_KEY status (only first few characters for security)
    secret_key = app.config.get('SECRET_KEY')
    if secret_key:
        print(f"SECRET_KEY is set: {secret_key[:10]}...")
    else:
        print("WARNING: SECRET_KEY is not set!")# Initialize SocketIO with Redis clustering support for production
    redis_url = None
    if not debug_mode and os.getenv('REDIS_HOST'):
        try:
            # Check if this is Azure environment
            if os.getenv('WEBSITES_PORT'):  # Azure App Service
                # Azure Redis configuration
                import redis
                redis_client = redis.Redis(
                    host=os.getenv('REDIS_HOST') or 'localhost',
                    port=int(os.getenv('REDIS_PORT', 6380)),
                    password=os.getenv('REDIS_PASSWORD'),
                    ssl=os.getenv('REDIS_SSL', 'true').lower() == 'true',
                    ssl_cert_reqs='none',
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                redis_client.ping()
                redis_url = f"redis://:{os.getenv('REDIS_PASSWORD')}@{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT', 6380)}"
                print(f"SocketIO clustering enabled with Azure Redis: {os.getenv('REDIS_HOST')}")
            else:
                # Standard Redis configuration
                import redis
                redis_client = redis.Redis(
                    host=os.getenv('REDIS_HOST', 'localhost'),
                    port=int(os.getenv('REDIS_PORT', 6379)),
                    db=int(os.getenv('REDIS_DB', 0)),
                    socket_connect_timeout=2
                )
                redis_client.ping()
                redis_url = f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}/{os.getenv('REDIS_DB', 0)}"
                print(f"SocketIO clustering enabled with Redis: {redis_url}")
        except Exception as e:
            print(f"Redis not available: {e}")
            # Fallback to FakeRedis for development/testing
            try:
                import fakeredis
                # Create a FakeRedis instance that persists across app instances
                fake_redis = fakeredis.FakeRedis(decode_responses=True)
                fake_redis.ping()  # Test connection
                
                # Use FakeRedis for message queue (simplified)
                print("Using FakeRedis for SocketIO clustering (development mode)")
                redis_url = None  # Will use threading mode but with better instance management
            except Exception as fe:
                print(f"FakeRedis also failed: {fe}")
                redis_url = None
    
    socketio = SocketIO(
        app, 
        cors_allowed_origins="*", 
        logger=True, 
        engineio_logger=True,
        message_queue=redis_url,  # Enable clustering if Redis URL provided
        async_mode='threading'  # Use threading mode for Windows compatibility
    )
    
    # Initialize extensions
    models_khoi_tao_ung_dung(app)
    SessionHandler(app)
    
    # Initialize Flask-Caching properly
    cache = Cache(app)
    
    # Initialize Flask-Mail
    mail = Mail(app)
    
    # Initialize cache manager (no need to set cache manually)
    from .cache.cache_manager import get_cache_manager
    cache_manager = get_cache_manager()
    
    migrate = Migrate(app, db)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # type: ignore
      # Configure CSRF settings before initializing CSRFProtect
    app.config['WTF_CSRF_TIME_LIMIT'] = None  # No time limit for CSRF tokens
    app.config['WTF_CSRF_CHECK_DEFAULT'] = True
    
    # Ensure SECRET_KEY is available for CSRF
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = 'lab-manager-development-secret-key-change-in-production-2025'
    csrf = CSRFProtect(app)
    
    # Initialize real-time monitoring
    from .real_time_monitor import init_real_time_monitor
    system_monitor = init_real_time_monitor(socketio)
    
    # Register user_loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from .models import NguoiDung
        return NguoiDung.query.get(int(user_id))
      # SocketIO event handlers
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
    
    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')
    
    @socketio.on('join_admin_dashboard')
    def handle_join_admin():
        join_room('admin_dashboard')
        print('Admin joined dashboard room')
        # Start monitoring if not already started
        if system_monitor and not system_monitor.is_monitoring:
            system_monitor.start_monitoring()
    
    @socketio.on('leave_admin_dashboard')
    def handle_leave_admin():
        leave_room('admin_dashboard')
        print('Admin left dashboard room')
    
    @socketio.on('join_user_room')
    def handle_join_user_room(data):
        user_id = data.get('user_id')
        if user_id:
            join_room(f'user_{user_id}')
            print(f'User {user_id} joined user room')
    
    @socketio.on('leave_user_room')
    def handle_leave_user_room(data):
        user_id = data.get('user_id')
        if user_id:
            leave_room(f'user_{user_id}')
            print(f'User {user_id} left user room')    
    # Register blueprints theo cấu trúc mới 
    from .routes.system_admin.system_admin import system_admin_bp
    from .routes.admin.admin_main import admin_bp  
    from .routes.user.user_main import user_bp
    from .routes.auth import auth_bp
    from .routes.lab import lab_bp
    from .routes.search import search_bp
    
    # Đăng ký blueprints theo thứ tự ưu tiên quyền hạn
    app.register_blueprint(system_admin_bp)  # Quyền cao nhất
    app.register_blueprint(admin_bp)         # Quyền admin
    app.register_blueprint(user_bp)          # Quyền user cơ bản
    app.register_blueprint(auth_bp)
    app.register_blueprint(lab_bp)
    app.register_blueprint(search_bp)
    
    # Register new API blueprint (temporarily disabled)
    # from .api import api_bp
    # app.register_blueprint(api_bp)
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/csrf-test', methods=['GET', 'POST'])
    def csrf_test():
        """CSRF test endpoint"""
        if request.method == 'POST':
            test_data = request.form.get('test_data')
            return jsonify({
                'success': True,
                'message': f'CSRF test passed! Received: {test_data}',
                'timestamp': datetime.now().isoformat()
            })
        return render_template('csrf_test.html')
    
    @app.route('/simple-login', methods=['GET', 'POST'])
    def simple_login():
        """Simple login route for testing CSRF functionality"""
        from .forms import LoginForm
        from flask_wtf.csrf import generate_csrf
        if request.method == 'GET':
            csrf_token = generate_csrf()
            return f'''
            <html>
            <body>
                <h1>Simple Login Test</h1>
                <p>CSRF Protection is working! SECRET_KEY is properly configured.</p>
                <form method="POST">
                    <input type="hidden" name="csrf_token" value="{csrf_token}" />
                    Email: <input type="email" name="email" required /> <br><br>
                    Password: <input type="password" name="password" required /> <br><br>
                    <input type="submit" value="Test Login" />
                </form>
            </body>
            </html>
            '''
        else:
            form = LoginForm()
            if form.validate_on_submit():
                return jsonify({"success": True, "message": "CSRF validation passed!"})
            else:
                return jsonify({"success": False, "errors": form.errors})    # Simple health check endpoint for load balancer
    @app.route('/healthz')
    def health_check():
        """Simple health check endpoint for load balancer monitoring"""
        return jsonify({
            'status': 'healthy',
            'instance_id': os.getenv('INSTANCE_ID', '1'),
            'instance_port': os.getenv('INSTANCE_PORT', '5000'),
            'timestamp': 'running'
        })
    
    @app.route('/lb-status')
    def load_balancer_status():
        """Detailed status for load balancer"""
        return jsonify({
            'instance_id': os.getenv('INSTANCE_ID', '1'),
            'ready': True,
            'active_connections': 0,  # Implement if needed
            'uptime': 'running'
        })

    @app.route('/health/azure')
    def azure_health_check():
        """Azure-specific health check"""
        from datetime import datetime
        
        return jsonify({
            'status': 'healthy',
            'instance_id': os.getenv('WEBSITE_INSTANCE_ID', os.getenv('INSTANCE_ID', 'unknown')),
            'site_name': os.getenv('WEBSITE_SITE_NAME', 'lab-manager'),
            'resource_group': os.getenv('WEBSITE_RESOURCE_GROUP', 'unknown'),
            'region': os.getenv('WEBSITE_SITE_REGION', 'unknown'),
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'azure': {
                'app_service': bool(os.getenv('WEBSITES_PORT')),
                'redis_configured': bool(os.getenv('REDIS_HOST')),
                'database_type': 'azure_sql' if 'database.windows.net' in os.getenv('DATABASE_URL', '') else 'sqlite'
            }
        })

    # Template context processors
    @app.context_processor
    def inject_template_globals():
        """Inject global variables into all templates"""
        from datetime import datetime
        return {
            'now': datetime.now,
            'utcnow': datetime.utcnow
        }

    # Context processors
    from .navigation import NavigationManager
    
    @app.context_processor
    def inject_navigation():
        """Inject navigation menu vào tất cả templates"""
        return {
            'navigation_menu': NavigationManager.get_current_user_menu(),
            'navigation_manager': NavigationManager
        }
    
    return app, socketio

# Cho phép import hàm nạp dữ liệu mẫu từ app package
from .init_sample_data import init_sample_data

# Import services for dependency injection
# from .services import UserService, LabSessionService, AdminService
