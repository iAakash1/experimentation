# Changelog

All notable changes to PlantDx are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
