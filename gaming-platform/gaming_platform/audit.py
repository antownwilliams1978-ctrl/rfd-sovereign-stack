"""Structured audit logging helpers."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from gaming_platform.models import SpinResult


def build_logger(name: str, log_path: Path | None = None) -> logging.Logger:
    """Create a logger without mutating global logging state."""

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(stream_handler)

    if log_path is not None:
        resolved_path = log_path.resolve()
        if not any(
            isinstance(handler, logging.FileHandler)
            and Path(handler.baseFilename).resolve() == resolved_path
            for handler in logger.handlers
        ):
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(resolved_path)
            file_handler.setFormatter(logging.Formatter("%(message)s"))
            logger.addHandler(file_handler)

    return logger


@dataclass(slots=True)
class AuditTrail:
    """Append-only structured audit trail."""

    logger: logging.Logger

    @classmethod
    def from_path(cls, log_path: Path | None = None) -> "AuditTrail":
        """Create an audit trail backed by an optional file."""

        return cls(logger=build_logger("gaming_platform.audit", log_path=log_path))

    def record_spin(self, result: SpinResult) -> None:
        """Record a completed spin."""

        self.logger.info(json.dumps(result.to_audit_payload(), sort_keys=True))
