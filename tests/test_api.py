"""
Test suite for PE Compass API
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from app.database import get_db, Base
from app.models import (
    Goal, Vertical, SubVertical, Capability, Process,
    ProcessLevel, ProcessCategory, SubProcess, DataEntity, Application, API
)

# Create test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def seed_test_data():
    """Seed test data for testing."""
    db = TestingSessionLocal()

    # Create test data
    goal = Goal(name="Test Goal")
    db.add(goal)
    db.flush()

    vertical = Vertical(name="Test Vertical", goal_id=goal.id)
    db.add(vertical)
    db.flush()

    sub_vertical = SubVertical(name="Test Sub-Vertical", vertical_id=vertical.id)
    db.add(sub_vertical)
    db.flush()

    capability = Capability(
        name="Test Capability",
        description="Test Description",
        sub_vertical_id=sub_vertical.id,
    )
    db.add(capability)
    db.flush()

    process = Process(
        name="Test Process",
        description="Test Process Description",
        capability_id=capability.id,
    )
    db.add(process)
    db.flush()

    process_level = ProcessLevel(level="Level 1")
    db.add(process_level)
    db.flush()

    process_category = ProcessCategory(name="Test Category")
    db.add(process_category)
    db.flush()

    sub_process = SubProcess(
        name="Test Sub-Process",
        description="Test Sub-Process Description",
        process_id=process.id,
        process_level_id=process_level.id,
        process_category_id=process_category.id,
    )
    db.add(sub_process)
    db.flush()

    data_entity = DataEntity(name="Test Data Entity", sub_process_id=sub_process.id)
    db.add(data_entity)
    db.flush()

    application = Application(name="Test Application", data_entity_id=data_entity.id)
    db.add(application)
    db.flush()

    api = API(name="Test API", application_id=application.id)
    db.add(api)

    db.commit()
    db.close()


class TestHealthEndpoint:
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestCapabilityEndpoints:
    @classmethod
    def setup_class(cls):
        """Setup test data before running tests."""
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        seed_test_data()

    def test_get_all_capabilities(self):
        """Test getting all capabilities."""
        response = client.get("/api/capabilities")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_capability_by_name(self):
        """Test getting capability by name."""
        response = client.get("/api/capability/Test%20Capability")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Capability"
        assert data["goal"] == "Test Goal"
        assert data["vertical"] == "Test Vertical"

    def test_get_capability_not_found(self):
        """Test getting non-existent capability."""
        response = client.get("/api/capability/Nonexistent")
        assert response.status_code == 404

    def test_search_capabilities(self):
        """Test searching capabilities."""
        response = client.get("/api/capabilities/search?keyword=Test")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
