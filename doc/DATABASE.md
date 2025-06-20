# Database Documentation - Lab Manager System

## Tổng quan Cơ sở dữ liệu

Hệ thống Lab Manager sử dụng SQLAlchemy ORM với SQLite làm cơ sở dữ liệu mặc định. Thiết kế database có thể dễ dàng chuyển đổi sang PostgreSQL, MySQL hoặc các RDBMS khác.

## Cấu hình Database

### Database URL
```python
# Development (SQLite)
SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"

# Production (PostgreSQL example)
SQLALCHEMY_DATABASE_URI = "postgresql://user:password@localhost/labmanager"
```

### Migration Support
- Sử dụng Flask-Migrate (Alembic)
- Migrations được lưu trong thư mục `migrations/versions/`

## Sơ đồ ERD (Entity Relationship Diagram)

```mermaid
erDiagram
    NguoiDung ||--o{ NhatKyHoatDong : creates
    NguoiDung ||--o{ GhiDanh : enrolls
    NguoiDung ||--o{ DangKyCa : registers
    NguoiDung ||--o{ VaoCa : attends
    NguoiDung ||--o{ CaThucHanh : creates
    NguoiDung ||--o{ DanhGiaCa : reviews
    NguoiDung ||--o{ ThongBao : receives
    NguoiDung ||--o{ TaiLieuCa : uploads
    NguoiDung ||--o{ DatThietBi : books
    NguoiDung ||--o{ MauCaThucHanh : creates
    
    KhoaHoc ||--o{ BaiHoc : contains
    KhoaHoc ||--o{ GhiDanh : has
    
    CaThucHanh ||--o{ DangKyCa : has
    CaThucHanh ||--o{ VaoCa : has
    CaThucHanh ||--o{ TaiLieuCa : has
    CaThucHanh ||--o{ DanhGiaCa : has
    CaThucHanh ||--o{ DatThietBi : uses
    
    ThietBi ||--o{ DatThietBi : booked_for
    
    NguoiDung {
        int id PK
        string ten_nguoi_dung
        string email
        string mat_khau_hash
        string vai_tro
        datetime ngay_tao
        datetime last_seen
        text bio
        boolean is_verified
        string verification_token
        int verification_token_expiry
        boolean active
        int failed_login_attempts
        datetime last_failed_login
        datetime account_locked_until
        string reset_token
        int reset_token_expiry
    }
    
    CaThucHanh {
        int id PK
        string tieu_de
        text mo_ta
        date ngay
        datetime gio_bat_dau
        datetime gio_ket_thuc
        string dia_diem
        int so_luong_toi_da
        boolean dang_hoat_dong
        string ma_xac_thuc
        int nguoi_tao_ma FK
        datetime ngay_tao
        text tags
        string anh_bia
        string muc_do_kho
        text yeu_cau_thiet_bi
        text ghi_chu_noi_bo
        boolean cho_phep_dang_ky_tre
        boolean tu_dong_xac_nhan
        int thong_bao_truoc
        string trang_thai
        int diem_so_toi_da
        int thoi_gian_lam_bai
    }
    
    DangKyCa {
        int id PK
        int nguoi_dung_ma FK
        int ca_thuc_hanh_ma FK
        text ghi_chu
        string trang_thai_tham_gia
        datetime ngay_dang_ky
        int uu_tien
        boolean da_xac_nhan
        datetime ngay_xac_nhan
    }
    
    VaoCa {
        int id PK
        int nguoi_dung_ma FK
        int ca_thuc_hanh_ma FK
        datetime thoi_gian_vao
        datetime thoi_gian_ra
        text ket_qua
        int diem_so
        text nhan_xet_gv
        string tep_nop_bai
        string trang_thai_nop
        datetime thoi_gian_nop
        string vi_tri_ngoi
    }
    
    NhatKyHoatDong {
        int id PK
        int nguoi_dung_ma FK
        string hanh_dong
        text chi_tiet
        string dia_chi_ip
        datetime thoi_gian
    }
    
    CaiDatHeThong {
        int id PK
        string khoa
        text gia_tri
        string kieu
        string mo_ta
        datetime ngay_tao
        datetime ngay_cap_nhat
    }
    
    KhoaHoc {
        int id PK
        string tieu_de
        text mo_ta
        datetime ngay_tao
    }
    
    BaiHoc {
        int id PK
        string tieu_de
        text noi_dung
        int khoa_hoc_ma FK
    }
    
    GhiDanh {
        int id PK
        int nguoi_dung_ma FK
        int khoa_hoc_ma FK
        datetime ngay_ghi_danh
    }
    
    ThietBi {
        int id PK
        string ten_thiet_bi
        text mo_ta
        int so_luong_co_san
        string trang_thai
        string vi_tri
        text ghi_chu
        datetime ngay_tao
    }
    
    DatThietBi {
        int id PK
        int ca_thuc_hanh_ma FK
        int thiet_bi_ma FK
        int so_luong_dat
        int nguoi_dat FK
        datetime ngay_dat
        string trang_thai
    }
    
    TaiLieuCa {
        int id PK
        int ca_thuc_hanh_ma FK
        string ten_tep
        string duong_dan_tep
        int kich_thuoc_tep
        string loai_tep
        text mo_ta
        int nguoi_tai_len FK
        datetime ngay_tai_len
        boolean kich_hoat
    }
    
    MauCaThucHanh {
        int id PK
        string ten_mau
        text mo_ta
        string tieu_de_mac_dinh
        text mo_ta_mac_dinh
        int thoi_gian_thuc_hien
        int so_luong_toi_da_mac_dinh
        text tags_mac_dinh
        text yeu_cau_thiet_bi_mac_dinh
        string muc_do_kho
        int diem_so_toi_da
        int nguoi_tao_ma FK
        datetime ngay_tao
        boolean kich_hoat
    }
    
    DanhGiaCa {
        int id PK
        int ca_thuc_hanh_ma FK
        int nguoi_danh_gia FK
        int diem_danh_gia
        text nhan_xet
        datetime ngay_danh_gia
    }
    
    ThongBao {
        int id PK
        int nguoi_nhan FK
        string tieu_de
        text noi_dung
        string loai
        string lien_ket
        boolean da_doc
        datetime ngay_tao
        datetime ngay_doc
    }
    
    SinhVien {
        int id PK
        string ten
        string email
        date ngay_sinh
        string lop
        datetime ngay_tao
    }
```

