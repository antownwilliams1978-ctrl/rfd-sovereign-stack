"""Custom exceptions for SEBEK.

Provides structured error handling across the application.
"""


class SebekError(Exception):
    """Base exception for all SEBEK errors."""

    pass


class ConfigError(SebekError):
    """Raised when configuration is invalid or missing."""

    pass


class VectorDBError(SebekError):
    """Raised when vector database operations fail."""

    pass


class IngestionError(SebekError):
    """Raised when document ingestion fails."""

    pass


class SpeechError(SebekError):
    """Raised when speech recognition/synthesis fails."""

    pass


class OllamaError(SebekError):
    """Raised when Ollama API operations fail."""

    pass


class EmbeddingError(SebekError):
    """Raised when embedding generation fails."""

    pass
