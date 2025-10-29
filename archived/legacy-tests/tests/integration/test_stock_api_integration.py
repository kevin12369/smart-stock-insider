"""
股票API集成测试
测试前端与后端股票数据API的完整交互流程
"""

import pytest
import asyncio
import aiohttp
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
import time

from tests.utils import TestDataGenerator, APITestHelper
from tests.conftest import get_test_config


class TestStockAPIIntegration:
    """股票API集成测试类"""

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
    def test_stocks(self):
        """测试股票数据"""
        return TestDataGenerator.generate_stock_data(10)

    @pytest.fixture
    def api_helper(self):
        """API测试助手"""
        return APITestHelper()

    @pytest.mark.asyncio
    async def test_get_stock_list_complete_flow(self, api_client, test_stocks, api_helper):
        """测试获取股票列表的完整流程"""

        # 1. 获取股票列表
        async with api_client.get("/api/stocks") as response:
            assert response.status == 200

            data = await response.json()
            assert "data" in data
            assert "pagination" in data
            assert isinstance(data["data"], list)

            if data["data"]:
                stock = data["data"][0]
                api_helper.validate_stock_response(stock)

    @pytest.mark.asyncio
    async def test_get_stock_detail_complete_flow(self, api_client, test_stocks, api_helper):
        """测试获取股票详情的完整流程"""

        # 首先获取股票列表以获得有效的股票代码
        async with api_client.get("/api/stocks") as response:
            data = await response.json()

            if not data["data"]:
                pytest.skip("没有可用的股票数据")

            symbol = data["data"][0]["symbol"]

        # 获取股票详情
        async with api_client.get(f"/api/stocks/{symbol}") as response:
            assert response.status == 200

            stock_detail = await response.json()
            api_helper.validate_stock_response(stock_detail)
            assert stock_detail["symbol"] == symbol

    @pytest.mark.asyncio
    async def test_realtime_price_updates(self, api_client, api_helper):
        """测试实时价格更新流程"""

        # 获取股票列表
        async with api_client.get("/api/stocks") as response:
            data = await response.json()

            if not data["data"]:
                pytest.skip("没有可用的股票数据")

            symbols = [stock["symbol"] for stock in data["data"][:5]]  # 取前5只股票

        # 请求实时价格
        payload = {"symbols": symbols}
        async with api_client.post("/api/stocks/realtime", json=payload) as response:
            assert response.status == 200

            realtime_data = await response.json()
            assert isinstance(realtime_data, list)

            for price_data in realtime_data:
                api_helper.validate_realtime_price_response(price_data)
                assert price_data["symbol"] in symbols

    @pytest.mark.asyncio
    async def test_stock_search_workflow(self, api_client, api_helper):
        """测试股票搜索工作流程"""

        search_terms = ["AAPL", "Apple", "科技", "Microsoft"]

        for search_term in search_terms:
            async with api_client.get(f"/api/stocks/search?keyword={search_term}&limit=10") as response:
                assert response.status == 200

                search_results = await response.json()
                assert isinstance(search_results, list)

                for result in search_results:
                    api_helper.validate_stock_response(result)

                    # 验证搜索相关性
                    assert (
                        search_term.lower() in result["symbol"].lower() or
                        search_term.lower() in result["name"].lower()
                    )

    @pytest.mark.asyncio
    async def test_stock_filtering_and_pagination(self, api_client, api_helper):
        """测试股票筛选和分页功能"""

        # 测试分页
        page_size = 5
        async with api_client.get(f"/api/stocks?page=1&limit={page_size}") as response:
            data = await response.json()
            assert response.status == 200

            assert len(data["data"]) <= page_size
            assert data["pagination"]["page"] == 1
            assert data["pagination"]["size"] == page_size

        # 测试市场筛选
        async with api_client.get("/api/stocks?market=SH") as response:
            data = await response.json()
            assert response.status == 200

            for stock in data["data"]:
                assert stock["market"] == "SH"

        # 测试行业筛选
        async with api_client.get("/api/stocks?sector=Technology") as response:
            data = await response.json()
            assert response.status == 200

            for stock in data["data"]:
                assert stock["sector"] == "Technology"

    @pytest.mark.asyncio
    async def test_stock_price_history_flow(self, api_client, api_helper):
        """测试股票价格历史数据流程"""

        # 获取股票列表以获得有效的股票代码
        async with api_client.get("/api/stocks") as response:
            data = await response.json()

            if not data["data"]:
                pytest.skip("没有可用的股票数据")

            symbol = data["data"][0]["symbol"]

        # 获取不同时间段的历史数据
        time_periods = ["1d", "1w", "1m", "3m", "1y"]

        for period in time_periods:
            async with api_client.get(f"/api/stocks/{symbol}/history?period={period}") as response:
                if response.status == 404:
                    continue  # 某些时间段可能不支持

                assert response.status == 200

                history_data = await response.json()
                assert "data" in history_data
                assert "period" in history_data
                assert history_data["period"] == period

                for price_point in history_data["data"]:
                    api_helper.validate_price_history_response(price_point)

    @pytest.mark.asyncio
    async def test_watchlist_integration_flow(self, api_client, api_helper):
        """测试自选股集成流程"""

        # 获取股票列表
        async with api_client.get("/api/stocks") as response:
            data = await response.json()

            if not data["data"]:
                pytest.skip("没有可用的股票数据")

            test_stock = data["data"][0]
            symbol = test_stock["symbol"]

        # 添加到自选股
        watchlist_data = {
            "symbol": symbol,
            "name": test_stock["name"],
            "sector": test_stock["sector"]
        }

        async with api_client.post("/api/watchlist/add", json=watchlist_data) as response:
            # 注意：这可能会返回409如果已经在自选股中
            assert response.status in [200, 201, 409]

        # 获取自选股列表
        async with api_client.get("/api/watchlist") as response:
            assert response.status == 200

            watchlist = await response.json()
            assert isinstance(watchlist, list)

            # 验证股票是否在自选股中
            watch_symbols = [item["symbol"] for item in watchlist]
            if symbol in watch_symbols:
                # 从自选股中移除
                async with api_client.delete(f"/api/watchlist/{symbol}") as response:
                    assert response.status in [200, 404]

    @pytest.mark.asyncio
    async def test_technical_indicators_flow(self, api_client, api_helper):
        """测试技术指标流程"""

        # 获取股票列表
        async with api_client.get("/api/stocks") as response:
            data = await response.json()

            if not data["data"]:
                pytest.skip("没有可用的股票数据")

            symbol = data["data"][0]["symbol"]

        # 获取技术指标
        indicators = ["MA", "MACD", "RSI", "BOLL", "KDJ"]

        for indicator in indicators:
            async with api_client.get(f"/api/stocks/{symbol}/indicators?type={indicator}") as response:
                if response.status == 404:
                    continue  # 某些指标可能不支持

                assert response.status == 200

                indicator_data = await response.json()
                assert "indicator" in indicator_data
                assert "data" in indicator_data
                assert indicator_data["indicator"] == indicator

    @pytest.mark.asyncio
    async def test_market_overview_flow(self, api_client, api_helper):
        """测试市场概览流程"""

        # 获取市场概览
        async with api_client.get("/api/market/overview") as response:
            assert response.status == 200

            overview = await response.json()
            api_helper.validate_market_overview_response(overview)

        # 获取市场指数
        async with api_client.get("/api/market/indices") as response:
            assert response.status == 200

            indices = await response.json()
            assert isinstance(indices, list)

            for index in indices:
                api_helper.validate_market_index_response(index)

        # 获取市场统计
        async with api_client.get("/api/market/stats") as response:
            assert response.status == 200

            stats = await response.json()
            api_helper.validate_market_stats_response(stats)

    @pytest.mark.asyncio
    async def test_error_handling_integration(self, api_client):
        """测试错误处理集成"""

        # 测试无效股票代码
        async with api_client.get("/api/stocks/INVALID") as response:
            assert response.status == 404

            error = await response.json()
            assert "error" in error

        # 测试无效搜索参数
        async with api_client.get("/api/stocks/search?keyword=") as response:
            assert response.status == 400

        # 测试无效分页参数
        async with api_client.get("/api/stocks?page=-1") as response:
            assert response.status == 400

        # 测试无效的实时价格请求
        async with api_client.post("/api/stocks/realtime", json={}) as response:
            assert response.status == 400

    @pytest.mark.asyncio
    async def test_concurrent_requests_performance(self, api_client):
        """测试并发请求性能"""

        # 创建多个并发请求
        symbols = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]

        async def fetch_stock_details(symbol):
            async with api_client.get(f"/api/stocks/{symbol}") as response:
                if response.status == 200:
                    return await response.json()
                return None

        # 并发执行请求
        start_time = time.time()
        results = await asyncio.gather(
            *[fetch_stock_details(symbol) for symbol in symbols],
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
    async def test_api_response_consistency(self, api_client, api_helper):
        """测试API响应一致性"""

        # 获取股票列表
        async with api_client.get("/api/stocks") as response:
            data = await response.json()

            if not data["data"]:
                pytest.skip("没有可用的股票数据")

            symbol = data["data"][0]["symbol"]

        # 多次获取同一股票的详情，验证数据一致性
        responses = []
        for _ in range(3):
            async with api_client.get(f"/api/stocks/{symbol}") as response:
                if response.status == 200:
                    stock_data = await response.json()
                    responses.append(stock_data)

            # 添加小延迟避免缓存问题
            await asyncio.sleep(0.1)

        # 验证响应一致性
        if len(responses) >= 2:
            # 基本字段应该保持一致
            consistent_fields = ["symbol", "name", "sector", "industry"]
            for field in consistent_fields:
                assert responses[0][field] == responses[-1][field]

    @pytest.mark.asyncio
    async def test_data_format_validation(self, api_client, api_helper):
        """测试数据格式验证"""

        # 测试股票列表格式
        async with api_client.get("/api/stocks") as response:
            data = await response.json()

            assert isinstance(data, dict)
            assert "data" in data
            assert "pagination" in data

            # 验证分页格式
            pagination = data["pagination"]
            required_pagination_fields = ["page", "size", "total", "pages"]
            for field in required_pagination_fields:
                assert field in pagination
                assert isinstance(pagination[field], (int, type(None)))

        # 测试实时价格格式
        async with api_client.post("/api/stocks/realtime", json={"symbols": ["AAPL"]}) as response:
            if response.status == 200:
                realtime_data = await response.json()

                assert isinstance(realtime_data, list)

                for item in realtime_data:
                    required_fields = ["symbol", "price", "change", "change_percent", "timestamp"]
                    for field in required_fields:
                        assert field in item

                    # 验证数值类型
                    assert isinstance(item["price"], (int, float))
                    assert isinstance(item["change"], (int, float))
                    assert isinstance(item["change_percent"], (int, float))

    @pytest.mark.asyncio
    async def test_rate_limiting_behavior(self, api_client):
        """测试速率限制行为"""

        # 快速发送多个请求
        requests = []
        for i in range(20):  # 发送20个快速请求
            async with api_client.get("/api/stocks") as response:
                requests.append(response.status)

            # 极短的延迟
            await asyncio.sleep(0.01)

        # 检查是否有速率限制响应
        rate_limited_responses = [code for code in requests if code == 429]

        # 如果有速率限制，验证其行为
        if rate_limited_responses:
            assert len(rate_limited_responses) > 0

            # 等待后重试应该成功
            await asyncio.sleep(1)
            async with api_client.get("/api/stocks") as response:
                assert response.status == 200