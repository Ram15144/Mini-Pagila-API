# Pagila API Implementation Plan

## Project Overview
This document outlines a phased implementation approach for the Mini Pagila API project with Gen AI capabilities. The project includes database migrations, CRUD endpoints, Semantic Kernel AI integration, authentication, and comprehensive testing.

## Project Structure
```
pagila_api/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/                # API version 1
│   │       ├── __init__.py
│   │       ├── films.py       # Film endpoints
│   │       ├── rentals.py     # Rental endpoints
│   │       └── ai.py          # AI endpoints
│   └── main.py                # FastAPI app & lifespan
├── core/                      # Shared infrastructure
│   ├── __init__.py
│   ├── config.py              # Pydantic BaseSettings
│   ├── database.py            # AsyncSession setup
│   ├── auth.py                # OAuth2PasswordBearer token guard
│   ├── logging.py             # structlog configuration
│   ├── ai_kernel.py           # Semantic Kernel factory
│   └── migrations/            # Alembic migrations
│       ├── alembic.ini
│       ├── env.py
│       └── versions/
├── domain/
│   ├── __init__.py
│   ├── models.py              # SQLModel definitions
│   └── schemas.py             # Pydantic DTOs
├── services/
│   ├── __init__.py
│   ├── film_service.py        # Film business logic
│   ├── rental_service.py      # Rental business logic
│   └── ai_service.py          # AI business logic
├── repositories/
│   ├── __init__.py
│   ├── film_repository.py     # Film data access
│   └── rental_repository.py   # Rental data access
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Test configuration
│   ├── test_films.py          # Film endpoint tests
│   ├── test_rentals.py        # Rental endpoint tests
│   └── test_ai.py             # AI endpoint tests
├── docs/
│   ├── project_plan.md
│   └── implementation_plan.md
├── __init__.py
├── Makefile                   # Development commands
├── docker-compose.yml         # Docker services
├── pyproject.toml             # Poetry dependencies
├── .env.example               # Environment template
├── README.md
└── alembic.ini
```

## Phase-by-Phase Implementation

## Makefile Commands

The project includes a comprehensive Makefile to simplify common development tasks:

```makefile
# Makefile for Pagila API

.PHONY: help setup install clean dev test test-watch lint format type-check migrate db-setup db-reset docker-up docker-down

# Default target
help:
	@echo "Available commands:"
	@echo "  setup       - Complete project setup (install deps, setup db, run migrations)"
	@echo "  install     - Install dependencies with Poetry"
	@echo "  clean       - Clean up cache and temp files"
	@echo "  dev         - Start development server with auto-reload"
	@echo "  test        - Run all tests"
	@echo "  test-watch  - Run tests in watch mode"
	@echo "  lint        - Run linting (ruff)"
	@echo "  format      - Format code (ruff format)"
	@echo "  type-check  - Run type checking (mypy)"
	@echo "  migrate     - Run database migrations"
	@echo "  db-setup    - Setup PostgreSQL with Pagila data"
	@echo "  db-reset    - Reset database and re-run setup"
	@echo "  docker-up   - Start services with Docker Compose"
	@echo "  docker-down - Stop Docker services"

# Project setup
setup: install db-setup migrate
	@echo "✅ Project setup complete!"

install:
	@echo "📦 Installing dependencies..."
	poetry install

clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

# Development
dev:
	@echo "🚀 Starting development server..."
	poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testing
test:
	@echo "🧪 Running tests..."
	poetry run pytest -v --tb=short

test-watch:
	@echo "👀 Running tests in watch mode..."
	poetry run pytest-watch --runner "poetry run pytest -v --tb=short"

test-coverage:
	@echo "📊 Running tests with coverage..."
	poetry run pytest --cov=. --cov-report=html --cov-report=term

# Code quality
lint:
	@echo "🔍 Running linter..."
	poetry run ruff check .

format:
	@echo "✨ Formatting code..."
	poetry run ruff format .

type-check:
	@echo "🔎 Type checking..."
	poetry run mypy .

quality: format lint type-check
	@echo "✅ Code quality checks complete!"

# Database operations
migrate:
	@echo "📊 Running database migrations..."
	poetry run alembic upgrade head

migrate-create:
	@echo "📝 Creating new migration..."
	@read -p "Migration message: " msg; \
	poetry run alembic revision --autogenerate -m "$$msg"

db-setup:
	@echo "🗄️  Setting up PostgreSQL with Pagila data..."
	createdb pagila || echo "Database 'pagila' may already exist"
	psql pagila < scripts/pagila-schema.sql
	psql pagila < scripts/pagila-data.sql

db-reset:
	@echo "🔄 Resetting database..."
	dropdb pagila || echo "Database 'pagila' may not exist"
	$(MAKE) db-setup

# Docker operations
docker-up:
	@echo "🐳 Starting services with Docker..."
	docker-compose up -d

docker-down:
	@echo "🛑 Stopping Docker services..."
	docker-compose down

docker-logs:
	@echo "📜 Showing Docker logs..."
	docker-compose logs -f

# CI/CD helpers
ci-test: install lint type-check test
	@echo "✅ CI pipeline complete!"

# Pre-commit setup
pre-commit-install:
	@echo "🪝 Installing pre-commit hooks..."
	poetry run pre-commit install

pre-commit-run:
	@echo "🔄 Running pre-commit on all files..."
	poetry run pre-commit run --all-files
```

