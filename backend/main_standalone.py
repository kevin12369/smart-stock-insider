#!/usr/bin/env python3
"""
智股通AI增强轻量化版独立主应用

Author: Smart Stock Insider Team
Version: 1.0.0
"""

import sys
import os
sys.path.append('.')

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from contextlib import asynccontextmanager
from datetime import datetime

# 直接导入需要的组件，避免复杂依赖
try:
    from services.ai_service.glm_analyzer import glm_analyzer
    GLM_AVAILABLE = True
    logger.info("[SUCCESS] GLM-4.5-Flash AI服务可用")
except ImportError as e:
    GLM_AVAILABLE = False
    logger.warning(f"[WARNING] GLM服务不可用: {e}")

try:
    from services.data_service.stock_service_lite import stock_service_lite
    DATA_SERVICE_AVAILABLE = True
    logger.info("[SUCCESS] 股票数据服务可用")
except ImportError as e:
    DATA_SERVICE_AVAILABLE = False
    logger.warning(f"[WARNING] 股票数据服务不可用: {e}")

try:
    from services.ai_service.expert_roundtable.round_table_coordinator import round_table_coordinator
    ROUND_TABLE_AVAILABLE = True
    logger.info("[SUCCESS] 专家圆桌会议系统可用")
except ImportError as e:
    ROUND_TABLE_AVAILABLE = False
    logger.warning(f"[WARNING] 专家圆桌会议系统不可用: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("[INFO] 智股通AI增强轻量化版启动中...")

    if GLM_AVAILABLE:
        try:
            glm_healthy = await glm_analyzer.health_check()
            if glm_healthy:
                logger.info("[SUCCESS] GLM-4.5-Flash AI服务连接正常")
            else:
                logger.warning("[WARNING] GLM-4.5-Flash AI服务连接异常")
        except Exception as e:
            logger.error(f"[ERROR] GLM服务检查失败: {e}")

    logger.info("[INFO] 智股通AI增强轻量化版启动完成")
    yield
    logger.info("[INFO] 智股通应用正在关闭...")


# 创建FastAPI应用
app = FastAPI(
    title="智股通AI增强轻量化版",
    description="基于GLM-4.5-Flash的智能股票分析平台",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "智股通AI增强轻量化版",
        "version": "1.0.0",
        "status": "running",
        "services": {
            "glm_ai": GLM_AVAILABLE,
            "data_service": DATA_SERVICE_AVAILABLE,
            "expert_roundtable": ROUND_TABLE_AVAILABLE
        },
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "services": {}
    }

    if GLM_AVAILABLE:
        try:
            glm_status = await glm_analyzer.health_check()
            health_status["services"]["glm_ai"] = "healthy" if glm_status else "unhealthy"
        except Exception as e:
            health_status["services"]["glm_ai"] = f"error: {str(e)}"
    else:
        health_status["services"]["glm_ai"] = "unavailable"

    health_status["services"]["data_service"] = "available" if DATA_SERVICE_AVAILABLE else "unavailable"
    health_status["services"]["expert_roundtable"] = "available" if ROUND_TABLE_AVAILABLE else "unavailable"

    return health_status


@app.get("/api/expert-roundtable/experts")
async def get_available_experts():
    """获取可用专家列表"""
    return {
        "experts": [
            {
                "id": "technical",
                "name": "技术面分析师",
                "description": "15年技术分析经验，专注技术指标、K线形态和趋势分析",
                "specialties": ["MACD", "KDJ", "RSI", "布林带", "趋势线"],
                "confidence": 0.85,
                "available": GLM_AVAILABLE
            },
            {
                "id": "fundamental",
                "name": "基本面分析师",
                "description": "专业财务分析背景，精通估值模型和行业分析",
                "specialties": ["财务报表", "估值模型", "ROE分析", "竞争优势"],
                "confidence": 0.80,
                "available": GLM_AVAILABLE
            },
            {
                "id": "news",
                "name": "新闻分析师",
                "description": "资深财经记者背景，擅长新闻情感分析和事件解读",
                "specialties": ["情感分析", "政策解读", "市场情绪", "舆情监测"],
                "confidence": 0.75,
                "available": GLM_AVAILABLE
            },
            {
                "id": "risk",
                "name": "风控分析师",
                "description": "专业风险管理师，专注投资风险控制和仓位管理",
                "specialties": ["VaR计算", "仓位管理", "止损策略", "波动率分析"],
                "confidence": 0.85,
                "available": GLM_AVAILABLE
            }
        ]
    }


@app.post("/api/expert-roundtable/quick-analysis")
async def quick_analysis(symbol: str):
    """快速分析"""
    if not GLM_AVAILABLE:
        return {
            "success": False,
            "message": "GLM AI服务不可用",
            "symbol": symbol
        }

    try:
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
            "timestamp": str(datetime.now())
        }

    except Exception as e:
        logger.error(f"快速分析失败: {e}")
        return {
            "success": False,
            "message": f"分析失败: {str(e)}",
            "symbol": symbol
        }


@app.get("/api/stock/{symbol}/info")
async def get_stock_info(symbol: str):
    """获取股票信息"""
    if not DATA_SERVICE_AVAILABLE:
        return {
            "success": False,
            "error": "SERVICE_UNAVAILABLE",
            "message": "股票数据服务不可用，请稍后再试",
            "symbol": symbol
        }

    try:
        info = await stock_service_lite.get_stock_info(symbol)

        # 检查是否是错误响应
        if isinstance(info, dict) and info.get('success') == False:
            return info

        return {
            "success": True,
            "data": info
        }
    except Exception as e:
        logger.error(f"获取股票信息失败: {e}")
        return {
            "success": False,
            "error": "UNEXPECTED_ERROR",
            "message": f"获取失败: {str(e)}",
            "symbol": symbol
        }


@app.post("/api/expert-roundtable/full-analysis")
async def full_analysis(symbol: str):
    """完整专家圆桌分析"""
    if not ROUND_TABLE_AVAILABLE:
        return {
            "success": False,
            "message": "专家圆桌会议系统不可用",
            "symbol": symbol
        }

    try:
        result = await round_table_coordinator.start_round_table(symbol)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        logger.error(f"专家圆桌分析失败: {e}")
        return {
            "success": False,
            "message": f"分析失败: {str(e)}",
            "symbol": symbol
        }


def setup_logging():
    """配置日志"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )


if __name__ == "__main__":
    # 配置日志
    setup_logging()

    logger.info("=" * 60)
    logger.info("[STARTUP] 智股通AI增强轻量化版")
    logger.info("=" * 60)
    logger.info("   特性: 专家圆桌会议 + GLM-4.5-Flash AI")
    logger.info(f"   GLM服务: {'可用' if GLM_AVAILABLE else '不可用'}")
    logger.info(f"   数据服务: {'可用' if DATA_SERVICE_AVAILABLE else '不可用'}")
    logger.info(f"   专家系统: {'可用' if ROUND_TABLE_AVAILABLE else '不可用'}")
    logger.info("=" * 60)

    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8001,
            log_level="warning"
        )
    except KeyboardInterrupt:
        logger.info("[INFO] 应用已停止")
    except Exception as e:
        logger.error(f"[ERROR] 应用启动失败: {e}")
        sys.exit(1)