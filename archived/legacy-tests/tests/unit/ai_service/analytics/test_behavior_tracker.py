"""
用户行为追踪器单元测试
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.services.ai_service.analytics.behavior_tracker import (
    BehaviorTracker, ActionType, DeviceType, UserAction, UserSession
)

@pytest.fixture
def behavior_tracker():
    """行为追踪器夹具"""
    config = {
        "session_timeout": 1800,  # 30分钟
        "max_actions_per_user": 1000,
        "max_sessions_per_user": 100
    }
    return BehaviorTracker(config)

@pytest.fixture
def sample_user_action():
    """示例用户行为"""
    return UserAction(
        action_id="action_001",
        user_id="user_001",
        action_type=ActionType.PAGE_VIEW,
        timestamp=datetime.now(),
        session_id="session_001",
        page="/dashboard",
        duration=45.5,
        properties={"device": "desktop", "referrer": "/login"}
    )

@pytest.fixture
def sample_user_actions():
    """示例用户行为列表"""
    base_time = datetime.now()
    return [
        UserAction(
            action_id="action_001",
            user_id="user_001",
            action_type=ActionType.PAGE_VIEW,
            timestamp=base_time,
            session_id="session_001",
            page="/dashboard",
            duration=45.5
        ),
        UserAction(
            action_id="action_002",
            user_id="user_001",
            action_type=ActionType.STOCK_SEARCH,
            timestamp=base_time + timedelta(minutes=2),
            session_id="session_001",
            page="/search",
            properties={"query": "腾讯", "symbol": "0700.HK"}
        ),
        UserAction(
            action_id="action_003",
            user_id="user_002",
            action_type=ActionType.CHAT_MESSAGE,
            timestamp=base_time + timedelta(minutes=5),
            session_id="session_002",
            page="/chat",
            properties={"intent": "knowledge_query", "message_length": 25}
        ),
        UserAction(
            action_id="action_004",
            user_id="user_001",
            action_type=ActionType.PORTFOLIO_CREATE,
            timestamp=base_time + timedelta(minutes=10),
            session_id="session_001",
            page="/portfolio",
            value=10000.0
        )
    ]

class TestBehaviorTracker:
    """行为追踪器测试类"""

    def test_initialization(self, behavior_tracker):
        """测试初始化"""
        assert behavior_tracker.session_timeout == 1800
        assert behavior_tracker.max_actions_per_user == 1000
        assert behavior_tracker.max_sessions_per_user == 100
        assert len(behavior_tracker.conversion_events) > 0
        assert ActionType.PORTFOLIO_CREATE in behavior_tracker.conversion_events

    def test_generate_action_id(self, behavior_tracker):
        """测试生成行为ID"""
        action_id1 = behavior_tracker._generate_action_id()
        action_id2 = behavior_tracker._generate_action_id()

        assert isinstance(action_id1, str)
        assert isinstance(action_id2, str)
        assert action_id1 != action_id2
        assert len(action_id1) > 0

    async def test_track_action(self, behavior_tracker, sample_user_action):
        """测试追踪用户行为"""
        # 追踪行为
        action_id = await behavior_tracker.track_action(
            user_id=sample_user_action.user_id,
            action_type=sample_user_action.action_type,
            page=sample_user_action.page,
            session_id=sample_user_action.session_id,
            properties=sample_user_action.properties,
            duration=sample_user_action.duration,
            value=sample_user_action.value
        )

        assert action_id is not None
        assert action_id in behavior_tracker.actions

        # 验证行为记录
        tracked_action = behavior_tracker.actions[action_id]
        assert tracked_action.user_id == sample_user_action.user_id
        assert tracked_action.action_type == sample_user_action.action_type
        assert tracked_action.page == sample_user_action.page

    async def test_track_multiple_actions(self, behavior_tracker, sample_user_actions):
        """测试追踪多个用户行为"""
        action_ids = []

        for action in sample_user_actions:
            action_id = await behavior_tracker.track_action(
                user_id=action.user_id,
                action_type=action.action_type,
                page=action.page,
                session_id=action.session_id,
                properties=action.properties,
                duration=action.duration,
                value=action.value
            )
            action_ids.append(action_id)

        assert len(action_ids) == len(sample_user_actions)
        assert all(action_id in behavior_tracker.actions for action_id in action_ids)

        # 验证用户行为分组
        user_001_actions = behavior_tracker.user_actions["user_001"]
        assert len(user_001_actions) == 2  # user_001有2个行为

    async def test_start_session(self, behavior_tracker):
        """测试开始会话"""
        user_id = "user_001"
        device_type = DeviceType.DESKTOP

        session_id = await behavior_tracker.start_session(
            user_id=user_id,
            device_type=device_type
        )

        assert session_id is not None
        assert session_id in behavior_tracker.user_sessions
        assert session_id in behavior_tracker.active_sessions

        session = behavior_tracker.user_sessions[session_id]
        assert session.user_id == user_id
        assert session.device_type == device_type
        assert session.start_time is not None
        assert session.end_time is None

    async def test_end_session(self, behavior_tracker):
        """测试结束会话"""
        user_id = "user_001"

        # 开始会话
        session_id = await behavior_tracker.start_session(user_id=user_id)

        # 结束会话
        result = await behavior_tracker.end_session(session_id)

        assert result is True

        # 验证会话状态
        session = behavior_tracker.user_sessions[session_id]
        assert session.end_time is not None
        assert session.total_duration >= 0

        # 验证活跃会话被移除
        assert session_id not in behavior_tracker.active_sessions

    async def test_get_user_actions(self, behavior_tracker, sample_user_actions):
        """测试获取用户行为"""
        # 添加一些行为
        for action in sample_user_actions:
            await behavior_tracker.track_action(
                user_id=action.user_id,
                action_type=action.action_type,
                page=action.page,
                session_id=action.session_id
            )

        # 获取用户行为
        user_001_actions = await behavior_tracker.get_user_actions("user_001")
        user_002_actions = await behavior_tracker.get_user_actions("user_002")

        assert len(user_001_actions) == 2
        assert len(user_002_actions) == 1

        # 验证行为类型过滤
        search_actions = await behavior_tracker.get_user_actions(
            "user_001",
            action_type=ActionType.STOCK_SEARCH
        )
        assert len(search_actions) == 1
        assert search_actions[0].action_type == ActionType.STOCK_SEARCH

    async def test_get_user_sessions(self, behavior_tracker):
        """测试获取用户会话"""
        user_id = "user_001"

        # 创建多个会话
        session1 = await behavior_tracker.start_session(user_id=user_id)
        await asyncio.sleep(0.1)
        session2 = await behavior_tracker.start_session(user_id=user_id)

        # 获取用户会话
        sessions = await behavior_tracker.get_user_sessions(user_id)

        assert len(sessions) == 2
        assert all(session.user_id == user_id for session in sessions)

        # 结束一个会话
        await behavior_tracker.end_session(session1)

        # 再次获取会话
        active_sessions = await behavior_tracker.get_user_sessions(user_id, active_only=True)
        assert len(active_sessions) == 1
        assert active_sessions[0].session_id == session2

    async def test_session_timeout(self, behavior_tracker):
        """测试会话超时"""
        # 创建短超时的追踪器
        short_tracker = BehaviorTracker({"session_timeout": 1})  # 1秒超时

        user_id = "user_001"
        session_id = await short_tracker.start_session(user_id=user_id)

        # 等待超时
        await asyncio.sleep(2)

        # 清理过期会话
        await short_tracker.cleanup_expired_sessions()

        # 验证会话已被清理
        assert session_id not in short_tracker.active_sessions

    async def test_conversion_tracking(self, behavior_tracker):
        """测试转化追踪"""
        user_id = "user_001"
        session_id = await behavior_tracker.start_session(user_id=user_id)

        # 追踪一些行为，包括转化事件
        await behavior_tracker.track_action(
            user_id=user_id,
            action_type=ActionType.PAGE_VIEW,
            session_id=session_id,
            page="/landing"
        )

        await behavior_tracker.track_action(
            user_id=user_id,
            action_type=ActionType.PORTFOLIO_CREATE,
            session_id=session_id,
            page="/portfolio"
        )

        # 获取会话
        session = behavior_tracker.user_sessions[session_id]
        assert session.conversion_events == 1

    def test_calculate_session_metrics(self, behavior_tracker):
        """测试计算会话指标"""
        actions = [
            Mock(timestamp=datetime.now(), duration=30.0),
            Mock(timestamp=datetime.now(), duration=45.0),
            Mock(timestamp=datetime.now(), duration=60.0)
        ]

        session = Mock(actions=["action_1", "action_2", "action_3"])
        session.start_time = datetime.now() - timedelta(minutes=5)
        session.end_time = datetime.now()

        # 模拟计算指标
        metrics = behavior_tracker._calculate_session_metrics(session, actions)

        assert metrics["page_views"] == 3
        assert metrics["total_duration"] > 0
        assert metrics["conversion_events"] >= 0

    async def test_user_behavior_summary(self, behavior_tracker, sample_user_actions):
        """测试用户行为摘要"""
        user_id = "user_001"

        # 添加行为
        for action in sample_user_actions:
            if action.user_id == user_id:
                await behavior_tracker.track_action(
                    user_id=action.user_id,
                    action_type=action.action_type,
                    page=action.page,
                    session_id=action.session_id
                )

        # 获取摘要
        summary = await behavior_tracker.get_user_behavior_summary(user_id)

        assert "total_actions" in summary
        assert "total_sessions" in summary
        assert "action_types" in summary
        assert "most_active_hour" in summary
        assert "avg_session_duration" in summary

        assert summary["total_actions"] >= 1

    async def test_behavior_funnel_analysis(self, behavior_tracker):
        """测试行为漏斗分析"""
        funnel_steps = [
            ActionType.PAGE_VIEW,
            ActionType.STOCK_SEARCH,
            ActionType.PORTFOLIO_CREATE
        ]

        # 创建用户行为序列
        user_id = "funnel_user_001"
        session_id = await behavior_tracker.start_session(user_id=user_id)

        # 模拟漏斗行为
        await behavior_tracker.track_action(
            user_id=user_id,
            action_type=ActionType.PAGE_VIEW,
            session_id=session_id,
            page="/home"
        )

        await behavior_tracker.track_action(
            user_id=user_id,
            action_type=ActionType.STOCK_SEARCH,
            session_id=session_id,
            page="/search"
        )

        await behavior_tracker.track_action(
            user_id=user_id,
            action_type=ActionType.PORTFOLIO_CREATE,
            session_id=session_id,
            page="/portfolio"
        )

        # 分析漏斗
        funnel_analysis = await behavior_tracker.get_funnel_analysis(funnel_steps, days=1)

        assert len(funnel_analysis["steps"]) == len(funnel_steps)
        assert all("count" in step for step in funnel_analysis["steps"])
        assert all("conversion_rate" in step for step in funnel_analysis["steps"])

    def test_action_type_validation(self, behavior_tracker):
        """测试行为类型验证"""
        # 测试有效行为类型
        for action_type in ActionType:
            assert behavior_tracker._is_valid_action_type(action_type)

        # 测试无效行为类型
        invalid_type = "invalid_action_type"
        assert not behavior_tracker._is_valid_action_type(invalid_type)

    def test_device_type_handling(self, behavior_tracker):
        """测试设备类型处理"""
        # 测试设备类型转换
        assert behavior_tracker._parse_device_type("desktop") == DeviceType.DESKTOP
        assert behavior_tracker._parse_device_type("mobile") == DeviceType.MOBILE
        assert behavior_tracker._parse_device_type("tablet") == DeviceType.TABLET
        assert behavior_tracker._parse_device_type("unknown") == DeviceType.DESKTOP  # 默认值

    async def test_properties_validation(self, behavior_tracker):
        """测试属性验证"""
        valid_properties = {
            "string_prop": "value",
            "number_prop": 123,
            "bool_prop": True,
            "list_prop": [1, 2, 3]
        }

        # 验证有效属性
        assert behavior_tracker._validate_properties(valid_properties)

        # 测试无效属性（包含不可序列化的对象）
        invalid_properties = {
            "invalid_prop": object()
        }

        # 应该过滤掉无效属性
        validated = behavior_tracker._validate_properties(invalid_properties)
        assert "invalid_prop" not in validated

    async def test_action_limits(self, behavior_tracker):
        """测试行为限制"""
        user_id = "limit_test_user"
        max_actions = 5

        # 创建有限制的追踪器
        limited_tracker = BehaviorTracker({"max_actions_per_user": max_actions})

        # 添加超过限制的行为
        action_ids = []
        for i in range(max_actions + 2):
            try:
                action_id = await limited_tracker.track_action(
                    user_id=user_id,
                    action_type=ActionType.PAGE_VIEW,
                    page=f"/page_{i}"
                )
                action_ids.append(action_id)
            except Exception as e:
                # 应该在达到限制时抛出异常或优雅处理
                break

        # 验证不超过限制
        assert len(action_ids) <= max_actions

    async def test_real_time_statistics(self, behavior_tracker, sample_user_actions):
        """测试实时统计"""
        # 添加一些行为
        for action in sample_user_actions:
            await behavior_tracker.track_action(
                user_id=action.user_id,
                action_type=action.action_type,
                page=action.page,
                session_id=action.session_id
            )

        # 获取实时统计
        stats = await behavior_tracker.get_real_time_statistics()

        assert "total_actions" in stats
        assert "active_sessions" in stats
        assert "unique_users" in stats
        assert "top_actions" in stats
        assert "user_growth" in stats

        assert stats["total_actions"] >= len(sample_user_actions)

    def test_system_statistics(self, behavior_tracker):
        """测试系统统计"""
        stats = behavior_tracker.get_system_statistics()

        assert "total_actions" in stats
        assert "total_sessions" in stats
        assert "total_users" in stats
        assert "action_type_distribution" in stats
        assert "device_type_distribution" in stats

        # 验证分布总和
        action_dist = stats["action_type_distribution"]
        if action_dist:
            total_actions = sum(action_dist.values())
            assert total_actions == stats["total_actions"]

    async def test_data_cleanup(self, behavior_tracker):
        """测试数据清理"""
        # 添加一些过期数据
        old_time = datetime.now() - timedelta(days=10)

        old_action = UserAction(
            action_id="old_action",
            user_id="old_user",
            action_type=ActionType.PAGE_VIEW,
            timestamp=old_time,
            session_id="old_session"
        )

        behavior_tracker.actions["old_action"] = old_action
        behavior_tracker.user_actions["old_user"] = ["old_action"]

        # 清理过期数据
        await behavior_tracker.cleanup_old_data(days=7)

        # 验证过期数据被清理
        assert "old_action" not in behavior_tracker.actions
        assert "old_user" not in behavior_tracker.user_actions

    def test_action_serialization(self):
        """测试行为序列化"""
        action = UserAction(
            action_id="test_action",
            user_id="test_user",
            action_type=ActionType.PAGE_VIEW,
            timestamp=datetime.now(),
            session_id="test_session",
            properties={"key": "value"}
        )

        # 序列化为字典
        action_dict = action.to_dict()

        assert action_dict["action_id"] == "test_action"
        assert action_dict["user_id"] == "test_user"
        assert action_dict["action_type"] == ActionType.PAGE_VIEW.value

        # 从字典创建行为
        new_action = UserAction.from_dict(action_dict)

        assert new_action.action_id == action.action_id
        assert new_action.user_id == action.user_id
        assert new_action.action_type == action.action_type

@pytest.mark.unit
@pytest.mark.analytics
@pytest.mark.ai
class TestBehaviorTrackerIntegration:
    """行为追踪器集成测试"""

    @pytest.mark.asyncio
    async def test_complete_user_journey(self, behavior_tracker):
        """测试完整用户旅程"""
        user_id = "journey_user_001"

        # 1. 用户登录
        await behavior_tracker.track_action(
            user_id=user_id,
            action_type=ActionType.LOGIN,
            properties={"login_method": "email"}
        )

        # 2. 开始会话
        session_id = await behavior_tracker.start_session(
            user_id=user_id,
            device_type=DeviceType.DESKTOP
        )

        # 3. 浏览首页
        await behavior_tracker.track_action(
            user_id=user_id,
            action_type=ActionType.PAGE_VIEW,
            session_id=session_id,
            page="/dashboard",
            duration=15.0
        )

        # 4. 搜索股票
        await behavior_tracker.track_action(
            user_id=user_id,
            action_type=ActionType.STOCK_SEARCH,
            session_id=session_id,
            page="/search",
            properties={"query": "腾讯", "symbol": "0700.HK"}
        )

        # 5. 查看股票详情
        await behavior_tracker.track_action(
            user_id=user_id,
            action_type=ActionType.STOCK_VIEW,
            session_id=session_id,
            page="/stock/0700.HK",
            duration=45.0
        )

        # 6. 创建投资组合（转化事件）
        await behavior_tracker.track_action(
            user_id=user_id,
            action_type=ActionType.PORTFOLIO_CREATE,
            session_id=session_id,
            page="/portfolio",
            value=10000.0
        )

        # 7. 结束会话
        await behavior_tracker.end_session(session_id)

        # 验证用户旅程
        actions = await behavior_tracker.get_user_actions(user_id)
        assert len(actions) >= 5  # 至少5个主要行为

        sessions = await behavior_tracker.get_user_sessions(user_id)
        assert len(sessions) >= 1

        # 验证转化追踪
        session = behavior_tracker.user_sessions[session_id]
        assert session.conversion_events >= 1

        # 获取用户行为摘要
        summary = await behavior_tracker.get_user_behavior_summary(user_id)
        assert summary["total_actions"] >= 5
        assert summary["conversion_events"] >= 1

    @pytest.mark.asyncio
    async def test_multi_user_behavior_comparison(self, behavior_tracker):
        """测试多用户行为比较"""
        users = ["user_a", "user_b", "user_c"]

        # 为不同用户创建不同的行为模式
        for i, user_id in enumerate(users):
            session_id = await behavior_tracker.start_session(user_id=user_id)

            # 用户A：浏览型用户
            if user_id == "user_a":
                for j in range(5):
                    await behavior_tracker.track_action(
                        user_id=user_id,
                        action_type=ActionType.PAGE_VIEW,
                        session_id=session_id,
                        page=f"/page_{j}",
                        duration=20.0
                    )

            # 用户B：搜索型用户
            elif user_id == "user_b":
                for j in range(3):
                    await behavior_tracker.track_action(
                        user_id=user_id,
                        action_type=ActionType.STOCK_SEARCH,
                        session_id=session_id,
                        page="/search",
                        properties={"query": f"stock_{j}"}
                    )

            # 用户C：转化型用户
            elif user_id == "user_c":
                await behavior_tracker.track_action(
                    user_id=user_id,
                    action_type=ActionType.PORTFOLIO_CREATE,
                    session_id=session_id,
                    value=5000.0
                )

            await behavior_tracker.end_session(session_id)

        # 比较用户行为
        user_summaries = {}
        for user_id in users:
            user_summaries[user_id] = await behavior_tracker.get_user_behavior_summary(user_id)

        # 验证不同用户的行为模式
        assert user_summaries["user_a"]["total_actions"] >= 5  # 浏览型用户行为最多
        assert user_summaries["user_b"]["action_types"].get("stock_search", 0) >= 3  # 搜索型用户
        assert user_summaries["user_c"]["conversion_events"] >= 1  # 转化型用户

    @pytest.mark.asyncio
    async def test_behavior_funnel_with_multiple_users(self, behavior_tracker):
        """测试多用户行为漏斗"""
        funnel_steps = [
            ActionType.PAGE_VIEW,
            ActionType.STOCK_SEARCH,
            ActionType.STOCK_VIEW,
            ActionType.PORTFOLIO_CREATE
        ]

        # 创建多个用户，每个用户在漏斗的不同阶段停止
        users_data = [
            {"user_id": "funnel_user_1", "steps": [ActionType.PAGE_VIEW]},
            {"user_id": "funnel_user_2", "steps": [ActionType.PAGE_VIEW, ActionType.STOCK_SEARCH]},
            {"user_id": "funnel_user_3", "steps": [ActionType.PAGE_VIEW, ActionType.STOCK_SEARCH, ActionType.STOCK_VIEW]},
            {"user_id": "funnel_user_4", "steps": funnel_steps},
            {"user_id": "funnel_user_5", "steps": funnel_steps},
        ]

        for user_data in users_data:
            user_id = user_data["user_id"]
            steps = user_data["steps"]
            session_id = await behavior_tracker.start_session(user_id=user_id)

            for step in steps:
                await behavior_tracker.track_action(
                    user_id=user_id,
                    action_type=step,
                    session_id=session_id
                )

            await behavior_tracker.end_session(session_id)

        # 分析漏斗
        funnel_analysis = await behavior_tracker.get_funnel_analysis(funnel_steps, days=1)

        # 验证漏斗数据
        assert len(funnel_analysis["steps"]) == len(funnel_steps)

        # 验证转化率递减（漏斗效应）
        conversion_rates = [step["conversion_rate"] for step in funnel_analysis["steps"]]
        for i in range(1, len(conversion_rates)):
            assert conversion_rates[i] <= conversion_rates[i-1]

        # 验证最终转化率
        final_step = funnel_analysis["steps"][-1]
        expected_final_conversions = len([u for u in users_data if set(u["steps"]) >= set(funnel_steps)])
        assert final_step["count"] >= expected_final_conversions

    @pytest.mark.asyncio
    async def test_session_behavior_patterns(self, behavior_tracker):
        """测试会话行为模式"""
        # 创建不同类型的会话
        session_patterns = [
            {
                "name": "短会话",
                "actions": [
                    (ActionType.PAGE_VIEW, 10),
                    (ActionType.STOCK_SEARCH, 5)
                ],
                "expected_duration": 60  # 1分钟
            },
            {
                "name": "长会话",
                "actions": [
                    (ActionType.PAGE_VIEW, 30),
                    (ActionType.STOCK_SEARCH, 20),
                    (ActionType.STOCK_VIEW, 60),
                    (ActionType.PORTFOLIO_CREATE, 30)
                ],
                "expected_duration": 300  # 5分钟
            },
            {
                "name": "高活跃会话",
                "actions": [
                    (ActionType.PAGE_VIEW, 5),
                    (ActionType.STOCK_SEARCH, 5),
                    (ActionType.STOCK_VIEW, 5),
                    (ActionType.CHAT_MESSAGE, 5),
                    (ActionType.PORTFOLIO_UPDATE, 5),
                    (ActionType.RISK_ANALYSIS, 5)
                ],
                "expected_duration": 180  # 3分钟
            }
        ]

        for pattern in session_patterns:
            user_id = f"{pattern['name']}_user"
            session_id = await behavior_tracker.start_session(user_id=user_id)

            # 添加会话行为
            for action_type, duration in pattern["actions"]:
                await behavior_tracker.track_action(
                    user_id=user_id,
                    action_type=action_type,
                    session_id=session_id,
                    duration=duration
                )

            # 模拟会话持续时间
            session = behavior_tracker.user_sessions[session_id]
            session.start_time = datetime.now() - timedelta(seconds=pattern["expected_duration"])
            session.end_time = datetime.now()

        # 分析会话模式
        sessions = await behavior_tracker.get_user_sessions(f"{session_patterns[0]['name']}_user")
        assert len(sessions) >= 1

        # 验证会话指标
        for session in sessions:
            if session.total_duration:
                assert session.total_duration >= 0
            assert session.page_views >= 1