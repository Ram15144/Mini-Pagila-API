# Pagila API

A Mini Pagila API with Gen AI capabilities built with FastAPI, SQLModel, and Semantic Kernel.
This repo was created with the help of cursor IDE.

## 🌟 Features

- **🎬 Film Management**: Complete CRUD operations with pagination, search, and filtering
- **📀 Rental Operations**: Full rental lifecycle with business logic validation
- **🤖 AI Integration**: OpenAI GPT-4o-mini powered chat and film recommendations
- **🔒 Authentication**: OAuth2PasswordBearer token authentication
- **📊 Database**: PostgreSQL with enhanced Pagila schema and migrations
- **🧪 Testing**: Comprehensive test suite with 92+ tests
- **📈 Logging**: Structured logging with correlation IDs and performance metrics
- **⚡ Real-time**: Server-Sent Events (SSE) for streaming AI responses

## 📚 Project Structure Details

```
pagila_api/
├── app/                            # FastAPI application
│   ├── api/v1/                     # API version 1 endpoints
│   │   ├── films.py                # Film CRUD operations  
│   │   ├── rentals.py              # Rental operations
│   │   └── ai.py                   # AI-powered endpoints
│   └── main.py                     # Application setup and middleware
├── core/                           # Core infrastructure
│   ├── auth.py                     # OAuth2PasswordBearer authentication
│   ├── config.py                   # Pydantic settings management
│   ├── database.py                 # AsyncSession and database lifecycle
│   ├── ai_kernel.py                # Semantic Kernel factory
│   ├── logging.py                  # Structured logging configuration
│   └── migrations/                 # Alembic database migrations
│       ├── versions/               # Migration version files
│       ├── env.py                  # Migration variables
│       ├── script.py.mako          # Used for generating new migrations
│       └── README.md               # Migration Info
├── domain/                         # Domain layer
│   ├── base.py                   # Metadata base
│   ├── models.py                   # SQLModel database models
│   └── schemas.py                  # Pydantic request/response schemas
├── services/                       # Business logic layer
│   ├── film_service.py             # Film business operations
│   ├── rental_service.py           # Rental business operations
│   └── ai_service.py               # AI business operations with agent orchestration
├── repositories/                   # Data access layer
│   ├── film_repository.py          # Film data access
│   └── rental_repository.py        # Rental data access
├── app/agents/                     # Agent orchestration system
│   ├── base_agent.py               # Base agent interface
│   ├── search_agent.py             # Film rental specialized agent
│   └── llm_agent.py                # General knowledge agent
├── tests/                          # Test suite
│   ├── test_films.py               # Film endpoint tests
│   ├── test_rentals.py             # Rental endpoint tests
│   ├── test_ai.py                  # AI endpoint tests
│   ├── test_agents.py              # Agent orchestration tests
│   ├── test_handoff_integration.py # Agent handoff integration tests
│   ├── test_auth.py                # Authentication tests
│   ├── test_protected_endpoint.py  # Protected Endpoint tests
│   ├── test_models.py              # Model validation tests
│   ├── test_logging.py             # Logging tests
│   ├── test_health.py              # Health Endpoint tests
│   └── conftest.py                 # Test configuration
├── docs/                           # Documentation
├── docker/                         # Docker configuration
├── Makefile                        # Development commands
├── pyproject.toml                  # Poetry dependencies and tool config
├── alembic.ini                     # Database migration configuration
└── README.md                       # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+ (via pyenv)
- Poetry 1.8+
- PostgreSQL 15+
- OpenAI API Key

### 1. Complete Setup (One Command)
```bash
make setup
```

### 2. Activate Conda Env
```bash
conda activate pagila_api
```

### 3. Activate Conda Env
Seed sample data
```bash
make setup-sample-data
```

### 4. Start Development Server
#### Option 1: Start application locally
```bash
make start-app
```
OR
#### Option 2: Start application using docker
```bash
make start-docker
```

### 5. Health Test API
```bash
curl http://localhost:8000/health
```

### 6. View Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### 🎬 Films API
- `GET /api/v1/films` - List films with pagination and category filtering
- `GET /api/v1/films/{id}` - Get specific film details
- `GET /api/v1/films/search/title?q=` - Search films by title
- `GET /api/v1/films/streaming/available` - Get streaming-available films

### 📀 Rentals API
- `GET /api/v1/customers/{id}/rentals` - Get customer rental history
- `GET /api/v1/rentals/{id}` - Get specific rental details
- `GET /api/v1/rentals/active` - Get active (unreturned) rentals

### 🔒 Protected Endpoints (Require `Bearer dvd_admin`)
- `POST /api/v1/customers/{id}/rentals` - Create new rental
- `PUT /api/v1/rentals/{id}/return` - Return rental

### 🤖 AI Endpoints
- `GET /api/v1/ai/ask?question=` - Stream AI responses using SSE
- `POST /api/v1/ai/summary` - Generate structured film summaries
- `POST /api/v1/ai/handoff` - **NEW**: Intelligent agent handoff for specialized question handling

### 🩺 System Endpoints
- `GET /health` - Health check
- `GET /protected` - Authentication test

## 🔐 Authentication

The API uses OAuth2PasswordBearer authentication:

- **Token**: `dvd_admin`
- **Header**: `Authorization: Bearer dvd_admin`

### Testing Authentication
```bash
# Valid token - returns user info
curl -H "Authorization: Bearer dvd_admin" http://localhost:8000/protected

