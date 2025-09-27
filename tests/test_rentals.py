"""Test rental endpoints."""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from datetime import datetime


@pytest.mark.asyncio
async def test_create_rental_authenticated(client: AsyncClient):
    """Test rental creation with valid authentication."""
    headers = {"Authorization": "Bearer dvd_admin"}
    rental_data = {
        "inventory_id": 1,
        "staff_id": 1
    }
    
    with patch('repositories.rental_repository.RentalRepository.validate_rental_data') as mock_validate, \
         patch('repositories.rental_repository.RentalRepository.create_rental') as mock_create:
        
        # Mock successful validation
        mock_validate.return_value = {
            "valid": True,
            "errors": []
        }
        
        # Mock successful rental creation
        mock_rental = AsyncMock(
            rental_id=1,
            customer_id=1,
            inventory_id=1,
            staff_id=1,
            rental_date=datetime(2023, 1, 1, 12, 0, 0),
            return_date=None,
            last_update=datetime(2023, 1, 1, 12, 0, 0)
        )
        mock_create.return_value = mock_rental
        
        response = await client.post(
            "/api/v1/customers/1/rentals",
            json=rental_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["rental_id"] == 1
        assert data["customer_id"] == 1
        assert data["inventory_id"] == 1
        assert data["staff_id"] == 1
        assert data["return_date"] is None


@pytest.mark.asyncio
async def test_create_rental_unauthenticated(client: AsyncClient):
    """Test rental creation without authentication."""
    rental_data = {
        "inventory_id": 1,
        "staff_id": 1
    }
    
    response = await client.post(
        "/api/v1/customers/1/rentals",
        json=rental_data
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_rental_invalid_token(client: AsyncClient):
    """Test rental creation with invalid token."""
    headers = {"Authorization": "Bearer invalid_token"}
    rental_data = {
        "inventory_id": 1,
        "staff_id": 1
    }
    
    response = await client.post(
        "/api/v1/customers/1/rentals",
        json=rental_data,
        headers=headers
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_rental_invalid_customer_id(client: AsyncClient):
    """Test rental creation with invalid customer ID."""
    headers = {"Authorization": "Bearer dvd_admin"}
    rental_data = {
        "inventory_id": 1,
        "staff_id": 1
    }
    
    # Test zero customer ID
    response = await client.post(
        "/api/v1/customers/0/rentals",
        json=rental_data,
        headers=headers
    )
    assert response.status_code == 422  # Validation error from Path parameter
    
    # Test negative customer ID
    response = await client.post(
        "/api/v1/customers/-1/rentals",
        json=rental_data,
        headers=headers
    )
    assert response.status_code == 422  # Validation error from Path parameter


@pytest.mark.asyncio
async def test_create_rental_invalid_request_data(client: AsyncClient):
    """Test rental creation with invalid request data."""
    headers = {"Authorization": "Bearer dvd_admin"}
    
    # Test missing inventory_id
    response = await client.post(
        "/api/v1/customers/1/rentals",
        json={"staff_id": 1},
        headers=headers
    )
    assert response.status_code == 422  # Validation error
    
    # Test missing staff_id
    response = await client.post(
        "/api/v1/customers/1/rentals",
        json={"inventory_id": 1},
        headers=headers
    )
    assert response.status_code == 422  # Validation error
    
    # Test invalid inventory_id (negative) - this is caught by pydantic validation
    response = await client.post(
        "/api/v1/customers/1/rentals",
        json={"inventory_id": -1, "staff_id": 1},
        headers=headers
    )
    assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_create_rental_validation_failures(client: AsyncClient):
    """Test rental creation with business validation failures."""
    headers = {"Authorization": "Bearer dvd_admin"}
    rental_data = {
        "inventory_id": 1,
        "staff_id": 1
    }
    
    with patch('repositories.rental_repository.RentalRepository.validate_rental_data') as mock_validate:
        # Mock validation failure
        mock_validate.return_value = {
            "valid": False,
            "errors": ["Customer not found", "Inventory item already rented"]
        }
        
        response = await client.post(
            "/api/v1/customers/1/rentals",
            json=rental_data,
            headers=headers
        )
        
        assert response.status_code == 422
        data = response.json()
        assert "validation failed" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_customer_rentals(client: AsyncClient):
    """Test getting customer rentals."""
    with patch('repositories.rental_repository.RentalRepository.get_customer_rentals') as mock_get:
        mock_rentals = [
            AsyncMock(
                rental_id=1,
                customer_id=1,
                inventory_id=1,
                staff_id=1,
                rental_date=datetime(2023, 1, 1),
                return_date=None,
                last_update=datetime(2023, 1, 1)
            ),
            AsyncMock(
                rental_id=2,
                customer_id=1,
                inventory_id=2,
                staff_id=1,
                rental_date=datetime(2023, 1, 2),
                return_date=datetime(2023, 1, 5),
                last_update=datetime(2023, 1, 5)
            )
        ]
        mock_get.return_value = mock_rentals
        
        response = await client.get("/api/v1/customers/1/rentals")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["rental_id"] == 1
        assert data[1]["rental_id"] == 2


@pytest.mark.asyncio
async def test_get_customer_rentals_with_pagination(client: AsyncClient):
    """Test getting customer rentals with pagination."""
    with patch('repositories.rental_repository.RentalRepository.get_customer_rentals') as mock_get:
        mock_get.return_value = []
        
        response = await client.get("/api/v1/customers/1/rentals?skip=10&limit=5")
        
        assert response.status_code == 200
        # Verify pagination parameters were passed
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]['skip'] == 10
        assert call_args[1]['limit'] == 5


@pytest.mark.asyncio
async def test_get_customer_rentals_invalid_id(client: AsyncClient):
    """Test getting rentals for invalid customer ID."""
    response = await client.get("/api/v1/customers/0/rentals")
    assert response.status_code == 422  # Path validation error
    
    response = await client.get("/api/v1/customers/-1/rentals")
    assert response.status_code == 422  # Path validation error


@pytest.mark.asyncio
async def test_get_rental_by_id(client: AsyncClient):
    """Test getting a rental by ID."""
    with patch('repositories.rental_repository.RentalRepository.get_rental_by_id') as mock_get:
        mock_rental = AsyncMock(
            rental_id=1,
            customer_id=1,
            inventory_id=1,
            staff_id=1,
            rental_date=datetime(2023, 1, 1),
            return_date=None,
            last_update=datetime(2023, 1, 1)
        )
        mock_get.return_value = mock_rental
        
        response = await client.get("/api/v1/rentals/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["rental_id"] == 1


@pytest.mark.asyncio
async def test_get_rental_by_id_not_found(client: AsyncClient):
    """Test getting a non-existent rental."""
    with patch('repositories.rental_repository.RentalRepository.get_rental_by_id') as mock_get:
        mock_get.return_value = None
        
        response = await client.get("/api/v1/rentals/999")
        
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_active_rentals(client: AsyncClient):
    """Test getting active rentals."""
    with patch('repositories.rental_repository.RentalRepository.get_active_rentals') as mock_get:
        mock_get.return_value = []
        
        response = await client.get("/api/v1/rentals/active")
        
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_active_rentals_with_customer_filter(client: AsyncClient):
    """Test getting active rentals with customer filter."""
    with patch('repositories.rental_repository.RentalRepository.get_active_rentals') as mock_get:
        mock_get.return_value = []
        
        response = await client.get("/api/v1/rentals/active?customer_id=1")
        
        assert response.status_code == 200
        # Verify customer filter was passed
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]['customer_id'] == 1


@pytest.mark.asyncio
async def test_return_rental_authenticated(client: AsyncClient):
    """Test returning a rental with authentication."""
    headers = {"Authorization": "Bearer dvd_admin"}
    
    with patch('repositories.rental_repository.RentalRepository.return_rental') as mock_return:
        mock_rental = AsyncMock(
            rental_id=1,
            customer_id=1,
            inventory_id=1,
            staff_id=1,
            rental_date=datetime(2023, 1, 1),
            return_date=datetime(2023, 1, 5),
            last_update=datetime(2023, 1, 5)
        )
        mock_return.return_value = mock_rental
        
        response = await client.put("/api/v1/rentals/1/return", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["rental_id"] == 1
        assert data["return_date"] is not None


@pytest.mark.asyncio
async def test_return_rental_unauthenticated(client: AsyncClient):
    """Test returning a rental without authentication."""
    response = await client.put("/api/v1/rentals/1/return")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_return_rental_not_found(client: AsyncClient):
    """Test returning a non-existent rental."""
    headers = {"Authorization": "Bearer dvd_admin"}
    
    with patch('repositories.rental_repository.RentalRepository.return_rental') as mock_return, \
         patch('repositories.rental_repository.RentalRepository.get_rental_by_id') as mock_get:
        
        mock_return.return_value = None
        mock_get.return_value = None  # Rental doesn't exist
        
        response = await client.put("/api/v1/rentals/999/return", headers=headers)
        
        assert response.status_code == 404


def test_rental_service_initialization():
    """Test rental service initialization."""
    from services.rental_service import RentalService
    from repositories.rental_repository import RentalRepository
    
    repository = RentalRepository()
    service = RentalService(repository)
    
    assert service.repository == repository


def test_rental_repository_initialization():
    """Test rental repository initialization."""
    from repositories.rental_repository import RentalRepository
    
    repository = RentalRepository()
    assert repository is not None
