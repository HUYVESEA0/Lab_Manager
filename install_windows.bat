@echo off
echo ===============================================
echo Lab Manager - Windows Installation Fix
echo ===============================================
echo.

echo Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python not found! Please install Python 3.8+ first.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo.

echo Upgrading pip...
python -m pip install --upgrade pip
echo.

echo ===============================================
echo Method 1: Installing with binary wheels only
echo ===============================================
python -m pip install --only-binary=:all: --upgrade setuptools wheel
python -m pip install --only-binary=lxml lxml
if %errorlevel% equ 0 (
    echo Success! Installing remaining requirements...
    python -m pip install -r requirements.txt
    if %errorlevel% equ 0 goto :success
)

echo.
echo ===============================================
echo Method 2: Installing safe requirements
echo ===============================================
python -m pip install -r requirements_safe.txt
if %errorlevel% equ 0 goto :success

echo.
echo ===============================================
echo Method 3: Installing minimal requirements
echo ===============================================
python -m pip install Flask Flask-SQLAlchemy Flask-Login Flask-WTF
python -m pip install python-dotenv requests
if %errorlevel% equ 0 goto :minimal_success

echo.
echo ===============================================
echo All methods failed!
echo ===============================================
echo.
echo You need to install Microsoft Visual C++ Build Tools:
echo 1. Go to: https://visualstudio.microsoft.com/visual-cpp-build-tools/
echo 2. Download "Build Tools for Visual Studio 2022"
echo 3. Install with "C++ build tools" workload
echo 4. Restart your computer
echo 5. Run this script again
echo.
goto :end

:minimal_success
echo.
echo ===============================================
echo Minimal installation completed!
echo ===============================================
echo.
echo Some advanced features may not work, but basic functionality should be available.
echo You can try to install additional packages later.
goto :run_app

:success
echo.
echo ===============================================
echo Installation completed successfully!
echo ===============================================
echo.

:run_app
echo Setting up database...
python -c "
try:
    from app import create_app
    from app.models import db
    app, socketio = create_app()
    with app.app_context():
        db.create_all()
        print('Database created successfully!')
except Exception as e:
    print(f'Database setup error: {e}')
    print('You may need to run: python -c \"from app.models import db; db.create_all()\"')
"
echo.

echo Starting Lab Manager...
echo You can access the application at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
python run.py

:end
pause
