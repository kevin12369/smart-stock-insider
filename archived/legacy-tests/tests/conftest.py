"""
pytest配置文件
定义测试夹具和全局测试配置
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Generator, AsyncGenerator, Dict, Any
import json
import pandas as pd
from unittest.mock import Mock, AsyncMock

from backend.services.ai_service.chatbot.chatbot_service import ChatBotService
from backend.services.ai_service.sentiment.sentiment_analyzer import FinancialSentimentAnalyzer
from backend.services.ai_service.portfolio.optimizer import PortfolioOptimizer
from backend.services.ai_service.analytics.behavior_tracker import BehaviorTracker

@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """创建临时目录"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)

@pytest.fixture
def test_config() -> Dict[str, Any]:
    """测试配置"""
    return {
        "chatbot": {
            "max_conversation_history": 10,
            "session_timeout": 1800,
            "knowledge_base_path": "tests/fixtures/knowledge.json"
        },
        "sentiment": {
            "model_name": "bert-base-chinese",
            "max_length": 512,
            "batch_size": 16
        },
        "portfolio": {
            "risk_free_rate": 0.03,
            "frequency": 252,
            "max_iterations": 1000,
            "tolerance": 1e-8
        },
        "analytics": {
            "session_timeout": 1800,
            "max_actions_per_user": 1000,
            "max_sessions_per_user": 100
        }
    }

@pytest.fixture
async def chatbot_service(test_config: Dict[str, Any]) -> AsyncGenerator[ChatBotService, None]:
    """ChatBot服务夹具"""
    service = ChatBotService(test_config["chatbot"])
    await service.initialize()
    yield service
    await service.cleanup()

@pytest.fixture
async def sentiment_analyzer(test_config: Dict[str, Any]) -> AsyncGenerator[FinancialSentimentAnalyzer, None]:
    """情感分析器夹具"""
    analyzer = FinancialSentimentAnalyzer(test_config["sentiment"])
    # 不加载实际模型，使用基于词典的方法
    yield analyzer
    await analyzer.cleanup()

@pytest.fixture
def portfolio_optimizer(test_config: Dict[str, Any]) -> PortfolioOptimizer:
    """投资组合优化器夹具"""
    return PortfolioOptimizer(test_config["portfolio"])

@pytest.fixture
def behavior_tracker(test_config: Dict[str, Any]) -> BehaviorTracker:
    """行为追踪器夹具"""
    return BehaviorTracker(test_config["analytics"])

@pytest.fixture
def sample_financial_data() -> pd.DataFrame:
    """示例金融数据"""
    dates = pd.date_range("2023-01-01", "2023-12-31", freq="D")
    np.random.seed(42)

    # 模拟股票收益率数据
    returns_data = {
        "AAPL": np.random.normal(0.001, 0.02, len(dates)),
        "MSFT": np.random.normal(0.0008, 0.018, len(dates)),
        "GOOGL": np.random.normal(0.0012, 0.022, len(dates)),
        "AMZN": np.random.normal(0.0005, 0.025, len(dates)),
        "TSLA": np.random.normal(0.0015, 0.035, len(dates))
    }

    return pd.DataFrame(returns_data, index=dates)

@pytest.fixture
def sample_chatbot_conversations() -> list:
    """示例ChatBot对话数据"""
    return [
        {
            "user_id": "user001",
            "session_id": "session001",
            "message": "什么是市盈率？",
            "intent": "knowledge_query",
            "expected_response": "市盈率是股票价格与每股收益的比率..."
        },
        {
            "user_id": "user001",
            "session_id": "session001",
            "message": "帮我分析一下腾讯股票",
            "intent": "stock_analysis",
            "expected_response": "腾讯股票的分析如下..."
        },
        {
            "user_id": "user002",
            "session_id": "session002",
            "message": "今天市场怎么样？",
            "intent": "market_overview",
            "expected_response": "今天市场整体表现..."
        }
    ]

@pytest.fixture
def sample_sentiment_texts() -> list:
    """示例情感分析文本"""
    return [
        {
            "text": "腾讯股价大涨5%，创历史新高",
            "expected_sentiment": "positive",
            "expected_confidence": 0.8
        },
        {
            "text": "市场担心通胀风险，科技股集体下跌",
            "expected_sentiment": "negative",
            "expected_confidence": 0.7
        },
        {
            "text": "央行维持利率不变，市场反应平淡",
            "expected_sentiment": "neutral",
            "expected_confidence": 0.6
        }
    ]

@pytest.fixture
def sample_portfolio_assets() -> list:
    """示例投资组合资产数据"""
    return [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "expected_return": 0.12,
            "volatility": 0.22,
            "category": "technology"
        },
        {
            "symbol": "MSFT",
            "name": "Microsoft Corporation",
            "expected_return": 0.10,
            "volatility": 0.18,
            "category": "technology"
        },
        {
            "symbol": "GOOGL",
            "name": "Alphabet Inc.",
            "expected_return": 0.11,
            "volatility": 0.20,
            "category": "technology"
        }
    ]

@pytest.fixture
def sample_user_actions() -> list:
    """示例用户行为数据"""
    return [
        {
            "user_id": "user001",
            "action_type": "page_view",
            "page": "/dashboard",
            "duration": 45.2,
            "timestamp": "2023-10-29T10:00:00Z"
        },
        {
            "user_id": "user001",
            "action_type": "stock_search",
            "properties": {"symbol": "AAPL", "query": "苹果股票"},
            "timestamp": "2023-10-29T10:05:00Z"
        },
        {
            "user_id": "user002",
            "action_type": "chat_message",
            "properties": {"intent": "knowledge_query", "message_length": 25},
            "timestamp": "2023-10-29T10:10:00Z"
        }
    ]

@pytest.fixture
def mock_redis_client():
    """模拟Redis客户端"""
    client = Mock()
    client.get = Mock(return_value=None)
    client.set = Mock(return_value=True)
    client.delete = Mock(return_value=True)
    client.exists = Mock(return_value=False)
    return client

@pytest.fixture
def mock_database_client():
    """模拟数据库客户端"""
    client = Mock()
    client.execute = Mock(return_value=[])
    client.commit = Mock(return_value=True)
    client.rollback = Mock(return_value=True)
    return client

# 测试标记
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line("markers", "unit: 单元测试")
    config.addinivalue_line("markers", "integration: 集成测试")
    config.addinivalue_line("markers", "e2e: 端到端测试")
    config.addinivalue_line("markers", "performance: 性能测试")
    config.addinivalue_line("markers", "slow: 慢速测试")
    config.addinivalue_line("markers", "ai: AI相关测试")
    config.addinivalue_line("markers", "api: API测试")

# 测试收集钩子
def pytest_collection_modifyitems(config, items):
    """修改测试收集"""
    for item in items:
        # 为异步测试添加标记
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)

        # 根据路径添加标记
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e)
        elif "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)

# 测试报告钩子
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """生成测试报告"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call":
        # 添加测试元数据
        report.test_id = item.nodeid
        report.test_module = item.module.__name__
        report.test_function = item.function.__name__
        report.test_markers = [mark.name for mark in item.iter_markers()]