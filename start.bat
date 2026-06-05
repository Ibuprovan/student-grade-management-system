@echo off
chcp 65001 >nul
echo ========================================
echo   学生成绩管理系统 - 一键启动
echo ========================================
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.9 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查 Node.js 是否安装
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 16 或更高版本
    echo 下载地址: https://nodejs.org/
    pause
    exit /b 1
)

echo [信息] 正在检查并安装后端依赖...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [警告] 后端依赖安装可能有问题，但将继续启动...
)

echo [信息] 正在检查并安装前端依赖...
cd frontend
call npm install
cd ..
if %errorlevel% neq 0 (
    echo [警告] 前端依赖安装可能有问题，但将继续启动...
)

echo [信息] 正在初始化数据库...
python -m src.scripts.init_users
if %errorlevel% neq 0 (
    echo [警告] 数据库初始化可能有问题，但将继续启动...
)

echo.
echo [信息] 正在启动后端服务...
start "学生成绩管理系统 - 后端服务" cmd /k "cd /d %~dp0 && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"

echo [信息] 正在启动前端服务...
start "学生成绩管理系统 - 前端服务" cmd /k "cd /d %~dp0\frontend && npm run dev"

echo.
echo ========================================
echo   启动完成！
echo ========================================
echo.
echo 后端服务: http://localhost:8000
echo 前端界面: http://localhost:5173
echo.
echo 默认账户:
echo   管理员: admin / admin123
echo   教师:   teacher / teacher123
echo   学生:   student / student123
echo.
echo 按任意键退出此窗口（服务将继续运行）...
pause >nul