"""
ChatBot对话管理器单元测试
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.services.ai_service.chatbot.conversation_manager import (
    ConversationManager, DialogueState, Message
)

@pytest.fixture
def conversation_manager():
    """对话管理器夹具"""
    config = {
        "max_conversation_history": 10,
        "session_timeout": 1800,  # 30分钟
        "max_sessions_per_user": 5
    }
    return ConversationManager(config)

@pytest.fixture
def sample_message():
    """示例消息"""
    return Message(
        role="user",
        content="什么是市盈率？",
        timestamp=datetime.now(),
        metadata={"intent": "knowledge_query"}
    )

@pytest.fixture
def sample_conversation():
    """示例对话数据"""
    return {
        "user_id": "test_user_001",
        "session_id": "test_session_001",
        "messages": [
            {
                "role": "user",
                "content": "你好",
                "timestamp": datetime.now() - timedelta(minutes=5),
                "metadata": {}
            },
            {
                "role": "assistant",
                "content": "您好！我是您的智能投资助手，有什么可以帮助您的吗？",
                "timestamp": datetime.now() - timedelta(minutes=4),
                "metadata": {"state": "greeting"}
            }
        ]
    }

class TestConversationManager:
    """对话管理器测试类"""

    @pytest.mark.asyncio
    async def test_create_conversation(self, conversation_manager):
        """测试创建对话"""
        user_id = "test_user_001"

        conversation = await conversation_manager.create_conversation(user_id)

        assert conversation is not None
        assert conversation.user_id == user_id
        assert conversation.session_id is not None
        assert conversation.state == DialogueState.ACTIVE
        assert len(conversation.messages) == 1  # 应该包含欢迎消息
        assert conversation.messages[0].role == "assistant"

    @pytest.mark.asyncio
    async def test_get_conversation(self, conversation_manager, sample_conversation):
        """测试获取对话"""
        user_id = sample_conversation["user_id"]
        session_id = sample_conversation["session_id"]

        # 先创建对话
        await conversation_manager.create_conversation(user_id)

        # 获取对话
        conversation = await conversation_manager.get_conversation(session_id)

        assert conversation is not None
        assert conversation.user_id == user_id
        assert conversation.session_id == session_id

    @pytest.mark.asyncio
    async def test_get_nonexistent_conversation(self, conversation_manager):
        """测试获取不存在的对话"""
        non_existent_session = "non_existent_session"

        conversation = await conversation_manager.get_conversation(non_existent_session)

        assert conversation is None

    @pytest.mark.asyncio
    async def test_add_message(self, conversation_manager, sample_message):
        """测试添加消息"""
        user_id = "test_user_001"

        # 创建对话
        conversation = await conversation_manager.create_conversation(user_id)

        # 添加用户消息
        updated_conversation = await conversation_manager.add_message(
            conversation.session_id,
            sample_message
        )

        assert len(updated_conversation.messages) == 2  # 欢迎消息 + 用户消息
        assert updated_conversation.messages[-1].content == sample_message.content
        assert updated_conversation.messages[-1].role == sample_message.role

    @pytest.mark.asyncio
    async def test_get_conversation_history(self, conversation_manager, sample_conversation):
        """测试获取对话历史"""
        user_id = sample_conversation["user_id"]

        # 创建对话并添加多条消息
        conversation = await conversation_manager.create_conversation(user_id)

        messages = [
            Message(role="user", content="什么是市盈率？", timestamp=datetime.now()),
            Message(role="assistant", content="市盈率是...", timestamp=datetime.now()),
            Message(role="user", content="谢谢", timestamp=datetime.now())
        ]

        for msg in messages:
            await conversation_manager.add_message(conversation.session_id, msg)

        # 获取历史
        history = await conversation_manager.get_conversation_history(
            conversation.session_id,
            limit=5
        )

        assert len(history) >= len(messages) + 1  # +1 for welcome message
        assert history[-1]["content"] == "谢谢"

    @pytest.mark.asyncio
    async def test_clear_conversation(self, conversation_manager):
        """测试清除对话"""
        user_id = "test_user_001"

        # 创建对话
        conversation = await conversation_manager.create_conversation(user_id)

        # 添加一些消息
        message = Message(role="user", content="测试消息", timestamp=datetime.now())
        await conversation_manager.add_message(conversation.session_id, message)

        # 清除对话
        result = await conversation_manager.clear_conversation(conversation.session_id)

        assert result is True

        # 验证对话已清除
        cleared_conversation = await conversation_manager.get_conversation(conversation.session_id)
        assert cleared_conversation is None

    @pytest.mark.asyncio
    async def test_end_conversation(self, conversation_manager):
        """测试结束对话"""
        user_id = "test_user_001"

        # 创建对话
        conversation = await conversation_manager.create_conversation(user_id)

        # 结束对话
        result = await conversation_manager.end_conversation(conversation.session_id)

        assert result is True

        # 验证对话状态
        ended_conversation = await conversation_manager.get_conversation(conversation.session_id)
        assert ended_conversation is not None
        assert ended_conversation.state == DialogueState.ENDED

    @pytest.mark.asyncio
    async def test_get_user_active_sessions(self, conversation_manager):
        """测试获取用户活跃会话"""
        user_id = "test_user_001"

        # 创建多个对话
        session1 = await conversation_manager.create_conversation(user_id)
        session2 = await conversation_manager.create_conversation(user_id)

        # 结束其中一个
        await conversation_manager.end_conversation(session2.session_id)

        # 获取活跃会话
        active_sessions = await conversation_manager.get_user_active_sessions(user_id)

        assert len(active_sessions) == 1
        assert active_sessions[0].session_id == session1.session_id

    @pytest.mark.asyncio
    async def test_session_timeout(self, conversation_manager):
        """测试会话超时"""
        # 创建一个短超时的管理器
        short_timeout_config = {"session_timeout": 1}  # 1秒超时
        short_manager = ConversationManager(short_timeout_config)

        user_id = "test_user_001"

        # 创建对话
        conversation = await short_manager.create_conversation(user_id)

        # 等待超时
        await asyncio.sleep(2)

        # 检查会话是否超时
        await short_manager.cleanup_expired_sessions()

        # 验证会话已被清理
        expired_conversation = await short_manager.get_conversation(conversation.session_id)
        assert expired_conversation is None or expired_conversation.state == DialogueState.EXPIRED

    @pytest.mark.asyncio
    async def test_max_sessions_per_user(self, conversation_manager):
        """测试每用户最大会话数限制"""
        user_id = "test_user_001"

        # 创建超过限制的会话（假设限制为5）
        sessions = []
        for i in range(7):  # 创建7个会话
            session = await conversation_manager.create_conversation(user_id)
            sessions.append(session)

        # 验证只保留了最新的会话
        active_sessions = await conversation_manager.get_user_active_sessions(user_id)
        assert len(active_sessions) <= 5  # 不应该超过限制

    @pytest.mark.asyncio
    async def test_conversation_context(self, conversation_manager):
        """测试对话上下文"""
        user_id = "test_user_001"

        # 创建对话
        conversation = await conversation_manager.create_conversation(user_id)

        # 添加相关消息
        messages = [
            Message(role="user", content="我想了解腾讯股票", timestamp=datetime.now()),
            Message(role="assistant", content="腾讯(0700.HK)是中国领先的互联网公司...", timestamp=datetime.now()),
            Message(role="user", content="它的市盈率是多少？", timestamp=datetime.now())
        ]

        for msg in messages:
            await conversation_manager.add_message(conversation.session_id, msg)

        # 获取上下文
        context = await conversation_manager.get_conversation_context(conversation.session_id)

        assert "腾讯" in context
        assert "0700.HK" in context
        assert len(context) > 0

    @pytest.mark.asyncio
    async def test_conversation_state_transitions(self, conversation_manager):
        """测试对话状态转换"""
        user_id = "test_user_001"

        # 创建对话
        conversation = await conversation_manager.create_conversation(user_id)
        assert conversation.state == DialogueState.ACTIVE

        # 暂停对话
        await conversation_manager.pause_conversation(conversation.session_id)
        paused_conversation = await conversation_manager.get_conversation(conversation.session_id)
        assert paused_conversation.state == DialogueState.PAUSED

        # 恢复对话
        await conversation_manager.resume_conversation(conversation.session_id)
        resumed_conversation = await conversation_manager.get_conversation(conversation.session_id)
        assert resumed_conversation.state == DialogueState.ACTIVE

        # 结束对话
        await conversation_manager.end_conversation(conversation.session_id)
        ended_conversation = await conversation_manager.get_conversation(conversation.session_id)
        assert ended_conversation.state == DialogueState.ENDED

    @pytest.mark.asyncio
    async def test_conversation_statistics(self, conversation_manager):
        """测试对话统计"""
        user_id = "test_user_001"

        # 创建对话
        conversation = await conversation_manager.create_conversation(user_id)

        # 添加多条消息
        for i in range(5):
            message = Message(
                role="user" if i % 2 == 0 else "assistant",
                content=f"消息 {i}",
                timestamp=datetime.now()
            )
            await conversation_manager.add_message(conversation.session_id, message)

        # 获取统计
        stats = await conversation_manager.get_conversation_statistics(conversation.session_id)

        assert stats["message_count"] == 6  # 5条 + 1条欢迎消息
        assert stats["duration"] >= 0
        assert "user_message_count" in stats
        assert "assistant_message_count" in stats

    def test_message_serialization(self):
        """测试消息序列化"""
        message = Message(
            role="user",
            content="测试消息",
            timestamp=datetime.now(),
            metadata={"intent": "test", "confidence": 0.8}
        )

        # 转换为字典
        message_dict = message.to_dict()

        assert message_dict["role"] == "user"
        assert message_dict["content"] == "测试消息"
        assert "timestamp" in message_dict
        assert message_dict["metadata"]["intent"] == "test"

        # 从字典创建消息
        new_message = Message.from_dict(message_dict)

        assert new_message.role == message.role
        assert new_message.content == message.content
        assert new_message.metadata == message.metadata

    @pytest.mark.asyncio
    async def test_conversation_persistence(self, conversation_manager):
        """测试对话持久化"""
        user_id = "test_user_001"

        # 创建对话
        conversation = await conversation_manager.create_conversation(user_id)

        # 添加消息
        message = Message(role="user", content="持久化测试", timestamp=datetime.now())
        await conversation_manager.add_message(conversation.session_id, message)

        # 模拟持久化存储
        conversation_data = await conversation_manager.serialize_conversation(conversation.session_id)

        assert conversation_data is not None
        assert conversation_data["user_id"] == user_id
        assert len(conversation_data["messages"]) >= 1

    @pytest.mark.asyncio
    async def test_error_handling(self, conversation_manager):
        """测试错误处理"""
        # 测试无效session_id
        result = await conversation_manager.add_message("invalid_session", None)
        assert result is None

        # 测试无效消息
        conversation = await conversation_manager.create_conversation("test_user")
        result = await conversation_manager.add_message(conversation.session_id, None)
        assert result is None

        # 测试重复结束对话
        await conversation_manager.end_conversation(conversation.session_id)
        result2 = await conversation_manager.end_conversation(conversation.session_id)
        # 应该能处理重复结束，不抛出异常
        assert result2 is True or result2 is False

@pytest.mark.unit
@pytest.mark.chatbot
class TestConversationManagerIntegration:
    """对话管理器集成测试"""

    @pytest.mark.asyncio
    async def test_full_conversation_flow(self, conversation_manager):
        """测试完整对话流程"""
        user_id = "integration_test_user"

        # 1. 创建对话
        conversation = await conversation_manager.create_conversation(user_id)
        assert conversation is not None

        # 2. 用户发起询问
        user_message = Message(
            role="user",
            content="什么是市盈率？",
            timestamp=datetime.now()
        )
        conversation = await conversation_manager.add_message(
            conversation.session_id,
            user_message
        )

        # 3. 助手回复
        assistant_message = Message(
            role="assistant",
            content="市盈率是股票价格与每股收益的比率...",
            timestamp=datetime.now(),
            metadata={"intent": "knowledge_query", "confidence": 0.9}
        )
        conversation = await conversation_manager.add_message(
            conversation.session_id,
            assistant_message
        )

        # 4. 用户追问
        followup_message = Message(
            role="user",
            content="谢谢，能给我举个例子吗？",
            timestamp=datetime.now()
        )
        conversation = await conversation_manager.add_message(
            conversation.session_id,
            followup_message
        )

        # 5. 验证对话历史
        history = await conversation_manager.get_conversation_history(conversation.session_id)
        assert len(history) == 4  # 欢迎消息 + 3条交互消息

        # 6. 获取上下文
        context = await conversation_manager.get_conversation_context(conversation.session_id)
        assert "市盈率" in context

        # 7. 结束对话
        result = await conversation_manager.end_conversation(conversation.session_id)
        assert result is True

        # 8. 验证最终状态
        final_conversation = await conversation_manager.get_conversation(conversation.session_id)
        assert final_conversation.state == DialogueState.ENDED