## Chi tiết các bảng

### 1. Bảng NguoiDung (Users)
**Mục đích**: Quản lý tất cả người dùng trong hệ thống

| Cột | Kiểu dữ liệu | Mô tả |
|-----|-------------|-------|
| `id` | Integer, PK | ID người dùng |
| `ten_nguoi_dung` | String(80), Unique | Tên đăng nhập |
| `email` | String(120), Unique | Email người dùng |
| `mat_khau_hash` | String(256) | Mật khẩu đã hash |
| `vai_tro` | String(20) | Vai trò: nguoi_dung, quan_tri_vien, quan_tri_he_thong |
| `ngay_tao` | DateTime | Ngày tạo tài khoản |
| `last_seen` | DateTime | Lần cuối truy cập |
| `bio` | Text | Giới thiệu bản thân |
| `is_verified` | Boolean | Trạng thái xác thực email |
| `verification_token` | String(100) | Token xác thực email |
| `verification_token_expiry` | Integer | Thời gian hết hạn token |
| `active` | Boolean | Trạng thái hoạt động |
| `failed_login_attempts` | Integer | Số lần đăng nhập thất bại |
| `last_failed_login` | DateTime | Lần thất bại cuối |
| `account_locked_until` | DateTime | Thời gian khóa tài khoản |
| `reset_token` | String(100) | Token đặt lại mật khẩu |
| `reset_token_expiry` | Integer | Thời gian hết hạn reset token |

**Index**: 
- `idx_nguoi_dung_email` trên cột `email`
- `idx_nguoi_dung_ten_nguoi_dung` trên cột `ten_nguoi_dung`

### 2. Bảng CaThucHanh (Lab Sessions)
**Mục đích**: Quản lý các ca thực hành

| Cột | Kiểu dữ liệu | Mô tả |
|-----|-------------|-------|
| `id` | Integer, PK | ID ca thực hành |
| `tieu_de` | String(100) | Tiêu đề ca thực hành |
| `mo_ta` | Text | Mô tả chi tiết |
| `ngay` | Date | Ngày thực hiện |
| `gio_bat_dau` | DateTime | Thời gian bắt đầu |
| `gio_ket_thuc` | DateTime | Thời gian kết thúc |
| `dia_diem` | String(100) | Địa điểm thực hiện |
| `so_luong_toi_da` | Integer | Số lượng sinh viên tối đa |
| `dang_hoat_dong` | Boolean | Trạng thái hoạt động |
| `ma_xac_thuc` | String(10) | Mã xác nhận tham dự |
| `nguoi_tao_ma` | Integer, FK | ID người tạo |
| `ngay_tao` | DateTime | Ngày tạo |
| `tags` | Text (JSON) | Các tag phân loại |
| `anh_bia` | String(255) | Đường dẫn ảnh bìa |
| `muc_do_kho` | String(20) | Mức độ khó: dễ, trung bình, khó |
| `yeu_cau_thiet_bi` | Text (JSON) | Thiết bị yêu cầu |
| `ghi_chu_noi_bo` | Text | Ghi chú nội bộ |
| `cho_phep_dang_ky_tre` | Boolean | Cho phép đăng ký muộn |
| `tu_dong_xac_nhan` | Boolean | Tự động xác nhận đăng ký |
| `thong_bao_truoc` | Integer | Thông báo trước (phút) |
| `trang_thai` | String(20) | Trạng thái: scheduled, ongoing, completed, cancelled |
| `diem_so_toi_da` | Integer | Điểm số tối đa |
| `thoi_gian_lam_bai` | Integer | Thời gian làm bài (phút) |

