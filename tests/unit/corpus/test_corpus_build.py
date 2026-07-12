"""Full corpus build: coverage, validity, and the severity-honesty invariant."""

from __future__ import annotations

import re
from typing import Any

import pytest

from plantdx.concepts.policies import STAGE_TOKENS
from plantdx.corpus.validator import validate_caption


@pytest.mark.unit
@pytest.mark.requires_dkb
def test_every_disease_has_captions(bundle: tuple[Any, Any, Any]) -> None:
    _, _, (corpus, report) = bundle
    assert report["status"] == "valid"
    assert len(corpus.captions) > 0
    diseases = {c.disease_id for c in corpus.captions}
    assert len(diseases) == 18


@pytest.mark.unit
@pytest.mark.requires_dkb
def test_every_caption_revalidates(bundle: tuple[Any, Any, Any]) -> None:
    models, library, (corpus, _report) = bundle
    by_model = {m.disease_id: m for m in models.disease_models}
    by_template = {t.id: t for t in library.templates}
    for c in corpus.captions:
        assert validate_caption(c, by_model[c.disease_id], by_template[c.template_id]) == []


@pytest.mark.unit
@pytest.mark.requires_dkb
def test_no_caption_asserts_a_severity_stage(bundle: tuple[Any, Any, Any]) -> None:
    _, _, (corpus, _report) = bundle
    for c in corpus.captions:
        low = c.text.lower()
        for token in STAGE_TOKENS:
            assert not re.search(rf"(?<!\w){re.escape(token)}(?!\w)", low), c.text


@pytest.mark.unit
@pytest.mark.requires_dkb
def test_no_exact_duplicate_captions(bundle: tuple[Any, Any, Any]) -> None:
    _, _, (corpus, _report) = bundle
    norms = [" ".join(c.text.lower().split()) for c in corpus.captions]
    assert len(norms) == len(set(norms))


@pytest.mark.unit
@pytest.mark.requires_dkb
def test_captions_start_capital_end_period(bundle: tuple[Any, Any, Any]) -> None:
    _, _, (corpus, _report) = bundle
    for c in corpus.captions:
        assert c.text[0].isupper()
        assert c.text[-1] in ".!?"


@pytest.mark.unit
@pytest.mark.requires_dkb
def test_condition_and_crop_filters(bundle: tuple[Any, Any, Any]) -> None:
    models, library, _ = bundle
    from plantdx.corpus import build_corpus

    one, _ = build_corpus(models, library, condition="tomato_early_blight")
    assert {c.disease_id for c in one.captions} == {"tomato_early_blight"}
    mango, _ = build_corpus(models, library, crop="mango")
    assert {c.crop for c in mango.captions} == {"mango"}
