@echo off
echo ========================================
echo  Debt Manager - Complete Release
echo  Build + Publish in One Command
echo ========================================
echo.

echo This will:
echo 1. Build all executables
echo 2. Create Setup.exe installer
echo 3. Generate version.json with SHA256
echo 4. Publish to GitHub Releases
echo.

pause

echo.
echo [Step 1/2] Building release artifacts...
echo ========================================
call build_all.bat

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed! Aborting publish.
    pause
    exit /b 1
)

echo.
echo [Step 2/2] Publishing to GitHub Releases...
echo ========================================
call publish_release.bat

if errorlevel 1 (
    echo.
    echo [ERROR] Publish failed!
    echo Release artifacts are still in Output/ folder.
    echo You can retry publish_release.bat manually.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  RELEASE COMPLETE!
echo ========================================
echo.
echo Your release is now live at:
echo https://github.com/Duytri9123/debt-manager-release/releases
echo.
echo Users will receive auto-update notifications.
echo.
pause
