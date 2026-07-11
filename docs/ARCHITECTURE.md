# Architecture

How the `src/plantdx/` code maps to the caption-framework specification
(`caption_framework/`). The spec labels the runtime components **A–I**
(`00_methodology_overview.md §2`); each maps to a package here.

## Component → package map

| Spec component | Package / module | Interface class | Milestone |
|----------------|------------------|-----------------|-----------|
| — DKB loader | `knowledge_base/loader.py` | `DKBLoader` | M2 |
| (A) Ontology Builder | `ontology/builder.py` | `OntologyBuilder` | M2 |
| (B) Vocabulary Builder | `vocabulary/builder.py` | `VocabularyBuilder` | M2 |
| (C) Symptom Lexicon Builder | `vocabulary/lexicon.py` | `SymptomLexiconBuilder` | M2 |
| (D) Concept Selector | `generation/selector.py` | `ConceptSelector` | M3 |
| (E) Template Library | `generation/templates.py` | `TemplateLibrary` | M3 |
| (F) Slot Realizer + Expander | `generation/realizer.py`, `vocabulary/expander.py` | `SlotRealizer`, `VocabularyExpander` | M3 |
| (G) Validator Battery | `validation/battery.py`, `validation/validators.py` | `ValidatorBattery`, `V1..V12` | M3 |
| (H) Dedup + Diversity | `diversity/deduplicator.py`, `diversity/controller.py`, `diversity/metrics.py` | `Deduplicator`, `DiversityController`, `DiversityEvaluator` | M3 |
| (I) Emitter | `dataset/emitter.py` | `Emitter` | M4 |
| Orchestrator | `generation/engine.py` | `CaptionEngine` | M3 |
| Splits | `dataset/splits.py` | `SplitBuilder` | M4 |
| Converters | `dataset/converters.py` | `BaseConverter` + 5 subclasses + `CONVERTER_REGISTRY` | M4 |
| QA | `qa/*` | `AuditSampler`, `ReviewStore`, `AcceptanceEvaluator` | M4 |
| Training | `training/*` | `MLXVLMRunner`, `QLoRASettings` | M5 |
| Evaluation | `evaluation/*` | `ZeroShotEvaluator`, `ComparisonReporter` | M6 |

Supporting layers: `core/` (types, enums, exceptions, seeding — a leaf package
depending only on stdlib), `config/` (typed schema + loader), `utils/` (hashing,
io, logging, versioning).

## Dependency direction

```
core  ◄─ everything          (leaf; no PlantDx deps)
config ◄─ (uses core)
knowledge_base ◄─ ontology ◄─ vocabulary
                     └────────────┐
generation (D,E,F, engine) ─► validation, diversity, dataset(emitter)
dataset (schema, splits, converters, instructions, label_map)
qa, training, evaluation depend on dataset/core
```

Rules:
- `core` never imports another PlantDx package.
- Builders (A/B/C) run once at build time and only read the DKB + assets.
- The generation path (D–I) never imports a neural model and never reads pixels
  (invariant #1). Training/evaluation are the only packages that touch models.

## Data flow (runtime)

`dkb.json` → (A/B/C) `ontology/` + `vocabulary/` artifacts → per image the
`CaptionEngine` runs D→E→F→G→H→I → `captions/caption_library.jsonl` → diversity
metrics + QA → splits → per-model converters → training → evaluation. Full
diagram: `caption_framework/00_methodology_overview.md §2`.

## Determinism & provenance

All randomness derives from one `global_seed` via the pure functions in
`core.seeding` (`image_seed`/`caption_seed`/`attempt_seed`, SHA-256 fan-out).
Every emitted record carries a `Provenance` object (`core/types.py`) sufficient
to regenerate it bit-for-bit (doc 00 §6).
