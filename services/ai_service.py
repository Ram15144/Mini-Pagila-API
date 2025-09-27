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


class AIService(LoggingMixin):
    """Service for AI operations using Semantic Kernel."""

    def __init__(self, kernel: Optional[Kernel] = None):
        """Initialize AI service with Semantic Kernel."""
        super().__init__()
        self.kernel = kernel or get_kernel()
        self.film_repository = FilmRepository()
        self.logger.info("AI service initialized", model="gpt-4o-mini")

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

        AILogger.log_ai_request("ask_question", "gpt-4o-mini", question_length=len(question))

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
                "gpt-4o-mini", 
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
            "gpt-4o-mini", 
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
                "gpt-4o-mini",
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
