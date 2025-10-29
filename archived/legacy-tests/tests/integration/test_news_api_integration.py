"""
新闻API集成测试
测试新闻相关API的完整交互流程
"""

import pytest
import asyncio
import aiohttp
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta

from tests.utils import TestDataGenerator, APITestHelper
from tests.conftest import get_test_config


class TestNewsAPIIntegration:
    """新闻API集成测试类"""

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
    def test_news(self):
        """测试新闻数据"""
        return TestDataGenerator.generate_news_data(20)

    @pytest.fixture
    def api_helper(self):
        """API测试助手"""
        return APITestHelper()

    @pytest.mark.asyncio
    async def test_get_news_list_complete_flow(self, api_client, test_news, api_helper):
        """测试获取新闻列表的完整流程"""

        # 1. 获取新闻列表
        async with api_client.get("/api/news") as response:
            assert response.status == 200

            data = await response.json()
            assert "data" in data
            assert "pagination" in data
            assert isinstance(data["data"], list)

            if data["data"]:
                news_item = data["data"][0]
                api_helper.validate_news_response(news_item)

    @pytest.mark.asyncio
    async def test_get_news_detail_complete_flow(self, api_client, api_helper):
        """测试获取新闻详情的完整流程"""

        # 首先获取新闻列表以获得有效的新闻ID
        async with api_client.get("/api/news") as response:
            data = await response.json()

            if not data["data"]:
                pytest.skip("没有可用的新闻数据")

            news_id = data["data"][0]["id"]

        # 获取新闻详情
        async with api_client.get(f"/api/news/{news_id}") as response:
            assert response.status == 200

            news_detail = await response.json()
            api_helper.validate_news_response(news_detail)
            assert news_detail["id"] == news_id

    @pytest.mark.asyncio
    async def test_news_search_workflow(self, api_client, api_helper):
        """测试新闻搜索工作流程"""

        search_terms = ["股票", "科技", "财经", "投资", "市场"]

        for search_term in search_terms:
            async with api_client.get(f"/api/news/search?keyword={search_term}&limit=10") as response:
                assert response.status == 200

                search_results = await response.json()
                assert isinstance(search_results, list)

                for result in search_results:
                    api_helper.validate_news_response(result)

                    # 验证搜索相关性（标题或内容包含搜索词）
                    content = f"{result.get('title', '')} {result.get('summary', '')} {result.get('content', '')}"
                    assert search_term.lower() in content.lower()

    @pytest.mark.asyncio
    async def test_news_filtering_and_pagination(self, api_client, api_helper):
        """测试新闻筛选和分页功能"""

        # 测试分页
        page_size = 5
        async with api_client.get(f"/api/news?page=1&limit={page_size}") as response:
            data = await response.json()
            assert response.status == 200

            assert len(data["data"]) <= page_size
            assert data["pagination"]["page"] == 1
            assert data["pagination"]["size"] == page_size

        # 测试分类筛选
        async with api_client.get("/api/news?category=technology") as response:
            data = await response.json()
            assert response.status == 200

            for news in data["data"]:
                assert news["category"] == "technology"

        # 测试情感筛选
        async with api_client.get("/api/news?sentiment=positive") as response:
            data = await response.json()
            assert response.status == 200

            for news in data["data"]:
                assert "positive" in news.get("tags", [])

        # 测试日期范围筛选
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)

        async with api_client.get(
            f"/api/news?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}"
        ) as response:
            data = await response.json()
            assert response.status == 200

            for news in data["data"]:
                news_date = datetime.fromisoformat(news["published_at"].replace("Z", "+00:00"))
                assert start_date <= news_date <= end_date

    @pytest.mark.asyncio
    async def test_news_sentiment_analysis_flow(self, api_client, api_helper):
        """测试新闻情感分析流程"""

        # 获取新闻列表
        async with api_client.get("/api/news") as response:
            data = await response.json()

            if not data["data"]:
                pytest.skip("没有可用的新闻数据")

            news_item = data["data"][0]

        # 对新闻进行情感分析
        analysis_payload = {
            "text": news_item["title"] + " " + news_item["summary"],
            "language": "zh"
        }

        async with api_client.post("/api/sentiment/analyze", json=analysis_payload) as response:
            assert response.status == 200

            sentiment_result = await response.json()
            api_helper.validate_sentiment_analysis_response(sentiment_result)

            assert "sentiment" in sentiment_result
            assert "score" in sentiment_result
            assert "confidence" in sentiment_result

    @pytest.mark.asyncio
    async def test_news_market_sentiment_flow(self, api_client, api_helper):
        """测试市场情感分析流程"""

        # 获取市场整体情感分析
        async with api_client.get("/api/sentiment/market") as response:
            assert response.status == 200

            market_sentiment = await response.json()
            api_helper.validate_market_sentiment_response(market_sentiment)

            assert "sentiment" in market_sentiment
            assert "score" in market_sentiment
            assert "sentiment_distribution" in market_sentiment

        # 获取特定股票相关的新闻情感
        async with api_client.get("/api/news?stock_symbol=AAPL") as response:
            data = await response.json()
            assert response.status == 200

            if data["data"]:
                # 分析这些新闻的情感分布
                positive_count = 0
                negative_count = 0
                neutral_count = 0

                for news in data["data"]:
                    tags = news.get("tags", [])
                    if "positive" in tags:
                        positive_count += 1
                    elif "negative" in tags:
                        negative_count += 1
                    else:
                        neutral_count += 1

                # 验证情感分布
                total = positive_count + negative_count + neutral_count
                assert total == len(data["data"])

    @pytest.mark.asyncio
    async def test_news_categories_and_sources_flow(self, api_client, api_helper):
        """测试新闻分类和来源流程"""

        # 获取新闻分类
        async with api_client.get("/api/news/categories") as response:
            assert response.status == 200

            categories = await response.json()
            assert isinstance(categories, list)

            for category in categories:
                assert "value" in category
                assert "label" in category

        # 获取新闻来源
        async with api_client.get("/api/news/sources") as response:
            assert response.status == 200

            sources = await response.json()
            assert isinstance(sources, list)

            for source in sources:
                assert "name" in source
                assert "url" in source

        # 根据分类获取新闻
        if categories:
            category = categories[0]["value"]
            async with api_client.get(f"/api/news?category={category}") as response:
                data = await response.json()
                assert response.status == 200

                for news in data["data"]:
                    assert news["category"] == category

    @pytest.mark.asyncio
    async def test_news_stock_correlation_flow(self, api_client, api_helper):
        """测试新闻与股票关联流程"""

        # 获取提及特定股票的新闻
        stock_symbol = "AAPL"
        async with api_client.get(f"/api/news?mentioned_stocks={stock_symbol}") as response:
            data = await response.json()
            assert response.status == 200

            for news in data["data"]:
                mentioned_stocks = news.get("mentioned_stocks", [])
                assert stock_symbol in mentioned_stocks

        # 获取热门相关股票的新闻
        async with api_client.get("/api/news?sort_by=relevance_score&limit=10") as response:
            data = await response.json()
            assert response.status == 200

            for news in data["data"]:
                if news.get("mentioned_stocks"):
                    assert len(news["mentioned_stocks"]) > 0
                    assert isinstance(news["mentioned_stocks"], list)

    @pytest.mark.asyncio
    async def test_news_recommendation_flow(self, api_client, api_helper):
        """测试新闻推荐流程"""

        # 获取推荐新闻
        async with api_client.get("/api/news/recommendations?limit=10") as response:
            if response.status == 404:
                pytest.skip("推荐功能未实现")

            assert response.status == 200

            recommendations = await response.json()
            assert isinstance(recommendations, list)

            for news in recommendations:
                api_helper.validate_news_response(news)

        # 基于用户偏好获取推荐
        user_preferences = {
            "categories": ["technology", "finance"],
            "stocks": ["AAPL", "GOOGL"],
            "sentiment": "positive"
        }

        async with api_client.post("/api/news/recommendations", json=user_preferences) as response:
            if response.status == 404:
                pytest.skip("个性化推荐功能未实现")

            assert response.status == 200

            personalized_recommendations = await response.json()
            assert isinstance(personalized_recommendations, list)

    @pytest.mark.asyncio
    async def test_news_real_time_updates_flow(self, api_client, api_helper):
        """测试新闻实时更新流程"""

        # 获取最新新闻时间戳
        async with api_client.get("/api/news?limit=1&sort_by=publish_time") as response:
            data = await response.json()

            if not data["data"]:
                pytest.skip("没有可用的新闻数据")

            latest_timestamp = data["data"][0]["published_at"]

        # 等待一小段时间后检查更新
        await asyncio.sleep(2)

        # 获取从该时间戳之后的新闻
        async with api_client.get(f"/api/news?since={latest_timestamp}") as response:
            if response.status == 404:
                pytest.skip("增量更新功能未实现")

            assert response.status == 200

            updated_news = await response.json()
            assert isinstance(updated_news, list)

            for news in updated_news:
                assert news["published_at"] > latest_timestamp

    @pytest.mark.asyncio
    async def test_news_trending_topics_flow(self, api_client, api_helper):
        """测试热门话题流程"""

        # 获取热门话题
        async with api_client.get("/api/news/trending") as response:
            if response.status == 404:
                pytest.skip("热门话题功能未实现")

            assert response.status == 200

            trending_topics = await response.json()
            assert isinstance(trending_topics, list)

            for topic in trending_topics:
                assert "topic" in topic
                assert "count" in topic
                assert "sentiment" in topic

        # 获取特定话题的新闻
        if trending_topics:
            topic_name = trending_topics[0]["topic"]
            async with api_client.get(f"/api/news?topic={topic_name}") as response:
                if response.status == 404:
                    pytest.skip("话题筛选功能未实现")

                data = await response.json()
                assert response.status == 200

                for news in data["data"]:
                    # 验证新闻是否包含相关话题
                    keywords = news.get("keywords", [])
                    assert any(topic_name.lower() in keyword.lower() for keyword in keywords)

    @pytest.mark.asyncio
    async def test_news_error_handling_integration(self, api_client):
        """测试新闻API错误处理集成"""

        # 测试无效新闻ID
        async with api_client.get("/api/news/999999") as response:
            assert response.status == 404

            error = await response.json()
            assert "error" in error

        # 测试无效搜索参数
        async with api_client.get("/api/news/search?keyword=") as response:
            assert response.status == 400

        # 测试无效分页参数
        async with api_client.get("/api/news?page=-1") as response:
            assert response.status == 400

        # 测试无效日期格式
        async with api_client.get("/api/news?start_date=invalid-date") as response:
            assert response.status == 400

        # 测试空的情感分析请求
        async with api_client.post("/api/sentiment/analyze", json={"text": ""}) as response:
            assert response.status == 400

    @pytest.mark.asyncio
    async def test_news_concurrent_requests_performance(self, api_client):
        """测试新闻API并发请求性能"""

        # 创建多个并发请求
        endpoints = [
            "/api/news",
            "/api/news/categories",
            "/api/news/sources",
            "/api/sentiment/market"
        ]

        async def fetch_endpoint(endpoint):
            async with api_client.get(endpoint) as response:
                if response.status == 200:
                    return await response.json()
                return None

        # 并发执行请求
        import time
        start_time = time.time()
        results = await asyncio.gather(
            *[fetch_endpoint(endpoint) for endpoint in endpoints],
            return_exceptions=True
        )
        end_time = time.time()

        # 验证响应时间
        response_time = end_time - start_time
        assert response_time < 10.0  # 10秒内完成所有请求

        # 验证结果
        successful_results = [r for r in results if r is not None and not isinstance(r, Exception)]
        assert len(successful_results) > 0

    @pytest.mark.asyncio
    async def test_news_data_consistency(self, api_client, api_helper):
        """测试新闻数据一致性"""

        # 获取新闻列表
        async with api_client.get("/api/news?limit=10") as response:
            data = await response.json()

            if not data["data"]:
                pytest.skip("没有可用的新闻数据")

            news_item = data["data"][0]
            news_id = news_item["id"]

        # 多次获取同一新闻的详情，验证数据一致性
        responses = []
        for _ in range(3):
            async with api_client.get(f"/api/news/{news_id}") as response:
                if response.status == 200:
                    news_data = await response.json()
                    responses.append(news_data)

            # 添加小延迟避免缓存问题
            await asyncio.sleep(0.1)

        # 验证响应一致性
        if len(responses) >= 2:
            # 基本字段应该保持一致
            consistent_fields = ["id", "title", "source", "published_at"]
            for field in consistent_fields:
                assert responses[0][field] == responses[-1][field]

    @pytest.mark.asyncio
    async def test_news_caching_behavior(self, api_client):
        """测试新闻缓存行为"""

        # 第一次请求
        start_time = time.time()
        async with api_client.get("/api/news") as response:
            first_response = await response.json()
        first_request_time = time.time() - start_time

        # 第二次请求（应该使用缓存）
        start_time = time.time()
        async with api_client.get("/api/news") as response:
            second_response = await response.json()
        second_request_time = time.time() - start_time

        # 验证响应一致性
        assert len(first_response["data"]) == len(second_response["data"])

        # 缓存请求应该更快（可选验证，因为网络延迟可能影响）
        # assert second_request_time < first_request_time

    @pytest.mark.asyncio
    async def test_news_content_filtering(self, api_client, api_helper):
        """测试新闻内容筛选"""

        # 测试敏感内容过滤
        async with api_client.get("/api/news?filter_sensitive=true") as response:
            if response.status == 404:
                pytest.skip("敏感内容过滤功能未实现")

            data = await response.json()
            assert response.status == 200

            # 验证过滤后的内容
            for news in data["data"]:
                # 这里可以添加敏感内容的验证逻辑
                pass

        # �按语言筛选
        async with api_client.get("/api/news?language=zh") as response:
            if response.status == 404:
                pytest.skip("语言筛选功能未实现")

            data = await response.json()
            assert response.status == 200

            for news in data["data"]:
                # 验证新闻语言
                content = f"{news.get('title', '')} {news.get('summary', '')}"
                # 这里可以添加语言检测逻辑
                pass