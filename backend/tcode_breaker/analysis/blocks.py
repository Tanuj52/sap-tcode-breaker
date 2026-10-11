"""Control-structure tree and routine (event / FORM / method / FM) segmentation."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..parser.ast import Statement

EVENTS = {
    "LoadOfProgram": "LOAD-OF-PROGRAM",
    "Initialization": "INITIALIZATION",
    "AtSelectionScreen": "AT SELECTION-SCREEN",
    "StartOfSelection": "START-OF-SELECTION",
    "EndOfSelection": "END-OF-SELECTION",
    "TopOfPage": "TOP-OF-PAGE",
    "EndOfPage": "END-OF-PAGE",
    "AtLineSelection": "AT LINE-SELECTION",
    "AtUserCommand": "AT USER-COMMAND",
    "AtPF": "AT PF",
}

# Events that run as part of a normal report execution, in order.
RUN_ORDER = ["LOAD-OF-PROGRAM", "INITIALIZATION", "AT SELECTION-SCREEN", "START-OF-SELECTION", "END-OF-SELECTION"]

DECLARATIONS = {
    "Report", "Program", "FunctionPool", "Tables", "Data", "DataBegin", "DataEnd", "Type", "TypeBegin", "TypeEnd",
    "TypeEnum", "TypeEnumBegin", "TypeEnumEnd", "Constant", "ConstantBegin", "ConstantEnd", "Static", "StaticBegin",
    "StaticEnd", "FieldSymbol", "Parameter", "SelectOption", "SelectionScreen", "Ranges", "TypePools", "TypePool",
    "Include", "IncludeType", "ClassData", "ClassDataBegin", "ClassDataEnd", "Comment", "Empty", "FormDefinition",
    "ClassDeferred", "InterfaceDeferred", "ClassDefinitionLoad", "InterfaceLoad", "MethodDef", "InterfaceDef",
}

OPENERS = {
    "If": "EndIf",
    "Case": "EndCase",
    "CaseType": "EndCase",
    "Loop": "EndLoop",
    "LoopAtScreen": "EndLoop",
    "LoopExtract": "EndLoop",
    "Do": "EndDo",
    "While": "EndWhile",
    "SelectLoop": "EndSelect",
    "Try": "EndTry",
    "At": "EndAt",
    "AtFirst": "EndAt",
    "AtLast": "EndAt",
    "OnChange": "EndOn",
    "Provide": "EndProvide",
    "CatchSystemExceptions": "EndCatch",
    "With": "EndWith",
}
BRANCHES = {
    "If": {"ElseIf", "Else"},
    "Case": {"When", "WhenOthers"},
    "CaseType": {"WhenType", "WhenOthers"},
    "Try": {"Catch", "Cleanup"},
    "OnChange": {"Else"},
}


@dataclass
class Branch:
    header: Statement | None
    items: list["Item"] = field(default_factory=list)


@dataclass
class Control:
    type: str
    header: Statement
    branches: list[Branch]
    end: Statement | None = None

    @property
    def first_row(self) -> int:
        return self.header.row

    @property
    def last_row(self) -> int:
        return (self.end or self.header).end_row


Item = Statement | Control


@dataclass
class Routine:
    name: str
    kind: str  # event | form | method | function_module | module | main
    header: Statement | None
    end: Statement | None
    items: list[Item] = field(default_factory=list)
    statements: list[Statement] = field(default_factory=list)
    params: dict[str, list[str]] = field(default_factory=dict)  # USING / CHANGING / TABLES -> names


@dataclass
class ProgramStructure:
    routines: dict[str, Routine]
    global_decls: list[Statement]
    issues: list[str] = field(default_factory=list)
    method_defs: dict[str, Statement] = field(default_factory=dict)  # "CLASS=>METH" -> METHODS declaration

    def run_order(self) -> list[Routine]:
        return [self.routines[e] for e in RUN_ORDER if e in self.routines]


def _build_items(stmts: list[Statement], start: int, stop_types: set[str], issues: list[str]) -> tuple[list[Item], int]:
    """Build nested items from stmts[start:], stopping at a statement whose type is in stop_types.

    Returns (items, index_of_stop_statement_or_len).
    """
    items: list[Item] = []
    i = start
    while i < len(stmts):
        s = stmts[i]
        if s.type in stop_types:
            return items, i
        if s.type in OPENERS:
            closer = OPENERS[s.type]
            branch_types = BRANCHES.get(s.type, set())
            ctl = Control(type=s.type, header=s, branches=[Branch(header=s)])
            j = i + 1
            while True:
                sub_items, j = _build_items(stmts, j, branch_types | {closer}, issues)
                ctl.branches[-1].items.extend(sub_items)
                if j >= len(stmts):
                    issues.append(f"Unclosed {s.type} at line {s.row}")
                    break
                nxt = stmts[j]
                if nxt.type == closer:
                    ctl.end = nxt
                    j += 1
                    break
                ctl.branches.append(Branch(header=nxt))
                j += 1
            # CASE: statements between CASE and first WHEN are not executable; drop the empty leading branch
            if s.type in ("Case", "CaseType") and len(ctl.branches) > 1 and not ctl.branches[0].items:
                ctl.branches = ctl.branches[1:]
            items.append(ctl)
            i = j
            continue
        items.append(s)
        i += 1
    return items, i


def _flatten(items: list[Item]) -> list[Statement]:
    out: list[Statement] = []
    for it in items:
        if isinstance(it, Control):
            out.append(it.header)
            for b in it.branches:
                if b.header is not None and b.header is not it.header:
                    out.append(b.header)
                out.extend(_flatten(b.items))
            if it.end is not None:
                out.append(it.end)
        else:
            out.append(it)
    return out


def _form_params(s: Statement) -> dict[str, list[str]]:
    toks = s.tokens()
    params: dict[str, list[str]] = {}
    current = None
    skip_next = False
    for t in toks[2:]:
        u = t.upper()
        if u in ("USING", "CHANGING", "TABLES", "RAISING"):
            current = u
            params.setdefault(u, [])
            continue
        if skip_next:
            skip_next = False
            continue
        if u in ("TYPE", "LIKE", "STRUCTURE"):
            skip_next = True
            continue
        if u in ("VALUE", "(", ")", ".", "REF", "TO", "STANDARD", "TABLE", "ANY", "OPTIONAL"):
            continue
        if current and current != "RAISING" and t not in ("-",):
            params[current].append(u)
    return params


def build_structure(stmts: list[Statement]) -> ProgramStructure:
    issues: list[str] = []
    routines: dict[str, Routine] = {}
    global_decls: list[Statement] = []
    method_defs: dict[str, Statement] = {}
    implicit: list[Statement] = []
    i = 0
    current_event: Routine | None = None
    current_class: str | None = None

    def add_routine(r: Routine) -> Routine:
        if r.name in routines:
            existing = routines[r.name]
            existing.statements.extend(r.statements)
            return existing
        routines[r.name] = r
        return r

    pending_event_stmts: list[Statement] = []

    def close_event() -> None:
        nonlocal pending_event_stmts, current_event
        if current_event is not None:
            items, _ = _build_items(pending_event_stmts, 0, set(), issues)
            current_event.items.extend(items)
            current_event.statements.extend(pending_event_stmts)
        pending_event_stmts = []

    while i < len(stmts):
        s = stmts[i]
        t = s.type
        if t in ("Form", "FunctionModule", "MethodImplementation", "Module"):
            close_event()
            current_event = None
            closer = {"Form": "EndForm", "FunctionModule": "EndFunction", "MethodImplementation": "EndMethod", "Module": "EndModule"}[t]
            j = i + 1
            while j < len(stmts) and stmts[j].type != closer:
                j += 1
            body = stmts[i + 1 : j]
            toks = s.tokens()
            raw_name = toks[1] if len(toks) > 1 else f"anon_{s.row}"
            if t == "MethodImplementation":
                name = f"{(current_class or '').upper()}=>{raw_name.upper()}" if current_class else raw_name.upper()
                kind = "method"
            elif t == "FunctionModule":
                name, kind = raw_name.upper(), "function_module"
            elif t == "Module":
                name, kind = raw_name.upper(), "module"
            else:
                name, kind = raw_name.upper(), "form"
            items, _ = _build_items(body, 0, set(), issues)
            r = Routine(name=name, kind=kind, header=s, end=stmts[j] if j < len(stmts) else None, items=items, statements=body)
            if t == "Form":
                r.params = _form_params(s)
            if j >= len(stmts):
                issues.append(f"Unclosed {t} {name} at line {s.row}")
            add_routine(r)
            i = j + 1
            continue
        if t == "ClassImplementation":
            toks = [x for x in s.tokens() if x.upper() not in ("CLASS",)]
            current_class = toks[0].upper() if toks else None
            i += 1
            continue
        if t == "EndClass":
            current_class = None
            i += 1
            continue
        if t in ("ClassDefinition", "Interface"):
            closer = "EndClass" if t == "ClassDefinition" else "EndInterface"
            dtoks = [x for x in s.tokens() if x.upper() not in ("CLASS", "INTERFACE")]
            owner = dtoks[0].upper().rstrip(".") if dtoks else "?"
            j = i + 1
            while j < len(stmts) and stmts[j].type != closer:
                global_decls.append(stmts[j])
                if stmts[j].type == "MethodDef":
                    mt = [x for x in stmts[j].tokens() if x not in (":", ",")]
                    if len(mt) > 1:
                        method_defs[f"{owner}=>{mt[1].upper()}"] = stmts[j]
                j += 1
            i = j + 1
            continue
        if t == "Define":
            while i < len(stmts) and stmts[i].type != "EndOfDefinition":
                i += 1
            i += 1
            continue
        if t in EVENTS:
            close_event()
            name = EVENTS[t]
            current_event = routines.get(name) or add_routine(Routine(name=name, kind="event", header=s, end=None))
            i += 1
            continue
        if t in DECLARATIONS and current_event is None:
            global_decls.append(s)
            i += 1
            continue
        if current_event is None:
            implicit.append(s)
        else:
            pending_event_stmts.append(s)
        i += 1
    close_event()

    if implicit:
        items, _ = _build_items(implicit, 0, set(), issues)
        sos = routines.get("START-OF-SELECTION")
        if sos is None:
            routines["START-OF-SELECTION"] = Routine(name="START-OF-SELECTION", kind="event", header=None, end=None, items=items, statements=implicit)
        else:
            sos.items = items + sos.items
            sos.statements = implicit + sos.statements

    # annotate statements with routine names
    for r in routines.values():
        for st in _flatten(r.items) if r.items else r.statements:
            st.routine = r.name
    return ProgramStructure(routines=routines, global_decls=global_decls, issues=issues, method_defs=method_defs)


def flatten(items: list[Item]) -> list[Statement]:
    return _flatten(items)
