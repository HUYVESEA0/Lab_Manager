# English Models for Lab Manager Flask app
from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.schema import Index
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
import time
import json


db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default="user")  # system_admin, admin, user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    bio = db.Column(db.Text, nullable=True)
    
    # Email verification fields
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), nullable=True)
    verification_token_expiry = db.Column(db.Integer, nullable=True)
    
    # Account status
    active = db.Column(db.Boolean, default=True)
    failed_login_attempts = db.Column(db.Integer, default=0)
    last_failed_login = db.Column(db.DateTime, nullable=True)
    account_locked_until = db.Column(db.DateTime, nullable=True)
    
    # Password reset fields
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.Integer, nullable=True)

    def is_admin(self):
        """Check if user is any type of admin"""
        return self.role in ["admin", "system_admin"]

    def is_system_admin(self):
        """Check if user is system admin"""
        return self.role == "system_admin"

    def __init__(self, username=None, email=None, role="user"):
        self.username = username
        self.email = email
        self.role = role

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_reset_token(self):
        """Generate password reset token"""
        from flask import current_app
        self.reset_token = secrets.token_urlsafe(32)
        expiry_seconds = current_app.config.get('RESET_TOKEN_EXPIRATION', 3600)
        self.reset_token_expiry = int(time.time()) + expiry_seconds
        return self.reset_token
    
    def verify_reset_token(self, token):
        """Verify password reset token"""
        if not self.reset_token or not self.reset_token_expiry:
            return False
        if self.reset_token != token:
            return False
        if int(time.time()) > self.reset_token_expiry:
            return False
        return True
    
    def clear_reset_token(self):
        """Clear reset token after use"""
        self.reset_token = None
        self.reset_token_expiry = None

    @staticmethod
    def verify_reset_password_token(token):
        """Find and verify user by reset token"""
        user = User.query.filter_by(reset_token=token).first()
        if user and user.verify_reset_token(token):
            return user
        return None

    def role_level(self):
        """Get role level for hierarchy comparison"""
        levels = {"system_admin": 3, "admin": 2, "user": 1}
        return levels.get(self.role, 0)

    def __repr__(self):
        return f"<User {self.username}>"


class SystemSetting(db.Model):
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    data_type = db.Column(db.String(16), default="string")
    description = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<SystemSetting {self.key}={self.value}>"

    @staticmethod
    def get_value(key, default=None):
        setting = SystemSetting.query.filter_by(key=key).first()
        if setting is None:
            return default
        if setting.data_type == "boolean":
            return setting.value.lower() in ("true", "1", "yes")
        elif setting.data_type == "integer":
            return int(setting.value) if setting.value else 0
        elif setting.data_type == "float":
            return float(setting.value) if setting.value else 0.0
        return setting.value

    @staticmethod
    def set_value(key, value, data_type="string", description=""):
        setting = SystemSetting.query.filter_by(key=key).first()
        if setting is None:
            setting = SystemSetting(key=key, description=description, data_type=data_type)
            db.session.add(setting)
        setting.value = str(value) if value is not None else ""
        setting.data_type = data_type
        if description:
            setting.description = description
        db.session.commit()
        return setting


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    user = db.relationship("User", backref="activity_logs")
    action = db.Column(db.String(128), nullable=False)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ActivityLog {self.action} by {self.user.username if self.user else 'Unknown'} at {self.timestamp}>"


class Course(db.Model):
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    lessons = db.relationship("Lesson", backref="course", lazy=True)
    enrollments = db.relationship("Enrollment", backref="course", lazy=True)


class Lesson(db.Model):
    __tablename__ = 'lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)


class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)


class LabSession(db.Model):
    __tablename__ = 'lab_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    max_participants = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    verification_code = db.Column(db.String(10), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Enhanced fields
    tags = db.Column(db.Text, nullable=True)  # JSON array of tags
    cover_image = db.Column(db.String(255), nullable=True)
    difficulty_level = db.Column(db.String(20), default="medium")  # easy, medium, hard
    required_equipment = db.Column(db.Text, nullable=True)  # JSON array
    internal_notes = db.Column(db.Text, nullable=True)
    allow_late_registration = db.Column(db.Boolean, default=False)
    auto_approve = db.Column(db.Boolean, default=True)
    notification_minutes = db.Column(db.Integer, default=60)
    status = db.Column(db.String(20), default="scheduled")  # scheduled, ongoing, completed, cancelled
    max_score = db.Column(db.Integer, default=100)
    time_limit_minutes = db.Column(db.Integer, nullable=True)
    
    # Relationships
    registrations = db.relationship("SessionRegistration", backref="lab_session", lazy=True, cascade="all, delete-orphan")
    entries = db.relationship("SessionEntry", backref="lab_session", lazy=True, cascade="all, delete-orphan")
    materials = db.relationship("SessionMaterial", backref="lab_session", lazy=True, cascade="all, delete-orphan")
    ratings = db.relationship("SessionRating", backref="lab_session", lazy=True, cascade="all, delete-orphan")

    def can_register(self):
        if not self.is_active:
            return False
        if self.status != "scheduled":
            return False
        now = datetime.utcnow()
        if self.allow_late_registration:
            return self.end_time > now
        return self.start_time > now

    def is_ongoing(self):
        now = datetime.utcnow()
        return (self.start_time <= now <= self.end_time and 
                self.status == "ongoing")

    def is_full(self):
        return len(self.registrations) >= self.max_participants

    def get_tags(self):
        """Get tags as list"""
        if self.tags:
            try:
                return json.loads(self.tags)
            except:
                return []
        return []

    def set_tags(self, tag_list):
        """Set tags from list"""
        self.tags = json.dumps(tag_list) if tag_list else None

    def get_equipment(self):
        """Get required equipment as list"""
        if self.required_equipment:
            try:
                return json.loads(self.required_equipment)
            except:
                return []
        return []

    def set_equipment(self, equipment_list):
        """Set required equipment from list"""
        self.required_equipment = json.dumps(equipment_list) if equipment_list else None

    def get_completion_rate(self):
        """Calculate completion rate"""
        total_registered = len(self.registrations)
        if total_registered == 0:
            return 0
        completed = len([entry for entry in self.entries if entry.exit_time])
        return (completed / total_registered) * 100

    def get_average_score(self):
        """Calculate average score"""
        scores = [entry.score for entry in self.entries if entry.score is not None]
        return sum(scores) / len(scores) if scores else 0


