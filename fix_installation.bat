@echo off
echo Lab Manager - Installation Fix Script
echo =====================================
echo.

echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Trying to install lxml (method 1 - binary only)...
python -m pip install --only-binary=lxml lxml
if %errorlevel% equ 0 (
    echo Success! Installing remaining requirements...
    python -m pip install -r requirements.txt
    goto :success
)

echo.
echo Method 1 failed. Trying method 2 (specific version)...
python -m pip install lxml==4.9.3 --only-binary=lxml
if %errorlevel% equ 0 (
    echo Success! Installing remaining requirements...
    python -m pip install -r requirements.txt
    goto :success
)

echo.
echo Method 2 failed. Trying alternative requirements...
if exist requirements_alternative.txt (
    python -m pip install -r requirements_alternative.txt
    if %errorlevel% equ 0 goto :success
)

echo.
echo All methods failed. Please install Microsoft C++ Build Tools:
echo https://visualstudio.microsoft.com/visual-cpp-build-tools/
goto :end

:success
echo.
echo ===================================
echo Installation completed successfully!
echo ===================================
echo.
echo You can now run:
echo python run.py
echo.

:end
pause
