"""
智股通性能测试
使用Locust进行负载测试和压力测试
"""

from locust import HttpUser, task, between, events
import random
import time
import json
import logging
from typing import Dict, List, Any

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 测试数据
STOCK_SYMBOLS = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "JPM", "V", "WMT"]
SEARCH_TERMS = ["苹果", "谷歌", "微软", "亚马逊", "特斯拉", "科技股", "人工智能", "芯片", "银行", "零售"]
USER_NAMES = [f"user_{i}" for i in range(1000)]
QUESTIONS = [
    "请分析这只股票的投资价值",
    "这个风险水平适合保守投资者吗？",
    "有什么具体的投资建议吗？",
    "请分析技术指标",
    "市场趋势如何？",
    "这个行业前景怎么样？",
    "和同行业其他股票相比如何？",
    "请给出买入或卖出建议"
]

class BaseMetrics:
    """基础性能指标收集器"""

    @staticmethod
    def record_request_success(request_type, response_time, response_length):
        """记录成功的请求"""
        events.request_success.fire(
            request_type=request_type,
            response_time=response_time,
            response_length=response_length
        )

    @staticmethod
    def record_request_failure(request_type, error):
        """记录失败的请求"""
        events.request_failure.fire(
            request_type=request_type,
            error=error
        )