### 3. Bảng DangKyCa (Session Registrations)
**Mục đích**: Quản lý đăng ký tham gia ca thực hành

| Cột | Kiểu dữ liệu | Mô tả |
|-----|-------------|-------|
| `id` | Integer, PK | ID đăng ký |
| `nguoi_dung_ma` | Integer, FK | ID người dùng |
| `ca_thuc_hanh_ma` | Integer, FK | ID ca thực hành |
| `ghi_chu` | Text | Ghi chú đăng ký |
| `trang_thai_tham_gia` | String(20) | Trạng thái tham gia |
| `ngay_dang_ky` | DateTime | Ngày đăng ký |
| `uu_tien` | Integer | Mức ưu tiên |
| `da_xac_nhan` | Boolean | Đã xác nhận |
| `ngay_xac_nhan` | DateTime | Ngày xác nhận |

### 4. Bảng VaoCa (Session Attendance)
**Mục đích**: Theo dõi việc tham dự và kết quả ca thực hành

| Cột | Kiểu dữ liệu | Mô tả |
|-----|-------------|-------|
| `id` | Integer, PK | ID tham dự |
| `nguoi_dung_ma` | Integer, FK | ID người dùng |
| `ca_thuc_hanh_ma` | Integer, FK | ID ca thực hành |
| `thoi_gian_vao` | DateTime | Thời gian vào |
| `thoi_gian_ra` | DateTime | Thời gian ra |
| `ket_qua` | Text | Kết quả thực hành |
| `diem_so` | Integer | Điểm số |
| `nhan_xet_gv` | Text | Nhận xét giảng viên |
| `tep_nop_bai` | String(500) | File nộp bài |
| `trang_thai_nop` | String(20) | Trạng thái nộp bài |
| `thoi_gian_nop` | DateTime | Thời gian nộp |
| `vi_tri_ngoi` | String(20) | Vị trí ngồi |

### 5. Bảng NhatKyHoatDong (Activity Logs)
**Mục đích**: Ghi nhận lại tất cả hoạt động trong hệ thống

| Cột | Kiểu dữ liệu | Mô tả |
|-----|-------------|-------|
| `id` | Integer, PK | ID log |
| `nguoi_dung_ma` | Integer, FK | ID người dùng |
| `hanh_dong` | String(128) | Hành động thực hiện |
| `chi_tiet` | Text | Chi tiết hành động |
| `dia_chi_ip` | String(45) | Địa chỉ IP |
| `thoi_gian` | DateTime | Thời gian thực hiện |

### 6. Bảng CaiDatHeThong (System Settings)
**Mục đích**: Lưu trữ cấu hình hệ thống

| Cột | Kiểu dữ liệu | Mô tả |
|-----|-------------|-------|
| `id` | Integer, PK | ID cài đặt |
| `khoa` | String(64), Unique | Khóa cài đặt |
| `gia_tri` | Text | Giá trị cài đặt |
| `kieu` | String(16) | Kiểu dữ liệu: string, boolean, integer, float |
| `mo_ta` | String(256) | Mô tả cài đặt |
| `ngay_tao` | DateTime | Ngày tạo |
| `ngay_cap_nhat` | DateTime | Ngày cập nhật |

### 7. Bảng ThietBi (Equipment)
**Mục đích**: Quản lý thiết bị phòng thực hành

| Cột | Kiểu dữ liệu | Mô tả |
|-----|-------------|-------|
| `id` | Integer, PK | ID thiết bị |
| `ten_thiet_bi` | String(100) | Tên thiết bị |
| `mo_ta` | Text | Mô tả thiết bị |
| `so_luong_co_san` | Integer | Số lượng có sẵn |
| `trang_thai` | String(20) | Trạng thái: available, in_use, maintenance |
| `vi_tri` | String(100) | Vị trí đặt |
| `ghi_chu` | Text | Ghi chú |
| `ngay_tao` | DateTime | Ngày tạo |

### 8. Bảng ThongBao (Notifications)
**Mục đích**: Hệ thống thông báo cho người dùng

