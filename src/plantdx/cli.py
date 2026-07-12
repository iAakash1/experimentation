"""PlantDx command-line interface.

This module provides the CLI *surface* (argument parsing, subcommand routing,
``--version``/``--help``). The stage handlers are intentionally not implemented
in Milestone 1; each raises :class:`NotImplementedError` naming its milestone,
which :func:`main` renders as a clean message rather than a traceback.

Usage:
    plantdx --help
    plantdx --version
    plantdx audit            --config configs/config.yaml   [--dataset tomato|mango|all] [--reports-dir DIR]
    plantdx normalize        --config configs/config.yaml   [--dataset tomato|mango|all] [--mode copy|link]
    plantdx ontology         --config configs/config.yaml   [--output DIR] [--validate-only] [--stats-only]
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

    # audit (Milestone 2 — implemented)
    p_audit = sub.add_parser(
        "audit", help="Audit the datasets and write reproducibility reports (CPU-only)"
    )
    _add_config(p_audit)
    p_audit.add_argument(
        "--dataset", default="all",
        help="Dataset to audit: a config key (e.g. tomato, mango) or 'all' (default)",
    )
    p_audit.add_argument(
        "--reports-dir", default=None,
        help="Override the reports output directory (default: paths.reports_dir)",
    )

    # normalize (Milestone 2.1 — implemented)
    p_norm = sub.add_parser(
        "normalize",
        help="Normalize raw datasets into the canonical datasets/ structure (CPU-only)",
    )
    _add_config(p_norm)
    p_norm.add_argument(
        "--dataset", default="all",
        help="Dataset to normalize: a config key (e.g. tomato, mango) or 'all' (default)",
    )
    p_norm.add_argument(
        "--mode", default=None, choices=["copy", "link"],
        help="Override the placement mode (default: normalization.mode)",
    )

    # ontology (domain ontology compiler — implemented)
    p_onto = sub.add_parser(
        "ontology", help="Compile the domain ontology from the DKB (CPU-only, deterministic)"
    )
    _add_config(p_onto)
    p_onto.add_argument(
        "--output", default=None, help="Output directory (default: artifacts/ontology)"
    )
    p_onto.add_argument(
        "--validate-only", action="store_true", help="Compile and validate; write no artifacts"
    )
    p_onto.add_argument(
        "--stats-only", action="store_true", help="Compile, validate, print statistics; write nothing"
    )

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


def _run_audit(args: argparse.Namespace) -> int:
    """Handle ``plantdx audit`` (Milestone 2). Returns a process exit code."""
    from pathlib import Path

    from plantdx.__about__ import __version__
    from plantdx.audit import build_specs, run_audit
    from plantdx.config import config_hash, load_config
    from plantdx.core.exceptions import PlantDxError

    try:
        config = load_config(args.config)
    except PlantDxError as exc:
        print(f"plantdx audit: {exc}", file=sys.stderr)
        return 1

    specs = build_specs(config, base_dir=Path.cwd())
    if args.dataset != "all":
        specs = [spec for spec in specs if spec.key == args.dataset]
        if not specs:
            available = ", ".join(sorted(config.paths.datasets)) + ", all"
            print(f"plantdx audit: unknown dataset '{args.dataset}'. Available: {available}",
                  file=sys.stderr)
            return 1

    reports_dir = Path(args.reports_dir) if args.reports_dir else Path(config.paths.reports_dir)
    manifest = run_audit(
        specs, config.audit, reports_dir,
        plantdx_version=__version__, config_hash=config_hash(config),
    )
    print(f"Audit complete: {manifest.totals['images']} images across "
          f"{len(manifest.datasets)} dataset(s). Reports in {reports_dir}/")
    print(f"Audit checksum: {manifest.audit_checksum}")
    return 0


def _run_normalize(args: argparse.Namespace) -> int:
    """Handle ``plantdx normalize`` (Milestone 2.1). Returns a process exit code."""
    from pathlib import Path

    from plantdx.__about__ import __version__
    from plantdx.config import config_hash, load_config
    from plantdx.core.exceptions import PlantDxError
    from plantdx.normalization import run_normalization

    try:
        config = load_config(args.config)
    except PlantDxError as exc:
        print(f"plantdx normalize: {exc}", file=sys.stderr)
        return 1

    available = list(config.normalization.sources)
    crops = None if args.dataset == "all" else [args.dataset]
    if crops and args.dataset not in available:
        print(f"plantdx normalize: unknown dataset '{args.dataset}'. "
              f"Available: {', '.join(available)}, all", file=sys.stderr)
        return 1

    reports = run_normalization(
        config, base_dir=Path.cwd(), crops=crops, mode=args.mode,
        plantdx_version=__version__, config_hash=config_hash(config),
    )
    total_images = sum(r.image_count for r in reports.values())
    failures = sum(len(r.checksum_failures) for r in reports.values())
    print(f"Normalization complete: {total_images} images across {len(reports)} crop(s) "
          f"into {config.paths.processed_dir}/")
    for crop, report in reports.items():
        print(f"  {crop}: {report.image_count} images, {report.class_count} classes, "
              f"checksum {report.dataset_checksum[:12]}")
    if failures:
        print(f"WARNING: {failures} checksum verification failure(s).", file=sys.stderr)
        return 1
    return 0


def _run_ontology(args: argparse.Namespace) -> int:
    """Handle ``plantdx ontology`` (domain ontology compiler). Returns an exit code."""
    import json
    from pathlib import Path

    from plantdx.config import load_config
    from plantdx.core.exceptions import PlantDxError
    from plantdx.ontology.domain import (
        compile_ontology,
        compute_statistics,
        validate_ontology,
        write_artifacts,
    )
    from plantdx.ontology.domain.validator import OntologyValidationError

    try:
        config = load_config(args.config)
        result = compile_ontology(Path(config.paths.knowledge_base["dkb_json"]))
    except PlantDxError as exc:  # config error or DKB load/validate error
        print(f"plantdx ontology: {exc}", file=sys.stderr)
        return 2

    try:
        validate_ontology(result)
    except OntologyValidationError as exc:
        print(f"plantdx ontology: {exc}", file=sys.stderr)
        return 1

    stats = compute_statistics(result, "valid")
    checksum = result.ontology.provenance["content_hash"]

    if args.stats_only:
        print(json.dumps(stats, indent=2, sort_keys=True))
        return 0
    if args.validate_only:
        print(f"ontology valid: {stats['concept_count']} concepts, "
              f"{stats['edge_count']} edges, checksum {checksum}")
        return 0

    out_dir = (Path(args.output) if args.output
               else Path(config.paths.artifact_root) / config.paths.artifacts["ontology_dir"])
    written = write_artifacts(result, out_dir, stats)
    print(f"Ontology compiled: {stats['concept_count']} concepts, {stats['edge_count']} edges, "
          f"{stats['condition_concepts']} conditions ({stats['disease_concepts']} diseases).")
    print(f"Checksum: {checksum}")
    print(f"Artifacts written to {out_dir}/ ({len(written)} files).")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. Returns a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    if args.command == "audit":
        return _run_audit(args)
    if args.command == "normalize":
        return _run_normalize(args)
    if args.command == "ontology":
        return _run_ontology(args)

    try:
        _not_implemented(args.command)
    except NotImplementedError as exc:  # pragma: no cover - surface behavior
        print(f"plantdx: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
