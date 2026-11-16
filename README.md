# DataSource — Configurable Data Ingestion Engine

A robust, idempotent data ingestion service built with Python, FastAPI, SQLAlchemy, and Pydantic.

## Features
- **Configurable Sources**: Register JSON and CSV data sources.
- **Idempotency**: Prevents duplicate records using database-level unique constraints.
- **Validation & Rejection**: Bad records are safely rejected and logged without stopping the job.
- **Background Processing**: Jobs run asynchronously using FastAPI `BackgroundTasks`.
- **Checkpoints**: Tracks the last processed cursor (ready for pagination).
- **Export**: Download processed valid records as a CSV.

## Schema Documentation
- `data_sources`: Stores configuration for the endpoints.
- `ingestion_jobs`: Tracks the status and metrics of each run.
- `ingestion_records`: The actual data payloads (valid and rejected).
- `checkpoints`: Stores cursor values to support incremental syncs.

## Quick Start
1. Activate virtual environment: `.\.venv\Scripts\Activate.ps1`
2. Run the server: `uvicorn app.main:app --reload`
3. Go to `http://127.0.0.1:8000/docs` to interact with the API.

## Running Tests
```bash
pytest tests/ -v