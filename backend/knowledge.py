"""Knowledge library operations: browse, import in any format, fetch from Snowflake, AI proposals, gaps and raw files."""

from __future__ import annotations

from .core import ServiceError, clean

from tcode_breaker import app_settings, service
from tcode_breaker.config import get_settings
from tcode_breaker.knowledge import library
from tcode_breaker.knowledge.importer import ImportDraft, parse, preview, table_from_json, table_json
from tcode_breaker.knowledge.kb import KnowledgeBase
from tcode_breaker.knowledge.models import FM_KINDS, Provenance, S4Mapping, fm_from_spec

MAX = 20 * 1024 * 1024
RAW_FILES = [("tables.yaml", "Tables and fields"), ("fm_catalog.yaml", "Function module behaviour"), ("s4_mappings.yaml", "ECC → S/4 table remaps")]
VERIFIED = (Provenance.BUILTIN, Provenance.CLIENT_PACK, Provenance.LIBRARY, Provenance.CATALOG)

TEMPLATES = {
    "tables.csv": ("text/csv", "TABNAME,FIELDNAME,KEYFLAG,DATATYPE,LENG,DECIMALS,REFFIELD,DDTEXT,TABTEXT\n"
                               "ZSD_ORDERS,MANDT,X,CLNT,3,0,,Client,Custom sales order header\n"
                               "ZSD_ORDERS,VBELN,X,CHAR,10,0,,Sales document,Custom sales order header\n"
                               "ZSD_ORDERS,NETWR,,CURR,15,2,WAERK,Net value,Custom sales order header\n"
                               "ZSD_ORDERS,WAERK,,CUKY,5,0,,Document currency,Custom sales order header\n"
                               "ZSD_ORDERS,ERDAT,,DATS,8,0,,Created on,Custom sales order header\n"),
    "tables.json": ("application/json", '{\n  "tables": [\n    {\n      "name": "ZSD_ORDERS",\n      "description": "Custom sales order header",\n'
                                        '      "module": "SD",\n      "key": ["MANDT", "VBELN"],\n      "fields": [\n'
                                        '        {"name": "MANDT", "type": "CLNT", "length": 3, "description": "Client"},\n'
                                        '        {"name": "VBELN", "type": "CHAR", "length": 10, "description": "Sales document"},\n'
                                        '        {"name": "NETWR", "type": "CURR", "length": 15, "decimals": 2, "ref": "WAERK", "description": "Net value"},\n'
                                        '        {"name": "WAERK", "type": "CUKY", "length": 5, "description": "Document currency"}\n'
                                        '      ]\n    }\n  ]\n}\n'),
    "function_modules.yaml": ("application/x-yaml", "function_modules:\n  Z_GET_REGION_TEXT:\n    kind: lookup\n    output: EV_TEXT\n"
                                                     "    sql: \"T005U.BEZEI joined on LAND1 = {IV_LAND1} AND BLAND = {IV_REGIO} AND SPRAS = {LANGUAGE}\"\n"
                                                     "    tables: [T005U]\n    note: Region name for a country/region\n"
                                                     "  Z_ROUND_QTY:\n    kind: expression\n    output: EV_QTY\n    sql: \"ROUND({IV_QTY}, 0)\"\n"
                                                     "    note: Rounds a quantity to whole units\n"),
}


def kb() -> KnowledgeBase:
    return KnowledgeBase.load(library=True)


def cursor():
    from tcode_breaker.snowflake_client import get_connection

    try:
        return get_connection().cursor()
    except Exception as exc:  # noqa: BLE001
        raise ServiceError(f"Snowflake not connected: {clean(exc)}") from exc


def with_sources(d: ImportDraft, extra: dict | None = None) -> dict:
    out = preview(d, kb())
    out["fm_sources"] = [{"name": n, "lines": s.count("\n") + 1, "source": s} for n, s in d.fm_sources.items()]
    return {**out, **(extra or {})}


# ---------------------------------------------------------------------- browse
def overview() -> dict:
    k = kb()
    lib = k.library
    by_source: dict[str, int] = {}
    for t in k.tables.values():
        by_source[t.source.value] = by_source.get(t.source.value, 0) + 1
    return {"stats": k.stats(), "packs": service.list_packs(), "by_source": by_source,
            "library": {"path": str(library.library_dir()), "tables": lib.tables if lib else 0,
                        "function_modules": lib.function_modules if lib else 0, "fm_sources": len(lib.fm_sources) if lib else 0,
                        "issues": [i.__dict__ for i in lib.issues] if lib else []},
            "history": library.history(15)}


