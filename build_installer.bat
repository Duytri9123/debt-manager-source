@echo off
:: ─────────────────────────────────────────────────────────────────────────────
:: Build Installer Only (use after build.bat has created executables)
:: ─────────────────────────────────────────────────────────────────────────────

echo.
echo ========================================
echo  Building Installer with Inno Setup
echo ========================================
echo.

:: Check for Inno Setup
set ISCC_PATH=
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set ISCC_PATH=C:\Program Files\Inno Setup 6\ISCC.exe
)

if "%ISCC_PATH%"=="" (
    echo ERROR: Inno Setup 6 not found!
    echo.
    echo Please download and install from:
    echo https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

echo Using: %ISCC_PATH%
echo.

:: Create output directory
if not exist Output mkdir Output

:: Build installer
echo Compiling installer...
"%ISCC_PATH%" /OOutput installer\setup.iss

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Installer built successfully!
echo ========================================
echo.
echo Location: Output\MyApp_Setup.exe
echo.
echo Test commands:
echo   Normal install: Output\MyApp_Setup.exe
echo   Silent install: Output\MyApp_Setup.exe /VERYSILENT
echo.
pause
