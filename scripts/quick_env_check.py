#!/usr/bin/env python3
"""
快速环境检查脚本 - Windows兼容版本

Author: Smart Stock Insider Team
Version: 1.0.0
"""

import sys
import subprocess
from pathlib import Path

def run_command(cmd):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def check_python():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    print(f"当前版本: {version.major}.{version.minor}.{version.micro}")

    if version.major == 3 and version.minor >= 12:
        print("✓ Python版本兼容")
        return True
    else:
        print("✗ 需要Python 3.12+")
        return False

def check_virtual_env():
    """检查虚拟环境"""
    print("\n检查虚拟环境...")

    venv_path = Path(".venv")
    if not venv_path.exists():
        print("✗ 虚拟环境不存在")
        return False

    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ 虚拟环境已激活")
        return True
    else:
        print("✗ 虚拟环境未激活")
        return False

def check_node():
    """检查Node.js"""
    print("\n检查Node.js...")

    success, output, error = run_command("node --version")
    if success:
        print(f"✓ Node.js版本: {output}")
        return True
    else:
        print("✗ Node.js未安装")
        return False

def check_npm():
    """检查npm"""
    print("检查npm...")

    success, output, error = run_command("npm --version")
    if success:
        print(f"✓ npm版本: {output}")
        return True
    else:
        print("✗ npm未安装")
        return False

def check_rust():
    """检查Rust"""
    print("\n检查Rust...")

    success, output, error = run_command("rustc --version")
    if success:
        print(f"✓ Rust版本: {output}")
        return True
    else:
        print("✗ Rust未安装")
        return False

def check_redis():
    """检查Redis服务"""
    print("\n检查Redis...")

    success, output, error = run_command("redis-cli ping")
    if success and "PONG" in output:
        print("✓ Redis服务运行正常")
        return True
    else:
        print("✗ Redis服务未运行")
        return False

def check_project_files():
    """检查项目文件"""
    print("\n检查项目文件...")

    required_files = [
        "requirements-312.txt",
        "backend/main.py",
        "backend/core/config.py",
        "frontend/package.json",
        "frontend/src-tauri/Cargo.toml"
    ]

    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path}")
            all_exist = False

    return all_exist

def main():
    """主函数"""
    print("智股通项目环境检查")
    print("=" * 40)

    checks = [
        ("Python版本", check_python),
        ("虚拟环境", check_virtual_env),
        ("Node.js", check_node),
        ("npm", check_npm),
        ("Rust", check_rust),
        ("Redis", check_redis),
        ("项目文件", check_project_files)
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ {name}检查失败: {e}")
            results.append((name, False))

    # 总结
    print("\n" + "=" * 40)
    print("检查总结:")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"通过: {passed}/{total}")

    for name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {name}")

    if passed == total:
        print("\n🎉 环境检查通过！")
    else:
        print("\n⚠️ 存在环境问题，请按指南修复")

    print("\n下一步操作:")
    if not results[1][1]:  # 虚拟环境
        print("1. 运行: python scripts/setup_python_env.py")
        print("2. 激活虚拟环境")

    if passed == total:
        print("3. 运行: npm run dev")
    else:
        print("3. 修复问题后重新检查")

if __name__ == "__main__":
    main()