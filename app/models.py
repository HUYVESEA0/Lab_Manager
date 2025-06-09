# Models for Lab Manager Flask app
from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index
from werkzeug.security import check_password_hash, generate_password_hash


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

    # Flask compatibility helpers for legacy code and templates
    def is_admin(self):
        return self.vai_tro in ["quan_tri_vien", "quan_tri_he_thong"]

    def is_admin_manager(self):
        return self.vai_tro == "quan_tri_he_thong"

    def __init__(self, ten_nguoi_dung=None, email=None, vai_tro="nguoi_dung"):
        self.ten_nguoi_dung = ten_nguoi_dung
        self.email = email
        self.vai_tro = vai_tro

    def dat_mat_khau(self, mat_khau):
        self.mat_khau_hash = generate_password_hash(mat_khau)

    def kiem_tra_mat_khau(self, mat_khau):
        return check_password_hash(self.mat_khau_hash, mat_khau)

    def la_quan_tri_vien(self):
        return self.vai_tro in ["quan_tri_vien", "quan_tri_he_thong"]

    def la_quan_tri_he_thong(self):
        return self.vai_tro == "quan_tri_he_thong"

    def muc_vai_tro(self):
        muc = {"quan_tri_he_thong": 3, "quan_tri_vien": 2, "nguoi_dung": 1}
        return muc.get(self.vai_tro, 0)

    @property
    def la_nguoi_quan_tri(self):
        return self.vai_tro in ["quan_tri_vien", "quan_tri_he_thong"]

    @property
    def la_nguoi_quan_tri_he_thong(self):
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
    dang_ky = db.relationship("DangKyCa", backref="ca_thuc_hanh", lazy=True)
    vao_ca = db.relationship("VaoCa", backref="ca_thuc_hanh", lazy=True)

    def co_the_dang_ky(self):
        return self.dang_hoat_dong and self.ngay >= datetime.utcnow().date() and self.gio_bat_dau > datetime.utcnow()

    def dang_dien_ra(self):
        now = datetime.utcnow()
        return self.gio_bat_dau <= now <= self.gio_ket_thuc

    def da_day(self):
        return len(self.dang_ky) >= self.so_luong_toi_da

class DangKyCa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nguoi_dung_ma = db.Column(db.Integer, db.ForeignKey("nguoi_dung.id"), nullable=False)
    ca_thuc_hanh_ma = db.Column(db.Integer, db.ForeignKey("ca_thuc_hanh.id"), nullable=False)
    ghi_chu = db.Column(db.Text, nullable=True)
    trang_thai_tham_gia = db.Column(db.String(20), default="da_dang_ky")
    ngay_dang_ky = db.Column(db.DateTime, default=datetime.utcnow)

class VaoCa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nguoi_dung_ma = db.Column(db.Integer, db.ForeignKey("nguoi_dung.id"), nullable=False)
    ca_thuc_hanh_ma = db.Column(db.Integer, db.ForeignKey("ca_thuc_hanh.id"), nullable=False)
    thoi_gian_vao = db.Column(db.DateTime, default=datetime.utcnow)
    thoi_gian_ra = db.Column(db.DateTime, nullable=True)
    ket_qua = db.Column(db.Text, nullable=True)

def tao_chi_muc():
    Index("idx_nguoi_dung_email", NguoiDung.email)
    Index("idx_nguoi_dung_vai_tro", NguoiDung.vai_tro)
    Index("idx_nhat_ky_thoi_gian", NhatKyHoatDong.thoi_gian)
    Index("idx_ca_thuc_hanh_ngay", CaThucHanh.ngay)

def khoi_tao_ung_dung(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        tao_chi_muc()
