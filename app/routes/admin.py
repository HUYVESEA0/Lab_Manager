from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from ..decorators import admin_required, admin_manager_required
from ..forms import CreateUserForm, UserEditForm, SystemSettingsForm
from ..models import NguoiDung, CaThucHanh, NhatKyHoatDong, CaiDatHeThong, db
from ..utils import log_activity
from ..real_time_monitor import get_system_monitor
from ..cache.cache_manager import cached_route, cached_api, invalidate_user_cache, invalidate_model_cache
from ..cache.cached_queries import (
    get_dashboard_statistics, get_recent_activities, get_total_users,
    get_total_sessions, invalidate_user_caches, invalidate_session_caches,
    invalidate_activity_caches
)
import random
import psutil
import time

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Import cache from app
from flask import current_app

def get_cache():
    """Get cache instance from current app"""
    return current_app.extensions.get('cache')

@admin_bp.route('/')
@login_required
@admin_required
@cached_route(timeout=300, key_prefix='admin_dashboard')
def admin_dashboard():
    """Admin dashboard with role-based template rendering"""
    # Get dashboard statistics
    dashboard_stats = get_dashboard_statistics()
    
    # Transform the data structure to match template expectations
    stats = {
        'user_count': dashboard_stats['users']['total'],
        'lab_session_count': dashboard_stats['sessions']['total'],
        'activity_count': dashboard_stats.get('activity', {}).get('total', 0),
        'active_users': dashboard_stats['users'].get('active', 0),
        'active_lab_sessions': dashboard_stats['sessions'].get('active', 0),
        'active_sessions_today': dashboard_stats['sessions'].get('today', 0)
    }
    
    # Get recent users for the dashboard
    users = NguoiDung.query.order_by(NguoiDung.ngay_tao.desc()).limit(5).all()
    
    # Get recent activity logs
    recent_logs = NhatKyHoatDong.query.order_by(NhatKyHoatDong.thoi_gian.desc()).limit(5).all()
    
    # Get recent lab sessions
    recent_lab_sessions = CaThucHanh.query.order_by(CaThucHanh.ngay.desc()).limit(5).all()
    
    # Determine template based on user role
    if current_user.vai_tro == "quan_tri_he_thong":
        template = "admin/system_admin_dashboard.html"
    elif current_user.vai_tro == "quan_tri_vien":
        template = "admin/admin_dashboard.html"
    else:
        # Regular user should not access admin routes, but redirect to user dashboard
        flash("Bạn không có quyền truy cập khu vực này.", "warning")
        return redirect(url_for('user.dashboard'))
    
    return render_template(template, 
                         stats=stats,
                         users=users,
                         recent_logs=recent_logs,
                         recent_lab_sessions=recent_lab_sessions)

@admin_bp.route('/csrf-token')
@login_required
@admin_required
def get_csrf_token():
    """Get CSRF token for admin forms"""
    from flask_wtf.csrf import generate_csrf
    return jsonify({'csrf_token': generate_csrf()})

@admin_bp.route('/users')
@login_required
@admin_required
@cached_route(timeout=600, key_prefix='admin_users_page')
def admin_users():
    """Admin users page with caching"""
    return render_template("admin/users.html")

