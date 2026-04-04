"""FastAPI应用入口"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
