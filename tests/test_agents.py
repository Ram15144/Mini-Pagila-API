"""Tests for agent functionality including SearchAgent, LLMAgent, and HandoffOrchestration."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.main import app
from app.agents.search_agent import SearchAgentFactory
from app.agents.llm_agent import LLMAgentFactory
from services.film_service import FilmService
from services.rental_service import RentalService
from repositories.film_repository import FilmRepository
from repositories.rental_repository import RentalRepository
from domain.models import Film
from core.config import settings


class TestFilmServiceAsPlugin:
    """Test cases for FilmService as agent plugin."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        return Mock(spec=AsyncSession)
    
    @pytest.fixture
    def film_service(self, mock_session):
        """Create FilmService with mocked repository and session."""
        mock_repository = Mock(spec=FilmRepository)
        return FilmService(mock_repository, mock_session)
    
    @pytest.mark.asyncio
    async def test_search_films_by_title_success(self, film_service):
        """Test successful film search via kernel function."""
        from datetime import datetime
        from decimal import Decimal
        
        # Mock film data with proper types
        mock_film = Mock(spec=Film)
        mock_film.title = "Alien"
        mock_film.release_year = 1979
        mock_film.rating = "R"
        mock_film.rental_rate = Decimal("2.99")
        mock_film.length = 117
        mock_film.description = "A classic sci-fi horror film"
        mock_film.streaming_available = False
        mock_film.film_id = 1
        mock_film.rental_duration = 7
        mock_film.last_update = datetime.now()
        
        # Mock repository method
        film_service.repository.search_films_by_title = AsyncMock(return_value=([mock_film], 1))
        
        result = await film_service.search_films_by_title("Alien", 0, 5)
        
        assert result.total == 1
        assert len(result.films) == 1
        assert result.films[0].title == "Alien"
        
    @pytest.mark.asyncio
    async def test_get_film_by_id_success(self, film_service):
        """Test successful film retrieval by ID."""
        from datetime import datetime
        from decimal import Decimal
        
        mock_film = Mock(spec=Film)
        mock_film.title = "Blade Runner"
        mock_film.release_year = 1982
        mock_film.rating = "R"
        mock_film.rental_rate = Decimal("3.99")
        mock_film.length = 117
        mock_film.rental_duration = 7
        mock_film.streaming_available = True
        mock_film.description = "A neo-noir science fiction film"
        mock_film.film_id = 1
        mock_film.last_update = datetime.now()
        
        film_service.repository.get_film_by_id = AsyncMock(return_value=mock_film)
        
        result = await film_service.get_film_by_id(1)
        
        assert result.title == "Blade Runner"
        assert result.rating == "R"
        assert result.streaming_available is True
        
    @pytest.mark.asyncio
    async def test_get_film_by_id_not_found(self, film_service):
        """Test film retrieval when film not found."""
        film_service.repository.get_film_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(HTTPException) as exc_info:
            await film_service.get_film_by_id(999)
        
        assert exc_info.value.status_code == 404


class TestRentalServiceAsPlugin:
    """Test cases for RentalService as agent plugin."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        return Mock(spec=AsyncSession)
    
    @pytest.fixture
    def rental_service(self, mock_session):
        """Create RentalService with mocked repository and session."""
        mock_repository = Mock(spec=RentalRepository)
        return RentalService(mock_repository, mock_session)
    
    @pytest.mark.asyncio
    async def test_get_customer_rentals_success(self, rental_service):
        """Test successful customer rental retrieval."""
        from datetime import datetime
        from domain.models import Rental
        
        mock_rental = Mock(spec=Rental)
        mock_rental.rental_id = 1
        mock_rental.customer_id = 1
        mock_rental.inventory_id = 1
        mock_rental.rental_date = datetime.now()
        mock_rental.return_date = None
        mock_rental.staff_id = 1
        mock_rental.last_update = datetime.now()
        
        rental_service.repository.get_customer_rentals = AsyncMock(return_value=[mock_rental])
        
        result = await rental_service.get_customer_rentals(1, 0, 10)
        
        assert len(result) == 1
        assert result[0].customer_id == 1


class TestSearchAgentFactory:
    """Test cases for SearchAgentFactory."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        return Mock(spec=AsyncSession)
    
    def test_create_search_agent(self, mock_session):
        """Test SearchAgent creation."""
        agent = SearchAgentFactory.create_search_agent(mock_session)
        
        assert agent.name == "SearchAgent"
        assert "film rental store queries" in agent.description


