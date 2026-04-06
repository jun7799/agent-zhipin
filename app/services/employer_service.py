"""招聘方业务逻辑"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password, create_access_token
from app.core.api_key import generate_api_key, generate_api_key_secret
from app.models.employer import Employer
from app.models.job import Job
from app.utils.credit_code import validate_credit_code


async def register(
    db: AsyncSession, company_name: str, credit_code: str, email: str, password: str
) -> Employer:
    """招聘方注册"""
    if not validate_credit_code(credit_code):
        raise ValueError("统一社会信用代码格式不正确，需18位数字和大写字母")

    existing = await db.execute(select(Employer).where(Employer.email == email))
    if existing.scalar_one_or_none():
        raise ValueError("该邮箱已注册")

    existing = await db.execute(
        select(Employer).where(Employer.credit_code == credit_code)
    )
    if existing.scalar_one_or_none():
        raise ValueError("该信用代码已注册")

    employer = Employer(
        company_name=company_name,
        credit_code=credit_code,
        email=email,
        password_hash=hash_password(password),
        status="approved",
        api_key=generate_api_key(),
        api_key_secret=generate_api_key_secret(),
    )
    db.add(employer)
    await db.flush()
    return employer


async def login(db: AsyncSession, email: str, password: str) -> dict:
    """招聘方登录"""
    result = await db.execute(select(Employer).where(Employer.email == email))
    employer = result.scalar_one_or_none()
    if not employer or not verify_password(password, employer.password_hash):
        raise ValueError("邮箱或密码错误")

    token = create_access_token(
        {"sub": employer.id, "type": "employer", "email": employer.email}
    )
    return {
        "id": employer.id,
        "company_name": employer.company_name,
        "api_key": employer.api_key,
        "status": employer.status,
        "token": token,
    }


async def get_by_api_key(db: AsyncSession, api_key: str) -> Employer | None:
    """根据API Key获取招聘方"""
    result = await db.execute(select(Employer).where(Employer.api_key == api_key))
    return result.scalar_one_or_none()


async def get_profile(db: AsyncSession, employer_id: str) -> dict:
    """获取招聘方详细信息"""
    result = await db.execute(select(Employer).where(Employer.id == employer_id))
    employer = result.scalar_one_or_none()
    if not employer:
        raise ValueError("用户不存在")

    total_result = await db.execute(
        select(func.count()).select_from(Job).where(Job.employer_id == employer_id)
    )
    active_result = await db.execute(
        select(func.count()).select_from(Job).where(
            Job.employer_id == employer_id, Job.status == "active"
        )
    )
    total_jobs = total_result.scalar() or 0
    active_jobs = active_result.scalar() or 0

    return {
        "id": employer.id,
        "company_name": employer.company_name,
        "credit_code": employer.credit_code,
        "email": employer.email,
        "api_key": employer.api_key,
        "status": employer.status,
        "total_jobs": total_jobs,
        "active_jobs": active_jobs,
        "created_at": employer.created_at.isoformat() if employer.created_at else None,
    }
