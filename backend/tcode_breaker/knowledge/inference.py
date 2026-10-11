"""Metadata without a knowledge base.

Two sources fill in table/field metadata for tables the built-in dictionary does not know
(custom Z tables, CDS views, partial entries):

1. the Snowflake raw layer itself (INFORMATION_SCHEMA.COLUMNS of the source schema) - see catalog.py
2. the ABAP source: every `wa-field`, `alias~field`, `TYPE tab-field` whose variable is typed with
   (or flows from) a database table tells us that the table has that field. Types are borrowed
   from same-named fields of known SAP tables (SAP reuses domains: MATNR, WERKS, BUKRS, ...).

Inferred fields are marked Provenance.INFERRED and the table stays `fields_complete=False`,
so nothing downstream treats a guess as a verified fact.
"""

from __future__ import annotations

import re
from collections import Counter, defaultdict

from .kb import KnowledgeBase
from .models import FieldInfo, Provenance, TableInfo

_COMMENT_LINE = re.compile(r"^\*.*$", re.MULTILINE)
_STRING = re.compile(r"'(?:[^']|'')*'|`(?:[^`]|``)*`|\|[^|\n]*\|")
_INLINE_COMMENT = re.compile(r'"[^\n]*')
_FROM = re.compile(r"\b(?:FROM|JOIN)\s+(?!@)([A-Za-z0-9_/]+)(?:\s*\([^)]*\))?(?:\s+(?:AS\s+)?([A-Za-z0-9_]+))?", re.IGNORECASE)
_TABLES_STMT = re.compile(r"^\s*TABLES\s*:?\s*([A-Za-z0-9_/,\s]+)\.", re.IGNORECASE | re.MULTILINE)
_DECL = re.compile(
    r"^\s*(?:DATA|TYPES|FIELD-SYMBOLS|CLASS-DATA|STATICS|PARAMETERS)\b\s*:?\s*(.*?)\.\s*$",
    re.IGNORECASE | re.MULTILINE | re.DOTALL)
_ONE_DECL = re.compile(
    r"^\s*(<?[A-Za-z0-9_/]+>?)(?:\(\d+\))?\s+(?:TYPE|LIKE)\s+(?:(?:STANDARD|SORTED|HASHED|ANY|INDEX)\s+)?"
    r"(?:TABLE\s+OF\s+|LINE\s+OF\s+|RANGE\s+OF\s+)?(?:REF\s+TO\s+)?([A-Za-z0-9_/]+)", re.IGNORECASE)
_SELECT_INTO = re.compile(r"\bINTO\s+(?:CORRESPONDING\s+FIELDS\s+OF\s+)?(?:TABLE\s+)?@?(?:DATA\(|FINAL\()?(<?[A-Za-z0-9_]+>?)", re.IGNORECASE)
_FLOW = [
    # LOOP AT itab INTO wa / ASSIGNING <fs> / REFERENCE INTO
    re.compile(r"\bLOOP\s+AT\s+@?([A-Za-z0-9_]+)\s+(?:INTO|ASSIGNING|REFERENCE\s+INTO)\s+(?:DATA\(|FIELD-SYMBOL\()?(<?[A-Za-z0-9_]+>?)", re.IGNORECASE),
    re.compile(r"\bREAD\s+TABLE\s+([A-Za-z0-9_]+)\s+(?:.*?\s)?(?:INTO|ASSIGNING|REFERENCE\s+INTO)\s+(?:DATA\(|FIELD-SYMBOL\()?(<?[A-Za-z0-9_]+>?)", re.IGNORECASE),
    re.compile(r"\bAPPEND\s+(<?[A-Za-z0-9_]+>?)\s+TO\s+([A-Za-z0-9_]+)", re.IGNORECASE),
    re.compile(r"\bMODIFY\s+([A-Za-z0-9_]+)\s+FROM\s+(<?[A-Za-z0-9_]+>?)", re.IGNORECASE),
]
_FIELD_USE = re.compile(r"(?<![A-Za-z0-9_>~-])(<?[A-Za-z0-9_]+>?)(?:->|-)([A-Za-z0-9_]+)\b")
_TILDE_USE = re.compile(r"(?<![A-Za-z0-9_])([A-Za-z0-9_]+)~([A-Za-z0-9_]+)\b")
_LOCAL_TYPES = re.compile(r"^\s*TYPES\s*:?\s*(BEGIN\s+OF\s+)?([A-Za-z0-9_/]+)", re.IGNORECASE | re.MULTILINE)
_BUILTIN_TYPES = {"C", "N", "I", "P", "D", "T", "F", "X", "STRING", "XSTRING", "INT1", "INT2", "INT4", "INT8", "DECFLOAT16",
                  "DECFLOAT34", "UTCLONG", "ABAP_BOOL", "ABAP_BOOLEAN", "BOOLEAN", "CHAR", "NUMC", "DATS", "TIMS", "SYST",
                  "SY", "ANY", "DATA", "OBJECT", "TABLE", "STANDARD", "SORTED", "HASHED", "LINE", "RANGE", "REF"}
