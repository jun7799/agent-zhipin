"""FastAPI应用入口"""

import os
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时初始化数据库"""
    # SQLite需要创建data目录，PostgreSQL不需要
    if settings.DATABASE_URL.startswith("sqlite"):
        os.makedirs("data", exist_ok=True)
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="面向AI Agent的极简招聘信息API平台",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router)


# 全局异常处理：捕获所有未处理异常，返回详细错误信息
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(exc),
                "traceback": traceback.format_exc(),
            },
        },
    )


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/debug/db")
async def debug_db():
    """调试接口：测试数据库连接"""
    try:
        from app.database import engine, async_session
        from sqlalchemy import text
        async with async_session() as session:
            result = await session.execute(text("SELECT 1"))
            row = result.scalar()
            return {"status": "ok", "db_url_prefix": settings.DATABASE_URL[:30], "query_result": row}
    except Exception as e:
        return {"status": "error", "error": str(e), "error_type": type(e).__name__}


@app.get("/debug/hash")
async def debug_hash():
    """调试接口：测试密码哈希"""
    try:
        import bcrypt
        from app.core.security import hash_password
        hashed = hash_password("test123")
        return {"status": "ok", "bcrypt_version": bcrypt.__version__, "hash_prefix": hashed[:20]}
    except Exception as e:
        return {"status": "error", "error": str(e), "error_type": type(e).__name__}


@app.post("/debug/register")
async def debug_register():
    """调试接口：完整注册流程，捕获所有错误"""
    try:
        from app.database import async_session
        from app.services import employer_service
        async with async_session() as db:
            employer = await employer_service.register(
                db, "DebugCorp", "91110000MA00DEBUG01", "debug@corp.com", "Test123456"
            )
            return {"status": "ok", "employer_id": employer.id, "api_key": employer.api_key}
    except Exception as e:
        import traceback
        return {"status": "error", "error": str(e), "error_type": type(e).__name__, "traceback": traceback.format_exc()}
