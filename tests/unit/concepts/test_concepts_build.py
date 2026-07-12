"""Build-side tests for the Caption Concept Model (component A)."""

from __future__ import annotations

from typing import Any

import pytest

from plantdx.concepts import policies


def _by_id(models: Any) -> dict[str, Any]:
    return {m.disease_id: m for m in models.disease_models}


@pytest.mark.unit
@pytest.mark.requires_dkb
def test_one_model_per_disease(pipeline: tuple[Any, Any, Any]) -> None:
    _, _, models = pipeline
    assert len(models.disease_models) == 18
    assert len({m.disease_id for m in models.disease_models}) == 18


@pytest.mark.unit
@pytest.mark.requires_dkb
def test_healthy_forbids_all_disease_signs(pipeline: tuple[Any, Any, Any]) -> None:
    _, _, models = pipeline
    for m in models.disease_models:
        if m.condition_type == "HealthyState":
            assert "healthy_state" in m.mandatory
            assert "primary_sign" not in m.mandatory + m.optional
            assert "primary_sign" in m.forbidden


@pytest.mark.unit
@pytest.mark.requires_dkb
def test_disease_requires_primary_sign(pipeline: tuple[Any, Any, Any]) -> None:
    _, _, models = pipeline
    for m in models.disease_models:
        if m.condition_type != "HealthyState":
            assert "primary_sign" in m.mandatory
            assert "healthy_state" in m.forbidden


@pytest.mark.unit
@pytest.mark.requires_dkb
def test_quality_concepts_only_for_modifiable_signs(pipeline: tuple[Any, Any, Any]) -> None:
    _, _, models = pipeline
    for m in models.disease_models:
        offered = set(m.mandatory) | set(m.optional)
        if m.sign_type not in policies.MODIFIABLE_SIGN_TYPES:
            assert not (policies.MODIFIER_CONCEPTS & offered), m.disease_id


@pytest.mark.unit
@pytest.mark.requires_dkb
def test_agent_name_uses_scientific_name(pipeline: tuple[Any, Any, Any]) -> None:
    _, _, models = pipeline
    eb = _by_id(models)["tomato_early_blight"]
    agent = next(c for c in eb.concepts if c.concept_id == "agent_reference")
    assert agent.realizations == ("Alternaria solani",)
    assert agent.observable is False


@pytest.mark.unit
@pytest.mark.requires_dkb
def test_never_appear_includes_stage_tokens(pipeline: tuple[Any, Any, Any]) -> None:
    _, _, models = pipeline
    for m in models.disease_models:
        for token in policies.STAGE_TOKENS:
            assert token in m.never_appear


@pytest.mark.unit
@pytest.mark.requires_dkb
def test_negated_dkb_phrases_are_dropped(pipeline: tuple[Any, Any, Any]) -> None:
    """ "none (superficial ...)" must not become a realization (sooty mould necrosis)."""
    _, _, models = pipeline
    sm = _by_id(models)["mango_sooty_mould"]
    necrosis = next((c for c in sm.concepts if c.concept_id == "necrosis"), None)
    # necrosis is DKB-"none" for sooty mould -> not emitted as an available concept.
    assert necrosis is None or necrosis.status == policies.STATUS_FORBIDDEN


@pytest.mark.unit
@pytest.mark.requires_dkb
def test_size_is_always_forbidden(pipeline: tuple[Any, Any, Any]) -> None:
    _, _, models = pipeline
    for m in models.disease_models:
        assert "lesion_size" in m.forbidden
        assert "management" in m.forbidden
        assert "severity_stage" in m.forbidden


@pytest.mark.unit
@pytest.mark.requires_dkb
def test_evidence_present_for_scientific_concepts(pipeline: tuple[Any, Any, Any]) -> None:
    _, _, models = pipeline
    eb = _by_id(models)["tomato_early_blight"]
    primary = next(c for c in eb.concepts if c.concept_id == "primary_sign")
    assert primary.evidence  # traceable to cited sources