class StockInsiderUser(HttpUser):
    """智股通用户行为模拟"""

    wait_time = between(1, 3)  # 用户操作间隔

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = random.choice(USER_NAMES)
        self.risk_tolerance = random.choice(["conservative", "moderate", "aggressive"])
        self.favorite_stocks = random.sample(STOCK_SYMBOLS, random.randint(2, 5))
        logger.info(f"Created user: {self.username}, risk_tolerance: {self.risk_tolerance}")

    def on_start(self):
        """用户开始时的初始化"""
        self.authenticate_user()
        self.set_user_preferences()

    def authenticate_user(self):
        """用户认证"""
        try:
            # 模拟用户登录
            login_data = {
                "username": self.username,
                "password": "testpassword123"
            }

            response = self.client.post("/api/auth/login", json=login_data)

            if response.status_code == 200:
                # 保存认证令牌
                auth_data = response.json()
                if "token" in auth_data:
                    self.client.headers.update({
                        "Authorization": f"Bearer {auth_data['token']}"
                    })
                BaseMetrics.record_request_success(
                    "user_login",
                    response.elapsed.total_seconds() * 1000,
                    len(response.content)
                )
                logger.info(f"User {self.username} authenticated successfully")
            else:
                logger.warning(f"Authentication failed for user {self.username}: {response.status_code}")

        except Exception as e:
            logger.error(f"Authentication error for user {self.username}: {str(e)}")
            BaseMetrics.record_request_failure("user_login", str(e))

    def set_user_preferences(self):
        """设置用户偏好"""
        try:
            preferences = {
                "risk_tolerance": self.risk_tolerance,
                "preferred_sectors": ["technology", "healthcare", "finance"],
                "investment_goals": ["growth", "income"],
                "notification_settings": {
                    "price_alerts": True,
                    "news_alerts": True,
                    "ai_analysis_alerts": True
                }
            }

            response = self.client.post("/api/user/preferences", json=preferences)

            if response.status_code == 200:
                BaseMetrics.record_request_success(
                    "set_preferences",
                    response.elapsed.total_seconds() * 1000,
                    len(response.content)
                )
                logger.info(f"Preferences set for user {self.username}")

        except Exception as e:
            logger.error(f"Failed to set preferences for user {self.username}: {str(e)}")
            BaseMetrics.record_request_failure("set_preferences", str(e))

    @task(3)
    def view_dashboard(self):
        """查看仪表板"""
        try:
            response = self.client.get("/dashboard")

            if response.status_code == 200:
                BaseMetrics.record_request_success(
                    "view_dashboard",
                    response.elapsed.total_seconds() * 1000,
                    len(response.content)
                )
                logger.debug(f"User {self.username} viewed dashboard")
            else:
                logger.warning(f"Failed to view dashboard for user {self.username}: {response.status_code}")

        except Exception as e:
            logger.error(f"Dashboard view error for user {self.username}: {str(e)}")
            BaseMetrics.record_request_failure("view_dashboard", str(e))

    @task(5)
    def search_stocks(self):
        """搜索股票"""
        try:
            search_term = random.choice(SEARCH_TERMS)
            response = self.client.get(f"/api/stocks/search?keyword={search_term}&limit=10")

            if response.status_code == 200:
                data = response.json()
                BaseMetrics.record_request_success(
                    "search_stocks",
                    response.elapsed.total_seconds() * 1000,
                    len(response.content)
                )
                logger.debug(f"User {self.username} searched for: {search_term}")
            else:
                logger.warning(f"Search failed for user {self.username}: {response.status_code}")

        except Exception as e:
            logger.error(f"Stock search error for user {self.username}: {str(e)}")
            BaseMetrics.record_request_failure("search_stocks", str(e))

    @task(4)
    def get_stock_details(self):
        """获取股票详情"""
        try:
            symbol = random.choice(self.favorite_stocks)
            response = self.client.get(f"/api/stocks/{symbol}")

            if response.status_code == 200:
                BaseMetrics.record_request_success(
                    "get_stock_details",
                    response.elapsed.total_seconds() * 1000,
                    len(response.content)
                )
                logger.debug(f"User {self.username} viewed stock details for {symbol}")
            else:
                logger.warning(f"Failed to get stock details for user {self.username}: {response.status_code}")

        except Exception as e:
            logger.error(f"Stock details error for user {self.username}: {str(e)}")
            BaseMetrics.record_request_failure("get_stock_details", str(e))

    @task(2)
    def get_realtime_prices(self):
        """获取实时价格"""
        try:
            symbols = random.sample(self.favorite_stocks, min(3, len(self.favorite_stocks)))
            response = self.client.post("/api/stocks/realtime", json={"symbols": symbols})

            if response.status_code == 200:
                BaseMetrics.record_request_success(
                    "get_realtime_prices",
                    response.elapsed.total_seconds() * 1000,
                    len(response.content)
                )
                logger.debug(f"User {self.username} got realtime prices for {symbols}")
            else:
                logger.warning(f"Failed to get realtime prices for user {self.username}: {response.status_code}")

        except Exception as e:
            logger.error(f"Realtime prices error for user {self.username}: {str(e)}")
            BaseMetrics.record_request_failure("get_realtime_prices", str(e))

    @task(3)
    def get_news(self):
        """获取新闻"""
        try:
            category = random.choice(["technology", "finance", "healthcare"])
            response = self.client.get(f"/api/news?category={category}&limit=20")

            if response.status_code == 200:
                BaseMetrics.record_request_success(
                    "get_news",
                    response.elapsed.total_seconds() * 1000,
                    len(response.content)
                )
                logger.debug(f"User {self.username} got {category} news")
            else:
                logger.warning(f"Failed to get news for user {self.username}: {response.status_code}")

        except Exception as e:
            logger.error(f"News error for user {self.username}: {str(e)}")
            BaseMetrics.record_request_failure("get_news", str(e))

    @task(1)
    def request_ai_analysis(self):
        """请求AI分析"""
        try:
            symbol = random.choice(self.favorite_stocks)
            question = random.choice(QUESTIONS)

            analysis_request = {
                "symbol": symbol,
                "question": question,
                "role": random.choice(["technical_analyst", "fundamental_analyst", "risk_analyst"]),
                "context": {
                    "user_risk_tolerance": self.risk_tolerance
                }
            }

            # AI分析可能需要较长时间，设置更长的超时
            with self.client.post("/api/ai/analyze", json=analysis_request, catch_response=True, timeout=30) as response:
                if response.status_code == 200:
                    BaseMetrics.record_request_success(
                        "ai_analysis",
                        response.elapsed.total_seconds() * 1000,
                        len(response.content)
                    )
                    logger.debug(f"User {self.username} requested AI analysis for {symbol}")
                elif response.status_code == 202:
                    # 异步处理，记录请求成功
                    BaseMetrics.record_request_success(
                        "ai_analysis_async",
                        response.elapsed.total_seconds() * 1000,
                        len(response.content)
                    )
                    logger.debug(f"User {self.username} submitted async AI analysis for {symbol}")
                else:
                    logger.warning(f"AI analysis failed for user {self.username}: {response.status_code}")

        except Exception as e:
            logger.error(f"AI analysis error for user {self.username}: {str(e)}")
            BaseMetrics.record_request_failure("ai_analysis", str(e))

    @task(2)
    def get_portfolio_data(self):
        """获取投资组合数据"""
        try:
            response = self.client.get("/api/portfolio")

            if response.status_code == 200:
                BaseMetrics.record_request_success(
                    "get_portfolio",
                    response.elapsed.total_seconds() * 1000,
                    len(response.content)
                )
                logger.debug(f"User {self.username} viewed portfolio")
            else:
                logger.warning(f"Failed to get portfolio for user {self.username}: {response.status_code}")

        except Exception as e:
            logger.error(f"Portfolio error for user {self.username}: {str(e)}")
            BaseMetrics.record_request_failure("get_portfolio", str(e))

    @task(1)
    def optimize_portfolio(self):
        """投资组合优化"""
        try:
            optimization_request = {
                "symbols": self.favorite_stocks,
                "risk_tolerance": self.risk_tolerance,
                "investment_horizon": "1y",
                "optimization_goal": "max_sharpe"
            }

            with self.client.post("/api/portfolio/optimize", json=optimization_request, catch_response=True, timeout=60) as response:
                if response.status_code == 200:
                    BaseMetrics.record_request_success(
                        "portfolio_optimization",
                        response.elapsed.total_seconds() * 1000,
                        len(response.content)
                    )
                    logger.debug(f"User {self.username} optimized portfolio")
                elif response.status_code == 202:
                    BaseMetrics.record_request_success(
                        "portfolio_optimization_async",
                        response.elapsed.total_seconds() * 1000,
                        len(response.content)
                    )
                    logger.debug(f"User {self.username} submitted async portfolio optimization")
                else:
                    logger.warning(f"Portfolio optimization failed for user {self.username}: {response.status_code}")

        except Exception as e:
            logger.error(f"Portfolio optimization error for user {self.username}: {str(e)}")
            BaseMetrics.record_request_failure("portfolio_optimization", str(e))

    @task(2)
    def get_analytics(self):
        """获取用户分析数据"""
        try:
            response = self.client.get("/api/analytics/user")

            if response.status_code == 200:
                BaseMetrics.record_request_success(
                    "get_analytics",
                    response.elapsed.total_seconds() * 1000,
                    len(response.content)
                )
                logger.debug(f"User {self.username} viewed analytics")
            else:
                logger.warning(f"Failed to get analytics for user {self.username}: {response.status_code}")

        except Exception as e:
            logger.error(f"Analytics error for user {self.username}: {str(e)}")
            BaseMetrics.record_request_failure("get_analytics", str(e))

    @task(1)
    def add_to_watchlist(self):
        """添加到自选股"""
        try:
            symbol = random.choice(STOCK_SYMBOLS)
            watchlist_data = {
                "symbol": symbol,
                "action": "add"
            }

            response = self.client.post("/api/watchlist", json=watchlist_data)

            if response.status_code == 200:
                BaseMetrics.record_request_success(
                    "add_to_watchlist",
                    response.elapsed.total_seconds() * 1000,
                    len(response.content)
                )
                logger.debug(f"User {self.username} added {symbol} to watchlist")
            else:
                logger.warning(f"Failed to add to watchlist for user {self.username}: {response.status_code}")

        except Exception as e:
            logger.error(f"Watchlist error for user {self.username}: {str(e)}")
            BaseMetrics.record_request_failure("add_to_watchlist", str(e))


