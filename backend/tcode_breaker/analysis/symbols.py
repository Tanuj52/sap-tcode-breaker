"""Symbol table: TYPES, DATA, TABLES, FIELD-SYMBOLS, CONSTANTS and the selection screen."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..knowledge.kb import KnowledgeBase
from ..knowledge.models import FieldStatus, Provenance
from ..parser.ast import Statement
from .blocks import ProgramStructure, Routine

_TOKEN = re.compile(r"'(?:[^']|'')*'|`(?:[^`]|``)*`|\|[^|]*\||\S+")
_LEN_PAREN = re.compile(r"^([A-Za-z0-9_/<>]+)\((\d+)\)$")

ELEMENTARY_DEFAULT_LEN = {"CHAR": 1, "NUMC": 1, "DATS": 8, "TIMS": 6, "INT4": 10, "DEC": 8, "FLTP": 16, "STRG": 0, "RAW": 1}


@dataclass
class Comp:
    name: str
    ddic_type: str | None = None
    length: int | None = None
    decimals: int | None = None
    source_table: str | None = None
    source_field: str | None = None
    provenance: Provenance = Provenance.UNRESOLVED
    description: str = ""
    type_name: str | None = None

    def copy(self, name: str | None = None) -> "Comp":
        return Comp(name or self.name, self.ddic_type, self.length, self.decimals, self.source_table, self.source_field,
                    self.provenance, self.description, self.type_name)

    @property
    def is_numeric(self) -> bool:
        return (self.ddic_type or "").upper() in {"INT1", "INT2", "INT4", "INT8", "DEC", "CURR", "QUAN", "FLTP", "D16N", "PREC"}

    @property
    def is_charlike(self) -> bool:
        return not self.is_numeric


@dataclass
class TypeDef:
    name: str
    kind: str  # struct | table | elem | ref | unknown
    comps: list[Comp] = field(default_factory=list)
    row: "TypeDef | None" = None
    elem: Comp | None = None
    table_kind: str | None = None  # STANDARD | SORTED | HASHED | RANGE
    unique_key: list[str] = field(default_factory=list)
    provenance: Provenance = Provenance.UNRESOLVED
    db_table: str | None = None

    def columns(self) -> list[Comp]:
        if self.kind == "struct":
            return self.comps
        if self.kind == "table" and self.row is not None:
            return self.row.columns() if self.row.kind == "struct" else ([self.row.elem.copy("TABLE_LINE")] if self.row.elem else [])
        return []

    def comp(self, name: str) -> Comp | None:
        n = name.upper()
        for c in self.columns():
            if c.name == n:
                return c
        return None


@dataclass
class Var:
    name: str
    kind: str  # internal_table | structure | scalar | field_symbol | reference | range | constant | tables_wa
    type: TypeDef
    scope: str = "global"
    stmt: Statement | None = None
    inline: bool = False
    value: str | None = None
    header_line: bool = False

    @property
    def is_table(self) -> bool:
        return self.type.kind == "table"


@dataclass
class Param:
    name: str
    kind: str  # parameter | select_option | checkbox | radiobutton
    ref: str | None
    comp: Comp
    default: str | None = None
    obligatory: bool = False
    no_intervals: bool = False
    stmt: Statement | None = None
    group: str | None = None


def tokenize(text: str) -> list[str]:
    text = text.strip()
    if text.endswith((".", ",")):
        text = text[:-1]
    return _TOKEN.findall(text)


class Symbols:
    def __init__(self, kb: KnowledgeBase) -> None:
        self.kb = kb
        self.types: dict[tuple[str, str], TypeDef] = {}
        self.vars: dict[tuple[str, str], Var] = {}
        self.params: dict[str, Param] = {}
        self.issues: list[tuple[str, str, Statement | None]] = []  # (severity, message, stmt)
        self.db_type_refs: dict[str, set[str]] = {}  # table -> fields referenced via TYPE tab-field

    # ------------------------------------------------------------------ public lookups
    def var(self, name: str, scope: str = "global") -> Var | None:
        n = name.upper()
        return self.vars.get((scope, n)) or self.vars.get(("global", n))

    def type(self, name: str, scope: str = "global") -> TypeDef | None:
        n = name.upper()
        return self.types.get((scope, n)) or self.types.get(("global", n))

    def declare(self, var: Var) -> None:
        self.vars[(var.scope, var.name.upper())] = var

    # ------------------------------------------------------------------ type resolution
    def db_struct(self, table: str) -> TypeDef | None:
        info = self.kb.table(table)
        if info is None:
            return None
        comps = [
            Comp(f.name, f.ddic_type, f.length, f.decimals, info.name, f.name, f.source, f.description)
            for f in info.fields.values()
        ]
        return TypeDef(name=info.name, kind="struct", comps=comps, provenance=info.source, db_table=info.name)

    def elem_from_ref(self, ref: str, scope: str) -> Comp:
        """Resolve 'table-field', builtin types, constants-like names to an elementary component."""
        r = ref.upper()
        if "-" in r and not r.startswith("<"):
            head, _, tail = r.partition("-")
            # var-component (LIKE gs-comp) or table-field (TYPE scarr-carrid)
            v = self.var(head, scope)
            if v is not None and v.type.kind in ("struct", "table"):
                c = v.type.comp(tail)
                if c is not None:
                    return c.copy()
            local = self.type(head, scope)
            if local is not None and local.kind == "struct":
                c = local.comp(tail)
                if c is not None:
                    return c.copy()
            finfo, status = self.kb.field(head, tail)
            self.db_type_refs.setdefault(head, set()).add(tail)
            if finfo is not None:
                return Comp(tail, finfo.ddic_type, finfo.length, finfo.decimals, head, tail, finfo.source, finfo.description, r)
            prov = Provenance.INFERRED if status in (FieldStatus.UNVERIFIED, FieldStatus.NO_TABLE) else Provenance.UNRESOLVED
            return Comp(tail, None, None, None, head, tail, prov, "", r)
        builtin = self.kb.abap_types.get(r.lower())
        if builtin is not None:
            ddic = builtin.get("ddic")
            return Comp("", ddic, builtin.get("len"), builtin.get("dec"), None, None, Provenance.BUILTIN, "", r)
        local = self.type(r, scope)
        if local is not None and local.kind == "elem" and local.elem is not None:
            return local.elem.copy()
        return Comp("", None, None, None, None, None, Provenance.UNRESOLVED, "", r)

    def resolve(self, words: list[str], scope: str) -> TypeDef:
        """Resolve the part of a declaration after the name, e.g. ['TYPE','STANDARD','TABLE','OF','TY_OUT', ...]."""
        w = [x.upper() for x in words]
        if not w:
            return TypeDef("C", "elem", elem=Comp("", "CHAR", 1, None, provenance=Provenance.BUILTIN))
        mode = w[0]
        rest = w[1:]
        if mode not in ("TYPE", "LIKE"):
            # old-style "DATA lv(10)." or no type at all
            return TypeDef("C", "elem", elem=Comp("", "CHAR", 1, None, provenance=Provenance.BUILTIN))

        if rest[:2] == ["REF", "TO"]:
            return TypeDef(rest[2] if len(rest) > 2 else "?", "ref")

        if rest[:2] == ["LINE", "OF"] and len(rest) > 2:
            base = self._resolve_name(rest[2], mode, scope)
            return base.row if base.kind == "table" and base.row else base

        if rest[:2] == ["RANGE", "OF"] and len(rest) > 2:
            elem = self._resolve_name(rest[2], mode, scope)
            ec = elem.elem or Comp("")
            row = TypeDef("RANGE", "struct", comps=[
                Comp("SIGN", "CHAR", 1, provenance=Provenance.BUILTIN), Comp("OPTION", "CHAR", 2, provenance=Provenance.BUILTIN),
                ec.copy("LOW"), ec.copy("HIGH")])
            return TypeDef("RANGE", "table", row=row, table_kind="RANGE")

        table_kind = None
        idx = 0
        if rest and rest[0] in ("STANDARD", "SORTED", "HASHED", "ANY", "INDEX"):
            table_kind = rest[0]
            idx = 1
        if idx < len(rest) and rest[idx] == "TABLE" and idx + 1 < len(rest) and rest[idx + 1] == "OF":
            row = self._resolve_name(rest[idx + 2], mode, scope) if idx + 2 < len(rest) else TypeDef("?", "unknown")
            if mode == "LIKE" and row.kind == "table" and row.row is not None:
                row = row.row
            unique_key = []
            if "UNIQUE" in rest and "KEY" in rest:
                k = rest.index("KEY", rest.index("UNIQUE")) + 1
                while k < len(rest) and rest[k] not in ("WITH", "INITIAL", "OCCURS", "NON-UNIQUE", "VALUE"):
                    unique_key.append(rest[k])
                    k += 1
            return TypeDef(row.name, "table", row=row, table_kind=table_kind or "STANDARD", unique_key=unique_key, provenance=row.provenance)
        if rest and rest[0] == "TABLE" and len(rest) == 1:
            return TypeDef("?", "table", row=TypeDef("?", "unknown"), table_kind="STANDARD")

        if not rest:
            return TypeDef("?", "unknown")
        base = self._resolve_name(rest[0], mode, scope)
        if base.kind == "elem" and base.elem is not None:
            elem = base.elem.copy()
            if "LENGTH" in rest:
                try:
                    elem.length = int(rest[rest.index("LENGTH") + 1].strip("'"))
                except (ValueError, IndexError):
                    pass
            if "DECIMALS" in rest:
                try:
                    elem.decimals = int(rest[rest.index("DECIMALS") + 1])
                except (ValueError, IndexError):
                    pass
            elif elem.ddic_type == "DEC" and elem.decimals is None and elem.type_name in ("P",):
                elem.decimals = 0
            return TypeDef(base.name, "elem", elem=elem, provenance=elem.provenance)
        return base

    def _resolve_name(self, name: str, mode: str, scope: str) -> TypeDef:
        n = name.upper()
        if mode == "LIKE":
            v = self.var(n, scope)
            if v is not None:
                return v.type
            if "-" in n:
                c = self.elem_from_ref(n, scope)
                return TypeDef(n, "elem", elem=c, provenance=c.provenance)
        local = self.type(n, scope)
        if local is not None:
            return local
        if "-" not in n:
            db = self.db_struct(n)
            if db is not None:
                return db
        c = self.elem_from_ref(n, scope)
        if c.provenance == Provenance.UNRESOLVED and "-" not in n:
            # Unknown data element / DDIC structure / table type
            return TypeDef(n, "elem", elem=c, provenance=Provenance.UNRESOLVED)
        return TypeDef(n, "elem", elem=c, provenance=c.provenance)

    # ------------------------------------------------------------------ declaration processing
    def load(self, structure: ProgramStructure) -> None:
        self._process(structure.global_decls, "global")
        for r in structure.routines.values():
            scope = r.name if r.kind in ("form", "method", "function_module", "module") else "global"
            self._process(r.statements, scope)
            if r.kind == "form":
                self._declare_form_params(r)
            elif r.kind == "method":
                d = method_def(structure, r.name)
                if d is not None:
                    self._declare_method_params(r, d)

    def _declare_form_params(self, r: Routine) -> None:
        if r.header is None:
            return
        toks = tokenize(r.header.text)
        current = None
        i = 2
        while i < len(toks):
            u = toks[i].upper()
            if u in ("USING", "CHANGING", "TABLES", "RAISING"):
                current = u
                i += 1
                continue
            if current in ("USING", "CHANGING", "TABLES"):
                name = u
                m = re.match(r"VALUE\((.+)\)", name)
                if m:
                    name = m.group(1)
                type_words: list[str] = []
                j = i + 1
                if j < len(toks) and toks[j].upper() in ("TYPE", "LIKE", "STRUCTURE"):
                    kw = toks[j].upper()
                    type_words = ["TYPE" if kw == "STRUCTURE" else kw]
                    j += 1
                    while j < len(toks) and toks[j].upper() not in ("USING", "CHANGING", "TABLES", "RAISING") and (
                        len(type_words) < 2 or toks[j].upper() in ("TABLE", "OF", "STANDARD", "SORTED", "HASHED", "REF", "TO")
                        or type_words[-1].upper() in ("OF", "TO", "TABLE", "STANDARD", "SORTED", "HASHED", "REF", "TYPE", "LIKE")
                    ):
                        type_words.append(toks[j])
                        j += 1
                td = self.resolve(type_words, "global") if type_words else TypeDef("?", "unknown")
                if current == "TABLES" and td.kind != "table":
                    td = TypeDef(td.name, "table", row=td, table_kind="STANDARD")
                kind = "internal_table" if td.kind == "table" else ("structure" if td.kind == "struct" else "scalar")
                self.declare(Var(name, kind, td, scope=r.name, stmt=r.header))
                i = j
                continue
            i += 1

    def _declare_method_params(self, r: Routine, d: Statement) -> None:
        """METHODS m IMPORTING a TYPE t [OPTIONAL] EXPORTING ... CHANGING ... RETURNING VALUE(r) TYPE t."""
        toks = [t for t in tokenize(d.text) if t not in (":", ",")]
        sections = ("IMPORTING", "EXPORTING", "CHANGING", "RETURNING", "RAISING", "EXCEPTIONS")
        type_kw = {"TABLE", "OF", "STANDARD", "SORTED", "HASHED", "REF", "TO", "RANGE", "LINE", "ANY", "INDEX", "WITH",
                   "DEFAULT", "KEY", "EMPTY", "NON-UNIQUE", "UNIQUE"}
        params: dict[str, list[str]] = {}
        current = None
        i = 2
        while i < len(toks):
            u = toks[i].upper()
            if u in sections:
                current = u
                params.setdefault(u, [])
                i += 1
                continue
            if current in ("IMPORTING", "EXPORTING", "CHANGING", "RETURNING") and u not in ("OPTIONAL", "PREFERRED", "PARAMETER"):
                m = re.match(r"(?:VALUE|REFERENCE)\((.+)\)", toks[i], re.IGNORECASE)
                name = (m.group(1) if m else toks[i]).upper()
                type_words: list[str] = []
                j = i + 1
                if j < len(toks) and toks[j].upper() in ("TYPE", "LIKE"):
                    type_words = [toks[j].upper()]
                    j += 1
                    while j < len(toks):
                        w = toks[j].upper()
                        if w in type_kw or type_words[-1] in ("TYPE", "LIKE", "OF", "TO"):
                            if w == "DEFAULT":
                                j += 2
                                break
                            type_words.append(toks[j])
                            j += 1
                            continue
                        break
                td = self.resolve([w for w in type_words if w.upper() not in ("WITH", "DEFAULT", "KEY", "EMPTY")], "global") \
                    if type_words else TypeDef("?", "unknown")
                kind = "internal_table" if td.kind == "table" else ("structure" if td.kind == "struct" else "scalar")
                self.declare(Var(name, kind, td, scope=r.name, stmt=d))
                params[current].append(name)
                i = j
                continue
            i += 1
        r.params = params

    def _process(self, stmts: list[Statement], scope: str) -> None:
        struct_stack: list[tuple[str, str, list[Comp], Statement, bool]] = []  # (kind TYPES|DATA, name, comps, stmt, occurs)
        for s in stmts:
            t = s.type
            toks = tokenize(s.text)
            if not toks:
                continue
            try:
                if t in ("TypeBegin", "DataBegin", "StaticBegin", "ClassDataBegin", "ConstantBegin"):
                    # TYPES BEGIN OF name [OCCURS n]
                    name = toks[3] if len(toks) > 3 and toks[1].upper() == "BEGIN" else toks[-1]
                    occurs = "OCCURS" in [x.upper() for x in toks]
                    struct_stack.append(("TYPES" if t == "TypeBegin" else "DATA", name.upper(), [], s, occurs))
                elif t in ("TypeEnd", "DataEnd", "StaticEnd", "ClassDataEnd", "ConstantEnd"):
                    if not struct_stack:
                        continue
                    kind, name, comps, start, occurs = struct_stack.pop()
                    td = TypeDef(name, "struct", comps=comps, provenance=_merge_prov(comps))
                    if struct_stack:
                        # nested structure: flatten into parent with prefix (rare in reports)
                        parent = struct_stack[-1]
                        for c in comps:
                            parent[2].append(c.copy(f"{name}-{c.name}"))
                        self.issues.append(("info", f"Nested structure {name} flattened", s))
                    elif kind == "TYPES":
                        self.types[(scope, name)] = td
                    else:
                        if occurs:
                            tab = TypeDef(name, "table", row=td, table_kind="STANDARD")
                            self.declare(Var(name, "internal_table", tab, scope, start, header_line=True))
                        else:
                            self.declare(Var(name, "structure", td, scope, start))
                elif t in ("Type", "Data", "Static", "ClassData", "Constant") and struct_stack:
                    if len(toks) >= 2 and toks[1].upper() == "INCLUDE":
                        inc = self.resolve(["TYPE", toks[3]] if len(toks) > 3 else [], scope)
                        struct_stack[-1][2].extend(c.copy() for c in inc.columns())
                        continue
                    name, type_words = _split_decl(toks)
                    td = self.resolve(type_words, scope)
                    struct_stack[-1][2].append(_as_comp(name, td))
                elif t in ("IncludeType",) and struct_stack:
                    inc = self.resolve(["TYPE", toks[-1]], scope)
                    struct_stack[-1][2].extend(c.copy() for c in inc.columns())
                elif t == "Type":
                    name, type_words = _split_decl(toks)
                    td = self.resolve(type_words, scope)
                    td = TypeDef(name, td.kind, td.comps, td.row, td.elem, td.table_kind, td.unique_key, td.provenance, td.db_table)
                    self.types[(scope, name)] = td
                elif t in ("Data", "Static", "ClassData"):
                    name, type_words = _split_decl(toks)
                    td = self.resolve(type_words, scope)
                    words_u = [w.upper() for w in type_words]
                    header = "HEADER" in words_u and "LINE" in words_u
                    self.declare(Var(name, _var_kind(td), td, scope, s, header_line=header))
                elif t == "Constant":
                    name, type_words = _split_decl(toks)
                    td = self.resolve(type_words, scope)
                    value = None
                    words_u = [w.upper() for w in type_words]
                    if "VALUE" in words_u:
                        value = type_words[words_u.index("VALUE") + 1]
                    self.declare(Var(name, "constant", td, scope, s, value=value))
                elif t == "Tables":
                    for tab in toks[1:]:
                        if tab in (",",):
                            continue
                        td = self.db_struct(tab) or TypeDef(tab.upper(), "struct")
                        self.declare(Var(tab.upper(), "tables_wa", td, "global", s))
                elif t == "FieldSymbol":
                    name, type_words = _split_decl(toks)
                    td = self.resolve(type_words, scope) if type_words else TypeDef("ANY", "unknown")
                    self.declare(Var(name, "field_symbol", td, scope, s))
                elif t == "Ranges":
                    # RANGES r_x FOR tab-field
                    name = toks[1].upper()
                    td = self.resolve(["TYPE", "RANGE", "OF", toks[3]] if len(toks) > 3 else [], scope)
                    self.declare(Var(name, "range", td, scope, s))
                elif t == "Parameter":
                    self._param(toks, s, scope)
                elif t == "SelectOption":
                    self._select_option(toks, s, scope)
            except Exception as exc:  # noqa: BLE001 - never fail the whole analysis on one declaration
                self.issues.append(("warning", f"Could not interpret declaration: {exc}", s))

    def _param(self, toks: list[str], s: Statement, scope: str) -> None:
        name = toks[1].upper()
        m = _LEN_PAREN.match(toks[1])
        if m:
            name = m.group(1).upper()
        words = [w.upper() for w in toks[2:]]
        kind = "parameter"
        comp: Comp
        ref = None
        if "AS" in words and "CHECKBOX" in words:
            kind = "checkbox"
            comp = Comp(name, "CHAR", 1, provenance=Provenance.BUILTIN)
        elif "RADIOBUTTON" in words:
            kind = "radiobutton"
            comp = Comp(name, "CHAR", 1, provenance=Provenance.BUILTIN)
        else:
            if "TYPE" in words or "LIKE" in words:
                k = words.index("TYPE") if "TYPE" in words else words.index("LIKE")
                ref = toks[2 + k + 1].upper() if 2 + k + 1 < len(toks) else None
                tw = [words[k], ref] if ref else []
                for extra in ("LENGTH", "DECIMALS"):
                    if extra in words:
                        tw += [extra, words[words.index(extra) + 1]]
                td = self.resolve(tw, scope)
                comp = (td.elem.copy(name) if td.elem else Comp(name))
            else:
                comp = Comp(name, "CHAR", int(m.group(2)) if m else 8, provenance=Provenance.BUILTIN)
        default = None
        if "DEFAULT" in words:
            default = toks[2 + words.index("DEFAULT") + 1]
        group = toks[2 + words.index("GROUP") + 1].upper() if "GROUP" in words else None
        comp.name = name
        self.params[name] = Param(name, kind, ref, comp, default, "OBLIGATORY" in words, False, s, group)
        td = TypeDef(name, "elem", elem=comp, provenance=comp.provenance)
        self.declare(Var(name, "scalar", td, "global", s))

    def _select_option(self, toks: list[str], s: Statement, scope: str) -> None:
        name = toks[1].upper()
        words = [w.upper() for w in toks[2:]]
        ref = toks[2 + words.index("FOR") + 1].upper() if "FOR" in words else None
        if ref and "-" not in ref:
            v = self.var(ref, scope)
            comp = v.type.elem.copy(name) if v is not None and v.type.elem else Comp(name)
        else:
            comp = self.elem_from_ref(ref, scope).copy(name) if ref else Comp(name)
        default = toks[2 + words.index("DEFAULT") + 1] if "DEFAULT" in words else None
        self.params[name] = Param(name, "select_option", ref, comp, default, "OBLIGATORY" in words, "NO" in words and "INTERVALS" in words, s)
        row = TypeDef("RANGE", "struct", comps=[
            Comp("SIGN", "CHAR", 1, provenance=Provenance.BUILTIN), Comp("OPTION", "CHAR", 2, provenance=Provenance.BUILTIN),
            comp.copy("LOW"), comp.copy("HIGH")])
        self.declare(Var(name, "range", TypeDef("RANGE", "table", row=row, table_kind="RANGE"), "global", s, header_line=True))


def method_def(structure: ProgramStructure, routine: str) -> Statement | None:
    """Find the METHODS declaration of an implemented method ("CLS=>METH" or "CLS=>INTF~METH")."""
    d = structure.method_defs.get(routine)
    if d is None and "~" in routine:
        intf, _, meth = routine.split("=>", 1)[-1].partition("~")
        d = structure.method_defs.get(f"{intf}=>{meth}")
    return d


def _split_decl(toks: list[str]) -> tuple[str, list[str]]:
    """'DATA gt_out TYPE STANDARD TABLE OF ty_out' -> ('GT_OUT', ['TYPE', 'STANDARD', ...])."""
    raw_name = toks[1] if len(toks) > 1 else "?"
    m = _LEN_PAREN.match(raw_name)
    words = toks[2:]
    if m:
        raw_name = m.group(1)
        if not words or words[0].upper() not in ("TYPE", "LIKE"):
            words = ["TYPE", "C"] + words
        words = words + ["LENGTH", m.group(2)]
    return raw_name.upper(), words


def _as_comp(name: str, td: TypeDef) -> Comp:
    if td.kind == "elem" and td.elem is not None:
        return td.elem.copy(name)
    return Comp(name, None, None, None, None, None, td.provenance, "", td.name)


def _var_kind(td: TypeDef) -> str:
    if td.kind == "table":
        return "range" if td.table_kind == "RANGE" else "internal_table"
    if td.kind == "struct":
        return "structure"
    if td.kind == "ref":
        return "reference"
    return "scalar"


def _merge_prov(comps: list[Comp]) -> Provenance:
    if not comps:
        return Provenance.UNRESOLVED
    if all(c.provenance in (Provenance.BUILTIN, Provenance.CLIENT_PACK, Provenance.LIBRARY) for c in comps):
        return Provenance.BUILTIN
    if any(c.provenance == Provenance.UNRESOLVED for c in comps):
        return Provenance.INFERRED
    return Provenance.INFERRED
