"""FastAPI应用入口"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.config import settings
from app.database import init_db
from app.api.router import api_router

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


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
    """引导页"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/qrcode.jpg")
async def qrcode():
    """收款码图片"""
    return FileResponse(os.path.join(STATIC_DIR, "qrcode.jpg"), media_type="image/jpeg")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/skills/seeker.md")
async def seeker_skill():
    """求职者Skill文件"""
    return FileResponse(
        os.path.join(STATIC_DIR, "skills", "seeker.md"),
        media_type="text/markdown",
    )


@app.get("/skills/employer.md")
async def employer_skill():
    """招聘方Skill文件"""
    return FileResponse(
        os.path.join(STATIC_DIR, "skills", "employer.md"),
        media_type="text/markdown",
    )
