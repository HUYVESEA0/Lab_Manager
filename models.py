# Models for Python Manager application
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index

# Khởi tạo db mà không cần tham số app
db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default='user')  # 'admin_manager', 'admin', or 'user'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, username=None, email=None, role='user'):
        self.username = username
        self.email = email
        self.role = role
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def is_admin(self):
        return self.role in ['admin', 'admin_manager']
    
    def is_admin_manager(self):
        return self.role == 'admin_manager'
    
    def get_role_level(self):
        """Get numerical representation of role level for comparison"""
        role_levels = {
            'admin_manager': 3,
            'admin': 2,
            'user': 1
        }
        return role_levels.get(self.role, 0)

    @property
    def is_admin_user(self):
        return self.role in ['admin', 'admin_manager']
    
    @property
    def is_admin_manager_user(self):
        return self.role == 'admin_manager'

    def __repr__(self):
        return f'<User {self.username}>'

class SystemSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(16), default='string')  # string, boolean, integer, etc.
    description = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SystemSetting {self.key}={self.value}>"
    
    @staticmethod
    def get_setting(key, default=None):
        """Get a setting value by key"""
        setting = SystemSetting.query.filter_by(key=key).first()
        if setting is None:
            return default
        
        # Convert value based on type
        if setting.type == 'boolean':
            return setting.value.lower() in ('true', '1', 'yes')
        elif setting.type == 'integer':
            return int(setting.value) if setting.value else 0
        elif setting.type == 'float':
            return float(setting.value) if setting.value else 0.0
        
        # Default: return as string
        return setting.value
    
    @staticmethod
    def set_setting(key, value, type='string', description=''):
        """Set or create a setting"""
        setting = SystemSetting.query.filter_by(key=key).first()
        
        if setting is None:
            setting = SystemSetting(key=key, description=description, type=type)
            db.session.add(setting)
            
        # Convert value to string for storage
        setting.value = str(value) if value is not None else ''
        setting.type = type
        if description:
            setting.description = description
            
        db.session.commit()
        return setting

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', backref='activities')
    action = db.Column(db.String(128), nullable=False)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 can be up to 45 chars
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ActivityLog {self.action} by {self.user.username if self.user else 'Unknown'} at {self.timestamp}>"

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    lessons = db.relationship('Lesson', backref='course', lazy=True)
    enrollments = db.relationship('Enrollment', backref='course', lazy=True)

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)

class LabSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    max_students = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    verification_code = db.Column(db.String(10), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    registrations = db.relationship('SessionRegistration', backref='lab_session', lazy=True)
    entries = db.relationship('LabEntry', backref='lab_session', lazy=True)

    def can_register(self):
        return self.is_active and self.date >= datetime.utcnow().date() and self.start_time > datetime.utcnow()

    def is_in_progress(self):
        now = datetime.utcnow()
        return self.start_time <= now <= self.end_time

    def is_full(self):
        return len(self.registrations) >= self.max_students

class SessionRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('lab_session.id'), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    attendance_status = db.Column(db.String(20), default='registered')
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

class LabEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('lab_session.id'), nullable=False)
    check_in_time = db.Column(db.DateTime, default=datetime.utcnow)
    check_out_time = db.Column(db.DateTime, nullable=True)
    lab_result = db.Column(db.Text, nullable=True)

def create_indexes():
    # Tạo các index cho các truy vấn phổ biến
    Index('idx_user_email', User.email)
    Index('idx_user_role', User.role)
    Index('idx_activity_timestamp', ActivityLog.timestamp)
    Index('idx_lab_session_date', LabSession.date)

def init_app(app):
    # Khởi tạo db với app
    db.init_app(app)
    
    # Tạo context để sử dụng db.create_all() nếu cần
    with app.app_context():
        db.create_all()
        create_indexes()