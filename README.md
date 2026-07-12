<div align="center">

# 🌿 PlantDx

**A knowledge-grounded framework for constructing instruction-tuning datasets for agricultural Vision–Language Models.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![Code style: ruff](https://img.shields.io/badge/lint-ruff-black.svg)](.pre-commit-config.yaml)
[![Types: mypy](https://img.shields.io/badge/types-mypy-blue.svg)](pyproject.toml)
[![Status: scaffolding](https://img.shields.io/badge/status-milestone--1%20scaffold-orange.svg)](docs/ROADMAP.md)

</div>

> **Repository status — Milestone 1 (scaffolding).**
> This repository currently contains the full production structure, configuration, typed public APIs, and documentation. The pipeline stages (caption generation, validation, dataset building, training, evaluation) are defined as **typed interfaces only** and are implemented in later milestones. See the [Roadmap](#roadmap).

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
 converters     dataset/converters/*            canonical → per-model train files
 training       training/qlora.py,mlx_runner    train files → QLoRA adapters (MLX)
 evaluation     evaluation/*                    adapters → zero-shot vs fine-tuned report
```

## Repository Layout

```
experiments/                      # repository root
├── src/plantdx/                  # the Python package (typed interfaces; impl in later milestones)
│   ├── config/                   #   typed config schema + YAML loader
│   ├── core/                     #   shared types, enums, seeding, interfaces, exceptions
│   ├── knowledge_base/           #   DKB loader + record models (Stage 1 consumer)
│   ├── ontology/                 #   OntologyBuilder (component A) + models
│   ├── vocabulary/               #   VocabularyBuilder (B), SymptomLexicon (C), Expander (F)
│   ├── generation/               #   ConceptSelector (D), Templates (E), Realizer (F), Engine
│   ├── validation/               #   12-stage ValidatorBattery (G)
│   ├── diversity/                #   Deduplicator + DiversityController (H) + metrics
│   ├── dataset/                  #   Emitter (I), serialization, splits, converters
│   ├── qa/                       #   sampling, review, acceptance
│   ├── training/                 #   QLoRA / mlx-vlm runners
│   ├── evaluation/               #   zero-shot vs fine-tuned metrics
│   └── utils/                    #   io, hashing, logging, versioning
├── configs/                      # config.yaml, paths.yaml, generation/validation/training.yaml
├── assets/                       # AUTHORED inputs (templates, static vocab, label_map, overrides)
├── artifacts/                    # GENERATED outputs (gitignored) — maps to spec doc 06 tree
├── tests/                        # unit / integration / benchmark
├── docs/                         # developer + design documentation
├── scripts/                      # thin CLI wrappers
├── knowledge_base/               # Stage 1 — the DKB (FINAL)
├── caption_framework/            # Stage 2 — the design specification (FINAL)
├── tomato/raw/PlantVillage/      # dataset (existing)
└── mango/raw/MangoLeafBD/        # dataset (existing)
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

> ⚠️ Milestone 1 exposes the CLI surface and typed APIs; stage commands raise `NotImplementedError` until their milestone lands.

```bash
plantdx --help                                   # top-level CLI
plantdx ontology         --config configs/config.yaml   # domain ontology (implemented)
plantdx generate         --config configs/config.yaml   # Milestone 3
plantdx validate         --config configs/config.yaml   # Milestone 3
plantdx dataset build    --config configs/config.yaml   # Milestone 4
plantdx dataset convert  --model qwen3_vl               # Milestone 4
plantdx train            --model qwen3_vl               # Milestone 5
plantdx evaluate         --model qwen3_vl               # Milestone 6
```

Programmatic surface:

```python
from plantdx.config import load_config
from plantdx.ontology import OntologyBuilder

cfg = load_config("configs/config.yaml")
# builder = OntologyBuilder(cfg)          # implemented in Milestone 2
# ontology = builder.build()
```

## Datasets

| Crop | Dataset | Classes | Location | Note |
|------|---------|---------|----------|------|
| Tomato | PlantVillage (tomato subset) | 10 | `tomato/raw/PlantVillage/` | ~14k images |
| Mango | MangoLeafBD | 8 | `mango/raw/MangoLeafBD/` | 4k images, 500/class |

Datasets are **fixed** and are treated as ground truth. PlantDx never relabels or infers labels from pixels. Folder-name → `disease_id` mapping is authored in `assets/metadata/label_map.json` (see [`caption_framework/04_dataset_schema_spec.md`](caption_framework/04_dataset_schema_spec.md)).

## Models

Target VLMs for QLoRA fine-tuning (via MLX / `mlx-vlm` on Apple M4 Pro, 24 GB):

| Model | Params | Converter |
|-------|--------|-----------|
| Qwen3-VL-8B-Instruct | 8B | `dataset/converters/qwen3_vl.py` |
| Qwen2.5-VL-7B-Instruct | 7B | `dataset/converters/qwen2_5_vl.py` |
| InternVL3-8B | 8B | `dataset/converters/internvl3.py` |
| Gemma-3-12B | 12B | `dataset/converters/gemma3.py` |

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
| **M1** | Repository scaffolding: structure, configs, typed APIs, tests, docs | ✅ this milestone |
| **M2** | Ontology + Vocabulary + Symptom-Lexicon builders (DKB → ontology) | ⏳ next |
| **M3** | Caption Generation Engine + 12-stage Validation Engine | ⏳ |
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
