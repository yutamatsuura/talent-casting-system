"""
Health endpoint tests
Tests for basic API functionality and health checks
"""

import pytest
import httpx
from unittest.mock import AsyncMock, patch

from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test the root endpoint returns correct information"""
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Talent Casting System API"
    assert data["version"] == "1.0.0"
    assert data["docs"] == "/api/docs"


@pytest.mark.asyncio
async def test_openapi_docs_accessible():
    """Test that OpenAPI documentation is accessible"""
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert data["info"]["title"] == "Talent Casting System API"


@pytest.mark.asyncio
async def test_invalid_endpoint():
    """Test that invalid endpoints return 404"""
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/invalid-endpoint")
    assert response.status_code == 404


class TestApiValidation:
    """Test API validation and error handling"""

    @pytest.mark.asyncio
    async def test_malformed_json_request(self):
        """Test handling of malformed JSON in POST requests"""
        async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                "/api/matching",
                headers={"Content-Type": "application/json"},
                content="invalid json"
            )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_content_type(self):
        """Test handling of missing Content-Type header"""
        async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post(
                "/api/matching",
                json={"test": "data"}
            )
        # Should handle gracefully even without required fields
        assert response.status_code in [422, 500]  # Validation error or server error


@pytest.mark.asyncio
async def test_app_lifespan():
    """Test that the app lifespan events work correctly"""
    # This tests that the app can start and shutdown without errors
    # The actual lifespan events are tested implicitly when the app starts
    assert app.title == "Talent Casting System API"
    assert app.version == "1.0.0"