"""标签和城市接口"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.tag import Tag
from app.models.job import Job
from app.utils.response import success

router = APIRouter()


@router.get("/tags")
async def list_tags(
    category: str | None = None, db: AsyncSession = Depends(get_db)
):
    """获取标签列表"""
    query = select(Tag).order_by(Tag.sort_order)
    if category:
        query = query.where(Tag.category == category)

    result = await db.execute(query)
    tags = result.scalars().all()

    return success(
        {
            "tags": [
                {"id": t.id, "name": t.name, "category": t.category} for t in tags
            ]
        }
    )


@router.get("/cities")
async def list_cities(db: AsyncSession = Depends(get_db)):
    """获取城市列表（从已有岗位中提取）"""
    query = select(Job.city).where(Job.status == "active").distinct()
    result = await db.execute(query)
    cities = sorted([row[0] for row in result.all()])

    return success({"cities": cities})
