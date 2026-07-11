"""Contract tests: Milestone-1 stubs raise NotImplementedError, not silent no-ops."""

from __future__ import annotations

import pytest

from plantdx.config.loader import load_config
from plantdx.knowledge_base.loader import DKBLoader
from plantdx.utils.hashing import sha256_hex


@pytest.mark.unit
def test_config_loader_stub() -> None:
    with pytest.raises(NotImplementedError):
        load_config("configs/config.yaml")


@pytest.mark.unit
def test_dkb_loader_stub() -> None:
    with pytest.raises(NotImplementedError):
        DKBLoader("knowledge_base/dkb.json").load()


@pytest.mark.unit
def test_hashing_stub() -> None:
    with pytest.raises(NotImplementedError):
        sha256_hex("a", "b")
