# Hướng dẫn Tạo Người Dùng Mới - Lab Manager

## Tổng quan

Hệ thống Lab Manager cung cấp nhiều cách để tạo người dùng mới với các tính năng nâng cao về bảo mật và validation.

## Các cách tạo người dùng

### 1. Đăng ký tự do (Public Registration)

**Endpoint:** `/auth/register-advanced`

Dành cho người dùng tự đăng ký tài khoản với:
- Validation mật khẩu mạnh
- Kiểm tra real-time username/email
- UI hiện đại với password strength indicator
- Xác thực điều khoản sử dụng

**Các tính năng:**
- ✅ Validation password strength với regex
- ✅ Kiểm tra username format (chỉ chữ cái, số, gạch dưới)
- ✅ Xác thực email format
- ✅ Real-time availability check
- ✅ Password visibility toggle
- ✅ Responsive design

### 2. Tạo người dùng đơn lẻ (Admin)

**Endpoint:** `/admin/create-user`

Dành cho admin tạo người dùng với wizard interface:

**Bước 1: Thông tin cơ bản**
- Tên người dùng (3-20 ký tự)
- Email hợp lệ
- Validation real-time

**Bước 2: Bảo mật**
- Mật khẩu với strength indicator
- Xác nhận mật khẩu
- Yêu cầu password mạnh

**Bước 3: Vai trò**
- Người dùng thường
- Quản trị viên
- Quản trị hệ thống (chỉ system admin)

**Bước 4: Xác nhận**
- Preview thông tin người dùng
- Avatar tự động tạo
- Thông tin tổng hợp

### 3. Tạo người dùng hàng loạt (Bulk Creation)

**Endpoint:** `/admin/bulk-create-users`

Tạo nhiều người dùng cùng lúc bằng JSON:

```json
[
  {
    "ten_nguoi_dung": "user1",
    "email": "user1@example.com",
    "mat_khau": "SecurePass123!",
    "vai_tro": "nguoi_dung",
    "bio": "Sinh viên khoa CNTT"
  },
  {
    "ten_nguoi_dung": "admin1",
    "email": "admin1@example.com", 
    "mat_khau": "AdminPass456@",
    "vai_tro": "quan_tri_vien",
    "bio": "Quản trị viên hệ thống"
  }
]
```

**Tính năng:**
- ✅ JSON validation real-time
- ✅ Bulk validation password strength
- ✅ Import example data
- ✅ Detailed error reporting
- ✅ Progress tracking

## API Endpoints

### 1. Public Registration
```http
POST /api/users/register
Content-Type: application/json

{
  "ten_nguoi_dung": "username",
  "email": "user@example.com",
  "mat_khau": "SecurePass123!",
  "bio": "Giới thiệu bản thân"
}
```

### 2. Admin User Creation
```http
POST /api/users/create
Content-Type: application/json
Authorization: Required (Admin)

{
  "ten_nguoi_dung": "username",
  "email": "user@example.com",
  "mat_khau": "SecurePass123!",
  "vai_tro": "nguoi_dung",
  "bio": "Bio text"
}
```

### 3. Bulk User Creation
```http
POST /api/users/bulk-create
Content-Type: application/json
Authorization: Required (Admin)

{
  "users": [
    {
      "ten_nguoi_dung": "user1",
      "email": "user1@example.com",
      "mat_khau": "SecurePass123!",
      "vai_tro": "nguoi_dung"
    }
  ]
}
```

### 4. Check Username Availability
```http
POST /api/users/check-username
Content-Type: application/json

{
  "username": "desired_username"
}
```

### 5. Check Email Availability
```http
POST /api/users/check-email
Content-Type: application/json

{
  "email": "user@example.com"
}
```

## Quy tắc Validation

### Username
- Độ dài: 3-20 ký tự
- Ký tự cho phép: chữ cái (a-z, A-Z), số (0-9), gạch dưới (_)
- Phải unique trong hệ thống
- Không được chứa khoảng trắng hoặc ký tự đặc biệt

### Email
- Format hợp lệ theo RFC 5322
- Phải unique trong hệ thống
- Tự động lowercase khi lưu

