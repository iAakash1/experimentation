"""Emitter — component (I) (doc 00 §2, doc 04 §1).

Assembles the canonical :class:`CaptionRecord` from a validated draft plus full
provenance, and appends it to the caption library JSONL. Also mirrors the
provenance to ``artifacts/generation/provenance/`` for audit/regeneration.
"""

from __future__ import annotations

from pathlib import Path

from plantdx.core.types import (
    CaptionRecord,
    DiseaseLabel,
    ImageRef,
    Instruction,
    Provenance,
    Response,
    SelectedConcepts,
)
from plantdx.generation.models import CaptionDraft


class Emitter:
    """Builds and persists canonical caption records.

    Args:
        library_path: Path to ``caption_library.jsonl``.
        provenance_dir: Directory for mirrored provenance records.
    """

    def __init__(self, library_path: str | Path, provenance_dir: str | Path) -> None:
        self.library_path = Path(library_path)
        self.provenance_dir = Path(provenance_dir)

    def build(
        self,
        image: ImageRef,
        label: DiseaseLabel,
        draft: CaptionDraft,
        instruction: Instruction,
        response: Response,
        concepts: SelectedConcepts,
        provenance: Provenance,
    ) -> CaptionRecord:
        """Assemble a canonical record (does not write it)."""
        raise NotImplementedError("Milestone 4: record assembly")

    def emit(self, record: CaptionRecord) -> None:
        """Append a record to the library and mirror its provenance."""
        raise NotImplementedError("Milestone 4: record emission")