class PowerUser(StockInsiderUser):
    """高级用户 - 更频繁和复杂的操作"""

    wait_time = between(0.5, 2)  # 更短的操作间隔

    @task(5)
    def batch_stock_analysis(self):
        """批量股票分析"""
        try:
            symbols = random.sample(STOCK_SYMBOLS, 5)

            for symbol in symbols:
                analysis_request = {
                    "symbol": symbol,
                    "question": "快速技术分析",
                    "role": "technical_analyst"
                }

                response = self.client.post("/api/ai/analyze", json=analysis_request, catch_response=True)

                if response.status_code == 200:
                    BaseMetrics.record_request_success(
                        "batch_analysis",
                        response.elapsed.total_seconds() * 1000,
                        len(response.content)
                    )

                # 短暂延迟避免过载
                time.sleep(0.2)

        except Exception as e:
            logger.error(f"Batch analysis error: {str(e)}")
            BaseMetrics.record_request_failure("batch_analysis", str(e))


class MobileUser(StockInsiderUser):
    """移动用户 - 主要查看和简单操作"""

    wait_time = between(2, 5)  # 更长的操作间隔，模拟移动使用习惯

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client.headers.update({
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        })

    @task(4)
    def view_mobile_dashboard(self):
        """查看移动版仪表板"""
        try:
            response = self.client.get("/dashboard?mobile=true")

            if response.status_code == 200:
                BaseMetrics.record_request_success(
                    "mobile_dashboard",
                    response.elapsed.total_seconds() * 1000,
                    len(response.content)
                )

        except Exception as e:
            logger.error(f"Mobile dashboard error: {str(e)}")
            BaseMetrics.record_request_failure("mobile_dashboard", str(e))

    # 移动用户主要进行查看操作，减少复杂交互
    @task(6)
    def get_simple_stock_data(self):
        """获取简单股票数据"""
        try:
            symbol = random.choice(self.favorite_stocks)
            response = self.client.get(f"/api/stocks/{symbol}?simple=true")

            if response.status_code == 200:
                BaseMetrics.record_request_success(
                    "simple_stock_data",
                    response.elapsed.total_seconds() * 1000,
                    len(response.content)
                )

        except Exception as e:
            logger.error(f"Simple stock data error: {str(e)}")
            BaseMetrics.record_request_failure("simple_stock_data", str(e))


# 性能测试事件监听器
def on_locust_init(environment, runner, **kwargs):
    """Locust初始化时的回调"""
    logger.info("Performance test started")

    # 设置自定义统计
    environment.events.request_success.add_listener(success_listener)
    environment.events.request_failure.add_listener(failure_listener)

def success_listener(request_type, response_time, response_length, **kwargs):
    """成功请求监听器"""
    logger.info(f"Success: {request_type} - {response_time:.2f}ms - {response_length} bytes")

def failure_listener(request_type, error, **kwargs):
    """失败请求监听器"""
    logger.error(f"Failure: {request_type} - {error}")

# 导出用户类供Locust使用
__all__ = ['StockInsiderUser', 'PowerUser', 'MobileUser']