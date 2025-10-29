"""
异常处理模块

Author: Smart Stock Insider Team
Version: 1.0.0
"""

import logging
from typing import Any, Dict, Optional, Union
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class BaseAPIException(Exception):
    """基础API异常类"""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseAPIException):
    """数据验证错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class NotFoundError(BaseAPIException):
    """资源未找到错误"""

    def __init__(self, message: str, resource_type: Optional[str] = None):
        details = {"resource_type": resource_type} if resource_type else {}
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details=details
        )


class AuthenticationError(BaseAPIException):
    """认证错误"""

    def __init__(self, message: str = "认证失败"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationError(BaseAPIException):
    """授权错误"""

    def __init__(self, message: str = "权限不足"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=status.HTTP_403_FORBIDDEN
        )


class RateLimitError(BaseAPIException):
    """请求频率限制错误"""

    def __init__(self, message: str = "请求过于频繁", retry_after: Optional[int] = None):
        details = {"retry_after": retry_after} if retry_after else {}
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details
        )


class ExternalServiceError(BaseAPIException):
    """外部服务错误"""

    def __init__(
        self,
        message: str,
        service_name: Optional[str] = None,
        original_error: Optional[str] = None
    ):
        details = {
            "service_name": service_name,
            "original_error": original_error
        }
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details
        )


class DatabaseError(BaseAPIException):
    """数据库错误"""

    def __init__(self, message: str, operation: Optional[str] = None):
        details = {"operation": operation} if operation else {}
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class CacheError(BaseAPIException):
    """缓存错误"""

    def __init__(self, message: str, cache_key: Optional[str] = None):
        details = {"cache_key": cache_key} if cache_key else {}
        super().__init__(
            message=message,
            error_code="CACHE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class BusinessLogicError(BaseAPIException):
    """业务逻辑错误"""

    def __init__(self, message: str, business_code: Optional[str] = None):
        details = {"business_code": business_code} if business_code else {}
        super().__init__(
            message=message,
            error_code="BUSINESS_LOGIC_ERROR",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details
        )


class ConfigurationError(BaseAPIException):
    """配置错误"""

    def __init__(self, message: str, config_key: Optional[str] = None):
        details = {"config_key": config_key} if config_key else {}
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class AIServiceError(BaseAPIException):
    """AI服务错误"""

    def __init__(self, message: str, service_name: Optional[str] = None, error_code: Optional[str] = None):
        details = {
            "service_name": service_name,
            "ai_error_code": error_code
        }
        super().__init__(
            message=message,
            error_code="AI_SERVICE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details
        )


class RetryableError(BaseAPIException):
    """可重试错误"""

    def __init__(
        self,
        message: str,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        details = {
            "max_retries": max_retries,
            "retry_delay": retry_delay,
            "retryable": True
        }
        super().__init__(
            message=message,
            error_code="RETRYABLE_ERROR",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details
        )


async def api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """自定义API异常处理器"""
    logger.error(
        f"API异常: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method
        }
    )

    response_data = {
        "error": {
            "code": exc.error_code,
            "message": exc.message,
            "details": exc.details
        },
        "timestamp": None,  # 将在下面设置
        "path": request.url.path
    }

    # 如果是重试错误，添加重试信息
    if isinstance(exc, RateLimitError):
        headers = {}
        if exc.details.get("retry_after"):
            headers["Retry-After"] = str(exc.details["retry_after"])
        return JSONResponse(
            status_code=exc.status_code,
            content=response_data,
            headers=headers
        )

    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """请求验证异常处理器"""
    logger.warning(
        f"请求验证错误: {exc.errors()}",
        extra={
            "validation_errors": exc.errors(),
            "path": request.url.path,
            "method": request.method
        }
    )

    response_data = {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "请求数据验证失败",
            "details": {
                "validation_errors": exc.errors()
            }
        },
        "timestamp": None,
        "path": request.url.path
    }

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_data
    )


async def http_exception_handler(
    request: Request,
    exc: Union[HTTPException, StarletteHTTPException]
) -> JSONResponse:
    """HTTP异常处理器"""
    logger.warning(
        f"HTTP异常: {exc.status_code} - {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path,
            "method": request.method
        }
    )

    response_data = {
        "error": {
            "code": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "details": {}
        },
        "timestamp": None,
        "path": request.url.path
    }

    return JSONResponse(
        status_code=exc.status_code,
        content=response_data
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用异常处理器"""
    logger.error(
        f"未处理的异常: {type(exc).__name__} - {str(exc)}",
        extra={
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "path": request.url.path,
            "method": request.method
        },
        exc_info=True
    )

    response_data = {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "服务器内部错误",
            "details": {
                "exception_type": type(exc).__name__
            }
        },
        "timestamp": None,
        "path": request.url.path
    }

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_data
    )


def setup_exception_handlers(app):
    """设置异常处理器"""
    app.add_exception_handler(BaseAPIException, api_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)