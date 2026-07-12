# Changelog

All notable changes to PlantDx are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added — M3: Caption Concept Model + Template Engine + Caption Corpus + Exporters (CPU-only, deterministic, image-free)
- `src/plantdx/concepts/` — the **Caption Concept Model** compiler (component A):
  `ConceptModels = f(DKB, Ontology, Vocabulary)`. Per disease, derives the
  mandatory/optional/forbidden concept sets (20-concept taxonomy), canonical ordering,
  information budget, register policy, sign type, per-concept controlled realizations +
  evidence, and the `never_appear` set. Fail-closed `V-CON-1..11` battery. Entry point
  `plantdx.concepts.build_concept_models`; CLI `plantdx concepts`; artifacts in
  `artifacts/concepts/`. `lesion_size` is omitted (no controlled DKB vocabulary) and
  `severity_stage`/`management` are always forbidden (severity/observability honesty).
- `src/plantdx/templates/` + `assets/templates/templates.json` — the **Template Engine**
  (component E): 30 authored templates across the 8 doc-02 families, using a structured
  segment schema (`lit`/`slot`/`opt`/`list`) so optional-slot deletion is grammatical by
  construction. Fail-closed `V-TPL-1..8` battery; `compatible()` routing; CLI
  `plantdx templates`; `artifacts/templates/template_index.json`.
- `src/plantdx/corpus/` — the **Sentence Planner**, **Caption Generator**, **Caption
  Validator** (independent 12-check `V-CAP-1..12` battery), and **Corpus Builder**.
  Deterministically enumerates a bounded, de-duplicated, validated per-disease caption
  corpus (1,070 captions from the real DKB); drops-and-records failing candidates and
  hard-errors on a disease with zero valid captions. CLI `plantdx generate|validate|corpus`
  (with `--condition`/`--crop`/`--format`/`--all`); artifacts `captions.{json,jsonl,csv}` +
  stats + validation report + checksum in `artifacts/corpus/`. Every caption carries its
  full source-checksum pin (ontology, vocabulary, concepts, templates) and evidence chain.
- `src/plantdx/exporters/` — **Dataset Exporters**: pure reshapers of the one corpus into
  `generic`/`llava`/`paligemma`/`blip2`/`messages` formats (deterministic, byte-identical),
  each with a `manifest.json`. CLI `plantdx corpus --format <F>` / `--all`.
- `configs/paths.yaml`: new `artifacts.{concepts_dir,corpus_dir,exports_dir}` keys.
- Tests under `tests/unit/{concepts,templates,corpus,exporters}/` (build, validation-failure,
  determinism/golden-hash, generation grammar, CLI end-to-end) plus two unskipped M3
  integration tests (forbidden-term absence, bit-for-bit reproducibility). Docs:
  `docs/CONCEPTS.md`, `docs/CORPUS.md`.
- **Scope decision (deliberate):** this milestone builds the *disease-level*,
  image-independent corpus. Image cross-join, instruction pairing, image-based splits, and
  the image-grounded per-model VLM converters (`CONVERTER_REGISTRY`) remain M4; the M1
  image-grounded stubs (`generation/*`, `validation/*`, `diversity/*`,
  `dataset/{emitter,converters}`, `core.types.CaptionRecord`) are untouched. The ontology
  and vocabulary golden `content_hash`es were verified unchanged.

### Added — Vocabulary Builder + Symptom Lexicon Compiler (CPU-only, deterministic)
- `src/plantdx/vocabulary/domain/` — a deterministic `Vocabulary = f(Ontology, Policies)`
  compiler that projects the compiled domain ontology (never the DKB directly) into a
  flat controlled vocabulary (component B: color, shape, texture, extent, leaf region,
  sign type, agent name, disease name, environment, observability + confidence modifiers)
  and a bounded symptom lexicon (component C: one verbatim base realization per symptom,
  plus one linear single-modifier realization per attached quality value on primary,
  modifiable-sign-type symptoms — never a Cartesian product across axes). Modules:
  `models` (shared `LexicalItem` schema), `policies` (category → relation mappings),
  `graph_queries` (shared read-only ontology queries), `builder`, `lexicon`, `validator`
  (fail-closed `V-VOC-1..9` battery), `statistics`, `serialization`, `checksum`. Entry
  point `plantdx.vocabulary.domain.build_vocabulary_result`.
- `plantdx vocabulary` CLI (flags `--config`, `--output`, `--validate-only`,
  `--stats-only`; also `python -m plantdx vocabulary`). Writes six artifacts to
  `artifacts/vocabulary/` (`vocabulary.json`, `symptom_lexicon.json`, `concept_index.json`,
  `statistics.json`, `checksum.txt`, `validation_report.json`) — byte-identical across runs.