_KEYWORDS = {"SY", "SYST", "ME", "SUPER", "ABAP", "CL", "IF", "CX", "TEXT", "SCREEN"}
_COMP_CLAUSES = [
    (re.compile(r"\bLOOP\s+AT\s+([A-Za-z0-9_]+)\b.*?\bWHERE\b(.*)$", re.IGNORECASE | re.DOTALL), "cond"),
    (re.compile(r"\bREAD\s+TABLE\s+([A-Za-z0-9_]+)\b.*?\bWITH\s+(?:TABLE\s+)?KEY\b(.*?)(?:\bINTO\b|\bASSIGNING\b|\bTRANSPORTING\b|\bBINARY\b|$)", re.IGNORECASE | re.DOTALL), "cond"),
    (re.compile(r"\bDELETE\s+([A-Za-z0-9_]+)\s+WHERE\b(.*)$", re.IGNORECASE | re.DOTALL), "cond"),
    (re.compile(r"\bMODIFY\s+([A-Za-z0-9_]+)\b.*?\bWHERE\b(.*)$", re.IGNORECASE | re.DOTALL), "cond"),
    (re.compile(r"\bSORT\s+([A-Za-z0-9_]+)\s+BY\b(.*)$", re.IGNORECASE | re.DOTALL), "list"),
    (re.compile(r"\bDELETE\s+ADJACENT\s+DUPLICATES\s+FROM\s+([A-Za-z0-9_]+)\s+COMPARING\b(.*)$", re.IGNORECASE | re.DOTALL), "list"),
    (re.compile(r"\bMODIFY\s+([A-Za-z0-9_]+)\b.*?\bTRANSPORTING\b(.*?)(?:\bWHERE\b|$)", re.IGNORECASE | re.DOTALL), "list"),
]
_CMP_NAME = re.compile(r"(?<![A-Za-z0-9_>~-])([A-Za-z_][A-Za-z0-9_]*)\s*(?:=|<>|>=|<=|>|<|\bEQ\b|\bNE\b|\bGE\b|\bLE\b|\bGT\b|\bLT\b|\bIN\b|\bIS\b|\bBETWEEN\b|\bCP\b|\bCS\b)", re.IGNORECASE)
_TABLE_EXPR = re.compile(r"(?<![A-Za-z0-9_])([A-Za-z0-9_]+)\[\s*([^\]]*?)\]")
_RESERVED = {
    "SELECT", "FROM", "WHERE", "INTO", "TABLE", "AND", "OR", "NOT", "IS", "IN", "AS", "BY", "ON", "UP", "TO", "OF", "FOR", "ALL",
    "ENTRIES", "JOIN", "INNER", "LEFT", "OUTER", "GROUP", "ORDER", "HAVING", "DISTINCT", "SINGLE", "APPENDING", "CORRESPONDING",
    "FIELDS", "DATA", "TYPE", "LIKE", "VALUE", "LOOP", "AT", "ENDLOOP", "IF", "ENDIF", "ELSE", "READ", "WITH", "KEY", "SORT",
    "DELETE", "MODIFY", "APPEND", "INSERT", "COLLECT", "CLEAR", "REFRESH", "CASE", "WHEN", "ENDCASE", "DO", "ENDDO", "WHILE",
    "TRANSPORTING", "ASSIGNING", "REFERENCE", "INITIAL", "BETWEEN", "EQ", "NE", "LT", "GT", "LE", "GE", "CP", "CS", "NP", "NS",
    "NULL", "TRUE", "FALSE", "SPACE", "ME", "NEW", "CAST", "CONV", "COND", "SWITCH", "REDUCE", "EXISTS", "BINARY", "SEARCH",
    "UNION", "CROSS", "CLIENT", "SPECIFIED", "BYPASSING", "BUFFER", "PACKAGE", "SIZE", "ROWS", "OFFSET", "ASCENDING",
    "DESCENDING", "TEXT", "STABLE", "COMPARING", "ADJACENT", "DUPLICATES", "INDEX", "LINES", "FIELD", "SYMBOL", "ENDSELECT",
}
_CLAUSE_WORDS = {"AND", "OR", "NOT", "ASCENDING", "DESCENDING", "AS", "TEXT", "STABLE", "ALL", "FIELDS", "TABLE_LINE", "INITIAL",
                 "NULL", "KEY", "COMPONENTS", "BINARY", "SEARCH", "PRIMARY_KEY", "WITH", "INDEX"}


