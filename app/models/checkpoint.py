import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Checkpoint(Base):
    __tablename__ = "checkpoints"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("data_sources.id"), unique=True)
    cursor_value: Mapped[str] = mapped_column(String(255)) # e.g., last processed page, or last timestamp
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())