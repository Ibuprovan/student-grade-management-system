# 学生成绩管理系统 - 一键启动脚本 (PowerShell)
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  学生成绩管理系统 - 一键启动" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python 是否安装
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "[信息] Python 已安装: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[错误] 未找到 Python，请先安装 Python 3.9 或更高版本" -ForegroundColor Red
    Write-Host "下载地址: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "按 Enter 键退出"
    exit 1
}

# 检查 Node.js 是否安装
try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Node.js not found"
    }
    Write-Host "[信息] Node.js 已安装: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "[错误] 未找到 Node.js，请先安装 Node.js 16 或更高版本" -ForegroundColor Red
    Write-Host "下载地址: https://nodejs.org/" -ForegroundColor Yellow
    Read-Host "按 Enter 键退出"
    exit 1
}

Write-Host "[信息] 正在检查并安装后端依赖..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "[警告] 后端依赖安装可能有问题，但将继续启动..." -ForegroundColor Yellow
}

Write-Host "[信息] 正在检查并安装前端依赖..." -ForegroundColor Yellow
Set-Location frontend
npm install --legacy-peer-deps 2>$null
Set-Location ..
if ($LASTEXITCODE -ne 0) {
    Write-Host "[警告] 前端依赖安装可能有问题，但将继续启动..." -ForegroundColor Yellow
}

Write-Host "[信息] 正在初始化数据库..." -ForegroundColor Yellow
python -m src.scripts.init_users
if ($LASTEXITCODE -ne 0) {
    Write-Host "[警告] 数据库初始化可能有问题，但将继续启动..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[信息] 正在启动后端服务..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Normal

Write-Host "[信息] 正在启动前端服务..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev" -WindowStyle Normal

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  启动完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "后端服务: http://localhost:8000" -ForegroundColor Green
Write-Host "前端界面: http://localhost:5173" -ForegroundColor Green
Write-Host ""
Write-Host "默认账户:" -ForegroundColor Yellow
Write-Host "  管理员: admin / admin123" -ForegroundColor White
Write-Host "  教师:   teacher / teacher123" -ForegroundColor White
Write-Host "  学生:   student / student123" -ForegroundColor White
Write-Host ""
Write-Host "按任意键退出此窗口（服务将继续运行）..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")