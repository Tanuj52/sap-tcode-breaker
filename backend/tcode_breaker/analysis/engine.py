"""Symbolic ABAP interpreter: control flow, loops and value merging.

The interpreter walks the report's events in execution order (inlining PERFORMs and
custom function modules) and turns every change of an internal table into a Relation.
"""

from __future__ import annotations

import re

from ..parser.ast import Statement
from .blocks import Control, build_structure
from .engine_base import Emit, InterpreterBase, ItabState, LoopCtx
from .engine_stmts import StatementMixin, _and
from .expr import SqlExpr, initial_for, is_numeric, lit, unknown
from .opensql import SelectBuilder, conjuncts
from .relations import OutCol, Relation, Source, placeholder_sql
from .symbols import Comp, Symbols, tokenize

_FM_PARAM = re.compile(r'^\s*\*"\s+(?:VALUE\()?([A-Z0-9_]+)\)?\s+(?:TYPE|LIKE)\s+(?:REF\s+TO\s+)?(\S+)', re.IGNORECASE)
TERMINAL = {"Return", "Exit", "Continue", "Leave", "Stop", "Check"}


class Interpreter(StatementMixin, InterpreterBase):
    def run(self) -> None:
        for r in self.structure.run_order():
            self.call_stack.append(r.name)
            try:
                self.exec_items(r.items)
            finally:
                self.call_stack.pop()

    # ------------------------------------------------------------------ item lists
    def exec_items(self, items) -> None:
        pushed = 0
        for it in items:
            if isinstance(it, Control):
                pushed += self.exec_control(it)
                continue
            self._mark(it)
            res = self.exec_stmt(it)
            if res and res.startswith("push:"):
                pushed += int(res.split(":")[1])
            elif res == "terminal" and it.type in ("Return", "Exit", "Leave", "Stop") and self.loop is None:
                # unconditional RETURN: the rest of this routine does not run
                break
            elif res == "terminal" and it.type == "Continue" and self.loop is not None:
                break
        if pushed:
            del self.conds[len(self.conds) - pushed:]

    def _mark(self, s: Statement) -> None:
        if s.origin and s.origin != self.program:
            self.executed_fm.setdefault(s.origin, set()).add(s.index)
        else:
            self.executed.add(s.index)

    # ------------------------------------------------------------------ controls
    def exec_control(self, ctl: Control) -> int:
        self._mark(ctl.header)
        if self.loop is not None:
            self.loop.stmts.append(ctl.header)
        t = ctl.type
        if t == "If":
            return self.exec_branches(ctl, [self._cond_of(b.header) if b.header.type != "Else" else None for b in ctl.branches])
        if t in ("Case", "CaseType"):
            return self.exec_case(ctl)
        if t == "Loop":
            self.exec_loop(ctl)
            return 0
        if t == "SelectLoop":
            self.exec_select_loop(ctl)
            return 0
        if t == "Try":
            self.exec_items(ctl.branches[0].items)
            if len(ctl.branches) > 1:
                self.finding("info", "TRY_CATCH", "CATCH/CLEANUP branches are not translated (error paths).", ctl.header)
            return 0
        if t in ("At", "AtFirst", "AtLast", "OnChange"):
            if self.loop is not None:
                self.loop.unsupported.append(f"line {ctl.header.row}: control break {ctl.header.text[:60]} (needs window functions)")
            else:
                self.finding("warning", "UNSUPPORTED", f"{ctl.header.text[:60]} outside a LOOP", ctl.header)
            return 0
        # DO / WHILE / PROVIDE / ...
        if self.loop is not None:
            self.loop.unsupported.append(f"line {ctl.header.row}: {t} block inside a LOOP")
        else:
            for st in _flat(ctl):
                if st.type in ("Append", "InsertInternal", "Collect", "ModifyInternal", "DeleteInternal", "Select", "Move"):
                    self.unsupported(st, f"statement inside a {t} block")
        return 0

    def _cond_of(self, header: Statement) -> list[SqlExpr]:
        node = header.node.child("Cond")
        return [self.tr.cond(p) for p in conjuncts(node)] if node is not None else [unknown(header.text)]

    def exec_case(self, ctl: Control) -> int:
        subj_node = ctl.header.node.child("Source")
        subject = self.tr.source(subj_node)
        conds: list[list[SqlExpr] | None] = []
        for b in ctl.branches:
            h = b.header
            if h is None or h.type == "WhenOthers":
                conds.append(None)
                continue
            vals = [self.tr.source(n) for n in h.node.direct("Source")] + [self.tr.source(o.child("Source")) for o in h.node.direct("Or")]
            if not vals:
                conds.append([unknown(h.text)])
                continue
            parts = []
            for v in vals:
                a, bb = self.tr._null_safe(subject, v, "=")
                parts.append(a.combine(bb, sql=f"{a.sql} = {bb.sql}", ddic="BOOL"))
            c = parts[0].combine(*parts[1:], sql=" OR ".join(p.sql for p in parts), ddic="BOOL") if len(parts) > 1 else parts[0]
            conds.append([c])
        return self.exec_branches(ctl, conds)

    def exec_branches(self, ctl: Control, branch_conds: list[list[SqlExpr] | None]) -> int:
        """IF / CASE: run every branch on a forked state, then merge values into CASE expressions."""
        base_cells = self._snapshot_cells()
        base_itabs = {k: v.copy() for k, v in self.itabs.items()}
        results = []
        prior: list[SqlExpr] = []
        remainder: list[SqlExpr] = []
        has_else = any(c is None for c in branch_conds)
        for b, conds in zip(ctl.branches, branch_conds):
            self._restore_cells(base_cells)
            self.itabs = {k: v.copy() for k, v in base_itabs.items()}
            if b.header is not ctl.header and b.header is not None:
                self._mark(b.header)
            eff = [p.combine(sql=f"NOT COALESCE(({p.sql}), FALSE)", ddic="BOOL") for p in prior] + (conds or [])
            depth = len(self.conds)
            self.conds.extend(eff)
            saved_subrc = self.subrc
            self.exec_items(b.items)
            del self.conds[depth:]
            branch_cond = _and(conds) if conds else None
            results.append((branch_cond, self._snapshot_cells(), {k: v.copy() for k, v in self.itabs.items()}))
            if _is_terminal(b.items):
                if not self._ignorable_terminal(conds, b.items):
                    remainder.append(_and(eff).combine(sql=f"NOT COALESCE(({_and(eff).sql}), FALSE)", ddic="BOOL") if eff else lit("FALSE", "BOOL"))
                else:
                    self.finding("info", "EARLY_EXIT_IGNORED",
                                 f"Early exit when '{ctl.header.text[:70]}' (no data / error path) is not part of the SQL.", ctl.header)
            self.subrc = saved_subrc
            if conds:
                prior.append(_and(conds))
        if not has_else:
            results.append((None, base_cells, base_itabs))
        self._merge(results, base_cells, base_itabs, ctl)
        self.conds.extend(remainder)
        return len(remainder)

    def _ignorable_terminal(self, conds, items) -> bool:
        if conds is None:
            return False
        text = " ".join(c.sql.upper() for c in conds) + " ".join(u.upper() for c in conds for u in c.unknown)
        if "SY-SUBRC" in text or "NOT EXISTS (SELECT 1 FROM" in text:
            return True
        return all(isinstance(i, Statement) and i.type in ("Message", "Return", "Exit", "Leave", "Stop", "Write", "Continue") for i in items) and any(c.unknown for c in conds)

    # ------------------------------------------------------------------ fork / merge
    def _snapshot_cells(self) -> list[dict[str, SqlExpr]]:
        return [dict(self.globals)] + [dict(f.values) for f in self.frames[1:]]

    def _restore_cells(self, snap: list[dict[str, SqlExpr]]) -> None:
        self.globals.clear()
        self.globals.update(snap[0])
        for f, vals in zip(self.frames[1:], snap[1:]):
            f.values.clear()
            f.values.update(vals)

    def _merge(self, results, base_cells, base_itabs, ctl: Control) -> None:
        merged: list[dict[str, SqlExpr]] = []
        for idx in range(len(base_cells)):
            base = base_cells[idx]
            keys = set(base)
            for _, cells, _ in results:
                keys |= set(cells[idx]) if idx < len(cells) else set()
            out = dict(base)
            for k in keys:
                vals = [(c, cells[idx].get(k, base.get(k))) for c, cells, _ in results]
                if all(v is not None and base.get(k) is not None and v.sql == base[k].sql for _, v in vals):
                    continue
                default = base.get(k)
                if default is None:
                    default = self._initial_for_key(k)
                else_val = default
                arms = []
                for c, v in vals:
                    v = v if v is not None else default
                    if c is None:
                        else_val = v
                        break
                    arms.append((c, v))
                while arms and arms[-1][1].sql == else_val.sql:
                    arms.pop()
                if not arms:
                    out[k] = else_val
                    continue
                out[k] = _case(arms, else_val)
            merged.append(out)
        self._restore_cells(merged)
        # internal tables
        keys = set(base_itabs)
        for _, _, its in results:
            keys |= set(its)
        new_itabs = dict(base_itabs)
        for k in keys:
            states = [(c, its.get(k)) for c, _, its in results]
            base = base_itabs.get(k)
            changed = [(c, st) for c, st in states if st is not None and (base is None or st.rel is not base.rel or st.literal_rows != base.literal_rows or st.sort != base.sort)]
            if not changed:
                continue
            if len(changed) == 1:
                new_itabs[k] = changed[0][1]
                continue
            rel = self.new_relation(k.split(":")[-1], "union", [ctl.header], label="IF/CASE branches")
            first = changed[0][1].rel or self.current_rel(k.split(":")[-1])
            rel.columns = [OutCol(c.name, lit("NULL"), c.comp) for c in first.columns]
            parts = []
            prior = []
            for c, st in states:
                r = st.rel if st and st.rel is not None else (base.rel if base else None)
                if r is None:
                    continue
                conds = [p.combine(sql=f"NOT COALESCE(({p.sql}), FALSE)") for p in prior] + ([c] if c is not None else [])
                where = " AND ".join(x.sql for x in conds) or "TRUE"
                cols = ", ".join(f"b.{x.name.lower()}" for x in rel.columns) or "b.*"
                prm = " CROSS JOIN params prm" if "prm." in where else ""
                parts.append(f"SELECT {cols} FROM {r.id} b{prm} WHERE {where}")
                for x in conds:
                    rel.uses_params = rel.uses_params or x.uses_params
                if c is not None:
                    prior.append(c)
            rel.raw_sql = "\nUNION ALL\n".join(parts)
            rel.status = "partial" if any(c is not None and c.unknown for c, _ in states) else "deterministic"
            new_itabs[k] = ItabState(rel=rel)
        self.itabs = new_itabs

    def _initial_for_key(self, k: str) -> SqlExpr:
        parts = k.split("-")
        comp = self.comp_of(parts[0], parts[1:]) if parts else None
        return lit(initial_for(comp.ddic_type if comp else None, comp.length if comp else None), comp.ddic_type if comp else None)

    # ------------------------------------------------------------------ LOOP
    def exec_loop(self, ctl: Control) -> None:
        h = ctl.header
        node = h.node
        itab_name = self._source_name(node.child("LoopSource"))
        kws = node.keywords()
        if itab_name is None:
            self.unsupported(h, "LOOP source")
            return
        if "GROUP" in kws or "FROM" in kws or "TO" in kws and "INTO" not in kws:
            if "GROUP" in kws or "FROM" in kws:
                self._unsupported_loop(ctl, "LOOP ... GROUP BY / FROM / TO")
                return
        target = node.child("LoopTarget")
        row_var = None
        assigning = False
        if target is not None:
            tkws = target.keywords()
            assigning = "ASSIGNING" in tkws or "REFERENCE" in tkws
            inline = target.first("InlineData") or target.first("InlineFS")
            tf = target.first("TargetFieldSymbol") or target.first("TargetField") or target.first("FieldSymbol")
            if inline is not None:
                tf = inline.first("TargetFieldSymbol") or inline.first("TargetField") or inline.first("FieldSymbol") or tf
            row_var = tf.text().upper() if tf is not None else None
            if inline is not None and row_var and self.var_info(row_var) is None:
                from .symbols import TypeDef, Var

                rel0 = self.current_rel(itab_name)
                td = TypeDef(rel0.var, "struct", comps=[c.comp or Comp(c.name) for c in rel0.columns])
                self.frame.symbols.declare(Var(row_var, "field_symbol" if assigning else "structure", td, self.frame.scope))
        else:
            v = self.var_info(itab_name)
            if v is not None and v.header_line:
                row_var = itab_name  # LOOP AT itab. (header line)
        rel = self.current_rel(itab_name)
        if self.loop is not None:
            self._nested_loop(ctl, itab_name, rel, row_var)
            return
        items = ctl.branches[0].items
        grouped = self._control_break(ctl, itab_name, rel) if node.child("ComponentCond") is None else None
        if grouped is not None:
            rel, items = grouped
        alias = "src"
        loop = LoopCtx(var=self.itab_key(itab_name), rel=rel, alias=alias, row_var=self.locate(row_var)[0] if row_var else None,
                       assigning=assigning, sources=[Source(alias, "rel", rel.id)], where=[], cond_depth=len(self.conds), stmt=h)
        loop.ctl = ctl  # type: ignore[attr-defined]
        snapshot = self._snapshot_cells()
        self.loop = loop
        if row_var:
            self.bind_row(row_var, alias, rel, False)
        self._row = (alias, rel)
        try:
            wc = node.child("ComponentCond")
            if wc is not None:
                loop.where = [self.tr.cond(p) for p in conjuncts(wc)]
        finally:
            self._row = None
        try:
            self.exec_items(items)
        finally:
            self.loop = None
        self._materialize(loop, itab_name)
        # values computed inside the loop are per-row; after the loop they are the last row's values
        after = self._snapshot_cells()
        for i, (before, now) in enumerate(zip(snapshot, after)):
            for k, v in now.items():
                if k not in before or before[k].sql != v.sql:
                    now[k] = unknown(k, "value after LOOP (last iteration)")
        self._restore_cells(after)
        self.subrc = None

    def _control_break(self, ctl: Control, itab_name: str, rel: Relation):
        """LOOP AT itab INTO wa.  AT END OF f (or AT NEW f).  [SUM.]  ...  ENDAT.  ENDLOOP.
        The block runs once per group of the key (components up to and including f). With SUM, numeric
        components hold the group totals; components right of the key are '*' (character-like) or initial.
        Returns (group relation, block items) or None when the loop has another shape."""
        body = [it for it in ctl.branches[0].items if not (not isinstance(it, Control) and it.type in ("Comment", "Empty"))]
        if len(body) != 1 or not isinstance(body[0], Control) or body[0].type != "At":
            return None
        at = body[0]
        m = re.match(r"\s*AT\s+(END\s+OF|NEW)\s+([A-Za-z0-9_]+)\s*\.?\s*$", at.header.text, re.IGNORECASE)
        if not m:
            return None
        names = [c.name for c in rel.columns]
        key = m.group(2).upper()
        if key not in names:
            return None
        k = names.index(key)
        items = list(at.branches[0].items)
        has_sum = any(not isinstance(it, Control) and it.type == "Sum" for it in items)
        items = [it for it in items if isinstance(it, Control) or it.type != "Sum"]
        if not has_sum and any(c.comp is not None and c.comp.is_numeric for c in rel.columns[k + 1:]):
            # values right of the key would be "last row of the group": only safe when they are not numeric totals
            pass
        g = self.new_relation(rel.var, "collect", [at.header], label=f"AT {m.group(1).upper()} {key.lower()}" + (" + SUM" if has_sum else ""))
        g.sources = [Source("src", "rel", rel.id)]
        cols = []
        for i, c in enumerate(rel.columns):
            ddic = c.comp.ddic_type if c.comp else c.expr.ddic
            numeric = c.comp.is_numeric if c.comp else is_numeric(ddic)
            if i <= k:
                e = self.col("src", c.name, ddic)
            elif has_sum and numeric:
                e = SqlExpr(f"SUM(src.{c.name.lower()})", {("src", c.name)}, "expr", ddic)
            elif numeric:
                e = lit(initial_for(ddic), ddic)
            else:
                e = lit("'*'", ddic)
            cols.append(OutCol(c.name, e, c.comp))
        g.columns = cols
        g.group_by = [f"src.{c.name.lower()}" for c in rel.columns[: k + 1]]
        g.order_hint = list(self.itab(itab_name).sort)
        self.finding("info", "CONTROL_BREAK", f"{at.header.text.strip()} translated to one row per {', '.join(n.lower() for n in names[: k + 1])}"
                     + (" with SUM of the numeric fields." if has_sum else "."), at.header)
        return g, items

    def _nested_loop(self, ctl: Control, itab_name: str, rel: Relation, row_var: str | None) -> None:
        outer = self.loop
        alias = self.new_alias("n")
        src = Source(alias, "rel", rel.id, join="inner")
        node = ctl.header.node
        self._row = (alias, rel)
        try:
            wc = node.child("ComponentCond")
            src.on = [self.tr.cond(p) for p in conjuncts(wc)] if wc is not None else [lit("TRUE", "BOOL")]
        finally:
            self._row = None
        n_emits = len(outer.emits)
        outer.sources.append(src)
        if row_var:
            self.bind_row(row_var, alias, rel, False)
        acc = self._acc_begin(ctl)
        self.exec_items(ctl.branches[0].items)
        outer.sources.remove(src)
        if len(outer.emits) == n_emits:
            if not self._acc_end(acc, src, ctl):
                outer.unsupported.append(f"line {ctl.header.row}: nested LOOP without APPEND/COLLECT (accumulation)")
        else:
            self._acc_restore(acc)

    # ---- nested-loop accumulation:  LOOP AT inner WHERE k = outer-k.  total = total + inner-x.  ENDLOOP.
    #      -> total = total_before + (SELECT COALESCE(SUM(x), 0) FROM inner WHERE k = outer.k)
    def _acc_begin(self, ctl: Control) -> dict:
        keys: dict[str, tuple[str, list[str], SqlExpr]] = {}
        for st in _flat(ctl)[1:]:
            if st.type not in ("Move", "Add", "Subtract"):
                continue
            for t in st.node.find_all("Target"):
                base, comps, inline = self._target_parts(t)
                if not base or inline or "#OFFSET" in comps:
                    continue
                v = self.var_info(base)
                if v is None or v.is_table or (self.loop and self.loop.row_var == self.locate(base)[0]):
                    continue
                k, _ = self.key(base, comps)
                if k in keys:
                    continue
                comp = self.comp_of(base, comps)
                orig = self.get_cell(base, comps) or lit(initial_for(comp.ddic_type if comp else None), comp.ddic_type if comp else None)
                token = f"__ACC{len(self._acc_tokens)}__"
                self._acc_tokens.add(token)
                keys[k] = (base, comps, orig, token)
                ph = orig.combine(sql=token, kind="expr", ddic=orig.ddic)
                ph.unknown = []
                self.set_cell(base, comps, ph)
        return {"keys": {k: v[:3] for k, v in keys.items()}, "tokens": {k: v[3] for k, v in keys.items()}}

    def _acc_restore(self, acc: dict) -> None:
        for k, (base, comps, orig) in acc["keys"].items():
            cur = self.get_cell(base, comps)
            tok = acc["tokens"][k]
            if cur is not None and tok in cur.sql:
                self.set_cell(base, comps, cur.combine(sql=cur.sql.replace(tok, f"({orig.sql})"), ddic=cur.ddic) if cur.sql != tok else orig)

    def _acc_end(self, acc: dict, src: Source, ctl: Control) -> bool:
        ok = True
        changed = False
        for k, (base, comps, orig) in acc["keys"].items():
            tok = acc["tokens"][k]
            cur = self.get_cell(base, comps)
            if cur is None or cur.sql == tok:
                self.set_cell(base, comps, orig)
                continue
            changed = True
            if tok not in cur.sql or not _linear_in(cur.sql, tok):
                self.set_cell(base, comps, unknown(k, "value from a nested LOOP (last match)"))
                ok = False
                continue
            delta = cur.sql.replace(tok, "0")
            tcomp = self.comp_of(base, comps)
            ttype = (tcomp.ddic_type or "").upper() if tcomp else ""
            if ttype in ("INT1", "INT2", "INT4", "INT8"):
                delta = f"ROUND({delta}, 0)"  # ABAP rounds on every assignment to an integer
            elif ttype in ("DEC", "CURR", "QUAN") and tcomp.decimals is not None:
                delta = f"ROUND({delta}, {tcomp.decimals})"
            where = " AND ".join(e.sql for e in src.on) or "TRUE"
            agg = f"(SELECT COALESCE(SUM({delta}), 0) FROM {src.name} {src.alias} WHERE {where})"
            if orig.sql in ("''", "' '"):  # untyped work-area field: an accumulator starts at 0
                orig = lit("0", "DEC")
            total = orig.combine(cur, sql=agg if orig.sql in ("0", "0.0") else f"({orig.sql} + {agg})", kind="expr", ddic=cur.ddic or orig.ddic)
            total.deps = {d for d in total.deps if d[0] != src.alias}
            total.nullable = {a for a in total.nullable if a != src.alias}
            total.rels = set(total.rels) | {src.name}
            self.set_cell(base, comps, self.convert(total, self.comp_of(base, comps)))
        # any other value that picked up a placeholder: put the original value back
        for st_idx in range(len(self.frames)):
            store = self.store(st_idx)
            for kk, v in list(store.items()):
                for k2, tok in acc["tokens"].items():
                    if tok in v.sql and kk != k2:
                        store[kk] = v.combine(sql=v.sql.replace(tok, f"({acc['keys'][k2][2].sql})"), ddic=v.ddic)
        if changed and ok:
            self.finding("info", "NESTED_LOOP_SUM", f"Nested LOOP at line {ctl.header.row} accumulates values; translated to a correlated SUM.", ctl.header)
        return ok and changed

    def exec_select_loop(self, ctl: Control) -> None:
        h = ctl.header
        spec = SelectBuilder(self).build(h)
        if self.loop is not None:
            self.loop.unsupported.append(f"line {h.row}: SELECT ... ENDSELECT inside a LOOP")
            return
        var = f"SELECT_LOOP_{h.row}"
        rel = self.relation_from_select(spec, h, var=var)
        if spec.target_kind != "list" and spec.target:
            comps = self.struct_comps(spec.target)
            if comps:
                rel.columns = self._map_select_columns(spec, spec.target)
        loop = LoopCtx(var=var, rel=rel, alias="src", row_var=None, assigning=False, sources=[Source("src", "rel", rel.id)],
                       where=[], cond_depth=len(self.conds), stmt=h)
        snapshot = self._snapshot_cells()
        self.loop = loop
        if spec.target_kind == "list":
            for name, oc in zip(spec.targets_list, rel.columns):
                self.set_cell(name, [], self.col("src", oc.name, oc.expr.ddic))
        elif spec.target:
            self.bind_row(spec.target, "src", rel, False)
        try:
            self.exec_items(ctl.branches[0].items)
        finally:
            self.loop = None
        self._materialize(loop, var)
        after = self._snapshot_cells()
        for before, now in zip(snapshot, after):
            for k, v in now.items():
                if k not in before or before[k].sql != v.sql:
                    now[k] = unknown(k, "value after SELECT loop")
        self._restore_cells(after)

    def _unsupported_loop(self, ctl: Control, reason: str) -> None:
        for st in _flat(ctl):
            if st.type in ("Append", "InsertInternal", "Collect", "ModifyInternal"):
                self.unsupported(st, reason)
        self.finding("warning", "UNSUPPORTED", reason, ctl.header)

    # ------------------------------------------------------------------ loop materialization
    def _materialize(self, loop: LoopCtx, itab_name: str) -> None:
        notes = list(dict.fromkeys(loop.unsupported))
        status = "needs_llm" if notes else "deterministic"
        ctl = getattr(loop, "ctl", None)
        all_stmts = _flat(ctl) if ctl is not None else [loop.stmt] + loop.stmts
        abap = "\n".join(s.text for s in all_stmts)
        guard, problems = self.guard()
        if problems:
            notes.append("condition around LOOP not translatable: " + "; ".join(problems)[:200])
            status = "needs_llm"
        targets: dict[str, list[Emit]] = {}
        for e in loop.emits:
            targets.setdefault(e.target, []).append(e)
        for target, emits in targets.items():
            self._materialize_target(loop, target, emits, guard, status, notes, abap)
        if loop.modified:
            self._materialize_modify(loop, itab_name, guard, status, notes, abap)
        if not targets and not loop.modified and notes:
            written = []
            for st in all_stmts:
                if st.type in ("Append", "Collect", "InsertInternal", "ModifyInternal"):
                    tn = st.node.child("Target") or st.node.first("Target")
                    name = self._target_parts(tn)[0] if tn is not None else None
                    if name and name not in written and self.var_info(name) is not None and self.var_info(name).is_table:
                        written.append(name)
            for name in written:
                rel = self.new_relation(name.upper(), "llm", [loop.stmt], label="LOOP (needs LLM)")
                rel.columns = [OutCol(c.name, lit("NULL", c.ddic_type), c) for c in self.row_comps(name)]
                rel.sources = [Source(s.alias, s.kind, s.name, s.join, list(s.on), s.original, s.dedup_keys, s.dedup_order, s.extra_filter, s.lookup)
                               for s in loop.sources]
                rel.raw_sql = placeholder_sql(rel.columns, loop.rel, notes[0], keep_rows=False)
                rel.status = "needs_llm"
                rel.notes = notes
                rel.abap = abap
                self.set_itab(name, ItabState(rel=rel))
            if not written:
                self.finding("warning", "LOOP_UNSUPPORTED", f"LOOP AT {itab_name}: " + "; ".join(notes)[:300], loop.stmt)
            else:
                self.finding("warning", "NEEDS_LLM", f"LOOP AT {itab_name} needs the LLM translator: " + "; ".join(notes)[:200], loop.stmt)

    def _emit_select(self, loop: LoopCtx, e: Emit, comps: list[Comp], aggregate: bool) -> Relation:
        rel = self.new_relation(e.target, "collect" if aggregate else "loop_build", [loop.stmt, e.stmt],
                                label="COLLECT" if aggregate else ("APPEND in LOOP" if e.kind == "append" else "INSERT in LOOP"))
        sources = [Source(s.alias, s.kind, s.name, s.join, list(s.on), s.original, s.dedup_keys, s.dedup_order, s.extra_filter, s.lookup) for s in e.sources]
        conds = list(loop.where)
        for c in e.conds:
            if c.found_alias:
                src = next((s for s in sources if s.alias == c.found_alias), None)
                if src is not None and src.join == "left":
                    src.join = "inner"
                    continue
            conds.append(c)
        cols: list[OutCol] = []
        names = [c.name for c in comps] or list(e.values)
        for nme in names:
            c = next((x for x in comps if x.name == nme), None)
            v = e.values.get(nme)
            if v is None:
                v = lit(initial_for(c.ddic_type if c else None, c.length if c else None), c.ddic_type if c else None)
            v = self.convert(v, c)
            agg = "SUM" if aggregate and c is not None and c.is_numeric else None
            cols.append(OutCol(nme, v, c or Comp(nme, v.ddic), agg))
        used = {a for oc in cols for a, _ in oc.expr.deps} | {a for w in conds for a, _ in w.deps}
        for s in sources:
            used |= {a for oc in s.on for a, _ in oc.deps}
        # drop lookups that do not contribute (LEFT JOIN with no references)
        rel.sources = [s for s in sources if not (s.lookup and s.join == "left" and s.alias not in used)]
        rel.columns = cols
        rel.where = conds
        if aggregate:
            rel.group_all = True
            rel.unique_keys = [[c.name for c in cols if c.agg is None]]
        else:
            if all(s.join in ("from", "left") or s.lookup for s in rel.sources):
                for k in loop.rel.unique_keys:
                    mapped = []
                    for col in k:
                        hit = next((oc.name for oc in cols if oc.expr.sql == f"{loop.alias}.{col.lower()}"), None)
                        if hit is None:
                            break
                        mapped.append(hit)
                    else:
                        rel.unique_keys.append(mapped)
        rel.uses_params = any(x.uses_params for x in rel.all_exprs())
        for x in rel.all_exprs():
            if x.unknown:
                rel.status = "needs_llm"
                rel.notes += x.unknown[:3]
        return rel

    def _materialize_target(self, loop: LoopCtx, target: str, emits: list[Emit], guard, status, notes, abap) -> None:
        comps = self.row_comps(target)
        aggregate = any(e.kind == "collect" for e in emits)
        st = self.itab(target)
        prev = st.rel if st.rel is not None and not st.rel.is_empty else (self.current_rel(target) if st.literal_rows else None)
        parts = [self._emit_select(loop, e, comps, aggregate and len(emits) == 1 and prev is None) for e in emits]
        for p in parts:
            p.where += guard
            if notes:
                p.status = status
                p.notes = list(dict.fromkeys(p.notes + notes))
            p.abap = abap
        if len(parts) == 1 and (prev is None or not aggregate):
            final = parts[0]
            if prev is not None:
                final.union_with.append((prev.id, None))
                final.unique_keys = []
        else:
            union = self.new_relation(target, "union", [loop.stmt], label="APPEND (several)")
            cols = [c.name for c in parts[0].columns]
            selects = [f"SELECT {', '.join(c.lower() for c in cols)} FROM {p.id}" for p in parts]
            if prev is not None:
                selects.insert(0, f"SELECT {', '.join(c.lower() for c in cols)} FROM {prev.id}")
            union.raw_sql = "\nUNION ALL\n".join(selects)
            union.columns = [OutCol(c.name, lit("NULL"), c.comp) for c in parts[0].columns]
            union.status = status
            final = union
            if aggregate:
                agg = self.new_relation(target, "collect", [loop.stmt], label="COLLECT")
                agg.sources = [Source("c", "rel", union.id)]
                agg.columns = [OutCol(c.name, self.col("c", c.name, c.comp.ddic_type if c.comp else None), c.comp,
                                      "SUM" if c.comp is not None and c.comp.is_numeric else None) for c in parts[0].columns]
                agg.group_all = True
                agg.unique_keys = [[c.name for c in agg.columns if c.agg is None]]
                final = agg
        if any(e.kind == "insert" for e in emits):
            v = self.var_info(target)
            if v is not None and v.type.unique_key and v.type.table_kind in ("SORTED", "HASHED"):
                dd = self.new_relation(target, "dedup", [loop.stmt], label="INSERT (unique key)")
                dd.sources = [Source("t", "rel", final.id)]
                dd.columns = [OutCol(c.name, self.col("t", c.name, c.comp.ddic_type if c.comp else None), c.comp) for c in final.columns]
                keys = [k.upper() for k in v.type.unique_key]
                dd.qualify = f"ROW_NUMBER() OVER (PARTITION BY {', '.join('t.' + k.lower() for k in keys)} ORDER BY 1) = 1"
                dd.unique_keys = [keys]
                final = dd
        v = self.var_info(target)
        if v is not None and v.type.unique_key and v.type.table_kind in ("SORTED", "HASHED"):
            final.unique_keys.append([k.upper() for k in v.type.unique_key])
        sort = [(k.upper(), False) for k in v.type.unique_key] if v is not None and v.type.table_kind == "SORTED" and v.type.unique_key else []
        self.set_itab(target, ItabState(rel=final, sort=sort))
        if self.loop is None:
            for e in emits:
                self._check_uncleared(loop, e)

    def _check_uncleared(self, loop: LoopCtx, e: Emit) -> None:
        stmt_src = self._source_name(e.stmt.node.child("Source") or e.stmt.node.child("SimpleSource4"))
        if not stmt_src:
            return
        n, _ = self.locate(stmt_src)
        if n not in loop.cleared and n != loop.row_var:
            self.finding("info", "WA_NOT_CLEARED",
                         f"Work area {n} is not cleared inside the LOOP; in ABAP, fields not set in a row keep the previous row's values. "
                         "The SQL uses initial values.", e.stmt)

    def _materialize_modify(self, loop: LoopCtx, itab_name: str, guard, status, notes, abap) -> None:
        n = loop.var.split(":")[-1]
        rel = self.new_relation(n, "modify", [loop.stmt], label="LOOP ... modify rows")
        rel.sources = [s for s in loop.sources if not s.join == "inner"]
        base_cols = loop.rel.columns
        if loop.assigning and loop.row_var:
            cells = self.struct_cells(loop.row_var)
            # struct_cells sees the merged per-row values at the end of the loop body
            values = {c.name: cells.get(c.name) for c in base_cols}
        else:
            values = {c.name: self.col(loop.alias, c.name, c.comp.ddic_type if c.comp else None) for c in base_cols}
            for conds, upd in loop.updates:
                g = _and(conds) if conds else None
                for k, v in upd.items():
                    if k in values:
                        values[k] = v if g is None else v.combine(g, values[k], sql=f"CASE WHEN {g.sql} THEN {v.sql} ELSE {values[k].sql} END")
        cols = []
        for c in base_cols:
            v = values.get(c.name) or self.col(loop.alias, c.name, c.comp.ddic_type if c.comp else None)
            if guard:
                g = _and(guard)
                orig = self.col(loop.alias, c.name, c.comp.ddic_type if c.comp else None)
                if v.sql != orig.sql:
                    v = v.combine(g, sql=f"CASE WHEN {g.sql} THEN {v.sql} ELSE {orig.sql} END")
            cols.append(OutCol(c.name, self.convert(v, c.comp), c.comp))
        rel.columns = cols
        rel.where = list(loop.where) if False else []
        for d in loop.deletes:
            g = _and(d + guard) if (d or guard) else lit("TRUE", "BOOL")
            rel.where.append(g.combine(sql=f"NOT COALESCE(({g.sql}), FALSE)", ddic="BOOL"))
        if loop.where and loop.deletes:
            notes.append("DELETE inside LOOP ... WHERE: rows outside the WHERE are kept")
        used = {a for oc in cols for a, _ in oc.expr.deps} | {a for w in rel.where for a, _ in w.deps}
        rel.sources = [s for s in rel.sources if not (s.lookup and s.alias not in used)]
        if loop.where and not loop.deletes and any(c.expr.sql != f"{loop.alias}.{c.name.lower()}" for c in cols):
            w = _and(loop.where)
            rel.columns = [OutCol(c.name, c.expr if c.expr.sql == f"{loop.alias}.{c.name.lower()}" else
                                  c.expr.combine(w, sql=f"CASE WHEN {w.sql} THEN {c.expr.sql} ELSE {loop.alias}.{c.name.lower()} END"), c.comp)
                           for c in rel.columns]
        rel.unique_keys = list(loop.rel.unique_keys)
        rel.uses_params = any(x.uses_params for x in rel.all_exprs())
        rel.status = status
        rel.notes = list(notes)
        rel.abap = abap
        for x in rel.all_exprs():
            if x.unknown:
                rel.status = "needs_llm"
                rel.notes += x.unknown[:3]
        st = self.itab(itab_name)
        self.set_itab(itab_name, ItabState(rel=rel, sort=list(st.sort)))

    # ------------------------------------------------------------------ custom function modules
    def fm_program(self, name: str, source: str):
        cache = getattr(self, "_fm_cache", None)
        if cache is None:
            cache = self._fm_cache = {}
        if name in cache:
            return cache[name]
        from ..parser.bridge import parse_source

        try:
            parsed = parse_source(name, source, self.settings.abap_version)
        except Exception:  # noqa: BLE001
            cache[name] = None
            return None
        for st in parsed.statements:
            st.origin = name
        structure = build_structure(parsed.statements)
        symbols = Symbols(self.kb)
        symbols.load(structure)
        interface: dict[str, Comp] = {}
        for line in source.splitlines():
            m = _FM_PARAM.match(line)
            if m:
                pname, tname = m.group(1).upper(), m.group(2).upper()
                c = symbols.elem_from_ref(tname, "global")
                c.name = pname
                interface[pname] = c
        cache[name] = (structure, symbols, interface)
        self.fm_statements = getattr(self, "fm_statements", {})
        self.fm_statements[name] = parsed.statements
        return cache[name]


