#!/bin/bash
# Lab Manager - macOS Run Script
# Optimized startup script for macOS with comprehensive system checks

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS only!"
    exit 1
fi

print_header "Lab Manager - macOS Application Runner"
echo "====================================="

# Check if we're in the correct directory
if [[ ! -f "run.py" ]] || [[ ! -f "requirements.txt" ]]; then
    print_error "Please run this script from the Lab_Manager project directory"
    exit 1
fi

# Function to check system requirements
check_system_requirements() {
    print_info "Checking system requirements..."
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_status "Python $PYTHON_VERSION detected"
    else
        print_error "Python 3 not found. Please run setup_mac.sh first"
        exit 1
    fi
    
    # Check virtual environment
    if [[ ! -d "venv" ]]; then
        print_error "Virtual environment not found. Please run setup_mac.sh first"
        exit 1
    fi
    
    print_status "System requirements check passed"
}

# Function to activate virtual environment
activate_venv() {
    print_info "Activating virtual environment..."
    source venv/bin/activate
    
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_status "Virtual environment activated: $(basename $VIRTUAL_ENV)"
    else
        print_error "Failed to activate virtual environment"
        exit 1
    fi
}

# Function to check environment variables
check_environment() {
    print_info "Checking environment configuration..."
    
    # Check for .env file
    if [[ ! -f ".env" ]]; then
        print_warning ".env file not found. Creating default configuration..."
        cp .env.example .env 2>/dev/null || cat > .env << 'EOF'
FLASK_APP=run.py
FLASK_DEBUG=1
SECRET_KEY=lab-manager-development-secret-key-change-in-production-2025
DATABASE_URL=sqlite:///app.db
EOF
    fi
    
    # Load environment variables
    export FLASK_APP=run.py
    export FLASK_DEBUG=1
    
    print_status "Environment configuration loaded"
}

# Function to check database health
check_database() {
    print_info "Checking database health..."
    
    python3 -c "
try:
    from app import create_app
    app, _ = create_app()
    with app.app_context():
        from app.models import db
        # Simple database connection test
        db.engine.connect()
        print('✅ Database connection successful')
except Exception as e:
    print(f'⚠️  Database issue: {e}')
    print('💡 Tip: Run flask db upgrade to update database schema')
" 2>/dev/null
}

# Function to check required services
check_services() {
    print_info "Checking optional services..."
    
    # Check Redis (optional)
    if command -v redis-server &> /dev/null; then
        if pgrep redis-server &> /dev/null; then
            print_status "Redis is running"
        else
            print_info "Starting Redis server..."
            brew services start redis 2>/dev/null || print_warning "Could not start Redis automatically"
        fi
    else
        print_warning "Redis not installed (optional for clustering)"
    fi
    
    # Check PostgreSQL (optional)
    if command -v postgres &> /dev/null; then
        if brew services list | grep postgresql | grep started &> /dev/null; then
            print_status "PostgreSQL is running"
        else
            print_info "PostgreSQL available but not running"
        fi
    fi
}

# Function to show application info
show_app_info() {
    print_info "Application Information:"
    echo "  📁 Project: Lab Manager"
    echo "  🌐 Framework: Flask"
    echo "  🐍 Python: $(python3 --version | cut -d' ' -f2)"
    echo "  📦 Virtual Env: $(basename $VIRTUAL_ENV)"
    echo "  🗄️  Database: SQLite (default)"
    echo "  🔧 Mode: Development"
    echo ""
}

# Function to display available options
show_options() {
    echo "🚀 Available startup options:"
    echo "  1. Standard run (with health checks)"
    echo "  2. Quick start (minimal checks)"
    echo "  3. Debug mode (verbose logging)"
    echo "  4. Production mode (optimized)"
    echo "  5. Show routes"
    echo "  6. Database operations"
    echo "  7. Run tests"
    echo "  8. Exit"
    echo ""
}

# Function to run database operations
database_operations() {
    echo ""
    print_info "Database Operations:"
    echo "  1. Show database status"
    echo "  2. Create migration"
    echo "  3. Apply migrations"
    echo "  4. Initialize sample data"
    echo "  5. Reset database"
    echo "  6. Back to main menu"
    echo ""
    
    read -p "Choose database operation (1-6): " db_choice
    
    case $db_choice in
        1)
            print_info "Database Status:"
            python3 -c "
from app import create_app
app, _ = create_app()
with app.app_context():
    from app.models import db, NguoiDung
    try:
        user_count = NguoiDung.query.count()
        print(f'✅ Database connected - {user_count} users in system')
    except Exception as e:
        print(f'❌ Database error: {e}')
"
            ;;
        2)
            read -p "Enter migration message: " message
            flask db migrate -m "$message"
            ;;
        3)
            flask db upgrade
            print_status "Migrations applied"
            ;;
        4)
            python3 app/init_users.py
            print_status "Sample data initialized"
            ;;
        5)
            read -p "Are you sure you want to reset the database? (y/N): " confirm
            if [[ $confirm == "y" || $confirm == "Y" ]]; then
                rm -f instance/app.db
                flask db upgrade
                python3 app/init_users.py
                print_status "Database reset complete"
            fi
            ;;
        6)
            return
            ;;
        *)
            print_error "Invalid choice"
            ;;
    esac
    
    read -p "Press Enter to continue..."
}

# Function to run tests
run_tests() {
    print_info "Running test suite..."
    
    # Check if pytest is available
    if python3 -c "import pytest" 2>/dev/null; then
        python3 -m pytest test/ -v --tb=short
    else
        print_warning "pytest not found. Running basic tests..."
        python3 -c "
from app import create_app
try:
    app, socketio = create_app()
    print('✅ App creation test passed')
    with app.app_context():
        from app.models import db
        db.engine.connect()
        print('✅ Database connection test passed')
    print('✅ Basic tests completed successfully')
except Exception as e:
    print(f'❌ Test failed: {e}')
"
    fi
    
    read -p "Press Enter to continue..."
}

# Function to start the application
start_application() {
    local mode=$1
    
    case $mode in
        "quick")
            print_info "Quick starting application..."
            python3 run.py
            ;;
        "debug")
            print_info "Starting in debug mode..."
            export FLASK_DEBUG=1
            python3 run.py
            ;;
        "production")
            print_info "Starting in production mode..."
            export FLASK_ENV=production
            export FLASK_DEBUG=0
            gunicorn --bind 127.0.0.1:5000 --workers 4 run:app
            ;;
        *)
            print_info "Starting application with health checks..."
            check_database
            check_services
            echo ""
            print_status "All systems ready! Starting Lab Manager..."
            echo ""
            python3 run.py
            ;;
    esac
}

# Main execution
main() {
    check_system_requirements
    activate_venv
    check_environment
    show_app_info
    
    while true; do
        show_options
        read -p "Choose an option (1-8): " choice
        
        case $choice in
            1)
                start_application "standard"
                break
                ;;
            2)
                start_application "quick"
                break
                ;;
            3)
                start_application "debug"
                break
                ;;
            4)
                start_application "production"
                break
                ;;
            5)
                print_info "Available routes:"
                flask routes
                read -p "Press Enter to continue..."
                ;;
            6)
                database_operations
                ;;
            7)
                run_tests
                ;;
            8)
                print_info "Goodbye! 👋"
                exit 0
                ;;
            *)
                print_error "Invalid choice. Please select 1-8."
                ;;
        esac
    done
}

# Handle script interruption
trap 'echo -e "\n${YELLOW}⚠️  Application interrupted${NC}"; exit 130' INT

# Run main function
main

# Cleanup and exit
deactivate 2>/dev/null || true
print_status "Application stopped"
