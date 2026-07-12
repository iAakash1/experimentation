# PlantDx — Project Context

A short orientation for collaborators and contributors. For the full,
exhaustive engineering history and rationale, see the (gitignored,
AI-assistant-local) `CLAUDE.md` — this document is the public,
always-current summary.

## What this project is

PlantDx builds **knowledge-grounded instruction-tuning datasets** for
fine-tuning open-weight Vision-Language Models (VLMs) to describe and
diagnose diseases in tomato and mango leaves. Every caption the pipeline will
eventually produce is required to trace back to a cited, peer-reviewed or
extension-service scientific source — never to an LLM's or VLM's own guess.
This is a direct response to an earlier finding: a zero-shot benchmark of
general-purpose VLMs on crop-disease diagnosis performed poorly, so no model
is ever used to *generate or judge* training captions in this pipeline.

The end goal is an IEEE paper demonstrating that this knowledge-grounded,
deterministic approach produces better instruction-tuning supervision than
rule-based templates alone, LLM-generated captions, or VLM-self-captioned
images — backed by a released, reproducible artifact (not just a claim).

## Architecture at a glance

```
Disease Knowledge Base (FINAL, cited)
        │
        ▼
Domain Ontology Compiler ──► typed knowledge graph (deterministic, content-hashed)
        │
        ▼
[ next: Vocabulary Builder → Template Builder → Caption Generation Engine →
  Validation → Instruction Dataset Builder → QLoRA Fine-tuning → Evaluation ]

Raw datasets ──► Dataset Audit Engine ──► Dataset Normalization Engine
                                            ──► canonical datasets/<crop>/processed/
```

Three independent, CPU-only pipeline stages are implemented today; everything
from the Vocabulary Builder onward is still a typed interface stub
(`raise NotImplementedError`), by design — see [Current Status](#current-status).

## Implemented today

| Stage | Command | What it does |
|-------|---------|---------------|
| **Dataset Audit Engine** | `plantdx audit` | Inventories the raw datasets: counts, class distribution, corrupt/duplicate detection, deterministic checksums. Read-only. |
| **Dataset Normalization Engine** | `plantdx normalize` | Extracts and canonicalizes tomato/mango classes from the raw datasets into `datasets/<crop>/processed/<class>/`. Raw datasets are never modified. |
| **Domain Ontology Compiler** | `plantdx ontology` | Compiles `knowledge_base/dkb.json` into a typed, evidence-linked knowledge graph. Fail-closed validation; deterministic, content-hashed output. |

All three are CPU-only, fully deterministic (byte-identical output from the
same inputs), and covered by CI (`ruff check`, `ruff format --check`,
`pytest`, `mypy` — all green).

## Not yet implemented

Everything downstream of the ontology compiler: the Vocabulary Builder, the
Symptom Lexicon Builder, the Caption Generation Engine, the 12-stage caption
Validation Engine, the Instruction Dataset Builder (splits + per-model
converters), QLoRA training, and evaluation. These exist today only as typed
package interfaces with `NotImplementedError` bodies — the public API shape
is fixed, the logic is not written. **The Vocabulary Builder is next.**

## Repository layout

```
src/plantdx/            the Python package (see table above for what's real vs. stubbed)
knowledge_base/          Stage 1 — the Disease Knowledge Base (FINAL; 18 diseases, cited)
caption_framework/       Stage 2 — the caption-generation design spec (FINAL; no code)
ontology_design/         Stage 3 — the domain-ontology design spec (FINAL; no code)
configs/                 all pipeline configuration (YAML)
tests/                   mirrors src/plantdx/
docs/                    developer docs, including AUDIT.md, NORMALIZATION.md, ONTOLOGY.md, KNOWN_ISSUES.md
artifacts/, datasets/    generated outputs (gitignored; regenerable from source + config)
tomato/raw/, mango/raw/  the two raw datasets (gitignored; immutable, never edited by the pipeline)
```

## Datasets

- **Tomato** — raw source is the *full* PlantVillage dataset (multi-crop,
  ~54k images, 38 classes) — normalization extracts the 10 tomato-relevant
  classes and canonicalizes their names.
- **Mango** — MangoLeafBD, 4,000 images, 8 classes, already flat/clean.

Both are treated as immutable ground truth; the pipeline never relabels or
infers from pixels. See `docs/AUDIT.md` and `docs/NORMALIZATION.md`.

## Disease Knowledge Base

`knowledge_base/dkb.json` — 18 hand-curated, cited disease records (10
tomato + 8 mango), each with 46 fields covering identity, causal agent,
symptoms, controlled vocabularies, and references resolving into a shared
`reference_registry`. This file is the **single source of scientific truth**
for the entire project — every downstream fact must trace back to it.

## Core design principles

1. **Deterministic** — every stage is a pure function of its declared
   inputs; no wall-clock, no unseeded randomness.
2. **No hallucination by construction** — a caption can only ever assert
   what's structurally licensed by the ontology (observable, evidenced,
   within the closed vocabulary) — not filtered after the fact, made
   impossible up front.
3. **Observability-honest** — both datasets are single-leaf images; the
   system can never claim a symptom that wouldn't be visible in one (no
   fruit/twig/whole-plant claims), enforced as a structural graph property.
4. **Severity-honest** — no per-image severity claims, since no such label
   exists in the source data (only class-level severity knowledge is
   retained).
5. **DKB-first, ontology-first, vocabulary-first, template-first** — a
   strict layering where scientific fact (DKB) → formal knowledge (ontology)
   → controlled language (vocabulary) → sentence structure (templates) are
   kept separate and each is independently reviewable.

## CI

```bash
ruff check .            # lint
ruff format --check .   # formatting
pytest                  # tests (unit / integration / benchmark markers)
mypy                    # strict type checking
```
All four are green as of the latest commit. GitHub Actions
(`.github/workflows/ci.yml`) runs this matrix across Python 3.10–3.12 on
every push/PR to `main`.

## Getting started

```bash
git clone git@github.com:iAakash1/experimentation.git && cd experimentation
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install

plantdx audit                    # inventory the raw datasets
plantdx normalize --dataset mango  # build the canonical normalized mango dataset
plantdx ontology                  # compile the DKB into the knowledge graph
```

See `docs/AUDIT.md`, `docs/NORMALIZATION.md`, and `docs/ONTOLOGY.md` for full
usage of each implemented stage, and `docs/ROADMAP.md` for the complete
milestone plan.

## Known issues

See [`docs/KNOWN_ISSUES.md`](docs/KNOWN_ISSUES.md) — currently one deferred
issue: re-running `plantdx normalize` on an already-normalized dataset causes
its manifest/report to show 0 images (the actual normalized files are
unaffected; only that report is stale until the crop's `processed/` output
is cleared and rebuilt). Not dangerous, understood, deliberately deferred
rather than fixed as part of an unrelated CI-stabilization pass.

## Contributing

See `CONTRIBUTING.md` and `docs/DEVELOPMENT.md`. The short version: the DKB
and both design specifications (`caption_framework/`, `ontology_design/`) are
**FINAL** — implementation must follow them exactly, not redesign them. Every
change should preserve determinism, reproducibility, and the observability/
severity-honesty invariants described above. When in doubt, ask before
deviating from a written spec.
