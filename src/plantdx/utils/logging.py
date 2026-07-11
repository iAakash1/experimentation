"""Structured logging setup (interface).

Configures a ``rich`` console handler and an optional JSONL file handler from the
logging config. Implemented in Milestone 2.
"""

from __future__ import annotations

import logging


def configure_logging(level: str = "INFO", *, rich: bool = True, json_file: str | None = None) -> None:
    """Configure the root ``plantdx`` logger."""
    raise NotImplementedError("Milestone 2: logging configuration")


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced child logger under ``plantdx``."""
    raise NotImplementedError("Milestone 2: logger factory")
