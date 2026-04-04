"""通用响应格式"""

from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None


class MetaInfo(BaseModel):
    rate_limit: dict[str, Any] | None = None


class ApiResponse(BaseModel):
    success: bool
    data: Any = None
    error: ErrorResponse | None = None
    meta: MetaInfo | None = None


def success_response(data: Any, meta: MetaInfo | None = None) -> dict:
    """构建成功响应"""
    return {
        "success": True,
        "data": data,
        "error": None,
        "meta": meta,
    }


def error_response(
    code: str, message: str, details: dict[str, Any] | None = None
) -> dict:
    """构建错误响应"""
    return {
        "success": False,
        "data": None,
        "error": {"code": code, "message": message, "details": details},
        "meta": None,
    }
