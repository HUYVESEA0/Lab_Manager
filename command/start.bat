@echo off
REM Lab Manager - Windows Start Script
REM This batch file ensures the Flask application starts correctly on Windows

echo 🚀 Lab Manager - Starting Application
echo ==================================

REM Set Flask environment variables
set FLASK_APP=run.py
set FLASK_DEBUG=1

REM Check if virtual environment is activated
if defined VIRTUAL_ENV (
    echo ✅ Virtual environment active: %VIRTUAL_ENV%
) else (
    echo ⚠️  Warning: No virtual environment detected. Consider using 'venv\Scripts\activate'
)

REM Check if required files exist
if not exist "run.py" (
    echo ❌ Error: run.py not found. Make sure you're in the Lab_Manager directory.
    pause
    exit /b 1
)

if not exist ".env" (
    echo ⚠️  Warning: .env file not found. Using default configuration.
)

echo 📋 Available commands:
echo   1. Direct execution:     python run.py
echo   2. Flask CLI (basic):    flask run
echo   3. Flask CLI (custom):   flask run --host=127.0.0.1 --port=5000 --debug
echo   4. Show routes:          flask routes
echo.

REM Ask user which method to use
set /p choice="Choose execution method (1-4) or press Enter for default (1): "

if "%choice%"=="" set choice=1

if "%choice%"=="1" (
    echo 🔧 Starting with system health checks...
    python run.py
) else if "%choice%"=="2" (
    echo 🔧 Starting with Flask CLI (basic)...
    flask run
) else if "%choice%"=="3" (
    echo 🔧 Starting with Flask CLI (custom)...
    flask run --host=127.0.0.1 --port=5000 --debug
) else if "%choice%"=="4" (
    echo 📋 Showing available routes...
    flask routes
) else (
    echo ❌ Invalid choice. Using default method...
    python run.py
)

pause
