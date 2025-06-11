#!/usr/bin/env python3
"""
Fix Installation Issues for Lab Manager
Handles common Python package installation problems on Windows
"""

import subprocess
import sys
import os
import platform
import json
from pathlib import Path

def check_system_info():
    """Check system information"""
    print("🖥️  System Information:")
    print(f"   OS: {platform.system()} {platform.release()}")
    print(f"   Python: {sys.version}")
    print(f"   Architecture: {platform.architecture()[0]}")
    print()

def upgrade_pip():
    """Upgrade pip to latest version"""
    print("📦 Upgrading pip...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ])
        print("✅ pip upgraded successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to upgrade pip: {e}")
        return False

def install_lxml_with_fallback():
    """Install lxml with multiple fallback methods"""
    print("🔧 Installing lxml with fallback methods...")
    
    methods = [
        {
            "name": "Pre-compiled wheel (binary only)",
            "command": [sys.executable, "-m", "pip", "install", "--only-binary=lxml", "lxml"]
        },
        {
            "name": "Specific lxml version with wheel",
            "command": [sys.executable, "-m", "pip", "install", "lxml==4.9.3", "--only-binary=lxml"]
        },
        {
            "name": "From wheel repository",
            "command": [sys.executable, "-m", "pip", "install", "lxml", 
                       "--find-links", "https://download.lxml.de/python/"]
        },
        {
            "name": "No cache directory",
            "command": [sys.executable, "-m", "pip", "install", "lxml", "--no-cache-dir"]
        },
        {
            "name": "Force reinstall",
            "command": [sys.executable, "-m", "pip", "install", "lxml", "--force-reinstall", "--no-deps"]
        }
    ]
    
    for method in methods:
        print(f"\n🔄 Trying: {method['name']}")
        try:
            subprocess.check_call(method['command'])
            print(f"✅ Success with: {method['name']}")
            return True
        except subprocess.CalledProcessError:
            print(f"❌ Failed: {method['name']}")
            continue
    
    print("\n❌ All lxml installation methods failed!")
    return False

def try_conda_install():
    """Try installing via conda if available"""
    print("\n🐍 Checking for conda...")
    
    try:
        # Check if conda is available
        subprocess.check_call(["conda", "--version"], 
                            stdout=subprocess.DEVNULL, 
                            stderr=subprocess.DEVNULL)
        
        print("✅ Conda found, trying conda install...")
        subprocess.check_call(["conda", "install", "-y", "lxml"])
        print("✅ lxml installed via conda!")
        return True
        
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Conda not available")
        return False

def create_alternative_requirements():
    """Create alternative requirements.txt without problematic packages"""
    print("\n📝 Creating alternative requirements file...")
    
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        alternative_lines = []
        problematic_packages = ["lxml"]
        alternatives = {
            "lxml": "# lxml - Install manually: pip install --only-binary=lxml lxml\nbeautifulsoup4>=4.12.0\nhtml5lib>=1.1"
        }
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                alternative_lines.append(line)
                continue
                
            package_name = line.split("==")[0].split(">=")[0].split("<=")[0].strip()
            
            if package_name.lower() in [p.lower() for p in problematic_packages]:
                if package_name.lower() in alternatives:
                    alternative_lines.append(alternatives[package_name.lower()])
                else:
                    alternative_lines.append(f"# {line} - PROBLEMATIC PACKAGE")
            else:
                alternative_lines.append(line)
        
        # Save alternative requirements
        with open("requirements_alternative.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(alternative_lines))
        
        print("✅ Alternative requirements saved to: requirements_alternative.txt")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create alternative requirements: {e}")
        return False

def install_requirements_safely():
    """Install requirements with safe fallbacks"""
    print("\n📦 Installing requirements safely...")
    
    requirements_files = ["requirements.txt", "requirements_alternative.txt"]
    
    for req_file in requirements_files:
        if not os.path.exists(req_file):
            continue
            
        print(f"\n🔄 Trying {req_file}...")
        
        methods = [
            {
                "name": f"Standard install from {req_file}",
                "command": [sys.executable, "-m", "pip", "install", "-r", req_file]
            },
            {
                "name": f"Binary-only install from {req_file}",
                "command": [sys.executable, "-m", "pip", "install", 
                           "--only-binary=:all:", "-r", req_file]
            },
            {
                "name": f"No-cache install from {req_file}",
                "command": [sys.executable, "-m", "pip", "install", 
                           "--no-cache-dir", "-r", req_file]
            }
        ]
        
        for method in methods:
            print(f"   🔄 {method['name']}")
            try:
                subprocess.check_call(method['command'])
                print(f"   ✅ Success!")
                return True
            except subprocess.CalledProcessError:
                print(f"   ❌ Failed")
                continue
    
    print("❌ All requirements installation methods failed!")
    return False

def download_build_tools_info():
    """Provide information about downloading build tools"""
    print("\n🛠️  Microsoft Visual C++ Build Tools Required")
    print("=" * 60)
    print("If all installation methods fail, you need to install:")
    print("Microsoft Visual C++ 14.0 or greater")
    print()
    print("📥 Download from:")
    print("https://visualstudio.microsoft.com/visual-cpp-build-tools/")
    print()
    print("📋 Installation steps:")
    print("1. Download 'Build Tools for Visual Studio 2022'")
    print("2. Run the installer")
    print("3. Select 'C++ build tools' workload")
    print("4. Include these components:")
    print("   - MSVC v143 - VS 2022 C++ x64/x86 build tools")
    print("   - Windows 10/11 SDK (latest version)")
    print("   - CMake tools for Visual Studio")
    print("5. Install and restart your computer")
    print("6. Try running this script again")
    print()

def create_install_script():
    """Create a batch script for easy installation"""
    print("\n📜 Creating installation helper script...")
    
    if platform.system() == "Windows":
        script_content = """@echo off
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
"""
        with open("fix_installation.bat", "w") as f:
            f.write(script_content)
        print("✅ Windows batch script created: fix_installation.bat")
        
    else:  # Unix/Linux/Mac
        script_content = """#!/bin/bash
echo "Lab Manager - Installation Fix Script"
echo "====================================="
echo

echo "Upgrading pip..."
python3 -m pip install --upgrade pip

echo
echo "Trying to install lxml (method 1 - binary only)..."
if python3 -m pip install --only-binary=lxml lxml; then
    echo "Success! Installing remaining requirements..."
    python3 -m pip install -r requirements.txt
    echo "Installation completed successfully!"
    exit 0
fi

echo
echo "Method 1 failed. Trying method 2 (specific version)..."
if python3 -m pip install lxml==4.9.3 --only-binary=lxml; then
    echo "Success! Installing remaining requirements..."
    python3 -m pip install -r requirements.txt
    echo "Installation completed successfully!"
    exit 0
fi

echo
echo "Method 2 failed. Trying alternative requirements..."
if [ -f "requirements_alternative.txt" ]; then
    if python3 -m pip install -r requirements_alternative.txt; then
        echo "Installation completed successfully!"
        exit 0
    fi
fi

echo
echo "All methods failed. You may need to install build tools."
echo "On Ubuntu/Debian: sudo apt-get install build-essential libxml2-dev libxslt1-dev"
echo "On CentOS/RHEL: sudo yum install gcc libxml2-devel libxslt-devel"
echo "On macOS: xcode-select --install"
exit 1
"""
        with open("fix_installation.sh", "w") as f:
            f.write(script_content)
        os.chmod("fix_installation.sh", 0o755)
        print("✅ Unix shell script created: fix_installation.sh")

def main():
    """Main function to fix installation issues"""
    print("🔧 Lab Manager Installation Fix")
    print("=" * 50)
    
    check_system_info()
    
    # Step 1: Upgrade pip
    if not upgrade_pip():
        print("⚠️  Continuing without pip upgrade...")
    
    # Step 2: Try to install lxml specifically
    lxml_success = install_lxml_with_fallback()
    
    # Step 3: Try conda if lxml failed
    if not lxml_success:
        lxml_success = try_conda_install()
    
    # Step 4: Create alternative requirements if needed
    if not lxml_success:
        create_alternative_requirements()
    
    # Step 5: Install requirements
    req_success = install_requirements_safely()
    
    # Step 6: Create helper scripts
    create_install_script()
    
    # Summary
    print(f"\n{'='*50}")
    print("INSTALLATION FIX SUMMARY")
    print(f"{'='*50}")
    
    if lxml_success and req_success:
        print("🎉 Installation completed successfully!")
        print("\n📋 Next steps:")
        print("1. Run: python run.py")
        print("2. Access: http://localhost:5000")
    elif req_success:
        print("✅ Requirements installed (alternative packages used)")
        print("⚠️  lxml not installed - some features may be limited")
        print("\n📋 Next steps:")
        print("1. Run: python run.py")
        print("2. If you need lxml, install Visual C++ Build Tools")
    else:
        print("❌ Installation failed")
        download_build_tools_info()
        print("\n📋 Helper scripts created:")
        if platform.system() == "Windows":
            print("- fix_installation.bat (run this script)")
        else:
            print("- fix_installation.sh (run this script)")
    
    return lxml_success and req_success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
