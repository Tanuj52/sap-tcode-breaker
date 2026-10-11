"""Service layer for the staged pipeline (used by the API and the CLI).

Stages:  uploaded -> analyzed -> reviewed (user context) -> converted -> validated
Each stage can be run on its own (interactive) or all at once with run_all (streamlined).
"""

from __future__ import annotations

import io
import json
import threading
import zipfile
from pathlib import Path

from .analysis.assemble import analyze
from .analysis.pipeline import RunResult, UserContext, run_program
from .config import get_settings
from .ir.models import ProgramAnalysis
from .knowledge.kb import KnowledgeBase
from .knowledge.models import ProjectSettings
from .storage.projects import ConvertOptions, Project, ProjectContext, ProjectStore

_lock = threading.Lock()
_runs: dict[str, RunResult] = {}


def store() -> ProjectStore:
    return ProjectStore()


def pack_dirs(packs: list[str]) -> list[Path]:
    root = get_settings().packs_dir
    out = []
    for p in packs:
        path = Path(p)
        out.append(path if path.is_absolute() else root / p)
    return out


def list_packs() -> list[dict]:
    root = get_settings().packs_dir
    out = []
    for d in sorted(root.iterdir()) if root.exists() else []:
        if d.is_dir() and not d.name.startswith("_"):
            kb = KnowledgeBase()
            kb._load_pack(d)  # noqa: SLF001 - summary only
            s = kb.packs[-1]
            out.append({"name": d.name, "manifest": s.manifest, "tables": s.tables, "ddic_fields": s.ddic_fields,
                        "fm_sources": s.fm_sources, "gold_pairs": s.gold_pairs, "issues": [i.__dict__ for i in s.issues]})
    return out


_DEFAULT_TO_SETTING = {"source_database": "target_database", "source_schema": "target_schema", "view_database": "view_database",
                       "view_schema": "view_schema", "table_pattern": "table_pattern", "source_system": "source_system",
                       "client": "client", "language": "language", "confidential": "confidential", "infer_fields": "infer_fields"}


def app_defaults() -> dict:
    from . import app_settings

    d = app_settings.load().defaults
    return {dst: getattr(d, src) for src, dst in _DEFAULT_TO_SETTING.items() if getattr(d, src) not in (None, "")}


def knowledge(p: Project) -> tuple[KnowledgeBase, ProjectSettings]:
    """Settings precedence: app defaults (Settings page) < knowledge-pack manifests < project overrides."""
    kb = KnowledgeBase.load(pack_dirs(p.packs), library=True)
    merged = app_defaults()
    for pack in kb.packs:
        merged.update({k: v for k, v in pack.manifest.items() if k in ProjectSettings.model_fields and v not in (None, "")})
    merged.update({k: v for k, v in p.settings.items() if v not in (None, "") and k in ProjectSettings.model_fields})
    merged["packs"] = [pk.name for pk in kb.packs]
    return kb, ProjectSettings(**merged)


def use_catalog(p: Project) -> bool:
    from . import app_settings

    v = p.settings.get("use_catalog")
    return app_settings.load().defaults.use_catalog if v in (None, "") else bool(v)


def catalog_for(p: Project, settings: ProjectSettings, refresh: bool = False) -> dict | None:
    """Live table/column metadata of the source schema for the tables the program references (cached per project)."""
    st = store()
    if not (use_catalog(p) and settings.target_database and settings.target_schema):
        return None
    from .knowledge.inference import referenced_tables

    tables = set(referenced_tables("\n".join(st.files(p).values())))
    kb = KnowledgeBase.load(pack_dirs(p.packs), library=True)
    tables |= {m.new_table.upper() for t in list(tables) if (m := kb.s4_mapping_for(t)) is not None and m.new_table}
    tables = sorted(tables)
    source = f"{settings.target_database}.{settings.target_schema}".upper()
    cached = st.read_artifact(p, "catalog.json")
    if cached and not refresh:
        doc = json.loads(cached)
        if doc.get("source") == source and doc.get("pattern") == settings.table_pattern and set(tables) <= set(doc.get("asked", [])):
            return doc
    try:
        from .knowledge.catalog import fetch_catalog
        from .snowflake_client import get_connection

        doc = fetch_catalog(get_connection().cursor(), settings.target_database, settings.target_schema, settings, tables)
        doc["asked"] = tables
        doc["pattern"] = settings.table_pattern
        doc["error"] = None
    except Exception as exc:  # noqa: BLE001 - no connection / no access: inference only
        doc = {"source": source, "tables": {}, "asked": [], "error": " ".join(str(exc).split())[:300]}
    st.write_artifact(p, "catalog.json", doc)
    return doc


