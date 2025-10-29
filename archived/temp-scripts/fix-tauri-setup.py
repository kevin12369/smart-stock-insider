#!/usr/bin/env python3
"""
Tauri安装修复脚本
确保Tauri正确配置在workspaces环境中
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description, timeout=60):
    """运行命令并显示结果"""
    print(f"\n🔧 {description}")
    print(f"执行: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        if result.returncode == 0:
            print("✅ 成功")
            if result.stdout.strip() and len(result.stdout) < 300:
                print(f"输出: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ 失败 (退出码: {result.returncode})")
            if result.stderr and len(result.stderr) < 300:
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
    print("🚀 Tauri安装修复器")
    print("=" * 50)

    # 1. 检查项目结构
    print("\n📂 检查项目结构")
    structure_files = [
        ("package.json", "根目录package.json"),
        ("frontend/package.json", "前端package.json"),
        ("frontend/src-tauri/tauri.conf.json", "Tauri配置文件"),
        ("frontend/src-tauri/Cargo.toml", "Rust配置文件"),
    ]

    structure_ok = sum(1 for file_path, desc in structure_files if check_file_exists(file_path, desc))

    # 2. 检查npm workspaces状态
    print(f"\n🔍 检查npm workspaces状态")
    workspaces_ok = run_command("npm ls --depth=1", "检查workspaces依赖")

    # 3. 检查Tauri CLI
    print(f"\n🛠️ 检查Tauri CLI")
    tauri_cli_ok = run_command("npx tauri --version", "检查Tauri CLI版本")

    # 4. 检查Tauri info
    print(f"\n📊 Tauri信息检查")
    tauri_info_ok = run_command("cd frontend && npx tauri info", "获取Tauri详细信息", timeout=30)

    # 5. 检查Rust环境（可选）
    print(f"\n🦀 检查Rust环境")
    rust_check = run_command("rustc --version", "检查Rust编译器")

    # 6. 如果Tauri有问题，尝试修复
    if not tauri_info_ok:
        print(f"\n🔨 尝试修复Tauri配置")

        # 确保Tauri CLI安装
        run_command("npm install --save-dev @tauri-apps/cli", "确保Tauri CLI安装")

        # 重新生成Tauri配置（如果需要）
        if not Path("frontend/src-tauri/Cargo.toml").exists():
            print("重新初始化Tauri项目...")
            run_command("cd frontend && npx tauri init", "重新初始化Tauri")

        # 再次检查
        tauri_info_ok = run_command("cd frontend && npx tauri info", "重新检查Tauri信息", timeout=30)

    # 总结
    print(f"\n📊 修复结果总结:")
    print(f"  项目结构: {structure_ok}/{len(structure_files)} ✅")
    print(f"  Workspaces状态: {'✅' if workspaces_ok else '❌'}")
    print(f"  Tauri CLI: {'✅' if tauri_cli_ok else '❌'}")
    print(f"  Tauri配置: {'✅' if tauri_info_ok else '❌'}")
    print(f"  Rust环境: {'✅' if rust_check else '⚠️ (可选)'}")

    # 成功判断
    critical_ok = structure_ok >= 3 and workspaces_ok and tauri_cli_ok

    if critical_ok and tauri_info_ok:
        print(f"\n🎉 Tauri配置完全正常！")
        print(f"\n📝 可以执行的命令:")
        print(f"  npm run dev:frontend  # 启动前端开发")
        print(f"  npm run dev           # 启动完整项目")
        print(f"  cd frontend && npx tauri dev  # 直接启动Tauri")
        return True
    elif critical_ok:
        print(f"\n⚠️ Tauri基本配置正常，但可能需要进一步检查")
        print(f"\n📝 建议尝试:")
        print(f"  cd frontend && npx tauri dev")
        return True
    else:
        print(f"\n❌ Tauri配置存在问题")
        print(f"\n📝 建议手动修复:")
        if structure_ok < 3:
            print(f"  - 检查项目文件是否完整")
        if not workspaces_ok:
            print(f"  - 运行 npm install 重新安装依赖")
        if not tauri_cli_ok:
            print(f"  - 运行 npm install -g @tauri-apps/cli")
        return False

if __name__ == "__main__":
    success = main()
    print(f"\n{'='*50}")
    if success:
        print("✅ Tauri修复完成，可以启动开发！")
    else:
        print("❌ 需要手动解决部分问题")
    sys.exit(0 if success else 1)