@admin_bp.route('/create-user', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Create user - Enhanced with API support"""
    form = CreateUserForm()
    
    # Handle API request
    if request.is_json:
        try:
            data = request.get_json()
            
            # Validate data
            if not all(key in data for key in ['ten_nguoi_dung', 'email', 'mat_khau', 'vai_tro']):
                return jsonify({'success': False, 'message': 'Missing required fields'}), 400
            
            # Check if user exists
            if NguoiDung.query.filter_by(email=data['email']).first():
                return jsonify({'success': False, 'message': 'Email đã tồn tại'}), 400
            
            if NguoiDung.query.filter_by(ten_nguoi_dung=data['ten_nguoi_dung']).first():
                return jsonify({'success': False, 'message': 'Tên người dùng đã tồn tại'}), 400
              # Create user
            nguoi_dung = NguoiDung(
                ten_nguoi_dung=data['ten_nguoi_dung'],
                email=data['email'],
                vai_tro=data['vai_tro']
            )
            nguoi_dung.dat_mat_khau(data['mat_khau'])
            db.session.add(nguoi_dung)
            db.session.commit()
            
            # Invalidate user-related caches after creating user
            invalidate_user_caches()
            
            log_activity("Tạo người dùng", f"Tạo người dùng {data['ten_nguoi_dung']} qua API")
            
            return jsonify({
                'success': True,
                'message': f"Người dùng {data['ten_nguoi_dung']} đã được tạo thành công!",
                'user': {
                    'id': nguoi_dung.id,
                    'ten_nguoi_dung': nguoi_dung.ten_nguoi_dung,
                    'email': nguoi_dung.email,
                    'vai_tro': nguoi_dung.vai_tro
                }
            })
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating user via API: {str(e)}")
            return jsonify({'success': False, 'message': 'Có lỗi xảy ra khi tạo người dùng'}), 500
    
    # Handle traditional form request
    if form.validate_on_submit():
        nguoi_dung = NguoiDung(            ten_nguoi_dung=form.ten_nguoi_dung.data,
            email=form.email.data,
            vai_tro=form.vai_tro.data
        )
        nguoi_dung.dat_mat_khau(form.mat_khau.data)
        db.session.add(nguoi_dung)
        db.session.commit()
        
        # Invalidate user-related caches after creating user
        invalidate_user_caches()
        invalidate_activity_caches()
        
        log_activity("Tạo người dùng", f"Tạo người dùng {form.ten_nguoi_dung.data}")
        flash(f"Người dùng {form.ten_nguoi_dung.data} đã được tạo thành công!", "success")
        return redirect(url_for("admin.admin_users"))
    
    return render_template("admin/admin_create_user.html", form=form)

@admin_bp.route('/edit-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user - Enhanced with API support"""
    nguoi_dung = NguoiDung.query.get_or_404(user_id)
    
    # Handle API request
    if request.is_json:
        try:
            data = request.get_json()
            
            # Validate email uniqueness
            if 'email' in data and data['email'] != nguoi_dung.email:
                if NguoiDung.query.filter_by(email=data['email']).first():
                    return jsonify({'success': False, 'message': 'Email đã tồn tại'}), 400
            
            # Validate username uniqueness
            if 'ten_nguoi_dung' in data and data['ten_nguoi_dung'] != nguoi_dung.ten_nguoi_dung:
                if NguoiDung.query.filter_by(ten_nguoi_dung=data['ten_nguoi_dung']).first():
                    return jsonify({'success': False, 'message': 'Tên người dùng đã tồn tại'}), 400
            
            # Update user data
            if 'ten_nguoi_dung' in data:
                nguoi_dung.ten_nguoi_dung = data['ten_nguoi_dung']
            if 'email' in data:
                nguoi_dung.email = data['email']
            if 'vai_tro' in data:
                nguoi_dung.vai_tro = data['vai_tro']
            
            # Update password if provided
            if data.get('new_password') and data.get('confirm_password'):
                if data['new_password'] == data['confirm_password']:
                    nguoi_dung.dat_mat_khau(data['new_password'])
                else:
                    return jsonify({'success': False, 'message': 'Mật khẩu xác nhận không khớp'}), 400
            
            db.session.commit()
            log_activity("Cập nhật người dùng", f"Cập nhật người dùng {nguoi_dung.ten_nguoi_dung} qua API")
            
            return jsonify({
                'success': True,
                'message': f"Người dùng {nguoi_dung.ten_nguoi_dung} đã được cập nhật thành công!",
                'user': {
                    'id': nguoi_dung.id,
                    'ten_nguoi_dung': nguoi_dung.ten_nguoi_dung,
                    'email': nguoi_dung.email,
                    'vai_tro': nguoi_dung.vai_tro
                }
            })
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating user via API: {str(e)}")
            return jsonify({'success': False, 'message': 'Có lỗi xảy ra khi cập nhật người dùng'}), 500
    
    # Handle traditional form request
    form = UserEditForm(original_ten_nguoi_dung=nguoi_dung.ten_nguoi_dung, original_email=nguoi_dung.email)
    if form.validate_on_submit():
        nguoi_dung.ten_nguoi_dung = form.ten_nguoi_dung.data
        nguoi_dung.email = form.email.data
        nguoi_dung.vai_tro = form.vai_tro.data
        if request.form.get("change_password"):
            new_password = request.form.get("new_password")
            confirm_password = request.form.get("confirm_password")
            if new_password and new_password == confirm_password:
                nguoi_dung.dat_mat_khau(new_password)
            elif new_password:
                flash("Xác nhận mật khẩu không khớp!", "danger")
                return render_template("admin/admin_edit_user.html", form=form, user=nguoi_dung)
        db.session.commit()
        log_activity("Cập nhật người dùng", f"Cập nhật người dùng {nguoi_dung.ten_nguoi_dung}")
        flash(f"Người dùng {nguoi_dung.ten_nguoi_dung} đã được cập nhật thành công!", "success")
        return redirect(url_for("admin.admin_users"))
    
    # Set form data from current user
    form.ten_nguoi_dung.data = nguoi_dung.ten_nguoi_dung
    form.email.data = nguoi_dung.email
    form.vai_tro.data = nguoi_dung.vai_tro
    return render_template("admin/admin_edit_user.html", form=form, user=nguoi_dung)

@admin_bp.route('/api/user-management', methods=['POST'])
@login_required 
@admin_manager_required
def api_user_management():
    """API endpoint for user management operations (promote, demote, delete)"""
    try:
        data = request.get_json()
        if not data or 'action' not in data or 'user_id' not in data:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        user_id = data['user_id']
        action = data['action']
        
        nguoi_dung = NguoiDung.query.get_or_404(user_id)
        
        if action == 'promote_to_admin':
            if nguoi_dung.vai_tro != "nguoi_dung":
                return jsonify({'success': False, 'message': 'Chỉ người dùng thường mới có thể được nâng cấp lên quản trị viên'}), 400
            nguoi_dung.vai_tro = "quan_tri_vien"
            message = f"Người dùng {nguoi_dung.ten_nguoi_dung} đã được nâng cấp lên quản trị viên!"
            log_activity("Nâng cấp quản trị viên", f"Người dùng {nguoi_dung.ten_nguoi_dung} đã được nâng cấp lên quản trị viên.")
        
        elif action == 'promote_to_system_admin':
            if nguoi_dung.vai_tro != "quan_tri_vien":
                return jsonify({'success': False, 'message': 'Chỉ quản trị viên mới có thể được nâng cấp lên quản trị hệ thống'}), 400
            nguoi_dung.vai_tro = "quan_tri_he_thong"
            message = f"Người dùng {nguoi_dung.ten_nguoi_dung} đã được nâng cấp lên quản trị hệ thống!"
            log_activity("Nâng cấp quản trị hệ thống", f"Người dùng {nguoi_dung.ten_nguoi_dung} đã được nâng cấp lên quản trị hệ thống.")
        
        elif action == 'demote':
            if nguoi_dung.vai_tro not in ["quan_tri_vien", "quan_tri_he_thong"]:
                return jsonify({'success': False, 'message': 'Chỉ quản trị viên hoặc quản trị hệ thống mới có thể bị hạ cấp'}), 400
            nguoi_dung.vai_tro = "nguoi_dung"
            message = f"Người dùng {nguoi_dung.ten_nguoi_dung} đã bị hạ cấp xuống người dùng thường!"
            log_activity("Hạ cấp quản trị viên", f"Người dùng {nguoi_dung.ten_nguoi_dung} đã bị hạ cấp xuống người dùng thường.")
        
        elif action == 'delete':
            if nguoi_dung.vai_tro == "quan_tri_he_thong":
                return jsonify({'success': False, 'message': 'Không thể xóa quản trị hệ thống'}), 400
            username = nguoi_dung.ten_nguoi_dung
            db.session.delete(nguoi_dung)
            message = f"Người dùng {username} đã bị xóa!"
            log_activity("Xóa người dùng", f"Người dùng {username} đã bị xóa.")
        
        else:
            return jsonify({'success': False, 'message': 'Action không hợp lệ'}), 400
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': message,
            'user': {
                'id': nguoi_dung.id if action != 'delete' else user_id,
                'ten_nguoi_dung': nguoi_dung.ten_nguoi_dung if action != 'delete' else None,
                'vai_tro': nguoi_dung.vai_tro if action != 'delete' else None
            } if action != 'delete' else None
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in user management API: {str(e)}")
        return jsonify({'success': False, 'message': 'Có lỗi xảy ra khi thực hiện thao tác'}), 500

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def system_settings():
    """System settings - Enhanced with API support"""
    # Initialize default settings if none exist
    if CaiDatHeThong.query.count() == 0:
        CaiDatHeThong.dat_gia_tri("app_name", "Lab Manager", "string", "Tên ứng dụng")
        CaiDatHeThong.dat_gia_tri(
            "app_description", "Một ứng dụng Flask để quản lý các phòng thực hành", "string", "Mô tả ứng dụng"
        )
        CaiDatHeThong.dat_gia_tri("enable_registration", True, "boolean", "Bật đăng ký người dùng")
        CaiDatHeThong.dat_gia_tri("enable_password_reset", True, "boolean", "Bật đặt lại mật khẩu")
        CaiDatHeThong.dat_gia_tri("items_per_page", 25, "integer", "Số mục trên mỗi trang trong danh sách")
    
    # Handle API request
    if request.is_json:
        try:
            data = request.get_json()
            
            # Update settings from API data
            for key, value in data.items():
                if key == 'app_name':
                    CaiDatHeThong.dat_gia_tri("app_name", value, "string", "Tên ứng dụng")
                elif key == 'app_description':
                    CaiDatHeThong.dat_gia_tri("app_description", value, "string", "Mô tả ứng dụng")
                elif key == 'enable_registration':
                    CaiDatHeThong.dat_gia_tri("enable_registration", bool(value), "boolean", "Bật đăng ký người dùng")
                elif key == 'enable_password_reset':
                    CaiDatHeThong.dat_gia_tri("enable_password_reset", bool(value), "boolean", "Bật đặt lại mật khẩu")
                elif key == 'items_per_page':
                    CaiDatHeThong.dat_gia_tri("items_per_page", int(value), "integer", "Số mục trên mỗi trang")
            
            db.session.commit()
            log_activity("Cập nhật cài đặt", "Cài đặt hệ thống đã được cập nhật qua API")
            
            return jsonify({
                'success': True,
                'message': 'Cài đặt hệ thống đã được cập nhật thành công!'
            })
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating settings via API: {str(e)}")
            return jsonify({'success': False, 'message': 'Có lỗi xảy ra khi cập nhật cài đặt'}), 500
    
    # Handle traditional form request
    form = SystemSettingsForm()
    if form.validate_on_submit():
        CaiDatHeThong.dat_gia_tri("app_name", form.app_name.data, "string", "Tên ứng dụng")
        CaiDatHeThong.dat_gia_tri("app_description", form.app_description.data, "string", "Mô tả ứng dụng")
        CaiDatHeThong.dat_gia_tri(
            "enable_registration", form.enable_registration.data, "boolean", "Bật đăng ký người dùng"
        )
        CaiDatHeThong.dat_gia_tri(
            "enable_password_reset", form.enable_password_reset.data, "boolean", "Bật đặt lại mật khẩu"
        )
        CaiDatHeThong.dat_gia_tri(
            "items_per_page", form.items_per_page.data, "integer", "Số mục trên mỗi trang trong danh sách"
        )
        db.session.commit()
        log_activity("Cập nhật cài đặt", "Cài đặt hệ thống đã được cập nhật")
        flash("Cài đặt hệ thống đã được cập nhật thành công!", "success")
        return redirect(url_for("admin.system_settings"))
    
    # Load current settings into form
    app_name = CaiDatHeThong.lay_gia_tri("app_name", "Lab Manager")
    form.app_name.data = str(app_name) if app_name is not None else ""
    app_desc = CaiDatHeThong.lay_gia_tri("app_description", "Một ứng dụng Flask để quản lý các dự án Python")
    form.app_description.data = str(app_desc) if app_desc is not None else ""
    enable_reg = CaiDatHeThong.lay_gia_tri("enable_registration", True)
    form.enable_registration.data = bool(enable_reg)
    enable_reset = CaiDatHeThong.lay_gia_tri("enable_password_reset", True)
    form.enable_password_reset.data = bool(enable_reset)
    items_per_page = CaiDatHeThong.lay_gia_tri("items_per_page", 25)
    form.items_per_page.data = int(items_per_page) if items_per_page is not None else 25
    
    settings = CaiDatHeThong.query.all()
    
    # Return appropriate template based on user role
    if hasattr(current_user, 'la_nguoi_quan_tri_he_thong') and current_user.la_nguoi_quan_tri_he_thong:
        return render_template("admin/system_admin_settings.html", form=form, settings=settings)
    return render_template("admin/admin_system_settings.html", form=form, settings=settings)

# Traditional routes (for backward compatibility)
@admin_bp.route('/tao-quan-tri-vien/<int:user_id>')
@login_required
@admin_manager_required
def tao_quan_tri_vien(user_id):
    nguoi_dung = NguoiDung.query.get_or_404(user_id)
    if nguoi_dung.vai_tro != "nguoi_dung":
        flash("Chỉ người dùng thường mới có thể được nâng cấp lên quản trị viên.", "danger")
        return redirect(url_for("admin.admin_users"))
    nguoi_dung.vai_tro = "quan_tri_vien"
    db.session.commit()
    log_activity("Nâng cấp quản trị viên", f"Người dùng {nguoi_dung.ten_nguoi_dung} đã được nâng cấp lên quản trị viên.")
    flash(f"Người dùng {nguoi_dung.ten_nguoi_dung} đã được nâng cấp lên quản trị viên!", "success")
    return redirect(url_for("admin.admin_users"))

@admin_bp.route('/nang-cap-quan-tri-vien-cap-cao/<int:user_id>')
@login_required
@admin_manager_required
def nang_cap_quan_tri_vien_cap_cao(user_id):
    nguoi_dung = NguoiDung.query.get_or_404(user_id)
    if nguoi_dung.vai_tro != "quan_tri_vien":
        flash("Chỉ quản trị viên mới có thể được nâng cấp lên quản trị hệ thống.", "danger")
        return redirect(url_for("admin.admin_users"))
    nguoi_dung.vai_tro = "quan_tri_he_thong"
    db.session.commit()
    log_activity(
        "Nâng cấp quản trị hệ thống", f"Người dùng {nguoi_dung.ten_nguoi_dung} đã được nâng cấp lên quản trị hệ thống."
    )
    flash(f"Người dùng {nguoi_dung.ten_nguoi_dung} đã được nâng cấp lên quản trị hệ thống!", "success")
    return redirect(url_for("admin.admin_users"))

@admin_bp.route('/xoa-quyen-admin/<int:user_id>')
@login_required
@admin_manager_required
def xoa_quyen_admin(user_id):
    nguoi_dung = NguoiDung.query.get_or_404(user_id)
    if nguoi_dung.vai_tro not in ["quan_tri_vien", "quan_tri_he_thong"]:
        flash("Chỉ quản trị viên hoặc quản trị hệ thống mới có thể bị hạ cấp.", "danger")
        return redirect(url_for("admin.admin_users"))
    nguoi_dung.vai_tro = "nguoi_dung"
    db.session.commit()
    log_activity("Hạ cấp quản trị viên", f"Người dùng {nguoi_dung.ten_nguoi_dung} đã bị hạ cấp xuống người dùng thường.")
    flash(f"Người dùng {nguoi_dung.ten_nguoi_dung} đã bị hạ cấp xuống người dùng thường!", "success")
    return redirect(url_for("admin.admin_users"))

@admin_bp.route('/xoa-nguoi-dung/<int:user_id>')
@login_required
@admin_manager_required
def xoa_nguoi_dung(user_id):
    nguoi_dung = NguoiDung.query.get_or_404(user_id)
    if nguoi_dung.vai_tro == "quan_tri_he_thong":
        flash("Không thể xóa quản trị hệ thống.", "danger")
        return redirect(url_for("admin.admin_users"))
    db.session.delete(nguoi_dung)
    db.session.commit()
    log_activity("Xóa người dùng", f"Người dùng {nguoi_dung.ten_nguoi_dung} đã bị xóa.")
    flash(f"Người dùng {nguoi_dung.ten_nguoi_dung} đã bị xóa!", "success")
    return redirect(url_for("admin.admin_users"))

# Add more traditional admin routes...
@admin_bp.route('/activity-logs')
@admin_bp.route('/activity-logs/<int:page>')
@login_required
@admin_required
@cached_route(timeout=120, key_prefix='admin_activity_logs')
def activity_logs(page=1):
    """View activity logs with pagination"""
    per_page = CaiDatHeThong.lay_gia_tri("items_per_page", 25)
    logs = NhatKyHoatDong.query.order_by(NhatKyHoatDong.thoi_gian.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return render_template("admin/admin_logs.html", logs=logs)

@admin_bp.route('/lab-sessions')
@login_required
@admin_required
@cached_route(timeout=180, key_prefix='admin_lab_sessions_page')
def admin_lab_sessions():
    """Show lab sessions management page with caching"""
    # Check if enhanced view is requested
    enhanced_view = request.args.get('enhanced', 'false').lower() == 'true'
    
    if enhanced_view:
        # Use enhanced template with modern UI and advanced features
        return render_template("admin/enhanced_lab_sessions.html")
    else:
        # Use existing template for backward compatibility
        lab_sessions = CaThucHanh.query.order_by(CaThucHanh.thoi_gian_bat_dau.desc()).all()
        return render_template("admin/admin_lab_sessions.html", lab_sessions=lab_sessions)

@admin_bp.route('/lab-sessions/enhanced')
@login_required
@admin_required
@cached_route(timeout=180, key_prefix='admin_lab_sessions_enhanced')
def enhanced_lab_sessions():
    """Show enhanced lab sessions management page"""
    return render_template("admin/enhanced_lab_sessions.html")

@admin_bp.route('/system')
@login_required
@admin_required
def system_dashboard():
    """System monitoring dashboard with real-time metrics"""
    # Get real system stats
    dashboard_stats = get_dashboard_statistics()
    
    # Transform the data structure to match template expectations
    stats = {
        'user_count': dashboard_stats['users']['total'],
        'active_users': dashboard_stats['users'].get('active', 0),
        'lab_session_count': dashboard_stats['sessions']['total'],
        'active_lab_sessions': dashboard_stats['sessions'].get('active', 0),
        'critical_alerts': 0,  # You can implement this later
        'warning_alerts': 0,   # You can implement this later
        'new_users_week': dashboard_stats['users'].get('weekly', 0),
        'daily_logins': dashboard_stats['users'].get('today', 0),
        'active_sessions_today': dashboard_stats['sessions'].get('today', 0),
        'activities_today': dashboard_stats.get('activity', {}).get('today', 0),
        'db_usage_percent': 0,  # You can implement this later
        'db_size': 'N/A'        # You can implement this later
    }
    
    return render_template(
        'admin/system_admin_dashboard.html',
        stats=stats,
        dashboard_title="System Monitor Dashboard",
        cache_version="v1.0"
    )

@admin_bp.route('/test-dashboard')
def test_dashboard():
    """Test dashboard without authentication for debugging"""
    # Fake stats for testing
    fake_stats = {
        'user_count': 156,
        'active_users': 23,
        'lab_session_count': 45,
        'active_lab_sessions': 8,
        'critical_alerts': 2,
        'warning_alerts': 3,
        'new_users_week': 12,
        'daily_logins': 45,
        'active_sessions_today': 23,
        'activities_today': 234,
        'db_usage_percent': 65,
        'db_size': '8.5 MB'
    }
    
    # Use the dedicated simple test template
    return render_template(
        'admin/test_dashboard_simple.html',
        stats=fake_stats,
        dashboard_title="Test System Dashboard (No Auth)",
        cache_version="test005"
    )

@admin_bp.route('/test-dashboard-full')
def test_dashboard_full():
    """Test full dashboard template without authentication"""
    from flask_login import AnonymousUserMixin
    
    # Mock current_user for template
    class MockUser:
        def is_authenticated(self):
            return True
        def is_admin(self):
            return True
    
    # Fake stats for testing
    fake_stats = {
        'user_count': 156,
        'active_users': 23,
        'lab_session_count': 45,
        'active_lab_sessions': 8,
        'critical_alerts': 2,
        'warning_alerts': 3,
        'new_users_week': 12,
        'daily_logins': 45,
        'active_sessions_today': 23,
        'activities_today': 234,
        'db_usage_percent': 65,
        'db_size': '8.5 MB'
    }
    
    # Render with mocked user context
    from flask import g
    g.current_user = MockUser()
    
    return render_template(
        'admin/system_admin_dashboard.html',
        stats=fake_stats,
        dashboard_title="Test Full Dashboard (Mocked Auth)",
        cache_version="test003"
    )

@admin_bp.route('/debug-api')
def debug_api():
    """Debug route to test API directly"""
    import requests
    try:
        response = requests.get('http://localhost:5000/api/v1/system/metrics-demo')
        return f"""
        <h1>API Debug</h1>
        <h2>Status: {response.status_code}</h2>
        <h3>Response:</h3>
        <pre>{response.text}</pre>
        <h3>Test in Browser:</h3>
        <script>
        console.log('Testing fetch...');
        fetch('/api/v1/system/metrics-demo')
            .then(r => r.json())
            .then(data => {{
                console.log('Success:', data);
                document.body.innerHTML += '<div style="color: green;">✅ API Working! CPU: ' + data.system.cpu_usage + '%</div>';
            }})
            .catch(error => {{
                console.error('Error:', error);
                document.body.innerHTML += '<div style="color: red;">❌ Error: ' + error.message + '</div>';
            }});
        </script>
        """
    except Exception as e:
        return f"<h1>Error: {e}</h1>"