def _linear_in(sql: str, tok: str) -> bool:
    """Is `sql` of the form acc + delta (possibly inside CASE branches)? Each occurrence of the
    accumulator token must be added to (`tok + ...`) or be a whole CASE branch value, and no
    enclosing group may be multiplied, divided or passed to a function."""
    i = sql.find(tok)
    while i >= 0:
        after = sql[i + len(tok):].lstrip()
        before = sql[:i].rstrip()
        if not (after.startswith("+") or before.endswith(("THEN", "ELSE", "(")) and (after.startswith((")", "END", "WHEN", "ELSE")) or not after)):
            return False
        depth, j = 0, i - 1
        while j >= 0:  # walk out through enclosing parentheses
            ch = sql[j]
            if ch == ")":
                depth += 1
            elif ch == "(":
                if depth == 0:
                    pre = sql[:j].rstrip()
                    if pre.endswith(("*", "/")) or re.search(r"[A-Za-z_]\w*$", pre) and not re.search(r"(THEN|ELSE|WHEN|AND|OR|NOT)$", pre, re.I):
                        return False
                    k, d2 = j + 1, 1
                    while k < len(sql) and d2:
                        d2 += {"(": 1, ")": -1}.get(sql[k], 0)
                        k += 1
                    if sql[k:].lstrip().startswith(("*", "/")):
                        return False
                else:
                    depth -= 1
            j -= 1
        i = sql.find(tok, i + 1)
    return not re.search(r"[*/]\s*" + re.escape(tok) + "|" + re.escape(tok) + r"\s*[*/]", sql)


def _case(arms: list[tuple[SqlExpr, SqlExpr]], else_val: SqlExpr) -> SqlExpr:
    # CASE WHEN <found> THEN COALESCE(x, init) ELSE init END  ->  COALESCE(x, init)
    if len(arms) == 1:
        c, v = arms[0]
        if c.found_alias and v.sql.startswith("COALESCE(") and v.sql.endswith(f", {else_val.sql})"):
            return v
    parts = [x for c, v in arms for x in (c, v)] + [else_val]
    sql = "CASE " + " ".join(f"WHEN {c.sql} THEN {v.sql}" for c, v in arms) + f" ELSE {else_val.sql} END"
    ddic = next((v.ddic for _, v in arms if v.ddic), else_val.ddic)
    return parts[0].combine(*parts[1:], sql=sql, ddic=ddic)


def _is_terminal(items) -> bool:
    if not items:
        return False
    last = items[-1]
    return isinstance(last, Statement) and last.type in ("Return", "Exit", "Leave", "Stop", "Continue")


def _flat(ctl: Control) -> list[Statement]:
    from .blocks import flatten

    return flatten([ctl])


__all__ = ["Interpreter", "tokenize"]
