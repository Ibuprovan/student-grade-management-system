@echo off
echo ========================================
echo   Restarting Backend Service
echo ========================================
echo.

:: Kill existing Python processes
echo [INFO] Stopping existing processes...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

:: Clean pycache
echo [INFO] Cleaning pycache...
for /r "%~dp0src" /d %%d in (__pycache__) do rd /s /q "%%d" 2>nul

:: Start backend
echo [INFO] Starting backend service...
echo.
cd /d %~dp0
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
