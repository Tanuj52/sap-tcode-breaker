"""Application settings (environment-driven, prefix TCB_)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TCB_", env_file=".env", extra="ignore")

    # Paths
    repo_root: Path = _REPO_ROOT
    data_dir: Path = _REPO_ROOT / "data"
    packs_dir: Path = _REPO_ROOT / "knowledge-packs"
    parser_bridge: Path = _REPO_ROOT / "parser-bridge" / "index.js"
    node_bin: str = "node"

    # Parsing
    abap_version: str = "v757"
    parser_timeout_s: int = 120

    # Snowflake
    snowflake_connection: str | None = None  # name in ~/.snowflake/connections.toml; None = default
    validation_database: str = "TCODE_BREAKER"
    validation_schema: str = "STUBS"

    # LLM
    default_model: str = "cortex:claude-sonnet-4-5"
    llm_timeout_s: int = 180

    # API
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
