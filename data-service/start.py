#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据服务启动脚本
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("错误：需要Python 3.8或更高版本")
        return False
    print(f"Python版本: {sys.version}")
    return True

def check_dependencies():
    """检查依赖包"""
    print("检查依赖包...")
    required_packages = [
        'akshare',
        'pandas',
        'numpy',
        'requests',
        'fastapi',
        'uvicorn',
        'pydantic',
        'aiofiles',
        'loguru'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} (缺失)")

    if missing_packages:
        print(f"\n缺失的包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False

    print("所有依赖包检查通过")
    return True

def install_dependencies():
    """安装依赖包"""
    print("安装依赖包...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("依赖包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖包安装失败: {e}")
        return False

def check_data_service():
    """检查数据服务文件"""
    required_files = [
        'main.py',
        'data_provider.py',
        'config.py'
    ]

    for file in required_files:
        if not os.path.exists(file):
            print(f"错误：找不到文件 {file}")
            return False

    print("数据服务文件检查通过")
    return True

def start_service():
    """启动数据服务"""
    print("启动智股通数据服务...")

    # 设置环境变量
    env = os.environ.copy()
    env['PYTHONPATH'] = str(Path(__file__).parent)

    try:
        # 启动服务
        process = subprocess.Popen([
            sys.executable, "main.py"
        ], env=env, cwd=Path(__file__).parent)

        print(f"数据服务已启动，PID: {process.pid}")
        print("服务地址: http://127.0.0.1:8001")
        print("API文档: http://127.0.0.1:8001/docs")

        # 等待服务启动
        time.sleep(2)

        return process

    except Exception as e:
        print(f"启动服务失败: {e}")
        return None

def main():
    """主函数"""
    print("=" * 50)
    print("智股通数据服务启动器")
    print("=" * 50)

    # 检查Python版本
    if not check_python_version():
        return

    # 检查数据服务文件
    if not check_data_service():
        return

    # 检查依赖包
    if not check_dependencies():
        # 尝试安装依赖包
        print("\n尝试自动安装依赖包...")
        if not install_dependencies():
            return

    # 启动服务
    process = start_service()
    if process is None:
        return

    print("\n数据服务运行中，按 Ctrl+C 停止服务")

    try:
        # 等待进程结束
        process.wait()
    except KeyboardInterrupt:
        print("\n正在停止数据服务...")
        process.terminate()
        try:
            process.wait(timeout=5)
            print("数据服务已停止")
        except subprocess.TimeoutExpired:
            print("强制停止数据服务...")
            process.kill()
            process.wait()

if __name__ == "__main__":
    main()