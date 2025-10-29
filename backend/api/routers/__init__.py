"""
API路由模块

Author: Smart Stock Insider Team
Version: 1.0.0
"""

from fastapi import APIRouter

# 导入各个路由模块
from .stocks import router as stocks_router
from .ai import router as ai_router
from .news import router as news_router

# 创建主路由
api_router = APIRouter()

# 注册子路由
api_router.include_router(stocks_router)
api_router.include_router(ai_router)
api_router.include_router(news_router)

# 导出的路由模块
__all__ = ["stocks", "ai", "news"]