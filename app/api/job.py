"""岗位查询接口路由 - 带限流防滥用"""

from fastapi import APIRouter, Depends, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services import job_service, rate_limit_service
from app.core.security import decode_access_token
from app.utils.response import success, error

router = APIRouter()


async def _get_caller_info(
    request: Request, authorization: str | None = None
) -> dict:
    """获取调用者信息"""
    ip = request.headers.get("X-Real-IP") or request.headers.get(
        "X-Forwarded-For", request.client.host if request.client else "unknown"
    )
    if "," in ip:
        ip = ip.split(",")[0].strip()

    caller_type = "anonymous"
    caller_id = None

    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        payload = decode_access_token(token)
        if payload and payload.get("type") == "applicant":
            caller_type = "applicant"
            caller_id = payload.get("sub")
        elif payload and payload.get("type") == "employer":
            caller_type = "employer"
            caller_id = payload.get("sub")

    return {
        "ip": ip,
        "caller_type": caller_type,
        "caller_id": caller_id,
    }


@router.get("/jobs/search")
async def search_jobs(
    request: Request,
    city: str | None = None,
    salary_min: int | None = None,
    salary_max: int | None = None,
    job_type: str | None = None,
    keyword: str | None = None,
    experience: str | None = None,
    tags: str | None = None,
    page: int = 1,
    page_size: int = 10,
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """搜索岗位（匿名5次/天，注册用户50次/天）"""
    caller = await _get_caller_info(request, authorization)

    rate_info = await rate_limit_service.check_query_limit(
        db, caller["ip"], caller["caller_type"], caller["caller_id"]
    )

    if not rate_info["allowed"]:
        return error(
            "RATE_LIMIT_EXCEEDED",
            "今日查询次数已用完，请明天再试，或注册账号获取更多次数",
            429,
            {"limit": rate_info["limit"], "used": rate_info["used"], "remaining": rate_info["remaining"]},
        )

    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None

    data = await job_service.search_jobs(
        db, city=city, salary_min=salary_min, salary_max=salary_max,
        job_type=job_type, keyword=keyword, experience=experience,
        tags=tag_list, page=page, page_size=min(page_size, 50),
    )

    await rate_limit_service.record_query(
        db, caller["ip"], "/v1/jobs/search", caller["caller_type"], caller["caller_id"]
    )

    return success(data, meta={"rate_limit": rate_info})


@router.get("/jobs/{job_id}")
async def get_job(
    job_id: str,
    request: Request,
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """获取单个岗位详情"""
    caller = await _get_caller_info(request, authorization)

    rate_info = await rate_limit_service.check_query_limit(
        db, caller["ip"], caller["caller_type"], caller["caller_id"]
    )

    if not rate_info["allowed"]:
        return error("RATE_LIMIT_EXCEEDED", "今日查询次数已用完", 429)

    data = await job_service.get_job_by_id(db, job_id)
    if not data:
        return error("NOT_FOUND", "岗位不存在", 404)

    await rate_limit_service.record_query(
        db, caller["ip"], f"/v1/jobs/{job_id}", caller["caller_type"], caller["caller_id"]
    )

    return success(data, meta={"rate_limit": rate_info})
