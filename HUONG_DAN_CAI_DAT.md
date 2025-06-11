# Hướng Dẫn Cài Đặt Lab Manager

## 🚀 Cài Đặt Nhanh

### Phương Pháp 1: Sử dụng Script Tự Động
```bash
# Chạy script khắc phục lỗi cài đặt
python fix_installation.py

# Hoặc chạy batch script (Windows)
fix_installation.bat
```

### Phương Pháp 2: Cài Đặt Thủ Công
```bash
# Nâng cấp pip
python -m pip install --upgrade pip

# Cài đặt lxml (package hay gặp lỗi)
python -m pip install --only-binary=lxml lxml

# Cài đặt các dependencies còn lại
python -m pip install -r requirements.txt

# Chạy ứng dụng
python run.py
```

## ⚠️ Khắc Phục Lỗi Thường Gặp

### Lỗi Microsoft Visual C++ 14.0
**Triệu chứng:** 
```
error: Microsoft Visual C++ 14.0 or greater is required
```

**Giải pháp:**
1. Tải và cài đặt [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Chọn workload "C++ build tools" 
3. Bao gồm các components:
   - MSVC v143 - VS 2022 C++ x64/x86 build tools
   - Windows 10/11 SDK (latest version)
   - CMake tools for Visual Studio
4. Restart máy tính sau khi cài đặt

### Lỗi lxml Build Failed
**Triệu chứng:**
```
Building wheel for lxml failed
```

**Giải pháp:**
```bash
# Cài lxml từ pre-compiled wheel
python -m pip install --only-binary=lxml lxml

# Hoặc sử dụng phiên bản cụ thể
python -m pip install lxml==4.9.3 --only-binary=lxml
```

### Lỗi selectolax Requires C++ Build Tools
**Giải pháp:** Package này đã được comment trong requirements.txt và thay thế bằng BeautifulSoup4.

## 📦 Dependencies Chính

- **Flask 2.2.3** - Web framework
- **SQLAlchemy 1.4.46** - Database ORM
- **Flask-WTF 1.1.1** - Form handling với CSRF protection
- **lxml 5.4.0** - XML/HTML parsing
- **BeautifulSoup4 4.12.2** - HTML parsing (thay thế cho selectolax)
- **Selenium 4.15.2** - Web testing
- **pytest 7.4.3** - Testing framework

## 🔧 Files Hỗ Trợ Cài Đặt

- `fix_installation.py` - Script Python khắc phục lỗi cài đặt
- `fix_installation.bat` - Batch script cho Windows
- `requirements_safe.txt` - Requirements với alternatives an toàn
- `install_windows.bat` - Script cài đặt tự động cho Windows

## ✅ Kiểm Tra Cài Đặt

Sau khi cài đặt thành công:

```bash
# Chạy ứng dụng
python run.py

# Mở trình duyệt và truy cập
# http://127.0.0.1:5000
```

Nếu thấy thông báo:
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

Thì cài đặt đã thành công! 🎉

## 🧪 Chạy Tests

```bash
# Chạy tất cả CSRF tests
python test/run_all_csrf_tests.py

# Chạy unit tests
python -m pytest test/csrf_unit_tests.py

# Chạy integration tests  
python -m pytest test/csrf_integration_tests.py
```

## 🆘 Hỗ Trợ

Nếu gặp vấn đề:
1. Chạy `python fix_installation.py` để tự động khắc phục
2. Kiểm tra log lỗi trong terminal
3. Đảm bảo đã cài đặt Python 3.8+ và pip mới nhất
4. Restart terminal sau khi cài đặt Build Tools

## 🎯 Quick Start

```bash
# Clone hoặc tải project
cd Lab_Manager

# Chạy script khắc phục (khuyến nghị)
python fix_installation.py

# Chạy app
python run.py

# Truy cập http://127.0.0.1:5000
```

**Lưu ý:** Script `fix_installation.py` sẽ tự động thử nhiều phương pháp cài đặt khác nhau và chọn phương pháp phù hợp nhất cho hệ thống của bạn.
