from fastapi import FastAPI
from app.core.config import settings
from app.api import sources, jobs, records

app = FastAPI(title=settings.app_name)

app.include_router(sources.router)
app.include_router(jobs.router)
app.include_router(records.router)

@app.get("/health")
def health():
    return {"status": "ok"}