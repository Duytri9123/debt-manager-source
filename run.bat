@echo off
echo ========================================
echo  Quan ly Cong no & Don hang B2B
echo  Python + PySide6 + Vue.js
echo ========================================
echo.

echo [1/3] Kiem tra dependencies...
pip list | findstr Flask >nul
if errorlevel 1 (
    echo Cai dat dependencies...
    pip install -r requirements.txt
)

echo.
echo [2/3] Khoi tao database...
echo.

echo [3/3] Khoi dong ung dung...
echo.

python main.py

pause