# Invalid token - returns 401
curl -H "Authorization: Bearer invalid" http://localhost:8000/protected
```

## 🗄️ Database

### Enhanced Pagila Database
Based on the standard Pagila sample database with enhancements:

**Core Tables:**
- `film` - with `streaming_available` boolean field added
- `customer`, `rental`, `inventory`, `staff` - Standard Pagila tables
- `category`, `language`, `address`, `city`, `country` - Reference data

**New Tables:**
- `streaming_subscription` - Customer streaming subscriptions

### Sample Data
- **20 Films**: Mix of genres and ratings with streaming availability
- **15 Customers**: Active customers across 2 stores  
- **40 Inventory Items**: Films available for rental
- **15 Rentals**: Mix of active and returned rentals

### Enhanced Pagila Schema
Based on the PostgreSQL Pagila sample database with enhancements:

**Migrations Applied:**
1. **Migration #1**: Added base tables
1. **Migration #2**: Added `streaming_available BOOLEAN DEFAULT FALSE` to `film` table
2. **Migration #3**: Created `streaming_subscription` table for customer subscriptions

**Sample SQL Data:**
- Available in scripts folder

## 🛠️ Development Commands

### Basic Operations
```bash
make help             # Show all available commands
make setup            # Complete project setup
make dev              # Start development server
make test             # Run test suite
make clean            # Clean cache files
```

### Code Quality
```bash
make lint             # Run linting (ruff)
make format           # Format code (ruff format)
make type-check       # Run type checking (mypy)
make quality          # Run all code quality checks
```

### Database Operations
```bash
make db-setup         # Setup PostgreSQL with Pagila data
make db-reset         # Reset and reload database
make migrate          # Run database migrations
make migrate-create   # Create new migration
```

### Testing
Before testing make sure you have your OPENAI_API_KEY in .env.local file.
> **_NOTE:_** 
If conda env is activated and there are some import errors when running tests use python to run the tests: `python run pytest -v --tb=short`
```bash
make test             # Run all tests
make test-watch       # Run tests in watch mode
make test-coverage    # Run tests with coverage report
```
### Docker Operations
```bash
make docker-up        # Start services with Docker Compose
make docker-down      # Stop Docker services
make docker-logs      # View Docker logs
```

## 🧪 Testing

### Test Cases Overview
- Comprehensive coverage across 92+ tests covering all endpoints and systems.
- **Unit Tests**
  - **Service Layer**: Business logic validation
  - **Repository Layer**: Data access operations  
  - **Model Layer**: Domain model validation
  - **Agent System**: Individual agent factory testing with proper mocking
- **Integration Tests**
  - **API Endpoints**: End-to-end request/response testing
  - **Database Operations**: Real database integration
  - **AI Integration**: Live OpenAI API testing
  - **Agent Handoff**: Complete orchestration pipeline testing
- **Mock Testing**
  - **External Dependencies**: Mocked for fast, reliable tests
  - **Error Scenarios**: Validation, authentication, and business logic errors
  - **Edge Cases**: Boundary condition validation
  - **Dependency Injection**: FastAPI dependency override for proper test isolation
- **Performance**: Response time and load testing
- **Resource Management**: Runtime cleanup and error handling verification

### Running Tests
```bash
# All tests
make test

# Run specific test categories
poetry run pytest tests/test_films.py -v             # Film tests
poetry run pytest tests/test_rentals.py -v           # Rental tests  
poetry run pytest tests/test_ai.py -v                # AI tests
poetry run pytest tests/test_agents.py -v            # Agent orchestration tests
poetry run pytest tests/test_handoff_integration.py -v # Agent handoff tests
poetry run pytest tests/test_auth.py -v              # Auth tests

