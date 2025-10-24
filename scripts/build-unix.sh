#!/bin/bash

# 智股通 Unix/Linux/macOS 构建脚本

set -e  # 遇到错误时退出

echo "========================================"
echo "智股通 Unix/Linux/macOS 构建脚本"
echo "========================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查构建环境
echo "[1/6] 检查构建环境..."

# 检查Go
if ! command -v go &> /dev/null; then
    log_error "未找到Go，请先安装Go 1.24+"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    log_error "未找到Node.js，请先安装Node.js 18+"
    exit 1
fi

# 检查npm
if ! command -v npm &> /dev/null; then
    log_error "未找到npm，请先安装npm"
    exit 1
fi

# 检查Wails
if ! command -v wails &> /dev/null; then
    log_info "安装Wails CLI..."
    go install github.com/wailsapp/wails/v2/cmd/wails@latest
fi

# 显示版本信息
log_info "Go版本: $(go version)"
log_info "Node.js版本: $(node --version)"
log_info "npm版本: $(npm --version)"
log_info "Wails版本: $(wails version)"

# 清理旧构建
echo "[2/6] 清理旧构建文件..."
rm -rf dist build release

# 安装前端依赖
echo "[3/6] 安装前端依赖..."
cd frontend
npm install
if [ $? -ne 0 ]; then
    log_error "前端依赖安装失败"
    exit 1
fi
cd ..

# 安装Go依赖
echo "[4/6] 安装Go依赖..."
go mod tidy
if [ $? -ne 0 ]; then
    log_error "Go依赖安装失败"
    exit 1
fi

# 前端构建
echo "[5/6] 构建前端..."
cd frontend
npm run build
if [ $? -ne 0 ]; then
    log_error "前端构建失败"
    exit 1
fi
cd ..

# Wails应用构建
echo "[6/6] 构建桌面应用..."
wails build -clean -web2 -upx
if [ $? -ne 0 ]; then
    log_error "Wails构建失败"
    exit 1
fi

# 创建发布目录
mkdir -p release

# 复制构建文件
log_info "复制构建文件到release目录..."
if [ -f "dist/smart-stock-insider" ]; then
    cp "dist/smart-stock-insider" release/
fi

if [ -f "dist/smart-stock-insider.app" ]; then
    cp -r "dist/smart-stock-insider.app" release/
fi

# 复制库文件（Linux）
if ls dist/*.so 1> /dev/null 2>&1; then
    cp dist/*.so release/
fi

# 复制配置文件
if [ -f "wails.json" ]; then
    cp "wails.json" release/
fi

# 创建必要目录
mkdir -p release/data
mkdir -p release/logs
mkdir -p release/backups

# 复制数据库架构文件
if [ -f "data/smart_stock.db" ]; then
    cp "data/smart_stock.db" release/data/
fi

# 复制备份脚本
if [ -f "scripts/backup-database.sh" ]; then
    cp "scripts/backup-database.sh" release/
    chmod +x release/backup-database.sh
fi

# 复制服务脚本
if [ -f "scripts/install-service.sh" ]; then
    cp "scripts/install-service.sh" release/
    chmod +x release/install-service.sh
fi

# 设置执行权限
chmod +x release/smart-stock-insider 2>/dev/null || true

echo "========================================"
echo "构建完成!"
echo "========================================"

# 根据平台显示结果
OS=$(uname -s)
case $OS in
    Linux*)
        echo "可执行文件: release/smart-stock-insider"
        echo "数据目录: release/data/"
        echo "日志目录: release/logs/"
        echo ""
        echo "运行应用: ./release/smart-stock-insider"

        # 检查是否为Linux桌面环境
        if [ -n "$DISPLAY" ]; then
            echo "或双击运行: release/smart-stock-insider"
        fi
        ;;
    Darwin*)
        echo "应用包: release/smart-stock-insider.app"
        echo "数据目录: release/data/"
        echo "日志目录: release/logs/"
        echo ""
        echo "安装应用: cp -r release/smart-stock-insider.app /Applications/"
        echo "运行应用: open release/smart-stock-insider.app"
        ;;
esac

echo ""

# 询问是否立即运行
if command -v zenity &> /dev/null; then
    # 使用zenity显示对话框
    if zenity --question --text="是否立即运行应用?" --default-cancel; then
        echo "启动应用..."
        cd release

        case $OS in
            Linux*)
                ./smart-stock-insider &
                ;;
            Darwin*)
                open smart-stock-insider.app &
                ;;
        esac
    fi
else
    # 命令行询问
    read -p "是否立即运行应用? (y/n): " run_app
    if [ "$run_app" = "y" ] || [ "$run_app" = "Y" ]; then
        echo "启动应用..."
        cd release

        case $OS in
            Linux*)
                ./smart-stock-insider &
                ;;
            Darwin*)
                open smart-stock-insider.app &
                ;;
        esac
    fi
fi

echo "构建脚本执行完成!"