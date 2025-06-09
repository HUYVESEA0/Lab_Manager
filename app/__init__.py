from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO, join_room, leave_room
from .models import db, khoi_tao_ung_dung as models_khoi_tao_ung_dung
from .session_handler import SessionHandler
from .decorators import *
from .utils import *
import os

# Global SocketIO instance
socketio = None

def create_app():
    global socketio
    app = Flask(__name__)
    # Load environment variables from .env if present
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()    # Load config class based on FLASK_DEBUG (replacing deprecated FLASK_ENV)
    debug_mode = os.getenv("FLASK_DEBUG", "1").lower() in ['1', 'true', 'yes', 'on']
    env = "development" if debug_mode else "production"
    from config import config
    app.config.from_object(config.get(env, config["default"]))
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
    
    # Initialize extensions
    models_khoi_tao_ung_dung(app)
    SessionHandler(app)
    cache = Cache(app)
    migrate = Migrate(app, db)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # type: ignore
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
    
    # Register blueprints
    from .routes.admin import admin_bp
    from .routes.auth import auth_bp
    from .routes.lab import lab_bp
    from .routes.user import user_bp
    from .routes.search import search_bp
    
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(lab_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(search_bp)
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app, socketio

# Cho phép import hàm nạp dữ liệu mẫu từ app package
from .init_sample_data import init_sample_data
