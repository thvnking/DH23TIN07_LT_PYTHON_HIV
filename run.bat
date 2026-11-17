@echo off
setlocal
chcp 65001 > nul
cd /d "%~dp0"

echo ======================================================================
echo   DANG KHOI DONG WEB BAN DO HIV/AIDS TOAN CAU (DH23TIN07)
echo ======================================================================
echo.

set "PYTHON_CMD="
python --version >nul 2>&1
if not errorlevel 1 set "PYTHON_CMD=python"

if not defined PYTHON_CMD (
    py -3 --version >nul 2>&1
    if not errorlevel 1 set "PYTHON_CMD=py -3"
)

if not defined PYTHON_CMD (
    echo KHONG TIM THAY TRINH THONG DICH PYTHON HOAT DONG.
    echo Hay cai dat Python 3 tu https://www.python.org/downloads/windows/
    echo va chon "Add python.exe to PATH", sau do dong va mo lai cua so nay.
    echo.
    pause
    exit /b 1
)

echo Dang chay ung dung. Trinh duyet se mo tai http://127.0.0.1:8000
echo Neu cong 8000 dang ban, ung dung se thu cong 8501.
echo Nhan Ctrl+C tai cua so nay de dung server.
echo.
%PYTHON_CMD% app.py
if errorlevel 1 (
    echo.
    echo Ung dung da dung do loi. Hay kiem tra thong bao loi phia tren.
    pause
)

endlocal
