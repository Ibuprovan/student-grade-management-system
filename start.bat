@echo off
echo ========================================
echo   Student Grade Management System - Quick Start
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.9 or higher.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Please install Node.js 16 or higher.
    echo Download: https://nodejs.org/
    pause
    exit /b 1
)

echo [INFO] Checking and installing backend dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Backend dependency installation may have issues, but will continue...
)

echo [INFO] Checking and installing frontend dependencies...
cd frontend
call npm install
cd ..
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
start "Student Grade Management System - Backend" cmd /k "cd /d %~dp0 && python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"

echo [INFO] Starting frontend service...
start "Student Grade Management System - Frontend" cmd /k "cd /d %~dp0\frontend && npm run dev"

echo.
echo ========================================
echo   Startup completed!
echo ========================================
echo.
echo Backend service: http://localhost:8000
echo Frontend interface: http://localhost:5173
echo.
echo Default accounts:
echo   Admin: admin / admin123
echo   Teacher: teacher / teacher123
echo   Student: student / student123
echo.
echo Press any key to exit this window (services will continue running)...
pause >nul