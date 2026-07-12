"""Deterministic caption-corpus statistics (``statistics.json``)."""

from __future__ import annotations

from typing import Any

from plantdx.corpus.models import Corpus


def _tokens(text: str) -> list[str]:
    return text.lower().split()


def compute(corpus: Corpus, validation_status: str) -> dict[str, Any]:
    """Return the statistics document (all values deterministic)."""
    captions = corpus.captions
    by_disease: dict[str, int] = {}
    by_family: dict[str, int] = {}
    by_register: dict[str, int] = {}
    by_confidence: dict[str, int] = {}
    unigrams: set[str] = set()
    total_tokens = 0
    hedged = 0
    for c in captions:
        by_disease[c.disease_id] = by_disease.get(c.disease_id, 0) + 1
        by_family[c.family] = by_family.get(c.family, 0) + 1
        by_register[c.register] = by_register.get(c.register, 0) + 1
        by_confidence[c.confidence] = by_confidence.get(c.confidence, 0) + 1
        hedged += int(c.hedged)
        toks = _tokens(c.text)
        total_tokens += len(toks)
        unigrams.update(toks)

    return {
        "content_hash": corpus.provenance.get("content_hash", ""),
        "validation_status": validation_status,
        "caption_count": len(captions),
        "disease_count": len(by_disease),
        "hedged_count": hedged,
        "total_tokens": total_tokens,
        "distinct_unigrams": len(unigrams),
        "distinct_1_ratio": round(len(unigrams) / total_tokens, 4) if total_tokens else 0.0,
        "mean_tokens_per_caption": round(total_tokens / len(captions), 2) if captions else 0.0,
        "by_disease": {k: by_disease[k] for k in sorted(by_disease)},
        "by_family": {k: by_family[k] for k in sorted(by_family)},
        "by_register": {k: by_register[k] for k in sorted(by_register)},
        "by_confidence": {k: by_confidence[k] for k in sorted(by_confidence)},
    }
