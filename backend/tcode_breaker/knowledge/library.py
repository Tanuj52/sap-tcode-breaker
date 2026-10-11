"""The user's knowledge library: a writable pack at data/knowledge/ that every project loads.

Everything added from the Knowledge page (Snowflake fetch, DDIC replica, AI proposals, pasted or
uploaded files, manual edits) lands here, in the same files a knowledge pack uses, so the library
can be exported as a pack and a pack can be imported into the library:

    data/knowledge/
      tables.yaml               tables + fields (base/sap_tables.yaml format, plus origin/updated)
      fm_catalog.yaml           function module / method behaviour
      s4_mappings.yaml          ECC -> S/4 table remaps
      function_modules/*.abap   source of custom function modules
      history.jsonl             change log shown in the UI
"""

from __future__ import annotations

import io
import json
import re
import threading
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

from ..config import get_settings
from .models import FM_KINDS, FieldInfo, FMInfo, S4Mapping, TableInfo, fm_from_spec, Provenance

_lock = threading.RLock()
_NAME = re.compile(r"^[A-Z0-9_/]{1,40}$")
_FM_HEADER = re.compile(r"^\s*FUNCTION\s+([A-Za-z0-9_/]+)\s*\.", re.IGNORECASE | re.MULTILINE)
RAW_FILES = ("tables.yaml", "fm_catalog.yaml", "s4_mappings.yaml")


def library_dir() -> Path:
    return get_settings().data_dir / "knowledge"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


# ---------------------------------------------------------------------- spec <-> model
def field_spec(f: FieldInfo) -> str:
    """FieldInfo -> compact `TYPE(len,dec) [ref=X] Description` notation used by every YAML file."""
    t = (f.ddic_type or "CHAR").upper()
    size = ""
    if f.length:
        size = f"({f.length}" + (f",{f.decimals}" if f.decimals else "") + ")"
    ref = f" ref={f.ref_field.upper()}" if f.ref_field else ""
    desc = " " + " ".join(f.description.split()) if f.description else ""
    return f"{t}{size}{ref}{desc}"


def table_spec(t: TableInfo, origin: str | None = None) -> dict:
    spec: dict = {"description": t.description or ""}
    if t.module:
        spec["module"] = t.module
    if t.release and t.release != "both":
        spec["release"] = t.release
    key = t.key or [n for n, f in t.fields.items() if f.is_key]
    if key:
        spec["key"] = [k.upper() for k in key]
    spec["fields_complete"] = bool(t.fields_complete)
    for attr in ("text_table", "text_of", "key_note"):
        if getattr(t, attr, None):
            spec[attr] = getattr(t, attr)
    spec["origin"] = origin or t.origin or "manual"
    spec["updated"] = now()
    spec["fields"] = {n.upper(): field_spec(f) for n, f in t.fields.items()}
    return spec


def fm_spec(f: FMInfo, origin: str | None = None) -> dict:
    spec: dict = {"kind": f.kind}
    for attr in ("output", "sql", "note", "table_param", "fieldcat_param"):
        v = getattr(f, attr)
        if v:
            spec[attr] = v
    if f.tables:
        spec["tables"] = [t.upper() for t in f.tables]
    spec["origin"] = origin or f.origin or "manual"
    spec["updated"] = now()
    return spec


# ---------------------------------------------------------------------- files
def _path(name: str) -> Path:
    return library_dir() / name


def _read(name: str) -> dict:
    p = _path(name)
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _write(name: str, doc: dict, header: str) -> None:
    p = _path(name)
    p.parent.mkdir(parents=True, exist_ok=True)
    text = header + yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=200)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(p)


_HEADERS = {
    "tables.yaml": "# Your knowledge library - tables. Edited from the Knowledge page; same format as a pack's tables.yaml.\n"
                   "# Field spec: TYPE(len[,dec]) [ref=FIELD] Description\n",
    "fm_catalog.yaml": "# Your knowledge library - function module / method behaviour (same format as base/fm_catalog.yaml).\n",
    "s4_mappings.yaml": "# Your knowledge library - ECC -> S/4HANA table remaps (same format as base/s4_simplification.yaml).\n",
}


def _log(action: str, items: list[str], origin: str | None = None, detail: str = "") -> None:
    p = _path("history.jsonl")
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"at": now(), "action": action, "items": items[:200], "count": len(items), "origin": origin, "detail": detail}) + "\n")


