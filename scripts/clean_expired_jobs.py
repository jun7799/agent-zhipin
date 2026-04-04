"""清理过期岗位脚本"""

import asyncio
import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import update
from app.database import async_session
from app.models.job import Job


async def clean_expired():
    """将已过期的active岗位设为expired"""
    now = datetime.now(timezone.utc)
    async with async_session() as session:
        result = await session.execute(
            update(Job)
            .where(Job.status == "active", Job.expire_at < now)
            .values(status="expired")
        )
        await session.commit()
        count = result.rowcount
        print(f"[OK] 已清理 {count} 条过期岗位")


if __name__ == "__main__":
    asyncio.run(clean_expired())
