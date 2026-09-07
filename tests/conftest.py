"""Pytest configuration and shared fixtures.

Provides reusable fixtures for testing SEBEK components.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock
import tempfile
import shutil

from sebek.config import Config, OllamaConfig, VectorDBConfig, VaultConfig, SpeechConfig
from sebek.utils.logging import get_logger


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files.

    Yields:
        Path: Temporary directory path that is cleaned up after the test.
    """
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_config(temp_dir):
    """Create a mock configuration for testing.

    Args:
        temp_dir: Temporary directory fixture.

    Returns:
        Config: Mock configuration with temp paths.
    """
    # Create a copy of config with temp paths
    original_db = Config.vectordb
    original_vault = Config.vault
    original_speech = Config.speech
    original_logging = Config.logging

    # Override with temp directories
    Config.vectordb = VectorDBConfig(
        db_dir=temp_dir / "vectordb",
        chunk_size=original_db.chunk_size,
        chunk_overlap=original_db.chunk_overlap,
        batch_size=original_db.batch_size,
    )
    Config.vault = VaultConfig(
        vault_path=temp_dir / "vault",
    )
    Config.speech = SpeechConfig(
        vosk_model_path=temp_dir / "vosk_model",
        persist_dir=temp_dir / "speech_data",
    )
    Config.logging = original_logging

    yield Config

    # Restore original config
    Config.vectordb = original_db
    Config.vault = original_vault
    Config.speech = original_speech
    Config.logging = original_logging


@pytest.fixture
def mock_vector_db():
    """Create a mock vector database.

    Returns:
        MagicMock: Mock Chroma vector store.
    """
    mock_db = MagicMock()
    mock_db.similarity_search.return_value = [
        Mock(page_content="Sample document 1"),
        Mock(page_content="Sample document 2"),
    ]
    mock_db.add_documents.return_value = None
    return mock_db


@pytest.fixture
def mock_ollama_response():
    """Create a mock Ollama API response.

    Returns:
        dict: Mock LLM response.
    """
    return {
        "response": "This is a test response from SEBEK.",
        "model": "sebek-core",
        "created_at": "2026-09-03T01:00:00Z",
        "total_duration": 1000000000,
        "load_duration": 100000000,
        "prompt_eval_count": 10,
        "prompt_eval_duration": 500000000,
        "eval_count": 20,
        "eval_duration": 400000000,
    }


@pytest.fixture
def sample_documents():
    """Create sample documents for ingestion testing.

    Returns:
        list: List of mock LangChain Document objects.
    """
    mock_docs = []
    for i in range(3):
        doc = Mock()
        doc.page_content = f"Sample document {i} with some content for testing."
        doc.metadata = {"source": f"test_{i}.txt", "index": i}
        mock_docs.append(doc)
    return mock_docs


@pytest.fixture
def sample_speech_result():
    """Create a sample speech recognition result.

    Returns:
        dict: Mock speech recognition result.
    """
    return {
        "text": "hello sebek how are you",
        "confidence": 0.95,
        "words": [
            {"conf": 0.98, "start": 0.0, "end": 0.5, "result": "hello"},
            {"conf": 0.92, "start": 0.5, "end": 1.0, "result": "sebek"},
        ],
        "vosk": {
            "result": [
                {"conf": 0.98, "start": 0.0, "end": 0.5, "result": "hello"},
                {"conf": 0.92, "start": 0.5, "end": 1.0, "result": "sebek"},
            ],
            "text": "hello sebek how are you",
        },
    }


@pytest.fixture
def logger_fixture():
    """Get a test logger.

    Returns:
        logging.Logger: Logger for testing.
    """
    return get_logger("sebek.test")