def history(limit: int = 50) -> list[dict]:
    p = _path("history.jsonl")
    if not p.exists():
        return []
    rows = []
    for line in p.read_text(encoding="utf-8").splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return list(reversed(rows))


# ---------------------------------------------------------------------- tables
def save_tables(tables: list[TableInfo], origin: str, mode: str = "merge", base: dict[str, TableInfo] | None = None) -> list[str]:
    """Write tables into the library.

    mode=merge   : incoming fields are added to / override the table's current fields (library entry,
                   else the built-in or pack definition given in `base`); other fields are kept.
    mode=replace : the incoming definition becomes the whole entry.
    """
    with _lock:
        doc = _read("tables.yaml")
        entries = doc.setdefault("tables", {}) or {}
        doc["tables"] = entries
        saved = []
        for t in tables:
            name = t.name.upper()
            if not _NAME.match(name):
                continue
            if mode == "merge":
                current = _library_table(name, entries.get(name)) or ((base or {}).get(name))
                if current is not None:
                    merged = current.model_copy(deep=True)
                    for fname, f in t.fields.items():
                        old = merged.fields.get(fname)
                        if old is not None and origin == "ai" and old.source != Provenance.AI:
                            continue  # an AI proposal never overrides a field from a verified source
                        if old is not None:
                            f = f.model_copy(update={k: getattr(old, k) for k in ("description", "ref_field") if not getattr(f, k) and getattr(old, k)})
                        merged.fields[fname] = f
                    trusted = origin == "ai" and current.source != Provenance.AI
                    for attr in ("description", "module", "text_table", "text_of"):
                        if getattr(t, attr) and not (trusted and getattr(merged, attr)):
                            setattr(merged, attr, getattr(t, attr))
                    if t.key and not (trusted and merged.key):
                        merged.key = t.key
                    merged.fields_complete = t.fields_complete or (merged.fields_complete and current.source != Provenance.BUILTIN)
                    t = merged
            entries[name] = table_spec(t, origin)
            saved.append(name)
        _write("tables.yaml", doc, _HEADERS["tables.yaml"])
        if saved:
            _log("tables saved", saved, origin, mode)
        return saved


def _library_table(name: str, spec: dict | None) -> TableInfo | None:
    if not spec:
        return None
    from .kb import _table_from_spec

    return _table_from_spec(name, spec, Provenance.LIBRARY)


def delete_tables(names: list[str]) -> list[str]:
    with _lock:
        doc = _read("tables.yaml")
        entries = doc.get("tables") or {}
        gone = [n.upper() for n in names if entries.pop(n.upper(), None) is not None]
        doc["tables"] = entries
        _write("tables.yaml", doc, _HEADERS["tables.yaml"])
        if gone:
            _log("tables removed", gone)
        return gone


# ---------------------------------------------------------------------- function modules
def save_fms(fms: list[FMInfo], origin: str, section: str = "function_modules") -> list[str]:
    with _lock:
        doc = _read("fm_catalog.yaml")
        entries = doc.get(section) or {}
        saved = []
        for f in fms:
            name = f.name.upper()
            if f.kind not in FM_KINDS:
                raise ValueError(f"{name}: kind must be one of {', '.join(FM_KINDS)}")
            entries[name] = fm_spec(f, origin)
            saved.append(name)
        doc[section] = entries
        _write("fm_catalog.yaml", doc, _HEADERS["fm_catalog.yaml"])
        if saved:
            _log("function modules saved", saved, origin)
        return saved


def delete_fms(names: list[str]) -> list[str]:
    with _lock:
        doc = _read("fm_catalog.yaml")
        gone = []
        for section in ("function_modules", "methods"):
            entries = doc.get(section) or {}
            gone += [n.upper() for n in names if entries.pop(n.upper(), None) is not None]
            doc[section] = entries
        _write("fm_catalog.yaml", doc, _HEADERS["fm_catalog.yaml"])
        for n in names:
            p = _path(f"function_modules/{_safe(n)}.abap")
            if p.exists():
                p.unlink()
                gone.append(n.upper())
        if gone:
            _log("function modules removed", sorted(set(gone)))
        return sorted(set(gone))


