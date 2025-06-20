from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify, session
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from ...models import db, NguoiDung, CaiDatHeThong, CaThucHanh, DangKyCa, VaoCa, NhatKyHoatDong, ThongBao
from ...decorators import admin_required, admin_manager_required
from ...forms import CreateUserForm, UserEditForm, SystemSettingsForm
from ...utils import log_activity
from ...cache.cache_manager import invalidate_user_cache, invalidate_model_cache
from ...cache.cached_queries import (
    get_total_users, get_active_users_count, get_users_by_role, get_recent_users,
    get_total_sessions, get_active_sessions_count, get_sessions_today, get_sessions_by_status,
    get_recent_activities, get_activities_today, get_activities_by_type,
    invalidate_user_caches, invalidate_activity_caches
)
from ...services.notification_service import NotificationService, notify_system_maintenance, notify_new_feature
from sqlalchemy import func
import json

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Add notification routes
@admin_bp.route('/notifications')
@login_required
@admin_required
def admin_notifications():
    """Admin notifications management"""
    try:
        # Get all recent notifications for overview
        all_notifications = db.session.query(ThongBao).order_by(ThongBao.ngay_tao.desc()).limit(100).all()
        
        # Get notification statistics
        total_notifications = ThongBao.query.count()
        unread_notifications = ThongBao.query.filter_by(da_doc=False).count()
        
        # Get user notification counts
        user_notification_stats = db.session.query(
            NguoiDung.ten_nguoi_dung,
            func.count(ThongBao.id).label('total'),
            func.sum(func.case([(ThongBao.da_doc == False, 1)], else_=0)).label('unread')        ).join(ThongBao, NguoiDung.id == ThongBao.nguoi_nhan).group_by(NguoiDung.id).all()
        
        return render_template('admin/admin_dashboard.html',
                             notifications=all_notifications,
                             total_notifications=total_notifications,
                             unread_notifications=unread_notifications,
                             user_stats=user_notification_stats)
    except Exception as e:
        current_app.logger.error(f"Error loading admin notifications: {str(e)}")
        flash("Có lỗi xảy ra khi tải thông báo.", "danger")
        return render_template('admin/admin_dashboard.html',
                             notifications=[], total_notifications=0,
                             unread_notifications=0, user_stats=[])

@admin_bp.route('/send-notification', methods=['POST'])
@login_required
@admin_required
def send_notification():
    """Send notification to users"""
    try:
        data = request.get_json()
        
        title = data.get('title', '')
        content = data.get('content', '')
        notification_type = data.get('type', 'info')
        target = data.get('target', 'all')  # all, role, user
        target_value = data.get('target_value', '')
        link = data.get('link', '')
        
        if not title or not content:
            return jsonify({'success': False, 'message': 'Tiêu đề và nội dung không được để trống'})
        
        count = 0
        if target == 'all':
            count = NotificationService.broadcast_to_all(title, content, notification_type, link)
        elif target == 'role':
            count = NotificationService.broadcast_to_role(target_value, title, content, notification_type, link)
        elif target == 'user':
            user = NguoiDung.query.filter_by(ten_nguoi_dung=target_value).first()
            if user:
                NotificationService.create_notification(user.id, title, content, notification_type, link)
                count = 1
        
        log_activity_local("Gửi thông báo", f"Đã gửi thông báo '{title}' đến {count} người dùng")
        
        return jsonify({
            'success': True,
            'message': f'Đã gửi thông báo đến {count} người dùng'        })
        
    except Exception as e:
        current_app.logger.error(f"Error sending notification: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Có lỗi xảy ra khi gửi thông báo'
        }), 500

def log_activity_local(hoat_dong, mo_ta):
    """Local helper function for activity logging"""
    try:
        log_activity(hoat_dong, mo_ta)
    except Exception as e:
        current_app.logger.error(f"Failed to log activity: {str(e)}")

