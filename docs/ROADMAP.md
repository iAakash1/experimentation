# Roadmap

Milestones and their acceptance criteria. Each milestone is a separate,
reviewable body of work; scope PRs to a single milestone.

## M1 — Repository scaffolding ✅ (this milestone)
- Production structure, packaging, tooling, configs, typed public APIs, tests, docs.
- **Acceptance:** `make check` green; every module imports; CLI surface parses;
  registries complete; stubs raise `NotImplementedError`. No pipeline logic.

## M2 — Dataset Audit Engine ✅ (implemented)
- CPU-only audit that inventories the configured datasets and writes a
  reproducibility report (`reports/`). See [AUDIT.md](AUDIT.md). Also implemented
  the M2-tagged infrastructure it depends on: config loader, `utils.io`,
  `utils.hashing`, `utils.logging`.
- **Acceptance:** `plantdx audit` runs on CPU and emits `dataset_card.md`,
  per-dataset summaries, CSVs, and a deterministic `audit_manifest.json`; unit
  tests cover discovery, corrupt handling, duplicates, checksum determinism, and
  report generation.

## M2.1 — Dataset Normalization Engine ✅ (implemented)
- CPU-only, filesystem-only. Copies the tomato + mango classes from the immutable
  raw datasets into `datasets/<crop>/processed/<canonical_class>/`, with a class
  map, manifest, dataset card, and combined run report. See [NORMALIZATION.md](NORMALIZATION.md).
- **Acceptance:** `plantdx normalize` extracts only mapped classes, normalizes names,
  merges train/val (preserving split in the manifest), verifies every copied file's
  checksum, and never modifies `raw/`. Unit tests cover layout detection, extraction,
  dedup/collision, checksum verification, and report generation.

## M2.2 — Domain Ontology Compiler ✅ (implemented)
- CPU-only, deterministic `Ontology = f(DKB, Policies)`. Compiles the DKB into a
  typed knowledge graph (`src/plantdx/ontology/domain/`) and writes six artifacts
  to `artifacts/ontology/`. Design: [`ontology_design/`](../ontology_design/); usage:
  [ONTOLOGY.md](ONTOLOGY.md). Distinct from the caption-concept model in
  `plantdx.ontology` (M2b below).
- **Acceptance:** `plantdx ontology` builds + validates (fail-closed) the 18-condition
  graph; repeated builds are byte-identical (content-hash pinned); unit tests cover
  hierarchy, graph generation, ordering, checksum, and every validation-failure mode.

## M2b — Caption concept model + Vocabulary + Symptom Lexicon (a view over the ontology)
- Implement `DKBLoader`, `OntologyBuilder` (A), `VocabularyBuilder` (B),
  `SymptomLexiconBuilder` (C), and the derivation rules (doc 01 §3.2), overrides
  (doc 01 §6), and self-checks (doc 01 §8).
- **Acceptance:** ontology is a pure projection of the DKB (every vocab value
  traces to a DKB field); build self-checks pass for all 18 classes; unit tests
  for each derivation rule; `test_ontology_is_pure_projection_of_dkb` unskipped.

## M3 — Caption Generation Engine + Validation Engine
- Implement components D–H and the `CaptionEngine` loop (doc 00 §3), the 12
  validators (doc 03), the expander lattice (doc 01 §7), seeding, diversity
  metrics/gates.
- **Acceptance:** deterministic bit-for-bit regeneration; zero forbidden terms in
  accepted captions; fallback rate ≤ 2%; diversity hard-gates pass on a pilot
  corpus; the generation/reproducibility integration tests unskipped.

## M4 — Instruction Dataset Builder + splits + converters + QA
- Implement `Emitter` (I), `SplitBuilder`, `LabelResolver`, `InstructionBank`,
  the 5 converters, and the QA sampling/review/acceptance modules.
- **Acceptance:** image-grouped stratified splits; all converters preserve
  response text and validate their lines; QA acceptance rule + kappa computed;
  converter/split integration tests unskipped.

## M5 — QLoRA fine-tuning (MLX)
- Implement `QLoRASettings` resolution and `MLXVLMRunner`; fine-tune all four
  models on the identical library/splits (M4 pin the mlx-vlm version).
- **Acceptance:** each model trains to completion on M4 Pro / 24 GB; adapters
  produced; runs reproducible from `configs/training.yaml`.

## M6 — Evaluation
- Implement classification + caption metrics, zero-shot harness, and the
  zero-shot-vs-fine-tuned comparison, including the diagnostic confusable-pair
  breakdown.
- **Acceptance:** comparison report reproduces on test + diagnostic splits;
  metrics wired to the paper tables.
