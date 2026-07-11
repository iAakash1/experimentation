# scripts/

Thin wrappers around the `plantdx` CLI and common developer flows. They contain
**no logic** — the logic lives in the package (`src/plantdx/`). Prefer the CLI
(`plantdx …`) directly; these exist for convenience and reproducible invocations.

| Script | Purpose |
|--------|---------|
| `dev_setup.sh` | Create a venv, install `.[dev]`, install pre-commit hooks. |
| `run_pipeline.sh` | Run the end-to-end pipeline stages in order (stubbed until each milestone lands). |

Make them executable with `chmod +x scripts/*.sh`.
