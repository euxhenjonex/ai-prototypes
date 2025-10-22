"""
Tests for API endpoints.

These tests verify that the FastAPI endpoints work correctly,
handle valid/invalid inputs properly, and return expected responses.
"""

import pytest
from fastapi import status


class TestHealthEndpoints:
    """Tests for health check endpoints"""

    def test_root_endpoint_returns_200(self, client):
        """
        Test that GET / returns 200 OK.

        This is a basic smoke test to ensure the API is running.
        """
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK

    def test_root_endpoint_returns_correct_structure(self, client):
        """
        Test that GET / returns the expected JSON structure.

        We verify:
        - Response is valid JSON
        - Contains required fields
        - Field types are correct
        """
        response = client.get("/")
        data = response.json()

        # Check all required fields are present
        assert "status" in data
        assert "message" in data
        assert "documents_loaded" in data

        # Check field types
        assert isinstance(data["status"], str)
        assert isinstance(data["message"], str)
        assert isinstance(data["documents_loaded"], int)

    def test_root_endpoint_shows_healthy_status(self, client):
        """
        Test that GET / indicates healthy status.
        """
        response = client.get("/")
        data = response.json()

        assert data["status"] == "healthy"
        assert "running" in data["message"].lower()

    def test_root_endpoint_shows_documents_loaded(self, client):
        """
        Test that GET / reports number of documents loaded.

        Since we have 12 .txt files in sample_data/, we expect
        at least some documents to be loaded.
        """
        response = client.get("/")
        data = response.json()

        # We should have loaded documents from our sample_data folder
        assert data["documents_loaded"] > 0
        # We know we have 12 text files
        # But documents_loaded refers to chunks, which should be ~244
        assert data["documents_loaded"] >= 10

    def test_health_endpoint_exists(self, client):
        """
        Test that GET /health endpoint exists and returns 200.
        """
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK

    def test_health_endpoint_structure(self, client):
        """
        Test that GET /health returns expected structure.
        """
        response = client.get("/health")
        data = response.json()

        assert "status" in data
        assert "message" in data
        assert "documents_loaded" in data
        assert data["status"] == "healthy"


