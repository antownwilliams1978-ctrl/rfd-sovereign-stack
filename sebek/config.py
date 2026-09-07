"""Centralized configuration management for SEBEK.

Handles environment variables, defaults, and validation for:
- Ollama/LLM configuration
- Vector database paths
- File vault locations
- Speech recognition settings
- API endpoints
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class OllamaConfig:
    """Ollama LLM service configuration."""

    url: str
    """Base URL for Ollama API endpoint."""

    api_observe_endpoint: str
    """Endpoint for posting observations/speech."""

    embedding_model: str
    """Model name for text embeddings (e.g., 'nomic-embed-text')."""

    chat_model: str
    """Model name for chat completions (e.g., 'sebek-core')."""

    temperature: float = 0.3
    """Temperature for LLM responses (0.0-1.0)."""

    max_tokens: int = 2048
    """Maximum tokens in LLM response."""


@dataclass
class VectorDBConfig:
    """Vector database (Chroma) configuration."""

    db_dir: Path
    """Directory for persistent Chroma vector database."""

    chunk_size: int = 500
    """Characters per document chunk for embedding."""

    chunk_overlap: int = 50
    """Overlap between consecutive chunks."""

    batch_size: int = 5000
    """Batch size for ingesting documents."""

    similarity_k: int = 3
    """Number of similar documents to retrieve (RAG)."""

    max_query_chars: int = 3000
    """Max query length before truncation for embeddings."""


@dataclass
class VaultConfig:
    """File vault configuration for document ingestion."""

    vault_path: Path
    """Root path to file vault for ingestion."""

    supported_extensions: tuple = (".md", ".txt", ".csv")
    """File extensions to ingest."""

    exclude_patterns: tuple = ("90_DUPLICATES", "$RECYCLE.BIN", "System Volume Information")
    """Directory patterns to skip during ingestion."""


@dataclass
class SpeechConfig:
    """Speech recognition and synthesis configuration."""

    vosk_model_path: Path
    """Path to Vosk offline ASR model directory."""

    persist_dir: Path
    """Directory for storing audio snippets."""

    sample_rate: int = 16000
    """Audio sample rate (Hz)."""

    channels: int = 1
    """Number of audio channels (mono=1, stereo=2)."""

    blocksize: int = 8000
    """Audio block size in bytes."""

    enable_tts: bool = True
    """Enable text-to-speech feedback."""

    log_path: Optional[Path] = None
    """Log file for speech agent (optional)."""


@dataclass
class LoggingConfig:
    """Logging configuration."""

    level: str = "INFO"
    """Logging level (DEBUG, INFO, WARNING, ERROR)."""

    log_dir: Path = Path("./logs")
    """Directory for log files."""

    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    """Log message format."""

    enable_file_logging: bool = True
    """Whether to write logs to files."""


class Config:
    """Main configuration class for SEBEK.

    Loads settings from environment variables with sensible defaults.
    All paths are converted to Path objects for cross-platform compatibility.

    Environment variables:
        SEBEK_OLLAMA_URL: Ollama base URL (default: http://localhost:11434)
        SEBEK_EMBEDDING_MODEL: Embedding model name
        SEBEK_CHAT_MODEL: Chat model name
        SEBEK_DB_DIR: Vector database directory
        SEBEK_VAULT_PATH: File vault root path
        SEBEK_VOSK_MODEL: Vosk model directory
        SEBEK_SPEECH_PERSIST_DIR: Speech audio storage directory
        SEBEK_LOG_LEVEL: Logging level
        SEBEK_LOG_DIR: Log directory
    """

    # Ollama configuration
    ollama = OllamaConfig(
        url=os.getenv("SEBEK_OLLAMA_URL", "http://localhost:11434"),
        api_observe_endpoint=os.getenv(
            "SEBEK_OLLAMA_OBSERVE", "http://localhost:11434/api/observe"
        ),
        embedding_model=os.getenv("SEBEK_EMBEDDING_MODEL", "nomic-embed-text"),
        chat_model=os.getenv("SEBEK_CHAT_MODEL", "sebek-core"),
        temperature=float(os.getenv("SEBEK_LLM_TEMPERATURE", "0.3")),
        max_tokens=int(os.getenv("SEBEK_LLM_MAX_TOKENS", "2048")),
    )

    # Vector database configuration
    vectordb = VectorDBConfig(
        db_dir=Path(os.getenv("SEBEK_DB_DIR", "./sebek_memory_db")),
        chunk_size=int(os.getenv("SEBEK_CHUNK_SIZE", "500")),
        chunk_overlap=int(os.getenv("SEBEK_CHUNK_OVERLAP", "50")),
        batch_size=int(os.getenv("SEBEK_BATCH_SIZE", "5000")),
        similarity_k=int(os.getenv("SEBEK_SIMILARITY_K", "3")),
        max_query_chars=int(os.getenv("SEBEK_MAX_QUERY_CHARS", "3000")),
    )

    # File vault configuration
    vault = VaultConfig(
        vault_path=Path(os.getenv("SEBEK_VAULT_PATH", "/mnt/f/")),
    )

    # Speech configuration
    speech = SpeechConfig(
        vosk_model_path=Path(os.getenv("SEBEK_VOSK_MODEL", "./models/vosk-model-small-en-us-0.15")),
        persist_dir=Path(os.getenv("SEBEK_SPEECH_PERSIST_DIR", "./sebek_speech_data")),
        sample_rate=int(os.getenv("SEBEK_SAMPLE_RATE", "16000")),
        channels=int(os.getenv("SEBEK_CHANNELS", "1")),
        blocksize=int(os.getenv("SEBEK_BLOCKSIZE", "8000")),
        enable_tts=os.getenv("SEBEK_ENABLE_TTS", "true").lower() == "true",
        log_path=Path(os.getenv("SEBEK_SPEECH_LOG", "./sebek_speech.log"))
        if os.getenv("SEBEK_SPEECH_LOG")
        else None,
    )

    # Logging configuration
    logging = LoggingConfig(
        level=os.getenv("SEBEK_LOG_LEVEL", "INFO"),
        log_dir=Path(os.getenv("SEBEK_LOG_DIR", "./logs")),
        enable_file_logging=os.getenv("SEBEK_LOG_FILE", "true").lower() == "true",
    )

    @classmethod
    def validate(cls) -> bool:
        """Validate critical configuration paths and settings.

        Returns:
            bool: True if validation passes, False otherwise.

        Raises:
            ValueError: If critical configuration is missing or invalid.
        """
        issues = []

        # Validate Ollama URL is accessible format
        if not cls.ollama.url.startswith(("http://", "https://")):
            issues.append(f"Invalid Ollama URL format: {cls.ollama.url}")

        # Warn about vault path
        if not cls.vault.vault_path.exists():
            logger.warning(f"Vault path does not exist: {cls.vault.vault_path}")

        # Warn about Vosk model
        if not cls.speech.vosk_model_path.exists():
            logger.warning(f"Vosk model not found at: {cls.speech.vosk_model_path}")

        if issues:
            raise ValueError("\n".join(issues))

        return True

    @classmethod
    def ensure_directories(cls) -> None:
        """Create required directories if they don't exist."""
        for path in [
            cls.vectordb.db_dir,
            cls.speech.persist_dir,
            cls.logging.log_dir,
        ]:
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {path}")

    @classmethod
    def to_dict(cls) -> dict:
        """Export configuration as dictionary (for logging/debugging).

        Returns:
            dict: Configuration as nested dictionary.
        """
        return {
            "ollama": {
                "url": cls.ollama.url,
                "embedding_model": cls.ollama.embedding_model,
                "chat_model": cls.ollama.chat_model,
                "temperature": cls.ollama.temperature,
            },
            "vectordb": {
                "db_dir": str(cls.vectordb.db_dir),
                "chunk_size": cls.vectordb.chunk_size,
                "batch_size": cls.vectordb.batch_size,
            },
            "vault": {
                "vault_path": str(cls.vault.vault_path),
                "supported_extensions": cls.vault.supported_extensions,
            },
            "speech": {
                "vosk_model_path": str(cls.speech.vosk_model_path),
                "persist_dir": str(cls.speech.persist_dir),
                "enable_tts": cls.speech.enable_tts,
            },
            "logging": {
                "level": cls.logging.level,
                "log_dir": str(cls.logging.log_dir),
            },
        }
