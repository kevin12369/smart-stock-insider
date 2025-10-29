"""
API模块初始化

Author: Smart Stock Insider Team
Version: 1.0.0
"""

from fastapi import APIRouter

from .routers import (
    stocks,
    news,
    ai
)

# 创建主路由器
api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])