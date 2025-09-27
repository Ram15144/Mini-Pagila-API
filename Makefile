# Makefile for Pagila API

.PHONY: help setup setup-sample-data test test-watch test-coverage lint format type-check quality migrate migrate-create db-create db-schema db-create-data db-setup db-remove db-data-reset docker-up docker-down docker-logs stop start-app start-docker check-python check-conda check-poetry setup-poetry verify-conda-setup setup-conda-env cleanup

CURDIR_ESCAPED := $(CURDIR)
RM_CMD := rm -rf
MKDIR_CMD := mkdir -p
PATH_SEP := /
CONDA_ACTIVATE := source $$(conda info --base)/etc/profile.d/conda.sh && conda activate
CONDA_DEACTIVATE := conda deactivate
PKILL_CMD := pkill -f
NULL_DEVICE := /dev/null
SHELL_EXPORT := export
ENV_FILE := .env.local
PYTHON_CMD := python3.12

# Variables
POETRY := poetry
DOCKER_COMPOSE := docker compose
DC_FILE := docker$(PATH_SEP)docker-compose.yml
CONDA_ENV_NAME := pagila_api

# Detect Conda paths dynamically
export PATH := /opt/anaconda3/bin:$(PATH)
CONDA_ROOT := $(shell conda info --base)
CONDA_ENV_PATH := $(shell conda info --base)/envs/$(CONDA_ENV_NAME)
CONDA_BIN_PATH := $(CONDA_ENV_PATH)/bin
PYTHON_PATH := $(CONDA_BIN_PATH)/python
POETRY_PATH := $(CONDA_BIN_PATH)/poetry

# Database configuration
DB_NAME := pagila
DB_USER := postgres
DB_PASSWORD := postgres

# Service ports
PAGILA_API_PORT := 8000

