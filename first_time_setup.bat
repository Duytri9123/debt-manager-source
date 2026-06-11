@echo off
echo ========================================
echo  Debt Manager - First Time Setup
echo  Auto-Install Python ^& Build
echo ========================================
echo.

echo This script will:
echo 1. Check if Python is installed
echo 2. Install Python if needed
echo 3. Install all dependencies
echo 4. Build the application
echo 5. Create installer
echo 6. Generate version.json
echo.

echo ========================================
echo  STEP 1: Checking Python Installation
echo ========================================
echo.

python --version >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Python is installed!
    python --version
    echo.
    goto INSTALL_DEPS
)

echo [WARNING] Python is NOT installed or not in PATH!
echo.
echo You need to install Python first:
echo.
echo 1. Go to: https://www.python.org/downloads/
echo 2. Download Python 3.10 or later
echo 3. Run the installer
echo 4. IMPORTANT: Check "Add Python to PATH"
echo 5. Click "Install Now"
echo 6. After installation, run: build_all.bat
echo.
echo Or download directly from:
echo https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe
echo.
pause
exit /b 1

:INSTALL_DEPS
echo ========================================
echo  STEP 2: Installing Dependencies
echo ========================================
echo.

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %errorlevel% == 0 (
    echo [OK] Dependencies installed!
    echo.
) else (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)

goto BUILD

:BUILD
echo ========================================
echo  STEP 3: Building Application
echo ========================================
echo.

call build_all.bat

if %errorlevel% == 0 (
    echo.
    echo ========================================
    echo  BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Your release is ready in Output/ folder.
    echo.
) else (
    echo.
    echo [ERROR] Build failed!
    echo Check the errors above.
    echo.
)

pause
