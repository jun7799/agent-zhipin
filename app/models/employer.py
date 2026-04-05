"""招聘方模型"""

import uuid
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Employer(Base):
    __tablename__ = "employers"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    company_name: Mapped[str] = mapped_column(String(200), nullable=False)
    credit_code: Mapped[str] = mapped_column(String(18), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    api_key: Mapped[str | None] = mapped_column(String(128), unique=True, nullable=True)
    api_key_secret: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # pending/approved/rejected/disabled
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")

    # 岗位额度：免费3个 + 单条购买的额外额度
    free_slots: Mapped[int] = mapped_column(Integer, nullable=False, default=3)

    # 订阅类型: free/monthly/yearly
    subscription_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="free"
    )
    subscription_expire_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # 当月已发布岗位数（包月/包年用）
    period_jobs_posted: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # 当前计费周期起始时间
    period_start_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )
