"""ABAP expression / condition -> Snowflake SQL translation.

The translator is pure: it asks a context object to resolve field references,
so the same code serves the symbolic interpreter, Open SQL host variables and
FM parameter binding.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Protocol

from ..parser.ast import Node

NUMERIC_TYPES = {"INT1", "INT2", "INT4", "INT8", "DEC", "CURR", "QUAN", "FLTP", "D16N", "PREC"}


@dataclass
class SqlExpr:
    sql: str
    deps: set[tuple[str, str]] = field(default_factory=set)  # (alias, column)
    kind: str = "expr"  # col | lit | expr | unknown | param
    ddic: str | None = None  # DDIC type hint of the value
    uses_params: bool = False
    unknown: list[str] = field(default_factory=list)  # ABAP fragments that could not be translated
    nullable: set[str] = field(default_factory=set)  # aliases from LEFT JOINs this value depends on
    found_alias: str | None = None  # set on "lookup found" predicates (sy-subrc = 0)
    var: str | None = None  # ABAP variable this value stands for (itab / range references)
    itab_guard: str | None = None  # set on "<itab> IS NOT INITIAL" predicates
    rels: set[str] = field(default_factory=set)  # relation tokens referenced inside the SQL (subqueries)

    @property
    def ok(self) -> bool:
        return not self.unknown

    def combine(self, *others: "SqlExpr", sql: str, kind: str = "expr", ddic: str | None = None) -> "SqlExpr":
        deps = set(self.deps)
        unknown = list(self.unknown)
        nullable = set(self.nullable)
        rels = set(self.rels)
        uses_params = self.uses_params
        for o in others:
            deps |= o.deps
            unknown += o.unknown
            nullable |= o.nullable
            rels |= o.rels
            uses_params = uses_params or o.uses_params
        out = SqlExpr(sql, deps, kind, ddic, uses_params, unknown, nullable)
        out.rels = rels
        return out


def lit(sql: str, ddic: str | None = None) -> SqlExpr:
    return SqlExpr(sql, kind="lit", ddic=ddic)


def unknown(abap: str, reason: str = "") -> SqlExpr:
    tag = abap.replace("*/", "* /")
    return SqlExpr(f"NULL /* TCB-UNRESOLVED: {tag} */", kind="unknown", unknown=[abap + (f" ({reason})" if reason else "")])


def initial_for(ddic: str | None, length: int | None = None) -> str:
    t = (ddic or "CHAR").upper()
    if t in NUMERIC_TYPES:
        return "0"
    if t == "DATS":
        return "'00000000'"
    if t == "TIMS":
        return "'000000'"
    if t == "NUMC":
        return f"'{'0' * (length or 1)}'" if length and length <= 40 else "''"
    return "''"


def is_numeric(ddic: str | None) -> bool:
    return (ddic or "").upper() in NUMERIC_TYPES


def sql_string(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


class ExprContext(Protocol):
    def field(self, base: str, comps: list[str], node: Node) -> SqlExpr: ...
    def db_column(self, alias: str | None, column: str) -> SqlExpr: ...
    def sql_function(self, node: Node) -> SqlExpr: ...
    def in_range(self, lhs: SqlExpr, name: str, negate: bool) -> SqlExpr: ...
    def range_initial(self, name: str) -> SqlExpr: ...
    def select_option(self, name: str) -> str | None: ...  # SQL of the param array, if `name` is a select-option
    def lines(self, name: str) -> SqlExpr: ...
    def reduce(self, node: Node) -> SqlExpr: ...
    def table_expression(self, node: Node) -> SqlExpr: ...
    def text_symbol(self, key: str) -> SqlExpr: ...


_ARITH = {"+": 1, "-": 1, "*": 2, "/": 2, "DIV": 2, "MOD": 2, "**": 3, "||": 0}
_COMPARE = {"=": "=", "EQ": "=", "<>": "<>", "NE": "<>", "><": "<>", "<": "<", "LT": "<", ">": ">", "GT": ">",
            "<=": "<=", "LE": "<=", "=<": "<=", ">=": ">=", "GE": ">=", "=>": ">="}
_CONSTRUCTORS = {"VALUE", "COND", "SWITCH", "REDUCE", "CONV", "CORRESPONDING", "EXACT", "NEW", "REF", "CAST", "FILTER", "BOOLC", "XSDBOOL"}


class ExprTranslator:
    def __init__(self, ctx: ExprContext) -> None:
        self.ctx = ctx

    # ------------------------------------------------------------------ sources
    def source(self, node: Node | None) -> SqlExpr:
        if node is None:
            return unknown("<empty>")
        if node.type in ("Source", "SimpleSource1", "SimpleSource2", "SimpleSource3", "SimpleSource4", "SQLSource", "SQLSourceSimple"):
            first = node.children[0] if node.children else None
            if first is not None and first.is_token and first.value.upper() in _CONSTRUCTORS:
                return self.constructor(node)
            parts = self._flatten(node)
            return self._build(parts)
        return self._operand(node)

    def _flatten(self, node: Node) -> list[tuple[str, object]]:
        parts: list[tuple[str, object]] = []
        ch = node.children
        i = 0
        while i < len(ch):
            c = ch[i]
            if c.is_token:
                v = c.value.upper()
                if v == "(":
                    # parenthesized group: '(' Source ')'
                    inner = ch[i + 1] if i + 1 < len(ch) else None
                    e = self.source(inner)
                    parts.append(("opd", e.combine(sql=f"({e.sql})", ddic=e.ddic)))
                    i += 3
                    continue
                if v == "&&":
                    parts.append(("op", "||"))
                elif v in ("@",):
                    pass
                elif v == "-" and not parts:
                    parts.append(("opd", lit("0")))
                    parts.append(("op", "-"))
                elif v in _CONSTRUCTORS:
                    parts.append(("opd", self.constructor(node)))
                    return parts
                else:
                    parts.append(("opd", unknown(c.value)))
                i += 1
                continue
            if c.type == "ArithOperator":
                parts.append(("op", (c.first_token().value or "").upper()))
            elif c.type in ("Source", "SimpleSource3", "SQLSource"):
                first = c.children[0] if c.children else None
                if first is not None and first.is_token and first.value.upper() in _CONSTRUCTORS:
                    parts.append(("opd", self.constructor(c)))
                else:
                    parts.extend(self._flatten(c))
            elif c.type == "Dereference":
                pass
            else:
                parts.append(("opd", self._operand(c)))
            i += 1
        return parts

    def _build(self, parts: list[tuple[str, object]]) -> SqlExpr:
        operands = [p for p in parts if p[0] == "opd"]
        if not operands:
            return unknown("<empty expression>")
        if len(parts) == 1:
            return parts[0][1]  # type: ignore[return-value]

        # precedence climbing over the flat list
        pos = 0

        def parse(min_prec: int) -> SqlExpr:
            nonlocal pos
            left: SqlExpr = parts[pos][1]  # type: ignore[assignment]
            pos += 1
            while pos < len(parts) and parts[pos][0] == "op" and _ARITH.get(parts[pos][1], -1) >= min_prec:  # type: ignore[arg-type]
                op = parts[pos][1]
                prec = _ARITH[op]  # type: ignore[index]
                pos += 1
                right = parse(prec + 1 if op != "**" else prec)
                left = self._apply(op, left, right)  # type: ignore[arg-type]
            return left

        try:
            return parse(0)
        except (IndexError, TypeError):
            return unknown(" ".join(str(p[1].sql if hasattr(p[1], "sql") else p[1]) for p in parts))

    def _apply(self, op: str, a: SqlExpr, b: SqlExpr) -> SqlExpr:
        ddic = "DEC" if is_numeric(a.ddic) or is_numeric(b.ddic) or op in ("/", "*") else (a.ddic or b.ddic)
        if op == "||":
            return a.combine(b, sql=f"{a.sql} || {b.sql}", ddic="STRG")
        if op == "DIV":
            return a.combine(b, sql=f"FLOOR({a.sql} / NULLIF({b.sql}, 0))", ddic="INT4")
        if op == "MOD":
            return a.combine(b, sql=f"MOD({a.sql}, {b.sql})", ddic=ddic)
        if op == "**":
            return a.combine(b, sql=f"POWER({a.sql}, {b.sql})", ddic="FLTP")
        if op in ("+", "-") and (a.ddic or "").upper() == "DATS" and is_numeric(b.ddic):
            sign = "" if op == "+" else "-"
            return a.combine(b, sql=f"TO_VARCHAR(DATEADD(day, {sign}{b.sql}, TRY_TO_DATE({a.sql}, 'YYYYMMDD')), 'YYYYMMDD')", ddic="DATS")
        if op == "-" and (a.ddic or "").upper() == "DATS" and (b.ddic or "").upper() == "DATS":
            return a.combine(b, sql=f"DATEDIFF(day, TRY_TO_DATE({b.sql}, 'YYYYMMDD'), TRY_TO_DATE({a.sql}, 'YYYYMMDD'))", ddic="INT4")
        return a.combine(b, sql=f"{a.sql} {op} {b.sql}", ddic=ddic)

    def _operand(self, node: Node) -> SqlExpr:
        t = node.type
        if t == "Constant":
            return self.constant(node)
        if t in ("FieldChain", "SimpleFieldChain", "SimpleFieldChain2", "SourceField", "SourceFieldSymbol", "Field", "FieldSymbol"):
            return self.field_chain(node)
        if t == "MethodCallChain":
            return self.method_call(node)
        if t == "StringTemplate":
            return self.string_template(node)
        if t == "TextElement":
            key = node.first("TextElementKey")
            return self.ctx.text_symbol(key.text() if key else node.text())
        if t in ("Source", "SimpleSource1", "SimpleSource2", "SimpleSource3", "SimpleSource4", "SQLSource"):
            return self.source(node)
        if t in ("SQLFieldName", "SQLAliasField"):
            return self.db_field(node)
        if t == "SQLFunction" or t == "SQLAggregation":
            return self.ctx.sql_function(node)
        if t == "SQLCase":
            return self.ctx.sql_function(node)
        return unknown(node.text(), f"unsupported operand {t}")

    def constant(self, node: Node) -> SqlExpr:
        inner = node.children[0] if node.children else node
        if inner.type == "Integer":
            return lit("".join(t.value for t in inner.tokens()), "INT4")
        if inner.type == "ConstantString" or inner.is_token:
            raw = inner.text()
            return self.string_literal(raw)
        if inner.type == "TextSymbol":
            return self.ctx.text_symbol(inner.text())
        # concatenated literals 'a' & 'b'
        toks = [t.value for t in node.tokens() if t.value not in ("&",)]
        return lit(" || ".join(self.string_literal(t).sql for t in toks), "CHAR")

    @staticmethod
    def string_literal(raw: str) -> SqlExpr:
        raw = raw.strip()
        if raw.startswith("'") and raw.endswith("'"):
            body = raw[1:-1].replace("''", "'")
            # decimal numbers are written as quoted literals in ABAP: '1.5'
            if re.fullmatch(r"-?\d+\.\d+", body):
                return lit(body, "DEC")
            return lit(sql_string(body), "CHAR")
        if raw.startswith("`") and raw.endswith("`"):
            return lit(sql_string(raw[1:-1].replace("``", "`")), "STRG")
        if re.fullmatch(r"-?\d+", raw):
            return lit(raw, "INT4")
        return lit(sql_string(raw), "CHAR")

    def field_chain(self, node: Node) -> SqlExpr:
        toks = node.tokens()
        base = None
        comps: list[str] = []
        offset = None
        length = None
        table_expr = node.first("TableExpression")
        if table_expr is not None:
            return self.ctx.table_expression(node)
        for c in (node.children if not node.is_token else [node]):
            if c.type in ("SourceField", "SourceFieldSymbol", "Field", "FieldSymbol", "TargetField", "TargetFieldSymbol", "ClassName"):
                base = c.text()
            elif c.type in ("ComponentName", "AttributeName"):
                comps.append(c.text())
            elif c.type == "FieldOffset":
                offset = "".join(t.value for t in c.tokens() if t.value != "+")
            elif c.type == "FieldLength":
                length = "".join(t.value for t in c.tokens() if t.value not in ("(", ")"))
            elif c.is_token and c.value not in ("-", "=>", "->", "~"):
                if base is None:
                    base = c.value
        if base is None and toks:
            base = toks[0].value
        if base and "~" in base:  # Open SQL alias~field as a single token
            alias, _, col = base.partition("~")
            e = self.ctx.field(alias, [col] + comps, node)
        else:
            e = self.ctx.field(base or "?", comps, node)
        if offset is not None or length is not None:
            off_sql = self._offset_sql(offset)
            if length is not None and length != "*":
                e = e.combine(sql=f"SUBSTR({e.sql}, {off_sql}, {self._len_sql(length)})", ddic="CHAR")
            else:
                e = e.combine(sql=f"SUBSTR({e.sql}, {off_sql})", ddic="CHAR")
        return e

    def _offset_sql(self, offset: str | None) -> str:
        if offset is None:
            return "1"
        if offset.isdigit():
            return str(int(offset) + 1)
        e = self.ctx.field(offset, [], Node({"v": offset}))
        return f"{e.sql} + 1"

    def _len_sql(self, length: str) -> str:
        if length.isdigit():
            return length
        return self.ctx.field(length, [], Node({"v": length})).sql

    # ------------------------------------------------------------------ functions
    def _call_args(self, call: Node) -> tuple[list[SqlExpr], dict[str, SqlExpr]]:
        param = call.first("MethodCallParam")
        positional: list[SqlExpr] = []
        named: dict[str, SqlExpr] = {}
        if param is None:
            return positional, named
        for c in param.children:
            if c.type in ("Source",):
                positional.append(self.source(c))
            elif c.type in ("ParameterListS", "MethodParameters"):
                for p in c.find_all("ParameterS"):
                    name = p.first("ParameterName")
                    src = p.child("Source")
                    if name is not None:
                        named[name.text().upper()] = self.source(src)
            elif c.type == "ParameterS":
                name = c.first("ParameterName")
                if name is not None:
                    named[name.text().upper()] = self.source(c.child("Source"))
        return positional, named

    def method_call(self, node: Node) -> SqlExpr:
        calls = node.direct("MethodCall")
        if len(calls) != 1 or node.child("ClassName") is not None or any(c.is_token and c.value in ("->", "=>") for c in node.children):
            hook = getattr(self.ctx, "functional_call", None)
            res = hook(node) if hook is not None else None
            return res if res is not None else unknown(node.text(), "method call")
        call = calls[0]
        name_node = call.first("MethodName")
        name = (name_node.text() if name_node else "").lower()
        pos, named = self._call_args(call)
        arg = pos[0] if pos else named.get("VAL")

        def one(sql_fn: str, ddic: str | None = None) -> SqlExpr:
            if arg is None:
                return unknown(node.text())
            return arg.combine(sql=sql_fn.format(arg.sql), ddic=ddic or arg.ddic)

        if name == "lines":
            src = call.first("MethodCallParam")
            inner = src.first("Source") if src else None
            fc = inner.first("FieldChain") if inner else None
            return self.ctx.lines(fc.text() if fc else (inner.text() if inner else ""))
        simple = {
            "strlen": ("LENGTH(RTRIM({}))", "INT4"),
            "numofchar": ("LENGTH(RTRIM({}))", "INT4"),
            "to_upper": ("UPPER({})", None),
            "to_lower": ("LOWER({})", None),
            "to_mixed": ("INITCAP({})", None),
            "abs": ("ABS({})", None),
            "ceil": ("CEIL({})", None),
            "floor": ("FLOOR({})", None),
            "trunc": ("TRUNC({})", None),
            "frac": ("({0} - TRUNC({0}))", None),
            "sign": ("SIGN({})", "INT4"),
            "sqrt": ("SQRT({})", "FLTP"),
            "reverse": ("REVERSE({})", None),
        }
        if name in simple:
            fn, ddic = simple[name]
            if arg is None:
                return unknown(node.text())
            return arg.combine(sql=fn.format(arg.sql), ddic=ddic or arg.ddic)
        if name == "condense":
            if arg is None:
                return unknown(node.text())
            return one("REGEXP_REPLACE(TRIM({}), ' +', ' ')", "STRG")
        if name == "round":
            dec = named.get("DEC")
            if arg is None:
                return unknown(node.text())
            return arg.combine(*( [dec] if dec else []), sql=f"ROUND({arg.sql}, {dec.sql if dec else 0})")
        if name == "substring":
            off = named.get("OFF")
            ln = named.get("LEN")
            if arg is None:
                return unknown(node.text())
            off_sql = f"{off.sql} + 1" if off else "1"
            sql = f"SUBSTR({arg.sql}, {off_sql}, {ln.sql})" if ln else f"SUBSTR({arg.sql}, {off_sql})"
            return arg.combine(*[x for x in (off, ln) if x], sql=sql, ddic="STRG")
        if name in ("nmin", "nmax"):
            vals = [v for k, v in sorted(named.items()) if k.startswith("VAL")]
            if len(vals) < 2:
                return unknown(node.text())
            fn = "LEAST" if name == "nmin" else "GREATEST"
            return vals[0].combine(*vals[1:], sql=f"{fn}({', '.join(v.sql for v in vals)})", ddic="DEC")
        if name == "replace":
            sub = named.get("SUB")
            with_ = named.get("WITH")
            if arg is None or sub is None or with_ is None:
                return unknown(node.text())
            return arg.combine(sub, with_, sql=f"REPLACE({arg.sql}, {sub.sql}, {with_.sql})", ddic="STRG")
        if name == "shift_left":
            sub = named.get("SUB")
            if arg is None:
                return unknown(node.text())
            if sub is not None:
                return arg.combine(sub, sql=f"LTRIM({arg.sql}, {sub.sql})", ddic="STRG")
            places = named.get("PLACES")
            if places is not None:
                return arg.combine(places, sql=f"SUBSTR({arg.sql}, {places.sql} + 1)", ddic="STRG")
            return one("LTRIM({})", "STRG")
        if name == "shift_right":
            sub = named.get("SUB")
            if arg is None:
                return unknown(node.text())
            if sub is not None:
                return arg.combine(sub, sql=f"RTRIM({arg.sql}, {sub.sql})", ddic="STRG")
            return one("RTRIM({})", "STRG")
        if name in ("boolc", "xsdbool"):
            inner = call.first("Cond")
            if inner is None:
                return unknown(node.text())
            c = self.cond(inner)
            return c.combine(sql=f"CASE WHEN {c.sql} THEN 'X' ELSE '' END", ddic="CHAR")
        if name == "concat_lines_of":
            return unknown(node.text(), "concat_lines_of")
        if name == "line_exists":
            return self.ctx.table_expression(node)
        if name == "contains":
            sub = named.get("SUB")
            if arg is None or sub is None:
                return unknown(node.text())
            return arg.combine(sub, sql=f"CONTAINS({arg.sql}, {sub.sql})", ddic="BOOL")
        if name == "matches":
            regex = named.get("REGEX") or named.get("PCRE")
            if arg is None or regex is None:
                return unknown(node.text())
            return arg.combine(regex, sql=f"REGEXP_LIKE({arg.sql}, {regex.sql})", ddic="BOOL")
        if name in ("escape", "translate", "segment", "match", "count", "find", "distance", "repeat", "insert", "cmax", "cmin", "char_off"):
            return unknown(node.text(), f"built-in {name}")
        hook = getattr(self.ctx, "functional_call", None)
        res = hook(node) if hook is not None else None
        return res if res is not None else unknown(node.text(), "method call")

    def string_template(self, node: Node) -> SqlExpr:
        pieces: list[SqlExpr] = []
        for c in node.children:
            if c.is_token:
                text = c.value
                if text.startswith(("|", "}")):
                    text = text[1:]
                if text.endswith(("{", "|")):
                    text = text[:-1]
                text = text.replace("\\|", "|").replace("\\{", "{").replace("\\}", "}").replace("\\\\", "\\")
                text = text.replace("\\n", "\n").replace("\\t", "\t")
                if text:
                    pieces.append(lit(sql_string(text), "STRG"))
            elif c.type == "StringTemplateSource":
                src = self.source(c.child("Source"))
                fmt = c.first("StringTemplateFormatting")
                if fmt is not None:
                    ftxt = fmt.text().upper().replace(" ", "")
                    if "ALPHA=OUT" in ftxt:
                        src = src.combine(sql=f"LTRIM({src.sql}, '0')")
                    elif "ALPHA=IN" in ftxt:
                        src = src.combine(sql=src.sql)
                    else:
                        src.unknown.append(f"string template format {fmt.text()}")
                pieces.append(src.combine(sql=f"TO_VARCHAR({src.sql})" if is_numeric(src.ddic) else src.sql))
        if not pieces:
            return lit("''", "STRG")
        if len(pieces) == 1:
            return pieces[0]
        return pieces[0].combine(*pieces[1:], sql=" || ".join(p.sql for p in pieces), ddic="STRG")

    def constructor(self, node: Node) -> SqlExpr:
        kw = node.children[0].value.upper()
        if kw == "COND":
            body = node.child("CondBody")
            if body is None:
                return unknown(node.text())
            arms: list[str] = []
            parts: list[SqlExpr] = []
            else_sql = "NULL"
            ch = body.children
            i = 0
            while i < len(ch):
                c = ch[i]
                if c.is_token and c.value.upper() == "WHEN":
                    cond = self.cond(ch[i + 1])
                    val = self.source(ch[i + 3])
                    parts += [cond, val]
                    arms.append(f"WHEN {cond.sql} THEN {val.sql}")
                    i += 4
                    continue
                if c.is_token and c.value.upper() == "ELSE":
                    val = self.source(ch[i + 1])
                    parts.append(val)
                    else_sql = val.sql
                    i += 2
                    continue
                i += 1
            if not parts:
                return unknown(node.text())
            ddic = next((p.ddic for p in parts[1::2] if p.ddic), None)
            return parts[0].combine(*parts[1:], sql=f"CASE {' '.join(arms)} ELSE {else_sql} END", ddic=ddic)
        if kw == "SWITCH":
            body = node.child("SwitchBody")
            if body is None:
                return unknown(node.text())
            ch = body.children
            subject = self.source(ch[0])
            arms = []
            parts = [subject]
            else_sql = "NULL"
            i = 1
            while i < len(ch):
                c = ch[i]
                if c.is_token and c.value.upper() == "WHEN":
                    v = self.source(ch[i + 1])
                    r = self.source(ch[i + 3])
                    parts += [v, r]
                    arms.append(f"WHEN {v.sql} THEN {r.sql}")
                    i += 4
                    continue
                if c.is_token and c.value.upper() == "ELSE":
                    r = self.source(ch[i + 1])
                    parts.append(r)
                    else_sql = r.sql
                    i += 2
                    continue
                i += 1
            return subject.combine(*parts[1:], sql=f"CASE {subject.sql} {' '.join(arms)} ELSE {else_sql} END")
        if kw in ("CONV", "EXACT"):
            inner = node.first("Source")
            return self.source(inner) if inner is not None else unknown(node.text())
        if kw in ("BOOLC", "XSDBOOL"):
            c = node.first("Cond")
            if c is None:
                return unknown(node.text())
            cc = self.cond(c)
            return cc.combine(sql=f"CASE WHEN {cc.sql} THEN 'X' ELSE '' END", ddic="CHAR")
        if kw == "REDUCE":
            return self.ctx.reduce(node)
        return unknown(node.text(), f"{kw} constructor")

    # ------------------------------------------------------------------ conditions
    def cond(self, node: Node | None) -> SqlExpr:
        if node is None:
            return unknown("<empty condition>")
        if node.type in ("Compare", "ComponentCompare", "SQLCompare"):
            return self.compare(node)
        if node.type in ("CondSub", "ComponentCondSub", "SQLCondSub"):
            neg = node.children and node.children[0].is_token and node.children[0].value.upper() == "NOT"
            inner = node.first("Cond") or node.first("ComponentCond") or node.first("SQLCond")
            e = self.cond(inner)
            return e.combine(sql=f"NOT ({e.sql})" if neg else f"({e.sql})", ddic="BOOL")
        parts: list[str] = []
        exprs: list[SqlExpr] = []
        pending_not = False
        for c in node.children:
            if c.is_token:
                v = c.value.upper()
                if v in ("AND", "OR"):
                    parts.append(v)
                elif v == "NOT":
                    pending_not = True
                elif v == "EQUIV":
                    parts.append("=")
                continue
            e = self.cond(c)
            sql = e.sql
            if pending_not:
                sql = f"NOT ({sql})"
                pending_not = False
            exprs.append(e)
            parts.append(sql)
        if not exprs:
            return unknown(node.text())
        has_or = "OR" in parts
        if has_or and "AND" in parts:
            # wrap AND groups for readability; SQL precedence already matches ABAP (AND binds tighter)
            pass
        sql = " ".join(parts)
        res = exprs[0].combine(*exprs[1:], sql=sql, ddic="BOOL")
        if len(exprs) == 1:
            res.found_alias = exprs[0].found_alias
        return res

    def compare(self, node: Node) -> SqlExpr:
        ch = node.children
        neg = False
        operands: list[SqlExpr] = []
        op: str | None = None
        kws: list[str] = []
        i = 0
        while i < len(ch):
            c = ch[i]
            if c.is_token:
                v = c.value.upper()
                if v == "NOT" and not operands:
                    neg = True
                else:
                    kws.append(v)
                i += 1
                continue
            if (
                c.type in ("SQLSource", "SQLSourceSimple")
                and i + 2 < len(ch)
                and ch[i + 1].is_token
                and ch[i + 1].value == "-"
                and ch[i + 2].type == "SQLFieldName"
            ):
                # Old-style Open SQL host chain split by the parser: SQLSource '-' SQLFieldName  (itab-comp)
                fc = c.first("FieldChain")
                base = fc.text() if fc is not None else c.text().lstrip("@")
                comps = [ch[i + 2].text()]
                j = i + 3
                while j + 1 < len(ch) and ch[j].is_token and ch[j].value == "-" and ch[j + 1].type == "SQLFieldName":
                    comps.append(ch[j + 1].text())
                    j += 2
                operands.append(self.ctx.field(base, comps, c))
                i = j
                continue
            if c.type in ("CompareOperator", "SQLCompareOperator"):
                op = (c.first_token().value or "").upper()
            elif c.type == "SQLIn":
                kws.append("IN")
                src = c.child("SQLSource")
                operands.append(self._in_rhs(c, src))
            elif c.type == "Or":  # CASE WHEN a OR b
                operands.append(self.source(c.child("Source")))
            elif c.type in ("ComponentChainSimple", "ComponentChain"):
                operands.append(self.ctx.field("__ROW__", [c.text()], c))
            elif c.type in ("Source", "SimpleSource3", "SQLSource", "SQLFieldName", "SQLAliasField", "FieldChain", "Constant", "MethodCallChain"):
                operands.append(self._host_or_source(c))
            else:
                operands.append(self._operand(c))
            i += 1

        def wrap(e: SqlExpr) -> SqlExpr:
            return e.combine(sql=f"NOT ({e.sql})", ddic="BOOL") if neg else e

        if "INITIAL" in kws and operands:
            a = operands[0]
            is_not = kws.count("NOT") > 0
            test = self.initial_test(a)
            res = a.combine(sql=f"NOT ({test})" if is_not else test, ddic="BOOL")
            if a.kind == "itab" and is_not and not neg:
                res.itab_guard = a.var
            return wrap(res)
        if ("BOUND" in kws or "ASSIGNED" in kws or "SUPPLIED" in kws) and operands:
            is_not = "NOT" in kws
            return wrap(lit("FALSE" if is_not else "TRUE", "BOOL"))
        if "BETWEEN" in kws and len(operands) >= 3:
            a, lo, hi = operands[:3]
            nb = "NOT " if "NOT" in kws else ""
            return wrap(a.combine(lo, hi, sql=f"{a.sql} {nb}BETWEEN {lo.sql} AND {hi.sql}", ddic="BOOL"))
        if "IN" in kws and len(operands) >= 2:
            a, rng = operands[0], operands[1]
            ni = "NOT" in kws
            if rng.kind == "range_ref":
                return wrap(self.ctx.in_range(a, rng.sql, ni))
            if rng.kind == "value_list":
                return wrap(a.combine(rng, sql=f"{a.sql} {'NOT ' if ni else ''}IN {rng.sql}", ddic="BOOL"))
            return wrap(unknown(node.text(), "IN with a non-range operand"))
        if "NULL" in kws and operands:
            return wrap(operands[0].combine(sql=f"{operands[0].sql} IS {'NOT ' if 'NOT' in kws else ''}NULL", ddic="BOOL"))
        if op and len(operands) >= 2:
            a, b = operands[0], operands[1]
            if op in ("CP", "NP"):
                pat = self._cp_pattern(b)
                sql = f"{a.sql} {'NOT ' if op == 'NP' else ''}ILIKE {pat}"
                return wrap(a.combine(b, sql=sql, ddic="BOOL"))
            if op in ("CS", "NS"):
                sql = f"{'NOT ' if op == 'NS' else ''}CONTAINS(UPPER({a.sql}), UPPER({b.sql}))"
                return wrap(a.combine(b, sql=sql, ddic="BOOL"))
            if op in ("CO", "CN", "CA", "NA"):
                return wrap(unknown(node.text(), f"operator {op}"))
            if op == "LIKE":
                return wrap(a.combine(b, sql=f"{a.sql} LIKE {b.sql}", ddic="BOOL"))
            sop = _COMPARE.get(op)
            if sop is None:
                return wrap(unknown(node.text(), f"operator {op}"))
            # sy-subrc tests on lookups
            if a.kind in ("subrc", "subrc_bool"):
                return wrap(self._subrc_test(a, sop, b))
            if b.kind in ("subrc", "subrc_bool"):
                return wrap(self._subrc_test(b, _flip(sop), a))
            a2, b2 = self._null_safe(a, b, sop)
            res = a2.combine(b2, sql=f"{a2.sql} {sop} {b2.sql}", ddic="BOOL")
            return wrap(res)
        if len(operands) == 1 and operands[0].ddic == "BOOL":
            return wrap(operands[0])
        if len(operands) == 1 and operands[0].found_alias:
            return wrap(operands[0])
        return wrap(unknown(node.text(), "condition"))

    def _host_or_source(self, c: Node) -> SqlExpr:
        if c.type in ("SQLFieldName", "SQLAliasField"):
            return self.db_field(c)
        return self.source(c)

    def db_field(self, node: Node) -> SqlExpr:
        text = node.text()
        alias, sep, col = text.partition("~")
        if not sep:
            alias, col = None, text  # type: ignore[assignment]
        return self.ctx.db_column(alias, col)

    def _in_rhs(self, sqlin: Node, src: Node | None) -> SqlExpr:
        if src is not None:
            fc = src.first("FieldChain")
            name = fc.text() if fc is not None else src.text().lstrip("@")
            return SqlExpr(name.upper(), kind="range_ref")
        # IN ( 'A', 'B' ) value list
        vals = [self.source(s) for s in sqlin.find_all("SQLSource")] or []
        if vals:
            return vals[0].combine(*vals[1:], sql="(" + ", ".join(v.sql for v in vals) + ")", kind="value_list")
        return unknown(sqlin.text())

    def _subrc_test(self, subrc: SqlExpr, op: str, value: SqlExpr) -> SqlExpr:
        if subrc.kind == "subrc_bool" and value.sql in ("0", "4", "8") and op in ("=", "<>"):
            ok = (op == "=") == (value.sql == "0")
            sql = subrc.sql if ok else f"NOT ({subrc.sql})"
            return subrc.combine(sql=sql, ddic="BOOL")
        alias = subrc.found_alias
        if alias is None or value.sql not in ("0", "4", "8"):
            return unknown(f"sy-subrc {op} {value.sql}", "sy-subrc not bound to a lookup")
        found = (op == "=" and value.sql == "0") or (op == "<>" and value.sql != "0")
        sql = f"{subrc.sql} IS {'NOT ' if found else ''}NULL"
        res = SqlExpr(sql, set(subrc.deps), "expr", "BOOL")
        if found:
            res.found_alias = alias
        return res

    def initial_test(self, a: SqlExpr) -> str:
        t = (a.ddic or "").upper()
        if a.kind == "range_ref":
            return self.ctx.range_initial(a.sql).sql
        if a.kind == "itab":
            return f"NOT EXISTS (SELECT 1 FROM {a.sql})"
        if a.kind == "subrc_bool":  # sy-subrc IS INITIAL  <=>  sy-subrc = 0
            return f"({a.sql})"
        if t == "BOOL":
            return f"NOT COALESCE({a.sql}, FALSE)"
        if t in NUMERIC_TYPES:
            return f"COALESCE({a.sql}, 0) = 0"
        if t == "NUMC":
            return f"COALESCE(LTRIM({a.sql}, '0'), '') = ''"
        if t == "DATS":
            return f"COALESCE(NULLIF({a.sql}, '00000000'), '') = ''"
        if t == "TIMS":
            return f"COALESCE(NULLIF({a.sql}, '000000'), '') = ''"
        return f"COALESCE(TRIM({a.sql}), '') = ''"

    def _null_safe(self, a: SqlExpr, b: SqlExpr, op: str) -> tuple[SqlExpr, SqlExpr]:
        """ABAP has no NULL: guard column operands where NULL would change the result."""

        def guard(x: SqlExpr, other: SqlExpr) -> SqlExpr:
            if x.kind != "col" and not x.nullable:
                return x
            xd = x.ddic
            if xd is None and other.kind == "lit" and re.fullmatch(r"-?\d+(\.\d+)?", other.sql):
                xd = "DEC"  # type unknown (no metadata): follow the literal it is compared with
            init = initial_for(xd)
            other_is_initial = other.kind == "lit" and other.sql in ("''", "0", "'00000000'", "'000000'")
            if op == "<>" or other_is_initial or x.nullable:
                if other_is_initial and init == "''":
                    return x.combine(sql=f"COALESCE(TRIM({x.sql}), '')", kind="expr", ddic=x.ddic)
                return x.combine(sql=f"COALESCE({x.sql}, {init})", kind="expr", ddic=x.ddic)
            return x

        if b.kind == "lit" and b.sql in ("''",) and is_numeric(a.ddic):
            b = lit("0", a.ddic)
        charlike = ("NUMC", "CHAR", "STRG", "SSTR")
        if is_numeric(b.ddic) and (a.ddic or "").upper() in charlike and a.kind != "lit":
            a = a.combine(sql=f"COALESCE(TRY_TO_NUMBER({a.sql}), 0)", kind="expr", ddic="DEC")
            return a, b
        if is_numeric(a.ddic) and (b.ddic or "").upper() in charlike and b.kind != "lit":
            b = b.combine(sql=f"COALESCE(TRY_TO_NUMBER({b.sql}), 0)", kind="expr", ddic="DEC")
            return a, b
        return guard(a, b), guard(b, a)

    @staticmethod
    def _cp_pattern(b: SqlExpr) -> str:
        if b.kind == "lit" and b.sql.startswith("'"):
            body = b.sql[1:-1]
            out = []
            i = 0
            while i < len(body):
                ch = body[i]
                if ch == "#" and i + 1 < len(body):
                    nxt = body[i + 1]
                    out.append("\\\\" + nxt if nxt in "%_" else nxt)
                    i += 2
                    continue
                out.append({"*": "%", "+": "_", "%": "\\\\%", "_": "\\\\_"}.get(ch, ch))
                i += 1
            return "'" + "".join(out) + "'"
        return f"REPLACE(REPLACE({b.sql}, '*', '%'), '+', '_')"


def _flip(op: str) -> str:
    return {"<": ">", ">": "<", "<=": ">=", ">=": "<="}.get(op, op)
