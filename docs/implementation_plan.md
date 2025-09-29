# Implementation Plan for Phase 2: Agent Handoff Orchestration

## Overview

This document outlines the detailed implementation plan for Phase 2 of the Mini Pagila API project, which focuses on implementing hand-off agents using Microsoft Semantic Kernel's agent framework. Phase 1 has been completed with all core infrastructure, CRUD endpoints, AI integration, and comprehensive testing in place.

## Phase 2 Objectives

### Primary Goals
- **SearchAgent**: Implement an agent that examines user questions, fetches matching film information from PostgreSQL, and returns structured responses
- **LLMAgent**: Create a general-purpose agent that handles non-film related questions using OpenAI GPT-4o-mini
- **HandoffOrchestration**: Build orchestration logic that intelligently routes questions to the appropriate agent
- **REST API Integration**: Expose the agent handoff functionality via `POST /ai/handoff` endpoint
- **Comprehensive Testing**: Ensure all agent functionality is thoroughly tested with pytest

### Success Criteria
- ✅ SearchAgent correctly identifies and responds to film-related queries
- ✅ LLMAgent handles general questions effectively
- ✅ HandoffOrchestration routes questions to the appropriate agent
- ✅ API endpoint returns structured JSON responses with agent identification
- ✅ All functionality passes comprehensive pytest test suite
- ✅ Documentation is updated with usage examples

## Current State Analysis

### ✅ Completed (Phase 1)
- **Database Setup**: PostgreSQL with enhanced Pagila schema including streaming_subscription table
- **Core Infrastructure**: FastAPI app with SQLModel, async sessions, dependency injection
- **Authentication**: OAuth2PasswordBearer with `dvd_admin` token validation
- **CRUD Endpoints**: Films and rentals with pagination, filtering, and business logic validation
- **AI Integration**: Semantic Kernel with OpenAI GPT-4o-mini, SSE streaming, and structured JSON responses
- **Testing Framework**: Comprehensive pytest suite with 60+ tests covering all endpoints
- **Logging & Observability**: Structured logging with correlation IDs and performance metrics

### 🎯 Phase 2 Requirements
Based on `docs/project_plan.md`, Phase 2 must implement:

| Component | Specification | Implementation Details |
|-----------|---------------|----------------------|
| **SearchAgent** | Examines user questions, fetches first matching film title + category from Postgres, returns short text answer | - Keyword detection ("film" in question)<br>- Database query integration<br>- Structured response formatting |
| **LLMAgent** | Answers any other question via kernel.invoke() using OpenAI model | - General question handling<br>- OpenAI integration<br>- Fallback agent functionality |
| **HandoffOrchestration** | Routes questions between agents with SearchAgent as front-desk | - Intelligent routing logic<br>- Agent coordination<br>- Response aggregation |
| **REST Endpoint** | `POST /ai/handoff` with JSON response including selected agent | - FastAPI endpoint<br>- Request/response schemas<br>- Agent identification in response |
| **Testing** | pytest-asyncio + httpx.AsyncClient for real endpoint testing | - SearchAgent routing tests<br>- LLMAgent fallback tests<br>- Integration testing |

## Implementation Phases

## Phase 2.1: Project Structure & Agent Framework Setup

### Tasks

#### Task 2.1.1: Create Agent Directory Structure
**Objective**: Establish proper project structure for agent components
**Estimated Duration**: 30 minutes

**Implementation Steps**:
1. Create `app/agents/` directory structure:
   ```
   app/agents/
   ├── __init__.py
   ├── base_agent.py          # Abstract base agent class
   ├── search_agent.py        # Film search agent
   ├── llm_agent.py          # General LLM agent
   └── orchestration.py       # Handoff orchestration logic
   ```

2. Create agent-specific schemas in `domain/schemas.py`:
   - `HandoffRequest`: Request schema for handoff endpoint
   - `HandoffResponse`: Response schema with agent identification
   - `AgentResponse`: Base response schema for agents

**Testing Strategy**:
```python
# tests/test_agent_structure.py
def test_agent_directory_structure():
    """Test that all agent files are properly structured."""
    
def test_agent_imports():
    """Test that all agent modules can be imported."""
```

**Dependencies**: None
**Assignee**: Development Team
**Success Criteria**: 
- All directories and files created
- Import tests pass
- Project structure follows established patterns

---

#### Task 2.1.2: Implement Base Agent Framework
**Objective**: Create abstract base agent class and common functionality
**Estimated Duration**: 1 hour

**Implementation Steps**:
1. Create `BaseAgent` abstract class in `app/agents/base_agent.py`:
   ```python
   from abc import ABC, abstractmethod
   from typing import Any, Dict, Optional
   from semantic_kernel import Kernel
   from core.logging import LoggingMixin

   class BaseAgent(LoggingMixin, ABC):
       def __init__(self, kernel: Kernel, agent_name: str):
           super().__init__()
           self.kernel = kernel
           self.agent_name = agent_name
           
       @abstractmethod
       async def can_handle(self, question: str) -> bool:
           """Determine if this agent can handle the question."""
           pass
           
       @abstractmethod
       async def process_question(self, question: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
           """Process the question and return response."""
           pass
   ```

