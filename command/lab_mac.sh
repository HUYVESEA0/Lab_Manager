#!/bin/bash
# Lab Manager - macOS Main Launcher
# Central hub for all macOS Lab Manager operations

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_header() {
    echo -e "${PURPLE}🍎 $1${NC}"
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script is designed for macOS only!"
    exit 1
fi

print_header "Lab Manager - macOS Control Center"
echo "=================================="

# Check if we're in the correct directory
if [[ ! -f "requirements.txt" ]]; then
    echo "❌ Please run this script from the Lab_Manager project directory"
    exit 1
fi

# Display current status
echo ""
print_info "Project Status:"

# Check virtual environment
if [[ -d "venv" ]]; then
    print_status "Virtual environment: Ready"
else
    echo "⚠️  Virtual environment: Not found"
fi

# Check .env file
if [[ -f ".env" ]]; then
    print_status "Configuration: Ready"
else
    echo "⚠️  Configuration: .env file missing"
fi

# Check database
if [[ -f "instance/app.db" ]]; then
    print_status "Database: Ready"
else
    echo "⚠️  Database: Not initialized"
fi

echo ""
echo "🚀 Available Operations:"
echo "  1. 🛠️  Complete Setup (first-time installation)"
echo "  2. ▶️  Run Application (start Lab Manager)"
echo "  3. 🔧 Manage Environment (virtual env & dependencies)"
echo "  4. 🧪 Run Tests (comprehensive test suite)"
echo "  5. 📚 View Documentation (open README)"
echo "  6. 🔍 System Check (health diagnostics)"
echo "  7. ❓ Help & Troubleshooting"
echo "  8. 🚪 Exit"
echo ""

read -p "Choose operation (1-8): " choice

case $choice in
    1)
        print_info "Starting complete setup..."
        if [[ -x "setup_mac.sh" ]]; then
            ./setup_mac.sh
        else
            echo "❌ setup_mac.sh not found or not executable"
        fi
        ;;
    2)
        print_info "Starting application..."
        if [[ -x "run_mac.sh" ]]; then
            ./run_mac.sh
        else
            echo "❌ run_mac.sh not found or not executable"
        fi
        ;;
    3)
        print_info "Opening environment manager..."
        if [[ -x "venv_mac.sh" ]]; then
            ./venv_mac.sh
        else
            echo "❌ venv_mac.sh not found or not executable"
        fi
        ;;
    4)
        print_info "Starting test suite..."
        if [[ -x "test_mac.sh" ]]; then
            ./test_mac.sh
        else
            echo "❌ test_mac.sh not found or not executable"
        fi
        ;;
    5)
        print_info "Opening documentation..."
        if command -v open &> /dev/null; then
            if [[ -f "README_macOS.md" ]]; then
                open README_macOS.md
            else
                open README.md
            fi
        else
            echo "📚 Documentation files:"
            ls -la README*.md 2>/dev/null || echo "No README files found"
        fi
        ;;
    6)
        print_info "Running system diagnostics..."
        echo ""
        echo "🔍 System Information:"
        echo "  OS: $(uname -s) $(uname -r)"
        echo "  Architecture: $(uname -m)"
        echo "  Python: $(python3 --version 2>&1 || echo 'Not found')"
        echo "  Homebrew: $(brew --version 2>&1 | head -1 || echo 'Not found')"
        echo ""
        echo "📁 Project Structure:"
        echo "  Virtual env: $([ -d venv ] && echo 'Present' || echo 'Missing')"
        echo "  Configuration: $([ -f .env ] && echo 'Present' || echo 'Missing')"
        echo "  Database: $([ -f instance/app.db ] && echo 'Present' || echo 'Missing')"
        echo "  Scripts: $(ls -1 *_mac.sh 2>/dev/null | wc -l | tr -d ' ') macOS scripts found"
        ;;
    7)
        print_info "Help & Troubleshooting"
        echo ""
        echo "🆘 Common Issues & Solutions:"
        echo ""
        echo "1. 'Permission denied' when running scripts:"
        echo "   Solution: chmod +x *.sh"
        echo ""
        echo "2. Python not found:"
        echo "   Solution: brew install python@3.11"
        echo ""
        echo "3. Virtual environment issues:"
        echo "   Solution: rm -rf venv && python3 -m venv venv"
        echo ""
        echo "4. Database errors:"
        echo "   Solution: rm instance/app.db && flask db upgrade"
        echo ""
        echo "5. Homebrew issues on M1/M2 Macs:"
        echo "   Solution: eval \"\$(/opt/homebrew/bin/brew shellenv)\""
        echo ""
        echo "📖 For detailed help, see README_macOS.md"
        ;;
    8)
        print_info "Goodbye! 👋"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please select 1-8."
        ;;
esac

echo ""
print_info "Operation completed. Run './lab_mac.sh' to return to main menu."
