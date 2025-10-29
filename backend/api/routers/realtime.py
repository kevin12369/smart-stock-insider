"""
实时数据API路由
提供WebSocket连接和实时数据管理接口
"""

import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from services.realtime_service.service import (
    realtime_service,
    websocket_stock_endpoint,
    websocket_news_endpoint,
    websocket_alert_endpoint,
    websocket_system_endpoint,
    ensure_realtime_service_running
)
from core.exceptions import ValidationError

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/realtime", tags=["实时数据"])

# 请求模型
class BroadcastMessageRequest(BaseModel):
    """广播消息请求"""
    message_type: str = Field(..., description="消息类型")
    data: Dict[str, Any] = Field(..., description="消息数据")
    target_type: Optional[str] = Field(None, description="目标连接类型")

class UserNotificationRequest(BaseModel):
    """用户通知请求"""
    user_id: str = Field(..., description="用户ID")
    title: str = Field(..., description="通知标题")
    content: str = Field(..., description="通知内容")
    priority: str = Field("medium", description="通知优先级")

class StockSubscriptionRequest(BaseModel):
    """股票订阅请求"""
    stock_code: str = Field(..., description="股票代码")
    action: str = Field(..., description="操作: add/remove")

# 响应模型
class ServiceStatusResponse(BaseModel):
    """服务状态响应"""
    service: str
    status: str
    start_time: Optional[str]
    uptime_seconds: float
    components: Dict[str, Any]
    config: Dict[str, Any]

class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: str
    timestamp: str
    components: Dict[str, str]
    metrics: Dict[str, Any]

