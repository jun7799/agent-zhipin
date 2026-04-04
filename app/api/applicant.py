"""应聘方接口路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import applicant_service
from app.schemas.applicant import (
    ApplicantRegisterRequest,
    ApplicantLoginRequest,
)
from app.utils.response import success, error

router = APIRouter()


@router.post("/register")
async def register(req: ApplicantRegisterRequest, db: AsyncSession = Depends(get_db)):
    """应聘方注册"""
    try:
        data = await applicant_service.register(db, req.email, req.password)
        return success(data, 201)
    except ValueError as e:
        return error("VALIDATION_ERROR", str(e), 400)


@router.post("/login")
async def login(req: ApplicantLoginRequest, db: AsyncSession = Depends(get_db)):
    """应聘方登录"""
    try:
        data = await applicant_service.login(db, req.email, req.password)
        return success(data)
    except ValueError as e:
        return error("AUTH_ERROR", str(e), 401)
