"""Configuration loading and merging (interface).

Responsibilities (Milestone 2):
    * read ``configs/config.yaml`` and resolve its ``includes:``;
    * deep-merge the composed YAML with precedence
      code-defaults < YAML < ``PLANTDX_*`` env vars < CLI overrides;
    * validate the result against :class:`plantdx.config.schema.PlantDxConfig`;
    * compute and attach the ``config_hash`` used in provenance (doc 00 §6).

Milestone 1 exposes the public signature only.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from plantdx.config.schema import PlantDxConfig


def load_config(
    path: str | Path = "configs/config.yaml",
    *,
    overrides: Mapping[str, Any] | None = None,
) -> PlantDxConfig:
    """Load, compose, validate, and return the merged configuration.

    Args:
        path: Path to the master ``config.yaml``.
        overrides: Optional highest-precedence overrides (e.g., from the CLI).

    Returns:
        A validated, frozen :class:`PlantDxConfig`.

    Raises:
        plantdx.core.exceptions.ConfigError: If a file is missing or invalid.
    """
    raise NotImplementedError("Milestone 2: configuration loading and merging")


def config_hash(config: PlantDxConfig) -> str:
    """Return a stable hash of the effective configuration (for provenance)."""
    raise NotImplementedError("Milestone 2: deterministic config hashing")
