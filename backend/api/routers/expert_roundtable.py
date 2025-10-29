#!/usr/bin/env python3
"""
专家圆桌会议API路由

Author: Smart Stock Insider Team
Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from loguru import logger

from services.ai_service.expert_roundtable.round_table_coordinator import round_table_coordinator
from services.ai_service.glm_analyzer import glm_analyzer


router = APIRouter(prefix="/api/expert-roundtable", tags=["专家圆桌会议"])


class AnalysisRequest(BaseModel):
    """分析请求模型"""
    symbol: str = Field(..., description="股票代码", example="000001")
    include_detailed_analysis: bool = Field(True, description="是否包含详细分析")
    save_to_history: bool = Field(True, description="是否保存到历史记录")


class AnalysisResponse(BaseModel):
    """分析响应模型"""
    success: bool
    message: str
    data: Dict[str, Any] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


@router.post("/analyze", response_model=AnalysisResponse)
async def start_expert_round_table(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    启动专家圆桌会议分析

    四位专家将从不同角度分析股票：
    - 技术面分析师：技术指标、K线形态、趋势分析
    - 基本面分析师：财务数据、估值模型、行业分析
    - 新闻分析师：新闻情感、事件影响、市场情绪
    - 风控分析师：风险评估、仓位建议、止损策略
    """
    try:
        logger.info(f"启动专家圆桌会议分析: {request.symbol}")

        # 验证股票代码格式
        if not request.symbol or len(request.symbol) < 4:
            raise HTTPException(status_code=400, detail="股票代码格式不正确")

        # 启动专家圆桌会议
        result = await round_table_coordinator.start_round_table(request.symbol)

        if result.get("meeting_status") == "failed":
            return AnalysisResponse(
                success=False,
                message=f"专家圆桌会议失败: {result.get('error', '未知错误')}",
                data=result
            )

        # 后台任务：保存分析结果
        if request.save_to_history:
            background_tasks.add_task(
                save_analysis_to_history,
                request.symbol,
                result
            )

        return AnalysisResponse(
            success=True,
            message="专家圆桌会议分析完成",
            data=result
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"专家圆桌会议API错误: {e}")
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@router.get("/status/{symbol}")
async def get_analysis_status(symbol: str):
    """获取股票分析状态"""
    try:
        # 这里可以实现分析状态查询逻辑
        # 目前返回模拟状态
        return {
            "symbol": symbol,
            "status": "completed",
            "last_analysis": datetime.now().isoformat(),
            "available_experts": ["technical", "fundamental", "news", "risk"]
        }
    except Exception as e:
        logger.error(f"获取分析状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")


@router.get("/history")
async def get_analysis_history(limit: int = 10):
    """获取分析历史记录"""
    try:
        # 这里可以实现历史记录查询逻辑
        # 目前返回模拟数据
        return {
            "total": 0,
            "data": [],
            "message": "历史记录功能正在开发中"
        }
    except Exception as e:
        logger.error(f"获取历史记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取历史记录失败: {str(e)}")


@router.get("/experts")
async def get_available_experts():
    """获取可用专家列表"""
    try:
        return {
            "experts": [
                {
                    "id": "technical",
                    "name": "技术面分析师",
                    "description": "15年技术分析经验，专注技术指标、K线形态和趋势分析",
                    "specialties": ["MACD", "KDJ", "RSI", "布林带", "趋势线"],
                    "confidence": 0.85
                },
                {
                    "id": "fundamental",
                    "name": "基本面分析师",
                    "description": "专业财务分析背景，精通估值模型和行业分析",
                    "specialties": ["财务报表", "估值模型", "ROE分析", "竞争优势"],
                    "confidence": 0.80
                },
                {
                    "id": "news",
                    "name": "新闻分析师",
                    "description": "资深财经记者背景，擅长新闻情感分析和事件解读",
                    "specialties": ["情感分析", "政策解读", "市场情绪", "舆情监测"],
                    "confidence": 0.75
                },
                {
                    "id": "risk",
                    "name": "风控分析师",
                    "description": "专业风险管理师，专注投资风险控制和仓位管理",
                    "specialties": ["VaR计算", "仓位管理", "止损策略", "波动率分析"],
                    "confidence": 0.85
                }
            ]
        }
    except Exception as e:
        logger.error(f"获取专家列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取专家列表失败: {str(e)}")


@router.get("/health")
async def health_check():
    """专家圆桌会议系统健康检查"""
    try:
        # 检查GLM服务状态
        glm_status = await glm_analyzer.health_check()

        return {
            "status": "healthy" if glm_status else "degraded",
            "glm_service": "online" if glm_status else "offline",
            "experts_available": 4,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.post("/quick-analysis")
async def quick_analysis(symbol: str):
    """快速分析（简化版）"""
    try:
        logger.info(f"快速分析: {symbol}")

        # 只调用技术分析师进行快速分析
        from services.ai_service.glm_analyzer import get_expert_analysis

        content = f"""
        请对股票 {symbol} 进行快速技术分析：
        - 当前技术指标状况
        - 短期走势判断
        - 关键技术价位
        - 简单操作建议
        """

        result = await get_expert_analysis("technical", content)

        return {
            "success": True,
            "symbol": symbol,
            "expert_type": "technical",
            "analysis": result,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"快速分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"快速分析失败: {str(e)}")


async def save_analysis_to_history(symbol: str, analysis_result: Dict[str, Any]):
    """保存分析结果到历史记录"""
    try:
        # 这里可以实现历史记录保存逻辑
        # 例如保存到数据库或文件
        logger.info(f"保存分析结果到历史记录: {symbol}")

        # 模拟保存操作
        await asyncio.sleep(0.1)  # 模拟数据库写入时间

        logger.info(f"分析结果已保存: {symbol}")
    except Exception as e:
        logger.error(f"保存历史记录失败: {e}")


# 导入必要的异步库
import asyncio