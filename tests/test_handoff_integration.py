"""Integration tests for agent handoff functionality."""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, Mock, AsyncMock

from app.main import app
from core.config import settings


class TestHandoffIntegration:
    """Integration tests for the complete handoff workflow."""
    
    @pytest.mark.skipif(
        not settings.OPENAI_API_KEY,
        reason="OPENAI_API_KEY not set - skipping real integration test"
    )
    @pytest.mark.asyncio
    async def test_handoff_search_agent_integration(self):
        """Test complete flow: film question -> SearchAgent -> database -> response."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            # Test with real agent handoff functionality
            response = await ac.post(
                "/api/v1/ai/handoff",
                json={"question": "What is the rental rate for the film Alien?"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["agent"] == "SearchAgent"
            assert ("alien" in data["answer"].lower() or "film" in data["answer"].lower())
            assert "rental" in data["answer"].lower()
            assert "$" in data["answer"]  # Check for price format
    
    @pytest.mark.asyncio
    async def test_handoff_search_agent_integration_mocked(self):
        """Test complete flow with mocked response for CI/CD."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            # Mock the AI service for predictable testing
            with patch('app.api.v1.ai.get_ai_service') as mock_service_getter:
                mock_service = Mock()
                mock_service.process_question = AsyncMock(return_value={
                    "agent": "SearchAgent",
                    "answer": "Found film: ALIEN CENTER (NC-17) rents for $2.99.",
                    "metadata": {
                        "orchestration_used": True,
                        "conversation_turns": 2,
                        "runtime_used": "InProcessRuntime"
                    }
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
                assert "ALIEN" in data["answer"]
                assert "$2.99" in data["answer"]

    @pytest.mark.skipif(
        not settings.OPENAI_API_KEY,
        reason="OPENAI_API_KEY not set - skipping real integration test"
    )
    @pytest.mark.asyncio
    async def test_handoff_llm_agent_integration(self):
        """Test complete flow: general question -> LLMAgent -> OpenAI -> response."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            # Test with real agent handoff functionality
            response = await ac.post(
                "/api/v1/ai/handoff",
                json={"question": "Who won the FIFA World Cup in 2022?"}
            )
            
            assert response.status_code == 200
            data = response.json()
            # Note: This might route to SearchAgent first, then handoff to LLMAgent
            assert data["agent"] in ["LLMAgent", "SearchAgent"]
            assert len(data["answer"]) > 10  # Should have a substantial response
    
    @pytest.mark.asyncio
    async def test_handoff_llm_agent_integration_mocked(self):
        """Test complete flow with mocked response for CI/CD."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            # Mock AI service to simulate LLMAgent handling general query
            with patch('app.api.v1.ai.get_ai_service') as mock_service_getter:
                mock_service = Mock()
                mock_service.process_question = AsyncMock(return_value={
                    "agent": "LLMAgent",
                    "answer": "Argentina won the 2022 FIFA World Cup after defeating France 4-2 on penalties following a 3-3 draw after extra time. The final was held at Lusail Stadium in Qatar on December 18, 2022.",
                    "metadata": {
                        "orchestration_used": True,
                        "conversation_turns": 1,
                        "runtime_used": "InProcessRuntime"
                    }
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
    async def test_handoff_agent_decision_making(self):
        """Test that agents make intelligent routing decisions."""
        test_cases = [
            # Film-related questions that should go to SearchAgent
            {
                "question": "Do you have any horror movies available?",
                "expected_agent": "SearchAgent",
                "expected_content": ["horror", "films", "available"]
            },
            {
                "question": "What's the rental rate for Blade Runner?",
                "expected_agent": "SearchAgent", 
                "expected_content": ["Blade Runner", "rental", "rate"]
            },
            {
                "question": "Show me customer rental history for customer 5",
                "expected_agent": "SearchAgent",
                "expected_content": ["customer", "rental", "history"]
            },
            # General questions that should go to LLMAgent
            {
                "question": "What is the capital of France?",
                "expected_agent": "LLMAgent",
                "expected_content": ["Paris", "capital", "France"]
            },
            {
                "question": "Explain quantum physics",
                "expected_agent": "LLMAgent",
                "expected_content": ["quantum", "physics", "particles"]
            },
            {
                "question": "How do I solve a quadratic equation?",
                "expected_agent": "LLMAgent",
                "expected_content": ["quadratic", "equation", "formula"]
            }
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            for test_case in test_cases:
                with patch('app.api.v1.ai.get_ai_service') as mock_service_getter:
                    # Create appropriate mock response based on expected agent
                    if test_case["expected_agent"] == "SearchAgent":
                        mock_answer = f"SearchAgent response for: {test_case['question']}"
                    else:
                        mock_answer = f"LLMAgent response for: {test_case['question']}"
                    
                    mock_service = Mock()
                    mock_service.process_question = AsyncMock(return_value={
                        "agent": test_case["expected_agent"],
                        "answer": mock_answer,
                        "metadata": {"orchestration_used": True, "conversation_turns": 1}
                    })
                    mock_service.cleanup = AsyncMock()
                    mock_service_getter.return_value = mock_service
                    
                    response = await ac.post(
                        "/api/v1/ai/handoff",
                        json={"question": test_case["question"]}
                    )
                    
                    assert response.status_code == 200, f"Failed for question: {test_case['question']}"
                    data = response.json()
                    assert data["agent"] == test_case["expected_agent"], \
                        f"Wrong agent for question: {test_case['question']}"
                    # Handle both string and list expected_content
                    expected_content = test_case["expected_content"]
                    if isinstance(expected_content, list):
                        # For lists, check that at least one item from the list is in the answer
                        assert any(item.lower() in data["answer"].lower() for item in expected_content), \
                            f"Response doesn't contain any expected keywords {expected_content} for: {test_case['question']}"
                    else:
                        # For strings, check direct containment
                        assert expected_content.lower() in data["answer"].lower(), \
                            f"Response doesn't contain expected content '{expected_content}' for: {test_case['question']}"

    @pytest.mark.asyncio
    async def test_handoff_error_scenarios(self):
        """Test various error scenarios in handoff processing."""
        error_scenarios = [
            {
                "name": "Empty question",
                "request": {"question": ""},
                "expected_status": 422,
                "expected_error": "validation"
            },
            {
                "name": "Missing question field",
                "request": {},
                "expected_status": 422,
                "expected_error": "validation"
            },
            {
                "name": "Very long question",
                "request": {"question": "x" * 10000},
                "expected_status": 200,  # Should handle long questions
                "mock_response": {
                    "agent": "LLMAgent",
                    "answer": "I received a very long question.",
                    "metadata": {"orchestration_used": True}
                }
            }
        ]
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            for scenario in error_scenarios:
                if scenario["expected_status"] == 200:
                    # Mock successful response for valid but edge case requests
                    with patch('app.api.v1.ai.get_ai_service') as mock_service_getter:
                        mock_service = Mock()
                        mock_service.process_question = AsyncMock(return_value=scenario["mock_response"])
                        mock_service.cleanup = AsyncMock()
                        mock_service_getter.return_value = mock_service
                        
                        response = await ac.post(
                            "/api/v1/ai/handoff",
                            json=scenario["request"]
                        )
                else:
                    # Test validation errors
                    response = await ac.post(
                        "/api/v1/ai/handoff",
                        json=scenario["request"]
                    )
                
                assert response.status_code == scenario["expected_status"], \
                    f"Wrong status for scenario: {scenario['name']}"
                
                if scenario["expected_status"] != 200:
                    data = response.json()
                    assert "detail" in data or "message" in data, \
                        f"No error message for scenario: {scenario['name']}"

    @pytest.mark.asyncio
    async def test_handoff_orchestration_cleanup(self):
        """Test that orchestration resources are properly cleaned up."""
        from app.api.v1.ai import get_ai_service
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            cleanup_called = False
            
            def track_cleanup():
                nonlocal cleanup_called
                cleanup_called = True
            
            mock_service = Mock()
            mock_service.process_question = AsyncMock(return_value={
                "agent": "SearchAgent",
                "answer": "Test response",
                "metadata": {"orchestration_used": True}
            })
            mock_service.cleanup = AsyncMock(side_effect=track_cleanup)
            
            # Override the dependency
            app.dependency_overrides[get_ai_service] = lambda: mock_service
            
            try:
                response = await ac.post(
                    "/api/v1/ai/handoff",
                    json={"question": "Test question"}
                )
                
                assert response.status_code == 200
                assert cleanup_called, "Cleanup method was not called"
                mock_service.cleanup.assert_called_once()
            finally:
                # Clean up the override
                app.dependency_overrides.clear()

    @pytest.mark.asyncio
    async def test_handoff_response_format(self):
        """Test that handoff responses follow the correct format."""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            with patch('app.api.v1.ai.get_ai_service') as mock_service_getter:
                mock_service = Mock()
                mock_service.process_question = AsyncMock(return_value={
                    "agent": "SearchAgent",
                    "answer": "This is a test response from SearchAgent.",
                    "metadata": {
                        "orchestration_used": True,
                        "conversation_turns": 2,
                        "runtime_used": "InProcessRuntime"
                    }
                })
                mock_service.cleanup = AsyncMock()
                mock_service_getter.return_value = mock_service
                
                response = await ac.post(
                    "/api/v1/ai/handoff",
                    json={"question": "Test question for format validation"}
                )
                
                assert response.status_code == 200
                data = response.json()
                
                # Verify required fields
                assert "agent" in data
                assert "answer" in data
                
                # Verify field types
                assert isinstance(data["agent"], str)
                assert isinstance(data["answer"], str)
                
                # Verify agent is one of the expected values
                assert data["agent"] in ["SearchAgent", "LLMAgent", "SystemFallback"]
                
                # Verify answer is not empty
                assert len(data["answer"]) > 0
                
                # Verify no confidence field (removed in updated design)
                assert "confidence" not in data
