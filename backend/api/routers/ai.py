"""
AI分析API路由
提供AI投资分析相关的API接口

Author: Smart Stock Insider Team
Version: 1.0.0
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from services.ai_service import ai_service, AnalystRole
from core.exceptions import AIServiceError

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/ai", tags=["AI分析"])


# 请求模型
class AnalysisRequest(BaseModel):
    """AI分析请求"""
    symbol: str = Field(..., description="股票代码", min_length=1, max_length=10)
    question: str = Field(..., description="分析问题", min_length=1, max_length=1000)
    role: str = Field(..., description="分析师角色", pattern="^(technical_analyst|fundamental_analyst|news_analyst|risk_analyst)$")
    use_cache: bool = Field(True, description="是否使用缓存")
    additional_context: Optional[Dict[str, Any]] = Field(None, description="额外上下文信息")


class ComprehensiveAnalysisRequest(BaseModel):
    """综合分析请求"""
    symbol: str = Field(..., description="股票代码", min_length=1, max_length=10)
    question: str = Field(..., description="分析问题", min_length=1, max_length=1000)
    roles: Optional[List[str]] = Field(None, description="分析师角色列表")
    use_cache: bool = Field(True, description="是否使用缓存")


class ExportRequest(BaseModel):
    """导出报告请求"""
    symbol: str = Field(..., description="股票代码", min_length=1, max_length=10)
    analysis_ids: Optional[List[int]] = Field(None, description="分析记录ID列表")
    format: str = Field("markdown", description="导出格式", pattern="^(markdown|html)$")


# 响应模型
class AnalysisResponse(BaseModel):
    """分析响应"""
    role: str
    symbol: str
    question: str
    answer: str
    confidence: float
    reasoning: Optional[str] = None
    suggestions: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class ComprehensiveAnalysisResponse(BaseModel):
    """综合分析响应"""
    symbol: str
    question: str
    results: Dict[str, AnalysisResponse]
    summary: Optional[str] = None


class HistoryResponse(BaseModel):
    """历史记录响应"""
    id: int
    symbol: str
    role: str
    question: str
    answer: str
    confidence: float
    created_at: str


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    service: str
    version: str
    glm_client: str
    analysts: List[str]
    timestamp: str


# 辅助函数
def validate_analyst_role(role: str) -> AnalystRole:
    """验证分析师角色"""
    try:
        return AnalystRole(role)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的分析师角色: {role}，支持的 roles: {[r.value for r in AnalystRole]}"
        )


def validate_analyst_roles(roles: Optional[List[str]]) -> Optional[List[AnalystRole]]:
    """验证分析师角色列表"""
    if not roles:
        return None

    valid_roles = []
    invalid_roles = []

    for role in roles:
        try:
            valid_roles.append(AnalystRole(role))
        except ValueError:
            invalid_roles.append(role)

    if invalid_roles:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的分析师角色: {invalid_roles}，支持的 roles: {[r.value for r in AnalystRole]}"
        )

    return valid_roles


# API端点
@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_stock(request: AnalysisRequest):
    """
    对指定股票进行AI分析

    - **symbol**: 股票代码
    - **question**: 分析问题
    - **role**: 分析师角色 (technical_analyst, fundamental_analyst, news_analyst, risk_analyst)
    - **use_cache**: 是否使用缓存
    - **additional_context**: 额外上下文信息
    """
    try:
        # 验证分析师角色
        analyst_role = validate_analyst_role(request.role)

        # 执行分析
        result = await ai_service.analyze_stock(
            symbol=request.symbol,
            question=request.question,
            role=analyst_role,
            use_cache=request.use_cache,
            additional_context=request.additional_context
        )

        return AnalysisResponse(
            role=result.role.value,
            symbol=result.symbol,
            question=result.question,
            answer=result.answer,
            confidence=result.confidence,
            reasoning=result.reasoning,
            suggestions=result.suggestions,
            metadata=result.metadata
        )

    except AIServiceError as e:
        logger.error(f"AI分析API错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"AI分析API未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/analyze/stream")
async def analyze_stock_stream(request: AnalysisRequest):
    """
    流式AI分析

    - **symbol**: 股票代码
    - **question**: 分析问题
    - **role**: 分析师角色
    - **additional_context**: 额外上下文信息

    返回Server-Sent Events流式响应
    """
    try:
        # 验证分析师角色
        analyst_role = validate_analyst_role(request.role)

        async def generate():
            try:
                async for chunk in ai_service.analyze_stock_stream(
                    symbol=request.symbol,
                    question=request.question,
                    role=analyst_role,
                    additional_context=request.additional_context
                ):
                    yield f"data: {chunk}\n\n"

                yield "data: [DONE]\n\n"

            except Exception as e:
                logger.error(f"流式分析错误: {str(e)}")
                yield f"data: ERROR: {str(e)}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"  # 禁用nginx缓冲
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"流式AI分析API错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/analyze/comprehensive", response_model=ComprehensiveAnalysisResponse)
async def analyze_comprehensive(request: ComprehensiveAnalysisRequest):
    """
    综合分析（使用多个分析师）

    - **symbol**: 股票代码
    - **question**: 分析问题
    - **roles**: 分析师角色列表，空表示使用所有分析师
    - **use_cache**: 是否使用缓存
    """
    try:
        # 验证分析师角色
        analyst_roles = validate_analyst_roles(request.roles)

        # 执行综合分析
        results = await ai_service.analyze_comprehensive(
            symbol=request.symbol,
            question=request.question,
            roles=analyst_roles,
            use_cache=request.use_cache
        )

        # 转换响应格式
        analysis_results = {}
        for role, result in results.items():
            if result:
                analysis_results[role.value] = AnalysisResponse(
                    role=result.role.value,
                    symbol=result.symbol,
                    question=result.question,
                    answer=result.answer,
                    confidence=result.confidence,
                    reasoning=result.reasoning,
                    suggestions=result.suggestions,
                    metadata=result.metadata
                )

        # 生成简单总结
        summary = f"已完成{len(analysis_results)}个分析师的综合分析。"

        return ComprehensiveAnalysisResponse(
            symbol=request.symbol,
            question=request.question,
            results=analysis_results,
            summary=summary
        )

    except AIServiceError as e:
        logger.error(f"综合分析API错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"综合分析API未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/analyze/comprehensive/stream")
async def analyze_comprehensive_stream(request: ComprehensiveAnalysisRequest):
    """
    流式综合分析

    - **symbol**: 股票代码
    - **question**: 分析问题
    - **roles**: 分析师角色列表，空表示使用所有分析师

    返回Server-Sent Events流式响应
    """
    try:
        # 验证分析师角色
        analyst_roles = validate_analyst_roles(request.roles)

        async def generate():
            try:
                async for chunk in ai_service.analyze_comprehensive_stream(
                    symbol=request.symbol,
                    question=request.question,
                    roles=analyst_roles
                ):
                    yield f"data: {chunk}\n\n"

                yield "data: [DONE]\n\n"

            except Exception as e:
                logger.error(f"流式综合分析错误: {str(e)}")
                yield f"data: ERROR: {str(e)}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"流式综合分析API错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/suggestions/{symbol}")
async def get_analysis_suggestions(
    symbol: str,
    role: Optional[str] = Query(None, description="分析师角色")
):
    """
    获取分析建议

    - **symbol**: 股票代码
    - **role**: 分析师角色，可选
    """
    try:
        # 验证分析师角色
        analyst_role = None
        if role:
            analyst_role = validate_analyst_role(role)

        # 获取建议
        suggestions = await ai_service.get_analysis_suggestions(symbol, analyst_role)

        return {
            "symbol": symbol,
            "role": role,
            "suggestions": suggestions
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取分析建议API错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/history")
async def get_analysis_history(
    symbol: Optional[str] = Query(None, description="股票代码"),
    role: Optional[str] = Query(None, description="分析师角色"),
    limit: int = Query(50, ge=1, le=200, description="返回记录数限制"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """
    获取分析历史记录

    - **symbol**: 股票代码，可选
    - **role**: 分析师角色，可选
    - **limit**: 返回记录数限制
    - **offset**: 偏移量
    """
    try:
        # 验证分析师角色
        analyst_role = None
        if role:
            analyst_role = validate_analyst_role(role)

        # 获取历史记录
        history = await ai_service.get_analysis_history(
            symbol=symbol,
            role=analyst_role,
            limit=limit,
            offset=offset
        )

        return {
            "symbol": symbol,
            "role": role,
            "limit": limit,
            "offset": offset,
            "total": len(history),
            "data": history
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取分析历史API错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/export")
async def export_analysis_report(request: ExportRequest):
    """
    导出分析报告

    - **symbol**: 股票代码
    - **analysis_ids**: 分析记录ID列表，可选
    - **format**: 导出格式 (markdown, html)
    """
    try:
        # 导出报告
        report_content = await ai_service.export_analysis_report(
            symbol=request.symbol,
            analysis_ids=request.analysis_ids,
            format=request.format
        )

        # 设置响应头
        filename = f"{request.symbol}_AI分析报告_{request.format}"
        media_type = "text/markdown" if request.format == "markdown" else "text/html"

        return StreamingResponse(
            iter([report_content]),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except AIServiceError as e:
        logger.error(f"导出报告API错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"导出报告API未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """AI服务健康检查"""
    try:
        health_data = await ai_service.health_check()
        return HealthResponse(**health_data)

    except Exception as e:
        logger.error(f"AI服务健康检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail="健康检查失败")


@router.get("/roles")
async def get_analyst_roles():
    """获取所有可用的分析师角色"""
    roles = []
    for role in AnalystRole:
        roles.append({
            "value": role.value,
            "name": role.value.replace("_analyst", "").replace("_", " ").title(),
            "description": get_role_description(role)
        })

    return {
        "roles": roles,
        "total": len(roles)
    }


def get_role_description(role: AnalystRole) -> str:
    """获取角色描述"""
    descriptions = {
        AnalystRole.TECHNICAL: "专业技术分析，基于技术指标和价格走势",
        AnalystRole.FUNDAMENTAL: "基本面分析，关注公司财务和行业状况",
        AnalystRole.NEWS: "新闻分析，基于市场情绪和政策变化",
        AnalystRole.RISK: "风控分析，专注风险评估和控制策略"
    }
    return descriptions.get(role, "专业投资分析师")


# 注意：异常处理器已在 main.py 中设置