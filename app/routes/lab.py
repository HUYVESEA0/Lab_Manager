from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import login_required, current_user
from flask_wtf.csrf import generate_csrf
from datetime import datetime, timedelta, time
from ..forms import SessionRegistrationForm, LabVerificationForm, LabResultForm, LabSessionForm
from ..models import CaThucHanh, DangKyCa, VaoCa, NguoiDung, db
from ..utils import log_activity
from ..cache.cache_manager import cached_route, cached_api, invalidate_user_cache, invalidate_model_cache
from ..cache.cached_queries import (
    get_total_sessions, get_active_sessions_count, get_sessions_today,
    invalidate_session_caches, invalidate_activity_caches
)
import random, string
from sqlalchemy import func

# Đổi tên model cho đúng chuẩn hóa tiếng Việt
CaThucHanhModel = CaThucHanh
DangKyCaModel = DangKyCa
VaoCaModel = VaoCa
NguoiDungModel = NguoiDung

lab_bp = Blueprint('lab', __name__, url_prefix='/lab')

@lab_bp.route('/csrf-token')
@login_required
def csrf_token():
    """Get CSRF token for lab forms"""
    return jsonify({'csrf_token': generate_csrf()})

@lab_bp.route('/sessions')
@login_required
@cached_route(timeout=180, key_prefix='lab_sessions_page')
def lab_sessions():
    """Show available lab sessions with caching - template expects data from API"""
    return render_template("lab/lab_sessions.html")

@lab_bp.route('/register/<int:session_id>', methods=['GET', 'POST'])
@login_required
def register_lab_session(session_id):
    """Register for lab session - supports both API and form submission"""
    ca_thuc_hanh = CaThucHanh.query.get_or_404(session_id)
    
    # Check if session is available for registration
    if not ca_thuc_hanh.co_the_dang_ky():
        flash("Ca thực hành này không khả dụng cho đăng ký.", "danger")
        return redirect(url_for("lab.lab_sessions"))
    
    # Check if user is already registered
    existing_reg = DangKyCa.query.filter_by(nguoi_dung_ma=current_user.id, ca_thuc_hanh_ma=session_id).first()
    if existing_reg:
        flash("Bạn đã đăng ký ca thực hành này.", "warning")
        return redirect(url_for("lab.lab_sessions"))
    
    form = SessionRegistrationForm()
    form.session_id.data = session_id
    
    if form.validate_on_submit():        # Traditional form submission - create registration directly
        registration = DangKyCa(nguoi_dung_ma=current_user.id, ca_thuc_hanh_ma=session_id, ghi_chu=form.notes.data)
        db.session.add(registration)
        db.session.commit()
        
        # Invalidate related caches after lab registration
        invalidate_user_cache(current_user.id)
        invalidate_session_caches()
        invalidate_activity_caches()
        
        log_activity("Lab registration", f"Registered for lab session {ca_thuc_hanh.tieu_de}")
        flash("Đăng ký ca thực hành thành công!", "success")
        return redirect(url_for("lab.lab_sessions"))
    
    # For GET requests or form validation errors, render template
    # Template will handle API-based registration via JavaScript
    return render_template("lab/register_session.html", form=form, session=ca_thuc_hanh)

@lab_bp.route('/verify/<int:session_id>', methods=['GET', 'POST'])
@login_required
def verify_lab_session(session_id):
    """Verify lab session attendance - supports both API and form submission"""
    ca_thuc_hanh = CaThucHanhModel.query.get_or_404(session_id)
    dang_ky = DangKyCaModel.query.filter_by(nguoi_dung_ma=current_user.id, ca_thuc_hanh_ma=session_id).first_or_404()
    
    # Check if session is currently running
    if not ca_thuc_hanh.dang_dien_ra():
        flash("Ca thực hành này hiện không diễn ra.", "danger")
        return redirect(url_for("lab.my_lab_sessions"))
    
    # Check if user already has an entry
    vao_ca = VaoCaModel.query.filter_by(nguoi_dung_ma=current_user.id, ca_thuc_hanh_ma=session_id).first()
    if vao_ca:
        return redirect(url_for("lab.lab_session_active", entry_id=vao_ca.id))
    
    form = LabVerificationForm()
    
    if form.validate_on_submit():
        # Traditional form submission - verify code directly
        if form.verification_code.data == ca_thuc_hanh.ma_xac_thuc:
            vao_ca = VaoCaModel(nguoi_dung_ma=current_user.id, ca_thuc_hanh_ma=session_id)
            db.session.add(vao_ca)
            dang_ky.trang_thai_tham_gia = "da_tham_gia"
            db.session.commit()
            log_activity("Vào ca thực hành", f"Vào ca thực hành {ca_thuc_hanh.tieu_de}")
            flash("Xác thực thành công! Bạn đã bắt đầu ca thực hành.", "success")
            return redirect(url_for("lab.lab_session_active", entry_id=vao_ca.id))
        else:
            flash("Mã xác thực không đúng.", "danger")
    
    # For GET requests or form validation errors, render template
    # Template will handle API-based verification via JavaScript
    return render_template("lab/verify_session.html", form=form, session=ca_thuc_hanh)