RED := \033[0;31m
GREEN := \033[0;32m
BLUE := \033[0;34m
NC := \033[0m

# Default target
help:
	@echo "Project setup and cleanup commands:"
	@echo "  setup       	   	- Complete project setup (install deps, setup db, run migrations)"
	@echo "  setup-sample-data 	- Setup sample data (remove db, create db, run migrations, create sample data)"
	@echo "  start-app         	- Start Pagila API Service using Uvicorn"
	@echo "  start-docker      	- Start Pagila API Service using Docker Compose"
	@echo "  stop          	- Stop all services and Docker containers"
	@echo "  cleanup           	- Clean up everything including conda env. Does not clean migration files and .env files\n"

	@echo "Code quality commands:"
	@echo "  test        		- Run all tests"
	@echo "  test-watch  		- Run tests in watch mode"
	@echo "  test-coverage   	- Run tests with coverage"
	@echo "  lint        		- Run linting (ruff)"
	@echo "  format      		- Format code (ruff format)"
	@echo "  type-check  		- Run type checking (mypy)"
	@echo "  quality         	- Run all code quality checks\n"

	@echo "Database commands:"
	@echo "  migrate     		- Run database migrations"
	@echo "  migrate-create  	- Create new migration"
	@echo "  db-create       	- Create database"
	@echo "  db-schema       	- Create database schema"
	@echo "  db-create-data  	- Create database data"
	@echo "  db-setup    		- Setup PostgreSQL with Pagila data"
	@echo "  db-remove       	- Remove database"
	@echo "  db-data-reset   	- Reset database and re-run setup\n"

	@echo "Docker commands:"
	@echo "  docker-up   		- Start services with Docker Compose"
	@echo "  docker-down 		- Stop Docker services"
	@echo "  docker-logs 		- View Docker logs\n"

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

db-create:
	@echo "🗄️  Creating database..."
	createdb pagila || echo "Database 'pagila' may already exist"

db-schema:
	@echo "🗄️  Creating database schema..."
	psql pagila < scripts/pagila-schema.sql || echo "Schema may already exist"

db-create-data:
	@echo "🗄️  Entering data into database..."
	psql pagila < scripts/pagila-data.sql || echo "Data may already exist"

db-setup:
	@echo "🗄️  Setting up PostgreSQL with Pagila data..."
	$(MAKE) db-create
	$(MAKE) db-schema
	$(MAKE) db-create-data

db-remove:
	@echo "🔄 Cleaning database..."
	dropdb pagila || echo "Database 'pagila' may not exist"

db-data-reset:
	@echo "🔄 Resetting database..."
	$(MAKE) db-remove
	$(MAKE) db-setup

# Docker operations
docker-up:
	@echo "🐳 Starting services with Docker..."
	$(DOCKER_COMPOSE) -f $(DC_FILE) up -d

docker-down:
	@echo "🛑 Stopping Docker services..."
	$(DOCKER_COMPOSE) -f $(DC_FILE) down

docker-logs:
	@echo "📜 Showing Docker logs..."
	$(DOCKER_COMPOSE) -f $(DC_FILE) logs -f

stop: ## Stop all services and Docker containers
	@echo "🛑 Stopping all services..."
	@echo "Stopping uvicorn processes..."
	@pkill -f "uvicorn" 2>/dev/null || true
	@echo "Stopping Python processes using our ports..."
	@make docker-down
	@for port in $(PAGILA_API_PORT); do \
		lsof -t -i :$$port 2>/dev/null | xargs kill -9 2>/dev/null || true; \
	done

	@echo "$(GREEN)✓ Service stopped$(NC)"
	@echo "Verifying if port $(PAGILA_API_PORT) is free..."

	@if lsof -i :$(PAGILA_API_PORT) >/dev/null 2>&1; then \
		echo "$(RED)Warning: Port $(PAGILA_API_PORT) is still in use$(NC)"; \
	else \
		echo "$(GREEN)✓ Port $(PAGILA_API_PORT) is free$(NC)"; \
	fi

start-app: ## Start Pagila API service locally using Uvicorn
	@echo "🚀 Starting Pagila API Service using Uvicorn..."
	@if [ ! -f "$(ENV_FILE)" ]; then \
		echo "$(RED)❌ $(ENV_FILE) not found. Please create it from .env.example$(NC)" && \
		exit 1; \
	fi
	
	@echo "Checking ports availability..."
	@if lsof -i :$(PAGILA_API_PORT) >/dev/null 2>&1; then \
		echo "$(RED)❌ Some ports are already in use. Running stop-all first...$(NC)" && \
		make stop-all && sleep 2; \
	else \
		echo "Ports are available"; \
	fi

	@echo "Starting service..."
	@echo "🚀 Starting Pagila API Service on port $(PAGILA_API_PORT)..."
	@echo "\n$(GREEN)Service is running at:$(NC)"
	@echo "$(BLUE)Pagila API:$(NC)        http://localhost:$(PAGILA_API_PORT)"
	@echo "\n$(GREEN)Documentation URLs:$(NC)"
	@echo "$(BLUE)Pagila API:$(NC)        http://localhost:$(PAGILA_API_PORT)/docs"
	@echo "\n$(GREEN)Health Check URL:$(NC)"
	@echo "$(BLUE)Pagila API:$(NC)        http://localhost:$(PAGILA_API_PORT)/health \n"
	@export PYTHONPATH="$(CURDIR)" && \
	$(POETRY) run uvicorn app.main:app --reload --port $(PAGILA_API_PORT)

start-docker: ## Start service using Docker Compose
	@echo "🚀 Starting Pagila API Service using Docker Compose..."
	@if [ ! -f "$(ENV_FILE)" ]; then \
		echo "$(RED)❌ $(ENV_FILE) not found. Please create it from .env.example$(NC)" && \
		exit 1; \
	fi
	
	@echo "Checking ports availability..."
	@if lsof -i :$(PAGILA_API_PORT) >/dev/null 2>&1; then \
		echo "$(RED)❌ Some ports are already in use. Running stop-all first...$(NC)" && \
		make stop-all && sleep 2; \
	else \
		echo "Ports are available"; \
	fi
	@echo "Starting services..."
	@make docker-up

	@echo "\n$(GREEN)Service is running at:$(NC)"
	@echo "$(BLUE)Pagila API:$(NC)        http://localhost:$(PAGILA_API_PORT)"
	@echo "\n$(GREEN)Documentation URLs:$(NC)"
	@echo "$(BLUE)Pagila API:$(NC)        http://localhost:$(PAGILA_API_PORT)/docs"
	@echo "\n$(GREEN)Health Check URL:$(NC)"
	@echo "$(BLUE)Pagila API:$(NC)        http://localhost:$(PAGILA_API_PORT)/health"

check-python: ## Check Python version
	@echo "🐍 Checking Python version..."
	@$(PYTHON_CMD) -c "import sys; \
		version = sys.version_info; \
		exit(0 if version.major == 3 and version.minor == 12 else 1)" || \
		(echo "$(RED)❌ Python 3.12 is required but not found$(NC)" && exit 1)
	@echo "$(GREEN)✓ Python 3.12 found$(NC)"

check-conda: ## Check if Conda is installed
	@echo "🐍 Checking Conda installation..."
	@which conda >/dev/null 2>&1 || ( \
		echo "$(RED)❌ Conda is not installed. Please install Miniconda or Anaconda.$(NC)" && \
		exit 1 \
	)
	@echo "$(GREEN)✓ Conda is installed$(NC)"

check-poetry: ## Check if Poetry is installed in Conda environment
	@echo "📦 Checking Poetry installation..."
	@bash -c '$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && \
	if ! command -v poetry >/dev/null 2>&1; then \
		echo "$(RED)❌ Poetry not found. Installing...$(NC)" && \
		python -m pip install poetry; \
	fi && \
	poetry --version'
	@echo "$(GREEN)✓ Poetry is installed$(NC)"

setup-poetry: check-poetry ## Setup Poetry in Conda environment
	@echo "📦 Setting up Poetry dependencies..."

	@bash -c '$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && \
		poetry config virtualenvs.create false && \
		poetry install --no-root && \
		poetry run pre-commit install'
	@echo "$(GREEN)✓ Poetry dependencies installed$(NC)"

verify-conda-setup: ## Verify Conda setup and paths
	@echo "🔍 Verifying Conda setup..."
	@echo "Conda Root: $(CONDA_ROOT)"
	@echo "Conda Environment Path: $(CONDA_ENV_PATH)"
	@if [ ! -d "$(CONDA_ROOT)" ]; then \
		echo "$(RED)❌ Conda installation not found at $(CONDA_ROOT)$(NC)"; \
		echo "Please ensure Conda is installed and 'conda info --base' returns the correct path"; \
		exit 1; \
	fi
	@if [ -d "$(CONDA_ENV_PATH)" ]; then \
		echo "$(GREEN)✓ Conda environment exists at: $(CONDA_ENV_PATH)$(NC)"; \
	else \
		echo "$(BLUE)ℹ️ Conda environment will be created at: $(CONDA_ENV_PATH)$(NC)"; \
	fi
	@echo "$(GREEN)✓ Conda setup verified$(NC)"

setup-conda-env: verify-conda-setup ## Create and setup Conda environment
	@echo "🐍 Setting up Conda environment..."
	@if ! conda env list | grep -q $(CONDA_ENV_NAME); then \
		echo "Creating new Conda environment: $(CONDA_ENV_NAME)..." && \
		conda create -y -n $(CONDA_ENV_NAME) python=3.12 pip && \
		bash -c '$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && \
		python -m pip install --upgrade pip setuptools wheel poetry'; \
	else \
		echo "Conda environment $(CONDA_ENV_NAME) already exists"; \
		bash -c '$(CONDA_ACTIVATE) $(CONDA_ENV_NAME) && \
		python -m pip install --upgrade pip setuptools wheel poetry'; \
	fi
	@echo "Configuring environment paths for Mac..."
	@ACTUAL_ENV_PATH=$$(conda env list | grep $(CONDA_ENV_NAME) | awk '{print $$2}') && \
	if [ ! -z "$$ACTUAL_ENV_PATH" ]; then \
		echo "Environment found at: $$ACTUAL_ENV_PATH"; \
		if [ ! -d "$(dir $(CONDA_ENV_PATH))" ]; then \
			mkdir -p "$(dir $(CONDA_ENV_PATH))"; \
		fi; \
		if [ ! -e "$(CONDA_ENV_PATH)" ]; then \
			ln -sf "$$ACTUAL_ENV_PATH" "$(CONDA_ENV_PATH)"; \
			echo "Created symlink: $(CONDA_ENV_PATH) -> $$ACTUAL_ENV_PATH"; \
		fi \
	fi

	@echo "$(GREEN)✓ Conda environment ready$(NC)"

setup: check-python ## Complete development environment setup
	@echo "🔧 Setting up development environment..."
	@if [ ! -f "$(ENV_FILE)" ]; then \
		echo "$(RED)❌ $(ENV_FILE) not found. Please create it from .env.example$(NC)" && \
		exit 1; \
	fi
	@make setup-conda-env || ( \
		echo "$(RED)❌ Conda environment setup failed$(NC)" && \
		exit 1 \
	)
	@make setup-poetry || ( \
		echo "$(RED)❌ Poetry setup failed$(NC)" && \
		exit 1 \
	)

	@echo "$(GREEN)✨ Development environment setup complete!$(NC)"
	@echo "$(BLUE)Environment Information:$(NC)"
	@echo "  Environment File: $(ENV_FILE)"
	@echo "  Conda Root: $(CONDA_ROOT)"
	@echo "  Conda Environment: $(CONDA_ENV_PATH)"
	@echo "  Conda Bin Path: $(CONDA_BIN_PATH)"
	@echo "  Python Path: $(PYTHON_PATH)"
	@echo "  Poetry Path: $(POETRY_PATH)"
	@echo "$(BLUE)To activate the environment:$(NC)"
	@echo "  conda activate $(CONDA_ENV_NAME)"
	@echo "$(BLUE)To start pagila api service locally:$(NC)"
	@echo "  make start-app"
	@echo "$(BLUE)Use Docker to host pagila api service:$(NC)"
	@echo "  make start-docker"

setup-sample-data: # 1.Removes database if present and recreates it 2. Runs migrations 3. Creates sample data
	@echo "🗄️  Setting up sample data..."
	@make db-remove
	@make db-create
	@make migrate
	@make db-create-data
	
cleanup: stop-all ## Clean everything except migration files and .env files
	@echo "🧹 Cleaning up project..."

	@echo "$(BLUE)Stopping service...$(NC)"
	@make stop-all 2>/dev/null || true
	@echo "$(BLUE)Cleaning Conda environment...$(NC)"
	@conda env remove -n $(CONDA_ENV_NAME) --yes 2>/dev/null || true
	@[ -L "$(CONDA_ENV_PATH)" ] && rm -f "$(CONDA_ENV_PATH)" 2>/dev/null || true
	@echo "$(BLUE)Removing cache directories...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(BLUE)Removing temporary files...$(NC)"
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.pyd" -delete 2>/dev/null || true
	@find . -type f -name "*.log" -delete 2>/dev/null || true
	@echo "$(BLUE)Cleaning Poetry files...$(NC)"
	@rm -f poetry.lock 2>/dev/null || true
	@echo "$(BLUE)Cleaning build artifacts...$(NC)"
	@rm -rf dist/ build/ *.egg-info 2>/dev/null || true

	@echo "$(GREEN)✨ Cleanup complete! Migration files and .env files preserved.$(NC)"
	@echo "$(BLUE)Preserved files:$(NC)"
	@echo "  - Migration files in core/migrations/"
	@echo "  - Environment files (.env.*)"
	@echo "  - Git files (.git/)"
	@echo "  - VS Code settings (.vscode/)"
	@echo "$(BLUE)To recreate the environment, run:$(NC)"
	@echo "  make setup"