"""Document ingestion pipeline for SEBEK.

Batch loads documents from file vault, chunks them, and ingests
into vector database for semantic search.
"""

import os
import logging
from pathlib import Path
from typing import List, Tuple, Optional

try:
    from langchain_community.document_loaders import TextLoader
    HAS_LOADERS = True
except ImportError:
    HAS_LOADERS = False

from sebek.config import Config
from sebek.utils.logging import get_logger
from sebek.utils.errors import IngestionError, VectorDBError
from sebek.utils.vectordb import initialize_vector_db, get_text_splitter

logger = get_logger(__name__)


def scan_vault_for_documents(
    vault_path: Optional[Path] = None,
    extensions: Optional[Tuple[str, ...]] = None,
    exclude_patterns: Optional[Tuple[str, ...]] = None,
) -> List[Tuple[Path, str]]:
    """Scan vault directory for documents matching supported extensions.

    Args:
        vault_path: Root path to scan. Uses config default if None.
        extensions: File extensions to include. Uses config default if None.
        exclude_patterns: Directory patterns to skip. Uses config default if None.

    Returns:
        List of (Path, relative_path_string) tuples for each found document.

    Raises:
        IngestionError: If vault path doesn't exist.

    Example:
        >>> docs = scan_vault_for_documents()
        >>> print(f"Found {len(docs)} documents")
    """
    vault_path = vault_path or Config.vault.vault_path
    extensions = extensions or Config.vault.supported_extensions
    exclude_patterns = exclude_patterns or Config.vault.exclude_patterns

    if not vault_path.exists():
        raise IngestionError(f"Vault path does not exist: {vault_path}")

    documents = []
    skipped_count = 0

    logger.info(f"Scanning vault at {vault_path} for {extensions}")

    for root, dirs, files in os.walk(vault_path):
        # Skip excluded directories
        dirs[:] = [
            d for d in dirs if not any(pattern in d for pattern in exclude_patterns)
        ]

        for file in files:
            if file.lower().endswith(extensions):
                file_path = Path(root) / file
                try:
                    # Quick validation - check if file is readable
                    if os.access(file_path, os.R_OK):
                        relative_path = str(file_path.relative_to(vault_path))
                        documents.append((file_path, relative_path))
                except (OSError, ValueError) as e:
                    skipped_count += 1
                    logger.debug(f"Skipped {file_path}: {e}")

    logger.info(
        f"Found {len(documents)} documents (skipped {skipped_count} unreadable files)"
    )
    return documents


def load_documents_from_vault(
    vault_path: Optional[Path] = None,
) -> List:
    """Load text content from all vault documents.

    Args:
        vault_path: Root path to load from. Uses config default if None.

    Returns:
        List of LangChain Document objects.

    Raises:
        IngestionError: If document loading fails.
    """
    if not HAS_LOADERS:
        raise IngestionError("LangChain document loaders not available")

    documents = []
    doc_paths = scan_vault_for_documents(vault_path)

    logger.info(f"Loading {len(doc_paths)} documents into memory")

    for file_path, rel_path in doc_paths:
        try:
            loader = TextLoader(str(file_path), encoding="utf-8")
            loaded = loader.load()
            documents.extend(loaded)

            if len(documents) % 100 == 0:
                logger.debug(f"Loaded {len(documents)} documents so far...")

        except UnicodeDecodeError:
            logger.warning(f"Skipped {rel_path}: encoding error")
        except (IOError, OSError) as e:
            logger.warning(f"Skipped {rel_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error loading {rel_path}: {e}")

    logger.info(f"Successfully loaded {len(documents)} text chunks")
    return documents


def ingest_documents_to_vectordb(
    vault_path: Optional[Path] = None,
    batch_size: Optional[int] = None,
) -> Tuple[int, int]:
    """End-to-end document ingestion pipeline.

    Loads documents from vault, splits into chunks, and ingests into
    vector database in batches.

    Args:
        vault_path: Root path to ingest from. Uses config default if None.
        batch_size: Batch size for ingestion. Uses config default if None.

    Returns:
        Tuple of (documents_ingested, chunks_created).

    Raises:
        IngestionError: If any step of ingestion fails.
        VectorDBError: If vector database operations fail.

    Example:
        >>> doc_count, chunk_count = ingest_documents_to_vectordb()
        >>> print(f"Ingested {doc_count} docs -> {chunk_count} chunks")
    """
    batch_size = batch_size or Config.vectordb.batch_size

    try:
        # Load documents
        logger.info("🦅 SEBEK MASS DIGESTION SEQUENCE INITIATED...")
        documents = load_documents_from_vault(vault_path)

        if not documents:
            logger.warning("No documents found in vault")
            return 0, 0

        # Split into chunks
        logger.info("Splitting documents into semantic chunks...")
        text_splitter = get_text_splitter()
        chunks = text_splitter.split_documents(documents)
        logger.info(
            f"Generated {len(chunks)} chunks from {len(documents)} documents"
        )

        # Initialize vector database
        logger.info("Connecting to vector database...")
        vector_db = initialize_vector_db()
        if not vector_db:
            raise VectorDBError("Failed to initialize vector database")

        # Ingest in batches
        logger.info(f"Ingesting {len(chunks)} chunks (batch size: {batch_size})...")
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            try:
                vector_db.add_documents(batch)
                logger.info(
                    f"Committed batch {i} to {i + len(batch)} of {len(chunks)} to memory"
                )
            except Exception as e:
                raise VectorDBError(f"Failed to ingest batch {i}: {e}") from e

        logger.info(
            f"✅ MASS DIGESTION COMPLETE. SEBEK ingested {len(chunks)} data blocks"
        )
        return len(documents), len(chunks)

    except (IngestionError, VectorDBError):
        raise
    except Exception as e:
        raise IngestionError(f"Unexpected error during ingestion: {e}") from e