@lab_bp.route('/active/<int:entry_id>', methods=['GET', 'POST'])
@login_required
def lab_session_active(entry_id):
    """Active lab session - supports both API and form submission"""
    vao_ca = VaoCaModel.query.filter_by(id=entry_id, nguoi_dung_ma=current_user.id).first_or_404()
    ca_thuc_hanh = vao_ca.ca_thuc_hanh
    
    # Check if session already ended
    if vao_ca.thoi_gian_ra:
        flash("Ca thực hành này đã kết thúc.", "info")
        return redirect(url_for("lab.my_lab_sessions"))
    
    form = LabResultForm()
    
    if form.validate_on_submit():
        # Traditional form submission - submit result directly
        vao_ca.ket_qua = form.lab_result.data
        vao_ca.thoi_gian_ra = datetime.now()
        db.session.commit()
        log_activity("Kết thúc ca thực hành", f"Hoàn thành ca thực hành {ca_thuc_hanh.tieu_de}")
        flash("Bạn đã nộp kết quả và kết thúc ca thực hành!", "success")
        return redirect(url_for("lab.my_lab_sessions"))
    
    # Calculate time information for template
    now = datetime.now()
    time_elapsed = now - vao_ca.thoi_gian_vao
    time_remaining = ca_thuc_hanh.gio_ket_thuc - now if now < ca_thuc_hanh.gio_ket_thuc else timedelta(0)
    
    # For GET requests or form validation errors, render template
    # Template will handle API-based result submission via JavaScript
    return render_template(
        "lab/active_session.html",
        entry=vao_ca,
        session=ca_thuc_hanh,
        form=form,
        time_elapsed=time_elapsed,
        time_remaining=time_remaining,
    )

@lab_bp.route('/my-sessions')
@login_required
@cached_route(timeout=120, key_prefix='user_lab_sessions')
def my_lab_sessions():
    """Show user's lab sessions with caching - template expects data from API"""
    return render_template("lab/my_sessions.html")

# --- ADMIN LAB ROUTES ---
from ..decorators import admin_required, admin_manager_required

@lab_bp.route('/admin/sessions')
@login_required
@admin_required
def admin_lab_sessions():
    """Admin lab sessions list - template expects data from API"""
    return render_template("admin/admin_lab_sessions.html")

