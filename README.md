<div align="center">

# 🌿 PlantDx

**A knowledge-grounded framework for constructing instruction-tuning datasets for agricultural Vision–Language Models.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![Code style: ruff](https://img.shields.io/badge/lint-ruff-black.svg)](.pre-commit-config.yaml)
[![Types: mypy](https://img.shields.io/badge/types-mypy-blue.svg)](pyproject.toml)
[![Status: M2b](https://img.shields.io/badge/status-milestone--2b-orange.svg)](docs/ROADMAP.md)

</div>

> **Repository status — Milestone 2b.**
> The dataset audit, dataset normalization, domain ontology compiler, and vocabulary +
> symptom lexicon compiler are implemented (CPU-only, deterministic). The caption
> generation pipeline (concept selection, templates, validation, dataset building,
> training, evaluation) is defined as **typed interfaces only** and is implemented in
> later milestones. See the [Roadmap](#roadmap).

---

## Project Overview

PlantDx builds **scientifically grounded** instruction-tuning datasets for fine-tuning open-weight Vision–Language Models (VLMs) to describe and identify diseases in **tomato** and **mango** leaves. Every caption is generated from a curated, cited **Disease Knowledge Base (DKB)** and a controlled vocabulary — **never** from a VLM/LLM prediction and **never** from image analysis. The dataset labels (PlantVillage, MangoLeafBD) are the only ground truth used.

The framework is a reproducible pipeline:

```
Disease Knowledge Base  →  Caption Ontology  →  Caption Generation Engine
        →  Validation Engine  →  Instruction Dataset Builder
        →  QLoRA Fine-tuning  →  Evaluation
```

The complete research design lives in [`caption_framework/`](caption_framework/) (Stage 2 specification) and [`knowledge_base/`](knowledge_base/) (Stage 1, the DKB). **These specifications are the source of truth**; this repository implements them exactly.

## Research Motivation

General-purpose open-weight VLMs are unreliable at zero-shot crop-disease diagnosis (confirmed by our own benchmark). Distilling captions from such models would encode their errors into the fine-tuned students — a circular failure mode. PlantDx removes models from the caption path entirely:

- **Knowledge-grounded** — every claim traces to an authoritative source (APS, UC IPM, UF/IFAS, CABI, peer-reviewed literature) recorded in the DKB.
- **Hallucination-resistant by construction** — a closed vocabulary plus a 12-stage validator make out-of-knowledge claims structurally impossible.
- **Observability-honest** — captions describe only what is visible in a single-leaf image; fruit/twig/whole-tree/yield features are documented but forbidden in captions.
- **Reproducible** — fully seeded, provenance-tracked, bit-for-bit regenerable.

Full argument: [`caption_framework/07_ieee_methodology_section.md`](caption_framework/07_ieee_methodology_section.md).

## Architecture Diagram

> This diagram shows the caption-generation pipeline (`caption_framework/`, still future work).
> It is preceded in practice by four already-implemented, independent CPU-only stages —
> `plantdx audit` → `plantdx normalize` → `plantdx ontology` (the **domain** ontology compiler,
> `ontology_design/`) → `plantdx vocabulary` (the vocabulary + symptom lexicon compiler, a
> deterministic projection of that graph) — which inventory the raw datasets, produce the
> canonical normalized datasets, compile the DKB into a typed knowledge graph, and derive a
> controlled vocabulary + bounded symptom lexicon from it. The "Ontology Builder (A)" below is
> the *caption-concept* model, a separate, not-yet-implemented downstream view over that graph;
> "Vocabulary Builder (B)" and "Symptom Lexicon (C)" below are already implemented against the
> domain ontology directly (`plantdx.vocabulary.domain`), per `ontology_design/01_architecture.md`
> §1.5's "re-founded, not redesigned" principle.

```
                ┌──────────────────────────────────────────────┐
                │  Disease Knowledge Base (Stage 1, FINAL)      │
                │  knowledge_base/dkb.json  (single source of   │
                │  truth: 18 classes × 46 fields, cited)        │
                └───────────────────────┬──────────────────────┘
                     build-time, deterministic derivation
        ┌───────────────────────────────┼───────────────────────────────┐
        ▼                               ▼                               ▼
 ┌───────────────┐             ┌───────────────┐             ┌───────────────┐
 │ Ontology      │             │ Vocabulary    │             │ Symptom       │
 │ Builder (A)   │             │ Builder (B)   │             │ Lexicon (C)   │
 └───────┬───────┘             └───────┬───────┘             └───────┬───────┘
         └─────────────────────────────┼─────────────────────────────┘
                                       ▼
   label (folder GT) ─►  Concept Selector (D) ─► Template Library (E)
                                       ▼
                         Slot Realizer + Vocabulary Expander (F)
                                       ▼
                         Validator Battery (G, 12 stages) ──fail──► regenerate
                                       ▼ pass
                         De-duplicator + Diversity Controller (H)
                                       ▼
                         Emitter (I) ─► caption_library.jsonl
                                       ▼
             per-model Converters ─► QLoRA (MLX) ─► Evaluation
```

## Pipeline Diagram

```
 stage          module (src/plantdx/…)         input → output
 ───────────────────────────────────────────────────────────────────────
 knowledge base knowledge_base/                dkb.json (read-only)
 ontology       ontology/builder.py            dkb.json → caption_ontology.json
 vocabulary     vocabulary/builder.py,lexicon  dkb.json → vocab axes + lexicons
 generation     generation/engine.py           label + ontology → caption drafts
 validation     validation/battery.py          draft → accept | regenerate
 diversity      diversity/controller.py         accepted → dedup + balanced corpus
 dataset        dataset/emitter.py,splits.py    corpus → caption_library.jsonl + splits
 converters     dataset/converters.py           canonical → per-model train files
 training       training/qlora.py,mlx_runner    train files → QLoRA adapters (MLX)
 evaluation     evaluation/*                    adapters → zero-shot vs fine-tuned report
```

## Repository Layout

```
experiments/                      # repository root
├── src/plantdx/                  # the Python package
│   ├── config/                   #   typed config schema + YAML loader                    [implemented]
│   ├── core/                     #   shared types, enums, seeding, exceptions             [implemented]
│   ├── audit/                    #   Dataset Audit Engine (`plantdx audit`)                [implemented]
│   ├── normalization/            #   Dataset Normalization Engine (`plantdx normalize`)    [implemented]
│   ├── knowledge_base/           #   DKB loader + record models (Stage 1 consumer)         [stub]
│   ├── ontology/                 #   caption-concept model (OntologyBuilder, component A)  [stub]
│   │   └── domain/               #   Domain Ontology Compiler (`plantdx ontology`)         [implemented]
│   ├── vocabulary/               #   VocabularyExpander (F, caption-concept view)          [stub]
│   │   └── domain/               #   Vocabulary + Symptom Lexicon Compiler (`plantdx vocabulary`) [implemented]
│   ├── generation/                #   ConceptSelector (D), Templates (E), Realizer (F), Engine [stub]
│   ├── validation/               #   12-stage ValidatorBattery (G)                        [stub]
│   ├── diversity/                #   Deduplicator + DiversityController (H) + metrics      [stub]
│   ├── dataset/                  #   Emitter (I), serialization, splits, converters        [stub]
│   ├── qa/                       #   sampling, review, acceptance                          [stub]
│   ├── training/                 #   QLoRA / mlx-vlm runners                               [stub]
│   ├── evaluation/               #   zero-shot vs fine-tuned metrics                       [stub]
│   └── utils/                    #   io, hashing, logging, versioning                      [implemented]
├── configs/                      # config.yaml, paths.yaml, audit/normalization/generation/validation/training.yaml
├── assets/                       # AUTHORED inputs (templates, static vocab, label_map, overrides)
├── artifacts/                    # GENERATED outputs (gitignored) — includes artifacts/ontology/, artifacts/vocabulary/
├── datasets/                     # GENERATED, normalized canonical datasets (gitignored)
├── tests/                        # unit / integration / benchmark
├── docs/                         # developer documentation (AUDIT.md, NORMALIZATION.md, ONTOLOGY.md, ...)
├── scripts/                      # thin CLI wrappers
├── knowledge_base/                # Stage 1 — the DKB (FINAL)
├── caption_framework/             # Stage 2 — the caption framework design specification (FINAL)
├── ontology_design/               # Stage 3 — the domain ontology design specification (FINAL)
├── tomato/raw/PlantVillage/      # raw dataset, immutable (existing)
└── mango/raw/MangoLeafBD/        # raw dataset, immutable (existing)
```

> The `artifacts/` tree mirrors the **final** artifact layout in [`caption_framework/06_folder_structure_spec.md`](caption_framework/06_folder_structure_spec.md); `configs/paths.yaml` is the single mapping layer. See [`docs/REPO_LAYOUT.md`](docs/REPO_LAYOUT.md) for the spec↔repo correspondence.

## Installation

Requires **Python 3.10+** and (for training) **Apple Silicon** with MLX.

```bash
git clone git@github.com:iAakash1/experimentation.git
cd experimentation

python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"          # editable install + dev tooling
pre-commit install               # enable lint/format/type hooks
```

Training extras (Apple Silicon only):

```bash
pip install -e ".[train]"        # mlx, mlx-vlm
```

## Quick Start

> ⚠️ `audit`, `normalize`, `ontology`, and `vocabulary` are implemented (CPU-only, deterministic).
> Later-stage commands still raise `NotImplementedError` until their milestone lands.

```bash
plantdx --help                                           # top-level CLI
plantdx audit             --config configs/config.yaml   # implemented — dataset audit
plantdx normalize         --config configs/config.yaml   # implemented — dataset normalization
plantdx ontology          --config configs/config.yaml   # implemented — domain ontology compiler
plantdx vocabulary        --config configs/config.yaml   # implemented — vocabulary + symptom lexicon compiler
plantdx generate          --config configs/config.yaml   # Milestone 3
plantdx validate          --config configs/config.yaml   # Milestone 3
plantdx dataset build     --config configs/config.yaml   # Milestone 4
plantdx dataset convert   --model qwen3_vl                # Milestone 4
plantdx train             --model qwen3_vl                # Milestone 5
plantdx evaluate          --model qwen3_vl                # Milestone 6
```

Programmatic surface (implemented stages):

```python
from plantdx.config import load_config
from plantdx.ontology.domain import compile_ontology, validate_ontology
from plantdx.vocabulary.domain import build_vocabulary_result, validate_vocabulary_result

cfg = load_config("configs/config.yaml")
result = compile_ontology(cfg.paths.knowledge_base["dkb_json"])
validate_ontology(result)   # fail-closed; raises OntologyValidationError on any rule breach

vocab = build_vocabulary_result(result.ontology)
validate_vocabulary_result(vocab, result.ontology)   # fail-closed; raises VocabularyValidationError
```

See [`docs/AUDIT.md`](docs/AUDIT.md), [`docs/NORMALIZATION.md`](docs/NORMALIZATION.md),
[`docs/ONTOLOGY.md`](docs/ONTOLOGY.md), and [`docs/VOCABULARY.md`](docs/VOCABULARY.md) for each
implemented stage's full usage.

## Datasets

| Crop | Raw dataset | Raw location | Note |
|------|-------------|---------------|------|
| Tomato | Full PlantVillage (all crops; `train/`+`val/` split) | `tomato/raw/PlantVillage/` | ~14k tomato images across 10 classes; the audit engine discovered the raw download is the complete multi-crop PlantVillage, not a pre-filtered tomato subset — see [`docs/AUDIT.md`](docs/AUDIT.md). |
| Mango | MangoLeafBD (flat layout) | `mango/raw/MangoLeafBD/` | 4k images, 8 classes, 500/class. |

Raw datasets are **immutable** (never renamed, moved, or modified) and are treated as ground truth.
`plantdx normalize` extracts only the relevant classes, canonicalizes their names, and writes a
crop-independent structure to `datasets/<crop>/processed/<class>/` — see [`docs/NORMALIZATION.md`](docs/NORMALIZATION.md).
Downstream stages consume the **normalized** datasets, never `raw/` directly.

## Models

Target VLMs for QLoRA fine-tuning (via MLX / `mlx-vlm` on Apple M4 Pro, 24 GB). All five converters
(one per model, plus a generic `mlx_vlm` converter) live in a single module,
[`dataset/converters.py`](src/plantdx/dataset/converters.py), behind a `CONVERTER_REGISTRY`:

| Model | Params | Converter class |
|-------|--------|-----------|
| Qwen3-VL-8B-Instruct | 8B | `Qwen3VLConverter` |
| Qwen2.5-VL-7B-Instruct | 7B | `Qwen2_5VLConverter` |
| InternVL3-8B | 8B | `InternVL3Converter` |
| Gemma-3-12B | 12B | `Gemma3Converter` |

All four train on an **identical** canonical caption library and identical image-level splits (a precondition for fair comparison). Model-specific formatting is applied by pure converters at build time.

## Citation

```bibtex
@software{plantdx2026,
  title  = {PlantDx: A Knowledge-Grounded Framework for Instruction-Tuning
            Datasets for Agricultural Vision-Language Models},
  author = {PlantDx Contributors},
  year   = {2026},
  url    = {https://github.com/iAakash1/experimentation}
}
```

See [`CITATION.cff`](CITATION.cff) for machine-readable metadata.

## License

Released under the **Apache License 2.0** — see [`LICENSE`](LICENSE). Apache-2.0 is recommended for this project (permissive, patent grant, industry-standard for ML tooling). Dataset licenses (PlantVillage, MangoLeafBD) are retained by their original authors and are **not** redistributed here.

## Roadmap

| Milestone | Scope | Status |
|-----------|-------|--------|
| **M1** | Repository scaffolding: structure, configs, typed APIs, tests, docs | ✅ done |
| **M2** | Dataset Audit Engine (`plantdx audit`) | ✅ done |
| **M2.1** | Dataset Normalization Engine (`plantdx normalize`) | ✅ done |
| **M2.2** | Domain Ontology Compiler (`plantdx ontology`) | ✅ done |
| **M2b** | Vocabulary + Symptom Lexicon Compiler (`plantdx vocabulary`, a view over the ontology) | ✅ done |
| **M3** | Caption concept model (component A) + Caption Generation Engine + 12-stage Validation Engine | ⏳ next |
| **M4** | Instruction Dataset Builder + splits + per-model converters | ⏳ |
| **M5** | QLoRA fine-tuning (MLX) for all four models | ⏳ |
| **M6** | Evaluation: zero-shot vs fine-tuned; diagnostic confusable-pair split | ⏳ |

Detailed plan: [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Future Work

- Optional per-image **severity annotation** to unlock the (currently gated) severity-conditioned caption mode.
- Additional crops/diseases by extending the DKB (the single source of truth) and rebuilding the ontology.
- Human-preference alignment on top of the instruction-tuned checkpoints.
- Public release of the generated caption library and dataset card.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and the [developer guide](docs/DEVELOPMENT.md). All contributions must preserve the seven design invariants in [`caption_framework/README.md`](caption_framework/README.md).
