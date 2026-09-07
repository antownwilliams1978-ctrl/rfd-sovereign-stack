"""Tests for SEBEK logging utilities."""

import logging
import pytest
from pathlib import Path
from sebek.utils.logging import get_logger, setup_root_logger, disable_external_logging


class TestGetLogger:
    """Test logger retrieval and configuration."""

    def test_get_logger_returns_logger(self):
        """Test get_logger returns a Logger instance."""
        logger = get_logger("test.module")
        assert isinstance(logger, logging.Logger)

    def test_get_logger_caches_loggers(self):
        """Test loggers are cached."""
        logger1 = get_logger("test.cached")
        logger2 = get_logger("test.cached")
        assert logger1 is logger2

    def test_get_logger_with_custom_file(self, temp_dir):
        """Test get_logger with custom log file."""
        log_file = temp_dir / "test.log"
        logger = get_logger("test.file", log_file=log_file)

        logger.info("Test message")

        # Check file was created and contains message
        assert log_file.exists()
        content = log_file.read_text()
        assert "Test message" in content

    def test_logger_has_handlers(self):
        """Test logger has at least stream handler."""
        logger = get_logger("test.handlers")
        assert len(logger.handlers) > 0


class TestSetupRootLogger:
    """Test root logger setup."""

    def test_setup_root_logger_returns_logger(self):
        """Test setup_root_logger returns a Logger."""
        logger = setup_root_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "sebek"


class TestDisableExternalLogging:
    """Test external logging suppression."""

    def test_disable_external_logging_sets_level(self):
        """Test disable_external_logging sets WARNING level."""
        test_logger = logging.getLogger("external.lib")
        test_logger.setLevel(logging.DEBUG)

        disable_external_logging(["external.lib"])

        assert test_logger.level == logging.WARNING

    def test_disable_multiple_modules(self):
        """Test disabling multiple external modules."""
        modules = ["module1", "module2", "module3"]
        disable_external_logging(modules)

        for module in modules:
            logger = logging.getLogger(module)
            assert logger.level == logging.WARNING


class TestLoggerUsage:
    """Test actual logger usage patterns."""

    def test_logger_info_level(self, caplog):
        """Test INFO level logging."""
        logger = get_logger("test.info")

        logger.info("Test info message")

    def test_logger_error_level(self, caplog):
        """Test ERROR level logging."""
        logger = get_logger("test.error")

        logger.error("Test error message")

    def test_logger_warning_level(self, caplog):
        """Test WARNING level logging."""
        logger = get_logger("test.warning")

        logger.warning("Test warning message")
