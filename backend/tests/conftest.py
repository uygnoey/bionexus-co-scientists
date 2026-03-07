"""Pytest configuration and fixtures."""
import pytest
import asyncio
from typing import Generator


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_anthropic_api_key(monkeypatch):
    """Mock Anthropic API key."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_key_anthropic")


@pytest.fixture
def mock_openai_api_key(monkeypatch):
    """Mock OpenAI API key."""
    monkeypatch.setenv("OPENAI_API_KEY", "test_key_openai")


@pytest.fixture
def mock_all_api_keys(mock_anthropic_api_key, mock_openai_api_key):
    """Mock all required API keys."""
    pass