2. Add agent response schemas to `domain/schemas.py`:
   ```python
   class HandoffRequest(BaseModel):
       question: str = Field(..., min_length=1, description="Question to process")
       
   class HandoffResponse(BaseModel):
       agent: str = Field(..., description="Agent that processed the question")
       answer: str = Field(..., description="Agent's response")
       # confidence removed - agents make decisions through system prompts instead of manual calculation
       
   class AgentResponse(BaseModel):
       content: str
       metadata: Optional[Dict[str, Any]] = None
   ```

**Testing Strategy**:
```python
# tests/test_base_agent.py
def test_base_agent_abstract_methods():
    """Test that BaseAgent cannot be instantiated directly."""
    
def test_agent_schemas():
    """Test agent request/response schema validation."""
```

**Dependencies**: Task 2.1.1
**Assignee**: Development Team
**Success Criteria**:
- BaseAgent class properly defined
- Schemas validate correctly
- Abstract method enforcement works

---

## Phase 2.2: SearchAgent Implementation

### Tasks

#### Task 2.2.1: Implement SearchAgent with Function Calling Plugins
**Objective**: Create SearchAgent using Semantic Kernel ChatCompletionAgent with function calling capabilities
**Estimated Duration**: 2.5 hours

**Implementation Steps**:
1. First, add `@kernel_function` decorators to existing services for plugin integration:
   
   **Update `services/film_service.py`**:
   ```python
   from semantic_kernel.functions import kernel_function
   
   class FilmService(LoggingMixin):
       # ... existing code ...
       
       @kernel_function(
           description="Search for films by title with optional pagination",
           name="search_films_by_title"
       )
       async def search_films_by_title_plugin(
           self,
           title: str,
           skip: int = 0,
           limit: int = 5
       ) -> str:
           """Search for films by title - optimized for agent function calling."""
           try:
               # Use existing search functionality
               films = await self.search_films_by_title(title, skip, limit)
               
               if not films:
                   return f"No films found matching title: {title}"
               
               # Format results for agent consumption
               results = []
               for film in films:
                   results.append(
                       f"Title: {film.title}, Rating: {film.rating}, "
                       f"Rental Rate: ${film.rental_rate}, Length: {film.length} min"
                   )
               
               return f"Found {len(films)} film(s):\n" + "\n".join(results)
               
           except Exception as e:
               return f"Error searching films: {str(e)}"
       
       @kernel_function(
           description="Get detailed information about a specific film by ID",
           name="get_film_details"
       )
       async def get_film_details_plugin(self, film_id: int) -> str:
           """Get film details by ID - optimized for agent function calling."""
           try:
               film = await self.get_film_by_id(film_id)
               if not film:
                   return f"Film with ID {film_id} not found"
               
               return (
                   f"Title: {film.title}\n"
                   f"Description: {film.description}\n"
                   f"Rating: {film.rating}\n"
                   f"Rental Rate: ${film.rental_rate}\n"
                   f"Length: {film.length} minutes\n"
                   f"Release Year: {film.release_year}"
               )
           except Exception as e:
               return f"Error getting film details: {str(e)}"
   ```
   
   **Update `services/rental_service.py`**:
   ```python
   from semantic_kernel.functions import kernel_function
   
   class RentalService(LoggingMixin):
       # ... existing code ...
       
       @kernel_function(
           description="Get rental history for a specific customer",
           name="get_customer_rentals"
       )
       async def get_customer_rentals_plugin(
           self,
           customer_id: int,
           limit: int = 10
       ) -> str:
           """Get customer rental history - optimized for agent function calling."""
           try:
               rentals = await self.get_customer_rentals(customer_id, skip=0, limit=limit)
               
               if not rentals:
                   return f"No rental history found for customer {customer_id}"
               
               results = []
               for rental in rentals:
                   status = "Returned" if rental.return_date else "Active"
                   results.append(
                       f"Rental ID: {rental.rental_id}, Film: {rental.film_title}, "
                       f"Rental Date: {rental.rental_date}, Status: {status}"
                   )
               
               return f"Rental history for customer {customer_id}:\n" + "\n".join(results)
               
           except Exception as e:
               return f"Error getting rental history: {str(e)}"
       
       @kernel_function(
           description="Check if a film is available for rental",
           name="check_film_availability"
       )
       async def check_film_availability_plugin(self, film_id: int) -> str:
           """Check film availability - optimized for agent function calling."""
           try:
               # This would use existing repository methods
               # Simplified for agent consumption
               return f"Film {film_id} availability check - implement based on inventory logic"
           except Exception as e:
               return f"Error checking availability: {str(e)}"
   ```