def user_context(p: Project) -> UserContext:
    c = p.context
    return UserContext(fm_sources=dict(c.fm_sources), fm_hints=dict(c.fm_hints), business_names={k.upper(): v for k, v in c.business_names.items()},
                       table_renames={k.upper(): v for k, v in c.table_renames.items()}, notes=c.notes, output_table=c.output_table)


# ---------------------------------------------------------------------- stages
def stage_analyze(pid: str, refresh_catalog: bool = False) -> ProgramAnalysis:
    st = store()
    p = st.get(pid)
    kb, settings = knowledge(p)
    ctx = user_context(p)
    opts = p.convert
    catalog = catalog_for(p, settings, refresh_catalog)
    run = run_program(st.files(p), kb, settings, ctx, p.main, opts.mode, opts.view_name, catalog)
    with _lock:
        _runs[pid] = run
    a = analyze(run, ctx, opts.mode, opts.view_name)
    a.catalog = {"source": (catalog or {}).get("source"), "tables": len((catalog or {}).get("tables") or {}),
                 "error": (catalog or {}).get("error"), "enabled": catalog is not None}
    run.catalog_summary = a.catalog  # type: ignore[attr-defined] - carried into the convert stage
    st.write_artifact(p, "analysis.json", a.model_dump(mode="json"))
    if a.sql:
        st.write_artifact(p, "output.sql", a.sql)
    p.summary = {"lines": a.stats.lines, "tables": a.stats.tables, "relations": a.stats.relations,
                 "sql_status": a.sql_status, "llm_steps": a.stats.llm_relations, "program": a.name,
                 "programs": [x.name for x in run.ingest.programs] or [a.name]}
    st.mark(p, "analyzed", f"{a.stats.statements} statements, {a.stats.relations} steps, SQL {a.sql_status}")
    return a


def update_context(pid: str, context: ProjectContext | None = None, settings: dict | None = None,
                   convert: ConvertOptions | None = None, packs: list[str] | None = None, main=...) -> Project:
    st = store()
    p = st.get(pid)
    if main is not ...:
        p.main = main or None
    if context is not None:
        p.context = context
    if settings is not None:
        p.settings = {**p.settings, **settings}
    if convert is not None:
        p.convert = convert
    if packs is not None:
        p.packs = packs
    st.mark(p, "reviewed", "context updated")
    return p


def stage_convert(pid: str, options: ConvertOptions | None = None) -> dict:
    from .llm.client import LLMError, resolve
    from .translate.llm_translator import fill_unresolved, rerender

    st = store()
    p = st.get(pid)
    if options is not None:
        p.convert = options
        st.save(p)
    opts = p.convert
    stage_analyze(pid)  # always re-run with the latest context (cheap, deterministic)
    p = st.get(pid)
    run = _runs[pid]
    steps = []
    error = None
    if opts.use_llm and run.sql is not None and run.sql.status != "deterministic":
        from . import app_settings

        model = opts.model or app_settings.load().defaults.model or get_settings().default_model
        try:
            from .translate.llm_translator import compile_verifier

            verify = None
            try:
                from . import app_settings
                from .snowflake_client import get_connection

                d = app_settings.load().defaults
                verify = compile_verifier(get_connection().cursor(), run.kb, run.settings, d.validation_database, d.validation_schema)
            except Exception:  # noqa: BLE001 - no Snowflake: syntax checks only
                verify = None
            steps = [s.__dict__ for s in fill_unresolved(run, resolve(model), user_context(p), verify=verify)]
        except LLMError as exc:
            error = str(exc)
        rerender(run, opts.mode, opts.view_name)
    a = analyze(run, user_context(p), opts.mode, opts.view_name)
    a.catalog = getattr(run, "catalog_summary", {}) or {}
    for r in a.relations:
        rel = next((x for x in run.interp.relations if x.id == r.id), None)
        if rel is not None and rel.llm_sql:
            r.llm_model = next((n.split("by ")[-1] for n in rel.notes if n.startswith("translated by")), None)
    st.write_artifact(p, "analysis.json", a.model_dump(mode="json"))
    if a.sql:
        st.write_artifact(p, "output.sql", a.sql)
    st.write_artifact(p, "llm_steps.json", steps)
    p.summary.update({"sql_status": a.sql_status, "llm_steps": len(steps)})
    st.mark(p, "converted", f"SQL {a.sql_status}" + (f"; LLM error: {error}" if error else ""))
    return {"sql": a.sql, "status": a.sql_status, "mode": opts.mode, "steps": steps, "error": error,
            "unresolved": a.unresolved, "relations": [r.model_dump(mode="json") for r in a.relations]}


