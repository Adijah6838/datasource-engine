import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class DataSource(Base):
    __tablename__ = "data_sources"
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    source_type: Mapped[str] = mapped_column(String(50)) # "csv" or "json"
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())