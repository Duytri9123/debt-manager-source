@echo off
setlocal enabledelayedexpansion

:: ─────────────────────────────────────────────────────────────────────────────
:: Complete Build Script for B2B Management Application
:: ─────────────────────────────────────────────────────────────────────────────
:: 
:: This script:
::   1. Builds QuanLyB2B.exe (main application)
::   2. Builds Updater.exe (auto-update process)
::   3. Creates installer using Inno Setup
::   4. Calculates SHA256 for auto-update
::   5. Updates version.json
::
:: Prerequisites:
::   - Python 3.10+
::   - PyInstaller: pip install pyinstaller
::   - Inno Setup 6: https://jrsoftware.org/isdl.php
::
:: ─────────────────────────────────────────────────────────────────────────────

echo.
echo ========================================
echo  B2B Management - Complete Build Script
echo ========================================
echo.

:: ── Configuration ───────────────────────────────────────────────────────────
set APP_NAME=QuanLyB2B
set UPDATER_NAME=Updater
set INSTALLER_SCRIPT=installer\setup.iss
set VERSION_FILE=installer\version.json
set OUTPUT_DIR=Output
set DIST_DIR=dist

:: ── Check Python ────────────────────────────────────────────────────────────
echo [1/7] Checking Python installation...
py --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)
echo ✓ Python found
echo.

:: ── Check PyInstaller ───────────────────────────────────────────────────────
echo [2/7] Checking PyInstaller...
py -m pip list | findstr /i "pyinstaller" >nul
if errorlevel 1 (
    echo Installing PyInstaller...
    py -m pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller!
        pause
        exit /b 1
    )
)
echo ✓ PyInstaller found
echo.

:: ── Clean Previous Builds ───────────────────────────────────────────────────
echo [3/7] Cleaning previous builds...
if exist build rmdir /s /q build
if exist %DIST_DIR% rmdir /s /q %DIST_DIR%
if exist %OUTPUT_DIR% rmdir /s /q %OUTPUT_DIR%
if exist *.spec del /q *.spec
echo ✓ Cleaned
echo.

:: ── Build Main Application ──────────────────────────────────────────────────
echo [4/7] Building %APP_NAME%.exe...
py -m PyInstaller --clean ^
    --name="%APP_NAME%" ^
    --windowed ^
    --onefile ^
    --icon=installer\icon.ico ^
    --add-data "src;src" ^
    --hidden-import=PySide6 ^
    --hidden-import=PySide6.QtCore ^
    --hidden-import=PySide6.QtGui ^
    --hidden-import=PySide6.QtWidgets ^
    --hidden-import=openpyxl ^
    --exclude-module=tkinter ^
    --exclude-module=unittest ^
    main.py

if errorlevel 1 (
    echo ERROR: Failed to build %APP_NAME%.exe!
    pause
    exit /b 1
)
echo ✓ Built %APP_NAME%.exe
echo.

:: ── Build Updater ───────────────────────────────────────────────────────────
echo [5/7] Building %UPDATER_NAME%.exe...
py -m PyInstaller --clean ^
    --name="%UPDATER_NAME%" ^
    --onefile ^
    --console ^
    updater.py

if errorlevel 1 (
    echo ERROR: Failed to build %UPDATER_NAME%.exe!
    pause
    exit /b 1
)
echo ✓ Built %UPDATER_NAME%.exe
echo.

:: ── Verify Executables ──────────────────────────────────────────────────────
echo [6/7] Verifying executables...
if not exist %DIST_DIR%\%APP_NAME%.exe (
    echo ERROR: %APP_NAME%.exe not found in %DIST_DIR%!
    pause
    exit /b 1
)
if not exist %DIST_DIR%\%UPDATER_NAME%.exe (
    echo ERROR: %UPDATER_NAME%.exe not found in %DIST_DIR%!
    pause
    exit /b 1
)

