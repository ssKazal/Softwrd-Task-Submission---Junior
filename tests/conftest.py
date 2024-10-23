import pytest
from bson import ObjectId
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def allocation_data():
    """Fixture to provide data for creating an allocation."""
    return {
        "employee_id": str(ObjectId()),  # Generate a new ObjectId for employee_id
        "vehicle_id": str(ObjectId()),  # Generate a new ObjectId for vehicle_id
        "allocation_date": datetime(2024, 12, 1).isoformat(),  # Set the allocation date
    }


@pytest.fixture
def future_allocation_data():
    """Fixture to provide future allocation data for testing."""
    return {
        "employee_id": str(ObjectId()),
        "vehicle_id": str(ObjectId()),
        "allocation_date": (
            datetime.now().replace(hour=0, minute=0, second=0) + timedelta(days=1)
        ).isoformat(),  # Set to tomorrow
    }


@pytest.fixture
def past_allocation_data():
    """Fixture to provide past allocation data for testing."""
    return {
        "employee_id": str(ObjectId()),
        "vehicle_id": str(ObjectId()),
        "allocation_date": (
            datetime.now().replace(hour=0, minute=0, second=0) - timedelta(days=1)
        ).isoformat(),  # Set to yesterday
    }


@pytest.fixture
def valid_allocation_id(test_client, allocation_data):
    """Fixture to create an allocation first to get a valid ID for testing read/update/delete operations."""
    response = test_client.post("/api/allocations", json=allocation_data)
    assert response.status_code == 201
    return response.json().get("_id")  # Return the allocation ID


@pytest.fixture
def invalid_allocation_id():
    """Fixture to provide an invalid allocation ID for testing."""
    return str(ObjectId())


@pytest.fixture
def updated_allocation_data():
    """Fixture to provide data for updating an existing allocation."""
    return {
        "employee_id": str(ObjectId()),  # New employee_id for update
        "vehicle_id": str(ObjectId()),  # New vehicle_id for update
        "allocation_date": datetime(2024, 12, 2).isoformat(),  # New allocation date
    }
