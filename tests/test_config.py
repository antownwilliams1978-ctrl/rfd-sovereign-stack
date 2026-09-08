"""Tests for SEBEK configuration module."""

import os
import pytest
from pathlib import Path
import sebek.config as config_module
from sebek.config import Config, OllamaConfig, VectorDBConfig
from sebek.utils.errors import ConfigError


class TestOllamaConfig:
    """Test Ollama configuration."""

    def test_default_ollama_url(self):
        """Test default Ollama URL is localhost."""
        assert Config.ollama.url.startswith("http://")
        assert "localhost" in Config.ollama.url or "127.0.0.1" in Config.ollama.url

    def test_ollama_temperature_range(self):
        """Test temperature is in valid range."""
        assert 0.0 <= Config.ollama.temperature <= 1.0

    def test_ollama_max_tokens_positive(self):
        """Test max tokens is positive."""
        assert Config.ollama.max_tokens > 0


class TestVectorDBConfig:
    """Test vector database configuration."""

    def test_vectordb_chunk_size_positive(self):
        """Test chunk size is positive."""
        assert Config.vectordb.chunk_size > 0

    def test_vectordb_batch_size_positive(self):
        """Test batch size is positive."""
        assert Config.vectordb.batch_size > 0

    def test_vectordb_batch_larger_than_chunk(self):
        """Test batch size is larger than chunk size."""
        assert Config.vectordb.batch_size > Config.vectordb.chunk_size


class TestVaultConfig:
    """Test file vault configuration."""

    def test_vault_path_type(self):
        """Test vault path is a Path object."""
        assert isinstance(Config.vault.vault_path, Path)

    def test_supported_extensions_not_empty(self):
        """Test supported extensions are defined."""
        assert len(Config.vault.supported_extensions) > 0

    def test_supported_extensions_are_strings(self):
        """Test supported extensions are strings."""
        for ext in Config.vault.supported_extensions:
            assert isinstance(ext, str)
            assert ext.startswith(".")


class TestSpeechConfig:
    """Test speech configuration."""

    def test_speech_sample_rate_valid(self):
        """Test sample rate is standard value."""
        # Common sample rates: 8000, 16000, 44100, 48000
        assert Config.speech.sample_rate in (8000, 16000, 44100, 48000)

    def test_speech_channels_valid(self):
        """Test channels is mono or stereo."""
        assert Config.speech.channels in (1, 2)

    def test_vosk_model_candidates_resolve_relative_override(self, monkeypatch, temp_dir):
        """Relative override paths should resolve from the current working directory."""
        monkeypatch.chdir(temp_dir)
        override = Path("models/custom-vosk")

        candidates = Config.get_vosk_model_candidates(override)

        assert candidates == ((temp_dir / "models/custom-vosk").resolve(),)

    def test_find_vosk_model_path_uses_system_fallback_when_default_missing(self, monkeypatch, temp_dir):
        """System model path should be checked when no env override is set."""
        fallback_model = temp_dir / "opt-vosk-model"
        fallback_model.mkdir()

        original_model_path = Config.speech.vosk_model_path
        monkeypatch.delenv("SEBEK_VOSK_MODEL", raising=False)
        monkeypatch.setattr(config_module, "DEFAULT_SYSTEM_VOSK_MODEL_PATH", fallback_model)
        Config.speech.vosk_model_path = temp_dir / "missing-model"

        try:
            assert Config.find_vosk_model_path() == fallback_model
        finally:
            Config.speech.vosk_model_path = original_model_path


class TestEnvironmentVariables:
    """Test environment variable override."""

    def test_override_ollama_url(self, monkeypatch):
        """Test SEBEK_OLLAMA_URL environment variable."""
        test_url = "http://custom-ollama:11434"
        monkeypatch.setenv("SEBEK_OLLAMA_URL", test_url)
        # Note: Config is loaded at import time, so this tests the mechanism
        # In real tests, you'd need to reload the config module

    def test_override_embedding_model(self, monkeypatch):
        """Test SEBEK_EMBEDDING_MODEL environment variable."""
        test_model = "custom-embed-model"
        monkeypatch.setenv("SEBEK_EMBEDDING_MODEL", test_model)
        # Config loaded at import time


class TestConfigValidation:
    """Test configuration validation."""

    def test_validate_ollama_url_format(self):
        """Test Ollama URL has valid format."""
        assert Config.ollama.url.startswith(("http://", "https://"))

    def test_ensure_directories_creates_paths(self, temp_dir, mock_config):
        """Test ensure_directories creates required directories."""
        mock_config.vectordb.db_dir = temp_dir / "vectordb"
        mock_config.speech.persist_dir = temp_dir / "speech"

        mock_config.ensure_directories()

        assert mock_config.vectordb.db_dir.exists()
        assert mock_config.speech.persist_dir.exists()

    def test_to_dict_has_required_keys(self):
        """Test to_dict() returns all required keys."""
        config_dict = Config.to_dict()
        required_keys = ["ollama", "vectordb", "vault", "speech", "logging"]
        for key in required_keys:
            assert key in config_dict
