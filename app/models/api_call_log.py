"""API调用日志模型 - 限流依据"""

import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ApiCallLog(Base):
    __tablename__ = "api_call_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # employer/applicant/anonymous
    caller_type: Mapped[str] = mapped_column(String(20), nullable=False)
    caller_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    endpoint: Mapped[str] = mapped_column(String(200), nullable=False)
    api_key_used: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )
