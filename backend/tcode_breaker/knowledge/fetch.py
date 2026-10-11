"""Fetch table metadata from Snowflake into the knowledge library.

Two sources, both read-only:
  * INFORMATION_SCHEMA of any database.schema (the SAP replica, or any schema holding the tables):
    column names, Snowflake types, comments, primary keys if declared. DDIC types/descriptions are
    borrowed from same-named fields the dictionary already knows (SAP reuses domains: MATNR, WERKS...).
  * a replicated SAP data dictionary (DD03L fields, DD04T/DD03T field texts, DD02T table texts) in a
    schema: the exact SAP definition - keys, DDIC types, lengths, decimals, reference fields, labels.
"""

from __future__ import annotations

from .catalog import _ident, fetch_catalog
from .inference import field_type_index
from .models import FieldInfo, ProjectSettings, Provenance, TableInfo

DDIC_TABLES = ("DD03L", "DD04T", "DD03T", "DD02T", "DD02L")


def _lit(v: str) -> str:
    return "'" + str(v).replace("'", "''") + "'"


def ddic_status(cursor, database: str, schema: str, pattern: str = "{table}") -> dict:
    """Which replicated DDIC tables exist in database.schema (physical names follow `pattern`)."""
    phys = {t: pattern.replace("{table}", t).replace("{TABLE}", t).upper() for t in DDIC_TABLES}
    cursor.execute(f"SELECT table_name FROM {_ident(database)}.INFORMATION_SCHEMA.TABLES WHERE table_schema = {_lit(schema.upper())} "
                   f"AND table_name IN ({', '.join(_lit(p) for p in phys.values())})")
    present = {r[0].upper() for r in cursor.fetchall()}
    found = {t: phys[t] for t in DDIC_TABLES if phys[t] in present}
    return {"available": "DD03L" in found, "tables": found}


def from_ddic(cursor, database: str, schema: str, tables: list[str], pattern: str = "{table}", language: str = "E") -> tuple[dict[str, TableInfo], list[str]]:
    st = ddic_status(cursor, database, schema, pattern)
    if not st["available"]:
        raise ValueError(f"No DD03L table in {database}.{schema}" + (f" (looked for {pattern.replace('{table}', 'DD03L')})" if pattern != "{table}" else ""))
    q = lambda t: f"{_ident(database)}.{_ident(schema)}.{_ident(st['tables'][t])}"  # noqa: E731
    names = sorted({t.upper() for t in tables})[:2000]
    lang = _lit(language or "E")
    text_cols, joins = [], []
    if "DD04T" in st["tables"]:
        joins.append(f"LEFT JOIN {q('DD04T')} e ON e.ROLLNAME = l.ROLLNAME AND e.DDLANGUAGE = {lang} AND e.AS4LOCAL = 'A'")
        text_cols += ["e.SCRTEXT_M", "e.DDTEXT"]
    if "DD03T" in st["tables"]:
        joins.append(f"LEFT JOIN {q('DD03T')} f ON f.TABNAME = l.TABNAME AND f.FIELDNAME = l.FIELDNAME AND f.DDLANGUAGE = {lang} AND f.AS4LOCAL = 'A'")
        text_cols += ["f.DDTEXT"]
    txt = f"COALESCE({', '.join(text_cols)}, '')" if text_cols else "''"
    sql = (f"SELECT l.TABNAME, l.FIELDNAME, l.KEYFLAG, l.DATATYPE, l.LENG, l.DECIMALS, l.REFFIELD, {txt} AS TXT "
           f"FROM {q('DD03L')} l {' '.join(joins)} WHERE l.AS4LOCAL = 'A' AND l.TABNAME IN ({', '.join(_lit(n) for n in names)}) "
           f"ORDER BY l.TABNAME, l.POSITION")
    cursor.execute(sql)
    out: dict[str, TableInfo] = {}
    for tab, fname, keyflag, dtype, leng, dec, ref, text in cursor.fetchall():
        tab, fname = str(tab).upper(), str(fname or "").upper()
        if not fname or fname.startswith("."):
            continue
        t = out.setdefault(tab, TableInfo(name=tab, fields_complete=True, source=Provenance.LIBRARY, origin="ddic"))
        is_key = str(keyflag or "").strip().upper() == "X"
        if is_key:
            t.key.append(fname)
        t.fields[fname] = FieldInfo(name=fname, ddic_type=str(dtype or "CHAR").upper(), length=_int(leng), decimals=_int(dec) or None,
                                    ref_field=(str(ref).upper() if ref else None), description=str(text or "").strip(), is_key=is_key,
                                    source=Provenance.LIBRARY)
    if out and "DD02T" in st["tables"]:
        cursor.execute(f"SELECT TABNAME, DDTEXT FROM {q('DD02T')} WHERE DDLANGUAGE = {lang} AND AS4LOCAL = 'A' "
                       f"AND TABNAME IN ({', '.join(_lit(n) for n in out)})")
        for tab, text in cursor.fetchall():
            if str(tab).upper() in out:
                out[str(tab).upper()].description = str(text or "")
    missing = [n for n in names if n not in out]
    return out, missing


