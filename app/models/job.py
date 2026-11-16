import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("data_sources.id"))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    total_processed: Mapped[int] = mapped_column(Integer, default=0)
    total_rejected: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)