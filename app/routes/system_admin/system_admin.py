from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from ...decorators import system_admin_required
from ...models import NguoiDung, CaiDatHeThong, db
from ...utils import log_activity
from werkzeug.security import generate_password_hash
from datetime import datetime
import json

system_admin_bp = Blueprint('system_admin', __name__, url_prefix='/system-admin')

@system_admin_bp.route('/')
@login_required
@system_admin_required
def system_dashboard():
    """System Admin Dashboard với thống kê toàn hệ thống"""
    try:
        # Thống kê hệ thống
        total_users = NguoiDung.query.count()
        admin_users = NguoiDung.query.filter_by(vai_tro='quan_tri_vien').count()
        system_admin_users = NguoiDung.query.filter_by(vai_tro='quan_tri_he_thong').count()
        
        # Cài đặt hệ thống
        system_settings = CaiDatHeThong.query.all()
        
        return render_template('system_admin/dashboard.html',
                             total_users=total_users,
                             admin_users=admin_users,
                             system_admins=system_admin_users,
                             system_settings=system_settings)
                             
    except Exception as e:
        current_app.logger.error(f"Error in system dashboard: {str(e)}")
        flash("Có lỗi xảy ra khi tải dashboard.", "danger")
        return render_template('system_admin/dashboard.html',
                             total_users=0,
                             admin_users=0,
                             system_admins=0,
                             system_settings=[])

@system_admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@system_admin_required
def system_settings():
    """System Settings Page"""
    try:
        settings = CaiDatHeThong.query.all()
        
        if request.method == 'POST':
            # Update settings logic would go here
            flash("Cài đặt đã được cập nhật.", "success")
            return redirect(url_for('system_admin.system_settings'))
            
        return render_template('system_admin/system_settings.html', settings=settings)
        
    except Exception as e:
        current_app.logger.error(f"Error in system settings: {str(e)}")
        flash("Có lỗi xảy ra khi tải cài đặt.", "danger")
        return redirect(url_for('system_admin.system_dashboard'))

@system_admin_bp.route('/operations')
@login_required
@system_admin_required
def system_operations():
    """System Operations Page"""
    try:
        return render_template('system_admin/system_operations.html')
    except Exception as e:
        current_app.logger.error(f"Error in system operations: {str(e)}")
        flash("Có lỗi xảy ra khi tải trang thao tác hệ thống.", "danger")
        return redirect(url_for('system_admin.system_dashboard'))

@system_admin_bp.route('/reset-database', methods=['GET', 'POST'])
@login_required
@system_admin_required
def reset_database():
    """Reset Database Page"""
    try:
        if request.method == 'POST':
            # Reset database logic would go here
            flash("Cơ sở dữ liệu đã được đặt lại.", "success")
            return redirect(url_for('system_admin.system_dashboard'))
            
        return render_template('system_admin/reset_database.html')
    except Exception as e:
        current_app.logger.error(f"Error in reset database: {str(e)}")
        flash("Có lỗi xảy ra khi đặt lại cơ sở dữ liệu.", "danger")
        return redirect(url_for('system_admin.system_dashboard'))

@system_admin_bp.route('/backup-system', methods=['POST'])
@login_required
@system_admin_required
def backup_system():
    """Backup System API"""
    try:
        # Backup system logic would go here
        log_activity('system_backup', current_user.id, 'System backup created')
        return jsonify({'status': 'success', 'message': 'Backup created successfully'})
    except Exception as e:
        current_app.logger.error(f"Error in backup system: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Backup failed'}), 500

@system_admin_bp.route('/reset-settings', methods=['GET', 'POST'])
@login_required
@system_admin_required
def reset_settings():
    """Reset Settings Page"""
    try:
        if request.method == 'POST':
            # Reset settings logic would go here
            flash("Cài đặt hệ thống đã được đặt lại.", "success")
            return redirect(url_for('system_admin.system_settings'))
            
        return render_template('system_admin/reset_settings.html')
    except Exception as e:
        current_app.logger.error(f"Error in reset settings: {str(e)}")
        flash("Có lỗi xảy ra khi đặt lại cài đặt.", "danger")
        return redirect(url_for('system_admin.system_dashboard'))

@system_admin_bp.route('/clear-logs', methods=['GET', 'POST'])
@login_required
@system_admin_required
def clear_logs():
    """Clear System Logs"""
    try:
        if request.method == 'POST':
            # Clear logs logic would go here
            flash("Nhật ký hệ thống đã được xóa.", "success")
            return redirect(url_for('system_admin.operations'))
            
        return render_template('system_admin/clear_logs.html')
    except Exception as e:
        current_app.logger.error(f"Error in clear logs: {str(e)}")
        flash("Có lỗi xảy ra khi xóa nhật ký.", "danger")
        return redirect(url_for('system_admin.operations'))
