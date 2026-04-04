"""岗位信息模型"""

import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    employer_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("employers.id"), nullable=False
    )

    # 基本字段
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    company_name: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    salary_min: Mapped[int] = mapped_column(Integer, nullable=False)
    salary_max: Mapped[int] = mapped_column(Integer, nullable=False)
    education: Mapped[str | None] = mapped_column(String(20), nullable=True)
    experience: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # fulltime/parttime/remote
    job_type: Mapped[str] = mapped_column(String(20), nullable=False)

    # 详细信息
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # 联系方式
    contact_email: Mapped[str] = mapped_column(String(200), nullable=False)
    contact_wechat: Mapped[str | None] = mapped_column(String(100), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # 附加信息
    company_scale: Mapped[str | None] = mapped_column(String(50), nullable=True)
    industry: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # 状态与时间
    # active/expired/deleted
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    published_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )
    expire_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # 关系
    tags: Mapped[list["JobTag"]] = relationship(
        "JobTag", back_populates="job", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_jobs_query", "status", "city", "job_type", "published_at"),
        Index("idx_jobs_employer", "employer_id"),
    )
