"""Integration placeholders for the end-to-end pipeline.

These encode the intended behaviour of the assembled pipeline and are skipped
until the relevant milestone implements the components. Keeping them here makes
the acceptance criteria explicit and version-controlled.
"""

from __future__ import annotations

import pytest


@pytest.mark.integration
@pytest.mark.skip(reason="Milestone 2: DKB -> ontology derivation")
def test_ontology_is_pure_projection_of_dkb() -> None:
    """Every ontology vocab value must trace to a DKB field (invariant #2)."""


@pytest.mark.integration
@pytest.mark.skip(reason="Milestone 3: generation + validation")
def test_generation_never_emits_forbidden_terms() -> None:
    """No accepted caption contains a term from its disease `never_appear` set."""


@pytest.mark.integration
@pytest.mark.skip(reason="Milestone 3: reproducibility")
def test_generation_is_bit_for_bit_reproducible() -> None:
    """Same seed + config + DKB => identical caption library (doc 00 §6)."""


@pytest.mark.integration
@pytest.mark.skip(reason="Milestone 4: splits")
def test_splits_are_grouped_by_image() -> None:
    """All captions of an image share one split (no caption-level leakage)."""


@pytest.mark.integration
@pytest.mark.skip(reason="Milestone 4: converters")
def test_all_converters_preserve_response_text() -> None:
    """Converters change serialization only, never the caption/instruction text."""
