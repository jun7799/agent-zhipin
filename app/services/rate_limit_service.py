"""限流业务逻辑 - 简化版，防滥用"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_call_log import ApiCallLog

# 限额配置
LIMITS = {
    "anonymous": 5,       # 匿名用户 5次/天
    "applicant": 50,      # 注册求职者 50次/天
    "employer_query": 50, # 招聘方查询 50次/天
    "employer_post": 50,  # 招聘方发布 50个/天
}


async def check_query_limit(
    db: AsyncSession,
    ip_address: str,
    caller_type: str = "anonymous",
    caller_id: str | None = None,
) -> dict:
    """
    检查查询限流
    返回: {"allowed": bool, "limit": int, "used": int, "remaining": int}
    """
    if caller_type == "anonymous":
        limit = LIMITS["anonymous"]
    elif caller_type in ("applicant", "employer"):
        limit = LIMITS["employer_query"] if caller_type == "employer" else LIMITS["applicant"]
    else:
        limit = LIMITS["anonymous"]

    used = await _count_today(db, ip_address, caller_type, caller_id, action="query")
    return {
        "allowed": used < limit,
        "limit": limit,
        "used": used,
        "remaining": max(0, limit - used),
    }


async def check_post_limit(
    db: AsyncSession,
    caller_id: str,
) -> dict:
    """检查招聘方发布岗位限制（50个/天）"""
    limit = LIMITS["employer_post"]
    used = await _count_today(db, "", "employer", caller_id, action="post")
    return {
        "allowed": used < limit,
        "limit": limit,
        "used": used,
        "remaining": max(0, limit - used),
    }


async def record_query(
    db: AsyncSession,
    ip_address: str,
    endpoint: str,
    caller_type: str,
    caller_id: str | None = None,
):
    """记录一次查询调用"""
    log = ApiCallLog(
        id=str(uuid.uuid4()),
        caller_type=caller_type,
        caller_id=caller_id,
        ip_address=ip_address,
        endpoint=endpoint,
    )
    db.add(log)
    await db.flush()


async def record_post(
    db: AsyncSession,
    caller_id: str,
    endpoint: str = "/v1/employer/jobs",
):
    """记录一次岗位发布"""
    log = ApiCallLog(
        id=str(uuid.uuid4()),
        caller_type="employer",
        caller_id=caller_id,
        ip_address="",
        endpoint=endpoint,
    )
    db.add(log)
    await db.flush()


async def _count_today(
    db: AsyncSession,
    ip_address: str,
    caller_type: str,
    caller_id: str | None,
    action: str = "query",
) -> int:
    """统计今日调用次数"""
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    query = select(func.count()).select_from(ApiCallLog).where(
        ApiCallLog.created_at >= today_start,
        ApiCallLog.caller_type == caller_type,
    )

    if action == "query":
        if caller_id:
            query = query.where(ApiCallLog.caller_id == caller_id)
        else:
            query = query.where(ApiCallLog.ip_address == ip_address)
    elif action == "post":
        query = query.where(
            ApiCallLog.caller_id == caller_id,
            ApiCallLog.endpoint == "/v1/employer/jobs",
        )

    return (await db.execute(query)).scalar() or 0