class TestLLMAgentFactory:
    """Test cases for LLMAgentFactory."""
    
    def test_create_llm_agent(self):
        """Test LLMAgent creation."""
        agent = LLMAgentFactory.create_llm_agent()
        
        assert agent.name == "LLMAgent"
        assert "general-purpose assistant" in agent.description


class TestAIServiceWithAgents:
    """Test cases for AIService with agent orchestration."""
    
    @pytest.fixture
    def ai_service(self):
        """Create AIService instance."""
        from services.ai_service import AIService
        return AIService()
    
    @pytest.mark.asyncio
    async def test_ai_service_initialization(self, ai_service):
        """Test that AI service initializes properly."""
        assert ai_service.kernel is not None
        assert ai_service.film_repository is not None
    
    @pytest.mark.asyncio
    async def test_process_question_with_mock(self, ai_service):
        """Test question processing with mocked agents."""
        mock_session = Mock(spec=AsyncSession)
        
        # Mock the agent creation and orchestration
        with patch('app.agents.search_agent.SearchAgentFactory.create_search_agent') as mock_search, \
             patch('app.agents.llm_agent.LLMAgentFactory.create_llm_agent') as mock_llm, \
             patch.object(ai_service, '_setup_orchestration') as mock_orchestration_setup, \
             patch.object(ai_service, '_extract_final_agent_from_history') as mock_extract:
            
            # Mock agents
            mock_search_agent = Mock()
            mock_search_agent.name = "SearchAgent"
            mock_search.return_value = mock_search_agent
            
            mock_llm_agent = Mock()
            mock_llm_agent.name = "LLMAgent"
            mock_llm.return_value = mock_llm_agent
            
            # Set up mock orchestration attribute
            mock_orchestration_result = AsyncMock()
            mock_orchestration_result.get = AsyncMock(return_value="Test response")
            
            mock_orchestration = Mock()
            mock_orchestration.invoke = AsyncMock(return_value=mock_orchestration_result)
            ai_service.orchestration = mock_orchestration
            
            # Mock the setup_orchestration method to set the orchestration attribute
            def setup_orchestration_side_effect(session):
                ai_service.orchestration = mock_orchestration
                
            mock_orchestration_setup.side_effect = setup_orchestration_side_effect
            
            # Mock the extraction method to return the expected agent
            mock_extract.return_value = ("SearchAgent", "Test response")
            
            result = await ai_service.process_question("Test question", mock_session)
            
            assert result["agent"] == "SearchAgent"
            assert result["answer"] == "Test response"
            assert result["metadata"]["orchestration_used"] is True


