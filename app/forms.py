from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from .models import NguoiDung

class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email không được để trống"),
            Email(message="Vui lòng nhập địa chỉ email hợp lệ"),
        ],
    )
    password = PasswordField("Mật khẩu", validators=[DataRequired(message="Mật khẩu không được để trống")])
    remember_me = BooleanField("Ghi nhớ đăng nhập")
    submit = SubmitField("Đăng nhập")

class RegistrationForm(FlaskForm):
    ten_nguoi_dung = StringField(
        "Tên người dùng",
        validators=[
            DataRequired(message="Tên người dùng không được để trống"),
            Length(min=3, max=20, message="Tên người dùng phải từ 3 đến 20 ký tự"),
        ],
    )
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email không được để trống"),
            Email(message="Vui lòng nhập địa chỉ email hợp lệ"),
        ],
    )
    password = PasswordField(
        "Mật khẩu",
        validators=[
            DataRequired(message="Mật khẩu không được để trống"),
            Length(min=6, message="Mật khẩu phải có ít nhất 6 ký tự"),
        ],
    )
    confirm_password = PasswordField(
        "Xác nhận mật khẩu",
        validators=[
            DataRequired(message="Xác nhận mật khẩu không được để trống"),
            EqualTo("password", message="Mật khẩu và xác nhận mật khẩu phải giống nhau"),
        ],
    )
    submit = SubmitField("Đăng ký")

    def validate_ten_nguoi_dung(self, ten_nguoi_dung):
        nguoi_dung = NguoiDung.query.filter_by(ten_nguoi_dung=ten_nguoi_dung.data).first()
        if nguoi_dung:
            raise ValidationError("Tên người dùng đã tồn tại. Vui lòng chọn tên khác.")

    def validate_email(self, email):
        nguoi_dung = NguoiDung.query.filter_by(email=email.data).first()
        if nguoi_dung:
            raise ValidationError("Email này đã được đăng ký. Vui lòng sử dụng email khác.")