### Phase 0: Project Setup & Environment
**Objective**: Establish development environment and project structure

**Tasks**:
1. Initialize Poetry project with Python 3.12
2. Setup development dependencies and Makefile
3. Create project structure
4. Setup PostgreSQL with Pagila database
5. Initialize Alembic for migrations
6. Configure basic logging and environment variables

**Dependencies**:
```toml
[tool.poetry.dependencies]
python = "^3.12"
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
sqlmodel = "^0.0.14"
asyncpg = "^0.29.0"
alembic = "^1.12.0"
pydantic-settings = "^2.0.0"
structlog = "^23.2.0"
semantic-kernel = "^1.0.0"
openai = "^1.3.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
httpx = "^0.25.0"
mypy = "^1.6.0"
ruff = "^0.1.0"
pre-commit = "^3.5.0"
```

**Tests**:
- Verify project structure
- Test database connection
- Test environment variable loading

**Acceptance Criteria**:
- ✅ Poetry environment setup with all dependencies
- ✅ PostgreSQL running with Pagila data
- ✅ Alembic initialized and ready
- ✅ Basic tests pass

---

### Phase 1: Core Infrastructure & Database Migrations
**Objective**: Setup core infrastructure and implement required database migrations

**Tasks**:
1. **Database Models** (SQLModel)
   - Create Film model with existing Pagila fields
   - Create Customer model 
   - Create Rental model
   - Create Inventory model
   - Create Staff model
   - Create Category model

2. **Migration #1**: Add streaming_available to Film
   ```sql
   ALTER TABLE film ADD COLUMN streaming_available BOOLEAN DEFAULT FALSE;
   ```

3. **Migration #2**: Create streaming_subscription table
   ```sql
   CREATE TABLE streaming_subscription (
       id SERIAL PRIMARY KEY,
       customer_id INTEGER REFERENCES customer(customer_id),
       plan_name VARCHAR(100) NOT NULL,
       start_date DATE NOT NULL,
       end_date DATE
   );
   ```

4. **Core Infrastructure**
   - Database connection factory
   - AsyncSession dependency injection
   - Configuration management
   - Basic logging setup

**Tests**:
```python
# tests/test_migrations.py
async def test_migration_001_streaming_available():
    """Test streaming_available column was added to film table"""
    
async def test_migration_002_streaming_subscription_table():
    """Test streaming_subscription table was created with proper schema"""

# tests/test_database.py
async def test_database_connection():
    """Test database connection is working"""
    
async def test_session_dependency():
    """Test AsyncSession dependency injection"""
```

**Acceptance Criteria**:
- ✅ Both migrations run successfully
- ✅ SQLModel models defined for all entities
- ✅ Database connection and session management working
- ✅ Migration tests pass

---

### Phase 2: Authentication & Authorization
**Objective**: Implement token-based authentication system

**Tasks**:
1. **Auth Infrastructure**
   - OAuth2PasswordBearer token dependency
   - Token validation logic (hardcoded `dvd_admin`)
   - Auth decorators and dependencies

2. **Core Auth Module**
   ```python
   # core/auth.py
   from fastapi import HTTPException, status, Depends
   from fastapi.security import OAuth2PasswordBearer
   
   oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
   
   async def verify_token(token: str = Depends(oauth2_scheme)):
       if token != "dvd_admin":
           raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail="Invalid authentication token"
           )
       return token
   ```

**Tests**:
```python
# tests/test_auth.py
async def test_valid_token():
    """Test valid dvd_admin token is accepted"""
    
async def test_invalid_token():
    """Test invalid token is rejected with 401"""
    
async def test_missing_token():
    """Test missing token is rejected with 401"""
```

