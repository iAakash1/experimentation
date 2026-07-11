# PlantDx Documentation

Developer-facing documentation. The **research/design specification** (the source
of truth) lives in [`../caption_framework/`](../caption_framework/) and
[`../knowledge_base/`](../knowledge_base/); the docs here explain how the code
implements it.

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | How the `src/plantdx/` packages map to spec components A–I and the pipeline stages. |
| [REPO_LAYOUT.md](REPO_LAYOUT.md) | Repository layout and its correspondence to the spec's artifact tree (doc 06). |
| [CONFIGURATION.md](CONFIGURATION.md) | Configuration reference (`configs/`), precedence, and tunables. |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Dev environment, workflow, testing, coding standards. |
| [ROADMAP.md](ROADMAP.md) | Milestones M1–M6 and their acceptance criteria. |
| [adr/](adr/) | Architecture Decision Records. |

## The seven design invariants (every change must preserve these)

1. Label-only grounding · 2. DKB is the single source of truth · 3. Closed
vocabulary · 4. Observability (single-leaf) · 5. Pest/pathogen register integrity
· 6. Severity honesty · 7. Reproducibility.

See [`../caption_framework/README.md`](../caption_framework/README.md) for the
authoritative statement.