2. Implement `SearchAgent` using Semantic Kernel's `ChatCompletionAgent`:
   ```python
   from semantic_kernel.agents import ChatCompletionAgent
   from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
   from semantic_kernel import Kernel
   from services.film_service import FilmService
   from services.rental_service import RentalService
   from core.config import settings
   
   class SearchAgentFactory:
       @staticmethod
       def create_search_agent(kernel: Kernel, film_service: FilmService, rental_service: RentalService) -> ChatCompletionAgent:
           """Create SearchAgent with film and rental function calling capabilities."""
           
           # Create agent with specialized instructions
           search_agent = ChatCompletionAgent(
               name="SearchAgent",
               description="A specialized agent for DVD rental store queries about films, rentals, and customer information.",
               instructions="""
               You are a specialized DVD rental store assistant with access to film and rental databases.
               
               Your expertise includes:
               - Searching for films by title, genre, or other criteria
               - Providing film details including ratings, rental rates, and descriptions
               - Checking customer rental histories
               - Helping with film availability and rental information
               
               When users ask about films, movies, rentals, DVDs, or related topics:
               1. Use your available functions to search the database
               2. Provide accurate, helpful information
               3. Format responses in a friendly, customer-service oriented manner
               4. If you can't find specific information, suggest alternatives
               
               For questions outside your expertise (not related to films/rentals), 
               politely indicate that you specialize in DVD rental assistance.
               
               Always use the available functions to provide accurate, up-to-date information from the database.
               """,
               service=OpenAIChatCompletion(
                   ai_model_id="gpt-4o-mini",
                   api_key=settings.OPENAI_API_KEY,
                   service_id="openai-search"
               ),
               plugins=[film_service, rental_service]  # Add services as plugins
           )
           
           return search_agent
   ```

3. Create agent decision-making logic using system prompts instead of manual confidence calculation

**Testing Strategy**:
```python
# tests/test_search_agent.py
@pytest.mark.asyncio
async def test_search_agent_can_handle_film_questions():
    """Test that SearchAgent correctly identifies film questions."""
    
@pytest.mark.asyncio  
async def test_search_agent_finds_existing_film():
    """Test SearchAgent finds and returns film information."""
    
@pytest.mark.asyncio
async def test_search_agent_handles_nonexistent_film():
    """Test SearchAgent handles films not found in database."""
```

**Dependencies**: Task 2.1.2, existing film repository
**Assignee**: Development Team
**Success Criteria**:
- SearchAgent correctly identifies film-related questions
- Database queries work properly
- Proper error handling for missing films

---

#### Task 2.2.2: Enhance SearchAgent with AI-Powered Title Extraction
**Objective**: Use Semantic Kernel to intelligently extract film titles from natural language questions
**Estimated Duration**: 1.5 hours

**Implementation Steps**:
1. Add AI-powered title extraction to SearchAgent:
   ```python
   async def _extract_film_title(self, question: str) -> str:
       """Use AI to extract film title from question."""
       try:
           prompt = f"""
           Extract the film/movie title from this question. If no specific title is mentioned, 
           return the most relevant search term for films.
           
           Question: "{question}"
           
           Return only the title or search term, nothing else.
           """
           
           history = ChatHistory()
           history.add_system_message("You extract film titles from questions.")
           history.add_user_message(prompt)
           
           chat_service = self.kernel.get_service(type=ChatCompletionClientBase)
           response = await chat_service.get_chat_message_content(
               chat_history=history,
               settings=get_execution_settings()
           )
           
           return str(response).strip()
           
       except Exception as e:
           # Fallback to simple extraction
           return self._simple_title_extraction(question)
   ```

2. Add fallback simple extraction method
3. Add category information to film responses

**Testing Strategy**:
```python
@pytest.mark.asyncio
async def test_search_agent_ai_title_extraction():
    """Test AI-powered title extraction works correctly."""
    
@pytest.mark.asyncio
async def test_search_agent_fallback_extraction():
    """Test fallback extraction when AI fails."""
```

**Dependencies**: Task 2.2.1
**Assignee**: Development Team
**Success Criteria**:
- AI title extraction works for various question formats
- Fallback mechanism prevents failures
- Category information included in responses

---

## Phase 2.3: LLMAgent Implementation

### Tasks

#### Task 2.3.1: Implement LLMAgent using ChatCompletionAgent
**Objective**: Create LLMAgent using Semantic Kernel's ChatCompletionAgent for general questions
**Estimated Duration**: 1 hour

