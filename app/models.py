# Models for Lab Manager Flask app
from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.schema import Index
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
import time
import secrets
import time
import json


db = SQLAlchemy()

# Chuẩn hóa: Model SinhVien thay cho Student
class SinhVien(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ten = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    ngay_sinh = db.Column(db.Date, nullable=True)
    lop = db.Column(db.String(50), nullable=True)
    ngay_tao = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SinhVien {self.ten} - {self.email}>"

class NguoiDung(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ten_nguoi_dung = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mat_khau_hash = db.Column(db.String(256))
    vai_tro = db.Column(db.String(20), default="nguoi_dung")  # quan_tri_he_thong, quan_tri_vien, nguoi_dung
    ngay_tao = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    bio = db.Column(db.Text, nullable=True)  # Thêm trường bio cho giới thiệu bản thân
    
    # Password reset fields
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.Integer, nullable=True)  # Unix timestamp    # Flask compatibility helpers for legacy code and templates
    def is_admin(self):
        """Check if user is any type of admin (quan_tri_vien or quan_tri_he_thong)"""
        return self.vai_tro in ["quan_tri_vien", "quan_tri_he_thong"]

    def is_admin_manager(self):
        """Check if user is system admin (quan_tri_he_thong)"""
        return self.vai_tro == "quan_tri_he_thong"
    
    def is_system_admin(self):
        """Alias for is_admin_manager for clarity"""
        return self.vai_tro == "quan_tri_he_thong"

    def __init__(self, ten_nguoi_dung=None, email=None, vai_tro="nguoi_dung"):
        self.ten_nguoi_dung = ten_nguoi_dung
        self.email = email
        self.vai_tro = vai_tro

    def dat_mat_khau(self, mat_khau):
        self.mat_khau_hash = generate_password_hash(mat_khau)

    def kiem_tra_mat_khau(self, mat_khau):
        return check_password_hash(self.mat_khau_hash, mat_khau)

    def tao_reset_token(self):
        """Tạo token đặt lại mật khẩu"""
        from flask import current_app
        self.reset_token = secrets.token_urlsafe(32)
        # Set expiry time (default 1 hour)
        expiry_seconds = current_app.config.get('RESET_TOKEN_EXPIRATION', 3600)
        self.reset_token_expiry = int(time.time()) + expiry_seconds
        return self.reset_token
    
    def xac_thuc_reset_token(self, token):
        """Xác thực token đặt lại mật khẩu"""
        if not self.reset_token or not self.reset_token_expiry:
            return False
        if self.reset_token != token:
            return False
        if int(time.time()) > self.reset_token_expiry:
            return False
        return True
    
    def xoa_reset_token(self):
        """Xóa token đặt lại mật khẩu sau khi sử dụng"""
        self.reset_token = None
        self.reset_token_expiry = None
      # English method aliases for compatibility
    def get_reset_password_token(self):
        """Generate password reset token (English alias)"""
        return self.tao_reset_token()
        
    @staticmethod
    def verify_reset_password_token(token):
        """Find and verify user by reset token"""
        user = NguoiDung.query.filter_by(reset_token=token).first()
        if user and user.xac_thuc_reset_token(token):
            return user
        return None
        
    @staticmethod
    def tim_theo_reset_token(token):
        """Tìm người dùng theo reset token"""
        return NguoiDung.query.filter_by(reset_token=token).first()

    def la_quan_tri_vien(self):
        """Vietnamese method - check if user is any type of admin"""
        return self.vai_tro in ["quan_tri_vien", "quan_tri_he_thong"]

    def la_quan_tri_he_thong(self):
        """Vietnamese method - check if user is system admin"""
        return self.vai_tro == "quan_tri_he_thong"

    def muc_vai_tro(self):
        """Get role level for hierarchy comparison"""
        muc = {"quan_tri_he_thong": 3, "quan_tri_vien": 2, "nguoi_dung": 1}
        return muc.get(self.vai_tro, 0)

    @property
    def la_nguoi_quan_tri(self):
        """Property version - check if user is any type of admin"""
        return self.vai_tro in ["quan_tri_vien", "quan_tri_he_thong"]

    @property
    def la_nguoi_quan_tri_he_thong(self):
        """Property version - check if user is system admin"""
        return self.vai_tro == "quan_tri_he_thong"

    # Legacy compatibility properties for templates
    @property
    def username(self):
        return self.ten_nguoi_dung

    @property
    def role(self):
        role_mapping = {
            "quan_tri_he_thong": "system_admin",
            "quan_tri_vien": "admin", 
            "nguoi_dung": "user"
        }
        return role_mapping.get(self.vai_tro, "user")

    @property
    def created_at(self):
        return self.ngay_tao
        
    def __repr__(self):
        return f"<NguoiDung {self.ten_nguoi_dung}>"

class CaiDatHeThong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    khoa = db.Column(db.String(64), unique=True, nullable=False)
    gia_tri = db.Column(db.Text, nullable=True)
    kieu = db.Column(db.String(16), default="string")
    mo_ta = db.Column(db.String(256))
    ngay_tao = db.Column(db.DateTime, default=datetime.utcnow)
    ngay_cap_nhat = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CaiDatHeThong {self.khoa}={self.gia_tri}>"

    @staticmethod
    def lay_gia_tri(khoa, mac_dinh=None):
        setting = CaiDatHeThong.query.filter_by(khoa=khoa).first()
        if setting is None:
            return mac_dinh
        if setting.kieu == "boolean":
            return setting.gia_tri.lower() in ("true", "1", "yes")
        elif setting.kieu == "integer":
            return int(setting.gia_tri) if setting.gia_tri else 0
        elif setting.kieu == "float":
            return float(setting.gia_tri) if setting.gia_tri else 0.0
        return setting.gia_tri

    @staticmethod
    def dat_gia_tri(khoa, gia_tri, kieu="string", mo_ta=""):
        setting = CaiDatHeThong.query.filter_by(khoa=khoa).first()
        if setting is None:
            setting = CaiDatHeThong(khoa=khoa, mo_ta=mo_ta, kieu=kieu)
            db.session.add(setting)
        setting.gia_tri = str(gia_tri) if gia_tri is not None else ""
        setting.kieu = kieu
        if mo_ta:
            setting.mo_ta = mo_ta
        db.session.commit()
        return setting

class NhatKyHoatDong(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nguoi_dung_ma = db.Column(db.Integer, db.ForeignKey("nguoi_dung.id"), nullable=True)
    nguoi_dung = db.relationship("NguoiDung", backref="nhat_ky")
    hanh_dong = db.Column(db.String(128), nullable=False)
    chi_tiet = db.Column(db.Text, nullable=True)
    dia_chi_ip = db.Column(db.String(45), nullable=True)
    thoi_gian = db.Column(db.DateTime, default=datetime.utcnow)

    # Aliases for English compatibility
    @property
    def timestamp(self):
        return self.thoi_gian
    
    @property
    def action(self):
        return self.hanh_dong
    
    @property
    def details(self):
        return self.chi_tiet
    
    @property
    def user_id(self):
        return self.nguoi_dung_ma
    
    @property
    def ip_address(self):
        return self.dia_chi_ip

    def __repr__(self):
        return f"<NhatKyHoatDong {self.hanh_dong} by {self.nguoi_dung.ten_nguoi_dung if self.nguoi_dung else 'Unknown'} at {self.thoi_gian}>"

class KhoaHoc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tieu_de = db.Column(db.String(100), nullable=False)
    mo_ta = db.Column(db.Text, nullable=False)
    ngay_tao = db.Column(db.DateTime, default=datetime.utcnow)
    bai_hoc = db.relationship("BaiHoc", backref="khoa_hoc", lazy=True)
    ghi_danh = db.relationship("GhiDanh", backref="khoa_hoc", lazy=True)

class BaiHoc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tieu_de = db.Column(db.String(100), nullable=False)
    noi_dung = db.Column(db.Text, nullable=False)
    khoa_hoc_ma = db.Column(db.Integer, db.ForeignKey("khoa_hoc.id"), nullable=False)

class GhiDanh(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nguoi_dung_ma = db.Column(db.Integer, db.ForeignKey("nguoi_dung.id"), nullable=False)
    khoa_hoc_ma = db.Column(db.Integer, db.ForeignKey("khoa_hoc.id"), nullable=False)
    ngay_ghi_danh = db.Column(db.DateTime, default=datetime.utcnow)

class CaThucHanh(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tieu_de = db.Column(db.String(100), nullable=False)
    mo_ta = db.Column(db.Text, nullable=False)
    ngay = db.Column(db.Date, nullable=False)
    gio_bat_dau = db.Column(db.DateTime, nullable=False)
    gio_ket_thuc = db.Column(db.DateTime, nullable=False)
    dia_diem = db.Column(db.String(100), nullable=False)
    so_luong_toi_da = db.Column(db.Integer, nullable=False)
    dang_hoat_dong = db.Column(db.Boolean, default=True)
    ma_xac_thuc = db.Column(db.String(10), nullable=False)
    nguoi_tao_ma = db.Column(db.Integer, db.ForeignKey("nguoi_dung.id"), nullable=False)
    ngay_tao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Enhanced fields
    tags = db.Column(db.Text, nullable=True)  # JSON array of tags
    anh_bia = db.Column(db.String(255), nullable=True)  # Cover image
    muc_do_kho = db.Column(db.String(20), default="trung_binh")  # easy, medium, hard
    yeu_cau_thiet_bi = db.Column(db.Text, nullable=True)  # JSON array of required equipment
    ghi_chu_noi_bo = db.Column(db.Text, nullable=True)  # Internal notes for admins
    cho_phep_dang_ky_tre = db.Column(db.Boolean, default=False)  # Allow late registration
    tu_dong_xac_nhan = db.Column(db.Boolean, default=True)  # Auto-approve registrations
    thong_bao_truoc = db.Column(db.Integer, default=60)  # Notification minutes before start
    trang_thai = db.Column(db.String(20), default="scheduled")  # scheduled, ongoing, completed, cancelled
    diem_so_toi_da = db.Column(db.Integer, default=100)  # Maximum score
    thoi_gian_lam_bai = db.Column(db.Integer, nullable=True)  # Time limit in minutes
    
    # Relationships
    dang_ky = db.relationship("DangKyCa", backref="ca_thuc_hanh", lazy=True, cascade="all, delete-orphan")
    vao_ca = db.relationship("VaoCa", backref="ca_thuc_hanh", lazy=True, cascade="all, delete-orphan")
    tai_lieu = db.relationship("TaiLieuCa", backref="ca_thuc_hanh", lazy=True, cascade="all, delete-orphan")
    danh_gia = db.relationship("DanhGiaCa", backref="ca_thuc_hanh", lazy=True, cascade="all, delete-orphan")

    def co_the_dang_ky(self):
        if not self.dang_hoat_dong:
            return False
        if self.trang_thai != "scheduled":
            return False
        now = datetime.utcnow()
        if self.cho_phep_dang_ky_tre:
            return self.gio_ket_thuc > now
        return self.gio_bat_dau > now

    def dang_dien_ra(self):
        now = datetime.utcnow()
        return (self.gio_bat_dau <= now <= self.gio_ket_thuc and 
                self.trang_thai == "ongoing")

    def da_day(self):
        return len(self.dang_ky) >= self.so_luong_toi_da

    def get_tags(self):
        """Get tags as list"""
        if self.tags:
            try:
                return json.loads(self.tags)
            except:
                return []
        return []

    def set_tags(self, tag_list):
        """Set tags from list"""
        self.tags = json.dumps(tag_list) if tag_list else None

    def get_equipment(self):
        """Get required equipment as list"""
        if self.yeu_cau_thiet_bi:
            try:
                return json.loads(self.yeu_cau_thiet_bi)
            except:
                return []
        return []

    def set_equipment(self, equipment_list):
        """Set required equipment from list"""
        self.yeu_cau_thiet_bi = json.dumps(equipment_list) if equipment_list else None

    def get_completion_rate(self):
        """Calculate completion rate"""
        total_registered = len(self.dang_ky)
        if total_registered == 0:
            return 0
        completed = len([entry for entry in self.vao_ca if entry.thoi_gian_ra])
        return (completed / total_registered) * 100

    def get_average_score(self):
        """Calculate average score"""
        scores = [entry.diem_so for entry in self.vao_ca if entry.diem_so is not None]
        return sum(scores) / len(scores) if scores else 0

# New models for enhanced features

class MauCaThucHanh(db.Model):
    """Lab session templates"""
    __tablename__ = 'mau_ca_thuc_hanh'
    
    id = db.Column(db.Integer, primary_key=True)
    ten_mau = db.Column(db.String(100), nullable=False)
    mo_ta = db.Column(db.Text, nullable=True)
    tieu_de_mac_dinh = db.Column(db.String(100), nullable=False)
    mo_ta_mac_dinh = db.Column(db.Text, nullable=False)
    thoi_gian_thuc_hien = db.Column(db.Integer, default=120)  # Duration in minutes
    so_luong_toi_da_mac_dinh = db.Column(db.Integer, default=20)
    tags_mac_dinh = db.Column(db.Text, nullable=True)
    yeu_cau_thiet_bi_mac_dinh = db.Column(db.Text, nullable=True)
    muc_do_kho = db.Column(db.String(20), default="trung_binh")
    diem_so_toi_da = db.Column(db.Integer, default=100)
    nguoi_tao_ma = db.Column(db.Integer, db.ForeignKey("nguoi_dung.id"), nullable=False)
    ngay_tao = db.Column(db.DateTime, default=datetime.utcnow)
    kich_hoat = db.Column(db.Boolean, default=True)

class TaiLieuCa(db.Model):
    """Session materials/files"""
    __tablename__ = 'tai_lieu_ca'
    
    id = db.Column(db.Integer, primary_key=True)
    ca_thuc_hanh_ma = db.Column(db.Integer, db.ForeignKey("ca_thuc_hanh.id"), nullable=False)
    ten_tep = db.Column(db.String(255), nullable=False)
    duong_dan_tep = db.Column(db.String(500), nullable=False)
    kich_thuoc_tep = db.Column(db.Integer, nullable=True)
    loai_tep = db.Column(db.String(50), nullable=True)
    mo_ta = db.Column(db.Text, nullable=True)
    nguoi_tai_len = db.Column(db.Integer, db.ForeignKey("nguoi_dung.id"), nullable=False)
    ngay_tai_len = db.Column(db.DateTime, default=datetime.utcnow)
    kich_hoat = db.Column(db.Boolean, default=True)

class ThietBi(db.Model):
    """Equipment/Resource management"""
    __tablename__ = 'thiet_bi'
    
    id = db.Column(db.Integer, primary_key=True)
    ten_thiet_bi = db.Column(db.String(100), nullable=False)
    mo_ta = db.Column(db.Text, nullable=True)
    so_luong_co_san = db.Column(db.Integer, default=1)
    trang_thai = db.Column(db.String(20), default="available")  # available, in_use, maintenance
    vi_tri = db.Column(db.String(100), nullable=True)
    ghi_chu = db.Column(db.Text, nullable=True)
    ngay_tao = db.Column(db.DateTime, default=datetime.utcnow)

class DatThietBi(db.Model):
    """Equipment booking for sessions"""
    __tablename__ = 'dat_thiet_bi'
    
    id = db.Column(db.Integer, primary_key=True)
    ca_thuc_hanh_ma = db.Column(db.Integer, db.ForeignKey("ca_thuc_hanh.id"), nullable=False)
    thiet_bi_ma = db.Column(db.Integer, db.ForeignKey("thiet_bi.id"), nullable=False)
    so_luong_dat = db.Column(db.Integer, default=1)
    nguoi_dat = db.Column(db.Integer, db.ForeignKey("nguoi_dung.id"), nullable=False)
    ngay_dat = db.Column(db.DateTime, default=datetime.utcnow)
    trang_thai = db.Column(db.String(20), default="pending")  # pending, confirmed, cancelled
    
    # Relationships
    thiet_bi = db.relationship("ThietBi", backref="dat_thiet_bi")
    ca_thuc_hanh = db.relationship("CaThucHanh", backref="dat_thiet_bi")

class DanhGiaCa(db.Model):
    """Session feedback and ratings"""
    __tablename__ = 'danh_gia_ca'
    
    id = db.Column(db.Integer, primary_key=True)
    ca_thuc_hanh_ma = db.Column(db.Integer, db.ForeignKey("ca_thuc_hanh.id"), nullable=False)
    nguoi_danh_gia = db.Column(db.Integer, db.ForeignKey("nguoi_dung.id"), nullable=False)
    diem_danh_gia = db.Column(db.Integer, nullable=False)  # 1-5 stars
    nhan_xet = db.Column(db.Text, nullable=True)
    ngay_danh_gia = db.Column(db.DateTime, default=datetime.utcnow)

class ThongBao(db.Model):
    """Notification system"""
    __tablename__ = 'thong_bao'
    
    id = db.Column(db.Integer, primary_key=True)
    nguoi_nhan = db.Column(db.Integer, db.ForeignKey("nguoi_dung.id"), nullable=False)
    tieu_de = db.Column(db.String(200), nullable=False)
    noi_dung = db.Column(db.Text, nullable=False)
    loai = db.Column(db.String(50), default="info")  # info, warning, success, error
    lien_ket = db.Column(db.String(500), nullable=True)
    da_doc = db.Column(db.Boolean, default=False)
    ngay_tao = db.Column(db.DateTime, default=datetime.utcnow)
    ngay_doc = db.Column(db.DateTime, nullable=True)

# Enhanced existing models
class DangKyCa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nguoi_dung_ma = db.Column(db.Integer, db.ForeignKey("nguoi_dung.id"), nullable=False)
    ca_thuc_hanh_ma = db.Column(db.Integer, db.ForeignKey("ca_thuc_hanh.id"), nullable=False)
    ghi_chu = db.Column(db.Text, nullable=True)
    trang_thai_tham_gia = db.Column(db.String(20), default="da_dang_ky")
    ngay_dang_ky = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Enhanced fields
    uu_tien = db.Column(db.Integer, default=0)  # Priority level
    da_xac_nhan = db.Column(db.Boolean, default=True)  # Registration confirmed
    ngay_xac_nhan = db.Column(db.DateTime, nullable=True)

class VaoCa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nguoi_dung_ma = db.Column(db.Integer, db.ForeignKey("nguoi_dung.id"), nullable=False)
    ca_thuc_hanh_ma = db.Column(db.Integer, db.ForeignKey("ca_thuc_hanh.id"), nullable=False)
    thoi_gian_vao = db.Column(db.DateTime, default=datetime.utcnow)
    thoi_gian_ra = db.Column(db.DateTime, nullable=True)
    ket_qua = db.Column(db.Text, nullable=True)
    
    # Enhanced fields
    diem_so = db.Column(db.Integer, nullable=True)  # Score/Grade
    nhan_xet_gv = db.Column(db.Text, nullable=True)  # Teacher comments
    tep_nop_bai = db.Column(db.String(500), nullable=True)  # Submitted files
    trang_thai_nop = db.Column(db.String(20), default="chua_nop")  # not_submitted, submitted, graded
    thoi_gian_nop = db.Column(db.DateTime, nullable=True)
    vi_tri_ngoi = db.Column(db.String(20), nullable=True)  # Seat assignment

def tao_chi_muc():
    Index("idx_nguoi_dung_email", NguoiDung.email)
    Index("idx_nguoi_dung_ten_nguoi_dung", NguoiDung.ten_nguoi_dung)

def khoi_tao_ung_dung(app):
    """Initialize database with the app"""
    db.init_app(app)
    tao_chi_muc()