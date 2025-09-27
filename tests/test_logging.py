"""Test structured logging functionality."""

import pytest
from httpx import AsyncClient
from unittest.mock import patch

from core.logging import (
    get_logger, 
    set_correlation_id, 
    get_correlation_id,
    LoggingMixin,
    RequestLogger,
    DatabaseLogger,
    AILogger
)


def test_correlation_id_management():
    """Test correlation ID context management."""
    # Test setting and getting correlation ID
    correlation_id = set_correlation_id("test-correlation-id")
    assert correlation_id == "test-correlation-id"
    assert get_correlation_id() == "test-correlation-id"
    
    # Test auto-generation
    auto_id = set_correlation_id()
    assert auto_id != "test-correlation-id"
    assert len(auto_id) > 10  # Should be a UUID


def test_logger_initialization():
    """Test logger initialization."""
    logger = get_logger("test-component")
    assert logger is not None
    # Structlog loggers don't have a 'name' attribute like standard loggers
    # We can verify it's a proper BoundLogger instead
    assert hasattr(logger, 'info')
    assert hasattr(logger, 'error')
    assert hasattr(logger, 'debug')


def test_logging_mixin():
    """Test LoggingMixin functionality."""
    class TestService(LoggingMixin):
        def __init__(self):
            super().__init__()
    
    service = TestService()
    assert service.logger is not None
    # Structlog loggers don't have a 'name' attribute like standard loggers
    # We can verify it's a proper BoundLogger instead
    assert hasattr(service.logger, 'info')
    assert hasattr(service.logger, 'error')
    assert hasattr(service.logger, 'debug')


def test_request_logger():
    """Test request logging utilities."""
    # Test static methods don't raise errors
    RequestLogger.log_request("GET", "/test", user_id="123")
    RequestLogger.log_response("GET", "/test", 200, 150.5, user_id="123")


def test_database_logger():
    """Test database logging utilities."""
    # Test static methods don't raise errors
    DatabaseLogger.log_query("SELECT", "films", limit=10, offset=0)
    DatabaseLogger.log_query_result("SELECT", result_count=5, total=100)


def test_ai_logger():
    """Test AI logging utilities."""
    # Test static methods don't raise errors
    AILogger.log_ai_request("ask_question", "gpt-4o-mini", question_length=20)
    AILogger.log_ai_response("ask_question", "gpt-4o-mini", token_count=50)
    
    # Test error logging
    try:
        raise ValueError("Test error")
    except Exception as e:
        AILogger.log_ai_error("ask_question", e, question_length=20)


@pytest.mark.asyncio
async def test_request_logging_integration(client: AsyncClient):
    """Test that requests are properly logged."""
    response = await client.get("/health")
    
    assert response.status_code == 200
    # Verify correlation ID is in response headers
    assert "X-Correlation-ID" in response.headers
    correlation_id = response.headers["X-Correlation-ID"]
    assert len(correlation_id) > 10  # Should be a valid correlation ID


@pytest.mark.asyncio
async def test_ai_logging_integration(client: AsyncClient):
    """Test AI logging integration."""
    with patch('repositories.film_repository.FilmRepository.get_film_by_id') as mock_get_film:
        # Create a proper mock film object with all required attributes
        class MockFilm:
            def __init__(self):
                self.film_id = 1
                self.title = 'Test Movie'
                self.description = 'A test movie'
                self.rating = 'PG'
                self.rental_rate = 4.99
                self.length = 120
                self.release_year = 2023
        
        mock_film = MockFilm()
        mock_get_film.return_value = mock_film
        
        response = await client.post(
            "/api/v1/ai/summary",
            json={"film_id": 1}
        )
        
        assert response.status_code == 200
        # Verify correlation ID is in response headers
        assert "X-Correlation-ID" in response.headers


@pytest.mark.asyncio
async def test_authentication_logging(client: AsyncClient):
    """Test authentication logging."""
    # Test invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    response = await client.get("/protected", headers=headers)
    
    assert response.status_code == 401
    assert "X-Correlation-ID" in response.headers


def test_logging_configuration():
    """Test logging configuration."""
    from core.logging import configure_logging
    
    # Should not raise errors
    configure_logging()


@pytest.mark.asyncio
async def test_sse_logging(client: AsyncClient):
    """Test SSE endpoint logging.""" 
    response = await client.get("/api/v1/ai/ask?question=Hello")
    
    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")
    assert "X-Correlation-ID" in response.headers
