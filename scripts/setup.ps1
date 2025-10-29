# 智股通项目初始化脚本 (PowerShell版本)
# Smart Stock Insider Project Setup Script

param(
    [switch]$SkipRequirements,
    [switch]$SkipDocker
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 开始初始化智股通项目..." -ForegroundColor Green

# 检查必要的工具
function Test-Requirements {
    if ($SkipRequirements) {
        Write-Host "⏭️  跳过环境检查" -ForegroundColor Yellow
        return
    }

    Write-Host "🔍 检查系统环境..." -ForegroundColor Blue

    # 检查Node.js
    try {
        $nodeVersion = node --version
        Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Node.js 未安装，请先安装 Node.js >= 18.0.0" -ForegroundColor Red
        exit 1
    }

    # 检查Python
    try {
        $pythonVersion = python --version
        Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Python 未安装，请先安装 Python >= 3.11" -ForegroundColor Red
        exit 1
    }

    # 检查Redis
    try {
        redis-cli --version | Out-Null
        Write-Host "✅ Redis 已安装" -ForegroundColor Green
    }
    catch {
        Write-Host "⚠️  Redis 未安装，建议安装 Redis 以启用缓存功能" -ForegroundColor Yellow
        Write-Host "   Windows: 请从 https://github.com/microsoftarchive/redis/releases 下载安装" -ForegroundColor Yellow
    }

    # 检查Docker
    if (-not $SkipDocker) {
        try {
            docker --version | Out-Null
            Write-Host "✅ Docker 已安装" -ForegroundColor Green
        }
        catch {
            Write-Host "⚠️  Docker 未安装，将使用本地开发环境" -ForegroundColor Yellow
        }
    }

    Write-Host "✅ 系统环境检查完成" -ForegroundColor Green
}

# 安装前端依赖
function Install-FrontendDependencies {
    Write-Host "📦 安装前端依赖..." -ForegroundColor Blue

    Set-Location frontend
    npm install
    Set-Location ..

    Write-Host "✅ 前端依赖安装完成" -ForegroundColor Green
}

# 安装后端依赖
function Install-BackendDependencies {
    Write-Host "🐍 安装后端依赖..." -ForegroundColor Blue

    # 检查是否有Python虚拟环境
    if (-not (Test-Path "backend\venv")) {
        Write-Host "🔧 创建Python虚拟环境..." -ForegroundColor Blue
        Set-Location backend
        python -m venv venv
        Set-Location ..
        Write-Host "✅ 虚拟环境创建完成" -ForegroundColor Green
    }

    # 激活虚拟环境并安装依赖
    Write-Host "📚 安装Python依赖包..." -ForegroundColor Blue
    Set-Location backend

    # 激活虚拟环境
    if (Test-Path "venv\Scripts\Activate.ps1") {
        . .\venv\Scripts\Activate.ps1
    }
    else {
        Write-Host "⚠️  虚拟环境激活脚本未找到" -ForegroundColor Yellow
    }

    pip install --upgrade pip
    pip install -r requirements.txt

    Set-Location ..
    Write-Host "✅ 后端依赖安装完成" -ForegroundColor Green
}

# 创建必要的目录
function New-ProjectDirectories {
    Write-Host "📁 创建项目目录..." -ForegroundColor Blue

    $directories = @(
        "data",
        "logs",
        "cache",
        "backups",
        "uploads",
        "backend\data",
        "backend\logs",
        "backend\cache",
        "backend\backups",
        "frontend\src\styles",
        "frontend\src\assets\icons"
    )

    foreach ($dir in $directories) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }

    Write-Host "✅ 目录创建完成" -ForegroundColor Green
}

# 复制环境配置文件
function Initialize-Environment {
    Write-Host "⚙️  设置环境配置..." -ForegroundColor Blue

    if (-not (Test-Path ".env")) {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ 已创建 .env 配置文件" -ForegroundColor Green
        Write-Host "   请根据需要修改配置参数" -ForegroundColor Yellow
    }
    else {
        Write-Host "ℹ️  .env 文件已存在，跳过创建" -ForegroundColor Blue
    }
}

# 初始化数据库
function Initialize-Database {
    Write-Host "🗄️  初始化数据库..." -ForegroundColor Blue

    # 创建数据库目录
    New-Item -ItemType Directory -Force -Path "data" | Out-Null

    Write-Host "✅ 数据库目录已创建" -ForegroundColor Green
    Write-Host "   数据库将在首次运行时自动初始化" -ForegroundColor Yellow
}

# 启动Redis服务 (如果可用)
function Start-RedisService {
    try {
        redis-cli --version | Out-Null
        Write-Host "🔄 启动 Redis 服务..." -ForegroundColor Blue

        # 检查Redis是否已在运行
        try {
            redis-cli ping | Out-Null
            Write-Host "✅ Redis 服务已在运行" -ForegroundColor Green
        }
        catch {
            # 尝试启动Redis服务
            Start-Process -FilePath "redis-server" -WindowStyle Hidden
            Write-Host "✅ Redis 服务已启动" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "⚠️  Redis 未安装，请手动启动 Redis 服务" -ForegroundColor Yellow
    }
}

# 显示启动说明
function Show-StartupInstructions {
    Write-Host ""
    Write-Host "🎉 智股通项目初始化完成！" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 启动说明：" -ForegroundColor Blue
    Write-Host ""
    Write-Host "方式一：本地开发" -ForegroundColor White
    Write-Host "  1. 启动后端服务：" -ForegroundColor Gray
    Write-Host "     cd backend && venv\Scripts\Activate && python main.py" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. 启动前端服务：" -ForegroundColor Gray
    Write-Host "     cd frontend && npm run tauri:dev" -ForegroundColor Gray
    Write-Host ""
    Write-Host "方式二：Docker 开发环境" -ForegroundColor White
    Write-Host "  docker-compose up -d" -ForegroundColor Gray
    Write-Host ""
    Write-Host "方式三：使用脚本快速启动" -ForegroundColor White
    Write-Host "  npm run dev" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📖 更多信息请查看 README.md" -ForegroundColor Blue
    Write-Host ""
    Write-Host "🌐 应用地址：" -ForegroundColor Blue
    Write-Host "  前端：http://localhost:3000" -ForegroundColor Gray
    Write-Host "  后端API：http://localhost:8000" -ForegroundColor Gray
    Write-Host "  API文档：http://localhost:8000/docs" -ForegroundColor Gray
    Write-Host ""
}

# 主函数
function Main {
    Write-Host "🎯 智股通项目初始化脚本 v1.0.0" -ForegroundColor Cyan
    Write-Host "==================================" -ForegroundColor Cyan
    Write-Host ""

    Test-Requirements
    New-ProjectDirectories
    Initialize-Environment
    Install-FrontendDependencies
    Install-BackendDependencies
    Initialize-Database
    Start-RedisService
    Show-StartupInstructions
}

# 执行主函数
Main