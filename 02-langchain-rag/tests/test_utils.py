"""
Tests for utility functions.

These are unit tests that test individual functions in isolation,
without requiring the full application or external API calls.
"""

import pytest
from pathlib import Path
from langchain_core.documents import Document

# Import functions to test
from main import (
    get_api_key,
    load_documents,
    create_vectorstore,
    format_docs,
    Config
)


class TestGetApiKey:
    """Tests for get_api_key function"""

    def test_get_api_key_returns_string(self):
        """
        Test that get_api_key returns a string.

        This assumes OPENAI_API_KEY is set in environment.
        """
        api_key = get_api_key()
        assert isinstance(api_key, str)
        assert len(api_key) > 0

    def test_get_api_key_raises_on_missing_key(self, monkeypatch):
        """
        Test that get_api_key raises ValueError when key is missing.

        monkeypatch is a pytest fixture that allows us to temporarily
        modify environment variables for testing.
        """
        # Remove the API key from environment
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        # Should raise ValueError
        with pytest.raises(ValueError, match="OPENAI_API_KEY not found"):
            get_api_key()


class TestLoadDocuments:
    """Tests for load_documents function"""

    def test_load_documents_from_temp_dir(self, temp_data_dir):
        """
        Test loading documents from a temporary directory.

        temp_data_dir is a fixture that creates a temp dir with sample files.
        """
        documents = load_documents(temp_data_dir)

        # Should return a list of Documents
        assert isinstance(documents, list)
        assert len(documents) > 0
        assert all(isinstance(doc, Document) for doc in documents)

    def test_load_documents_raises_on_missing_dir(self, tmp_path):
        """
        Test that load_documents raises FileNotFoundError for missing directory.
        """
        nonexistent_dir = tmp_path / "does_not_exist"

        with pytest.raises(FileNotFoundError, match="Data directory not found"):
            load_documents(nonexistent_dir)

    def test_load_documents_raises_on_empty_dir(self, tmp_path):
        """
        Test that load_documents raises ValueError when no .txt files found.
        """
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        with pytest.raises(ValueError, match="No text files found"):
            load_documents(empty_dir)

    def test_load_documents_creates_chunks(self, temp_data_dir):
        """
        Test that load_documents properly chunks the text.

        Documents should be split into chunks based on Config.CHUNK_SIZE.
        """
        documents = load_documents(temp_data_dir)

        # Check that chunks have reasonable size
        for doc in documents:
            # Chunks should not be empty
            assert len(doc.page_content) > 0
            # Chunks should generally be <= chunk_size (with some tolerance)
            # Some chunks can be slightly larger due to how splitting works
            assert len(doc.page_content) <= Config.CHUNK_SIZE + 100

    def test_load_documents_loads_all_txt_files(self, tmp_path):
        """
        Test that all .txt files in directory are loaded.
        """
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        # Create multiple files
        (data_dir / "doc1.txt").write_text("Content of document 1. " * 50)
        (data_dir / "doc2.txt").write_text("Content of document 2. " * 50)
        (data_dir / "doc3.txt").write_text("Content of document 3. " * 50)

        documents = load_documents(data_dir)

        # Should have created documents from all files
        # Exact number depends on chunking, but should be > 0
        assert len(documents) > 0

        # Combine all document content
        all_content = " ".join(doc.page_content for doc in documents)

        # All three documents should be represented
        assert "document 1" in all_content
        assert "document 2" in all_content
        assert "document 3" in all_content

    def test_load_documents_handles_unicode(self, tmp_path):
        """
        Test that load_documents properly handles Unicode characters.
        """
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        # Create file with Unicode characters
        unicode_content = "Hello 世界! Testing émojis 🚀 and spëcial çharacters."
        (data_dir / "unicode.txt").write_text(unicode_content, encoding="utf-8")

        documents = load_documents(data_dir)

        assert len(documents) > 0
        # Content should be preserved
        all_content = " ".join(doc.page_content for doc in documents)
        assert "世界" in all_content
        assert "🚀" in all_content

    def test_load_documents_skips_empty_files(self, tmp_path):
        """
        Test that empty files are skipped gracefully.
        """
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        # Create one valid file and one empty file
        (data_dir / "valid.txt").write_text("Valid content here.")
        (data_dir / "empty.txt").write_text("")

        # Should not raise error, just skip empty file
        documents = load_documents(data_dir)
        assert len(documents) > 0