def from_information_schema(cursor, database: str, schema: str, tables: list[str] | None, kb, pattern: str = "{table}") -> tuple[dict[str, TableInfo], list[str]]:
    """Columns of `tables` (SAP names; None = every table in the schema) as library entries."""
    settings = ProjectSettings(table_pattern=pattern or "{table}")
    doc = fetch_catalog(cursor, database, schema, settings, tables)
    keys = _primary_keys(cursor, database, schema)
    types = field_type_index(kb)
    out: dict[str, TableInfo] = {}
    for name, entry in (doc.get("tables") or {}).items():
        base = kb.table(name)
        pk = keys.get(entry["physical"].upper(), [])
        key = pk or (list(base.key) if base else [])
        t = TableInfo(name=name, description=(base.description if base and base.description else entry.get("comment") or ""),
                      module=base.module if base else "", key=[k.upper() for k in key], fields_complete=True,
                      text_table=base.text_table if base else None, text_of=base.text_of if base else None,
                      source=Provenance.LIBRARY, origin="snowflake")
        for c in entry["columns"]:
            fname = c["name"]
            known = (base.fields.get(fname) if base else None) or types.get(fname)
            if known is not None and known.ddic_type:
                f = known.model_copy(update={"name": fname, "source": Provenance.LIBRARY, "is_key": fname in t.key,
                                             "description": known.description or c.get("comment") or ""})
            else:
                f = FieldInfo(name=fname, ddic_type=c.get("ddic") or _native(c.get("snowflake_type")), length=c.get("length") or c.get("precision"),
                              decimals=c.get("scale") or None, description=c.get("comment") or "", is_key=fname in t.key, source=Provenance.LIBRARY)
            t.fields[fname] = f
        out[name] = t
    wanted = sorted({x.upper() for x in tables}) if tables else []
    return out, [n for n in wanted if n not in out]


def _native(sf_type: str | None) -> str:
    t = (sf_type or "").upper()
    return {"DATE": "DATS", "TIME": "TIMS"}.get(t, "TIMESTAMP" if t.startswith("TIMESTAMP") else "CHAR")


def _primary_keys(cursor, database: str, schema: str) -> dict[str, list[str]]:
    """Declared primary keys (replication tools often create them). Empty when none / not allowed."""
    try:
        cursor.execute(f"SHOW PRIMARY KEYS IN SCHEMA {_ident(database)}.{_ident(schema)}")
        cols = [d[0].lower() for d in cursor.description]
        rows = cursor.fetchall()
    except Exception:  # noqa: BLE001
        return {}
    ti, ci, si = cols.index("table_name"), cols.index("column_name"), cols.index("key_sequence")
    out: dict[str, list[tuple[int, str]]] = {}
    for r in rows:
        out.setdefault(str(r[ti]).upper(), []).append((int(r[si]), str(r[ci]).upper()))
    return {k: [c for _, c in sorted(v)] for k, v in out.items()}


def list_tables(cursor, database: str, schema: str, pattern: str = "{table}") -> list[str]:
    """SAP names of every table/view in a schema (reverse of table_pattern)."""
    from .catalog import sap_name

    cursor.execute(f"SELECT table_name FROM {_ident(database)}.INFORMATION_SCHEMA.TABLES WHERE table_schema = {_lit(schema.upper())} ORDER BY 1")
    settings = ProjectSettings(table_pattern=pattern or "{table}")
    return [sap_name(r[0], settings) for r in cursor.fetchall()]


def _int(v) -> int | None:
    try:
        return int(str(v).strip()) if v not in (None, "") else None
    except ValueError:
        return None

