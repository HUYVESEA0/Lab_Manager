#!/bin/bash
# Lab Manager - macOS Virtual Environment Manager
# Advanced virtual environment management for macOS

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

print_command() {
    echo -e "${CYAN}💻 $1${NC}"
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS only!"
    exit 1
fi

print_header "Lab Manager - Virtual Environment Manager"
echo "========================================"

# Check if we're in the correct directory
if [[ ! -f "requirements.txt" ]]; then
    print_error "Please run this script from the Lab_Manager project directory"
    exit 1
fi

# Function to check Python installation
check_python() {
    print_info "Checking Python installation..."
    
    # Check for Python 3
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [[ $PYTHON_MAJOR -ge 3 && $PYTHON_MINOR -ge 8 ]]; then
            print_status "Python $PYTHON_VERSION is compatible"
            PYTHON_CMD="python3"
        else
            print_error "Python $PYTHON_VERSION is too old. Python 3.8+ required"
            exit 1
        fi
    else
        print_error "Python 3 not found. Please install Python 3.8+ first"
        echo "Install with: brew install python@3.11"
        exit 1
    fi
}

# Function to show virtual environment status
show_venv_status() {
    print_info "Virtual Environment Status:"
    
    if [[ -d "venv" ]]; then
        echo "  📁 Location: $(pwd)/venv"
        if [[ -f "venv/bin/python" ]]; then
            VENV_PYTHON_VERSION=$(venv/bin/python --version 2>&1 | cut -d' ' -f2)
            echo "  🐍 Python Version: $VENV_PYTHON_VERSION"
            print_status "Virtual environment exists and is functional"
            
            # Check if currently activated
            if [[ "$VIRTUAL_ENV" == "$(pwd)/venv" ]]; then
                print_status "Virtual environment is currently ACTIVATED"
            else
                print_warning "Virtual environment exists but is NOT activated"
            fi
        else
            print_error "Virtual environment appears corrupted"
        fi
    else
        print_warning "Virtual environment does not exist"
    fi
    echo ""
}

# Function to create virtual environment
create_venv() {
    print_info "Creating new virtual environment..."
    
    # Remove existing venv if it exists
    if [[ -d "venv" ]]; then
        print_warning "Removing existing virtual environment..."
        rm -rf venv
    fi
    
    # Create new virtual environment
    $PYTHON_CMD -m venv venv
    
    if [[ -d "venv" && -f "venv/bin/python" ]]; then
        print_status "Virtual environment created successfully"
        
        # Activate and upgrade pip
        source venv/bin/activate
        print_info "Upgrading pip..."
        pip install --upgrade pip
        
        print_status "Virtual environment is ready"
    else
        print_error "Failed to create virtual environment"
        exit 1
    fi
}

# Function to install dependencies
install_dependencies() {
    print_info "Installing project dependencies..."
    
    if [[ ! -d "venv" ]]; then
        print_error "Virtual environment not found. Create it first."
        return 1
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip first
    print_info "Upgrading pip..."
    pip install --upgrade pip
    
    # Install requirements
    if [[ -f "requirements.txt" ]]; then
        print_info "Installing from requirements.txt..."
        pip install -r requirements.txt
        print_status "Dependencies installed successfully"
    else
        print_error "requirements.txt not found"
        return 1
    fi
    
    # Show installed packages
    print_info "Installed packages:"
    pip list --format=columns | head -20
    
    if [[ $(pip list | wc -l) -gt 20 ]]; then
        echo "... and $(( $(pip list | wc -l) - 20 )) more packages"
    fi
}

# Function to show dependency information
show_dependencies() {
    if [[ ! -d "venv" ]]; then
        print_error "Virtual environment not found"
        return 1
    fi
    
    source venv/bin/activate
    
    print_info "Dependency Information:"
    echo ""
    
    echo "📦 Core Flask Dependencies:"
    pip show flask flask-sqlalchemy flask-login flask-wtf 2>/dev/null | grep -E "Name:|Version:" | paste - -
    
    echo ""
    echo "📊 All Installed Packages:"
    pip list --format=columns
    
    echo ""
    echo "🔍 Outdated Packages:"
    pip list --outdated --format=columns || print_info "All packages are up to date"
}

# Function to update dependencies
update_dependencies() {
    if [[ ! -d "venv" ]]; then
        print_error "Virtual environment not found"
        return 1
    fi
    
    source venv/bin/activate
    
    print_info "Checking for updates..."
    
    # Show outdated packages
    OUTDATED=$(pip list --outdated --format=freeze 2>/dev/null | wc -l)
    
    if [[ $OUTDATED -gt 0 ]]; then
        print_warning "Found $OUTDATED outdated packages"
        pip list --outdated --format=columns
        
        echo ""
        read -p "Update all packages? (y/N): " confirm
        
        if [[ $confirm == "y" || $confirm == "Y" ]]; then
            print_info "Updating packages..."
            pip list --outdated --format=freeze | cut -d= -f1 | xargs -n1 pip install -U
            print_status "Packages updated"
            
            # Update requirements.txt
            read -p "Update requirements.txt? (y/N): " update_req
            if [[ $update_req == "y" || $update_req == "Y" ]]; then
                pip freeze > requirements.txt
                print_status "requirements.txt updated"
            fi
        fi
    else
        print_status "All packages are up to date"
    fi
}

# Function to activate virtual environment
activate_venv() {
    if [[ ! -d "venv" ]]; then
        print_error "Virtual environment not found. Create it first."
        return 1
    fi
    
    if [[ "$VIRTUAL_ENV" == "$(pwd)/venv" ]]; then
        print_status "Virtual environment is already activated"
    else
        print_info "To activate the virtual environment, run:"
        print_command "source venv/bin/activate"
        echo ""
        print_info "To deactivate later, run:"
        print_command "deactivate"
    fi
}

# Function to run environment health check
health_check() {
    print_info "Running environment health check..."
    
    if [[ ! -d "venv" ]]; then
        print_error "Virtual environment not found"
        return 1
    fi
    
    source venv/bin/activate
    
    # Check Python version
    VENV_PYTHON_VERSION=$(python --version 2>&1 | cut -d' ' -f2)
    print_status "Python version: $VENV_PYTHON_VERSION"
    
    # Check critical packages
    CRITICAL_PACKAGES=("flask" "flask-sqlalchemy" "flask-login" "flask-wtf")
    
    for package in "${CRITICAL_PACKAGES[@]}"; do
        if pip show "$package" &>/dev/null; then
            VERSION=$(pip show "$package" | grep Version | cut -d' ' -f2)
            print_status "$package $VERSION"
        else
            print_error "$package not installed"
        fi
    done
    
    # Test app creation
    print_info "Testing application creation..."
    python -c "
try:
    from app import create_app
    app, socketio = create_app()
    print('✅ Application creation test passed')
except Exception as e:
    print(f'❌ Application creation failed: {e}')
"
    
    print_status "Health check completed"
}

# Function to show environment information
show_env_info() {
    print_info "Environment Information:"
    echo "  🖥️  OS: $(uname -s) $(uname -r)"
    echo "  🏗️  Architecture: $(uname -m)"
    echo "  🐍 System Python: $(python3 --version 2>&1 | cut -d' ' -f2)"
    
    if [[ -d "venv" ]]; then
        source venv/bin/activate 2>/dev/null
        echo "  📦 Virtual Env Python: $(python --version 2>&1 | cut -d' ' -f2)"
        echo "  📁 Virtual Env Path: $VIRTUAL_ENV"
        echo "  📊 Installed Packages: $(pip list | wc -l | tr -d ' ')"
    fi
    
    echo "  💾 Available Disk Space: $(df -h . | tail -1 | awk '{print $4}')"
    echo ""
}

# Function to clean environment
clean_environment() {
    print_warning "Environment Cleanup Options:"
    echo "  1. Remove virtual environment"
    echo "  2. Clear Python cache files"
    echo "  3. Remove log files"
    echo "  4. Full cleanup (all above)"
    echo "  5. Cancel"
    echo ""
    
    read -p "Choose cleanup option (1-5): " clean_choice
    
    case $clean_choice in
        1)
            if [[ -d "venv" ]]; then
                rm -rf venv
                print_status "Virtual environment removed"
            else
                print_info "No virtual environment to remove"
            fi
            ;;
        2)
            find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
            find . -name "*.pyc" -delete 2>/dev/null || true
            print_status "Python cache files removed"
            ;;
        3)
            if [[ -d "logs" ]]; then
                rm -rf logs/*
                print_status "Log files removed"
            else
                print_info "No log files to remove"
            fi
            ;;
        4)
            if [[ -d "venv" ]]; then rm -rf venv; fi
            find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
            find . -name "*.pyc" -delete 2>/dev/null || true
            if [[ -d "logs" ]]; then rm -rf logs/*; fi
            print_status "Full cleanup completed"
            ;;
        5)
            print_info "Cleanup cancelled"
            ;;
        *)
            print_error "Invalid choice"
            ;;
    esac
}

# Function to show available options
show_options() {
    echo "🔧 Virtual Environment Management Options:"
    echo "  1. Show environment status"
    echo "  2. Create virtual environment"
    echo "  3. Install dependencies"
    echo "  4. Show dependencies"
    echo "  5. Update dependencies"
    echo "  6. Activate environment (instructions)"
    echo "  7. Health check"
    echo "  8. Environment information"
    echo "  9. Clean environment"
    echo "  10. Exit"
    echo ""
}

# Main execution
main() {
    check_python
    
    while true; do
        echo ""
        show_venv_status
        show_options
        read -p "Choose an option (1-10): " choice
        
        case $choice in
            1)
                show_venv_status
                ;;
            2)
                create_venv
                ;;
            3)
                install_dependencies
                ;;
            4)
                show_dependencies
                ;;
            5)
                update_dependencies
                ;;
            6)
                activate_venv
                ;;
            7)
                health_check
                ;;
            8)
                show_env_info
                ;;
            9)
                clean_environment
                ;;
            10)
                print_info "Goodbye! 👋"
                exit 0
                ;;
            *)
                print_error "Invalid choice. Please select 1-10."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Run main function
main
