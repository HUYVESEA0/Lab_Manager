# Lab Manager - macOS Setup Guide

🍎 **Complete macOS development environment for Lab Manager Flask application**

This guide provides macOS-specific scripts and instructions for setting up, running, and managing the Lab Manager application on Apple Silicon (M1/M2) and Intel Macs.

## 📋 Quick Start

### Prerequisites
- macOS 10.15+ (Catalina or later)
- Xcode Command Line Tools
- Internet connection

### One-Command Setup
```bash
# Clone and setup everything
git clone <your-repo-url> Lab_Manager
cd Lab_Manager
./setup_mac.sh
```

## 🛠️ Available Scripts

### 1. `setup_mac.sh` - Complete Environment Setup
**Full system setup and configuration**

```bash
./setup_mac.sh
```

**What it does:**
- ✅ Installs Homebrew (if not present)
- ✅ Installs Python 3.11+ and system dependencies
- ✅ Creates virtual environment
- ✅ Installs all Python packages
- ✅ Sets up database
- ✅ Creates sample users
- ✅ Configures VS Code settings
- ✅ Sets up Git hooks

**Features:**
- 🔧 Automatic M1/M2 Mac compatibility
- 🔍 System requirements validation
- 📝 Creates default `.env` configuration
- 🎨 VS Code launch configurations
- 🔒 Pre-commit hooks for code quality

### 2. `run_mac.sh` - Application Runner
**Smart application launcher with health checks**

```bash
./run_mac.sh
```

**Run modes:**
1. **Standard** - Full health checks + Flask app
2. **Quick** - Minimal checks, fast startup
3. **Debug** - Verbose logging enabled
4. **Production** - Optimized with Gunicorn
5. **Routes** - Show all application endpoints
6. **Database** - Database management tools
7. **Tests** - Run test suite

**Features:**
- 🏥 System health monitoring
- 🔄 Automatic Redis/PostgreSQL detection
- 📊 Real-time service status
- 🎯 Interactive menu system

### 3. `venv_mac.sh` - Virtual Environment Manager
**Advanced virtual environment management**

```bash
./venv_mac.sh
```

**Capabilities:**
1. **Status** - Check environment health
2. **Create** - Build new virtual environment
3. **Install** - Install/update dependencies
4. **Health Check** - Validate installation
5. **Dependencies** - View/update packages
6. **Cleanup** - Remove cache/temp files

**Features:**
- 📦 Dependency version management
- 🔍 Package conflict detection
- 🧹 Intelligent cleanup options
- 📊 Environment health reporting

### 4. `test_mac.sh` - Test Suite Runner
**Comprehensive testing framework**

```bash
./test_mac.sh
```

**Test Categories:**
1. **Basic** - App creation and imports
2. **Configuration** - Environment validation
3. **Authentication** - User/session testing
4. **Database** - Model and migration tests
5. **Security** - CSRF and session security
6. **Performance** - Startup and query timing
7. **Selenium** - Web interface testing (requires Chrome)
8. **Full Suite** - All tests with reporting

## 🔧 System Requirements

### Minimum Requirements
- **OS**: macOS 10.15+ (Catalina)
- **RAM**: 4GB (8GB recommended)
- **Storage**: 2GB free space
- **Python**: 3.8+ (auto-installed)

### Recommended Setup
- **OS**: macOS 12+ (Monterey)
- **RAM**: 8GB+
- **Storage**: 5GB free space
- **Python**: 3.11+ (default installation)
- **Browser**: Chrome (for Selenium testing)

## 📁 Directory Structure

```
Lab_Manager/
├── 🍎 macOS Scripts
│   ├── setup_mac.sh      # Complete setup
│   ├── run_mac.sh        # Application runner
│   ├── venv_mac.sh       # Environment manager
│   └── test_mac.sh       # Test suite
├── 📱 Application
│   ├── app/              # Flask application
│   ├── config.py         # Configuration
│   ├── run.py           # Main runner
│   └── requirements.txt  # Dependencies
├── 🗄️ Data
│   ├── instance/         # SQLite database
│   ├── logs/            # Application logs
│   └── migrations/      # Database migrations
└── 🔧 Environment
    ├── venv/            # Virtual environment
    ├── .env             # Environment variables
    └── .vscode/         # VS Code settings
```

## 🚀 Usage Examples

### First-Time Setup
```bash
# Complete setup from scratch
./setup_mac.sh

# Activate environment
source venv/bin/activate

# Start application
./run_mac.sh
```

### Daily Development
```bash
# Quick start
./run_mac.sh
# Choose option 2 (Quick start)

# Run tests
./test_mac.sh
# Choose option 8 (Full suite)

# Manage dependencies
./venv_mac.sh
# Choose option 4 (Show dependencies)
```

