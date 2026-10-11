"""Validation of generated SQL: syntax, compile (EXPLAIN on stub tables), identifiers, optional gold diff."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

import sqlglot

from ..knowledge.kb import KnowledgeBase
from ..knowledge.models import ProjectSettings
from .compare import CompareResult, compare, strip_select
from .stubs import ddl_for_table


@dataclass
class Check:
    name: str
    ok: bool | None  # None = skipped
    detail: str = ""


@dataclass
class ValidationReport:
    checks: list[Check] = field(default_factory=list)
    compare: CompareResult | None = None

    @property
    def ok(self) -> bool:
        return all(c.ok is not False for c in self.checks) and (self.compare is None or self.compare.ok)

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "checks": [c.__dict__ for c in self.checks],
            "compare": None if self.compare is None else self.compare.__dict__,
        }


def syntax_check(sql: str) -> Check:
    try:
        sqlglot.parse(sql, read="snowflake")
        return Check("syntax", True, "parsed by sqlglot (snowflake dialect)")
    except sqlglot.errors.ParseError as exc:
        return Check("syntax", False, str(exc).splitlines()[0][:300])


def placeholder_check(sql: str) -> Check:
    n = len(re.findall(r"TCB-(UNRESOLVED|NEEDS-LLM)", sql))
    return Check("unresolved placeholders", n == 0, f"{n} placeholder(s) left" if n else "none")


def tables_in_sql(sql: str) -> set[str]:
    out = set()
    try:
        for tree in sqlglot.parse(sql, read="snowflake"):
            if tree is None:
                continue
            ctes = {c.alias_or_name.upper() for c in tree.find_all(sqlglot.exp.CTE)}
            created = set()
            if isinstance(tree, sqlglot.exp.Create) and isinstance(tree.this, sqlglot.exp.Table):
                created.add(tree.this.name.upper())
            for t in tree.find_all(sqlglot.exp.Table):
                name = t.name.upper()
                if name and name not in ctes and name not in created and name != "PARAMS":
                    out.add(name)
    except sqlglot.errors.ParseError:
        pass
    return out


def identifier_check(sql: str, kb: KnowledgeBase) -> Check:
    tables = tables_in_sql(sql)
    unknown = sorted(t for t in tables if kb.table(t) is None)
    if unknown:
        return Check("known tables", None, f"not in knowledge base (cannot verify columns): {', '.join(unknown)}")
    return Check("known tables", True, ", ".join(sorted(tables)))


COMPILE_TIMEOUT_S = 90


def compile_check(cursor, sql: str, kb: KnowledgeBase, settings: ProjectSettings, stub_db: str, stub_schema: str) -> Check:
    """EXPLAIN the query against empty stub tables built from the knowledge base (no SAP data needed)."""
    body = strip_select(sql)
    if body.upper().startswith("CREATE"):
        body = re.sub(r"^CREATE OR REPLACE VIEW\s+\S+\s+AS\s+", "", body, flags=re.I)
    tables = tables_in_sql(body)
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {stub_db}")
        cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {stub_db}.{stub_schema}")
        for t in tables:
            from ..knowledge.catalog import sap_name

            ddl = ddl_for_table(kb, sap_name(t, settings), stub_db, stub_schema, settings, replace=True, physical=t)
            if ddl:
                cursor.execute(ddl)
        cursor.execute(f"USE SCHEMA {stub_db}.{stub_schema}")
        # point qualified names at the stub schema
        target = ".".join(p for p in (settings.target_database, settings.target_schema) if p)
        if target:
            body = re.sub(re.escape(target.lower()) + r"\.", "", body, flags=re.I)
        cursor.execute(f"EXPLAIN USING TEXT {body}", timeout=COMPILE_TIMEOUT_S)
        return Check("compiles on Snowflake", True, f"EXPLAIN ok against stubs in {stub_db}.{stub_schema}")
    except Exception as exc:  # noqa: BLE001
        msg = " ".join(str(exc).split())
        if "timeout" in msg.lower() or "cancel" in msg.lower():
            msg = (f"Snowflake did not finish compiling within {COMPILE_TIMEOUT_S}s: the query is very large "
                   f"({len(body):,} characters). It is syntactically checked; run it on a larger warehouse to confirm. " + msg[:200])
        return Check("compiles on Snowflake", False, msg[:700])


def validate(sql: str, kb: KnowledgeBase, settings: ProjectSettings, cursor=None, gold_sql: str | None = None,
             data_schema: str | None = None, stub_db: str = "TCODE_BREAKER", stub_schema: str = "STUBS") -> ValidationReport:
    rep = ValidationReport()
    rep.checks.append(syntax_check(sql))
    rep.checks.append(placeholder_check(sql))
    rep.checks.append(identifier_check(sql, kb))
    if cursor is not None:
        rep.checks.append(compile_check(cursor, sql, kb, settings, stub_db, stub_schema))
        if gold_sql and data_schema:
            rep.compare = compare(cursor, sql, gold_sql, data_schema)
    else:
        rep.checks.append(Check("compiles on Snowflake", None, "no Snowflake connection"))
    return rep
