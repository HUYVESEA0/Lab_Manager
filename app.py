from flask import Flask, render_template, redirect, url_for, flash, request, session, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
# Thay thế import url_parse từ werkzeug
from urllib.parse import urlparse
import datetime
import os
import random
import string
import json
from sqlalchemy import func
from flask_migrate import Migrate
from flask_caching import Cache
from functools import wraps
# Import models trước khi khởi tạo app
from models import db, User, SystemSetting, ActivityLog, init_app
from models import LabSession, SessionRegistration, LabEntry
from utils import log_activity, ensure_session_consistency
# Thêm import SessionHandler
from session_handler import SessionHandler
from utils import clear_auth_session
from werkzeug.exceptions import HTTPException
from werkzeug.datastructures import CombinedMultiDict, MultiDict
import traceback
from flask_wtf.csrf import CSRFError, CSRFProtect

app = Flask(__name__)  # Ensure this is defined at the module level
app.config.from_object('config.DevelopmentConfig')
# Cấu hình session để hết hạn sau 30 phút
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)
# Add a configuration flag to control UI changes
app.config['PRESERVE_USER_EXPERIENCE'] = True
app.config['SECRET_KEY'] = 'your-secret-key'  # Make sure this is properly set
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # Token valid for 1 hour

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Khởi tạo SQLAlchemy với Flask app
init_app(app)

# Khởi tạo Session Handler
session_handler = SessionHandler(app)

# Cấu hình cache
cache = Cache(app, config={
    'CACHE_TYPE': 'simple',  # Hoặc 'redis' nếu có Redis
    'CACHE_DEFAULT_TIMEOUT': 300  # 5 phút
})

migrate = Migrate(app, db)
# Thiết lập Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
# Import thêm decorator mới
from decorators import admin_required, admin_manager_required

# Add this after creating the Flask app but before any route definitions
@app.after_request
def set_secure_cookie(response):
    """Ensure all cookies have the secure flag set."""
    cookies = [cookie for cookie in response.headers if cookie[0] == 'Set-Cookie']
    
    for cookie_header in cookies:
        header_value = cookie_header[1]
        if '; secure' not in header_value.lower():
            # Add secure flag if not present
            response.headers.remove(cookie_header)
            response.headers.add(
                'Set-Cookie',
                f"{header_value}; Secure"
            )
    
    return response

# Khởi tạo admin user
def init_admin_user():
    # Không cần with app.app_context() vì function này sẽ được gọi trong một context
    # Check for admin_manager
    admin_manager = User.query.filter_by(role='admin_manager').first()
    if not admin_manager:
        admin_manager = User(
            username='HUYVIESEA',
            email='hhuy0847@gmail.com',
            role='admin_manager'
        )
        admin_manager.set_password('huyviesea@manager')
        db.session.add(admin_manager)
        db.session.commit()
        print('Admin Manager created: hhuy0847@gmail.com / admin_manager')
        
    # Check for regular admin
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            username='ADMINUSER',
            email='admin@example.com',
            role='admin'
        )
        admin.set_password('huyviesea@admin')
        db.session.add(admin)
        db.session.commit()
        print('Admin created: admin@example.com / huyviesea@admin')
        
    # Check for regular user
    user = User.query.filter_by(role='user').first()
    if not user:
        user = User(
            username='REGULARUSER',
            email='user@example.com',
            role='user'
        )
        user.set_password('huyviesea@user')
        db.session.add(user)
        db.session.commit()
        print('User created: user@example.com / huyviesea@user')

# Đảm bảo database tables được tạo và dữ liệu ban đầu được thêm
# trong app context
with app.app_context():
    db.create_all()
    init_admin_user()

