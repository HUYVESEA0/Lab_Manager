from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from ...models import db, NguoiDung, CaiDatHeThong, ThongBao
from ...utils import log_activity
from ...forms import ProfileForm, AccountSettingsForm
from ...cache.cache_manager import cached_route, invalidate_user_cache, invalidate_model_cache
from ...cache.cached_queries import (
    get_dashboard_statistics, get_recent_activities, get_total_users,
    invalidate_user_caches, invalidate_activity_caches
)
from ...services.notification_service import NotificationService
from sqlalchemy.exc import NoResultFound
from ..base_routes import UserRouteMixin

user_bp = Blueprint('user', __name__, url_prefix='/user')

# Notification routes
@user_bp.route('/notifications')
@login_required
def notifications():
    """User notifications page"""
    try:
        notifications = NotificationService.get_user_notifications(current_user.id)
        unread_count = NotificationService.get_unread_count(current_user.id)
        
        return render_template('user/notifications.html',
                             notifications=notifications,
                             unread_count=unread_count)
    except Exception as e:
        current_app.logger.error(f"Error loading user notifications: {str(e)}")
        flash("Có lỗi xảy ra khi tải thông báo.", "danger")
        return render_template('user/notifications.html',
                             notifications=[], unread_count=0)






# Route dashboard cho users
@user_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_authenticated:
        if hasattr(current_user, "is_system_admin") and current_user.is_system_admin():
            return redirect(url_for("system_admin.system_dashboard"))
        elif hasattr(current_user, "is_admin") and current_user.is_admin():
            return redirect(url_for("admin.admin_dashboard"))
        else:
            return render_template("user/dashboard_new.html")
    else:
        return redirect(url_for("auth.login"))

# CSRF token endpoint
@user_bp.route('/csrf-token')
@login_required
def get_csrf_token():
    """Get CSRF token for user forms"""
    from flask_wtf.csrf import generate_csrf
    return jsonify({'csrf_token': generate_csrf()})

# Dashboard route
@user_bp.route('/dashboard-old')
@login_required
@cached_route(timeout=180, key_prefix='user_dashboard')
def dashboard_old():
    """User dashboard with caching - Uses API for data fetching"""
    session_data = {
        "visits": session.get("visits", 0),
        "last_visit": session.get("last_visit", "N/A"),
        "login_time": session.get("login_time", "N/A"),
    }
    
    # Template will fetch data via API which is also cached
    return render_template("user/dashboard.html", session_data=session_data)

# Session manager  
@user_bp.route('/session-manager')
@login_required
@cached_route(timeout=300, key_prefix='user_session_manager')
def session_manager():
    return render_template("session_manager.html", session=session)

# Set session key
@user_bp.route('/set-session', methods=['POST'])
@login_required
def set_session():
    key = request.form.get("key")
    value = request.form.get("value")
    if key and value:
        session[key] = value
        flash(f'Khóa session "{key}" đã được thiết lập thành công!', "success")
    else:
        flash("Cả khóa và giá trị đều là bắt buộc", "danger")
    return redirect(url_for("user.session_manager"))

# Delete session key
@user_bp.route('/delete-session/<key>')
@login_required
def delete_session(key):
    if key in session:
        session.pop(key, None)
        flash(f'Khóa session "{key}" đã được xóa', "success")
    else:
        flash(f'Không tìm thấy khóa session "{key}"', "danger")
    return redirect(url_for("user.session_manager"))