class UserEditForm(FlaskForm):
    ten_nguoi_dung = StringField("Tên người dùng", validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    vai_tro = SelectField("Vai trò", choices=[("nguoi_dung", "Người dùng"), ("quan_tri_vien", "Quản trị viên"), ("quan_tri_he_thong", "Quản trị hệ thống")])
    submit = SubmitField("Cập nhật người dùng")

    def __init__(self, original_ten_nguoi_dung, original_email, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.original_ten_nguoi_dung = original_ten_nguoi_dung
        self.original_email = original_email

    def validate_ten_nguoi_dung(self, ten_nguoi_dung):
        if ten_nguoi_dung.data != self.original_ten_nguoi_dung:
            nguoi_dung = NguoiDung.query.filter_by(ten_nguoi_dung=ten_nguoi_dung.data).first()
            if nguoi_dung:
                raise ValidationError("Tên người dùng đã tồn tại. Vui lòng chọn tên khác.")

    def validate_email(self, email):
        if email.data != self.original_email:
            nguoi_dung = NguoiDung.query.filter_by(email=email.data).first()
            if nguoi_dung:
                raise ValidationError("Email đã được đăng ký. Vui lòng sử dụng email khác.")

class CreateUserForm(FlaskForm):
    ten_nguoi_dung = StringField("Tên người dùng", validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    mat_khau = PasswordField("Mật khẩu", validators=[DataRequired(), Length(min=6)])
    xac_nhan_mat_khau = PasswordField("Xác nhận mật khẩu", validators=[DataRequired(), EqualTo("mat_khau")])
    vai_tro = SelectField("Vai trò", choices=[("nguoi_dung", "Người dùng"), ("quan_tri_vien", "Quản trị viên"), ("quan_tri_he_thong", "Quản trị hệ thống")])
    submit = SubmitField("Tạo người dùng")

    def validate_ten_nguoi_dung(self, ten_nguoi_dung):
        nguoi_dung = NguoiDung.query.filter_by(ten_nguoi_dung=ten_nguoi_dung.data).first()
        if nguoi_dung:
            raise ValidationError("Tên người dùng đã tồn tại. Vui lòng chọn tên khác.")

    def validate_email(self, email):
        nguoi_dung = NguoiDung.query.filter_by(email=email.data).first()
        if nguoi_dung:
            raise ValidationError("Email đã được đăng ký. Vui lòng sử dụng email khác.")

class SystemSettingsForm(FlaskForm):
    app_name = StringField("Application Name", validators=[DataRequired(), Length(max=100)])
    app_description = StringField("Application Description", validators=[Length(max=255)])
    enable_registration = BooleanField("Enable User Registration")
    enable_password_reset = BooleanField("Enable Password Reset")
    items_per_page = SelectField(
        "Items Per Page", choices=[(10, "10"), (25, "25"), (50, "50"), (100, "100")], coerce=int
    )
    submit = SubmitField("Save Settings")

class SessionRegistrationForm(FlaskForm):
    session_id = HiddenField("Session ID", validators=[DataRequired()])
    notes = TextAreaField("Notes (Optional)", validators=[Length(max=500)])
    submit = SubmitField("Register for Session")

    def validate_session_id(self, session_id):
        from flask_login import current_user
        from .models import CaThucHanh, DangKyCa
        ca = CaThucHanh.query.get(session_id.data)
        if not ca:
            raise ValidationError("Ca thực hành không hợp lệ.")
        if not ca.dang_hoat_dong:
            raise ValidationError("Ca thực hành này không còn hoạt động.")
        if ca.da_day():
            raise ValidationError("Ca thực hành này đã đủ số lượng đăng ký.")
        if datetime.utcnow() >= ca.gio_bat_dau:
            raise ValidationError("Đã hết thời gian đăng ký ca thực hành này.")
        existing_registration = DangKyCa.query.filter_by(
            nguoi_dung_ma=current_user.id, ca_thuc_hanh_ma=session_id.data
        ).first()
        if existing_registration:
            raise ValidationError("Bạn đã đăng ký ca thực hành này rồi.")

class LabSessionForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    date = StringField("Date", validators=[DataRequired()])
    start_time = StringField("Start Time", validators=[DataRequired()])
    end_time = StringField("End Time", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    max_students = StringField("Max Students", validators=[DataRequired()])
    is_active = BooleanField("Is Active")
    verification_code = StringField("Verification Code")
    submit = SubmitField("Save")

class LabVerificationForm(FlaskForm):
    verification_code = StringField("Verification Code", validators=[DataRequired()])
    submit = SubmitField("Verify")

class LabResultForm(FlaskForm):
    lab_result = TextAreaField("Lab Result", validators=[DataRequired()])
    submit = SubmitField("Submit")

class CourseForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Save")

class LessonForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Save")

class ProfileForm(FlaskForm):
    ten_nguoi_dung = StringField(
        "Tên người dùng", 
        validators=[
            DataRequired(message="Tên người dùng không được để trống"),
            Length(min=3, max=20, message="Tên người dùng phải từ 3 đến 20 ký tự")
        ]
    )
    email = StringField(
        "Email", 
        validators=[
            DataRequired(message="Email không được để trống"),
            Email(message="Vui lòng nhập địa chỉ email hợp lệ")
        ]
    )
    bio = TextAreaField(
        "Giới thiệu bản thân", 
        validators=[Length(max=500, message="Giới thiệu không được vượt quá 500 ký tự")]
    )
    submit = SubmitField("Cập nhật hồ sơ")

    def __init__(self, original_ten_nguoi_dung, original_email, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_ten_nguoi_dung = original_ten_nguoi_dung
        self.original_email = original_email

    def validate_ten_nguoi_dung(self, ten_nguoi_dung):
        if ten_nguoi_dung.data != self.original_ten_nguoi_dung:
            nguoi_dung = NguoiDung.query.filter_by(ten_nguoi_dung=ten_nguoi_dung.data).first()
            if nguoi_dung:
                raise ValidationError("Tên người dùng đã tồn tại. Vui lòng chọn tên khác.")

    def validate_email(self, email):
        if email.data != self.original_email:
            nguoi_dung = NguoiDung.query.filter_by(email=email.data).first()
            if nguoi_dung:
                raise ValidationError("Email đã được đăng ký. Vui lòng sử dụng email khác.")

class AccountSettingsForm(FlaskForm):
    current_password = PasswordField(
        "Mật khẩu hiện tại", 
        validators=[DataRequired(message="Vui lòng nhập mật khẩu hiện tại")]
    )
    new_password = PasswordField(
        "Mật khẩu mới", 
        validators=[
            DataRequired(message="Mật khẩu mới không được để trống"),
            Length(min=6, message="Mật khẩu phải có ít nhất 6 ký tự")
        ]
    )
    confirm_password = PasswordField(
        "Xác nhận mật khẩu mới", 
        validators=[
            DataRequired(message="Xác nhận mật khẩu không được để trống"),
            EqualTo("new_password", message="Mật khẩu mới và xác nhận mật khẩu phải giống nhau")
        ]
    )
    enable_2fa = BooleanField("Kích hoạt xác thực hai lớp")
    submit = SubmitField("Cập nhật cài đặt")

class ResetPasswordRequestForm(FlaskForm):
    """Form để yêu cầu đặt lại mật khẩu"""
    email = StringField(
        "Email",
        validators=[
            DataRequired(message="Email không được để trống"),
            Email(message="Vui lòng nhập địa chỉ email hợp lệ"),
        ],
    )
    submit = SubmitField("Gửi yêu cầu đặt lại mật khẩu")

    def validate_email(self, email):
        nguoi_dung = NguoiDung.query.filter_by(email=email.data.lower().strip()).first()
        if not nguoi_dung:
            raise ValidationError("Email này không tồn tại trong hệ thống.")

class ResetPasswordForm(FlaskForm):
    """Form để đặt mật khẩu mới"""
    password = PasswordField(
        "Mật khẩu mới",
        validators=[
            DataRequired(message="Mật khẩu không được để trống"),
            Length(min=6, message="Mật khẩu phải có ít nhất 6 ký tự"),
        ],
    )
    confirm_password = PasswordField(
        "Xác nhận mật khẩu mới",
        validators=[
            DataRequired(message="Xác nhận mật khẩu không được để trống"),
            EqualTo("password", message="Mật khẩu và xác nhận mật khẩu phải giống nhau"),
        ],
    )
    submit = SubmitField("Đặt lại mật khẩu")
