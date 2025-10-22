"""
Pytest configuration and fixtures.

This file contains shared fixtures used across multiple test files.
Fixtures are reusable setup/teardown code that pytest automatically manages.
"""

import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from langchain_core.documents import Document

# Set test environment variables before importing the app
# Use a placeholder key for CI/CD environments without actual API keys
if not os.getenv("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "sk-test-key-for-testing"

# Import after setting env vars
from main import app, Config, initialize_app


@pytest.fixture
def client():
    """
    Create a TestClient for the FastAPI app.

    TestClient allows us to make HTTP requests to our API without actually
    running a server. It's much faster and doesn't require network calls.

    Usage in tests:
        def test_something(client):
            response = client.get("/")
            assert response.status_code == 200
    """
    return TestClient(app)


@pytest.fixture
def sample_documents():
    """
    Provide sample documents for testing.

    This fixture creates a small set of test documents so we don't need
    to load the entire knowledge base for every test.

    Returns:
        List of Document objects with AI/ML content
    """
    return [
        Document(
            page_content="""
            Artificial Intelligence (AI) is the simulation of human intelligence
            in machines. It includes machine learning, deep learning, and natural
            language processing. AI is used in healthcare, finance, and many other
            industries to automate tasks and enhance human capabilities.
            """
        ),
        Document(
            page_content="""
            Machine Learning is a subset of AI that enables computers to learn
            from data without being explicitly programmed. Common types include
            supervised learning, unsupervised learning, and reinforcement learning.
            Popular algorithms include linear regression, decision trees, and
            neural networks.
            """
        ),
        Document(
            page_content="""
            LangChain is a framework for building applications with Large Language
            Models. It provides tools for prompt management, chains, memory, agents,
            and vector stores. LangChain simplifies the development of LLM-powered
            applications like chatbots and question-answering systems.
            """
        ),
        Document(
            page_content="""
            Vector databases store high-dimensional vectors for semantic search.
            Popular options include FAISS, Pinecone, Chroma, and Weaviate.
            They enable efficient similarity search using embeddings.
            """
        ),
    ]


@pytest.fixture
def sample_query():
    """
    Provide a sample query for testing.

    Returns:
        dict: A valid query input
    """
    return {"question": "What is Artificial Intelligence?"}


@pytest.fixture
def invalid_queries():
    """
    Provide invalid query examples for testing validation.

    These should all fail validation and return appropriate error responses.

    Returns:
        List of invalid query dictionaries
    """
    return [
        {"question": ""},  # Empty string
        {"question": "   "},  # Only whitespace
        {"question": "x" * 1001},  # Too long (>1000 chars)
        {},  # Missing question field
    ]


@pytest.fixture
def temp_data_dir(tmp_path):
    """
    Create a temporary directory with sample text files for testing.

    tmp_path is a pytest built-in fixture that provides a temporary directory
    that's automatically cleaned up after the test.

    Args:
        tmp_path: pytest's temporary directory fixture

    Returns:
        Path: Path to temporary data directory with sample files
    """
    data_dir = tmp_path / "sample_data"
    data_dir.mkdir()

    # Create sample text files
    (data_dir / "doc1.txt").write_text(
        "Artificial Intelligence is transforming technology."
    )
    (data_dir / "doc2.txt").write_text(
        "Machine Learning is a subset of AI that learns from data."
    )
    (data_dir / "doc3.txt").write_text(
        "Deep Learning uses neural networks with multiple layers."
    )

    return data_dir


@pytest.fixture
def mock_openai_response():
    """
    Provide a mock OpenAI API response for testing.

    This is useful for tests that don't want to make real API calls.

    Returns:
        dict: Mock response in OpenAI's format
    """
    return {
        "id": "chatcmpl-test123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-4o-mini",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Artificial Intelligence (AI) is the simulation of human intelligence in machines that are programmed to think and learn like humans."
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 50,
            "completion_tokens": 30,
            "total_tokens": 80
        }
    }


# pytest configuration
def pytest_configure(config):
    """
    Configure pytest with custom markers.

    Markers allow us to categorize tests and run specific subsets.
    For example: pytest -m "not slow" will skip slow tests.
    """
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (require API keys)"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (fast, no external dependencies)"
    )