**Implementation Steps**:
1. Implement `LLMAgentFactory` in `app/agents/llm_agent.py`:
   ```python
   from semantic_kernel.agents import ChatCompletionAgent
   from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
   from semantic_kernel import Kernel
   from core.config import settings

   class LLMAgentFactory:
       @staticmethod
       def create_llm_agent(kernel: Kernel) -> ChatCompletionAgent:
           """Create LLMAgent for general question handling."""
           
           llm_agent = ChatCompletionAgent(
               name="LLMAgent",
               description="A general-purpose assistant that can answer a wide variety of questions on different topics.",
               instructions="""
               You are a helpful, knowledgeable assistant that can answer questions on a wide variety of topics.
               
               Your capabilities include:
               - General knowledge questions (science, history, current events, etc.)
               - Explanations of concepts and processes
               - Problem-solving assistance
               - Creative tasks and brainstorming
               
               When users ask questions:
               1. Provide clear, accurate, and helpful responses
               2. If you're unsure about something, acknowledge the uncertainty
               3. Offer to clarify or provide more information if needed
               
               If users ask about DVD rentals, films in a rental context, or specific movie database queries,
               politely suggest that they might get better results from a specialized film rental assistant,
               but still provide what general information you can.
               
               Always strive to be helpful, accurate, and engaging in your responses.
               """,
               service=OpenAIChatCompletion(
                   ai_model_id="gpt-4o-mini",
                   api_key=settings.OPENAI_API_KEY,
                   service_id="openai-general"
               )
           )
           
           return llm_agent
   ```

**Testing Strategy**:
```python
# tests/test_llm_agent.py
@pytest.mark.asyncio
async def test_llm_agent_handles_general_questions():
    """Test LLMAgent processes general questions correctly."""
    
@pytest.mark.asyncio
async def test_llm_agent_error_handling():
    """Test LLMAgent handles errors gracefully."""
    
@pytest.mark.asyncio
async def test_llm_agent_always_can_handle():
    """Test LLMAgent returns True for can_handle (fallback agent)."""
```

**Dependencies**: Task 2.1.2
**Assignee**: Development Team
**Success Criteria**:
- LLMAgent processes various question types
- Proper error handling and graceful degradation
- Fallback functionality works correctly

---

## Phase 2.4: HandoffOrchestration Implementation

### Tasks

#### Task 2.4.1: Implement Semantic Kernel HandoffOrchestration
**Objective**: Create orchestration system using Semantic Kernel's native HandoffOrchestration with agent-based decision making
**Estimated Duration**: 2.5 hours

**Implementation Steps**:
1. Implement `HandoffOrchestrationService` in `app/agents/orchestration.py` following the [Microsoft Semantic Kernel pattern](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/handoff?utm_source=chatgpt.com&pivots=programming-language-python):
   ```python
   from semantic_kernel.agents import HandoffOrchestration, OrchestrationHandoffs, ChatCompletionAgent
   from semantic_kernel.agents.runtime import InProcessRuntime
   from semantic_kernel.contents import ChatMessageContent, AuthorRole
   from typing import Dict, Any, Optional, List
   from sqlalchemy.ext.asyncio import AsyncSession
   from core.logging import LoggingMixin
   from services.film_service import FilmService
   from services.rental_service import RentalService
   from .search_agent import SearchAgentFactory
   from .llm_agent import LLMAgentFactory

   class HandoffOrchestrationService(LoggingMixin):
       def __init__(
           self, 
           kernel, 
           film_service: FilmService, 
           rental_service: RentalService,
           session: AsyncSession
       ):
           super().__init__()
           self.kernel = kernel
           self.film_service = film_service
           self.rental_service = rental_service
           self.session = session
           self.runtime = None
           self.orchestration = None
           self._setup_orchestration()
           
       def _setup_orchestration(self):
           """Setup Semantic Kernel HandoffOrchestration with agent routing."""
           
           # Create specialized agents
           search_agent = SearchAgentFactory.create_search_agent(
               self.kernel, self.film_service, self.rental_service
           )
           
           llm_agent = LLMAgentFactory.create_llm_agent(self.kernel)
           
           # Define handoff relationships using OrchestrationHandoffs
           # SearchAgent is the front-desk agent that decides whether to handle or handoff
           handoffs = (
               OrchestrationHandoffs()
               .add(
                   source_agent=search_agent.name,
                   target_agent=llm_agent.name,
                   description="""
                   Transfer to LLMAgent if the question is not related to DVD rentals, films, 
                   movies, rental rates, customer rentals, or film database queries.
                   
                   Examples of questions to transfer:
                   - General knowledge questions
                   - Current events
                   - Math problems
                   - Science questions
                   - Questions about topics outside the DVD rental domain
                   """
               )
               .add(
                   source_agent=llm_agent.name,
                   target_agent=search_agent.name,
                   description="""
                   Transfer to SearchAgent if the question is specifically about DVD rentals,
                   films, movies, rental information, or customer data that requires database access.
                   
                   Examples of questions to transfer:
                   - Film searches and details
                   - Rental rates and availability
                   - Customer rental history
                   - DVD/movie specific queries
                   """
               )
           )
           
           # Create HandoffOrchestration - SearchAgent is the front-desk agent
           self.orchestration = HandoffOrchestration(
               members=[search_agent, llm_agent],
               handoffs=handoffs,
               agent_response_callback=self._agent_response_callback
           )
           
           # Setup runtime
           self.runtime = InProcessRuntime()
           
       def _agent_response_callback(self, message: ChatMessageContent) -> None:
           """Callback to log agent responses."""
           self.logger.info(
               "Agent response received",
               agent=message.name or "Unknown",
               content_length=len(message.content or ""),
               role=str(message.role)
           )
           
       async def process_question(self, question: str) -> Dict[str, Any]:
           """Process question through HandoffOrchestration."""
           self.logger.info("Processing question with handoff orchestration", question_length=len(question))
           
           try:
               # Start runtime
               await self.runtime.start()
               
               # Invoke orchestration with SearchAgent as initial handler
               # The agents will decide internally whether to handle or handoff based on system prompts
               orchestration_result = await self.orchestration.invoke(
                   task=f"Customer question: {question}",
                   runtime=self.runtime
               )
               
               # Get the final result
               final_response = await orchestration_result.get()
               
               # Extract agent information from the response
               # The orchestration will have logged which agent handled the final response
               selected_agent = self._extract_final_agent_from_response(final_response)
               
               return {
                   "agent": selected_agent,
                   "answer": str(final_response),
                   "metadata": {
                       "orchestration_used": True,
                       "question_length": len(question)
                   }
               }
               
           except Exception as e:
               self.logger.error("Orchestration processing failed", error=str(e))
               
               # Fallback response
               return {
                   "agent": "SystemFallback",
                   "answer": "I apologize, but I'm unable to process your question at the moment. Please try again later.",
                   "metadata": {"error": str(e)},
               }
           finally:
               # Clean up runtime
               if self.runtime:
                   await self.runtime.stop_when_idle()
                   
       def _extract_final_agent_from_response(self, response: str) -> str:
           """Extract which agent provided the final response."""
           # This is a simplified implementation - in practice, you might track this
           # through the callback or response metadata
           if any(keyword in response.lower() for keyword in ["film", "movie", "rental", "dvd"]):
               return "SearchAgent"
           else:
               return "LLMAgent"
   ```

