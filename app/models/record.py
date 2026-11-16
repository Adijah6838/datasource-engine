import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func, ForeignKey, JSON, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class IngestionRecord(Base):
    __tablename__ = "ingestion_records"
    __table_args__ = (UniqueConstraint("source_id", "external_id", name="uq_source_external_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("data_sources.id"))
    external_id: Mapped[str] = mapped_column(String(255), index=True)
    raw_data: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(50)) # "valid" or "rejected"
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())