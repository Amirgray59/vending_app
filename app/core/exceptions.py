"""
Exceptionهای دامنه‌ای (Domain Exceptions).

این کلاس‌ها مستقل از HTTP هستند و در سرویس‌ها پرتاب می‌شوند.
یک exception-handler عمومی آن‌ها را به پاسخ HTTP مناسب تبدیل می‌کند.
"""

from typing import Any


class AppException(Exception):
    """پایه تمام استثناهای دامنه."""

    status_code: int = 500
    error_code: str = "internal_error"
    default_message: str = "خطای داخلی سرور رخ داده است."

    def __init__(
        self,
        message: str | None = None,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message or self.default_message
        self.details = details or {}
        super().__init__(self.message)


# ---------- 400 ----------
class ValidationException(AppException):
    status_code = 400
    error_code = "validation_error"
    default_message = "Ivalid input"


class BusinessRuleException(AppException):
    status_code = 400
    error_code = "business_rule_violation"
    default_message = "Invalid business rule"


# ---------- 401 ----------
class UnauthorizedException(AppException):
    status_code = 401
    error_code = "unauthorized"
    default_message = "No authorization"


class InvalidCredentialsException(AppException):
    status_code = 401
    error_code = "invalid_credentials"
    default_message = "Ivalid username or password"


class TokenExpiredException(AppException):
    status_code = 401
    error_code = "token_expired"
    default_message = "Invalid or expired Token"


# ---------- 403 ----------
class ForbiddenException(AppException):
    status_code = 403
    error_code = "forbidden"
    default_message = "Invalid role (you don't have access)"


# ---------- 404 ----------
class NotFoundException(AppException):
    status_code = 404
    error_code = "not_found"
    default_message = "Not found"


# ---------- 409 ----------
class ConflictException(AppException):
    status_code = 409
    error_code = "conflict"
    default_message = "Conflict from server"


# ---------- 429 ----------
class RateLimitException(AppException):
    status_code = 429
    error_code = "rate_limit_exceeded"
    default_message = "Too many requests!"


# ---------- Hardware / device ----------
class DeviceOfflineException(AppException):
    status_code = 503
    error_code = "device_offline"
    default_message = "Device is offline"


class DeviceProtocolException(AppException):
    status_code = 502
    error_code = "device_protocol_error"
    default_message = "Protocol error (from device or server)"
