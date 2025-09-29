"""AI service for Semantic Kernel operations."""

import json
import re
from typing import AsyncIterator, Any, Optional
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.open_ai_prompt_execution_settings import OpenAIChatPromptExecutionSettings
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from pydantic import ValidationError
from semantic_kernel import Kernel
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase

from core.ai_kernel import get_kernel, get_execution_settings, get_json_execution_settings
from core.logging import LoggingMixin, AILogger
from domain.schemas import FilmSummary, FilmSummaryRequest
from domain.models import Film
from repositories.film_repository import FilmRepository


from semantic_kernel.agents import HandoffOrchestration, OrchestrationHandoffs
from semantic_kernel.contents import ChatMessageContent, AuthorRole
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from semantic_kernel.agents.runtime import InProcessRuntime
from core.config import settings
from core.logging import LoggingMixin
from app.agents.search_agent import SearchAgentFactory
from app.agents.llm_agent import LLMAgentFactory



class AIService(LoggingMixin):
    """Service for AI operations using Semantic Kernel."""

    def __init__(self, kernel: Optional[Kernel] = None, runtime: InProcessRuntime = InProcessRuntime()):
        """Initialize AI service with Semantic Kernel."""
        super().__init__()
        self.kernel = kernel or get_kernel()

        # Film repository
        self.film_repository = FilmRepository()

        # Agent orchestration
        self.runtime = runtime
        self.conversation_history = []

        self.logger.info("AI service initialized", model=settings.OPENAI_MODEL_ID)

    async def ask_question(self, question: str) -> AsyncIterator[str]:
        """
        Stream AI response to user question.
        
        Args:
            question: User question to process
            
        Yields:
            str: Chunks of the AI response
            
        Raises:
            HTTPException: If question processing fails
        """
        if not question or len(question.strip()) < 1:
            self.log_validation_error("ask_question", ["Question cannot be empty"], question=question)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question cannot be empty"
            )

        AILogger.log_ai_request("ask_question", settings.OPENAI_MODEL_ID, question_length=len(question))

        try:
            # Create chat history with system message
            history = ChatHistory()
            history.add_system_message(
                "You are a helpful assistant for a DVD rental store called Pagila. "
                "You can help customers find movies, understand rental policies, and "
                "provide general assistance with the DVD rental service."
            )
            history.add_user_message(question.strip())

            # Get chat completion service
            chat_completion_service = self.kernel.get_service(type=ChatCompletionClientBase)
            
            # Get execution settings
            execution_settings = get_execution_settings()

            # Stream the response
            response_stream = chat_completion_service.get_streaming_chat_message_content(
                chat_history=history,
                settings=execution_settings
            )

            chunk_count = 0
            total_content = ""
            async for chunk in response_stream:
                if chunk:
                    # Extract content from the chunk
                    content = str(chunk)
                    if content and content.strip():
                        chunk_count += 1
                        total_content += content
                        yield content

            # Log completion
            AILogger.log_ai_response(
                "ask_question", 
                settings.OPENAI_MODEL_ID, 
                token_count=len(total_content.split()),
                chunk_count=chunk_count,
                response_length=len(total_content)
            )

        except Exception as e:
            AILogger.log_ai_error("ask_question", e, question_length=len(question))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process question: {str(e)}"
            )

    async def summarize_film(
        self, 
        session: AsyncSession, 
        request: FilmSummaryRequest
    ) -> FilmSummary:
        """
        Generate structured film summary with recommendation.
        
        Args:
            session: Database session
            request: Film summary request with film ID
            
        Returns:
            FilmSummary with title, rating, and recommendation
            
        Raises:
            HTTPException: If film not found or processing fails
        """
        if request.film_id <= 0:
            self.log_validation_error("summarize_film", ["Film ID must be positive"], film_id=request.film_id)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Film ID must be positive"
            )

        self.log_operation_start("summarize_film", film_id=request.film_id)

        # Get film from database
        film = await self.film_repository.get_film_by_id(session, request.film_id)
        
        if not film:
            self.logger.warning("Film not found", film_id=request.film_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Film with ID {request.film_id} not found"
            )

        AILogger.log_ai_request(
            "summarize_film", 
            settings.OPENAI_MODEL_ID, 
            film_id=request.film_id,
            film_title=film.title,
            film_rating=film.rating,
            rental_rate=float(film.rental_rate)
        )

        try:
            # Create prompt for film summary
            prompt = self._create_summary_prompt(film)
            # Create chat history with structured output schema
            history = ChatHistory()
            # Create system message with FilmSummary schema
            schema_description = self._get_film_summary_schema_description()
            system_message = f"""
                # Description:
                You are an API that returns film summaries in strict JSON format. 
                You must return a valid JSON object matching this exact schema: {schema_description}

                # Rules:
                - title: Extract or use the film's title
                - rating: Use the film's actual rating (G, PG, PG-13, R, NC-17)
                - recommended: Set to true if rating is mature (R or NC-17) AND rental_rate < 3.00, false otherwise
                - Return ONLY valid JSON with no additional text or explanations

                # Example Response:
                ```json
                {{
                    "title": "Film Title",
                    "rating": "PG-13",
                    "recommended": true
                }}
                ```

            """;
            history.add_system_message(system_message)
            history.add_user_message(prompt)
            # Get chat completion service
            chat_completion_service = self.kernel.get_service(type=ChatCompletionClientBase)
            # Get JSON execution settings
            execution_settings: OpenAIChatPromptExecutionSettings = get_json_execution_settings(response_schema=FilmSummary)
            # Get the response
            response = await chat_completion_service.get_chat_message_content(
                chat_history=history,
                settings=execution_settings
            )
            # Parse and validate the JSON response with Pydantic
            result = self._parse_and_validate_response(response, film)
            
            AILogger.log_ai_response(
                "summarize_film",
                settings.OPENAI_MODEL_ID,
                film_id=request.film_id,
                recommended=result.recommended
            )
            
            self.log_operation_success("summarize_film", film_id=request.film_id, recommended=result.recommended)
            
            return result
            
        except Exception as e:
            self.log_operation_error("summarize_film", e, film_id=request.film_id)
            AILogger.log_ai_error("summarize_film", e, film_id=request.film_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate film summary: {str(e)}"
            )


    def _create_summary_prompt(self, film: Film) -> str:
        """
        Create prompt for film summary with JSON response format.
        
        Args:
            film: Film model instance
            
        Returns:
            Formatted prompt string
        """
        return f"""
        Analyze the following film and provide a summary in JSON format:
        
        Title: {film.title or "Unknown"}  # type: ignore
        Description: {film.description or "No description available"}  # type: ignore
        Rating: {film.rating or "Not Rated"}  # type: ignore
        Rental Rate: ${film.rental_rate or 0.0:.2f}  # type: ignore
        Length: {film.length or 0} minutes  # type: ignore
        Release Year: {film.release_year or 0}  # type: ignore
        
        Return JSON with keys:
        - title: Film title
        - rating: Film rating (G, PG, PG-13, R, NC-17)
        - recommended: true if rating is more mature than PG-13 AND rental_rate < 3.00, false otherwise

        Example Response:
        ```json
        {{
            "title": "Film Title",
            "rating": "PG-13",
            "recommended": true
        }}
        ```
        """

    def _calculate_recommendation(self, film: Film) -> bool:
        """
        Calculate recommendation based on business rules.
        
        Args:
            film: Film model instance
            
        Returns:
            True if recommended, False otherwise
        """
        # Recommend if rating is more mature than PG-13 and rental rate < 3.00
        mature_ratings = ["R", "NC-17"]
        rating_is_mature = (film.rating or "") in mature_ratings  # type: ignore
        rental_is_cheap = (film.rental_rate or 0.0) < 3.00  # type: ignore
        
        return rating_is_mature and rental_is_cheap  # type: ignore

    def _get_film_summary_schema_description(self) -> str:
        """
        Get the JSON schema description for FilmSummary.
        
        Returns:
            Formatted schema description string
        """
        return """
        {
            "title": "string (required) - The film's title",
            "rating": "string (required) - Film rating: G, PG, PG-13, R, or NC-17", 
            "recommended": "boolean (required) - true if rating is R/NC-17 AND rental_rate < 3.00"
        }
        """

    def _parse_and_validate_response(self, response: Any, film: Film) -> FilmSummary:
        """
        Parse AI response and validate with Pydantic.
        
        Args:
            response: AI response object
            film: Original film for fallback data
            
        Returns:
            Validated FilmSummary object
            
        Raises:
            HTTPException: If parsing or validation fails
        """
        try:
            # Extract response text
            response_text = str(response).strip()

            # Parse JSON
            try:
                summary_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                # Try to extract JSON from response if it contains extra text
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    summary_data = json.loads(json_match.group())
                else:
                    raise e
            
            # Validate with Pydantic
            try:
                return FilmSummary(**summary_data)
            except ValidationError:
                # Enhanced fallback with partial data from AI response
                return FilmSummary(
                    title=summary_data.get("title", film.title or "Unknown"),  # type: ignore
                    rating=summary_data.get("rating", film.rating or "Not Rated"),  # type: ignore
                    recommended=bool(summary_data.get("recommended", self._calculate_recommendation(film)))
                )
                
        except (json.JSONDecodeError, ValidationError, Exception):
            # Complete fallback using film data
            return FilmSummary(
                title=film.title or "Unknown",  # type: ignore
                rating=film.rating or "Not Rated",  # type: ignore
                recommended=self._calculate_recommendation(film)
            )

    def _agent_response_callback(self, message: ChatMessageContent) -> None:
        """
        Callback to log and track agent responses.
        
        Args:
            message: Chat message from agent
        """
        self.conversation_history.append(message)
        self.logger.info(
            "Agent response received",
            agent=message.name or "Unknown",
            content_length=len(message.content or ""),
            role=str(message.role)
        )

    def _setup_orchestration(self, session: AsyncSession):
        """Setup Semantic Kernel HandoffOrchestration with agent routing."""

        # Create specialized agents
        search_agent = SearchAgentFactory.create_search_agent(session)
        llm_agent = LLMAgentFactory.create_llm_agent()
        
        # Define handoff relationships using OrchestrationHandoffs
        # SearchAgent is the front-desk agent that decides whether to handle or handoff
        handoffs = (
            OrchestrationHandoffs()
            .add(
                source_agent=search_agent.name,
                target_agent=llm_agent.name,
                description=f"""
                Transfer to {llm_agent.name} if the question is not related to DVD rentals, films, 
                movies, rental rates, customer rentals, film database queries, or streaming availability.
                
                Examples of questions to transfer to {llm_agent.name}:
                - General knowledge questions (science, history, current events)
                - Math problems and calculations
                - Technology questions unrelated to DVD rental business
                - Educational questions
                - Creative writing or brainstorming
                - Questions about topics completely outside the DVD rental domain
                
                Keep handling questions about:
                - Film searches, titles, details
                - Rental rates, availability, policies
                - Customer rental history
                - Streaming availability
                - Movie recommendations from our catalog
                """
            )
        )
        # Create HandoffOrchestration - SearchAgent is the front-desk agent
        self.orchestration = HandoffOrchestration(
            members=[search_agent, llm_agent],
            handoffs=handoffs,
            agent_response_callback=self._agent_response_callback
        )
        
        self.logger.info("HandoffOrchestration setup completed")

        self.runtime.start()
        self.logger.info("Runtime started")
        
    async def process_question(self, question: str, session: AsyncSession) -> Dict[str, Any]:
        """
        Process question through HandoffOrchestration.
        
        Args:
            question: User question to process
            
        Returns:
            Dictionary with agent response and metadata
        """
        self.logger.info("Processing question with handoff orchestration", question_length=len(question))
        self._setup_orchestration(session)
        try:
            # Clear conversation history for this question
            self.conversation_history.clear()
            # Invoke orchestration with SearchAgent as initial handler
            # The agents will decide internally whether to handle or handoff based on system prompts
            task_message = f"Customer question: {question}"
            self.logger.info("Invoking orchestration", task=task_message)
            orchestration_result = await self.orchestration.invoke(
                task=task_message,
                runtime=self.runtime
            )

            await orchestration_result.get()
            # Extract agent information from the conversation history
            selected_agent, response = self._extract_final_agent_from_history()
            self.logger.info("Orchestration completed", response_length=len(str(response)))
            return {
                "agent": selected_agent,
                "answer": str(response).strip(),
                "metadata": {
                    "orchestration_used": True,
                    "question_length": len(question),
                    "conversation_turns": len(self.conversation_history),
                    "runtime_used": "InProcessRuntime"
                }
            }
            
        except Exception as e:
            self.logger.error("Orchestration processing failed", error=str(e), question_length=len(question))
            
            # Fallback response
            return {
                "agent": "SystemFallback",
                "answer": "I apologize, but I'm unable to process your question at the moment. Please try again later.",
                "metadata": {
                    "error": str(e),
                    "orchestration_used": False,
                    "fallback_used": True
                }
            }
        finally:
            # Clean up runtime
            if self.runtime:
                try:
                    await self.runtime.stop_when_idle()
                    self.logger.info("Runtime stopped successfully")
                except Exception as e:
                    self.logger.warning("Runtime cleanup failed", error=str(e))
                    
    def _extract_final_agent_from_history(self) -> tuple[str, str]:
        """
        Extract which agent provided the final response from conversation history.
        
        Returns:
            Name of the agent that provided the final response
        """
        if not self.conversation_history:
            return "Unknown", "Unknown"
        
        # Look for the last assistant message in the conversation
        for message in reversed(self.conversation_history):
            if message.role == AuthorRole.ASSISTANT and message.name:
                return message.name, message.content
        
        # Fallback: analyze content to guess the agent
        if self.conversation_history:
            last_message = self.conversation_history[-1]
            content = (last_message.content or "").lower()
            
            # Check for database/film-related content
            film_keywords = ["film", "movie", "rental", "dvd", "streaming", "customer", "database"]
            if any(keyword in content for keyword in film_keywords):
                return "SearchAgent", last_message.content
            else:
                return "LLMAgent", last_message.content
        
        return "Unknown", "Unknown"
    
    def get_conversation_history(self) -> List[ChatMessageContent]:
        """
        Get the conversation history for debugging.
        
        Returns:
            List of chat messages from the conversation
        """
        return self.conversation_history.copy()
    
    async def cleanup(self):
        """Clean up resources."""
        if self.runtime:
            try:
                await self.runtime.stop()
                self.logger.info("HandoffOrchestrationService cleanup completed")
            except Exception as e:
                self.logger.error("Cleanup failed", error=str(e))