def _clean(text: str) -> str:
    text = _COMMENT_LINE.sub("", text)
    text = _STRING.sub("''", text)
    return _INLINE_COMMENT.sub("", text)


def referenced_tables(text: str) -> set[str]:
    """Database tables named after FROM / JOIN / TABLES anywhere in the source."""
    src = _clean(text)
    out = {m.group(1).upper() for m in _FROM.finditer(src) if not m.group(1).startswith("@")}
    for m in _TABLES_STMT.finditer(src):
        out.update(t.upper() for t in re.split(r"[\s,]+", m.group(1)) if t)
    return {t for t in out if t not in ("TABLE", "DATA") and re.fullmatch(r"[A-Z0-9_/]+", t)}


def infer_tables(text: str, kb: KnowledgeBase, local_types: set[str] | None = None) -> dict[str, set[str]]:
    """Return {db_table: {fields used in the code}} for tables referenced in SELECT/JOIN/TABLES."""
    src = _clean(text)
    tables: set[str] = set()
    alias_of: dict[str, str] = {}
    for m in _FROM.finditer(src):
        t = m.group(1).upper()
        if t in ("TABLE", "DATA", "@DATA") or t.startswith("@"):
            continue
        tables.add(t)
        alias_of[t] = t
        if m.group(2) and m.group(2).upper() not in ("WHERE", "INTO", "INNER", "LEFT", "JOIN", "FIELDS", "GROUP", "ORDER",
                                                     "UP", "FOR", "ON", "APPENDING", "BYPASSING", "WITH", "CLIENT"):
            alias_of[m.group(2).upper()] = t
    for m in _TABLES_STMT.finditer(src):
        for t in re.split(r"[\s,]+", m.group(1)):
            if t:
                tables.add(t.upper())
    # variable/type -> referenced type name
    type_of: dict[str, str] = {}
    for m in _DECL.finditer(src):
        for part in _split_top(m.group(1)):
            d = _ONE_DECL.match(part)
            if d:
                type_of[d.group(1).upper()] = d.group(2).upper()
    local = {k for k in (local_types or set())} | {m.group(2).upper() for m in _LOCAL_TYPES.finditer(src)}
    # DDIC structures / table types the dictionary does not know (e.g. ZSTR_OUTPUT): their components are
    # inferred from usage too, so internal tables typed with them get real columns
    structs = {t for t in set(type_of.values()) - tables - local
               if t not in _BUILTIN_TYPES and kb.table(t) is None and re.fullmatch(r"[A-Z][A-Z0-9_/]*", t)}
    tables = tables | structs
    if not tables:
        return {}

    def table_for(var: str, depth: int = 0) -> str | None:
        v = var.upper()
        if depth > 8:
            return None
        if v in tables and v not in type_of:
            return v
        t = type_of.get(v)
        if t is None:
            return None
        if t in tables and t not in local:
            return t
        return table_for(t, depth + 1)

    # data flow: SELECT ... FROM T ... INTO itab, LOOP AT itab INTO wa, ...
    links: list[tuple[str, str]] = []
    for stmt in src.split("."):
        fm = _FROM.search(stmt)
        im = _SELECT_INTO.search(stmt)
        if fm and im and re.search(r"\bSELECT\b", stmt, re.IGNORECASE) and "*" in stmt.split(fm.group(0))[0] + stmt[:40]:
            links.append((im.group(1).upper(), fm.group(1).upper()))
        for rx in _FLOW:
            for m in rx.finditer(stmt):
                a, b = m.group(1).upper(), m.group(2).upper()
                links.append((b, a) if rx.pattern.startswith(r"\bLOOP") or rx.pattern.startswith(r"\bREAD") else (a, b))
    var_table: dict[str, str] = {}
    for _ in range(4):  # propagate a few hops
        for dst, src_name in links:
            t = var_table.get(src_name) or table_for(src_name) or (src_name if src_name in tables and src_name not in type_of else None)
            if t and dst not in var_table and table_for(dst) is None and dst not in type_of:
                var_table[dst] = t

    used: dict[str, set[str]] = defaultdict(set)
    for m in _TILDE_USE.finditer(src):
        t = alias_of.get(m.group(1).upper())
        if t:
            used[t].add(m.group(2).upper())
    for m in _FIELD_USE.finditer(src):
        base, fld = m.group(1).upper(), m.group(2).upper()
        if base in _KEYWORDS or fld.isdigit():
            continue
        t = var_table.get(base) or table_for(base) or (base if base in tables else None)
        if t:
            used[t].add(fld)
    # components named without a work area: LOOP AT itab WHERE comp = .. / READ TABLE itab WITH KEY comp = ..
    # / SORT itab BY comp / DELETE itab WHERE comp .. / DELETE ADJACENT DUPLICATES FROM itab COMPARING comp / itab[ comp = .. ]
    for stmt in src.split("."):
        for rx, part in _COMP_CLAUSES:
            m = rx.search(stmt)
            if not m:
                continue
            itab = m.group(1).upper()
            t = var_table.get(itab) or table_for(itab)
            if not t:
                continue
            clause = m.group(2)
            names = _CMP_NAME.findall(clause) if part == "cond" else re.findall(r"[A-Za-z_][A-Za-z0-9_]*", clause)
            for n in names:
                u = n.upper()
                if u not in _CLAUSE_WORDS and "-" not in n:
                    used[t].add(u)
        for m in _TABLE_EXPR.finditer(stmt):
            t = var_table.get(m.group(1).upper()) or table_for(m.group(1))
            if t:
                for n in _CMP_NAME.findall(m.group(2)):
                    if n.upper() not in _CLAUSE_WORDS:
                        used[t].add(n.upper())
    used = {t: {f for f in fs if f not in _RESERVED and not f[:1].isdigit()} for t, fs in used.items()}
    return {t: used.get(t, set()) for t in tables if t not in structs or used.get(t)}


