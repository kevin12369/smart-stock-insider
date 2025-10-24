#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据服务配置文件
"""

import os
from typing import List

class Config:
    # 服务器配置
    SERVER_HOST = "127.0.0.1"
    SERVER_PORT = 8001

    # 调试模式
    DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"

    # 数据缓存配置
    CACHE_ENABLED = True
    CACHE_EXPIRE_SECONDS = 300  # 5分钟
    CACHE_MAX_SIZE = 1000

    # API限流配置
    RATE_LIMIT_ENABLED = True
    MAX_REQUESTS_PER_MINUTE = 60

    # 数据源配置
    DATA_SOURCE_TIMEOUT = 30  # 秒
    MAX_RETRY_COUNT = 3
    RETRY_DELAY = 1  # 秒

    # 日志配置
    LOG_LEVEL = "INFO"
    LOG_FILE = "data-service.log"

    # 数据库配置
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/cache.db")

    # 支持的股票市场
    SUPPORTED_MARKETS = ["sh", "sz", "bj"]

    # 常用股票代码（用于测试和默认数据）
    DEFAULT_STOCK_CODES = [
        "000001",  # 平安银行
        "000002",  # 万科A
        "600000",  # 浦发银行
        "600036",  # 招商银行
        "000858",  # 五粮液
        "600519",  # 贵州茅台
        "000725",  # 京东方A
        "002415",  # 海康威视
        "002594",  # 比亚迪
        "300750",  # 宁德时代
    ]

    # 技术指标参数
    TECHNICAL_INDICATORS = {
        "MA": [5, 10, 20, 60],
        "EMA": [12, 26],
        "MACD": {"fast": 12, "slow": 26, "signal": 9},
        "RSI": {"period": 14},
        "KDJ": {"n": 9, "m1": 3, "m2": 3},
        "BOLL": {"n": 20, "k": 2},
        "CCI": {"period": 14},
        "WR": {"period": 14}
    }

# 创建全局配置实例
config = Config()