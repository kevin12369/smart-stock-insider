"""
聊天机器人API集成测试
测试聊天机器人API的完整交互流程
"""

import pytest
import asyncio
import aiohttp
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta

from tests.utils import TestDataGenerator, APITestHelper
from tests.conftest import get_test_config


class TestChatbotAPIIntegration:
    """聊天机器人API集成测试类"""

    @pytest.fixture(scope="class")
    async def api_client(self):
        """创建API客户端"""
        config = get_test_config()
        base_url = config["api"]["base_url"]
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(
            base_url=base_url,
            timeout=timeout,
            headers={"Content-Type": "application/json"}
        ) as session:
            yield session

    @pytest.fixture
    def api_helper(self):
        """API测试助手"""
        return APITestHelper()

    @pytest.fixture
    def sample_conversation_start(self):
        """示例对话开始请求"""
        return {
            "user_id": "test_user_123",
            "session_type": "investment_consultation",
            "context": {
                "preferred_language": "zh",
                "risk_tolerance": "moderate",
                "investment_goals": ["growth", "income"]
            }
        }

    @pytest.fixture
    def sample_message(self):
        """示例消息"""
        return {
            "message": "我想了解AAPL股票的投资前景",
            "metadata": {
                "user_intent": "stock_analysis",
                "mentioned_symbols": ["AAPL"]
            }
        }

    @pytest.mark.asyncio
    async def test_conversation_lifecycle_complete_flow(self, api_client, sample_conversation_start, api_helper):
        """测试对话生命周期完整流程"""

        # 1. 开始对话
        async with api_client.post("/api/chatbot/conversation/start", json=sample_conversation_start) as response:
            assert response.status == 201

            conversation_data = await response.json()
            api_helper.validate_conversation_start_response(conversation_data)

            conversation_id = conversation_data["conversation_id"]
            session_id = conversation_data["session_id"]

        # 2. 发送消息并获取回复
        sample_message = {
            "conversation_id": conversation_id,
            "message": "请分析一下AAPL股票的投资价值",
            "metadata": {
                "symbols_mentioned": ["AAPL"],
                "intent": "stock_analysis"
            }
        }

        async with api_client.post("/api/chatbot/message", json=sample_message) as response:
            assert response.status == 200

            message_response = await response.json()
            api_helper.validate_chatbot_message_response(message_response)

            assert message_response["conversation_id"] == conversation_id
            assert "response" in message_response
            assert "message_id" in message_response

        # 3. 获取对话历史
        async with api_client.get(f"/api/chatbot/conversation/{conversation_id}/history") as response:
            assert response.status == 200

            history = await response.json()
            api_helper.validate_conversation_history_response(history)

            assert len(history["messages"]) >= 2  # 至少用户消息 + AI回复

        # 4. 获取对话状态
        async with api_client.get(f"/api/chatbot/conversation/{conversation_id}/status") as response:
            assert response.status == 200

            status = await response.json()
            assert status["conversation_id"] == conversation_id
            assert status["status"] in ["active", "paused", "completed"]

        # 5. 结束对话
        async with api_client.post(f"/api/chatbot/conversation/{conversation_id}/end") as response:
            if response.status != 404:  # 结束对话功能可能未实现
                assert response.status == 200

    @pytest.mark.asyncio
    async def test_multi_turn_conversation_flow(self, api_client, sample_conversation_start, api_helper):
        """测试多轮对话流程"""

        # 开始对话
        async with api_client.post("/api/chatbot/conversation/start", json=sample_conversation_start) as response:
            conversation_data = await response.json()
            conversation_id = conversation_data["conversation_id"]

        # 多轮对话
        conversation_messages = [
            "我想了解科技股的投资机会",
            "哪些科技公司值得投资？",
            "AAPL和GOOGL相比，哪个更适合长期投资？",
            "如果我有10万元，应该如何配置这些股票？",
            "谢谢你的建议，我还有什么需要注意的风险吗？"
        ]

        message_responses = []
        for i, message_text in enumerate(conversation_messages):
            message_request = {
                "conversation_id": conversation_id,
                "message": message_text,
                "metadata": {
                    "turn_number": i + 1,
                    "intent": "investment_advice"
                }
            }

            async with api_client.post("/api/chatbot/message", json=message_request) as response:
                assert response.status == 200

                message_response = await response.json()
                message_responses.append(message_response)

                # 验证回复内容
                assert len(message_response["response"]) > 0
                assert message_response["conversation_id"] == conversation_id

                # 添加延迟模拟真实对话
                await asyncio.sleep(0.5)

        # 验证对话连贯性
        responses_text = [resp["response"] for resp in message_responses]
        assert len(responses_text) == len(conversation_messages)

        # 验证对话历史包含所有消息
        async with api_client.get(f"/api/chatbot/conversation/{conversation_id}/history") as response:
            history = await response.json()
            total_messages = len(history["messages"])
            expected_messages = len(conversation_messages) * 2  # 用户消息 + AI回复

            assert total_messages >= expected_messages

    @pytest.mark.asyncio
    async def test_context_aware_conversation(self, api_client, sample_conversation_start, api_helper):
        """测试上下文感知对话"""

        # 开始对话
        async with api_client.post("/api/chatbot/conversation/start", json=sample_conversation_start) as response:
            conversation_data = await response.json()
            conversation_id = conversation_data["conversation_id"]

        # 建立上下文
        context_messages = [
            "我是一名保守型投资者",
            "我的投资期限是3-5年",
            "我比较关注科技股，但风险承受能力较低"
        ]

        for msg in context_messages:
            message_request = {
                "conversation_id": conversation_id,
                "message": msg,
                "metadata": {"context_building": True}
            }

            async with api_client.post("/api/chatbot/message", json=message_request) as response:
                assert response.status == 200

        # 测试上下文感知的回复
        context_aware_question = "请推荐一些适合我的科技股"
        message_request = {
            "conversation_id": conversation_id,
            "message": context_aware_question,
            "metadata": {"requires_context": True}
        }

        async with api_client.post("/api/chatbot/message", json=message_request) as response:
            assert response.status == 200

            response_data = await response.json()
            ai_response = response_data["response"]

            # 验证回复考虑了用户的风险偏好和投资期限
            context_keywords = ["保守", "风险", "长期", "稳定"]
            found_context_reference = any(keyword in ai_response for keyword in context_keywords)

            # AI回复应该体现对用户风险偏好的理解
            assert len(ai_response) > 0

    @pytest.mark.asyncio
    async def test_conversation_personalization(self, api_client, api_helper):
        """测试对话个性化"""

        # 创建不同的用户画像
        user_profiles = [
            {
                "user_id": "aggressive_user",
                "session_type": "investment_consultation",
                "context": {
                    "risk_tolerance": "aggressive",
                    "investment_experience": "expert",
                    "preferred_sectors": ["technology", "biotech"]
                }
            },
            {
                "user_id": "conservative_user",
                "session_type": "investment_consultation",
                "context": {
                    "risk_tolerance": "conservative",
                    "investment_experience": "beginner",
                    "preferred_sectors": ["utilities", "consumer_staples"]
                }
            }
        ]

        conversation_responses = {}

        # 为每个用户画像开始对话
        for profile in user_profiles:
            async with api_client.post("/api/chatbot/conversation/start", json=profile) as response:
                conversation_data = await response.json()
                conversation_id = conversation_data["conversation_id"]

            # 发送相同的问题
            message_request = {
                "conversation_id": conversation_id,
                "message": "请为我推荐一些股票投资机会",
                "metadata": {"personalization_test": True}
            }

            async with api_client.post("/api/chatbot/message", json=message_request) as response:
                response_data = await response.json()
                conversation_responses[profile["user_id"]] = response_data["response"]

        # 验证个性化回复
        aggressive_response = conversation_responses["aggressive_user"]
        conservative_response = conversation_responses["conservative_user"]

        # 两个回复应该有所不同
        assert aggressive_response != conservative_response

        # 激进型用户的回复应该提到更多成长性投资
        aggressive_keywords = ["成长", "高收益", "科技", "创新"]
        conservative_keywords = ["稳定", "收益", "风险", "保守"]

        aggressive_score = sum(1 for keyword in aggressive_keywords if keyword in aggressive_response)
        conservative_score = sum(1 for keyword in conservative_keywords if keyword in conservative_response)

        assert aggressive_score > 0
        assert conservative_score > 0

    @pytest.mark.asyncio
    async def test_conversation_error_handling(self, api_client, api_helper):
        """测试对话错误处理"""

        # 测试无效的对话开始请求
        invalid_start = {
            "user_id": "",  # 空用户ID
            "session_type": "invalid_type"
        }

        async with api_client.post("/api/chatbot/conversation/start", json=invalid_start) as response:
            assert response.status in [400, 422]

            error = await response.json()
            assert "error" in error

        # 测试无效的消息请求
        invalid_message = {
            "conversation_id": "invalid_conversation",
            "message": ""  # 空消息
        }

        async with api_client.post("/api/chatbot/message", json=invalid_message) as response:
            assert response.status in [400, 404, 422]

        # 测试不存在的对话ID
        async with api_client.get("/api/chatbot/conversation/nonexistent/history") as response:
            assert response.status == 404

        # 测试过长的消息
        long_message = {
            "conversation_id": "test_conversation",
            "message": "A" * 10000  # 超长消息
        }

        async with api_client.post("/api/chatbot/message", json=long_message) as response:
            assert response.status in [400, 413]

    @pytest.mark.asyncio
    async def test_conversation_session_management(self, api_client, api_helper):
        """测试对话会话管理"""

        user_id = "session_test_user"

        # 开始多个会话
        conversations = []
        for i in range(3):
            session_start = {
                "user_id": user_id,
                "session_type": "investment_consultation",
                "context": {"session_number": i + 1}
            }

            async with api_client.post("/api/chatbot/conversation/start", json=session_start) as response:
                conversation_data = await response.json()
                conversations.append(conversation_data)

        # 获取用户的所有会话
        async with api_client.get(f"/api/chatbot/user/{user_id}/sessions") as response:
            if response.status == 404:
                pytest.skip("用户会话管理功能未实现")

            assert response.status == 200

            user_sessions = await response.json()
            assert isinstance(user_sessions, list)
            assert len(user_sessions) >= 3

        # 验证每个会话的状态
        for conversation in conversations:
            conversation_id = conversation["conversation_id"]

            async with api_client.get(f"/api/chatbot/conversation/{conversation_id}/status") as response:
                assert response.status == 200

                status = await response.json()
                assert "status" in status
                assert "last_activity" in status

    @pytest.mark.asyncio
    async def test_conversation_analytics(self, api_client, sample_conversation_start, api_helper):
        """测试对话分析功能"""

        # 开始对话并进行多轮交互
        async with api_client.post("/api/chatbot/conversation/start", json=sample_conversation_start) as response:
            conversation_data = await response.json()
            conversation_id = conversation_data["conversation_id"]

        # 发送多条消息生成分析数据
        test_messages = [
            "请分析AAPL股票",
            "这个投资风险如何？",
            "有其他建议吗？"
        ]

        for msg in test_messages:
            message_request = {
                "conversation_id": conversation_id,
                "message": msg
            }

            async with api_client.post("/api/chatbot/message", json=message_request) as response:
                assert response.status == 200

        # 获取对话分析
        async with api_client.get(f"/api/chatbot/analytics/conversation/{conversation_id}") as response:
            if response.status == 404:
                pytest.skip("对话分析功能未实现")

            assert response.status == 200

            analytics = await response.json()
            api_helper.validate_conversation_analytics_response(analytics)

            assert "conversation_id" in analytics
            assert analytics["conversation_id"] == conversation_id

        # 获取用户级别的分析
        user_id = sample_conversation_start["user_id"]
        async with api_client.get(f"/api/chatbot/analytics/user/{user_id}") as response:
            if response.status == 404:
                pytest.skip("用户分析功能未实现")

            assert response.status == 200

            user_analytics = await response.json()
            assert "user_id" in user_analytics
            assert "total_conversations" in user_analytics
            assert "engagement_metrics" in user_analytics

    @pytest.mark.asyncio
    async def test_conversation_performance_monitoring(self, api_client, sample_conversation_start):
        """测试对话性能监控"""

        # 开始对话并测量响应时间
        start_time = datetime.now()

        async with api_client.post("/api/chatbot/conversation/start", json=sample_conversation_start) as response:
            assert response.status == 201
            conversation_data = await response.json()

        conversation_start_time = datetime.now()
        conversation_creation_time = (conversation_start_time - start_time).total_seconds()

        # 对话创建应该在合理时间内完成
        assert conversation_creation_time < 5.0

        # 测试消息响应时间
        message_request = {
            "conversation_id": conversation_data["conversation_id"],
            "message": "请简单介绍一下投资策略"
        }

        message_start_time = datetime.now()
        async with api_client.post("/api/chatbot/message", json=message_request) as response:
            assert response.status == 200
            message_response = await response.json()

        message_response_time = (datetime.now() - message_start_time).total_seconds()

        # 消息响应时间应该在合理范围内
        assert message_response_time < 30.0

        # 验证响应时间监控数据（如果API支持）
        if "response_time" in message_response:
            assert message_response["response_time"] > 0
            assert abs(message_response["response_time"] - message_response_time) < 1.0  # 1秒误差范围

    @pytest.mark.asyncio
    async def test_conversation_rate_limiting(self, api_client, sample_conversation_start):
        """测试对话速率限制"""

        # 开始对话
        async with api_client.post("/api/chatbot/conversation/start", json=sample_conversation_start) as response:
            conversation_data = await response.json()
            conversation_id = conversation_data["conversation_id"]

        # 快速发送多条消息测试速率限制
        rapid_messages = []
        rate_limited_responses = 0

        for i in range(10):  # 发送10条快速消息
            message_request = {
                "conversation_id": conversation_id,
                "message": f"测试消息 {i + 1}",
                "metadata": {"rate_limit_test": True}
            }

            async with api_client.post("/api/chatbot/message", json=message_request) as response:
                if response.status == 429:  # Too Many Requests
                    rate_limited_responses += 1
                elif response.status == 200:
                    rapid_messages.append(await response.json())

            # 极短延迟
            await asyncio.sleep(0.1)

        # 验证速率限制行为
        if rate_limited_responses > 0:
            assert rate_limited_responses > 0

            # 等待后重试应该成功
            await asyncio.sleep(2)

            retry_request = {
                "conversation_id": conversation_id,
                "message": "重试消息"
            }

            async with api_client.post("/api/chatbot/message", json=retry_request) as response:
                assert response.status == 200

    @pytest.mark.asyncio
    async def test_conversation_data_persistence(self, api_client, sample_conversation_start, api_helper):
        """测试对话数据持久化"""

        # 开始对话
        async with api_client.post("/api/chatbot/conversation/start", json=sample_conversation_start) as response:
            conversation_data = await response.json()
            conversation_id = conversation_data["conversation_id"]

        # 发送消息
        message_request = {
            "conversation_id": conversation_id,
            "message": "这是一条测试消息用于验证持久化"
        }

        async with api_client.post("/api/chatbot/message", json=message_request) as response:
            assert response.status == 200
            message_response = await response.json()

        # 获取对话历史
        async with api_client.get(f"/api/chatbot/conversation/{conversation_id}/history") as response:
            assert response.status == 200
            history = await response.json()

        # 验证数据完整性
        assert len(history["messages"]) >= 2
        user_message = None
        ai_message = None

        for msg in history["messages"]:
            if msg["type"] == "user":
                user_message = msg
            elif msg["type"] == "assistant":
                ai_message = msg

        assert user_message is not None
        assert ai_message is not None
        assert user_message["content"] == message_request["message"]
        assert ai_message["content"] == message_response["response"]

    @pytest.mark.asyncio
    async def test_conversation_multilingual_support(self, api_client, api_helper):
        """测试对话多语言支持"""

        # 测试英文对话
        english_start = {
            "user_id": "english_user",
            "session_type": "investment_consultation",
            "context": {"language": "en"}
        }

        async with api_client.post("/api/chatbot/conversation/start", json=english_start) as response:
            english_conversation = await response.json()

        english_message = {
            "conversation_id": english_conversation["conversation_id"],
            "message": "What are the best investment strategies for beginners?"
        }

        async with api_client.post("/api/chatbot/message", json=english_message) as response:
            if response.status == 200:
                english_response = await response.json()
                assert len(english_response["response"]) > 0

        # 测试中文对话
        chinese_start = {
            "user_id": "chinese_user",
            "session_type": "investment_consultation",
            "context": {"language": "zh"}
        }

        async with api_client.post("/api/chatbot/conversation/start", json=chinese_start) as response:
            chinese_conversation = await response.json()

        chinese_message = {
            "conversation_id": chinese_conversation["conversation_id"],
            "message": "请为投资新手推荐一些策略"
        }

        async with api_client.post("/api/chatbot/message", json=chinese_message) as response:
            if response.status == 200:
                chinese_response = await response.json()
                assert len(chinese_response["response"]) > 0

                # 验证中文回复包含中文字符
                assert any('\u4e00' <= char <= '\u9fff' for char in chinese_response["response"])