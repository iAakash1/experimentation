"""PlantDx command-line interface.

This module provides the CLI *surface* (argument parsing, subcommand routing,
``--version``/``--help``). The stage handlers are intentionally not implemented
in Milestone 1; each raises :class:`NotImplementedError` naming its milestone,
which :func:`main` renders as a clean message rather than a traceback.

Usage:
    plantdx --help
    plantdx --version
    plantdx audit             --config configs/config.yaml
                              [--dataset tomato|mango|all] [--reports-dir DIR]
    plantdx normalize         --config configs/config.yaml
                              [--dataset tomato|mango|all] [--mode copy|link]
    plantdx ontology          --config configs/config.yaml
                              [--output DIR] [--validate-only] [--stats-only]
    plantdx vocabulary       --config configs/config.yaml
                              [--output DIR] [--validate-only] [--stats-only]
    plantdx concepts         --config configs/config.yaml
                              [--output DIR] [--validate-only] [--stats-only]
    plantdx templates        --config configs/config.yaml
                              [--output DIR] [--validate-only] [--stats-only]
    plantdx generate         --config configs/config.yaml
                              [--condition ID] [--crop tomato|mango]
                              [--output DIR] [--validate-only] [--stats-only]
    plantdx validate         --config configs/config.yaml [--condition ID] [--crop C]
    plantdx corpus           --config configs/config.yaml
                              [--condition ID] [--crop C] [--format F | --all]
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
from pathlib import Path
from typing import Any

from plantdx.__about__ import __version__

_MILESTONE = {
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
        "--dataset",
        default="all",
        help="Dataset to audit: a config key (e.g. tomato, mango) or 'all' (default)",
    )
    p_audit.add_argument(
        "--reports-dir",
        default=None,
        help="Override the reports output directory (default: paths.reports_dir)",
    )

    # normalize (Milestone 2.1 — implemented)
    p_norm = sub.add_parser(
        "normalize",
        help="Normalize raw datasets into the canonical datasets/ structure (CPU-only)",
    )
    _add_config(p_norm)
    p_norm.add_argument(
        "--dataset",
        default="all",
        help="Dataset to normalize: a config key (e.g. tomato, mango) or 'all' (default)",
    )
    p_norm.add_argument(
        "--mode",
        default=None,
        choices=["copy", "link"],
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
        "--stats-only",
        action="store_true",
        help="Compile, validate, print statistics; write nothing",
    )

    # vocabulary (vocabulary + symptom lexicon compiler — implemented)
    p_vocab = sub.add_parser(
        "vocabulary", help="Derive the vocabulary + symptom lexicon from the ontology (CPU-only)"
    )
    _add_config(p_vocab)
    p_vocab.add_argument(
        "--output", default=None, help="Output directory (default: artifacts/vocabulary)"
    )
    p_vocab.add_argument(
        "--validate-only", action="store_true", help="Compile and validate; write no artifacts"
    )
    p_vocab.add_argument(
        "--stats-only",
        action="store_true",
        help="Compile, validate, print statistics; write nothing",
    )

    # concepts (Caption Concept Model compiler — implemented)
    p_con = sub.add_parser(
        "concepts", help="Derive the per-disease Caption Concept Model (CPU-only, deterministic)"
    )
    _add_config(p_con)
    p_con.add_argument("--output", default=None, help="Override output directory")
    p_con.add_argument("--validate-only", action="store_true", help="Build+validate; write nothing")
    p_con.add_argument("--stats-only", action="store_true", help="Build+validate; print stats")

    # templates (Template Engine — implemented)
    p_tpl = sub.add_parser(
        "templates", help="Validate + index the authored caption template library (CPU-only)"
    )
    _add_config(p_tpl)
    p_tpl.add_argument("--output", default=None, help="Override output directory")
    p_tpl.add_argument("--validate-only", action="store_true", help="Validate; write no artifacts")
    p_tpl.add_argument("--stats-only", action="store_true", help="Validate; print statistics")

    def _add_corpus_filters(p: argparse.ArgumentParser) -> None:
        p.add_argument("--condition", default=None, help="Restrict to one disease id")
        p.add_argument("--crop", default=None, help="Restrict to one crop (tomato|mango)")

    # generate (build the caption corpus — implemented)
    p_gen = sub.add_parser(
        "generate", help="Generate the deterministic caption corpus (CPU-only, image-free)"
    )
    _add_config(p_gen)
    _add_corpus_filters(p_gen)
    p_gen.add_argument("--output", default=None, help="Override output directory")
    p_gen.add_argument("--validate-only", action="store_true", help="Build+validate; write nothing")
    p_gen.add_argument("--stats-only", action="store_true", help="Build+validate; print stats")

    # validate (independent caption validation — implemented)
    p_val = sub.add_parser("validate", help="Build + independently validate the caption corpus")
    _add_config(p_val)
    _add_corpus_filters(p_val)

    # corpus (build corpus + dataset exporters — implemented)
    p_corp = sub.add_parser("corpus", help="Build the corpus and write dataset exporters")
    _add_config(p_corp)
    _add_corpus_filters(p_corp)
    p_corp.add_argument("--output", default=None, help="Override output directory")
    p_corp.add_argument(
        "--format", default=None, help="Export only this format (see --all for every format)"
    )
    p_corp.add_argument("--all", action="store_true", help="Export all formats (the default)")

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
            print(
                f"plantdx audit: unknown dataset '{args.dataset}'. Available: {available}",
                file=sys.stderr,
            )
            return 1

    reports_dir = Path(args.reports_dir) if args.reports_dir else Path(config.paths.reports_dir)
    manifest = run_audit(
        specs,
        config.audit,
        reports_dir,
        plantdx_version=__version__,
        config_hash=config_hash(config),
    )
    print(
        f"Audit complete: {manifest.totals['images']} images across "
        f"{len(manifest.datasets)} dataset(s). Reports in {reports_dir}/"
    )
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
        print(
            f"plantdx normalize: unknown dataset '{args.dataset}'. "
            f"Available: {', '.join(available)}, all",
            file=sys.stderr,
        )
        return 1

    reports = run_normalization(
        config,
        base_dir=Path.cwd(),
        crops=crops,
        mode=args.mode,
        plantdx_version=__version__,
        config_hash=config_hash(config),
    )
    total_images = sum(r.image_count for r in reports.values())
    failures = sum(len(r.checksum_failures) for r in reports.values())
    print(
        f"Normalization complete: {total_images} images across {len(reports)} crop(s) "
        f"into {config.paths.processed_dir}/"
    )
    for crop, report in reports.items():
        print(
            f"  {crop}: {report.image_count} images, {report.class_count} classes, "
            f"checksum {report.dataset_checksum[:12]}"
        )
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
        print(
            f"ontology valid: {stats['concept_count']} concepts, "
            f"{stats['edge_count']} edges, checksum {checksum}"
        )
        return 0

    out_dir = (
        Path(args.output)
        if args.output
        else Path(config.paths.artifact_root) / config.paths.artifacts["ontology_dir"]
    )
    written = write_artifacts(result, out_dir, stats)
    print(
        f"Ontology compiled: {stats['concept_count']} concepts, {stats['edge_count']} edges, "
        f"{stats['condition_concepts']} conditions ({stats['disease_concepts']} diseases)."
    )
    print(f"Checksum: {checksum}")
    print(f"Artifacts written to {out_dir}/ ({len(written)} files).")
    return 0


def _run_vocabulary(args: argparse.Namespace) -> int:
    """Handle ``plantdx vocabulary`` (vocabulary + symptom lexicon compiler). Returns exit code."""
    import json
    from pathlib import Path

    from plantdx.config import load_config
    from plantdx.core.exceptions import PlantDxError
    from plantdx.ontology.domain import compile_ontology, validate_ontology
    from plantdx.ontology.domain.validator import OntologyValidationError
    from plantdx.vocabulary.domain import (
        build_vocabulary_result,
        compute_statistics,
        validate_vocabulary_result,
        write_artifacts,
    )
    from plantdx.vocabulary.domain.validator import VocabularyValidationError

    try:
        config = load_config(args.config)
        onto_result = compile_ontology(Path(config.paths.knowledge_base["dkb_json"]))
    except PlantDxError as exc:  # config error or DKB load/validate error
        print(f"plantdx vocabulary: {exc}", file=sys.stderr)
        return 2

    try:
        validate_ontology(onto_result)
    except OntologyValidationError as exc:
        print(f"plantdx vocabulary: source ontology is invalid: {exc}", file=sys.stderr)
        return 1

    ontology = onto_result.ontology
    result = build_vocabulary_result(ontology)

    try:
        report = validate_vocabulary_result(result, ontology)
    except VocabularyValidationError as exc:
        print(f"plantdx vocabulary: {exc}", file=sys.stderr)
        return 1

    stats = compute_statistics(result, "valid")
    checksum = result.provenance["content_hash"]

    if args.stats_only:
        print(json.dumps(stats, indent=2, sort_keys=True))
        return 0
    if args.validate_only:
        print(
            f"vocabulary valid: {stats['vocabulary_item_count']} vocabulary items, "
            f"{stats['lexicon_item_count']} lexicon items, checksum {checksum}"
        )
        return 0

    out_dir = (
        Path(args.output)
        if args.output
        else Path(config.paths.artifact_root) / config.paths.artifacts["vocabulary_dir"]
    )
    written = write_artifacts(result, out_dir, stats, report)
    print(
        f"Vocabulary compiled: {stats['vocabulary_item_count']} vocabulary items, "
        f"{stats['lexicon_item_count']} lexicon items."
    )
    print(f"Checksum: {checksum}")
    print(f"Artifacts written to {out_dir}/ ({len(written)} files).")
    return 0


class _Bundle:
    """Small carrier for the compiled upstream pipeline (CLI-internal)."""

    def __init__(
        self, config: Any, ontology: Any, vocab: Any, models: Any, concepts_report: Any
    ) -> None:
        self.config = config
        self.ontology = ontology
        self.vocab = vocab
        self.models = models
        self.concepts_report = concepts_report
        self.corpus: Any = None
        self.corpus_report: Any = None


def _artifact_dir(config: Any, key: str, override: str | None) -> Path:
    """Resolve an artifact output directory from config or a CLI ``--output`` override."""
    if override:
        return Path(override)
    root = Path(str(config.paths.artifact_root))
    return root / str(config.paths.artifacts[key])


def _compile_concepts(config_path: str) -> _Bundle:
    """Build ontology -> vocabulary -> concept models (validated). Returns a bundle."""
    from plantdx.concepts import build_concept_models, validate_concept_models
    from plantdx.config import load_config
    from plantdx.ontology.domain import compile_ontology, validate_ontology
    from plantdx.vocabulary.domain import build_vocabulary_result, validate_vocabulary_result

    config = load_config(config_path)
    onto = compile_ontology(Path(config.paths.knowledge_base["dkb_json"]))
    validate_ontology(onto)
    vocab = build_vocabulary_result(onto.ontology)
    validate_vocabulary_result(vocab, onto.ontology)
    models = build_concept_models(onto.dkb, onto.ontology, vocab)
    report = validate_concept_models(models, onto.ontology, vocab)
    return _Bundle(config, onto.ontology, vocab, models, report)


def _run_concepts(args: argparse.Namespace) -> int:
    """Handle ``plantdx concepts`` (Caption Concept Model compiler)."""
    import json

    from plantdx.concepts import compute_statistics, write_artifacts
    from plantdx.concepts.validator import ConceptValidationError
    from plantdx.core.exceptions import PlantDxError

    try:
        b = _compile_concepts(args.config)
    except ConceptValidationError as exc:
        print(f"plantdx concepts: {exc}", file=sys.stderr)
        return 1
    except PlantDxError as exc:
        print(f"plantdx concepts: {exc}", file=sys.stderr)
        return 2

    stats = compute_statistics(b.models, "valid")
    checksum = b.models.provenance["content_hash"]
    if args.stats_only:
        print(json.dumps(stats, indent=2, sort_keys=True))
        return 0
    if args.validate_only:
        print(f"concepts valid: {stats['disease_count']} disease models, checksum {checksum}")
        return 0
    out_dir = _artifact_dir(b.config, "concepts_dir", args.output)
    written = write_artifacts(b.models, out_dir, stats, b.concepts_report)
    print(f"Concept models compiled: {stats['disease_count']} diseases.")
    print(f"Checksum: {checksum}")
    print(f"Artifacts written to {out_dir}/ ({len(written)} files).")
    return 0


def _run_templates(args: argparse.Namespace) -> int:
    """Handle ``plantdx templates`` (Template Engine)."""
    import json

    from plantdx.config import load_config
    from plantdx.core.exceptions import PlantDxError
    from plantdx.templates import (
        compute_statistics,
        load_library,
        validate_library,
        write_artifacts,
    )
    from plantdx.templates.validator import TemplateValidationError

    try:
        config = load_config(args.config)
        library = load_library(config.paths.assets["templates"])
        report = validate_library(library)
    except TemplateValidationError as exc:
        print(f"plantdx templates: {exc}", file=sys.stderr)
        return 1
    except PlantDxError as exc:
        print(f"plantdx templates: {exc}", file=sys.stderr)
        return 2

    stats = compute_statistics(library, "valid")
    if args.stats_only:
        print(json.dumps(stats, indent=2, sort_keys=True))
        return 0
    if args.validate_only:
        print(f"templates valid: {stats['template_count']} templates, hash {stats['content_hash']}")
        return 0
    out_dir = _artifact_dir(config, "templates_dir", args.output)
    written = write_artifacts(library, out_dir, stats, report)
    print(f"Templates validated + indexed: {stats['template_count']} templates.")
    print(f"Checksum: {stats['content_hash']}")
    print(f"Artifacts written to {out_dir}/ ({len(written)} files).")
    return 0


def _build_corpus_from_args(args: argparse.Namespace) -> _Bundle:
    """Compile upstream, load templates, and build the (filtered) corpus."""
    from plantdx.corpus import build_corpus
    from plantdx.templates import load_library, validate_library

    b = _compile_concepts(args.config)
    library = load_library(b.config.paths.assets["templates"])
    validate_library(library)
    corpus, report = build_corpus(
        b.models,
        library,
        condition=getattr(args, "condition", None),
        crop=getattr(args, "crop", None),
    )
    b.corpus = corpus
    b.corpus_report = report
    return b


def _run_generate(args: argparse.Namespace) -> int:
    """Handle ``plantdx generate`` (build the caption corpus)."""
    import json

    from plantdx.core.exceptions import PlantDxError
    from plantdx.corpus import compute_statistics, write_artifacts
    from plantdx.corpus.builder import CorpusBuildError

    try:
        b = _build_corpus_from_args(args)
    except (CorpusBuildError, PlantDxError) as exc:
        print(f"plantdx generate: {exc}", file=sys.stderr)
        return 1

    stats = compute_statistics(b.corpus, "valid")
    checksum = b.corpus.provenance["content_hash"]
    if args.stats_only:
        print(json.dumps(stats, indent=2, sort_keys=True))
        return 0
    if args.validate_only:
        print(f"corpus valid: {stats['caption_count']} captions, checksum {checksum}")
        return 0
    out_dir = _artifact_dir(b.config, "corpus_dir", args.output)
    written = write_artifacts(b.corpus, out_dir, stats, b.corpus_report)
    print(
        f"Caption corpus generated: {stats['caption_count']} captions across "
        f"{stats['disease_count']} diseases."
    )
    print(f"Checksum: {checksum}")
    print(f"Artifacts written to {out_dir}/ ({len(written)} files).")
    return 0


def _run_validate(args: argparse.Namespace) -> int:
    """Handle ``plantdx validate`` (independent caption validation)."""
    import json

    from plantdx.core.exceptions import PlantDxError
    from plantdx.corpus.builder import CorpusBuildError

    try:
        b = _build_corpus_from_args(args)
    except (CorpusBuildError, PlantDxError) as exc:
        print(f"plantdx validate: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(b.corpus_report, indent=2, sort_keys=True))
    return 0


def _run_corpus(args: argparse.Namespace) -> int:
    """Handle ``plantdx corpus`` (build corpus + dataset exporters)."""
    from plantdx.core.exceptions import PlantDxError
    from plantdx.corpus import compute_statistics, write_artifacts
    from plantdx.corpus.builder import CorpusBuildError
    from plantdx.exporters import FORMATS, write_all, write_export

    try:
        b = _build_corpus_from_args(args)
    except (CorpusBuildError, PlantDxError) as exc:
        print(f"plantdx corpus: {exc}", file=sys.stderr)
        return 1
    if args.format is not None and args.format not in FORMATS:
        print(
            f"plantdx corpus: unknown format '{args.format}'. Known: {', '.join(FORMATS)}",
            file=sys.stderr,
        )
        return 1

    stats = compute_statistics(b.corpus, "valid")
    corpus_dir = _artifact_dir(b.config, "corpus_dir", args.output)
    write_artifacts(b.corpus, corpus_dir, stats, b.corpus_report)
    exports_dir = _artifact_dir(b.config, "exports_dir", None)
    if args.format is not None:
        write_export(b.corpus, args.format, exports_dir)
        formats_written = [args.format]
    else:
        write_all(b.corpus, exports_dir)
        formats_written = list(FORMATS)
    print(f"Caption corpus built: {stats['caption_count']} captions -> {corpus_dir}/")
    print(f"Exported formats {formats_written} -> {exports_dir}/")
    print(f"Checksum: {b.corpus.provenance['content_hash']}")
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
    if args.command == "vocabulary":
        return _run_vocabulary(args)
    if args.command == "concepts":
        return _run_concepts(args)
    if args.command == "templates":
        return _run_templates(args)
    if args.command == "generate":
        return _run_generate(args)
    if args.command == "validate":
        return _run_validate(args)
    if args.command == "corpus":
        return _run_corpus(args)

    try:
        _not_implemented(args.command)
    except NotImplementedError as exc:  # pragma: no cover - surface behavior
        print(f"plantdx: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
