"""应聘方业务逻辑"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password, create_access_token
from app.config import settings
from app.models.applicant import Applicant


async def register(db: AsyncSession, email: str, password: str) -> dict:
    """应聘方注册"""
    existing = await db.execute(select(Applicant).where(Applicant.email == email))
    if existing.scalar_one_or_none():
        raise ValueError("该邮箱已注册")

    applicant = Applicant(
        email=email,
        password_hash=hash_password(password),
    )
    db.add(applicant)
    await db.flush()

    token = create_access_token(
        {"sub": applicant.id, "type": "applicant", "email": applicant.email}
    )
    return {
        "id": applicant.id,
        "email": applicant.email,
        "daily_limit": settings.RATE_LIMIT_REGISTERED,
        "message": "注册成功",
        "token": token,
    }


async def login(db: AsyncSession, email: str, password: str) -> dict:
    """应聘方登录"""
    result = await db.execute(select(Applicant).where(Applicant.email == email))
    applicant = result.scalar_one_or_none()
    if not applicant or not verify_password(password, applicant.password_hash):
        raise ValueError("邮箱或密码错误")

    # 判断会员是否过期
    from datetime import datetime, timezone

    is_member = applicant.is_member and (
        applicant.member_expire_at
        and applicant.member_expire_at > datetime.now(timezone.utc)
    )

    if is_member:
        daily_limit = settings.RATE_LIMIT_MEMBER
    else:
        daily_limit = settings.RATE_LIMIT_REGISTERED

    token = create_access_token(
        {
            "sub": applicant.id,
            "type": "applicant",
            "email": applicant.email,
            "is_member": is_member,
        }
    )
    return {
        "id": applicant.id,
        "email": applicant.email,
        "is_member": is_member,
        "member_expire_at": (
            applicant.member_expire_at.isoformat()
            if applicant.member_expire_at
            else None
        ),
        "daily_limit": daily_limit,
        "token": token,
    }


async def get_by_id(db: AsyncSession, applicant_id: str) -> Applicant | None:
    """根据ID获取应聘方"""
    result = await db.execute(select(Applicant).where(Applicant.id == applicant_id))
    return result.scalar_one_or_none()
