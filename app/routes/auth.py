from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from ..forms import LoginForm, RegistrationForm, AdvancedRegistrationForm, ResetPasswordRequestForm, ResetPasswordForm
from ..models import NguoiDung, db
from ..utils import log_activity, clear_auth_session
from ..services.user_service import UserService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    login_form = LoginForm()
    reg_form = RegistrationForm()
    if reg_form.validate_on_submit():
        nguoi_dung = NguoiDung(ten_nguoi_dung=reg_form.ten_nguoi_dung.data, email=reg_form.email.data)
        nguoi_dung.dat_mat_khau(reg_form.password.data)
        from ..models import db
        db.session.add(nguoi_dung)
        db.session.commit()
        flash("Tài khoản của bạn đã được tạo! Bạn có thể đăng nhập ngay bây giờ", "success")
        return redirect(url_for('auth.login'))
    return render_template(
        "log_regis.html", login_form=login_form, reg_form=reg_form, form=reg_form, register=True, title="Đăng ký"
    )

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    login_form = LoginForm()
    reg_form = RegistrationForm()
    if request.args.get("next"):
        session["next_url"] = request.args.get("next")
    if request.method == "POST" and login_form.validate_on_submit():
        email_input = login_form.email.data.lower().strip() if login_form.email.data else ""
        nguoi_dung = NguoiDung.query.filter_by(email=email_input).first()
        if not nguoi_dung:
            flash("Email không tồn tại trong hệ thống", "danger")
            return render_template("auth/log_regis.html", login_form=login_form, reg_form=reg_form, form=login_form, register=False, title="Đăng nhập")
        if not nguoi_dung.kiem_tra_mat_khau(login_form.password.data):
            flash("Mật khẩu không chính xác", "danger")
            return render_template("auth/log_regis.html", login_form=login_form, reg_form=reg_form, form=login_form, register=False, title="Đăng nhập")
        log_activity("Đăng nhập người dùng", f"Đăng nhập thành công từ {request.remote_addr}", nguoi_dung)
        important_keys = ["csrf_token", "next_url", "next"]
        preserved_values = {k: session[k] for k in important_keys if k in session}
        login_user(nguoi_dung, remember=login_form.remember_me.data)
        for k, v in preserved_values.items():
            session[k] = v
        session["user_email"] = nguoi_dung.email
        session["login_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        flash("Đăng nhập thành công!", "success")
        next_url = request.args.get("next")
        
        if not next_url and "next_url" in session:
            next_url = session.pop("next_url", None)
        
        if not next_url and "next" in session:
            next_url = session.pop("next", None)
        
        if next_url:
            return redirect(next_url)
        
        if hasattr(nguoi_dung, "is_admin_manager") and nguoi_dung.is_admin_manager():
            return redirect(url_for("admin.admin_dashboard"))
        elif hasattr(nguoi_dung, "is_admin") and nguoi_dung.is_admin():
            return redirect(url_for("admin.admin_dashboard"))
        else:
            return redirect(url_for("user.dashboard"))
    return render_template("auth/log_regis.html", login_form=login_form, reg_form=reg_form, form=login_form, register=False, title="Đăng nhập")

@auth_bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    """Handle password reset request"""
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        email = form.email.data
        if email:
            email = email.lower().strip()
            user = NguoiDung.query.filter_by(email=email).first()
        else:
            user = None
        
        if user:
            from ..utils import send_password_reset_email
            if send_password_reset_email(user):
                flash('Đã gửi hướng dẫn đặt lại mật khẩu đến email của bạn.', 'info')
            else:
                flash('Có lỗi xảy ra khi gửi email. Vui lòng thử lại sau.', 'danger')
        else:
            # Don't reveal if email exists or not for security
            flash('Đã gửi hướng dẫn đặt lại mật khẩu đến email của bạn.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', title='Đặt lại mật khẩu', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token"""
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    
    user = NguoiDung.verify_reset_password_token(token)
    if not user:
        flash('Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn.', 'danger')
        return redirect(url_for('auth.reset_password_request'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Mật khẩu của bạn đã được đặt lại thành công.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', title='Đặt lại mật khẩu', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        ten_nguoi_dung = getattr(current_user, "ten_nguoi_dung", "")
        log_activity("User logout", f"User {ten_nguoi_dung} logged out")
        logout_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logout_user()
        clear_auth_session()
        flash(f"Bạn đã đăng xuất lúc {logout_time}", "info")
    return redirect(url_for('auth.login'))

@auth_bp.route('/register-advanced', methods=['GET', 'POST'])
def register_advanced():
    """Đăng ký nâng cao với validation mạnh"""
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))
    
    form = AdvancedRegistrationForm()
    if form.validate_on_submit():
        try:
            user_service = UserService()
            
            user_data = {
                'ten_nguoi_dung': form.ten_nguoi_dung.data,
                'email': form.email.data.lower().strip() if form.email.data else '',
                'mat_khau': form.password.data,
                'bio': form.bio.data or '',
                'vai_tro': 'nguoi_dung'
            }
            
            result, status_code = user_service.create_user(user_data)
            
            if status_code == 200:
                flash("Tài khoản của bạn đã được tạo thành công! Bạn có thể đăng nhập ngay bây giờ.", "success")
                return redirect(url_for('auth.login'))
            else:
                flash(result.get('message', 'Có lỗi xảy ra khi tạo tài khoản'), "danger")
                
        except Exception as e:
            flash("Có lỗi xảy ra khi tạo tài khoản. Vui lòng thử lại.", "danger")
    
    return render_template("auth/register_advanced.html", form=form, title="Đăng ký tài khoản")

@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    """Xác thực email"""
    try:
        user = NguoiDung.query.filter_by(verification_token=token).first()
        
        if not user:
            flash("Token xác thực không hợp lệ hoặc đã hết hạn.", "danger")
            return redirect(url_for('auth.login'))
        
        if user.xac_thuc_verification_token(token):
            user.xac_thuc_email()
            db.session.commit()
            
            log_activity("Xác thực email", f"Email {user.email} đã được xác thực", user)
            flash("Email của bạn đã được xác thực thành công!", "success")
        else:
            flash("Token xác thực không hợp lệ hoặc đã hết hạn.", "danger")
            
    except Exception as e:
        flash("Có lỗi xảy ra khi xác thực email.", "danger")
    
    return redirect(url_for('auth.login'))
