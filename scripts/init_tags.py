"""初始化标签种子数据"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import async_session, init_db
from app.models.tag import Tag


SEED_TAGS = [
    # 行业标签
    ("互联网/IT", "industry", 1),
    ("金融", "industry", 2),
    ("教育", "industry", 3),
    ("医疗健康", "industry", 4),
    ("制造业", "industry", 5),
    ("电商/零售", "industry", 6),
    ("AI/人工智能", "industry", 7),
    ("游戏", "industry", 8),
    ("新能源", "industry", 9),
    ("物流/供应链", "industry", 10),
    ("房产/建筑", "industry", 11),
    ("文化/传媒", "industry", 12),
    # 职位类型标签
    ("技术开发", "job_category", 1),
    ("产品经理", "job_category", 2),
    ("UI/UX设计", "job_category", 3),
    ("数据分析", "job_category", 4),
    ("运营", "job_category", 5),
    ("市场/营销", "job_category", 6),
    ("人事/行政", "job_category", 7),
    ("财务", "job_category", 8),
    ("法务", "job_category", 9),
    ("客服", "job_category", 10),
    ("销售", "job_category", 11),
    ("项目管理", "job_category", 12),
    ("算法/AI", "job_category", 13),
    ("测试/QA", "job_category", 14),
    ("运维/DevOps", "job_category", 15),
]


async def main():
    print("[INFO] 初始化数据库...")
    await init_db()

    print("[INFO] 插入标签数据...")
    async with async_session() as session:
        for name, category, sort_order in SEED_TAGS:
            from sqlalchemy import select

            existing = await session.execute(
                select(Tag).where(Tag.name == name)
            )
            if existing.scalar_one_or_none():
                print(f"  [SKIP] {name} 已存在")
                continue

            tag = Tag(name=name, category=category, sort_order=sort_order)
            session.add(tag)
            print(f"  [ADD] {name} ({category})")

        await session.commit()

    print("[OK] 标签数据初始化完成")


if __name__ == "__main__":
    asyncio.run(main())
