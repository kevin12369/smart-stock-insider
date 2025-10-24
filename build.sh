#!/bin/bash
# 智股通项目标准化构建脚本
# 打包命名规则: 项目缩写-系统-支持的架构-版本号

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
PROJECT_NAME="ssi"
SYSTEM="windows"
ARCH="amd64"
VERSION="v0.0.1-dev"
OUTPUT_NAME="${PROJECT_NAME}-${SYSTEM}-${ARCH}-${VERSION}"

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_success() {
    print_message "$GREEN" "✅ $1"
}

print_info() {
    print_message "$BLUE" "ℹ️  $1"
}

print_warning() {
    print_message "$YELLOW" "⚠️  $1"
}

print_error() {
    print_message "$RED" "❌ $1"
}

# 检查依赖
check_dependencies() {
    print_info "检查构建依赖..."

    if ! command -v go &> /dev/null; then
        print_error "Go未安装，请先安装Go 1.21+"
        exit 1
    fi

    if ! command -v wails &> /dev/null; then
        print_error "Wails CLI未安装，请先安装Wails"
        exit 1
    fi

    if ! command -v node &> /dev/null; then
        print_error "Node.js未安装，请先安装Node.js 18+"
        exit 1
    fi

    print_success "所有依赖检查通过"
}

# 清理旧的构建文件
clean_build() {
    print_info "清理旧的构建文件..."

    # 删除旧的exe文件
    rm -f *.exe

    # 删除旧的安装包
    rm -f *.installer
    rm -f *.sha256

    # 清理构建目录
    if [ -d "build" ]; then
        rm -rf build
    fi

    print_success "清理完成"
}

# 更新版本号
update_version() {
    print_info "更新版本号: $VERSION"
    echo "$VERSION" > VERSION
    print_success "版本号已更新"
}

# 构建前端
build_frontend() {
    print_info "构建前端应用..."

    cd frontend
    npm install
    npm run build

    if [ $? -eq 0 ]; then
        print_success "前端构建完成"
    else
        print_error "前端构建失败"
        exit 1
    fi

    cd ..
}

# 构建后端
build_backend() {
    print_info "构建后端应用..."

    go mod tidy
    go mod download

    print_success "后端依赖准备完成"
}

# 构建应用
build_application() {
    print_info "构建Wails应用..."

    # 使用clean选项确保完全重新构建
    wails build -clean -upx

    if [ $? -eq 0 ]; then
        print_success "应用构建完成"
    else
        print_error "应用构建失败"
        exit 1
    fi
}

# 重命名文件
rename_output() {
    print_info "重命名构建文件..."

    if [ -f "build/bin/smart-stock-insider.exe" ]; then
        mv "build/bin/smart-stock-insider.exe" "${OUTPUT_NAME}.exe"
        print_success "文件已重命名为: ${OUTPUT_NAME}.exe"
    else
        print_error "构建的exe文件不存在"
        exit 1
    fi
}

# 生成校验和
generate_checksum() {
    print_info "生成文件校验和..."

    if [ -f "${OUTPUT_NAME}.exe" ]; then
        sha256sum "${OUTPUT_NAME}.exe" > "${OUTPUT_NAME}.exe.sha256"
        print_success "校验和已生成: ${OUTPUT_NAME}.exe.sha256"

        # 显示校验和信息
        print_info "文件信息:"
        ls -lh "${OUTPUT_NAME}.exe"
        echo ""
        print_info "SHA256校验和:"
        cat "${OUTPUT_NAME}.exe.sha256"
    else
        print_error "目标文件不存在，无法生成校验和"
    fi
}

# 生成安装包
create_installer() {
    print_info "生成Windows安装包..."

    wails build -nsis

    if [ $? -eq 0 ]; then
        # 重命名安装包
        if [ -f "build/bin/smart-stock-insider-installer.exe" ]; then
            mv "build/bin/smart-stock-insider-installer.exe" "${OUTPUT_NAME}-installer.exe"
            print_success "安装包已生成: ${OUTPUT_NAME}-installer.exe"
        fi
    else
        print_warning "安装包生成失败，但exe文件已生成"
    fi
}

# 构建信息显示
show_build_info() {
    echo ""
    print_info "🎉 构建完成！"
    echo ""
    echo "📦 构建信息:"
    echo "   项目名称: 智股通 (Smart Stock Insider)"
    echo "   构建文件: ${OUTPUT_NAME}.exe"
    echo "   版本号:   ${VERSION}"
    echo "   系统架构: ${SYSTEM}-${ARCH}"
    echo ""

    if [ -f "${OUTPUT_NAME}.exe" ]; then
        echo "📋 生成的文件:"
        ls -lh "${OUTPUT_NAME}.exe"*
    fi

    echo ""
    print_info "🚀 使用方法:"
    echo "   1. 直接运行: ./${OUTPUT_NAME}.exe"
    echo "   2. 安装包:   ./${OUTPUT_NAME}-installer.exe"
    echo ""
}

# 主函数
main() {
    echo ""
    print_info "🏗️  智股通项目标准化构建"
    echo "======================================"
    echo ""

    # 执行构建步骤
    check_dependencies
    clean_build
    update_version
    build_frontend
    build_backend
    build_application
    rename_output
    generate_checksum
    create_installer
    show_build_info
}

# 处理命令行参数
case "${1:-}" in
    "clean")
        clean_build
        ;;
    "frontend")
        build_frontend
        ;;
    "backend")
        build_backend
        ;;
    "build")
        build_application
        rename_output
        ;;
    "package")
        create_installer
        ;;
    "checksum")
        generate_checksum
        ;;
    *)
        main
        ;;
esac