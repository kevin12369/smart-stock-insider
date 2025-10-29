"""
测试工具模块
提供测试过程中常用的工具函数和辅助类
"""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional, Callable, Union
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from unittest.mock import Mock, AsyncMock
import tempfile
import shutil
from pathlib import Path

class AsyncTestCase:
    """异步测试基类"""

    @staticmethod
    async def run_async_with_timeout(coro, timeout: float = 30.0):
        """运行异步协程并设置超时"""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise AssertionError(f"测试超时 ({timeout}秒)")

class TestDataGenerator:
    """测试数据生成器"""

    @staticmethod
    def generate_stock_prices(days: int = 252, initial_price: float = 100.0,
                             volatility: float = 0.2, drift: float = 0.0005) -> pd.Series:
        """生成模拟股票价格数据"""
        np.random.seed(42)

        returns = np.random.normal(drift, volatility / np.sqrt(252), days)
        prices = [initial_price]

        for ret in returns:
            prices.append(prices[-1] * (1 + ret))

        dates = pd.date_range(end=datetime.now(), periods=days, freq="D")
        return pd.Series(prices[1:], index=dates, name="price")

    @staticmethod
    def generate_portfolio_returns(num_assets: int = 5, num_days: int = 252,
                                 risk_free_rate: float = 0.03) -> pd.DataFrame:
        """生成投资组合收益率数据"""
        np.random.seed(42)

        dates = pd.date_range(end=datetime.now(), periods=num_days, freq="D")
        assets = [f"ASSET_{i:02d}" for i in range(num_assets)]

        # 生成相关的收益率数据
        returns_data = {}
        for i, asset in enumerate(assets):
            # 不同的资产有不同的风险收益特征
            expected_return = risk_free_rate + np.random.uniform(0.02, 0.15)
            volatility = np.random.uniform(0.1, 0.3)

            returns = np.random.normal(
                expected_return / 252,
                volatility / np.sqrt(252),
                num_days
            )
            returns_data[asset] = returns

        return pd.DataFrame(returns_data, index=dates)

    @staticmethod
    def generate_user_actions(num_users: int = 10, actions_per_user: int = 20) -> List[Dict[str, Any]]:
        """生成用户行为数据"""
        np.random.seed(42)

        action_types = [
            "page_view", "stock_search", "stock_view", "news_click",
            "chat_message", "portfolio_create", "portfolio_update",
            "risk_analysis", "sentiment_check"
        ]

        pages = [
            "/dashboard", "/stocks", "/portfolio", "/news", "/chat",
            "/analysis", "/settings", "/profile"
        ]

        actions = []
        start_time = datetime.now() - timedelta(days=30)

        for user_id in range(1, num_users + 1):
            for action_num in range(1, actions_per_user + 1):
                action = {
                    "action_id": f"action_{user_id:03d}_{action_num:03d}",
                    "user_id": f"user_{user_id:03d}",
                    "action_type": np.random.choice(action_types),
                    "timestamp": start_time + timedelta(
                        days=np.random.randint(0, 30),
                        hours=np.random.randint(0, 24),
                        minutes=np.random.randint(0, 60)
                    ),
                    "page": np.random.choice(pages),
                    "duration": np.random.uniform(5, 300),  # 5秒到5分钟
                    "properties": {
                        "device": np.random.choice(["desktop", "mobile", "tablet"]),
                        "session_duration": np.random.uniform(60, 3600)
                    }
                }
                actions.append(action)

        return sorted(actions, key=lambda x: x["timestamp"])

    @staticmethod
    def generate_sentiment_texts(num_texts: int = 100) -> List[Dict[str, Any]]:
        """生成情感分析测试文本"""
        np.random.seed(42)

        positive_templates = [
            "{}股价大涨{}%，表现强劲",
            "{}财报超预期，净利润增长{}%",
            "{}获得重要合同，未来前景看好",
            "分析师上调{}评级至'买入'",
            "{}新产品发布成功，市场反应积极"
        ]

        negative_templates = [
            "{}股价下跌{}%，市场担忧",
            "{}财报不及预期，营收下降{}%",
            "{}面临监管风险，业务受影响",
            "分析师下调{}评级至'卖出'",
            "{}市场份额下降，竞争加剧"
        ]

        neutral_templates = [
            "{}股价保持平稳，成交量正常",
            "{}召开股东大会，审议常规议案",
            "{}发布公告，无重大事项",
            "分析师维持{}评级不变",
            "{}进行组织架构调整"
        ]

        companies = ["腾讯", "阿里巴巴", "百度", "京东", "美团", "小米", "网易", "拼多多"]

        texts = []
        for i in range(num_texts):
            sentiment_type = np.random.choice(["positive", "negative", "neutral"],
                                           p=[0.4, 0.3, 0.3])

            if sentiment_type == "positive":
                template = np.random.choice(positive_templates)
                expected_sentiment = "positive"
            elif sentiment_type == "negative":
                template = np.random.choice(negative_templates)
                expected_sentiment = "negative"
            else:
                template = np.random.choice(neutral_templates)
                expected_sentiment = "neutral"

            company = np.random.choice(companies)
            percentage = np.random.uniform(1, 20)

            text = template.format(company, f"{percentage:.1f}")

            texts.append({
                "text": text,
                "expected_sentiment": expected_sentiment,
                "expected_confidence": np.random.uniform(0.6, 0.95),
                "company": company
            })

        return texts

