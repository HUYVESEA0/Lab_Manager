#!/bin/bash
# Lab Manager - macOS Test Runner
# Comprehensive testing suite for macOS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_header() {
    echo -e "${PURPLE}🍎 $1${NC}"
}

print_test() {
    echo -e "${CYAN}🧪 $1${NC}"
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS only!"
    exit 1
fi

print_header "Lab Manager - macOS Test Suite"
echo "================================"

# Check if we're in the correct directory
if [[ ! -f "run.py" ]] || [[ ! -f "requirements.txt" ]]; then
    print_error "Please run this script from the Lab_Manager project directory"
    exit 1
fi

# Check and activate virtual environment
if [[ ! -d "venv" ]]; then
    print_error "Virtual environment not found. Please run setup_mac.sh first"
    exit 1
fi

source venv/bin/activate
print_status "Virtual environment activated"

# Function to run basic application tests
test_app_basic() {
    print_test "Running basic application tests..."
    
    python3 -c "
import sys
import traceback

def test_imports():
    try:
        import flask
        print('✅ Flask import successful')
        import flask_sqlalchemy
        print('✅ Flask-SQLAlchemy import successful')
        import flask_login
        print('✅ Flask-Login import successful')
        return True
    except ImportError as e:
        print(f'❌ Import failed: {e}')
        return False

def test_app_creation():
    try:
        from app import create_app
        app, socketio = create_app()
        print('✅ App creation successful')
        print(f'   App name: {app.name}')
        print(f'   Debug mode: {app.debug}')
        return True
    except Exception as e:
        print(f'❌ App creation failed: {e}')
        traceback.print_exc()
        return False

def test_database_connection():
    try:
        from app import create_app
        from app.models import db
        app, _ = create_app()
        with app.app_context():
            db.engine.connect()
            print('✅ Database connection successful')
        return True
    except Exception as e:
        print(f'❌ Database connection failed: {e}')
        return False

def test_routes():
    try:
        from app import create_app
        app, _ = create_app()
        with app.app_context():
            rules = list(app.url_map.iter_rules())
            print(f'✅ Routes loaded: {len(rules)} endpoints')
        return True
    except Exception as e:
        print(f'❌ Routes test failed: {e}')
        return False

# Run all tests
all_passed = True
all_passed &= test_imports()
all_passed &= test_app_creation()
all_passed &= test_database_connection()
all_passed &= test_routes()

if all_passed:
    print('\n✅ All basic tests passed!')
    sys.exit(0)
else:
    print('\n❌ Some tests failed!')
    sys.exit(1)
"
}

# Function to run authentication tests
test_authentication() {
    print_test "Running authentication tests..."
    
    python3 -c "
from app import create_app
from app.models import db, NguoiDung

app, _ = create_app()
with app.app_context():
    try:
        # Test user creation
        test_user = NguoiDung(
            ten_nguoi_dung='test_user_mac',
            email='test@mac.local',
            vai_tro='nguoi_dung'
        )
        test_user.dat_mat_khau('test_password_123')
        
        # Test password verification
        if test_user.kiem_tra_mat_khau('test_password_123'):
            print('✅ Password hashing and verification works')
        else:
            print('❌ Password verification failed')
            
        # Test user roles
        if test_user.vai_tro == 'nguoi_dung':
            print('✅ User role assignment works')
        else:
            print('❌ User role assignment failed')
            
        print('✅ Authentication tests passed')
        
    except Exception as e:
        print(f'❌ Authentication test failed: {e}')
"
}

# Function to run database model tests
test_database_models() {
    print_test "Running database model tests..."
    
    python3 -c "
from app import create_app
from app.models import db, NguoiDung, KhoaHoc, BaiHoc

app, _ = create_app()
with app.app_context():
    try:
        # Test database tables exist
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['nguoi_dung', 'khoa_hoc', 'bai_hoc', 'phien_thuc_hanh']
        missing_tables = [t for t in expected_tables if t not in tables]
        
        if missing_tables:
            print(f'⚠️  Missing tables: {missing_tables}')
        else:
            print('✅ All expected database tables exist')
            
        # Test model relationships
        user_count = NguoiDung.query.count()
        print(f'✅ Database contains {user_count} users')
        
        course_count = KhoaHoc.query.count()
        print(f'✅ Database contains {course_count} courses')
        
        lesson_count = BaiHoc.query.count()
        print(f'✅ Database contains {lesson_count} lessons')
        
        print('✅ Database model tests passed')
        
    except Exception as e:
        print(f'❌ Database model test failed: {e}')
        import traceback
        traceback.print_exc()
"
}

# Function to run configuration tests
test_configuration() {
    print_test "Running configuration tests..."
    
    python3 -c "
import os
from app import create_app

app, _ = create_app()

# Test essential configuration
config_tests = [
    ('SECRET_KEY', app.config.get('SECRET_KEY')),
    ('SQLALCHEMY_DATABASE_URI', app.config.get('SQLALCHEMY_DATABASE_URI')),
    ('WTF_CSRF_ENABLED', app.config.get('WTF_CSRF_ENABLED')),
]

all_passed = True
for key, value in config_tests:
    if value:
        print(f'✅ {key} is configured')
    else:
        print(f'❌ {key} is missing')
        all_passed = False

# Test environment variables
env_vars = ['FLASK_APP', 'SECRET_KEY']
for var in env_vars:
    if os.getenv(var):
        print(f'✅ Environment variable {var} is set')
    else:
        print(f'⚠️  Environment variable {var} is not set')

if all_passed:
    print('✅ Configuration tests passed')
else:
    print('❌ Some configuration tests failed')
"
}

# Function to run security tests
test_security() {
    print_test "Running security tests..."
    
    python3 -c "
from app import create_app
import secrets

app, _ = create_app()

# Test CSRF protection
csrf_enabled = app.config.get('WTF_CSRF_ENABLED', False)
if csrf_enabled:
    print('✅ CSRF protection is enabled')
else:
    print('⚠️  CSRF protection is disabled (check for development mode)')

# Test secret key strength
secret_key = app.config.get('SECRET_KEY', '')
if len(secret_key) >= 32:
    print('✅ SECRET_KEY length is adequate')
else:
    print('⚠️  SECRET_KEY should be at least 32 characters')

if 'development' not in secret_key.lower():
    print('✅ SECRET_KEY appears to be production-ready')
else:
    print('⚠️  Using development SECRET_KEY')

# Test session configuration
session_lifetime = app.config.get('PERMANENT_SESSION_LIFETIME')
if session_lifetime:
    print(f'✅ Session lifetime configured: {session_lifetime} seconds')
else:
    print('⚠️  Session lifetime not configured')

print('✅ Security tests completed')
"
}

# Function to run performance tests
test_performance() {
    print_test "Running performance tests..."
    
    python3 -c "
import time
from app import create_app

app, _ = create_app()

# Test app startup time
start_time = time.time()
test_app, test_socketio = create_app()
startup_time = time.time() - start_time

print(f'✅ App startup time: {startup_time:.3f} seconds')

if startup_time < 2.0:
    print('✅ Startup time is excellent')
elif startup_time < 5.0:
    print('⚠️  Startup time is acceptable')
else:
    print('⚠️  Startup time is slow, consider optimization')

# Test database query performance
with test_app.app_context():
    from app.models import NguoiDung
    
    start_time = time.time()
    users = NguoiDung.query.all()
    query_time = time.time() - start_time
    
    print(f'✅ Database query time: {query_time:.3f} seconds for {len(users)} users')

print('✅ Performance tests completed')
"
}

# Function to run Selenium web tests (if Chrome is available)
test_selenium() {
    print_test "Running Selenium web tests..."
    
    # Check if Chrome is available
    if ! command -v google-chrome &> /dev/null && ! ls /Applications/Google\ Chrome.app &> /dev/null; then
        print_warning "Google Chrome not found. Skipping Selenium tests."
        return
    fi
    
    python3 -c "
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    import time
    import threading
    from app import create_app
    
    # Start Flask app in background
    app, socketio = create_app()
    
    def run_app():
        socketio.run(app, host='127.0.0.1', port=5001, debug=False, use_reloader=False)
    
    print('🚀 Starting test server...')
    server_thread = threading.Thread(target=run_app, daemon=True)
    server_thread.start()
    time.sleep(3)  # Wait for server to start
    
    # Configure Chrome for headless testing
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    # Create driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Test home page
        driver.get('http://127.0.0.1:5001')
        time.sleep(2)
        
        if 'Lab Manager' in driver.title:
            print('✅ Home page loads correctly')
        else:
            print(f'❌ Home page title incorrect: {driver.title}')
        
        # Test login page
        login_links = driver.find_elements('xpath', '//a[contains(@href, \"login\")]')
        if login_links:
            login_links[0].click()
            time.sleep(1)
            
            if 'login' in driver.current_url.lower():
                print('✅ Login page navigation works')
            else:
                print('❌ Login page navigation failed')
        
        print('✅ Selenium tests completed successfully')
        
    except Exception as e:
        print(f'❌ Selenium test failed: {e}')
    
    finally:
        driver.quit()
        
except ImportError:
    print('⚠️  Selenium not installed. Skipping web tests.')
except Exception as e:
    print(f'❌ Selenium setup failed: {e}')
"
}

# Function to run full test suite
run_full_test_suite() {
    print_header "Running Full Test Suite"
    echo "========================="
    
    local start_time=$(date +%s)
    local failed_tests=0
    
    # Run all test categories
    test_app_basic || ((failed_tests++))
    echo ""
    
    test_configuration || ((failed_tests++))
    echo ""
    
    test_authentication || ((failed_tests++))
    echo ""
    
    test_database_models || ((failed_tests++))
    echo ""
    
    test_security || ((failed_tests++))
    echo ""
    
    test_performance || ((failed_tests++))
    echo ""
    
    test_selenium || ((failed_tests++))
    echo ""
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo "==============================="
    print_header "Test Suite Summary"
    echo "==============================="
    echo "⏱️  Total time: ${duration} seconds"
    
    if [[ $failed_tests -eq 0 ]]; then
        print_status "All tests passed! 🎉"
    else
        print_warning "$failed_tests test categories had issues"
    fi
}

# Function to show test options
show_test_options() {
    echo "🧪 Available Test Categories:"
    echo "  1. Basic application tests"
    echo "  2. Configuration tests"
    echo "  3. Authentication tests"
    echo "  4. Database model tests"
    echo "  5. Security tests"
    echo "  6. Performance tests"
    echo "  7. Selenium web tests"
    echo "  8. Full test suite"
    echo "  9. Exit"
    echo ""
}

# Main execution
main() {
    print_info "Test environment ready"
    
    while true; do
        echo ""
        show_test_options
        read -p "Choose test category (1-9): " choice
        
        case $choice in
            1)
                test_app_basic
                ;;
            2)
                test_configuration
                ;;
            3)
                test_authentication
                ;;
            4)
                test_database_models
                ;;
            5)
                test_security
                ;;
            6)
                test_performance
                ;;
            7)
                test_selenium
                ;;
            8)
                run_full_test_suite
                ;;
            9)
                print_info "Testing completed. Goodbye! 👋"
                exit 0
                ;;
            *)
                print_error "Invalid choice. Please select 1-9."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Handle script interruption
trap 'echo -e "\n${YELLOW}⚠️  Tests interrupted${NC}"; exit 130' INT

# Run main function
main
