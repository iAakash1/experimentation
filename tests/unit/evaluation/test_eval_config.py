"""Eval config resolution: defaults + fail-closed validation."""

from __future__ import annotations

import pytest

from plantdx.core.exceptions import ConfigError
from plantdx.evaluation.config import resolve_eval_config


@pytest.mark.unit
def test_defaults_match_the_frozen_tomato_run() -> None:
    cfg = resolve_eval_config()
    assert cfg.stage == "all"
    assert cfg.split == "test"
    assert "Qwen2.5-VL" in cfg.model_path
    # The checkpoint DIRECTORY, not the weights file inside it -- mlx-vlm's
    # apply_lora_layers expects a directory containing adapter_config.json +
    # adapters.safetensors (see evaluation/checkpoint.py).
    assert not cfg.adapter_path.endswith("adapters.safetensors")
    assert "qwen25vl_tomato_qlora" in cfg.adapter_path
    assert cfg.predictions_path.endswith("raw/predictions.jsonl")


@pytest.mark.unit
def test_overrides_are_applied() -> None:
    cfg = resolve_eval_config(stage="analyze", split="validation", max_samples=10, batch_size=4)
    assert cfg.stage == "analyze"
    assert cfg.split == "validation"
    assert cfg.max_samples == 10
    assert cfg.batch_size == 4


@pytest.mark.unit
@pytest.mark.parametrize(
    "kwargs",
    [
        {"stage": "bogus"},
        {"split": "bogus"},
        {"device": "bogus"},
        {"batch_size": 0},
        {"max_samples": 0},
    ],
)
def test_invalid_values_fail_closed(kwargs: dict) -> None:
    with pytest.raises(ConfigError):
        resolve_eval_config(**kwargs)
