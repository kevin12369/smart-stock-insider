"""
测试模块
包含所有测试相关的基础配置和工具
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 测试环境配置
TEST_ENV = os.getenv("TEST_ENV", "development")

# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///./test.db"

# 测试Redis配置
TEST_REDIS_URL = "redis://localhost:6379/1"

# 测试日志级别
TEST_LOG_LEVEL = "DEBUG"

# 测试超时设置
DEFAULT_TIMEOUT = 30
ASYNC_TIMEOUT = 60

# 模拟数据路径
TEST_FIXTURES_PATH = Path(__file__).parent / "fixtures"