#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版Tauri检查脚本
"""

import subprocess
import sys
import os

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"\n{description}")
    print(f"Command: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print("SUCCESS")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()[:200]}")
            return True
        else:
            print(f"FAILED (code: {result.returncode})")
            if result.stderr.strip():
                print(f"Error: {result.stderr.strip()[:200]}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print("Tauri Setup Checker")
    print("=" * 50)

    # 检查npm workspaces
    print("\n1. Checking npm workspaces:")
    workspaces_ok = run_command("npm ls --depth=0", "Check workspaces")

    # 检查Tauri CLI
    print("\n2. Checking Tauri CLI:")
    tauri_cli_ok = run_command("npx tauri --version", "Check Tauri CLI")

    # 检查Tauri info
    print("\n3. Checking Tauri info:")
    tauri_info_ok = run_command("cd frontend && npx tauri info", "Check Tauri info")

    # 总结
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"  Workspaces: {'OK' if workspaces_ok else 'FAIL'}")
    print(f"  Tauri CLI: {'OK' if tauri_cli_ok else 'FAIL'}")
    print(f"  Tauri Info: {'OK' if tauri_info_ok else 'FAIL'}")

    if workspaces_ok and tauri_cli_ok:
        print("\nRESULT: Tauri is properly installed!")
        print("\nYou can run:")
        print("  npm run dev:frontend")
        print("  npm run dev")
        return True
    else:
        print("\nRESULT: Issues found with Tauri setup")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)