# <AI-Generated START>
"""Configuration loading for ollama-evals.

Precedence for the Ollama endpoint (highest first):
  1. OLLAMA_BASE_URL environment variable
  2. base_url in the loaded YAML (models.local.yaml preferred over models.yaml)
  3. built-in default http://127.0.0.1:11434/v1

The committed config never contains a personal host — a LAN host (e.g. a Mac mini)
belongs in the env var or a gitignored models.local.yaml.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

import yaml

DEFAULT_BASE_URL = "http://127.0.0.1:11434/v1"


@dataclass(frozen=True)
class JudgeConfig:
    """LLM-as-judge settings. Local by default (fully offline)."""

    provider: str = "local"  # "local" | "remote"
    model: str = "qwen2.5:14b"
    remote_model: str | None = None
    remote_api_key_env: str | None = None


@dataclass(frozen=True)
class Config:
    base_url: str = DEFAULT_BASE_URL
    temperature: float = 0.0
    seed: int = 7
    num_ctx: int = 8192
    models: list[str] = field(default_factory=list)
    judge: JudgeConfig = field(default_factory=JudgeConfig)


def resolve_config_path(search_dir: Path) -> Path | None:
    """Return the config file to use, preferring the gitignored local override."""
    local = search_dir / "models.local.yaml"
    if local.is_file():
        return local
    shared = search_dir / "models.yaml"
    if shared.is_file():
        return shared
    return None


def load_config(path: Path | None = None, env: Mapping[str, str] | None = None) -> Config:
    """Load configuration from ``path`` (if given) and apply the env override."""
    env = os.environ if env is None else env
    raw: dict = {}
    if path is not None:
        raw = yaml.safe_load(Path(path).read_text()) or {}

    defaults = raw.get("defaults") or {}
    judge_raw = raw.get("judge") or {}
    judge = JudgeConfig(
        provider=judge_raw.get("provider", "local"),
        model=judge_raw.get("model", "qwen2.5:14b"),
        remote_model=judge_raw.get("remote_model"),
        remote_api_key_env=judge_raw.get("remote_api_key_env"),
    )

    base_url = env.get("OLLAMA_BASE_URL") or raw.get("base_url") or DEFAULT_BASE_URL

    return Config(
        base_url=base_url,
        temperature=float(defaults.get("temperature", 0.0)),
        seed=int(defaults.get("seed", 7)),
        num_ctx=int(defaults.get("num_ctx", 8192)),
        models=list(raw.get("models") or []),
        judge=judge,
    )
# <AI-Generated END>
