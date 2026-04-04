"""岗位-标签关联模型"""

import uuid

from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class JobTag(Base):
    __tablename__ = "job_tags"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    tag_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tags.id"), nullable=False
    )

    # 关系
    job: Mapped["Job"] = relationship("Job", back_populates="tags")
    tag: Mapped["Tag"] = relationship("Tag")

    __table_args__ = (UniqueConstraint("job_id", "tag_id", name="uq_job_tag"),)
