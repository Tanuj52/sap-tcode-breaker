"""Engine bootstrap and every project, pipeline, settings and Snowflake operation used by the Streamlit app."""

from __future__ import annotations

import io
import json
import os
import re
import shutil
import sys
import zipfile
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
APP_DIR = BACKEND_DIR.parent
DATA_DIR = Path(os.environ.get("TCB_DATA_DIR") or APP_DIR / "data").resolve()
PARSER = BACKEND_DIR / "abap_parser.js"


def find_node() -> str | None:
    found = shutil.which(os.environ.get("TCB_NODE_BIN") or "node")
    if found:
        return found
    try:
        import nodejs_wheel
    except ImportError:
        return None
    root = Path(nodejs_wheel.__file__).parent
    for candidate in (root / "bin" / "node", root / "node.exe", root / "bin" / "node.exe"):
        if candidate.exists():
            return str(candidate)
    return None


NODE = find_node()
os.environ["TCB_DATA_DIR"] = str(DATA_DIR)
if NODE:
    os.environ["TCB_NODE_BIN"] = NODE
os.environ["TCB_REPO_ROOT"] = str(BACKEND_DIR)
os.environ["TCB_PACKS_DIR"] = str(BACKEND_DIR / "knowledge-packs")
os.environ["TCB_PARSER_BRIDGE"] = str(PARSER)
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from tcode_breaker import app_settings, service, snowflake_client  # noqa: E402
from tcode_breaker.ingest.normalizer import object_name  # noqa: E402
from tcode_breaker.llm.client import LLMError, complete, list_models, resolve  # noqa: E402
from tcode_breaker.storage.projects import ConvertOptions, ProjectContext  # noqa: E402

VERSION = "0.1.0"
MAX_UPLOAD = 20 * 1024 * 1024
TEXT_EXT = (".abap", ".txt", ".src", ".prog", ".inc")
UI_PREFS = DATA_DIR / "ui.json"


class ServiceError(Exception):
    pass


def clean(exc: Exception, limit: int = 500) -> str:
    return " ".join(str(exc).split())[:limit]


def engine_ready() -> tuple[bool, str]:
    if not PARSER.exists():
        return False, f"The ABAP parser bundle is missing ({PARSER})."
    if not NODE:
        return False, ("Node.js 18+ is needed to parse ABAP. Install it, or `pip install nodejs-wheel-binaries` "
                       "(already listed in requirements.txt), then restart the app.")
    return True, ""


