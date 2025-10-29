"""
缓存管理模块

Author: Smart Stock Insider Team
Version: 1.0.0
"""

import json
import pickle
import logging
from typing import Any, Optional, Union, Callable, Dict, List
from datetime import datetime, timedelta
from functools import wraps
import hashlib

import redis.asyncio as redis
from pydantic import BaseModel

from core.config import settings

logger = logging.getLogger(__name__)


class CacheKey:
    """缓存键生成器"""

    @staticmethod
    def stock_price(symbol: str, date: Optional[str] = None) -> str:
        """生成股票价格缓存键"""
        if date:
            return f"stock:price:{symbol}:{date}"
        return f"stock:price:{symbol}:latest"

    @staticmethod
    def stock_indicator(symbol: str, indicator_type: str, period: int) -> str:
        """生成股票指标缓存键"""
        return f"stock:indicator:{symbol}:{indicator_type}:{period}"

    @staticmethod
    def news_list(category: Optional[str] = None, limit: int = 20) -> str:
        """生成新闻列表缓存键"""
        if category:
            return f"news:list:{category}:{limit}"
        return f"news:list:default:{limit}"

    @staticmethod
    def news_sentiment(news_id: int, model: str = "default") -> str:
        """生成新闻情感分析缓存键"""
        return f"news:sentiment:{news_id}:{model}"

    @staticmethod
    def ai_analysis(symbol: str, analysis_type: str, model: str = "glm") -> str:
        """生成AI分析缓存键"""
        return f"ai:analysis:{symbol}:{analysis_type}:{model}"

    @staticmethod
    def user_watchlist(user_id: int) -> str:
        """生成用户自选股缓存键"""
        return f"user:watchlist:{user_id}"

    @staticmethod
    def search_results(query: str, result_type: str = "stock") -> str:
        """生成搜索结果缓存键"""
        # 对查询进行哈希以避免特殊字符问题
        query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
        return f"search:{result_type}:{query_hash}"

    @staticmethod
    def api_rate_limit(client_id: str, endpoint: str) -> str:
        """生成API限流缓存键"""
        now = datetime.now().strftime("%Y%m%d%H")
        return f"rate_limit:{client_id}:{endpoint}:{now}"

    @staticmethod
    def service_health(service_name: str) -> str:
        """生成服务健康状态缓存键"""
        return f"service:health:{service_name}"

    @staticmethod
    def backtest_result(strategy_id: str, symbol: str) -> str:
        """生成回测结果缓存键"""
        return f"backtest:result:{strategy_id}:{symbol}"


class CacheSerializer:
    """缓存序列化器"""

    @staticmethod
    def serialize(data: Any) -> bytes:
        """序列化数据"""
        try:
            # 尝试JSON序列化（更快，更易读）
            if isinstance(data, (dict, list, str, int, float, bool)) or data is None:
                return json.dumps(data, ensure_ascii=False, default=str).encode('utf-8')
            else:
                # 复杂对象使用pickle
                return pickle.dumps(data)
        except Exception as e:
            logger.error(f"缓存序列化失败: {e}")
            raise

    @staticmethod
    def deserialize(data: bytes, use_pickle: bool = False) -> Any:
        """反序列化数据"""
        try:
            if use_pickle:
                return pickle.loads(data)
            else:
                # 尝试JSON反序列化
                return json.loads(data.decode('utf-8'))
        except (json.JSONDecodeError, pickle.PickleError) as e:
            logger.error(f"缓存反序列化失败: {e}")
            raise


