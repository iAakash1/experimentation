"""Evaluation run configuration: resolved from CLI flags, validated fail-closed.

An evaluation run is driven entirely by `plantdx evaluate` flags (no YAML layer
like training's `configs/train/` — the eval surface is small enough that flags
with sensible frozen-run defaults are simpler and just as reproducible, since
every resolved value is recorded into the reproducibility manifest anyway).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from plantdx.core.exceptions import ConfigError

_STAGES = frozenset({"inference", "analyze", "all"})
_SPLITS = frozenset({"train", "validation", "test"})
_DEVICES = frozenset({"auto", "cpu", "gpu"})

_DEFAULT_MODEL_PATH = "mlx-community/Qwen2.5-VL-7B-Instruct-4bit"
# The checkpoint DIRECTORY (mlx-vlm's apply_lora_layers expects a directory
# containing adapter_config.json + adapters.safetensors side by side, not the
# weights file alone) -- see evaluation/checkpoint.py.
_DEFAULT_ADAPTER = "checkpoints/qwen25vl_tomato_qlora"
_DEFAULT_DATASET_DIR = "artifacts/training/qwen25vl_tomato_qlora/dataset"
_DEFAULT_OUTPUT_DIR = "reports/qwen25vl_tomato_qlora/evaluation"


@dataclass(frozen=True)
class EvalConfig:
    """Fully-resolved settings for one `plantdx evaluate` invocation."""

    stage: str  # inference | analyze | all
    model_path: str  # base model repo id/path (never modified, never retrained)
    adapter_path: str  # trained LoRA adapter checkpoint DIRECTORY (frozen artifact)
    dataset_dir: str  # dir containing the frozen train/validation/test.jsonl
    split: str  # which split to evaluate (default: test)
    output_dir: str  # reports/<run>/evaluation/
    batch_size: int
    max_samples: int | None  # None = evaluate every sample in the split
    seed: int
    device: str  # auto | cpu | gpu (mlx picks its own device; recorded for the manifest)
    predictions_path: str  # the stage-1 -> stage-2 artifact contract


def resolve_eval_config(
    *,
    stage: str = "all",
    model: str | None = None,
    adapter: str | None = None,
    dataset: str | None = None,
    split: str = "test",
    output_dir: str | None = None,
    batch_size: int = 1,
    max_samples: int | None = None,
    seed: int = 20260711,
    device: str = "auto",
    predictions_path: str | None = None,
) -> EvalConfig:
    """Resolve and validate an :class:`EvalConfig` from CLI-flag values.

    Every parameter has a default matching the frozen tomato/Qwen2.5-VL run, so
    ``plantdx evaluate`` with no flags evaluates that exact run's test split.
    """
    errors: list[str] = []
    if stage not in _STAGES:
        errors.append(f"--stage must be one of {sorted(_STAGES)} (got {stage!r})")
    if split not in _SPLITS:
        errors.append(f"--split must be one of {sorted(_SPLITS)} (got {split!r})")
    if device not in _DEVICES:
        errors.append(f"--device must be one of {sorted(_DEVICES)} (got {device!r})")
    if batch_size <= 0:
        errors.append(f"--batch-size must be > 0 (got {batch_size})")
    if max_samples is not None and max_samples <= 0:
        errors.append(f"--max-samples must be > 0 (got {max_samples})")
    if errors:
        raise ConfigError("evaluation config invalid:\n  " + "\n  ".join(errors))

    out_dir = output_dir or _DEFAULT_OUTPUT_DIR
    return EvalConfig(
        stage=stage,
        model_path=model or _DEFAULT_MODEL_PATH,
        adapter_path=adapter or _DEFAULT_ADAPTER,
        dataset_dir=dataset or _DEFAULT_DATASET_DIR,
        split=split,
        output_dir=out_dir,
        batch_size=batch_size,
        max_samples=max_samples,
        seed=seed,
        device=device,
        predictions_path=predictions_path or str(Path(out_dir) / "raw" / "predictions.jsonl"),
    )