# WebSocket端点
@router.websocket("/stock")
async def websocket_stock(
    websocket: WebSocket,
    token: Optional[str] = Query(None, description="认证令牌")
):
    """
    股票数据WebSocket连接

    - **token**: 可选的认证令牌
    """
    try:
        # 确保实时服务正在运行
        await ensure_realtime_service_running()

        # 处理WebSocket连接
        await websocket_stock_endpoint(websocket, token)

    except WebSocketDisconnect:
        logger.info("股票数据WebSocket连接断开")
    except Exception as e:
        logger.error(f"股票数据WebSocket连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail="WebSocket连接失败")

@router.websocket("/news")
async def websocket_news(
    websocket: WebSocket,
    token: Optional[str] = Query(None, description="认证令牌")
):
    """
    新闻推送WebSocket连接

    - **token**: 可选的认证令牌
    """
    try:
        # 确保实时服务正在运行
        await ensure_realtime_service_running()

        # 处理WebSocket连接
        await websocket_news_endpoint(websocket, token)

    except WebSocketDisconnect:
        logger.info("新闻推送WebSocket连接断开")
    except Exception as e:
        logger.error(f"新闻推送WebSocket连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail="WebSocket连接失败")

@router.websocket("/alerts")
async def websocket_alerts(
    websocket: WebSocket,
    token: Optional[str] = Query(None, description="认证令牌")
):
    """
    市场提醒WebSocket连接

    - **token**: 可选的认证令牌
    """
    try:
        # 确保实时服务正在运行
        await ensure_realtime_service_running()

        # 处理WebSocket连接
        await websocket_alert_endpoint(websocket, token)

    except WebSocketDisconnect:
        logger.info("市场提醒WebSocket连接断开")
    except Exception as e:
        logger.error(f"市场提醒WebSocket连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail="WebSocket连接失败")

@router.websocket("/system")
async def websocket_system(
    websocket: WebSocket,
    token: Optional[str] = Query(None, description="认证令牌")
):
    """
    系统通知WebSocket连接

    - **token**: 可选的认证令牌
    """
    try:
        # 确保实时服务正在运行
        await ensure_realtime_service_running()

        # 处理WebSocket连接
        await websocket_system_endpoint(websocket, token)

    except WebSocketDisconnect:
        logger.info("系统通知WebSocket连接断开")
    except Exception as e:
        logger.error(f"系统通知WebSocket连接失败: {str(e)}")
        raise HTTPException(status_code=500, detail="WebSocket连接失败")

# REST API端点
@router.get("/status", response_model=ServiceStatusResponse)
async def get_service_status():
    """获取实时服务状态"""
    try:
        status_data = realtime_service.get_service_status()
        return ServiceStatusResponse(**status_data)

    except Exception as e:
        logger.error(f"获取服务状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取服务状态失败")

@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """实时服务健康检查"""
    try:
        health_data = await realtime_service.health_check()
        return HealthCheckResponse(**health_data)

    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail="健康检查失败")

@router.post("/start")
async def start_service():
    """启动实时服务"""
    try:
        if realtime_service.is_running:
            return {"message": "实时服务已在运行", "status": "running"}

        await realtime_service.start()
        return {"message": "实时服务启动成功", "status": "running"}

    except Exception as e:
        logger.error(f"启动实时服务失败: {str(e)}")
        raise HTTPException(status_code=500, detail="启动实时服务失败")

@router.post("/stop")
async def stop_service():
    """停止实时服务"""
    try:
        if not realtime_service.is_running:
            return {"message": "实时服务未运行", "status": "stopped"}

        await realtime_service.stop()
        return {"message": "实时服务已停止", "status": "stopped"}

    except Exception as e:
        logger.error(f"停止实时服务失败: {str(e)}")
        raise HTTPException(status_code=500, detail="停止实时服务失败")

@router.post("/broadcast")
async def send_broadcast_message(request: BroadcastMessageRequest):
    """
    发送广播消息

    - **message_type**: 消息类型
    - **data**: 消息数据
    - **target_type**: 目标连接类型（可选）
    """
    try:
        # 确保服务正在运行
        await ensure_realtime_service_running()

        # 发送广播消息
        await realtime_service.send_broadcast_message(
            message_data={
                "type": request.message_type,
                "data": request.data
            },
            target_type=request.target_type
        )

        return {
            "message": "广播消息发送成功",
            "message_type": request.message_type,
            "target_type": request.target_type,
            "timestamp": "2024-01-01T00:00:00Z"  # 应该使用实际时间
        }

    except Exception as e:
        logger.error(f"发送广播消息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="发送广播消息失败")

@router.post("/notify")
async def send_user_notification(request: UserNotificationRequest):
    """
    发送用户通知

    - **user_id**: 用户ID
    - **title**: 通知标题
    - **content**: 通知内容
    - **priority**: 通知优先级
    """
    try:
        # 确保服务正在运行
        await ensure_realtime_service_running()

        # 发送用户通知
        success = await realtime_service.send_user_notification(
            user_id=request.user_id,
            title=request.title,
            content=request.content,
            priority=request.priority
        )

        if success:
            return {
                "message": "用户通知发送成功",
                "user_id": request.user_id,
                "title": request.title,
                "timestamp": "2024-01-01T00:00:00Z"  # 应该使用实际时间
            }
        else:
            raise HTTPException(status_code=400, detail="用户通知发送失败")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"发送用户通知失败: {str(e)}")
        raise HTTPException(status_code=500, detail="发送用户通知失败")

@router.post("/stock/subscription")
async def manage_stock_subscription(request: StockSubscriptionRequest):
    """
    管理股票订阅

    - **stock_code**: 股票代码
    - **action**: 操作类型 (add/remove)
    """
    try:
        # 确保服务正在运行
        await ensure_realtime_service_running()

        if request.action == "add":
            await realtime_service.add_stock_subscription(request.stock_code)
            action_desc = "添加"
        elif request.action == "remove":
            await realtime_service.remove_stock_subscription(request.stock_code)
            action_desc = "移除"
        else:
            raise ValidationError("无效的操作类型")

        return {
            "message": f"股票订阅{action_desc}成功",
            "stock_code": request.stock_code,
            "action": request.action,
            "timestamp": "2024-01-01T00:00:00Z"  # 应该使用实际时间
        }

    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"管理股票订阅失败: {str(e)}")
        raise HTTPException(status_code=500, detail="管理股票订阅失败")

@router.get("/connections")
async def get_active_connections():
    """获取活跃连接统计"""
    try:
        stats = realtime_service.get_service_status()
        connection_stats = stats["components"]["websocket_manager"]

        return {
            "total_connections": connection_stats["total_connections"],
            "connections_by_type": connection_stats["connections_by_type"],
            "total_users": connection_stats["total_users"],
            "subscriptions": connection_stats["subscriptions"]
        }

    except Exception as e:
        logger.error(f"获取连接统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取连接统计失败")

@router.get("/stats")
async def get_service_stats():
    """获取服务详细统计"""
    try:
        stats = realtime_service.get_service_status()
        return stats

    except Exception as e:
        logger.error(f"获取服务统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取服务统计失败")

# 错误处理
@router.exception_handler(ValidationError)
async def validation_error_handler(request, exc: ValidationError):
    """验证错误处理器"""
    logger.error(f"参数验证错误: {str(exc)}")
    raise HTTPException(status_code=400, detail=f"参数错误: {str(exc)}")

@router.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """通用异常处理器"""
    logger.error(f"实时服务API错误: {str(exc)}")
    raise HTTPException(status_code=500, detail="服务器内部错误")