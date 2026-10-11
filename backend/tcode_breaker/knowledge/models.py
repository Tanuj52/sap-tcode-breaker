"""Knowledge base data models."""

from __future__ import annotations

import re
from enum import Enum

from pydantic import BaseModel, Field


class Provenance(str, Enum):
    """Where a piece of knowledge came from. Shown next to every resolved item in the UI."""

    CLIENT_PACK = "client_pack"
    LIBRARY = "library"  # added by the user from the Knowledge page (data/knowledge/)
    AI = "ai_generated"  # proposed by an LLM from the table / FM name; review before trusting
    BUILTIN = "builtin"
    CATALOG = "snowflake_catalog"  # read live from the Snowflake source schema (INFORMATION_SCHEMA)
    INFERRED = "inferred"  # derived from the ABAP source itself (e.g. TYPE mara-matnr, wa-field usage)
    UNRESOLVED = "unresolved"


class FieldStatus(str, Enum):
    KNOWN = "known"  # listed in the knowledge base
    UNVERIFIED = "unverified"  # table known but field list is partial
    UNKNOWN = "unknown"  # table field list is complete and does not contain the field
    NO_TABLE = "no_table"  # table not in the knowledge base


class FieldInfo(BaseModel):
    name: str
    ddic_type: str | None = "CHAR"  # None = type unknown (inferred from usage only)
    length: int | None = None
    decimals: int | None = None
    ref_field: str | None = None
    description: str = ""
    is_key: bool = False
    source: Provenance = Provenance.BUILTIN


class TableInfo(BaseModel):
    name: str
    description: str = ""
    module: str = ""
    release: str = "both"  # ecc | s4 | both
    key: list[str] = Field(default_factory=list)
    key_note: str | None = None
    fields: dict[str, FieldInfo] = Field(default_factory=dict)
    fields_complete: bool = False
    text_table: str | None = None
    text_of: str | None = None
    source: Provenance = Provenance.BUILTIN
    origin: str | None = None  # library entries: manual | snowflake | ddic | ai | import:<file>
    updated: str | None = None


class FMInfo(BaseModel):
    name: str
    kind: str  # expression | lookup | ui | output_sink | side_effect | opaque | custom
    output: str | None = None
    sql: str | None = None
    tables: list[str] = Field(default_factory=list)
    note: str | None = None
    table_param: str | None = None
    fieldcat_param: str | None = None
    source: Provenance = Provenance.BUILTIN
    has_source_code: bool = False
    origin: str | None = None
    updated: str | None = None


FM_KINDS = ("expression", "lookup", "ui", "output_sink", "side_effect", "opaque", "custom")


def fm_from_spec(name: str, spec: dict, source: Provenance) -> FMInfo:
    """Build an FMInfo from a catalog entry, ignoring unknown keys (hand-edited files stay loadable)."""
    data = {k: v for k, v in (spec or {}).items() if k in FMInfo.model_fields and k not in ("name", "source")}
    if spec and spec.get("origin") == "ai":
        source = Provenance.AI
    data.setdefault("kind", "opaque")
    return FMInfo(name=name.upper(), source=source, **data)


class S4Mapping(BaseModel):
    id: str
    title: str
    old_tables: list[str]
    new_table: str | None
    join_collapse: bool = False
    join_key: list[str] = Field(default_factory=list)
    filter: str | None = None
    columns: str | dict[str, str] = "same_name"
    confidence: str = "verify"
    note: str = ""

    def map_column(self, column: str) -> str:
        if isinstance(self.columns, dict):
            return self.columns.get(column.upper(), column.upper())
        return column.upper()


class TypeSpec(BaseModel):
    raw: str
    typed: str
    initial: str
    family: str
    note: str | None = None


class ProjectSettings(BaseModel):
    """Per-project (per-client) conversion settings. Defaults can come from a pack manifest."""

    source_system: str = "ecc"  # ecc | s4
    abap_version: str = "v757"
    target_database: str | None = None
    target_schema: str | None = None
    client: str | None = None  # MANDT value to filter on; None = no client filter
    language: str = "E"
    type_mode: str = "raw"  # raw | typed
    physical_tables: list[str] | None = None  # tables that exist in Snowflake; None = assume all
    table_renames: dict[str, str] = Field(default_factory=dict)
    confidential: bool = True  # True = only Cortex / local models may see the code
    infer_fields: bool = True  # fill unknown tables' field lists from how the code uses them
    view_database: str | None = None  # where CREATE VIEW goes (gold layer); default = source database
    view_schema: str | None = None
    table_pattern: str = "{table}"  # physical name in the raw layer, e.g. "SAP_{table}" or "{table}_RAW"
    packs: list[str] = Field(default_factory=list)

    def is_physical(self, table: str) -> bool:
        if self.physical_tables is None:
            return True
        return table.upper() in {t.upper() for t in self.physical_tables}


_FIELD_SPEC = re.compile(
    r"^\s*(?P<type>[A-Z0-9]+)\s*(?:\(\s*(?P<len>\d+)\s*(?:,\s*(?P<dec>\d+)\s*)?\))?"
    r"(?:\s+ref=(?P<ref>[A-Z0-9_]+))?\s*(?P<desc>.*)$"
)


def parse_field_spec(name: str, spec: str, source: Provenance, key: list[str]) -> FieldInfo:
    """Parse the compact `TYPE(len,dec) [ref=FIELD] Description` notation."""
    m = _FIELD_SPEC.match(spec or "")
    if not m:
        return FieldInfo(name=name.upper(), description=str(spec), source=source, is_key=name.upper() in key)
    return FieldInfo(
        name=name.upper(),
        ddic_type=m.group("type"),
        length=int(m.group("len")) if m.group("len") else None,
        decimals=int(m.group("dec")) if m.group("dec") else None,
        ref_field=m.group("ref"),
        description=(m.group("desc") or "").strip(),
        is_key=name.upper() in key,
        source=source,
    )
