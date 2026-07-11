# Roadmap

Milestones and their acceptance criteria. Each milestone is a separate,
reviewable body of work; scope PRs to a single milestone.

## M1 — Repository scaffolding ✅ (this milestone)
- Production structure, packaging, tooling, configs, typed public APIs, tests, docs.
- **Acceptance:** `make check` green; every module imports; CLI surface parses;
  registries complete; stubs raise `NotImplementedError`. No pipeline logic.

## M2 — Ontology + Vocabulary + Symptom Lexicon (DKB → ontology)
- Implement `DKBLoader`, `OntologyBuilder` (A), `VocabularyBuilder` (B),
  `SymptomLexiconBuilder` (C), and the derivation rules (doc 01 §3.2), overrides
  (doc 01 §6), and self-checks (doc 01 §8). Config loader + hashing + io.
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