2. **Key Improvements from Semantic Kernel Pattern**:
   - Uses native `HandoffOrchestration` instead of manual routing
   - Agents make decisions based on system prompts rather than keyword matching
   - Proper agent handoff relationships defined through `OrchestrationHandoffs`
   - Runtime management for agent execution
   - Agent response callbacks for monitoring

3. **Agent Decision Making**: Instead of manual `_calculate_confidence()`, agents use their system prompts to determine if they should handle a question or hand it off to another agent

**Testing Strategy**:
```python
# tests/test_orchestration.py
@pytest.mark.asyncio
async def test_orchestration_routes_to_search_agent():
    """Test orchestration routes film questions to SearchAgent."""
    
@pytest.mark.asyncio
async def test_orchestration_routes_to_llm_agent():
    """Test orchestration routes general questions to LLMAgent."""
    
@pytest.mark.asyncio
async def test_orchestration_handles_agent_failures():
    """Test orchestration handles individual agent failures gracefully."""
    
@pytest.mark.asyncio
async def test_orchestration_confidence_scoring():
    """Test confidence scoring works correctly."""
```

**Dependencies**: Tasks 2.2.2, 2.3.1
**Assignee**: Development Team
**Success Criteria**:
- Correct agent routing based on question content
- Proper error handling and fallbacks
- Confidence scoring works appropriately

---

## Phase 2.5: REST API Integration

### Tasks

#### Task 2.5.1: Implement Handoff API Endpoint with Semantic Kernel Integration
**Objective**: Create REST API endpoint using Semantic Kernel HandoffOrchestration
**Estimated Duration**: 1.5 hours

