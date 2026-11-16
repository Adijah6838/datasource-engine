import time
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.source import DataSource
from app.models.record import IngestionRecord
from app.models.job import IngestionJob
from app.models.checkpoint import Checkpoint
from app.services.parsers import parse_csv, parse_json

def retry_on_exception(func, max_retries=3, delay=1.0):
    """Helper to retry transient failures."""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(delay)

def run_ingestion_job(job_id: uuid.UUID, db: Session):
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    if not job:
        return

    source = db.query(DataSource).filter(DataSource.id == job.source_id).first()
    if not source:
        job.status = "failed"
        db.commit()
        return

    job.status = "running"
    db.commit()

    # Fetch config
    file_path = source.config.get("path")
    id_field = source.config.get("id_field", "id")
    pagination = source.config.get("pagination", None)

    # Fetch checkpoint
    checkpoint = db.query(Checkpoint).filter(Checkpoint.source_id == source.id).first()

    try:
        # Select parser
        if source.source_type == "csv":
            parser = parse_csv
        elif source.source_type == "json":
            parser = parse_json
        else:
            raise ValueError(f"Unsupported source type: {source.source_type}")

        processed = 0
        rejected = 0
        last_cursor = None

        # Retry reading the file
        records = retry_on_exception(lambda: list(parser(file_path, pagination)))

        for row in records:
            # Extract ID
            ext_id = str(row.get(id_field, "")).strip()

            if not ext_id:
                rejected += 1
                # Save rejected record (use random UUID as external_id to avoid unique constraint issues)
                db.add(IngestionRecord(
                    source_id=source.id, external_id=str(uuid.uuid4()),
                    raw_data=row, status="rejected", rejection_reason=f"Missing ID field: {id_field}"
                ))
                continue

            # Idempotency check (Optional here since DB UniqueConstraint handles it, but good for speed)
            existing = db.query(IngestionRecord).filter(
                IngestionRecord.source_id == source.id,
                IngestionRecord.external_id == ext_id
            ).first()

            if existing:
                continue # Skip duplicate silently

            # Save valid
            db.add(IngestionRecord(
                source_id=source.id, external_id=ext_id,
                raw_data=row, status="valid"
            ))
            processed += 1
            last_cursor = ext_id

        # Update Checkpoint if we processed new records
        if last_cursor:
            if not checkpoint:
                checkpoint = Checkpoint(source_id=source.id, cursor_value=last_cursor)
                db.add(checkpoint)
            else:
                checkpoint.cursor_value = last_cursor

        job.total_processed = processed
        job.total_rejected = rejected
        job.status = "completed"
        job.finished_at = datetime.utcnow()
        db.commit()

    except Exception as e:
        db.rollback()
        job.status = "failed"
        job.finished_at = datetime.utcnow()
        db.commit()
        print(f"Job failed: {str(e)}")