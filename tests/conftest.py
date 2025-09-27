"""Test configuration and fixtures."""

import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import NullPool

from core.config import settings


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_engine():
    """Create test database engine."""
    # Use a test database URL or in-memory SQLite for tests
    test_database_url = settings.DATABASE_URL.replace("/pagila", "/test_pagila")
    
    engine = create_async_engine(
        test_database_url,
        poolclass=NullPool,
        echo=False
    )
    yield engine
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """Create test database session."""
    async with AsyncSession(test_engine) as session:
        yield session


@pytest.fixture
async def client():
    """Create test client."""
    # Import here to avoid circular imports when app is not yet created
    from app.main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
