"""Open SQL (SELECT) -> relational source/column specification.

Handles classic and strict (7.40+) syntax, joins, aliases, aggregates, FOR ALL ENTRIES,
client handling and ECC -> S/4HANA table remapping.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..knowledge.models import Provenance
from ..parser.ast import Node, Statement
from .expr import SqlExpr, initial_for, lit, unknown
from .relations import Source

if TYPE_CHECKING:  # pragma: no cover
    from .engine import Interpreter

CLIENT_FIELDS = ("MANDT", "CLIENT", "RCLNT")


@dataclass
class SqlTable:
    abap_alias: str
    render_alias: str
    original: str
    physical: str  # mapped table name (unqualified)
    qualified: str
    nullable: bool = False
    column_map: dict[str, str] = field(default_factory=dict)
    collapsed_into: str | None = None


@dataclass
class SelectSpec:
    stmt: Statement
    single: bool = False
    distinct: bool = False
    sources: list[Source] = field(default_factory=list)
    tables: dict[str, SqlTable] = field(default_factory=dict)  # abap alias (upper) -> table
    items: list[tuple[str, SqlExpr]] = field(default_factory=list)  # (output name, expr)
    star: bool = False
    where: list[SqlExpr] = field(default_factory=list)
    fae_var: str | None = None
    fae_alias: str | None = None
    fae_conds: list[SqlExpr] = field(default_factory=list)
    group_by: list[SqlExpr] = field(default_factory=list)
    having: list[SqlExpr] = field(default_factory=list)
    order_by: list[tuple[str, bool]] = field(default_factory=list)
    order_primary_key: bool = False
    up_to: int | None = None
    target: str | None = None
    target_kind: str = "table"  # table | struct | list
    targets_list: list[str] = field(default_factory=list)
    inline: bool = False
    corresponding: bool = False
    appending: bool = False
    notes: list[str] = field(default_factory=list)
    base_table: str | None = None

    @property
    def uses_params(self) -> bool:
        exprs = [e for _, e in self.items] + self.where + self.fae_conds + [c for s in self.sources for c in s.on]
        return any(e.uses_params for e in exprs)


class SqlContext:
    """Resolution state while translating one SELECT."""

    def __init__(self, spec: SelectSpec) -> None:
        self.spec = spec
        self.clause = "select"


def conjuncts(node: Node | None) -> list[Node]:
    """Split a condition node on top-level AND (only if there is no top-level OR)."""
    if node is None:
        return []
    toks = [c.value.upper() for c in node.children if c.is_token]
    if "OR" in toks or "EQUIV" in toks or "NOT" in toks:
        return [node]
    parts = [c for c in node.children if not c.is_token]
    return parts or [node]


class SelectBuilder:
    def __init__(self, interp: "Interpreter") -> None:
        self.it = interp

    # ------------------------------------------------------------------ entry
    def build(self, stmt: Statement) -> SelectSpec:
        it = self.it
        sel = stmt.node.child("Select") or stmt.node.child("SelectLoop") or stmt.node
        spec = SelectSpec(stmt=stmt)
        kws = [t.upper() for t in sel.keywords()]
        spec.single = "SINGLE" in kws
        spec.distinct = "DISTINCT" in kws
        fl = sel.first("SQLFieldList") or sel.first("SQLFieldListLoop")
        if fl is not None and fl.has_keyword("DISTINCT"):
            spec.distinct = True

        self._sources(sel, spec)
        ctx = SqlContext(spec)
        prev = it._sql
        it._sql = ctx
        try:
            # joins ON
            ctx.clause = "join"
            for src, cond in self._pending_on:
                src.on = [c for c in (it.tr.cond(n) for n in conjuncts(cond)) if not _self_equal(c)]
            # field list
            ctx.clause = "select"
            self._fields(sel, spec)
            # FOR ALL ENTRIES
            fae = sel.first("SQLForAllEntries")
            if fae is not None:
                src = fae.first("SQLSource")
                fc = src.first("FieldChain") if src is not None else None
                spec.fae_var = (fc.text() if fc is not None else (src.text() if src else "")).lstrip("@").upper()
                spec.fae_alias = it.new_alias("fae")
                it._fae = (spec.fae_var, spec.fae_alias)
            # WHERE
            ctx.clause = "where"
            where_node = _where_node(sel)
            for part in conjuncts(where_node):
                e = it.tr.cond(part)
                if spec.fae_alias and any(a == spec.fae_alias for a, _ in e.deps):
                    spec.fae_conds.append(e)
                else:
                    spec.where.append(e)
            # GROUP BY / HAVING / ORDER BY
            ctx.clause = "group"
            gb = sel.first("SQLGroupBy")
            if gb is not None:
                for f in gb.find_all_outer("SQLField") or gb.find_all_outer("SQLFieldName"):
                    spec.group_by.append(it.tr.source(f.children[0]) if f.type == "SQLField" else it.tr.db_field(f))
            hv = sel.first("SQLHaving")
            if hv is not None:
                for part in conjuncts(hv.first("SQLCond")):
                    spec.having.append(it.tr.cond(part))
            ctx.clause = "order"
            ob = sel.first("SQLOrderBy")
            if ob is not None:
                if ob.has_keyword("PRIMARY"):
                    spec.order_primary_key = True
                else:
                    self._order_by(ob, spec)
            up = sel.first("SQLUpTo")
            if up is not None:
                nums = [t.value for t in up.tokens() if t.value and t.value.isdigit()]
                spec.up_to = int(nums[0]) if nums else None
                if spec.up_to is None:
                    spec.notes.append("UP TO n ROWS with a variable row count")
        finally:
            it._sql = prev
            it._fae = None
        self._client_filter(spec)
        self._target(sel, spec)
        return spec

    # ------------------------------------------------------------------ FROM / JOIN
    def _sources(self, sel: Node, spec: SelectSpec) -> None:
        it = self.it
        self._pending_on: list[tuple[Source, Node | None]] = []
        frm = sel.first("SQLFrom")
        body = frm.first("SQLFromBody") if frm is not None else None
        if body is None:
            spec.notes.append("SELECT without a recognizable FROM clause")
            return
        entries: list[tuple[Node, str, Node | None]] = []
        first = body.child("SQLFromSource")
        if first is not None:
            entries.append((first, "from", None))
        for j in body.direct("SQLJoin"):
            kw = j.keywords()
            jt = "left" if "LEFT" in kw else ("right" if "RIGHT" in kw else ("cross" if "CROSS" in kw else "inner"))
            fs = j.first("SQLFromSource")
            if fs is not None:
                entries.append((fs, jt, j.child("SQLCond")))
        if first is None and not entries:
            # strict syntax "FROM ( a INNER JOIN b ON ... )" nests sources deeper
            for fs in body.find_all("SQLFromSource"):
                entries.append((fs, "from" if not entries else "inner", None))

        used_aliases: set[str] = set()
        by_physical: dict[str, SqlTable] = {}
        for fs, jt, cond in entries:
            dbt = fs.first("DatabaseTable")
            table = (dbt.text() if dbt is not None else fs.text()).upper()
            as_name = fs.first("SQLAsName")
            abap_alias = (as_name.text() if as_name is not None else table).upper()
            physical, mapping = it.map_table(table, spec)
            collapse = mapping is not None and mapping.join_collapse and physical in by_physical
            if collapse:
                target = by_physical[physical]
                spec.tables[abap_alias] = SqlTable(abap_alias, target.render_alias, table, physical, target.qualified,
                                                   target.nullable, _col_map(mapping), collapsed_into=target.abap_alias)
                it.note_table(table, "read", spec.stmt, mapped_to=physical)
                continue
            render = _render_alias(abap_alias if as_name is not None else table, used_aliases)
            used_aliases.add(render)
            qualified = it.qualify(physical)
            nullable = jt == "left"
            st = SqlTable(abap_alias, render, table, physical, qualified, nullable, _col_map(mapping) if mapping else {})
            spec.tables[abap_alias] = st
            if physical not in by_physical:
                by_physical[physical] = st
            # when an unmapped table is collapsed later (VBAK + VBUK), the mapped one joins this entry
            src = Source(alias=render, kind="db", name=qualified, join=("from" if jt == "from" else jt), original=table)
            if mapping is not None and mapping.filter:
                src.extra_filter.append(mapping.filter)
            if jt == "right":
                spec.notes.append("RIGHT OUTER JOIN translated as written; verify initial-value semantics")
            spec.sources.append(src)
            self._pending_on.append((src, cond))
            it.note_table(table, "read", spec.stmt, mapped_to=physical if physical != table else None)
            if spec.base_table is None:
                spec.base_table = table

    def _client_filter(self, spec: SelectSpec) -> None:
        client = self.it.settings.client
        if not client:
            return
        for st in spec.tables.values():
            if st.collapsed_into:
                continue
            info = self.it.kb.table(st.physical)
            if info is None:
                continue
            cf = next((f for f in CLIENT_FIELDS if f in info.key), None)
            if cf:
                spec.where.append(lit(f"{st.render_alias}.{cf.lower()} = '{client}'", "BOOL"))

    # ------------------------------------------------------------------ fields
    def _fields(self, sel: Node, spec: SelectSpec) -> None:
        it = self.it
        fl = sel.first("SQLFieldList") or sel.first("SQLFieldListLoop")
        if fl is None:
            spec.star = True
            return
        if any(t.value == "*" for t in fl.tokens()) and not fl.find_all("SQLAggregation"):
            spec.star = True
            self._star_items(spec)
            return
        for f in fl.find_all_outer("SQLField"):
            as_node = f.child("SQLAsName")
            expr_node = next((c for c in f.children if not c.is_token and c.type != "SQLAsName"), None)
            if expr_node is None:
                continue
            if expr_node.type in ("SQLFieldName", "SQLAliasField"):
                e = it.tr.db_field(expr_node)
                col = expr_node.text().split("~")[-1].upper()
                name = as_node.text().upper() if as_node is not None else col
                if col.endswith("*"):  # alias~*
                    alias = expr_node.text().split("~")[0].upper()
                    self._star_items(spec, only_alias=alias)
                    continue
            elif expr_node.type == "SQLAggregation":
                e = self.aggregation(expr_node)
                name = as_node.text().upper() if as_node is not None else _agg_default_name(expr_node)
            else:
                e = it.tr._operand(expr_node)
                name = as_node.text().upper() if as_node is not None else f"COL{len(spec.items) + 1}"
            spec.items.append((name, e))

    def _star_items(self, spec: SelectSpec, only_alias: str | None = None) -> None:
        it = self.it
        for alias, st in spec.tables.items():
            if st.collapsed_into or (only_alias and alias != only_alias):
                continue
            info = it.kb.table(st.original) or it.kb.table(st.physical)
            if info is None:
                spec.notes.append(f"SELECT * from {st.original}: field list unknown (table not in knowledge base)")
                continue
            for f in info.fields:
                if f in CLIENT_FIELDS and len(spec.tables) == 1:
                    pass
                spec.items.append((f, it.db_column(alias, f)))

    def aggregation(self, node: Node) -> SqlExpr:
        it = self.it
        fn = (node.children[0].value or "").upper()
        if any(t.value == "*" for t in node.tokens()):
            return SqlExpr("COUNT(*)", kind="expr", ddic="INT4")
        inner = node.first("SQLFunctionInput") or node.first("SQLFieldName") or node.first("SQLAliasField")
        arg = it.tr.db_field(inner.first("SQLFieldName") or inner.first("SQLAliasField") or inner) if inner is not None else unknown(node.text())
        distinct = "DISTINCT " if node.has_keyword("DISTINCT") else ""
        ddic = "INT4" if fn == "COUNT" else (arg.ddic if fn in ("MIN", "MAX", "SUM") else "FLTP")
        return arg.combine(sql=f"{fn}({distinct}{arg.sql})", ddic=ddic)

    def _order_by(self, ob: Node, spec: SelectSpec) -> None:
        items: list[tuple[str, bool]] = []
        for c in ob.children:
            if c.type in ("SQLOrderBy", "SQLOrder"):
                self._order_by(c, spec)
                continue
            if c.type in ("SQLFieldName", "SQLAliasField", "SQLField"):
                name = c.text().split("~")[-1].upper()
                items.append((name, False))
            elif c.is_token and c.value.upper() in ("DESCENDING", "DESC") and items:
                items[-1] = (items[-1][0], True)
        spec.order_by.extend(items)

    # ------------------------------------------------------------------ INTO
    def _target(self, sel: Node, spec: SelectSpec) -> None:
        into = sel.first("SQLIntoTable") or sel.first("SQLIntoStructure") or sel.first("SQLIntoList")
        if into is None:
            spec.notes.append("SELECT without INTO target")
            return
        kws = into.keywords()
        spec.corresponding = "CORRESPONDING" in kws
        spec.appending = "APPENDING" in kws
        if into.type == "SQLIntoTable":
            spec.target_kind = "table"
        elif into.type == "SQLIntoList":
            spec.target_kind = "list"
        else:
            spec.target_kind = "struct"
        targets = into.find_all("SQLTarget") or [into]
        names = []
        for t in targets:
            inline = t.first("InlineData")
            tf = t.first("TargetField") or t.first("TargetFieldSymbol")
            if inline is not None:
                spec.inline = True
                tf = inline.first("TargetField")
            if tf is not None:
                # include component chain (INTO wa-comp)
                chain = t.first("Target")
                txt = chain.text() if chain is not None and inline is None else tf.text()
                names.append(txt.lstrip("@").upper().replace(" ", ""))
        if spec.target_kind == "list" or (spec.target_kind == "struct" and len(names) > 1):
            spec.target_kind = "list"
            spec.targets_list = names
            spec.target = names[0] if names else None
        else:
            spec.target = names[0] if names else None


def _where_node(sel: Node) -> Node | None:
    seen_where = False
    for c in sel.children:
        if c.is_token and c.value.upper() == "WHERE":
            seen_where = True
            continue
        if seen_where and c.type == "SQLCond":
            return c
    return None


def _render_alias(name: str, used: set[str]) -> str:
    base = name.lower()
    if len(base) > 4:
        base = base[0]
    alias = base
    n = 2
    while alias in used or alias in ("prm", "src", "as", "on", "in", "or", "by", "to", "is"):
        alias = f"{base}{n}"
        n += 1
    return alias


def _col_map(mapping) -> dict[str, str]:
    if mapping is None or not isinstance(mapping.columns, dict):
        return {}
    return {k.upper(): v.upper() for k, v in mapping.columns.items()}


def _agg_default_name(node: Node) -> str:
    fn = (node.children[0].value or "").upper()
    inner = node.first("SQLFieldName") or node.first("SQLAliasField")
    col = inner.text().split("~")[-1].upper() if inner is not None else "ALL"
    return f"{fn}_{col}" if fn != "COUNT" else "COUNT"


def _self_equal(e: SqlExpr) -> bool:
    parts = [p.strip() for p in e.sql.split("=")]
    return len(parts) == 2 and parts[0] == parts[1]


__all__ = ["SelectBuilder", "SelectSpec", "SqlTable", "conjuncts", "CLIENT_FIELDS", "initial_for", "Provenance"]
