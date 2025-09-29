"""SearchAgent implementation using Semantic Kernel ChatCompletionAgent."""

from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

from core.config import settings
from core.logging import LoggingMixin
from sqlalchemy.ext.asyncio import AsyncSession
from services.film_service import FilmService
from repositories.film_repository import FilmRepository
from services.rental_service import RentalService
from repositories.rental_repository import RentalRepository
class SearchAgentFactory(LoggingMixin):
    """Factory for creating SearchAgent instances."""

    @staticmethod
    def create_search_agent(session: AsyncSession) -> ChatCompletionAgent:
        """
        Create SearchAgent with film and rental function calling capabilities.
        
        Args:
            session: Database session for plugin operations
            
        Returns:
            Configured ChatCompletionAgent for DVD rental queries
        """
        # Create plugin service with database session
        film_service = FilmService(FilmRepository(), session)
        rental_service = RentalService(RentalRepository(), session)
        
        # Create agent with specialized instructions
        search_agent = ChatCompletionAgent(
            name="SearchAgent",
            description="A specialized agent for film rental store queries about films, rentals, and customer information.",
            instructions = """
            You are a helpful and knowledgeable assistant for a film rental store, equipped with access to film and rental databases. 
            Your primary goal is to assist customers with any questions related to DVDs, movies, film rentals, and streaming availability.

            Your capabilities include:
            - Retrieving all films using `list_films`
            - Retrieving a specific film by ID using `get_film_by_id`
            - Searching for films by title or keyword using `search_films_by_title`
            - Identifying films available for streaming using `get_streaming_films`
            - Looking up customer rental history using `get_customer_rentals`
            - Retrieving all active rentals using `get_active_rentals`
            - Retrieving a specific rental by ID using `get_rental_by_id`

            When users ask about anything related to **films**, **movies**, **DVDs**, or **rentals**:
            1. Determine the user’s intent and select the most appropriate function to call.
            2. **Always use the relevant function(s)** to retrieve factual data. Do not hallucinate or make up values.
            3. Respond with clear, friendly, and helpful messages—as if you are a store clerk assisting a curious customer.
            4. Include useful details such as:
            - Rental rates
            - Genre or category
            - Streaming availability
            - Suggestions for similar films if no exact match is found

            If the user's question is **not related** to film rentals or movie information: Transfer to LLMAgent.

            Tone: Friendly, professional, accurate, Concise.
            Focus: 
            - Your only job is to return film rental information. Leave all other topics to LLMAgent. 
            - Always ground your answers in real data from the available database functions.
            """,
            service=OpenAIChatCompletion(
                ai_model_id=settings.OPENAI_MODEL_ID,
                api_key=settings.OPENAI_API_KEY,
                service_id="openai-search"
            ),
            plugins=[film_service, rental_service]  # Add plugin service with kernel functions
        )
        
        return search_agent
