#!/usr/bin/env python3
"""
智股通项目快速启动验证脚本
验证前端和后端环境是否配置正确
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description, timeout=30):
    """运行命令并显示结果"""
    print(f"\n🔍 {description}")
    print(f"执行: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            print("✅ 成功")
            if result.stdout.strip() and len(result.stdout) < 200:
                print(f"输出: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ 失败 (退出码: {result.returncode})")
            if result.stderr and len(result.stderr) < 200:
                print(f"错误: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print("⏰ 超时")
        return False
    except Exception as e:
        print(f"❌ 异常: {e}")
        return False

def check_file_exists(file_path, description):
    """检查文件是否存在"""
    print(f"\n📁 {description}")
    if Path(file_path).exists():
        print(f"✅ {file_path} 存在")
        return True
    else:
        print(f"❌ {file_path} 不存在")
        return False

def main():
    """主函数"""
    print("🚀 智股通项目启动验证")
    print("=" * 50)

    # 检查项目结构
    print("\n📂 项目结构检查")
    structure_checks = [
        ("package.json", "根目录package.json"),
        ("frontend/package.json", "前端package.json"),
        ("frontend/src-tauri/tauri.conf.json", "Tauri配置文件"),
        ("backend/main.py", "后端主文件"),
        ("backend/core/config.py", "后端配置文件"),
        ("backend/requirements.txt", "后端依赖文件"),
    ]

    structure_ok = sum(1 for file_path, desc in structure_checks if check_file_exists(file_path, desc))

    # 检查Node.js环境
    print("\n🟢 Node.js环境检查")
    node_checks = [
        ("node --version", "Node.js版本"),
        ("npm --version", "npm版本"),
        ("npm ls", "npm workspaces状态"),
    ]

    node_ok = sum(1 for cmd, desc in node_checks if run_command(cmd, desc))

    # 检查前端环境
    print("\n🔵 前端环境检查")
    frontend_checks = [
        ("npx tauri --version", "Tauri CLI版本"),
        ("cd frontend && npx tauri info", "Tauri配置信息"),
    ]

    frontend_ok = sum(1 for cmd, desc in frontend_checks if run_command(cmd, desc))

    # 检查Python环境
    print("\n🟣 Python环境检查")
    python_checks = [
        ("python --version", "Python版本"),
        ("pip --version", "pip版本"),
    ]

    python_ok = sum(1 for cmd, desc in python_checks if run_command(cmd, desc))

    # 检查后端依赖
    print("\n🔴 后端依赖检查")
    backend_commands = [
        ("cd backend && python install_dependencies.py", "安装后端依赖"),
    ]

    backend_ok = sum(1 for cmd, desc in backend_commands if run_command(cmd, desc, timeout=120))

    # 配置验证
    print("\n⚙️ 配置验证")
    config_checks = [
        ("cd frontend && npx tauri info", "Tauri配置验证"),
    ]

    config_ok = sum(1 for cmd, desc in config_checks if run_command(cmd, desc))

    # 总结
    print(f"\n📊 验证结果总结:")
    print(f"  项目结构: {structure_ok}/{len(structure_checks)} ✅")
    print(f"  Node.js环境: {node_ok}/{len(node_checks)} ✅")
    print(f"  前端环境: {frontend_ok}/{len(frontend_checks)} ✅")
    print(f"  Python环境: {python_ok}/{len(python_checks)} ✅")
    print(f"  后端依赖: {backend_ok}/{len(backend_commands)} ✅")
    print(f"  配置验证: {config_ok}/{len(config_commands)} ✅")

    total_checks = len(structure_checks) + len(node_checks) + len(frontend_checks) + len(python_checks) + len(backend_commands) + len(config_checks)
    total_ok = structure_ok + node_ok + frontend_ok + python_ok + backend_ok + config_ok
    success_rate = (total_ok / total_checks) * 100

    print(f"\n🎯 总体成功率: {success_rate:.1f}%")

    if success_rate >= 80:
        print("\n🎉 环境配置基本完成！")
        print("\n📝 下一步建议:")
        print("  1. 运行 npm run dev 启动完整项目")
        print("  2. 或者单独启动:")
        print("     - 前端: npm run dev:frontend")
        print("     - 后端: cd backend && python main.py")
        return True
    else:
        print("\n⚠️ 环境配置存在问题，请检查上述失败项目")
        print("\n📝 修复建议:")
        if node_ok < len(node_checks):
            print("  - 安装Node.js和npm")
        if frontend_ok < len(frontend_checks):
            print("  - 运行 npm install 安装前端依赖")
        if python_ok < len(python_checks):
            print("  - 安装Python 3.8+")
        if backend_ok < len(backend_commands):
            print("  - 检查Python环境和pip配置")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n{'='*50}")
    print("验证完成！" if success else "请修复问题后重新验证！")
    sys.exit(0 if success else 1)