:: Show file sizes
for %%A in ("%DIST_DIR%\%APP_NAME%.exe") do (
    echo   %APP_NAME%.exe: %%~zA bytes
)
for %%A in ("%DIST_DIR%\%UPDATER_NAME%.exe") do (
    echo   %UPDATER_NAME%.exe: %%~zA bytes
)
echo ✓ Executables verified
echo.

:: ── Build Installer (if Inno Setup is installed) ────────────────────────────
echo [7/7] Building installer...

:: Check for Inno Setup
set ISCC_PATH=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe
) else if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set ISCC_PATH=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe
)

if "%ISCC_PATH%"=="" (
    echo WARNING: Inno Setup 6 not found!
    echo.
    echo Please install Inno Setup 6 from:
    echo https://jrsoftware.org/isdl.php
    echo.
    echo After installation, run this script again to create the installer.
    echo.
    echo Your executables are ready in: %DIST_DIR%\
    echo   - %APP_NAME%.exe
    echo   - %UPDATER_NAME%.exe
    echo.
    pause
    exit /b 0
)

echo Using Inno Setup: %ISCC_PATH%
echo.

:: Run Inno Setup Compiler
"%ISCC_PATH%" /O%OUTPUT_DIR% %INSTALLER_SCRIPT%

if errorlevel 1 (
    echo ERROR: Failed to build installer!
    pause
    exit /b 1
)

:: Verify installer
if not exist %OUTPUT_DIR%\MyApp_Setup.exe (
    echo ERROR: Installer not found in %OUTPUT_DIR%!
    pause
    exit /b 1
)

for %%A in ("%OUTPUT_DIR%\MyApp_Setup.exe") do (
    echo   MyApp_Setup.exe: %%~zA bytes
)

echo ✓ Installer built successfully
echo.

:: ── Calculate SHA256 ────────────────────────────────────────────────────────
echo ─────────────────────────────────────────────────────────
echo Calculating SHA256 for auto-update...
echo ─────────────────────────────────────────────────────────

certutil -hashfile "%OUTPUT_DIR%\MyApp_Setup.exe" SHA256 > temp_sha256.txt
for /f "skip=1 tokens=*" %%A in (temp_sha256.txt) do (
    set SHA256=%%A
    goto :found_hash
)
:found_hash
del temp_sha256.txt

:: Remove spaces from SHA256
set SHA256=%SHA256: =%

echo SHA256: %SHA256%
echo.

:: ── Update version.json ─────────────────────────────────────────────────────
echo Updating version.json with SHA256...

:: Use PowerShell to update JSON
powershell -Command ^
    "$json = Get-Content '%VERSION_FILE%' | ConvertFrom-Json; ^
     $json.sha256 = '%SHA256%'; ^
     $json.file_size = (Get-Item '%OUTPUT_DIR%\MyApp_Setup.exe').Length; ^
     $json | ConvertTo-Json -Depth 10 | Set-Content '%VERSION_FILE%' -Encoding UTF8"

if errorlevel 1 (
    echo WARNING: Failed to update version.json
    echo Please update it manually with the SHA256 above
) else (
    echo ✓ version.json updated
)
echo.

:: ── Build Summary ───────────────────────────────────────────────────────────
echo ========================================
echo  BUILD COMPLETED SUCCESSFULLY!
echo ========================================
echo.
echo Files created:
echo   1. %DIST_DIR%\%APP_NAME%.exe      (Main application)
echo   2. %DIST_DIR%\%UPDATER_NAME%.exe  (Auto-update process)
echo   3. %OUTPUT_DIR%\MyApp_Setup.exe   (Installer)
echo.
echo Auto-update metadata:
echo   - installer\version.json (updated with SHA256)
echo.
echo Next steps:
echo   1. Test installer: %OUTPUT_DIR%\MyApp_Setup.exe
echo   2. Test application after installation
echo   3. Commit version.json to GitHub
echo   4. Create GitHub Release with MyApp_Setup.exe
echo.
echo Silent install command:
echo   MyApp_Setup.exe /VERYSILENT /NORESTART
echo.
echo ========================================

pause