| Cột | Kiểu dữ liệu | Mô tả |
|-----|-------------|-------|
| `id` | Integer, PK | ID thông báo |
| `nguoi_nhan` | Integer, FK | ID người nhận |
| `tieu_de` | String(200) | Tiêu đề thông báo |
| `noi_dung` | Text | Nội dung thông báo |
| `loai` | String(50) | Loại: info, warning, success, error |
| `lien_ket` | String(500) | Liên kết liên quan |
| `da_doc` | Boolean | Đã đọc |
| `ngay_tao` | DateTime | Ngày tạo |
| `ngay_doc` | DateTime | Ngày đọc |

## Relationships & Foreign Keys

### Các mối quan hệ chính:

1. **NguoiDung -> CaThucHanh**: Một người có thể tạo nhiều ca thực hành
2. **NguoiDung -> DangKyCa**: Một người có thể đăng ký nhiều ca
3. **NguoiDung -> VaoCa**: Một người có thể tham dự nhiều ca
4. **CaThucHanh -> DangKyCa**: Một ca có nhiều đăng ký
5. **CaThucHanh -> VaoCa**: Một ca có nhiều người tham dự
6. **CaThucHanh -> TaiLieuCa**: Một ca có nhiều tài liệu
7. **ThietBi -> DatThietBi**: Một thiết bị có thể được đặt cho nhiều ca

### Cascade Operations:

- `CaThucHanh` xóa → Tự động xóa `DangKyCa`, `VaoCa`, `TaiLieuCa`, `DanhGiaCa`
- `NguoiDung` xóa → Set NULL cho `nguoi_tao_ma` trong `CaThucHanh`

## Database Commands

### Khởi tạo Database
```bash
# Initialize migration repository
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### Backup Database
```bash
# SQLite backup
cp app.db backup_$(date +%Y%m%d_%H%M%S).db

# PostgreSQL backup
pg_dump labmanager > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Database Maintenance
```bash
# Check database integrity (SQLite)
sqlite3 app.db "PRAGMA integrity_check;"

# Vacuum database (SQLite)
sqlite3 app.db "VACUUM;"

# Analyze statistics (SQLite)
sqlite3 app.db "ANALYZE;"
```

## Indexes và Performance

### Existing Indexes:
- `NguoiDung.email` (Unique)
- `NguoiDung.ten_nguoi_dung` (Unique)
- `CaiDatHeThong.khoa` (Unique)

### Recommended Additional Indexes:
```sql
-- For frequent queries
CREATE INDEX idx_ca_thuc_hanh_ngay ON ca_thuc_hanh(ngay);
CREATE INDEX idx_ca_thuc_hanh_trang_thai ON ca_thuc_hanh(trang_thai);
CREATE INDEX idx_dang_ky_ca_nguoi_dung ON dang_ky_ca(nguoi_dung_ma);
CREATE INDEX idx_vao_ca_nguoi_dung ON vao_ca(nguoi_dung_ma);
CREATE INDEX idx_nhat_ky_thoi_gian ON nhat_ky_hoat_dong(thoi_gian);
CREATE INDEX idx_thong_bao_nguoi_nhan ON thong_bao(nguoi_nhan, da_doc);
```

## Security Considerations

### Password Security:
- Sử dụng Werkzeug password hashing
- Salt tự động được tạo
- Không lưu password plain text

### Token Security:
- Reset tokens có thời gian hết hạn
- Verification tokens được tạo ngẫu nhiên
- Tokens được xóa sau khi sử dụng

### Access Control:
- Role-based access control
- Foreign key constraints
- SQL injection protection thông qua ORM

## Sample Data Structure

### Vai trò người dùng:
```python
VAI_TRO = {
    'nguoi_dung': 'Người dùng thông thường',
    'quan_tri_vien': 'Quản trị viên', 
    'quan_tri_he_thong': 'Quản trị hệ thống'
}
```

### Trạng thái ca thực hành:
```python
TRANG_THAI_CA = {
    'scheduled': 'Đã lên lịch',
    'ongoing': 'Đang diễn ra',
    'completed': 'Đã hoàn thành',
    'cancelled': 'Đã hủy'
}
```

### Mức độ khó:
```python
MUC_DO_KHO = {
    'de': 'Dễ',
    'trung_binh': 'Trung bình', 
    'kho': 'Khó'
}
```

## Migration History

### Current Migrations:
1. `0c09e8fa5431` - Add user security and verification fields

### Planned Migrations:
- Add full-text search indexes
- Add audit trail tables
- Add file storage metadata
- Add API rate limiting tables

---

*Database được thiết kế để đảm bảo tính toàn vẹn dữ liệu, hiệu suất cao và khả năng mở rộng trong tương lai.*
