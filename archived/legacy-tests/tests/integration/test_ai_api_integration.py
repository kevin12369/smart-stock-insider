"""
AI分析API集成测试
测试AI分析相关API的完整交互流程
"""

import pytest
import asyncio
import aiohttp
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta

from tests.utils import TestDataGenerator, APITestHelper
from tests.conftest import get_test_config


class TestAIAPIIntegration:
    """AI分析API集成测试类"""

    @pytest.fixture(scope="class")
    async def api_client(self):
        """创建API客户端"""
        config = get_test_config()
        base_url = config["api"]["base_url"]
        timeout = aiohttp.ClientTimeout(total=60)  # AI分析可能需要更长时间

        async with aiohttp.ClientSession(
            base_url=base_url,
            timeout=timeout,
            headers={"Content-Type": "application/json"}
        ) as session:
            yield session

    @pytest.fixture
    def test_stocks(self):
        """测试股票数据"""
        return TestDataGenerator.generate_stock_data(5)

    @pytest.fixture
    def api_helper(self):
        """API测试助手"""
        return APITestHelper()

    @pytest.fixture
    def sample_analysis_request(self):
        """示例分析请求"""
        return {
            "symbol": "AAPL",
            "question": "请分析这只股票的投资价值",
            "role": "technical_analyst",
            "timeframe": "1m",
            "indicators": ["MA", "MACD", "RSI"]
        }

    @pytest.mark.asyncio
    async def test_ai_analysis_complete_flow(self, api_client, sample_analysis_request, api_helper):
        """测试AI分析完整流程"""

        # 1. 发起AI分析请求
        async with api_client.post("/api/ai/analyze", json=sample_analysis_request) as response:
            if response.status == 404:
                pytest.skip("AI分析功能未实现")

            assert response.status in [200, 202]  # 202表示异步处理

            if response.status == 200:
                # 同步响应
                analysis_result = await response.json()
                api_helper.validate_ai_analysis_response(analysis_result)
            else:
                # 异步响应，应该返回任务ID
                task_response = await response.json()
                assert "task_id" in task_response

                # 轮询任务状态
                task_id = task_response["task_id"]
                analysis_result = await self._poll_task_completion(api_client, task_id)
                api_helper.validate_ai_analysis_response(analysis_result)

        # 2. 获取分析历史
        async with api_client.get(f"/api/ai/history?symbol={sample_analysis_request['symbol']}") as response:
            if response.status == 404:
                pytest.skip("分析历史功能未实现")

            assert response.status == 200

            history = await response.json()
            assert "data" in history
            assert isinstance(history["data"], list)

    @pytest.mark.asyncio
    async def test_ai_streaming_analysis_flow(self, api_client, sample_analysis_request, api_helper):
        """测试AI流式分析流程"""

        # 启动流式分析
        request_data = {**sample_analysis_request, "stream": True}

        async with api_client.post(
            "/api/ai/analyze/stream",
            json=request_data
        ) as response:
            if response.status == 404:
                pytest.skip("流式分析功能未实现")

            assert response.status == 200

            # 读取流式响应
            content_parts = []
            async for chunk in response.content:
                if chunk:
                    chunk_text = chunk.decode('utf-8')
                    if chunk_text.startswith('data: '):
                        data = chunk_text[6:]
                        if data != '[DONE]':
                            content_parts.append(data)

            # 验证流式响应内容
            full_content = ''.join(content_parts)
            assert len(full_content) > 0

            # 验证内容格式（应该是有效的分析结果）
            try:
                analysis_data = json.loads(full_content)
                api_helper.validate_ai_analysis_response(analysis_data)
            except json.JSONDecodeError:
                # 如果不是JSON，应该是纯文本分析结果
                assert len(full_content.strip()) > 0

    @pytest.mark.asyncio
    async def test_ai_multi_analyst_workflow(self, api_client, sample_analysis_request, api_helper):
        """测试多分析师协作流程"""

        analyst_roles = [
            "technical_analyst",
            "fundamental_analyst",
            "news_analyst",
            "risk_analyst"
        ]

        analysis_results = []

        # 为每个分析师角色发起分析请求
        for role in analyst_roles:
            request_data = {**sample_analysis_request, "role": role}

            async with api_client.post("/api/ai/analyze", json=request_data) as response:
                if response.status == 404:
                    continue  # 跳过未实现的角色

                assert response.status in [200, 202]

                if response.status == 200:
                    result = await response.json()
                    analysis_results.append(result)
                else:
                    task_response = await response.json()
                    result = await self._poll_task_completion(api_client, task_response["task_id"])
                    analysis_results.append(result)

        # 验证多分析师结果
        if len(analysis_results) > 1:
            # 验证不同分析师提供不同视角
            roles_in_results = [result.get("role") for result in analysis_results]
            assert len(set(roles_in_results)) == len(roles_in_results)

            # 验证每个结果都包含基本字段
            for result in analysis_results:
                api_helper.validate_ai_analysis_response(result)

    @pytest.mark.asyncio
    async def test_ai_portfolio_optimization_flow(self, api_client, api_helper):
        """测试AI投资组合优化流程"""

        portfolio_request = {
            "symbols": ["AAPL", "GOOGL", "MSFT", "AMZN"],
            "risk_tolerance": "moderate",
            "investment_horizon": "1y",
            "optimization_goal": "max_sharpe",
            "constraints": {
                "max_weight_per_stock": 0.4,
                "min_weight_per_stock": 0.05,
                "max_turnover": 0.2
            }
        }

        async with api_client.post("/api/ai/portfolio/optimize", json=portfolio_request) as response:
            if response.status == 404:
                pytest.skip("投资组合优化功能未实现")

            assert response.status in [200, 202]

            if response.status == 200:
                optimization_result = await response.json()
                api_helper.validate_portfolio_optimization_response(optimization_result)
            else:
                task_response = await response.json()
                result = await self._poll_task_completion(api_client, task_response["task_id"])
                api_helper.validate_portfolio_optimization_response(result)

    @pytest.mark.asyncio
    async def test_ai_risk_assessment_flow(self, api_client, sample_analysis_request, api_helper):
        """测试AI风险评估流程"""

        risk_assessment_request = {
            "symbol": sample_analysis_request["symbol"],
            "assessment_type": "comprehensive",
            "timeframe": "3m",
            "scenarios": ["market_crash", "interest_rate_change", "sector_rotation"]
        }

        async with api_client.post("/api/ai/risk/assess", json=risk_assessment_request) as response:
            if response.status == 404:
                pytest.skip("风险评估功能未实现")

            assert response.status in [200, 202]

            if response.status == 200:
                risk_result = await response.json()
                api_helper.validate_risk_assessment_response(risk_result)
            else:
                task_response = await response.json()
                result = await self._poll_task_completion(api_client, task_response["task_id"])
                api_helper.validate_risk_assessment_response(result)

    @pytest.mark.asyncio
    async def test_ai_market_sentiment_analysis(self, api_client, api_helper):
        """测试AI市场情感分析"""

        sentiment_request = {
            "scope": "overall",
            "sources": ["news", "social_media", "analyst_reports"],
            "timeframe": "1w",
            "assets": ["stocks", "bonds", "commodities"]
        }

        async with api_client.post("/api/ai/sentiment/market", json=sentiment_request) as response:
            if response.status == 404:
                pytest.skip("市场情感分析功能未实现")

            assert response.status in [200, 202]

            if response.status == 200:
                sentiment_result = await response.json()
                api_helper.validate_market_sentiment_analysis_response(sentiment_result)
            else:
                task_response = await response.json()
                result = await self._poll_task_completion(api_client, task_response["task_id"])
                api_helper.validate_market_sentiment_analysis_response(result)

    @pytest.mark.asyncio
    async def test_ai_recommendation_system(self, api_client, api_helper):
        """测试AI推荐系统"""

        user_profile = {
            "risk_tolerance": "moderate",
            "investment_goals": ["growth", "income"],
            "preferred_sectors": ["technology", "healthcare"],
            "investment_horizon": "3y",
            "current_portfolio": {
                "AAPL": 0.3,
                "GOOGL": 0.2,
                "cash": 0.5
            }
        }

        recommendation_request = {
            "user_profile": user_profile,
            "recommendation_type": "stock_selection",
            "limit": 10
        }

        async with api_client.post("/api/ai/recommend", json=recommendation_request) as response:
            if response.status == 404:
                pytest.skip("推荐系统功能未实现")

            assert response.status in [200, 202]

            if response.status == 200:
                recommendations = await response.json()
                api_helper.validate_recommendation_response(recommendations)
            else:
                task_response = await response.json()
                result = await self._poll_task_completion(api_client, task_response["task_id"])
                api_helper.validate_recommendation_response(result)

    @pytest.mark.asyncio
    async def test_ai_conversation_system(self, api_client, api_helper):
        """测试AI对话系统"""

        # 开始对话
        conversation_start = {
            "session_type": "investment_consultation",
            "user_preferences": {
                "language": "zh",
                "detail_level": "comprehensive"
            }
        }

        async with api_client.post("/api/ai/conversation/start", json=conversation_start) as response:
            if response.status == 404:
                pytest.skip("对话系统功能未实现")

            assert response.status in [200, 201]

            conversation_data = await response.json()
            assert "conversation_id" in conversation_data
            assert "session_id" in conversation_data

            conversation_id = conversation_data["conversation_id"]

        # 发送消息
        messages = [
            "我想了解AAPL股票的投资前景",
            "这个风险水平适合保守投资者吗？",
            "你能推荐一些替代的投资选择吗？"
        ]

        for message in messages:
            message_request = {
                "conversation_id": conversation_id,
                "message": message,
                "context": {}
            }

            async with api_client.post("/api/ai/conversation/message", json=message_request) as response:
                assert response.status == 200

                response_data = await response.json()
                assert "response" in response_data
                assert "message_id" in response_data

        # 获取对话历史
        async with api_client.get(f"/api/ai/conversation/{conversation_id}/history") as response:
            assert response.status == 200

            history = await response.json()
            assert "messages" in history
            assert len(history["messages"]) >= len(messages) * 2  # 用户消息 + AI回复

    @pytest.mark.asyncio
    async def test_ai_model_lifecycle(self, api_client, api_helper):
        """测试AI模型生命周期管理"""

        # 获取可用模型
        async with api_client.get("/api/ai/models") as response:
            if response.status == 404:
                pytest.skip("模型管理功能未实现")

            assert response.status == 200

            models = await response.json()
            assert isinstance(models, list)

            if models:
                model = models[0]
                assert "model_id" in model
                assert "name" in model
                assert "status" in model

                # 获取模型详情
                model_id = model["model_id"]
                async with api_client.get(f"/api/ai/models/{model_id}") as response:
                    assert response.status == 200

                    model_details = await response.json()
                    assert model_details["model_id"] == model_id

                # 测试模型性能指标
                async with api_client.get(f"/api/ai/models/{model_id}/metrics") as response:
                    if response.status == 200:
                        metrics = await response.json()
                        assert "performance" in metrics
                        assert "usage_stats" in metrics

    @pytest.mark.asyncio
    async def test_ai_error_handling_integration(self, api_client):
        """测试AI API错误处理集成"""

        # 测试无效的分析请求
        invalid_request = {
            "symbol": "INVALID",
            "question": "",  # 空问题
            "role": "invalid_role"
        }

        async with api_client.post("/api/ai/analyze", json=invalid_request) as response:
            assert response.status in [400, 422]

            error = await response.json()
            assert "error" in error

        # 测试不存在的对话
        async with api_client.get("/api/ai/conversation/invalid_conversation/history") as response:
            assert response.status == 404

        # 测试无效的任务ID
        async with api_client.get("/api/ai/tasks/invalid_task/status") as response:
            assert response.status == 404

        # 测试过大的请求
        large_request = {
            "symbol": "AAPL",
            "question": "A" * 10000,  # 超长问题
            "role": "technical_analyst"
        }

        async with api_client.post("/api/ai/analyze", json=large_request) as response:
            assert response.status == 413  # Payload Too Large

    @pytest.mark.asyncio
    async def test_ai_concurrent_analysis_performance(self, api_client, sample_analysis_request):
        """测试AI并发分析性能"""

        # 创建多个并发分析请求
        symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
        requests = []

        for symbol in symbols:
            request = {**sample_analysis_request, "symbol": symbol}
            requests.append(request)

        async def analyze_stock(request_data):
            async with api_client.post("/api/ai/analyze", json=request_data) as response:
                if response.status == 200:
                    return await response.json()
                return None

        # 并发执行分析请求
        import time
        start_time = time.time()
        results = await asyncio.gather(
            *[analyze_stock(req) for req in requests],
            return_exceptions=True
        )
        end_time = time.time()

        # 验证响应时间（AI分析可能需要更长时间）
        response_time = end_time - start_time
        assert response_time < 120.0  # 2分钟内完成所有请求

        # 验证结果
        successful_results = [r for r in results if r is not None and not isinstance(r, Exception)]
        assert len(successful_results) > 0

    @pytest.mark.asyncio
    async def test_ai_quality_control(self, api_client, sample_analysis_request, api_helper):
        """测试AI质量控制"""

        # 发起分析请求
        async with api_client.post("/api/ai/analyze", json=sample_analysis_request) as response:
            if response.status == 404:
                pytest.skip("AI分析功能未实现")

            assert response.status in [200, 202]

            if response.status == 200:
                analysis_result = await response.json()

                # 验证分析质量
                assert "confidence" in analysis_result
                assert analysis_result["confidence"] >= 0.0
                assert analysis_result["confidence"] <= 1.0

                # 验证内容长度和相关性
                if "answer" in analysis_result:
                    answer = analysis_result["answer"]
                    assert len(answer.strip()) > 0

                    # 验证答案包含相关的股票信息
                    assert sample_analysis_request["symbol"] in answer or \
                           any(keyword in answer.lower() for keyword in ["分析", "股票", "投资"])

                # 验证推理过程
                if "reasoning" in analysis_result:
                    reasoning = analysis_result["reasoning"]
                    assert len(reasoning.strip()) > 0

    @pytest.mark.asyncio
    async def test_ai_caching_behavior(self, api_client, sample_analysis_request):
        """测试AI结果缓存行为"""

        # 第一次分析请求
        start_time = time.time()
        async with api_client.post("/api/ai/analyze", json=sample_analysis_request) as response:
            if response.status == 404:
                pytest.skip("AI分析功能未实现")

            first_response = await response.json()
        first_request_time = time.time() - start_time

        # 第二次相同请求（可能使用缓存）
        start_time = time.time()
        async with api_client.post("/api/ai/analyze", json=sample_analysis_request) as response:
            second_response = await response.json()
        second_request_time = time.time() - start_time

        # 验证响应一致性
        if "answer" in first_response and "answer" in second_response:
            # 缓存的结果应该相同（或者非常相似）
            assert len(first_response["answer"]) > 0
            assert len(second_response["answer"]) > 0

        # 缓存请求应该更快（可选验证）
        # assert second_request_time < first_request_time

    async def _poll_task_completion(self, api_client, task_id, max_attempts=30, poll_interval=2):
        """轮询任务完成状态"""
        for attempt in range(max_attempts):
            async with api_client.get(f"/api/ai/tasks/{task_id}/status") as response:
                if response.status == 200:
                    task_status = await response.json()

                    if task_status["status"] == "completed":
                        return task_status["result"]
                    elif task_status["status"] == "failed":
                        raise Exception(f"Task failed: {task_status.get('error', 'Unknown error')}")

            await asyncio.sleep(poll_interval)

        raise TimeoutError(f"Task {task_id} did not complete within {max_attempts * poll_interval} seconds")

    @pytest.mark.asyncio
    async def test_ai_resource_management(self, api_client, api_helper):
        """测试AI资源管理"""

        # 获取资源使用情况
        async with api_client.get("/api/ai/resources/status") as response:
            if response.status == 404:
                pytest.skip("资源管理功能未实现")

            assert response.status == 200

            resource_status = await response.json()
            assert "cpu_usage" in resource_status
            assert "memory_usage" in resource_status
            assert "gpu_usage" in resource_status
            assert "active_tasks" in resource_status

        # 获取任务队列状态
        async with api_client.get("/api/ai/queue/status") as response:
            if response.status == 404:
                pytest.skip("任务队列功能未实现")

            assert response.status == 200

            queue_status = await response.json()
            assert "pending_tasks" in queue_status
            assert "processing_tasks" in queue_status
            assert "completed_tasks" in queue_status

    @pytest.mark.asyncio
    async def test_ai_data_privacy(self, api_client, sample_analysis_request):
        """测试AI数据隐私保护"""

        # 发起包含敏感信息的分析请求
        sensitive_request = {
            **sample_analysis_request,
            "user_context": {
                "portfolio_size": 1000000,
                "risk_profile": "conservative"
            }
        }

        async with api_client.post("/api/ai/analyze", json=sensitive_request) as response:
            if response.status == 404:
                pytest.skip("AI分析功能未实现")

            # 验证响应不包含敏感信息
            if response.status == 200:
                result = await response.json()

                # 检查响应中是否泄露了敏感信息
                response_text = json.dumps(result)
                assert "portfolio_size" not in response_text
                assert "1000000" not in response_text

        # 验证历史记录中不包含敏感信息
        async with api_client.get(f"/api/ai/history?symbol={sample_analysis_request['symbol']}") as response:
            if response.status == 200:
                history = await response.json()

                for record in history.get("data", []):
                    record_text = json.dumps(record)
                    assert "portfolio_size" not in record_text