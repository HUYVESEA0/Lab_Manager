#!/bin/bash
# Lab Manager - macOS Setup Script
# Complete setup script for macOS development environment

set -e  # Exit on any error

echo "🍎 Lab Manager - macOS Setup Script"
echo "==================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS only!"
    exit 1
fi

print_status "Detected macOS system"

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    print_warning "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for M1/M2 Macs
    if [[ $(uname -m) == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi
else
    print_status "Homebrew is already installed"
fi

# Update Homebrew
print_info "Updating Homebrew..."
brew update

# Check and install Python 3.8+
if ! command -v python3 &> /dev/null; then
    print_warning "Python3 not found. Installing Python..."
    brew install python@3.11
else
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [[ $PYTHON_MAJOR -ge 3 && $PYTHON_MINOR -ge 8 ]]; then
        print_status "Python $PYTHON_VERSION is compatible"
    else
        print_warning "Python $PYTHON_VERSION is too old. Installing Python 3.11..."
        brew install python@3.11
    fi
fi

# Install additional dependencies
print_info "Installing system dependencies..."
brew install postgresql redis git

# Install Chrome for Selenium testing (if not already installed)
if ! command -v google-chrome &> /dev/null && ! ls /Applications/Google\ Chrome.app &> /dev/null; then
    print_warning "Google Chrome not found. Installing Chrome for Selenium testing..."
    brew install --cask google-chrome
else
    print_status "Google Chrome is available for Selenium testing"
fi

# Create project directory structure
print_info "Setting up project environment..."

# Check if we're in the Lab_Manager directory
if [[ ! -f "requirements.txt" ]] || [[ ! -f "run.py" ]]; then
    print_error "Please run this script from the Lab_Manager project directory"
    exit 1
fi

# Create virtual environment
print_info "Creating Python virtual environment..."
if [[ -d "venv" ]]; then
    print_warning "Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

python3 -m venv venv
print_status "Virtual environment created"

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_info "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [[ ! -f ".env" ]]; then
    print_info "Creating .env configuration file..."
    cat > .env << 'EOF'
# Flask Configuration
FLASK_APP=run.py
FLASK_DEBUG=1
SECRET_KEY=lab-manager-development-secret-key-change-in-production-2025

# Database Configuration
DATABASE_URL=sqlite:///app.db

# CSRF Configuration
WTF_CSRF_ENABLED=true
WTF_CSRF_TIME_LIMIT=3600

# Email Configuration (Gmail example)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@labmanager.com

# Session Configuration
PERMANENT_SESSION_LIFETIME=1800

# Cache Configuration
CACHE_TYPE=simple
CACHE_DEFAULT_TIMEOUT=300

# User Accounts (for initial setup)
SYSTEM_ADMIN_USERNAME=HUYVIESEA
SYSTEM_ADMIN_EMAIL=hhuy0847@gmail.com
SYSTEM_ADMIN_PASSWORD=huyviesea@manager

ADMIN_USERNAME=ADMIN
ADMIN_EMAIL=hhuy08@gmail.com
ADMIN_PASSWORD=huyviesea@admin

USER_USERNAME=USER
USER_EMAIL=hhuy084@gmail.com
USER_PASSWORD=huyviesea@user

# Redis Configuration (optional)
# REDIS_HOST=localhost
# REDIS_PORT=6379
# REDIS_DB=0
EOF
    print_status "Created .env file with default configuration"
    print_warning "Please update .env file with your actual email credentials"
else
    print_status ".env file already exists"
fi

# Initialize database
print_info "Initializing database..."
export FLASK_APP=run.py
flask db upgrade 2>/dev/null || (
    print_info "Creating initial migration..."
    flask db init
    flask db migrate -m "Initial migration"
    flask db upgrade
)

# Create initial users
print_info "Creating initial users..."
python app/init_users.py

# Set up Git hooks (optional)
if [[ -d ".git" ]]; then
    print_info "Setting up Git hooks..."
    # Create pre-commit hook for code quality
    mkdir -p .git/hooks
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook for Lab Manager

echo "Running pre-commit checks..."

# Check Python syntax
python -m py_compile app/*.py
if [[ $? -ne 0 ]]; then
    echo "Python syntax errors found!"
    exit 1
fi

# Check for secrets in .env
if git diff --cached --name-only | grep -q ".env"; then
    echo "Warning: .env file is being committed!"
    echo "Make sure no secrets are included."
fi

echo "Pre-commit checks passed!"
EOF
    chmod +x .git/hooks/pre-commit
    print_status "Git hooks configured"
fi

# Create launch configuration for VS Code
if command -v code &> /dev/null; then
    print_info "Creating VS Code configuration..."
    mkdir -p .vscode
    
    cat > .vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Flask",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/run.py",
            "env": {
                "FLASK_APP": "run.py",
                "FLASK_DEBUG": "1"
            },
            "args": [],
            "jinja": true,
            "justMyCode": true
        }
    ]
}
EOF

    cat > .vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "venv/": true,
        "instance/": true
    }
}
EOF
    print_status "VS Code configuration created"
fi

# Final status check
print_info "Running system health check..."
source venv/bin/activate
python -c "
import sys
print(f'Python version: {sys.version}')
import flask
print(f'Flask version: {flask.__version__}')
try:
    from app import create_app
    app, socketio = create_app()
    print('✅ App creation successful')
except Exception as e:
    print(f'❌ App creation failed: {e}')
"

echo ""
echo "🎉 Setup completed successfully!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Update .env file with your email credentials"
echo "3. Start the application: ./run_mac.sh"
echo ""
echo "Available commands:"
echo "- ./run_mac.sh          - Start the application"
echo "- ./test_mac.sh         - Run tests"
echo "- source venv/bin/activate - Activate virtual environment"
echo ""
echo "📚 Documentation: README.md"
echo "🐛 Issues: Check the logs/ directory"
echo ""
print_status "Happy coding! 🚀"