def _split_top(text: str) -> list[str]:
    """Split a chained declaration on top-level commas."""
    parts, depth, cur = [], 0, ""
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return parts


def field_type_index(kb: KnowledgeBase) -> dict[str, FieldInfo]:
    """Most common definition of each field name across known tables (SAP domain reuse)."""
    by_name: dict[str, Counter] = defaultdict(Counter)
    sample: dict[tuple, FieldInfo] = {}
    for t in kb.tables.values():
        if t.source == Provenance.INFERRED:
            continue
        for f in t.fields.values():
            key = (f.ddic_type, f.length, f.decimals)
            by_name[f.name][key] += 1
            sample.setdefault((f.name,) + key, f)
    out = {}
    for name, cnt in by_name.items():
        key = cnt.most_common(1)[0][0]
        out[name] = sample[(name,) + key]
    return out


def apply_inference(kb: KnowledgeBase, text: str, local_types: set[str] | None = None) -> list[str]:
    """Add inferred fields to the (per-run) knowledge base. Returns the tables that were extended."""
    used = infer_tables(text, kb, local_types)
    if not used:
        return []
    types = field_type_index(kb)
    touched = []
    for t, fields in used.items():
        info = kb.tables.get(t)
        if info is not None and info.fields_complete:
            continue
        added = info is None
        info = info.model_copy(deep=True) if info is not None else TableInfo(name=t, source=Provenance.INFERRED)
        for f in sorted(fields):
            if f in info.fields:
                continue
            ref = types.get(f)
            info.fields[f] = FieldInfo(name=f, ddic_type=ref.ddic_type if ref else None, length=ref.length if ref else None,
                                       decimals=ref.decimals if ref else None, description=ref.description if ref else "",
                                       source=Provenance.INFERRED)
            added = True
        if added:
            kb.tables[t] = info
            touched.append(t)
    return touched
