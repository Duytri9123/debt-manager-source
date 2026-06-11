@echo off
echo ========================================
echo  Publish Release to GitHub
echo  Automated GitHub Release Creation
echo ========================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo.
    echo Please create a .env file with your GitHub token:
    echo.
    echo GITHUB_TOKEN=your_github_personal_access_token
    echo GITHUB_OWNER=Duytri9123
    echo GITHUB_REPO=debt-manager-release
    echo.
    echo To create a GitHub token:
    echo 1. Go to: https://github.com/settings/tokens
    echo 2. Click "Generate new token (classic)"
    echo 3. Select scope: repo
    echo 4. Copy the token
    echo 5. Create .env file and paste it
    echo.
    pause
    exit /b 1
)

REM Check if Output directory exists
if not exist "Output" (
    echo [ERROR] Output directory not found!
    echo Please run build_all.bat first.
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "Output\DebtManager_Setup.exe" (
    echo [ERROR] DebtManager_Setup.exe not found!
    echo Please run build_all.bat first.
    pause
    exit /b 1
)

if not exist "Output\version.json" (
    echo [ERROR] version.json not found!
    echo Please run build_all.bat first.
    pause
    exit /b 1
)

echo [INFO] Starting release publication...
echo.

REM Run Python script
python scripts\publish_release.py

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to publish release!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Release Published Successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Verify release at: https://github.com/Duytri9123/debt-manager-release/releases
echo 2. Test auto-update from previous version
echo 3. Announce release to users
echo.
pause
