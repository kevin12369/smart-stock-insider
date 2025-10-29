"""
测试数据fixtures
包含各种测试所需的示例数据
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any

def load_chatbot_fixtures() -> Dict[str, Any]:
    """加载ChatBot测试数据"""
    return {
        "conversations": [
            {
                "user_id": "test_user_001",
                "session_id": "test_session_001",
                "message": "什么是市盈率？",
                "intent": "knowledge_query",
                "entities": {"concept": "市盈率"},
                "expected_keywords": ["市盈率", "估值", "财务指标"]
            },
            {
                "user_id": "test_user_001",
                "session_id": "test_session_001",
                "message": "帮我分析一下腾讯股票",
                "intent": "stock_analysis",
                "entities": {"company": "腾讯", "stock": "0700.HK"},
                "expected_keywords": ["腾讯", "股票", "分析"]
            },
            {
                "user_id": "test_user_002",
                "session_id": "test_session_002",
                "message": "今天市场怎么样？",
                "intent": "market_overview",
                "entities": {"time": "今天"},
                "expected_keywords": ["市场", "行情", "今日"]
            }
        ],
        "knowledge_base": {
            "市盈率": {
                "definition": "股票价格与每股收益的比率",
                "category": "财务指标",
                "importance": 0.9
            },
            "腾讯": {
                "company_info": "腾讯控股有限公司",
                "stock_code": "0700.HK",
                "industry": "互联网"
            }
        }
    }

def load_sentiment_fixtures() -> Dict[str, Any]:
    """加载情感分析测试数据"""
    return {
        "texts": [
            {
                "text": "腾讯股价大涨5%，创历史新高，表现非常强劲",
                "expected_sentiment": "positive",
                "expected_confidence": 0.85,
                "expected_entities": [
                    {"type": "company", "value": "腾讯"},
                    {"type": "percentage", "value": "5%"}
                ],
                "expected_keywords": ["大涨", "历史新高", "强劲"]
            },
            {
                "text": "市场担心通胀风险，科技股集体下跌，投资者情绪悲观",
                "expected_sentiment": "negative",
                "expected_confidence": 0.78,
                "expected_entities": [
                    {"type": "concept", "value": "通胀风险"},
                    {"type": "sector", "value": "科技股"}
                ],
                "expected_keywords": ["担心", "下跌", "悲观"]
            },
            {
                "text": "央行维持利率不变，市场反应平淡，交易量正常",
                "expected_sentiment": "neutral",
                "expected_confidence": 0.65,
                "expected_entities": [
                    {"type": "institution", "value": "央行"},
                    {"type": "metric", "value": "利率"}
                ],
                "expected_keywords": ["维持", "平淡", "正常"]
            }
        ]
    }

def load_portfolio_fixtures() -> Dict[str, Any]:
    """加载投资组合测试数据"""
    # 生成示例收益率数据
    dates = pd.date_range("2023-01-01", "2023-12-31", freq="D")
    np.random.seed(42)

    assets = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM"]

    returns_data = {}
    for asset in assets:
        # 模拟不同的收益率和波动率
        if asset in ["AAPL", "MSFT", "GOOGL"]:
            returns = np.random.normal(0.001, 0.02, len(dates))
        elif asset in ["TSLA", "NVDA"]:
            returns = np.random.normal(0.0015, 0.035, len(dates))
        elif asset in ["AMZN", "META"]:
            returns = np.random.normal(0.0008, 0.028, len(dates))
        else:  # JPM
            returns = np.random.normal(0.0005, 0.018, len(dates))

        returns_data[asset] = returns

    returns_df = pd.DataFrame(returns_data, index=dates)

    # 计算年化收益率和波动率
    expected_returns = (returns_df.mean() * 252).to_dict()
    volatilities = (returns_df.std() * np.sqrt(252)).to_dict()

    return {
        "returns_data": returns_df,
        "assets": [
            {
                "symbol": symbol,
                "name": f"{symbol} Inc.",
                "expected_return": expected_returns[symbol],
                "volatility": volatilities[symbol],
                "category": "technology" if symbol in ["AAPL", "MSFT", "GOOGL", "META", "NVDA"] else "finance"
            }
            for symbol in assets
        ],
        "covariance_matrix": returns_df.cov() * 252,
        "correlation_matrix": returns_df.corr()
    }

def load_analytics_fixtures() -> Dict[str, Any]:
    """加载用户行为分析测试数据"""
    return {
        "users": [
            {
                "user_id": "test_user_001",
                "profile": {
                    "investment_experience": "intermediate",
                    "risk_tolerance": "moderate",
                    "preferred_categories": ["股票查询", "市场分析"],
                    "interaction_style": "formal"
                }
            },
            {
                "user_id": "test_user_002",
                "profile": {
                    "investment_experience": "beginner",
                    "risk_tolerance": "conservative",
                    "preferred_categories": ["投资教育", "风险管理"],
                    "interaction_style": "friendly"
                }
            }
        ],
        "actions": [
            {
                "action_id": "action_001",
                "user_id": "test_user_001",
                "action_type": "page_view",
                "page": "/dashboard",
                "session_id": "session_001",
                "timestamp": datetime(2023, 10, 29, 10, 0, 0),
                "duration": 45.2
            },
            {
                "action_id": "action_002",
                "user_id": "test_user_001",
                "action_type": "stock_search",
                "page": "/search",
                "session_id": "session_001",
                "timestamp": datetime(2023, 10, 29, 10, 5, 0),
                "properties": {"symbol": "AAPL", "query": "苹果股票"}
            },
            {
                "action_id": "action_003",
                "user_id": "test_user_002",
                "action_type": "chat_message",
                "page": "/chat",
                "session_id": "session_002",
                "timestamp": datetime(2023, 10, 29, 10, 10, 0),
                "properties": {"intent": "knowledge_query", "message_length": 25}
            },
            {
                "action_id": "action_004",
                "user_id": "test_user_001",
                "action_type": "portfolio_create",
                "page": "/portfolio",
                "session_id": "session_001",
                "timestamp": datetime(2023, 10, 29, 10, 15, 0),
                "value": 10000.0
            }
        ],
        "sessions": [
            {
                "session_id": "session_001",
                "user_id": "test_user_001",
                "start_time": datetime(2023, 10, 29, 10, 0, 0),
                "end_time": datetime(2023, 10, 29, 10, 20, 0),
                "total_duration": 1200.0,
                "page_views": 5,
                "actions": ["action_001", "action_002", "action_004"]
            },
            {
                "session_id": "session_002",
                "user_id": "test_user_002",
                "start_time": datetime(2023, 10, 29, 10, 10, 0),
                "end_time": datetime(2023, 10, 29, 10, 25, 0),
                "total_duration": 900.0,
                "page_views": 3,
                "actions": ["action_003"]
            }
        ]
    }

def load_api_fixtures() -> Dict[str, Any]:
    """加载API测试数据"""
    return {
        "endpoints": {
            "chatbot": [
                {
                    "method": "POST",
                    "path": "/api/chatbot/conversation/start",
                    "request": {"user_id": "test_user_001"},
                    "expected_status": 201,
                    "expected_response_keys": ["success", "data", "message"]
                },
                {
                    "method": "POST",
                    "path": "/api/chatbot/conversation/chat",
                    "request": {
                        "user_id": "test_user_001",
                        "message": "什么是市盈率？",
                        "session_id": "test_session_001"
                    },
                    "expected_status": 200,
                    "expected_response_keys": ["session_id", "response", "intent", "confidence"]
                }
            ],
            "sentiment": [
                {
                    "method": "POST",
                    "path": "/api/sentiment/analyze",
                    "request": {
                        "text": "腾讯股价大涨5%，创历史新高",
                        "include_entities": True,
                        "include_keywords": True
                    },
                    "expected_status": 200,
                    "expected_response_keys": ["text", "sentiment", "confidence", "scores"]
                }
            ],
            "portfolio": [
                {
                    "method": "POST",
                    "path": "/api/portfolio/optimize",
                    "request": {
                        "assets": [
                            {"symbol": "AAPL", "expected_return": 0.12, "volatility": 0.22},
                            {"symbol": "MSFT", "expected_return": 0.10, "volatility": 0.18}
                        ],
                        "method": "markowitz"
                    },
                    "expected_status": 200,
                    "expected_response_keys": ["weights", "expected_return", "expected_volatility", "sharpe_ratio"]
                }
            ],
            "analytics": [
                {
                    "method": "POST",
                    "path": "/api/analytics/track/action",
                    "request": {
                        "user_id": "test_user_001",
                        "action_type": "page_view",
                        "page": "/dashboard"
                    },
                    "expected_status": 201,
                    "expected_response_keys": ["success", "action_id", "message"]
                }
            ]
        }
    }

def load_performance_fixtures() -> Dict[str, Any]:
    """加载性能测试数据"""
    return {
        "load_test_scenarios": [
            {
                "name": "chatbot_concurrent_users",
                "description": "ChatBot并发用户测试",
                "concurrent_users": 50,
                "duration": 60,  # 秒
                "requests_per_second": 10,
                "endpoint": "/api/chatbot/conversation/chat"
            },
            {
                "name": "sentiment_batch_analysis",
                "description": "情感分析批量处理测试",
                "batch_size": 100,
                "concurrent_batches": 5,
                "endpoint": "/api/sentiment/analyze/batch"
            },
            {
                "name": "portfolio_optimization_stress",
                "description": "投资组合优化压力测试",
                "asset_count": 50,
                "concurrent_optimizations": 10,
                "endpoint": "/api/portfolio/optimize"
            }
        ]
    }