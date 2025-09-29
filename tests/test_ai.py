"""Test AI endpoints."""

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_ai_ask_basic_question(client: AsyncClient):
    """Test AI ask endpoint with basic question using SSE."""
    response = await client.get("/api/v1/ai/ask?question=Hello")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    
    # Read the SSE response
    content = response.text
    assert len(content) > 0  # Should get some response from OpenAI
    assert "event: start" in content  # Should contain start event
    assert "event: message" in content or "event: complete" in content  # Should contain response events


@pytest.mark.asyncio
async def test_ai_ask_empty_question(client: AsyncClient):
    """Test AI ask endpoint with empty question."""
    response = await client.get("/api/v1/ai/ask?question=")
    assert response.status_code == 422  # Validation error for min_length


@pytest.mark.asyncio
async def test_ai_ask_missing_question(client: AsyncClient):
    """Test AI ask endpoint without question parameter."""
    response = await client.get("/api/v1/ai/ask")
    assert response.status_code == 422  # Missing required parameter


@pytest.mark.asyncio
async def test_ai_ask_streaming_response(client: AsyncClient):
    """Test AI ask endpoint returns SSE streaming response."""
    response = await client.get("/api/v1/ai/ask?question=What is a DVD?")
    
    assert response.status_code == 200
    # Verify it's an SSE streaming response
    assert "text/event-stream" in response.headers.get("content-type", "")
    
    # Verify SSE headers
    assert response.headers.get("cache-control") == "no-cache"
    assert response.headers.get("connection") == "keep-alive"


