```batch
@echo off
title Finance Manager
color 0A

echo ============================================
echo   Finance Manager - Starting...
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not installed!
    echo.
    echo Download from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH"
    echo.
    pause
    exit
)

echo [1/3] Installing dependencies...
pip install -q -r requirements.txt

echo [2/3] Starting server...
echo.
echo Starting backend server...
start /B python server_desktop.py

echo [3/3] Waiting for server...
timeout /t 5 /nobreak >nul

echo Opening browser...
start http://localhost:8001

echo.
echo ============================================
echo   App is running at: http://localhost:8001
echo ============================================
echo   Default Login:
echo   Email: admin@financeapp.com
echo   Password: admin123
echo ============================================
echo.
echo   Keep this window open!
echo   Press Ctrl+C to stop the server
echo.

pause
