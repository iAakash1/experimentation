"""Hashing helpers (interface).

Centralizes the SHA-256 based hashing used for seeds, config hashes, DKB pinning,
and caption ids so the whole pipeline shares one canonical hashing convention
(doc 00 §6). Implemented in Milestone 2.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def sha256_hex(*parts: str | bytes | int) -> str:
    """Return the SHA-256 hex digest of the concatenated, canonicalized parts."""
    raise NotImplementedError("Milestone 2: canonical SHA-256 hashing")


def stable_json_hash(obj: Mapping[str, Any]) -> str:
    """Return a stable hash of a JSON-serializable mapping (sorted keys)."""
    raise NotImplementedError("Milestone 2: stable JSON hashing")