class TestCreateVectorstore:
    """Tests for create_vectorstore function"""

    @pytest.mark.integration
    def test_create_vectorstore_with_sample_docs(self, sample_documents):
        """
        Test creating a vector store from sample documents.

        This is an integration test because it calls OpenAI's embeddings API.
        """
        import os
        api_key = os.getenv("OPENAI_API_KEY")

        vectorstore = create_vectorstore(sample_documents, api_key)

        # Should return a FAISS object
        assert vectorstore is not None
        # Should be able to search
        results = vectorstore.similarity_search("What is AI?", k=2)
        assert len(results) > 0

    def test_create_vectorstore_raises_on_empty_documents(self):
        """
        Test that create_vectorstore raises ValueError for empty document list.
        """
        import os
        api_key = os.getenv("OPENAI_API_KEY")

        with pytest.raises(ValueError, match="Cannot create vectorstore from empty"):
            create_vectorstore([], api_key)


class TestFormatDocs:
    """Tests for format_docs function"""

    def test_format_docs_single_document(self):
        """
        Test formatting a single document.
        """
        docs = [Document(page_content="Test content")]
        result = format_docs(docs)

        assert result == "Test content"

    def test_format_docs_multiple_documents(self):
        """
        Test formatting multiple documents.

        Documents should be joined with double newlines.
        """
        docs = [
            Document(page_content="First document"),
            Document(page_content="Second document"),
            Document(page_content="Third document"),
        ]
        result = format_docs(docs)

        assert "First document" in result
        assert "Second document" in result
        assert "Third document" in result
        # Should be separated by double newlines
        assert "\n\n" in result

    def test_format_docs_empty_list(self):
        """
        Test formatting an empty document list.
        """
        result = format_docs([])
        assert result == ""

    def test_format_docs_preserves_content(self):
        """
        Test that formatting preserves exact content.
        """
        docs = [
            Document(page_content="Content with\nnewlines"),
            Document(page_content="Content with    spaces"),
        ]
        result = format_docs(docs)

        assert "Content with\nnewlines" in result
        assert "Content with    spaces" in result


class TestConfig:
    """Tests for Config class"""

    def test_config_has_required_attributes(self):
        """
        Test that Config class has all required configuration attributes.
        """
        assert hasattr(Config, "BASE_DIR")
        assert hasattr(Config, "ENV_PATH")
        assert hasattr(Config, "DATA_PATH")
        assert hasattr(Config, "CHUNK_SIZE")
        assert hasattr(Config, "CHUNK_OVERLAP")
        assert hasattr(Config, "RETRIEVER_K")
        assert hasattr(Config, "LLM_MODEL")
        assert hasattr(Config, "LLM_TEMPERATURE")

    def test_config_paths_are_path_objects(self):
        """
        Test that Config paths are Path objects.
        """
        assert isinstance(Config.BASE_DIR, Path)
        assert isinstance(Config.ENV_PATH, Path)
        assert isinstance(Config.DATA_PATH, Path)

    def test_config_chunk_size_is_positive(self):
        """
        Test that chunk size configuration is positive.
        """
        assert Config.CHUNK_SIZE > 0
        assert Config.CHUNK_OVERLAP >= 0
        assert Config.CHUNK_OVERLAP < Config.CHUNK_SIZE

    def test_config_retriever_k_is_positive(self):
        """
        Test that retriever k (number of documents to retrieve) is positive.
        """
        assert Config.RETRIEVER_K > 0
        assert isinstance(Config.RETRIEVER_K, int)

    def test_config_temperature_in_valid_range(self):
        """
        Test that LLM temperature is in valid range [0, 2].

        OpenAI accepts temperature values between 0 and 2.
        """
        assert 0 <= Config.LLM_TEMPERATURE <= 2

    def test_config_llm_model_is_string(self):
        """
        Test that LLM model is a non-empty string.
        """
        assert isinstance(Config.LLM_MODEL, str)
        assert len(Config.LLM_MODEL) > 0


# Parametrized test example
@pytest.mark.parametrize("num_docs,expected_min_length", [
    (1, 1),
    (3, 5),
    (5, 9),
])
def test_format_docs_length(num_docs, expected_min_length):
    """
    Parametrized test: verify formatted output has minimum length.

    For N documents, we expect at least:
    N * (min content length) + (N-1) * (separator length)
    """
    docs = [Document(page_content="X") for _ in range(num_docs)]
    result = format_docs(docs)

    # Result length should be at least: num_docs * 1 + (num_docs - 1) * 2
    # (1 char per doc + 2 chars for \n\n separator)
    assert len(result) >= expected_min_length
