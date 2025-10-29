#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的测试环境检查器
"""

import sys
import os
import importlib
from pathlib import Path

def main():
    print("智股通项目测试环境检查")
    print("=" * 40)

    project_root = Path(__file__).parent.parent

    # 检查Python包
    print("\n1. Python包检查:")
    packages = ['locust', 'requests']
    for package in packages:
        try:
            module = importlib.import_module(package)
            version = getattr(module, '__version__', 'UNKNOWN')
            print(f"   {package}: OK (v{version})")
        except ImportError:
            print(f"   {package}: NOT INSTALLED")

    # 检查测试文件
    print("\n2. 测试文件检查:")
    test_files = [
        'tests/performance/locustfile.py',
        'tests/performance/run-performance-tests.py',
        'tests/e2e/playwright.config.ts',
        'tests/reports/generate-test-report.py'
    ]

    for file_path in test_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"   {file_path}: EXISTS")
        else:
            print(f"   {file_path}: MISSING")

    # 检查Locust功能
    print("\n3. Locust功能检查:")
    try:
        import locust
        print(f"   Locust导入: OK (v{locust.__version__})")

        # 检查locustfile语法
        locustfile_path = project_root / 'tests/performance/locustfile.py'
        if locustfile_path.exists():
            with open(locustfile_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'class StockInsiderUser' in content:
                    print("   locustfile.py内容: OK")
                else:
                    print("   locustfile.py内容: MISSING USER CLASS")

    except Exception as e:
        print(f"   Locust功能: ERROR - {e}")

    # 检查前端配置
    print("\n4. 前端配置检查:")
    frontend_configs = [
        'frontend/package.json',
        'frontend/vite.config.ts'
    ]

    for config_path in frontend_configs:
        full_path = project_root / config_path
        if full_path.exists():
            print(f"   {config_path}: EXISTS")
        else:
            print(f"   {config_path}: MISSING")

    print("\n" + "=" * 40)
    print("检查完成！")

    # 给出简单建议
    print("\n建议:")
    print("- 如果看到NOT INSTALLED，请运行: pip install <package_name>")
    print("- 如果看到MISSING，请确认文件是否存在")
    print("- 如果所有项目都正常，可以开始进行测试验证")

if __name__ == "__main__":
    main()