def tables() -> list[dict]:
    return [{"name": t.name, "description": t.description, "module": t.module, "release": t.release, "fields": len(t.fields),
             "key": t.key, "source": t.source.value, "origin": t.origin, "updated": t.updated, "fields_complete": t.fields_complete}
            for t in sorted(kb().tables.values(), key=lambda x: x.name)]


def table(name: str) -> dict | None:
    t = kb().table(name)
    if t is None:
        return None
    base = KnowledgeBase.load().table(name)
    return {"name": t.name, **table_json(t), "in_library": t.source in (Provenance.LIBRARY, Provenance.AI), "builtin": base is not None}


def fms() -> list[dict]:
    k = kb()
    out = []
    for section, items in (("function_modules", k.fms), ("methods", k.methods)):
        for f in sorted(items.values(), key=lambda x: x.name):
            out.append({"section": section, **f.model_dump(mode="json"), "has_source_code": f.has_source_code or k.fm_source(f.name) is not None})
    return out


def fm_source(name: str) -> str | None:
    return library.fm_source(name) or kb().fm_source(name)


def history(limit: int = 100) -> list[dict]:
    return library.history(limit)


def gaps(project: str | None = None) -> dict:
    try:
        return service.knowledge_gaps(project)
    except KeyError:
        return {"tables": [], "fms": [], "projects_scanned": 0}


# ---------------------------------------------------------------------- import
def import_any(text: str = "", filename: str | None = None, data: bytes | None = None, default_table: str = "", ai: bool = False) -> dict:
    try:
        if data is not None:
            if len(data) > MAX:
                raise ServiceError("File is larger than 20 MB")
            d = parse(data, filename, default_table or None, origin="ai" if ai else f"import:{filename}")
        else:
            if not text.strip():
                raise ServiceError("Paste something or choose a file")
            d = parse(text, None, default_table or None, origin="ai" if ai else "import:paste")
    except ServiceError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise ServiceError(f"Could not read the input: {clean(exc)}") from exc
    return with_sources(d)


# ---------------------------------------------------------------------- Snowflake
def ddic_status(database: str, schema: str, pattern: str = "{table}") -> dict:
    from tcode_breaker.knowledge.fetch import ddic_status as status

    try:
        return status(cursor(), database, schema, pattern)
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "tables": {}, "error": clean(exc)}


def fetch_snowflake(database: str, schema: str, names: list[str], all_tables: bool = False, pattern: str = "{table}") -> dict:
    from tcode_breaker.knowledge.fetch import from_information_schema

    if not names and not all_tables:
        raise ServiceError("Name the tables to fetch, or choose all tables in the schema")
    if not database or not schema:
        raise ServiceError("Choose the database and schema")
    try:
        got, missing = from_information_schema(cursor(), database, schema, None if all_tables else names, kb(), pattern)
    except ServiceError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise ServiceError(clean(exc)) from exc
    d = ImportDraft(format="snowflake", tables=got)
    if missing:
        d.warnings.append(f"Not found in {database}.{schema}: {', '.join(missing)}")
    return with_sources(d, {"missing": missing, "source": f"{database}.{schema}".upper()})


def fetch_ddic(database: str, schema: str, names: list[str], pattern: str = "{table}", language: str = "E") -> dict:
    from tcode_breaker.knowledge.fetch import from_ddic

    if not names:
        raise ServiceError("Name the tables to look up in the replicated DD03L")
    try:
        got, missing = from_ddic(cursor(), database, schema, names, pattern, language)
    except ServiceError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise ServiceError(clean(exc)) from exc
    d = ImportDraft(format="ddic", tables=got)
    if missing:
        d.warnings.append(f"Not in DD03L: {', '.join(missing)}")
    return with_sources(d, {"missing": missing, "source": f"{database}.{schema}".upper()})


def schema_tables(database: str, schema: str, pattern: str = "{table}") -> list[str]:
    from tcode_breaker.knowledge.fetch import list_tables

    try:
        return list_tables(cursor(), database, schema, pattern)
    except ServiceError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise ServiceError(clean(exc)) from exc


