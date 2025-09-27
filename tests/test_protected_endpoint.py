"""Test protected endpoint functionality."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_protected_endpoint_without_auth(client: AsyncClient):
    """Test that protected endpoint returns 401 without authentication."""
    response = await client.get("/protected")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_with_invalid_token(client: AsyncClient):
    """Test that protected endpoint returns 401 with invalid token."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = await client.get("/protected", headers=headers)
    assert response.status_code == 401
    data = response.json()
    assert "Invalid authentication token" in data["detail"]


@pytest.mark.asyncio
async def test_protected_endpoint_with_valid_token(client: AsyncClient):
    """Test that protected endpoint works with valid token."""
    headers = {"Authorization": "Bearer dvd_admin"}
    response = await client.get("/protected", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Access granted"
    assert data["user"] == "dvd_admin"
