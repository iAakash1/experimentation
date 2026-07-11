"""Typed configuration schema (Pydantic models).

Mirrors the YAML files under ``configs/``. These models are concrete — they are
the validated contract for configuration. Loading/merging behavior lives in
:mod:`plantdx.config.loader` (stubbed until Milestone 2).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

_Frozen = ConfigDict(extra="forbid", frozen=True)


class LoggingConfig(BaseModel):
    """Console/file logging settings."""

    model_config = _Frozen
    level: str = "INFO"
    rich: bool = True
    json_file: str | None = None


class ReproducibilityConfig(BaseModel):
    """Determinism guardrails (doc 00 §6). Hashing is SHA-256 throughout."""

    model_config = _Frozen
    strict: bool = True
    verify_regeneration: bool = True


class ProjectConfig(BaseModel):
    """Project-level identity and versioning."""

    model_config = _Frozen
    name: str = "plantdx"
    library_version: str = "L1"


class DatasetPath(BaseModel):
    """One dataset's on-disk location and layout."""

    model_config = _Frozen
    name: str
    root: str
    image_glob: str
    classes: int


class PathsConfig(BaseModel):
    """Path mapping layer (``configs/paths.yaml``; spec doc 06)."""

    model_config = ConfigDict(extra="allow", frozen=True)
    knowledge_base: dict[str, str]
    datasets: dict[str, DatasetPath]
    assets: dict[str, str]
    artifact_root: str = "artifacts"
    artifacts: dict[str, str]
    outputs: dict[str, str] = Field(default_factory=dict)


class AntiDomination(BaseModel):
    """Anti-domination caps (doc 00 §7.3)."""

    model_config = _Frozen
    max_template_share: float = 0.08
    max_skeleton_share: float = 0.12
    max_opening_trigram_share: float = 0.15


class GenerationConfig(BaseModel):
    """Caption generation settings (``configs/generation.yaml``)."""

    model_config = ConfigDict(extra="allow", frozen=True)
    global_seed: int = 20260711
    captions_per_image: int = 3
    balance_mode: str = "per_image_fixed"
    t_class: int | None = None
    max_attempts: int = 8
    max_adjectives: int = 3
    hedging_probability: float = 0.9
    severity_conditioned: bool = False
    epsilon_coverage: float = 0.30
    style_distribution: dict[str, float] = Field(default_factory=dict)
    task_distribution: dict[str, float] = Field(default_factory=dict)
    anti_domination: AntiDomination = Field(default_factory=AntiDomination)


class DedupConfig(BaseModel):
    """De-duplication settings (doc 00 §7.5)."""

    model_config = _Frozen
    jaccard_threshold: float = 0.90
    minhash_num_perm: int = 128
    shingle_size: int = 5


class SplitsConfig(BaseModel):
    """Split policy (doc 04 §5)."""

    model_config = _Frozen
    group_by: str = "image"
    stratify_by: str = "disease_id"
    train: float = 0.80
    val: float = 0.10
    test: float = 0.10
    seed: int = 20260711
    build_diagnostic_split: bool = True


class ValidationConfig(BaseModel):
    """Validation battery settings (``configs/validation.yaml``; doc 03).

    The 12 blocking validators are code-defined and always-on
    (:data:`plantdx.validation.validators.ORDERED_VALIDATORS`); the config carries
    only the fallback templates, matching rules, soft checks, grammar, and gates.
    ``max_attempts`` is single-sourced from :class:`GenerationConfig`.
    """

    model_config = ConfigDict(extra="allow", frozen=True)
    fallback_templates: list[str] = Field(default_factory=list)
    soft_checks: list[str] = Field(default_factory=list)


class TrainingConfig(BaseModel):
    """QLoRA / MLX training settings (``configs/training.yaml``; doc 04 §6)."""

    model_config = ConfigDict(extra="allow", frozen=True)
    backend: str = "mlx_vlm"
    precision: str = "qlora"
    defaults: dict[str, object] = Field(default_factory=dict)
    models: dict[str, dict[str, object]] = Field(default_factory=dict)


class PlantDxConfig(BaseModel):
    """The fully-merged, validated PlantDx configuration."""

    model_config = ConfigDict(extra="allow", frozen=True)
    project: ProjectConfig = Field(default_factory=ProjectConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    reproducibility: ReproducibilityConfig = Field(default_factory=ReproducibilityConfig)
    paths: PathsConfig
    generation: GenerationConfig = Field(default_factory=GenerationConfig)
    dedup: DedupConfig = Field(default_factory=DedupConfig)
    diversity_gates: dict[str, float] = Field(default_factory=dict)
    splits: SplitsConfig = Field(default_factory=SplitsConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    training: TrainingConfig = Field(default_factory=TrainingConfig)
