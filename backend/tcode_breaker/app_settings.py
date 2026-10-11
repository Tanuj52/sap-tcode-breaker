"""Application settings editable from the UI: Snowflake connection, API keys, defaults.

Stored in <data_dir>/app_settings.json (file mode 0600). Secrets (passwords, tokens, API keys)
are never sent back to the browser; the API returns masked values and `has_*` flags.
"""

from __future__ import annotations

import json
import os
import threading
import tomllib
from pathlib import Path

from pydantic import BaseModel, Field

from .config import get_settings

_lock = threading.Lock()
SECRET_FIELDS = ("password", "token", "private_key_passphrase")


class SnowflakeCustom(BaseModel):
    account: str = ""
    user: str = ""
    authenticator: str = "snowflake"  # snowflake | externalbrowser | programmatic_access_token | snowflake_jwt | oauth
    password: str = ""
    token: str = ""
    private_key_file: str = ""
    private_key_passphrase: str = ""
    role: str = ""
    warehouse: str = ""
    database: str = ""
    schema_: str = Field("", alias="schema")

    model_config = {"populate_by_name": True}


class SnowflakeSettings(BaseModel):
    mode: str = "named"  # named (connections.toml) | custom
    connection_name: str = ""
    custom: SnowflakeCustom = Field(default_factory=SnowflakeCustom)


class CustomProvider(BaseModel):
    """Any OpenAI-compatible endpoint (vLLM, LM Studio, Azure OpenAI proxy, OpenRouter, ...)."""

    name: str
    base_url: str
    api_key: str = ""
    models: list[str] = Field(default_factory=list)
    private: bool = False  # True if the endpoint runs inside your network


class Defaults(BaseModel):
    model: str = "cortex:claude-sonnet-4-5"
    use_llm: bool = True
    mode: str = "select"  # select | view
    source_system: str = "ecc"
    source_database: str = ""  # raw layer (SAP replica)
    source_schema: str = ""
    view_database: str = ""  # gold layer (where CREATE VIEW goes)
    view_schema: str = ""
    table_pattern: str = "{table}"
    client: str = ""
    language: str = "E"
    confidential: bool = True
    infer_fields: bool = True
    use_catalog: bool = True  # read table/column metadata from the source schema
    validation_database: str = "TCODE_BREAKER"
    validation_schema: str = "STUBS"


class AppSettings(BaseModel):
    snowflake: SnowflakeSettings = Field(default_factory=SnowflakeSettings)
    api_keys: dict[str, str] = Field(default_factory=dict)  # env-var name -> key
    providers: list[CustomProvider] = Field(default_factory=list)
    defaults: Defaults = Field(default_factory=Defaults)


def _path() -> Path:
    return get_settings().data_dir / "app_settings.json"


def load() -> AppSettings:
    p = _path()
    if not p.exists():
        s = AppSettings()
        env_conn = get_settings().snowflake_connection
        if env_conn:
            s.snowflake.connection_name = env_conn
        return s
    try:
        return AppSettings.model_validate_json(p.read_text(encoding="utf-8"))
    except ValueError:
        return AppSettings()


def save(s: AppSettings) -> None:
    with _lock:
        p = _path()
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(s.model_dump_json(indent=2, by_alias=True), encoding="utf-8")
        os.chmod(tmp, 0o600)
        tmp.replace(p)


def mask(value: str) -> str:
    if not value:
        return ""
    return "••••" + value[-4:] if len(value) > 8 else "••••"


def public_view(s: AppSettings) -> dict:
    """Settings as shown to the UI: secrets masked."""
    d = json.loads(s.model_dump_json(by_alias=True))
    for f in SECRET_FIELDS:
        v = getattr(s.snowflake.custom, f)
        d["snowflake"]["custom"][f] = mask(v)
        d["snowflake"]["custom"][f"has_{f}"] = bool(v)
    d["api_keys"] = {k: mask(v) for k, v in s.api_keys.items() if v}
    for prov, raw in zip(d["providers"], s.providers):
        prov["api_key"] = mask(raw.api_key)
        prov["has_api_key"] = bool(raw.api_key)
    return d


def merge_update(current: AppSettings, incoming: dict) -> AppSettings:
    """Apply a UI update. Masked / empty secret values keep the stored secret."""
    def keep(new: str | None, old: str) -> str:
        if new is None or new.startswith("••••"):
            return old
        return new

    data = json.loads(current.model_dump_json(by_alias=True))
    sf = incoming.get("snowflake") or {}
    if sf:
        custom_in = sf.get("custom") or {}
        for f in SECRET_FIELDS:
            custom_in[f] = keep(custom_in.get(f), getattr(current.snowflake.custom, f))
        data["snowflake"].update({k: v for k, v in sf.items() if k != "custom"})
        data["snowflake"]["custom"].update({k: v for k, v in custom_in.items() if not k.startswith("has_")})
    if "api_keys" in incoming:
        keys = dict(current.api_keys)
        for k, v in (incoming["api_keys"] or {}).items():
            if v is None or v == "":
                keys.pop(k, None)
            elif not str(v).startswith("••••"):
                keys[k] = v
        data["api_keys"] = keys
    if "providers" in incoming:
        old = {p.name: p for p in current.providers}
        provs = []
        for p in incoming["providers"] or []:
            p = {k: v for k, v in p.items() if not k.startswith("has_")}
            p["api_key"] = keep(p.get("api_key"), old[p["name"]].api_key if p.get("name") in old else "")
            provs.append(p)
        data["providers"] = provs
    if "defaults" in incoming:
        data["defaults"].update(incoming["defaults"] or {})
    return AppSettings.model_validate(data)


def connections_toml() -> list[dict]:
    """Named connections from ~/.snowflake/connections.toml (non-secret fields only)."""
    home = Path(os.environ.get("SNOWFLAKE_HOME", Path.home() / ".snowflake"))
    out = []
    for name in ("connections.toml", "config.toml"):
        p = home / name
        if not p.exists():
            continue
        try:
            doc = tomllib.loads(p.read_text(encoding="utf-8"))
        except (tomllib.TOMLDecodeError, OSError):
            continue
        section = doc.get("connections", doc) if name == "config.toml" else doc
        for cname, c in section.items():
            if isinstance(c, dict) and ("account" in c or "host" in c):
                out.append({"name": cname, "account": c.get("account", ""), "user": c.get("user", ""), "role": c.get("role", ""),
                            "warehouse": c.get("warehouse", ""), "authenticator": c.get("authenticator", "snowflake"),
                            "file": str(p)})
        if out:
            break
    return out


def api_key(env_name: str) -> str | None:
    """API key for a provider: UI-stored key first, then the environment."""
    return load().api_keys.get(env_name) or os.environ.get(env_name)