**Acceptance Criteria**:
- ✅ OAuth2PasswordBearer authentication working
- ✅ Token validation for `dvd_admin` implemented
- ✅ Proper 401 responses for invalid/missing tokens
- ✅ Authentication tests pass

---

### Phase 3: Films CRUD Endpoints
**Objective**: Implement films listing with pagination and filtering

**Tasks**:
1. **Film Repository**
   ```python
   # repositories/film_repository.py
   class FilmRepository:
       async def list_films(self, session: AsyncSession, skip: int, limit: int, category: str = None) -> List[Film]:
           """List films with pagination and optional category filter"""
           
       async def get_film_by_id(self, session: AsyncSession, film_id: int) -> Film | None:
           """Get film by ID"""
   ```

2. **Film Service**
   ```python
   # app/services/film_service.py
   class FilmService:
       def __init__(self, repository: FilmRepository):
           self.repository = repository
           
       async def list_films(self, session: AsyncSession, query: FilmQuery) -> FilmListResponse:
           """Business logic for listing films"""
   ```

3. **Film Endpoints**
   ```python
   # app/api/v1/films.py
   @router.get("/films", response_model=FilmListResponse)
   async def list_films(
       skip: int = Query(0, ge=0),
       limit: int = Query(10, ge=1, le=100),
       category: str = Query(None),
       session: AsyncSession = Depends(get_session),
       service: FilmService = Depends(get_film_service)
   ):
       """List films with pagination and optional category filter"""
   ```

4. **DTOs/Schemas**
   ```python
   # domain/schemas.py
   class FilmResponse(BaseModel):
       film_id: int
       title: str
       description: str
       rating: str
       rental_rate: Decimal
       streaming_available: bool
       
   class FilmListResponse(BaseModel):
       films: List[FilmResponse]
       total: int
       skip: int
       limit: int
   ```

**Tests**:
```python
# tests/test_films.py
async def test_list_films_default_pagination():
    """Test films listing with default pagination"""
    
async def test_list_films_with_category_filter():
    """Test films listing filtered by category"""
    
async def test_list_films_pagination():
    """Test films listing with custom pagination"""
    
async def test_list_films_empty_result():
    """Test films listing with no results"""
```

**Acceptance Criteria**:
- ✅ GET `/films` endpoint returns paginated results
- ✅ Category filtering works correctly
- ✅ Proper pagination metadata returned
- ✅ Repository and service layers implemented
- ✅ All film endpoint tests pass

---

### Phase 4: Rental Creation Endpoint
**Objective**: Implement protected rental creation endpoint

**Tasks**:
1. **Rental Repository**
   ```python
   # repositories/rental_repository.py
   class RentalRepository:
       async def create_rental(self, session: AsyncSession, rental_data: RentalCreate) -> Rental:
           """Create new rental record"""
           
       async def get_customer_rentals(self, session: AsyncSession, customer_id: int) -> List[Rental]:
           """Get all rentals for a customer"""
   ```

2. **Rental Service**
   ```python
   # services/rental_service.py
   class RentalService:
       async def create_rental(self, session: AsyncSession, customer_id: int, rental_data: RentalCreate) -> RentalResponse:
           """Business logic for creating rentals with validation"""
   ```

3. **Rental Endpoints**
   ```python
   # app/api/v1/rentals.py
   @router.post("/customers/{customer_id}/rentals", response_model=RentalResponse)
   async def create_rental(
       customer_id: int,
       rental_data: RentalCreate,
       session: AsyncSession = Depends(get_session),
       service: RentalService = Depends(get_rental_service),
       _: str = Depends(verify_token)  # Requires authentication
   ):
       """Create new rental - requires dvd_admin token"""
   ```

**Tests**:
```python
# tests/test_rentals.py
async def test_create_rental_authenticated():
    """Test rental creation with valid token"""
    
async def test_create_rental_unauthenticated():
    """Test rental creation without token returns 401"""
    
async def test_create_rental_invalid_customer():
    """Test rental creation with invalid customer ID"""
    
async def test_create_rental_invalid_inventory():
    """Test rental creation with invalid inventory ID"""
```

**Acceptance Criteria**:
- ✅ POST `/customers/{id}/rentals` endpoint implemented
- ✅ Authentication required (dvd_admin token)
- ✅ Proper validation for customer_id, inventory_id, staff_id
- ✅ Rental date automatically set to current timestamp
- ✅ All rental endpoint tests pass

---

