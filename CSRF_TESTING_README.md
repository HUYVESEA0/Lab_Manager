# CSRF Testing Setup Guide

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Run the automated installer
python install_csrf_deps.py

# Or manually install
pip install -r requirements.txt
pip install selenium webdriver-manager chromedriver-autoinstaller
```

### 2. Setup Test Environment
```bash
# Setup test environment (optional)
python test/setup_csrf_tests.py
```

### 3. Run Tests
```bash
# Run all tests with HTML report
python test/run_all_csrf_tests.py --html

# Run individual test suites
python test/csrf_unit_tests.py
python test/csrf_integration_tests.py
python test/csrf_system_test.py
```

## 📦 Dependencies

### Required Packages
- **Flask ecosystem**: Flask, Flask-WTF, Flask-Login
- **Testing**: pytest, requests
- **Browser automation**: selenium, webdriver-manager

### Optional Packages
- **chromedriver-autoinstaller**: Automatic Chrome driver management
- **beautifulsoup4**: HTML parsing for tests
- **coverage**: Code coverage reports

## 🔧 Troubleshooting

### Selenium Import Error
```
ImportError: No module named 'selenium'
```

**Solution:**
```bash
pip install selenium==4.15.2 webdriver-manager==4.0.1
```

### Chrome Driver Issues
```
WebDriverException: 'chromedriver' executable needs to be in PATH
```

**Solutions:**
1. **Automatic (Recommended):**
   ```bash
   python install_csrf_deps.py
   ```

2. **Manual:**
   - Download Chrome driver from [chromedriver.chromium.org](https://chromedriver.chromium.org/)
   - Add to PATH or place in project directory
   - Ensure Chrome browser is installed

### Permission Issues (Windows)
```
PermissionError: [WinError 5] Access is denied
```

**Solution:**
- Run terminal as Administrator
- Or use virtual environment:
  ```bash
  python -m venv csrf_test_env
  csrf_test_env\Scripts\activate  # Windows
  source csrf_test_env/bin/activate  # Linux/Mac
  pip install -r requirements.txt
  ```

## 🧪 Test Types

### 1. Unit Tests (`csrf_unit_tests.py`)
- CSRF token generation
- API endpoint testing
- Validation logic
- Middleware functionality

### 2. Integration Tests (`csrf_integration_tests.py`)
- Browser-based testing with Selenium
- Real user interaction simulation
- Performance testing
- End-to-end workflows

### 3. System Tests (`csrf_system_test.py`)
- HTTP request testing
- Security validation
- API endpoint verification
- Error handling

## 📊 Test Reports

### HTML Reports
Generated automatically with `--html` flag:
```
csrf-test-report-YYYYMMDD-HHMMSS.html
```

### JSON Results
Detailed test results saved as:
```
csrf-test-results-YYYYMMDD-HHMMSS.json
```

## 🌐 Demo Pages

After starting the Flask application, access:

- **CSRF Demo**: `/csrf-demo`
  - Interactive CSRF testing
  - Token management
  - Security demonstrations

- **API Integration Demo**: `/api-integration-demo`
  - API endpoint testing
  - Request builder
  - Response viewer

- **Basic Test Page**: `/csrf-test`
  - Simple CSRF testing interface

## ⚙️ Configuration

### Test Configuration (`test/csrf_test_config.json`)
```json
{
  "test_server": {
    "host": "localhost",
    "port": 5001,
    "url": "http://localhost:5001"
  },
  "csrf_endpoints": [
    "/api/v1/csrf-token",
    "/csrf-token",
    "/admin/csrf-token",
    "/lab/csrf-token"
  ],
  "browser_options": {
    "headless": true,
    "no_sandbox": true,
    "disable_gpu": true
  }
}
```

## 🔍 Manual Testing

### 1. Start Application
```bash
python run.py
```

### 2. Access Demo Pages
- Navigate to `http://localhost:5000/csrf-demo`
- Test various CSRF scenarios
- Monitor browser console for errors

### 3. API Testing
- Use `/api-integration-demo` for interactive testing
- Test endpoints with curl:
  ```bash
  curl -X GET http://localhost:5000/api/v1/csrf-token
  ```

## 📝 Common Issues

### 1. Tests Fail with "CSRF token missing"
- Ensure Flask app is configured with `WTF_CSRF_ENABLED = True`
- Check that CSRF token is included in requests
- Verify session handling

### 2. Browser Tests Skip/Fail
- Install Chrome browser
- Update Chrome driver: `python install_csrf_deps.py`
- Check firewall/antivirus blocking

### 3. Performance Tests Timeout
- Increase timeout values in test configuration
- Check system resources
- Reduce concurrent request count

## 🆘 Getting Help

1. **Check logs**: Look for error messages in test output
2. **Verify setup**: Run `python install_csrf_deps.py`
3. **Test manually**: Use demo pages to isolate issues
4. **Check dependencies**: Ensure all packages are installed correctly

## 📚 Additional Resources

- [Flask-WTF Documentation](https://flask-wtf.readthedocs.io/)
- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [CSRF Protection Best Practices](https://owasp.org/www-community/attacks/csrf)