- Every item carries the full traceability schema (`id, surface_form, canonical_form,
  concept, concept_id, confidence, source, ontology_node, dkb_reference, evidence,
  language, part_of_speech`), grounding it back through its ontology node to the DKB
  disease(s) and evidence that licensed it.
- Discovered and handled a real cross-axis word collision in the DKB (a few conditions,
  e.g. `mango_gall_midge`, use the same word — "raised" — as both a shape and a texture
  value): the lexicon builder deterministically keeps only the highest-priority axis
  (`MODIFIER_RELATIONS` order) per symptom, so no duplicate realizations are ever emitted.
- Tests under `tests/unit/vocabulary/` (`test_vocabulary_domain_*`, `test_vocabulary_cli.py`):
  category coverage, agent-name labeling, shared-value traceability, bounded (non-combinatorial)
  lexicon realizations, cross-axis dedup, every fail-closed validation mode, determinism,
  a real-DKB golden-hash regression, and real CLI end-to-end runs. Docs: `docs/VOCABULARY.md`.

### Fixed — CI stabilization pass (Ruff / mypy / pytest green; no behavior change)
- Fixed a circular import (`dataset/emitter.py` ⇄ `generation/engine.py`) with a
  `TYPE_CHECKING`-guarded import; zero runtime effect (`from __future__ import annotations`
  already made the annotation lazy).
- Fixed a pytest module-cache collision: two unrelated test fixture files shared the basename
  `_dataset.py` (`tests/unit/audit/` and `tests/unit/normalization/`), and two test modules
  shared `test_discovery.py`, silently shadowing each other under pytest's default import mode.
  Renamed `tests/unit/normalization/_dataset.py` → `_sample_raw_datasets.py` and
  `tests/unit/normalization/test_discovery.py` → `test_layout_detection.py`.
- Updated 3 tests that had drifted from already-implemented reality: `test_cli.py` still
  exercised the pre-domain-compiler `ontology build` stub subcommand; `test_stub_contracts.py`
  still asserted `load_config`/`sha256_hex` raise `NotImplementedError` (both are implemented);
  `test_repo_structure.py` read `paths.yaml` at its pre-nesting key path.
- 120 Ruff findings resolved (docstrings, import order, unicode-in-docstrings, `Path.open()`
  over `open()`, broad `pytest.raises(Exception)` narrowed to the actual observed exception,
  a `policies as P` import alias removed in favor of the qualified name). Two lint rules
  (`N801` on `Qwen2_5VLConverter`, `N818` on `InvariantViolation`) were suppressed with scoped,
  justified `# noqa` rather than renamed, since renaming would break the public API.
