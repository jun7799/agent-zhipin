"""岗位业务逻辑"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.job import Job
from app.models.tag import Tag
from app.models.job_tag import JobTag
from app.models.employer import Employer


async def create_job(
    db: AsyncSession,
    employer: Employer,
    job_data: dict,
    tag_names: list[str] | None = None,
) -> Job:
    """发布岗位"""
    # 检查免费额度
    if employer.free_slots <= 0:
        raise ValueError(
            "免费发布额度已用完，请购买额外发布次数"
        )

    job = Job(
        employer_id=employer.id,
        company_name=employer.company_name,
        title=job_data["title"],
        city=job_data["city"],
        salary_min=job_data["salary_min"],
        salary_max=job_data["salary_max"],
        education=job_data.get("education"),
        experience=job_data.get("experience"),
        job_type=job_data["job_type"],
        description=job_data["description"],
        contact_email=job_data["contact_email"],
        contact_wechat=job_data.get("contact_wechat"),
        contact_phone=job_data.get("contact_phone"),
        company_scale=job_data.get("company_scale"),
        industry=job_data.get("industry"),
        expire_at=job_data.get("expire_at"),
    )
    db.add(job)

    # 扣减免费额度
    employer.free_slots -= 1

    await db.flush()

    # 处理标签
    if tag_names:
        await _add_tags_to_job(db, job.id, tag_names)

    return job


async def update_job(
    db: AsyncSession,
    job_id: str,
    employer_id: str,
    update_data: dict,
    tag_names: list[str] | None = None,
) -> Job:
    """更新岗位"""
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.employer_id == employer_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise ValueError("岗位不存在或无权操作")
    if job.status == "deleted":
        raise ValueError("已删除的岗位无法更新")

    # 更新字段
    for key, value in update_data.items():
        if value is not None and hasattr(job, key):
            setattr(job, key, value)

    await db.flush()

    # 更新标签
    if tag_names is not None:
        # 先删除旧标签
        from sqlalchemy import delete

        await db.execute(delete(JobTag).where(JobTag.job_id == job_id))
        await _add_tags_to_job(db, job_id, tag_names)

    return job


async def delete_job(db: AsyncSession, job_id: str, employer_id: str) -> Job:
    """删除岗位（软删除）"""
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.employer_id == employer_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise ValueError("岗位不存在或无权操作")

    job.status = "deleted"
    await db.flush()
    return job


async def expire_job(db: AsyncSession, job_id: str, employer_id: str) -> Job:
    """设为过期"""
    result = await db.execute(
        select(Job).where(Job.id == job_id, Job.employer_id == employer_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise ValueError("岗位不存在或无权操作")

    job.status = "expired"
    await db.flush()
    return job


async def get_employer_jobs(
    db: AsyncSession,
    employer_id: str,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
) -> dict:
    """获取招聘方自己的岗位列表"""
    query = select(Job).where(Job.employer_id == employer_id)
    count_query = select(func.count()).select_from(Job).where(
        Job.employer_id == employer_id
    )

    if status:
        query = query.where(Job.status == status)
        count_query = count_query.where(Job.status == status)

    # 总数
    total = (await db.execute(count_query)).scalar() or 0

    # 分页
    offset = (page - 1) * page_size
    query = query.order_by(Job.published_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    jobs = result.scalars().all()

    return {
        "jobs": [_job_to_dict(j) for j in jobs],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


async def search_jobs(
    db: AsyncSession,
    city: str | None = None,
    salary_min: int | None = None,
    salary_max: int | None = None,
    job_type: str | None = None,
    keyword: str | None = None,
    experience: str | None = None,
    tags: list[str] | None = None,
    page: int = 1,
    page_size: int = 10,
) -> dict:
    """搜索岗位（核心查询接口）"""
    now = datetime.now(timezone.utc)
    conditions = [Job.status == "active"]

    # 自动过滤过期岗位
    conditions.append(or_(Job.expire_at.is_(None), Job.expire_at > now))

    if city:
        conditions.append(Job.city == city)
    if salary_min is not None:
        conditions.append(Job.salary_max >= salary_min)
    if salary_max is not None:
        conditions.append(Job.salary_min <= salary_max)
    if job_type:
        conditions.append(Job.job_type == job_type)
    if keyword:
        conditions.append(
            or_(
                Job.title.contains(keyword),
                Job.description.contains(keyword),
            )
        )
    if experience:
        conditions.append(Job.experience == experience)

    where_clause = and_(*conditions)

    # 如果有标签筛选
    if tags:
        tag_subquery = (
            select(JobTag.job_id)
            .join(Tag)
            .where(Tag.name.in_(tags))
            .group_by(JobTag.job_id)
        )
        query = select(Job).where(where_clause, Job.id.in_(tag_subquery))
        count_query = (
            select(func.count())
            .select_from(Job)
            .where(where_clause, Job.id.in_(tag_subquery))
        )
    else:
        query = select(Job).where(where_clause)
        count_query = select(func.count()).select_from(Job).where(where_clause)

    total = (await db.execute(count_query)).scalar() or 0

    offset = (page - 1) * page_size
    query = query.order_by(Job.published_at.desc()).offset(offset).limit(page_size)
    result = await db.execute(query)
    jobs = result.scalars().all()

    # 获取每个岗位的标签
    job_list = []
    for job in jobs:
        job_dict = _job_to_dict(job)
        # 查询标签
        tag_result = await db.execute(
            select(Tag.name)
            .join(JobTag)
            .where(JobTag.job_id == job.id)
        )
        job_dict["tags"] = [t[0] for t in tag_result.all()]
        job_list.append(job_dict)

    return {
        "jobs": job_list,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": total > offset + page_size,
    }


async def get_job_by_id(db: AsyncSession, job_id: str) -> dict | None:
    """获取单个岗位详情"""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(Job).where(
            Job.id == job_id,
            Job.status == "active",
            or_(Job.expire_at.is_(None), Job.expire_at > now),
        )
    )
    job = result.scalar_one_or_none()
    if not job:
        return None

    job_dict = _job_to_dict(job)
    tag_result = await db.execute(
        select(Tag.name).join(JobTag).where(JobTag.job_id == job.id)
    )
    job_dict["tags"] = [t[0] for t in tag_result.all()]
    return job_dict


async def _add_tags_to_job(db: AsyncSession, job_id: str, tag_names: list[str]):
    """给岗位添加标签"""
    for name in tag_names:
        result = await db.execute(select(Tag).where(Tag.name == name))
        tag = result.scalar_one_or_none()
        if tag:
            job_tag = JobTag(
                id=str(uuid.uuid4()), job_id=job_id, tag_id=tag.id
            )
            db.add(job_tag)
    await db.flush()


def _job_to_dict(job: Job) -> dict:
    """Job模型转字典"""
    return {
        "id": job.id,
        "employer_id": job.employer_id,
        "title": job.title,
        "company_name": job.company_name,
        "city": job.city,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "education": job.education,
        "experience": job.experience,
        "job_type": job.job_type,
        "description": job.description,
        "contact_email": job.contact_email,
        "contact_wechat": job.contact_wechat,
        "contact_phone": job.contact_phone,
        "company_scale": job.company_scale,
        "industry": job.industry,
        "status": job.status,
        "published_at": job.published_at.isoformat() if job.published_at else None,
        "expire_at": job.expire_at.isoformat() if job.expire_at else None,
    }
