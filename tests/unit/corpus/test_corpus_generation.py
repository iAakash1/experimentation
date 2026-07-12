"""Planner + generator: realization, normalization, and slot-deletion grammar."""

from __future__ import annotations

import pytest

from plantdx.corpus.generator import _normalize, _oxford, generate
from plantdx.corpus.models import PIECE_CONCEPT, PIECE_LIT, PlanPiece, SentencePlan


def _plan(*pieces: PlanPiece) -> SentencePlan:
    return SentencePlan(
        disease_id="d",
        template_id="T",
        family="short",
        register="visual",
        hedged=False,
        asserted_concepts=(),
        pieces=pieces,
    )


@pytest.mark.unit
def test_normalize_fixes_spacing_and_terminal() -> None:
    assert _normalize("this  leaf ,  ok") == "This leaf, ok."


@pytest.mark.unit
def test_normalize_article_agreement() -> None:
    assert _normalize("a apple on a leaf") == "An apple on a leaf."


@pytest.mark.unit
def test_normalize_protects_genus_abbreviation() -> None:
    text = _normalize("caused by Capnodium spp. and C. mangiferae on the leaf")
    # A genus-abbreviation period must not trigger sentence capitalization.
    assert "C. mangiferae" in text
    assert "C. Mangiferae" not in text


@pytest.mark.unit
def test_normalize_capitalizes_true_sentence_start() -> None:
    assert _normalize("the leaf shows spots. lesions can be seen") == (
        "The leaf shows spots. Lesions can be seen."
    )


@pytest.mark.unit
def test_oxford_list() -> None:
    assert _oxford(["a"], "and") == "a"
    assert _oxford(["a", "b"], "and") == "a and b"
    assert _oxford(["a", "b", "c"], "and") == "a, b, and c"


@pytest.mark.unit
def test_optional_slot_deletion_stays_grammatical() -> None:
    # An optional piece that is absent leaves no dangling glue/punctuation.
    plan = _plan(
        PlanPiece(kind=PIECE_LIT, text="Lesions"),
        PlanPiece(kind=PIECE_LIT, text=" can be seen"),
        PlanPiece(kind=PIECE_LIT, text="."),
    )
    assert generate(plan) == "Lesions can be seen."


@pytest.mark.unit
def test_concept_piece_glue_and_suffix() -> None:
    plan = _plan(
        PlanPiece(kind=PIECE_LIT, text="early blight"),
        PlanPiece(
            kind=PIECE_CONCEPT, concept="agent_reference", phrase="A. solani", glue=" (", suffix=")"
        ),
        PlanPiece(kind=PIECE_LIT, text="."),
    )
    assert generate(plan) == "Early blight (A. solani)."
