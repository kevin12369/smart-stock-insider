#!/bin/bash

# 智股通项目初始化脚本
# Smart Stock Insider Project Setup Script

set -e

echo "🚀 开始初始化智股通项目..."

# 检查必要的工具
check_requirements() {
    echo "🔍 检查系统环境..."

    # 检查Node.js
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js 未安装，请先安装 Node.js >= 18.0.0"
        exit 1
    fi

    # 检查Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 未安装，请先安装 Python >= 3.11"
        exit 1
    fi

    # 检查Redis
    if ! command -v redis-server &> /dev/null; then
        echo "⚠️  Redis 未安装，建议安装 Redis 以启用缓存功能"
        echo "   Ubuntu/Debian: sudo apt install redis-server"
        echo "   macOS: brew install redis"
        echo "   Windows: 请下载 Redis for Windows"
    fi

    # 检查Docker (可选)
    if command -v docker &> /dev/null; then
        echo "✅ Docker 已安装"
    else
        echo "⚠️  Docker 未安装，将使用本地开发环境"
    fi

    echo "✅ 系统环境检查完成"
}

# 安装前端依赖
setup_frontend() {
    echo "📦 安装前端依赖..."
    cd frontend
    npm install
    echo "✅ 前端依赖安装完成"
    cd ..
}

# 安装后端依赖
setup_backend() {
    echo "🐍 安装后端依赖..."

    # 检查是否有Python虚拟环境
    if [ ! -d "backend/venv" ]; then
        echo "🔧 创建Python虚拟环境..."
        cd backend
        python3 -m venv venv
        echo "✅ 虚拟环境创建完成"
        cd ..
    fi

    # 激活虚拟环境并安装依赖
    echo "📚 安装Python依赖包..."
    cd backend
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "✅ 后端依赖安装完成"
    cd ..
}

# 创建必要的目录
create_directories() {
    echo "📁 创建项目目录..."

    directories=(
        "data"
        "logs"
        "cache"
        "backups"
        "uploads"
        "backend/data"
        "backend/logs"
        "backend/cache"
        "backend/backups"
        "frontend/src/styles"
        "frontend/src/assets/icons"
    )

    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
    done

    echo "✅ 目录创建完成"
}

# 复制环境配置文件
setup_environment() {
    echo "⚙️  设置环境配置..."

    if [ ! -f ".env" ]; then
        cp .env.example .env
        echo "✅ 已创建 .env 配置文件"
        echo "   请根据需要修改配置参数"
    else
        echo "ℹ️  .env 文件已存在，跳过创建"
    fi
}

# 初始化数据库
init_database() {
    echo "🗄️  初始化数据库..."

    # 创建数据库目录
    mkdir -p data

    echo "✅ 数据库目录已创建"
    echo "   数据库将在首次运行时自动初始化"
}

# 启动Redis服务 (如果可用)
start_redis() {
    if command -v redis-server &> /dev/null; then
        echo "🔄 启动 Redis 服务..."
        if pgrep redis-server > /dev/null; then
            echo "✅ Redis 服务已在运行"
        else
            redis-server --daemonize yes
            echo "✅ Redis 服务已启动"
        fi
    else
        echo "⚠️  Redis 未安装，请手动启动 Redis 服务"
    fi
}

# 显示启动说明
show_startup_instructions() {
    echo ""
    echo "🎉 智股通项目初始化完成！"
    echo ""
    echo "📋 启动说明："
    echo ""
    echo "方式一：本地开发"
    echo "  1. 启动后端服务："
    echo "     cd backend && source venv/bin/activate && python main.py"
    echo ""
    echo "  2. 启动前端服务："
    echo "     cd frontend && npm run tauri:dev"
    echo ""
    echo "方式二：Docker 开发环境"
    echo "  docker-compose up -d"
    echo ""
    echo "方式三：使用脚本快速启动"
    echo "  npm run dev"
    echo ""
    echo "📖 更多信息请查看 README.md"
    echo ""
    echo "🌐 应用地址："
    echo "  前端：http://localhost:3000"
    echo "  后端API：http://localhost:8000"
    echo "  API文档：http://localhost:8000/docs"
    echo ""
}

# 主函数
main() {
    echo "🎯 智股通项目初始化脚本 v1.0.0"
    echo "=================================="
    echo ""

    check_requirements
    create_directories
    setup_environment
    setup_frontend
    setup_backend
    init_database
    start_redis
    show_startup_instructions
}

# 执行主函数
main "$@"