@pytest.mark.asyncio  
async def test_ai_summary_valid_film(client: AsyncClient):
    """Test AI summary with valid film ID."""
    with patch('repositories.film_repository.FilmRepository.get_film_by_id') as mock_get_film:
        # Mock film data
        mock_film = AsyncMock(
            film_id=1,
            title="Test Movie",
            description="A test movie",
            rating="R",
            rental_rate=2.99,
            length=120
        )
        mock_get_film.return_value = mock_film
        
        response = await client.post(
            "/api/v1/ai/summary",
            json={"film_id": 1}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "title" in data
        assert "rating" in data
        assert "recommended" in data
        assert isinstance(data["recommended"], bool)


@pytest.mark.asyncio
async def test_ai_summary_invalid_film(client: AsyncClient):
    """Test AI summary with invalid film ID."""
    with patch('repositories.film_repository.FilmRepository.get_film_by_id') as mock_get_film:
        mock_get_film.return_value = None
        
        response = await client.post(
            "/api/v1/ai/summary", 
            json={"film_id": 999}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_ai_summary_invalid_film_id(client: AsyncClient):
    """Test AI summary with invalid film ID format."""
    response = await client.post(
        "/api/v1/ai/summary",
        json={"film_id": 0}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_ai_summary_missing_film_id(client: AsyncClient):
    """Test AI summary without film_id."""
    response = await client.post(
        "/api/v1/ai/summary",
        json={}
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_ai_summary_json_structure(client: AsyncClient):
    """Test AI summary returns proper JSON structure."""
    with patch('repositories.film_repository.FilmRepository.get_film_by_id') as mock_get_film:
        # Mock film data
        mock_film = AsyncMock(
            film_id=1,
            title="Inception",
            description="A mind-bending thriller",
            rating="PG-13",
            rental_rate=4.99,
            length=148
        )
        mock_get_film.return_value = mock_film
        
        response = await client.post(
            "/api/v1/ai/summary",
            json={"film_id": 1}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields are present
        assert "title" in data
        assert "rating" in data
        assert "recommended" in data
        
        # Verify types
        assert isinstance(data["title"], str)
        assert isinstance(data["rating"], str)
        assert isinstance(data["recommended"], bool)


def test_ai_summary_recommendation_logic():
    """Test AI summary recommendation logic."""
    with patch('core.ai_kernel.get_kernel') as mock_get_kernel:
        # Mock kernel to avoid OpenAI initialization
        mock_kernel = MagicMock()
        mock_get_kernel.return_value = mock_kernel
        
        from services.ai_service import AIService
        from domain.models import Film
        from decimal import Decimal
        
        service = AIService(kernel=mock_kernel)
        
        # Test case 1: R rating + cheap rental = recommended
        film1 = Film(
            film_id=1,
            title="Test Movie 1",
            rating="R",
            rental_rate=Decimal("2.99"),
            rental_duration=3
        )
        assert service._calculate_recommendation(film1) is True
        
        # Test case 2: PG-13 rating + cheap rental = not recommended (rating not mature enough)
        film2 = Film(
            film_id=2,
            title="Test Movie 2", 
            rating="PG-13",
            rental_rate=Decimal("2.99"),
            rental_duration=3
        )
        assert service._calculate_recommendation(film2) is False
        
        # Test case 3: R rating + expensive rental = not recommended (rental too expensive)
        film3 = Film(
            film_id=3,
            title="Test Movie 3",
            rating="R", 
            rental_rate=Decimal("4.99"),
            rental_duration=3
        )
        assert service._calculate_recommendation(film3) is False
        
        # Test case 4: NC-17 rating + cheap rental = recommended
        film4 = Film(
            film_id=4,
            title="Test Movie 4",
            rating="NC-17",
            rental_rate=Decimal("1.99"),
            rental_duration=3
        )
        assert service._calculate_recommendation(film4) is True


def test_ai_service_initialization():
    """Test AI service initialization."""
    with patch('core.ai_kernel.get_kernel') as mock_get_kernel:
        mock_kernel = MagicMock()
        mock_get_kernel.return_value = mock_kernel
        
        from services.ai_service import AIService
        
        service = AIService()
        assert service.kernel is not None
        assert service.film_repository is not None


def test_ai_kernel_factory():
    """Test AI kernel factory (without actual OpenAI connection)."""
    with patch('semantic_kernel.connectors.ai.open_ai.OpenAIChatCompletion') as mock_completion:
        mock_completion.return_value = MagicMock()
        
        from core.ai_kernel import AIKernelFactory
        
        # Reset singleton for testing
        AIKernelFactory._kernel = None
        
        # Test factory method
        kernel1 = AIKernelFactory.get_kernel()
        kernel2 = AIKernelFactory.get_kernel()
        
        # Should return the same instance (singleton)
        assert kernel1 is kernel2


def test_execution_settings():
    """Test execution settings creation."""
    from core.ai_kernel import get_execution_settings, get_json_execution_settings
    
    # Test default settings
    settings = get_execution_settings()
    assert settings.max_tokens == 1000
    assert settings.temperature == 0.7
    
    # Test JSON settings
    json_settings = get_json_execution_settings()
    assert json_settings.response_format == {"type": "json_object"}


def test_sse_response_format():
    """Test SSE response format structure."""
    import json
    
    # Test SSE event format
    event_data = {"status": "processing", "question": "test"}
    sse_line = f"event: start\ndata: {json.dumps(event_data)}\n\n"
    
    assert "event: start" in sse_line
    assert "data: " in sse_line
    assert json.dumps(event_data) in sse_line
    
    # Test message event format
    message_data = {"type": "chunk", "content": "Hello", "partial_response": "Hello"}
    message_line = f"event: message\ndata: {json.dumps(message_data)}\n\n"
    
    assert "event: message" in message_line
    assert "Hello" in message_line


def test_prompt_creation():
    """Test film summary prompt creation."""
    with patch('core.ai_kernel.get_kernel') as mock_get_kernel:
        mock_kernel = MagicMock()
        mock_get_kernel.return_value = mock_kernel
        
        from services.ai_service import AIService
        from domain.models import Film
        from decimal import Decimal
        
        service = AIService(kernel=mock_kernel)
        
        film = Film(
            film_id=1,
            title="Test Movie",
            description="A great test movie",
            rating="PG-13",
            rental_rate=Decimal("3.99"),
            length=120,
            release_year=2023,
            rental_duration=3
        )
        
        prompt = service._create_summary_prompt(film)
        
        assert "Test Movie" in prompt
        assert "A great test movie" in prompt
        assert "PG-13" in prompt
        assert "3.99" in prompt
        assert "JSON" in prompt
