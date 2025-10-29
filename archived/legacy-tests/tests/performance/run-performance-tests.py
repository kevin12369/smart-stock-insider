#!/usr/bin/env python3
"""
性能测试运行脚本
自动化运行不同类型的性能测试并生成报告
"""

import argparse
import subprocess
import os
import sys
import json
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('performance_tests.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PerformanceTestRunner:
    """性能测试运行器"""

    def __init__(self, config_file: str = "locust.conf"):
        self.config_file = config_file
        self.results_dir = Path("results")
        self.reports_dir = Path("reports")
        self.test_results = {}

        # 确保目录存在
        self.results_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

    def run_test(self, test_name: str, test_config: Dict[str, Any]) -> bool:
        """运行单个性能测试"""
        logger.info(f"Starting performance test: {test_name}")

        # 构建Locust命令
        cmd = self._build_locust_command(test_name, test_config)

        try:
            # 记录开始时间
            start_time = time.time()

            # 运行测试
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=test_config.get('run-time', 300) + 60  # 额外60秒超时
            )

            # 记录结束时间
            end_time = time.time()
            duration = end_time - start_time

            # 处理结果
            success = self._process_test_result(test_name, result, duration)

            if success:
                logger.info(f"Test {test_name} completed successfully in {duration:.2f} seconds")
            else:
                logger.error(f"Test {test_name} failed")

            return success

        except subprocess.TimeoutExpired:
            logger.error(f"Test {test_name} timed out")
            return False
        except Exception as e:
            logger.error(f"Error running test {test_name}: {str(e)}")
            return False

    def _build_locust_command(self, test_name: str, test_config: Dict[str, Any]) -> str:
        """构建Locust命令"""
        cmd_parts = ["locust"]

        # 基础参数
        cmd_parts.extend([
            "--config", self.config_file,
            "--host", test_config.get("host", "http://localhost:8000"),
            "--users", str(test_config.get("users", 10)),
            "--spawn-rate", str(test_config.get("spawn-rate", 2)),
            "--run-time", f"{test_config.get('run-time', 60)}s",
            "--html-report", f"{self.reports_dir}/{test_name}_report.html",
            "--csv", f"{self.results_dir}/{test_name}_stats",
            "--loglevel", test_config.get("loglevel", "INFO"),
            "--logfile", f"{self.results_dir}/{test_name}.log"
        ])

        # 用户类配置
        if "user_classes" in test_config:
            user_classes = test_config["user_classes"]
            if isinstance(user_classes, list):
                cmd_parts.extend(["--user-class", ",".join(user_classes)])

            if "ratio" in test_config:
                cmd_parts.extend(["--user-ratio", ",".join(test_config["ratio"])])

        # 其他参数
        if test_config.get("print_stats", True):
            cmd_parts.append("--print-stats")

        if test_config.get("headless", True):
            cmd_parts.append("--headless")

        # 峰值测试特殊配置
        if test_name == "spike-test":
            spike_config = test_config.get("spike", {})
            if spike_config:
                cmd_parts.extend([
                    "--spike-users", str(spike_config.get("users", 100)),
                    "--spike-spawn-rate", str(spike_config.get("spawn-rate", 20)),
                    "--spike-duration", f"{spike_config.get('duration', 60)}s",
                    "--spike-wait", f"{spike_config.get('wait', 30)}s"
                ])

        return " ".join(cmd_parts)

    def _process_test_result(self, test_name: str, result: subprocess.CompletedProcess, duration: float) -> bool:
        """处理测试结果"""
        self.test_results[test_name] = {
            "return_code": result.returncode,
            "duration": duration,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timestamp": datetime.now().isoformat()
        }

        # 保存详细结果
        self._save_test_result(test_name, result)

        # 检查是否成功
        if result.returncode == 0:
            # 生成测试摘要
            self._generate_test_summary(test_name, result.stdout)
            return True
        else:
            logger.error(f"Test failed with return code {result.returncode}")
            logger.error(f"STDERR: {result.stderr}")
            return False

    def _save_test_result(self, test_name: str, result: subprocess.CompletedProcess):
        """保存测试结果"""
        result_file = self.results_dir / f"{test_name}_result.json"

        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results[test_name], f, indent=2, ensure_ascii=False)

    def _generate_test_summary(self, test_name: str, stdout: str):
        """生成测试摘要"""
        summary_file = self.reports_dir / f"{test_name}_summary.txt"

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"Performance Test Summary: {test_name}\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Test completed at: {datetime.now().isoformat()}\n")
            f.write(f"Duration: {self.test_results[test_name]['duration']:.2f} seconds\n\n")
            f.write("Locust Output:\n")
            f.write("-" * 20 + "\n")
            f.write(stdout)

    def run_all_tests(self) -> bool:
        """运行所有预定义的测试"""
        logger.info("Starting all performance tests")

        test_configs = self._get_test_configs()
        all_success = True

        for test_name, config in test_configs.items():
            success = self.run_test(test_name, config)
            if not success:
                all_success = False
                logger.error(f"Test {test_name} failed")

            # 测试间隔
            if test_name != list(test_configs.keys())[-1]:
                logger.info("Waiting 30 seconds before next test...")
                time.sleep(30)

        # 生成综合报告
        self._generate_comprehensive_report()

        return all_success

    def _get_test_configs(self) -> Dict[str, Dict[str, Any]]:
        """获取测试配置"""
        return {
            "baseline-test": {
                "users": 10,
                "spawn-rate": 2,
                "run-time": 60,
                "user_classes": ["StockInsiderUser"],
                "loglevel": "INFO",
                "print_stats": True,
                "headless": True
            },
            "load-test": {
                "users": 50,
                "spawn-rate": 5,
                "run-time": 180,
                "user_classes": ["StockInsiderUser", "MobileUser"],
                "ratio": ["0.8", "0.2"],
                "loglevel": "INFO",
                "print_stats": True,
                "headless": True
            },
            "stress-test": {
                "users": 200,
                "spawn-rate": 20,
                "run-time": 300,
                "user_classes": ["StockInsiderUser", "PowerUser", "MobileUser"],
                "ratio": ["0.6", "0.3", "0.1"],
                "loglevel": "INFO",
                "print_stats": True,
                "headless": True
            },
            "soak-test": {
                "users": 30,
                "spawn-rate": 3,
                "run-time": 1800,  # 30分钟
                "user_classes": ["StockInsiderUser"],
                "loglevel": "INFO",
                "print_stats": False,  # 长时间测试不打印统计
                "headless": True
            },
            "spike-test": {
                "users": 5,
                "spawn-rate": 1,
                "run-time": 60,
                "user_classes": ["StockInsiderUser"],
                "spike": {
                    "users": 300,
                    "spawn-rate": 50,
                    "duration": 60,
                    "wait": 30
                },
                "loglevel": "INFO",
                "print_stats": True,
                "headless": True
            }
        }

    def _generate_comprehensive_report(self):
        """生成综合性能测试报告"""
        report_file = self.reports_dir / "comprehensive_performance_report.html"

        html_content = self._build_html_report()

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"Comprehensive report generated: {report_file}")

    def _build_html_report(self) -> str:
        """构建HTML报告"""
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>智股通性能测试报告</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: #1890ff;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .test-summary {{
            background-color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .status-success {{
            color: #52c41a;
            font-weight: bold;
        }}
        .status-failure {{
            color: #ff4d4f;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f0f0f0;
        }}
        .report-links {{
            text-align: center;
            margin: 20px 0;
        }}
        .report-links a {{
            display: inline-block;
            margin: 5px 10px;
            padding: 10px 20px;
            background-color: #1890ff;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>智股通性能测试报告</h1>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>

    <div class="test-summary">
        <h2>测试概览</h2>
        <table>
            <tr>
                <th>测试名称</th>
                <th>用户数</th>
                <th>持续时间(秒)</th>
                <th>状态</th>
                <th>报告</th>
            </tr>
"""

        for test_name, result in self.test_results.items():
            status = "成功" if result["return_code"] == 0 else "失败"
            status_class = "status-success" if result["return_code"] == 0 else "status-failure"

            html += f"""
            <tr>
                <td>{test_name}</td>
                <td>-</td>
                <td>{result["duration"]:.2f}</td>
                <td class="{status_class}">{status}</td>
                <td><a href="{test_name}_report.html" target="_blank">查看详情</a></td>
            </tr>
"""

        html += """
        </table>
    </div>

    <div class="report-links">
        <h3>详细报告</h3>
"""

        for test_name in self.test_results.keys():
            html += f'<a href="{test_name}_report.html" target="_blank">{test_name}报告</a>'

        html += """
    </div>

    <div class="test-summary">
        <h2>测试建议</h2>
        <ul>
            <li>查看各个测试的详细报告，特别关注响应时间和错误率</li>
            <li>重点关注stress-test的结果，验证系统在高负载下的稳定性</li>
            <li>检查soak-test的长期运行情况，确保系统无内存泄漏</li>
            <li>对比不同用户类型的行为模式和资源消耗</li>
        </ul>
    </div>
</body>
</html>
"""
        return html

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="智股通性能测试运行器")
    parser.add_argument(
        "--test",
        choices=["baseline-test", "load-test", "stress-test", "soak-test", "spike-test", "all"],
        default="all",
        help="要运行的测试类型"
    )
    parser.add_argument(
        "--config",
        default="locust.conf",
        help="Locust配置文件路径"
    )
    parser.add_argument(
        "--host",
        default="http://localhost:8000",
        help="目标服务主机地址"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="无界面模式运行"
    )

    args = parser.parse_args()

    # 检查依赖
    try:
        subprocess.run(["locust", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("Locust未安装，请先安装: pip install locust")
        sys.exit(1)

    # 检查locustfile
    if not os.path.exists("locustfile.py"):
        logger.error("locustfile.py不存在，请确保在正确的目录中运行")
        sys.exit(1)

    # 运行测试
    runner = PerformanceTestRunner(args.config)

    if args.test == "all":
        success = runner.run_all_tests()
    else:
        test_configs = runner._get_test_configs()
        if args.test in test_configs:
            config = test_configs[args.test]
            if args.host:
                config["host"] = args.host
            if args.headless:
                config["headless"] = True
            success = runner.run_test(args.test, config)
        else:
            logger.error(f"未知的测试类型: {args.test}")
            sys.exit(1)

    # 设置退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()