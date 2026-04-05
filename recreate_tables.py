"""重建数据库表 - 支持timezone"""
import asyncio
from app.database import engine, Base, init_db
from sqlalchemy import text


async def recreate():
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f'DROP TABLE IF EXISTS {table.name} CASCADE'))
    print('All tables dropped')
    await init_db()
    print('Tables recreated')
asyncio.run(recreate())