class CacheManager:
    """缓存管理器"""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.default_ttl = settings.CACHE_TTL_DEFAULT
        self.key_prefix = "smart_stock:"

    async def initialize(self):
        """初始化缓存管理器"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=False,  # 使用bytes以支持序列化
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            await self.redis_client.ping()
            logger.info("✅ 缓存管理器初始化成功")
        except Exception as e:
            logger.error(f"❌ 缓存管理器初始化失败: {e}")
            # 缓存失败不应该阻止应用启动
            self.redis_client = None

    def _make_key(self, key: str) -> str:
        """生成完整的缓存键"""
        return f"{self.key_prefix}{key}"

    async def get(
        self,
        key: str,
        default: Any = None,
        use_pickle: bool = False
    ) -> Any:
        """
        获取缓存值

        Args:
            key: 缓存键
            default: 默认值
            use_pickle: 是否使用pickle序列化

        Returns:
            缓存值或默认值
        """
        if not self.redis_client:
            return default

        try:
            full_key = self._make_key(key)
            data = await self.redis_client.get(full_key)

            if data is None:
                return default

            return CacheSerializer.deserialize(data, use_pickle)

        except Exception as e:
            logger.error(f"获取缓存失败 {key}: {e}")
            return default

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        use_pickle: bool = False
    ) -> bool:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒）
            use_pickle: 是否使用pickle序列化

        Returns:
            设置是否成功
        """
        if not self.redis_client:
            return False

        try:
            full_key = self._make_key(key)
            data = CacheSerializer.serialize(value)
            expire_time = ttl or self.default_ttl

            await self.redis_client.setex(full_key, expire_time, data)
            logger.debug(f"缓存设置成功: {key} (TTL: {expire_time}s)")
            return True

        except Exception as e:
            logger.error(f"设置缓存失败 {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            删除是否成功
        """
        if not self.redis_client:
            return False

        try:
            full_key = self._make_key(key)
            result = await self.redis_client.delete(full_key)
            logger.debug(f"缓存删除: {key} - {'成功' if result else '不存在'}")
            return result > 0

        except Exception as e:
            logger.error(f"删除缓存失败 {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        检查缓存是否存在

        Args:
            key: 缓存键

        Returns:
            缓存是否存在
        """
        if not self.redis_client:
            return False

        try:
            full_key = self._make_key(key)
            result = await self.redis_client.exists(full_key)
            return result > 0

        except Exception as e:
            logger.error(f"检查缓存存在性失败 {key}: {e}")
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """
        设置缓存过期时间

        Args:
            key: 缓存键
            ttl: 过期时间（秒）

        Returns:
            设置是否成功
        """
        if not self.redis_client:
            return False

        try:
            full_key = self._make_key(key)
            result = await self.redis_client.expire(full_key, ttl)
            return result

        except Exception as e:
            logger.error(f"设置缓存过期时间失败 {key}: {e}")
            return False

    async def ttl(self, key: str) -> int:
        """
        获取缓存剩余时间

        Args:
            key: 缓存键

        Returns:
            剩余时间（秒），-1表示永不过期，-2表示不存在
        """
        if not self.redis_client:
            return -2

        try:
            full_key = self._make_key(key)
            return await self.redis_client.ttl(full_key)

        except Exception as e:
            logger.error(f"获取缓存TTL失败 {key}: {e}")
            return -2

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        递增缓存值

        Args:
            key: 缓存键
            amount: 递增数量

        Returns:
            递增后的值
        """
        if not self.redis_client:
            return None

        try:
            full_key = self._make_key(key)
            return await self.redis_client.incrby(full_key, amount)

        except Exception as e:
            logger.error(f"递增缓存失败 {key}: {e}")
            return None

    async def get_many(self, keys: List[str], use_pickle: bool = False) -> Dict[str, Any]:
        """
        批量获取缓存

        Args:
            keys: 缓存键列表
            use_pickle: 是否使用pickle序列化

        Returns:
            缓存值字典
        """
        if not self.redis_client or not keys:
            return {}

        try:
            full_keys = [self._make_key(key) for key in keys]
            values = await self.redis_client.mget(full_keys)

            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    try:
                        result[key] = CacheSerializer.deserialize(value, use_pickle)
                    except Exception as e:
                        logger.error(f"反序列化缓存失败 {key}: {e}")
                        result[key] = None
                else:
                    result[key] = None

            return result

        except Exception as e:
            logger.error(f"批量获取缓存失败: {e}")
            return {}

    async def set_many(
        self,
        mapping: Dict[str, Any],
        ttl: Optional[int] = None,
        use_pickle: bool = False
    ) -> bool:
        """
        批量设置缓存

        Args:
            mapping: 键值对映射
            ttl: 过期时间（秒）
            use_pickle: 是否使用pickle序列化

        Returns:
            设置是否成功
        """
        if not self.redis_client or not mapping:
            return False

        try:
            expire_time = ttl or self.default_ttl
            pipe = self.redis_client.pipeline()

            for key, value in mapping.items():
                full_key = self._make_key(key)
                data = CacheSerializer.serialize(value, use_pickle)
                pipe.setex(full_key, expire_time, data)

            await pipe.execute()
            logger.debug(f"批量设置缓存成功: {len(mapping)} 个键")
            return True

        except Exception as e:
            logger.error(f"批量设置缓存失败: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """
        清除匹配模式的缓存

        Args:
            pattern: 匹配模式

        Returns:
            清除的键数量
        """
        if not self.redis_client:
            return 0

        try:
            full_pattern = self._make_key(pattern)
            keys = await self.redis_client.keys(full_pattern)

            if keys:
                count = await self.redis_client.delete(*keys)
                logger.info(f"清除缓存模式 {pattern}: {count} 个键")
                return count

            return 0

        except Exception as e:
            logger.error(f"清除缓存模式失败 {pattern}: {e}")
            return 0

    async def get_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            统计信息字典
        """
        if not self.redis_client:
            return {"status": "disconnected"}

        try:
            info = await self.redis_client.info()
            return {
                "status": "connected",
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": (
                    info.get("keyspace_hits", 0) / max(
                        info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1
                    )
                )
            }

        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return {"status": "error", "error": str(e)}

    async def close(self):
        """关闭缓存连接"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("🔚 缓存连接已关闭")


# 全局缓存管理器实例
cache_manager = CacheManager()


def cached(
    key_func: Callable,
    ttl: Optional[int] = None,
    use_pickle: bool = False,
    cache_none: bool = False
):
    """
    缓存装饰器

    Args:
        key_func: 生成缓存键的函数
        ttl: 过期时间（秒）
        use_pickle: 是否使用pickle序列化
        cache_none: 是否缓存None值
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache_key = key_func(*args, **kwargs)

            # 尝试从缓存获取
            cached_result = await cache_manager.get(cache_key, use_pickle=use_pickle)
            if cached_result is not None or (cached_result is None and cache_none):
                logger.debug(f"缓存命中: {cache_key}")
                return cached_result

            # 执行函数
            logger.debug(f"缓存未命中: {cache_key}")
            result = await func(*args, **kwargs)

            # 缓存结果
            if result is not None or cache_none:
                await cache_manager.set(cache_key, result, ttl, use_pickle)

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache_key = key_func(*args, **kwargs)

            # 同步函数的缓存逻辑（简化版）
            # 注意：这里简化了同步处理，实际项目中可能需要更复杂的处理
            return func(*args, **kwargs)

        return async_wrapper if hasattr(func, '__await__') else sync_wrapper

    return decorator


# 预定义的缓存配置
CACHE_CONFIGS = {
    "stock_price": {"ttl": settings.CACHE_TTL_STOCK_DATA, "use_pickle": False},
    "stock_indicator": {"ttl": 3600, "use_pickle": False},  # 1小时
    "news_list": {"ttl": settings.CACHE_TTL_NEWS, "use_pickle": False},
    "news_sentiment": {"ttl": 7200, "use_pickle": False},  # 2小时
    "ai_analysis": {"ttl": 1800, "use_pickle": False},  # 30分钟
    "search_results": {"ttl": 600, "use_pickle": False},  # 10分钟
    "user_watchlist": {"ttl": 300, "use_pickle": False},  # 5分钟
    "backtest_result": {"ttl": 3600, "use_pickle": True},  # 1小时，复杂对象
}