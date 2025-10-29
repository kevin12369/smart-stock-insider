#!/usr/bin/env python3
"""
测试运行脚本
提供各种测试运行选项和报告生成
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Optional

def run_command(cmd: List[str], description: str) -> bool:
    """运行命令并返回结果"""
    print(f"\n{'='*60}")
    print(f"运行: {description}")
    print(f"命令: {' '.join(cmd)}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} - 成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - 失败 (退出码: {e.returncode})")
        return False

def run_unit_tests(verbose: bool = False, coverage: bool = True) -> bool:
    """运行单元测试"""
    cmd = ["python", "-m", "pytest", "tests/unit", "-m", "unit"]

    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend([
            "--cov=backend",
            "--cov-report=html:htmlcov/unit",
            "--cov-report=term-missing",
            "--cov-report=xml:coverage-unit.xml",
            "--cov-fail-under=80"
        ])

    return run_command(cmd, "单元测试")

def run_integration_tests(verbose: bool = False) -> bool:
    """运行集成测试"""
    cmd = ["python", "-m", "pytest", "tests/integration", "-m", "integration"]

    if verbose:
        cmd.append("-v")

    return run_command(cmd, "集成测试")

def run_e2e_tests(verbose: bool = False) -> bool:
    """运行端到端测试"""
    cmd = ["python", "-m", "pytest", "tests/e2e", "-m", "e2e"]

    if verbose:
        cmd.append("-v")

    return run_command(cmd, "端到端测试")

def run_performance_tests(verbose: bool = False) -> bool:
    """运行性能测试"""
    cmd = ["python", "-m", "pytest", "tests/performance", "-m", "performance"]

    if verbose:
        cmd.append("-v")

    return run_command(cmd, "性能测试")

def run_ai_tests(verbose: bool = False) -> bool:
    """运行AI相关测试"""
    cmd = ["python", "-m", "pytest", "-m", "ai"]

    if verbose:
        cmd.append("-v")

    return run_command(cmd, "AI功能测试")

def run_api_tests(verbose: bool = False) -> bool:
    """运行API测试"""
    cmd = ["python", "-m", "pytest", "-m", "api"]

    if verbose:
        cmd.append("-v")

    return run_command(cmd, "API接口测试")

def run_all_tests(verbose: bool = False, coverage: bool = True) -> bool:
    """运行所有测试"""
    print("\n🚀 开始运行所有测试...")

    test_functions = [
        (run_unit_tests, "单元测试"),
        (run_integration_tests, "集成测试"),
        (run_ai_tests, "AI功能测试"),
        (run_api_tests, "API接口测试")
    ]

    all_passed = True

    for test_func, test_name in test_functions:
        if not test_func(verbose=verbose, coverage=coverage):
            all_passed = False
            print(f"\n⚠️ {test_name}失败，继续运行其他测试...")

    return all_passed

def run_slow_tests(verbose: bool = False) -> bool:
    """运行慢速测试"""
    cmd = ["python", "-m", "pytest", "-m", "slow"]

    if verbose:
        cmd.append("-v")

    return run_command(cmd, "慢速测试")

def generate_test_report() -> bool:
    """生成测试报告"""
    print("\n📊 生成测试报告...")

    # 合并覆盖率报告
    cmd_merge = [
        "python", "-m", "coverage", "combine",
        "coverage-unit.xml",
        "coverage-integration.xml",
        "coverage-e2e.xml"
    ]

    # 生成HTML报告
    cmd_html = [
        "python", "-m", "coverage", "html",
        "--directory=htmlcov/combined"
    ]

    # 生成XML报告
    cmd_xml = [
        "python", "-m", "coverage", "xml",
        "--outfile=coverage-combined.xml"
    ]

    success = True

    if not run_command(cmd_merge, "合并覆盖率报告"):
        success = False

    if not run_command(cmd_html, "生成HTML覆盖率报告"):
        success = False

    if not run_command(cmd_xml, "生成XML覆盖率报告"):
        success = False

    return success

def check_code_quality() -> bool:
    """检查代码质量"""
    print("\n🔍 检查代码质量...")

    quality_checks = [
        (["python", "-m", "flake8", "backend/"], "Flake8代码风格检查"),
        (["python", "-m", "black", "--check", "backend/"], "Black代码格式检查"),
        (["python", "-m", "isort", "--check-only", "backend/"], "isort导入排序检查"),
        (["python", "-m", "mypy", "backend/"], "MyPy类型检查"),
        (["python", "-m", "bandit", "-r", "backend/"], "Bandit安全检查")
    ]

    all_passed = True

    for cmd, check_name in quality_checks:
        try:
            run_command(cmd, check_name)
        except Exception:
            print(f"⚠️ {check_name}发现问题")
            all_passed = False

    return all_passed

def cleanup_test_artifacts() -> bool:
    """清理测试产物"""
    print("\n🧹 清理测试产物...")

    cleanup_commands = [
        (["rm", "-rf", ".pytest_cache"], "清理pytest缓存"),
        (["rm", "-rf", "__pycache__"], "清理Python缓存"),
        (["rm", "-rf", ".coverage"], "清理覆盖率文件"),
        (["rm", "-rf", "htmlcov"], "清理HTML报告"),
        (["rm", "-rf", "*.xml"], "清理XML报告"),
        (["find", ".", "-name", "*.pyc", "-delete"], "清理编译文件"),
        (["find", ".", "-name", "*.pyo", "-delete"], "清理优化文件")
    ]

    for cmd, desc in cleanup_commands:
        try:
            subprocess.run(cmd, check=False, capture_output=True)
        except Exception:
            pass  # 忽略错误，某些文件可能不存在

    print("✅ 测试产物清理完成")
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="智能投研项目测试运行器")

    parser.add_argument(
        "test_type",
        choices=["unit", "integration", "e2e", "performance", "ai", "api", "all", "slow"],
        help="测试类型"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="详细输出"
    )

    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="不生成覆盖率报告"
    )

    parser.add_argument(
        "--quality",
        action="store_true",
        help="运行代码质量检查"
    )

    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="清理测试产物"
    )

    parser.add_argument(
        "--report",
        action="store_true",
        help="生成测试报告"
    )

    args = parser.parse_args()

    # 确保在项目根目录
    os.chdir(Path(__file__).parent.parent)

    success = True

    # 清理旧产物
    if args.cleanup:
        cleanup_test_artifacts()

    # 运行测试
    if args.test_type == "unit":
        success = run_unit_tests(verbose=args.verbose, coverage=not args.no_coverage)
    elif args.test_type == "integration":
        success = run_integration_tests(verbose=args.verbose)
    elif args.test_type == "e2e":
        success = run_e2e_tests(verbose=args.verbose)
    elif args.test_type == "performance":
        success = run_performance_tests(verbose=args.verbose)
    elif args.test_type == "ai":
        success = run_ai_tests(verbose=args.verbose)
    elif args.test_type == "api":
        success = run_api_tests(verbose=args.verbose)
    elif args.test_type == "all":
        success = run_all_tests(verbose=args.verbose, coverage=not args.no_coverage)
    elif args.test_type == "slow":
        success = run_slow_tests(verbose=args.verbose)

    # 代码质量检查
    if args.quality and success:
        quality_success = check_code_quality()
        success = success and quality_success

    # 生成报告
    if args.report and success:
        report_success = generate_test_report()
        success = success and report_success

    # 输出结果
    if success:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()