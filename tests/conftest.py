import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app as fastapi_app
from app.db.base import Base
from app.db.session import get_db

# Import models to ensure they are registered
import app.models.source
import app.models.record
import app.models.job
import app.models.checkpoint

# Import the jobs module so we can patch its SessionLocal
import app.api.jobs as jobs_module

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session, monkeypatch):
    # Patch the SessionLocal in jobs.py to point to the test database
    monkeypatch.setattr(jobs_module, "SessionLocal", TestingSessionLocal)
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    fastapi_app.dependency_overrides[get_db] = override_get_db
    with TestClient(fastapi_app) as c:
        yield c
    fastapi_app.dependency_overrides.clear()