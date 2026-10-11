"""Generate Snowflake stub tables (DDL) from the knowledge base.

Stub tables let generated SQL be compiled/EXPLAINed without access to real SAP data.
"""

from __future__ import annotations

from ..knowledge.kb import KnowledgeBase
from ..knowledge.models import FieldInfo, ProjectSettings


def column_type(kb: KnowledgeBase, f: FieldInfo, settings: ProjectSettings | None = None) -> str:
    spec = kb.type_spec(f.ddic_type)
    if spec is None:
        return "VARCHAR"
    length = f.length or 255
    decimals = f.decimals or 0
    sql_type = spec.raw.format(len=length, dec=decimals)
    if settings is not None and settings.type_mode == "typed":
        if spec.family == "date":
            return "DATE"
        if spec.family == "time":
            return "TIME"
    if sql_type.startswith("NUMBER(") and length > 38:
        sql_type = f"NUMBER(38,{min(decimals, 37)})"
    return sql_type


def ddl_for_table(
    kb: KnowledgeBase,
    table: str,
    database: str | None = None,
    schema: str | None = None,
    settings: ProjectSettings | None = None,
    replace: bool = False,
    extra_columns: list[str] | None = None,
    physical: str | None = None,
) -> str | None:
    info = kb.table(table)
    if info is None:
        return None
    cols = [f'    {f.name} {column_type(kb, f, settings)}' for f in info.fields.values()] or ["    TCB_NO_COLUMNS_KNOWN VARCHAR"]
    known = set(info.fields)
    for extra in extra_columns or []:
        if extra.upper() not in known:
            cols.append(f"    {extra.upper()} VARCHAR")
    qualified = ".".join(p for p in (database, schema, physical or info.name) if p)
    verb = "CREATE OR REPLACE TABLE" if replace else "CREATE TABLE IF NOT EXISTS"
    comment = info.description.replace("'", "''")
    return f"{verb} {qualified} (\n" + ",\n".join(cols) + f"\n) COMMENT = 'tcode-breaker stub: {comment}'"
