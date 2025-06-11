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

# CSRF token endpoint
@user_bp.route('/csrf-token')
@login_required
def get_csrf_token():
    """Get CSRF token for user forms"""
    from flask_wtf.csrf import generate_csrf
    return jsonify({'csrf_token': generate_csrf()})

# Dashboard route
@user_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard - Now uses API for data fetching"""
    session_data = {
        "visits": session.get("visits", 0),
        "last_visit": session.get("last_visit", "N/A"),
        "login_time": session.get("login_time", "N/A"),
    }
    
    # Template will fetch data via API
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
    """User profile - Enhanced with API support"""
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    # Handle API request
    if request.is_json:
        try:
            data = request.get_json()
            
            # Validate email uniqueness if changed
            if 'email' in data and data['email'] != current_user.email:
                if NguoiDung.query.filter_by(email=data['email']).first():
                    return jsonify({'success': False, 'message': 'Email đã tồn tại'}), 400
            
            # Validate username uniqueness if changed
            if 'ten_nguoi_dung' in data and data['ten_nguoi_dung'] != current_user.ten_nguoi_dung:
                if NguoiDung.query.filter_by(ten_nguoi_dung=data['ten_nguoi_dung']).first():
                    return jsonify({'success': False, 'message': 'Tên người dùng đã tồn tại'}), 400
            
            # Update user data
            if 'ten_nguoi_dung' in data:
                current_user.ten_nguoi_dung = data['ten_nguoi_dung']
            if 'email' in data:
                current_user.email = data['email']
            if 'bio' in data and hasattr(current_user, 'bio'):
                current_user.bio = data['bio']
            
            db.session.commit()
            log_activity("Cập nhật hồ sơ", "Người dùng đã cập nhật thông tin hồ sơ cá nhân qua API")
            
            return jsonify({
                'success': True,
                'message': 'Hồ sơ cá nhân đã được cập nhật thành công!',
                'user': {
                    'ten_nguoi_dung': current_user.ten_nguoi_dung,
                    'email': current_user.email,
                    'bio': getattr(current_user, 'bio', '') if hasattr(current_user, 'bio') else ''
                }
            })
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating profile via API: {str(e)}")
            return jsonify({'success': False, 'message': 'Có lỗi xảy ra khi cập nhật hồ sơ'}), 500
    
    # Handle traditional form request
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
    """User settings - Enhanced with API support"""
    
    # Handle API request
    if request.is_json:
        try:
            data = request.get_json()
            
            # Validate current password
            if 'current_password' not in data:
                return jsonify({'success': False, 'message': 'Mật khẩu hiện tại là bắt buộc'}), 400
            
            if not current_user.kiem_tra_mat_khau(data['current_password']):
                return jsonify({'success': False, 'message': 'Mật khẩu hiện tại không chính xác'}), 400
            
            # Update password if provided
            if 'new_password' in data and 'confirm_password' in data:
                if data['new_password'] != data['confirm_password']:
                    return jsonify({'success': False, 'message': 'Mật khẩu mới và xác nhận mật khẩu không khớp'}), 400
                current_user.dat_mat_khau(data['new_password'])
            
            # Update 2FA setting if provided
            if 'enable_2fa' in data:
                two_fa_setting = CaiDatHeThong.query.filter_by(
                    khoa=f"user_{current_user.id}_2fa_enabled"
                ).first()
                
                if two_fa_setting:
                    two_fa_setting.gia_tri = str(data['enable_2fa']).lower()
                else:
                    two_fa_setting = CaiDatHeThong(
                        khoa=f"user_{current_user.id}_2fa_enabled",
                        gia_tri=str(data['enable_2fa']).lower(),
                        kieu="boolean",
                        mo_ta=f"Cài đặt 2FA cho người dùng {current_user.ten_nguoi_dung}"
                    )
                    db.session.add(two_fa_setting)
            
            db.session.commit()
            log_activity("Cập nhật cài đặt", "Người dùng đã cập nhật cài đặt tài khoản qua API")
            
            return jsonify({
                'success': True,
                'message': 'Cài đặt tài khoản đã được cập nhật thành công!'
            })
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating settings via API: {str(e)}")
            return jsonify({'success': False, 'message': 'Có lỗi xảy ra khi cập nhật cài đặt'}), 500
    
    # Handle traditional form request
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
        # Import models here to avoid circular imports
        from ..models import DangKyCa, VaoCa, CaThucHanh, NhatKyHoatDong
        
        # Get user's lab session statistics
        total_sessions = DangKyCa.query.filter_by(nguoi_dung_ma=current_user.id).count()
        completed_sessions = VaoCa.query.filter_by(nguoi_dung_ma=current_user.id)\
                                       .filter(VaoCa.thoi_gian_ra.isnot(None)).count()
        
        # Get upcoming sessions
        upcoming_sessions = db.session.query(CaThucHanh)\
                                     .join(DangKyCa)\
                                     .filter(DangKyCa.nguoi_dung_ma == current_user.id)\
                                     .filter(CaThucHanh.ngay >= datetime.utcnow().date())\
                                     .order_by(CaThucHanh.ngay.asc())\
                                     .limit(5).all()
        
        # Get recent activities
        recent_activities = NhatKyHoatDong.query.filter_by(nguoi_dung_ma=current_user.id)\
                                               .order_by(NhatKyHoatDong.thoi_gian.desc())\
                                               .limit(5).all()
        
        # Calculate total lab hours
        total_hours = 0
        lab_entries = VaoCa.query.filter_by(nguoi_dung_ma=current_user.id)\
                                .filter(VaoCa.thoi_gian_ra.isnot(None)).all()
        for entry in lab_entries:
            if entry.thoi_gian_vao and entry.thoi_gian_ra:
                duration = entry.thoi_gian_ra - entry.thoi_gian_vao
                total_hours += duration.total_seconds() / 3600
        
        return jsonify({
            'user_info': {
                'name': current_user.ten_nguoi_dung,
                'email': current_user.email,
                'role': current_user.vai_tro,
                'is_active': getattr(current_user, 'dang_hoat_dong', True),
                'member_since': current_user.ngay_tao.isoformat() if hasattr(current_user, 'ngay_tao') and current_user.ngay_tao else None
            },
            'stats': {
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'total_hours': round(total_hours, 1),
                'upcoming_sessions': len(upcoming_sessions)
            },
            'upcoming_sessions': [{
                'id': session.id,
                'title': session.tieu_de,
                'date': session.ngay.isoformat() if session.ngay else None,
                'time': f"{session.gio_bat_dau} - {session.gio_ket_thuc}" if session.gio_bat_dau and session.gio_ket_thuc else None,
                'room': session.phong_thuc_hanh
            } for session in upcoming_sessions],
            'recent_activities': [{
                'action': activity.hanh_dong,
                'description': activity.chi_tiet,
                'timestamp': activity.thoi_gian.isoformat(),
                'icon': {
                    'Đăng nhập': 'sign-in-alt',
                    'Đăng xuất': 'sign-out-alt', 
                    'Cập nhật hồ sơ': 'user-edit',
                    'Lab check-in': 'flask',
                    'Lab check-out': 'check-circle',
                    'Lab registration': 'calendar-plus'
                }.get(activity.hanh_dong, 'info-circle')
            } for activity in recent_activities]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting user dashboard data: {str(e)}")
        return jsonify({'error': 'Failed to get user dashboard data'}), 500

@user_bp.route('/api/profile')
@login_required
def get_profile_api():
    """API endpoint to get current user's profile data"""
    try:
        # Import models here to avoid circular imports
        from ..models import DangKyCa, VaoCa, CaThucHanh, NhatKyHoatDong
        
        # Calculate user statistics
        total_sessions = DangKyCa.query.filter_by(nguoi_dung_ma=current_user.id).count()
        completed_sessions = VaoCa.query.filter_by(nguoi_dung_ma=current_user.id)\
                                       .filter(VaoCa.thoi_gian_ra.isnot(None)).count()
        
        # Calculate total hours spent in lab
        total_hours = 0
        lab_entries = VaoCa.query.filter_by(nguoi_dung_ma=current_user.id)\
                                .filter(VaoCa.thoi_gian_ra.isnot(None)).all()
        for entry in lab_entries:
            if entry.thoi_gian_vao and entry.thoi_gian_ra:
                duration = entry.thoi_gian_ra - entry.thoi_gian_vao
                total_hours += duration.total_seconds() / 3600
        
        # Days since joined
        days_since_joined = 0
        if hasattr(current_user, 'ngay_tao') and current_user.ngay_tao:
            days_since_joined = (datetime.utcnow() - current_user.ngay_tao).days
        
        # Recent sessions
        recent_sessions = db.session.query(CaThucHanh)\
                                   .join(DangKyCa)\
                                   .filter(DangKyCa.nguoi_dung_ma == current_user.id)\
                                   .order_by(CaThucHanh.ngay.desc())\
                                   .limit(5).all()
        
        # Recent activities
        recent_activities = NhatKyHoatDong.query.filter_by(nguoi_dung_ma=current_user.id)\
                                               .order_by(NhatKyHoatDong.thoi_gian.desc())\
                                               .limit(10).all()
        
        return jsonify({
            'user': {
                'id': current_user.id,
                'ten_nguoi_dung': current_user.ten_nguoi_dung,
                'email': current_user.email,
                'vai_tro': current_user.vai_tro,
                'bio': getattr(current_user, 'bio', '') if hasattr(current_user, 'bio') else '',
                'ngay_tao': current_user.ngay_tao.isoformat() if hasattr(current_user, 'ngay_tao') and current_user.ngay_tao else None,
                'is_active': getattr(current_user, 'is_active', True)
            },
            'stats': {
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'total_hours': round(total_hours, 1),
                'days_since_joined': days_since_joined
            },
            'recent_sessions': [{
                'id': session.id,
                'title': session.tieu_de,
                'date': session.ngay.isoformat() if session.ngay else None,
                'time': f"{session.gio_bat_dau} - {session.gio_ket_thuc}" if session.gio_bat_dau and session.gio_ket_thuc else None,
                'room': session.phong_thuc_hanh,
                'status': 'completed'  # Could be enhanced with actual status logic
            } for session in recent_sessions],
            'recent_activities': [{
                'action': activity.hanh_dong,
                'description': activity.chi_tiet,
                'timestamp': activity.thoi_gian.isoformat(),
                'icon': {
                    'Đăng nhập': 'sign-in-alt',
                    'Đăng xuất': 'sign-out-alt',
                    'Cập nhật hồ sơ': 'user-edit',
                    'Lab check-in': 'flask',
                    'Lab check-out': 'check-circle',
                    'Lab registration': 'calendar-plus'
                }.get(activity.hanh_dong, 'info-circle')
            } for activity in recent_activities]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting user profile data: {str(e)}")
        return jsonify({'error': 'Failed to get user profile data'}), 500

@user_bp.route('/api/settings')
@login_required
def get_settings_api():
    """API endpoint to get current user's settings"""
    try:
        # Get 2FA setting
        two_fa_setting = CaiDatHeThong.query.filter_by(
            khoa=f"user_{current_user.id}_2fa_enabled"
        ).first()
        
        return jsonify({
            'settings': {
                'enable_2fa': two_fa_setting.gia_tri.lower() == 'true' if two_fa_setting else False,
                'email_notifications': True,  # Could be expanded with actual settings
                'theme': 'light'  # Could be expanded with actual theme settings
            },
            'user': {
                'ten_nguoi_dung': current_user.ten_nguoi_dung,
                'email': current_user.email
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting user settings: {str(e)}")
        return jsonify({'error': 'Failed to get user settings'}), 500