@admin_bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    """Admin dashboard với thống kê tổng quan"""
    try:
        # Thống kê cơ bản
        total_users = get_total_users()
        active_users = get_active_users_count()
        users_by_role = get_users_by_role()
        recent_users = get_recent_users()
        
        # Thống kê ca thực hành
        total_sessions = get_total_sessions()
        active_sessions = get_active_sessions_count()
        sessions_today = get_sessions_today()
        sessions_by_status = get_sessions_by_status()
        
        # Hoạt động gần đây
        recent_activities = get_recent_activities()
        activities_today = get_activities_today()
        activities_by_type = get_activities_by_type()
        
        # Tính toán thống kê bổ sung
        user_growth_rate = 0
        if total_users > 0:
            last_week_users = NguoiDung.query.filter(
                NguoiDung.ngay_tao <= datetime.now() - timedelta(days=7)
            ).count()
            if last_week_users > 0:
                user_growth_rate = ((total_users - last_week_users) / last_week_users) * 100
        
        return render_template("admin/admin_dashboard.html",
                             total_users=total_users,
                             active_users=active_users,
                             users_by_role=users_by_role,
                             recent_users=recent_users,
                             total_sessions=total_sessions,
                             active_sessions=active_sessions,
                             sessions_today=sessions_today,
                             sessions_by_status=sessions_by_status,
                             recent_activities=recent_activities,
                             activities_today=activities_today,
                             activities_by_type=activities_by_type,
                             user_growth_rate=user_growth_rate)
    except Exception as e:
        current_app.logger.error(f"Error in admin dashboard: {str(e)}")
        flash("Có lỗi xảy ra khi tải dashboard.", "danger")
        # Provide default values when there's an error
        return render_template("admin/admin_dashboard.html",
                             total_users=0,
                             active_users=0,
                             users_by_role={},
                             recent_users=[],
                             total_sessions=0,
                             active_sessions=0,
                             sessions_today=0,
                             sessions_by_status={},
                             recent_activities=[],
                             activities_today=0,
                             activities_by_type={},
                             user_growth_rate=0)

@admin_bp.route('/csrf-token')
@login_required
@admin_required
def get_csrf_token():
    """Get CSRF token for admin operations"""
    from flask_wtf.csrf import generate_csrf
    return jsonify({'csrf_token': generate_csrf()})

@admin_bp.route('/users')
@login_required
@admin_required
def admin_users():
    """Admin user management page"""
    users = NguoiDung.query.all()
    return render_template("admin/admin_users.html", users=users)