### Phase 5: Semantic Kernel Setup & AI Ask Endpoint  
**Objective**: Setup Semantic Kernel and implement SSE streaming chat endpoint

**Tasks**:
1. **AI Kernel Factory**
   ```python
   # core/ai_kernel.py
   import semantic_kernel as sk
   from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
   
   def create_kernel() -> sk.Kernel:
       kernel = sk.Kernel()
       kernel.add_service(
           OpenAIChatCompletion(
               ai_model_id="gpt-4o-mini",
               api_key=settings.openai_api_key
           )
       )
       return kernel
   ```

2. **AI Service**
   ```python
   # services/ai_service.py
   class AIService:
       def __init__(self, kernel: sk.Kernel):
           self.kernel = kernel
           
       async def ask_question(self, question: str) -> AsyncIterator[str]:
           """Stream response to user question"""
   ```

3. **AI Ask Endpoint with SSE**
   ```python
   # app/api/v1/ai.py
   @router.get("/ai/ask")
   async def ask_question(
       question: str = Query(..., min_length=1),
       ai_service: AIService = Depends(get_ai_service)
   ):
       """Stream AI response using Server-Sent Events"""
       async def generate_sse_response():
           yield f"event: start\ndata: {json.dumps({'status': 'processing'})}\n\n"
           
           async for chunk in ai_service.ask_question(question):
               chunk_data = {"content": chunk}
               yield f"event: message\ndata: {json.dumps(chunk_data)}\n\n"
               
           yield f"event: complete\ndata: {json.dumps({'status': 'completed'})}\n\n"
           
       return StreamingResponse(
           generate_sse_response(),
           media_type="text/event-stream",
           headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
       )
   ```

**Tests**:
```python
# tests/test_ai.py
async def test_ai_ask_basic_question():
    """Test AI ask endpoint with SSE streaming"""
    response = await client.get("/api/v1/ai/ask?question=Hello")
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert "event: start" in response.text
    
async def test_ai_ask_streaming_response():
    """Test SSE headers and format"""
    assert "cache-control: no-cache" in response.headers
    assert "connection: keep-alive" in response.headers
```

**Acceptance Criteria**:
- ✅ Semantic Kernel properly configured with OpenAI
- ✅ GET `/ai/ask?question=` endpoint streams using SSE
- ✅ Proper SSE event format (start, message, complete, error)
- ✅ Real-time streaming with JavaScript EventSource support
- ✅ Proper error handling for empty/invalid questions
- ✅ AI ask endpoint tests pass

---

### Phase 6: AI Summary Endpoint with JSON Response
**Objective**: Implement structured JSON summary endpoint

**Tasks**:
1. **Enhanced AI Service**
   ```python
   # app/services/ai_service.py (extended)
   class AIService:
       async def summarize_film(self, film_id: int) -> FilmSummary:
           """Generate structured film summary with recommendation"""
           
       def _create_summary_prompt(self, film: Film) -> str:
           """Create prompt for film summary with JSON response format"""
   ```

2. **Film Summary Endpoint**
   ```python
   # app/api/v1/ai.py (extended)
   @router.post("/ai/summary", response_model=FilmSummary)
   async def summarize_film(
       request: FilmSummaryRequest,
       ai_service: AIService = Depends(get_ai_service)
   ):
       """Generate structured film summary and recommendation"""
   ```

3. **Summary DTOs**
   ```python
   # domain/schemas.py (extended)
   class FilmSummaryRequest(BaseModel):
       film_id: int
       
   class FilmSummary(BaseModel):
       title: str
       rating: str
       recommended: bool
   ```

4. **Prompt Management**
   ```python
   # core/prompts.py
   FILM_SUMMARY_PROMPT = """
   You are an API returning strictly JSON with keys: title, rating, recommended.
   Recommend true if rating > PG-13 and rental_rate < 3.00.
   
   Film data: {film_data}
   
   Return only valid JSON with no additional text.
   """
   ```

**Tests**:
```python
# tests/test_ai.py (extended)
async def test_ai_summary_valid_film():
    """Test AI summary with valid film ID"""
    
async def test_ai_summary_invalid_film():
    """Test AI summary with invalid film ID returns 404"""
    
async def test_ai_summary_json_structure():
    """Test AI summary returns proper JSON structure"""
    
async def test_ai_summary_recommendation_logic():
    """Test recommendation logic based on rating and rental_rate"""
```

