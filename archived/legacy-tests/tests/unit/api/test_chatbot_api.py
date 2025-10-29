"""
ChatBot API单元测试
"""

import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# 创建FastAPI应用
from fastapi import FastAPI
from backend.api.chatbot import router as chatbot_router

app = FastAPI()
app.include_router(chatbot_router)

client = TestClient(app)

@pytest.fixture
def mock_chatbot_service():
    """模拟ChatBot服务"""
    with patch('backend.api.chatbot.chatbot_service') as mock_service:
        mock_service.start_conversation = AsyncMock(return_value={
            "session_id": "test_session_001",
            "response": "您好！我是您的智能投资助手，有什么可以帮助您的吗？",
            "suggestions": ["什么是市盈率？", "帮我分析股票", "今日市场行情"]
        })

        mock_service.process_message = AsyncMock(return_value={
            "session_id": "test_session_001",
            "response": "市盈率是股票价格与每股收益的比率...",
            "intent": "knowledge_query",
            "confidence": 0.9,
            "suggestions": ["市净率是什么？", "如何计算市盈率？"],
            "context": {"previous_topic": "市盈率"}
        })

        mock_service.get_conversation_history = AsyncMock(return_value=[
            {
                "role": "user",
                "content": "什么是市盈率？",
                "timestamp": "2023-10-29T10:00:00Z"
            },
            {
                "role": "assistant",
                "content": "市盈率是股票价格与每股收益的比率...",
                "timestamp": "2023-10-29T10:00:05Z"
            }
        ])

        mock_service.clear_conversation = AsyncMock(return_value={
            "success": True,
            "message": "对话历史已清除"
        })

        mock_service.end_conversation = AsyncMock(return_value={
            "success": True,
            "message": "对话已结束"
        })

        mock_service.get_user_suggestions = AsyncMock(return_value=[
            "查看股票详情",
            "分析投资组合",
            "了解市场动态"
        ])

        mock_service.get_user_stats = AsyncMock(return_value={
            "total_actions": 25,
            "recent_actions": 5,
            "total_sessions": 3,
            "avg_session_duration": 120.5,
            "satisfaction_score": 0.85,
            "most_active_hour": 14,
            "favorite_category": "股票查询",
            "interaction_style": "formal"
        })

        mock_service.get_service_stats = AsyncMock(return_value={
            "total_conversations": 1000,
            "active_sessions": 50,
            "avg_response_time": 1.2,
            "user_satisfaction": 0.82
        })

        yield mock_service

@pytest.fixture
def sample_conversation_start():
    """示例对话开始请求"""
    return {
        "user_id": "test_user_001"
    }

@pytest.fixture
def sample_chat_message():
    """示例聊天消息"""
    return {
        "message": "什么是市盈率？",
        "user_id": "test_user_001",
        "session_id": "test_session_001",
        "context": {"previous_topic": "基础概念"}
    }

@pytest.fixture
def sample_feedback():
    """示例反馈数据"""
    return {
        "rating": 5,
        "comments": "回答很有帮助，谢谢！",
        "suggestions": "希望增加更多例子"
    }