@admin_bp.route('/create-user', methods=['GET', 'POST'])
@login_required
@admin_manager_required
def create_user():
    """Create user - Enhanced with better validation"""
    form = CreateUserForm()
    
    if form.validate_on_submit():
        try:
            # Create new user với thông tin cơ bản có sẵn
            nguoi_dung_moi = NguoiDung(
                ten_nguoi_dung=form.ten_nguoi_dung.data,
                email=form.email.data,
                vai_tro=form.vai_tro.data
            )
            
            # Set password using the model's method
            if form.mat_khau.data:
                nguoi_dung_moi.dat_mat_khau(form.mat_khau.data)
            
            # Set account status if kich_hoat field exists in form
            if hasattr(form, 'kich_hoat') and form.kich_hoat.data is not None:
                nguoi_dung_moi.active = form.kich_hoat.data
            
            db.session.add(nguoi_dung_moi)
            db.session.commit()
            
            invalidate_user_cache()
            invalidate_model_cache('NguoiDung')
            
            # Log activity với thông tin chi tiết
            log_activity("Tạo người dùng", 
                        f"Tạo người dùng {form.ten_nguoi_dung.data} ({form.email.data}) với vai trò {form.vai_tro.data}")
            
            # Gửi email chào mừng nếu được yêu cầu
            if hasattr(form, 'gui_email_chao_mung') and form.gui_email_chao_mung.data:
                try:
                    # TODO: Implement send welcome email
                    current_app.logger.info(f"Welcome email should be sent to {form.email.data}")
                except Exception as email_error:
                    current_app.logger.warning(f"Failed to send welcome email: {email_error}")
            
            flash(f"Người dùng {form.ten_nguoi_dung.data} đã được tạo thành công!", "success")
            return redirect(url_for('admin.admin_users'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating user: {str(e)}")
            flash("Có lỗi xảy ra khi tạo người dùng. Vui lòng thử lại.", "danger")
    else:
        # Log validation errors for debugging
        if form.errors:
            current_app.logger.warning(f"Form validation errors: {form.errors}")
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f"Lỗi {field}: {error}", "danger")
    
    return render_template("admin/admin_create_user.html", form=form)

@admin_bp.route('/edit-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_manager_required
def edit_user(user_id):
    """Edit user - Enhanced with better validation"""
    nguoi_dung = NguoiDung.query.get_or_404(user_id)
    form = UserEditForm(nguoi_dung.ten_nguoi_dung, nguoi_dung.email, obj=nguoi_dung)
    
    if form.validate_on_submit():
        try:
            # Update user data
            nguoi_dung.ten_nguoi_dung = form.ten_nguoi_dung.data
            nguoi_dung.email = form.email.data
            nguoi_dung.vai_tro = form.vai_tro.data
            
            db.session.commit()
            
            invalidate_user_cache()
            invalidate_model_cache('NguoiDung')
            
            log_activity("Cập nhật người dùng", f"Cập nhật người dùng {nguoi_dung.ten_nguoi_dung}")
            flash(f"Người dùng {nguoi_dung.ten_nguoi_dung} đã được cập nhật thành công!", "success")
            
            return redirect(url_for('admin.admin_users'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating user: {str(e)}")
            flash("Có lỗi xảy ra khi cập nhật người dùng. Vui lòng thử lại.", "danger")
    
    # Pre-populate form
    form.ten_nguoi_dung.data = nguoi_dung.ten_nguoi_dung
    form.email.data = nguoi_dung.email
    form.vai_tro.data = nguoi_dung.vai_tro
    return render_template("admin/admin_edit_user.html", form=form, user=nguoi_dung)

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    """System settings - Enhanced with better validation"""
    form = SystemSettingsForm()
    
    if form.validate_on_submit():
        try:
            # Update all system settings
            settings_map = {
                'app_name': form.app_name.data,
                'app_description': form.app_description.data,
                'enable_registration': str(form.enable_registration.data).lower(),
                'enable_password_reset': str(form.enable_password_reset.data).lower(),
                'items_per_page': str(form.items_per_page.data)
            }
            
            for key, value in settings_map.items():
                setting = CaiDatHeThong.query.filter_by(khoa=key).first()
                if setting:
                    setting.gia_tri = value
                else:
                    setting = CaiDatHeThong(khoa=key, gia_tri=value)
                    db.session.add(setting)
            
            db.session.commit()
            invalidate_model_cache('CaiDatHeThong')
            
            log_activity("Cập nhật cài đặt", "Cài đặt hệ thống đã được cập nhật")
            flash("Cài đặt đã được cập nhật thành công!", "success")
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating settings: {str(e)}")
            flash("Có lỗi xảy ra khi cập nhật cài đặt.", "danger")
    
    # Load current settings
    settings = {s.khoa: s.gia_tri for s in CaiDatHeThong.query.all()}
    
    # Populate form with current values
    form.app_name.data = settings.get('app_name', 'Lab Manager')
    form.app_description.data = settings.get('app_description', '')
    form.enable_registration.data = settings.get('enable_registration', 'true').lower() == 'true'
    form.enable_password_reset.data = settings.get('enable_password_reset', 'true').lower() == 'true'
    form.items_per_page.data = int(settings.get('items_per_page', 25))
    
    return render_template("admin/admin_system_settings.html", form=form, settings=settings)

@admin_bp.route('/tao-quan-tri-vien/<int:user_id>')
@login_required
@admin_manager_required
def tao_quan_tri_vien(user_id):
    """Promote user to admin"""
    nguoi_dung = NguoiDung.query.get_or_404(user_id)
    
    if nguoi_dung.vai_tro != "nguoi_dung":
        flash("Chỉ người dùng thường mới có thể được nâng cấp lên quản trị viên.", "warning")
        return redirect(url_for('admin.admin_users'))
    
    nguoi_dung.vai_tro = "quan_tri_vien"
    db.session.commit()
    
    invalidate_user_cache()
    log_activity("Nâng cấp quản trị viên", f"Người dùng {nguoi_dung.ten_nguoi_dung} đã được nâng cấp lên quản trị viên.")
    flash(f"Người dùng {nguoi_dung.ten_nguoi_dung} đã được nâng cấp lên quản trị viên!", "success")
    return redirect(url_for('admin.admin_users'))

@admin_bp.route('/nang-cap-quan-tri-vien-cap-cao/<int:user_id>')
@login_required
@admin_manager_required
def nang_cap_quan_tri_vien_cap_cao(user_id):
    """Promote admin to system admin"""
    nguoi_dung = NguoiDung.query.get_or_404(user_id)
    
    if nguoi_dung.vai_tro != "quan_tri_vien":
        flash("Chỉ quản trị viên mới có thể được nâng cấp lên quản trị hệ thống.", "warning")
        return redirect(url_for('admin.admin_users'))
    
    nguoi_dung.vai_tro = "quan_tri_he_thong"
    db.session.commit()
    
    invalidate_user_cache()
    log_activity("Nâng cấp quản trị hệ thống", f"Người dùng {nguoi_dung.ten_nguoi_dung} đã được nâng cấp lên quản trị hệ thống.")
    flash(f"Người dùng {nguoi_dung.ten_nguoi_dung} đã được nâng cấp lên quản trị hệ thống!", "success")
    return redirect(url_for('admin.admin_users'))

@admin_bp.route('/xoa-quyen-admin/<int:user_id>')
@login_required
@admin_manager_required
def xoa_quyen_admin(user_id):
    """Demote admin user"""
    nguoi_dung = NguoiDung.query.get_or_404(user_id)
    
    if nguoi_dung.vai_tro not in ["quan_tri_vien", "quan_tri_he_thong"]:
        flash("Chỉ quản trị viên hoặc quản trị hệ thống mới có thể bị hạ cấp.", "warning")
        return redirect(url_for('admin.admin_users'))
    
    nguoi_dung.vai_tro = "nguoi_dung"
    db.session.commit()
    
    invalidate_user_cache()
    log_activity("Hạ cấp quản trị viên", f"Người dùng {nguoi_dung.ten_nguoi_dung} đã bị hạ cấp xuống người dùng thường.")
    flash(f"Người dùng {nguoi_dung.ten_nguoi_dung} đã bị hạ cấp xuống người dùng thường!", "success")
    return redirect(url_for('admin.admin_users'))

@admin_bp.route('/delete-user/<int:user_id>', methods=['POST'])
@login_required
@admin_manager_required
def delete_user(user_id):
    """Delete user - REST endpoint"""
    try:
        nguoi_dung = NguoiDung.query.get_or_404(user_id)
        
        # Prevent deletion of system administrators
        if nguoi_dung.vai_tro == "quan_tri_he_thong":
            return jsonify({
                'success': False,
                'message': 'Không thể xóa quản trị hệ thống.'
            }), 400
        
        # Prevent self-deletion
        if nguoi_dung.id == current_user.id:
            return jsonify({
                'success': False,
                'message': 'Không thể xóa chính mình.'
            }), 400
        
        username = nguoi_dung.ten_nguoi_dung
        
        # Check if user has any active sessions or related data
        # You might want to add more checks here based on your business logic
        
        db.session.delete(nguoi_dung)
        db.session.commit()
        
        # Invalidate caches
        invalidate_user_caches()
        
        log_activity_local("Xóa người dùng", f"Người dùng {username} đã bị xóa.")
        
        return jsonify({
            'success': True,
            'message': f'Người dùng {username} đã được xóa thành công!'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting user: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Có lỗi xảy ra khi xóa người dùng.'
        }), 500

@admin_bp.route('/xoa-nguoi-dung/<int:user_id>')
@login_required
@admin_manager_required
def xoa_nguoi_dung(user_id):
    """Delete user"""
    nguoi_dung = NguoiDung.query.get_or_404(user_id)
    
    if nguoi_dung.vai_tro == "quan_tri_he_thong":
        flash("Không thể xóa quản trị hệ thống.", "danger")
        return redirect(url_for('admin.admin_users'))
    
    username = nguoi_dung.ten_nguoi_dung
    db.session.delete(nguoi_dung)
    db.session.commit()
    
    invalidate_user_cache()
    invalidate_model_cache('NguoiDung')
    log_activity("Xóa người dùng", f"Người dùng {username} đã bị xóa.")
    flash(f"Người dùng {username} đã bị xóa!", "success")
    return redirect(url_for('admin.admin_users'))

@admin_bp.route('/activity-logs')
@admin_bp.route('/activity-logs/<int:page>')
@login_required
@admin_required
def activity_logs(page=1):
    """Admin activity logs"""
    logs = NhatKyHoatDong.query.order_by(NhatKyHoatDong.thoi_gian.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template("admin/admin_logs.html", logs=logs)

@admin_bp.route('/lab-sessions')
@login_required
@admin_required
def admin_lab_sessions():
    """Admin lab sessions management"""
    sessions = CaThucHanh.query.order_by(CaThucHanh.ngay.desc()).all()
    
    for session in sessions:
        session.so_nguoi_dang_ky = DangKyCa.query.filter_by(ca_thuc_hanh_ma=session.id).count()
        session.so_nguoi_da_vao = VaoCa.query.filter_by(ca_thuc_hanh_ma=session.id).count()
    
    # Get today's date for statistics
    today = datetime.now().date()
    
    return render_template("admin/admin_lab_sessions.html", sessions=sessions, today=today)

@admin_bp.route('/lab-sessions/enhanced')
@login_required
@admin_required
def admin_lab_sessions_enhanced():
    """Enhanced lab sessions management with more features"""
    return render_template("admin/admin_lab_sessions.html")

@admin_bp.route('/system')
@login_required
@admin_required
def admin_system():
    """Admin system monitoring and management"""
    try:
        # System statistics
        system_stats = {
            'total_users': get_total_users(),
            'active_sessions': get_active_sessions_count(),
            'total_activities': NhatKyHoatDong.query.count(),
            'recent_activities': get_recent_activities(limit=10)
        }
        
        # Database status
        db_stats = {
            'users_table': NguoiDung.query.count(),
            'sessions_table': CaThucHanh.query.count(),
            'activities_table': NhatKyHoatDong.query.count(),
            'settings_table': CaiDatHeThong.query.count()        }
        
        return render_template("admin/admin_system_settings.html", 
                             system_stats=system_stats, 
                             db_stats=db_stats)
    except Exception as e:
        current_app.logger.error(f"Error in system page: {str(e)}")
        flash("Có lỗi xảy ra khi tải thông tin hệ thống.", "danger")
        return redirect(url_for('admin.admin_dashboard'))

