"""
数据库配置和初始化模块

Author: Smart Stock Insider Team
Version: 1.0.0
"""

import asyncio
import logging
from pathlib import Path
from typing import AsyncGenerator

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from core.config import settings

logger = logging.getLogger(__name__)

# 数据库配置
DATABASE_URL = settings.DATABASE_URL

# 创建同步引擎（用于alembic迁移）
sync_engine = create_engine(
    DATABASE_URL.replace("sqlite://", "sqlite:///"),
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False}  # SQLite特定配置
)

# 创建异步引擎
async_database_url = DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
async_engine = create_async_engine(
    async_database_url,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False}  # SQLite特定配置
)

# 创建会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# 创建基础模型类
Base = declarative_base()

# 元数据
metadata = MetaData()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """获取异步数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"数据库会话错误: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库"""
    try:
        # 确保数据目录存在
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)

        # 创建所有表
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logger.info("✅ 数据库初始化成功")

    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise


async def close_db():
    """关闭数据库连接"""
    try:
        await async_engine.dispose()
        logger.info("✅ 数据库连接已关闭")
    except Exception as e:
        logger.error(f"❌ 关闭数据库连接失败: {e}")


class DatabaseManager:
    """数据库管理器"""

    def __init__(self):
        self.engine = async_engine
        self.session_factory = AsyncSessionLocal

    async def create_tables(self):
        """创建所有表"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self):
        """删除所有表"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def get_session(self) -> AsyncSession:
        """获取数据库会话"""
        return self.session_factory()

    async def execute_raw_sql(self, sql: str):
        """执行原始SQL"""
        async with self.engine.begin() as conn:
            return await conn.execute(sql)

    async def check_connection(self) -> bool:
        """检查数据库连接"""
        try:
            from sqlalchemy import text
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"数据库连接检查失败: {e}")
            return False


# 全局数据库管理器实例
db_manager = DatabaseManager()


# 依赖注入：获取数据库会话
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI依赖注入：获取数据库会话"""
    async for session in get_async_session():
        yield session


# 数据库健康检查
async def health_check() -> dict:
    """数据库健康检查"""
    try:
        is_connected = await db_manager.check_connection()

        # 获取表信息
        async with db_manager.get_session() as session:
            # 这里可以添加更多的健康检查逻辑
            result = {
                "status": "healthy" if is_connected else "unhealthy",
                "database_url": settings.DATABASE_URL.split("///")[-1],  # 隐藏密码等敏感信息
                "connected": is_connected
            }

        return result

    except Exception as e:
        logger.error(f"数据库健康检查失败: {e}")
        return {
            "status": "error",
            "error": str(e),
            "connected": False
        }