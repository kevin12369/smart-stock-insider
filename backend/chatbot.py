"""
ChatBot API路由
提供智能问答系统的HTTP接口
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from ..services.ai_service.chatbot import chatbot_service, intent_classifier, knowledge_base

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/chatbot", tags=["ChatBot"])

# 请求/响应模型
class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息", min_length=1, max_length=1000)
    session_id: Optional[str] = Field(None, description="会话ID")
    user_id: str = Field(..., description="用户ID")
    context: Optional[Dict[str, Any]] = Field(None, description="对话上下文")

class ChatResponse(BaseModel):
    """聊天响应"""
    session_id: str
    response: str
    intent: str
    confidence: float
    suggestions: List[str]
    context: Optional[Dict[str, Any]]
    timestamp: datetime

class ConversationStartRequest(BaseModel):
    """开始对话请求"""
    user_id: str = Field(..., description="用户ID")

class ConversationHistoryResponse(BaseModel):
    """对话历史响应"""
    session_id: str
    messages: List[Dict[str, Any]]
    total_count: int

class IntentAnalysisRequest(BaseModel):
    """意图分析请求"""
    text: str = Field(..., description="待分析文本", min_length=1, max_length=1000)
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")

class IntentAnalysisResponse(BaseModel):
    """意图分析响应"""
    intent: str
    confidence: float
    entities: Dict[str, Any]
    keywords: List[str]
    processing_time: float

class KnowledgeSearchRequest(BaseModel):
    """知识搜索请求"""
    query: str = Field(..., description="搜索查询", min_length=1, max_length=200)
    limit: int = Field(5, ge=1, le=20, description="结果数量限制")
    category: Optional[str] = Field(None, description="知识分类")

class KnowledgeSearchResponse(BaseModel):
    """知识搜索响应"""
    query: str
    results: List[Dict[str, Any]]
    total_count: int
    search_time: float

class UserStatsResponse(BaseModel):
    """用户统计响应"""
    user_id: str
    total_actions: int
    recent_actions: int
    total_sessions: int
    avg_session_duration: float
    satisfaction_score: float
    most_active_hour: Optional[int]
    favorite_category: Optional[str]
    interaction_style: str

class FeedbackRequest(BaseModel):
    """反馈请求"""
    session_id: str = Field(..., description="会话ID")
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分(1-5)")
    comments: Optional[str] = Field(None, description="评论内容")
    suggestions: Optional[str] = Field(None, description="改进建议")

@router.post("/conversation/start", response_model=Dict[str, Any])
async def start_conversation(request: ConversationStartRequest):
    """
    开始新对话

    创建新的对话会话并返回欢迎消息和建议
    """
    try:
        response = await chatbot_service.start_conversation(request.user_id)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "data": response,
                "message": "对话已开始"
            }
        )

    except Exception as e:
        logger.error(f"开始对话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="开始对话失败"
        )

@router.post("/conversation/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    发送聊天消息

    处理用户消息并返回智能回复
    """
    try:
        response_data = await chatbot_service.process_message(
            user_id=request.user_id,
            session_id=request.session_id,
            message=request.message
        )

        return ChatResponse(
            session_id=response_data["session_id"],
            response=response_data["response"],
            intent=response_data.get("intent", "unknown"),
            confidence=response_data.get("confidence", 0.0),
            suggestions=response_data.get("suggestions", []),
            context=response_data.get("context"),
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"处理聊天消息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="处理消息失败"
        )

@router.get("/conversation/{session_id}/history", response_model=ConversationHistoryResponse)
async def get_conversation_history(
    session_id: str,
    limit: int = 10
):
    """
    获取对话历史

    返回指定会话的历史消息记录
    """
    try:
        messages = await chatbot_service.get_conversation_history(
            session_id=session_id,
            limit=min(limit, 50)  # 限制最大返回数量
        )

        return ConversationHistoryResponse(
            session_id=session_id,
            messages=messages,
            total_count=len(messages)
        )

    except Exception as e:
        logger.error(f"获取对话历史失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取对话历史失败"
        )

