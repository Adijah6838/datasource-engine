import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict

# --- Source Schemas ---
class SourceCreate(BaseModel):
    name: str
    source_type: str
    config: dict

class SourceRead(SourceCreate):
    id: uuid.UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Job Schemas ---
class JobCreate(BaseModel):
    source_id: uuid.UUID

class JobRead(BaseModel):
    id: uuid.UUID
    source_id: uuid.UUID
    status: str
    total_processed: int
    total_rejected: int
    started_at: datetime
    finished_at: datetime | None
    model_config = ConfigDict(from_attributes=True)

# --- Record Schemas ---
class RecordRead(BaseModel):
    id: uuid.UUID
    external_id: str
    raw_data: dict
    status: str
    rejection_reason: str | None
    model_config = ConfigDict(from_attributes=True)