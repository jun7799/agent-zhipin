"""数据库连接与会话管理"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# PostgreSQL需要连接池配置，SQLite不需要
is_postgres = settings.DATABASE_URL.startswith("postgresql")

engine_kwargs = {"echo": settings.DEBUG}
if is_postgres:
    # 去掉URL中的sslmode参数，通过connect_args传SSL
    db_url = settings.DATABASE_URL.split("?")[0]
    engine_kwargs.update({
        "pool_size": 5,
        "max_overflow": 10,
        "pool_pre_ping": True,
        "connect_args": {"ssl": True},
    })
else:
    db_url = settings.DATABASE_URL

engine = create_async_engine(db_url, **engine_kwargs)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """FastAPI依赖注入：获取数据库会话"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    """初始化数据库（创建所有表）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
