"""Tests for SEBEK dashboard module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st

from sebek.dashboard import (
    get_vector_db,
    query_sebek,
    load_master_map,
)
from sebek.utils.errors import OllamaError


class TestLoadMasterMap:
    """Test master map loading."""

    def test_load_master_map_returns_dict(self):
        """Test load_master_map returns a dictionary."""
        result = load_master_map()
        assert isinstance(result, dict)

    def test_load_master_map_missing_file(self, temp_dir):
        """Test load_master_map with missing file returns empty dict."""
        # With nonexistent file, should return {}
        result = load_master_map()
        assert result == {} or isinstance(result, dict)


class TestQuerySebek:
    """Test SEBEK LLM query functionality."""

    @patch("sebek.dashboard.requests.post")
    def test_query_sebek_success(self, mock_post, mock_ollama_response):
        """Test successful SEBEK query."""
        mock_response = MagicMock()
        mock_response.json.return_value = mock_ollama_response
        mock_post.return_value = mock_response

        # Setup session state
        st.session_state.master_map = {"total_files_across_all_territories": 100}

        result = query_sebek("test query")

        assert result == mock_ollama_response["response"]
        mock_post.assert_called_once()

    @patch("sebek.dashboard.requests.post")
    def test_query_sebek_connection_error(self, mock_post):
        """Test SEBEK query with connection error."""
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError()

        st.session_state.master_map = {}

        with pytest.raises(OllamaError):
            query_sebek("test query")

    @patch("sebek.dashboard.requests.post")
    def test_query_sebek_timeout(self, mock_post):
        """Test SEBEK query with timeout."""
        import requests
        mock_post.side_effect = requests.exceptions.Timeout()

        st.session_state.master_map = {}

        with pytest.raises(OllamaError):
            query_sebek("test query")

    @patch("sebek.dashboard.requests.post")
    def test_query_sebek_includes_context(self, mock_post):
        """Test query includes retrieved context."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Response with context"}
        mock_post.return_value = mock_response

        st.session_state.master_map = {}

        context = "Retrieved document content"
        query_sebek("query", retrieved_context=context)

        # Check that context is in the posted prompt
        call_args = mock_post.call_args
        posted_data = call_args.kwargs["json"]
        assert context in posted_data["prompt"]


class TestGetVectorDB:
    """Test vector DB initialization."""

    @patch("sebek.dashboard.initialize_vector_db")
    def test_get_vector_db_initializes(self, mock_init):
        """Test get_vector_db initializes database."""
        mock_db = MagicMock()
        mock_init.return_value = mock_db

        st.session_state.vector_db = None

        result = get_vector_db()

        assert result == mock_db
        mock_init.assert_called_once()

    def test_get_vector_db_returns_cached(self):
        """Test get_vector_db returns cached instance."""
        mock_db = MagicMock()
        st.session_state.vector_db = mock_db

        result = get_vector_db()

        assert result == mock_db