@lab_bp.route('/admin/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_lab_session():
    """Create lab session - supports both API and form submission"""
    form = LabSessionForm()
    
    if form.validate_on_submit():
        # Traditional form submission - create session directly
        ma_xac_thuc = form.verification_code.data
        if not ma_xac_thuc:
            ma_xac_thuc = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Parse date and time
        date_obj = datetime.strptime(form.date.data, "%Y-%m-%d").date() if form.date.data else datetime.now().date()
        
        if isinstance(form.start_time.data, str):
            gio_bat_dau_obj = datetime.strptime(form.start_time.data, "%H:%M").time()
        else:
            gio_bat_dau_obj = form.start_time.data if form.start_time.data else time(9, 0)
        
        if isinstance(form.end_time.data, str):
            gio_ket_thuc_obj = datetime.strptime(form.end_time.data, "%H:%M").time()
        else:
            gio_ket_thuc_obj = form.end_time.data if form.end_time.data else time(11, 0)
        
        gio_bat_dau = datetime.combine(date_obj, gio_bat_dau_obj)
        gio_ket_thuc = datetime.combine(date_obj, gio_ket_thuc_obj)
        
        ca_thuc_hanh = CaThucHanhModel(
            tieu_de=form.title.data,
            mo_ta=form.description.data,
            ngay=date_obj,
            gio_bat_dau=gio_bat_dau,
            gio_ket_thuc=gio_ket_thuc,
            dia_diem=form.location.data,
            so_luong_toi_da=form.max_students.data,
            dang_hoat_dong=form.is_active.data,
            ma_xac_thuc=ma_xac_thuc,
            nguoi_tao_ma=current_user.id,
        )
        
        db.session.add(ca_thuc_hanh)
        db.session.commit()
        log_activity("Tạo ca thực hành", f"Đã tạo ca thực hành: {form.title.data}")
        flash(f'Ca thực hành "{form.title.data}" đã được tạo thành công! Mã xác thực: {ma_xac_thuc}', "success")
        return redirect(url_for("lab.admin_lab_sessions"))
    
    # For GET requests or form validation errors, render template
    # Template will handle API-based creation via JavaScript
    return render_template("admin/admin_create_lab_session.html", form=form)

@lab_bp.route('/admin/edit/<int:session_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_lab_session(session_id):
    """Edit lab session - supports both API and form submission"""
    ca_thuc_hanh = CaThucHanhModel.query.get_or_404(session_id)
    form = LabSessionForm()
    
    if form.validate_on_submit():
        # Traditional form submission - update session directly
        date_obj = datetime.strptime(form.date.data, "%Y-%m-%d").date() if form.date.data else datetime.now().date()
        
        if isinstance(form.start_time.data, str):
            gio_bat_dau_obj = datetime.strptime(form.start_time.data, "%H:%M").time()
        else:
            gio_bat_dau_obj = form.start_time.data if form.start_time.data else time(9, 0)
        
        if isinstance(form.end_time.data, str):
            gio_ket_thuc_obj = datetime.strptime(form.end_time.data, "%H:%M").time()
        else:
            gio_ket_thuc_obj = form.end_time.data if form.end_time.data else time(11, 0)
        
        gio_bat_dau = datetime.combine(date_obj, gio_bat_dau_obj)
        gio_ket_thuc = datetime.combine(date_obj, gio_ket_thuc_obj)
        
        ca_thuc_hanh.tieu_de = form.title.data
        ca_thuc_hanh.mo_ta = form.description.data
        ca_thuc_hanh.ngay = date_obj
        ca_thuc_hanh.gio_bat_dau = gio_bat_dau
        ca_thuc_hanh.gio_ket_thuc = gio_ket_thuc
        ca_thuc_hanh.dia_diem = form.location.data
        ca_thuc_hanh.so_luong_toi_da = form.max_students.data
        ca_thuc_hanh.dang_hoat_dong = form.is_active.data
        
        if form.verification_code.data:
            ca_thuc_hanh.ma_xac_thuc = form.verification_code.data
        
        db.session.commit()
        log_activity("Chỉnh sửa ca thực hành", f"Đã cập nhật ca thực hành: {ca_thuc_hanh.tieu_de}")
        flash(f'Ca thực hành "{ca_thuc_hanh.tieu_de}" đã được cập nhật!', "success")
        return redirect(url_for("lab.admin_lab_sessions"))
    
    # Pre-populate form with current session data
    form.title.data = ca_thuc_hanh.tieu_de
    form.description.data = ca_thuc_hanh.mo_ta
    form.date.data = ca_thuc_hanh.ngay
    form.start_time.data = ca_thuc_hanh.gio_bat_dau.time()
    form.end_time.data = ca_thuc_hanh.gio_ket_thuc.time()
    form.location.data = ca_thuc_hanh.dia_diem
    form.max_students.data = ca_thuc_hanh.so_luong_toi_da
    form.is_active.data = ca_thuc_hanh.dang_hoat_dong
    form.verification_code.data = ca_thuc_hanh.ma_xac_thuc
    
    # For GET requests or form validation errors, render template
    # Template will handle API-based editing via JavaScript
    return render_template("admin/admin_edit_lab_session.html", form=form, session=ca_thuc_hanh)

@lab_bp.route('/admin/attendees/<int:session_id>')
@login_required
@admin_required
def lab_session_attendees(session_id):
    """Admin lab session attendees - template expects data from API"""
    ca_thuc_hanh = CaThucHanhModel.query.get_or_404(session_id)
    return render_template("admin/admin_session_attendees.html", session=ca_thuc_hanh)

@lab_bp.route('/admin/schedule-sessions')
@login_required
@admin_manager_required
def schedule_lab_sessions():
    """Admin schedule lab sessions - template expects data from API"""
    return render_template("admin/admin_schedule_sessions.html")

@lab_bp.route('/admin/schedule-rooms', methods=['GET', 'POST'])
@login_required
@admin_manager_required
def schedule_lab_rooms():
    """Admin schedule lab rooms - supports both API and form submission"""
    schedule = []
    
    if request.method == "POST":
        # Traditional form submission - generate schedule directly
        ca_thuc_hanh_list = CaThucHanhModel.query.filter_by(dang_hoat_dong=True).order_by(CaThucHanhModel.ngay, CaThucHanhModel.gio_bat_dau).all()
        rooms = ["Phòng 1", "Phòng 2", "Phòng 3", "Phòng 4", "Phòng 5", "Phòng 6"]
        
        for i, ca_thuc_hanh in enumerate(ca_thuc_hanh_list):
            room = rooms[i % len(rooms)]
            schedule.append({"session": ca_thuc_hanh, "room": room})
        
        flash("Các ca thực hành đã được lên lịch phòng thành công!", "success")
    
    # For GET requests or after processing, render template
    # Template will handle API-based scheduling via JavaScript
    return render_template("admin/admin_schedule_lab_rooms.html", schedule=schedule)