### Password
- Độ dài tối thiểu: 8 ký tự
- Bắt buộc có:
  - Ít nhất 1 chữ hoa (A-Z)
  - Ít nhất 1 chữ thường (a-z)
  - Ít nhất 1 số (0-9)
  - Ít nhất 1 ký tự đặc biệt (!@#$%^&*()_+-=[]{}|;:,.<>?)

### Vai trò (Role)
- `nguoi_dung`: Người dùng thường
- `quan_tri_vien`: Quản trị viên
- `quan_tri_he_thong`: Quản trị hệ thống (highest level)

## Tính năng Bảo mật

### 1. Account Locking
- Khóa tài khoản sau 5 lần đăng nhập sai
- Thời gian khóa: 30 phút
- Tự động reset counter khi đăng nhập thành công

### 2. Email Verification
- Token xác thực gửi qua email
- Thời gian hết hạn: 24 giờ
- Tài khoản chưa xác thực có hạn chế quyền

### 3. Password Security
- Hash bằng Werkzeug (PBKDF2)
- Salt tự động
- Không lưu plain text password

## Database Schema

### Bảng NguoiDung (Users)
```sql
-- Các trường mới được thêm
is_verified BOOLEAN DEFAULT FALSE,
verification_token VARCHAR(100),
verification_token_expiry INTEGER,
active BOOLEAN DEFAULT TRUE,
failed_login_attempts INTEGER DEFAULT 0,
last_failed_login DATETIME,
account_locked_until DATETIME
```

## Migration

Chạy migration để thêm các trường mới:

```bash
flask db migrate -m "Add user security fields"
flask db upgrade
```

## JavaScript Components

### UserCreationManager
File: `app/static/js/user-creation.js`

**Tính năng:**
- Real-time validation
- Password strength indicator
- AJAX form submission
- Error handling
- Notification system
- Bulk creation support

**Sử dụng:**
```javascript
// Tự động khởi tạo khi DOM loaded
document.addEventListener('DOMContentLoaded', function() {
    new UserCreationManager();
});
```

## CSS Styling

### Classes chính
- `.notification`: Thông báo floating
- `.bulk-results-modal`: Modal kết quả bulk creation
- `.password-strength`: Indicator độ mạnh password
- `.validation-feedback`: Thông báo validation
- `.wizard-*`: Các thành phần wizard interface

## Error Handling

### Client-side
- Real-time validation
- User-friendly error messages
- Visual feedback (red/green borders)
- Floating notifications

### Server-side
- Comprehensive error logging
- Structured error responses
- Database rollback on failure
- Rate limiting protection

## Performance

### Caching
- User list cached 5 minutes
- User stats cached 3 minutes
- Automatic cache invalidation on user changes

### Database
- Indexes on email và username
- Optimized queries with pagination
- Bulk insert for multiple users

## Testing

### Unit Tests
```python
# Test user creation
def test_create_user_success():
    user_data = {
        'ten_nguoi_dung': 'testuser',
        'email': 'test@example.com',
        'mat_khau': 'SecurePass123!',
        'vai_tro': 'nguoi_dung'
    }
    result, status = user_service.create_user(user_data)
    assert status == 200
    assert result['success'] == True
```

### API Tests
```python
# Test API endpoint
def test_register_api():
    response = client.post('/api/users/register', json={
        'ten_nguoi_dung': 'newuser',
        'email': 'new@example.com',
        'mat_khau': 'SecurePass123!'
    })
    assert response.status_code == 201
```

## Troubleshooting

### Lỗi thường gặp

1. **Username/Email đã tồn tại**
   - Kiểm tra database
   - Sử dụng API check availability

2. **Password không đủ mạnh**
   - Kiểm tra regex validation
   - Ensure 8+ chars với mixed case, numbers, symbols

3. **Email verification không hoạt động**
   - Kiểm tra SMTP settings
   - Verify token expiration

4. **Bulk creation lỗi**
   - Validate JSON format
   - Check individual user data
   - Review error logs

### Debug Mode
```python
# Enable debug logging
import logging
logging.getLogger('app.services.user_service').setLevel(logging.DEBUG)
```

## Customization

### Thêm fields mới
1. Update `NguoiDung` model
2. Add to forms (`AdvancedRegistrationForm`, `CreateUserForm`)
3. Update templates
4. Modify API endpoints
5. Run migration

### Custom validation
```python
def custom_username_validator(form, field):
    # Custom validation logic
    if not custom_check(field.data):
        raise ValidationError('Custom error message')
```

## Best Practices

### Security
- ✅ Always hash passwords
- ✅ Validate input on both client and server
- ✅ Use CSRF protection
- ✅ Implement rate limiting
- ✅ Log security events

### UX
- ✅ Real-time feedback
- ✅ Clear error messages
- ✅ Progressive enhancement
- ✅ Mobile-friendly design
- ✅ Accessible forms

### Performance
- ✅ Cache frequently accessed data
- ✅ Use pagination for large lists
- ✅ Optimize database queries
- ✅ Minimize JavaScript payload
- ✅ Lazy load components
