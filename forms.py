from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User
from datetime import datetime

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Email không được để trống'),
        Email(message='Vui lòng nhập địa chỉ email hợp lệ')
    ])
    password = PasswordField('Mật khẩu', validators=[
        DataRequired(message='Mật khẩu không được để trống')
    ])
    remember_me = BooleanField('Ghi nhớ đăng nhập')
    submit = SubmitField('Đăng nhập')

class RegistrationForm(FlaskForm):
    username = StringField('Tên người dùng', validators=[
        DataRequired(message='Tên người dùng không được để trống'),
        Length(min=3, max=20, message='Tên người dùng phải từ 3 đến 20 ký tự')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email không được để trống'),
        Email(message='Vui lòng nhập địa chỉ email hợp lệ')
    ])
    password = PasswordField('Mật khẩu', validators=[
        DataRequired(message='Mật khẩu không được để trống'),
        Length(min=6, message='Mật khẩu phải có ít nhất 6 ký tự')
    ])
    confirm_password = PasswordField('Xác nhận mật khẩu', validators=[
        DataRequired(message='Xác nhận mật khẩu không được để trống'),
        EqualTo('password', message='Mật khẩu và xác nhận mật khẩu phải giống nhau')
    ])
    submit = SubmitField('Đăng ký')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Tên người dùng đã tồn tại. Vui lòng chọn tên khác.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email này đã được đăng ký. Vui lòng sử dụng email khác.')

class UserEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[
        ('user', 'User'), 
        ('admin', 'Admin'),
        ('admin_manager', 'Admin Manager')
    ])
    submit = SubmitField('Update User')
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
        
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already taken. Please choose another one.')
                
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already registered. Please use another one.')

class CreateUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[
        ('user', 'User'), 
        ('admin', 'Admin'),
        ('admin_manager', 'Admin Manager')
    ])
    submit = SubmitField('Create User')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose another one.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use another one.')

class SystemSettingsForm(FlaskForm):
    app_name = StringField('Application Name', validators=[DataRequired(), Length(max=100)])
    app_description = StringField('Application Description', validators=[Length(max=255)])
    enable_registration = BooleanField('Enable User Registration')
    enable_password_reset = BooleanField('Enable Password Reset')
    items_per_page = SelectField('Items Per Page', 
                                choices=[(10, '10'), (25, '25'), (50, '50'), (100, '100')],
                                coerce=int)
    submit = SubmitField('Save Settings')

class SessionRegistrationForm(FlaskForm):
    session_id = HiddenField('Session ID', validators=[DataRequired()])
    notes = TextAreaField('Notes (Optional)', validators=[Length(max=500)])
    submit = SubmitField('Register for Session')
    
    def validate_session_id(self, session_id):
        from models import LabSession, SessionRegistration
        from flask_login import current_user
        
        session = LabSession.query.get(session_id.data)
        if not session:
            raise ValidationError('Invalid session selected.')
        
        if not session.is_active:
            raise ValidationError('This session is no longer active.')
            
        if session.is_full():
            raise ValidationError('This session is already full.')
            
        if datetime.utcnow() >= session.start_time:
            raise ValidationError('Registration for this session is closed.')
            
        # Check if user is already registered
        existing_registration = SessionRegistration.query.filter_by(
            student_id=current_user.id, session_id=session_id.data
        ).first()
        
        if existing_registration:
            raise ValidationError('You are already registered for this session.')

class LabSessionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    date = StringField('Date', validators=[DataRequired()])
    start_time = StringField('Start Time', validators=[DataRequired()])
    end_time = StringField('End Time', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    max_students = StringField('Max Students', validators=[DataRequired()])
    is_active = BooleanField('Is Active')
    verification_code = StringField('Verification Code')
    submit = SubmitField('Save')

class LabVerificationForm(FlaskForm):
    verification_code = StringField('Verification Code', validators=[DataRequired()])
    submit = SubmitField('Verify')

class LabResultForm(FlaskForm):
    lab_result = TextAreaField('Lab Result', validators=[DataRequired()])
    submit = SubmitField('Submit')

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class CourseForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Save')

class LessonForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Save')
