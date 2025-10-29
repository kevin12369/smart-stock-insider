#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境验证脚本 - 检查Python 3.12环境和项目依赖

Author: Smart Stock Insider Team
Version: 1.0.0
"""
import sys
import os

# 设置控制台编码为UTF-8 (Windows兼容)
if sys.platform == "win32":
    os.system("chcp 65001 > nul")

import sys
import os
import subprocess
import importlib
import platform
from pathlib import Path

class EnvironmentVerifier:
    """环境验证器"""

    def __init__(self):
        self.results = []
        self.python_version = sys.version_info

    def log_result(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        status = "✅" if success else "❌"
        self.results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
        print(f"{status} {test_name}")
        if message:
            print(f"   {message}")

    def check_python_version(self):
        """检查Python版本"""
        print("🐍 检查Python版本...")

        if self.python_version.major != 3 or self.python_version.minor < 12:
            self.log_result(
                "Python版本检查",
                False,
                f"当前版本: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}, 需要: 3.12+"
            )
            return False

        self.log_result(
            "Python版本检查",
            True,
            f"版本: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}"
        )
        return True

    def check_virtual_environment(self):
        """检查虚拟环境"""
        print("\n🏗️ 检查虚拟环境...")

        venv_path = Path(".venv")
        if not venv_path.exists():
            self.log_result("虚拟环境检查", False, "虚拟环境不存在")
            return False

        # 检查是否在虚拟环境中
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            self.log_result("虚拟环境检查", True, "虚拟环境已激活")
        else:
            self.log_result("虚拟环境检查", False, "虚拟环境未激活")
            return False

        return True

    def check_critical_dependencies(self):
        """检查关键依赖"""
        print("\n📦 检查关键依赖...")

        critical_deps = {
            "fastapi": "0.104.1",
            "uvicorn": "0.24.0",
            "sqlalchemy": "2.0.23",
            "pydantic": "2.6.0",
            "pydantic_settings": "2.1.0",
            "redis": "5.0.1",
            "torch": "2.2.0",
            "transformers": "4.38.0",
            "httpx": "0.25.2",
            "loguru": "0.7.2"
        }

        all_success = True
        for dep, min_version in critical_deps.items():
            try:
                module = importlib.import_module(dep)
                version = getattr(module, '__version__', 'unknown')

                # 简单版本比较
                if version != 'unknown' and self._compare_versions(version, min_version):
                    self.log_result(f"依赖检查: {dep}", True, f"版本: {version}")
                else:
                    self.log_result(f"依赖检查: {dep}", False, f"版本: {version}, 需要: {min_version}+")
                    all_success = False

            except ImportError as e:
                self.log_result(f"依赖检查: {dep}", False, f"导入失败: {e}")
                all_success = False

        return all_success

    def check_redis_connection(self):
        """检查Redis连接"""
        print("\n🔴 检查Redis连接...")

        try:
            import redis
            from core.config import settings

            # 使用配置中的Redis URL
            redis_url = settings.REDIS_URL
            if not redis_url:
                redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"

            client = redis.from_url(redis_url, socket_connect_timeout=5)
            client.ping()
            self.log_result("Redis连接检查", True, f"连接成功: {redis_url}")
            return True

        except redis.ConnectionError as e:
            self.log_result("Redis连接检查", False, f"连接失败: {e}")
            return False
        except Exception as e:
            self.log_result("Redis连接检查", False, f"检查异常: {e}")
            return False

    def check_database_connection(self):
        """检查数据库连接"""
        print("\n💾 检查数据库连接...")

        try:
            from core.database import db_manager
            import asyncio

            async def test_db():
                return await db_manager.check_connection()

            # 运行异步检查
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                is_connected = loop.run_until_complete(test_db())
                if is_connected:
                    self.log_result("数据库连接检查", True, "SQLite连接成功")
                else:
                    self.log_result("数据库连接检查", False, "SQLite连接失败")
                return is_connected
            finally:
                loop.close()

        except Exception as e:
            self.log_result("数据库连接检查", False, f"检查异常: {e}")
            return False

    def check_project_structure(self):
        """检查项目结构"""
        print("\n📁 检查项目结构...")

        required_paths = [
            "backend/main.py",
            "backend/core",
            "backend/api",
            "backend/models",
            "backend/services",
            "frontend/src",
            "frontend/src-tauri",
            "frontend/package.json",
            "requirements-312.txt"
        ]

        all_exist = True
        for path in required_paths:
            full_path = Path(path)
            if full_path.exists():
                self.log_result(f"结构检查: {path}", True)
            else:
                self.log_result(f"结构检查: {path}", False, "路径不存在")
                all_exist = False

        return all_exist

    def check_config_files(self):
        """检查配置文件"""
        print("\n⚙️ 检查配置文件...")

        config_files = [
            (".env", "环境配置文件"),
            ("backend/core/config.py", "后端配置"),
            ("frontend/src-tauri/tauri.conf.json", "Tauri配置"),
            ("frontend/src-tauri/Cargo.toml", "Rust依赖")
        ]

        all_good = True
        for config_file, description in config_files:
            if Path(config_file).exists():
                self.log_result(f"配置检查: {description}", True)
            else:
                self.log_result(f"配置检查: {description}", False, "文件不存在")
                if config_file == ".env":
                    print("   提示: 可以运行 'python scripts/setup_python_env.py' 创建环境配置文件")

        return all_good

    def check_node_environment(self):
        """检查Node.js环境"""
        print("\n🟢 检查Node.js环境...")

        try:
            # 检查Node.js版本
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                node_version = result.stdout.strip()
                self.log_result("Node.js检查", True, f"版本: {node_version}")
            else:
                self.log_result("Node.js检查", False, "Node.js未安装或不可用")
                return False

            # 检查npm版本
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                npm_version = result.stdout.strip()
                self.log_result("npm检查", True, f"版本: {npm_version}")
            else:
                self.log_result("npm检查", False, "npm未安装或不可用")
                return False

            # 检查前端依赖
            frontend_path = Path("frontend")
            if frontend_path.exists():
                node_modules = frontend_path / "node_modules"
                if node_modules.exists():
                    self.log_result("前端依赖检查", True, "node_modules存在")
                else:
                    self.log_result("前端依赖检查", False, "需要运行 'npm install'")

            return True

        except Exception as e:
            self.log_result("Node.js环境检查", False, f"检查异常: {e}")
            return False

    def check_rust_environment(self):
        """检查Rust环境"""
        print("\n🦀 检查Rust环境...")

        try:
            # 检查Rust版本
            result = subprocess.run(["rustc", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                rust_version = result.stdout.strip()
                self.log_result("Rust检查", True, f"版本: {rust_version}")
            else:
                self.log_result("Rust检查", False, "Rust未安装或不可用")
                return False

            # 检查Cargo版本
            result = subprocess.run(["cargo", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                cargo_version = result.stdout.strip()
                self.log_result("Cargo检查", True, f"版本: {cargo_version}")
            else:
                self.log_result("Cargo检查", False, "Cargo未安装或不可用")
                return False

            return True

        except Exception as e:
            self.log_result("Rust环境检查", False, f"检查异常: {e}")
            return False

    def run_backend_service_test(self):
        """运行后端服务测试"""
        print("\n🧪 测试后端服务启动...")

        try:
            # 尝试导入主要模块
            from main import app
            self.log_result("后端应用导入", True, "FastAPI应用加载成功")

            # 检查API路由
            routes = [route.path for route in app.routes]
            self.log_result("API路由检查", True, f"发现 {len(routes)} 个路由")

            return True

        except Exception as e:
            self.log_result("后端服务测试", False, f"启动测试失败: {e}")
            return False

    def _compare_versions(self, current: str, minimum: str) -> bool:
        """简单版本比较"""
        try:
            current_parts = [int(x) for x in current.split('.')]
            minimum_parts = [int(x) for x in minimum.split('.')]

            for cur, min_ in zip(current_parts, minimum_parts):
                if cur > min_:
                    return True
                if cur < min_:
                    return False
            return True
        except:
            return True  # 如果版本解析失败，假设兼容

    def run_all_checks(self):
        """运行所有检查"""
        print("🔍 开始环境验证...")
        print(f"   操作系统: {platform.system()} {platform.release()}")
        print(f"   Python: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        print(f"   工作目录: {os.getcwd()}")
        print()

        checks = [
            ("Python版本", self.check_python_version),
            ("虚拟环境", self.check_virtual_environment),
            ("关键依赖", self.check_critical_dependencies),
            ("Redis连接", self.check_redis_connection),
            ("数据库连接", self.check_database_connection),
            ("项目结构", self.check_project_structure),
            ("配置文件", self.check_config_files),
            ("Node.js环境", self.check_node_environment),
            ("Rust环境", self.check_rust_environment),
            ("后端服务", self.run_backend_service_test),
        ]

        results = {}
        for check_name, check_func in checks:
            try:
                results[check_name] = check_func()
            except Exception as e:
                self.log_result(f"{check_name}检查", False, f"检查异常: {e}")
                results[check_name] = False

        self.print_summary(results)
        return results

    def print_summary(self, results):
        """打印检查总结"""
        print("\n" + "="*60)
        print("📊 环境验证总结")
        print("="*60)

        passed = sum(1 for result in results.values() if result)
        total = len(results)

        print(f"通过率: {passed}/{total} ({passed/total*100:.1f}%)")
        print()

        # 分类显示结果
        print("✅ 通过的检查:")
        for name, result in results.items():
            if result:
                print(f"   - {name}")

        print("\n❌ 失败的检查:")
        for name, result in results.items():
            if not result:
                print(f"   - {name}")

        # 给出建议
        print("\n💡 建议:")
        if passed == total:
            print("   🎉 环境配置完美！可以开始开发工作。")
        else:
            print("   请修复上述失败项后重新运行验证。")

            if not results.get("虚拟环境"):
                print("   - 运行 'python scripts/setup_python_env.py' 配置Python环境")

            if not results.get("关键依赖"):
                print("   - 激活虚拟环境后运行 'pip install -r requirements-312.txt'")

            if not results.get("Redis连接"):
                print("   - 确保Redis服务正在运行")

            if not results.get("Node.js环境"):
                print("   - 安装Node.js和npm: https://nodejs.org/")

            if not results.get("Rust环境"):
                print("   - 安装Rust: https://rustup.rs/")

        print("="*60)

def main():
    """主函数"""
    verifier = EnvironmentVerifier()
    results = verifier.run_all_checks()

    # 返回退出码
    all_passed = all(results.values())
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())