def stage_validate(pid: str, data_schema: str | None = None, gold_sql: str | None = None) -> dict:
    from .validate.checks import validate

    from . import app_settings

    st = store()
    p = st.get(pid)
    kb, settings = knowledge(p)
    sql = st.read_artifact(p, "output.sql")
    if not sql:
        raise ValueError("Convert the project first")
    run = _runs.get(pid)
    if run is None:
        stage_analyze(pid)
        run = _runs.get(pid)
    gold_kb = kb
    if run is not None and run.kb is not None:
        kb, settings = run.kb, run.settings
    if gold_sql is None:
        g = gold_kb.gold_for(p.summary.get("program") or "")
        gold_sql = g.sql if g else None
        if gold_sql is None:
            sample_gold = get_settings().repo_root / "samples" / "gold" / f"{(p.summary.get('program') or '').lower()}.sql"
            gold_sql = sample_gold.read_text(encoding="utf-8") if sample_gold.exists() else None
    if data_schema is None and settings.target_database and settings.target_schema:
        data_schema = f"{settings.target_database}.{settings.target_schema}"
    cur = None
    try:
        from .snowflake_client import get_connection

        cur = get_connection().cursor()
    except Exception:  # noqa: BLE001 - validation still runs offline checks
        cur = None
    d = app_settings.load().defaults
    rep = validate(sql, kb, settings, cur, gold_sql, data_schema if gold_sql else None, d.validation_database, d.validation_schema)
    out = rep.as_dict()
    out["gold_available"] = gold_sql is not None
    st.write_artifact(p, "validation.json", out)
    p.summary["validated"] = rep.ok
    st.mark(p, "validated", "all checks passed" if rep.ok else "checks failed")
    return out


def run_all(pid: str, options: ConvertOptions | None = None, validate_sql: bool = True) -> dict:
    """Streamlined mode: analyze -> convert (LLM for leftovers) -> validate."""
    conv = stage_convert(pid, options)
    result = {"convert": conv}
    if validate_sql and conv.get("sql"):
        result["validation"] = stage_validate(pid)
    return result


def get_analysis(pid: str) -> dict | None:
    st = store()
    p = st.get(pid)
    raw = st.read_artifact(p, "analysis.json")
    return json.loads(raw) if raw else None


def export_zip(pid: str) -> bytes:
    st = store()
    p = st.get(pid)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name in ("output.sql", "analysis.json", "validation.json", "llm_steps.json"):
            data = st.read_artifact(p, name)
            if data:
                z.writestr(name, data)
        z.writestr("project.json", p.model_dump_json(indent=2))
        a = get_analysis(pid)
        if a:
            z.writestr("REPORT.md", report_markdown(p, a))
        for f, content in st.files(p).items():
            z.writestr(f"source/{f}", content)
    return buf.getvalue()


def report_markdown(p: Project, a: dict) -> str:
    lines = [f"# Conversion report: {a['name']}", "", f"Project: {p.name}  |  Workspace: {p.workspace}  |  SQL status: **{a['sql_status']}**", ""]
    s = a["stats"]
    lines += [f"- Lines: {s['lines']}, statements: {s['statements']}, relevant lines (slice): {s['slice_lines']}",
              f"- Tables: {s['tables']}, routines: {s['routines']} ({s['dead_routines']} unused), steps (CTEs): {s['relations']} "
              f"({s['deterministic_relations']} deterministic, {s['llm_relations']} needing LLM)", ""]
    lines += ["## Tables", "", "| Table | Business name | Columns used |", "|---|---|---|"]
    for t in a["tables"]:
        if t["reads"] or t["writes"]:
            lines.append(f"| {t['name']} | {t['business_name']} | {', '.join(c['name'] for c in t['columns'])} |")
    if a.get("output"):
        lines += ["", "## Output columns", "", "| Column | Business name | Source |", "|---|---|---|"]
        for c in a["output"]["columns"]:
            if not c["hidden"]:
                src = ", ".join(f"{l['table']}.{l['field']}" for l in c["lineage"]) + (" (derived)" if c["derived"] else "")
                lines.append(f"| {c['name']} | {c['business_name']} | {src} |")
    lines += ["", "## Findings", ""]
    for f in a["findings"]:
        loc = f" ({f['loc']['file']}:{f['loc']['line']})" if f.get("loc") else ""
        lines.append(f"- **{f['severity']}** {f['code']}: {f['message']}{loc}")
    lines += ["", "## SQL", "", "```sql", a.get("sql") or "-- not generated", "```"]
    return "\n".join(lines)