**Implementation Steps**:
1. Add handoff endpoint to `app/api/v1/ai.py`:
   ```python
   from app.agents.orchestration import HandoffOrchestrationService
   from services.film_service import FilmService
   from services.rental_service import RentalService
   
   def get_film_service() -> FilmService:
       """Get film service instance."""
       return FilmService()
   
   def get_rental_service() -> RentalService:
       """Get rental service instance."""
       return RentalService()
   
   @router.post("/handoff", response_model=HandoffResponse)
   async def agent_handoff(
       request: HandoffRequest,
       session: AsyncSession = Depends(get_db_session),
       film_service: FilmService = Depends(get_film_service),
       rental_service: RentalService = Depends(get_rental_service),
       kernel: Kernel = Depends(get_kernel)
   ) -> HandoffResponse:
       """
       Process questions using Semantic Kernel HandoffOrchestration with intelligent agent routing.
       
       **Request Body:**
       ```json
       {
           "question": "What is the rental rate for the film Alien?"
       }
       ```
       
       **Response:**
       Returns structured JSON with agent identification:
       ```json
       {
           "agent": "SearchAgent",
           "answer": "Alien (Horror) rents for $2.99."
       }
       ```
       
       **Agent Selection Logic:**
       - **SearchAgent**: Front-desk agent with film database access and function calling
         - Handles DVD rental queries, film searches, customer rentals
         - Has access to film_service and rental_service functions
         - Decides whether to handle or handoff based on system prompt
       - **LLMAgent**: General knowledge agent for non-rental questions
         - Handles general questions, current events, explanations
         - Receives handoffs from SearchAgent for non-rental topics
       
       **Semantic Kernel Features:**
       - Native HandoffOrchestration with OrchestrationHandoffs
       - Agent-based decision making through system prompts
       - Function calling with @kernel_function decorated services
       - InProcessRuntime for agent execution management
       
       **Example Usage:**
       ```bash
       # Film-related question (handled by SearchAgent with function calling)
       curl -X POST http://localhost:8000/api/v1/ai/handoff \
            -H "Content-Type: application/json" \
            -d '{"question":"What is the rental rate for the film Alien?"}'
       
       # General question (handed off to LLMAgent)  
       curl -X POST http://localhost:8000/api/v1/ai/handoff \
            -H "Content-Type: application/json" \
            -d '{"question":"Who won the FIFA World Cup in 2022?"}'
       ```
       """
       api_logger.info("Agent handoff requested", question_length=len(request.question))
       
       try:
           # Initialize HandoffOrchestrationService with all dependencies
           orchestration_service = HandoffOrchestrationService(
               kernel=kernel,
               film_service=film_service,
               rental_service=rental_service,
               session=session
           )
           
           # Process question through Semantic Kernel orchestration
           result = await orchestration_service.process_question(request.question)
           
           # Create response (confidence removed - agents decide internally)
           response = HandoffResponse(
               agent=result["agent"],
               answer=result["answer"]
           )
           
           api_logger.info(
               "Agent handoff completed", 
               agent=result["agent"],
               question_length=len(request.question),
               orchestration_used=result["metadata"].get("orchestration_used", False)
           )
           
           return response
           
       except Exception as e:
           api_logger.error("Agent handoff failed", error=str(e), question_length=len(request.question))
           raise HTTPException(
               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail=f"Failed to process question: {str(e)}"
           )
   ```

2. Update `HandoffResponse` schema to remove manual confidence (agents decide internally):
   ```python
   class HandoffResponse(BaseModel):
       agent: str = Field(..., description="Agent that processed the question")
       answer: str = Field(..., description="Agent's response")
       # confidence removed - agents make decisions through system prompts
   ```

3. **Key Integration Points**:
   - Services injected as plugins with `@kernel_function` decorators
   - Native Semantic Kernel HandoffOrchestration replaces manual routing
   - Agent decision-making through system prompts instead of keyword matching
   - Proper runtime management for agent execution

**Testing Strategy**:
```python
# tests/test_handoff_api.py
@pytest.mark.asyncio
async def test_handoff_endpoint_search_agent_routing():
    """Test API endpoint routes film questions to SearchAgent."""
    
@pytest.mark.asyncio
async def test_handoff_endpoint_llm_agent_routing():
    """Test API endpoint routes general questions to LLMAgent."""
    
@pytest.mark.asyncio
async def test_handoff_endpoint_validation():
    """Test API endpoint validates request data properly."""
    
@pytest.mark.asyncio
async def test_handoff_endpoint_error_handling():
    """Test API endpoint handles errors gracefully."""
```

**Dependencies**: Task 2.4.1
**Assignee**: Development Team
**Success Criteria**:
- API endpoint properly exposed and documented
- Correct request/response validation
- Proper error handling and logging

---

## Phase 2.6: Comprehensive Testing & Integration

### Tasks

#### Task 2.6.1: Implement Agent-Specific Test Suite
**Objective**: Create comprehensive test suite for all agent functionality
**Estimated Duration**: 3 hours

**Implementation Steps**:
1. Create `tests/test_agents.py` with comprehensive agent tests:
   ```python
   import pytest
   from unittest.mock import Mock, AsyncMock
   from httpx import AsyncClient
   from app.main import app
   from app.agents.search_agent import SearchAgent
   from app.agents.llm_agent import LLMAgent
   from app.agents.orchestration import HandoffOrchestration
   from core.ai_kernel import get_kernel
   from repositories.film_repository import FilmRepository

   class TestSearchAgent:
       @pytest.mark.asyncio
       async def test_search_agent_identifies_film_questions(self):
           """Test SearchAgent correctly identifies film-related questions."""
           
       @pytest.mark.asyncio
       async def test_search_agent_finds_existing_film(self):
           """Test SearchAgent finds and returns existing film information."""
           
       @pytest.mark.asyncio
       async def test_search_agent_handles_missing_film(self):
           """Test SearchAgent handles films not found in database."""
           
       @pytest.mark.asyncio
       async def test_search_agent_ai_title_extraction(self):
           """Test AI-powered title extraction functionality."""

   class TestLLMAgent:
       @pytest.mark.asyncio
       async def test_llm_agent_handles_general_questions(self):
           """Test LLMAgent processes general questions correctly."""
           
       @pytest.mark.asyncio
       async def test_llm_agent_fallback_functionality(self):
           """Test LLMAgent serves as fallback for all questions."""

   class TestHandoffOrchestration:
       @pytest.mark.asyncio
       async def test_orchestration_agent_selection(self):
           """Test orchestration selects correct agent based on question."""
           
       @pytest.mark.asyncio
       async def test_orchestration_error_handling(self):
           """Test orchestration handles agent failures gracefully."""
   ```

