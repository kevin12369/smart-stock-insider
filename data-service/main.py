#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智股通数据服务主程序
提供RESTful API接口，获取和处理股票数据
"""

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import logging
from datetime import datetime, timedelta
import json

from data_provider import DataProvider
from ai_service import init_ai_service, get_ai_service
from config import config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="智股通数据服务",
    description="提供股票数据获取和处理功能",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据提供者实例
data_provider = DataProvider()

# 数据模型
class StockBasicInfo(BaseModel):
    code: str
    name: str
    industry: Optional[str] = None
    market: Optional[str] = None
    listing_date: Optional[str] = None

class StockDailyData(BaseModel):
    code: str
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    amount: float

class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: str

def create_api_response(success: bool, message: str, data=None, error=None) -> ApiResponse:
    """创建统一的API响应格式"""
    return ApiResponse(
        success=success,
        message=message,
        data=data,
        error=error,
        timestamp=datetime.now().isoformat()
    )

@app.get("/")
async def root():
    """根路径，服务状态检查"""
    return create_api_response(True, "智股通数据服务运行正常")

@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 测试数据提供者连接
        status = data_provider.health_check()
        return create_api_response(True, "服务健康", data={"status": status})
    except Exception as e:
        return create_api_response(False, "服务异常", error=str(e))

@app.get("/api/stock/basic")
async def get_stock_basic(
    code: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """获取股票基本信息"""
    try:
        if code:
            # 获取单个股票信息
            stock = await data_provider.get_stock_basic(code)
            if stock:
                return create_api_response(True, "获取股票信息成功", data=stock)
            else:
                return create_api_response(False, "未找到股票信息")
        else:
            # 获取股票列表
            stocks = await data_provider.get_stock_list(limit, offset)
            return create_api_response(True, "获取股票列表成功", data=stocks)
    except Exception as e:
        logger.error(f"获取股票基本信息失败: {e}")
        return create_api_response(False, "获取股票信息失败", error=str(e))

@app.get("/api/stock/daily")
async def get_stock_daily(
    code: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(200, ge=1, le=2000)
):
    """获取股票日线数据"""
    try:
        data = await data_provider.get_daily_data(code, start_date, end_date, limit)
        if data:
            return create_api_response(True, "获取日线数据成功", data=data)
        else:
            return create_api_response(False, "未找到日线数据")
    except Exception as e:
        logger.error(f"获取日线数据失败: {e}")
        return create_api_response(False, "获取日线数据失败", error=str(e))

@app.get("/api/stock/realtime")
async def get_stock_realtime(code: str):
    """获取股票实时数据"""
    try:
        data = await data_provider.get_realtime_data(code)
        if data:
            return create_api_response(True, "获取实时数据成功", data=data)
        else:
            return create_api_response(False, "未找到实时数据")
    except Exception as e:
        logger.error(f"获取实时数据失败: {e}")
        return create_api_response(False, "获取实时数据失败", error=str(e))

@app.get("/api/stock/batch")
async def get_batch_data(codes: str = Query(...), fields: str = "basic,daily"):
    """批量获取股票数据"""
    try:
        code_list = codes.split(',')
        requested_fields = fields.split(',')

        result = await data_provider.get_batch_data(code_list, requested_fields)
        return create_api_response(True, "批量获取数据成功", data=result)
    except Exception as e:
        logger.error(f"批量获取数据失败: {e}")
        return create_api_response(False, "批量获取数据失败", error=str(e))

@app.get("/api/market/index")
async def get_market_index():
    """获取主要指数信息"""
    try:
        indices = await data_provider.get_market_indices()
        return create_api_response(True, "获取指数信息成功", data=indices)
    except Exception as e:
        logger.error(f"获取指数信息失败: {e}")
        return create_api_response(False, "获取指数信息失败", error=str(e))

@app.get("/api/market/sectors")
async def get_sector_data():
    """获取行业板块数据"""
    try:
        sectors = await data_provider.get_sector_data()
        return create_api_response(True, "获取行业数据成功", data=sectors)
    except Exception as e:
        logger.error(f"获取行业数据失败: {e}")
        return create_api_response(False, "获取行业数据失败", error=str(e))

@app.post("/api/data/refresh")
async def refresh_data():
    """刷新数据缓存"""
    try:
        await data_provider.refresh_cache()
        return create_api_response(True, "数据缓存刷新成功")
    except Exception as e:
        logger.error(f"刷新数据失败: {e}")
        return create_api_response(False, "刷新数据失败", error=str(e))

# AI分析相关API端点

@app.post("/api/ai/technical-analysis")
async def technical_analysis(request: dict):
    """技术分析"""
    try:
        ai = get_ai_service()
        if not ai:
            return create_api_response(False, "AI服务未初始化")

        # 创建请求对象
        from ai_service import TechnicalAnalysisRequest
        analysis_request = TechnicalAnalysisRequest(**request)

        result = await ai.technical_analysis(analysis_request)
        return create_api_response(True, "技术分析完成", data=result.dict())

    except Exception as e:
        logger.error(f"技术分析失败: {e}")
        return create_api_response(False, "技术分析失败", error=str(e))

@app.post("/api/ai/fundamental-analysis")
async def fundamental_analysis(request: dict):
    """基本面分析"""
    try:
        ai = get_ai_service()
        if not ai:
            return create_api_response(False, "AI服务未初始化")

        from ai_service import FundamentalAnalysisRequest
        analysis_request = FundamentalAnalysisRequest(**request)

        result = await ai.fundamental_analysis(analysis_request)
        return create_api_response(True, "基本面分析完成", data=result.dict())

    except Exception as e:
        logger.error(f"基本面分析失败: {e}")
        return create_api_response(False, "基本面分析失败", error=str(e))

@app.post("/api/ai/news-analysis")
async def news_analysis(request: dict):
    """消息面分析"""
    try:
        ai = get_ai_service()
        if not ai:
            return create_api_response(False, "AI服务未初始化")

        from ai_service import NewsAnalysisRequest
        analysis_request = NewsAnalysisRequest(**request)

        result = await ai.news_analysis(analysis_request)
        return create_api_response(True, "消息面分析完成", data=result.dict())

    except Exception as e:
        logger.error(f"消息面分析失败: {e}")
        return create_api_response(False, "消息面分析失败", error=str(e))

@app.post("/api/ai/portfolio-analysis")
async def portfolio_analysis(request: dict):
    """组合分析"""
    try:
        ai = get_ai_service()
        if not ai:
            return create_api_response(False, "AI服务未初始化")

        from ai_service import PortfolioAnalysisRequest
        analysis_request = PortfolioAnalysisRequest(**request)

        result = await ai.portfolio_analysis(analysis_request)
        return create_api_response(True, "组合分析完成", data=result.dict())

    except Exception as e:
        logger.error(f"组合分析失败: {e}")
        return create_api_response(False, "组合分析失败", error=str(e))

@app.get("/api/ai/capabilities")
async def get_ai_capabilities():
    """获取AI分析能力"""
    try:
        capabilities = {
            "technical_analysis": {
                "supported_indicators": ["MACD", "RSI", "KDJ", "MA", "BOLL", "CCI", "WR"],
                "analysis_types": ["comprehensive", "trend", "oscillator", "volume"],
                "features": ["trend_analysis", "support_resistance", "signal_generation", "recommendation"]
            },
            "fundamental_analysis": {
                "depths": ["basic", "detailed", "comprehensive"],
                "features": ["valuation_analysis", "financial_health", "peer_comparison"],
                "metrics": ["PE", "PB", "ROE", "Debt_Ratio", "Growth_Rates"]
            },
            "news_analysis": {
                "features": ["sentiment_analysis", "keyword_extraction", "risk_identification"],
                "data_sources": ["news_feeds", "social_media", "announcements"],
                "analysis_period": "支持自定义天数分析"
            },
            "portfolio_analysis": {
                "analysis_types": ["risk_return", "correlation", "optimization"],
                "features": ["risk_metrics", "return_metrics", "correlation_matrix", "optimization_suggestions"],
                "support": ["multi_stock", "risk_assessment", "performance_attribution"]
            }
        }

        return create_api_response(True, "获取AI能力成功", data=capabilities)

    except Exception as e:
        logger.error(f"获取AI能力失败: {e}")
        return create_api_response(False, "获取AI能力失败", error=str(e))

@app.get("/api/data/status")
async def get_data_status():
    """获取数据服务状态"""
    try:
        status = await data_provider.get_service_status()
        return create_api_response(True, "获取服务状态成功", data=status)
    except Exception as e:
        logger.error(f"获取服务状态失败: {e}")
        return create_api_response(False, "获取服务状态失败", error=str(e))

@app.on_event("startup")
async def startup_event():
    """服务启动时的初始化"""
    logger.info("智股通数据服务启动中...")
    try:
        await data_provider.initialize()
        logger.info("数据服务初始化完成")

        # 初始化AI分析服务
        init_ai_service(data_provider)
        logger.info("AI分析服务初始化完成")
    except Exception as e:
        logger.error(f"数据服务初始化失败: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """服务关闭时的清理"""
    logger.info("智股通数据服务关闭中...")
    try:
        await data_provider.cleanup()
        logger.info("数据服务清理完成")
    except Exception as e:
        logger.error(f"数据服务清理失败: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.SERVER_HOST,
        port=config.SERVER_PORT,
        reload=config.DEBUG_MODE,
        log_level="info"
    )