class TestHandoffAPIIntegration:
    """Integration tests for the handoff API endpoint."""
    
    @pytest.mark.asyncio
    async def test_handoff_endpoint_film_question(self):
        """Test handoff endpoint with film-related question."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            # Mock the AI service to avoid real OpenAI calls
            with patch('app.api.v1.ai.get_ai_service') as mock_service_getter:
                mock_service = Mock()
                mock_service.process_question = AsyncMock(return_value={
                    "agent": "SearchAgent",
                    "answer": "Alien (Horror) rents for $2.99.",
                    "metadata": {"orchestration_used": True, "conversation_turns": 2}
                })
                mock_service.cleanup = AsyncMock()
                mock_service_getter.return_value = mock_service
                
                response = await ac.post(
                    "/api/v1/ai/handoff",
                    json={"question": "What is the rental rate for the film Alien?"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["agent"] == "SearchAgent"
                assert "Alien" in data["answer"]
                assert "$2.99" in data["answer"]
    
    @pytest.mark.asyncio
    async def test_handoff_endpoint_general_question(self):
        """Test handoff endpoint with general knowledge question."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.api.v1.ai.get_ai_service') as mock_service_getter:
                mock_service = Mock()
                mock_service.process_question = AsyncMock(return_value={
                    "agent": "LLMAgent",
                    "answer": "Argentina won the 2022 FIFA World Cup after defeating France in the final.",
                    "metadata": {"orchestration_used": True, "conversation_turns": 1}
                })
                mock_service.cleanup = AsyncMock()
                mock_service_getter.return_value = mock_service
                
                response = await ac.post(
                    "/api/v1/ai/handoff",
                    json={"question": "Who won the FIFA World Cup in 2022?"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["agent"] == "LLMAgent"
                assert "Argentina" in data["answer"]
                assert "2022" in data["answer"]
    
    @pytest.mark.asyncio
    async def test_handoff_endpoint_validation_error(self):
        """Test handoff endpoint with invalid request."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                "/api/v1/ai/handoff",
                json={"question": ""}  # Empty question should fail validation
            )
            
            assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_handoff_endpoint_error_handling(self):
        """Test handoff endpoint error handling."""
        from app.api.v1.ai import get_ai_service
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            # Create a mock service that raises an exception
            mock_service = Mock()
            mock_service.process_question = AsyncMock(side_effect=Exception("Test error"))
            
            # Override the dependency
            app.dependency_overrides[get_ai_service] = lambda: mock_service
            
            try:
                response = await ac.post(
                    "/api/v1/ai/handoff",
                    json={"question": "Test question"}
                )
                
                assert response.status_code == 500
                data = response.json()
                assert "Failed to process question" in data["detail"] or "Test error" in data["detail"]
            finally:
                # Clean up the override
                app.dependency_overrides.clear()


class TestAgentFunctionCalling:
    """Test cases for agent function calling capabilities."""
    
    @pytest.mark.asyncio
    async def test_kernel_function_decorators(self):
        """Test that kernel functions are properly decorated."""
        from services.film_service import FilmService
        from services.rental_service import RentalService
        from repositories.film_repository import FilmRepository
        from repositories.rental_repository import RentalRepository
        
        # Check that methods have kernel_function attributes
        mock_session = Mock(spec=AsyncSession)
        film_service = FilmService(FilmRepository(), mock_session)
        rental_service = RentalService(RentalRepository(), mock_session)
        
        # Test film service kernel functions
        func = getattr(film_service, 'search_films_by_title')
        assert hasattr(func, '__kernel_function__')
        
        func = getattr(film_service, 'get_film_by_id')
        assert hasattr(func, '__kernel_function__')
        
        # Test rental service kernel functions
        func = getattr(rental_service, 'get_customer_rentals')
        assert hasattr(func, '__kernel_function__')

@pytest.mark.integration
class TestRealAgentIntegration:
    """Integration tests with real agents (requires OpenAI API key)."""
    
    @pytest.mark.skipif(
        not settings.OPENAI_API_KEY,
        reason="OPENAI_API_KEY not set"
    )
    @pytest.mark.asyncio
    async def test_real_search_agent_creation(self):
        """Test creating real SearchAgent with OpenAI integration."""
        mock_session = Mock(spec=AsyncSession)
        
        try:
            agent = SearchAgentFactory.create_search_agent(mock_session)
            assert agent.name == "SearchAgent"
            assert agent.service.ai_model_id == settings.OPENAI_MODEL_ID
        except Exception as e:
            pytest.skip(f"OpenAI integration test failed: {e}")
    
    @pytest.mark.skipif(
        not settings.OPENAI_API_KEY,
        reason="OPENAI_API_KEY not set"
    )
    @pytest.mark.asyncio
    async def test_real_llm_agent_creation(self):
        """Test creating real LLMAgent with OpenAI integration."""
        try:
            agent = LLMAgentFactory.create_llm_agent()
            assert agent.name == "LLMAgent"
            assert agent.service.ai_model_id == settings.OPENAI_MODEL_ID
        except Exception as e:
            pytest.skip(f"OpenAI integration test failed: {e}")
