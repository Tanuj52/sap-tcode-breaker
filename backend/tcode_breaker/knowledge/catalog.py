"""Live metadata from the Snowflake raw layer (the SAP replica).

The source schema is the ground truth: which SAP tables were replicated and which columns
they have. Reading it means no knowledge pack is needed for custom Z tables or a client's
specific replication; the built-in SAP dictionary is only used for descriptions and ABAP types.
"""

from __future__ import annotations

import re

from .models import ProjectSettings

_SF_TO_DDIC = [
    (re.compile(r"^(VARCHAR|TEXT|STRING|CHAR)"), "CHAR"),
    (re.compile(r"^(NUMBER|DECIMAL|NUMERIC)\((\d+),\s*0\)$"), "INT8"),
    (re.compile(r"^(NUMBER|DECIMAL|NUMERIC)"), "DEC"),
    (re.compile(r"^(FLOAT|DOUBLE|REAL)"), "FLTP"),
    (re.compile(r"^(INT|INTEGER|BIGINT|SMALLINT|TINYINT)"), "INT8"),
    (re.compile(r"^BOOLEAN$"), "CHAR"),
]
NATIVE_TEMPORAL = ("DATE", "TIME", "TIMESTAMP_NTZ", "TIMESTAMP_LTZ", "TIMESTAMP_TZ", "TIMESTAMP")


def ddic_for_snowflake_type(data_type: str, precision: int | None, scale: int | None) -> tuple[str | None, int | None, int | None]:
    t = (data_type or "").upper()
    if t in NATIVE_TEMPORAL:
        return None, None, None  # converted by the replication tool; ABAP semantics need the raw format
    if t in ("NUMBER", "DECIMAL", "NUMERIC"):
        return ("INT8" if not scale else "DEC"), precision, scale
    for rx, ddic in _SF_TO_DDIC:
        if rx.match(t):
            return ddic, None, None
    return "CHAR", None, None


def sap_name(physical: str, settings: ProjectSettings) -> str:
    """Reverse table_pattern / table_renames: physical Snowflake name -> SAP table name."""
    p = physical.upper()
    for sap, phys in settings.table_renames.items():
        if phys.split(".")[-1].upper() == p:
            return sap.upper()
    pat = (settings.table_pattern or "{table}").upper()
    if pat != "{TABLE}" and "{TABLE}" in pat:
        pre, post = pat.split("{TABLE}", 1)
        if p.startswith(pre) and p.endswith(post):
            return p[len(pre): len(p) - len(post) if post else None]
    return p


def physical_name(table: str, settings: ProjectSettings) -> str:
    t = table.upper()
    if t in settings.table_renames:
        return settings.table_renames[t]
    return (settings.table_pattern or "{table}").replace("{table}", t).replace("{TABLE}", t)


def fetch_catalog(cursor, database: str, schema: str, settings: ProjectSettings, tables: list[str] | None = None) -> dict:
    """Read tables + columns of `database.schema`. Returns {"tables": {SAP_NAME: {...}}, "source": "DB.SCHEMA"}."""
    db = _ident(database)
    sc = schema.upper().replace("'", "''")
    q = (f"SELECT c.table_name, c.column_name, c.data_type, c.numeric_precision, c.numeric_scale, "
         f"c.character_maximum_length, c.comment, t.comment, t.table_type, t.row_count "
         f"FROM {db}.INFORMATION_SCHEMA.COLUMNS c JOIN {db}.INFORMATION_SCHEMA.TABLES t "
         f"ON t.table_schema = c.table_schema AND t.table_name = c.table_name "
         f"WHERE c.table_schema = '{sc}'")
    wanted = None
    if tables:
        wanted = sorted({physical_name(t, settings).split(".")[-1].upper() for t in tables})
        if len(wanted) <= 2000:
            q += " AND c.table_name IN (" + ", ".join("'" + w.replace("'", "''") + "'" for w in wanted) + ")"
    q += " ORDER BY c.table_name, c.ordinal_position"
    cursor.execute(q)
    out: dict[str, dict] = {}
    for tname, cname, dtype, prec, scale, clen, ccomment, tcomment, ttype, rows in cursor.fetchall():
        key = sap_name(tname, settings)
        entry = out.setdefault(key, {"physical": tname, "comment": tcomment or "", "type": ttype, "rows": rows, "columns": []})
        ddic, p, s = ddic_for_snowflake_type(dtype, prec, scale)
        entry["columns"].append({"name": cname.upper(), "snowflake_type": dtype, "ddic": ddic, "precision": p, "scale": s,
                                 "length": clen, "comment": ccomment or ""})
    return {"source": f"{database}.{schema}".upper(), "tables": out, "requested": wanted or []}


def list_schemas(cursor, database: str) -> list[str]:
    cursor.execute(f"SELECT schema_name FROM {_ident(database)}.INFORMATION_SCHEMA.SCHEMATA ORDER BY 1")
    return [r[0] for r in cursor.fetchall() if r[0] != "INFORMATION_SCHEMA"]


def _ident(name: str) -> str:
    n = name.strip()
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_$]*", n):
        return n
    return '"' + n.replace('"', '""') + '"'
