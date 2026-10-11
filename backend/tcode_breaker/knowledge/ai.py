"""AI help for the knowledge library.

Two ways, both produce text in a format importer.parse() reads:
  * generate(): ask a configured model (Cortex by default) directly. Only object NAMES (and the columns
    the code uses) are sent - never program source. Results are tagged origin=ai and stay
    fields_complete=false, so the converter treats them as unverified until the user reviews them.
  * prompt(): build a self-contained prompt the user can paste into any AI chat (or hand to an SAP
    colleague); the answer is pasted back into the Knowledge page.
"""

from __future__ import annotations

from .importer import ImportDraft, parse
from .models import Provenance

TABLE_FORMAT = """Return ONLY a YAML block (no commentary) in exactly this shape:
tables:
  TABNAME:
    description: <short table description>
    module: <SAP module, e.g. SD>
    confidence: high | medium | low
    key: [MANDT, FIELD1, FIELD2]
    fields:
      MANDT: CLNT(3) Client
      FIELD1: CHAR(10) Short field label
      AMOUNT: CURR(15,2) ref=CURRENCY_FIELD Net value
Rules:
- One line per field in SE11 order: NAME: TYPE(length[,decimals]) [ref=FIELD] Label.
- TYPE is the ABAP Dictionary type: CHAR, NUMC, DATS, TIMS, CURR, QUAN, DEC, INT1, INT2, INT4, INT8, CUKY, UNIT, LANG, CLNT, FLTP, STRG, RAW.
- key lists the primary key fields (include MANDT if the table is client-dependent; text tables usually have SPRAS in the key).
- ref= names the currency/unit field of CURR/QUAN fields when it is in the same table.
- Use S/4HANA lengths where they differ from ECC (e.g. MATNR CHAR(40)).
- Accuracy matters more than completeness: list only fields you are sure exist. If you do not know a table
  (for example a customer Z/Y table), write it as   TABNAME: {unknown: true}   instead of guessing."""

FM_FORMAT = """Return ONLY a YAML block (no commentary) in exactly this shape:
function_modules:
  FM_NAME:
    kind: expression | lookup | ui | output_sink | side_effect | opaque
    output: <exporting parameter that carries the result>          # expression / lookup only
    sql: <Snowflake SQL expression using {PARAMETER} placeholders> # expression only
    tables: [TAB1, TAB2]                                           # lookup only: tables it reads
    note: <one sentence: what it does>
Meaning of kind:
- expression: pure function of its inputs that one Snowflake expression can reproduce (e.g. conversion exits, date arithmetic).
- lookup: reads master/customizing data; describe the equivalent join in `sql` and list the tables.
- ui: dialogs, popups, progress indicators - no data effect.
- output_sink: displays an internal table (ALV, list output).
- side_effect: writes, sends, locks, commits.
- opaque: real logic that one SQL expression cannot reproduce.
If you do not know a function module, give it kind: opaque and note: unknown."""


def prompt(kind: str, names: list[str], columns: dict[str, list[str]] | None = None, system: str = "S/4HANA") -> str:
    names = [n.upper() for n in names if n.strip()]
    if kind == "fms":
        return (f"You are an SAP ABAP expert. For each of these function modules ({system}), describe its behaviour so that a "
                f"converter can reproduce it in Snowflake SQL.\n\nFunction modules: {', '.join(names)}\n\n{FM_FORMAT}\n")
    lines = [f"You are an SAP ABAP Dictionary expert. Give the field definitions of these SAP tables ({system}), as shown in SE11.",
             "", "Tables: " + ", ".join(names)]
    used = {t: c for t, c in (columns or {}).items() if c and t.upper() in names}
    if used:
        lines += ["", "The program uses at least these fields - they must be included:"]
        lines += [f"- {t}: {', '.join(sorted(set(c)))}" for t, c in used.items()]
        lines += ["", "List every field of each table, not just these."]
    lines += ["", TABLE_FORMAT, ""]
    return "\n".join(lines)


def generate(kind: str, names: list[str], model_id: str, columns: dict[str, list[str]] | None = None, system: str = "S/4HANA") -> tuple[ImportDraft, list[dict]]:
    """Ask the model in batches; returns the merged draft and per-batch call info."""
    from ..llm.client import LLMError, complete, resolve

    spec = resolve(model_id)
    draft = ImportDraft(format="ai")
    calls = []
    batch = 4 if kind == "tables" else 10
    names = [n.upper() for n in names if n.strip()]
    for i in range(0, len(names), batch):
        part = names[i:i + batch]
        sys_msg = "You produce precise SAP metadata in the exact machine-readable format requested. No prose."
        try:
            c = complete(spec, sys_msg, prompt(kind, part, columns, system), max_tokens=8000 if kind == "tables" else 3000)
        except LLMError as exc:
            draft.warnings.append(f"{', '.join(part)}: {exc}")
            calls.append({"names": part, "ok": False, "error": str(exc)})
            continue
        sub = parse(c.text, origin="ai")
        for t in list(sub.tables.values()):
            if list(t.fields) == ["UNKNOWN"] or not t.fields:
                sub.tables.pop(t.name)
                sub.unknown.append(t.name)
            else:
                t.fields_complete = False  # never trust an AI field list as complete
        for f in list(sub.fms.values()):
            if (f.note or "").strip().lower().startswith("unknown"):
                sub.fms.pop(f.name)
                sub.unknown.append(f.name)
        got = set(sub.tables) | set(sub.fms)
        sub.unknown += [n for n in part if n not in got and n not in sub.unknown]
        draft.merge(sub)
        calls.append({"names": part, "ok": True, "seconds": round(c.seconds, 1), "model": c.model})
    draft.format = "ai"
    for t in draft.tables.values():
        t.origin, t.source = "ai", Provenance.AI
        for f in t.fields.values():
            f.source = Provenance.AI
    for f in draft.fms.values():
        f.origin, f.source = "ai", Provenance.AI
    return draft, calls
