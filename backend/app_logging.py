"""
日志配置模块

Author: Smart Stock Insider Team
Version: 1.0.0
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Dict, Any

from core.config import settings


def setup_logging():
    """设置日志配置"""

    # 创建日志目录
    log_dir = Path(settings.LOG_FILE).parent
    log_dir.mkdir(exist_ok=True)

    # 日志格式
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s:%(lineno)-4d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    console_handler.setFormatter(formatter)

    # 文件处理器（带轮转）
    file_handler = logging.handlers.RotatingFileHandler(
        filename=settings.LOG_FILE,
        maxBytes=_parse_size(settings.LOG_MAX_SIZE),
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    file_handler.setFormatter(formatter)

    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # 配置特定模块的日志级别
    _configure_module_loggers()

    # 配置第三方库日志级别
    _configure_third_party_loggers()

    logging.info("🎯 智股通日志系统初始化完成")
    logging.info(f"📝 日志级别: {settings.LOG_LEVEL}")
    logging.info(f"📁 日志文件: {settings.LOG_FILE}")


def _configure_module_loggers():
    """配置应用模块日志器"""
    module_loggers = {
        "api": "INFO",
        "services": "INFO",
        "core": "INFO",
        "models": "INFO",
        "utils": "INFO"
    }

    for module, level in module_loggers.items():
        logger = logging.getLogger(module)
        logger.setLevel(getattr(logging, level))


def _configure_third_party_loggers():
    """配置第三方库日志器"""
    third_party_loggers = {
        "uvicorn": "WARNING",
        "uvicorn.access": "WARNING",
        "sqlalchemy": "WARNING",
        "sqlalchemy.engine": "WARNING",
        "sqlalchemy.pool": "WARNING",
        "httpx": "WARNING",
        "websockets": "WARNING",
        "asyncio": "WARNING",
        "aiohttp": "WARNING"
    }

    for logger_name, level in third_party_loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, level))


def _parse_size(size_str: str) -> int:
    """解析大小字符串"""
    size_str = size_str.upper().strip()

    if size_str.endswith('KB'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        return int(size_str)


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器"""

    # 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
        'RESET': '\033[0m'      # 重置
    }

    def format(self, record):
        # 添加颜色
        level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        record.levelname = f"{level_color}{record.levelname}{self.COLORS['RESET']}"

        return super().format(record)


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志器"""
    return logging.getLogger(name)


class RequestLogger:
    """请求日志记录器"""

    def __init__(self):
        self.logger = get_logger("request")

    def log_request(self, method: str, path: str, status_code: int, duration: float, **kwargs):
        """记录请求日志"""
        self.logger.info(
            f"📥 {method} {path} -> {status_code} ({duration:.3f}s)",
            extra=kwargs
        )

    def log_error(self, method: str, path: str, error: Exception, **kwargs):
        """记录错误日志"""
        self.logger.error(
            f"❌ {method} {path} -> {type(error).__name__}: {str(error)}",
            extra=kwargs,
            exc_info=True
        )


class BusinessLogger:
    """业务日志记录器"""

    def __init__(self):
        self.logger = get_logger("business")

    def log_stock_analysis(self, symbol: str, analysis_type: str, result: Any, **kwargs):
        """记录股票分析日志"""
        self.logger.info(
            f"📈 股票分析 - {symbol} ({analysis_type})",
            extra={"symbol": symbol, "type": analysis_type, "result": str(result), **kwargs}
        )

    def log_ai_analysis(self, role: str, symbol: str, request: str, **kwargs):
        """记录AI分析日志"""
        self.logger.info(
            f"🤖 AI分析 - {role} 分析 {symbol}",
            extra={"role": role, "symbol": symbol, "request": request, **kwargs}
        )

    def log_news_update(self, source: str, count: int, **kwargs):
        """记录新闻更新日志"""
        self.logger.info(
            f"📰 新闻更新 - {source}: {count} 条",
            extra={"source": source, "count": count, **kwargs}
        )

    def log_backtest(self, strategy: str, symbol: str, result: Any, **kwargs):
        """记录回测日志"""
        self.logger.info(
            f"🔄 回测完成 - {strategy} ({symbol})",
            extra={"strategy": strategy, "symbol": symbol, "result": str(result), **kwargs}
        )


class PerformanceLogger:
    """性能日志记录器"""

    def __init__(self):
        self.logger = get_logger("performance")

    def log_slow_query(self, query: str, duration: float, **kwargs):
        """记录慢查询日志"""
        if duration > 1.0:  # 超过1秒的查询
            self.logger.warning(
                f"⏱️ 慢查询检测 ({duration:.3f}s): {query[:100]}...",
                extra={"query": query, "duration": duration, **kwargs}
            )

    def log_memory_usage(self, component: str, memory_mb: float, **kwargs):
        """记录内存使用日志"""
        self.logger.info(
            f"💾 内存使用 - {component}: {memory_mb:.2f}MB",
            extra={"component": component, "memory_mb": memory_mb, **kwargs}
        )

    def log_api_call(self, api: str, duration: float, status: str, **kwargs):
        """记录API调用日志"""
        self.logger.info(
            f"🌐 API调用 - {api}: {status} ({duration:.3f}s)",
            extra={"api": api, "duration": duration, "status": status, **kwargs}
        )


# 全局日志器实例
request_logger = RequestLogger()
business_logger = BusinessLogger()
performance_logger = PerformanceLogger()