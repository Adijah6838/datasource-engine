from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.source import DataSource
from app.schemas.schemas import SourceCreate, SourceRead

router = APIRouter(prefix="/sources", tags=["Sources"])

@router.post("/", response_model=SourceRead)
def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    existing = db.query(DataSource).filter(DataSource.name == source.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Source name already exists")
    new_source = DataSource(name=source.name, source_type=source.source_type, config=source.config)
    db.add(new_source)
    db.commit()
    db.refresh(new_source)
    return new_source

@router.get("/", response_model=list[SourceRead])
def list_sources(db: Session = Depends(get_db)):
    return db.query(DataSource).all()