"""Relational model produced by the symbolic interpreter.

Every version of an internal table becomes one Relation, which renders as one CTE.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..parser.ast import Statement
from .expr import SqlExpr
from .symbols import Comp


_REL_TOKEN = re.compile(r"__R\d+__")


@dataclass
class Source:
    alias: str
    kind: str  # db | rel | params
    name: str  # (mapped) DB table name or relation id
    join: str = "from"  # from | inner | left | cross
    on: list[SqlExpr] = field(default_factory=list)
    original: str | None = None  # original DB table before S/4 mapping
    dedup_keys: list[str] | None = None  # wrap in QUALIFY ROW_NUMBER() OVER (PARTITION BY keys) = 1
    dedup_order: list[tuple[str, bool]] = field(default_factory=list)
    extra_filter: list[str] = field(default_factory=list)  # filters on the source itself (e.g. RECORD_TYPE)
    lookup: bool = False  # created by READ TABLE / SELECT SINGLE

    def ref_sql(self) -> str:
        if self.dedup_keys is not None or self.extra_filter:
            inner = f"SELECT * FROM {self.name}"
            if self.extra_filter:
                inner += " WHERE " + " AND ".join(self.extra_filter)
            if self.dedup_keys:
                order = ", ".join(f"{c} {'DESC' if d else 'ASC'}" for c, d in self.dedup_order) or "1"
                inner += f" QUALIFY ROW_NUMBER() OVER (PARTITION BY {', '.join(self.dedup_keys)} ORDER BY {order}) = 1"
            return f"({inner}) {self.alias}"
        return f"{self.name} {self.alias}"


@dataclass
class OutCol:
    name: str
    expr: SqlExpr
    comp: Comp | None = None
    agg: str | None = None  # SUM for COLLECT numeric columns

    @property
    def sql(self) -> str:
        if self.agg == "SUM":
            if self.expr.kind == "lit" and self.expr.sql == "1":
                return "COUNT(*)"
            return f"SUM({self.expr.sql})"
        return self.expr.sql


@dataclass
class Relation:
    id: str
    var: str
    kind: str  # db_read | fae_read | filter | dedup | loop_build | collect | modify | union | values | value_for | copy | empty | llm
    sources: list[Source] = field(default_factory=list)
    columns: list[OutCol] = field(default_factory=list)
    where: list[SqlExpr] = field(default_factory=list)
    distinct: bool = False
    group_all: bool = False
    group_by: list[str] = field(default_factory=list)
    qualify: str | None = None
    union_with: list[tuple[str, SqlExpr | None]] = field(default_factory=list)  # (relation id, guard) appended via UNION ALL
    order_hint: list[tuple[str, bool]] = field(default_factory=list)  # ABAP SORT order valid for this version
    unique_keys: list[list[str]] = field(default_factory=list)
    status: str = "deterministic"  # deterministic | needs_llm | partial
    notes: list[str] = field(default_factory=list)
    stmts: list[Statement] = field(default_factory=list)
    uses_params: bool = False
    label: str = ""
    llm_sql: str | None = None  # SQL body supplied by the LLM translator for needs_llm relations
    is_empty: bool = False
    raw_sql: str | None = None  # full SELECT body (used by values / llm relations)
    having: list[SqlExpr] = field(default_factory=list)
    limit: int | None = None
    abap: str = ""  # ABAP source of the statements behind this relation (LLM context)

    @property
    def column_names(self) -> list[str]:
        return [c.name for c in self.columns]

    def col(self, name: str) -> OutCol | None:
        n = name.upper()
        for c in self.columns:
            if c.name == n:
                return c
        return None

    def inputs(self) -> list[str]:
        out = [s.name for s in self.sources if s.kind in ("rel", "db")]
        out += [u for u, _ in self.union_with]
        texts = [self.qualify or ""] + [s.ref_sql() for s in self.sources if s.kind == "rel"]
        for e in self.all_exprs():
            texts.append(e.sql)
            for dep in e.rels:
                if dep not in out:
                    out.append(dep)
        for t in texts:  # subqueries embedded in expressions reference relations by token
            for dep in _REL_TOKEN.findall(t):
                if dep not in out and dep != self.id:
                    out.append(dep)
        return out

    def all_exprs(self) -> list[SqlExpr]:
        out = [c.expr for c in self.columns] + list(self.where) + list(self.having)
        for s in self.sources:
            out += s.on
        out += [g for _, g in self.union_with if g is not None]
        return out

    def is_unique_on(self, cols: list[str]) -> bool:
        cs = {c.upper() for c in cols}
        return any(k and set(k) <= cs for k in self.unique_keys)

    # ------------------------------------------------------------------ rendering
    def body_sql(self) -> str:
        if self.llm_sql:
            return self.llm_sql.strip().rstrip(";")
        if self.raw_sql is not None:
            return self.raw_sql
        if self.is_empty:
            cols = ", ".join(f"CAST(NULL AS VARCHAR) AS {c.name}" for c in self.columns) or "NULL AS dummy"
            return f"SELECT {cols} WHERE FALSE"
        lines = ["SELECT " + ("DISTINCT " if self.distinct else "") + (",\n       ".join(_col_sql(c) for c in self.columns) or "*")]
        first = True
        for s in self.sources:
            if first:
                lines.append(f"FROM {s.ref_sql()}")
                first = False
                continue
            if s.join == "cross":
                lines.append(f"CROSS JOIN {s.ref_sql()}")
            else:
                kw = "LEFT JOIN" if s.join == "left" else "INNER JOIN"
                on = " AND ".join(e.sql for e in s.on) or "TRUE"
                lines.append(f"{kw} {s.ref_sql()} ON {on}")
        if self.where:
            lines.append("WHERE " + "\n  AND ".join(_wrap(w.sql) for w in self.where))
        if self.group_all:
            lines.append("GROUP BY ALL")
        elif self.group_by:
            lines.append("GROUP BY " + ", ".join(self.group_by))
        if self.having:
            lines.append("HAVING " + " AND ".join(_wrap(h.sql) for h in self.having))
        if self.qualify:
            lines.append(f"QUALIFY {self.qualify}")
        if self.limit is not None:
            lines.append(f"LIMIT {self.limit}")
        sql = "\n".join(lines)
        # Rows kept from earlier versions (APPEND to a non-empty table, or a guarded rebuild)
        for rel_id, guard in self.union_with:
            cols = ", ".join(f"u.{c.lower()}" for c in self.column_names) or "u.*"
            tail = f"\nWHERE {guard.sql}" if guard is not None else ""
            prm = "\nCROSS JOIN params prm" if guard is not None and re.search(r"\bprm\.", guard.sql) else ""
            sql = f"SELECT {cols} FROM {rel_id} u{prm}{tail}\nUNION ALL\n{sql}"
        return sql


def _col_sql(c: OutCol) -> str:
    sql = c.sql
    name = c.name.lower()
    if sql.lower() == name or sql.lower().endswith("." + name):
        return sql
    return f"{sql} AS {name}"


def _wrap(sql: str) -> str:
    s = sql.strip()
    if " OR " in s.upper() and not (s.startswith("(") and s.endswith(")")):
        return f"({s})"
    return s


def placeholder_sql(columns: list[OutCol], prev: "Relation | None", reason: str, keep_rows: bool) -> str:
    """Body for a step the rules could not translate: explicit, typed column list so the whole
    query still compiles; marked TCB-NEEDS-LLM so status and validation stay honest."""
    from .expr import is_numeric

    have = {c.name for c in prev.columns} if prev is not None else set()
    cols = []
    for c in columns:
        ddic = c.comp.ddic_type if c.comp else c.expr.ddic
        if keep_rows and c.name in have:
            cols.append(f"p.{c.name.lower()} AS {c.name.lower()}")
        else:
            typ = f"NUMBER(38,{(c.comp.decimals if c.comp and c.comp.decimals else 0)})" if is_numeric(ddic) else "VARCHAR"
            cols.append(f"CAST(NULL AS {typ}) AS {c.name.lower()}")
    reason = reason.replace("*/", "* /")[:120]
    body = "SELECT " + (",\n       ".join(cols) or "NULL AS table_line")
    src = f"\nFROM {prev.id} p" if prev is not None else ""
    return body + src + ("" if keep_rows else "\nWHERE FALSE") + f" /* TCB-NEEDS-LLM: {reason} */"
