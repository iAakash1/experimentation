"""Sentence Planner (component D->F, structural).

Consumes a disease :class:`ConceptModel`, a :class:`Template`, and a chosen
concept subset; produces a :class:`SentencePlan` — the ordered, still-structural
filling of the template's slots with controlled realizations. It does NOT emit
English (that is the Caption Generator's job). Every realization is chosen
deterministically from the concept model's controlled phrase set; nothing is
invented. Required slots must be fillable (the corpus builder guarantees this via
template compatibility); an unfillable required slot is a hard error.
"""

from __future__ import annotations

from plantdx.concepts.models import CaptionConcept, ConceptModel
from plantdx.corpus.models import (
    PIECE_CONCEPT,
    PIECE_LIST,
    PIECE_LIT,
    PlanPiece,
    SentencePlan,
)
from plantdx.corpus.seeds import choice_index
from plantdx.templates.models import SEG_LIST, SEG_LIT, SEG_OPT, SEG_SLOT, Template


def plan_caption(
    model: ConceptModel, template: Template, selected: frozenset[str], variant: str
) -> SentencePlan:
    """Build one sentence plan for ``template`` filled with ``selected`` concepts.

    ``selected`` is the concept-id subset to realize (already includes every
    required slot). ``variant`` is a stable string that diversifies realization
    choices across captions of the same (disease, template).
    """
    concepts = {c.concept_id: c for c in model.concepts}
    pieces: list[PlanPiece] = []
    asserted: set[str] = set()

    for seg in template.segments:
        if seg.kind == SEG_LIT:
            pieces.append(PlanPiece(kind=PIECE_LIT, text=seg.text))
        elif seg.kind == SEG_SLOT:
            phrase = _realize(concepts[seg.concept], model, template, variant)
            pieces.append(PlanPiece(kind=PIECE_CONCEPT, concept=seg.concept, phrase=phrase))
            asserted.add(seg.concept)
        elif seg.kind == SEG_OPT:
            if seg.concept in selected:
                phrase = _realize(concepts[seg.concept], model, template, variant)
                pieces.append(
                    PlanPiece(
                        kind=PIECE_CONCEPT,
                        concept=seg.concept,
                        phrase=phrase,
                        glue=seg.glue,
                        suffix=seg.suffix,
                    )
                )
                asserted.add(seg.concept)
        elif seg.kind == SEG_LIST:
            items = tuple(
                (c, _realize(concepts[c], model, template, variant))
                for c in seg.concepts
                if c in selected
            )
            if items:
                pieces.append(PlanPiece(kind=PIECE_LIST, items=items, glue=seg.glue, conj=seg.conj))
                asserted.update(c for c, _ in items)

    return SentencePlan(
        disease_id=model.disease_id,
        template_id=template.id,
        family=template.family,
        register=template.register,
        hedged=template.hedged,
        asserted_concepts=tuple(sorted(asserted)),
        pieces=tuple(pieces),
    )


def _realize(concept: CaptionConcept, model: ConceptModel, template: Template, variant: str) -> str:
    """Deterministically pick one controlled realization for a concept."""
    options = concept.realizations
    if not options:
        raise ValueError(
            f"{model.disease_id}/{template.id}: concept {concept.concept_id} has no realization"
        )
    idx = choice_index(len(options), model.disease_id, template.id, concept.concept_id, variant)
    return options[idx]
