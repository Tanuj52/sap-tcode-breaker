"""LLM translation of unresolved relations (and the naive full-program baseline for benchmarks).

Each unresolved relation becomes one small, contract-bound prompt: the input CTE schemas,
the exact output columns, the ABAP statements behind the step and any user context. The
model returns only a SELECT body, which is syntax-checked before it is accepted.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import sqlglot

from ..analysis.pipeline import RunResult, UserContext, full_view_name
from ..analysis.relations import Relation
from ..llm.client import LLMError, ModelSpec, approx_tokens, check_privacy, complete
from .sqlgen import render

SYSTEM = (
    "You translate one step of an SAP ABAP report into one Snowflake SQL SELECT statement. "
    "Rules: ABAP has no NULL - use COALESCE to initial values ('' for character, 0 for numbers, '00000000' for dates) "
    "when a LEFT JOIN may not match. DATS fields are VARCHAR 'YYYYMMDD'. Use only the input relations and columns given. "
    "Return exactly one SELECT statement (it may use sub-queries and window functions) in a ```sql block, nothing else."
)

_TOKEN = re.compile(r"__R\d+__")


# Exact ABAP semantics for constructs the compiler hands to the LLM. Injected only when relevant,
# so even small models get the knowledge they lack instead of guessing.
PRIMERS = {
    "AT END OF": ("ABAP 'AT END OF f ... SUM ... ENDAT' inside a LOOP over a table sorted by f: the block runs once per "
                  "group of f (at the group's last row); SUM replaces every numeric component of the work area with the "
                  "group total. Equivalent SQL: SELECT f, SUM(<numeric fields>) FROM <input> GROUP BY f (one row per group)."),
    "AT NEW": ("ABAP 'AT NEW f ... ENDAT' runs once at the first row of each group of f (table sorted by f). "
               "SQL: QUALIFY ROW_NUMBER() OVER (PARTITION BY f ORDER BY <sort>) = 1, or GROUP BY f when SUM is used."),
    "AT FIRST": "ABAP 'AT FIRST' runs once before the first row; 'AT LAST ... SUM' runs once with totals over all rows.",
    "ON CHANGE OF": "ABAP 'ON CHANGE OF f' runs when f differs from the previous row (LAG(f) OVER (ORDER BY <sort>) IS DISTINCT FROM f).",
    "EXIT INSIDE LOOP": "ABAP EXIT inside LOOP stops the loop: only rows before the first row meeting the exit condition are processed.",
    "ACCUMULATION": "A variable accumulated across LOOP iterations (x = x + ...) is a running or total SUM; use SUM() OVER or GROUP BY.",
    "READ TABLE ... INDEX": "READ TABLE itab INDEX n reads the n-th row in the current sort order (ROW_NUMBER() = n).",
}


def primers_for(rel: Relation) -> list[str]:
    text = (" ".join(rel.notes) + "\n" + rel.abap).upper()
    return [v for k, v in PRIMERS.items() if k in text]


@dataclass
class StepResult:
    relation: str
    cte: str
    ok: bool
    model: str
    sql: str | None = None
    error: str | None = None
    prompt_tokens: int = 0
    seconds: float = 0.0
    repairs: int = 0


def _schema(rel: Relation, name: str) -> str:
    cols = ", ".join(f"{c.name.lower()} {(c.comp.ddic_type if c.comp and c.comp.ddic_type else 'ANY')}" for c in rel.columns)
    return f"{name}({cols})"


def build_prompt(run: RunResult, rel: Relation, names: dict[str, str], ctx: UserContext, budget_tokens: int) -> str:
    by_id = {r.id: r for r in run.interp.relations}
    inputs = [i for i in rel.inputs() if _TOKEN.fullmatch(i)] + _TOKEN.findall(rel.raw_sql or "")
    inputs = [i for i in dict.fromkeys(inputs) if i in by_id and i != rel.id]
    if not inputs and rel.raw_sql:
        inputs = [i for i in _TOKEN.findall(rel.raw_sql) if i in by_id]
    db_tables = sorted({s.name for s in rel.sources if s.kind == "db"})
    out_cols = ", ".join(f"{c.name.lower()} {(c.comp.ddic_type if c.comp and c.comp.ddic_type else 'ANY')}" for c in rel.columns)
    parts = [
        "Input relations (already available as CTEs):",
        *[f"- {_schema(by_id[i], names.get(i, i))}" for i in inputs],
        *[f"- database table {t}" for t in db_tables],
    ]
    step_text = (rel.abap + " " + rel.body_sql() + " " + " ".join(rel.notes)).upper()
    step_params = sorted(p for p in run.interp.params_used if re.search(rf"\b(PRM\.)?{re.escape(p)}\b", step_text))
    if step_params:  # only parameters this step itself uses (inputs are already filtered)
        parts.append("- params(" + ", ".join(p.lower() for p in step_params) + ")  one row: CROSS JOIN params prm")
        if any(run.symbols.params[n].kind == "select_option" for n in step_params if n in run.symbols.params):
            parts.append("  select-options are ARRAYs of values (empty = no filter). Filter with exactly: "
                         "(ARRAY_SIZE(prm.s_x) = 0 OR ARRAY_CONTAINS(col::VARIANT, prm.s_x))")
    parts += [
        "",
        f"Produce relation '{names.get(rel.id, rel.var.lower())}' with exactly these columns in this order:",
        out_cols,
        "",
        *([f"No usable draft: write the SELECT from the ABAP statements below, reading from "
           f"{', '.join(names.get(i, i) for i in inputs) or 'the input relations'}. Return only the SELECT body for "
           f"'{names.get(rel.id, rel.var.lower())}' (no WITH clause that defines it)."] if "WHERE FALSE /* TCB-NEEDS-LLM" in rel.body_sql() else [
            "Deterministic draft (may contain NULL /* TCB-UNRESOLVED */ placeholders you must replace):",
            _TOKEN.sub(lambda m: names.get(m.group(0), m.group(0)), rel.body_sql())]),
        "",
        "Why it is unresolved: " + "; ".join(rel.notes[:6]),
    ]
    primers = primers_for(rel)
    if primers:
        parts += ["", "ABAP semantics you must reproduce:", *[f"- {p}" for p in primers]]
    parts += [
        "",
        "ABAP statements behind this step:",
        "```abap",
        rel.abap.strip()[: max(800, budget_tokens * 3)],
        "```",
    ]
    if ctx.notes:
        parts += ["", "Additional context from the user:", ctx.notes]
    text = "\n".join(parts)
    if approx_tokens(text) > budget_tokens:
        text = text[: budget_tokens * 4]
    return text


def _unwrap_self_cte(sql: str, name: str) -> str:
    """`WITH name AS (body) SELECT * FROM name` -> body (models sometimes wrap their answer this way)."""
    try:
        tree = sqlglot.parse_one(sql, read="snowflake")
    except sqlglot.errors.ParseError:
        return sql
    wkey = "with_" if "with_" in tree.args else "with"  # key name differs across sqlglot versions
    w = tree.args.get(wkey)
    if w is None:
        return sql
    ctes = {c.alias_or_name.lower(): c for c in w.expressions}
    if name.lower() not in ctes:
        return sql
    outer = tree.copy()
    outer.set(wkey, None)
    if re.sub(r"\s+", " ", outer.sql(dialect="snowflake")).strip().upper() == f"SELECT * FROM {name.upper()}":
        others = [c for k, c in ctes.items() if k != name.lower()]
        body = ctes[name.lower()].this.copy()
        if others:
            body.set(wkey, sqlglot.exp.With(expressions=[c.copy() for c in others]))
        return body.sql(dialect="snowflake")
    # rename the inner definition so it does not collide with the outer CTE of the same name
    return sql if not re.search(rf"\b{re.escape(name)}\b", outer.sql(dialect="snowflake"), re.I) else re.sub(
        rf"\b{re.escape(name)}\b", f"{name}_inner", sql, flags=re.I)


def extract_sql(text: str) -> str | None:
    m = re.search(r"```(?:sql)?\s*(.+?)```", text, re.S | re.I)
    body = (m.group(1) if m else text).strip().rstrip(";").strip()
    if not re.match(r"^(WITH|SELECT)\b", body, re.I):
        return None
    return body


def fill_unresolved(run: RunResult, spec: ModelSpec, ctx: UserContext | None = None, max_steps: int = 20,
                    verify=None, repairs: int = 2) -> list[StepResult]:
    """Translate every unresolved relation. `verify(run) -> error | None` compiles the whole query (repair loop)."""
    ctx = ctx or UserContext()
    check_privacy(spec, run.settings.confidential)
    if run.sql is None:
        return []
    names = run.sql.cte_names
    by_id = {r.id: r for r in run.interp.relations}
    results: list[StepResult] = []
    budget = max(1500, int(spec.context * 0.4))
    for rid in run.sql.order:
        rel = by_id[rid]
        if rel.status == "deterministic" or rel.llm_sql:
            continue
        if len(results) >= max_steps:
            break
        prompt = build_prompt(run, rel, names, ctx, budget)
        res = StepResult(rel.id, names.get(rel.id, rel.id), False, spec.id, prompt_tokens=approx_tokens(prompt))
        for attempt in range(2 + (repairs if verify else 0)):
            try:
                c = complete(spec, SYSTEM, prompt, max_tokens=2500)
            except LLMError as exc:
                res.error = str(exc)
                break
            res.seconds += c.seconds
            sql = extract_sql(c.text)
            if sql is None:
                res.error = "model did not return a SELECT"
                prompt += "\n\nReturn only a SELECT statement in a ```sql block."
                continue
            try:
                sqlglot.parse_one(sql, read="snowflake")
            except sqlglot.errors.ParseError as exc:
                res.error = f"SQL does not parse: {str(exc)[:200]}"
                prompt += f"\n\nYour previous answer did not parse ({str(exc)[:200]}). Fix it."
                continue
            sql = _unwrap_self_cte(sql, names.get(rel.id, rel.var.lower()))
            # map CTE names back to relation tokens so the final render stays consistent
            back = {v: k for k, v in names.items()}
            rel.llm_sql = re.sub(r"\b(" + "|".join(map(re.escape, sorted(back, key=len, reverse=True))) + r")\b",
                                 lambda m: back[m.group(1)], sql) if back else sql
            if verify is not None:
                err = verify(run)
                if err:
                    rel.llm_sql = None
                    res.error = f"does not compile: {err[:200]}"
                    res.repairs = getattr(res, "repairs", 0) + 1
                    prompt += f"\n\nYour previous answer:\n```sql\n{sql}\n```\nfailed to compile on Snowflake: {err[:300]}\nReturn a corrected SELECT."
                    continue
            rel.notes.append(f"translated by {spec.id}")
            res.ok = True
            res.sql = sql
            res.error = None
            break
        results.append(res)
    return results


def rerender(run: RunResult, mode: str = "select", view_name: str | None = None) -> None:
    if run.output_rel is None:
        return
    header = f"Generated by tcode-breaker from {run.flat.name} ({', '.join(run.flat.files)})"
    run.sql = render(run.output_rel, run.interp.relations, list(run.symbols.params.values()), run.interp.params_used,
                     run.output_cols, run.output.sort if run.output else [], mode,
                     full_view_name(run.settings, view_name, run.flat.name), header)


def compile_verifier(cursor, kb, settings, stub_db: str = "TCODE_BREAKER", stub_schema: str = "STUBS"):
    """Build a verify(run) callback that EXPLAINs the whole query against stub tables."""
    from ..validate.checks import compile_check

    def verify(run: RunResult) -> str | None:
        rerender(run)
        if run.sql is None:
            return "no SQL"
        chk = compile_check(cursor, run.sql.sql, kb, settings, stub_db, stub_schema)
        return None if chk.ok else chk.detail

    return verify


NAIVE_SYSTEM = (
    "You convert SAP ABAP report programs into one equivalent Snowflake SQL query. The SAP tables exist in Snowflake "
    "with the same table and column names. Selection-screen PARAMETERS become literals with their defaults; "
    "SELECT-OPTIONS are ignored when empty. Return only the SQL in a ```sql block."
)


def naive_convert(source: str, spec: ModelSpec, schema_hint: str | None = None) -> tuple[str | None, dict]:
    """Baseline for benchmarks: send the whole (flattened) program in one prompt."""
    prompt = (f"Database/schema: {schema_hint}\n\n" if schema_hint else "") + "ABAP program:\n```abap\n" + source + "\n```"
    meta = {"prompt_tokens": approx_tokens(prompt), "model": spec.id}
    if approx_tokens(prompt) > spec.context * 0.9:
        meta["error"] = f"program ({approx_tokens(prompt)} tokens) exceeds the model context ({spec.context})"
        return None, meta
    c = complete(spec, NAIVE_SYSTEM, prompt, max_tokens=4000)
    meta["seconds"] = c.seconds
    return extract_sql(c.text), meta
