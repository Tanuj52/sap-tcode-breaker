"""Statement handlers for the symbolic interpreter (mixin)."""

from __future__ import annotations

import re

from ..parser.ast import Node, Statement
from .engine_base import Emit, Frame, ItabState, OutputRec
from .expr import SqlExpr, initial_for, lit, unknown
from .opensql import SelectBuilder, conjuncts
from .relations import OutCol, Relation, Source, placeholder_sql
from .symbols import Comp, tokenize

IGNORED = {
    "Write", "Message", "Format", "Uline", "Skip", "NewLine", "NewPage", "SetPFStatus", "SetTitlebar", "GetTime",
    "GetRunTime", "Commit", "Rollback", "SetScreen", "LeaveScreen", "SetCursor", "Comment", "Empty", "Data", "Type",
    "TypeBegin", "TypeEnd", "DataBegin", "DataEnd", "Constant", "ConstantBegin", "ConstantEnd", "FieldSymbol",
    "Static", "Tables", "Ranges", "TypePools", "Parameter", "SelectOption", "SelectionScreen", "Include", "Report",
    "Program", "SetHandler", "Raise", "Unassign", "Free", "SetParameter", "GetParameter", "Position", "Hide",
    "Summary", "Detail", "Reserve", "Back", "CreateObject", "SetLanguage",
}
DB_WRITES = {"InsertDatabase", "ModifyDatabase", "UpdateDatabase", "DeleteDatabase"}