# With coverage
make test-coverage
```
> **_NOTE:_** 
If conda env is activated and there are some import errors when running tests use python to run the tests: `python run pytest -v --tb=short`

### Test Categories
- **✅ Happy Path**: Successful operations for all endpoints
- **✅ Validation**: Input validation and error handling
- **✅ Authentication**: Token validation and security
- **✅ Business Logic**: Rental rules and film recommendations
- **✅ AI Integration**: Real OpenAI API testing
- **✅ Agent Orchestration**: Complete handoff system testing with mocking
- **✅ Resource Management**: Runtime cleanup and lifecycle testing
- **✅ Error Handling**: Comprehensive error scenarios and fallback testing
- **✅ Performance**: Response time validation

## 🤖 AI Features

### Semantic Kernel Integration
Powered by Microsoft Semantic Kernel with OpenAI GPT-4o-mini:

- **Streaming Chat**: Real-time responses using Server-Sent Events
- **Film Recommendations**: Smart recommendations based on rating and price
- **Structured Responses**: JSON-formatted film summaries
- **Business Logic**: Recommends films with mature rating (R/NC-17) and rental_rate < $3.00
- **Agent Handoff**: Intelligent routing between specialized agents using native HandoffOrchestration

### Agent Handoff System
Two-agent system with intelligent question routing:

#### 🔍 SearchAgent
- **Specialization**: DVD rental store queries and film database operations
- **Capabilities**: 
  - Film searches by title with database integration
  - Rental rate and availability information
  - Customer rental history lookup
  - Streaming film recommendations
- **Function Calling**: Direct database access through @kernel_function decorated services
- **Decision Making**: Uses system prompts to determine if question requires database access
- **Factory Pattern**: `SearchAgentFactory.create_search_agent()` for consistent agent creation

#### 🧠 LLMAgent  
- **Specialization**: General knowledge and non-rental questions
- **Capabilities**:
  - Science, history, and current events
  - Math problems and calculations
  - Educational support and explanations
  - Creative tasks and brainstorming
- **Handoff Logic**: Receives questions from SearchAgent when outside rental domain
- **Factory Pattern**: `LLMAgentFactory.create_llm_agent()` for consistent agent creation

#### 🔄 HandoffOrchestration & Runtime Management
- **Framework**: Native Semantic Kernel HandoffOrchestration with OrchestrationHandoffs
- **Runtime**: InProcessRuntime for agent execution management with automatic cleanup
- **Decision Making**: Agent-based routing through intelligent system prompts (no manual confidence calculation)
- **Front-desk Pattern**: SearchAgent serves as initial handler, deciding whether to process or handoff
- **Resource Management**: Automatic runtime lifecycle with proper cleanup in finally blocks
- **Error Handling**: Comprehensive error handling with fallback responses and cleanup

#### 🏭 Agent Architecture
- **Base Agent**: Abstract base class for consistent agent interfaces
- **Service Integration**: Plugins provide database access through Semantic Kernel function calling
- **Session Management**: Proper database session handling for agent operations
- **Logging Integration**: Structured logging throughout the orchestration pipeline

#### 🧪 Comprehensive Testing
- **Unit Tests**: Individual agent factory and method testing with mocking
- **Integration Tests**: End-to-end handoff orchestration testing
- **Error Scenarios**: Comprehensive error handling and cleanup verification
- **Mocking Strategy**: FastAPI dependency override for reliable test isolation
- **Edge Cases**: Validation testing, timeout handling, and resource cleanup

### AI Endpoints

#### Streaming Chat
```bash
# Using curl with SSE
curl -H "Accept: text/event-stream" \
     "http://localhost:8000/api/v1/ai/ask?question=What%20movies%20do%20you%20recommend?"
```

#### Film Summary
```bash
curl -X POST http://localhost:8000/api/v1/ai/summary \
     -H "Content-Type: application/json" \
     -d '{"film_id": 1}'
```

#### Agent Handoff (NEW)
```bash
# Film-related question (handled by SearchAgent with database access)
curl -X POST http://localhost:8000/api/v1/ai/handoff \
     -H "Content-Type: application/json" \
     -d '{"question":"What is the rental rate for the film Alien?"}'

# General question (handled by LLMAgent)
curl -X POST http://localhost:8000/api/v1/ai/handoff \
     -H "Content-Type: application/json" \
     -d '{"question":"Who won the FIFA World Cup in 2022?"}'