# ---------------------------------------------------------------------- AI
def prompt(kind: str, names: list[str], columns: dict[str, list[str]] | None = None, system: str = "S/4HANA") -> str:
    from tcode_breaker.knowledge.ai import prompt as build

    return build(kind, names, columns or {}, system)


def propose(kind: str, names: list[str], model: str | None, columns: dict[str, list[str]] | None = None,
            system: str = "S/4HANA", force: bool = False) -> dict:
    from tcode_breaker.knowledge.ai import generate

    names = [n.strip().upper() for n in names if n.strip()][:60]
    if not names:
        raise ServiceError("Name at least one table or function module")
    k = kb()
    look = k.table if kind == "tables" else k.fm
    known = [n for n in names if look(n) is not None and look(n).source in VERIFIED]
    ask = names if force else [n for n in names if n not in known]
    if not ask:
        return with_sources(ImportDraft(format="ai"), {"calls": [], "model": None, "skipped_known": known})
    model = model or app_settings.load().defaults.model or get_settings().default_model
    try:
        d, calls = generate(kind, ask, model, columns or {}, system)
    except Exception as exc:  # noqa: BLE001
        raise ServiceError(clean(exc)) from exc
    return with_sources(d, {"calls": calls, "model": model, "skipped_known": [] if force else known})


# ---------------------------------------------------------------------- save / delete
def save(tables_: list[dict] | None = None, fms_: list[dict] | None = None, fm_sources: list[dict] | None = None,
         s4: list[dict] | None = None, origin: str = "manual", mode: str = "merge") -> dict:
    base = KnowledgeBase.load(library=False)
    errors: list[str] = []
    parsed = []
    for obj in tables_ or []:
        try:
            parsed.append(table_from_json(obj, obj.get("origin") or origin))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{obj.get('name')}: {clean(exc)}")
    by_origin: dict[str, list] = {}
    for t in parsed:
        by_origin.setdefault(t.origin or origin, []).append(t)
    saved_tables = []
    for o, items in by_origin.items():
        saved_tables += library.save_tables(items, o, mode if mode in ("merge", "replace") else "merge", base.tables)
    saved_fms = []
    for section in ("function_modules", "methods"):
        items = []
        for obj in [x for x in fms_ or [] if (x.get("section") or "function_modules") == section]:
            name = str(obj.get("name") or "").upper().strip()
            if not name or obj.get("kind") not in FM_KINDS:
                errors.append(f"{name or '?'}: kind must be one of {', '.join(FM_KINDS)}")
                continue
            items.append(fm_from_spec(name, {**obj, "origin": obj.get("origin") or origin}, Provenance.LIBRARY))
        if items:
            saved_fms += library.save_fms(items, origin, section)
    saved_src = []
    for obj in fm_sources or []:
        try:
            saved_src += library.save_fm_sources(str(obj.get("source") or ""), origin)
        except ValueError as exc:
            errors.append(f"{obj.get('name')}: {exc}")
    saved_s4 = []
    if s4:
        try:
            saved_s4 = library.save_s4([S4Mapping(**m) for m in s4], origin)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"S/4 remaps: {clean(exc)}")
    return {"tables": saved_tables, "fms": saved_fms, "fm_sources": saved_src, "s4": saved_s4, "errors": errors}


def delete_table(name: str) -> list[str]:
    gone = library.delete_tables([name])
    if not gone:
        raise ServiceError(f"{name.upper()} is not in your library (built-in entries cannot be deleted, only overridden)")
    return gone


def delete_fm(name: str) -> list[str]:
    gone = library.delete_fms([name])
    if not gone:
        raise ServiceError(f"{name.upper()} is not in your library")
    return gone


# ---------------------------------------------------------------------- library files
def export_library() -> bytes:
    return library.export_zip()


def raw_file(name: str) -> str:
    try:
        return library.read_raw(name)
    except KeyError as exc:
        raise ServiceError(f"Unknown library file {name}") from exc


def validate_raw(name: str, text: str) -> list[str]:
    return library.validate_raw(name, text)


def write_raw(name: str, text: str) -> None:
    try:
        library.write_raw(name, text)
    except KeyError as exc:
        raise ServiceError(f"Unknown library file {name}") from exc
    except ValueError as exc:
        raise ServiceError(str(exc)) from exc


def reset_library() -> None:
    library.reset()