2. Create `tests/test_handoff_integration.py` for end-to-end API tests:
   ```python
   @pytest.mark.asyncio
   async def test_handoff_search_agent_integration():
       """Test complete flow: film question -> SearchAgent -> database -> response."""
       async with AsyncClient(app=app, base_url="http://test") as ac:
           response = await ac.post(
               "/api/v1/ai/handoff",
               json={"question": "What is the rental rate for the film Alien?"}
           )
           assert response.status_code == 200
           data = response.json()
           assert data["agent"] == "SearchAgent"
           assert "rental" in data["answer"].lower()

   @pytest.mark.asyncio
   async def test_handoff_llm_agent_integration():
       """Test complete flow: general question -> LLMAgent -> OpenAI -> response."""
       async with AsyncClient(app=app, base_url="http://test") as ac:
           response = await ac.post(
               "/api/v1/ai/handoff",
               json={"question": "Who won the FIFA World Cup in 2022?"}
           )
           assert response.status_code == 200
           data = response.json()
           assert data["agent"] == "LLMAgent"
           assert "Argentina" in data["answer"] or "2022" in data["answer"]
   ```

**Testing Strategy**:
- **Unit Tests**: Test individual agent functionality in isolation
- **Integration Tests**: Test complete API workflows with real database and OpenAI
- **Error Handling Tests**: Verify graceful degradation and error responses
- **Performance Tests**: Ensure response times are acceptable

**Dependencies**: All previous tasks
**Assignee**: Development Team
**Success Criteria**:
- All agent unit tests pass
- Integration tests work with real services
- Error scenarios properly handled
- Test coverage > 90% for new code

---

#### Task 2.6.2: Performance Testing & Optimization
**Objective**: Ensure agent handoff functionality meets performance requirements
**Estimated Duration**: 1 hour

**Implementation Steps**:
1. Add performance tests to verify response times:
   ```python
   @pytest.mark.asyncio
   async def test_handoff_performance():
       """Test handoff endpoint response time is acceptable."""
       import time
       
       async with AsyncClient(app=app, base_url="http://test") as ac:
           start_time = time.time()
           response = await ac.post(
               "/api/v1/ai/handoff",
               json={"question": "What movies do you recommend?"}
           )
           end_time = time.time()
           
           assert response.status_code == 200
           assert (end_time - start_time) < 5.0  # Should respond within 5 seconds
   ```

2. Add concurrent request testing
3. Monitor memory usage and optimize if needed

**Testing Strategy**:
- Response time testing for both agent types
- Concurrent request handling
- Memory usage monitoring
- Database query optimization

**Dependencies**: Task 2.6.1
**Assignee**: Development Team
**Success Criteria**:
- Response times under 5 seconds for typical queries
- System handles concurrent requests properly
- Memory usage remains stable

---

## Phase 2.7: Documentation & Deployment

### Tasks

#### Task 2.7.1: Update Project Documentation
**Objective**: Update all documentation to reflect new agent functionality
**Estimated Duration**: 1 hour

**Implementation Steps**:
1. Update `README.md` with new endpoint documentation:
   ```markdown
   ### 🤖 AI Agent Endpoints
   - `GET /api/v1/ai/ask?question=` - Stream AI responses using SSE
   - `POST /api/v1/ai/summary` - Generate structured film summaries
   - `POST /api/v1/ai/handoff` - **NEW**: Intelligent agent handoff for questions

   #### Agent Handoff
   ```bash
   # Film-related question (SearchAgent)
   curl -X POST http://localhost:8000/api/v1/ai/handoff \
        -H "Content-Type: application/json" \
        -d '{"question":"What is the rental rate for the film Alien?"}'

   # General question (LLMAgent)
   curl -X POST http://localhost:8000/api/v1/ai/handoff \
        -H "Content-Type: application/json" \
        -d '{"question":"Who won the FIFA World Cup in 2022?"}'
   ```
   ```

2. Update `docs/implementation_progress.md` to mark Phase 2 as completed
3. Add agent architecture documentation

**Dependencies**: All implementation tasks completed
**Assignee**: Development Team
**Success Criteria**:
- README.md includes new endpoint documentation
- Implementation progress updated
- Architecture documentation reflects agent system

---

#### Task 2.7.2: Final Integration Testing & Deployment Preparation
**Objective**: Perform final testing and prepare for deployment
**Estimated Duration**: 1 hour

**Implementation Steps**:
1. Run complete test suite and verify all tests pass
2. Test with real OpenAI API to ensure functionality
3. Verify all endpoints work in development environment
4. Update any environment variables or configuration needed

