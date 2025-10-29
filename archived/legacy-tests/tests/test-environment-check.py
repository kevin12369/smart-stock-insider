#!/usr/bin/env python3
"""
智股通项目测试环境检查器
快速验证测试环境和依赖的可用性
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path

class TestEnvironmentChecker:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.results = {
            'python_packages': {},
            'node_packages': {},
            'test_files': {},
            'config_files': {},
            'overall_status': 'UNKNOWN'
        }

    def check_python_packages(self):
        """检查Python依赖包"""
        packages = ['locust', 'requests', 'configparser']

        print("🐍 Python包检查:")
        for package in packages:
            try:
                module = importlib.import_module(package)
                version = getattr(module, '__version__', 'UNKNOWN')
                self.results['python_packages'][package] = {'status': '✅', 'version': version}
                print(f"  {package}: ✅ {version}")
            except ImportError as e:
                self.results['python_packages'][package] = {'status': '❌', 'error': str(e)}
                print(f"  {package}: ❌ 未安装")

    def check_test_files(self):
        """检查测试文件是否存在"""
        print("\n📁 测试文件检查:")

        test_files = [
            'tests/performance/locustfile.py',
            'tests/performance/run-performance-tests.py',
            'tests/performance/frontend-performance.spec.ts',
            'tests/e2e/playwright.config.ts',
            'tests/e2e/helpers/test-helpers.ts',
            'tests/e2e/fixtures/test-data.ts',
            'tests/e2e/tests/dashboard.spec.ts',
            'tests/e2e/tests/ai-analysis.spec.ts',
            'tests/reports/generate-test-report.py'
        ]

        for file_path in test_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.results['test_files'][file_path] = {'status': '✅', 'path': str(full_path)}
                print(f"  {file_path}: ✅")
            else:
                self.results['test_files'][file_path] = {'status': '❌', 'path': str(full_path)}
                print(f"  {file_path}: ❌ 不存在")

    def check_config_files(self):
        """检查配置文件"""
        print("\n⚙️ 配置文件检查:")

        config_files = [
            'tests/performance/locust.conf',
            'frontend/package.json',
            'frontend/vite.config.ts',
            'frontend/tsconfig.json'
        ]

        for file_path in config_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                try:
                    size = full_path.stat().st_size
                    self.results['config_files'][file_path] = {'status': '✅', 'size': size}
                    print(f"  {file_path}: ✅ ({size} bytes)")
                except Exception as e:
                    self.results['config_files'][file_path] = {'status': '⚠️', 'error': str(e)}
                    print(f"  {file_path}: ⚠️ {e}")
            else:
                self.results['config_files'][file_path] = {'status': '❌', 'path': str(full_path)}
                print(f"  {file_path}: ❌ 不存在")

    def check_locust_functionality(self):
        """检查Locust基本功能"""
        print("\n🚀 Locust功能检查:")

        try:
            # 检查locustfile.py语法
            locustfile_path = self.project_root / 'tests/performance/locustfile.py'
            if locustfile_path.exists():
                result = subprocess.run([
                    sys.executable, '-m', 'py_compile', str(locustfile_path)
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    print("  locustfile.py语法: ✅")
                    self.results['locust_syntax'] = '✅'
                else:
                    print(f"  locustfile.py语法: ❌ {result.stderr}")
                    self.results['locust_syntax'] = '❌'

            # 检查性能测试脚本
            script_path = self.project_root / 'tests/performance/run-performance-tests.py'
            if script_path.exists():
                result = subprocess.run([
                    sys.executable, str(script_path), '--help'
                ], capture_output=True, text=True)

                if result.returncode == 0 and 'usage:' in result.stdout:
                    print("  性能测试脚本: ✅")
                    self.results['performance_script'] = '✅'
                else:
                    print("  性能测试脚本: ❌")
                    self.results['performance_script'] = '❌'

        except Exception as e:
            print(f"  Locust功能检查异常: ⚠️ {e}")
            self.results['locust_functionality'] = '⚠️'

    def check_report_generation(self):
        """检查报告生成功能"""
        print("\n📊 报告生成检查:")

        try:
            report_script = self.project_root / 'tests/reports/generate-test-report.py'
            if report_script.exists():
                result = subprocess.run([
                    sys.executable, str(report_script), '--help'
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    print("  报告生成脚本: ✅")
                    self.results['report_generation'] = '✅'
                else:
                    print("  报告生成脚本: ❌")
                    self.results['report_generation'] = '❌'
        except Exception as e:
            print(f"  报告生成检查异常: ⚠️ {e}")
            self.results['report_generation'] = '⚠️'

    def generate_summary(self):
        """生成检查摘要"""
        print("\n" + "="*50)
        print("📋 测试环境检查摘要")
        print("="*50)

        # 统计各项目状态
        python_ok = sum(1 for item in self.results['python_packages'].values() if '✅' in item['status'])
        python_total = len(self.results['python_packages'])

        files_ok = sum(1 for item in self.results['test_files'].values() if '✅' in item['status'])
        files_total = len(self.results['test_files'])

        configs_ok = sum(1 for item in self.results['config_files'].values() if '✅' in item['status'])
        configs_total = len(self.results['config_files'])

        print(f"🐍 Python包: {python_ok}/{python_total} 通过")
        print(f"📁 测试文件: {files_ok}/{files_total} 存在")
        print(f"⚙️ 配置文件: {configs_ok}/{configs_total} 正常")

        # 计算总体状态
        total_items = python_total + files_total + configs_total
        ok_items = python_ok + files_ok + configs_ok
        success_rate = (ok_items / total_items) * 100 if total_items > 0 else 0

        if success_rate >= 90:
            overall_status = "🎉 优秀"
            color = "绿色"
        elif success_rate >= 75:
            overall_status = "✅ 良好"
            color = "蓝色"
        elif success_rate >= 50:
            overall_status = "⚠️ 一般"
            color = "黄色"
        else:
            overall_status = "❌ 需要修复"
            color = "红色"

        print(f"\n🎯 总体状态: {overall_status} ({success_rate:.1f}%)")

        # 给出建议
        print("\n💡 建议:")
        if python_ok < python_total:
            print("  - 安装缺失的Python包: pip install <package_name>")
        if files_ok < files_total:
            print("  - 检查缺失的测试文件")
        if configs_ok < configs_total:
            print("  - 检查配置文件格式和内容")

        if success_rate >= 90:
            print("  🚀 测试环境准备就绪，可以开始执行测试")
        elif success_rate >= 75:
            print("  🔧 测试环境基本就绪，建议修复小问题后开始测试")
        else:
            print("  ⚠️ 测试环境需要进一步配置才能开始测试")

        return success_rate

def main():
    """主函数"""
    print("🔍 智股通项目测试环境检查器")
    print("="*50)

    checker = TestEnvironmentChecker()

    # 执行各项检查
    checker.check_python_packages()
    checker.check_test_files()
    checker.check_config_files()
    checker.check_locust_functionality()
    checker.check_report_generation()

    # 生成摘要
    success_rate = checker.generate_summary()

    return success_rate

if __name__ == "__main__":
    success_rate = main()
    sys.exit(0 if success_rate >= 75 else 1)