from forms import LoginForm, RegistrationForm, UserEditForm, CreateUserForm, SystemSettingsForm
from forms import LabSessionForm, SessionRegistrationForm, LabVerificationForm, LabResultForm

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Cache trang index trong 5 phút
@app.route('/')
@cache.cached(timeout=300)  # Cache trong 5 phút
def index():
    # Đếm số lần truy cập trang chủ
    if 'visits' in session:
        session['visits'] = session.get('visits') + 1
    else:
        session['visits'] = 1
    # Lưu thời gian truy cập cuối cùng
    session['last_visit'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    notifications = []
    news_items = []
    lab_sessions = []
    if current_user.is_authenticated and current_user.is_admin_manager():
        notifications = ["New user registration pending approval", "System maintenance scheduled"]
        news_items = ["Version 2.0 released", "New features added to lab management"]
        lab_sessions = [
            {"title": "Python Basics", "date": "2023-10-15", "status": "Completed"},
            {"title": "Advanced Flask", "date": "2023-10-20", "status": "Ongoing"},
        ]
    stats = {
        'lab_session_count': LabSession.query.count(),
        'active_lab_sessions': LabSession.query.filter_by(is_active=True).count()
    }
    return render_template('index.html', notifications=notifications, news_items=news_items, lab_sessions=lab_sessions, stats=stats)

# Tạo các utility function cho việc tối ưu
def get_user_stats(refresh=False):
    cache_key = f'user_stats_{current_user.id if current_user.is_authenticated else 0}'
    if refresh:
        cache.delete(cache_key)
    stats = cache.get(cache_key)
    if stats is None:
        # Tính toán và caching kết quả
        stats = {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'total_sessions': LabSession.query.count()
        }
        cache.set(cache_key, stats, timeout=300)  # 5 phút
    return stats

# Thêm decorators để giới hạn tốc độ truy cập API
def rate_limit(max_calls, period=60):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            key = f"rate_limit_{request.remote_addr}_{f.__name__}"
            current = cache.get(key) or 0
            if current >= max_calls:
                return jsonify({"error": "Too many requests"}), 429
            cache.set(key, current + 1, timeout=period)
            return f(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    login_form = LoginForm()
    reg_form = RegistrationForm()
    
    if reg_form.validate_on_submit():
        user = User(username=reg_form.username.data, email=reg_form.email.data)
        user.set_password(reg_form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Tài khoản của bạn đã được tạo! Bạn có thể đăng nhập ngay bây giờ', 'success')
        return redirect(url_for('login'))
    
    return render_template('log_regis.html', login_form=login_form, reg_form=reg_form, form=reg_form, register=True, title='Đăng ký')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    login_form = LoginForm()
    reg_form = RegistrationForm()
    
    # Store next URL from query params for later use
    if request.args.get('next'):
        session['next_url'] = request.args.get('next')
    
    # Debug log for request data
    app.logger.debug(f"Login request method: {request.method}")
    app.logger.debug(f"Form data: {request.form}")
    
    try:
        if request.method == 'POST' and login_form.validate_on_submit():
            try:
                # Find user by email
                user = User.query.filter_by(email=login_form.email.data.lower().strip()).first()
            
                if not user:
                    flash('Email không tồn tại trong hệ thống', 'danger')
                    app.logger.warning(f"Login failed: Email not found: {login_form.email.data}")
                    return render_template('log_regis.html', login_form=login_form, reg_form=reg_form, 
                                          form=login_form, register=False, title='Đăng nhập')
                
                # Check password
                if not user.check_password(login_form.password.data):
                    flash('Mật khẩu không chính xác', 'danger')
                    app.logger.warning(f"Login failed: Incorrect password for {user.email}")
                    return render_template('log_regis.html', login_form=login_form, reg_form=reg_form, 
                                          form=login_form, register=False, title='Đăng nhập')
                
                # Log the login activity
                log_activity('User login', f"Successful login from {request.remote_addr}", user)
                
                # FIXED: Preserve critical session values but don't clear the session
                # This prevents losing important data like CSRF tokens
                important_keys = ['csrf_token', 'next_url', 'next']
                preserved_values = {k: session[k] for k in important_keys if k in session}
                
                # Login the user first
                login_user(user, remember=login_form.remember_me.data)
                
                # Then update any preserved session data
                for k, v in preserved_values.items():
                    session[k] = v
                
                # Add user info to session
                session['user_email'] = user.email
                session['login_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Show success message
                flash('Đăng nhập thành công!', 'success')
                
                # Determine redirect URL - check multiple possible sources
                next_url = request.args.get('next')
                if not next_url and 'next_url' in session:
                    next_url = session.pop('next_url', None)
                
                # Check if next URL is also in session from Flask-Login
                if not next_url and 'next' in session:
                    next_url = session.pop('next', None)
                    
                # Check if redirect URL is safe and redirect if it is
                if next_url and url_has_allowed_host_and_scheme(next_url, request.host):
                    app.logger.info(f"Redirecting after login to: {next_url}")
                    return redirect(next_url)
                else:
                    app.logger.info("Redirecting to dashboard after login")
                    return redirect(url_for('dashboard'))
                
            except Exception as e:
                app.logger.error(f"Error during login: {str(e)}")
                flash('Đã xảy ra lỗi trong quá trình đăng nhập. Vui lòng thử lại sau.', 'danger')
        
        # Display form validation errors
        elif request.method == 'POST':
            app.logger.warning(f"Form validation failed with errors: {login_form.errors}")
            for field, errors in login_form.errors.items():
                for error in errors:
                    flash(f'{getattr(login_form, field).label.text if field != "csrf_token" else "CSRF Token"}: {error}', 'danger')
    
    except Exception as e:
        app.logger.error(f"Unexpected error during login process: {str(e)}")
        flash("Đã xảy ra lỗi không mong muốn. Vui lòng thử lại sau.", "danger")
    
    return render_template('log_regis.html', login_form=login_form, reg_form=reg_form, 
                          form=login_form, register=False, title='Đăng nhập')

@app.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        username = current_user.username
        log_activity('User logout', f'User {username} logged out')
        
        # Lưu thời gian đăng xuất trước khi xóa session
        logout_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Đăng xuất người dùng
        logout_user()
        
        # Xóa các session liên quan đến xác thực
        clear_auth_session()
        
        # Đặt thông báo đăng xuất
        flash(f'Bạn đã đăng xuất lúc {logout_time}', 'info')
    
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Cache theo user_id để mỗi người dùng có cache riêng
    cache_key = f'dashboard_{current_user.id}'
    cached_data = cache.get(cache_key)
    
    if cached_data is None:
        session_data = {
            'visits': session.get('visits', 0),
            'last_visit': session.get('last_visit', 'N/A'),
            'login_time': session.get('login_time', 'N/A')
        }
        # Lưu vào cache
        cache.set(cache_key, session_data, timeout=60)  # 1 phút
    else:
        session_data = cached_data
        
    return render_template('dashboard.html', session_data=session_data)

@app.route('/session-manager')
@login_required
def session_manager():
    return render_template('session_manager.html', session=session)

@app.route('/set-session', methods=['POST'])
@login_required
def set_session():
    key = request.form.get('key')
    value = request.form.get('value')
    if key and value:
        session[key] = value
        flash(f'Khóa session "{key}" đã được thiết lập thành công!', 'success')
    else:
        flash('Cả khóa và giá trị đều là bắt buộc', 'danger')
    return redirect(url_for('session_manager'))

@app.route('/delete-session/<key>')
@login_required
def delete_session(key):
    if key in session:
        session.pop(key, None)
        flash(f'Khóa session "{key}" đã được xóa', 'success')
    else:
        flash(f'Không tìm thấy khóa session "{key}"', 'danger')
    return redirect(url_for('session_manager'))

@app.route('/clear-session')
@login_required
def clear_session():
    user_email = session.get('user_email')
    login_time = session.get('login_time')
    session.clear()
    if user_email:
        session['user_email'] = user_email
    if login_time:
        session['login_time'] = login_time
    flash('Tất cả dữ liệu phiên đã được xóa', 'success')
    return redirect(url_for('session_manager'))

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    if current_user.role == 'admin_manager':
        users = User.query.order_by(User.created_at.desc()).all()
    else:
        users = User.query.filter_by(role='user').order_by(User.created_at.desc()).all()
    recent_lab_sessions = LabSession.query.order_by(LabSession.date.desc()).limit(5).all()
    recent_logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(5).all()
    stats = {
        'user_count': User.query.count(),
        'lab_session_count': LabSession.query.count(),
        'activity_count': ActivityLog.query.count()
    }
    return render_template('admin/dashboard.html',
                          users=users, 
                          stats=stats, 
                          recent_logs=recent_logs, 
                          recent_lab_sessions=recent_lab_sessions,
                          is_admin_manager=current_user.role == 'admin_manager')

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/create-user', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Người dùng {form.username.data} đã được tạo thành công!', 'success')
        return redirect(url_for('admin_users'))
    return render_template('admin/create_user.html', form=form)

@app.route('/admin/edit-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserEditForm(original_username=user.username, original_email=user.email)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        if request.form.get('change_password'):
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            if new_password and new_password == confirm_password:
                user.set_password(new_password)
            elif new_password:
                flash('Xác nhận mật khẩu không khớp!', 'danger')
                return render_template('admin/edit_user.html', form=form, user=user)
        db.session.commit()
        flash(f'Người dùng {user.username} đã được cập nhật thành công!', 'success')
        return redirect(url_for('admin_users'))
    form.username.data = user.username
    form.email.data = user.email
    form.role.data = user.role
    return render_template('admin/edit_user.html', form=form, user=user)

@app.route('/admin/make-admin/<int:user_id>')
@login_required
@admin_manager_required
def make_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'user':
        flash('Chỉ người dùng thường mới có thể được nâng cấp lên quản trị viên.', 'danger')
        return redirect(url_for('admin_users'))
    user.role = 'admin'
    db.session.commit()
    log_activity('Make admin', f'User {user.username} was promoted to admin.')
    flash(f'Người dùng {user.username} đã được nâng cấp lên quản trị viên!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/make-admin-manager/<int:user_id>')
@login_required
@admin_manager_required
def make_admin_manager(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'admin':
        flash('Chỉ quản trị viên mới có thể được nâng cấp lên quản trị viên cấp cao.', 'danger')
        return redirect(url_for('admin_users'))
    user.role = 'admin_manager'
    db.session.commit()
    log_activity('Make admin manager', f'User {user.username} was promoted to admin_manager.')
    flash(f'Người dùng {user.username} đã được nâng cấp lên quản trị viên cấp cao!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/remove-admin/<int:user_id>')
@login_required
@admin_manager_required
def remove_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.role not in ['admin', 'admin_manager']:
        flash('Chỉ quản trị viên hoặc quản trị viên cấp cao mới có thể bị hạ cấp.', 'danger')
        return redirect(url_for('admin_users'))
    user.role = 'user'
    db.session.commit()
    log_activity('Remove admin', f'User {user.username} was demoted to user.')
    flash(f'Người dùng {user.username} đã bị hạ cấp xuống người dùng thường!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/delete-user/<int:user_id>')
@login_required
@admin_manager_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin_manager':
        flash('Không thể xóa quản trị viên cấp cao.', 'danger')
        return redirect(url_for('admin_users'))
    db.session.delete(user)
    db.session.commit()
    log_activity('Delete user', f'User {user.username} was deleted.')
    flash(f'Người dùng {user.username} đã bị xóa!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
@admin_required
@cache.cached(timeout=60)
def system_settings():
    if SystemSetting.query.count() == 0:
        SystemSetting.set_setting('app_name', 'Python Manager', 'string', 'Application Name')
        SystemSetting.set_setting('app_description', 'A Flask application for managing Python projects', 'string', 'Application Description')
        SystemSetting.set_setting('enable_registration', True, 'boolean', 'Enable User Registration')
        SystemSetting.set_setting('enable_password_reset', True, 'boolean', 'Enable Password Reset')
        SystemSetting.set_setting('items_per_page', 25, 'integer', 'Number of items per page in listings')
    form = SystemSettingsForm()
    if form.validate_on_submit():
        SystemSetting.set_setting('app_name', form.app_name.data, 'string', 'Application Name')
        SystemSetting.set_setting('app_description', form.app_description.data, 'string', 'Application Description')
        SystemSetting.set_setting('enable_registration', form.enable_registration.data, 'boolean', 'Enable User Registration')
        SystemSetting.set_setting('enable_password_reset', form.enable_password_reset.data, 'boolean', 'Enable Password Reset')
        SystemSetting.set_setting('items_per_page', form.items_per_page.data, 'integer', 'Number of items per page in listings')
        db.session.commit()
        log_activity('Update settings', 'System settings were updated')
        flash('Cài đặt hệ thống đã được cập nhật thành công!', 'success')
        return redirect(url_for('system_settings'))
    form.app_name.data = SystemSetting.get_setting('app_name', 'Python Manager')
    form.app_description.data = SystemSetting.get_setting('app_description', 'A Flask application for managing Python projects')
    form.enable_registration.data = SystemSetting.get_setting('enable_registration', True)
    form.enable_password_reset.data = SystemSetting.get_setting('enable_password_reset', True)
    form.items_per_page.data = SystemSetting.get_setting('items_per_page', 25)
    settings = SystemSetting.query.all()
    if current_user.is_admin_manager():
        return render_template('admin/admin_system_settings.html', form=form, settings=settings)
    return render_template('admin/system_settings.html', form=form, settings=settings)

@app.route('/admin/settings/reset', methods=['GET', 'POST'])
@login_required
@admin_manager_required
def reset_settings():
    """Reset all system settings to default values"""
    if request.method == 'POST' and request.form.get('confirm') == 'yes':
        # Xóa tất cả các cài đặt hiện tại
        SystemSetting.query.delete()
        db.session.commit()
        # Khởi tạo lại các cài đặt mặc định
        SystemSetting.set_setting('app_name', 'Python Manager', 'string', 'Application Name')
        SystemSetting.set_setting('app_description', 'A Flask application for managing Python projects', 'string', 'Application Description')
        SystemSetting.set_setting('enable_registration', True, 'boolean', 'Enable User Registration')
        SystemSetting.set_setting('enable_password_reset', True, 'boolean', 'Enable Password Reset')
        SystemSetting.set_setting('items_per_page', 25, 'integer', 'Number of items per page in listings')
        log_activity('Reset settings', 'All system settings were reset to default values')
        flash('Tất cả cài đặt hệ thống đã được đặt lại về giá trị mặc định.', 'success')
        return redirect(url_for('system_settings'))
    return render_template('admin/reset_settings.html')

@app.route('/admin/logs/clear', methods=['POST'])
@login_required
@admin_required
def clear_logs():
    if request.form.get('confirm') == 'yes':
        log_activity('Clear all logs', 'All activity logs were cleared from the system')
        last_log = ActivityLog.query.order_by(ActivityLog.id.desc()).first()
        if last_log:
            ActivityLog.query.filter(ActivityLog.id != last_log.id).delete()
        else:
            ActivityLog.query.delete()
        db.session.commit()
        flash('Tất cả nhật ký hoạt động đã được xóa', 'success')
    else:
        flash('Yêu cầu xác nhận để xóa nhật ký', 'danger')
    return redirect(url_for('activity_logs'))

@app.route('/admin/activity-logs')
@login_required
@admin_required
def activity_logs():
    page = request.args.get('page', 1, type=int)
    logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template('admin/logs.html', logs=logs)

@app.route('/admin/system-operations')
@login_required
@admin_manager_required
def system_operations():
    return render_template('admin/system_operations.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query or len(query) < 2:
        flash('Vui lòng nhập ít nhất 2 ký tự để tìm kiếm', 'warning')
        return redirect(url_for('index'))
    users = User.query.filter(
        (User.username.ilike(f'%{query}%')) |
        (User.email.ilike(f'%{query}%'))
    ).all()
    activities = []
    if current_user.is_authenticated and current_user.is_admin():
        activities = ActivityLog.query.filter(
            (ActivityLog.action.ilike(f'%{query}%')) |
            (ActivityLog.details.ilike(f'%{query}%'))
        ).limit(25).all()
    settings = []
    if current_user.is_authenticated and current_user.is_admin():
        settings = SystemSetting.query.filter(
            (SystemSetting.key.ilike(f'%{query}%')) |
            (SystemSetting.value.ilike(f'%{query}%')) |
            (SystemSetting.description.ilike(f'%{query}%'))
        ).all()
    if current_user.is_authenticated:
        log_activity('Search', f'User searched for: {query}')
    results_found = bool(users or activities or settings)
    return render_template('search_results.html',
                          query=query, 
                          users=users,
                          activities=activities,
                          settings=settings,
                          results_found=results_found)

@app.route('/lab-sessions')
@login_required
def lab_sessions():
    now = datetime.datetime.now()
    available_sessions = LabSession.query.filter(
        LabSession.is_active == True,
        LabSession.date >= now.date(),
        LabSession.start_time > now
    ).order_by(LabSession.date, LabSession.start_time).all()
    registered_sessions = LabSession.query.join(SessionRegistration).filter(
        SessionRegistration.student_id == current_user.id
    ).order_by(LabSession.date, LabSession.start_time).all()
    return render_template('lab/lab_sessions.html', 
                           available_sessions=available_sessions, 
                           registered_sessions=registered_sessions)

@app.route('/register-lab-session/<int:session_id>', methods=['GET', 'POST'])
@login_required
def register_lab_session(session_id):
    lab_session = LabSession.query.get_or_404(session_id)
    if not lab_session.can_register(): 
        flash('Ca thực hành này không khả dụng cho đăng ký.', 'danger')
        return redirect(url_for('lab_sessions'))
    existing_reg = SessionRegistration.query.filter_by(
        student_id=current_user.id, session_id=session_id
    ).first()
    if existing_reg:
        flash('Bạn đã đăng ký ca thực hành này.', 'warning')
        return redirect(url_for('lab_sessions'))
    form = SessionRegistrationForm()
    form.session_id.data = session_id
    if form.validate_on_submit():
        registration = SessionRegistration(
            student_id=current_user.id,
            session_id=session_id,
            notes=form.notes.data
        )
        db.session.add(registration)
        db.session.commit()
        log_activity('Lab registration', f'Registered for lab session {lab_session.title}')
        flash('Đăng ký ca thực hành thành công!', 'success')
        return redirect(url_for('lab_sessions'))
    return render_template('lab/register_session.html', form=form, session=lab_session)

@app.route('/verify-lab-session/<int:session_id>', methods=['GET', 'POST'])
@login_required
def verify_lab_session(session_id):
    lab_session = LabSession.query.get_or_404(session_id)
    registration = SessionRegistration.query.filter_by(
        student_id=current_user.id, session_id=session_id
    ).first_or_404()
    if not lab_session.is_in_progress():
        flash('Ca thực hành này hiện không diễn ra.', 'danger')
        return redirect(url_for('my_lab_sessions'))
    existing_entry = LabEntry.query.filter_by(
        student_id=current_user.id, session_id=session_id
    ).first()
    if existing_entry:
        return redirect(url_for('lab_session_active', entry_id=existing_entry.id))
    form = LabVerificationForm()
    if form.validate_on_submit():
        if form.verification_code.data == lab_session.verification_code:
            entry = LabEntry(
                student_id=current_user.id,
                session_id=session_id
            )
            db.session.add(entry)
            registration.attendance_status = 'attended'
            db.session.commit()
            log_activity('Lab check-in', f'Checked in to lab session {lab_session.title}')
            flash('Xác thực thành công! Bạn đã bắt đầu ca thực hành.', 'success')
            return redirect(url_for('lab_session_active', entry_id=entry.id))
        else:
            flash('Mã xác thực không đúng.', 'danger')
    return render_template('lab/verify_session.html', form=form, session=lab_session)

@app.route('/lab-session-active/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def lab_session_active(entry_id):
    entry = LabEntry.query.filter_by(
        id=entry_id, student_id=current_user.id
    ).first_or_404()
    lab_session = entry.lab_session
    if entry.check_out_time:
        flash('Ca thực hành này đã kết thúc.', 'info')
        return redirect(url_for('my_lab_sessions'))
    form = LabResultForm()
    if form.validate_on_submit():
        entry.lab_result = form.lab_result.data
        entry.check_out_time = datetime.datetime.now()
        db.session.commit()
        log_activity('Lab check-out', f'Completed lab session {lab_session.title}')
        flash('Bạn đã nộp kết quả và kết thúc ca thực hành!', 'success')
        return redirect(url_for('my_lab_sessions'))
    now = datetime.datetime.now()
    time_elapsed = now - entry.check_in_time
    time_remaining = lab_session.end_time - now if now < lab_session.end_time else datetime.timedelta(0)
    return render_template('lab/active_session.html',
                           entry=entry,
                           session=lab_session,
                           form=form,
                           time_elapsed=time_elapsed,
                           time_remaining=time_remaining)

@app.route('/my-lab-sessions')
@login_required
def my_lab_sessions():
    registered_sessions = LabSession.query.join(SessionRegistration).filter(
        SessionRegistration.student_id == current_user.id
    ).order_by(LabSession.date, LabSession.start_time).all()
    lab_history = LabEntry.query.filter_by(
        student_id=current_user.id
    ).order_by(LabEntry.check_in_time.desc()).all()
    return render_template('lab/my_sessions.html',
                           sessions=registered_sessions,
                           lab_history=lab_history)

@app.route('/admin/lab-sessions')
@login_required
@admin_required
def admin_lab_sessions():
    lab_sessions = LabSession.query.order_by(LabSession.date.desc(), LabSession.start_time).all()
    return render_template('admin/lab_sessions.html', sessions=lab_sessions)

@app.route('/admin/create-lab-session', methods=['GET', 'POST'])
@login_required
@admin_required
def create_lab_session():
    form = LabSessionForm()
    if form.validate_on_submit():
        verification_code = form.verification_code.data
        if not verification_code:
            verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Parse date string to datetime.date object
        date_obj = datetime.datetime.strptime(form.date.data, '%Y-%m-%d').date()
        
        # Parse time strings to datetime.time objects
        if isinstance(form.start_time.data, str):
            start_time_obj = datetime.datetime.strptime(form.start_time.data, '%H:%M').time()
        else:
            start_time_obj = form.start_time.data
            
        if isinstance(form.end_time.data, str):
            end_time_obj = datetime.datetime.strptime(form.end_time.data, '%H:%M').time()
        else:
            end_time_obj = form.end_time.data
        
        # Now use the proper date and time objects
        start_datetime = datetime.datetime.combine(date_obj, start_time_obj)
        end_datetime = datetime.datetime.combine(date_obj, end_time_obj)
        
        lab_session = LabSession(
            title=form.title.data,
            description=form.description.data,
            date=date_obj,
            start_time=start_datetime,
            end_time=end_datetime,
            location=form.location.data,
            max_students=form.max_students.data,
            is_active=form.is_active.data,
            verification_code=verification_code,
            created_by=current_user.id
        )
        db.session.add(lab_session)
        db.session.commit()
        log_activity('Create lab session', f'Created lab session: {form.title.data}')
        flash(f'Ca thực hành "{form.title.data}" đã được tạo thành công! Mã xác thực: {verification_code}', 'success')
        return redirect(url_for('admin_lab_sessions'))
    return render_template('admin/create_lab_session.html', form=form)

@app.route('/admin/edit-lab-session/<int:session_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_lab_session(session_id):
    lab_session = LabSession.query.get_or_404(session_id)
    form = LabSessionForm()
    if form.validate_on_submit():
        # Parse date string to datetime.date object
        date_obj = datetime.datetime.strptime(form.date.data, '%Y-%m-%d').date()
        
        # Parse time strings to datetime.time objects
        if isinstance(form.start_time.data, str):
            start_time_obj = datetime.datetime.strptime(form.start_time.data, '%H:%M').time()
        else:
            start_time_obj = form.start_time.data
            
        if isinstance(form.end_time.data, str):
            end_time_obj = datetime.datetime.strptime(form.end_time.data, '%H:%M').time()
        else:
            end_time_obj = form.end_time.data
        
        # Now use the proper date and time objects
        start_datetime = datetime.datetime.combine(date_obj, start_time_obj)
        end_datetime = datetime.datetime.combine(date_obj, end_time_obj)
        
        lab_session.title = form.title.data
        lab_session.description = form.description.data
        lab_session.date = date_obj
        lab_session.start_time = start_datetime
        lab_session.end_time = end_datetime
        lab_session.location = form.location.data
        lab_session.max_students = form.max_students.data
        lab_session.is_active = form.is_active.data
        if form.verification_code.data:
            lab_session.verification_code = form.verification_code.data
        db.session.commit()
        log_activity('Edit lab session', f'Updated lab session: {lab_session.title}')
        flash(f'Ca thực hành "{lab_session.title}" đã được cập nhật!', 'success')
        return redirect(url_for('admin_lab_sessions'))
    form.title.data = lab_session.title
    form.description.data = lab_session.description
    form.date.data = lab_session.date
    form.start_time.data = lab_session.start_time.time()
    form.end_time.data = lab_session.end_time.time()
    form.location.data = lab_session.location
    form.max_students.data = lab_session.max_students
    form.is_active.data = lab_session.is_active
    form.verification_code.data = lab_session.verification_code
    return render_template('admin/edit_lab_session.html', form=form, session=lab_session)

@app.route('/admin/lab-session-attendees/<int:session_id>')
@login_required
@admin_required
def lab_session_attendees(session_id):
    lab_session = LabSession.query.get_or_404(session_id)
    registrations = SessionRegistration.query.filter_by(
        session_id=session_id
    ).join(User).order_by(User.username).all()
    entries = LabEntry.query.filter_by(
        session_id=session_id
    ).join(User).order_by(LabEntry.check_in_time).all()
    return render_template('admin/session_attendees.html',
                           session=lab_session,
                           registrations=registrations,
                           entries=entries)

@app.route('/admin/schedule-lab-sessions')
@login_required
@admin_manager_required
def schedule_lab_sessions():
    valid_sessions = db.session.query(
        LabSession, func.count(SessionRegistration.id).label('student_count')
    ).join(SessionRegistration).group_by(LabSession.id).having(
        func.count(SessionRegistration.id) >= 5
    ).order_by(LabSession.date, LabSession.start_time).all()
    pending_sessions = db.session.query(
        LabSession, func.count(SessionRegistration.id).label('student_count')
    ).join(SessionRegistration).group_by(LabSession.id).having(
        func.count(SessionRegistration.id) < 5
    ).order_by(LabSession.date, LabSession.start_time).all()
    return render_template('admin/schedule_sessions.html',
                           valid_sessions=valid_sessions,
                           pending_sessions=pending_sessions)

@app.route('/admin/schedule-lab-rooms', methods=['GET', 'POST'])
@login_required
@admin_manager_required
def schedule_lab_rooms():
    schedule = []  # Initialize schedule as an empty list
    if request.method == 'POST':
        lab_sessions = LabSession.query.filter_by(is_active=True).order_by(LabSession.date, LabSession.start_time).all()
        rooms = ['Room 1', 'Room 2', 'Room 3', 'Room 4', 'Room 5', 'Room 6']
        for i, session in enumerate(lab_sessions):
            room = rooms[i % len(rooms)]
            schedule.append({'session': session, 'room': room})
        flash('Các ca thực hành đã được lên lịch thành công!', 'success')
    return render_template('admin/schedule_lab_rooms.html', schedule=schedule)

@app.route('/admin/reset-database', methods=['GET', 'POST'])
@login_required
@admin_manager_required
def reset_database():
    if request.method == 'POST' and request.form.get('confirm') == 'yes':
        log_activity('Database reset', 'Database was reset by admin')
        with app.app_context():
            db.drop_all()
            db.create_all()
            init_admin_user()
        flash('Cơ sở dữ liệu đã được thiết lập lại thành công!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/reset_database.html')

@app.route('/admin-manager/dashboard')
@login_required
@admin_manager_required
def admin_manager_dashboard():
    stats = {
        'user_count': User.query.count(),
        'admin_count': User.query.filter(User.role.in_(['admin', 'admin_manager'])).count(),
        'regular_users': User.query.filter_by(role='user').count(),
        'lab_session_count': LabSession.query.count(),
        'active_lab_sessions': LabSession.query.filter(LabSession.date >= datetime.datetime.now()).count(),
        'activity_count': ActivityLog.query.count(),
        'system_settings_count': SystemSetting.query.count()
    }
    recent_logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(10).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_lab_sessions = LabSession.query.order_by(LabSession.date.desc()).limit(5).all()
    log_activity('Access system admin dashboard', 'Admin manager accessed the system dashboard')
    return render_template('admin/admin_manager_dashboard.html', 
                          stats=stats, 
                          recent_logs=recent_logs,
                          recent_users=recent_users,
                          recent_lab_sessions=recent_lab_sessions)

@app.route('/get-form-data/<form_type>')
def get_form_data(form_type):
    """Route để lấy dữ liệu form thông qua AJAX"""
    if form_type == 'login':
        form = LoginForm()
        return jsonify({'csrf_token': form.csrf_token._value()})
    elif form_type == 'register':
        form = RegistrationForm()
        return jsonify({'csrf_token': form.csrf_token._value()})
    return jsonify({'error': 'Invalid form type'})

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

@app.errorhandler(400)
def bad_request(e):
    return render_template('errors/error.html', 
                         error_title="Bad Request",
                         error_code="400",
                         error_message="The request could not be understood by the server.",
                         error_description="The request may contain syntax errors or invalid parameters.",
                         error_icon="fa-exclamation-circle"), 400

# Global error handler for all other exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    # Log the error
    app.logger.error(f"Unhandled exception: {str(e)}")
    
    # If it's already an HTTP exception, let the specific handlers deal with it
    if isinstance(e, HTTPException):
        return render_template('errors/error.html',
                              error_title=e.name,
                              error_code=e.code,
                              error_message=e.description,
                              error_description="An error occurred while processing your request.",
                              error_icon="fa-exclamation-triangle"), e.code
    
    # For all other exceptions, show a generic 500 error
    return render_template('errors/500.html'), 500

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    app.logger.error(f"CSRF Error: {str(e)}")
    flash("CSRF token validation failed. This could be due to your session expiring. Please try again.", "danger")
    return redirect(url_for('login'))

# Add this function to safely create a CombinedMultiDict
def safe_combine_dicts(dicts_or_dict):
    """
    Safely creates a CombinedMultiDict from input which might not be iterable.
    Handles the case where a single dict is passed instead of an iterable of dicts.
    """
    try:
        # If it's already a proper iterable of dicts
        if isinstance(dicts_or_dict, (list, tuple)):
            return CombinedMultiDict(dicts_or_dict)
        
        # If it's a single dict, wrap it in a list
        elif isinstance(dicts_or_dict, (dict, MultiDict)):
            return CombinedMultiDict([dicts_or_dict])
            
        # If it's None, return an empty CombinedMultiDict
        elif dicts_or_dict is None:
            return CombinedMultiDict()
            
        # If it's something else entirely
        else:
            app.logger.error(f"Invalid type passed to combine_dicts: {type(dicts_or_dict)}")
            return CombinedMultiDict()
            
    except Exception as e:
        app.logger.error(f"Error creating CombinedMultiDict: {e}")
        return CombinedMultiDict()

# Find places where CombinedMultiDict is used directly and replace with safe_combine_dicts
# For example, if you have code like:
# combined_data = CombinedMultiDict(request.form)
# Replace it with:
# combined_data = safe_combine_dicts(request.form)

# Function to validate if a redirect URL is safe
def url_has_allowed_host_and_scheme(url, allowed_hosts):
    """
    Check if the URL's host is in the allowed hosts and uses a safe scheme.
    Returns True if the URL is safe to redirect to, False otherwise.
    """
    if not url:
        return False
    
    parsed_url = urlparse(url)
    
    # If there's no netloc/host, it's a relative URL which is safe
    if not parsed_url.netloc:
        return True
    
    # Check if the host is allowed
    if isinstance(allowed_hosts, str):
        allowed_hosts = [allowed_hosts]
    
    return parsed_url.netloc in allowed_hosts and parsed_url.scheme in ('http', 'https')

# Add this error handler to catch unhandled exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled exception: {str(e)}\n{traceback.format_exc()}")
    return "An internal error occurred. Please try again later.", 500

@app.errorhandler(Exception)
def handle_general_exception(e):
    app.logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    # In development, you might want to see the full traceback
    if app.debug:
        raise e
    return render_template('error.html', error=str(e)), 500

application = app  # alias for WSGI servers

if __name__ == '__main__':
    # Hiển thị thông tin chạy ứng dụng
    print(f"Starting Python Manager in development mode (debug={app.debug})...")
    print(f"Visit http://127.0.0.1:5000 to access the application")
    print("Use Ctrl+C to stop the server")
    
    # Khởi chạy ứng dụng với cấu hình phát triển
    app.run(host='0.0.0.0', port=5000, debug=True)