"""招聘方接口路由"""

from datetime import datetime

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import employer_service, job_service
from app.schemas.employer import EmployerRegisterRequest, EmployerLoginRequest
from app.schemas.job import JobCreateRequest, JobUpdateRequest
from app.utils.response import success, error

router = APIRouter()


async def _get_employer(authorization: str | None, db: AsyncSession):
    """通过API Key获取当前招聘方，失败返回None"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    api_key = authorization[7:]
    employer = await employer_service.get_by_api_key(db, api_key)
    if not employer or employer.status != "approved":
        return None
    return employer


@router.post("/register")
async def register(req: EmployerRegisterRequest, db: AsyncSession = Depends(get_db)):
    """招聘方注册"""
    try:
        employer = await employer_service.register(
            db, req.company_name, req.credit_code, req.email, req.password
        )
        return success(
            {
                "id": employer.id,
                "company_name": employer.company_name,
                "status": employer.status,
                "api_key": employer.api_key,
                "message": "注册成功，API Key已发放",
            },
            201,
        )
    except ValueError as e:
        return error("VALIDATION_ERROR", str(e), 400)


@router.post("/login")
async def login(req: EmployerLoginRequest, db: AsyncSession = Depends(get_db)):
    """招聘方登录"""
    try:
        data = await employer_service.login(db, req.email, req.password)
        return success(data)
    except ValueError as e:
        return error("AUTH_ERROR", str(e), 401)


@router.get("/profile")
async def profile(
    authorization: str = Header(None), db: AsyncSession = Depends(get_db)
):
    """获取招聘方账户信息"""
    employer = await _get_employer(authorization, db)
    if not employer:
        return error("AUTH_ERROR", "API Key无效或账号未审核", 401)

    try:
        data = await employer_service.get_profile(db, employer.id)
        return success(data)
    except ValueError as e:
        return error("NOT_FOUND", str(e), 404)


@router.post("/jobs")
async def create_job(
    req: JobCreateRequest,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """发布岗位"""
    employer = await _get_employer(authorization, db)
    if not employer:
        return error("AUTH_ERROR", "API Key无效或账号未审核", 401)

    job_data = {
        "title": req.title,
        "city": req.city,
        "salary_min": req.salary_min,
        "salary_max": req.salary_max,
        "job_type": req.job_type,
        "description": req.description,
        "contact_email": req.contact_email,
        "education": req.education,
        "experience": req.experience,
        "contact_wechat": req.contact_wechat,
        "contact_phone": req.contact_phone,
        "company_scale": req.company_scale,
        "industry": req.industry,
        "expire_at": req.expire_at,
    }

    try:
        job = await job_service.create_job(db, employer, job_data, req.tags)
        return success(
            {
                "id": job.id,
                "title": job.title,
                "status": job.status,
                "published_at": (
                    job.published_at.isoformat() if job.published_at else None
                ),
                "deducted_slots": 1,
                "remaining_slots": employer.free_slots,
            },
            201,
        )
    except ValueError as e:
        if "额度" in str(e):
            return error("SLOTS_EXHAUSTED", str(e), 402)
        return error("VALIDATION_ERROR", str(e), 400)


@router.put("/jobs/{job_id}")
async def update_job(
    job_id: str,
    req: JobUpdateRequest,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """更新岗位"""
    employer = await _get_employer(authorization, db)
    if not employer:
        return error("AUTH_ERROR", "API Key无效", 401)

    update_data = {
        k: v
        for k, v in {
            "title": req.title,
            "city": req.city,
            "salary_min": req.salary_min,
            "salary_max": req.salary_max,
            "job_type": req.job_type,
            "description": req.description,
            "contact_email": req.contact_email,
            "education": req.education,
            "experience": req.experience,
            "contact_wechat": req.contact_wechat,
            "contact_phone": req.contact_phone,
            "company_scale": req.company_scale,
            "industry": req.industry,
            "expire_at": req.expire_at,
        }.items()
        if v is not None
    }

    try:
        job = await job_service.update_job(
            db, job_id, employer.id, update_data, req.tags
        )
        return success(
            {
                "id": job.id,
                "title": job.title,
                "updated_at": (
                    job.updated_at.isoformat() if job.updated_at else None
                ),
            }
        )
    except ValueError as e:
        return error("NOT_FOUND", str(e), 404)


@router.delete("/jobs/{job_id}")
async def delete_job(
    job_id: str,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """删除岗位"""
    employer = await _get_employer(authorization, db)
    if not employer:
        return error("AUTH_ERROR", "API Key无效", 401)

    try:
        job = await job_service.delete_job(db, job_id, employer.id)
        return success({"id": job.id, "message": "岗位已删除"})
    except ValueError as e:
        return error("NOT_FOUND", str(e), 404)


@router.patch("/jobs/{job_id}/expire")
async def expire_job(
    job_id: str,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """设为过期"""
    employer = await _get_employer(authorization, db)
    if not employer:
        return error("AUTH_ERROR", "API Key无效", 401)

    try:
        job = await job_service.expire_job(db, job_id, employer.id)
        return success({"id": job.id, "status": "expired", "message": "岗位已设为过期"})
    except ValueError as e:
        return error("NOT_FOUND", str(e), 404)


@router.get("/jobs")
async def list_my_jobs(
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """查看自己的岗位列表"""
    employer = await _get_employer(authorization, db)
    if not employer:
        return error("AUTH_ERROR", "API Key无效", 401)

    data = await job_service.get_employer_jobs(
        db, employer.id, page, page_size, status
    )
    return success(data)