class SessionTemplate(db.Model):
    """Lab session templates for quick creation"""
    __tablename__ = 'session_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    default_title = db.Column(db.String(100), nullable=False)
    default_description = db.Column(db.Text, nullable=False)
    duration_minutes = db.Column(db.Integer, default=120)
    default_max_participants = db.Column(db.Integer, default=20)
    default_tags = db.Column(db.Text, nullable=True)
    default_equipment = db.Column(db.Text, nullable=True)
    difficulty_level = db.Column(db.String(20), default="medium")
    max_score = db.Column(db.Integer, default=100)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)


class SessionMaterial(db.Model):
    """Session materials/files"""
    __tablename__ = 'session_materials'
    
    id = db.Column(db.Integer, primary_key=True)
    lab_session_id = db.Column(db.Integer, db.ForeignKey("lab_sessions.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    file_type = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)


class Equipment(db.Model):
    """Equipment/Resource management"""
    __tablename__ = 'equipment'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    quantity_available = db.Column(db.Integer, default=1)
    status = db.Column(db.String(20), default="available")  # available, in_use, maintenance
    location = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class EquipmentBooking(db.Model):
    """Equipment booking for sessions"""
    __tablename__ = 'equipment_bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    lab_session_id = db.Column(db.Integer, db.ForeignKey("lab_sessions.id"), nullable=False)
    equipment_id = db.Column(db.Integer, db.ForeignKey("equipment.id"), nullable=False)
    quantity_booked = db.Column(db.Integer, default=1)
    booked_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    booked_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="pending")  # pending, confirmed, cancelled
    
    # Relationships
    equipment = db.relationship("Equipment", backref="bookings")
    lab_session = db.relationship("LabSession", backref="equipment_bookings")


class SessionRating(db.Model):
    """Session feedback and ratings"""
    __tablename__ = 'session_ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    lab_session_id = db.Column(db.Integer, db.ForeignKey("lab_sessions.id"), nullable=False)
    rated_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text, nullable=True)
    rated_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    """Notification system"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), default="info")  # info, warning, success, error
    link = db.Column(db.String(500), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)


class SessionRegistration(db.Model):
    """User registration for lab sessions"""
    __tablename__ = 'session_registrations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    lab_session_id = db.Column(db.Integer, db.ForeignKey("lab_sessions.id"), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default="registered")
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Enhanced fields
    priority = db.Column(db.Integer, default=0)
    is_confirmed = db.Column(db.Boolean, default=True)
    confirmed_at = db.Column(db.DateTime, nullable=True)


class SessionEntry(db.Model):
    """Lab session entry/exit tracking"""
    __tablename__ = 'session_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    lab_session_id = db.Column(db.Integer, db.ForeignKey("lab_sessions.id"), nullable=False)
    entry_time = db.Column(db.DateTime, default=datetime.utcnow)
    exit_time = db.Column(db.DateTime, nullable=True)
    results = db.Column(db.Text, nullable=True)
    
    # Enhanced fields
    score = db.Column(db.Integer, nullable=True)
    teacher_comment = db.Column(db.Text, nullable=True)
    submitted_files = db.Column(db.String(500), nullable=True)
    submission_status = db.Column(db.String(20), default="not_submitted")  # not_submitted, submitted, graded
    submitted_at = db.Column(db.DateTime, nullable=True)
    seat_assignment = db.Column(db.String(20), nullable=True)


def create_indexes():
    """Create database indexes for performance"""
    Index("idx_users_email", User.email)
    Index("idx_users_username", User.username)
    Index("idx_lab_sessions_date", LabSession.session_date)
    Index("idx_lab_sessions_status", LabSession.status)
    Index("idx_session_registrations_user", SessionRegistration.user_id)
    Index("idx_session_entries_user", SessionEntry.user_id)


def init_app(app):
    """Initialize database with the app"""
    db.init_app(app)
    create_indexes()
