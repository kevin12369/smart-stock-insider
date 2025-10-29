"""
用户分析API单元测试
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 创建FastAPI应用
from fastapi import FastAPI
from backend.api.analytics import router as analytics_router

app = FastAPI()
app.include_router(analytics_router)

client = TestClient(app)

@pytest.fixture
def mock_behavior_tracker():
    """模拟行为追踪器"""
    with patch('backend.api.analytics.behavior_tracker') as mock_tracker:
        # 模拟追踪行为
        mock_tracker.track_action = AsyncMock(return_value="action_001")

        # 模拟获取用户行为
        mock_tracker.get_user_actions = AsyncMock(return_value=[
            Mock(
                action_id="action_001",
                user_id="user_001",
                action_type=Mock(value="page_view"),
                timestamp=datetime.now(),
                page="/dashboard",
                duration=45.5,
                properties={"device": "desktop"}
            ),
            Mock(
                action_id="action_002",
                user_id="user_001",
                action_type=Mock(value="stock_search"),
                timestamp=datetime.now(),
                page="/search",
                properties={"query": "腾讯", "symbol": "0700.HK"}
            )
        ])

        # 模拟获取用户行为摘要
        mock_tracker.get_user_behavior_summary = AsyncMock(return_value={
            "total_actions": 25,
            "recent_actions": 5,
            "total_sessions": 3,
            "avg_session_duration": 120.5,
            "satisfaction_score": 0.85,
            "most_active_hour": 14,
            "favorite_category": "股票查询",
            "interaction_style": "formal",
            "action_type_distribution": {
                "page_view": 15,
                "stock_search": 5,
                "chat_message": 3,
                "portfolio_create": 2
            }
        })

        # 模拟获取用户旅程
        mock_tracker.get_user_journey = AsyncMock(return_value=[
            {
                "action_id": "action_001",
                "action_type": "page_view",
                "page": "/dashboard",
                "timestamp": "2023-10-29T10:00:00Z",
                "duration": 30.0
            },
            {
                "action_id": "action_002",
                "action_type": "stock_search",
                "page": "/search",
                "timestamp": "2023-10-29T10:02:00Z",
                "properties": {"query": "腾讯"}
            }
        ])

        # 模拟构建用户画像
        mock_user_segmentation = Mock()
        mock_user_segmentation.build_user_profiles = AsyncMock(return_value={
            "user_001": {
                "user_id": "user_001",
                "behavior_metrics": {
                    "avg_session_duration": 120.5,
                    "action_frequency": 0.15,
                    "conversion_rate": 0.08
                },
                "engagement_metrics": {
                    "session_count": 5,
                    "avg_actions_per_session": 4.2,
                    "bounce_rate": 0.2
                },
                "value_metrics": {
                    "lifetime_value": 1000.0,
                    "conversion_value": 500.0
                },
                "preferences": {
                    "preferred_categories": ["股票查询", "市场分析"],
                    "risk_tolerance": "moderate",
                    "investment_experience": "intermediate"
                },
                "risk_profile": {
                    "risk_appetite": 0.6,
                    "diversification_score": 0.7,
                    "loss_aversion": 0.5
                }
            }
        })

        # 模拟用户细分
        mock_user_segmentation.segment_users_by_engagement = AsyncMock(return_value=Mock(
            segment_id="segment_001",
            name="高活跃用户",
            description="经常使用平台的活跃用户",
            segment_type=Mock(value="engagement"),
            size=50,
            characteristics=["高频访问", "高转化率", "长会话时长"],
            created_at=datetime.now()
        ))

        # 模拟获取所有细分
        mock_user_segmentation.get_all_segments = AsyncMock(return_value=[
            Mock(
                segment_id="segment_001",
                name="高活跃用户",
                segment_type=Mock(value="engagement"),
                size=50,
                characteristics=["高频访问"]
            ),
            Mock(
                segment_id="segment_002",
                name="价值用户",
                segment_type=Mock(value="value_based"),
                size=30,
                characteristics=["高转化", "高价值"]
            )
        ])

        # 模拟漏斗分析
        mock_tracker.get_funnel_analysis = AsyncMock(return_value={
            "steps": [
                {
                    "action_type": "page_view",
                    "count": 1000,
                    "conversion_rate": 1.0,
                    "dropoff_rate": 0.0
                },
                {
                    "action_type": "stock_search",
                    "count": 300,
                    "conversion_rate": 0.3,
                    "dropoff_rate": 0.7
                },
                {
                    "action_type": "portfolio_create",
                    "count": 90,
                    "conversion_rate": 0.09,
                    "dropoff_rate": 0.7
                }
            ],
            "overall_conversion_rate": 0.09,
            "funnel_efficiency": 0.09
        })

        # 模拟获取实时统计
        mock_tracker.get_real_time_stats = AsyncMock(return_value={
            "active_users": 25,
            "actions_per_minute": 5.2,
            "sessions_per_hour": 3.8,
            "avg_session_duration": 125.5,
            "top_actions": [
                {"action_type": "page_view", "count": 45},
                {"action_type": "stock_search", "count": 12},
                {"action_type": "chat_message", "count": 8}
            ],
            "recent_growth": {
                "users_24h": 5,
                "actions_24h": 125,
                "sessions_24h": 38
            }
        })

        # 模拟获取系统统计
        mock_tracker.get_system_statistics = Mock(return_value={
            "total_actions": 50000,
            "total_sessions": 8000,
            "total_users": 2000,
            "avg_actions_per_user": 25,
            "avg_session_duration": 135.5,
            "action_type_distribution": {
                "page_view": 25000,
                "stock_search": 8000,
                "chat_message": 6000,
                "portfolio_create": 1500,
                "risk_analysis": 3000
            },
            "device_type_distribution": {
                "desktop": 30000,
                "mobile": 18000,
                "tablet": 2000
            },
            "user_activity_trend": "increasing"
        })

        yield mock_tracker

@pytest.fixture
def sample_track_action_request():
    """示例追踪行为请求"""
    return {
        "user_id": "user_001",
        "action_type": "page_view",
        "page": "/dashboard",
        "session_id": "session_001",
        "properties": {
            "device": "desktop",
            "referrer": "/login",
            "utm_source": "google"
        },
        "duration": 45.5,
        "value": 1000.0
    }

@pytest.fixture
def sample_profile_request():
    """示例用户画像请求"""
    return {
        "user_ids": ["user_001", "user_002"]
    }

@pytest.fixture
def sample_segmentation_request():
    """示例用户细分请求"""
    return {
        "user_ids": ["user_001", "user_002", "user_003"],
        "segment_type": "engagement",
        "n_clusters": 3
    }

@pytest.fixture
def sample_funnel_request():
    """示例漏斗分析请求"""
    return {
        "funnel_steps": ["page_view", "stock_search", "portfolio_create"],
        "days": 30
    }

class TestAnalyticsAPI:
    """用户分析API测试类"""

    def test_track_action_success(self, mock_behavior_tracker, sample_track_action_request):
        """测试成功追踪用户行为"""
        response = client.post("/api/analytics/track/action", json=sample_track_action_request)

        assert response.status_code == 201
        data = response.json()

        assert "success" in data
        assert "action_id" in data
        assert "message" in data

        assert data["success"] is True
        assert data["action_id"] == "action_001"
        assert data["message"] == "用户行为已记录"

        # 验证服务调用
        mock_behavior_tracker.track_action.assert_called_once()

    def test_track_action_invalid_request(self):
        """测试无效的追踪请求"""
        invalid_requests = [
            {},  # 空请求
            {"action_type": "page_view"},  # 缺少user_id
            {"user_id": "", "action_type": "page_view"},  # 空user_id
            {"user_id": "user_001", "action_type": "invalid_action"},  # 无效行为类型
            {"user_id": "user_001", "action_type": "page_view", "page": ""},  # 空页面
            {"user_id": "x" * 300, "action_type": "page_view"}  # 用户ID过长
        ]

        for invalid_request in invalid_requests:
            response = client.post("/api/analytics/track/action", json=invalid_request)
            assert response.status_code == 422

    def test_track_action_with_all_fields(self, mock_behavior_tracker):
        """测试包含所有字段的追踪请求"""
        full_request = {
            "user_id": "user_001",
            "action_type": "portfolio_create",
            "page": "/portfolio",
            "session_id": "session_001",
            "properties": {
                "device": "desktop",
                "referrer": "/dashboard",
                "utm_source": "google",
                "campaign": "spring_promo"
            },
            "duration": 120.5,
            "value": 50000.0,
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0..."
        }

        response = client.post("/api/analytics/track/action", json=full_request)

        assert response.status_code == 201

    def test_get_user_actions_success(self, mock_behavior_tracker):
        """测试成功获取用户行为"""
        user_id = "user_001"

        response = client.get(f"/api/analytics/actions/{user_id}")

        assert response.status_code == 200
        data = response.json()

        assert "user_id" in data
        assert "actions" in data
        assert "total_count" in data
        assert "filters" in data

        assert data["user_id"] == user_id
        assert len(data["actions"]) == 2
        assert data["total_count"] == 2

        # 验证服务调用
        mock_behavior_tracker.get_user_actions.assert_called_once_with(user_id)

    def test_get_user_actions_with_filters(self, mock_behavior_tracker):
        """测试带过滤条件的用户行为获取"""
        user_id = "user_001"
        action_type = "stock_search"
        days = 7

        response = client.get(f"/api/analytics/actions/{user_id}?action_type={action_type}&days={days}")

        assert response.status_code == 200
        data = response.json()

        assert len(data["actions"]) == 1  # 只有stock_search类型的行为
        assert data["filters"]["action_type"] == action_type
        assert data["filters"]["days"] == days

    def test_get_user_actions_not_found(self, mock_behavior_tracker):
        """测试获取不存在用户的行为"""
        mock_behavior_tracker.get_user_actions.return_value = []

        user_id = "non_existent_user"

        response = client.get(f"/api/analytics/actions/{user_id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data["actions"]) == 0
        assert data["total_count"] == 0

    def test_get_user_behavior_summary_success(self, mock_behavior_tracker):
        """测试成功获取用户行为摘要"""
        user_id = "user_001"

        response = client.get(f"/api/analytics/summary/{user_id}")

        assert response.status_code == 200
        data = response.json()

        assert "total_actions" in data
        assert "recent_actions" in data
        assert "total_sessions" in data
        assert "avg_session_duration" in data
        assert "satisfaction_score" in data
        assert "most_active_hour" in data
        assert "favorite_category" in data
        assert "interaction_style" in data

        assert data["total_actions"] == 25
        assert data["satisfaction_score"] == 0.85

        # 验证服务调用
        mock_behavior_tracker.get_user_behavior_summary.assert_called_once_with(user_id)

    def test_get_user_journey_success(self, mock_behavior_tracker):
        """测试成功获取用户旅程"""
        user_id = "user_001"
        session_id = "session_001"

        response = client.get(f"/api/analytics/journey/{user_id}?session_id={session_id}")

        assert response.status_code == 200
        data = response.json()

        assert "user_id" in data
        assert "session_id" in data
        assert "journey" in data
        assert "total_steps" in data

        assert data["user_id"] == user_id
        assert data["session_id"] == session_id
        assert len(data["journey"]) == 2

        # 验证服务调用
        mock_behavior_tracker.get_user_journey.assert_called_once_with(
            user_id=user_id,
            session_id=session_id
        )

    def test_build_user_profiles_success(self, mock_behavior_tracker, sample_profile_request):
        """测试成功构建用户画像"""
        response = client.post("/api/analytics/profiles/build", json=sample_profile_request)

        assert response.status_code == 200
        data = response.json()

        assert "success" in data
        assert "profiles" in data
        assert "total_count" in data
        assert "message" in data

        assert data["success"] is True
        assert len(data["profiles"]) == 2
        assert "user_001" in data["profiles"]
        assert "user_002" in data["profiles"]

        # 验证画像内容
        profile_001 = data["profiles"]["user_001"]
        assert "behavior_metrics" in profile_001
        assert "engagement_metrics" in profile_001
        assert "preferences" in profile_001
        assert "risk_profile" in profile_001

    def test_build_user_profiles_empty_list(self, mock_behavior_tracker):
        """测试空用户列表构建画像"""
        empty_request = {"user_ids": []}

        response = client.post("/api/analytics/profiles/build", json=empty_request)

        assert response.status_code == 200
        data = response.json()

        assert data["success"] is True
        assert len(data["profiles"]) == 0
        assert data["total_count"] == 0

    def test_get_user_profile_success(self, mock_behavior_tracker):
        """测试成功获取用户画像"""
        user_id = "user_001"

        # 设置模拟画像数据
        mock_user_segmentation.user_profiles = {
            "user_001": {
                "user_id": user_id,
                "behavior_metrics": {"avg_session_duration": 120.5},
                "engagement_metrics": {"session_count": 5},
                "preferences": {"preferred_categories": ["股票查询"]},
                "risk_profile": {"risk_appetite": 0.6}
            }
        }

        mock_user_segmentation.get_user_segments = AsyncMock(return_value=[
            {"segment_id": "segment_001", "name": "活跃用户", "size": 100}
        ])

        response = client.get(f"/api/analytics/profile/{user_id}")

        assert response.status_code == 200
        data = response.json()

        assert "user_id" in data
        assert "behavior_metrics" in data
        assert "engagement_metrics" in data
        assert "preferences" in data
        assert "risk_profile" in data
        assert "segments" in data

        assert data["user_id"] == user_id

    def test_get_user_profile_not_found(self, mock_behavior_tracker):
        """测试获取不存在的用户画像"""
        mock_user_segmentation.user_profiles = {}

        user_id = "non_existent_user"

        response = client.get(f"/api/analytics/profile/{user_id}")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "用户画像不存在" in data["detail"]

    def test_run_user_segmentation_success(self, mock_behavior_tracker, sample_segmentation_request):
        """测试成功执行用户细分"""
        response = client.post("/api/analytics/segmentation/run", json=sample_segmentation)

        assert response.status_code == 200
        data = response.json()

        assert "success" in data
        assert "segments" in data
        assert "total_segments" in data
        assert "method" in data

        assert data["success"] is True
        assert data["method"] == "engagement"
        assert len(data["segments"]) == 1
        assert data["segments"][0]["segment_id"] == "segment_001"

    def test_run_user_segmentation_by_value(self, mock_behavior_tracker):
        """测试按价值细分用户"""
        request = {
            "user_ids": ["user_001", "user_002"],
            "segment_type": "value_based"
        }

        mock_value_segment = Mock(
            segment_id="segment_value_001",
            name="高价值用户",
            description="贡献高价值的用户",
            segment_type=Mock(value="value_based"),
            size=15,
            characteristics=["高转化", "高生命周期价值"]
        )

        mock_user_segmentation.segment_users_by_value = AsyncMock(return_value=mock_value_segment)

        response = client.post("/api/analytics/segmentation/run", json=request)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["method"] == "value_based"

    def test_run_user_segmentation_invalid_type(self, mock_behavior_tracker):
        """测试无效细分类型"""
        request = {
            "user_ids": ["user_001", "user_002"],
            "segment_type": "invalid_type"
        }

        response = client.post("/api/analytics/segmentation/run", json=request)

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert "不支持的细分类型" in data["detail"]

    def test_get_all_segments_success(self, mock_behavior_tracker):
        """测试成功获取所有用户细分"""
        response = client.get("/api/analytics/segments")

        assert response.status_code == 200
        data = response.json()

        assert "segments" in data
        assert "total_segments" in data

        assert len(data["segments"]) == 2
        assert all("segment_id" in segment for segment in data["segments"])
        assert all("name" in segment for segment in data["segments"])

    def test_get_segment_details_success(self, mock_behavior_tracker):
        """测试成功获取细分详情"""
        mock_user_segmentation.get_segment_details = AsyncMock(return_value=Mock(
            segment_id="segment_001",
            name="高活跃用户",
            description="经常使用平台的活跃用户",
            segment_type=Mock(value="engagement"),
            size=50,
            users=["user_001", "user_002", "user_003"],
            characteristics=["高频访问", "高转化率"],
            metadata={"created_by": "system", "updated_at": "2023-10-29T10:00:00Z"},
            created_at=datetime.now(),
            updated_at=datetime.now()
        ))

        segment_id = "segment_001"

        response = client.get(f"/api/analytics/segments/{segment_id}")

        assert response.status_code == 200
        data = response.json()

        assert "segment_id" in data
        assert "name" in data
        assert "description" in data
        assert "segment_type" in data
        assert "users" in data
        assert "size" in data
        assert "characteristics" in data
        assert "metadata" in data

        assert data["segment_id"] == segment_id
        assert data["size"] == 50
        assert len(data["users"]) == 3

    def test_get_segment_details_not_found(self, mock_behavior_tracker):
        """测试获取不存在的细分详情"""
        mock_user_segmentation.get_segment_details = AsyncMock(return_value=None)

        segment_id = "non_existent_segment"

        response = client.get(f"/api/analytics/segments/{segment_id}")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "细分不存在" in data["detail"]

    def test_analyze_funnel_success(self, mock_behavior_tracker, sample_funnel_request):
        """测试成功分析漏斗"""
        response = client.post("/api/analytics/funnel/analyze", json=sample_funnel_request)

        assert response.status_code == 200
        data = response.json()

        assert "steps" in data
        assert "overall_conversion_rate" in data
        assert "funnel_efficiency" in data

        assert len(data["steps"]) == 3
        assert data["overall_conversion_rate"] == 0.09

        # 验证漏斗步骤
        for step in data["steps"]:
            assert "action_type" in step
            assert "count" in step
            assert "conversion_rate" in step

        # 验证服务调用
        mock_behavior_tracker.get_funnel_analysis.assert_called_once()

    def test_analyze_funnel_invalid_request(self):
        """测试无效的漏斗分析请求"""
        invalid_requests = [
            {},  # 空请求
            {"funnel_steps": []},  # 空漏斗步骤
            {"funnel_steps": ["invalid_type"]},  # 无效行为类型
            {"funnel_steps": ["page_view"], "days": 400}  # 天数过多
        ]

        for invalid_request in invalid_requests:
            response = client.post("/api/analytics/funnel/analyze", json=invalid_request)
            assert response.status_code == 422

    def test_get_realtime_stats_success(self, mock_behavior_tracker):
        """测试成功获取实时统计"""
        response = client.get("/api/analytics/stats/realtime")

        assert response.status_code == 200
        data = response.json()

        assert "active_users" in data
        assert "actions_per_minute" in data
        assert "sessions_per_hour" in data
        assert "avg_session_duration" in data
        assert "top_actions" in data
        assert "recent_growth" in data

        assert data["active_users"] == 25
        assert data["actions_per_minute"] == 5.2

        # 验证服务调用
        mock_behavior_tracker.get_real_time_stats.assert_called_once()

    def test_get_system_statistics_success(self, mock_behavior_tracker):
        """测试成功获取系统统计"""
        response = client.get("/api/analytics/stats/system")

        assert response.status_code == 200
        data = response.json()

        assert "behavior_tracker" in data
        assert "user_segmentation" in data
        assert "generated_at" in data

        assert "behavior_tracker" in data
        assert data["behavior_tracker"]["total_actions"] == 50000
        assert data["behavior_tracker"]["total_users"] == 2000

    def test_health_check_success(self, mock_behavior_tracker):
        """测试健康检查成功"""
        response = client.get("/api/analytics/health")

        assert response.status_code == 200
        data = response.json()

        assert "status" in data
        assert "timestamp" in data
        assert "components" in data

        assert data["status"] == "healthy"
        assert "behavior_tracker" in data["components"]
        assert "user_profiler" in data["components"]

    def test_health_check_service_error(self, mock_behavior_tracker):
        """测试健康检查服务错误"""
        mock_behavior_tracker.get_system_statistics.side_effect = Exception("Service error")

        response = client.get("/api/analytics/health")

        assert response.status_code == 503
        data = response.json()

        assert data["status"] == "unhealthy"
        assert "timestamp" in data
        assert "error" in data

    def test_error_handling_500(self):
        """测试500错误处理"""
        with patch('backend.api.analytics.behavior_tracker') as mock_tracker:
            mock_tracker.track_action.side_effect = Exception("Internal error")

            response = client.post("/api/analytics/track/action", json={
                "user_id": "test_user",
                "action_type": "page_view"
            })

            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
            assert "追踪用户行为失败" in data["detail"]

    def test_concurrent_tracking(self, mock_behavior_tracker):
        """测试并发追踪"""
        import threading
        import time

        results = []
        errors = []

        def track_action(index):
            try:
                response = client.post("/api/analytics/track/action", json={
                    "user_id": f"user_{index}",
                    "action_type": "page_view",
                    "page": f"/page_{index}"
                })
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        # 创建多个并发线程
        threads = []
        for i in range(10):
            thread = threading.Thread(target=track_action, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证结果
        assert len(errors) == 0, f"并发追踪出现错误: {errors}"
        assert len(results) == 10
        assert all(status in [201, 422, 500] for status in results)

    def test_large_user_actions_handling(self, mock_behavior_tracker):
        """测试大量用户行为处理"""
        # 模拟大量用户行为
        mock_actions = [
            Mock(
                action_id=f"action_{i:05d}",
                user_id=f"user_{i % 100}",  # 100个不同用户
                action_type=Mock(value="page_view"),
                timestamp=datetime.now() - timedelta(minutes=i),
                page=f"/page_{i}"
            )
            for i in range(1000)
        ]

        mock_behavior_tracker.get_user_actions = AsyncMock(
            return_value=mock_actions[:50]  # 返回前50个
        )

        response = client.get("/api/analytics/actions/user_001")

        assert response.status_code == 200
        data = response.json()

        # 应该返回限制数量的行为
        assert len(data["actions"]) <= 50

    def test_user_id_validation(self):
        """测试用户ID验证"""
        invalid_user_ids = [
            "",  # 空字符串
            "x" * 300,  # 过长用户ID
            "user@domain.com",  # 包含特殊字符
            "用户001"  # 中文字符（如果系统不允许）
        ]

        for invalid_user_id in invalid_user_ids:
            response = client.get(f"/api/analytics/actions/{invalid_user_id}")
            assert response.status_code == 422

    def test_session_id_validation(self, mock_behavior_tracker):
        """测试会话ID验证"""
        invalid_session_ids = [
            "",  # 空字符串
            "x" * 100,  # 过长会话ID
            "session@invalid"  # 包含特殊字符
        ]

        for invalid_session_id in invalid_session_ids:
            response = client.get(f"/api/analytics/journey/user_001?session_id={invalid_session_id}")
            assert response.status_code == 422

    def test_action_type_validation(self, mock_behavior_tracker):
        """测试行为类型验证"""
        invalid_action_types = [
            "",  # 空字符串
            "invalid_action",  # 无效行为类型
            "ACTION_TYPE_INVALID"  # 错误格式
        ]

        for invalid_action_type in invalid_action_types:
            response = client.post("/api/analytics/track/action", json={
                "user_id": "test_user",
                "action_type": invalid_action_type
            })
            assert response.status_code == 422

    def test_datetime_validation(self):
        """测试日期时间验证"""
        invalid_timestamps = [
            "2023-13-32T25:60:60",  # 无效日期
            "2023-02-30T25:60:60",  # 无效日期（2月没有30天）
            "2023-02-28T25:60:60"  # 无效时间
        ]

        for invalid_timestamp in invalid_timestamps:
            request = {
                "user_id": "test_user",
                "action_type": "page_view",
                "timestamp": invalid_timestamp
            }

            response = client.post("/api/analytics/track/action", json=request)
            assert response.status_code == 422

@pytest.mark.unit
@pytest.mark.api
@pytest.mark.analytics
class TestAnalyticsAPIIntegration:
    """用户分析API集成测试"""

    def test_complete_user_analytics_workflow(self, mock_behavior_tracker, mock_user_segmentation):
        """测试完整的用户分析工作流程"""
        user_id = "workflow_test_user"

        # 1. 追踪一系列用户行为
        actions = [
            {
                "user_id": user_id,
                "action_type": "page_view",
                "page": "/dashboard",
                "duration": 30.0
            },
            {
                "user_id": user_id,
                "action_type": "stock_search",
                "page": "/search",
                "properties": {"query": "腾讯", "symbol": "0700.HK"}
            },
            {
                "user_id": user_id,
                "action_type": "chat_message",
                "page": "/chat",
                "properties": {"message_length": 25}
            },
            {
                "user_id": user_id,
                "action_type": "portfolio_create",
                "page": "/portfolio",
                "value": 10000.0
            }
        ]

        for action in actions:
            response = client.post("/api/analytics/track/action", json=action)
            assert response.status_code == 201

        # 2. 获取用户行为摘要
        summary_response = client.get(f"/api/analytics/summary/{user_id}")
        assert summary_response.status_code == 200

        # 3. 获取用户旅程
        journey_response = client.get(f"/api/analytics/journey/{user_id}")
        assert journey_response.status_code == 200

        # 4. 构建用户画像
        profile_response = client.post("/api/analytics/profiles/build", json={
            "user_ids": [user_id]
        })
        assert profile_response.status_code == 200

        # 5. 获取实时统计
        stats_response = client.get("/api/analytics/stats/realtime")
        assert stats_response.status_code == 200

        # 6. 健康检查
        health_response = client.get("/api/analytics/health")
        assert health_response.status_code == 200

    def test_user_lifecycle_tracking(self, mock_behavior_tracker):
        """测试用户生命周期追踪"""
        user_id = "lifecycle_user_001"

        # 1. 用户注册
        register_response = client.post("/api/analytics/track/action", json={
            "user_id": user_id,
            "action_type": "signup",
            "page": "/signup",
            "properties": {"method": "email"}
        })
        assert register_response.status_code == 201

        # 2. 用户登录
        login_response = client.post("/api/analytics/track/action", json={
            "user_id": user_id,
            "action_type": "login",
            "page": "/login",
            "properties": {"method": "email"}
        })
        assert login_response.status_code == 201

        # 3. 开始活跃使用
        active_actions = [
            {"action_type": "page_view", "page": "/dashboard", "duration": 45},
            {"action_type": "stock_search", "page": "/search"},
            {"action_type": "chat_message", "page": "/chat"},
            {"action_type": "portfolio_create", "page": "/portfolio", "value": 5000.0}
        ]

        for action in active_actions:
            response = client.post("/api/analytics/track/action", json={
                "user_id": user_id,
                **action
            })
            assert response.status_code == 201

        # 4. 获取用户发展统计
        summary_response = client.get(f"/api/analytics/summary/{user_id}")
        assert summary_response.status_code == 200

        # 验证用户行为发展
        summary_data = summary_response.json()
        assert summary_data["total_actions"] >= len(active_actions) + 2  # +2 for signup/login

    def test_segmentation_driven_personalization(self, mock_behavior_tracker, mock_user_segmentation):
        """测试基于细分的个性化"""
        # 创建不同类型的用户
        user_profiles = {
            "power_user": {
                "user_id": "power_user_001",
                "actions": [
                    {"action_type": "portfolio_create", "value": 50000},
                    {"action_type": "risk_analysis"},
                    {"action_type": "advanced_search"}
                ]
            },
            "casual_user": {
                "user_id": "casual_user_001",
                "actions": [
                    {"action_type": "page_view", "duration": 10.0},
                    {"action_type": "stock_search"}
                ]
            },
            "new_user": {
                "user_id": "new_user_001",
                "actions": [
                    {"action_type": "onboarding_view", "duration": 60.0}
                ]
            }
        }

        # 为每个用户追踪行为
        for user_type, user_data in user_profiles.items():
            user_id = user_data["user_id"]
            for action in user_data["actions"]:
                request = {
                    "user_id": user_id,
                    "action_type": action["action_type"]
                }
                if "page" in action:
                    request["page"] = f"/{action['action_type'].replace('_', '-')}"
                if "duration" in action:
                    request["duration"] = action["duration"]
                if "value" in action:
                    request["value"] = action["value"]

                response = client.post("/api/analytics/track/action", json=request)
                assert response.status_code == 201

        # 执行用户细分
        segmentation_response = client.post("/api/analytics/segmentation/run", json={
            "user_ids": list(user_profiles.keys()),
            "segment_type": "behavioral"
        })

        assert segmentation_response.status_code == 200

        # 验证细分结果
        segmentation_data = segmentation_response.json()
        assert len(segmentation_data["segments"]) >= 1

        # 为不同类型的用户提供个性化建议
        for user_type, user_data in user_profiles.items():
            user_id = user_data["user_id"]

            # 获取用户建议
            suggestions_response = client.get(f"/api/analytics/user/{user_id}/suggestions")
            assert suggestions_response.status_code == 200

            # 验证建议内容符合用户类型
            suggestions_data = suggestions_response.json()
            assert "suggestions" in suggestions_data

    def test_real_time_dashboard_updates(self, mock_behavior_tracker):
        """测试实时仪表板更新"""
        # 模拟实时活动
        real_time_activities = [
            {
                "user_id": "realtime_user_001",
                "action_type": "page_view",
                "page": "/dashboard"
            },
            {
                "user_id": "realtime_user_002",
                "action_type": "stock_search",
                "page": "/search"
            },
            {
                "user_id": "realtime_user_003",
                "action_type": "chat_message",
                "page": "/chat"
            }
        ]

        # 快速连续追踪
        responses = []
        for activity in real_time_activities:
            response = client.post("/api/analytics/track/action", json=activity)
            responses.append(response.status_code)

        assert all(status == 201 for status in responses)

        # 获取实时统计
        stats_response = client.get("/api/analytics/stats/realtime")
        assert stats_response.status_code == 200

        # 验证实时数据
        stats_data = stats_response.json()
        assert "active_users" in stats_data
        assert "actions_per_minute" in stats_data
        assert stats_data["active_users"] >= 3

        # 模拟时间推进后的状态变化
        mock_behavior_tracker.get_real_time_stats = AsyncMock(return_value={
            "active_users": 8,
            "actions_per_minute": 2.1,
            "top_actions": [
                {"action_type": "page_view", "count": 15},
                {"action_type": "chat_message", "count": 8}
            ],
            "recent_growth": {
                "users_24h": -5,
                "actions_24h": -25
            }
        })

        updated_stats_response = client.get("/api/analytics/stats/realtime")
        assert updated_stats_response.status_code == 200

        # 验证数据更新
        updated_stats_data = updated_stats_response.json()
        assert updated_stats_data["active_users"] == 8
        assert updated_stats_data["actions_per_minute"] == 2.1
        assert updated_stats_data["recent_growth"]["users_24h"] == -5

    def test_cross_device_user_analysis(self, mock_behavior_tracker):
        """测试跨设备用户分析"""
        user_id = "cross_device_user_001"

        # 模拟跨设备使用场景
        device_scenarios = [
            {
                "device_type": "desktop",
                "actions": [
                    {"action_type": "portfolio_create", "page": "/portfolio", "value": 10000.0},
                    {"action_type": "risk_analysis", "page": "/risk"}
                ]
            },
            {
                "device_type": "mobile",
                "actions": [
                    {"action_type": "page_view", "page": "/mobile/dashboard"},
                    {"action_type": "chat_message", "page": "/mobile/chat"}
                ]
            },
            {
                "device_type": "tablet",
                "actions": [
                    {"action_type": "stock_view", "page": "/tablet/stock"}
                ]
            }
        ]

        # 在不同设备上追踪行为
        for scenario in device_scenarios:
            for action in scenario["actions"]:
                request = {
                    "user_id": user_id,
                    "action_type": action["action_type"],
                    "page": action.get("page"),
                    "device_type": scenario["device_type"]
                }
                if "value" in action:
                    request["value"] = action["value"]

                response = client.post("/api/analytics/track/action", json=request)
                assert response.status_code == 201

        # 获取跨设备用户分析
        journey_response = client.get(f"/api/analytics/journey/{user_id}")
        assert journey_response.status_code == 200

        # 验证跨设备旅程
        journey_data = journey_response.json()
        journey = journey_data["journey"]
        device_types = [step.get("device_type", "unknown") for step in journey]

        assert len(set(device_types)) >= 2  # 至少使用了2种设备

        # 获取用户统计
        stats_response = client.get(f"/api/analytics/stats/realtime")
        assert stats_response.status_code == 200

        # 验证设备分布统计
        stats_data = stats_response.json()
        assert "device_type_distribution" in stats_data