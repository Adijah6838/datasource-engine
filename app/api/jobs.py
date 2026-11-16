import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.session import get_db, SessionLocal
from app.models.job import IngestionJob
from app.models.source import DataSource
from app.schemas.schemas import JobCreate, JobRead
from app.services.ingest import run_ingestion_job

router = APIRouter(prefix="/jobs", tags=["Jobs"])

def run_job_in_background(job_id: uuid.UUID):
    db = SessionLocal()
    try:
        run_ingestion_job(job_id, db)
    finally:
        db.close()

@router.post("/", response_model=JobRead)
def trigger_job(job: JobCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    source = db.query(DataSource).filter(DataSource.id == job.source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    
    new_job = IngestionJob(source_id=source.id, status="pending")
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    
    # Run the ingestion in the background so the API responds immediately
    background_tasks.add_task(run_job_in_background, new_job.id)
    
    return new_job

@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: uuid.UUID, db: Session = Depends(get_db)):
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job