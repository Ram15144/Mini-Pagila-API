"""Test film endpoints."""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_list_films_default_pagination(client: AsyncClient):
    """Test films listing with default pagination."""
    # Mock the repository call
    with patch('repositories.film_repository.FilmRepository.list_films') as mock_list:
        # Mock data
        mock_films = [
            AsyncMock(
                film_id=1,
                title="Test Film 1",
                description="A test film",
                release_year=2023,
                rental_duration=3,
                rental_rate=4.99,
                length=120,
                rating="PG-13",
                streaming_available=True,
                last_update="2023-01-01T00:00:00"
            ),
            AsyncMock(
                film_id=2,
                title="Test Film 2", 
                description="Another test film",
                release_year=2023,
                rental_duration=5,
                rental_rate=3.99,
                length=90,
                rating="G",
                streaming_available=False,
                last_update="2023-01-02T00:00:00"
            )
        ]
        mock_list.return_value = (mock_films, 2)
        
        response = await client.get("/api/v1/films")
        
        assert response.status_code == 200
        data = response.json()
        assert "films" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data
        assert data["total"] == 2
        assert data["skip"] == 0
        assert data["limit"] == 10
        assert len(data["films"]) == 2


@pytest.mark.asyncio
async def test_list_films_with_pagination(client: AsyncClient):
    """Test films listing with custom pagination."""
    with patch('repositories.film_repository.FilmRepository.list_films') as mock_list:
        mock_list.return_value = ([], 0)
        
        response = await client.get("/api/v1/films?skip=10&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert data["skip"] == 10
        assert data["limit"] == 5


@pytest.mark.asyncio
async def test_list_films_with_category_filter(client: AsyncClient):
    """Test films listing with category filter."""
    with patch('repositories.film_repository.FilmRepository.list_films') as mock_list:
        mock_list.return_value = ([], 0)
        
        response = await client.get("/api/v1/films?category=Action")
        
        assert response.status_code == 200
        # Verify the category parameter was passed to the repository
        mock_list.assert_called_once()
        call_args = mock_list.call_args
        assert call_args[1]['category'] == 'Action'


@pytest.mark.asyncio
async def test_list_films_invalid_pagination(client: AsyncClient):
    """Test films listing with invalid pagination parameters."""
    # Test negative skip
    response = await client.get("/api/v1/films?skip=-1")
    assert response.status_code == 422
    
    # Test limit too high
    response = await client.get("/api/v1/films?limit=101")
    assert response.status_code == 422
    
    # Test zero limit
    response = await client.get("/api/v1/films?limit=0")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_film_by_id(client: AsyncClient):
    """Test getting a film by ID."""
    with patch('repositories.film_repository.FilmRepository.get_film_by_id') as mock_get:
        mock_film = AsyncMock(
            film_id=1,
            title="Test Film",
            description="A test film",
            release_year=2023,
            rental_duration=3,
            rental_rate=4.99,
            length=120,
            rating="PG-13",
            streaming_available=True,
            last_update="2023-01-01T00:00:00"
        )
        mock_get.return_value = mock_film
        
        response = await client.get("/api/v1/films/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["film_id"] == 1
        assert data["title"] == "Test Film"


@pytest.mark.asyncio
async def test_get_film_by_id_not_found(client: AsyncClient):
    """Test getting a non-existent film."""
    with patch('repositories.film_repository.FilmRepository.get_film_by_id') as mock_get:
        mock_get.return_value = None
        
        response = await client.get("/api/v1/films/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_get_film_invalid_id(client: AsyncClient):
    """Test getting a film with invalid ID."""
    response = await client.get("/api/v1/films/0")
    assert response.status_code == 400
    
    # Negative numbers also reach our service and return 400
    response = await client.get("/api/v1/films/-1")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_search_films_by_title(client: AsyncClient):
    """Test searching films by title."""
    with patch('repositories.film_repository.FilmRepository.search_films_by_title') as mock_search:
        mock_search.return_value = ([], 0)
        
        response = await client.get("/api/v1/films/search/title?q=test")
        
        assert response.status_code == 200
        data = response.json()
        assert "films" in data
        assert "total" in data


@pytest.mark.asyncio
async def test_search_films_by_title_short_query(client: AsyncClient):
    """Test searching films with too short query."""
    response = await client.get("/api/v1/films/search/title?q=a")
    assert response.status_code == 422  # Validation error for min_length


@pytest.mark.asyncio
async def test_search_films_by_title_missing_query(client: AsyncClient):
    """Test searching films without query parameter."""
    response = await client.get("/api/v1/films/search/title")
    assert response.status_code == 422  # Missing required parameter


@pytest.mark.asyncio
async def test_get_streaming_films(client: AsyncClient):
    """Test getting streaming films."""
    with patch('repositories.film_repository.FilmRepository.get_streaming_films') as mock_streaming:
        mock_streaming.return_value = ([], 0)
        
        response = await client.get("/api/v1/films/streaming/available")
        
        assert response.status_code == 200
        data = response.json()
        assert "films" in data
        assert "total" in data


@pytest.mark.asyncio
async def test_get_streaming_films_with_pagination(client: AsyncClient):
    """Test getting streaming films with pagination."""
    with patch('repositories.film_repository.FilmRepository.get_streaming_films') as mock_streaming:
        mock_streaming.return_value = ([], 0)
        
        response = await client.get("/api/v1/films/streaming/available?skip=5&limit=15")
        
        assert response.status_code == 200
        data = response.json()
        assert data["skip"] == 5
        assert data["limit"] == 15


def test_film_service_business_logic():
    """Test film service business logic."""
    from services.film_service import FilmService
    from repositories.film_repository import FilmRepository
    
    # Test service initialization
    repository = FilmRepository()
    service = FilmService(repository)
    
    assert service.repository == repository


def test_film_repository_initialization():
    """Test film repository initialization."""
    from repositories.film_repository import FilmRepository
    
    repository = FilmRepository()
    assert repository is not None
