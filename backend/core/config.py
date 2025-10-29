"""
配置管理模块

Author: Smart Stock Insider Team
Version: 1.0.0
"""

import os
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""

    # 基础配置
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "智股通"
    VERSION: str = "1.0.0"

    # 服务配置
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./data/smart_stock.db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_URL: str = ""

    @field_validator("REDIS_URL", mode="before")
    @classmethod
    def assemble_redis_url(cls, v, info):
        if isinstance(v, str) and v.strip():
            return v

        # 从配置中获取Redis连接信息
        values = info.data if hasattr(info, 'data') else {}
        host = values.get("REDIS_HOST", "localhost")
        port = values.get("REDIS_PORT", 6379)
        password = values.get("REDIS_PASSWORD")
        db = values.get("REDIS_DB", 0)

        # 构建Redis URL，确保包含正确的协议
        if password:
            return f"redis://:{password}@{host}:{port}/{db}"
        else:
            return f"redis://{host}:{port}/{db}"

    # CORS配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "tauri://localhost",
        "http://localhost:4173"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    # AI模型配置
    GLM_API_KEY: str = "cfc8b95952484113863c16338f682547.VUsS3wsFHwDERwye"
    GLM_BASE_URL: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    GLM_MODEL: str = "glm-4.5-flash"

    # 数据源配置
    AKSHARE_ENABLED: bool = True
    DATA_CACHE_TTL: int = 300  # 5分钟
    BATCH_SIZE: int = 1000
    UPDATE_INTERVAL: int = 60  # 60秒

    # 微服务端口配置
    DATA_SERVICE_PORT: int = 8001
    AI_SERVICE_PORT: int = 8002
    NEWS_SERVICE_PORT: int = 8003
    BACKTEST_SERVICE_PORT: int = 8004
    NOTIFICATION_SERVICE_PORT: int = 8005

    # 新闻配置
    NEWS_UPDATE_INTERVAL: int = 300  # 5分钟
    MAX_NEWS_PER_SOURCE: int = 50
    NEWS_SOURCES_ENABLED: bool = True

    # 通知配置
    FEISHU_WEBHOOK_URL: Optional[str] = None
    NOTIFICATION_ENABLED: bool = True

    # 邮件配置
    EMAIL_SMTP_HOST: Optional[str] = None
    EMAIL_SMTP_PORT: int = 587
    EMAIL_USERNAME: Optional[str] = None
    EMAIL_PASSWORD: Optional[str] = None

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    LOG_MAX_SIZE: str = "10MB"
    LOG_BACKUP_COUNT: int = 5

    # 缓存配置
    CACHE_TTL_DEFAULT: int = 300
    CACHE_TTL_NEWS: int = 600
    CACHE_TTL_STOCK_DATA: int = 60

    # API限流配置
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    # 备份配置
    BACKUP_ENABLED: bool = True
    BACKUP_INTERVAL: int = 24  # 小时
    BACKUP_PATH: str = "./backups/"

    # 性能配置
    MAX_WORKERS: int = 4
    ASYNC_TIMEOUT: int = 30
    CONNECTION_TIMEOUT: int = 10

    # 功能开关
    AI_ANALYSIS_ENABLED: bool = True
    BACKTEST_ENABLED: bool = True
    NEWS_SENTIMENT_ENABLED: bool = True
    REAL_TIME_NOTIFICATIONS_ENABLED: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()


# 全局配置实例
settings = get_settings()

# 导出常用配置
API_KEY = settings.SECRET_KEY
DEBUG = settings.DEBUG
ENVIRONMENT = settings.ENVIRONMENT