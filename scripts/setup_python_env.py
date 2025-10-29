#!/usr/bin/env python3
"""
Python 3.12 环境自动配置脚本

Author: Smart Stock Insider Team
Version: 1.0.0
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """检查Python版本兼容性"""
    print("🔍 检查Python版本...")
    version = sys.version_info
    print(f"   当前Python版本: {version.major}.{version.minor}.{version.micro}")

    if version.major != 3 or version.minor < 12:
        print("❌ 错误: 需要Python 3.12或更高版本")
        return False

    print("✅ Python版本检查通过")
    return True

def create_virtual_environment():
    """创建Python虚拟环境"""
    print("🏗️ 创建Python虚拟环境...")

    venv_path = Path(".venv")
    if venv_path.exists():
        print("⚠️  虚拟环境已存在，删除旧环境...")
        import shutil
        shutil.rmtree(venv_path, ignore_errors=True)

    try:
        # 创建虚拟环境
        result = subprocess.run([
            sys.executable, "-m", "venv", ".venv"
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ 虚拟环境创建失败: {result.stderr}")
            return False

        print("✅ 虚拟环境创建成功")
        return True
    except Exception as e:
        print(f"❌ 虚拟环境创建异常: {e}")
        return False

def get_venv_python():
    """获取虚拟环境中的Python路径"""
    if platform.system() == "Windows":
        return ".venv\\Scripts\\python.exe"
    else:
        return ".venv/bin/python"

def get_venv_pip():
    """获取虚拟环境中的pip路径"""
    if platform.system() == "Windows":
        return ".venv\\Scripts\\pip.exe"
    else:
        return ".venv/bin/pip"

def upgrade_pip():
    """升级pip到最新版本"""
    print("⬆️ 升级pip...")

    venv_pip = get_venv_pip()
    try:
        result = subprocess.run([
            venv_pip, "install", "--upgrade", "pip"
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"⚠️ pip升级警告: {result.stderr}")
        else:
            print("✅ pip升级成功")
    except Exception as e:
        print(f"❌ pip升级失败: {e}")

def install_requirements():
    """安装项目依赖"""
    print("📦 安装项目依赖...")

    venv_pip = get_venv_pip()
    requirements_file = "requirements-312.txt"

    if not Path(requirements_file).exists():
        print(f"❌ 依赖文件不存在: {requirements_file}")
        return False

    try:
        result = subprocess.run([
            venv_pip, "install", "-r", requirements_file
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ 依赖安装失败: {result.stderr}")
            return False

        print("✅ 依赖安装成功")
        return True
    except Exception as e:
        print(f"❌ 依赖安装异常: {e}")
        return False

def create_env_file():
    """创建环境变量文件"""
    print("📝 创建环境配置文件...")

    env_example = """# 智股通环境配置文件
# 请根据实际情况修改以下配置

# 应用基础配置
ENVIRONMENT=development
DEBUG=true
APP_NAME=智股通
VERSION=1.0.0

# 服务配置
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# 安全配置
SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 数据库配置
DATABASE_URL=sqlite:///./data/smart_stock.db

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# AI模型配置
GLM_API_KEY=your-glm-api-key
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/chat/completions
GLM_MODEL=glm-4.5-flash

# 数据源配置
AKSHARE_ENABLED=true
DATA_CACHE_TTL=300
BATCH_SIZE=1000
UPDATE_INTERVAL=60

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
"""

    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_example)
        print("✅ 环境配置文件创建成功")
        return True
    except Exception as e:
        print(f"❌ 环境配置文件创建失败: {e}")
        return False

def print_activation_instructions():
    """打印环境激活说明"""
    print("\n" + "="*60)
    print("🎉 Python环境配置完成！")
    print("="*60)

    if platform.system() == "Windows":
        print("请运行以下命令激活虚拟环境:")
        print("   .venv\\Scripts\\activate")
        print("或:")
        print("   .\\.venv\\Scripts\\activate")
    else:
        print("请运行以下命令激活虚拟环境:")
        print("   source .venv/bin/activate")

    print("\n激活后可以运行:")
    print("   cd backend && python main.py")
    print("="*60)

def main():
    """主函数"""
    print("🚀 开始配置Python 3.12开发环境...")
    print(f"   操作系统: {platform.system()} {platform.release()}")
    print(f"   工作目录: {os.getcwd()}")
    print()

    # 步骤检查
    steps = [
        ("Python版本检查", check_python_version),
        ("虚拟环境创建", create_virtual_environment),
        ("pip升级", upgrade_pip),
        ("依赖安装", install_requirements),
        ("环境配置", create_env_file),
    ]

    for step_name, step_func in steps:
        print(f"📋 执行步骤: {step_name}")
        if not step_func():
            print(f"❌ {step_name}失败，终止配置")
            return False
        print()

    print_activation_instructions()
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)