# Clear all session (except user_email, login_time)
@user_bp.route('/clear-session')
@login_required
def clear_session():
    user_email = session.get("user_email")
    login_time = session.get("login_time")
    session.clear()
    if user_email:
        session["user_email"] = user_email
    if login_time:
        session["login_time"] = login_time
    flash("Tất cả dữ liệu phiên đã được xóa", "success")
    return redirect(url_for("user.session_manager"))

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@cached_route(timeout=300, key_prefix='user_profile', unless=lambda: request.method == 'POST')
def profile():
    """User profile page"""
    form = ProfileForm(original_ten_nguoi_dung=current_user.ten_nguoi_dung, original_email=current_user.email)
    has_bio_field = hasattr(current_user, 'bio')
    if form.validate_on_submit():
        current_user.ten_nguoi_dung = form.ten_nguoi_dung.data
        current_user.email = form.email.data
        if has_bio_field and form.bio.data is not None:
            current_user.bio = form.bio.data
        db.session.commit()
        invalidate_user_cache(current_user.id)
        invalidate_user_caches()
        log_activity("Cập nhật hồ sơ", "Người dùng đã cập nhật thông tin hồ sơ cá nhân")
        flash("Hồ sơ cá nhân đã được cập nhật thành công!", "success")
        return redirect(url_for('user.profile'))
    if request.method == 'GET':
        form.ten_nguoi_dung.data = current_user.ten_nguoi_dung
        form.email.data = current_user.email
        if has_bio_field:
            form.bio.data = current_user.bio
    # Get user statistics
    user_stats = {}
    try:
        from ...models import DangKyCa, VaoCa, CaThucHanh
        total_sessions = DangKyCa.query.filter_by(nguoi_dung_ma=current_user.id).count()
        completed_sessions = VaoCa.query.filter_by(nguoi_dung_ma=current_user.id)\
                                       .filter(VaoCa.thoi_gian_ra.isnot(None)).count()
        total_hours = 0
        lab_entries = VaoCa.query.filter_by(nguoi_dung_ma=current_user.id)\
                                .filter(VaoCa.thoi_gian_ra.isnot(None)).all()
        for entry in lab_entries:
            if entry.thoi_gian_vao and entry.thoi_gian_ra:
                duration = entry.thoi_gian_ra - entry.thoi_gian_vao
                total_hours += duration.total_seconds() / 3600
        days_since_joined = 0
        if hasattr(current_user, 'ngay_tao') and current_user.ngay_tao:
            days_since_joined = (datetime.utcnow() - current_user.ngay_tao).days
        recent_sessions = db.session.query(CaThucHanh)\
                                   .join(DangKyCa)\
                                   .filter(DangKyCa.nguoi_dung_ma == current_user.id)\
                                   .order_by(CaThucHanh.ngay.desc())\
                                   .limit(5).all()
        user_stats = {
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'total_hours': round(total_hours, 1),
            'days_since_joined': days_since_joined,
            'recent_sessions': recent_sessions
        }
    except Exception as e:
        user_stats = {
            'total_sessions': 0,
            'completed_sessions': 0,
            'total_hours': 0,
            'days_since_joined': 0,
            'recent_sessions': []
        }
    recent_activities = []
    try:
        from ...models import NhatKyHoatDong
        activities = NhatKyHoatDong.query.filter_by(nguoi_dung_ma=current_user.id)\
                                        .order_by(NhatKyHoatDong.thoi_gian.desc())\
                                        .limit(10).all()
        icon_map = {
            'Đăng nhập': 'sign-in-alt',
            'Đăng xuất': 'sign-out-alt',
            'Cập nhật hồ sơ': 'user-edit',
            'Lab check-in': 'flask',
            'Lab check-out': 'check-circle',
            'Lab registration': 'calendar-plus'
        }
        for activity in activities:
            activity.icon = icon_map.get(activity.hanh_dong, 'info-circle')
            recent_activities.append(activity)
    except Exception as e:
        recent_activities = []
    return render_template('user/profile.html', 
                         form=form, 
                         has_bio_field=has_bio_field, 
                         title="Hồ sơ cá nhân",
                         user_stats=user_stats,
                         recent_activities=recent_activities)

@user_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings page"""
    form = AccountSettingsForm()
    if form.validate_on_submit():
        if not current_user.kiem_tra_mat_khau(form.current_password.data):
            flash("Mật khẩu hiện tại không chính xác", "danger")
            return redirect(url_for('user.settings'))
        current_user.dat_mat_khau(form.new_password.data)
        try:
            two_fa_setting = CaiDatHeThong.query.filter_by(
                khoa=f"user_{current_user.id}_2fa_enabled"
            ).first()
            if two_fa_setting:
                two_fa_setting.gia_tri = str(form.enable_2fa.data).lower()
            else:
                two_fa_setting = CaiDatHeThong(
                    khoa=f"user_{current_user.id}_2fa_enabled",
                    gia_tri=str(form.enable_2fa.data).lower(),
                    kieu="boolean",
                    mo_ta=f"Cài đặt 2FA cho người dùng {current_user.ten_nguoi_dung}"
                )
                db.session.add(two_fa_setting)
            db.session.commit()
            invalidate_user_cache(current_user.id)
            invalidate_user_caches()
            log_activity("Cập nhật cài đặt", "Người dùng đã cập nhật cài đặt tài khoản")
            flash("Cài đặt tài khoản đã được cập nhật thành công!", "success")
            return redirect(url_for('user.settings'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Lỗi khi cập nhật cài đặt 2FA: {str(e)}")
            flash("Đã xảy ra lỗi khi cập nhật cài đặt. Vui lòng thử lại.", "danger")
    if request.method == 'GET':
        two_fa_setting = CaiDatHeThong.query.filter_by(
            khoa=f"user_{current_user.id}_2fa_enabled"
        ).first()
        if two_fa_setting:
            form.enable_2fa.data = two_fa_setting.gia_tri.lower() == 'true'
        else:
            form.enable_2fa.data = False
    return render_template('user/settings.html', form=form, title="Cài đặt tài khoản")