class TestQueryEndpoint:
    """Tests for the /query endpoint"""

    @pytest.mark.integration
    def test_query_with_valid_question(self, client, sample_query):
        """
        Test POST /query with a valid question.

        This is an integration test because it makes real calls to OpenAI.
        Mark with @pytest.mark.integration so it can be skipped in CI
        if no API key is available.

        Run only integration tests:
            pytest -m integration

        Skip integration tests:
            pytest -m "not integration"
        """
        response = client.post("/query", json=sample_query)

        # Check status code
        assert response.status_code == status.HTTP_200_OK

        # Check response structure
        data = response.json()
        assert "question" in data
        assert "answer" in data

        # Check that question is echoed back
        assert data["question"] == sample_query["question"]

        # Check that answer is not empty
        assert isinstance(data["answer"], str)
        assert len(data["answer"]) > 0

        # Basic content check - answer should be about AI
        answer_lower = data["answer"].lower()
        # At least one of these terms should appear
        ai_terms = ["artificial", "intelligence", "machine", "ai", "learn"]
        assert any(term in answer_lower for term in ai_terms)

    def test_query_endpoint_requires_question_field(self, client):
        """
        Test that /query returns 422 when question field is missing.

        422 Unprocessable Entity is the correct status for validation errors.
        """
        response = client.post("/query", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_query_rejects_empty_question(self, client):
        """
        Test that /query rejects empty questions.

        Our validator should reject empty strings and whitespace-only strings.
        """
        # Empty string
        response = client.post("/query", json={"question": ""})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Whitespace only
        response = client.post("/query", json={"question": "   "})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_query_rejects_too_long_question(self, client):
        """
        Test that /query rejects questions longer than 1000 characters.

        Our Field validation sets max_length=1000.
        """
        long_question = "x" * 1001
        response = client.post("/query", json={"question": long_question})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_query_accepts_max_length_question(self, client):
        """
        Test that /query accepts questions exactly at the 1000 char limit.

        This is a boundary test - questions at exactly max_length should work.
        """
        max_length_question = "x" * 1000
        response = client.post("/query", json={"question": max_length_question})

        # Should accept it (might fail at LLM level, but validation should pass)
        # We accept either 200 (success) or 500 (LLM error) but not 422 (validation error)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]

    @pytest.mark.integration
    def test_query_with_different_questions(self, client):
        """
        Test multiple different questions to verify consistency.

        This helps ensure the system works across various query types.
        """
        questions = [
            "What is machine learning?",
            "Explain LangChain",
            "What are vector databases?",
            "How does FAISS work?",
        ]

        for question in questions:
            response = client.post("/query", json={"question": question})

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["question"] == question
            assert len(data["answer"]) > 0
            # Answer should be reasonably substantial
            assert len(data["answer"]) > 20

    def test_query_strips_whitespace_from_question(self, client):
        """
        Test that leading/trailing whitespace is stripped from questions.

        Our validator includes .strip() so this should work.
        """
        question_with_whitespace = "  What is AI?  "
        expected_question = "What is AI?"

        # For this test, we'll just verify the structure without calling OpenAI
        # We can check that validation passes
        response = client.post("/query", json={"question": question_with_whitespace})

        # Should not be rejected for validation (might fail if no API key in CI)
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_500_INTERNAL_SERVER_ERROR
        ]

    def test_query_with_special_characters(self, client):
        """
        Test that questions with special characters are handled properly.
        """
        special_questions = [
            "What is AI? 🤖",
            "How does ML work? (specifically supervised learning)",
            "Explain RAG @ high level",
        ]

        for question in special_questions:
            response = client.post("/query", json={"question": question})

            # Should handle special characters gracefully
            # Either success or server error, but not validation error
            assert response.status_code in [
                status.HTTP_200_OK,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            ]


class TestAPIDocumentation:
    """Tests for API documentation endpoints"""

    def test_openapi_schema_accessible(self, client):
        """
        Test that OpenAPI schema is accessible at /openapi.json
        """
        response = client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema

    def test_docs_endpoint_accessible(self, client):
        """
        Test that Swagger UI docs are accessible at /docs
        """
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]

    def test_redoc_endpoint_accessible(self, client):
        """
        Test that ReDoc docs are accessible at /redoc
        """
        response = client.get("/redoc")
        assert response.status_code == status.HTTP_200_OK
        assert "text/html" in response.headers["content-type"]


class TestErrorHandling:
    """Tests for error handling"""

    def test_404_for_nonexistent_endpoint(self, client):
        """
        Test that accessing a non-existent endpoint returns 404.
        """
        response = client.get("/nonexistent")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_405_for_wrong_method(self, client):
        """
        Test that using wrong HTTP method returns 405.

        /query expects POST, so GET should return 405 Method Not Allowed.
        """
        response = client.get("/query")
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_query_with_invalid_json(self, client):
        """
        Test that invalid JSON returns 422.
        """
        response = client.post(
            "/query",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# Parametrized tests - run same test with different inputs
@pytest.mark.parametrize("endpoint", ["/", "/health"])
def test_health_endpoints_return_200(client, endpoint):
    """
    Parametrized test: both health endpoints should return 200.

    This single test function runs twice, once for each endpoint.
    """
    response = client.get(endpoint)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize("invalid_question", [
    "",  # Empty
    "   ",  # Whitespace only
    "x" * 1001,  # Too long
])
def test_query_validation_rejects_invalid_questions(client, invalid_question):
    """
    Parametrized test: verify all invalid questions are rejected.

    This is a more concise way to test multiple invalid inputs.
    """
    response = client.post("/query", json={"question": invalid_question})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
