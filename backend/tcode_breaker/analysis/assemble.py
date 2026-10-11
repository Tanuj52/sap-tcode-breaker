"""Assemble the public ProgramAnalysis IR from a pipeline run.

Produces everything the UI needs: inventory, call tree, data-flow graph with column-level
detail, output lineage, business glossary, slice and located findings.
"""

from __future__ import annotations

import re

from ..ir.models import (
    CallInfo, CallTreeNode, ColumnUsage, DataFlowGraph, DataObject, FileInfo, Finding, GraphColumn, GraphEdge,
    GraphNode, LineageSource, Loc, OutputColumn, OutputSpec, ProgramAnalysis, ProgramStats, RelationSummary,
    RoutineInfo, SelectionParam, SliceRange, TableUsage,
)
from ..knowledge.models import Provenance
from ..parser.ast import Statement
from .blocks import Control, flatten
from .pipeline import RunResult, UserContext
from .relations import Relation

_TOKEN = re.compile(r"__R\d+__")


class Assembler:
    def __init__(self, run: RunResult, context: UserContext | None = None) -> None:
        self.run = run
        self.ctx = context or UserContext()
        self.kb = run.interp.kb
        self.names = run.sql.cte_names if run.sql else {}
        self.by_id = {r.id: r for r in run.interp.relations}
        self.chain = [self.by_id[i] for i in (run.sql.order if run.sql else [])]

    # ------------------------------------------------------------------ helpers
    def loc(self, s: Statement | None) -> Loc | None:
        if s is None:
            return None
        if s.origin and s.origin != self.run.flat.name:
            return Loc(file=s.origin, line=s.row, end_line=s.end_row)
        a = self.run.flat.ref(s.row)
        b = self.run.flat.ref(s.end_row)
        return Loc(file=a.file, line=a.line, end_line=b.line if b.file == a.file else a.line)

    def sub(self, text: str) -> str:
        return _TOKEN.sub(lambda m: self.names.get(m.group(0), m.group(0)), text)

    def table_name(self, table: str) -> str:
        t = table.upper()
        if t in self.ctx.business_names:
            return self.ctx.business_names[t]
        info = self.kb.table(t)
        return info.description if info else ""

    def column_name(self, table: str | None, col: str) -> str:
        c = col.upper()
        if table:
            key = f"{table.upper()}-{c}"
            if key in self.ctx.business_names:
                return self.ctx.business_names[key]
            f, _ = self.kb.field(table, c)
            if f is not None and f.description:
                return f.description
        return self.ctx.business_names.get(c, "")

    # ------------------------------------------------------------------ build
    def build(self) -> ProgramAnalysis:
        run = self.run
        a = ProgramAnalysis(name=run.name, settings=run.settings)
        a.files = [FileInfo(name=f.name, filename=f.filename, kind=f.kind, lines=f.line_count) for f in run.ingest.files.values()]
        a.params = self.params()
        a.data_objects = self.data_objects()
        a.tables = self.tables()
        a.calls, a.routines, a.call_tree = self.calls()
        a.output = self.output()
        a.relations = self.relation_summaries()
        a.graph = self.graph(a)
        a.slice = self.slice()
        a.findings = self.findings()
        if run.sql:
            a.sql = run.sql.sql
            a.sql_status = run.sql.status
            a.unresolved = run.sql.unresolved
        else:
            a.sql_status = "failed"
        a.glossary = self.glossary(a)
        a.stats = self.stats(a)
        return a

    def params(self) -> list[SelectionParam]:
        out = []
        for p in self.run.symbols.params.values():
            out.append(SelectionParam(
                name=p.name, kind=p.kind, ref=p.ref, ddic_type=p.comp.ddic_type, length=p.comp.length, default=p.default,
                obligatory=p.obligatory, no_intervals=p.no_intervals, loc=self.loc(p.stmt), provenance=p.comp.provenance,
                used=p.name in self.run.interp.params_used))
        return out

    def data_objects(self) -> list[DataObject]:
        out = []
        for (scope, name), v in self.run.symbols.vars.items():
            if v.kind == "tables_wa" or name in self.run.symbols.params:
                continue
            cols = [self._col_info(c) for c in v.type.columns()][:200]
            out.append(DataObject(name=name, kind=v.kind, type_name=v.type.name, table_kind=v.type.table_kind,
                                  unique_key=v.type.unique_key, columns=cols, scope=scope, inline=v.inline,
                                  value=v.value, loc=self.loc(v.stmt)))
        return out

    def _col_info(self, c):
        from ..ir.models import ColumnInfo

        return ColumnInfo(name=c.name, ddic_type=c.ddic_type, length=c.length, decimals=c.decimals, source_table=c.source_table,
                          source_field=c.source_field, description=c.description, provenance=c.provenance)

    def tables(self) -> list[TableUsage]:
        interp = self.run.interp
        in_slice = {s.original or "" for r in self.chain for s in r.sources if s.kind == "db"}
        in_slice |= {s.name.split(".")[-1].upper() for r in self.chain for s in r.sources if s.kind == "db"}
        names = set(interp.tables) | set(self.run.symbols.db_type_refs)
        out = []
        for t in sorted(names):
            use = interp.tables.get(t)
            info = self.kb.table(t)
            cols: dict[str, set[str]] = {k: set(v) for k, v in (use.columns.items() if use else [])}
            for f in self.run.symbols.db_type_refs.get(t, set()):
                cols.setdefault(f.upper(), set()).add("type_ref")
            col_list = []
            for cname, usages in sorted(cols.items()):
                finfo, status = self.kb.field(t, cname)
                col_list.append(ColumnUsage(
                    name=cname, status=status.value, ddic_type=finfo.ddic_type if finfo else None, length=finfo.length if finfo else None,
                    decimals=finfo.decimals if finfo else None, description=finfo.description if finfo else "",
                    business_name=self.column_name(t, cname), is_key=bool(finfo and finfo.is_key), usages=sorted(usages),
                    provenance=finfo.source if finfo else (Provenance.INFERRED if status.value == "unverified" else Provenance.UNRESOLVED)))
            m = self.kb.s4_mapping_for(t) if self.run.settings.source_system == "s4" else None
            out.append(TableUsage(
                name=t, description=info.description if info else "", business_name=self.table_name(t), module=info.module if info else "",
                release=info.release if info else "", known=info is not None, provenance=info.source if info else Provenance.UNRESOLVED,
                columns=col_list, reads=use.reads if use else 0, writes=use.writes if use else 0, in_slice=t in in_slice,
                physical=self.run.settings.is_physical(t), mapped_to=use.mapped_to if use else None,
                s4_note=(m.title if m else None), locs=[l for l in (self.loc(s) for s in (use.stmts if use else [])) if l]))
        return out

    # ------------------------------------------------------------------ calls
    def calls(self) -> tuple[list[CallInfo], list[RoutineInfo], list[CallTreeNode]]:
        st = self.run.structure
        interp = self.run.interp
        calls: list[CallInfo] = []
        per_routine: dict[str, list[CallInfo]] = {}
        n = 0
        for r in st.routines.values():
            stmts = flatten(r.items) if r.items else r.statements
            for s in stmts:
                c = self._call_of(s, r.name)
                if c is None:
                    continue
                n += 1
                c.id = f"c{n}"
                calls.append(c)
                per_routine.setdefault(r.name, []).append(c)
        reachable: set[str] = set()
        stack = [r.name for r in st.run_order()]
        while stack:
            name = stack.pop()
            if name in reachable:
                continue
            reachable.add(name)
            for c in per_routine.get(name, []):
                if c.kind in ("perform", "method") and c.target in st.routines:
                    stack.append(c.target)
        for c in calls:
            c.reachable = c.caller in reachable
        routines = []
        for r in st.routines.values():
            routines.append(RoutineInfo(
                name=r.name, kind=r.kind if r.kind in ("event", "form", "method", "function_module", "module") else "main",
                loc=self.loc(r.header), end_loc=self.loc(r.end), statements=len(r.statements), reachable=r.name in reachable,
                calls=[c.id for c in per_routine.get(r.name, [])]))

        def node(name: str, kind: str, path: tuple[str, ...]) -> CallTreeNode:
            r = st.routines.get(name)
            t = CallTreeNode(id=f"{'/'.join(path)}", name=name, kind=kind, loc=self.loc(r.header) if r else None, reachable=name in reachable)
            if name in path[:-1]:
                t.recursive = True
                return t
            for c in per_routine.get(name, []):
                child_kind = c.kind if c.kind != "perform" else "form"
                if c.kind in ("perform", "method") and c.target in st.routines:
                    t.children.append(node(c.target, child_kind, path + (c.target,)))
                else:
                    t.children.append(CallTreeNode(id=f"{'/'.join(path)}/{c.id}", name=c.target, kind=c.kind, fm_kind=c.fm_kind,
                                                   loc=c.loc, reachable=c.reachable))
            return t

        tree = [node(r.name, "event", (r.name,)) for r in st.run_order()]
        dead = [r for r in st.routines.values() if r.name not in reachable and r.kind == "form"]
        if dead:
            tree.append(CallTreeNode(id="__unused__", name=f"Unused FORMs ({len(dead)})", kind="group", reachable=False,
                                     children=[CallTreeNode(id=f"__unused__/{r.name}", name=r.name, kind="form", loc=self.loc(r.header), reachable=False)
                                               for r in dead]))
        _ = interp
        return calls, routines, tree

    def _call_of(self, s: Statement, caller: str) -> CallInfo | None:
        interp = self.run.interp
        if s.type == "Perform":
            toks = s.tokens()
            target = toks[1].upper() if len(toks) > 1 else "?"
            return CallInfo(id="", kind="perform", target=target, caller=caller, loc=self.loc(s),
                            resolved=target in self.run.structure.routines, dynamic=target.startswith("("),
                            provenance=Provenance.INFERRED)
        if s.type == "CallFunction":
            fn = s.node.child("FunctionName")
            const = fn.first("Constant") if fn is not None else None
            if const is None:
                return CallInfo(id="", kind="function", target="(dynamic)", caller=caller, loc=self.loc(s), dynamic=True)
            name = const.text().strip("'").upper()
            info = self.kb.fm(name)
            has_src = name in interp.fm_sources or self.kb.fm_source(name) is not None
            kind = interp.fm_kinds.get(name) or (info.kind if info else ("custom" if has_src else "unknown"))
            return CallInfo(id="", kind="function", target=name, caller=caller, loc=self.loc(s), fm_kind=kind,
                            provenance=info.source if info else (Provenance.CLIENT_PACK if has_src else Provenance.UNRESOLVED),
                            resolved=info is not None or has_src)
        if s.type == "Call":
            chain = s.node.child("MethodCallChain") or s.node.first("MethodCallChain")
            if chain is None:
                return None
            calls = chain.find_all_outer("MethodCall")
            if not calls:
                return None
            meth = calls[-1].first("MethodName").text().upper()
            cls = chain.child("ClassName")
            if cls is not None:
                target = f"{cls.text().upper()}=>{meth}"
            else:
                txt = chain.text().upper()
                obj = txt.split("->")[0].strip() if "->" in txt else ""
                target = f"{obj}->{meth}" if obj and obj != meth else meth
            info = self.kb.method(target)
            local = target in self.run.structure.routines
            return CallInfo(id="", kind="method", target=target, caller=caller, loc=self.loc(s), fm_kind=info.kind if info else None,
                            resolved=info is not None or local, provenance=info.source if info else Provenance.INFERRED)
        if s.type in ("Submit", "CallTransaction"):
            toks = s.tokens()
            return CallInfo(id="", kind="submit" if s.type == "Submit" else "transaction", target=(toks[1] if len(toks) > 1 else "?").strip("'").upper(),
                            caller=caller, loc=self.loc(s))
        return None

    # ------------------------------------------------------------------ output + lineage
    def lineage(self, rel: Relation, col: str, depth: int = 0) -> tuple[list[LineageSource], bool]:
        if depth > 40:
            return [], True
        oc = rel.col(col)
        derived = False
        out: list[LineageSource] = []
        if oc is None:
            return [], True
        if rel.raw_sql is not None:
            for dep in _TOKEN.findall(rel.raw_sql):
                r2 = self.by_id.get(dep)
                if r2 is not None and r2.col(col) is not None:
                    src, d = self.lineage(r2, col, depth + 1)
                    out += src
                    derived = derived or d
            return _dedup(out), derived
        expr = oc.expr
        derived = not (expr.kind == "col" or re.fullmatch(r"COALESCE\(\w+\.\w+, [^()]*\)", expr.sql or "") is not None) or oc.agg is not None
        for alias, c in expr.deps:
            src = next((s for s in rel.sources if s.alias == alias), None)
            if src is None:
                continue
            if src.kind == "db":
                out.append(LineageSource(table=(src.original or src.name.split(".")[-1]).upper(), field=c))
            elif src.kind == "rel" and src.name in self.by_id:
                sub, d = self.lineage(self.by_id[src.name], c, depth + 1)
                out += sub
                derived = derived or d
        return _dedup(out), derived

    def output(self) -> OutputSpec | None:
        run = self.run
        rel = run.output_rel
        if rel is None or run.output is None:
            return None
        cols = []
        for spec in run.output_cols:
            oc = rel.col(spec.name)
            lin, derived = self.lineage(rel, spec.name)
            bname = self.ctx.business_names.get(spec.name) or (self.column_name(lin[0].table, lin[0].field) if lin and not derived else "")
            cols.append(OutputColumn(
                name=spec.name, label=spec.label, business_name=bname or spec.label, hidden=spec.hidden,
                ddic_type=oc.comp.ddic_type if oc and oc.comp else None, length=oc.comp.length if oc and oc.comp else None,
                decimals=oc.comp.decimals if oc and oc.comp else None, lineage=lin,
                expression=self.sub(oc.sql) if oc else None, derived=derived))
        return OutputSpec(kind=run.output.kind, table=run.output.var, relation_id=rel.id, columns=cols, order_by=run.output.sort,
                          column_source="fieldcat" if run.output.fieldcat and any(not c.hidden for c in run.output_cols) and
                          len(run.output_cols) != len(rel.columns) else "structure", loc=self.loc(run.output.stmt))

    def relation_summaries(self) -> list[RelationSummary]:
        out = []
        chain_ids = {r.id for r in self.chain}
        for r in self.run.interp.relations:
            if r.id not in chain_ids:
                continue
            out.append(RelationSummary(
                id=r.id, cte=self.names.get(r.id, r.id), var=r.var, kind=r.kind, label=r.label, status=r.status,
                columns=r.column_names, inputs=[self.names.get(i, i) for i in r.inputs()],
                sql=self.sub(r.body_sql()), abap=r.abap, notes=r.notes,
                locs=[l for l in (self.loc(s) for s in r.stmts) if l], in_slice=True))
        return out

    # ------------------------------------------------------------------ graph
    def graph(self, a: ProgramAnalysis) -> DataFlowGraph:
        g = DataFlowGraph()
        seen_tables: dict[str, GraphNode] = {}
        table_usage = {t.name: t for t in a.tables}
        e_n = 0

        def edge(src: str, dst: str, kind: str, label: str | None = None, **data) -> None:
            nonlocal e_n
            e_n += 1
            g.edges.append(GraphEdge(id=f"e{e_n}", source=src, target=dst, kind=kind, label=label, data=data))

        param_used = [p for p in a.params if p.used]
        if param_used:
            g.nodes.append(GraphNode(id="params", kind="param", label="Selection screen", sub=f"{len(param_used)} inputs",
                                     columns=[GraphColumn(name=p.name, ddic_type=p.ddic_type, business_name=self.column_name(*(p.ref.split("-") if p.ref and "-" in p.ref else (None, p.name))))
                                              for p in param_used]))
        for r in self.chain:
            cte = self.names.get(r.id, r.id)
            cols = []
            for c in r.columns:
                lin, derived = self.lineage(r, c.name)
                bname = self.column_name(lin[0].table, lin[0].field) if lin and not derived else self.ctx.business_names.get(c.name, "")
                cols.append(GraphColumn(name=c.name, ddic_type=c.comp.ddic_type if c.comp else c.expr.ddic,
                                        expression=self.sub(c.sql) if r.raw_sql is None else None, derived=derived, business_name=bname))
            status = "ok" if r.status == "deterministic" else ("llm" if r.llm_sql else ("unresolved" if r.status == "needs_llm" else "warning"))
            g.nodes.append(GraphNode(id=r.id, kind="itab", label=r.var.lower(), sub=r.label, op=r.kind, group=r.var, columns=cols,
                                     loc=self.loc(r.stmts[0]) if r.stmts else None, status=status,
                                     data={"cte": cte, "sql": self.sub(r.body_sql()), "notes": r.notes, "abap": r.abap,
                                           "where": [self.sub(w.sql) for w in r.where], "distinct": r.distinct,
                                           "group_all": r.group_all, "qualify": self.sub(r.qualify) if r.qualify else None}))
            for s in r.sources:
                on = [self.sub(c.sql) for c in s.on]
                if s.kind == "db":
                    tname = (s.original or s.name.split(".")[-1]).upper()
                    physical = s.name.split(".")[-1].upper()
                    if tname not in seen_tables:
                        tu = table_usage.get(tname)
                        node = GraphNode(id=f"db:{tname}", kind="db_table", label=tname, sub=self.table_name(tname) or None,
                                         columns=[GraphColumn(name=c.name, ddic_type=c.ddic_type, status=c.status, business_name=c.business_name)
                                                  for c in (tu.columns if tu else [])],
                                         status="ok" if tu is None or tu.known else "warning",
                                         data={"physical": s.name, "mapped_to": physical if physical != tname else None,
                                               "description": tu.description if tu else ""})
                        seen_tables[tname] = node
                        g.nodes.append(node)
                    kind = "read" if s.join == "from" else ("lookup" if s.lookup else "join")
                    label = None if s.join == "from" else f"{s.join.upper()} JOIN"
                    edge(f"db:{tname}", r.id, kind, label, on=on, join=s.join, alias=s.alias, filter=s.extra_filter)
                elif s.kind == "rel" and s.name in self.by_id:
                    kind = "flow" if s.join == "from" else ("lookup" if s.lookup else "join")
                    label = {"lookup": "READ TABLE" if s.lookup else None, "join": f"{s.join.upper()} JOIN"}.get(kind)
                    edge(s.name, r.id, kind, label, on=on, join=s.join, alias=s.alias, dedup=s.dedup_keys)
                elif s.kind == "params":
                    edge("params", r.id, "param")
            for w in r.where:
                for dep in w.rels:
                    if dep in self.by_id:
                        edge(dep, r.id, "fae", "FOR ALL ENTRIES" if r.kind == "fae_read" else "EXISTS", cond=self.sub(w.sql))
            for col in r.columns:
                for dep in col.expr.rels:
                    if dep in self.by_id:
                        edge(dep, r.id, "aggregate", "subquery", column=col.name)
            for dep, _ in r.union_with:
                edge(dep, r.id, "flow", "UNION ALL")
            if r.raw_sql:
                for dep in set(_TOKEN.findall(r.raw_sql)):
                    if dep in self.by_id:
                        edge(dep, r.id, "flow", "UNION ALL" if "UNION" in r.raw_sql else None)
            if r.uses_params and param_used and not any(e.source == "params" and e.target == r.id for e in g.edges):
                edge("params", r.id, "param")
        # function modules
        for c in a.calls:
            if c.kind != "function" or not c.reachable or c.fm_kind in ("ui", "output_sink", None):
                continue
            fid = f"fm:{c.target}"
            if not any(n.id == fid for n in g.nodes):
                g.nodes.append(GraphNode(id=fid, kind="fm", label=c.target, sub=c.fm_kind, loc=c.loc,
                                         status="ok" if c.resolved else "unresolved",
                                         data={"description": (self.kb.fm(c.target).note if self.kb.fm(c.target) else None)}))
            for r in self.chain:
                if f"'{c.target}'" in r.abap.upper():
                    edge(fid, r.id, "flow", "called in")
        if a.output is not None and a.output.relation_id:
            g.nodes.append(GraphNode(id="output", kind="output", label="Report output", sub=a.output.kind.upper(),
                                     columns=[GraphColumn(name=c.name, ddic_type=c.ddic_type, derived=c.derived, business_name=c.business_name or c.label)
                                              for c in a.output.columns if not c.hidden], loc=a.output.loc))
            edge(a.output.relation_id, "output", "output")
        # unique edges
        seen = set()
        uniq = []
        for e in g.edges:
            k = (e.source, e.target, e.kind, e.label)
            if k not in seen:
                seen.add(k)
                uniq.append(e)
        g.edges = uniq
        return g

    # ------------------------------------------------------------------ slice, findings, glossary, stats
    def slice(self) -> list[SliceRange]:
        rows: set[int] = set()
        loops: dict[int, Control] = {}
        for r in self.run.structure.routines.values():
            _index_controls(r.items, loops)
        main = self.run.flat.name
        for rel in self.chain:
            for s in rel.stmts:
                if s.origin and s.origin != main:
                    continue
                ctl = loops.get(s.index)
                if ctl is not None:
                    rows.update(range(ctl.first_row, ctl.last_row + 1))
                else:
                    rows.update(range(s.row, s.end_row + 1))
        if self.run.output and self.run.output.stmt is not None:
            rows.update(range(self.run.output.stmt.row, self.run.output.stmt.end_row + 1))
        vars_ = {r.var for r in self.chain}
        for (_, name), v in self.run.symbols.vars.items():
            if name in vars_ and v.stmt is not None:
                rows.update(range(v.stmt.row, v.stmt.end_row + 1))
        for p in self.run.symbols.params.values():
            if p.name in self.run.interp.params_used and p.stmt is not None:
                rows.add(p.stmt.row)
        ranges: list[SliceRange] = []
        for row in sorted(rows):
            ref = self.run.flat.ref(row)
            if ranges and ranges[-1].file == ref.file and ref.line <= ranges[-1].end + 1:
                ranges[-1].end = max(ranges[-1].end, ref.line)
            else:
                ranges.append(SliceRange(file=ref.file, start=ref.line, end=ref.line))
        return ranges

    def findings(self) -> list[Finding]:
        out = []
        for i in self.run.ingest.issues + self.run.flat.issues:
            out.append(Finding(severity=i.severity if i.severity in ("error", "warning", "info") else "info", code=i.code, message=i.message,
                               loc=Loc(file=i.ref.file, line=i.ref.line) if i.ref else None))
        for msg in self.run.issues:
            out.append(Finding(severity="warning", code="STRUCTURE", message=msg))
        for sev, msg, stmt in self.run.symbols.issues:
            out.append(Finding(severity=sev if sev in ("error", "warning", "info") else "info", code="DECLARATION", message=msg, loc=self.loc(stmt)))
        for u in self.run.parsed.unknown_statements:
            out.append(Finding(severity="warning", code="PARSE_UNKNOWN", message=f"Statement not recognized by the parser: {u.text[:100]}", loc=self.loc(u)))
        for f in self.run.interp.findings:
            out.append(Finding(severity=f.severity, code=f.code, message=f.message, loc=self.loc(f.stmt), hint=f.hint))
        order = {"error": 0, "warning": 1, "info": 2}
        return sorted(out, key=lambda f: (order.get(f.severity, 3), f.loc.line if f.loc else 0))

    def glossary(self, a: ProgramAnalysis) -> dict[str, str]:
        g: dict[str, str] = {}
        for t in a.tables:
            if t.business_name:
                g[t.name] = t.business_name
            for c in t.columns:
                if c.business_name:
                    g[f"{t.name}-{c.name}"] = c.business_name
        if a.output:
            for c in a.output.columns:
                if c.business_name:
                    g.setdefault(f"OUTPUT-{c.name}", c.business_name)
        g.update(self.ctx.business_names)
        return g

    def stats(self, a: ProgramAnalysis) -> ProgramStats:
        run = self.run
        slice_lines = sum(r.end - r.start + 1 for r in a.slice)
        return ProgramStats(
            lines=len(run.flat.line_map), statements=len(run.parsed.statements),
            slice_statements=sum(len(r.stmts) for r in self.chain), slice_lines=slice_lines,
            tables=len([t for t in a.tables if t.reads or t.writes]), columns=sum(len(t.columns) for t in a.tables),
            routines=len(a.routines), dead_routines=len([r for r in a.routines if not r.reachable]),
            calls=len(a.calls), relations=len(self.chain),
            deterministic_relations=len([r for r in self.chain if r.status == "deterministic"]),
            llm_relations=len([r for r in self.chain if r.status != "deterministic"]))


def _index_controls(items, out: dict[int, Control]) -> None:
    for it in items:
        if isinstance(it, Control):
            out[it.header.index] = it
            for b in it.branches:
                _index_controls(b.items, out)


def _dedup(items: list[LineageSource]) -> list[LineageSource]:
    seen = set()
    out = []
    for i in items:
        k = (i.table, i.field)
        if k not in seen:
            seen.add(k)
            out.append(i)
    return out


def analyze(run: RunResult, context: UserContext | None = None, mode: str = "select", view_name: str | None = None) -> ProgramAnalysis:
    a = Assembler(run, context).build()
    a.sql_mode = mode
    a.view_name = view_name
    a.programs = [p.name for p in run.ingest.programs] or [run.name]
    a.output_candidates = sorted({r.var for r in run.interp.relations if not r.is_empty and r.var and not r.var.startswith("SELECT_LOOP")
                                  and run.symbols.var(r.var) is not None})
    return a
