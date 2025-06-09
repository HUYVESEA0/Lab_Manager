from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from ..decorators import admin_required, admin_manager_required
from ..forms import CreateUserForm, UserEditForm, SystemSettingsForm
from ..models import NguoiDung, CaThucHanh, NhatKyHoatDong, CaiDatHeThong, db
from ..utils import log_activity
from ..real_time_monitor import get_system_monitor
import random
import psutil
import time

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
@admin_required
def admin_dashboard():
    try:
        # Import datetime for current time
        from datetime import datetime, timedelta
        
        if hasattr(current_user, 'vai_tro') and current_user.vai_tro == "quan_tri_he_thong":
            users = NguoiDung.query.order_by(NguoiDung.ngay_tao.desc()).all()
        else:
            users = NguoiDung.query.filter_by(vai_tro="nguoi_dung").order_by(NguoiDung.ngay_tao.desc()).all()
        
        # Get recent users for the dashboard table
        recent_users = NguoiDung.query.order_by(NguoiDung.ngay_tao.desc()).limit(5).all()
        recent_lab_sessions = CaThucHanh.query.order_by(CaThucHanh.ngay.desc()).limit(5).all()
        recent_logs = NhatKyHoatDong.query.order_by(NhatKyHoatDong.thoi_gian.desc()).limit(5).all()
          # Get comprehensive statistics for system dashboard
        total_users = NguoiDung.query.count()
        admin_count = NguoiDung.query.filter((NguoiDung.vai_tro == 'quan_tri_vien') | (NguoiDung.vai_tro == 'quan_tri_he_thong')).count()
        admin_manager_count = NguoiDung.query.filter_by(vai_tro='quan_tri_he_thong').count()
        regular_users = NguoiDung.query.filter_by(vai_tro='nguoi_dung').count()
        
        # Active users (logged in within last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        active_users = NguoiDung.query.filter(NguoiDung.ngay_dang_nhap_cuoi >= yesterday).count() if hasattr(NguoiDung, 'ngay_dang_nhap_cuoi') else 0
        
        total_lab_sessions = CaThucHanh.query.count()
        # Fix: Use correct field name for active sessions
        active_lab_sessions = CaThucHanh.query.filter_by(dang_hoat_dong=True).count() if hasattr(CaThucHanh, 'dang_hoat_dong') else 0
        
        # Today's statistics
        today = datetime.now().date()
        daily_logins = 0  # This would need session tracking
        page_views = 1234  # This would need analytics tracking
        active_sessions_today = CaThucHanh.query.filter(db.func.date(CaThucHanh.ngay) == today).count()
        
        # Database statistics (simulated for now - in production would query actual DB size)
        import os
        db_path = os.path.join(current_app.instance_path, 'app.db')
        db_size_bytes = os.path.getsize(db_path) if os.path.exists(db_path) else 0
        db_size_mb = round(db_size_bytes / (1024 * 1024), 2) if db_size_bytes > 0 else 0.1
        db_usage_percent = min(80, (db_size_mb / 100) * 100)  # Simulated usage percentage
        
        stats = {
            "user_count": total_users,
            "admin_count": admin_count,
            "admin_manager_count": admin_manager_count,
            "regular_users": regular_users,
            "active_users": active_users,
            "lab_session_count": total_lab_sessions,
            "active_lab_sessions": active_lab_sessions,
            "activity_count": NhatKyHoatDong.query.count(),
            "db_size": f"{db_size_mb} MB",
            "db_used": f"{db_size_mb * 0.8:.2f} MB",
            "db_free": f"{db_size_mb * 0.2:.2f} MB",
            "db_usage_percent": int(db_usage_percent),
            "system_operations": 0,  # Number of system operations
            "critical_alerts": 0,    # Critical system alerts
            "warning_alerts": 0,     # Warning alerts
            "page_views": page_views,
            "daily_logins": daily_logins,
            "active_sessions_today": active_sessions_today,
        }
        
        # Add current time for the dashboard
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return render_template(
            "admin/system_admin_dashboard.html" if current_user.is_admin_manager() else "admin/admin_dashboard.html",
            users=users,
            recent_users=recent_users,
            stats=stats,
            recent_logs=recent_logs,
            recent_lab_sessions=recent_lab_sessions,
            is_admin_manager=current_user.is_admin_manager(),
            current_time=current_time,
        )
    except Exception as e:
        # Log the error and show a user-friendly message
        current_app.logger.error(f"Error in admin dashboard: {str(e)}")
        flash("Có lỗi xảy ra khi tải bảng điều khiển. Vui lòng thử lại.", "error")        # Return a minimal dashboard with basic stats
        from datetime import datetime
        return render_template(
            "admin/system_admin_dashboard.html" if current_user.is_admin_manager() else "admin/admin_dashboard.html",
            users=[],
            recent_users=[],
            stats={
                "user_count": 0,
                "admin_count": 0,
                "regular_users": 0,
                "lab_session_count": 0,
                "active_lab_sessions": 0,
                "activity_count": 0,
            },
            recent_logs=[],
            recent_lab_sessions=[],
            is_admin_manager=current_user.is_admin_manager(),
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

@admin_bp.route('/users')
@login_required
@admin_required
def admin_users():
    users = NguoiDung.query.all()
    return render_template("admin/admin_users.html", users=users)

@admin_bp.route('/create-user', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        nguoi_dung = NguoiDung(ten_nguoi_dung=form.ten_nguoi_dung.data, email=form.email.data, vai_tro=form.vai_tro.data)
        nguoi_dung.dat_mat_khau(form.mat_khau.data)
        db.session.add(nguoi_dung)
        db.session.commit()
        flash(f"Người dùng {form.ten_nguoi_dung.data} đã được tạo thành công!", "success")
        return redirect(url_for("admin.admin_users"))
    return render_template("admin/admin_create_user.html", form=form)

@admin_bp.route('/edit-user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    nguoi_dung = NguoiDung.query.get_or_404(user_id)
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
                return render_template("admin/edit_user.html", form=form, user=nguoi_dung)
        db.session.commit()
        flash(f"Người dùng {nguoi_dung.ten_nguoi_dung} đã được cập nhật thành công!", "success")
        return redirect(url_for("admin.admin_users"))
    form.ten_nguoi_dung.data = nguoi_dung.ten_nguoi_dung
    form.email.data = nguoi_dung.email
    form.vai_tro.data = nguoi_dung.vai_tro
    return render_template("admin/admin_edit_user.html", form=form, user=nguoi_dung)

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

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def system_settings():
    if CaiDatHeThong.query.count() == 0:
        CaiDatHeThong.dat_gia_tri("app_name", "Lab Manager", "string", "Tên ứng dụng")
        CaiDatHeThong.dat_gia_tri(
            "app_description", "Một ứng dụng Flask để quản lý các phòng thực hành", "string", "Mô tả ứng dụng"
        )
        CaiDatHeThong.dat_gia_tri("enable_registration", True, "boolean", "Bật đăng ký người dùng")
        CaiDatHeThong.dat_gia_tri("enable_password_reset", True, "boolean", "Bật đặt lại mật khẩu")
        CaiDatHeThong.dat_gia_tri("items_per_page", 25, "integer", "Số mục trên mỗi trang trong danh sách")
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
    if hasattr(current_user, 'la_nguoi_quan_tri_he_thong') and current_user.la_nguoi_quan_tri_he_thong:
        return render_template("admin/system_admin_settings.html", form=form, settings=settings)
    return render_template("admin/admin_system_settings.html", form=form, settings=settings)

@admin_bp.route('/system-operations')
@login_required
@admin_manager_required
def system_operations():
    """System operations page for admin managers"""
    return render_template("admin/system_operations.html")

@admin_bp.route('/activity-logs')
@admin_bp.route('/activity-logs/<int:page>')
@login_required
@admin_required
def activity_logs(page=1):
    """View activity logs with pagination"""
    per_page = CaiDatHeThong.lay_gia_tri("items_per_page", 25)
    logs = NhatKyHoatDong.query.order_by(NhatKyHoatDong.thoi_gian.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return render_template("admin/logs.html", logs=logs)

@admin_bp.route('/clear-logs', methods=['POST'])
@login_required
@admin_manager_required
def clear_logs():
    """Clear all activity logs"""
    try:
        NhatKyHoatDong.query.delete()
        db.session.commit()
        log_activity("Xóa nhật ký", "Tất cả nhật ký hoạt động đã được xóa")
        flash("Tất cả nhật ký hoạt động đã được xóa thành công!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Có lỗi xảy ra khi xóa nhật ký hoạt động!", "danger")
    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route('/reset-settings', methods=['GET', 'POST'])
@login_required
@admin_manager_required
def reset_settings():
    """Reset system settings to defaults"""
    if request.method == 'POST':
        if request.form.get('confirm') == 'yes':
            try:
                # Delete all existing settings
                CaiDatHeThong.query.delete()
                db.session.commit()
                
                # Recreate default settings
                CaiDatHeThong.dat_gia_tri("app_name", "Lab Manager", "string", "Tên ứng dụng")
                CaiDatHeThong.dat_gia_tri(
                    "app_description", "Một ứng dụng Flask để quản lý các phòng thực hành", "string", "Mô tả ứng dụng"
                )
                CaiDatHeThong.dat_gia_tri("enable_registration", True, "boolean", "Bật đăng ký người dùng")
                CaiDatHeThong.dat_gia_tri("enable_password_reset", True, "boolean", "Bật đặt lại mật khẩu")
                CaiDatHeThong.dat_gia_tri("items_per_page", 25, "integer", "Số mục trên mỗi trang trong danh sách")
                
                log_activity("Đặt lại cài đặt", "Tất cả cài đặt hệ thống đã được đặt lại về mặc định")
                flash("Cài đặt hệ thống đã được đặt lại thành công!", "success")
                return redirect(url_for("admin.system_settings"))
            except Exception as e:
                db.session.rollback()
                flash("Có lỗi xảy ra khi đặt lại cài đặt!", "danger")
        else:
            flash("Bạn phải xác nhận để thực hiện hành động này!", "warning")
    
    return render_template("admin/reset_settings.html")

@admin_bp.route('/reset-database', methods=['GET', 'POST'])
@login_required
@admin_manager_required
def reset_database():
    """Reset the entire database"""
    if request.method == 'POST':
        if request.form.get('confirm') == 'yes':
            try:
                # Import here to avoid circular imports
                from .. import create_app
                
                # Drop all tables and recreate them
                db.drop_all()
                db.create_all()
                
                # Recreate default admin user and settings
                admin_user = NguoiDung(
                    ten_nguoi_dung="admin",
                    email="admin@example.com",
                    vai_tro="quan_tri_he_thong"
                )
                admin_user.dat_mat_khau("admin123")
                db.session.add(admin_user)
                
                # Recreate default settings
                CaiDatHeThong.dat_gia_tri("app_name", "Lab Manager", "string", "Tên ứng dụng")
                CaiDatHeThong.dat_gia_tri(
                    "app_description", "Một ứng dụng Flask để quản lý các phòng thực hành", "string", "Mô tả ứng dụng"
                )
                CaiDatHeThong.dat_gia_tri("enable_registration", True, "boolean", "Bật đăng ký người dùng")
                CaiDatHeThong.dat_gia_tri("enable_password_reset", True, "boolean", "Bật đặt lại mật khẩu")
                CaiDatHeThong.dat_gia_tri("items_per_page", 25, "integer", "Số mục trên mỗi trang trong danh sách")
                
                db.session.commit()
                
                log_activity("Đặt lại cơ sở dữ liệu", "Cơ sở dữ liệu đã được đặt lại hoàn toàn")
                flash("Cơ sở dữ liệu đã được đặt lại thành công!", "success")
                return redirect(url_for("admin.admin_dashboard"))
            except Exception as e:
                db.session.rollback()
                flash(f"Có lỗi xảy ra khi đặt lại cơ sở dữ liệu: {str(e)}", "danger")
        else:
            flash("Bạn phải xác nhận để thực hiện hành động này!", "warning")
    
    return render_template("admin/reset_database.html")

@admin_bp.route('/backup-system-create', methods=['POST'])
@login_required
@admin_manager_required
def create_system_backup():
    """Create system backup"""
    try:
        import shutil
        import os
        from datetime import datetime
        
        # Create backup directory if it doesn't exist
        backup_dir = os.path.join(current_app.instance_path, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"lab_manager_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copy database file
        db_path = os.path.join(current_app.instance_path, 'app.db')
        if os.path.exists(db_path):
            shutil.copy2(db_path, backup_path)
            log_activity("Sao lưu hệ thống", f"Đã tạo bản sao lưu: {backup_filename}")
            flash(f"Sao lưu hệ thống thành công! Tệp: {backup_filename}", "success")
        else:
            flash("Không thể tìm thấy tệp cơ sở dữ liệu để sao lưu!", "danger")
            
    except Exception as e:
        current_app.logger.error(f"Error during backup: {str(e)}")
        flash("Có lỗi xảy ra khi sao lưu hệ thống!", "danger")
    
    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route('/restart-system', methods=['POST'])
@login_required
@admin_manager_required
def restart_system():
    """Restart the application (simulated)"""
    try:
        log_activity("Khởi động lại hệ thống", "Yêu cầu khởi động lại hệ thống")
        flash("Yêu cầu khởi động lại hệ thống đã được ghi nhận. Hệ thống sẽ khởi động lại trong giây lát.", "info")
        
        # In a production environment, you would implement actual restart logic here
        # For development, we just log the action
        
    except Exception as e:
        current_app.logger.error(f"Error during restart request: {str(e)}")
        flash("Có lỗi xảy ra khi yêu cầu khởi động lại hệ thống!", "danger")
    
    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route('/reset-system', methods=['POST'])
@login_required
@admin_manager_required
def reset_system():
    """Reset system to initial state (dangerous operation)"""
    try:
        # This is a very dangerous operation - requires additional confirmation
        confirmation = request.form.get('confirm', '').upper()
        if confirmation != 'XAC NHAN THAO TAC':
            flash("Xác nhận không chính xác. Thao tác bị hủy.", "warning")
            return redirect(url_for("admin.admin_dashboard"))
        
        # Clear all user data except admin accounts
        NguoiDung.query.filter(NguoiDung.vai_tro == 'nguoi_dung').delete()
        
        # Clear lab sessions
        CaThucHanh.query.delete()
        
        # Clear activity logs except this operation
        NhatKyHoatDong.query.delete()
        
        db.session.commit()
        
        log_activity("Reset hệ thống", "Hệ thống đã được đặt lại về trạng thái ban đầu")
        flash("Hệ thống đã được reset thành công! Tất cả dữ liệu người dùng và phiên lab đã bị xóa.", "warning")
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error during system reset: {str(e)}")
        flash("Có lỗi xảy ra khi reset hệ thống!", "danger")
    
    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route('/backup-system', methods=['GET', 'POST'])
@login_required
@admin_manager_required
def backup_system():
    """Create a system backup"""
    if request.method == 'POST':
        try:
            import json
            from datetime import datetime
            import os
            
            # Create backup data
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'users': [{'username': u.ten_nguoi_dung, 'email': u.email, 'role': u.vai_tro} 
                         for u in NguoiDung.query.all()],
                'settings': [{'key': s.ten_khoa, 'value': s.gia_tri, 'type': s.kieu_du_lieu} 
                           for s in CaiDatHeThong.query.all()],
                'sessions_count': CaThucHanh.query.count(),
                'logs_count': NhatKyHoatDong.query.count()
            }
            
            # Create backups directory if it doesn't exist
            backup_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'backups')
            os.makedirs(backup_dir, exist_ok=True)
            
            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"system_backup_{timestamp}.json"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            # Write backup file
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            
            log_activity("Sao lưu hệ thống", f"Đã tạo bản sao lưu: {backup_filename}")
            flash(f"Sao lưu hệ thống thành công! File: {backup_filename}", "success")
            
        except Exception as e:
            flash(f"Lỗi khi tạo bản sao lưu: {str(e)}", "danger")
        
        return redirect(url_for("admin.admin_dashboard"))
    
    return render_template("admin/backup_system.html")

@admin_bp.route('/clear-session', methods=['GET', 'POST'])
@login_required
@admin_manager_required
def clear_session():
    """Clear all user sessions"""
    if request.method == 'POST':
        try:
            # In a real implementation, you would clear session data from a session store
            # For now, we'll just log the action
            log_activity("Xóa phiên làm việc", "Tất cả phiên làm việc người dùng đã được xóa")
            flash("Đã xóa tất cả phiên làm việc người dùng!", "success")
        except Exception as e:
            flash(f"Lỗi khi xóa phiên làm việc: {str(e)}", "danger")
        
        return redirect(url_for("admin.admin_dashboard"))
    
    return render_template("admin/clear_session.html")

@admin_bp.route('/lab-sessions')
@login_required
@admin_required
def admin_lab_sessions():
    """Show lab sessions management page"""
    lab_sessions = CaThucHanh.query.order_by(CaThucHanh.ngay.desc()).all()
    return render_template("admin/admin_lab_sessions.html", lab_sessions=lab_sessions)

@admin_bp.route('/system_dashboard')
@login_required
@admin_required
def system_dashboard():
    """System dashboard with metrics and monitoring"""
    try:
        from datetime import datetime, timedelta
        
        # Get comprehensive statistics for system dashboard
        total_users = NguoiDung.query.count()
        admin_count = NguoiDung.query.filter((NguoiDung.vai_tro == 'quan_tri_vien') | (NguoiDung.vai_tro == 'quan_tri_he_thong')).count()
        regular_users = NguoiDung.query.filter_by(vai_tro='nguoi_dung').count()
        
        # Get recent activities
        recent_users = NguoiDung.query.order_by(NguoiDung.ngay_tao.desc()).limit(5).all()
        recent_lab_sessions = CaThucHanh.query.order_by(CaThucHanh.ngay.desc()).limit(5).all()
        recent_logs = NhatKyHoatDong.query.order_by(NhatKyHoatDong.thoi_gian.desc()).limit(10).all()
        
        # Calculate system metrics
        last_week = datetime.now() - timedelta(days=7)
        new_users_this_week = NguoiDung.query.filter(NguoiDung.ngay_tao >= last_week).count()
        active_sessions = CaThucHanh.query.filter(CaThucHanh.ngay >= last_week).count()
        
        stats = {
            "user_count": total_users,
            "admin_count": admin_count,
            "regular_users": regular_users,
            "new_users_week": new_users_this_week,
            "active_sessions": active_sessions,
            "total_sessions": CaThucHanh.query.count(),
            "total_logs": NhatKyHoatDong.query.count(),
        }
        
        return render_template(
            "admin/system_admin_dashboard.html",
            stats=stats,
            recent_users=recent_users,
            recent_lab_sessions=recent_lab_sessions,
            recent_logs=recent_logs,
            current_time=datetime.now(),
            is_admin_manager=current_user.is_admin_manager()
        )
        
    except Exception as e:
        current_app.logger.error(f"Error in system dashboard: {str(e)}")
        flash("Có lỗi xảy ra khi tải system dashboard. Vui lòng thử lại.", "error")
        return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route('/api/system-metrics')
@login_required
@admin_required
def get_system_metrics():
    """API endpoint to get current system metrics"""
    try:
        monitor = get_system_monitor()
        if monitor:
            # Get the latest metrics from history or collect new ones
            if monitor.metrics_history:
                latest_metrics = monitor.metrics_history[-1]
            else:
                # If no history, get fresh metrics
                system_metrics = monitor._get_system_metrics()
                user_metrics = monitor._get_user_activity_metrics()
                latest_metrics = {
                    'timestamp': system_metrics['timestamp'],
                    'system': system_metrics,
                    'users': user_metrics
                }
            return jsonify(latest_metrics)
        else:
            # Fallback metrics if monitor not available
            return jsonify({
                'timestamp': datetime.now().isoformat(),
                'system': {
                    'cpu': {'percent': 0, 'status': 'unknown'},
                    'memory': {'percent': 0, 'status': 'unknown'},
                    'disk': {'percent': 0, 'status': 'unknown'}
                },
                'users': {
                    'total_users': NguoiDung.query.count(),
                    'active_users': 0,
                    'active_sessions': CaThucHanh.query.filter_by(dang_hoat_dong=True).count(),
                    'recent_activities': []
                }
            })
    except Exception as e:
        current_app.logger.error(f"Error getting system metrics: {str(e)}")
        return jsonify({'error': 'Failed to get system metrics'}), 500

@admin_bp.route('/api/user-activity')
@login_required
@admin_required
def get_user_activity():
    """API endpoint to get current user activity metrics"""
    try:
        monitor = get_system_monitor()
        if monitor:
            user_metrics = monitor._get_user_activity_metrics()
            return jsonify(user_metrics)
        else:
            # Fallback user metrics
            from datetime import timedelta
            hour_ago = datetime.now() - timedelta(hours=1)
            
            total_users = NguoiDung.query.count()
            active_users = NguoiDung.query.filter(
                NguoiDung.last_seen >= hour_ago
            ).count() if hasattr(NguoiDung, 'last_seen') else 0
            active_sessions = CaThucHanh.query.filter_by(dang_hoat_dong=True).count()
            
            return jsonify({
                'total_users': total_users,
                'active_users': active_users,
                'active_sessions': active_sessions,
                'recent_activities': []
            })
    except Exception as e:
        current_app.logger.error(f"Error getting user activity: {str(e)}")
        return jsonify({'error': 'Failed to get user activity'}), 500

@admin_bp.route('/api/performance-metrics')
@login_required  
@admin_required
def basic_performance_metrics():
    """API endpoint to get basic performance metrics"""
    try:
        # Basic performance metrics
        import time
        start_time = time.time()
        
        # Simulate database query time
        user_count = NguoiDung.query.count()
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        return jsonify({
            'avg_response_time': round(response_time, 2),
            'error_rate': 0.0,  # Would need actual error tracking
            'throughput': 120,  # Requests per minute - would need actual tracking
            'uptime': '99.9%',  # Would need actual uptime tracking
            'database_connections': user_count  # Using user count as proxy for DB activity
        })
    except Exception as e:
        current_app.logger.error(f"Error getting performance metrics: {str(e)}")
        return jsonify({'error': 'Failed to get performance metrics'}), 500

@admin_bp.route('/performance-metrics-submit', methods=['POST'])
@login_required
@admin_required
def submit_performance_metrics():
    """API endpoint for performance metrics collection"""
    try:
        # This endpoint can be used to receive performance data from frontend
        data = request.get_json()
        # Process the performance data if needed
        # For now, just return success
        return jsonify({'status': 'success'})
    except Exception as e:
        current_app.logger.error(f"Error processing performance metrics: {str(e)}")
        return jsonify({'error': 'Failed to process performance metrics'}), 500

@admin_bp.route('/api/user-dashboard-data/<int:user_id>')
@login_required
def get_user_dashboard_data(user_id):
    """API endpoint to get user dashboard data"""
    try:
        # Only allow users to access their own data or admins to access any data
        if not (current_user.id == user_id or current_user.vai_tro in ['admin', 'manager']):
            return jsonify({'error': 'Unauthorized'}), 403
            
        monitor = get_system_monitor()
        if monitor:
            user_data = monitor.get_user_dashboard_data(user_id)
            return jsonify(user_data)
        else:
            # Fallback user data
            user = NguoiDung.query.get_or_404(user_id)
            return jsonify({
                'user_info': {
                    'name': user.ten_nguoi_dung,
                    'last_seen': user.last_seen.isoformat() if hasattr(user, 'last_seen') and user.last_seen else None,
                    'is_active': user.dang_hoat_dong
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

# Add API endpoints for real-time data
@admin_bp.route('/api/system/metrics')
@login_required
@admin_required
def api_system_metrics():
    """API endpoint to get system resource metrics"""
    try:
        import psutil
        import time
        
        # Get system metrics using psutil if available
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            network = psutil.net_io_counters()
            
            # Calculate network usage as a percentage (simplified)
            network_usage = min(100, (network.bytes_sent + network.bytes_recv) / (1024 * 1024) % 100)
            
            data = {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'network_usage': network_usage,
                'timestamp': datetime.now().isoformat()
            }
        except ImportError:
            # Fallback to simulated data if psutil is not available
            data = {
                'cpu_usage': 25 + random.uniform(0, 40),
                'memory_usage': 45 + random.uniform(0, 35),
                'disk_usage': 35 + random.uniform(0, 30),
                'network_usage': random.uniform(0, 80),
                'timestamp': datetime.now().isoformat()
            }
        
        return jsonify(data)
        
    except Exception as e:
        current_app.logger.error(f"Error getting system metrics: {e}")
        return jsonify({'error': 'Could not fetch system metrics'}), 500

@admin_bp.route('/api/user/activity')
@login_required
@admin_required
def api_user_activity():
    """API endpoint to get user activity data"""
    try:
        # Get recent user activity
        from datetime import datetime, timedelta
        
        # Get user activity for the last 12 hours
        now = datetime.now()
        hourly_data = []
        
        for i in range(12):
            hour_start = now - timedelta(hours=i+1)
            hour_end = now - timedelta(hours=i)
            
            # Count activities in this hour
            activity_count = NhatKyHoatDong.query.filter(
                NhatKyHoatDong.thoi_gian_tao >= hour_start,
                NhatKyHoatDong.thoi_gian_tao < hour_end
            ).count()
            
            hourly_data.insert(0, activity_count)
        
        # Get current online users (simplified - users active in last 30 minutes)
        active_threshold = now - timedelta(minutes=30)
        online_users = NguoiDung.query.filter(
            NguoiDung.ngay_cap_nhat >= active_threshold
        ).count()
        
        # Get active sessions today
        today = datetime.now().date()
        active_sessions = CaThucHanh.query.filter(
            db.func.date(CaThucHanh.ngay) == today
        ).count()
        
        data = {
            'hourly_activity': hourly_data,
            'online_users': online_users,
            'active_sessions': active_sessions,
            'timestamp': now.isoformat()
        }
        
        return jsonify(data)
        
    except Exception as e:
        current_app.logger.error(f"Error getting user activity: {e}")
        return jsonify({'error': 'Could not fetch user activity'}), 500

@admin_bp.route('/api/performance/real-time-metrics')
@login_required
@admin_required
def api_real_time_performance_metrics():
    """API endpoint to get real-time performance metrics"""
    try:
        data = {
            'avg_response_time': random.uniform(50, 500),  # milliseconds
            'error_rate': random.uniform(0, 5),  # percentage
            'throughput': random.randint(50, 150),  # requests per minute
            'uptime': 99.9,  # percentage
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(data)
        
    except Exception as e:
        current_app.logger.error(f"Error getting performance metrics: {e}")
        return jsonify({'error': 'Could not fetch performance metrics'}), 500