**Acceptance Criteria**:
- ✅ POST `/ai/summary` endpoint returns structured JSON
- ✅ JSON contains required keys: title, rating, recommended
- ✅ Recommendation logic properly implemented
- ✅ Film lookup and error handling working
- ✅ AI summary endpoint tests pass

---

### Phase 7: Integration Testing & Documentation
**Objective**: Comprehensive testing and documentation

**Tasks**:
1. **Integration Tests**
   ```python
   # tests/test_integration.py
   async def test_complete_rental_flow():
       """Test complete flow: list films -> create rental"""
       
   async def test_complete_ai_flow():
       """Test complete flow: ask question -> get summary"""
   ```

2. **Performance Tests**
   ```python
   # tests/test_performance.py
   async def test_films_endpoint_performance():
       """Test films endpoint response time"""
       
   async def test_ai_streaming_performance():
       """Test AI streaming response time"""
   ```

3. **Documentation**
   - Complete README.md with setup instructions
   - API documentation with example curl commands
   - Environment variables documentation

4. **Code Quality**
   - Type hints validation with mypy
   - Code formatting with ruff
   - Pre-commit hooks setup

**Tests**:
```python
# tests/test_complete_suite.py
async def test_all_endpoints_health():
    """Test all endpoints are accessible and return expected status codes"""
    
async def test_database_migrations_complete():
    """Test all migrations have been applied"""
    
async def test_authentication_across_endpoints():
    """Test authentication requirements across all protected endpoints"""
```

**Acceptance Criteria**:
- ✅ All integration tests pass
- ✅ Performance benchmarks met
- ✅ Complete documentation provided
- ✅ Code quality checks pass
- ✅ Total test coverage > 90%

---

## Testing Strategy

### Test Configuration
```python
# tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.main import app
from core.database import get_session

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_session():
    """Create test database session"""
    engine = create_async_engine("postgresql+asyncpg://test:test@localhost/test_pagila")
    async with AsyncSession(engine) as session:
        yield session

@pytest.fixture
async def client(test_session):
    """Create test client with test database"""
    app.dependency_overrides[get_session] = lambda: test_session
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
```

### Test Categories
1. **Unit Tests**: Individual components (repositories, services)
2. **Integration Tests**: API endpoints with database
3. **End-to-End Tests**: Complete user workflows
4. **Performance Tests**: Response time and throughput
5. **Security Tests**: Authentication and authorization

### Continuous Testing
- Run tests after each phase completion
- Automated testing with pre-commit hooks
- Test coverage reporting
- Performance regression testing

## Environment Setup

### Development Environment
```bash
# Setup Python 3.12 with pyenv
pyenv install 3.12.0
pyenv local 3.12.0

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Clone and setup project (all-in-one command)
make setup

# Alternative: Step-by-step setup
make install          # Install dependencies
make db-setup         # Setup PostgreSQL with Pagila
make migrate          # Run migrations
make dev              # Start development server

# Common development commands
make test             # Run tests
make lint             # Check code quality
make format           # Format code
make type-check       # Run type checking
```

### Using Make Commands
The Makefile provides simplified commands for all common tasks:

- **`make setup`** - Complete project setup (one command setup)
- **`make dev`** - Start development server
- **`make test`** - Run test suite
- **`make quality`** - Run all code quality checks
- **`make db-reset`** - Reset and reload database
- **`make help`** - Show all available commands

### Docker Setup (Alternative)
For a containerized setup, the project includes a Docker Compose configuration:

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: pagila
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts:/scripts
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@postgres:5432/pagila
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - .:/app
    command: poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  postgres_data:
```

**Quick Docker Start:**
```bash
# Start all services
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down
```

### Environment Variables
```bash
# .env.example
DATABASE_URL=postgresql+asyncpg://user:password@localhost/pagila
OPENAI_API_KEY=your-openai-api-key
LOG_LEVEL=INFO
API_SECRET_KEY=your-secret-key
```

## Success Metrics

### Technical Metrics
- ✅ All 4 main endpoints implemented and tested
- ✅ 2 database migrations applied successfully  
- ✅ Authentication working with Bearer token
- ✅ AI streaming and JSON responses working
- ✅ Test coverage > 90%
- ✅ Response times < 500ms for CRUD, < 2s for AI

### Quality Metrics
- ✅ Type hints coverage > 95%
- ✅ Zero linting errors
- ✅ All security requirements met
- ✅ Complete documentation provided
- ✅ Clear separation of concerns maintained

This implementation plan provides a systematic approach to building the Pagila API with comprehensive testing at each phase, ensuring a robust and maintainable codebase.