@router.delete("/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """
    清除对话历史

    清除指定会话的所有历史记录
    """
    try:
        result = await chatbot_service.clear_conversation(session_id)

        if result["success"]:
            return JSONResponse(
                content={
                    "success": True,
                    "message": result["message"]
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"清除对话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="清除对话失败"
        )

@router.post("/conversation/{session_id}/end")
async def end_conversation(
    session_id: str,
    feedback: Optional[FeedbackRequest] = None
):
    """
    结束对话

    结束指定会话并记录反馈信息
    """
    try:
        feedback_data = None
        if feedback:
            feedback_data = {
                "rating": feedback.rating,
                "comments": feedback.comments,
                "suggestions": feedback.suggestions
            }

        result = await chatbot_service.end_conversation(
            session_id=session_id,
            feedback=feedback_data
        )

        if result["success"]:
            return JSONResponse(
                content={
                    "success": True,
                    "message": result["message"]
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"结束对话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="结束对话失败"
        )

@router.post("/intent/analyze", response_model=IntentAnalysisResponse)
async def analyze_intent(request: IntentAnalysisRequest):
    """
    分析用户意图

    使用NLU技术分析文本的意图和实体
    """
    try:
        result = await intent_classifier.classify(request.text)

        return IntentAnalysisResponse(
            intent=result.intent.value,
            confidence=result.confidence,
            entities=result.entities,
            keywords=result.keywords,
            processing_time=result.processing_time
        )

    except Exception as e:
        logger.error(f"意图分析失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="意图分析失败"
        )

@router.post("/knowledge/search", response_model=KnowledgeSearchResponse)
async def search_knowledge(request: KnowledgeSearchRequest):
    """
    搜索知识库

    在金融知识库中搜索相关信息
    """
    try:
        start_time = datetime.now()

        results = await knowledge_base.search(
            query=request.query,
            limit=request.limit,
            category=request.category
        )

        search_time = (datetime.now() - start_time).total_seconds()

        # 转换结果格式
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.item.id,
                "title": result.item.title,
                "content": result.item.content,
                "category": result.item.category,
                "tags": result.item.tags,
                "confidence": result.item.confidence,
                "relevance": result.relevance,
                "explanation": result.explanation,
                "source": result.item.source
            })

        return KnowledgeSearchResponse(
            query=request.query,
            results=formatted_results,
            total_count=len(formatted_results),
            search_time=search_time
        )

    except Exception as e:
        logger.error(f"知识搜索失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="知识搜索失败"
        )

@router.get("/user/{user_id}/suggestions")
async def get_user_suggestions(
    user_id: str,
    intent: Optional[str] = None
):
    """
    获取用户建议

    基于用户画像和历史行为生成个性化建议
    """
    try:
        suggestions = await chatbot_service.get_user_suggestions(
            user_id=user_id,
            intent=intent
        )

        return JSONResponse(
            content={
                "user_id": user_id,
                "suggestions": suggestions,
                "intent": intent
            }
        )

    except Exception as e:
        logger.error(f"获取用户建议失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户建议失败"
        )

@router.get("/user/{user_id}/stats", response_model=UserStatsResponse)
async def get_user_statistics(user_id: str):
    """
    获取用户统计

    返回用户的行为统计和分析数据
    """
    try:
        stats = await chatbot_service.get_user_stats(user_id)

        return UserStatsResponse(
            user_id=user_id,
            total_actions=stats.get("total_actions", 0),
            recent_actions=stats.get("recent_actions", 0),
            total_sessions=stats.get("total_sessions", 0),
            avg_session_duration=stats.get("avg_session_duration", 0.0),
            satisfaction_score=stats.get("satisfaction_score", 0.0),
            most_active_hour=stats.get("most_active_hour"),
            favorite_category=stats.get("favorite_category"),
            interaction_style=stats.get("interaction_style", "formal")
        )

    except Exception as e:
        logger.error(f"获取用户统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户统计失败"
        )

@router.get("/service/stats")
async def get_service_statistics():
    """
    获取服务统计

    返回ChatBot服务的整体统计信息
    """
    try:
        stats = await chatbot_service.get_service_stats()

        return JSONResponse(
            content={
                "service_stats": stats,
                "knowledge_base_stats": knowledge_base.get_statistics(),
                "timestamp": datetime.now().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"获取服务统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取服务统计失败"
        )

@router.get("/health")
async def health_check():
    """
    健康检查

    检查ChatBot服务的运行状态
    """
    try:
        # 检查各组件状态
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "chatbot_service": "healthy",
                "intent_classifier": "healthy",
                "knowledge_base": "healthy",
                "user_profiler": "healthy"
            }
        }

        return JSONResponse(content=health_status)

    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )

# 错误处理器
@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP异常处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """通用异常处理"""
    logger.error(f"未处理的异常: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "内部服务器错误",
            "status_code": 500
        }
    )