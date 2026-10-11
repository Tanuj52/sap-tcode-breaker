"""Source ingestion: classify uploaded files, inline INCLUDEs, keep a line map.

The flattened program is what the parser sees; `line_map[i]` gives the original
(file, line) of flat line i+1, so every finding and graph node can point back
to the user's files.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import PurePath

_INCLUDE = re.compile(r"^\s*INCLUDE\s+([A-Za-z0-9_/]+)\s*(IF\s+FOUND\s*)?\.\s*(\".*)?$", re.IGNORECASE)
_PROGRAM_HEADER = re.compile(r"^\s*(REPORT|PROGRAM)\s+([A-Za-z0-9_/]+)", re.IGNORECASE | re.MULTILINE)
_FUNCTION_HEADER = re.compile(r"^\s*FUNCTION\s+([A-Za-z0-9_/]+)\s*\.", re.IGNORECASE | re.MULTILINE)
_FUNCTION_POOL = re.compile(r"^\s*FUNCTION-POOL\s+", re.IGNORECASE | re.MULTILINE)
_CLASS_POOL = re.compile(r"^\s*CLASS\s+\S+\s+DEFINITION\s+PUBLIC", re.IGNORECASE | re.MULTILINE)
_MAX_DEPTH = 20


@dataclass(frozen=True)
class SourceRef:
    file: str
    line: int


@dataclass
class SourceFile:
    name: str  # object name, upper case, without extension (e.g. ZSF07_TOP)
    filename: str  # as uploaded
    content: str
    kind: str = "unknown"  # program | include | function_module | class | unknown

    @property
    def line_count(self) -> int:
        return self.content.count("\n") + (0 if self.content.endswith("\n") or not self.content else 1)


@dataclass
class IngestIssue:
    severity: str
    code: str
    message: str
    ref: SourceRef | None = None


@dataclass
class FlatProgram:
    name: str
    text: str
    line_map: list[SourceRef]
    files: list[str]  # files that contributed, main first
    issues: list[IngestIssue] = field(default_factory=list)

    def ref(self, flat_row: int) -> SourceRef:
        if 1 <= flat_row <= len(self.line_map):
            return self.line_map[flat_row - 1]
        return SourceRef(self.name, flat_row)


@dataclass
class IngestResult:
    programs: list[FlatProgram]
    function_modules: dict[str, str]  # FM name -> source
    files: dict[str, SourceFile]
    issues: list[IngestIssue] = field(default_factory=list)


def object_name(filename: str) -> str:
    """'zsf07_top.prog.abap' -> 'ZSF07_TOP'."""
    base = PurePath(filename).name
    for suffix in (".prog.abap", ".fugr.abap", ".clas.abap", ".abap", ".txt", ".src"):
        if base.lower().endswith(suffix):
            base = base[: -len(suffix)]
            break
    return base.upper()


def _includes_in(content: str) -> list[str]:
    out = []
    for line in content.splitlines():
        m = _INCLUDE.match(line)
        if m:
            out.append(m.group(1).upper())
    return out


def classify(files: dict[str, str]) -> dict[str, SourceFile]:
    result: dict[str, SourceFile] = {}
    for filename, content in files.items():
        content = content.replace("\r\n", "\n").replace("\r", "\n").lstrip("\ufeff")
        sf = SourceFile(name=object_name(filename), filename=filename, content=content)
        if _FUNCTION_HEADER.search(content) and not _PROGRAM_HEADER.search(content):
            sf.kind = "function_module"
        elif _PROGRAM_HEADER.search(content):
            sf.kind = "program"
        elif _FUNCTION_POOL.search(content):
            sf.kind = "include"
        elif _CLASS_POOL.search(content):
            sf.kind = "class"
        result[sf.name] = sf

    referenced = {inc for sf in result.values() for inc in _includes_in(sf.content)}
    # Uploaded file names often differ from the object name ("pkg__zinc_top.abap", "ZINC_TOP (1).txt").
    # Re-key a file under the INCLUDE name that ends its file name, or under its REPORT name.
    for inc in referenced - set(result):
        hits = [sf for sf in result.values() if re.search(rf"(^|[^A-Z0-9]){re.escape(inc)}([^A-Z0-9_]|$)", sf.name)]
        if len(hits) == 1 and hits[0].name not in referenced:
            sf = result.pop(hits[0].name)
            sf.name = inc
            result[inc] = sf
    for key in list(result):
        sf = result[key]
        m = _PROGRAM_HEADER.search(sf.content)
        if m and m.group(2).upper() != sf.name and m.group(2).upper() not in result and sf.name not in referenced:
            result.pop(key)
            sf.name = m.group(2).upper()
            result[sf.name] = sf
    for sf in result.values():
        if sf.kind == "unknown" or (sf.kind == "program" and sf.name in referenced):
            sf.kind = "include" if sf.name in referenced or sf.kind == "unknown" else sf.kind
    return result


def ingest(files: dict[str, str], main: str | None = None) -> IngestResult:
    """Classify files and build one flattened program per main program."""
    classified = classify(files)
    issues: list[IngestIssue] = []

    fms: dict[str, str] = {}
    for sf in classified.values():
        if sf.kind == "function_module":
            for name in _FUNCTION_HEADER.findall(sf.content):
                fms[name.upper()] = sf.content

    if main and main.upper() == "ZTCB_CLASS_DRIVER" and main.upper() not in classified:
        classified["ZTCB_CLASS_DRIVER"] = class_driver([sf for sf in classified.values() if sf.kind == "class"])
    if main:
        mains = [classified[main.upper()]] if main.upper() in classified else []
        if not mains:
            issues.append(IngestIssue("error", "MAIN_NOT_FOUND", f"Main program {main} not among uploaded files"))
    else:
        mains = [sf for sf in classified.values() if sf.kind == "program"]
        if not mains and any(sf.kind == "class" for sf in classified.values()):
            # ABAP Objects / ABAP Cloud upload without a report: drive the classes from a synthetic program
            driver = class_driver([sf for sf in classified.values() if sf.kind == "class"])
            classified[driver.name] = driver
            mains = [driver]
            issues.append(IngestIssue("info", "CLASS_DRIVER", "No REPORT found; the class methods that read data are run in "
                                      "definition order from a generated driver program."))
        if not mains:
            # Fall back: a single file without header is treated as the program
            candidates = [sf for sf in classified.values() if sf.kind in ("include", "unknown")]
            referenced = {inc for sf in classified.values() for inc in _includes_in(sf.content)}
            roots = [sf for sf in candidates if sf.name not in referenced]
            if len(roots) > 1:
                with_inc = sorted((sf for sf in roots if _includes_in(sf.content)), key=lambda sf: -len(_includes_in(sf.content)))
                roots = with_inc[:1] or roots
            if len(roots) == 1:
                mains = roots
                issues.append(IngestIssue("warning", "NO_REPORT_STATEMENT", f"No REPORT/PROGRAM statement; treating {roots[0].name} as main program"))
            elif not classified or all(sf.kind == "function_module" for sf in classified.values()):
                pass
            else:
                issues.append(IngestIssue("error", "NO_MAIN_PROGRAM", "Could not determine the main program; specify it explicitly"))

    programs = [_flatten(sf, classified) for sf in mains]
    return IngestResult(programs=programs, function_modules=fms, files=classified, issues=issues)


_METHOD_IMPL = re.compile(r"^\s*METHOD\s+([A-Za-z0-9_~/]+)\s*\.(.*?)^\s*ENDMETHOD\s*\.", re.IGNORECASE | re.MULTILINE | re.DOTALL)
_CLASS_DEF = re.compile(r"^\s*CLASS\s+([A-Za-z0-9_/]+)\s+DEFINITION\b(.*?)^\s*ENDCLASS\s*\.", re.IGNORECASE | re.MULTILINE | re.DOTALL)
_METHOD_DECL = re.compile(r"\b(CLASS-METHODS|METHODS)\s*:?\s*([A-Za-z0-9_~/]+)(.*?)(?=\.)", re.IGNORECASE | re.DOTALL)


_IMPORTING = re.compile(r"\bIMPORTING\b(.*?)(?=\bEXPORTING\b|\bCHANGING\b|\bRETURNING\b|\bRAISING\b|\bEXCEPTIONS\b|$)", re.IGNORECASE | re.DOTALL)
_IMP_PARAM = re.compile(r"(?:VALUE\(\s*([A-Za-z0-9_]+)\s*\)|\b([A-Za-z0-9_]+))\s+TYPE\s+(?:REF\s+TO\s+)?([A-Za-z0-9_/\-]+)(\s+OPTIONAL|\s+DEFAULT\s+\S+)?", re.IGNORECASE)


def class_driver(classes: list[SourceFile]) -> SourceFile:
    """Build `REPORT` + class sources + START-OF-SELECTION calling the data-reading methods.

    Methods that contain a SELECT (or are the classrun entry point) are called in source order.
    Their IMPORTING parameters become selection-screen parameters, so they show up as runtime
    inputs of the SQL (the `params` CTE) instead of being lost.
    """
    head = ["REPORT ztcb_class_driver."]
    decls: list[str] = []
    calls: list[str] = []
    seen_params: set[str] = set()
    for sf in classes:
        head.append(f"INCLUDE {sf.name}.")
        for cm in _CLASS_DEF.finditer(sf.content):
            cls = cm.group(1).lower()
            sigs = {}
            for m in re.finditer(r"\b(CLASS-METHODS|METHODS)\b\s*:?(.*?)\.", cm.group(2), re.IGNORECASE | re.DOTALL):
                for part in _split_chain(m.group(2)):
                    words = part.split()
                    if words:
                        sigs[words[0].lower()] = (m.group(1).upper() == "CLASS-METHODS", part)
            inst = f"go_{cls}"[:30]
            inst_calls = []
            for mm in _METHOD_IMPL.finditer(sf.content):
                meth = mm.group(1).lower()
                body = mm.group(2)
                is_entry = meth.endswith("~main") or meth.endswith("~select")
                if not is_entry and not re.search(r"^\s*SELECT\b", body, re.IGNORECASE | re.MULTILINE):
                    continue
                if meth == "constructor" or ("~" in meth and not is_entry):
                    continue
                static, sig = sigs.get(meth, (False, ""))
                args = []
                imp = _IMPORTING.search(sig or "")
                for pm in _IMP_PARAM.finditer(imp.group(1) if imp else ""):
                    pname = (pm.group(1) or pm.group(2)).lower()
                    if pname.upper() in ("TYPE", "VALUE"):
                        continue
                    if pname not in seen_params:
                        seen_params.add(pname)
                        decls.append(f"PARAMETERS {pname} TYPE {pm.group(3).lower()}.")
                    args.append(f"{pname} = {pname}")
                call = f"( {' '.join(args)} )" if args else "( )"
                if static:
                    calls.append(f"  {cls}=>{meth}{call}.")
                else:
                    inst_calls.append(f"  {inst}->{meth}{call}.")
            if inst_calls:
                decls.append(f"DATA {inst} TYPE REF TO {cls}.")
                calls.append(f"  CREATE OBJECT {inst}.")
                calls.extend(inst_calls)
    lines = head + decls + ["START-OF-SELECTION."] + calls
    return SourceFile(name="ZTCB_CLASS_DRIVER", filename="ztcb_class_driver.abap", content="\n".join(lines) + "\n", kind="program")


def _flatten(main: SourceFile, files: dict[str, SourceFile]) -> FlatProgram:
    out_lines: list[str] = []
    line_map: list[SourceRef] = []
    used: list[str] = []
    issues: list[IngestIssue] = []

    def emit(text: str, ref: SourceRef) -> None:
        out_lines.append(text)
        line_map.append(ref)

    referenced = {inc for sf in files.values() for inc in _includes_in(sf.content)}
    mains = [sf for sf in files.values() if sf.kind == "program"] or [main]
    others = [m.name for m in mains if m.name != main.name]

    def mine(sf: SourceFile) -> bool:
        """Does an unreferenced include belong to this main program (vs. another uploaded program)?"""
        if not others:
            return True
        own = _common_prefix(sf.name, main.name)
        return own >= 3 and all(own >= _common_prefix(sf.name, o) for o in others)

    candidates = [sf for sf in files.values() if sf.name not in referenced and sf.kind in ("include", "unknown") and sf.name != main.name]

    def suffix_match(inc: str) -> SourceFile | None:
        hits = [sf for sf in candidates if sf.name not in used and _suffix(sf.name) == _suffix(inc) and mine(sf)]
        return hits[0] if len(hits) == 1 else None

    def walk(sf: SourceFile, stack: list[str]) -> None:
        if sf.name not in used:
            used.append(sf.name)
        for lineno, line in enumerate(sf.content.split("\n"), start=1):
            m = _INCLUDE.match(line)
            if not m:
                emit(line, SourceRef(sf.name, lineno))
                continue
            inc = m.group(1).upper()
            ref = SourceRef(sf.name, lineno)
            if inc in stack:
                issues.append(IngestIssue("error", "INCLUDE_CYCLE", f"Include cycle: {' -> '.join(stack + [inc])}", ref))
                emit(f"* tcb: include cycle {inc} skipped", ref)
            elif len(stack) >= _MAX_DEPTH:
                issues.append(IngestIssue("error", "INCLUDE_DEPTH", f"Include nesting deeper than {_MAX_DEPTH}", ref))
                emit(f"* tcb: include {inc} skipped (depth)", ref)
            elif inc in files:
                emit(f"* tcb: >>> include {inc}", ref)
                walk(files[inc], stack + [inc])
                emit(f"* tcb: <<< include {inc}", ref)
            elif _suffix(inc) and (alt := suffix_match(inc)) is not None:
                issues.append(IngestIssue("info", "INCLUDE_MATCHED", f"Include {inc} not uploaded under that name; using {alt.filename}", ref))
                emit(f"* tcb: >>> include {inc} = {alt.name}", ref)
                walk(alt, stack + [alt.name])
                emit(f"* tcb: <<< include {inc}", ref)
            else:
                severity = "info" if m.group(2) else "warning"
                issues.append(IngestIssue(severity, "INCLUDE_MISSING", f"Include {inc} was not uploaded", ref))
                emit(f"* tcb: include {inc} not provided", ref)

    walk(main, [main.name])
    # Files nobody INCLUDEs (renamed includes, exports with different object names) are
    # appended so their FORMs / classes / declarations are still found.
    orphans = [sf for sf in files.values()
               if sf.name not in used and sf.name not in referenced and sf.kind in ("include", "unknown", "class")
               and not _is_screen_flow(sf.content) and (sf.kind == "class" or mine(sf))]
    for sf in orphans:
        issues.append(IngestIssue("info", "ORPHAN_ATTACHED", f"{sf.filename} is not INCLUDEd by {main.name} under that name; "
                                  "its code was attached to the program", SourceRef(sf.name, 1)))
        emit(f"* tcb: >>> attached {sf.name}", SourceRef(sf.name, 1))
        walk(sf, [main.name, sf.name])
        emit(f"* tcb: <<< attached {sf.name}", SourceRef(sf.name, 1))
    text, n_macros = expand_macros("\n".join(out_lines))
    if n_macros:
        issues.append(IngestIssue("info", "MACROS_EXPANDED", f"{n_macros} macro call(s) expanded (DEFINE ... END-OF-DEFINITION)"))
    return FlatProgram(name=main.name, text=text, line_map=line_map, files=used, issues=issues)


def _is_screen_flow(content: str) -> bool:
    """Dynpro flow logic (PROCESS BEFORE OUTPUT) is not ABAP program code."""
    return bool(re.search(r"^\s*PROCESS\s+(BEFORE|AFTER)\s+", content, re.IGNORECASE | re.MULTILINE))


def _suffix(name: str) -> str:
    return name.rsplit("_", 1)[-1] if "_" in name else ""


def _common_prefix(a: str, b: str) -> int:
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


# ---------------------------------------------------------------------- macros
_DEFINE = re.compile(r"^\s*DEFINE\s+([A-Za-z0-9_/]+)\s*\.(.*?)^\s*END-OF-DEFINITION\s*\.", re.IGNORECASE | re.MULTILINE | re.DOTALL)
_ARG = re.compile(r"'(?:[^']|'')*'|`(?:[^`]|``)*`|[^\s,.:]+(?:\.[^\s,.:]+)*")


def expand_macros(text: str) -> tuple[str, int]:
    """Inline DEFINE macros: the definition is commented out and each call is replaced by
    the body with &1..&9 substituted, on the same line (so line numbers stay intact)."""
    macros: dict[str, str] = {}

    def strip_def(m: re.Match) -> str:
        macros[m.group(1).upper()] = m.group(2)
        return "\n".join("* tcb-macro: " + ln for ln in m.group(0).split("\n"))

    text = _DEFINE.sub(strip_def, text)
    if not macros:
        return text, 0
    body_stmts = {k: _split_chain(re.sub(r'^\s*\*.*$|".*$', "", v, flags=re.MULTILINE).replace("\n", " "), ".")
                  for k, v in macros.items()}
    names = "|".join(re.escape(k) for k in sorted(macros, key=len, reverse=True))
    call = re.compile(rf"^(\s*)({names})(\s*:\s*|\s+)(.*?)\.\s*(\".*)?$", re.IGNORECASE)
    count = 0
    out = []
    for line in text.split("\n"):
        m = call.match(line)
        if not m or line.lstrip().startswith("*"):
            out.append(line)
            continue
        name = m.group(2).upper()
        chains = [m.group(4)] if ":" not in m.group(3) else _split_chain(m.group(4))
        expanded = []
        for args_text in chains:
            args = _ARG.findall(args_text)
            for st in body_stmts[name]:
                expanded.append(re.sub(r"&([1-9])", lambda a: args[int(a.group(1)) - 1] if int(a.group(1)) <= len(args) else "space", st) + ".")
        count += 1
        out.append(m.group(1) + " ".join(expanded))
    return "\n".join(out), count


def _split_chain(text: str, sep: str = ",") -> list[str]:
    """Split on `sep` outside string literals (a '.' between two digits is a decimal point)."""
    parts, cur, q = [], "", None
    for i, ch in enumerate(text):
        if q:
            cur += ch
            if ch == q:
                q = None
        elif ch in "'`":
            q = ch
            cur += ch
        elif ch == sep and not (sep == "." and cur[-1:].isdigit() and text[i + 1:i + 2].isdigit()):
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts if p.strip()]