def save_fm_sources(text: str, origin: str = "import") -> list[str]:
    """Store ABAP source containing one or more FUNCTION ... ENDFUNCTION blocks (one file per FM)."""
    blocks = split_function_modules(text)
    if not blocks:
        raise ValueError("No FUNCTION <name>. ... ENDFUNCTION. block found")
    with _lock:
        for name, body in blocks.items():
            p = _path(f"function_modules/{_safe(name)}.abap")
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body, encoding="utf-8")
    _log("FM source saved", list(blocks), origin)
    return list(blocks)


def fm_source(name: str) -> str | None:
    p = _path(f"function_modules/{_safe(name)}.abap")
    return p.read_text(encoding="utf-8") if p.exists() else None


def split_function_modules(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    matches = list(_FM_HEADER.finditer(text))
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunk = text[m.start():end]
        stop = re.search(r"^\s*ENDFUNCTION\s*\.", chunk, re.IGNORECASE | re.MULTILINE)
        out[m.group(1).upper()] = (chunk[: stop.end()] if stop else chunk).strip() + "\n"
    return out


def _safe(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", name.upper().strip("/")) or "FM"


# ---------------------------------------------------------------------- s4 mappings
def save_s4(mappings: list[S4Mapping], origin: str = "manual") -> list[str]:
    with _lock:
        doc = _read("s4_mappings.yaml")
        current = {m.get("id"): m for m in doc.get("mappings") or []}
        for m in mappings:
            current[m.id] = m.model_dump(exclude_defaults=False)
        doc["mappings"] = list(current.values())
        _write("s4_mappings.yaml", doc, _HEADERS["s4_mappings.yaml"])
    ids = [m.id for m in mappings]
    _log("S/4 remaps saved", ids, origin)
    return ids


# ---------------------------------------------------------------------- raw files
def read_raw(name: str) -> str:
    if name not in RAW_FILES:
        raise KeyError(name)
    p = _path(name)
    if p.exists():
        return p.read_text(encoding="utf-8")
    skeleton = {"tables.yaml": "tables: {}\n", "fm_catalog.yaml": "function_modules: {}\nmethods: {}\n", "s4_mappings.yaml": "mappings: []\n"}
    return _HEADERS[name] + skeleton[name]


def validate_raw(name: str, text: str) -> list[str]:
    """Problems that would stop the file from loading; empty list = OK."""
    from .kb import _table_from_spec

    try:
        doc = yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        return [f"YAML syntax: {exc}"]
    if not isinstance(doc, dict):
        return ["Top level must be a mapping"]
    errors = []
    if name == "tables.yaml":
        for tab, spec in (doc.get("tables") or {}).items():
            if not isinstance(spec, dict):
                errors.append(f"{tab}: entry must be a mapping")
                continue
            try:
                t = _table_from_spec(str(tab), spec, Provenance.LIBRARY)
                missing = [k for k in t.key if k not in t.fields]
                if missing:
                    errors.append(f"{tab}: key field(s) {', '.join(missing)} not in fields")
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{tab}: {exc}")
    elif name == "fm_catalog.yaml":
        for section in ("function_modules", "methods"):
            for fm, spec in (doc.get(section) or {}).items():
                if not isinstance(spec, dict) or spec.get("kind") not in FM_KINDS:
                    errors.append(f"{fm}: kind must be one of {', '.join(FM_KINDS)}")
                    continue
                try:
                    fm_from_spec(str(fm), spec, Provenance.LIBRARY)
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"{fm}: {exc}")
    elif name == "s4_mappings.yaml":
        for i, m in enumerate(doc.get("mappings") or []):
            try:
                S4Mapping(**m)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"mapping #{i + 1}: {exc}")
    return errors


def write_raw(name: str, text: str) -> None:
    if name not in RAW_FILES:
        raise KeyError(name)
    errors = validate_raw(name, text)
    if errors:
        raise ValueError("; ".join(errors[:10]))
    with _lock:
        p = _path(name)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
    _log(f"{name} edited", [name], "manual")


# ---------------------------------------------------------------------- export / import
def export_zip() -> bytes:
    buf = io.BytesIO()
    root = library_dir()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.yaml", f"name: library\ndescription: Exported knowledge library ({now()})\n")
        if root.exists():
            for p in sorted(root.rglob("*")):
                if p.is_file() and p.suffix != ".tmp" and p.name != "history.jsonl":
                    z.write(p, str(p.relative_to(root)))
    return buf.getvalue()


def reset() -> None:
    with _lock:
        root = library_dir()
        if root.exists():
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup = root.parent / f"knowledge_backup_{stamp}"
            root.rename(backup)
    _log("library reset (backup kept)", [])
