"""Model-agnostic LLM access: Snowflake Cortex + any OpenAI-compatible endpoint."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

import httpx
import yaml

from ..config import get_settings

_PRESETS = Path(__file__).resolve().parent / "models.yaml"


class LLMError(RuntimeError):
    pass


@dataclass
class ModelSpec:
    provider: str
    model: str
    kind: str
    context: int
    private: bool
    base_url: str | None = None
    api_key_env: str | None = None

    @property
    def id(self) -> str:
        return f"{self.provider}:{self.model}"

    api_key: str | None = None  # set for UI-defined custom providers

    @property
    def available(self) -> bool:
        if self.kind == "cortex" or self.api_key:
            return True
        if self.api_key_env:
            from ..app_settings import api_key

            return bool(api_key(self.api_key_env))
        return True


@dataclass
class Completion:
    text: str
    model: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    seconds: float = 0.0


def load_presets() -> dict:
    """Built-in presets + custom OpenAI-compatible providers defined in the app settings."""
    with _PRESETS.open(encoding="utf-8") as fh:
        doc = yaml.safe_load(fh) or {}
    try:
        from ..app_settings import load

        for p in load().providers:
            doc.setdefault("providers", {})[p.name] = {
                "kind": "openai", "base_url": p.base_url, "private": p.private, "_api_key": p.api_key,
                "models": {m: {"context": 32000} for m in p.models}}
    except Exception:  # noqa: BLE001 - settings are optional
        pass
    return doc


def list_models() -> list[ModelSpec]:
    out = []
    for pname, p in (load_presets().get("providers") or {}).items():
        for mname, m in (p.get("models") or {}).items():
            out.append(ModelSpec(pname, mname, p["kind"], int((m or {}).get("context", 8192)), bool(p.get("private")),
                                 p.get("base_url"), p.get("api_key_env"), p.get("_api_key") or None))
    return out


def resolve(model_id: str) -> ModelSpec:
    """'groq:llama-3.3-70b-versatile' or 'cortex:claude-sonnet-4-5'. Unknown models of a known provider are allowed."""
    provider, _, model = model_id.partition(":")
    presets = load_presets().get("providers") or {}
    if provider not in presets:
        raise LLMError(f"Unknown provider '{provider}'. Known: {', '.join(presets)}")
    p = presets[provider]
    m = (p.get("models") or {}).get(model) or {}
    return ModelSpec(provider, model, p["kind"], int(m.get("context", 8192)), bool(p.get("private")), p.get("base_url"),
                     p.get("api_key_env"), p.get("_api_key") or None)


def complete(spec: ModelSpec, system: str, user: str, max_tokens: int = 2000, temperature: float = 0.0) -> Completion:
    t0 = time.time()
    if spec.kind == "cortex":
        out = _cortex(spec, system, user, max_tokens, temperature)
    else:
        out = _openai(spec, system, user, max_tokens, temperature)
    out.seconds = time.time() - t0
    return out


def _cortex(spec: ModelSpec, system: str, user: str, max_tokens: int, temperature: float) -> Completion:
    from ..snowflake_client import cursor

    messages = json.dumps([{"role": "system", "content": system}, {"role": "user", "content": user}])
    options = json.dumps({"temperature": temperature, "max_tokens": max_tokens})
    with cursor() as cur:
        try:
            cur.execute("SELECT SNOWFLAKE.CORTEX.COMPLETE(%s, PARSE_JSON(%s), PARSE_JSON(%s))", (spec.model, messages, options))
            raw = cur.fetchone()[0]
        except Exception as exc:  # noqa: BLE001
            raise LLMError(f"Cortex call failed for {spec.model}: {str(exc).splitlines()[0]}") from exc
    data = json.loads(raw) if isinstance(raw, str) else raw
    choices = data.get("choices") or []
    text = (choices[0].get("messages") or choices[0].get("message") or "") if choices else ""
    if isinstance(text, dict):
        text = text.get("content", "")
    usage = data.get("usage") or {}
    return Completion(text=text, model=spec.id, prompt_tokens=usage.get("prompt_tokens"), completion_tokens=usage.get("completion_tokens"))


def _openai(spec: ModelSpec, system: str, user: str, max_tokens: int, temperature: float) -> Completion:
    from ..app_settings import api_key

    headers = {"Content-Type": "application/json"}
    key = spec.api_key or (api_key(spec.api_key_env) if spec.api_key_env else None)
    if spec.api_key_env and not key:
        raise LLMError(f"No API key for {spec.provider}. Add {spec.api_key_env} in Settings -> Models & keys.")
    if key:
        headers["Authorization"] = f"Bearer {key}"
        if spec.provider == "anthropic":
            headers["x-api-key"] = key
    body = {"model": spec.model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": temperature, "max_tokens": max_tokens}
    url = (spec.base_url or "").rstrip("/") + "/chat/completions"
    last = None
    for attempt in range(4):
        try:
            r = httpx.post(url, headers=headers, json=body, timeout=get_settings().llm_timeout_s)
        except httpx.HTTPError as exc:
            last = str(exc)
            time.sleep(2 ** attempt)
            continue
        if r.status_code == 429 or r.status_code >= 500:
            last = f"HTTP {r.status_code}: {r.text[:200]}"
            time.sleep(min(30, 2 ** (attempt + 1)))
            continue
        if r.status_code >= 400:
            raise LLMError(f"{spec.id}: HTTP {r.status_code}: {r.text[:300]}")
        data = r.json()
        msg = data["choices"][0]["message"]["content"]
        usage = data.get("usage") or {}
        return Completion(text=msg or "", model=spec.id, prompt_tokens=usage.get("prompt_tokens"), completion_tokens=usage.get("completion_tokens"))
    raise LLMError(f"{spec.id}: gave up after retries ({last})")


def approx_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def check_privacy(spec: ModelSpec, confidential: bool) -> None:
    if confidential and not spec.private:
        raise LLMError(f"Project is marked confidential; {spec.id} sends code outside Snowflake. "
                       "Use a Cortex or local (Ollama) model, or set confidential: false for public code.")