### Database Management
```bash
# Access database tools
./run_mac.sh
# Choose option 6 (Database operations)

# Available operations:
# - Show status
# - Create migrations
# - Apply migrations
# - Initialize sample data
# - Reset database
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Flask Configuration
FLASK_APP=run.py
FLASK_DEBUG=1
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///app.db

# Email (Gmail example)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Users (for initial setup)
SYSTEM_ADMIN_USERNAME=HUYVIESEA
SYSTEM_ADMIN_EMAIL=admin@example.com
SYSTEM_ADMIN_PASSWORD=secure-password
```

### VS Code Integration
The setup automatically creates:
- **Launch configuration** for debugging
- **Python interpreter** settings
- **Linting and formatting** setup
- **File exclusions** for cleaner workspace

## 🧪 Testing

### Automated Tests
```bash
# Run all tests
./test_mac.sh

# Specific test categories
./test_mac.sh
# 1. Basic application tests
# 2. Configuration tests
# 3. Authentication tests
# 4. Database model tests
# 5. Security tests
# 6. Performance tests
# 7. Selenium web tests
```

### Manual Testing
```bash
# Start test server
./run_mac.sh
# Choose option 3 (Debug mode)

# Access application
open http://127.0.0.1:5000
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Homebrew Installation
```bash
# If Homebrew fails to install
xcode-select --install
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. Python Version Issues
```bash
# Install specific Python version
brew install python@3.11
# Update PATH if needed
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
```

#### 3. Virtual Environment Problems
```bash
# Reset virtual environment
./venv_mac.sh
# Choose option 9 (Clean environment)
# Then option 1 (Remove virtual environment)
# Then option 2 (Create virtual environment)
```

#### 4. Database Issues
```bash
# Reset database
./run_mac.sh
# Choose option 6 (Database operations)
# Choose option 5 (Reset database)
```

#### 5. Permission Errors
```bash
# Fix script permissions
chmod +x *.sh

# Fix Homebrew permissions (if needed)
sudo chown -R $(whoami) /opt/homebrew
```

### Getting Help

#### Check System Status
```bash
# Environment health check
./venv_mac.sh
# Choose option 7 (Health check)

# Application diagnostics
./run_mac.sh
# Choose option 1 (Standard run with health checks)
```

#### Log Files
```bash
# View application logs
tail -f logs/app.log

# View error logs
tail -f logs/error.log
```

#### Debug Mode
```bash
# Run with maximum verbosity
export FLASK_DEBUG=1
./run_mac.sh
# Choose option 3 (Debug mode)
```

## 🔄 Updates and Maintenance

### Update Dependencies
```bash
# Check for updates
./venv_mac.sh
# Choose option 5 (Update dependencies)

# Update system packages
brew update && brew upgrade
```

### Update Application
```bash
# Pull latest changes
git pull origin main

# Update dependencies
./venv_mac.sh
# Choose option 3 (Install dependencies)

# Apply database migrations
./run_mac.sh
# Choose option 6 → option 3 (Apply migrations)
```

## 📊 Performance Optimization

### Development Mode
- Uses SQLite for faster development
- Single-threaded for easier debugging
- Hot reload enabled

### Production Mode
```bash
# Run in production mode
./run_mac.sh
# Choose option 4 (Production mode)

# Features:
# - Gunicorn multi-worker setup
# - Optimized database connections
# - Redis caching (if available)
# - Compressed static files
```

## 🔐 Security Considerations

### Development Security
- CSRF protection enabled by default
- Secure session configuration
- Environment variable isolation
- Git hooks prevent secret commits

### Production Security
- Strong SECRET_KEY generation
- Database connection encryption
- Session timeout configuration
- HTTPS redirection (when deployed)

## 📚 Additional Resources

### Flask Documentation
- [Flask Official Docs](https://flask.palletsprojects.com/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
- [Flask-Login](https://flask-login.readthedocs.io/)

### macOS Development
- [Homebrew Documentation](https://docs.brew.sh/)
- [Python on macOS](https://docs.python.org/3/using/mac.html)
- [VS Code on macOS](https://code.visualstudio.com/docs/setup/mac)

### Testing Resources
- [pytest Documentation](https://docs.pytest.org/)
- [Selenium WebDriver](https://selenium-python.readthedocs.io/)

---

## 🎉 Quick Reference

```bash
# Setup everything
./setup_mac.sh

# Run application
./run_mac.sh

# Manage environment
./venv_mac.sh

# Run tests
./test_mac.sh

# Activate environment manually
source venv/bin/activate

# Access application
open http://127.0.0.1:5000
```

**Happy coding on macOS! 🍎🚀**
