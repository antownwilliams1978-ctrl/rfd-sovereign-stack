"""Centralized logging configuration for SEBEK.

Provides a consistent logging setup across all SEBEK modules,
with optional file and stream handlers.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from sebek.config import Config

# Module-level cache of loggers
_loggers = {}


def get_logger(name: str, log_file: Optional[Path] = None) -> logging.Logger:
    """Get or create a logger with standard SEBEK configuration.

    Args:
        name: Logger name (typically __name__).
        log_file: Optional path to write logs to. If None, uses Config.logging.log_dir.

    Returns:
        logging.Logger: Configured logger instance.

    Example:
        >>> from sebek.utils.logging import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Starting SEBEK engine")
    """
    # Return cached logger if already configured
    if name in _loggers:
        return _loggers[name]

    logger = logging.getLogger(name)

    # Skip if logger already has handlers (avoid duplicates)
    if logger.handlers:
        return logger

    # Set log level from config
    log_level = getattr(logging, Config.logging.level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(Config.logging.format)

    # Stream handler (console output)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # File handler (optional)
    if Config.logging.enable_file_logging:
        # Use provided log_file or default from config
        if log_file is None:
            log_file = Config.logging.log_dir / f"{name.replace('.', '_')}.log"

        # Ensure log directory exists
        log_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except (IOError, OSError) as e:
            logger.warning(f"Failed to create file handler for {log_file}: {e}")

    # Prevent propagation to root logger (avoid duplicate logs)
    logger.propagate = False

    # Cache the logger
    _loggers[name] = logger

    return logger


def setup_root_logger() -> logging.Logger:
    """Setup the root logger for SEBEK.

    Call this once at application startup to initialize logging
    for all child loggers.

    Returns:
        logging.Logger: Root logger instance.
    """
    root_logger = logging.getLogger("sebek")
    log_level = getattr(logging, Config.logging.level.upper(), logging.INFO)
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers
    if not root_logger.handlers:
        formatter = logging.Formatter(Config.logging.format)

        # Stream handler
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        root_logger.addHandler(stream_handler)

        # File handler
        if Config.logging.enable_file_logging:
            log_file = Config.logging.log_dir / "sebek.log"
            log_file.parent.mkdir(parents=True, exist_ok=True)
            try:
                file_handler = logging.FileHandler(log_file, encoding="utf-8")
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)
            except (IOError, OSError) as e:
                stream_handler.emit(
                    logging.LogRecord(
                        "sebek",
                        logging.WARNING,
                        "",
                        0,
                        f"Failed to create file handler: {e}",
                        (),
                        None,
                    )
                )

    return root_logger


def disable_external_logging(modules: list[str]) -> None:
    """Suppress verbose logging from external libraries.

    Args:
        modules: List of module names to suppress (e.g., ["vosk", "chromadb"]).

    Example:
        >>> disable_external_logging(["vosk", "urllib3"])
    """
    for module in modules:
        logging.getLogger(module).setLevel(logging.WARNING)