```

## 📊 Logging & Observability

### Structured Logging
Built-in structured logging with:

- **Correlation IDs**: Track requests across all components
- **Performance Metrics**: Response times and operation durations
- **Component Tracking**: Service, repository, and API layer logging
- **AI Operations**: OpenAI request/response logging with token counts
- **Security Auditing**: Authentication attempt logging

### Log Output Example
```
2025-09-27 11:26:33 [info] Request started client_ip=127.0.0.1 correlation_id=b05c4925 method=GET path=/api/v1/ai/ask
2025-09-27 11:26:33 [info] AI service initialized model=gpt-4o-mini
2025-09-27 11:26:33 [info] AI ask_question started operation=ask_question question_length=5
2025-09-27 11:26:33 [info] AI ask_question completed chunk_count=14 response_length=53 token_count=10
2025-09-27 11:26:33 [info] Request completed correlation_id=b05c4925 duration_ms=2471.2 status_code=200
```

## 🏗️ Architecture

### Clean Architecture Pattern
- **API Layer** (`app/api/v1/`): FastAPI endpoints with validation
- **Service Layer** (`services/`): Business logic and validation  
- **Repository Layer** (`repositories/`): Data access with SQLModel
- **Domain Layer** (`domain/`): Models and schemas
- **Core Layer** (`core/`): Infrastructure (auth, database, AI, logging)

### Technology Stack
- **FastAPI**: Modern async web framework with dependency injection
- **SQLModel**: Type-safe ORM with async support
- **PostgreSQL**: Robust relational database
- **Semantic Kernel**: Microsoft's AI orchestration framework with HandoffOrchestration
- **OpenAI**: GPT-4o-mini for chat and summaries
- **Structlog**: Structured logging for observability
- **Poetry**: Dependency management
- **pytest**: Comprehensive testing framework with FastAPI test client
- **Mock/AsyncMock**: Advanced mocking for agent orchestration testing

## 🐳 Docker Support

### Quick Docker Start
```bash
make docker-up
```

### Manual Docker Commands
```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Configuration
- **PostgreSQL 15**: With health checks and volume persistence
- **API Service**: Auto-reload for development
- **Networking**: Proper service dependencies

## 📈 Performance

### Benchmarks (Local Only)
- **Film Listing**: ~50ms average response time
- **Film Search**: ~75ms with database queries
- **Rental Creation**: ~100ms with validation
- **AI Chat (SSE)**: ~2-5s depending on response length
- **AI Summary**: ~1-3s with OpenAI processing
- **Agent Handoff**: ~2-4s with intelligent routing and database integration

### Optimization Features
- **Database Indexing**: Optimized queries with proper joins
- **Connection Pooling**: Efficient database connection management
- **Async Operations**: Non-blocking I/O throughout
- **Streaming Responses**: Memory-efficient AI response streaming


## 🔄 Development Workflow

### 1. Make Changes
```bash
# Edit code
# Run tests
make test

# Check code quality
make quality
```

### 2. Test Endpoints
```bash
# Start server
make start-app

# Test in browser or Postman
# Use interactive docs at /docs
```

### 3. Database Changes
```bash
# Create migration
make migrate-create

# Apply migration
make migrate

# Update seed data and test with fresh data
make setup-sample-data
```

## 🎯 Key Capabilities

### 🎬 Film Management
- **Pagination**: Configurable page size (1-100 records)
- **Filtering**: Category-based filtering with case-insensitive search
- **Search**: Title-based search with partial matching
- **Streaming**: Filter films available for streaming

### 📀 Rental Operations
- **Validation**: Multi-layer business rule validation
- **Authentication**: Protected operations require authentication
- **History**: Complete rental history tracking
- **Returns**: Rental return processing with timestamps

### 🤖 AI Integration
- **Chat Assistance**: Natural language help for DVD rental queries
- **Film Recommendations**: Smart recommendations based on business rules
- **Streaming**: Real-time responses using Server-Sent Events
- **Structured Output**: JSON-formatted film analysis and recommendations

### 🔒 Security
- **OAuth2 Standard**: OAuth2PasswordBearer implementation
- **Token Validation**: Secure token verification
- **CORS Support**: Configurable cross-origin requests
- **Input Validation**: Comprehensive request validation

## 🎯 Example Usage

### List Films with Pagination
```bash
curl "http://localhost:8000/api/v1/films?skip=0&limit=10&category=Action"
```

### Search Films by Title
```bash
curl "http://localhost:8000/api/v1/films/search/title?q=ACADEMY"
```

### Create Rental (Protected)
```bash
curl -X POST http://localhost:8000/api/v1/customers/1/rentals \
  -H "Authorization: Bearer dvd_admin" \
  -H "Content-Type: application/json" \
  -d '{"inventory_id": 1, "staff_id": 1}'
```

### AI Chat with SSE (JavaScript)
```javascript
const eventSource = new EventSource('/api/v1/ai/ask?question=What movies do you recommend?');

eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('AI Response:', data.content);
};

eventSource.addEventListener('complete', function(event) {
    console.log('AI completed response');
    eventSource.close();
});
```

### AI Film Summary
```bash
curl -X POST http://localhost:8000/api/v1/ai/summary \
  -H "Content-Type: application/json" \
  -d '{"film_id": 1}'
```

## 📝 License

MIT License - This project is for educational and demonstration purposes.