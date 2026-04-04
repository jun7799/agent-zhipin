"""限流业务逻辑"""

from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_call_log import ApiCallLog
from app.config import settings


async def check_rate_limit(
    db: AsyncSession,
    ip_address: str,
    caller_type: str,
    caller_id: str | None = None,
    is_member: bool = False,
) -> dict:
    """
    检查限流，返回限流信息
    返回: {"allowed": bool, "limit": int, "used": int, "remaining": int}
    """
    # 确定限额
    if caller_type == "employer":
        limit = 999999  # 招聘方不限查询
    elif is_member:
        limit = settings.RATE_LIMIT_MEMBER
    elif caller_id:
        limit = settings.RATE_LIMIT_REGISTERED
    else:
        limit = settings.RATE_LIMIT_ANONYMOUS

    # 查询今日已用次数
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    query = select(func.count()).select_from(ApiCallLog).where(
        ApiCallLog.created_at >= today_start
    )

    if caller_id:
        query = query.where(ApiCallLog.caller_id == caller_id)
    else:
        query = query.where(ApiCallLog.ip_address == ip_address)

    used = (await db.execute(query)).scalar() or 0

    return {
        "allowed": used < limit,
        "limit": limit,
        "used": used,
        "remaining": max(0, limit - used),
    }


async def record_call(
    db: AsyncSession,
    ip_address: str,
    endpoint: str,
    caller_type: str,
    caller_id: str | None = None,
    api_key_used: str | None = None,
):
    """记录一次API调用"""
    import uuid

    log = ApiCallLog(
        id=str(uuid.uuid4()),
        caller_type=caller_type,
        caller_id=caller_id,
        ip_address=ip_address,
        endpoint=endpoint,
        api_key_used=api_key_used,
    )
    db.add(log)
    await db.flush()