# ---------------------------------------------------------------------- ui preferences
def ui_prefs() -> dict:
    try:
        return json.loads(UI_PREFS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def save_ui_prefs(**values) -> None:
    prefs = {**ui_prefs(), **values}
    UI_PREFS.parent.mkdir(parents=True, exist_ok=True)
    UI_PREFS.write_text(json.dumps(prefs, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------- settings
def settings() -> dict:
    return app_settings.public_view(app_settings.load())


def defaults() -> dict:
    return settings()["defaults"]


AUTH_LABEL = {"snowflake": "Password", "programmatic_access_token": "Programmatic access token", "snowflake_jwt": "Key pair (JWT)",
              "externalbrowser": "SSO (browser)", "oauth": "OAuth token"}


def connection_profile() -> dict:
    """What the app connects with, without secrets: kind, who, where and how it signs in."""
    sf = app_settings.load().snowflake
    env_name = os.environ.get("TCB_SNOWFLAKE_CONNECTION") or ""
    if sf.mode == "none":
        return {"kind": "none"}
    if sf.mode == "session" or (sf.mode == "named" and not (sf.connection_name or env_name) and in_snowflake()):
        return {"kind": "session", "label": "Snowflake session", "auth": "Service token mounted by Snowflake",
                "role": sf.custom.role, "warehouse": sf.custom.warehouse, "editable": True}
    if sf.mode == "custom" and sf.custom.account:
        c = sf.custom
        return {"kind": "custom", "label": f"{c.user}@{c.account}", "account": c.account, "user": c.user, "auth": AUTH_LABEL.get(c.authenticator, c.authenticator),
                "role": c.role, "warehouse": c.warehouse, "editable": True}
    name = sf.connection_name or env_name
    if name:
        info = next((x for x in app_settings.connections_toml() if x["name"] == name), {})
        return {"kind": "profile", "label": name, "account": info.get("account", ""), "user": info.get("user", ""),
                "auth": AUTH_LABEL.get(info.get("authenticator") or "snowflake", info.get("authenticator") or ""), "role": info.get("role", ""),
                "warehouse": info.get("warehouse", ""), "editable": False}
    return {"kind": "none"}


def remove_connection() -> None:
    s = app_settings.load()
    s.snowflake = app_settings.SnowflakeSettings(mode="none")
    app_settings.save(s)
    snowflake_client.reset()


def save_settings(patch: dict) -> dict:
    try:
        s = app_settings.merge_update(app_settings.load(), patch)
    except ValueError as exc:
        raise ServiceError(f"Invalid settings: {clean(exc)}") from exc
    app_settings.save(s)
    if "snowflake" in patch:
        snowflake_client.reset()
    return app_settings.public_view(s)


def test_snowflake(form: dict | None = None) -> dict:
    try:
        if form:
            saved = app_settings.load()
            app_settings.save(app_settings.merge_update(saved, {"snowflake": form}))
            try:
                kwargs = snowflake_client.connect_kwargs()
            finally:
                app_settings.save(saved)
            return snowflake_client.test_connection(kwargs)
        return snowflake_client.test_connection()
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": clean(exc)}


def snowflake_status() -> dict:
    try:
        return {"connected": True, **snowflake_client.test_connection()}
    except Exception as exc:  # noqa: BLE001
        return {"connected": False, "error": clean(exc, 300)}


def ident(name: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_$\-\" ]+", name or ""):
        raise ServiceError(f"Invalid identifier: {name}")
    return name if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_$]*", name) else '"' + name.replace('"', '""') + '"'


def sf_rows(sql: str) -> list[dict]:
    try:
        return snowflake_client.query_dicts(sql)[1]
    except Exception as exc:  # noqa: BLE001
        raise ServiceError(clean(exc, 400)) from exc


def databases() -> list[str]:
    return [r["name"] for r in sf_rows("SHOW TERSE DATABASES")]


def schemas(database: str) -> list[str]:
    return [r["name"] for r in sf_rows(f"SHOW TERSE SCHEMAS IN DATABASE {ident(database)}") if r["name"] != "INFORMATION_SCHEMA"]


def models() -> list[dict]:
    return [{"id": m.id, "provider": m.provider, "model": m.model, "context": m.context, "private": m.private,
             "available": m.available, "key_env": m.api_key_env, "kind": m.kind} for m in list_models()]


def test_model(model_id: str) -> dict:
    try:
        c = complete(resolve(model_id), "You are a health check.", "Reply with the single word OK.", max_tokens=5)
        return {"ok": True, "reply": c.text.strip()[:40], "seconds": round(c.seconds, 2)}
    except LLMError as exc:
        return {"ok": False, "error": str(exc)[:500]}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": clean(exc)}


# ---------------------------------------------------------------------- projects
def projects(workspace: str | None = None) -> list[dict]:
    return [p.model_dump(mode="json", exclude={"context"}) for p in service.store().list(workspace)]


def project(pid: str) -> dict | None:
    try:
        return service.store().get(pid).model_dump(mode="json")
    except KeyError:
        return None


def decode_upload(name: str, data: bytes) -> dict[str, str]:
    if len(data) > MAX_UPLOAD:
        raise ServiceError(f"{name} is larger than 20 MB")
    if name.lower().endswith(".zip"):
        out = {}
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for info in z.infolist():
                if info.is_dir() or info.file_size > MAX_UPLOAD or info.filename.startswith("__MACOSX"):
                    continue
                if info.filename.lower().endswith(TEXT_EXT):
                    out[info.filename] = z.read(info).decode("utf-8", errors="replace")
        return out
    return {name: data.decode("utf-8", errors="replace")}


def create_from_uploads(name: str, workspace: str, settings_: dict, uploads: list[tuple[str, bytes]]) -> dict:
    content: dict[str, str] = {}
    for fname, data in uploads:
        content.update(decode_upload(fname, data))
    if not content:
        raise ServiceError("No ABAP files found in the upload")
    return service.store().create(name, content, workspace or "default", [], settings_).model_dump(mode="json")


def split_paste(text: str, name: str, filename: str | None) -> dict[str, str]:
    parts = re.split(r"^\*{2,}\s*FILE:\s*(\S+)\s*$", text, flags=re.MULTILINE)
    files: dict[str, str] = {}
    if len(parts) > 1:
        if parts[0].strip():
            files[(filename or name) + ".abap"] = parts[0]
        for fname, body in zip(parts[1::2], parts[2::2]):
            files[fname if fname.lower().endswith(TEXT_EXT) else fname + ".abap"] = body
    else:
        base = re.sub(r"[^A-Za-z0-9_]", "_", filename or name).strip("_") or "program"
        files[base.lower() + ".abap"] = text
    return files


def create_from_paste(name: str, text: str, filename: str | None, workspace: str, settings_: dict) -> dict:
    text = text.replace("\r\n", "\n")
    if not text.strip():
        raise ServiceError("Paste some ABAP source first")
    if len(text.encode()) > MAX_UPLOAD:
        raise ServiceError("Pasted source is larger than 20 MB")
    files = split_paste(text, name, filename)
    return service.store().create(name, files, workspace or "default", [], settings_).model_dump(mode="json")


def create_from_sample(sample: str, workspace: str = "samples", packs: list[str] | None = None, settings_: dict | None = None) -> dict:
    try:
        files = service.sample_files(sample)
    except KeyError as exc:
        raise ServiceError(f"Unknown sample {sample}") from exc
    return service.store().create(sample, files, workspace, packs if packs is not None else ["demo"], settings_ or {}).model_dump(mode="json")


def delete_project(pid: str) -> None:
    service.store().delete(pid)


def sources(pid: str) -> dict[str, str]:
    st = service.store()
    return {object_name(k): v for k, v in st.files(st.get(pid)).items()}


def update_project(pid: str, context: dict | None = None, settings_: dict | None = None, convert: dict | None = None, main=...) -> dict:
    p = service.update_context(pid, ProjectContext(**context) if context is not None else None, settings_,
                               ConvertOptions(**convert) if convert is not None else None, None, main)
    return p.model_dump(mode="json")


def analyze(pid: str, refresh_catalog: bool = False) -> dict:
    try:
        return service.stage_analyze(pid, refresh_catalog).model_dump(mode="json")
    except ValueError as exc:
        raise ServiceError(str(exc)) from exc


def analysis(pid: str) -> dict | None:
    try:
        return service.get_analysis(pid)
    except KeyError:
        return None


def convert(pid: str, options: dict | None = None) -> dict:
    try:
        return service.stage_convert(pid, ConvertOptions(**options) if options else None)
    except ValueError as exc:
        raise ServiceError(str(exc)) from exc


def validate(pid: str) -> dict:
    try:
        return service.stage_validate(pid)
    except ValueError as exc:
        raise ServiceError(str(exc)) from exc


def last_validation(pid: str) -> dict | None:
    st = service.store()
    raw = st.read_artifact(st.get(pid), "validation.json")
    return json.loads(raw) if raw else None


def export_zip(pid: str) -> tuple[str, bytes]:
    return f"{service.store().get(pid).name}.zip", service.export_zip(pid)


def download(pid: str, kind: str) -> tuple[str, str, str] | None:
    st = service.store()
    p = st.get(pid)
    base = (p.summary.get("program") or p.name).lower()
    if kind == "sql":
        data = st.read_artifact(p, "output.sql")
        name, mime = f"{(p.convert.view_name or base) if p.convert.mode == 'view' else base}.sql", "application/sql"
    elif kind == "report":
        a = service.get_analysis(pid)
        data = service.report_markdown(p, a) if a else None
        name, mime = f"{base}_report.md", "text/markdown"
    elif kind in ("analysis", "validation"):
        data = st.read_artifact(p, f"{kind}.json")
        name, mime = f"{base}_{kind}.json", "application/json"
    elif kind == "lineage":
        a = service.get_analysis(pid)
        data = service.lineage_csv(a) if a else None
        name, mime = f"{base}_lineage.csv", "text/csv"
    else:
        raise ServiceError(f"Unknown download {kind}")
    return (name, data, mime) if data else None


def samples() -> list[dict]:
    return service.samples()


def demo_data_status() -> dict:
    try:
        rows = sf_rows("SHOW TERSE TABLES IN SCHEMA TCODE_BREAKER.SAP_DEMO")
        return {"ready": len(rows) >= 11, "tables": len(rows)}
    except ServiceError as exc:
        return {"ready": False, "tables": 0, "error": str(exc)}


def setup_demo_data() -> dict[str, int]:
    from tcode_breaker.bench.demo_data import setup_demo
    from tcode_breaker.knowledge.kb import KnowledgeBase

    try:
        cur = snowflake_client.get_connection().cursor()
        return setup_demo(cur, KnowledgeBase.load(service.pack_dirs(["demo"])))
    except Exception as exc:  # noqa: BLE001
        raise ServiceError(clean(exc)) from exc


def in_snowflake() -> bool:
    return snowflake_client.in_snowflake()