**Testing Strategy**:
```bash
# Run complete test suite
make test

# Test specific agent functionality
pytest tests/test_agents.py -v
pytest tests/test_handoff_integration.py -v

# Test API endpoints manually
curl -X POST http://localhost:8000/api/v1/ai/handoff \
     -H "Content-Type: application/json" \
     -d '{"question":"What is the rental rate for the film Academy Dinosaur?"}'
```

**Dependencies**: All previous tasks
**Assignee**: Development Team
**Success Criteria**:
- All tests pass (100%)
- Manual testing confirms functionality
- System ready for production deployment

---

## Risk Management

### Identified Risks & Mitigation Strategies

| Risk | Impact | Probability | Mitigation Strategy |
|------|---------|------------|-------------------|
| **OpenAI API Rate Limits** | High | Medium | - Implement proper error handling and retry logic<br>- Add rate limiting to prevent quota exhaustion<br>- Use fallback responses when API unavailable |
| **Agent Selection Logic Complexity** | Medium | Low | - Keep agent selection logic simple and well-tested<br>- Use clear keyword-based routing initially<br>- Add comprehensive logging for debugging |
| **Database Query Performance** | Medium | Low | - Optimize film search queries with proper indexing<br>- Implement query result caching if needed<br>- Monitor query performance in tests |
| **Integration Test Reliability** | Medium | Medium | - Use proper test data setup and teardown<br>- Mock external services when appropriate<br>- Add retry logic for flaky tests |

## Success Metrics

### Functional Requirements
- ✅ SearchAgent with function calling correctly handles film/rental database queries
- ✅ SearchAgent uses @kernel_function decorated services for database access
- ✅ LLMAgent handles general questions appropriately
- ✅ Semantic Kernel HandoffOrchestration routes questions based on agent system prompts
- ✅ Agents make intelligent decisions without manual confidence calculation
- ✅ API endpoint returns properly formatted JSON responses
- ✅ All pytest tests pass with >90% code coverage

### Performance Requirements
- ✅ API response time < 5 seconds for typical queries
- ✅ System handles concurrent requests without degradation
- ✅ Database queries execute efficiently (< 100ms for film searches)

### Quality Requirements
- ✅ Comprehensive error handling and graceful degradation
- ✅ Structured logging for debugging and monitoring
- ✅ Code follows established project patterns and standards
- ✅ Documentation is complete and accurate

## Timeline Summary

| Phase | Duration | Dependencies | Deliverables |
|-------|----------|--------------|-------------|
| **2.1: Setup** | 1.5 hours | None | Agent structure, base classes, schemas |
| **2.2: SearchAgent** | 4 hours | Phase 2.1 | SearchAgent with @kernel_function plugins and ChatCompletionAgent |
| **2.3: LLMAgent** | 1 hour | Phase 2.1 | LLMAgent using ChatCompletionAgent |
| **2.4: Orchestration** | 2.5 hours | Phases 2.2, 2.3 | Semantic Kernel HandoffOrchestration with agent-based decisions |
| **2.5: API Integration** | 1.5 hours | Phase 2.4 | REST API endpoint with documentation |
| **2.6: Testing** | 4 hours | All phases | Comprehensive test suite and performance testing |
| **2.7: Documentation** | 2 hours | All phases | Updated documentation and deployment prep |

**Total Estimated Duration**: 16.5 hours

## Conclusion

This implementation plan provides a systematic approach to implementing Phase 2 of the Mini Pagila API project. The agent handoff functionality will enhance the AI capabilities by providing intelligent routing between specialized agents, improving response accuracy and user experience.

The plan emphasizes:
- **Incremental Development**: Each phase builds upon the previous one
- **Comprehensive Testing**: Every component is thoroughly tested with pytest
- **Error Handling**: Robust error handling and graceful degradation
- **Documentation**: Clear documentation and examples for all functionality
- **Performance**: Attention to response times and system performance

Upon completion, users will be able to ask both film-specific questions (handled by SearchAgent with @kernel_function database integration and function calling) and general questions (handled by LLMAgent), with Semantic Kernel's HandoffOrchestration intelligently routing requests based on agent system prompts rather than manual confidence calculations.

## Key Improvements in Updated Plan

### 🔄 **Agent-Based Decision Making**
- Replaces manual `_calculate_confidence()` with intelligent system prompts
- Agents decide whether to handle or handoff questions based on their expertise
- Uses Semantic Kernel's native decision-making capabilities

### 🔧 **Function Calling Integration**  
- Services decorated with `@kernel_function` for seamless agent integration
- SearchAgent gains direct database access through function calling
- Film and rental services exposed as plugins to agents

### 🏗️ **Semantic Kernel Architecture**
- Uses `ChatCompletionAgent` instead of custom agent classes
- Native `HandoffOrchestration` with `OrchestrationHandoffs`
- Proper `InProcessRuntime` management for agent execution
- Agent response callbacks for monitoring and logging

### 📋 **Reference Implementation**
Following [Microsoft Semantic Kernel HandoffOrchestration documentation](https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-orchestration/handoff?utm_source=chatgpt.com&pivots=programming-language-python) for industry-standard patterns and best practices.
