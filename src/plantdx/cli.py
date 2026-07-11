"""PlantDx command-line interface.

This module provides the CLI *surface* (argument parsing, subcommand routing,
``--version``/``--help``). The stage handlers are intentionally not implemented
in Milestone 1; each raises :class:`NotImplementedError` naming its milestone,
which :func:`main` renders as a clean message rather than a traceback.

Usage:
    plantdx --help
    plantdx --version
    plantdx ontology build   --config configs/config.yaml
    plantdx vocabulary build --config configs/config.yaml
    plantdx generate         --config configs/config.yaml
    plantdx validate         --config configs/config.yaml
    plantdx dataset build    --config configs/config.yaml
    plantdx dataset convert  --model qwen3_vl
    plantdx qa sample        --config configs/config.yaml
    plantdx train            --model qwen3_vl
    plantdx evaluate         --model qwen3_vl
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from plantdx.__about__ import __version__

_MILESTONE = {
    "ontology": "Milestone 2",
    "vocabulary": "Milestone 2",
    "generate": "Milestone 3",
    "validate": "Milestone 3",
    "dataset": "Milestone 4",
    "qa": "Milestone 4",
    "train": "Milestone 5",
    "evaluate": "Milestone 6",
}


def _not_implemented(command: str) -> None:
    """Raise a milestone-tagged NotImplementedError for a stubbed command."""
    milestone = _MILESTONE.get(command, "a later milestone")
    raise NotImplementedError(f"`plantdx {command}` is implemented in {milestone}.")


def build_parser() -> argparse.ArgumentParser:
    """Construct the top-level argument parser and all subcommands."""
    parser = argparse.ArgumentParser(
        prog="plantdx",
        description="Knowledge-grounded instruction-tuning datasets for agricultural VLMs.",
    )
    parser.add_argument("--version", action="version", version=f"plantdx {__version__}")
    sub = parser.add_subparsers(dest="command", metavar="<command>")

    def _add_config(p: argparse.ArgumentParser) -> None:
        p.add_argument("--config", default="configs/config.yaml", help="Path to config.yaml")

    # ontology build
    p_onto = sub.add_parser("ontology", help="Build the caption ontology (M2)")
    onto_sub = p_onto.add_subparsers(dest="subcommand", metavar="<subcommand>")
    _add_config(onto_sub.add_parser("build", help="Derive ontology from the DKB"))

    # vocabulary build
    p_vocab = sub.add_parser("vocabulary", help="Build vocabulary + symptom lexicon (M2)")
    vocab_sub = p_vocab.add_subparsers(dest="subcommand", metavar="<subcommand>")
    _add_config(vocab_sub.add_parser("build", help="Derive vocabulary artifacts"))

    # generate / validate
    _add_config(sub.add_parser("generate", help="Generate the caption library (M3)"))
    _add_config(sub.add_parser("validate", help="Validate the caption library (M3)"))

    # dataset build / convert
    p_ds = sub.add_parser("dataset", help="Build splits and convert per-model datasets (M4)")
    ds_sub = p_ds.add_subparsers(dest="subcommand", metavar="<subcommand>")
    _add_config(ds_sub.add_parser("build", help="Build canonical dataset + splits"))
    p_conv = ds_sub.add_parser("convert", help="Convert to a target model's format")
    p_conv.add_argument("--model", required=True, help="Target model key (e.g. qwen3_vl)")

    # qa
    p_qa = sub.add_parser("qa", help="Quality-assurance sampling/acceptance (M4)")
    qa_sub = p_qa.add_subparsers(dest="subcommand", metavar="<subcommand>")
    _add_config(qa_sub.add_parser("sample", help="Draw a stratified audit sample"))
    _add_config(qa_sub.add_parser("accept", help="Evaluate the acceptance rule"))

    # train / evaluate
    p_train = sub.add_parser("train", help="QLoRA fine-tune a target model (M5)")
    p_train.add_argument("--model", required=True, help="Target model key")
    p_eval = sub.add_parser("evaluate", help="Evaluate zero-shot vs fine-tuned (M6)")
    p_eval.add_argument("--model", required=True, help="Target model key")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. Returns a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    try:
        _not_implemented(args.command)
    except NotImplementedError as exc:  # pragma: no cover - surface behavior
        print(f"plantdx: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
