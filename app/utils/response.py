"""统一响应工具函数"""

from typing import Any

from fastapi.responses import JSONResponse


def success(data: Any, status_code: int = 200, meta: dict | None = None) -> JSONResponse:
    """成功响应"""
    return JSONResponse(
        status_code=status_code,
        content={"success": True, "data": data, "error": None, "meta": meta},
    )


def error(
    code: str,
    message: str,
    status_code: int = 400,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    """错误响应"""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "data": None,
            "error": {"code": code, "message": message, "details": details},
            "meta": None,
        },
    )
