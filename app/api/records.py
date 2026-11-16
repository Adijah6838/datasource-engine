import io
import csv
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.record import IngestionRecord
from app.schemas.schemas import RecordRead

router = APIRouter(prefix="/records", tags=["Records"])

@router.get("/", response_model=list[RecordRead])
def list_records(status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(IngestionRecord)
    if status:
        query = query.filter(IngestionRecord.status == status)
    return query.limit(100).all()

@router.get("/export")
def export_records(db: Session = Depends(get_db)):
    records = db.query(IngestionRecord).filter(IngestionRecord.status == "valid").all()
    if not records:
        raise HTTPException(status_code=404, detail="No valid records found")
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=records[0].raw_data.keys())
    writer.writeheader()
    for r in records:
        writer.writerow(r.raw_data)
    
    output.seek(0)
    return StreamingResponse(iter([output.getvalue()]), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=export.csv"})