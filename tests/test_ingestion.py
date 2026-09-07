"""Tests for SEBEK ingestion module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from sebek.ingestion import (
    scan_vault_for_documents,
    load_documents_from_vault,
    ingest_documents_to_vectordb,
)
from sebek.utils.errors import IngestionError, VectorDBError


class TestScanVault:
    """Test vault scanning functionality."""

    def test_scan_vault_nonexistent_path_raises_error(self):
        """Test scanning nonexistent vault raises error."""
        with pytest.raises(IngestionError):
            scan_vault_for_documents(vault_path=Path("/nonexistent/path"))

    def test_scan_vault_empty_directory(self, temp_dir):
        """Test scanning empty vault returns empty list."""
        docs = scan_vault_for_documents(vault_path=temp_dir)
        assert docs == []

    def test_scan_vault_finds_markdown_files(self, temp_dir):
        """Test scanning finds .md files."""
        # Create test files
        (temp_dir / "test1.md").write_text("# Test")
        (temp_dir / "test2.md").write_text("# Test 2")
        (temp_dir / "test.txt").write_text("Text file")

        docs = scan_vault_for_documents(vault_path=temp_dir)

        # Should find 2 .md files
        md_files = [d for d in docs if d[0].suffix == ".md"]
        assert len(md_files) == 2

    def test_scan_vault_excludes_patterns(self, temp_dir):
        """Test scanning respects exclude patterns."""
        # Create directories
        normal_dir = temp_dir / "normal"
        normal_dir.mkdir()
        (normal_dir / "file.md").write_text("Content")

        exclude_dir = temp_dir / "90_DUPLICATES"
        exclude_dir.mkdir()
        (exclude_dir / "file.md").write_text("Excluded")

        docs = scan_vault_for_documents(vault_path=temp_dir)

        # Should only find file in normal directory
        assert len(docs) == 1
        assert "normal" in str(docs[0][0])


class TestLoadDocuments:
    """Test document loading."""

    @patch("sebek.ingestion.HAS_LOADERS", False)
    def test_load_documents_missing_loader_raises_error(self):
        """Test loading without LangChain raises error."""
        with pytest.raises(IngestionError):
            load_documents_from_vault()

    @patch("sebek.ingestion.HAS_LOADERS", True)
    @patch("sebek.ingestion.TextLoader")
    def test_load_documents_skips_encoding_errors(self, mock_loader_class, temp_dir):
        """Test loading skips files with encoding errors."""
        # Create test file
        (temp_dir / "test.md").write_text("Content")

        # Mock loader to raise UnicodeDecodeError
        mock_loader = MagicMock()
        mock_loader.load.side_effect = UnicodeDecodeError(
            "utf-8", b"", 0, 1, "invalid start byte"
        )
        mock_loader_class.return_value = mock_loader

        docs = load_documents_from_vault(vault_path=temp_dir)

        # Should return empty list (file skipped)
        assert docs == []


class TestIngestDocuments:
    """Test end-to-end ingestion."""

    @patch("sebek.ingestion.initialize_vector_db")
    @patch("sebek.ingestion.get_text_splitter")
    @patch("sebek.ingestion.load_documents_from_vault")
    def test_ingest_documents_success(
        self, mock_load, mock_splitter, mock_init_db, sample_documents
    ):
        """Test successful document ingestion."""
        # Setup mocks
        mock_load.return_value = sample_documents

        mock_split_instance = MagicMock()
        mock_split_instance.split_documents.return_value = sample_documents  # Same for simplicity
        mock_splitter.return_value = mock_split_instance

        mock_db = MagicMock()
        mock_init_db.return_value = mock_db

        # Run ingestion
        doc_count, chunk_count = ingest_documents_to_vectordb()

        # Verify
        assert doc_count == len(sample_documents)
        assert chunk_count == len(sample_documents)
        mock_db.add_documents.assert_called()

    @patch("sebek.ingestion.load_documents_from_vault")
    def test_ingest_empty_vault_returns_zero(
        self, mock_load
    ):
        """Test ingesting empty vault returns (0, 0)."""
        mock_load.return_value = []

        doc_count, chunk_count = ingest_documents_to_vectordb()

        assert doc_count == 0
        assert chunk_count == 0

    @patch("sebek.ingestion.initialize_vector_db")
    def test_ingest_vectordb_error_raises(
        self, mock_init_db
    ):
        """Test ingestion fails if vector DB unavailable."""
        mock_init_db.return_value = None

        with patch("sebek.ingestion.load_documents_from_vault") as mock_load:
            mock_load.return_value = [{"page_content": "test"}]

            with pytest.raises(VectorDBError):
                ingest_documents_to_vectordb()
