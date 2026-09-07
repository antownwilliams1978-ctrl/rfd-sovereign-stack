"""Document ingestion script - standalone CLI for mass ingestion.

This module provides a command-line interface for ingesting documents
from a file vault into SEBEK's vector database.

Usage:
    python -m sebek.ingestion_cli [--vault-path PATH] [--batch-size SIZE]

Environment variables:
    SEBEK_VAULT_PATH: Override default vault path
    SEBEK_BATCH_SIZE: Override default batch size
"""

import sys
import argparse
from pathlib import Path

from sebek.config import Config
from sebek.utils.logging import get_logger, setup_root_logger
from sebek.ingestion import ingest_documents_to_vectordb
from sebek.utils.errors import IngestionError

logger = get_logger(__name__)


def main() -> int:
    """Main entry point for ingestion CLI.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    parser = argparse.ArgumentParser(
        description="Ingest documents from file vault into SEBEK vector database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--vault-path",
        type=Path,
        default=None,
        help=f"Path to file vault (default: {Config.vault.vault_path})",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help=f"Batch size for ingestion (default: {Config.vectordb.batch_size})",
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)",
    )

    args = parser.parse_args()

    # Setup logging
    setup_root_logger()

    try:
        # Ensure directories exist
        Config.ensure_directories()

        # Run ingestion
        doc_count, chunk_count = ingest_documents_to_vectordb(
            vault_path=args.vault_path,
            batch_size=args.batch_size,
        )

        logger.info(f"Ingestion complete: {doc_count} docs → {chunk_count} chunks")
        return 0

    except IngestionError as e:
        logger.error(f"Ingestion failed: {e}")
        return 1
    except KeyboardInterrupt:
        logger.info("Ingestion interrupted by user")
        return 1
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
