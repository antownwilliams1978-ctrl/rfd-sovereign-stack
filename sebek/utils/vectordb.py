"""Vector database utilities for SEBEK.

Provides high-level operations for Chroma vector database:
- Safe similarity search with context-length error handling
- Batch document ingestion
- Vector store initialization
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import OllamaEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    HAS_VECTORDB = True
except ImportError:
    HAS_VECTORDB = False

from sebek.config import Config
from sebek.utils.errors import VectorDBError, EmbeddingError

logger = logging.getLogger(__name__)


def initialize_vector_db() -> Optional["Chroma"]:
    """Initialize Chroma vector database with configured embeddings.

    Returns:
        Chroma: Initialized vector store, or None if database unavailable.

    Raises:
        VectorDBError: If database initialization fails.
    """
    if not HAS_VECTORDB:
        logger.warning("LangChain vector database dependencies not available")
        return None

    try:
        # Ensure directory exists
        Config.vectordb.db_dir.mkdir(parents=True, exist_ok=True)

        # Initialize embeddings
        embed_model = OllamaEmbeddings(
            model=Config.ollama.embedding_model,
            base_url=Config.ollama.url,
        )

        # Initialize Chroma
        vector_db = Chroma(
            persist_directory=str(Config.vectordb.db_dir),
            embedding_function=embed_model,
        )

        logger.info(f"Vector database initialized at {Config.vectordb.db_dir}")
        return vector_db

    except Exception as e:
        raise VectorDBError(f"Failed to initialize vector database: {e}") from e


def safe_similarity_search(
    vector_db: "Chroma",
    query: str,
    k: int = 3,
    logger_instance: Optional[logging.Logger] = None,
    max_chars: int = 3000,
) -> List[Dict[str, Any]]:
    """Perform similarity search with context-length error recovery.

    Protects against embedding context-length errors by truncating the query
    if necessary. Keeps the tail of the query (most recent context) and prefixes
    truncated results with a note.

    Args:
        vector_db: Chroma vector store instance.
        query: Query string to search for.
        k: Number of similar documents to return. Defaults to 3.
        logger_instance: Optional logger for warnings. Defaults to module logger.
        max_chars: Maximum characters before truncation. Defaults to 3000.

    Returns:
        List of documents matching the query, or empty list if search fails.

    Example:
        >>> db = initialize_vector_db()
        >>> results = safe_similarity_search(db, "authentication workflow", k=5)
        >>> for doc in results:
        ...     print(doc.page_content)
    """
    if logger_instance is None:
        logger_instance = logger

    def truncate_for_embedding(s: str, maxc: int) -> str:
        """Truncate string for embedding, keeping the tail and adding prefix."""
        if len(s) <= maxc:
            return s
        tail = s[-(maxc - 32) :]
        return "[TRUNCATED CONTEXT]\n" + tail

    # Initial truncation if needed
    q = query
    if len(q) > max_chars:
        if logger_instance and hasattr(logger_instance, "warning"):
            logger_instance.warning(
                f"Query length {len(q)} > {max_chars}, truncating for embedding."
            )
        q = truncate_for_embedding(q, max_chars)

    try:
        return vector_db.similarity_search(q, k=k)
    except ValueError as ve:
        text = str(ve)
        # Check if it's a context-length error
        if "context length" in text or "input length" in text:
            if logger_instance and hasattr(logger_instance, "warning"):
                logger_instance.warning(
                    "Embedding rejected input due to context length; retrying with smaller input."
                )
            # Retry with more aggressive truncation
            q2 = truncate_for_embedding(q, int(max_chars / 2))
            try:
                return vector_db.similarity_search(q2, k=k)
            except Exception as e2:
                if logger_instance and hasattr(logger_instance, "exception"):
                    logger_instance.exception(
                        f"Retry after truncation failed: {e2}"
                    )
                return []
        else:
            if logger_instance and hasattr(logger_instance, "exception"):
                logger_instance.exception(f"Embedding call failed: {ve}")
            return []
    except Exception as e:
        if logger_instance and hasattr(logger_instance, "exception"):
            logger_instance.exception(f"Unexpected error during similarity_search: {e}")
        return []


def get_text_splitter(
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
) -> "RecursiveCharacterTextSplitter":
    """Get a configured text splitter for document chunking.

    Args:
        chunk_size: Characters per chunk. Uses config default if None.
        chunk_overlap: Overlap between chunks. Uses config default if None.

    Returns:
        RecursiveCharacterTextSplitter: Configured splitter instance.

    Raises:
        VectorDBError: If LangChain dependencies are unavailable.
    """
    if not HAS_VECTORDB:
        raise VectorDBError("LangChain dependencies required for text splitting")

    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or Config.vectordb.chunk_size,
        chunk_overlap=chunk_overlap or Config.vectordb.chunk_overlap,
    )
