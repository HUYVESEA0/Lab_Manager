from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from ..forms import LoginForm, RegistrationForm
from ..models import NguoiDung
from ..utils import log_activity, clear_auth_session

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
        if hasattr(nguoi_dung, "la_nguoi_quan_tri_he_thong") and nguoi_dung.la_nguoi_quan_tri_he_thong:
            return redirect(url_for("admin.admin_dashboard"))
        elif hasattr(nguoi_dung, "la_nguoi_quan_tri") and nguoi_dung.la_nguoi_quan_tri:
            return redirect(url_for("admin.admin_dashboard"))
        else:
            return redirect(url_for("user.dashboard"))
    return render_template("auth/log_regis.html", login_form=login_form, reg_form=reg_form, form=login_form, register=False, title="Đăng nhập")

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
