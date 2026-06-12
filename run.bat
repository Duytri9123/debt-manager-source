@echo off
set PYTHONIOENCODING=utf-8
echo ========================================
echo  Quan ly Cong no ^& Don hang B2B
echo  Python + PySide6 + Vue.js
echo ========================================
echo.

if exist .venv\Scripts\python.exe (
    echo [1/3] Kiem tra dependencies dung venv...
    .venv\Scripts\python.exe -m pip list | findstr Flask >nul
    if errorlevel 1 (
        echo Cai dat dependencies...
        .venv\Scripts\python.exe -m pip install -r requirements.txt
    )
    echo.
    echo [2/3] Khoi tao database...
    echo.
    echo [3/3] Khoi dong ung dung...
    echo.
    .venv\Scripts\python.exe main.py
) else (
    echo [1/3] Kiem tra dependencies dung python he thong...
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
)

pause
