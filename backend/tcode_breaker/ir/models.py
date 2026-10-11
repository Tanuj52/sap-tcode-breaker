"""Public intermediate representation (IR) of an analyzed ABAP program.

This is the contract between the analysis engine, the SQL generator, the API and the UI.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from ..knowledge.models import Provenance, ProjectSettings

Severity = Literal["error", "warning", "info"]


class Loc(BaseModel):
    file: str
    line: int
    end_line: int | None = None


class Finding(BaseModel):
    severity: Severity
    code: str
    message: str
    loc: Loc | None = None
    node_id: str | None = None
    hint: str | None = None


class ColumnInfo(BaseModel):
    name: str
    ddic_type: str | None = None
    length: int | None = None
    decimals: int | None = None
    source_table: str | None = None
    source_field: str | None = None
    description: str = ""
    provenance: Provenance = Provenance.UNRESOLVED


class SelectionParam(BaseModel):
    name: str
    kind: Literal["parameter", "select_option", "checkbox", "radiobutton"]
    ref: str | None = None
    ddic_type: str | None = None
    length: int | None = None
    default: str | None = None
    obligatory: bool = False
    no_intervals: bool = False
    loc: Loc | None = None
    provenance: Provenance = Provenance.UNRESOLVED
    used: bool = False


class DataObject(BaseModel):
    name: str
    kind: Literal["internal_table", "structure", "scalar", "field_symbol", "reference", "range", "constant", "tables_wa"]
    type_name: str | None = None
    table_kind: str | None = None
    unique_key: list[str] = Field(default_factory=list)
    columns: list[ColumnInfo] = Field(default_factory=list)
    scope: str = "global"
    inline: bool = False
    value: str | None = None
    loc: Loc | None = None


class ColumnUsage(BaseModel):
    name: str
    status: str  # known | unverified | unknown | no_table
    ddic_type: str | None = None
    length: int | None = None
    decimals: int | None = None
    description: str = ""
    business_name: str = ""
    is_key: bool = False
    usages: list[str] = Field(default_factory=list)  # select, where, join, group, order, type_ref
    provenance: Provenance = Provenance.UNRESOLVED


class TableUsage(BaseModel):
    name: str
    description: str = ""
    business_name: str = ""
    module: str = ""
    release: str = ""
    known: bool = False
    provenance: Provenance = Provenance.UNRESOLVED
    columns: list[ColumnUsage] = Field(default_factory=list)
    reads: int = 0
    writes: int = 0
    in_slice: bool = False
    physical: bool = True
    mapped_to: str | None = None
    s4_note: str | None = None
    locs: list[Loc] = Field(default_factory=list)


class CallInfo(BaseModel):
    id: str
    kind: Literal["perform", "function", "method", "submit", "transaction", "screen"]
    target: str
    caller: str
    loc: Loc | None = None
    fm_kind: str | None = None  # from the FM catalog: expression, lookup, ui, output_sink, side_effect, opaque, custom
    provenance: Provenance = Provenance.UNRESOLVED
    resolved: bool = False
    dynamic: bool = False
    reachable: bool = True
    args: dict[str, str] = Field(default_factory=dict)


class RoutineInfo(BaseModel):
    name: str
    kind: Literal["event", "form", "method", "function_module", "module", "main"]
    loc: Loc | None = None
    end_loc: Loc | None = None
    statements: int = 0
    reachable: bool = False
    calls: list[str] = Field(default_factory=list)  # CallInfo ids


class CallTreeNode(BaseModel):
    id: str
    name: str
    kind: str
    fm_kind: str | None = None
    loc: Loc | None = None
    reachable: bool = True
    recursive: bool = False
    children: list["CallTreeNode"] = Field(default_factory=list)


class LineageSource(BaseModel):
    table: str
    field: str


class OutputColumn(BaseModel):
    name: str
    label: str = ""
    business_name: str = ""
    hidden: bool = False
    ddic_type: str | None = None
    length: int | None = None
    decimals: int | None = None
    lineage: list[LineageSource] = Field(default_factory=list)
    expression: str | None = None  # SQL expression at the last transformation step
    derived: bool = False


class OutputSpec(BaseModel):
    kind: str  # alv_grid | salv | alv_list | write_list | download | inferred
    table: str
    relation_id: str | None = None
    columns: list[OutputColumn] = Field(default_factory=list)
    order_by: list[tuple[str, bool]] = Field(default_factory=list)  # (column, descending)
    column_source: str = "structure"  # fieldcat | structure | inferred
    loc: Loc | None = None


class GraphColumn(BaseModel):
    name: str
    ddic_type: str | None = None
    status: str | None = None
    expression: str | None = None
    derived: bool = False
    business_name: str = ""


class GraphNode(BaseModel):
    id: str
    kind: Literal["db_table", "itab", "op", "param", "output", "fm", "lookup"]
    label: str
    sub: str | None = None
    op: str | None = None
    group: str | None = None
    columns: list[GraphColumn] = Field(default_factory=list)
    loc: Loc | None = None
    status: Literal["ok", "warning", "unresolved", "llm"] = "ok"
    in_slice: bool = True
    data: dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    kind: Literal["read", "join", "lookup", "fae", "filter", "param", "flow", "output", "aggregate"]
    label: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)


class DataFlowGraph(BaseModel):
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)


class FileInfo(BaseModel):
    name: str
    filename: str
    kind: str
    lines: int


class SliceRange(BaseModel):
    file: str
    start: int
    end: int


class ProgramStats(BaseModel):
    lines: int = 0
    statements: int = 0
    slice_statements: int = 0
    slice_lines: int = 0
    tables: int = 0
    columns: int = 0
    routines: int = 0
    dead_routines: int = 0
    calls: int = 0
    relations: int = 0
    deterministic_relations: int = 0
    llm_relations: int = 0


class RelationSummary(BaseModel):
    """A transformation step (one CTE) as exposed to the UI."""

    id: str
    cte: str = ""
    var: str
    kind: str
    label: str = ""
    status: str
    columns: list[str]
    inputs: list[str]
    sql: str
    abap: str = ""
    notes: list[str] = Field(default_factory=list)
    locs: list[Loc] = Field(default_factory=list)
    in_slice: bool = True
    llm_model: str | None = None


class ProgramAnalysis(BaseModel):
    name: str
    settings: ProjectSettings
    files: list[FileInfo] = Field(default_factory=list)
    stats: ProgramStats = Field(default_factory=ProgramStats)
    params: list[SelectionParam] = Field(default_factory=list)
    data_objects: list[DataObject] = Field(default_factory=list)
    tables: list[TableUsage] = Field(default_factory=list)
    calls: list[CallInfo] = Field(default_factory=list)
    routines: list[RoutineInfo] = Field(default_factory=list)
    call_tree: list[CallTreeNode] = Field(default_factory=list)
    graph: DataFlowGraph = Field(default_factory=DataFlowGraph)
    output: OutputSpec | None = None
    relations: list[RelationSummary] = Field(default_factory=list)
    slice: list[SliceRange] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    sql: str | None = None
    sql_status: str = "pending"  # deterministic | needs_llm | partial | failed
    sql_mode: str = "select"
    view_name: str | None = None
    unresolved: list[str] = Field(default_factory=list)
    glossary: dict[str, str] = Field(default_factory=dict)  # TABLE or TABLE-FIELD -> business name
    catalog: dict = Field(default_factory=dict)  # live metadata source summary (Snowflake raw layer)
    programs: list[str] = Field(default_factory=list)  # main programs found in the upload
    output_candidates: list[str] = Field(default_factory=list)  # internal tables that can be chosen as the result
