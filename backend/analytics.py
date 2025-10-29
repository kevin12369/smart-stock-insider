"""
用户行为分析API路由
提供用户行为追踪、细分和推荐功能的HTTP接口
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from ..services.ai_service.analytics import behavior_tracker, user_segmentation

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["User Analytics"])

# 请求/响应模型
class TrackActionRequest(BaseModel):
    """行为追踪请求"""
    user_id: str = Field(..., description="用户ID")
    action_type: str = Field(..., description="行为类型")
    page: Optional[str] = Field(None, description="页面")
    session_id: Optional[str] = Field(None, description="会话ID")
    properties: Optional[Dict[str, Any]] = Field(None, description="行为属性")
    device_type: Optional[str] = Field("desktop", description="设备类型")
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")
    duration: Optional[float] = Field(None, description="持续时间")
    value: Optional[float] = Field(None, description="行为价值")

class UserProfileRequest(BaseModel):
    """用户画像请求"""
    user_ids: Optional[List[str]] = Field(None, description="用户ID列表")

class SegmentationRequest(BaseModel):
    """细分请求"""
    user_ids: Optional[List[str]] = Field(None, description="用户ID列表")
    segment_type: str = Field("engagement", description="细分类型")
    n_clusters: int = Field(5, ge=2, le=10, description="聚类数量")

class JourneyRequest(BaseModel):
    """用户旅程请求"""
    user_id: str = Field(..., description="用户ID")
    session_id: Optional[str] = Field(None, description="会话ID")

class FunnelAnalysisRequest(BaseModel):
    """漏斗分析请求"""
    funnel_steps: List[str] = Field(..., description="漏斗步骤")
    days: int = Field(30, ge=1, le=365, description="分析天数")

@router.post("/track/action")
async def track_user_action(request: TrackActionRequest):
    """
    追踪用户行为

    记录用户在平台上的各种行为数据
    """
    try:
        from ..services.ai_service.analytics.behavior_tracker import ActionType, DeviceType

        # 转换行为类型
        try:
            action_type = ActionType(request.action_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的行为类型: {request.action_type}"
            )

        # 转换设备类型
        try:
            device_type = DeviceType(request.device_type)
        except ValueError:
            device_type = DeviceType.DESKTOP

        # 追踪行为
        action_id = await behavior_tracker.track_action(
            user_id=request.user_id,
            action_type=action_type,
            page=request.page,
            session_id=request.session_id,
            properties=request.properties,
            device_type=device_type.value,
            ip_address=request.ip_address,
            user_agent=request.user_agent,
            duration=request.duration,
            value=request.value
        )

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "success": True,
                "action_id": action_id,
                "message": "用户行为已记录"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"追踪用户行为失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="追踪用户行为失败"
        )

@router.get("/actions/{user_id}")
async def get_user_actions(
    user_id: str,
    limit: int = 100,
    action_type: Optional[str] = None,
    days: Optional[int] = None
):
    """
    获取用户行为列表

    返回指定用户的行为记录
    """
    try:
        from ..services.ai_service.analytics.behavior_tracker import ActionType

        # 转换过滤条件
        action_type_enum = None
        if action_type:
            try:
                action_type_enum = ActionType(action_type)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"不支持的行为类型: {action_type}"
                )

        # 设置时间范围
        start_date = None
        if days:
            start_date = datetime.now() - timedelta(days=days)

        # 获取行为数据
        actions = await behavior_tracker.get_user_actions(
            user_id=user_id,
            limit=limit,
            action_type=action_type_enum,
            start_date=start_date
        )

        # 转换响应格式
        action_list = []
        for action in actions:
            action_list.append({
                "action_id": action.action_id,
                "action_type": action.action_type.value,
                "timestamp": action.timestamp.isoformat(),
                "page": action.page,
                "session_id": action.session_id,
                "device_type": action.device_type.value,
                "properties": action.properties,
                "duration": action.duration,
                "value": action.value
            })

        return JSONResponse(
            content={
                "user_id": user_id,
                "actions": action_list,
                "total_count": len(action_list),
                "filters": {
                    "action_type": action_type,
                    "days": days
                }
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户行为失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户行为失败"
        )

@router.get("/summary/{user_id}")
async def get_user_behavior_summary(user_id: str, days: int = 30):
    """
    获取用户行为摘要

    返回用户行为统计分析
    """
    try:
        summary = await behavior_tracker.get_user_behavior_summary(user_id, days)

        return JSONResponse(
            content=summary
        )

    except Exception as e:
        logger.error(f"获取用户行为摘要失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户行为摘要失败"
        )

@router.get("/journey/{user_id}")
async def get_user_journey(request: JourneyRequest):
    """
    获取用户旅程

    返回用户在平台上的完整行为路径
    """
    try:
        journey = await behavior_tracker.get_user_journey(
            user_id=request.user_id,
            session_id=request.session_id
        )

        return JSONResponse(
            content={
                "user_id": request.user_id,
                "session_id": request.session_id,
                "journey": journey,
                "total_steps": len(journey)
            }
        )

    except Exception as e:
        logger.error(f"获取用户旅程失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户旅程失败"
        )

@router.post("/profiles/build")
async def build_user_profiles(request: UserProfileRequest):
    """
    构建用户画像

    基于用户行为数据生成用户画像
    """
    try:
        profiles = await user_segmentation.build_user_profiles(request.user_ids)

        # 转换响应格式
        profile_list = {}
        for user_id, profile in profiles.items():
            profile_list[user_id] = {
                "user_id": profile.user_id,
                "behavior_metrics": profile.behavior_metrics,
                "engagement_metrics": profile.engagement_metrics,
                "value_metrics": profile.value_metrics,
                "preferences": profile.preferences,
                "risk_profile": profile.risk_profile,
                "updated_at": profile.updated_at.isoformat()
            }

        return JSONResponse(
            content={
                "success": True,
                "profiles": profile_list,
                "total_count": len(profiles),
                "message": f"已构建 {len(profiles)} 个用户画像"
            }
        )

    except Exception as e:
        logger.error(f"构建用户画像失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="构建用户画像失败"
        )

@router.get("/profile/{user_id}")
async def get_user_profile(user_id: str):
    """
    获取用户画像

    返回指定用户的详细画像信息
    """
    try:
        if user_id not in user_segmentation.user_profiles:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户画像不存在"
            )

        profile = user_segmentation.user_profiles[user_id]
        user_segments = await user_segmentation.get_user_segments(user_id)

        return JSONResponse(
            content={
                "user_id": profile.user_id,
                "behavior_metrics": profile.behavior_metrics,
                "engagement_metrics": profile.engagement_metrics,
                "value_metrics": profile.value_metrics,
                "preferences": profile.preferences,
                "risk_profile": profile.risk_profile,
                "segments": user_segments,
                "updated_at": profile.updated_at.isoformat()
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户画像失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户画像失败"
        )

@router.post("/segmentation/run")
async def run_user_segmentation(request: SegmentationRequest):
    """
    执行用户细分

    使用指定方法对用户进行分群
    """
    try:
        from ..services.ai_service.analytics.user_segmentation import SegmentType

        # 转换细分类型
        try:
            segment_type = SegmentType(request.segment_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的细分类型: {request.segment_type}"
            )

        # 执行细分
        if segment_type == SegmentType.ENGAGEMENT:
            segment = await user_segmentation.segment_users_by_engagement(request.user_ids)
        elif segment_type == SegmentType.VALUE_BASED:
            segment = await user_segmentation.segment_users_by_value(request.user_ids)
        elif segment_type == SegmentType.BEHAVIORAL:
            segments = await user_segmentation.cluster_based_segmentation(request.user_ids, request.n_clusters)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"暂不支持的细分类型: {request.segment_type}"
            )

        # 处理返回结果
        if segment_type == SegmentType.BEHAVIORAL:
            # 返回多个细分
            segment_list = []
            for seg in segments:
                segment_list.append({
                    "segment_id": seg.segment_id,
                    "name": seg.name,
                    "description": seg.description,
                    "segment_type": seg.segment_type.value,
                    "size": seg.size,
                    "characteristics": seg.characteristics,
                    "created_at": seg.created_at.isoformat()
                })

            return JSONResponse(
                content={
                    "success": True,
                    "segments": segment_list,
                    "total_segments": len(segment_list),
                    "method": request.segment_type
                }
            )
        else:
            # 返回单个细分
            if segment:
                return JSONResponse(
                    content={
                        "success": True,
                        "segment": {
                            "segment_id": segment.segment_id,
                            "name": segment.name,
                            "description": segment.description,
                            "segment_type": segment.segment_type.value,
                            "size": segment.size,
                            "characteristics": segment.characteristics,
                            "created_at": segment.created_at.isoformat()
                        },
                        "method": request.segment_type
                    }
                )
            else:
                return JSONResponse(
                    content={
                        "success": False,
                        "message": "细分失败"
                    }
                )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户细分失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="用户细分失败"
        )

@router.get("/segments")
async def get_all_segments():
    """
    获取所有用户细分

    返回系统中所有的用户细分信息
    """
    try:
        segments = await user_segmentation.get_all_segments()

        segment_list = []
        for segment in segments:
            segment_list.append({
                "segment_id": segment.segment_id,
                "name": segment.name,
                "description": segment.description,
                "segment_type": segment.segment_type.value,
                "size": segment.size,
                "characteristics": segment.characteristics,
                "created_at": segment.created_at.isoformat(),
                "updated_at": segment.updated_at.isoformat()
            })

        return JSONResponse(
            content={
                "segments": segment_list,
                "total_segments": len(segment_list)
            }
        )

    except Exception as e:
        logger.error(f"获取用户细分失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取用户细分失败"
        )

@router.get("/segments/{segment_id}")
async def get_segment_details(segment_id: str):
    """
    获取细分详情

    返回指定细分的详细信息和用户列表
    """
    try:
        segment = await user_segmentation.get_segment_details(segment_id)

        if not segment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="细分不存在"
            )

        return JSONResponse(
            content={
                "segment_id": segment.segment_id,
                "name": segment.name,
                "description": segment.description,
                "segment_type": segment.segment_type.value,
                "users": segment.users,
                "size": segment.size,
                "characteristics": segment.characteristics,
                "metadata": segment.metadata,
                "created_at": segment.created_at.isoformat(),
                "updated_at": segment.updated_at.isoformat()
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取细分详情失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取细分详情失败"
        )

@router.post("/funnel/analyze")
async def analyze_funnel(request: FunnelAnalysisRequest):
    """
    漏斗分析

    分析用户在特定转化路径上的行为表现
    """
    try:
        from ..services.ai_service.analytics.behavior_tracker import ActionType

        # 转换漏斗步骤
        try:
            funnel_steps = [ActionType(step) for step in request.funnel_steps]
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的漏斗步骤: {str(e)}"
            )

        # 执行漏斗分析
        funnel_analysis = await behavior_tracker.get_funnel_analysis(funnel_steps, request.days)

        return JSONResponse(
            content=funnel_analysis
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"漏斗分析失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="漏斗分析失败"
        )

@router.get("/stats/realtime")
async def get_realtime_stats():
    """
    获取实时统计

    返回平台的实时用户行为统计
    """
    try:
        stats = await behavior_tracker.get_real_time_stats()

        return JSONResponse(
            content=stats
        )

    except Exception as e:
        logger.error(f"获取实时统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取实时统计失败"
        )

@router.get("/stats/system")
async def get_system_statistics():
    """
    获取系统统计

    返回用户行为分析系统的整体统计信息
    """
    try:
        behavior_stats = behavior_tracker.get_system_statistics()
        segmentation_stats = user_segmentation.get_segmentation_statistics()

        return JSONResponse(
            content={
                "behavior_tracker": behavior_stats,
                "user_segmentation": segmentation_stats,
                "generated_at": datetime.now().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"获取系统统计失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取系统统计失败"
        )

@router.get("/health")
async def health_check():
    """
    健康检查

    检查用户行为分析服务的运行状态
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "behavior_tracker": "healthy",
                "user_segmentation": "healthy"
            },
            "statistics": {
                "total_actions": len(behavior_tracker.actions),
                "total_sessions": len(behavior_tracker.user_sessions),
                "total_users": len(behavior_tracker.user_actions),
                "active_sessions": len(behavior_tracker.active_sessions),
                "total_segments": len(user_segmentation.segments)
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