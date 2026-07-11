"""I/O helpers (interface): JSON / JSONL / YAML read-write.

Thin, typed wrappers so the pipeline reads and writes artifacts consistently
(UTF-8, newline-delimited JSONL, atomic writes). Implemented in Milestone 2.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from pathlib import Path
from typing import Any


def read_json(path: str | Path) -> Any:
    """Read a JSON file."""
    raise NotImplementedError("Milestone 2: JSON read")


def write_json(path: str | Path, obj: Any) -> None:
    """Write a JSON file atomically."""
    raise NotImplementedError("Milestone 2: JSON write")


def read_jsonl(path: str | Path) -> Iterator[dict[str, Any]]:
    """Iterate records from a JSONL file."""
    raise NotImplementedError("Milestone 2: JSONL read")


def append_jsonl(path: str | Path, record: Mapping[str, Any]) -> None:
    """Append one record to a JSONL file."""
    raise NotImplementedError("Milestone 2: JSONL append")


def write_jsonl(path: str | Path, records: Iterable[Mapping[str, Any]]) -> None:
    """Write many records to a JSONL file atomically."""
    raise NotImplementedError("Milestone 2: JSONL write")


def read_yaml(path: str | Path) -> Any:
    """Read a YAML file."""
    raise NotImplementedError("Milestone 2: YAML read")
