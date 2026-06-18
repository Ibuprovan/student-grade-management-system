@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ========================================
echo   Student Grade Management System
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.9 or higher.
    pause
    exit /b 1
)

:: Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Please install Node.js 16 or higher.
    pause
    exit /b 1
)

echo [INFO] Installing backend dependencies...
pip install -r "%~dp0requirements.txt"
if %errorlevel% neq 0 (
    echo [WARNING] Backend dependency installation may have issues, but will continue...
)

echo [INFO] Installing frontend dependencies...
cd /d "%~dp0frontend"
call npm install --legacy-peer-deps 2>nul
cd /d "%~dp0"
if %errorlevel% neq 0 (
    echo [WARNING] Frontend dependency installation may have issues, but will continue...
)

echo [INFO] Initializing database...
python -m src.scripts.init_users
if %errorlevel% neq 0 (
    echo [WARNING] Database initialization may have issues, but will continue...
)

echo.
echo [INFO] Starting backend service...
start "Backend" cmd /k "cd /d "%~dp0" && python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"

echo [INFO] Starting frontend service...
start "Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ========================================
echo   Startup completed!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Default accounts:
echo   admin / admin123
echo   teacher / teacher123
echo   student / student123
echo.
echo Press any key to exit this window...
pause >nul
