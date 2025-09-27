FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml poetry.lock ./
COPY app/ ./app/
COPY core/ ./core/
COPY domain/ ./domain/
COPY repositories/ ./repositories/
COPY services/ ./services/
COPY scripts/ ./scripts/
COPY alembic.ini ./
# Install dependencies (including dev dependencies for migrations)
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Add deployment timeout to prevent premature timeouts
ENV DEPLOY_TIMEOUT=300s

# API Health Check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 