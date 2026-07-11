"""Every package module imports cleanly (no syntax/typing/import-cycle errors)."""

from __future__ import annotations

import importlib

import pytest

MODULES = [
    "plantdx",
    "plantdx.cli",
    "plantdx.__main__",
    "plantdx.audit",
    "plantdx.audit.models",
    "plantdx.audit.discovery",
    "plantdx.audit.images",
    "plantdx.audit.duplicates",
    "plantdx.audit.report",
    "plantdx.audit.engine",
    "plantdx.normalization",
    "plantdx.normalization.models",
    "plantdx.normalization.engine",
    "plantdx.normalization.report",
    "plantdx.core",
    "plantdx.core.enums",
    "plantdx.core.exceptions",
    "plantdx.core.types",
    "plantdx.core.seeding",
    "plantdx.config",
    "plantdx.config.schema",
    "plantdx.config.loader",
    "plantdx.knowledge_base",
    "plantdx.knowledge_base.models",
    "plantdx.knowledge_base.loader",
    "plantdx.ontology",
    "plantdx.ontology.models",
    "plantdx.ontology.builder",
    "plantdx.ontology.concept_schema",
    "plantdx.vocabulary",
    "plantdx.vocabulary.models",
    "plantdx.vocabulary.builder",
    "plantdx.vocabulary.lexicon",
    "plantdx.vocabulary.expander",
    "plantdx.generation",
    "plantdx.generation.models",
    "plantdx.generation.selector",
    "plantdx.generation.templates",
    "plantdx.generation.realizer",
    "plantdx.generation.planner",
    "plantdx.generation.engine",
    "plantdx.validation",
    "plantdx.validation.report",
    "plantdx.validation.validators",
    "plantdx.validation.battery",
    "plantdx.validation.grammar",
    "plantdx.diversity",
    "plantdx.diversity.deduplicator",
    "plantdx.diversity.controller",
    "plantdx.diversity.metrics",
    "plantdx.dataset",
    "plantdx.dataset.serialization",
    "plantdx.dataset.emitter",
    "plantdx.dataset.splits",
    "plantdx.dataset.label_map",
    "plantdx.dataset.instructions",
    "plantdx.dataset.converters",
    "plantdx.qa",
    "plantdx.qa.sampling",
    "plantdx.qa.review",
    "plantdx.qa.acceptance",
    "plantdx.training",
    "plantdx.training.qlora",
    "plantdx.training.mlx_runner",
    "plantdx.evaluation",
    "plantdx.evaluation.metrics",
    "plantdx.evaluation.zero_shot",
    "plantdx.evaluation.compare",
    "plantdx.utils",
    "plantdx.utils.hashing",
    "plantdx.utils.io",
    "plantdx.utils.logging",
    "plantdx.utils.versioning",
]


@pytest.mark.unit
@pytest.mark.parametrize("module", MODULES)
def test_module_imports(module: str) -> None:
    assert importlib.import_module(module) is not None


@pytest.mark.unit
def test_version_is_exposed() -> None:
    import plantdx

    assert isinstance(plantdx.__version__, str)
    assert plantdx.__version__.count(".") == 2
