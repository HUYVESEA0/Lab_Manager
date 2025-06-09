from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from ..models import db, NguoiDung, CaiDatHeThong
from ..utils import log_activity
from ..forms import ProfileForm, AccountSettingsForm
from sqlalchemy.exc import NoResultFound

user_bp = Blueprint('user', __name__)

# Route index ("/")
# Only keep one index route to avoid conflict
@user_bp.route("/")
def index():
    if current_user.is_authenticated:
        if hasattr(current_user, "is_admin_manager") and current_user.is_admin_manager():
            return redirect(url_for("admin.admin_dashboard"))
        elif hasattr(current_user, "is_admin") and current_user.is_admin():
            return redirect(url_for("admin.admin_dashboard"))
        else:
            return redirect(url_for("user.dashboard"))
    else:
        return redirect(url_for("auth.login"))

# Dashboard route
@user_bp.route('/dashboard')
@login_required
def dashboard():
    session_data = {
        "visits": session.get("visits", 0),
        "last_visit": session.get("last_visit", "N/A"),
        "login_time": session.get("login_time", "N/A"),
    }
    
    return render_template("dashboard.html", session_data=session_data)

# Session manager
@user_bp.route('/session-manager')
@login_required
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
def profile():
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    form = ProfileForm(original_ten_nguoi_dung=current_user.ten_nguoi_dung, original_email=current_user.email)
    
    # Check if the model has a bio field
    has_bio_field = hasattr(current_user, 'bio')
    
    if form.validate_on_submit():
        current_user.ten_nguoi_dung = form.ten_nguoi_dung.data
        current_user.email = form.email.data
        
        # Only update bio if the field exists
        if has_bio_field and form.bio.data is not None:
            current_user.bio = form.bio.data
            
        db.session.commit()
        log_activity("Cập nhật hồ sơ", "Người dùng đã cập nhật thông tin hồ sơ cá nhân")
        flash("Hồ sơ cá nhân đã được cập nhật thành công!", "success")
        return redirect(url_for('user.profile'))
    
    # Set form data from current_user
    if request.method == 'GET':
        form.ten_nguoi_dung.data = current_user.ten_nguoi_dung
        form.email.data = current_user.email
        if has_bio_field:
            form.bio.data = current_user.bio
    
    # Get user statistics
    user_stats = {}
    try:
        # Import models here to avoid circular imports
        from ..models import DangKyCa, VaoCa, CaThucHanh
        
        # Total registered sessions (Đăng ký ca)
        total_sessions = DangKyCa.query.filter_by(nguoi_dung_ma=current_user.id).count()
        
        # Completed sessions (with check-out time)
        completed_sessions = VaoCa.query.filter_by(nguoi_dung_ma=current_user.id)\
                                       .filter(VaoCa.thoi_gian_ra.isnot(None)).count()
        
        # Calculate total hours spent in lab
        total_hours = 0
        lab_entries = VaoCa.query.filter_by(nguoi_dung_ma=current_user.id)\
                                .filter(VaoCa.thoi_gian_ra.isnot(None)).all()
        for entry in lab_entries:
            if entry.thoi_gian_vao and entry.thoi_gian_ra:
                duration = entry.thoi_gian_ra - entry.thoi_gian_vao
                total_hours += duration.total_seconds() / 3600  # Convert to hours
        
        # Days since joined
        days_since_joined = 0
        if hasattr(current_user, 'ngay_tao') and current_user.ngay_tao:
            days_since_joined = (datetime.utcnow() - current_user.ngay_tao).days
        
        # Recent sessions (last 5)
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
        # If there's an error getting stats, provide default values
        user_stats = {
            'total_sessions': 0,
            'completed_sessions': 0,
            'total_hours': 0,
            'days_since_joined': 0,
            'recent_sessions': []
        }
    
    # Get recent activities
    recent_activities = []
    try:
        from ..models import NhatKyHoatDong
        activities = NhatKyHoatDong.query.filter_by(nguoi_dung_ma=current_user.id)\
                                        .order_by(NhatKyHoatDong.thoi_gian.desc())\
                                        .limit(10).all()
        
        for activity in activities:
            # Map activity types to icons
            icon_map = {
                'Đăng nhập': 'sign-in-alt',
                'Đăng xuất': 'sign-out-alt',
                'Cập nhật hồ sơ': 'user-edit',
                'Lab check-in': 'flask',
                'Lab check-out': 'check-circle',
                'Lab registration': 'calendar-plus'
            }
            
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
    form = AccountSettingsForm()
    
    if form.validate_on_submit():
        # Check if current password is correct
        if not current_user.kiem_tra_mat_khau(form.current_password.data):
            flash("Mật khẩu hiện tại không chính xác", "danger")
            return redirect(url_for('user.settings'))
        
        # Update password
        current_user.dat_mat_khau(form.new_password.data)
        
        # Update 2FA setting
        try:
            # Save the 2FA setting in the database
            # Check if there's an existing 2FA setting for this user
            two_fa_setting = CaiDatHeThong.query.filter_by(
                khoa=f"user_{current_user.id}_2fa_enabled"
            ).first()
            
            if two_fa_setting:
                # Update the existing setting
                two_fa_setting.gia_tri = str(form.enable_2fa.data).lower()
            else:
                # Create a new setting
                two_fa_setting = CaiDatHeThong(
                    khoa=f"user_{current_user.id}_2fa_enabled",
                    gia_tri=str(form.enable_2fa.data).lower(),
                    kieu="boolean",
                    mo_ta=f"Cài đặt 2FA cho người dùng {current_user.ten_nguoi_dung}"
                )
                db.session.add(two_fa_setting)
                
            db.session.commit()
            log_activity("Cập nhật cài đặt", "Người dùng đã cập nhật cài đặt tài khoản")
            flash("Cài đặt tài khoản đã được cập nhật thành công!", "success")
            return redirect(url_for('user.settings'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Lỗi khi cập nhật cài đặt 2FA: {str(e)}")
            flash("Đã xảy ra lỗi khi cập nhật cài đặt. Vui lòng thử lại.", "danger")
    
    # Set initial form values
    if request.method == 'GET':
        # Get 2FA setting
        two_fa_setting = CaiDatHeThong.query.filter_by(
            khoa=f"user_{current_user.id}_2fa_enabled"
        ).first()
        
        if two_fa_setting:
            form.enable_2fa.data = two_fa_setting.gia_tri.lower() == 'true'
        else:
            form.enable_2fa.data = False
            
    return render_template('user/settings.html', form=form, title="Cài đặt tài khoản")

@user_bp.route('/api/dashboard-data')
@login_required
def get_user_dashboard_data_api():
    """API endpoint to get current user's dashboard data"""
    try:
        from ..real_time_monitor import get_system_monitor
        from flask import jsonify
        
        monitor = get_system_monitor()
        if monitor:
            user_data = monitor.get_user_dashboard_data(current_user.id)
            return jsonify(user_data)
        else:
            # Fallback user data
            return jsonify({
                'user_info': {
                    'name': current_user.ten_nguoi_dung,
                    'last_seen': current_user.last_seen.isoformat() if hasattr(current_user, 'last_seen') and current_user.last_seen else None,
                    'is_active': current_user.dang_hoat_dong
                },
                'sessions': {
                    'upcoming': 0,
                    'completed': 0,
                    'sessions_list': []
                }
            })
    except Exception as e:
        current_app.logger.error(f"Error getting user dashboard data: {str(e)}")
        return jsonify({'error': 'Failed to get user dashboard data'}), 500
