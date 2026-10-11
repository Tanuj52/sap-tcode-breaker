"""Render relations into Snowflake SQL: a CTE SELECT or CREATE OR REPLACE VIEW."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..analysis.expr import initial_for, sql_string
from ..analysis.relations import Relation, Source
from ..analysis.symbols import Param

_TOKEN = re.compile(r"__R\d+__")
_PRM = re.compile(r"\bprm\.[a-z_0-9]+")
KIND_SUFFIX = {
    "db_read": "read", "fae_read": "fae", "filter": "filter", "dedup": "dedup", "loop_build": "build", "collect": "agg",
    "modify": "mod", "union": "union", "values": "values", "value_for": "value", "copy": "copy", "empty": "empty",
    "llm": "llm",
}


@dataclass
class OutputColumnSpec:
    name: str
    label: str = ""
    hidden: bool = False


@dataclass
class SqlResult:
    sql: str
    cte_names: dict[str, str] = field(default_factory=dict)  # relation id -> CTE name
    order: list[str] = field(default_factory=list)  # relation ids in CTE order
    status: str = "deterministic"
    unresolved: list[str] = field(default_factory=list)


def ancestry(final: Relation, by_id: dict[str, Relation]) -> list[Relation]:
    seen: set[str] = set()
    order: list[Relation] = []

    def visit(rel: Relation) -> None:
        if rel.id in seen:
            return
        seen.add(rel.id)
        deps = {d for d in rel.inputs() if _TOKEN.fullmatch(d)}
        for text in (rel.raw_sql or "", rel.llm_sql or ""):
            deps |= set(_TOKEN.findall(text))
        for dep in sorted(deps, key=lambda d: int(d[3:-2])):
            if dep in by_id:
                visit(by_id[dep])
        order.append(rel)

    visit(final)
    return order


def params_cte(params: list[Param], used: set[str]) -> str | None:
    cols = []
    for p in params:
        if p.name not in used:
            continue
        if p.kind == "select_option":
            if p.default:
                cols.append(f"ARRAY_CONSTRUCT({_literal(p.default, p.comp.ddic_type)}) AS {p.name.lower()}")
            else:
                cols.append(f"ARRAY_CONSTRUCT() AS {p.name.lower()}")
            continue
        val = _literal(p.default, p.comp.ddic_type) if p.default else initial_for(p.comp.ddic_type, p.comp.length)
        cast = _cast(p.comp.ddic_type, p.comp.length, p.comp.decimals)
        cols.append(f"{val}::{cast} AS {p.name.lower()}")
    if not cols:
        return None
    return "SELECT " + ",\n       ".join(cols)


def _literal(default: str, ddic: str | None) -> str:
    d = default.strip()
    up = d.upper()
    if up in ("SPACE", "ABAP_FALSE"):
        return "''"
    if up == "ABAP_TRUE":
        return "'X'"
    if up == "SY-DATUM":
        return "TO_VARCHAR(CURRENT_DATE(), 'YYYYMMDD')"
    if up == "SY-LANGU":
        return "'E'"
    if d.startswith("'") and d.endswith("'"):
        return sql_string(d[1:-1].replace("''", "'"))
    if re.fullmatch(r"-?\d+(\.\d+)?", d):
        return d if (ddic or "").upper() not in ("CHAR", "NUMC", "DATS", "TIMS") else sql_string(d)
    return sql_string(d)


def _cast(ddic: str | None, length: int | None, decimals: int | None) -> str:
    t = (ddic or "CHAR").upper()
    if t in ("INT1", "INT2", "INT4", "INT8"):
        return "NUMBER"
    if t in ("DEC", "CURR", "QUAN"):
        return f"NUMBER(38,{decimals or 0})"
    if t == "FLTP":
        return "FLOAT"
    return "VARCHAR"


def render(final: Relation, relations: list[Relation], params: list[Param], params_used: set[str],
           output_cols: list[OutputColumnSpec], order_by: list[tuple[str, bool]], mode: str = "select",
           view_name: str | None = None, header: str | None = None) -> SqlResult:
    by_id = {r.id: r for r in relations}
    chain = ancestry(final, by_id)
    names: dict[str, str] = {}
    used_names: set[str] = {"params"}
    last_of_var: dict[str, str] = {}
    for r in chain:
        last_of_var[r.var] = r.id
    for r in chain:
        base = re.sub(r"[^a-z0-9_]", "_", r.var.lower()) or "rel"
        if base[0].isdigit():
            base = "t_" + base
        name = base if last_of_var.get(r.var) == r.id else f"{base}_{KIND_SUFFIX.get(r.kind, r.kind)}"
        cand, n = name, 2
        while cand in used_names:
            cand = f"{name}_{n}"
            n += 1
        used_names.add(cand)
        names[r.id] = cand

    def sub(text: str) -> str:
        return _TOKEN.sub(lambda m: names.get(m.group(0), m.group(0)), text)

    ctes: list[tuple[str, str, Relation | None]] = []
    referenced = set()
    for r in chain:
        texts = [e.sql for e in r.all_exprs()] + [r.raw_sql or "", r.llm_sql or "", r.qualify or ""]
        referenced |= {m.group(0)[4:].upper() for t in texts for m in _PRM.finditer(t)}
    needs_params = any(r.uses_params for r in chain) or bool(referenced)
    pc = params_cte(params, set(params_used) | referenced) if needs_params else None
    if pc:
        ctes.append(("params", pc, None))
    unresolved: list[str] = []
    status = "deterministic"
    for r in chain:
        uses = r.uses_params or any(_PRM.search(e.sql) for e in r.all_exprs()) or bool(r.qualify and _PRM.search(r.qualify))
        if uses and pc and not any(s.kind == "params" for s in r.sources) and r.raw_sql is None and r.llm_sql is None:
            # right after FROM, so every later JOIN ... ON can use prm.*
            r.sources.insert(1 if r.sources else 0, Source("prm", "params", "params", "cross"))
        body = sub(r.body_sql())
        if r.status != "deterministic" and not r.llm_sql:
            status = "needs_llm" if r.status == "needs_llm" else ("partial" if status == "deterministic" else status)
            unresolved.append(f"{names[r.id]}: " + "; ".join(r.notes[:3]))
        if "TCB-UNRESOLVED" in body or "TCB-NEEDS-LLM" in body:
            status = "needs_llm"
        ctes.append((names[r.id], body, r))

    final_name = names[final.id]
    visible = [c for c in output_cols if not c.hidden] or [OutputColumnSpec(c) for c in final.column_names]
    select_cols = ", ".join(c.name.lower() for c in visible) or "*"
    order_sql = ", ".join(f"{c.lower()}{' DESC' if d else ''}" for c, d in order_by if final.col(c) is not None)
    lines: list[str] = []
    if header:
        lines.extend(f"-- {h}" for h in header.splitlines())
    if mode == "view":
        lines.append(f"CREATE OR REPLACE VIEW {view_name or final_name + '_v'} AS")
    lines.append("WITH")
    for i, (name, body, rel) in enumerate(ctes):
        comment = ""
        if rel is not None and rel.label:
            comment = f"-- {rel.label}" + (f" [{rel.status.upper()}]" if rel.status != "deterministic" and not rel.llm_sql else "")
        indented = "\n".join("    " + ln for ln in body.splitlines())
        sep = "," if i < len(ctes) - 1 else ""
        if comment:
            lines.append(f"{comment}")
        lines.append(f"{name} AS (\n{indented}\n){sep}")
    lines.append(f"SELECT {select_cols}\nFROM {final_name}")
    if order_sql and mode != "view":
        lines.append(f"ORDER BY {order_sql}")
    sql = "\n".join(lines) + ";"
    return SqlResult(sql=sql, cte_names=names, order=[r.id for r in chain], status=status, unresolved=unresolved)
