@echo off
echo ========================================
echo  Debt Manager - Complete Build System
echo  Build Setup.exe + Generate version.json
echo ========================================
echo.

set VERSION=1.0.0
set APP_NAME=DebtManager
set OUTPUT_DIR=Output
set PYTHON=python
if exist ".venv\Scripts\python.exe" set PYTHON=.venv\Scripts\python.exe

echo [INFO] Version: %VERSION%
echo [INFO] Output Directory: %OUTPUT_DIR%
echo [INFO] Python: %PYTHON%
echo.

"%PYTHON%" -m PyInstaller --version >nul 2>nul
if errorlevel 1 (
    echo [INFO] Installing build dependencies...
    "%PYTHON%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies!
        pause
        exit /b 1
    )
)

REM Create output directory
if not exist %OUTPUT_DIR% mkdir %OUTPUT_DIR%

REM Step 1: Build Main Application
echo [1/5] Building Main Application (DebtManager.exe)...
"%PYTHON%" -m PyInstaller QuanLyB2B.spec --clean --distpath=%OUTPUT_DIR%
if errorlevel 1 (
    echo [ERROR] Failed to build main application!
    pause
    exit /b 1
)
echo.

REM Step 2: Build Updater
echo [2/5] Building Updater (updater.exe)...
"%PYTHON%" -m PyInstaller updater.spec --clean --distpath=%OUTPUT_DIR%
if errorlevel 1 (
    echo [ERROR] Failed to build updater!
    pause
    exit /b 1
)
echo.

REM Step 3: Create Inno Setup Installer
echo [3/5] Creating Installer (DebtManager_Setup.exe)...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\setup.iss
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    "C:\Program Files\Inno Setup 6\ISCC.exe" installer\setup.iss
) else if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" (
    "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" installer\setup.iss
) else (
    echo [WARNING] Inno Setup not found! Skipping installer creation.
    echo Please install Inno Setup 6 from https://jrsoftware.org/isdl.php
    pause
    exit /b 1
)
if errorlevel 1 (
    echo [ERROR] Failed to create installer!
    pause
    exit /b 1
)
echo.

REM Verify installer output
if exist "%OUTPUT_DIR%\%APP_NAME%_Setup.exe" (
    echo [OK] Installer created at %OUTPUT_DIR%\%APP_NAME%_Setup.exe
) else (
    echo [ERROR] Installer not found!
    pause
    exit /b 1
)
echo.

REM Step 4: Generate version.json
echo [4/5] Generating version.json...
"%PYTHON%" scripts\generate_version.py ^
    --setup "%OUTPUT_DIR%\%APP_NAME%_Setup.exe" ^
    --version %VERSION% ^
    --min-version 1.0.0 ^
    --notes "Initial release" "Offline desktop application" "Auto-update support"
if errorlevel 1 (
    echo [ERROR] Failed to generate version.json!
    pause
    exit /b 1
)
echo.

REM Move version.json to Output directory
if exist "version.json" (
    move /Y "version.json" "%OUTPUT_DIR%\version.json"
    echo [OK] version.json moved to %OUTPUT_DIR%\version.json
)
echo.

REM Step 5: Summary
echo [5/5] Build Summary
echo ========================================
echo.
echo Files generated in %OUTPUT_DIR%\:
echo.
dir /B %OUTPUT_DIR%
echo.
echo ========================================
echo  Build Complete!
echo ========================================
echo.
echo Release artifacts in %OUTPUT_DIR%\
echo.
dir /B %OUTPUT_DIR%
echo.
echo ========================================
echo  Opening Output folder...
echo ========================================
start %OUTPUT_DIR%
echo.
echo Next Steps:
echo 1. Test %OUTPUT_DIR%\%APP_NAME%_Setup.exe locally
echo 2. Run publish_release.bat to publish to GitHub Releases
echo    OR manually upload to:
echo    https://github.com/Duytri9123/debt-manager-release/releases/new
echo.
echo ========================================
pause
