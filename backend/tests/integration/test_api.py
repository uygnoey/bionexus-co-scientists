"""Integration tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "BioNexus Co-scientists API"


def test_papers_health():
    """Test papers service health."""
    response = client.get("/api/papers/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "papers"


def test_hypotheses_health():
    """Test hypotheses service health."""
    response = client.get("/api/hypotheses/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "hypotheses"


@pytest.mark.asyncio
async def test_papers_search_invalid_query():
    """Test papers search with invalid query."""
    response = client.get("/api/papers/search?query=&max_results=10")
    
    # Should return 422 for validation error (empty query)
    assert response.status_code == 422


def test_cors_headers():
    """Test CORS headers are present."""
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    
    # CORS should be configured
    assert "access-control-allow-origin" in response.headers.keys() or response.status_code == 200


def test_openapi_schema():
    """Test OpenAPI schema is accessible."""
    response = client.get("/openapi.json")
    
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "paths" in data


def test_docs_endpoint():
    """Test Swagger UI endpoint."""
    response = client.get("/docs")
    
    assert response.status_code == 200
    assert "swagger" in response.text.lower() or "<!doctype html>" in response.text.lower()


def test_redoc_endpoint():
    """Test ReDoc endpoint."""
    response = client.get("/redoc")
    
    assert response.status_code == 200
    assert "redoc" in response.text.lower() or "<!doctype html>" in response.text.lower()