class MockResponse:
    """模拟HTTP响应"""

    def __init__(self, json_data: Dict[str, Any], status_code: int = 200):
        self._json_data = json_data
        self.status_code = status_code

    def json(self) -> Dict[str, Any]:
        return self._json_data

    @property
    def text(self) -> str:
        return json.dumps(self._json_data)

class DatabaseMock:
    """模拟数据库连接"""

    def __init__(self):
        self.data = {}
        self.transactions = []

    async def execute(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """模拟执行SQL查询"""
        # 简单的查询模拟
        if "SELECT" in query.upper():
            return list(self.data.values())
        elif "INSERT" in query.upper():
            if params:
                key = str(params.get("id", len(self.data)))
                self.data[key] = params
            return [{"affected_rows": 1}]
        elif "UPDATE" in query.upper():
            if params and "id" in params:
                key = str(params["id"])
                if key in self.data:
                    self.data[key].update(params)
            return [{"affected_rows": 1}]
        elif "DELETE" in query.upper():
            if params and "id" in params:
                key = str(params["id"])
                if key in self.data:
                    del self.data[key]
            return [{"affected_rows": 1}]
        return []

    async def commit(self):
        """模拟提交事务"""
        self.transactions.append({"type": "commit", "timestamp": datetime.now()})

    async def rollback(self):
        """模拟回滚事务"""
        self.transactions.append({"type": "rollback", "timestamp": datetime.now()})

class RedisMock:
    """模拟Redis连接"""

    def __init__(self):
        self.data = {}
        self.expiry = {}

    async def get(self, key: str) -> Optional[str]:
        """获取缓存值"""
        if key in self.expiry and datetime.now() > self.expiry[key]:
            del self.data[key]
            del self.expiry[key]
            return None
        return self.data.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """设置缓存值"""
        self.data[key] = value
        if ex:
            self.expiry[key] = datetime.now() + timedelta(seconds=ex)
        return True

    async def delete(self, key: str) -> bool:
        """删除缓存值"""
        if key in self.data:
            del self.data[key]
        if key in self.expiry:
            del self.expiry[key]
        return True

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if key in self.expiry and datetime.now() > self.expiry[key]:
            del self.data[key]
            del self.expiry[key]
            return False
        return key in self.data

class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.metrics = {}

    def start_timer(self, name: str):
        """开始计时"""
        self.metrics[name] = {"start_time": time.time()}

    def end_timer(self, name: str) -> float:
        """结束计时并返回耗时"""
        if name not in self.metrics:
            raise ValueError(f"Timer '{name}' not found")

        elapsed = time.time() - self.metrics[name]["start_time"]
        self.metrics[name]["elapsed"] = elapsed
        return elapsed

    def get_elapsed_time(self, name: str) -> Optional[float]:
        """获取计时结果"""
        return self.metrics.get(name, {}).get("elapsed")

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """获取所有性能指标"""
        return self.metrics.copy()

class TempFileManager:
    """临时文件管理器"""

    def __init__(self):
        self.temp_files = []

    def create_temp_file(self, content: str = "", suffix: str = ".tmp") -> str:
        """创建临时文件"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)
        temp_file.write(content)
        temp_file.close()

        self.temp_files.append(temp_file.name)
        return temp_file.name

    def create_temp_dir(self) -> str:
        """创建临时目录"""
        temp_dir = tempfile.mkdtemp()
        self.temp_files.append(temp_dir)
        return temp_dir

    def cleanup(self):
        """清理所有临时文件"""
        for path in self.temp_files:
            try:
                if Path(path).is_file():
                    Path(path).unlink()
                elif Path(path).is_dir():
                    shutil.rmtree(path)
            except Exception as e:
                print(f"清理临时文件失败 {path}: {e}")

        self.temp_files.clear()

def assert_close(actual: float, expected: float, tolerance: float = 1e-6,
                message: Optional[str] = None):
    """断言两个浮点数接近"""
    if abs(actual - expected) > tolerance:
        error_msg = f"期望 {expected} ± {tolerance}，实际 {actual}"
        if message:
            error_msg = f"{message}: {error_msg}"
        raise AssertionError(error_msg)

def assert_lists_equal(actual: List[Any], expected: List[Any],
                     ignore_order: bool = False, message: Optional[str] = None):
    """断言两个列表相等"""
    if ignore_order:
        actual_sorted = sorted(actual)
        expected_sorted = sorted(expected)
        if actual_sorted != expected_sorted:
            error_msg = f"列表内容不相等（忽略顺序）\n实际: {actual_sorted}\n期望: {expected_sorted}"
    else:
        if actual != expected:
            error_msg = f"列表内容不相等\n实际: {actual}\n期望: {expected}"

    if message:
        error_msg = f"{message}: {error_msg}"

    raise AssertionError(error_msg)

def assert_dict_contains(actual: Dict[str, Any], expected_subset: Dict[str, Any],
                       message: Optional[str] = None):
    """断言字典包含指定的键值对"""
    missing_keys = []
    mismatched_values = {}

    for key, expected_value in expected_subset.items():
        if key not in actual:
            missing_keys.append(key)
        elif actual[key] != expected_value:
            mismatched_values[key] = {
                "expected": expected_value,
                "actual": actual[key]
            }

    if missing_keys or mismatched_values:
        error_parts = []
        if missing_keys:
            error_parts.append(f"缺少键: {missing_keys}")
        if mismatched_values:
            error_parts.append(f"值不匹配: {mismatched_values}")

        error_msg = "; ".join(error_parts)
        if message:
            error_msg = f"{message}: {error_msg}"

        raise AssertionError(error_msg)