"""Stage 1 orchestration: adapter path resolution, without needing real mlx-vlm.

``load_model``/``_generate`` are mocked (real mlx-vlm inference needs Apple
Silicon + a loaded 7B model; that path is exercised manually, not in CI) --
these tests instead pin down the *contract* between ``run_inference`` and the
checkpoint resolver, which is exactly where the reported bug lived.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from plantdx.evaluation.checkpoint import ADAPTER_CONFIG_NAME, ADAPTER_WEIGHTS_NAME
from plantdx.evaluation.config import resolve_eval_config
from plantdx.training.inference import LoadedModel


@pytest.fixture
def checkpoint_dir(tmp_path: Path) -> Path:
    ckpt = tmp_path / "checkpoints" / "test_run"
    ckpt.mkdir(parents=True)
    (ckpt / ADAPTER_CONFIG_NAME).write_text("{}", encoding="utf-8")
    (ckpt / ADAPTER_WEIGHTS_NAME).write_bytes(b"fake-weights")
    return ckpt


@pytest.fixture
def eval_dataset_dir(tmp_path: Path) -> Path:
    d = tmp_path / "dataset"
    d.mkdir()
    row = {
        "image": "/data/tomato/processed/healthy/img.JPG",
        "question": "Describe the visible condition of this tomato leaf.",
        "answer": "This is a healthy tomato leaf.",
    }
    (d / "train.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    (d / "test.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    return d


def _fake_loaded_model(model_path: str, adapter_path: str | None = None) -> LoadedModel:
    return LoadedModel(
        model=object(),
        processor=object(),
        config=object(),
        model_path=model_path,
        adapter_path=adapter_path,
    )


@pytest.mark.unit
def test_run_inference_passes_the_resolved_directory_not_the_raw_config(
    checkpoint_dir: Path, eval_dataset_dir: Path, tmp_path: Path
) -> None:
    """Regression test for the reported bug: passing a path ending in
    `adapters.safetensors` in `--adapter` must still reach `load_model` as the
    checkpoint DIRECTORY, never as the raw file path."""
    from plantdx.evaluation import inference_runner

    weights_file_path = str(checkpoint_dir / ADAPTER_WEIGHTS_NAME)  # the exact buggy input
    cfg = resolve_eval_config(
        stage="inference",
        adapter=weights_file_path,
        dataset=str(eval_dataset_dir),
        output_dir=str(tmp_path / "out"),
    )

    captured_adapter_paths: list[str | None] = []

    def fake_load_model(model_path: str, adapter_path: str | None = None) -> LoadedModel:
        captured_adapter_paths.append(adapter_path)
        return _fake_loaded_model(model_path, adapter_path)

    with (
        patch.object(inference_runner, "load_model", side_effect=fake_load_model),
        patch.object(
            inference_runner,
            "_generate",
            return_value=inference_runner._GenerationTelemetry(
                text="ok",
                elapsed_ms=1.0,
                prompt_tokens=1,
                generation_tokens=1,
                peak_memory_gb=0.0,
                confidence=None,
            ),
        ),
    ):
        inference_runner.run_inference(cfg)

    # base model: no adapter; fine-tuned model: the RESOLVED directory, never
    # the raw `.../adapters.safetensors` file path from the config.
    assert captured_adapter_paths == [None, str(checkpoint_dir)]
    assert weights_file_path not in captured_adapter_paths


@pytest.mark.unit
def test_run_inference_writes_predictions_and_metadata(
    checkpoint_dir: Path, eval_dataset_dir: Path, tmp_path: Path
) -> None:
    from plantdx.evaluation import inference_runner

    cfg = resolve_eval_config(
        stage="inference",
        adapter=str(checkpoint_dir),
        dataset=str(eval_dataset_dir),
        output_dir=str(tmp_path / "out"),
    )

    with (
        patch.object(inference_runner, "load_model", side_effect=_fake_loaded_model),
        patch.object(
            inference_runner,
            "_generate",
            return_value=inference_runner._GenerationTelemetry(
                text="a healthy tomato leaf",
                elapsed_ms=5.0,
                prompt_tokens=10,
                generation_tokens=5,
                peak_memory_gb=8.0,
                confidence=0.9,
            ),
        ),
    ):
        out_path = inference_runner.run_inference(cfg)

    assert out_path.is_file()
    rows = [json.loads(line) for line in out_path.read_text().splitlines()]
    assert len(rows) == 1
    assert rows[0]["finetuned_prediction"] == "a healthy tomato leaf"
    metadata = json.loads((out_path.parent / "metadata.json").read_text())
    assert metadata["sample_count"] == 1


@pytest.mark.unit
def test_run_inference_fails_closed_on_malformed_checkpoint(
    eval_dataset_dir: Path, tmp_path: Path
) -> None:
    from plantdx.core.exceptions import DerivationError
    from plantdx.evaluation import inference_runner

    cfg = resolve_eval_config(
        stage="inference",
        adapter=str(tmp_path / "no_such_checkpoint"),
        dataset=str(eval_dataset_dir),
        output_dir=str(tmp_path / "out"),
    )
    with pytest.raises(DerivationError, match="not found"):
        inference_runner.run_inference(cfg)