def lineage_csv(a: dict) -> str:
    import csv

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["output_column", "business_name", "source_table", "source_field", "derived", "expression"])
    for c in (a.get("output") or {}).get("columns", []):
        lin = c.get("lineage") or [{}]
        for l in lin:
            w.writerow([c["name"], c.get("business_name", ""), l.get("table", ""), l.get("field", ""), c.get("derived", False), c.get("sql", "")])
    return buf.getvalue()


def knowledge_gaps(pid: str | None = None) -> dict:
    """What the analyses could not resolve from any knowledge source, across projects (or one project).

    tables: referenced tables whose fields came only from the code (or nowhere) - not in the Snowflake
            schema, the library, a pack or the dictionary - plus known tables without a description.
    fms:    function modules with no known behaviour and no source.
    `filled` = knowledge added since the analysis ran (re-analyze the project to use it).
    """
    from .knowledge.models import Provenance

    st = store()
    projects = [st.get(pid)] if pid else st.list()
    kbs: dict[tuple, KnowledgeBase] = {}
    tables: dict[str, dict] = {}
    fms: dict[str, dict] = {}
    scanned = 0
    for p in projects:
        raw = st.read_artifact(p, "analysis.json")
        if not raw:
            continue
        scanned += 1
        a = json.loads(raw)
        key = tuple(p.packs)
        kb = kbs.get(key) or kbs.setdefault(key, KnowledgeBase.load(pack_dirs(p.packs), library=True))
        ref = {"id": p.id, "name": p.name}
        for t in a.get("tables") or []:
            if not (t.get("reads") or t.get("writes") or t.get("in_slice")):
                continue
            prov = t.get("provenance")
            if prov in ("inferred", "unresolved") or not t.get("known"):
                reason = "missing"
            elif not t.get("description"):
                reason = "no_description"
            else:
                continue
            now_info = kb.table(t["name"])
            exists = now_info is not None and now_info.source not in (Provenance.INFERRED, Provenance.UNRESOLVED)
            g = tables.setdefault(t["name"], {"name": t["name"], "reason": reason, "columns": set(), "projects": [], "in_slice": False,
                                              "_defined": True, "_described": True})
            g["columns"] |= {c["name"] for c in t.get("columns") or []}
            g["in_slice"] = g["in_slice"] or bool(t.get("in_slice"))
            g["_defined"] = g["_defined"] and exists
            g["_described"] = g["_described"] and exists and bool(now_info.description)
            if reason == "missing":
                g["reason"] = "missing"
            if ref not in g["projects"]:
                g["projects"].append(ref)
        for c in a.get("calls") or []:
            if c.get("kind") != "function" or c.get("resolved") or c.get("target", "").startswith("("):
                continue
            name = c["target"]
            filled = kb.fm(name) is not None or kb.fm_source(name) is not None
            g = fms.setdefault(name, {"name": name, "filled": filled, "projects": [], "calls": 0, "reachable": False})
            g["calls"] += 1
            g["filled"] = g["filled"] and filled
            g["reachable"] = g["reachable"] or bool(c.get("reachable"))
            if ref not in g["projects"]:
                g["projects"].append(ref)
    for g in tables.values():
        defined, described = g.pop("_defined"), g.pop("_described")
        g["filled"] = defined if g["reason"] == "missing" else described
    tl = sorted(tables.values(), key=lambda g: (g["filled"], g["reason"] != "missing", not g["in_slice"], -len(g["projects"]), g["name"]))
    for g in tl:
        g["columns"] = sorted(g["columns"])
    fl = sorted(fms.values(), key=lambda g: (g["filled"], not g["reachable"], -g["calls"], g["name"]))
    return {"tables": tl, "fms": fl, "projects_scanned": scanned}


def samples() -> list[dict]:
    root = get_settings().repo_root / "samples" / "abap"
    out = []
    for d in sorted(root.iterdir()) if root.exists() else []:
        if d.is_dir():
            files = sorted(str(f.relative_to(d)) for f in d.rglob("*.abap"))
            out.append({"name": d.name, "files": files, "lines": sum((d / f).read_text().count("\n") for f in files)})
    return out


def sample_files(name: str) -> dict[str, str]:
    root = get_settings().repo_root / "samples" / "abap" / name
    if not root.is_dir() or ".." in name:
        raise KeyError(name)
    return {str(f.relative_to(root)): f.read_text(encoding="utf-8") for f in root.rglob("*.abap")}