- 1 mypy error fixed in `audit/report.py` (an explicit `list[list[object]]` annotation,
  matching an existing sibling function's pattern).
- **Ontology `content_hash` verified unchanged (`sha256:25ae0f6d9692a6d00a8968dc916a3665001bba29dd45616afe5e9b3c49bf2ca4`)
  across every step of this pass** — all changes were formatting, imports, docstrings, and
  type annotations, never semantic.

### Added — Domain Ontology Compiler (CPU-only, deterministic)
- `src/plantdx/ontology/domain/` — a deterministic `Ontology = f(DKB, Policies)` compiler
  that turns the DKB into a typed knowledge graph: `models`, `policies` (fixed T-Box +
  classification maps), `graph`, `builder`, `validator` (fail-closed V-ONT battery),
  `statistics`, `serialization` (canonical JSON), `checksum` (content-only). Entry point
  `plantdx.ontology.domain.compile_ontology`.
- `plantdx ontology` CLI (flags `--config`, `--output`, `--validate-only`, `--stats-only`;
  also `python -m plantdx ontology`). Writes six artifacts to `artifacts/ontology/`
  (`ontology.json`, `concept_graph.json`, `concept_index.json`, `ontology_statistics.json`,
  `ontology_checksum.txt`, `ontology_build.log`) — byte-identical across runs.
- Tests under `tests/unit/ontology/` (`test_domain_*`): DKB loading, hierarchy/inheritance,
  graph generation, ordering, checksum determinism, real-DKB golden-hash regression, and
  every fail-closed validation mode. Docs: `docs/ONTOLOGY.md`.

### Changed
- Repurposed the `plantdx ontology` CLI command from a stub (`ontology build`) to the real
  domain-ontology compiler. The M1 caption-ontology stubs (`plantdx.ontology.{builder,models,
  concept_schema}`) are preserved unchanged; the domain compiler lives in the
  `plantdx.ontology.domain` subpackage so no other package is affected.

### Added — Milestone 2.1: Dataset Normalization Engine (CPU-only, filesystem)
- `src/plantdx/normalization/` — copies the tomato + mango classes from the immutable
  raw datasets into `datasets/<crop>/processed/<canonical_class>/`; structure-agnostic
  layout detection (flat and train/val), canonical class naming, SHA-256 verification,
  duplicate/collision handling, and writers for `class_mapping.json`, `manifest.json`,
  `dataset_card.md`, and a combined `normalization_report.json`. Entry point
  `plantdx.normalization.run_normalization`.
- `plantdx normalize` CLI command (and `python -m plantdx normalize`).
- `configs/normalization.yaml` (+ `NormalizationConfig`, `SourceSpec`, `paths.processed_dir`);
  wired into `config.yaml` includes.
- Tests under `tests/unit/normalization/` (layout detection, extraction, dedup/collision,
  checksum verification, raw immutability, report generation). Docs: `docs/NORMALIZATION.md`.
- `.gitignore`: `/datasets/` (generated normalized output).

### Added — Milestone 2: Dataset Audit Engine (CPU-only)
- `src/plantdx/audit/` — image discovery, metadata inspection (Pillow, no full decode),
  SHA-256 hashing, exact + optional average-hash near-duplicate detection, folder
  validation, per-dataset summaries, deterministic checksums, and report writers
  (CSV/JSON/Markdown + manifest + log). Entry point `plantdx.audit.run_audit`.
- `plantdx audit` CLI command (and `python -m plantdx audit`).
- `configs/audit.yaml` (+ `AuditConfig`, `paths.reports_dir`); wired into `config.yaml` includes.
- Implemented the M2 infrastructure the audit depends on: config loader
  (`config/loader.py`), `utils/io.py`, `utils/hashing.py`, `utils/logging.py`.
- Tests under `tests/unit/audit/` (discovery, corrupt handling, duplicates, checksum
  determinism, report/JSON/CSV/manifest generation). Docs: `docs/AUDIT.md`.

### Changed
- `configs/paths.yaml` nested under a top-level `paths:` key so the loader maps it to
  `PlantDxConfig.paths` (consistent with the other included config files).
- Pillow moved from the `train` extra to a core runtime dependency (needed by the audit).
- `reports/` added to `.gitignore` (generated audit output).

### Changed — post-review simplification (no methodology change)
- Removed `core/interfaces.py` (unused generic Protocols that duplicated the concrete ABCs).
- Refactored `core/seeding.py` from a `SeedDeriver` class to pure module-level functions
  (`image_seed`, `caption_seed`, `attempt_seed`); updated `CaptionEngine` to take `global_seed`.
- Consolidated the `dataset/converters/` package (7 files) into a single `dataset/converters.py`
  (base ABC + 5 converters + `CONVERTER_REGISTRY`); public API and registry unchanged.
- Renamed `dataset/schema.py` → `dataset/serialization.py` (disambiguates from `config/schema.py`).
- Removed unused dependency `typing-extensions`; moved the M3 generation/diversity stack
  (`numpy`, `tqdm`, `datasketch`, `sacrebleu`) to a `generate` extra.
- Trimmed `__init__.py` re-exports to true public entry points across all subpackages.
- Removed speculative config: per-validator enable/blocking toggles, duplicated `max_attempts`,
  `reproducibility.hash_algorithm`, and the duplicated eval output dir.

### Added — Milestone 1: repository scaffolding
- Production repository structure (`src/` layout, `configs/`, `tests/`, `docs/`, `assets/`, `artifacts/`).
- Packaging and tooling: `pyproject.toml`, `requirements*.txt`, `.pre-commit-config.yaml`,
  `.editorconfig`, `.gitignore`, `Makefile`, `MANIFEST.in`, Apache-2.0 `LICENSE`, `NOTICE`, `CITATION.cff`.
- Typed public APIs and module responsibilities for every pipeline component
  (ontology, vocabulary, generation, validation, diversity, dataset, qa, training, evaluation) —
  **interfaces only**, no algorithm implementations.
- Configuration files: `config.yaml`, `paths.yaml`, `generation.yaml`, `validation.yaml`, `training.yaml`.
- Test scaffolding (unit / integration / benchmark) and developer documentation.
- CLI surface (`plantdx …`) with stubbed subcommands.

### Notes
- No pipeline logic is implemented in this milestone; stage entry points raise
  `NotImplementedError` pointing to their target milestone.
- Stage 1 (DKB) and the Stage 2 specification were completed prior to this changelog
  and live in `knowledge_base/` and `caption_framework/`.

<!-- Milestone template:
## [X.Y.Z] - YYYY-MM-DD
### Added
### Changed
### Fixed
-->
