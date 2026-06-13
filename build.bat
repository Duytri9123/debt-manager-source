@echo off
echo ========================================
echo  Build DebtManager to .exe
echo  Python + PySide6 Desktop App
echo ========================================
echo.

set PYTHON=python
if exist ".venv\Scripts\python.exe" set PYTHON=.venv\Scripts\python.exe

echo [1/3] Kiem tra PyInstaller...
"%PYTHON%" -m PyInstaller --version >nul 2>nul
if errorlevel 1 (
    echo Cai dat dependencies...
    "%PYTHON%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Build dependencies install failed.
        pause
        exit /b 1
    )
)

echo.
echo [2/3] Xoa build cu...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist QuanLyB2B.spec.bak del QuanLyB2B.spec.bak

echo.
echo [3/3] Build ung dung...
"%PYTHON%" -m PyInstaller QuanLyB2B.spec --clean
if errorlevel 1 (
    echo Build failed.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Build hoan thanh!
echo  File .exe nam trong thu muc: dist\DebtManager.exe
echo ========================================
echo.
pause
