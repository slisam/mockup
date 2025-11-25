"""Pytest configuration and fixtures."""
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Force local mode for tests
os.environ['MODE'] = 'local'

from app.core.db.session import Base
from app.main import app
from app.core.db.session import get_db
from app.models.transformations import Transformation  # Import model to register with Base.metadata
from app.api.routes.transformations import get_transformations_service
from app.services.transformations import TransformationsService


@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test."""
    # Use file-based SQLite for tests to avoid connection issues
    import tempfile
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False}
    )

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        engine.dispose()
        os.close(db_fd)
        os.unlink(db_path)


@pytest.fixture(scope="function")
def client(test_db):
    """Create a test client with overridden DB dependency."""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    def override_get_transformations_service():
        return TransformationsService(db=test_db)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_transformations_service] = override_get_transformations_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_transformation_data():
    """Sample transformation input data."""
    return {
        "carrier": "MSC",
        "trade_lane": "EU-US",
        "dates": [
            {
                "application_date": "2024-01-01",
                "validity_date": "2024-12-31"
            }
        ]
    }
