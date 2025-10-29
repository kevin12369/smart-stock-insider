"""
新闻API路由
提供新闻相关的API接口

Author: Smart Stock Insider Team
Version: 1.0.0
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from services.news_service import news_service
from core.exceptions import ExternalServiceError, ValidationError

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/news", tags=["新闻"])


# 请求模型
class NewsListRequest(BaseModel):
    """新闻列表请求"""
    category: Optional[str] = Field(None, description="新闻分类")
    source: Optional[str] = Field(None, description="新闻来源")
    stock_code: Optional[str] = Field(None, description="股票代码")
    sentiment: Optional[str] = Field(None, description="情感倾向")
    keyword: Optional[str] = Field(None, description="搜索关键词")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    limit: int = Field(20, ge=1, le=200, description="返回数量限制")
    offset: int = Field(0, ge=0, description="偏移量")
    sort_by: str = Field("publish_time", description="排序字段")
    sort_order: str = Field("desc", description="排序顺序")


class NewsSearchRequest(BaseModel):
    """新闻搜索请求"""
    query: str = Field(..., description="搜索关键词", min_length=1, max_length=100)
    limit: int = Field(20, ge=1, le=100, description="返回数量限制")


# 响应模型
class NewsResponse(BaseModel):
    """新闻响应"""
    id: int
    title: str
    summary: str
    source: str
    author: Optional[str]
    publish_time: Optional[str]
    url: str
    image_url: Optional[str]
    category: Optional[str]
    tags: List[str]
    keywords: List[str]
    mentioned_stocks: List[str]
    relevance_score: float
    created_at: Optional[str]


class NewsDetailResponse(BaseModel):
    """新闻详情响应"""
    id: int
    title: str
    summary: str
    content: str
    source: str
    author: Optional[str]
    publish_time: Optional[str]
    url: str
    image_url: Optional[str]
    category: Optional[str]
    tags: List[str]
    keywords: List[str]
    mentioned_stocks: List[str]
    relevance_score: float
    created_at: Optional[str]
    sentiment: Optional[Dict[str, Any]]


class NewsListResponse(BaseModel):
    """新闻列表响应"""
    data: List[NewsResponse]
    total: int
    limit: int
    offset: int
    filters: Dict[str, Any]
    sort: Dict[str, str]


class NewsStatisticsResponse(BaseModel):
    """新闻统计响应"""
    total_news: int
    today_news: int
    categories: Dict[str, int]
    sources: Dict[str, int]
    latest_update: Optional[str]
    generated_at: str


class NewsSourceResponse(BaseModel):
    """新闻源响应"""
    name: str
    category: str
    enabled: bool


class RecommendationRequest(BaseModel):
    """推荐请求"""
    user_id: str = Field(..., description="用户ID")
    limit: int = Field(20, ge=1, le=100, description="推荐数量限制")


class FeedbackRequest(BaseModel):
    """用户反馈请求"""
    user_id: str = Field(..., description="用户ID")
    news_id: int = Field(..., description="新闻ID")
    feedback_type: str = Field(..., description="反馈类型")
    feedback_data: Optional[Dict[str, Any]] = Field(None, description="反馈数据")


class RecommendationResponse(BaseModel):
    """推荐响应"""
    id: int
    title: str
    summary: str
    source: str
    publish_time: Optional[str]
    recommendation_score: float
    recommendation_reasons: List[str]
    recommendation_type: str
    confidence: float


# API端点
@router.get("/list", response_model=NewsListResponse)
async def get_news_list(
    category: Optional[str] = Query(None, description="新闻分类"),
    source: Optional[str] = Query(None, description="新闻来源"),
    stock_code: Optional[str] = Query(None, description="股票代码"),
    sentiment: Optional[str] = Query(None, description="情感倾向"),
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    limit: int = Query(20, ge=1, le=200, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    sort_by: str = Query("publish_time", description="排序字段"),
    sort_order: str = Query("desc", description="排序顺序")
):
    """
    获取新闻列表

    - **category**: 新闻分类
    - **source**: 新闻来源
    - **stock_code**: 股票代码
    - **sentiment**: 情感倾向 (positive, negative, neutral)
    - **keyword**: 搜索关键词
    - **start_date**: 开始日期
    - **end_date**: 结束日期
    - **limit**: 返回数量限制
    - **offset**: 偏移量
    - **sort_by**: 排序字段 (publish_time, relevance_score)
    - **sort_order**: 排序顺序 (asc, desc)
    """
    try:
        result = await news_service.get_news_list(
            category=category,
            source=source,
            stock_code=stock_code,
            sentiment=sentiment,
            keyword=keyword,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )

        return NewsListResponse(**result)

    except Exception as e:
        logger.error(f"获取新闻列表API错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/{news_id}", response_model=NewsDetailResponse)
async def get_news_detail(news_id: int):
    """
    获取新闻详情

    - **news_id**: 新闻ID
    """
    try:
        detail = await news_service.get_news_detail(news_id)
        if not detail:
            raise HTTPException(status_code=404, detail="新闻不存在")

        return NewsDetailResponse(**detail)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取新闻详情API错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/stock/{stock_code}")
async def get_news_by_stock(
    stock_code: str,
    days: int = Query(7, ge=1, le=30, description="获取天数"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制")
):
    """
    获取指定股票的相关新闻

    - **stock_code**: 股票代码
    - **days**: 获取天数
    - **limit**: 返回数量限制
    """
    try:
        news_list = await news_service.get_news_by_stock(
            stock_code=stock_code,
            days=days,
            limit=limit
        )

        return {
            "stock_code": stock_code,
            "days": days,
            "data": news_list,
            "total": len(news_list)
        }

    except Exception as e:
        logger.error(f"获取股票新闻API错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/search")
async def search_news(request: NewsSearchRequest):
    """
    搜索新闻

    - **query**: 搜索关键词
    - **limit**: 返回数量限制
    """
    try:
        news_list = await news_service.search_news(
            query=request.query,
            limit=request.limit
        )

        return {
            "query": request.query,
            "data": news_list,
            "total": len(news_list)
        }

    except Exception as e:
        logger.error(f"搜索新闻API错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/sources", response_model=List[NewsSourceResponse])
async def get_news_sources():
    """获取新闻源列表"""
    try:
        sources = await news_service.get_news_sources()
        return [NewsSourceResponse(**source) for source in sources]

    except Exception as e:
        logger.error(f"获取新闻源API错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/statistics", response_model=NewsStatisticsResponse)
async def get_news_statistics():
    """获取新闻统计信息"""
    try:
        statistics = await news_service.get_news_statistics()
        return NewsStatisticsResponse(**statistics)

    except Exception as e:
        logger.error(f"获取新闻统计API错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/collect")
async def collect_news(background_tasks: BackgroundTasks, force_refresh: bool = False):
    """
    采集新闻

    - **force_refresh**: 是否强制刷新
    """
    try:
        # 异步执行新闻采集
        background_tasks.add_task(news_service.collect_and_process_news, force_refresh)

        return {
            "message": "新闻采集任务已启动",
            "force_refresh": force_refresh,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"采集新闻API错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/health")
async def health_check():
    """新闻服务健康检查"""
    try:
        health_data = await news_service.health_check()
        return health_data

    except Exception as e:
        logger.error(f"新闻服务健康检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail="健康检查失败")


@router.get("/categories")
async def get_news_categories():
    """获取新闻分类列表"""
    try:
        categories = [
            {"value": "财经", "label": "财经新闻"},
            {"value": "证券", "label": "证券新闻"},
            {"value": "政策", "label": "政策新闻"},
            {"value": "公司", "label": "公司新闻"},
            {"value": "国际", "label": "国际新闻"},
            {"value": "科技", "label": "科技新闻"}
        ]

        return {
            "categories": categories,
            "total": len(categories)
        }

    except Exception as e:
        logger.error(f"获取新闻分类API错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/sentiment/summary")
async def get_sentiment_summary(
    stock_code: Optional[str] = Query(None, description="股票代码"),
    days: int = Query(7, ge=1, le=30, description="统计天数")
):
    """
    获取情感分析摘要

    - **stock_code**: 股票代码（可选）
    - **days**: 统计天数
    """
    try:
        summary = await news_service.get_sentiment_summary(stock_code, days)
        return summary

    except Exception as e:
        logger.error(f"获取情感摘要API错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/recommendations", response_model=List[RecommendationResponse])
async def get_personalized_recommendations(request: RecommendationRequest):
    """
    获取个性化新闻推荐

    - **user_id**: 用户ID
    - **limit**: 推荐数量限制
    """
    try:
        recommendations = await news_service.get_personalized_recommendations(
            user_id=request.user_id,
            limit=request.limit
        )

        return [RecommendationResponse(**rec) for rec in recommendations]

    except Exception as e:
        logger.error(f"获取个性化推荐API错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/feedback")
async def update_user_feedback(request: FeedbackRequest):
    """
    更新用户反馈

    - **user_id**: 用户ID
    - **news_id**: 新闻ID
    - **feedback_type**: 反馈类型 (like, dislike, share, comment, bookmark)
    - **feedback_data**: 反馈数据
    """
    try:
        await news_service.update_user_feedback(
            user_id=request.user_id,
            news_id=request.news_id,
            feedback_type=request.feedback_type,
            feedback_data=request.feedback_data
        )

        return {
            "message": "用户反馈已更新",
            "user_id": request.user_id,
            "news_id": request.news_id,
            "feedback_type": request.feedback_type,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"更新用户反馈API错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/recommendations/{user_id}/explanation/{news_id}")
async def get_recommendation_explanation(user_id: str, news_id: int):
    """
    获取推荐解释

    - **user_id**: 用户ID
    - **news_id**: 新闻ID
    """
    try:
        explanation = await news_service.get_recommendation_explanation(user_id, news_id)
        return explanation

    except Exception as e:
        logger.error(f"获取推荐解释API错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.get("/hot")
async def get_hot_news(
    limit: int = Query(20, ge=1, le=100, description="返回数量限制")
):
    """
    获取热门新闻

    - **limit**: 返回数量限制
    """
    try:
        hot_news = await news_service.get_hot_news(limit)
        return {
            "data": hot_news,
            "total": len(hot_news),
            "generated_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"获取热门新闻API错误: {str(e)}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


# 注意：异常处理器已在 main.py 中设置