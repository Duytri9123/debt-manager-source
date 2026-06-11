@echo off
echo ========================================
echo  Build QuanLyB2B to .exe
echo  Python + PySide6 + Vue.js Design
echo ========================================
echo.

echo [1/3] Kiem tra PyInstaller...
pip list | findstr pyinstaller >nul
if errorlevel 1 (
    echo Cai dat PyInstaller...
    pip install pyinstaller
)

echo.
echo [2/3] Xoa build cu...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist QuanLyB2B.spec.bak del QuanLyB2B.spec.bak

echo.
echo [3/3] Build ung dung...
pyinstaller QuanLyB2B.spec --clean

echo.
echo ========================================
echo  Build hoan thanh!
echo  File .exe nam trong thu muc: dist\QuanLyB2B.exe
echo ========================================
echo.
pause
