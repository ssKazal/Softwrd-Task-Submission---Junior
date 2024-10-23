import pytest


@pytest.mark.asyncio
async def test_create_allocation(test_client, allocation_data):
    """Test to create a vehicle allocation."""
    response = test_client.post("/api/allocations", json=allocation_data)
    assert response.status_code == 201  # Check for successful creation


@pytest.mark.asyncio
async def test_create_allocation_with_past_date(test_client, past_allocation_data):
    """Test to create an allocation with a past date."""
    response = test_client.post("/api/allocations", json=past_allocation_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Allocation date must be in the future!"


@pytest.mark.asyncio
async def test_read_allocations(test_client):
    """Test to read all allocations."""
    response = test_client.get("/api/allocations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_read_allocation(test_client, valid_allocation_id):
    """Test to read a specific allocation."""
    response = test_client.get(f"/api/allocations/{str(valid_allocation_id)}")
    assert response.status_code == 200, f"Failed to read allocation: {response.json()}"
    assert "employee" in response.json()
    assert "vehicle" in response.json()


@pytest.mark.asyncio
async def test_update_allocation(
    test_client, valid_allocation_id, updated_allocation_data
):
    """Test to update an existing allocation."""
    response = test_client.put(
        f"/api/allocations/{valid_allocation_id}", json=updated_allocation_data
    )
    assert response.status_code == 200
    assert (
        response.json()["allocation_date"] == updated_allocation_data["allocation_date"]
    )


@pytest.mark.asyncio
async def test_delete_allocation_with_unfinished_future_date(
    test_client, valid_allocation_id
):
    """Test to delete an allocation."""
    response = test_client.delete(f"/api/allocations/{valid_allocation_id}")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_read_allocation_not_found(test_client, invalid_allocation_id):
    """Test to read a non-existent allocation."""
    response = test_client.get(f"/api/allocations/{invalid_allocation_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Allocation not found!"
