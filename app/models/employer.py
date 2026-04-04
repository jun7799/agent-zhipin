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
    api_key: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    api_key_secret: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # pending/approved/rejected/disabled
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    free_slots: Mapped[int] = mapped_column(Integer, nullable=False, default=6)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
