"""Interpreter state, value cells and expression-context callbacks."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..knowledge.kb import KnowledgeBase
from ..knowledge.models import ProjectSettings, S4Mapping
from ..parser.ast import Node, Statement
from .blocks import ProgramStructure
from .expr import ExprTranslator, SqlExpr, initial_for, is_numeric, lit, sql_string, unknown
from .relations import Relation, Source
from .symbols import Comp, Symbols, Var

SYSTEM_FIELDS = {
    "DATUM": ("TO_VARCHAR(CURRENT_DATE(), 'YYYYMMDD')", "DATS"),
    "UZEIT": ("TO_VARCHAR(CURRENT_TIME(), 'HH24MISS')", "TIMS"),
    "UNAME": ("CURRENT_USER()", "CHAR"),
    "DATLO": ("TO_VARCHAR(CURRENT_DATE(), 'YYYYMMDD')", "DATS"),
    "TIMLO": ("TO_VARCHAR(CURRENT_TIME(), 'HH24MISS')", "TIMS"),
    "BATCH": ("''", "CHAR"),  # the SQL runs "online": background-only branches are skipped
    "BINPT": ("''", "CHAR"),
    "CALLD": ("''", "CHAR"),
    "DBCNT": (None, "INT4"),
    "REPID": (None, "CHAR"),
    "CPROG": (None, "CHAR"),
}


@dataclass
class Frame:
    name: str
    scope: str
    symbols: Symbols
    kind: str = "routine"  # routine | fm | global
    aliases: dict[str, str] = field(default_factory=dict)
    values: dict[str, SqlExpr] = field(default_factory=dict)
    param_types: dict[str, Comp] = field(default_factory=dict)


@dataclass
class ItabState:
    rel: Relation | None = None
    sort: list[tuple[str, bool]] = field(default_factory=list)
    literal_rows: list[dict[str, SqlExpr]] | None = None

    def copy(self) -> "ItabState":
        return ItabState(self.rel, list(self.sort), None if self.literal_rows is None else [dict(r) for r in self.literal_rows])


@dataclass
class Emit:
    target: str
    kind: str  # append | collect | insert
    values: dict[str, SqlExpr]
    conds: list[SqlExpr]
    sources: list[Source]
    stmt: Statement


@dataclass
class LoopCtx:
    var: str
    rel: Relation
    alias: str
    row_var: str | None
    assigning: bool
    sources: list[Source]
    where: list[SqlExpr]
    cond_depth: int
    stmt: Statement
    parent: "LoopCtx | None" = None
    emits: list[Emit] = field(default_factory=list)
    modified: bool = False
    updates: list[tuple[list[SqlExpr], dict[str, SqlExpr]]] = field(default_factory=list)
    deletes: list[list[SqlExpr]] = field(default_factory=list)
    unsupported: list[str] = field(default_factory=list)
    stmts: list[Statement] = field(default_factory=list)
    cleared: set[str] = field(default_factory=set)
    nested: bool = False


@dataclass
class OutputRec:
    kind: str
    var: str
    rel: Relation | None
    sort: list[tuple[str, bool]]
    fieldcat: list[dict[str, SqlExpr]] | None
    stmt: Statement
    structure_name: str | None = None


@dataclass
class TableUse:
    name: str
    columns: dict[str, set[str]] = field(default_factory=dict)
    reads: int = 0
    writes: int = 0
    stmts: list[Statement] = field(default_factory=list)
    mapped_to: str | None = None


@dataclass
class RawFinding:
    severity: str
    code: str
    message: str
    stmt: Statement | None = None
    hint: str | None = None


class InterpreterBase:
    """State + ExprContext implementation. Statement handlers live in engine.Interpreter."""

    def __init__(self, kb: KnowledgeBase, settings: ProjectSettings, symbols: Symbols, structure: ProgramStructure,
                 program: str, fm_sources: dict[str, str] | None = None) -> None:
        self.kb = kb
        self.settings = settings
        self.sym = symbols
        self.structure = structure
        self.program = program
        self.fm_sources = {k.upper(): v for k, v in (fm_sources or {}).items()}
        self.tr = ExprTranslator(self)
        self.relations: list[Relation] = []
        self.itabs: dict[str, ItabState] = {}
        self.globals: dict[str, SqlExpr] = {}
        self.frames: list[Frame] = [Frame("GLOBAL", "global", symbols, kind="global")]
        self.conds: list[SqlExpr] = []
        self.loop: LoopCtx | None = None
        self.subrc: SqlExpr | None = None
        self.outputs: list[OutputRec] = []
        self._missing_reported = set()
        self._acc_tokens: set[str] = set()
        self.written_vars = _written_vars(structure)
        self.findings: list[RawFinding] = []
        self.tables: dict[str, TableUse] = {}
        self.executed: set[int] = set()
        self.executed_fm: dict[str, set[int]] = {}
        self.call_stack: list[str] = []
        self.calls_seen: list[tuple[str, str, Statement]] = []  # (kind, target, stmt)
        self.params_used: set[str] = set()
        self.fm_kinds: dict[str, str] = {}
        self._row: tuple[str, Relation | None] | None = None
        self._sql = None
        self._fae: tuple[str, str] | None = None
        self._rid = 0
        self._aid = 0
        self._stop = False
        self._origin = program

    # ------------------------------------------------------------------ findings / ids
    _missing_reported: set

    def finding(self, severity: str, code: str, message: str, stmt: Statement | None = None, hint: str | None = None) -> None:
        key = (code, message, stmt.index if stmt else None, stmt.origin if stmt else None)
        for f in self.findings:
            if (f.code, f.message, f.stmt.index if f.stmt else None, f.stmt.origin if f.stmt else None) == key:
                return
        self.findings.append(RawFinding(severity, code, message, stmt, hint))

    def new_alias(self, prefix: str) -> str:
        self._aid += 1
        return f"{prefix}{self._aid}"

    def new_relation(self, var: str, kind: str, stmts: list[Statement] | None = None, label: str = "") -> Relation:
        self._rid += 1
        rel = Relation(id=f"__R{self._rid}__", var=var, kind=kind, stmts=list(stmts or []), label=label)
        self.relations.append(rel)
        return rel

    # ------------------------------------------------------------------ names, frames, cells
    @property
    def frame(self) -> Frame:
        return self.frames[-1]

    def locate(self, name: str) -> tuple[str, int]:
        """Resolve FORM/FM parameter aliases. Returns (canonical name, frame index owning it; 0 = global)."""
        n = name.upper()
        i = len(self.frames) - 1
        while i > 0 and n in self.frames[i].aliases:
            n = self.frames[i].aliases[n]
            i -= 1
        while i > 0:
            fr = self.frames[i]
            if fr.kind == "fm" or (fr.scope, n) in fr.symbols.vars or n in fr.param_types or _has_prefix(fr.values, n):
                return n, i
            if fr.kind == "routine":
                # FORM locals are declared in the symbol table; everything else is global
                break
            i -= 1
        return n, 0

    def store(self, idx: int) -> dict[str, SqlExpr]:
        return self.globals if idx == 0 else self.frames[idx].values

    def var_info(self, name: str) -> Var | None:
        n, idx = self.locate(name)
        fr = self.frames[idx]
        return fr.symbols.var(n, fr.scope if idx else "global")

    def comp_of(self, base: str, comps: list[str]) -> Comp | None:
        n, idx = self.locate(base)
        fr = self.frames[idx]
        if not comps and n in fr.param_types:
            return fr.param_types[n]
        v = fr.symbols.var(n, fr.scope if idx else "global")
        if v is None:
            return None
        if not comps:
            return v.type.elem if v.type.kind == "elem" else None
        if v.type.kind in ("struct", "table"):
            return v.type.comp(comps[0])
        return None

    def struct_comps(self, name: str) -> list[str]:
        v = self.var_info(name)
        if v is not None:
            cols = [c.name for c in v.type.columns()]
            if cols:
                return cols
        n, idx = self.locate(name)
        prefix = n + "-"
        return [k[len(prefix):] for k in self.store(idx) if k.startswith(prefix) and "-" not in k[len(prefix):]]

    def key(self, base: str, comps: list[str]) -> tuple[str, int]:
        n, idx = self.locate(base)
        return (n + "".join("-" + c.upper() for c in comps)), idx

    def get_cell(self, base: str, comps: list[str]) -> SqlExpr | None:
        k, idx = self.key(base, comps)
        return self.store(idx).get(k)

    def set_cell(self, base: str, comps: list[str], value: SqlExpr) -> None:
        k, idx = self.key(base, comps)
        self.store(idx)[k] = value

    def struct_cells(self, name: str) -> dict[str, SqlExpr]:
        n, idx = self.locate(name)
        st = self.store(idx)
        out: dict[str, SqlExpr] = {}
        for comp in self.struct_comps(name):
            v = st.get(f"{n}-{comp}")
            if v is None:
                c = self.comp_of(name, [comp])
                v = lit(initial_for(c.ddic_type if c else None, c.length if c else None), c.ddic_type if c else None)
            out[comp] = v
        return out

    def clear_var(self, base: str, comps: list[str] | None = None) -> None:
        n, idx = self.locate(base)
        st = self.store(idx)
        if comps:
            c = self.comp_of(base, comps)
            st[n + "".join("-" + x.upper() for x in comps)] = lit(initial_for(c.ddic_type if c else None, c.length if c else None), c.ddic_type if c else None)
            return
        v = self.var_info(base)
        if v is not None and v.is_table and not v.header_line:
            self.set_itab(base, ItabState(rel=self.empty_relation(base)))
            return
        prefix = n + "-"
        for k in [k for k in st if k.startswith(prefix)]:
            del st[k]
        for comp in self.struct_comps(base):
            c = self.comp_of(base, [comp])
            st[f"{n}-{comp}"] = lit(initial_for(c.ddic_type if c else None, c.length if c else None), c.ddic_type if c else None)
        if v is not None and v.type.kind == "elem":
            st[n] = lit(initial_for(v.type.elem.ddic_type if v.type.elem else None), v.type.elem.ddic_type if v.type.elem else None)
        if self.loop is not None:
            self.loop.cleared.add(n)

    def bind_row(self, var: str, alias: str, rel: Relation, nullable: bool) -> None:
        n, idx = self.locate(var)
        st = self.store(idx)
        prefix = n + "-"
        for k in [k for k in st if k.startswith(prefix)]:
            del st[k]
        for c in rel.columns:
            ddic = c.comp.ddic_type if c.comp else c.expr.ddic
            length = c.comp.length if c.comp else None
            st[f"{n}-{c.name}"] = self.col(alias, c.name, ddic, nullable, length)

    def col(self, alias: str, name: str, ddic: str | None, nullable: bool = False, length: int | None = None) -> SqlExpr:
        ref = f"{alias}.{name.lower()}"
        if nullable:
            e = SqlExpr(f"COALESCE({ref}, {initial_for(ddic, length)})", {(alias, name.upper())}, "expr", ddic)
            e.nullable = {alias}
            return e
        return SqlExpr(ref, {(alias, name.upper())}, "col", ddic)

    # ------------------------------------------------------------------ itabs
    def itab_key(self, name: str) -> str:
        n, idx = self.locate(name)
        return n if idx == 0 else f"{self.frames[idx].scope}:{n}"

    def itab(self, name: str) -> ItabState:
        k = self.itab_key(name)
        if k not in self.itabs:
            self.itabs[k] = ItabState()
        return self.itabs[k]

    def set_itab(self, name: str, state: ItabState) -> None:
        self.itabs[self.itab_key(name)] = state

    def row_comps(self, name: str) -> list[Comp]:
        v = self.var_info(name)
        if v is None:
            return []
        return [c.copy() for c in v.type.columns()]

    def empty_relation(self, var: str) -> Relation:
        rel = self.new_relation(var.upper(), "empty", label="empty")
        rel.is_empty = True
        from .relations import OutCol

        rel.columns = [OutCol(c.name, lit("NULL", c.ddic_type), c) for c in self.row_comps(var)]
        return rel

    def current_rel(self, name: str) -> Relation:
        st = self.itab(name)
        if st.rel is None:
            if st.literal_rows:
                st.rel = self.values_relation(name, st.literal_rows)
            else:
                st.rel = self.empty_relation(name)
        return st.rel

    def values_relation(self, name: str, rows: list[dict[str, SqlExpr]]) -> Relation:
        from .relations import OutCol

        comps = self.row_comps(name)
        names = [c.name for c in comps] or sorted({k for r in rows for k in r})
        rel = self.new_relation(name.upper(), "values", label="literal rows")
        selects = []
        for r in rows:
            parts = []
            for nme in names:
                c = next((x for x in comps if x.name == nme), None)
                v = r.get(nme) or lit(initial_for(c.ddic_type if c else None, c.length if c else None))
                parts.append(f"{v.sql} AS {nme.lower()}")
            selects.append("SELECT " + ", ".join(parts))
        rel.raw_sql = "\nUNION ALL\n".join(selects) if selects else None
        rel.columns = [OutCol(n, lit("NULL"), next((x for x in comps if x.name == n), None)) for n in names]
        return rel

    # ------------------------------------------------------------------ tables
    def map_table(self, table: str, spec=None) -> tuple[str, S4Mapping | None]:
        t = table.upper()
        if self.settings.source_system == "s4" and not self.settings.is_physical(t):
            m = self.kb.s4_mapping_for(t)
            if m is not None and m.new_table:
                self.finding("info" if m.confidence == "high" else "warning", "S4_TABLE_MAPPED",
                             f"{t} is not a physical table in the S/4HANA replica; reading {m.new_table} instead ({m.title}).",
                             spec.stmt if spec else None, m.note.strip() or None)
                return m.new_table.upper(), m
            self.finding("warning", "TABLE_NOT_REPLICATED", f"Table {t} is not in the list of tables replicated to Snowflake.",
                         spec.stmt if spec else None)
        elif self.settings.source_system == "s4":
            m = self.kb.s4_mapping_for(t)
            if m is not None and m.new_table is None:
                self.finding("info", "S4_NOTE", f"{t}: {m.title}.", spec.stmt if spec else None, m.note.strip() or None)
        if self.settings.source_system != "s4" and not self.settings.is_physical(t) and t not in self._missing_reported:
            self._missing_reported.add(t)
            self.finding("warning", "TABLE_NOT_IN_SOURCE", f"{t} was not found in the Snowflake source schema "
                         f"{'.'.join(p for p in (self.settings.target_database, self.settings.target_schema) if p)}.",
                         spec.stmt if spec else None, "Replicate the table, or map it with a table rename.")
        return t, None

    def qualify(self, table: str) -> str:
        from ..knowledge.catalog import physical_name

        name = physical_name(table, self.settings).lower()
        if "." in name:  # a rename may already be fully qualified
            return name
        parts = [p for p in (self.settings.target_database, self.settings.target_schema) if p]
        return ".".join([p.lower() for p in parts] + [name])

    def note_table(self, table: str, mode: str, stmt: Statement | None, column: str | None = None,
                   usage: str | None = None, mapped_to: str | None = None) -> None:
        t = table.upper()
        tu = self.tables.setdefault(t, TableUse(t))
        if mapped_to:
            tu.mapped_to = mapped_to
        if column is None:
            if mode == "read":
                tu.reads += 1
            elif mode == "write":
                tu.writes += 1
            if stmt is not None and stmt not in tu.stmts:
                tu.stmts.append(stmt)
            return
        tu.columns.setdefault(column.upper(), set()).add(usage or mode)

    # ------------------------------------------------------------------ ExprContext
    def field(self, base: str, comps: list[str], node: Node) -> SqlExpr:
        b = base.upper().lstrip("@")
        comps = [c.upper() for c in comps]
        if b == "__ROW__" and self._row is not None:
            alias, rel = self._row
            c = rel.col(comps[0]) if rel is not None and comps else None
            ddic = c.comp.ddic_type if c is not None and c.comp else (c.expr.ddic if c else None)
            return self.col(alias, comps[0] if comps else "TABLE_LINE", ddic)
        if self._fae is not None and b == self._fae[0] and comps:
            rel = self.current_rel(b)
            c = rel.col(comps[0])
            return self.col(self._fae[1], comps[0], c.comp.ddic_type if c is not None and c.comp else None)
        if b == "SY":
            return self.system_field(comps[0] if comps else "")
        if b in ("ABAP_TRUE",):
            return lit("'X'", "CHAR")
        if b in ("ABAP_FALSE", "SPACE"):
            return lit("''", "CHAR")
        if b == "ABAP_UNDEFINED":
            return lit("'-'", "CHAR")

        n, idx = self.locate(b)
        if idx == 0 and n in self.sym.params:
            p = self.sym.params[n]
            self.params_used.add(n)
            if p.kind == "select_option":
                if comps:
                    return unknown(f"{b}-{'-'.join(comps)}", "component of a select-option")
                return SqlExpr(n, kind="range_ref", var=n)
            e = SqlExpr(f"prm.{n.lower()}", kind="param", ddic=p.comp.ddic_type, uses_params=True)
            return e
        cell = self.store(idx).get(n + "".join("-" + c for c in comps))
        if cell is not None:
            return cell
        v = self.var_info(b)
        if v is not None:
            if v.kind == "constant" and v.value is not None and not comps:
                return self.tr.string_literal(v.value) if v.value.startswith(("'", "`")) or re.fullmatch(r"-?\d+", v.value) else lit(sql_string(v.value))
            if v.kind == "range" and not comps:
                return SqlExpr(n, kind="range_ref", var=n)
            if v.is_table and not comps and not v.header_line:
                rel = self.current_rel(b)
                e = SqlExpr(rel.id, kind="itab", var=n)
                e.rels = {rel.id}
                return e
            c = v.type.comp(comps[0]) if comps and v.type.kind in ("struct", "table") else (v.type.elem if not comps else None)
            if c is not None or (not comps and v.type.kind == "elem"):
                ddic = c.ddic_type if c else None
                if self.loop is not None and v.scope == "global" and v.kind in ("structure", "scalar") and n not in self.loop.cleared:
                    # value from before the loop / previous iteration: initial on first use
                    pass
                return lit(initial_for(ddic, c.length if c else None), ddic)
        if not comps and b.upper() in self.fm_param_names():
            return lit("''")
        if v is not None and n not in self.written_vars and b not in self.written_vars:
            # declared but never written anywhere in the program: ABAP initial value
            c = self.comp_of(b, comps) if comps else None
            return lit(initial_for(c.ddic_type if c else None), c.ddic_type if c else None)
        return unknown(base + "".join("-" + c for c in comps), "value not tracked")

    def fm_param_names(self) -> set[str]:
        return set(self.frame.param_types) if self.frame.kind == "fm" else set()

    def system_field(self, name: str) -> SqlExpr:
        n = name.upper()
        if n == "SUBRC":
            if self.subrc is not None:
                return self.subrc
            return unknown("sy-subrc", "not bound to a lookup")
        if n in ("LANGU", "SPRAS"):
            return lit(sql_string(self.settings.language), "LANG")
        if n == "MANDT":
            return lit(sql_string(self.settings.client or ""), "CLNT")
        if n in ("REPID", "CPROG"):
            return lit(sql_string(self.program), "CHAR")
        if n in SYSTEM_FIELDS and SYSTEM_FIELDS[n][0]:
            return lit(SYSTEM_FIELDS[n][0], SYSTEM_FIELDS[n][1])
        return unknown(f"sy-{name}", "system field")

    def db_column(self, alias: str | None, column: str) -> SqlExpr:
        ctx = self._sql
        col = column.upper()
        if ctx is None:
            return unknown(f"{alias}~{column}" if alias else column, "database column outside SQL")
        spec = ctx.spec
        st = None
        if alias is not None:
            st = spec.tables.get(alias.upper())
        else:
            live = [t for t in spec.tables.values()]
            if len({t.render_alias for t in live}) == 1:
                st = live[0]
            else:
                hits = [t for t in live if self.kb.field(t.original, col)[0] is not None]
                st = hits[0] if hits else (live[0] if live else None)
                if len(hits) != 1:
                    self.finding("warning", "AMBIGUOUS_COLUMN", f"Column {col} could belong to several joined tables; assumed {st.original if st else '?'}.", spec.stmt)
        if st is None:
            return unknown(f"{alias}~{column}", "unknown table alias")
        phys_col = st.column_map.get(col, col)
        self.note_table(st.original, "read", None, col, ctx.clause)
        if st.physical != st.original:
            self.note_table(st.physical, "read", None, phys_col, ctx.clause, None)
        finfo, status = self.kb.field(st.physical, phys_col)
        if finfo is None:
            finfo, status = self.kb.field(st.original, col)
        ddic = finfo.ddic_type if finfo else None
        length = finfo.length if finfo else None
        if status.value == "unknown":
            self.finding("warning", "UNKNOWN_COLUMN", f"{st.original}-{col} is not a field of {st.original} in the knowledge base.", spec.stmt)
        nullable = st.nullable and ctx.clause == "select"
        return self.col(st.render_alias, phys_col, ddic, nullable, length)

    def sql_function(self, node: Node) -> SqlExpr:
        if node.type == "SQLAggregation":
            from .opensql import SelectBuilder

            return SelectBuilder(self).aggregation(node)  # type: ignore[arg-type]
        if node.type == "SQLCase":
            return unknown(node.text(), "CASE in Open SQL")
        name_tok = node.first_token()
        fn = (name_tok.value if name_tok else "").upper()
        args = [self.tr.source(c) for c in node.find_all_outer("SQLFunctionInput")] or [self.tr.source(c) for c in node.direct("SQLSource")]
        simple = {"ABS": "ABS", "CEIL": "CEIL", "FLOOR": "FLOOR", "LOWER": "LOWER", "UPPER": "UPPER", "LENGTH": "LENGTH",
                  "COALESCE": "COALESCE", "CONCAT": "CONCAT", "ROUND": "ROUND", "SUBSTRING": "SUBSTR", "LPAD": "LPAD",
                  "RPAD": "RPAD", "LTRIM": "LTRIM", "RTRIM": "RTRIM", "REPLACE": "REPLACE", "DIV": "DIV0", "MOD": "MOD"}
        if fn in simple and args:
            return args[0].combine(*args[1:], sql=f"{simple[fn]}({', '.join(a.sql for a in args)})", ddic=args[0].ddic)
        return unknown(node.text(), f"Open SQL function {fn}")

    def in_range(self, lhs: SqlExpr, name: str, negate: bool) -> SqlExpr:
        n, idx = self.locate(name)
        if idx == 0 and n in self.sym.params and self.sym.params[n].kind == "select_option":
            self.params_used.add(n)
            arr = f"prm.{n.lower()}"
            test = f"(ARRAY_SIZE({arr}) = 0 OR ARRAY_CONTAINS({lhs.sql}::VARIANT, {arr}))"
            res = lhs.combine(sql=f"NOT {test}" if negate else test, ddic="BOOL")
            res.uses_params = True
            if self.sym.params[n].no_intervals is False:
                self.finding("info", "SELECT_OPTION_EQ_ONLY",
                             f"Select-option {n} is passed as an ARRAY of single values (I/EQ). Ranges/patterns need the RANGE table variant.", None)
            return res
        st = self.itab(n)
        if st.literal_rows is not None:
            inc: list[str] = []
            exc: list[str] = []
            for r in st.literal_rows:
                sign = (r.get("SIGN").sql if r.get("SIGN") else "'I'").strip("'")
                opt = (r.get("OPTION").sql if r.get("OPTION") else "'EQ'").strip("'")
                low = r.get("LOW") or lit("''")
                high = r.get("HIGH") or lit("''")
                expr = {"EQ": f"{lhs.sql} = {low.sql}", "NE": f"{lhs.sql} <> {low.sql}", "BT": f"{lhs.sql} BETWEEN {low.sql} AND {high.sql}",
                        "NB": f"{lhs.sql} NOT BETWEEN {low.sql} AND {high.sql}", "GT": f"{lhs.sql} > {low.sql}",
                        "GE": f"{lhs.sql} >= {low.sql}", "LT": f"{lhs.sql} < {low.sql}", "LE": f"{lhs.sql} <= {low.sql}",
                        "CP": f"{lhs.sql} ILIKE REPLACE(REPLACE({low.sql}, '*', '%'), '+', '_')"}.get(opt)
                if expr is None:
                    return unknown(f"{lhs.sql} IN {n}", f"range option {opt}")
                (exc if sign == "E" else inc).append(expr)
            if not inc and not exc:
                return lit("TRUE", "BOOL")
            sql = "(" + " OR ".join(inc) + ")" if inc else "TRUE"
            if exc:
                sql += " AND NOT (" + " OR ".join(exc) + ")"
            res = lhs.combine(sql=f"NOT ({sql})" if negate else f"({sql})", ddic="BOOL")
            return res
        return unknown(f"{lhs.sql} IN {n}", "range table filled at runtime")

    def range_initial(self, name: str) -> SqlExpr:
        n, idx = self.locate(name)
        if idx == 0 and n in self.sym.params:
            self.params_used.add(n)
            e = SqlExpr(f"ARRAY_SIZE(prm.{n.lower()}) = 0", kind="expr", ddic="BOOL", uses_params=True)
            return e
        st = self.itab(n)
        if st.literal_rows is not None:
            return lit("FALSE" if st.literal_rows else "TRUE", "BOOL")
        return unknown(f"{n} IS INITIAL")

    def lines(self, name: str) -> SqlExpr:
        n = name.upper().rstrip("[]")
        rel = self.current_rel(n)
        e = SqlExpr(f"(SELECT COUNT(*) FROM {rel.id})", kind="expr", ddic="INT4")
        e.rels = {rel.id}
        return e

    def table_expression(self, node: Node) -> SqlExpr:
        return unknown(node.text(), "table expression")

    def text_symbol(self, key: str) -> SqlExpr:
        self.finding("info", "TEXT_SYMBOL", f"Text symbol {key} has no text pool; its key is used as a literal.", None)
        return lit(sql_string(f"TEXT-{key}"), "CHAR")

    def reduce(self, node: Node) -> SqlExpr:
        body = node.child("ReduceBody")
        if body is None:
            return unknown(node.text(), "REDUCE")
        init = body.child("InlineFieldDefinition")
        fors = body.direct("For")
        nxt = body.child("ReduceNext")
        if init is None or len(fors) != 1 or nxt is None:
            return unknown(node.text(), "REDUCE pattern")
        acc = (init.first("Field").text() if init.first("Field") else "").upper()
        init_val = self.tr.source(init.child("Source"))
        loopdef = fors[0].child("InlineLoopDefinition")
        if loopdef is None:
            return unknown(node.text(), "REDUCE pattern")
        row_var = loopdef.first("TargetField").text().upper()
        itab_name = loopdef.child("Source").text().upper()
        rel = self.current_rel(itab_name)
        alias = self.new_alias("r")
        saved_row = self._row
        n, idx = self.locate(row_var)
        saved = {k: v for k, v in self.store(idx).items() if k.startswith(n + "-")}
        self.bind_row(row_var, alias, rel, False)
        self._row = (alias, rel)
        try:
            where_node = fors[0].child("ComponentCond") or fors[0].child("Cond")
            where = self.tr.cond(where_node) if where_node is not None else None
            src = nxt.child("Source")
            parts = self.tr._flatten(src) if src is not None else []
            # NEXT acc = acc + <expr>
            if len(parts) >= 3 and parts[1] == ("op", "+") and getattr(parts[0][1], "sql", "").upper().endswith(acc) is False:
                pass
            first = parts[0][1] if parts else None
            is_acc = first is not None and isinstance(first, SqlExpr) and (first.unknown and acc in first.unknown[0].upper() or first.sql.upper() == acc)
            if not (len(parts) >= 3 and is_acc and parts[1] == ("op", "+")):
                return unknown(node.text(), "REDUCE pattern")
            rest = self.tr._build(parts[2:])
            agg = "COUNT(*)" if rest.kind == "lit" and rest.sql == "1" else f"SUM({rest.sql})"
            sql = f"(SELECT {agg} FROM {rel.id} {alias}" + (f" WHERE {where.sql}" if where is not None else "") + ")"
            res = (where or rest).combine(rest, sql=f"{init_val.sql} + COALESCE({sql}, 0)" if init_val.sql != "0" else f"COALESCE({sql}, 0)", ddic="INT4")
            res.deps = {d for d in res.deps if d[0] != alias}
            res.rels = res.rels | {rel.id}
            return res
        finally:
            st = self.store(idx)
            for k in [k for k in st if k.startswith(n + "-")]:
                del st[k]
            st.update(saved)
            self._row = saved_row

    # ------------------------------------------------------------------ conversions
    def convert(self, e: SqlExpr, comp: Comp | None) -> SqlExpr:
        if comp is None or comp.ddic_type is None or e.kind == "unknown":
            return e
        t = comp.ddic_type.upper()
        src = (e.ddic or "").upper()
        if is_numeric(t):
            if e.kind == "lit" and e.sql.startswith("'"):
                body = e.sql.strip("'").strip()
                if re.fullmatch(r"-?\d+(\.\d+)?", body):
                    return lit(body, t)
                if body == "":
                    return lit("0", t)
            elif src in ("CHAR", "NUMC", "STRG", "SSTR", "CUKY", "UNIT", "LANG", "CLNT"):
                e = e.combine(sql=f"TRY_TO_NUMBER({e.sql})", ddic=t)
            if "/" in e.sql and e.kind != "lit":
                dec = comp.decimals if t in ("DEC", "CURR", "QUAN") else (0 if t.startswith("INT") else None)
                if dec is not None and "ROUND(" not in e.sql:
                    e = e.combine(sql=f"ROUND({e.sql}, {dec})", ddic=t)
            out = e.combine(sql=e.sql, kind=e.kind, ddic=t)
            out.found_alias = e.found_alias
            return out
        if t in ("CHAR", "STRG", "SSTR") and is_numeric(src):
            return e.combine(sql=f"TO_VARCHAR({e.sql})", ddic=t)
        if t == "NUMC" and is_numeric(src):
            return e.combine(sql=f"LPAD(TO_VARCHAR({e.sql}), {comp.length or 1}, '0')", ddic=t)
        if src == "" and e.kind != "lit":
            out = e.combine(sql=e.sql, kind=e.kind, ddic=t)
            return out
        return e

    def guard(self, exclude_itab: str | None = None) -> tuple[list[SqlExpr], list[str]]:
        """Top-level conditions active for the current statement."""
        start = self.loop.cond_depth if self.loop is not None else 0
        out: list[SqlExpr] = []
        problems: list[str] = []
        for c in self.conds[start:] if self.loop is not None else self.conds:
            if c.itab_guard and (exclude_itab is None or c.itab_guard == exclude_itab.upper()):
                if exclude_itab is not None:
                    continue
            if c.unknown:
                problems.extend(c.unknown)
                continue
            out.append(c)
        return out, problems


def _has_prefix(d: dict[str, SqlExpr], name: str) -> bool:
    if name in d:
        return True
    p = name + "-"
    return any(k.startswith(p) for k in d)


_WRITE_NODES = ("Target", "SQLTarget", "FSTarget", "InlineData", "InlineFS", "InlineFieldDefinition", "SimpleTarget")


def _written_vars(structure) -> set[str]:
    """Names of every variable that is a write target somewhere (assignment, INTO, ASSIGNING, CHANGING ...)."""
    out: set[str] = set()
    stmts = list(structure.global_decls)
    for r in structure.routines.values():
        stmts.extend(r.statements)
        if r.header is not None:
            stmts.append(r.header)
    for st in stmts:
        node = getattr(st, "node", None)
        if node is None:
            continue
        for t in _WRITE_NODES:
            for n in node.find_all(t):
                txt = n.text().upper().lstrip("@")
                txt = re.sub(r"^(DATA|FINAL|FIELD-SYMBOL)\(", "", txt).rstrip(")")
                base = re.split(r"[-\[]|->|=>", txt, maxsplit=1)[0].strip()
                if base:
                    out.add(base)
        if st.type in ("Parameter", "SelectOption", "Form", "MethodImplementation"):
            out.update(x.upper() for x in st.tokens()[1:2])
    return out
