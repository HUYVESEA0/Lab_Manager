from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, PasswordField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Regexp
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
    # Thông tin cơ bản
    ten_nguoi_dung = StringField("Tên người dùng", validators=[
        DataRequired(message="Tên người dùng là bắt buộc"), 
        Length(min=3, max=20, message="Tên người dùng phải có từ 3-20 ký tự"),
        Regexp(r'^[a-zA-Z0-9_]+$', message="Tên người dùng chỉ được chứa chữ cái, số và dấu gạch dưới")
    ])
    
    ho_ten = StringField("Họ và tên", validators=[
        DataRequired(message="Họ và tên là bắt buộc"),
        Length(min=2, max=100, message="Họ và tên phải có từ 2-100 ký tự")
    ])
    
    email = StringField("Email", validators=[
        DataRequired(message="Email là bắt buộc"), 
        Email(message="Email không hợp lệ")
    ])
    
    so_dien_thoai = StringField("Số điện thoại", validators=[
        Length(max=15, message="Số điện thoại không được quá 15 ký tự"),
        Regexp(r'^[0-9+\-\s()]*$', message="Số điện thoại chỉ được chứa số và các ký tự +, -, (, ), khoảng trắng")
    ])
    
    # Bảo mật
    mat_khau = PasswordField("Mật khẩu", validators=[
        DataRequired(message="Mật khẩu là bắt buộc"), 
        Length(min=6, message="Mật khẩu phải có ít nhất 6 ký tự")
    ])
    
    xac_nhan_mat_khau = PasswordField("Xác nhận mật khẩu", validators=[
        DataRequired(message="Xác nhận mật khẩu là bắt buộc"), 
        EqualTo("mat_khau", message="Mật khẩu xác nhận không khớp")
    ])
    
    # Vai trò và quyền
    vai_tro = SelectField("Vai trò", choices=[
        ("nguoi_dung", "Người dùng"), 
        ("quan_tri_vien", "Quản trị viên"), 
        ("quan_tri_he_thong", "Quản trị hệ thống")
    ], validators=[DataRequired(message="Vui lòng chọn vai trò")])
    
    # Cài đặt tài khoản
    kich_hoat = BooleanField("Kích hoạt tài khoản ngay", default=True)
    gui_email_chao_mung = BooleanField("Gửi email chào mừng", default=True)
    yeu_cau_doi_mat_khau = BooleanField("Yêu cầu đổi mật khẩu lần đầu đăng nhập", default=False)
    
    # Ghi chú
    ghi_chu = TextAreaField("Ghi chú", validators=[
        Length(max=500, message="Ghi chú không được quá 500 ký tự")
    ])
    
    submit = SubmitField("Tạo người dùng")

    def validate_ten_nguoi_dung(self, ten_nguoi_dung):
        nguoi_dung = NguoiDung.query.filter_by(ten_nguoi_dung=ten_nguoi_dung.data).first()
        if nguoi_dung:
            raise ValidationError("Tên người dùng đã tồn tại. Vui lòng chọn tên khác.")

    def validate_email(self, email):
        nguoi_dung = NguoiDung.query.filter_by(email=email.data).first()
        if nguoi_dung:
            raise ValidationError("Email đã được đăng ký. Vui lòng sử dụng email khác.")
    
    def validate_mat_khau(self, mat_khau):
        password = mat_khau.data
        if len(password) < 6:
            raise ValidationError("Mật khẩu phải có ít nhất 6 ký tự.")
        
        # Kiểm tra độ mạnh mật khẩu
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        
        score = sum([has_upper, has_lower, has_digit])
        if score < 2:
            raise ValidationError("Mật khẩu nên chứa ít nhất 2 trong các yếu tố: chữ hoa, chữ thường, số.")


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

class AdvancedRegistrationForm(FlaskForm):
    """Form đăng ký nâng cao với validation mạnh"""
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
            Length(min=8, message="Mật khẩu phải có ít nhất 8 ký tự"),
        ],
    )
    confirm_password = PasswordField(
        "Xác nhận mật khẩu",
        validators=[
            DataRequired(message="Xác nhận mật khẩu không được để trống"),
            EqualTo("password", message="Mật khẩu và xác nhận mật khẩu phải giống nhau"),
        ],
    )
    bio = TextAreaField(
        "Giới thiệu bản thân",
        validators=[Length(max=500, message="Giới thiệu không được quá 500 ký tự")],
        render_kw={"placeholder": "Viết vài dòng về bản thân bạn (tùy chọn)"}
    )
    terms_accepted = BooleanField(
        "Tôi đồng ý với điều khoản sử dụng",
        validators=[DataRequired(message="Bạn phải đồng ý với điều khoản sử dụng")]
    )
    submit = SubmitField("Đăng ký")

    def validate_ten_nguoi_dung(self, ten_nguoi_dung):
        # Check username format
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', ten_nguoi_dung.data):
            raise ValidationError("Tên người dùng chỉ được chứa chữ cái, số và dấu gạch dưới.")
        
        # Check if exists
        nguoi_dung = NguoiDung.query.filter_by(ten_nguoi_dung=ten_nguoi_dung.data).first()
        if nguoi_dung:
            raise ValidationError("Tên người dùng đã tồn tại. Vui lòng chọn tên khác.")

    def validate_email(self, email):
        nguoi_dung = NguoiDung.query.filter_by(email=email.data.lower().strip()).first()
        if nguoi_dung:
            raise ValidationError("Email này đã được đăng ký. Vui lòng sử dụng email khác.")

    def validate_password(self, password):
        """Validate password strength"""
        pwd = password.data
        
        if len(pwd) < 8:
            raise ValidationError("Mật khẩu phải có ít nhất 8 ký tự.")
        
        has_upper = any(c.isupper() for c in pwd)
        has_lower = any(c.islower() for c in pwd)
        has_digit = any(c.isdigit() for c in pwd)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in pwd)
        
        if not (has_upper and has_lower and has_digit and has_special):
            raise ValidationError(
                "Mật khẩu phải bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt."
            )

class BulkUserCreationForm(FlaskForm):
    """Form tạo người dùng hàng loạt"""
    users_data = TextAreaField(
        "Dữ liệu người dùng (JSON)",
        validators=[DataRequired(message="Dữ liệu người dùng không được để trống")],
        render_kw={
            "rows": 10,
            "placeholder": """[
  {
    "ten_nguoi_dung": "user1",
    "email": "user1@example.com",
    "mat_khau": "SecurePass123!",
    "vai_tro": "nguoi_dung"
  },
  {
    "ten_nguoi_dung": "user2", 
    "email": "user2@example.com",
    "mat_khau": "SecurePass456!",
    "vai_tro": "nguoi_dung"
  }
]"""
        }
    )
    submit = SubmitField("Tạo hàng loạt")

    def validate_users_data(self, users_data):
        import json
        try:
            data = json.loads(users_data.data)
            if not isinstance(data, list):
                raise ValidationError("Dữ liệu phải là một mảng JSON.")
            
            for i, user in enumerate(data):
                if not isinstance(user, dict):
                    raise ValidationError(f"Người dùng thứ {i+1} phải là một object.")
                
                required_fields = ['ten_nguoi_dung', 'email', 'mat_khau']
                for field in required_fields:
                    if field not in user:
                        raise ValidationError(f"Người dùng thứ {i+1} thiếu trường '{field}'.")
                        
        except json.JSONDecodeError:
            raise ValidationError("Dữ liệu JSON không hợp lệ.")