class TestChatBotAPI:
    """ChatBot API测试类"""

    def test_start_conversation_success(self, mock_chatbot_service, sample_conversation_start):
        """测试成功开始对话"""
        response = client.post("/api/chatbot/conversation/start", json=sample_conversation_start)

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "message" in data

        # 验证服务调用
        mock_chatbot_service.start_conversation.assert_called_once_with("test_user_001")

    def test_start_conversation_invalid_request(self):
        """测试无效的对话开始请求"""
        # 缺少必需字段
        invalid_request = {"invalid_field": "value"}

        response = client.post("/api/chatbot/conversation/start", json=invalid_request)

        assert response.status_code == 422  # Validation error

    def test_start_conversation_empty_user_id(self):
        """测试空用户ID"""
        invalid_request = {"user_id": ""}

        response = client.post("/api/chatbot/conversation/start", json=invalid_request)

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_chat_message_success(self, mock_chatbot_service, sample_chat_message):
        """测试成功发送聊天消息"""
        response = client.post("/api/chatbot/conversation/chat", json=sample_chat_message)

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "response" in data
        assert "intent" in data
        assert "confidence" in data
        assert "suggestions" in data
        assert "timestamp" in data

        # 验证响应内容
        assert data["session_id"] == "test_session_001"
        assert data["response"] == "市盈率是股票价格与每股收益的比率..."
        assert data["intent"] == "knowledge_query"
        assert data["confidence"] == 0.9

        # 验证服务调用
        mock_chatbot_service.process_message.assert_called_once()

    def test_chat_message_invalid_request(self):
        """测试无效的聊天消息请求"""
        invalid_request = {"invalid_field": "value"}

        response = client.post("/api/chatbot/conversation/chat", json=invalid_request)

        assert response.status_code == 422

    def test_chat_message_missing_required_fields(self):
        """测试缺少必需字段的聊天消息"""
        # 缺少message字段
        incomplete_request = {
            "user_id": "test_user_001",
            "session_id": "test_session_001"
        }

        response = client.post("/api/chatbot/conversation/chat", json=incomplete_request)

        assert response.status_code == 422

    def test_chat_message_too_long_message(self):
        """测试消息过长"""
        long_message_request = {
            "message": "x" * 1001,  # 超过1000字符限制
            "user_id": "test_user_001",
            "session_id": "test_session_001"
        }

        response = client.post("/api/chatbot/conversation/chat", json=long_message_request)

        assert response.status_code == 422

    def test_get_conversation_history_success(self, mock_chatbot_service):
        """测试成功获取对话历史"""
        session_id = "test_session_001"
        limit = 10

        response = client.get(f"/api/chatbot/conversation/{session_id}/history?limit={limit}")

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "messages" in data
        assert "total_count" in data

        assert data["session_id"] == session_id
        assert len(data["messages"]) == 2
        assert data["total_count"] == 2

        # 验证服务调用
        mock_chatbot_service.get_conversation_history.assert_called_once_with(
            session_id=session_id,
            limit=10
        )

    def test_get_conversation_history_invalid_limit(self, mock_chatbot_service):
        """测试无效的限制参数"""
        session_id = "test_session_001"
        invalid_limit = 100  # 超过最大限制50

        response = client.get(f"/api/chatbot/conversation/{session_id}/history?limit={invalid_limit}")

        assert response.status_code == 200
        # 应该使用最大限制50
        mock_chatbot_service.get_conversation_history.assert_called_once_with(
            session_id=session_id,
            limit=50
        )

    def test_get_conversation_history_not_found(self, mock_chatbot_service):
        """测试获取不存在的对话历史"""
        mock_chatbot_service.get_conversation_history.return_value = []

        session_id = "non_existent_session"

        response = client.get(f"/api/chatbot/conversation/{session_id}/history")

        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == 0
        assert data["total_count"] == 0

    def test_clear_conversation_success(self, mock_chatbot_service):
        """测试成功清除对话"""
        session_id = "test_session_001"

        response = client.delete(f"/api/chatbot/conversation/{session_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data

        # 验证服务调用
        mock_chatbot_service.clear_conversation.assert_called_once_with(session_id)

    def test_clear_conversation_not_found(self, mock_chatbot_service):
        """测试清除不存在的对话"""
        mock_chatbot_service.clear_conversation.return_value = {
            "success": False,
            "message": "对话不存在"
        }

        session_id = "non_existent_session"

        response = client.delete(f"/api/chatbot/conversation/{session_id}")

        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "对话不存在"

    def test_end_conversation_success(self, mock_chatbot_service, sample_feedback):
        """测试成功结束对话"""
        session_id = "test_session_001"

        response = client.post(
            f"/api/chatbot/conversation/{session_id}/end",
            json=sample_feedback
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "message" in data

        # 验证服务调用
        mock_chatbot_service.end_conversation.assert_called_once()

    def test_end_conversation_without_feedback(self, mock_chatbot_service):
        """测试不提供反馈结束对话"""
        session_id = "test_session_001"

        response = client.post(f"/api/chatbot/conversation/{session_id}/end")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

        # 验证服务调用
        mock_chatbot_service.end_conversation.assert_called_once()

    def test_analyze_intent_success(self):
        """测试成功分析意图"""
        # 注意：这个测试需要模拟intent_classifier
        with patch('backend.api.chatbot.intent_classifier') as mock_classifier:
            mock_classifier.classify = AsyncMock(return_value=Mock(
                intent=Mock(value="knowledge_query"),
                confidence=0.85,
                entities={"concept": "市盈率"},
                keywords=["市盈率", "估值"],
                processing_time=0.15
            ))

            request_data = {
                "text": "什么是市盈率？",
                "context": {"domain": "finance"}
            }

            response = client.post("/api/chatbot/intent/analyze", json=request_data)

            assert response.status_code == 200
            data = response.json()
            assert "intent" in data
            assert "confidence" in data
            assert "entities" in data
            assert "keywords" in data
            assert "processing_time" in data

            assert data["intent"] == "knowledge_query"
            assert data["confidence"] == 0.85

    def test_search_knowledge_success(self):
        """测试成功搜索知识库"""
        with patch('backend.api.chatbot.knowledge_base') as mock_kb:
            mock_search_result = Mock()
            mock_search_result.item = Mock(
                id="kb_001",
                title="市盈率定义",
                content="市盈率是...",
                category="基础概念",
                tags=["估值", "财务"],
                confidence=0.9
            )
            mock_search_result.relevance = 0.85
            mock_search_result.explanation = "标题匹配"

            mock_kb.search = AsyncMock(return_value=[mock_search_result])

            request_data = {
                "query": "市盈率",
                "limit": 5,
                "category": "基础概念"
            }

            response = client.post("/api/chatbot/knowledge/search", json=request_data)

            assert response.status_code == 200
            data = response.json()
            assert "query" in data
            assert "results" in data
            assert "total_count" in data
            assert "search_time" in data

            assert len(data["results"]) == 1
            assert data["results"][0]["title"] == "市盈率定义"

    def test_get_user_suggestions_success(self, mock_chatbot_service):
        """测试成功获取用户建议"""
        user_id = "test_user_001"
        intent = "stock_analysis"

        response = client.get(f"/api/chatbot/user/{user_id}/suggestions?intent={intent}")

        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "suggestions" in data
        assert "intent" in data

        assert data["user_id"] == user_id
        assert data["intent"] == intent
        assert len(data["suggestions"]) == 3

        # 验证服务调用
        mock_chatbot_service.get_user_suggestions.assert_called_once_with(
            user_id=user_id,
            intent=intent
        )

    def test_get_user_statistics_success(self, mock_chatbot_service):
        """测试成功获取用户统计"""
        user_id = "test_user_001"

        response = client.get(f"/api/chatbot/user/{user_id}/stats")

        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "total_actions" in data
        assert "recent_actions" in data
        assert "total_sessions" in data
        assert "avg_session_duration" in data
        assert "satisfaction_score" in data
        assert "most_active_hour" in data
        assert "favorite_category" in data
        assert "interaction_style" in data

        assert data["user_id"] == user_id
        assert data["total_actions"] == 25
        assert data["satisfaction_score"] == 0.85

        # 验证服务调用
        mock_chatbot_service.get_user_stats.assert_called_once_with(user_id)

    def test_get_service_statistics_success(self, mock_chatbot_service):
        """测试成功获取服务统计"""
        with patch('backend.api.chatbot.knowledge_base') as mock_kb:
            mock_kb.get_statistics.return_value = {
                "total_items": 1000,
                "categories": ["股票", "基金", "技术分析"],
                "total_categories": 3
            }

            response = client.get("/api/chatbot/service/stats")

            assert response.status_code == 200
            data = response.json()
            assert "service_stats" in data
            assert "knowledge_base_stats" in data
            assert "timestamp" in data

            # 验证服务统计
            assert data["service_stats"]["total_conversations"] == 1000
            assert data["service_stats"]["active_sessions"] == 50

            # 验证知识库统计
            assert data["knowledge_base_stats"]["total_items"] == 1000

    def test_health_check_success(self, mock_chatbot_service):
        """测试健康检查成功"""
        response = client.get("/api/chatbot/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "components" in data

        assert data["status"] == "healthy"
        assert "chatbot_service" in data["components"]
        assert "intent_classifier" in data["components"]
        assert "knowledge_base" in data["components"]
        assert "user_profiler" in data["components"]

    def test_health_check_service_error(self, mock_chatbot_service):
        """测试健康检查服务错误"""
        # 模拟服务异常
        mock_chatbot_service.get_service_stats.side_effect = Exception("Service error")

        response = client.get("/api/chatbot/health")

        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert "timestamp" in data
        assert "error" in data

    def test_error_handling_500(self):
        """测试500错误处理"""
        with patch('backend.api.chatbot.chatbot_service') as mock_service:
            # 模拟服务抛出异常
            mock_service.start_conversation.side_effect = Exception("Internal error")

            response = client.post("/api/chatbot/conversation/start", json={"user_id": "test_user"})

            assert response.status_code == 500
            data = response.json()
            assert data["success"] is False
            assert data["error"] == "内部服务器错误"
            assert data["status_code"] == 500

    def test_cors_headers(self):
        """测试CORS头"""
        response = client.options("/api/chatbot/conversation/start")
        # 注意：实际测试中需要配置CORS中间件

    def test_rate_limiting(self):
        """测试速率限制"""
        # 发送大量请求
        responses = []
        for i in range(10):
            response = client.post("/api/chatbot/conversation/start", json={"user_id": f"user_{i}"})
            responses.append(response)

        # 注意：实际测试中需要配置速率限制中间件
        assert all(response.status_code in [200, 201, 429] for response in responses)

    def test_request_validation(self):
        """测试请求验证"""
        # 测试各种无效请求
        invalid_requests = [
            {},  # 空请求
            {"user_id": None},  # null值
            {"user_id": 123},  # 错误类型
            {"user_id": "x" * 300}  # 过长字符串
        ]

        for invalid_request in invalid_requests:
            response = client.post("/api/chatbot/conversation/start", json=invalid_request)
            assert response.status_code == 422

    def test_response_format(self, mock_chatbot_service):
        """测试响应格式"""
        # 开始对话
        response = client.post("/api/chatbot/conversation/start", json={"user_id": "test_user"})
        assert response.status_code == 201

        # 验证响应是JSON格式
        try:
            data = response.json()
            assert isinstance(data, dict)
        except ValueError:
            pytest.fail("响应不是有效的JSON格式")

        # 验证响应头
        assert "application/json" in response.headers.get("content-type", "")

    def test_concurrent_requests(self, mock_chatbot_service):
        """测试并发请求"""
        import threading
        import time

        results = []
        errors = []

        def make_request(user_id):
            try:
                response = client.post("/api/chatbot/conversation/start", json={"user_id": user_id})
                results.append(response.status_code)
            except Exception as e:
                errors.append(str(e))

        # 创建多个并发线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request, args=(f"user_{i}",))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证结果
        assert len(errors) == 0, f"并发请求出现错误: {errors}"
        assert len(results) == 5
        assert all(status in [200, 201] for status in results)

@pytest.mark.unit
@pytest.mark.api
@pytest.mark.chatbot
class TestChatBotAPIIntegration:
    """ChatBot API集成测试"""

    def test_complete_conversation_flow(self, mock_chatbot_service):
        """测试完整对话流程"""
        user_id = "integration_test_user"

        # 1. 开始对话
        start_response = client.post("/api/chatbot/conversation/start", json={"user_id": user_id})
        assert start_response.status_code == 201
        start_data = start_response.json()
        session_id = "test_session_001"  # 模拟返回的session_id

        # 2. 发送消息
        chat_response = client.post("/api/chatbot/conversation/chat", json={
            "message": "什么是市盈率？",
            "user_id": user_id,
            "session_id": session_id
        })
        assert chat_response.status_code == 200

        # 3. 获取对话历史
        history_response = client.get(f"/api/chatbot/conversation/{session_id}/history")
        assert history_response.status_code == 200
        history_data = history_response.json()
        assert len(history_data["messages"]) >= 1

        # 4. 结束对话
        end_response = client.post(f"/api/chatbot/conversation/{session_id}/end", json={
            "rating": 5,
            "comments": "很满意"
        })
        assert end_response.status_code == 200

    def test_error_recovery_flow(self, mock_chatbot_service):
        """测试错误恢复流程"""
        # 模拟服务错误
        mock_chatbot_service.process_message.side_effect = Exception("Service unavailable")

        user_id = "error_test_user"
        session_id = "error_session_001"

        # 发送消息应该返回错误
        response = client.post("/api/chatbot/conversation/chat", json={
            "message": "测试消息",
            "user_id": user_id,
            "session_id": session_id
        })

        assert response.status_code == 500
        error_data = response.json()
        assert "error" in error_data

        # 恢复服务后应该能正常工作
        mock_chatbot_service.process_message.side_effect = None
        mock_chatbot_service.process_message.return_value = {
            "session_id": session_id,
            "response": "恢复正常服务",
            "intent": "recovery",
            "confidence": 1.0,
            "suggestions": []
        }

        recovery_response = client.post("/api/chatbot/conversation/chat", json={
            "message": "恢复测试",
            "user_id": user_id,
            "session_id": session_id
        })

        assert recovery_response.status_code == 200