class StatementMixin:
    # ------------------------------------------------------------------ dispatch
    def exec_stmt(self, s: Statement) -> str | None:  # noqa: C901 - dispatcher
        t = s.type
        if self.loop is not None:
            self.loop.stmts.append(s)
        handler = {
            "Move": self.exec_move, "MoveCorresponding": self.exec_move_corresponding, "Clear": self.exec_clear,
            "Refresh": self.exec_clear, "Select": self.exec_select, "ReadTable": self.exec_read,
            "Append": self.exec_append, "InsertInternal": self.exec_insert, "Collect": self.exec_collect,
            "ModifyInternal": self.exec_modify, "DeleteInternal": self.exec_delete, "Sort": self.exec_sort,
            "Perform": self.exec_perform, "CallFunction": self.exec_call_function, "Call": self.exec_method_call,
            "Assign": self.exec_assign, "Concatenate": self.exec_concatenate, "Condense": self.exec_condense,
            "Translate": self.exec_translate, "Shift": self.exec_shift,
            "Add": self.exec_arith, "Subtract": self.exec_arith, "Multiply": self.exec_arith, "Divide": self.exec_arith,
        }.get(t)
        if t == "Check":
            return self.exec_check(s)
        if t in ("Return", "Exit", "Continue", "Leave", "Stop"):
            if self.loop is not None and t == "Exit":
                self.loop.unsupported.append(f"EXIT inside LOOP (line {s.row})")
            return "terminal"
        if t in DB_WRITES:
            tab = next((n.text() for n in s.node.find_all("DatabaseTable")), "?")
            if t == "ModifyDatabase" and self._modify_itab_ambiguous(s, tab):
                return None
            self.note_table(tab, "write", s)
            self.finding("warning", "DB_WRITE", f"Program writes to database table {tab.upper()}; writes are not part of the SQL output.", s)
            return None
        if t == "AuthorityCheck":
            self.finding("info", "AUTHORITY_CHECK", "AUTHORITY-CHECK is not replicated; consider a Snowflake row access policy.", s)
            self.success_subrc()
            return None
        if t in ("Submit", "CallTransaction", "CallScreen", "CallSelectionScreen"):
            self.finding("warning", "EXTERNAL_CALL", f"{s.text.split('.')[0]} calls another program/screen; not followed.", s)
            self.calls_seen.append(("submit" if t == "Submit" else "transaction", s.tokens()[1] if len(s.tokens()) > 1 else "?", s))
            return None
        if handler is not None:
            try:
                handler(s)
            except Exception as exc:  # noqa: BLE001 - one bad statement must not kill the analysis
                self.unsupported(s, f"interpreter error: {exc}")
            return None
        if t in IGNORED:
            return None
        self.unsupported(s, f"statement {t} not interpreted")
        return None

    def exists_subrc(self, rel: Relation) -> SqlExpr:
        e = SqlExpr(f"EXISTS (SELECT 1 FROM {rel.id})", kind="subrc_bool", ddic="BOOL")
        e.rels = {rel.id}
        return e

    def success_subrc(self) -> None:
        """After calls whose return code we cannot evaluate, follow the success path (sy-subrc = 0)."""
        self.subrc = SqlExpr("TRUE", kind="subrc_bool", ddic="BOOL")

    def exec_arith(self, s: Statement) -> None:
        """ADD a TO b / SUBTRACT a FROM b / MULTIPLY b BY a / DIVIDE b BY a."""
        src = s.node.child("Source")
        tnode = s.node.child("Target")
        if src is None or tnode is None:
            self.unsupported(s, f"{s.type} form")
            return
        base, comps, _ = self._target_parts(tnode)
        if base is None:
            return
        cur = self.field(base, comps, s.node)
        val = self.tr.source(src)
        op = {"Add": "+", "Subtract": "-", "Multiply": "*", "Divide": "/"}[s.type]
        self._assign(base, comps, cur.combine(val, sql=f"({cur.sql} {op} {val.sql})", ddic=cur.ddic or val.ddic), s)

    def unsupported(self, s: Statement, reason: str) -> None:
        msg = f"line {s.row}: {reason}: {s.text[:120]}"
        if self.loop is not None:
            self.loop.unsupported.append(msg)
            return
        # top level: if the statement writes an internal table, that table now needs the LLM
        targets = [n.text().upper() for n in s.node.find_all("TargetField")][:1]
        for name in targets:
            v = self.var_info(name)
            if v is not None and v.is_table:
                prev = self.current_rel(name)
                rel = self.new_relation(v.name, "llm", [s], label=f"{s.type} (needs LLM)")
                rel.columns = [OutCol(c.name, lit("NULL", c.ddic_type), c) for c in self.row_comps(name)] or list(prev.columns)
                rel.status = "needs_llm"
                rel.notes.append(reason)
                rel.abap = s.text
                rel.raw_sql = placeholder_sql(rel.columns, prev, reason, keep_rows=True)
                self.itab(name).rel = rel
        self.finding("warning", "UNSUPPORTED", f"{reason}: {s.text[:100]}", s)

    # ------------------------------------------------------------------ helpers
    def _target_parts(self, node: Node | None) -> tuple[str | None, list[str], bool]:
        """Target node -> (base, components, inline)."""
        if node is None:
            return None, [], False
        inline = node.first("InlineData") if node.type != "InlineData" else node
        if inline is not None:
            tf = inline.first("TargetField")
            return (tf.text().upper() if tf else None), [], True
        base = None
        comps: list[str] = []
        for c in node.children:
            if c.type in ("TargetField", "TargetFieldSymbol", "Field", "FieldSymbol", "SourceField", "SourceFieldSymbol"):
                base = c.text().upper()
            elif c.type == "ComponentName":
                comps.append(c.text().upper())
            elif c.type in ("FieldOffset", "FieldLength"):
                comps.append("#OFFSET")
        if base is None:
            fc = node.first("TargetField") or node.first("TargetFieldSymbol")
            base = fc.text().upper() if fc else node.text().upper()
        return base, comps, False

    def _source_name(self, node: Node | None) -> str | None:
        if node is None:
            return None
        fc = node.first("FieldChain") or node.first("SimpleFieldChain") or node.first("SourceField") or node.first("Field")
        txt = (fc.text() if fc is not None else node.text()).upper()
        return txt.replace("[]", "").strip()

    def _assign(self, base: str, comps: list[str], value: SqlExpr, s: Statement) -> None:
        if "#OFFSET" in comps:
            self.unsupported(s, "assignment to an offset/length of a field")
            return
        comp = self.comp_of(base, comps)
        if not (self._acc_tokens and any(t in value.sql for t in self._acc_tokens)):
            value = self.convert(value, comp)  # accumulators are converted once, after the nested loop
        if self.loop is not None and value.unknown:
            self.loop.unsupported.append(f"line {s.row}: value not translatable: {'; '.join(value.unknown)[:150]}")
        n, _ = self.locate(base)
        if self.loop is not None and self.loop.row_var and self.loop.assigning and n == self.loop.row_var:
            self.loop.modified = True
        self.set_cell(base, comps, value)

    # ------------------------------------------------------------------ assignments
    def exec_move(self, s: Statement) -> None:
        tgt_nodes = s.node.direct("Target")
        src = s.node.child("Source")
        if not tgt_nodes or src is None:
            self.unsupported(s, "assignment form")
            return
        first = src.children[0] if src.children else None
        kw = first.value.upper() if first is not None and first.is_token else None
        for tnode in tgt_nodes:
            base, comps, inline = self._target_parts(tnode)
            if base is None:
                continue
            v = self.var_info(base)
            is_table = (v is not None and v.is_table and not comps) or (inline and kw in ("VALUE", "CORRESPONDING", "FILTER"))
            if kw == "VALUE" and src.first("For") is not None:
                self.value_for(base, src, s, inline)
                continue
            if kw == "VALUE" and is_table:
                self.value_rows(base, src, s)
                continue
            if kw == "VALUE" and not is_table:
                body = src.child("ValueBody")
                self.clear_var(base)
                for fa in (body.direct("FieldAssignment") if body else []):
                    sub = fa.first("FieldSub")
                    self._assign(base, [sub.text().upper()] if sub else [], self.tr.source(fa.child("Source")), s)
                continue
            if kw == "CORRESPONDING" or (is_table and src.first("FieldChain") is not None and kw is None):
                srcname = self._source_name(src.first("Source") if kw == "CORRESPONDING" else src)
                sv = self.var_info(srcname) if srcname else None
                if sv is not None and sv.is_table:
                    self.copy_table(base, srcname, s, inline)
                    continue
                if sv is not None and sv.type.kind == "struct":
                    self._copy_struct(srcname, base, by_name=True, s=s)
                    continue
            # whole structure copy
            if not comps and v is not None and v.type.kind == "struct":
                srcname = self._source_name(src)
                sv = self.var_info(srcname) if srcname else None
                if sv is not None and sv.type.kind == "struct":
                    self._copy_struct(srcname, base, by_name=True, s=s)
                    continue
            value = self.tr.source(src)
            if value.kind == "itab" and not comps and (v is None or v.is_table):
                rel = next((r for r in self.relations if r.id == value.sql), None)
                if rel is not None:
                    if v is None:
                        from .symbols import TypeDef, Var

                        row = TypeDef(base, "struct", comps=[c.comp or Comp(c.name, c.expr.ddic) for c in rel.columns])
                        self.frame.symbols.declare(Var(base, "internal_table", TypeDef(base, "table", row=row), self.frame.scope, s, inline=True))
                    self.set_itab(base, ItabState(rel=rel))
                    continue
            if inline and v is None:
                self.frame.symbols.declare(_inline_var(base, value, self.frame.scope))
            self._assign(base, comps, value, s)

    def _copy_struct(self, src: str, dst: str, by_name: bool, s: Statement) -> None:
        cells = self.struct_cells(src)
        dst_comps = self.struct_comps(dst) or list(cells)
        for c in dst_comps:
            if c in cells:
                self._assign(dst, [c], cells[c], s)

    def exec_move_corresponding(self, s: Statement) -> None:
        srcname = self._source_name(s.node.child("Source"))
        tnode = s.node.child("SimpleTarget") or s.node.child("Target")
        base, comps, _ = self._target_parts(tnode)
        if srcname is None or base is None:
            self.unsupported(s, "MOVE-CORRESPONDING form")
            return
        sv = self.var_info(srcname)
        if sv is not None and sv.is_table and not sv.header_line:
            self.copy_table(base, srcname, s, False)
            return
        self._copy_struct(srcname, base, True, s)

    def exec_clear(self, s: Statement) -> None:
        targets = s.node.direct("Target") or s.node.find_all("Target")
        for tnode in targets:
            base, comps, _ = self._target_parts(tnode)
            if base:
                if s.type == "Refresh":
                    self.set_itab(base, ItabState(rel=self.empty_relation(base)))
                else:
                    self.clear_var(base, comps or None)

    def exec_assign(self, s: Statement) -> None:
        # ASSIGN src TO <fs>: alias the field symbol to the source variable
        src = s.node.first("AssignSource")
        fs = s.node.first("FSTarget")
        if src is None or fs is None:
            self.unsupported(s, "ASSIGN form")
            return
        if src.first("Dynamic") is not None or "COMPONENT" in src.keywords():
            self.unsupported(s, "dynamic ASSIGN")
            return
        name = self._source_name(src)
        fsn = fs.text().upper()
        if name:
            self.frame.aliases[fsn] = name

    # ------------------------------------------------------------------ string statements
    def exec_concatenate(self, s: Statement) -> None:
        kws = s.node.keywords()
        if "LINES" in kws:
            self.unsupported(s, "CONCATENATE LINES OF")
            return
        srcs = [self.tr.source(c) for c in s.node.direct("SimpleSource3")]
        sep = None
        if "SEPARATED" in kws:
            sep = srcs.pop()
        base, comps, _ = self._target_parts(s.node.child("Target"))
        if not srcs or base is None:
            self.unsupported(s, "CONCATENATE form")
            return
        parts = [f"RTRIM({e.sql})" if "RESPECTING" not in kws else e.sql for e in srcs]
        joiner = f" || {sep.sql} || " if sep is not None else " || "
        if sep is not None and sep.sql == "''":
            joiner = " || ' ' || "
        self._assign(base, comps, srcs[0].combine(*srcs[1:], sql=joiner.join(parts), ddic="CHAR"), s)

    def exec_condense(self, s: Statement) -> None:
        base, comps, _ = self._target_parts(s.node.child("Target"))
        if base is None:
            return
        cur = self.tr.field_chain(s.node.child("Target")) if False else self.field(base, comps, s.node)
        fn = "REPLACE({}, ' ', '')" if "NO-GAPS" in s.node.keywords() else "REGEXP_REPLACE(TRIM({}), ' +', ' ')"
        self._assign(base, comps, cur.combine(sql=fn.format(cur.sql)), s)

    def exec_translate(self, s: Statement) -> None:
        base, comps, _ = self._target_parts(s.node.child("Target"))
        kws = s.node.keywords()
        if base is None or ("UPPER" not in kws and "LOWER" not in kws):
            self.unsupported(s, "TRANSLATE ... USING")
            return
        cur = self.field(base, comps, s.node)
        fn = "UPPER" if "UPPER" in kws else "LOWER"
        self._assign(base, comps, cur.combine(sql=f"{fn}({cur.sql})"), s)

    def exec_shift(self, s: Statement) -> None:
        base, comps, _ = self._target_parts(s.node.child("Target"))
        kws = s.node.keywords()
        if base is None or "DELETING" not in kws:
            self.unsupported(s, "SHIFT form")
            return
        what = s.node.first("Source")
        ch = self.tr.source(what) if what is not None else lit("' '")
        cur = self.field(base, comps, s.node)
        fn = "LTRIM" if "LEADING" in kws else "RTRIM"
        self._assign(base, comps, cur.combine(ch, sql=f"{fn}({cur.sql}, {ch.sql})"), s)

    # ------------------------------------------------------------------ SELECT
    def exec_select(self, s: Statement) -> None:
        spec = SelectBuilder(self).build(s)
        for n in spec.notes:
            self.finding("warning", "SELECT_NOTE", n, s)
        if spec.target is None:
            self.unsupported(s, "SELECT target not recognized")
            return
        if self.loop is not None:
            if spec.single or spec.target_kind != "table":
                self.lookup_select_single(spec, s)
            else:
                self.loop.unsupported.append(f"line {s.row}: SELECT INTO TABLE inside a LOOP (nested read per row)")
            self.subrc_after(None)
            return
        if spec.single or spec.target_kind in ("struct", "list"):
            self.scalar_select(spec, s)
            return
        rel = self.relation_from_select(spec, s)
        if spec.inline and self.var_info(spec.target) is None:
            from .symbols import TypeDef, Var

            row = TypeDef(spec.target, "struct", comps=[c.comp or Comp(c.name, c.expr.ddic) for c in rel.columns])
            self.frame.symbols.declare(Var(spec.target.upper(), "internal_table", TypeDef(spec.target, "table", row=row, table_kind="STANDARD"),
                                           self.frame.scope, s, inline=True))
        self.store_table_result(spec.target, rel, s, appending=spec.appending, sort=spec.order_by)
        self.subrc = self.exists_subrc(self.current_rel(spec.target))

    def relation_from_select(self, spec, s: Statement, var: str | None = None) -> Relation:
        target = (var or spec.target or "?").upper()
        rel = self.new_relation(target, "fae_read" if spec.fae_var else "db_read", [s], label="SELECT")
        rel.sources = list(spec.sources)
        rel.where = list(spec.where)
        rel.distinct = spec.distinct or bool(spec.fae_var)
        rel.having = list(spec.having)
        rel.limit = spec.up_to
        if spec.group_by:
            rel.group_by = [g.sql for g in spec.group_by]
        if spec.fae_var:
            drv = self.current_rel(spec.fae_var)
            cond = " AND ".join(c.sql for c in spec.fae_conds) or "TRUE"
            e = SqlExpr(f"EXISTS (SELECT 1 FROM {drv.id} {spec.fae_alias} WHERE {cond})", kind="expr", ddic="BOOL")
            e.rels = {drv.id}
            for c in spec.fae_conds:
                e.deps |= {d for d in c.deps if d[0] != spec.fae_alias}
                e.uses_params = e.uses_params or c.uses_params
            rel.where.append(e)
            guarded = any(c.itab_guard == spec.fae_var for c in self.conds)
            if not guarded:
                self.finding("warning", "FAE_NO_EMPTY_CHECK",
                             f"FOR ALL ENTRIES IN {spec.fae_var} without an IS NOT INITIAL check: SAP reads ALL rows when "
                             f"{spec.fae_var} is empty, the SQL returns none.", s)
        guard, problems = self.guard(exclude_itab=spec.fae_var)
        guard = [g for g in guard if not (g.itab_guard and g.itab_guard == spec.fae_var)]
        rel.where += guard
        if problems:
            rel.status = "partial"
            rel.notes.append("condition around SELECT not translatable: " + "; ".join(problems)[:200])
        # columns mapped onto the target structure
        rel.columns = self._map_select_columns(spec, target)
        if any(e.unknown for e in rel.all_exprs()):
            rel.status = "needs_llm"
            rel.notes += [u for e in rel.all_exprs() for u in e.unknown][:5]
        rel.uses_params = any(e.uses_params for e in rel.all_exprs())
        rel.unique_keys = self._select_unique_keys(spec, rel)
        if spec.order_by:
            rel.order_hint = list(spec.order_by)
        rel.abap = s.text
        return rel

    def _map_select_columns(self, spec, target: str) -> list[OutCol]:
        items = list(spec.items)
        comps = [] if spec.inline else self.row_comps(target)
        if not comps:
            return [OutCol(n, e, Comp(n, e.ddic)) for n, e in items]
        out: list[OutCol] = []
        by_name = {n: e for n, e in items}
        positional = not spec.corresponding and not spec.star
        for i, c in enumerate(comps):
            if positional:
                e = items[i][1] if i < len(items) else None
            else:
                e = by_name.get(c.name)
            if e is None:
                e = lit(initial_for(c.ddic_type, c.length), c.ddic_type)
            out.append(OutCol(c.name, self.convert(e, c), c))
        if positional and len(items) > len(comps):
            self.finding("warning", "SELECT_MORE_FIELDS", f"SELECT returns more fields than {target} has components.", spec.stmt)
        return out

    def _select_unique_keys(self, spec, rel: Relation) -> list[list[str]]:
        if not spec.sources:
            return []
        keys: list[list[str]] = []
        if rel.distinct:
            keys.append(rel.column_names)
        if spec.group_by:
            keys.append([n for n, e in spec.items if e.sql in {g.sql for g in spec.group_by}])
            return keys
        base = spec.sources[0]
        info = self.kb.table(base.original or "") if base.original else None
        if info is None:
            return keys
        fixed = set()
        for w in spec.where:
            m = re.fullmatch(rf"{re.escape(base.alias)}\.(\w+) = (?:'[^']*'|prm\.\w+|-?\d+)", w.sql.strip())
            if m:
                fixed.add(m.group(1).upper())
        pk = [k for k in info.key if k not in ("MANDT", "CLIENT", "RCLNT") and k not in fixed]
        # n:1 joins keep the base key
        for j in spec.sources[1:]:
            jinfo = self.kb.table(j.original or "")
            if jinfo is None:
                return keys
            jpk = {k for k in jinfo.key if k not in ("MANDT", "CLIENT", "RCLNT")}
            covered = {m.group(1).upper() for c in j.on for m in [re.match(rf"{re.escape(j.alias)}\.(\w+) =", c.sql.strip())] if m}
            if not jpk <= covered:
                return keys
        name_of = {}
        for oc in rel.columns:
            m = re.fullmatch(rf"(?:COALESCE\()?{re.escape(base.alias)}\.(\w+)(?:, .*\))?", oc.expr.sql)
            if m:
                name_of[m.group(1).upper()] = oc.name
        if pk and all(k in name_of for k in pk):
            keys.append([name_of[k] for k in pk])
        return keys

    def store_table_result(self, var: str, rel: Relation, s: Statement, appending: bool = False,
                           sort: list | None = None, guard_handled: bool = True) -> None:
        st = self.itab(var)
        prev = st.rel
        guard, _ = self.guard()
        prev_nonempty = prev is not None and not prev.is_empty
        if appending and prev_nonempty:
            rel.union_with.append((prev.id, None))
            rel.unique_keys = []
        elif prev_nonempty and guard:
            g = _and(guard)
            rel.union_with.append((prev.id, g.combine(sql=f"NOT ({g.sql})", ddic="BOOL")))
        v = self.var_info(var)
        if v is not None and v.type.unique_key and v.type.table_kind in ("SORTED", "HASHED"):
            rel.unique_keys.append([k.upper() for k in v.type.unique_key])
        new = ItabState(rel=rel, sort=list(sort or []))
        if v is not None and v.type.table_kind == "SORTED" and v.type.unique_key:
            new.sort = [(k.upper(), False) for k in v.type.unique_key]
        self.set_itab(var, new)

    def scalar_select(self, spec, s: Statement) -> None:
        """SELECT SINGLE / INTO structure at top level -> scalar subqueries per target field."""
        from_sql = " ".join([spec.sources[0].ref_sql()] + [
            f"{'LEFT' if x.join == 'left' else 'INNER'} JOIN {x.ref_sql()} ON {' AND '.join(c.sql for c in x.on) or 'TRUE'}"
            for x in spec.sources[1:]]) if spec.sources else "(SELECT 1)"
        where = " AND ".join(w.sql for w in spec.where)
        names = spec.targets_list or [spec.target]
        items = spec.items
        uses_params = spec.uses_params
        if spec.target_kind == "list":
            pairs = list(zip(names, [e for _, e in items]))
        else:
            base = spec.target
            comps = self.struct_comps(base)
            if comps and (spec.corresponding or spec.star):
                pairs = [(f"{base}-{n}", e) for n, e in items if n in comps]
            elif comps and len(items) > 1:
                pairs = [(f"{base}-{c}", e) for c, (_, e) in zip(comps, items)]
            else:
                pairs = [(base, items[0][1])] if items else []
        for tname, e in pairs:
            sql = f"(SELECT {e.sql} FROM {from_sql}{' WHERE ' + where if where else ''} LIMIT 1)"
            val = SqlExpr(sql, kind="expr", ddic=e.ddic, uses_params=uses_params)
            parts = tname.split("-")
            self._assign(parts[0], parts[1:], val, s)
        exists = f"EXISTS (SELECT 1 FROM {from_sql}{' WHERE ' + where if where else ''})"
        self.subrc = SqlExpr(exists, kind="subrc_bool", ddic="BOOL", uses_params=uses_params)

    def lookup_select_single(self, spec, s: Statement) -> None:
        """SELECT SINGLE inside a LOOP -> LEFT JOIN lookup on the DB table."""
        loop = self.loop
        if len(spec.sources) != 1:
            loop.unsupported.append(f"line {s.row}: SELECT SINGLE with joins inside a LOOP")
            return
        src = spec.sources[0]
        alias = self.new_alias("lk")
        on = []
        for w in spec.where:
            on.append(w.combine(sql=re.sub(rf"\b{re.escape(src.alias)}\.", f"{alias}.", w.sql)))
        lk = Source(alias=alias, kind="db", name=src.name, join="left", on=on, original=src.original, lookup=True,
                    extra_filter=list(src.extra_filter))
        info = self.kb.table(src.original or "")
        covered = {m.group(1).upper() for c in on for m in [re.match(rf"{alias}\.(\w+) =", c.sql.strip())] if m}
        pk = [k for k in (info.key if info else []) if k not in ("MANDT", "CLIENT", "RCLNT")]
        if not pk or not set(pk) <= covered:
            lk.dedup_keys = sorted(covered) or ["1"]
            lk.dedup_keys = [k.lower() for k in lk.dedup_keys]
            self.finding("info", "SELECT_SINGLE_NOT_UNIQUE",
                         f"SELECT SINGLE on {src.original} does not specify the full key; the first match is taken.", s)
        loop.sources.append(lk)
        names = spec.targets_list or [spec.target]
        items = spec.items
        if spec.target_kind == "list":
            pairs = list(zip(names, items))
        else:
            comps = self.struct_comps(spec.target)
            if comps and len(items) >= 1 and (spec.corresponding or spec.star or len(items) > 1):
                pairs = [(f"{spec.target}-{n}", (n, e)) for n, e in items if (n in comps or not spec.corresponding)]
            else:
                pairs = [(spec.target, items[0])] if items else []
        for tname, (_, e) in pairs:
            colname = e.sql.split(".")[-1].rstrip(")").split(",")[0]
            m = re.search(rf"\b{re.escape(src.alias)}\.(\w+)", e.sql)
            col = m.group(1) if m else colname
            parts = tname.split("-")
            comp = self.comp_of(parts[0], parts[1:])
            val = self.col(alias, col, e.ddic or (comp.ddic_type if comp else None), True, comp.length if comp else None)
            self._assign(parts[0], parts[1:], val, s)
        first_key = next(iter(sorted(covered)), None) or (pk[0] if pk else "1")
        self.subrc_after(SqlExpr(f"{alias}.{first_key.lower()}", {(alias, first_key.upper())}, "subrc", found_alias=alias))

    def subrc_after(self, e: SqlExpr | None) -> None:
        self.subrc = e

    def read_index(self, s: Statement, itab_name: str) -> bool:
        """READ TABLE itab INDEX n (top level): the n-th row in the table's sort order;
        on a select-option, the n-th selection value (s_x-low)."""
        node = s.node
        toks = [t.upper() for t in tokenize(s.text)]
        idx_tok = toks[toks.index("INDEX") + 1] if "INDEX" in toks and toks.index("INDEX") + 1 < len(toks) else ""
        if not idx_tok.isdigit() or self.loop is not None:
            return False
        n = int(idx_tok)
        target = node.child("ReadTableTarget")
        tf = None
        if target is not None:
            inline = target.first("InlineData") or target.first("InlineFS")
            tf = (inline or target).first("TargetField") or (inline or target).first("TargetFieldSymbol") or (inline or target).first("FieldSymbol")
        tgt = tf.text().upper() if tf is not None else None
        pname = self.locate(itab_name)[0]
        p = self.sym.params.get(pname)
        if p is not None and p.kind == "select_option":
            self.params_used.add(pname)
            arr = f"prm.{pname.lower()}"
            low = SqlExpr(f"COALESCE(GET({arr}, {n - 1})::VARCHAR, '')", kind="expr", ddic=p.comp.ddic_type, uses_params=True)
            if tgt:
                from .symbols import TypeDef, Var

                if self.var_info(tgt) is None:
                    v = self.var_info(pname)
                    self.frame.symbols.declare(Var(tgt, "structure", v.type.row if v and v.type.row else TypeDef(tgt, "struct"), self.frame.scope, s, inline=True))
                self.set_cell(tgt, ["SIGN"], lit("'I'"))
                self.set_cell(tgt, ["OPTION"], lit("'EQ'"))
                self.set_cell(tgt, ["LOW"], low)
                self.set_cell(tgt, ["HIGH"], lit("''", p.comp.ddic_type))
            self.subrc = SqlExpr(f"ARRAY_SIZE({arr}) >= {n}", kind="subrc_bool", ddic="BOOL", uses_params=True)
            return True
        st = self.itab(itab_name)
        rel = self.current_rel(itab_name)
        order = ", ".join(f"r.{c.lower()}{' DESC' if d else ''}" for c, d in st.sort if rel.col(c) is not None)
        if not order:
            self.finding("info", "READ_INDEX_ORDER", f"READ TABLE {itab_name} INDEX {n}: the table has no known sort order; "
                         "the row picked depends on the database order.", s)
        tail = f"{' ORDER BY ' + order if order else ''} LIMIT 1{f' OFFSET {n - 1}' if n > 1 else ''}"
        if tgt:
            if self.var_info(tgt) is None:
                from .symbols import TypeDef, Var

                self.frame.symbols.declare(Var(tgt, "structure", TypeDef(rel.var, "struct", comps=[c.comp or Comp(c.name) for c in rel.columns]),
                                               self.frame.scope, s, inline=True))
            for c in rel.columns:
                e = SqlExpr(f"(SELECT r.{c.name.lower()} FROM {rel.id} r{tail})", kind="expr", ddic=c.comp.ddic_type if c.comp else None)
                e.rels = {rel.id}
                self.set_cell(tgt, [c.name], e)
        ex = SqlExpr(f"(SELECT COUNT(*) FROM {rel.id}) >= {n}", kind="subrc_bool", ddic="BOOL")
        ex.rels = {rel.id}
        self.subrc = ex
        return True

    # ------------------------------------------------------------------ READ TABLE
    def exec_read(self, s: Statement) -> None:
        node = s.node
        src_node = node.child("SimpleSource2") or node.first("Source")
        itab_name = self._source_name(src_node)
        kws = node.keywords()
        if itab_name is None:
            self.unsupported(s, "READ TABLE source")
            return
        if "INDEX" in kws and self.read_index(s, itab_name):
            return
        if "INDEX" in kws:
            self.unsupported(s, "READ TABLE ... INDEX")
            return
        rel = self.current_rel(itab_name)
        keys: list[tuple[str, SqlExpr]] = []
        for cc in node.find_all("ComponentCompareSimple"):
            ch = cc.children
            i = 0
            while i < len(ch):
                c = ch[i]
                if c.type in ("ComponentChainSimple", "ComponentChain"):
                    comp = c.text().upper()
                    val = self.tr.source(ch[i + 2]) if i + 2 < len(ch) else unknown(cc.text())
                    keys.append((comp, val))
                    i += 3
                    continue
                i += 1
        if not keys and "WITH" in kws:
            self.unsupported(s, "READ TABLE key form")
            return
        target = node.child("ReadTableTarget")
        tgt_name = None
        assigning = False
        if target is not None:
            tf = target.first("TargetFieldSymbol") or target.first("TargetField") or target.first("InlineFS")
            inline = target.first("InlineData") or target.first("InlineFS")
            if inline is not None:
                tf = inline.first("TargetField") or inline.first("TargetFieldSymbol") or inline.first("FieldSymbol") or tf
            tgt_name = tf.text().upper() if tf is not None else None
            assigning = "ASSIGNING" in target.keywords()
            if inline is not None and tgt_name and self.var_info(tgt_name) is None:
                from .symbols import TypeDef, Var

                td = TypeDef(rel.var, "struct", comps=[c.comp or Comp(c.name) for c in rel.columns])
                self.frame.symbols.declare(Var(tgt_name, "field_symbol" if assigning else "structure", td, self.frame.scope))
        if self.loop is None:
            # top-level READ: single row -> scalar subqueries
            where = " AND ".join(f"r.{k.lower()} = {v.sql}" for k, v in keys) or "TRUE"
            if tgt_name:
                for c in rel.columns:
                    e = SqlExpr(f"(SELECT r.{c.name.lower()} FROM {rel.id} r WHERE {where} LIMIT 1)", kind="expr",
                                ddic=c.comp.ddic_type if c.comp else None)
                    e.rels = {rel.id}
                    self.set_cell(tgt_name, [c.name], e)
            ex = SqlExpr(f"(SELECT 1 FROM {rel.id} r WHERE {where} LIMIT 1)", kind="subrc", found_alias="__top__")
            self.subrc = ex
            return
        alias = self.new_alias("lk")
        on = []
        for k, v in keys:
            c = rel.col(k)
            ref = self.col(alias, k, c.comp.ddic_type if c is not None and c.comp else None)
            a, b = self.tr._null_safe(ref, v, "=")
            on.append(a.combine(b, sql=f"{ref.sql} = {b.sql}", ddic="BOOL"))
        lk = Source(alias=alias, kind="rel", name=rel.id, join="left", on=on, lookup=True)
        key_cols = [k for k, _ in keys]
        if not rel.is_unique_on(key_cols):
            lk.dedup_keys = [k.lower() for k in key_cols]
            st = self.itab(itab_name)
            lk.dedup_order = [(c.lower(), d) for c, d in st.sort if c not in key_cols]
            self.finding("info", "READ_FIRST_MATCH",
                         f"READ TABLE {itab_name} by ({', '.join(key_cols)}) may match several rows; the first match is taken"
                         + (" (order of the last SORT)." if lk.dedup_order else " (order not determined)."), s)
        self.loop.sources.append(lk)
        if tgt_name:
            self.bind_row(tgt_name, alias, rel, True)
        first = key_cols[0] if key_cols else (rel.column_names[0] if rel.columns else "1")
        self.subrc = SqlExpr(f"{alias}.{first.lower()}", {(alias, first.upper())}, "subrc", found_alias=alias)

    # ------------------------------------------------------------------ APPEND / INSERT / COLLECT
    def _row_source_values(self, s: Statement, src_node: Node | None, target: str) -> dict[str, SqlExpr] | None:
        if src_node is None:
            return None
        first = src_node.children[0] if src_node.children else None
        if first is not None and first.is_token and first.value.upper() == "VALUE":
            body = src_node.child("ValueBody")
            vals: dict[str, SqlExpr] = {}
            for fa in (body.direct("FieldAssignment") if body else []):
                sub = fa.first("FieldSub")
                if sub is not None:
                    vals[sub.text().upper()] = self.tr.source(fa.child("Source"))
            return vals
        name = self._source_name(src_node)
        if name is None:
            return None
        return self.struct_cells(name)

    def exec_append(self, s: Statement) -> None:
        kws = s.node.keywords()
        tnode = s.node.child("Target") or s.node.first("Target")
        target, _, _ = self._target_parts(tnode)
        if "LINES" in kws:
            src = self._source_name(s.node.child("Source") or s.node.first("Source"))
            if target is None or src is None:
                self.unsupported(s, "APPEND LINES form")
                return
            self.union_tables(target, src, s)
            return
        src_node = s.node.child("Source") or s.node.child("SimpleSource4")
        if src_node is None and target is not None:
            # APPEND itab (header line) / APPEND INITIAL LINE
            if "INITIAL" in kws:
                self.unsupported(s, "APPEND INITIAL LINE")
                return
            vals = self.struct_cells(target)
        else:
            vals = self._row_source_values(s, src_node, target or "")
        if target is None or vals is None:
            self.unsupported(s, "APPEND form")
            return
        self.emit_row(target, "append", vals, s)

    def exec_insert(self, s: Statement) -> None:
        kws = s.node.keywords()
        tnode = s.node.child("Target") or s.node.first("Target")
        target, _, _ = self._target_parts(tnode)
        if "LINES" in kws:
            src = self._source_name(s.node.first("Source"))
            if target and src:
                self.union_tables(target, src, s)
            return
        if "INDEX" in kws:
            self.unsupported(s, "INSERT ... INDEX")
            return
        vals = self._row_source_values(s, s.node.child("Source") or s.node.first("SimpleSource4"), target or "")
        if target is None or vals is None:
            self.unsupported(s, "INSERT form")
            return
        self.emit_row(target, "insert", vals, s)

    def exec_collect(self, s: Statement) -> None:
        srcname = self._source_name(s.node.child("Source"))
        target, _, _ = self._target_parts(s.node.child("Target"))
        if srcname is None or target is None:
            self.unsupported(s, "COLLECT form")
            return
        self.emit_row(target, "collect", self.struct_cells(srcname), s)

    def emit_row(self, target: str, kind: str, vals: dict[str, SqlExpr], s: Statement) -> None:
        if self.loop is not None:
            conds = list(self.conds[self.loop.cond_depth:])
            self.loop.emits.append(Emit(target.upper(), kind, dict(vals), conds, [_copy_source(x) for x in self.loop.sources], s))
            return
        # top level: literal rows (field catalogs, range tables, small value lists)
        if any(v.deps or v.unknown for v in vals.values()):
            self.unsupported(s, "APPEND of a computed row outside a LOOP")
            return
        st = self.itab(target)
        if st.rel is not None and not st.rel.is_empty and st.literal_rows is None:
            self.unsupported(s, "APPEND of a literal row to a filled table")
            return
        rows = list(st.literal_rows or [])
        rows.append(dict(vals))
        self.set_itab(target, ItabState(rel=None, sort=[], literal_rows=rows))

    def union_tables(self, target: str, src: str, s: Statement) -> None:
        srel = self.current_rel(src)
        st = self.itab(target)
        if self.loop is not None:
            self.loop.unsupported.append(f"line {s.row}: APPEND/INSERT LINES OF inside a LOOP")
            return
        rel = self.new_relation(target.upper(), "union", [s], label="APPEND LINES OF")
        comps = self.row_comps(target) or [c.comp or Comp(c.name) for c in srel.columns]
        rel.columns = [OutCol(c.name, self.col("u", c.name, c.ddic_type) if srel.col(c.name) else lit(initial_for(c.ddic_type, c.length)), c) for c in comps]
        rel.sources = [Source("u", "rel", srel.id)]
        guard, _ = self.guard()
        rel.where = guard
        if st.rel is not None and not st.rel.is_empty or st.literal_rows:
            prev = self.current_rel(target)
            rel.union_with.append((prev.id, None))
        self.set_itab(target, ItabState(rel=rel))

    # ------------------------------------------------------------------ MODIFY / DELETE / SORT
    def exec_modify(self, s: Statement) -> None:
        kws = s.node.keywords()
        tnode = s.node.child("Target") or s.node.first("Target")
        target, _, _ = self._target_parts(tnode)
        src = self._source_name(s.node.child("Source") or s.node.first("Source"))
        transporting = [c.text().upper() for c in s.node.find_all("ComponentChainSimple")] if "TRANSPORTING" in kws else None
        if target is None or src is None:
            self.unsupported(s, "MODIFY form")
            return
        vals = self.struct_cells(src)
        if transporting:
            vals = {k: v for k, v in vals.items() if k in transporting}
        n, _ = self.locate(target)
        if self.loop is not None and self.loop.var == self.itab_key(target) and "WHERE" not in kws:
            self.loop.modified = True
            self.loop.updates.append((list(self.conds[self.loop.cond_depth:]), vals))
            return
        if self.loop is None and "WHERE" in kws:
            rel = self.current_rel(target)
            new = self.new_relation(n, "modify", [s], label="MODIFY ... WHERE")
            self._row = ("t", rel)
            try:
                cond = self.tr.cond(s.node.child("ComponentCond"))
            finally:
                self._row = None
            guard, _ = self.guard()
            g = _and(guard + [cond])
            new.sources = [Source("t", "rel", rel.id)]
            new.columns = []
            for c in rel.columns:
                base = self.col("t", c.name, c.comp.ddic_type if c.comp else None)
                if c.name in vals:
                    new.columns.append(OutCol(c.name, base.combine(g, vals[c.name], sql=f"CASE WHEN {g.sql} THEN {vals[c.name].sql} ELSE {base.sql} END"), c.comp))
                else:
                    new.columns.append(OutCol(c.name, base, c.comp))
            new.unique_keys = list(rel.unique_keys)
            new.uses_params = any(e.uses_params for e in new.all_exprs())
            self.set_itab(target, ItabState(rel=new, sort=list(self.itab(target).sort)))
            return
        self.unsupported(s, "MODIFY form (by key/index)")

    def _modify_itab_ambiguous(self, s: Statement, tab: str) -> bool:
        """`MODIFY itab FROM wa` without TABLE is parsed as a database write when the parser cannot see
        that `itab` is an internal table. Handle it as the internal-table MODIFY it is."""
        v = self.var_info(tab)
        if v is None or v.type.kind != "table":
            return False
        toks = [x.upper().rstrip(".") for x in s.tokens()]
        if "FROM" not in toks or toks.index("FROM") + 1 >= len(toks):
            self.unsupported(s, "MODIFY form")
            return True
        src = toks[toks.index("FROM") + 1]
        try:
            vals = self.struct_cells(src)
            if "TRANSPORTING" in toks:
                names = toks[toks.index("TRANSPORTING") + 1:]
                names = names[: names.index("WHERE")] if "WHERE" in names else names
                vals = {k: v for k, v in vals.items() if k in names}
            if self.loop is not None and self.loop.var == self.itab_key(tab) and "WHERE" not in toks:
                self.loop.modified = True
                self.loop.updates.append((list(self.conds[self.loop.cond_depth:]), vals))
                return True
        except Exception as exc:  # noqa: BLE001
            self.unsupported(s, f"interpreter error: {exc}")
            return True
        self.unsupported(s, "MODIFY form (by key/index)")
        return True

    def exec_delete(self, s: Statement) -> None:
        kws = s.node.keywords()
        tnode = s.node.child("Target") or s.node.first("Target")
        target, _, _ = self._target_parts(tnode)
        if target is None:
            self.unsupported(s, "DELETE form")
            return
        n, _ = self.locate(target)
        if "ADJACENT" in kws:
            self.dedup(target, s)
            return
        if "WHERE" in kws:
            if self.loop is not None:
                self.loop.unsupported.append(f"line {s.row}: DELETE ... WHERE inside a LOOP")
                return
            rel = self.current_rel(target)
            new = self.new_relation(n, "filter", [s], label="DELETE ... WHERE")
            self._row = ("t", rel)
            try:
                cond = self.tr.cond(s.node.child("ComponentCond"))
            finally:
                self._row = None
            guard, problems = self.guard()
            g = _and(guard + [cond])
            new.sources = [Source("t", "rel", rel.id)]
            new.columns = [OutCol(c.name, self.col("t", c.name, c.comp.ddic_type if c.comp else None), c.comp) for c in rel.columns]
            new.where = [g.combine(sql=f"NOT COALESCE(({g.sql}), FALSE)", ddic="BOOL")]
            new.unique_keys = list(rel.unique_keys)
            new.order_hint = list(rel.order_hint)
            new.uses_params = g.uses_params
            if cond.unknown or problems:
                new.status = "needs_llm"
                new.notes += cond.unknown + problems
            new.abap = s.text
            self.set_itab(target, ItabState(rel=new, sort=list(self.itab(target).sort)))
            return
        if self.loop is not None and self.loop.var == self.itab_key(target) and len(kws) <= 1:
            self.loop.modified = True
            self.loop.deletes.append(list(self.conds[self.loop.cond_depth:]))
            return
        self.unsupported(s, "DELETE form (by index/key/FROM)")

    def dedup(self, target: str, s: Statement) -> None:
        n, _ = self.locate(target)
        rel = self.current_rel(target)
        st = self.itab(target)
        comparing = [c.text().upper() for c in s.node.find_all("SimpleFieldChain2")] or [c.text().upper() for c in s.node.find_all("ComponentChainSimple")]
        all_fields = "ALL" in s.node.keywords() or not comparing
        new = self.new_relation(n, "dedup", [s], label="DELETE ADJACENT DUPLICATES")
        new.sources = [Source("t", "rel", rel.id)]
        new.columns = [OutCol(c.name, self.col("t", c.name, c.comp.ddic_type if c.comp else None), c.comp) for c in rel.columns]
        guard, _ = self.guard()
        if all_fields and not guard:
            new.distinct = True
            new.unique_keys = [rel.column_names]
        else:
            have = set(rel.column_names)
            part = [c for c in (comparing if not all_fields else rel.column_names) if c in have] or rel.column_names
            sort_cols = [c for c, _ in st.sort]
            if sort_cols[: len(part)] and set(sort_cols[: len(part)]) != set(part):
                self.finding("warning", "DEDUP_NOT_SORTED",
                             f"DELETE ADJACENT DUPLICATES on {n} compares ({', '.join(part)}) but the table is sorted by "
                             f"({', '.join(sort_cols)}); only adjacent duplicates are removed in ABAP.", s)
            elif not sort_cols:
                self.finding("warning", "DEDUP_NOT_SORTED", f"DELETE ADJACENT DUPLICATES on {n} without a preceding SORT.", s)
            order = ", ".join(f"t.{c.lower()} {'DESC' if d else 'ASC'}" for c, d in st.sort if c not in part and c in have) or "1"
            rn = f"ROW_NUMBER() OVER (PARTITION BY {', '.join('t.' + p.lower() for p in part)} ORDER BY {order}) = 1"
            if guard:
                g = _and(guard)
                new.qualify = f"NOT ({g.sql}) OR {rn}"
                new.uses_params = g.uses_params
            else:
                new.qualify = rn
            new.unique_keys = [part]
        new.order_hint = list(st.sort)
        new.abap = s.text
        self.set_itab(target, ItabState(rel=new, sort=list(st.sort)))

    def exec_sort(self, s: Statement) -> None:
        tnode = s.node.child("Target") or s.node.first("Target")
        target, _, _ = self._target_parts(tnode)
        if target is None:
            return
        kws_all = [c.value.upper() if c.is_token else c.type for c in s.node.children]
        order: list[tuple[str, bool]] = []
        default_desc = False
        seen_by = False
        for item in s.node.children:
            if item.is_token:
                v = item.value.upper()
                if v == "BY":
                    seen_by = True
                elif v == "DESCENDING":
                    if order and seen_by:
                        order[-1] = (order[-1][0], True)
                    else:
                        default_desc = True
                elif v == "ASCENDING" and order:
                    order[-1] = (order[-1][0], False)
                continue
            if item.type in ("ComponentChain", "ComponentChainSimple", "SourceFieldSymbol", "Dynamic"):
                if item.type == "Dynamic":
                    self.finding("warning", "DYNAMIC_SORT", "SORT BY a dynamic component; order not determined.", s)
                    continue
                order.append((item.text().upper(), default_desc))
        if not order:
            v = self.var_info(target)
            keys = [k.upper() for k in v.type.unique_key] if v and v.type.unique_key else [c.name for c in self.row_comps(target) if c.is_charlike]
            order = [(k, default_desc) for k in keys]
        st = self.itab(target)
        if self.loop is not None:
            self.loop.unsupported.append(f"line {s.row}: SORT inside a LOOP")
            return
        st.sort = order
        _ = kws_all

    # ------------------------------------------------------------------ PERFORM / CALL FUNCTION / methods
    def exec_perform(self, s: Statement) -> None:
        toks = tokenize(s.text)
        if len(toks) < 2:
            return
        name = toks[1].upper()
        if name.startswith("("):
            self.finding("warning", "DYNAMIC_PERFORM", "Dynamic PERFORM; target not followed.", s)
            return
        up = [t.upper() for t in toks]
        if "PROGRAM" in up or "IF" in up and "FOUND" in up and name not in self.structure.routines:
            self.finding("warning", "EXTERNAL_PERFORM", f"PERFORM {name} in another program; not followed.", s)
            return
        self.calls_seen.append(("perform", name, s))
        r = self.structure.routines.get(name)
        if r is None:
            self.finding("warning", "FORM_NOT_FOUND", f"FORM {name} not found in the uploaded source.", s)
            return
        actual: dict[str, list[str]] = {}
        cur = None
        for t in toks[2:]:
            u = t.upper()
            if u in ("USING", "CHANGING", "TABLES"):
                cur = u
                actual.setdefault(u, [])
                continue
            if cur:
                actual[cur].append(t)
        frame = Frame(name=name, scope=name, symbols=self.sym, kind="routine")
        for section in ("TABLES", "USING", "CHANGING"):
            formals = r.params.get(section, [])
            acts = actual.get(section, [])
            for f, a in zip(formals, acts):
                if a.startswith(("'", "`")) or re.fullmatch(r"-?\d+", a):
                    frame.values[f.upper()] = self.tr.string_literal(a)
                elif "-" in a and not a.startswith("<"):
                    base, *comps = a.upper().split("-")
                    frame.values[f.upper()] = self.field(base, comps, s.node)
                else:
                    n, _ = self.locate(a)
                    frame.aliases[f.upper()] = n
        self.run_routine(r, frame)

    def run_routine(self, r, frame: Frame) -> None:
        if r.name in self.call_stack:
            self.finding("warning", "RECURSION", f"Recursive call of {r.name} not followed.", r.header)
            return
        self.call_stack.append(r.name)
        self.frames.append(frame)
        saved_subrc = self.subrc
        try:
            self.exec_items(r.items)
        finally:
            self.frames.pop()
            self.call_stack.pop()
            self.subrc = saved_subrc if self.loop is not None else self.subrc

    def _fm_params(self, s: Statement) -> dict[str, dict[str, Node]]:
        out: dict[str, dict[str, Node]] = {"EXPORTING": {}, "IMPORTING": {}, "CHANGING": {}, "TABLES": {}}
        fp = s.node.child("FunctionParameters") or s.node.first("FunctionParameters")
        if fp is None:
            return out
        section = None
        for c in fp.children:
            if c.is_token:
                section = c.value.upper()
                continue
            if c.type == "FunctionExporting":
                for p in c.find_all("FunctionExportingParameter"):
                    nm = p.first("ParameterName")
                    if nm is not None:
                        out["EXPORTING"][nm.text().upper()] = p.child("Source")
            elif c.type == "ParameterListT" and section in out:
                for p in c.find_all("ParameterT"):
                    nm = p.first("ParameterName")
                    if nm is not None:
                        out[section][nm.text().upper()] = p.child("Target") or p.first("Target")
        return out

    def exec_call_function(self, s: Statement) -> None:
        fn_node = s.node.child("FunctionName")
        const = fn_node.first("Constant") if fn_node is not None else None
        if const is None:
            self.finding("warning", "DYNAMIC_FM", "CALL FUNCTION with a dynamic name; not followed.", s)
            return
        name = const.text().strip("'").upper()
        self.calls_seen.append(("function", name, s))
        params = self._fm_params(s)
        info = self.kb.fm(name)
        source = self.fm_sources.get(name) or self.kb.fm_source(name)
        kind = info.kind if info else ("custom" if source else "unknown")
        if source and kind in ("custom", "opaque", "unknown"):
            kind = "custom"
        self.fm_kinds[name] = kind
        self.subrc = None
        if kind == "output_sink":
            tparam = (info.table_param or "T_OUTTAB").upper()
            tnode = params["TABLES"].get(tparam) or params["CHANGING"].get(tparam)
            var = self._target_parts(tnode)[0] if tnode is not None else None
            fc_node = params["EXPORTING"].get((info.fieldcat_param or "IT_FIELDCAT").upper())
            fc_var = self._source_name(fc_node) if fc_node is not None else None
            struct_node = params["EXPORTING"].get("I_STRUCTURE_NAME")
            self.record_output("alv_grid" if "GRID" in name else "alv_list", var, fc_var, s,
                               struct_node.text().strip("'") if struct_node is not None else None)
            return
        if kind in ("ui", "side_effect", "output_sink"):
            self.success_subrc()
        if kind in ("ui",):
            if name == "REUSE_ALV_FIELDCATALOG_MERGE":
                tnode = params["CHANGING"].get("CT_FIELDCAT") or params["TABLES"].get("CT_FIELDCAT")
                fc = self._target_parts(tnode)[0] if tnode is not None else None
                if fc:
                    self.set_itab(fc, ItabState(literal_rows=[{"__MERGE__": lit("'X'")}]))
            return
        if kind == "side_effect":
            self.finding("info", "FM_SIDE_EFFECT", f"{name} has side effects (file, mail, lock, commit); not part of the SQL.", s)
            return
        if kind == "expression" and info and info.sql:
            exprs = {k: self.tr.source(v) for k, v in params["EXPORTING"].items()}
            out_param = (info.output or "").upper()
            tnode = params["IMPORTING"].get(out_param) or params["CHANGING"].get(out_param)
            if tnode is None:
                return
            base, comps, _ = self._target_parts(tnode)
            comp = self.comp_of(base, comps) if base else None
            sql = info.sql
            missing = []
            for pname in re.findall(r"\{([A-Za-z_0-9]+)\}", sql):
                if pname == "len":
                    sql = sql.replace("{len}", str(comp.length if comp and comp.length else 10))
                elif pname.upper() in exprs:
                    sql = sql.replace("{" + pname + "}", exprs[pname.upper()].sql)
                else:
                    missing.append(pname)
            if missing:
                val = unknown(s.text, f"{name}: parameters {missing} not supplied")
            else:
                first = next(iter(exprs.values()), lit("NULL"))
                val = first.combine(*list(exprs.values())[1:], sql=sql)
                val.ddic = None
            if base:
                self._assign(base, comps, val, s)
            return
        if kind == "custom" and source:
            self.inline_fm(name, source, params, s)
            self.success_subrc()
            return
        # lookup / opaque / unknown: targets become unresolved
        reason = (info.note if info and info.note else None) or (f"{name}: {kind}" if info else f"{name}: function module source not provided")
        self.finding("warning" if kind != "lookup" else "info", "FM_UNRESOLVED", reason, s,
                     "Upload the function module source or add it to fm_catalog.yaml in a knowledge pack." if kind == "unknown" else (info.sql if info else None))
        for sect in ("IMPORTING", "CHANGING"):
            for pname, tnode in params[sect].items():
                base, comps, _ = self._target_parts(tnode)
                if base:
                    self.set_cell(base, comps, unknown(f"{name}-{pname}", reason))
                    if self.loop is not None:
                        self.loop.unsupported.append(f"line {s.row}: {reason}")
        for pname, tnode in params["TABLES"].items():
            base, _, _ = self._target_parts(tnode)
            if base and self.loop is None:
                self.unsupported(s, f"{name} fills table {base}")

    def inline_fm(self, name: str, source: str, params: dict[str, dict[str, Node]], s: Statement) -> None:
        prog = self.fm_program(name, source)
        if prog is None:
            self.finding("warning", "FM_PARSE", f"Could not parse source of {name}.", s)
            return
        structure, symbols, interface = prog
        r = structure.routines.get(name)
        if r is None:
            self.finding("warning", "FM_PARSE", f"FUNCTION {name} not found in its source.", s)
            return
        frame = Frame(name=name, scope=name, symbols=symbols, kind="fm", param_types=dict(interface))
        for pname, node in params["EXPORTING"].items():
            e = self.tr.source(node)
            frame.values[pname] = self.convert(e, interface.get(pname))
        for pname, node in params["CHANGING"].items():
            base, comps, _ = self._target_parts(node)
            if base:
                frame.values[pname] = self.field(base, comps, node)
        if params["TABLES"]:
            self.finding("warning", "FM_TABLES", f"{name} uses TABLES parameters; table results are not inlined.", s)
        saved_origin = self._origin
        self._origin = name
        self.run_routine(r, frame)
        self._origin = saved_origin
        for sect in ("IMPORTING", "CHANGING"):
            for pname, tnode in params[sect].items():
                base, comps, _ = self._target_parts(tnode)
                val = frame.values.get(pname)
                if base and val is not None:
                    self._assign(base, comps, val, s)
                elif base:
                    self._assign(base, comps, lit(initial_for(interface.get(pname).ddic_type if interface.get(pname) else None)), s)

    def _method_key(self, chain: Node, calls: list[Node]) -> tuple[str, str]:
        meth = calls[-1].first("MethodName").text().upper()
        cls = chain.child("ClassName")
        fieldn = chain.child("FieldChain") or chain.child("Field")
        if cls is not None:
            return f"{cls.text().upper()}=>{meth}", meth
        if fieldn is not None or len(calls) > 1:
            obj = (fieldn.text() if fieldn is not None else chain.children[0].text()).upper()
            v = self.var_info(obj.split("->")[0])
            cname = v.type.name.upper() if v is not None and v.type.kind == "ref" else obj
            if obj in ("ME", "SUPER") or obj.startswith("ME->"):
                cname = self.current_class() or obj
            return f"{cname}->{meth}", meth
        return f"{self.current_class() or 'ME'}->{meth}", meth  # bare call inside a method: own class

    def _method_args(self, call: Node) -> tuple[dict[str, dict[str, Node]], Node | None]:
        """Caller-side actual parameters by section (+ a single positional argument)."""
        out: dict[str, dict[str, Node]] = {"EXPORTING": {}, "IMPORTING": {}, "CHANGING": {}, "RECEIVING": {}}
        root = call.first("MethodCallParam") or call.first("MethodParameters") or call
        positional = None
        section = "EXPORTING"

        def walk(n: Node, top: bool) -> None:
            nonlocal section, positional
            for c in n.children:
                if c.is_token:
                    if c.value.upper() in out:
                        section = c.value.upper()
                    continue
                if c.type in ("ParameterS", "ParameterT"):
                    nm = c.first("ParameterName")
                    if nm is not None:
                        out[section][nm.text().upper()] = c.child("Target") or c.child("Source") or c
                    continue
                if c.type == "Source" and top and positional is None:
                    positional = c
                    continue
                if c.type in ("MethodParameters", "ParameterListS", "ParameterListT", "MethodCallParam"):
                    walk(c, top and c.type == "MethodCallParam")

        walk(root, True)
        return out, positional

    def call_local_method(self, local, call: Node, s: Statement | None):
        """Run a method implementation with its actual parameters bound. Returns (frame, returning-param name)."""
        args, positional = self._method_args(call)
        frame = Frame(name=local.name, scope=local.name, symbols=self.sym, kind="routine")
        imp = local.params.get("IMPORTING", [])
        if positional is not None and imp and imp[0] not in args["EXPORTING"]:
            args["EXPORTING"][imp[0]] = positional
        for formal, node in args["EXPORTING"].items():
            name = self._source_name(node) if node.type == "Source" and node.first("FieldChain") is not None and len(node.children) == 1 else None
            v = self.var_info(name) if name and "-" not in name else None
            if v is not None and (v.is_table or v.type.kind == "struct"):
                frame.aliases[formal] = self.locate(name)[0]
            else:
                frame.values[formal] = self.tr.source(node) if node.type == "Source" else self.field(*self._target_parts(node)[:2], node)
        for sect in ("IMPORTING", "CHANGING"):  # caller targets <- method EXPORTING / CHANGING
            for formal, node in args[sect].items():
                base, comps, inline = self._target_parts(node)
                if base and not comps:
                    if inline and self.var_info(base) is None:
                        fv = self.sym.var(formal, local.name)
                        if fv is not None:
                            from .symbols import Var

                            self.frame.symbols.declare(Var(base, fv.kind, fv.type, self.frame.scope, s, inline=True))
                    frame.aliases[formal] = self.locate(base)[0]
        self.run_routine(local, frame)
        ret = (local.params.get("RETURNING") or [None])[0]
        for _, node in args["RECEIVING"].items():
            base, comps, _ = self._target_parts(node)
            if base and ret:
                self._store_result(base, comps, local, frame, ret, s)
        return frame, ret

    def method_result(self, local, frame: Frame, ret: str) -> SqlExpr:
        v = self.sym.var(ret, local.name)
        if v is not None and v.is_table:
            st = self.itabs.get(f"{local.name}:{ret}")
            rel = st.rel if st is not None and st.rel is not None else self.empty_relation(ret)
            e = SqlExpr(rel.id, kind="itab", var=ret)
            e.rels = {rel.id}
            return e
        val = frame.values.get(ret)
        if val is not None:
            return val
        c = v.type.elem if v is not None and v.type.kind == "elem" else None
        return lit(initial_for(c.ddic_type if c else None), c.ddic_type if c else None)

    def _store_result(self, base: str, comps: list[str], local, frame: Frame, ret: str, s: Statement | None) -> None:
        res = self.method_result(local, frame, ret)
        if res.kind == "itab":
            rel = next((r for r in self.relations if r.id == res.sql), None)
            if rel is not None:
                self.set_itab(base, ItabState(rel=rel))
            return
        if s is not None:
            self._assign(base, comps, res, s)
        else:
            self.set_cell(base, comps, res)

    def functional_call(self, node: Node) -> SqlExpr | None:
        """`x = obj->meth( a )` / `IF is_ok( b ).`: run a local method, return its RETURNING value."""
        calls = node.find_all_outer("MethodCall") if node.type != "MethodCall" else [node]
        if not calls or calls[-1].first("MethodName") is None:
            return None
        key, meth = self._method_key(node, calls)
        local = self.structure.routines.get(key.replace("->", "=>")) or self.find_method(key, meth)
        if local is None or local.name in self.call_stack or not local.params.get("RETURNING"):
            return None
        self.calls_seen.append(("method", local.name, None))
        frame, ret = self.call_local_method(local, calls[-1], None)
        return self.method_result(local, frame, ret) if ret else None

    def exec_method_call(self, s: Statement) -> None:
        chain = s.node.child("MethodCallChain") or s.node.first("MethodCallChain")
        if chain is None:
            self.unsupported(s, "method call form")
            return
        calls = chain.find_all_outer("MethodCall")
        if not calls:
            return
        key, meth = self._method_key(chain, calls)
        self.calls_seen.append(("method", key, s))
        info = self.kb.method(key) or self.kb.method(key.replace("->", "=>"))
        params: dict[str, dict[str, Node]] = {"EXPORTING": {}, "IMPORTING": {}, "CHANGING": {}}
        mp = calls[-1].first("MethodParameters")
        section = "EXPORTING"
        if mp is not None:
            for c in mp.children:
                if c.is_token:
                    section = c.value.upper()
                    continue
                for p in c.find_all("ParameterT") + c.find_all("ParameterS"):
                    nm = p.first("ParameterName")
                    if nm is not None:
                        params.setdefault(section, {})[nm.text().upper()] = p.child("Target") or p.child("Source") or p
        if info is not None and info.kind == "output_sink":
            tparam = (info.table_param or "T_TABLE").upper()
            node = params.get("CHANGING", {}).get(tparam) or params.get("EXPORTING", {}).get(tparam)
            var = self._source_name(node) if node is not None else None
            fc_node = params.get("CHANGING", {}).get((info.fieldcat_param or "").upper())
            fc = self._source_name(fc_node) if fc_node is not None else None
            self.record_output("salv" if "SALV" in key else "alv_grid", var, fc, s)
            return
        if info is not None:
            self.success_subrc()
            return
        local = self.structure.routines.get(key.replace("->", "=>")) or self.find_method(key, meth)
        if local is not None:
            self.call_local_method(local, calls[-1], s)
            self.success_subrc()
            return
        if self.loop is not None:
            self.loop.unsupported.append(f"line {s.row}: method call {key}")

    def current_class(self) -> str | None:
        for name in reversed(self.call_stack):
            if "=>" in name:
                return name.split("=>")[0]
        return None

    def find_method(self, key: str, meth: str):
        """Resolve a method whose class is not known statically (chained calls, untyped references,
        interface methods): unique implementation by name, else the one in the caller's class."""
        hits = [r for n, r in self.structure.routines.items() if r.kind == "method" and (n.endswith("=>" + meth) or n.endswith("~" + meth))]
        if len(hits) == 1:
            return hits[0]
        own = self.current_class()
        for r in hits:
            if own and r.name.startswith(own + "=>"):
                return r
        return None

    def record_output(self, kind: str, var: str | None, fieldcat: str | None, s: Statement, structure_name: str | None = None) -> None:
        if var is None:
            self.finding("warning", "OUTPUT_TABLE", "Output call found but its table parameter could not be resolved.", s)
            return
        rel = self.current_rel(var)
        st = self.itab(var)
        fc_rows = self.itab(fieldcat).literal_rows if fieldcat else None
        self.outputs.append(OutputRec(kind, var.upper(), rel, list(st.sort), fc_rows, s, structure_name))

    def exec_check(self, s: Statement) -> str:
        cond_node = s.node.child("Cond")
        if cond_node is None:
            return "none"
        for part in conjuncts(cond_node):
            self.conds.append(self.tr.cond(part))
        return f"push:{len(conjuncts(cond_node))}"

    # ------------------------------------------------------------------ table constructors
    def value_for(self, target: str, src: Node, s: Statement, inline: bool) -> None:
        body = src.child("ValueBody")
        fors = body.direct("For") if body else []
        line = body.child("ValueBodyLine") if body else None
        if len(fors) != 1 or line is None:
            self.unsupported(s, "VALUE #( FOR ... ) form")
            return
        ld = fors[0].child("InlineLoopDefinition")
        row_var = ld.first("TargetField").text().upper() if ld is not None and ld.first("TargetField") else None
        itab_name = self._source_name(ld.child("Source")) if ld is not None else None
        if row_var is None or itab_name is None:
            self.unsupported(s, "VALUE #( FOR ... ) form")
            return
        srel = self.current_rel(itab_name)
        alias = self.new_alias("v")
        rel = self.new_relation(target.upper(), "value_for", [s], label="VALUE #( FOR ... )")
        rel.sources = [Source(alias, "rel", srel.id)]
        self.bind_row(row_var, alias, srel, False)
        self._row = (alias, srel)
        try:
            where_node = fors[0].child("ComponentCond") or fors[0].child("Cond")
            if where_node is not None:
                rel.where.append(self.tr.cond(where_node))
        finally:
            self._row = None
        type_node = src.first("TypeNameOrInfer")
        tname = type_node.text().upper() if type_node is not None else "#"
        td = self.frame.symbols.type(tname, self.frame.scope) if tname != "#" else None
        v = self.var_info(target)
        comps = (td.columns() if td is not None else []) or (v.type.columns() if v else [])
        vals = {}
        for fa in line.direct("FieldAssignment"):
            sub = fa.first("FieldSub")
            if sub is not None:
                vals[sub.text().upper()] = self.tr.source(fa.child("Source"))
        names = [c.name for c in comps] or list(vals)
        for nme in names:
            c = next((x for x in comps if x.name == nme), None)
            e = vals.get(nme) or lit(initial_for(c.ddic_type if c else None, c.length if c else None), c.ddic_type if c else None)
            rel.columns.append(OutCol(nme, self.convert(e, c), c or Comp(nme, e.ddic)))
        guard, _ = self.guard()
        rel.where += guard
        rel.uses_params = any(e.uses_params for e in rel.all_exprs())
        if any(e.unknown for e in rel.all_exprs()):
            rel.status = "needs_llm"
            rel.notes += [u for e in rel.all_exprs() for u in e.unknown][:5]
        rel.unique_keys = [k for k in srel.unique_keys if all(rel.col(x) is not None for x in k)]
        rel.abap = s.text
        if inline and v is None:
            from .symbols import TypeDef, Var

            row = TypeDef(tname, "struct", comps=[c.comp for c in rel.columns if c.comp])
            self.frame.symbols.declare(Var(target.upper(), "internal_table", TypeDef(tname, "table", row=row, table_kind="STANDARD"), self.frame.scope, s, inline=True))
        self.set_itab(target, ItabState(rel=rel))

    def value_rows(self, target: str, src: Node, s: Statement) -> None:
        body = src.child("ValueBody")
        rows = []
        for line in (body.direct("ValueBodyLine") if body else []):
            vals = {}
            for fa in line.direct("FieldAssignment"):
                sub = fa.first("FieldSub")
                if sub is not None:
                    vals[sub.text().upper()] = self.tr.source(fa.child("Source"))
            rows.append(vals)
        if any(v.deps or v.unknown for r in rows for v in r.values()):
            self.unsupported(s, "VALUE table with computed rows")
            return
        self.set_itab(target, ItabState(literal_rows=rows))

    def copy_table(self, target: str, src: str, s: Statement, inline: bool) -> None:
        srel = self.current_rel(src)
        v = self.var_info(target)
        comps = v.type.columns() if v is not None else []
        if not comps:
            if inline and v is None:
                from .symbols import TypeDef, Var

                sv = self.var_info(src)
                if sv is not None:
                    self.frame.symbols.declare(Var(target.upper(), "internal_table", sv.type, self.frame.scope, s, inline=True))
            self.set_itab(target, ItabState(rel=srel, sort=list(self.itab(src).sort)))
            return
        rel = self.new_relation(target.upper(), "copy", [s], label="table copy")
        rel.sources = [Source("t", "rel", srel.id)]
        for c in comps:
            sc = srel.col(c.name)
            e = self.col("t", c.name, c.ddic_type) if sc is not None else lit(initial_for(c.ddic_type, c.length), c.ddic_type)
            rel.columns.append(OutCol(c.name, self.convert(e, c), c))
        rel.unique_keys = [k for k in srel.unique_keys if all(rel.col(x) is not None for x in k)]
        self.set_itab(target, ItabState(rel=rel, sort=list(self.itab(src).sort)))


def _and(conds: list[SqlExpr]) -> SqlExpr:
    if not conds:
        return lit("TRUE", "BOOL")
    if len(conds) == 1:
        return conds[0]
    return conds[0].combine(*conds[1:], sql=" AND ".join(f"({c.sql})" if " OR " in c.sql.upper() else c.sql for c in conds), ddic="BOOL")


def _copy_source(x: Source) -> Source:
    return Source(x.alias, x.kind, x.name, x.join, list(x.on), x.original, None if x.dedup_keys is None else list(x.dedup_keys),
                  list(x.dedup_order), list(x.extra_filter), x.lookup)


def _inline_var(name: str, value: SqlExpr, scope: str):
    from .symbols import TypeDef, Var

    return Var(name.upper(), "scalar", TypeDef(name.upper(), "elem", elem=Comp(name.upper(), value.ddic)), scope, inline=True)
