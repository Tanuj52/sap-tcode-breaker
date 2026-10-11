"""Project workspace: rail, header, downloads, live runs and the seven sections (overview to validate)."""

from __future__ import annotations

import re
import time

import pandas as pd
import streamlit as st

from backend import core
from frontend import canvas, ui
from frontend.ui import badge, esc, icon

STAGES = [("uploaded", "Upload", "sources stored"), ("analyzed", "Analyze", "tables, flow, slice"), ("reviewed", "Context", "optional additions"),
          ("converted", "Convert", "Snowflake SQL"), ("validated", "Validate", "compile and compare")]
SECTIONS = [
    ("overview", "Overview", ":material/dashboard:", "Understand", "What the program reads, computes and shows, and what needs attention."),
    ("flow", "Data flow", ":material/account_tree:", "Understand", "Tables, internal tables and steps as a map. Pick a node for its columns, ABAP and SQL."),
    ("calls", "Call tree", ":material/call_split:", "Understand", "Events in execution order with every FORM, method and function module they call."),
    ("source", "Source", ":material/code:", "Understand", "The uploaded ABAP. Highlighted lines are the slice that feeds the output."),
    ("review", "Context", ":material/sell:", "Deliver", "Optional checkpoint: business names, function module sources, table renames, result table."),
    ("convert", "SQL", ":material/database:", "Deliver", "Generate the CTE query or view. Rules first; a model only for unresolved steps."),
    ("validate", "Validate", ":material/verified_user:", "Deliver", "Syntax, placeholders, EXPLAIN on Snowflake and a row-by-row comparison to a reference."),
]
SECTION = {s[0]: s for s in SECTIONS}
KIND_COLOR = {"db_table": "var(--c-node-table)", "itab": "var(--c-node-itab)", "param": "var(--c-node-param)", "output": "var(--c-node-output)", "fm": "var(--c-node-fm)"}
KIND_ICON = {"db_table": "database", "itab": "layers", "param": "sliders", "output": "monitor", "fm": "function"}
FM_TONE = {"custom": "ai", "unknown": "bad", "opaque": "bad", "expression": "ok"}
PROV_ORDER = ["snowflake_catalog", "client_pack", "library", "builtin", "ai_generated", "inferred", "unresolved"]
PROV_COLOR = {"snowflake_catalog": "var(--c-ok)", "client_pack": "var(--c-ai)", "library": "var(--c-accent)", "builtin": "var(--c-info)",
              "ai_generated": "var(--c-warn)", "inferred": "color-mix(in oklab, var(--c-warn) 55%, transparent)", "unresolved": "var(--c-bad)"}
SEV_ICON = {"error": "xcircle", "warning": "alert", "info": "info"}
SEV_CLASS = {"error": "bad", "warning": "warn", "info": "info"}
ABAP_KEYWORDS = set("""REPORT PROGRAM INCLUDE DATA TYPES TYPE TABLE OF STANDARD SORTED HASHED WITH KEY DEFAULT EMPTY UNIQUE NON-UNIQUE BEGIN END
CONSTANTS VALUE PARAMETERS SELECT-OPTIONS FOR OBLIGATORY SELECT SINGLE FROM INTO CORRESPONDING FIELDS WHERE AND OR NOT IN BETWEEN LIKE IS INITIAL
NULL ORDER BY GROUP HAVING UP TO ROWS ENDSELECT INNER LEFT OUTER JOIN ON AS ALL ENTRIES LOOP AT ENDLOOP ASSIGNING REFERENCE READ INDEX BINARY
SEARCH TRANSPORTING APPEND COLLECT INSERT MODIFY DELETE ADJACENT DUPLICATES COMPARING SORT ASCENDING DESCENDING CLEAR REFRESH FREE MOVE IF ELSE
ELSEIF ENDIF CASE WHEN OTHERS ENDCASE DO ENDDO WHILE ENDWHILE CHECK EXIT CONTINUE RETURN FORM ENDFORM PERFORM USING CHANGING TABLES FUNCTION
ENDFUNCTION CALL METHOD METHODS CLASS ENDCLASS DEFINITION IMPLEMENTATION PUBLIC PRIVATE PROTECTED SECTION CREATE OBJECT NEW START-OF-SELECTION
END-OF-SELECTION INITIALIZATION AT-SELECTION-SCREEN AT NEW FIRST LAST SUM ENDAT EXPORTING IMPORTING EXCEPTIONS RECEIVING WRITE SKIP ULINE FORMAT
CONCATENATE SPLIT CONDENSE TRANSLATE REPLACE SHIFT FIELD-SYMBOLS FIELD-SYMBOL DEFINE END-OF-DEFINITION ADD SUBTRACT MULTIPLY DIVIDE EQ NE LT GT LE
GE TRY CATCH ENDTRY RAISE MESSAGE TEXT LINES DESCRIBE OPEN CURSOR FETCH NEXT CLOSE PACKAGE SIZE LIKE REF TO FINAL CONV COND SWITCH THEN""".split())


# ---------------------------------------------------------------------- live runs
def run_stage(pid: str, kind: str, name: str, options: dict | None = None, refresh_catalog: bool = False) -> bool:
    started = time.time()
    label = {"run": "Running the pipeline", "analyze": "Analyzing", "convert": "Converting", "validate": "Validating"}[kind]
    with st.status(f"{label} · {name}", expanded=True) as status:
        try:
            if kind in ("analyze", "run"):
                st.write("Reading sources, parsing ABAP, reading the Snowflake schema and interpreting the program…")
                a = core.analyze(pid, refresh_catalog)
                cat = a.get("catalog") or {}
                st.write(f":material/check: Analyzed {a['stats']['lines']:,} lines · {a['stats']['statements']:,} statements · {a['stats']['relations']} steps · "
                         f"schema: {'not read (' + cat['error'][:90] + ')' if cat.get('error') else str(cat.get('tables', 0)) + ' tables' if cat.get('enabled') else 'off'}")
                if cat.get("error"):
                    ui.notify("warn", "Snowflake schema not read", f"{cat['error'][:160]}. Field lists were inferred from the code.")
            if kind in ("convert", "run"):
                st.write("Generating SQL: one CTE per step, rules first, a model only for unresolved steps…")
                c = core.convert(pid, options)
                st.write(f":material/check: SQL {ui.status_label(c['status'])} · {len(c['relations'])} steps"
                         + (f" · {len(c['steps'])} filled by AI" if c["steps"] else "") + (f" · AI error: {c['error'][:120]}" if c["error"] else ""))
                if c["error"]:
                    ui.notify("warn", "Converted with AI errors", c["error"][:200])
                if kind == "run" and not c.get("sql"):
                    status.update(label=f"No SQL generated · {time.time() - started:.1f} s", state="error")
                    return True
            if kind in ("validate", "run"):
                st.write("Validating: syntax, placeholders, EXPLAIN against stub tables, row comparison to a reference…")
                v = core.validate(pid)
                passed = sum(1 for x in v["checks"] if x["ok"] is True)
                st.write(f":material/check: {passed} of {len(v['checks'])} checks passed" + (" · results identical to the reference" if (v.get("compare") or {}).get("ok") else ""))
                ui.notify("ok" if v["ok"] else "warn", "All validation checks passed" if v["ok"] else "Some validation checks need attention")
            status.update(label=f"{label} done · {time.time() - started:.1f} s", state="complete", expanded=False)
            return True
        except core.ServiceError as exc:
            status.update(label=f"{label} failed", state="error")
            st.error(str(exc))
        except Exception as exc:  # noqa: BLE001
            status.update(label=f"{label} failed", state="error")
            st.error(core.clean(exc))
    return False


# ---------------------------------------------------------------------- rail + header
def pipeline_steps(stage: str) -> str:
    idx = next((i for i, s in enumerate(STAGES) if s[0] == stage), -1)
    items = "".join(f'<li class="{"done" if i <= idx else ""}" title="{sub}"><span class="dot">{icon("check", 11, 3) if i <= idx else i + 1}</span>'
                    f'<div class="l"><b>{label}</b><span>{sub}</span></div></li>' for i, (sid, label, sub) in enumerate(STAGES))
    return f'<ol class="pipe-steps">{items}</ol>'


def rail(p: dict, a: dict | None, view: str) -> None:
    badges = ""
    if a:
        badges += badge(ui.status_label(a["sql_status"]), ui.status_tone(a["sql_status"]))
        badges += badge("S/4HANA" if a["settings"].get("source_system") == "s4" else "ECC")
        cat = a.get("catalog") or {}
        if cat.get("enabled"):
            badges += badge(f'{icon("database", 11)}{"schema not read" if cat.get("error") else str(cat.get("tables")) + " in schema"}', "warn" if cat.get("error") else "ok", cat.get("error") or "")
    name = esc(p["name"]).replace("_", "_<wbr>")
    ui.html(f'<div class="rail-sec"><a class="plain faint" style="display:inline-flex;align-items:center;gap:4px;font-size:11.5px" href="?page=projects">'
            f'{icon("back", 12)}{esc(p["workspace"])}</a>'
            f'<div class="mono" style="margin-top:8px;font-size:15px;font-weight:600;line-height:1.35;color:var(--c-fg);overflow-wrap:anywhere">{name}</div>'
            f'<div class="row" style="gap:6px;margin-top:10px">{badges}</div></div>'
            f'<div class="rail-sec"><div class="eyebrow faint" style="margin-bottom:12px">Pipeline</div>{pipeline_steps(p["stage"])}</div>')
    counts = {"flow": len(a["graph"]["nodes"]), "calls": a["stats"]["routines"], "source": len(a["files"]), "convert": len(a["relations"])} if a else {}
    rules = []
    for group in ("Understand", "Deliver"):
        ui.html(f'<div class="eyebrow faint" style="padding:{"14px" if group == "Understand" else "10px"} 10px 6px">{group}</div>')
        for sid, label, ico, g, _ in SECTIONS:
            if g != group:
                continue
            if st.button(label, key=f"sec_{sid}", icon=ico, type="tertiary", width="stretch"):
                ui.go("p", pid=p["id"], view=sid)
            if sid in counts:
                rules.append(f'.st-key-sec_{sid} [data-testid="stBaseButton-tertiary"]::after{{content:"{counts[sid]}"}}')
    rules.append(f".st-key-sec_{view} button{{background:var(--c-surface-2)!important;color:var(--c-fg)!important}}"
                 f".st-key-sec_{view} [data-testid='stIconMaterial']{{color:var(--c-accent)!important}}"
                 f".st-key-sec_{view} button::before{{content:'';position:absolute;left:-12px;top:50%;width:3px;height:20px;transform:translateY(-50%);"
                 f"border-radius:0 3px 3px 0;background:var(--c-accent)}}")
    st.markdown("<style>" + "".join(rules) + "</style>", unsafe_allow_html=True)
    if a:
        s = a["stats"]
        ruled = f"{round(100 * s['deterministic_relations'] / s['relations'])}%" if s["relations"] else "–"
        cells = "".join(f'<div style="background:var(--c-surface);padding:12px 16px"><div class="tabular" style="font-size:15px;font-weight:600;color:var(--c-fg)">{v}</div>'
                        f'<div class="eyebrow faint" style="font-size:9.5px;margin-top:2px">{k}</div></div>'
                        for k, v in [("lines", f"{s['lines']:,}"), ("tables", s["tables"]), ("steps", s["relations"]), ("rules", ruled)])
        ui.html(f'<div style="margin:16px -12px 0;display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--c-line);border-top:1px solid var(--c-line)">{cells}</div>')


def downloads(p: dict) -> None:
    with st.popover("Download", icon=":material/download:"):
        ui.html('<div class="eyebrow faint" style="padding:2px 2px 6px">Artifacts</div>')
        items = [("sql", "SQL file (.sql)", "CREATE OR REPLACE VIEW" if p["convert"]["mode"] == "view" else "WITH … SELECT", ":material/database:"),
                 ("report", "Conversion report (.md)", "tables, columns, findings, SQL", ":material/description:"),
                 ("lineage", "Column lineage (.csv)", "output column → source table.field", ":material/table_view:"),
                 ("analysis", "Analysis (.json)", "full machine-readable analysis", ":material/data_object:"),
                 ("validation", "Validation (.json)", "checks and comparison", ":material/verified_user:")]
        for kind, label, hint, ico in items:
            got = core.download(p["id"], kind)
            if got:
                st.download_button(label, data=got[1], file_name=got[0], mime=got[2], icon=ico, width="stretch", key=f"dl_{kind}", help=hint)
            else:
                st.button(label, disabled=True, icon=ico, width="stretch", key=f"dl_{kind}", help="Run the pipeline first")
        a = core.analysis(p["id"])
        if a:
            st.download_button("Diagram (.svg)", data=standalone_svg(flow_svg(a, True, False, None)), file_name=f"{p['name']}_flow.svg", mime="image/svg+xml",
                               icon=":material/image:", width="stretch", key="dl_svg", help="static diagram; PNG and the live layout export from the Data flow toolbar")
        st.divider()
        name, data = core.export_zip(p["id"])
        st.download_button("Full bundle (.zip)", data=data, file_name=name, mime="application/zip", icon=":material/inventory_2:", width="stretch",
                           key="dl_zip", help="everything incl. sources")


@st.dialog("Delete project")
def confirm_delete(p: dict) -> None:
    st.write(f"Delete **{p['name']}**? This removes its files and results.")
    a, b = st.columns(2)
    if a.button("Cancel", width="stretch"):
        st.rerun()
    if b.button("Delete", type="primary", icon=":material/delete:", width="stretch"):
        core.delete_project(p["id"])
        ui.notify("ok", "Project deleted")
        ui.go("projects")


@st.dialog("Project settings", width="large")
def settings_dialog(p: dict, a: dict | None) -> None:
    s = {**((a or {}).get("settings") or {}), **p["settings"]}
    programs = (a or {}).get("programs") or []
    main = p.get("main") or ""
    if len(programs) > 1:
        main = st.selectbox("Main program", [""] + programs, index=([""] + programs).index(main) if main in programs else 0,
                            format_func=lambda x: x or f"automatic ({programs[0]})", help="The upload contains several programs; choose the one to convert.")
    c1, c2, c3 = st.columns(3)
    system = c1.selectbox("SAP system", ["ecc", "s4"], index=1 if s.get("source_system") == "s4" else 0, format_func=lambda x: {"ecc": "ECC", "s4": "S/4HANA"}[x])
    client = c2.text_input("Client (MANDT)", value=s.get("client") or "", help="empty = no filter")
    lang = c3.text_input("Language", value=s.get("language") or "E", max_chars=2).upper()
    raw_db, raw_sc = ui.location_picker("Source: raw SAP layer", s.get("target_database") or "", s.get("target_schema") or "", f"ps_raw_{p['id']}",
                                        "The SQL reads SAP tables from here; columns are read live from this schema.")
    pattern = st.text_input("Physical table name pattern", value=s.get("table_pattern") or "{table}", help="{table} = SAP name, e.g. SAP_{table}") or "{table}"
    gold_db, gold_sc = ui.location_picker("Target: gold layer for views", s.get("view_database") or "", s.get("view_schema") or "", f"ps_gold_{p['id']}",
                                          "Where CREATE OR REPLACE VIEW creates the view. Empty = same as source.", "e.g. SAP_GOLD", "e.g. REPORTING")
    t1, t2, t3 = st.columns(3)
    use_catalog = t1.toggle("Read schema metadata", value=s.get("use_catalog", True) is not False)
    infer = t2.toggle("Infer fields from code", value=s.get("infer_fields", True) is not False)
    conf = t3.toggle("Confidential code", value=s.get("confidential", True) is not False)
    b1, b2 = st.columns(2)
    if b1.button("Cancel", width="stretch"):
        st.rerun()
    if b2.button("Save and re-analyze", type="primary", icon=":material/save:", width="stretch"):
        values = {"source_system": system, "target_database": raw_db, "target_schema": raw_sc, "view_database": gold_db, "view_schema": gold_sc,
                  "table_pattern": pattern, "client": client, "language": lang, "confidential": conf, "infer_fields": infer, "use_catalog": use_catalog}
        core.update_project(p["id"], settings_={k: (None if v == "" else v) for k, v in values.items()}, main=main or None)
        st.session_state[f"pending_{p['id']}"] = ("analyze", True)
        ui.notify("ok", "Project settings saved")
        st.rerun()


def header(p: dict, a: dict | None, view: str, rail_open: bool) -> None:
    sec = SECTION[view]
    with st.container(horizontal=True, vertical_alignment="center", key="phead", gap="small"):
        if st.button("", icon=":material/left_panel_close:" if rail_open else ":material/left_panel_open:", type="tertiary", key="hd_rail",
                     help="Hide project panel" if rail_open else "Show project panel"):
            core.save_ui_prefs(rail="closed" if rail_open else "open")
            st.rerun()
        ui.html(f"<div class='row' style='gap:6px;font-size:13px;flex-wrap:nowrap;min-width:0'><a class='plain faint' href='?page=projects'>Projects</a>"
                f"<span class='faint'>›</span><span class='mono fg' style='font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap'>{esc(p['name'])}</span>"
                f"<span class='faint'>›</span><span class='muted' style='white-space:nowrap'>{sec[1]}</span></div>")
        if st.button("", icon=":material/tune:", type="tertiary", help="Project settings (source, target, output)", key="hd_settings"):
            settings_dialog(p, a)
        if st.button("Re-analyze", icon=":material/refresh:", key="hd_analyze"):
            st.session_state[f"pending_{p['id']}"] = ("analyze", True)
            st.rerun()
        downloads(p)
        if st.button("Run all", icon=":material/rocket_launch:", type="primary", key="hd_run", help="Analyze, convert (AI for leftovers) and validate"):
            st.session_state[f"pending_{p['id']}"] = ("run", False)
            st.rerun()
        if st.button("", icon=":material/delete:", type="tertiary", help="Delete project", key="hd_delete"):
            confirm_delete(p)


def section_head(view: str, action: tuple[str, str, str] | None = None, pid: str = "") -> None:
    sid, label, ico, group, desc = SECTION[view]
    glyph = {"overview": "dashboard", "flow": "network", "calls": "branch", "source": "code", "review": "tag", "convert": "database", "validate": "shield"}[sid]
    with st.container(horizontal=True, vertical_alignment="bottom", key=f"sh_{view}_row"):
        ui.html(f"<div class='fade-up'><div class='row accent' style='gap:8px'>{icon(glyph, 16)}<span class='eyebrow'>{group}</span></div>"
                f"<div class='display' style='font-size:28px;line-height:1.2;color:var(--c-fg);margin-top:6px'>{label}</div>"
                f"<div class='muted' style='font-size:14px;margin-top:4px;max-width:680px'>{desc}</div></div>")
        if action and st.button(action[0], icon=action[1], key=f"sh_{view}"):
            ui.go("p", pid=pid, view=action[2])


# ---------------------------------------------------------------------- page
def render(pid: str, view: str, autorun: bool = False) -> None:
    p = core.project(pid)
    if p is None:
        with st.container(key="pcontent"):
            ui.empty("This project does not exist (it may have been deleted).", "folder")
            if st.button("Back to projects"):
                ui.go("projects")
        return
    view = view if view in SECTION else "overview"
    rail_open = core.ui_prefs().get("rail") != "closed"
    pending = st.session_state.pop(f"pending_{pid}", None)
    if autorun:
        pending = ("run", False)
    a = core.analysis(pid)
    if pending is None and (p["stage"] == "uploaded" or a is None):
        pending = ("analyze", False)
    with st.container(horizontal=True, key="pshell", gap=None):
        if rail_open:
            with st.container(key="prail", width=248):
                rail(p, a, view)
        with st.container(key="pbody"):
            header(p, a, view, rail_open)
            if pending:
                with st.container(key="pcontent"):
                    kind, refresh = pending
                    run_stage(pid, kind, p["name"], p["convert"], refresh)
                if autorun or kind == "run":
                    ui.go("p", pid=pid, view="convert")
                st.rerun()
            if a is None:
                with st.container(key="pcontent"):
                    ui.empty("No analysis yet.", "search")
                return
            if view == "flow":
                with st.container(key="pflowbox"):
                    flow(p, a)
                return
            with st.container(key="pcontent"):
                if view == "overview":
                    section_head(view, ("Open data flow", ":material/account_tree:", "flow"), pid)
                    overview(p, a)
                elif view == "calls":
                    section_head(view)
                    call_tree(p, a)
                elif view == "source":
                    section_head(view)
                    source_view(p, a)
                elif view == "review":
                    section_head(view, ("Go to SQL", ":material/auto_fix_high:", "convert"), pid)
                    review(p, a)
                elif view == "convert":
                    section_head(view, ("Validate", ":material/verified_user:", "validate"), pid)
                    convert_panel(p, a)
                elif view == "validate":
                    section_head(view)
                    validate_panel(p)


def jump(pid: str, loc: dict | None) -> str:
    if not loc:
        return ""
    return f'<a class="tcb-link mono" style="font-size:11px" href="{ui.link("p", pid=pid, view="source", file=loc["file"], line=loc["line"])}">{esc(loc["file"])}:{loc["line"]}</a>'


# ---------------------------------------------------------------------- overview
def knowledge_card(a: dict, pid: str) -> None:
    used = [t for t in a["tables"] if t["reads"] or t["writes"] or t["in_slice"]]
    mix = [(pv, sum(1 for t in used if t["provenance"] == pv)) for pv in PROV_ORDER]
    mix = [(pv, n) for pv, n in mix if n]
    missing = [t for t in used if t["provenance"] in ("inferred", "unresolved") or not t["known"]]
    review_ai = [t for t in used if t["provenance"] == "ai_generated"]
    fms = sorted({c["target"] for c in a["calls"] if c["kind"] == "function" and not c["resolved"] and not c["target"].startswith("(")})
    gaps = len(missing) + len(fms)
    with ui.panel("pj1"):
        ui.heading("Knowledge", f"{gaps} gap(s) no source resolved" if gaps else "every table and FM resolved", "library")
        if used:
            bar = "".join(f'<span title="{ui.prov_label(pv)}: {n}" style="width:{100 * n / len(used)}%;background:{PROV_COLOR[pv]}"></span>' for pv, n in mix)
            legend = "".join(f'<span class="row" style="gap:5px"><span style="width:8px;height:8px;border-radius:2px;background:{PROV_COLOR[pv]}"></span>{ui.prov_label(pv)} '
                             f'<b class="tabular fg">{n}</b></span>' for pv, n in mix)
            ui.html(f'<div class="bar" style="height:10px;box-shadow:inset 0 0 0 1px var(--c-line)">{bar}</div><div class="row muted" style="gap:12px;margin-top:8px;font-size:11px">{legend}</div>')
        if missing:
            chips = "".join(f'<span class="badge b-warn mono">{esc(t["name"])}</span>' for t in missing[:10]) + (f'<span class="faint" style="font-size:11px">+{len(missing) - 10}</span>' if len(missing) > 10 else "")
            ui.html(f'<div class="muted" style="font-size:11px;font-weight:500;margin-top:12px">Tables known only from the code</div><div class="row" style="gap:4px;margin-top:6px">{chips}</div>')
            if st.button(f"Add {ui.plural(len(missing), 'table')}", icon=":material/auto_fix_high:", type="primary", key="kc_tables"):
                ui.go("knowledge", tab="add", tables=",".join(t["name"] for t in missing), **{"from": pid})
        if fms:
            chips = "".join(f'<span class="badge b-bad mono">{esc(n)}</span>' for n in fms[:8]) + (f'<span class="faint" style="font-size:11px">+{len(fms) - 8}</span>' if len(fms) > 8 else "")
            ui.html(f'<div class="muted" style="font-size:11px;font-weight:500;margin-top:12px">Function modules with unknown behaviour</div><div class="row" style="gap:4px;margin-top:6px">{chips}</div>')
            if st.button(f"Describe {len(fms)} FM{'' if len(fms) == 1 else 's'}", icon=":material/code:", key="kc_fms"):
                ui.go("knowledge", tab="add", fms=",".join(fms), **{"from": pid})
        if review_ai:
            ui.html(f'<div class="muted" style="font-size:11.5px;margin-top:10px"><span class="warn">{icon("alert", 13)}</span> {esc(", ".join(t["name"] for t in review_ai))} '
                    f'use AI-proposed definitions; verify them in SE11.</div>')
        if not (missing or fms or review_ai):
            ui.html(f'<div class="row muted" style="gap:8px;margin-top:10px;font-size:12px"><span class="ok">{icon("shield")}</span>Nothing to add for this program.</div>')


def type_text(c: dict) -> str:
    t = esc(c.get("ddic_type") or "?")
    if c.get("length"):
        t += f"({c['length']}" + (f",{c['decimals']}" if c.get("decimals") else "") + ")"
    return t


def lineage_chips(c: dict) -> str:
    chips = " ".join(f"<span class='chip'>{esc(x.get('table'))}.{esc(x.get('field'))}</span>" for x in c.get("lineage") or [])
    if c.get("derived"):
        chips += " " + badge(icon("sparkles", 11) + "calculated", "ai")
    return chips


def overview(p: dict, a: dict) -> None:
    s = a["stats"]
    pid = p["id"]
    used = [t for t in a["tables"] if t["reads"] or t["writes"]]
    pct = 100 * s["slice_lines"] / s["lines"] if s["lines"] else 0
    ruled = s["deterministic_relations"] / s["relations"] if s["relations"] else 0
    sev = {k: sum(1 for f in a["findings"] if f["severity"] == k) for k in ("error", "warning", "info")}
    out = a.get("output")
    left, right = st.columns([1.25, 1])
    with left, ui.panel("ov_ready"):
        ring = ui.ring(ruled, 128, 12, inner=f'<span class="display tabular" style="font-size:34px;line-height:1;color:var(--c-fg)">{round(ruled * 100)}%</span>'
                                             f'<span class="faint" style="margin-top:4px;font-size:11px">rule-based</span>')
        chips = "".join(f'<span class="row" style="gap:6px;border-radius:6px;border:1px solid var(--c-{"line-strong" if sev[k] else "line"});padding:4px 8px;width:fit-content">'
                        f'<span class="{SEV_CLASS[k]}">{icon(SEV_ICON[k], 14)}</span><b class="tabular fg">{sev[k]}</b>{k}{"" if sev[k] == 1 else "s"}</span>' for k in sev)
        output = f' · output <span class="mono fg">{esc(out["table"].lower())}</span> ({esc(out["kind"])})' if out else " · no output table found"
        steps = f"{s['relations']} SQL steps" if a.get("sql") else "No SQL yet"
        llm = f", {s['llm_relations']} need a model" if s["llm_relations"] else ""
        with st.container(horizontal=True, vertical_alignment="center", gap="large"):
            ui.html(ring, width="content")
            with st.container():
                ui.html(f'<div class="eyebrow faint">Conversion readiness</div><div style="margin-top:6px;font-size:20px;font-weight:600;color:var(--c-fg)">{steps}</div>'
                        f'<div style="margin-top:6px">{badge(ui.status_label(a["sql_status"]), ui.status_tone(a["sql_status"]))}</div>'
                        f'<div class="muted" style="font-size:13px;margin-top:6px">{s["deterministic_relations"]} by rules{llm}{output}</div>'
                        f'<div class="muted" style="display:flex;flex-direction:column;gap:8px;margin-top:12px;font-size:12px">{chips}</div>')
                if st.button("Open SQL" if a.get("sql") else "Generate SQL", icon=":material/auto_fix_high:", type="primary", key="ov_sql"):
                    ui.go("p", pid=pid, view="convert")
                if st.button("Add context", icon=":material/sell:", key="ov_ctx"):
                    ui.go("p", pid=pid, view="review")
    with right:
        slices = {}
        for r in a["slice"]:
            slices[r["file"]] = slices.get(r["file"], 0) + r["end"] - r["start"] + 1
        files = "".join(f'<div class="row" style="gap:8px;font-size:11.5px;flex-wrap:nowrap"><span class="mono muted" style="width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'
                        f'{esc(f.get("filename") or f["name"])}</span><span class="bar" style="flex:1;height:6px"><span style="width:{100 * slices.get(f["name"], 0) / f["lines"] if f["lines"] else 0}%;'
                        f'background:color-mix(in oklab,var(--c-accent) 80%,transparent)"></span></span><span class="mono faint tabular" style="width:70px;text-align:right">'
                        f'{slices.get(f["name"], 0)}/{f["lines"]}</span></div>' for f in a["files"][:12])
        ui.html(f'<div class="card" style="padding:24px"><div class="eyebrow faint">Program slice</div><div class="row" style="gap:8px;margin-top:8px;align-items:baseline">'
                f'<span class="display tabular" style="font-size:34px;line-height:1;color:var(--c-fg)">{s["slice_lines"]:,}</span>'
                f'<span class="muted" style="font-size:13px">of {s["lines"]:,} lines feed the output</span></div>'
                f'<div class="bar" style="height:12px;margin-top:16px;box-shadow:inset 0 0 0 1px var(--c-line)"><span style="width:{max(pct, 1 if s["slice_lines"] else 0)}%;background:var(--c-accent)"></span>'
                f'<span class="hatch" style="flex:1"></span></div><div class="between faint" style="margin-top:6px;font-size:11px"><span>{pct:.{1 if pct < 10 else 0}f}% translated</span>'
                f'<span>{100 - pct:.0f}% listed only</span></div><div style="margin-top:14px;max-height:112px;overflow:auto;display:grid;gap:6px">{files}</div></div>')
    ui.html(ui.kpis([("Lines", f"{s['lines']:,}", f"{len(a['files'])} file(s)"), ("Statements", f"{s['statements']:,}", f"{s['slice_statements']:,} in slice"),
                     ("SAP tables", s["tables"], f"{s['columns']} columns referenced"), ("Routines", s["routines"], f"{s['dead_routines']} never called"),
                     ("Calls", s["calls"], "FM, method, FORM"), ("Params", len(a["params"]), "selection screen")]))
    st.write("")
    tables_col, side = st.columns([2, 1])
    with tables_col:
        with ui.panel("pj2"):
            ui.heading("SAP tables and columns", f"{len(used)} table(s) read or written", "database")
            if not used:
                st.caption("The program reads no database table.")
            for i, t in enumerate(used):
                tags = (f" · → {t['mapped_to']}" if t.get("mapped_to") else "") + (" · writes" if t["writes"] else "")
                with st.expander(f"**{t['name']}**  {t.get('business_name') or t['description']}  ·  {ui.prov_label(t['provenance'])}{tags}  ·  {len(t['columns'])} cols", expanded=i == 0):
                    rows = "".join(f'<tr><td class="m">{esc(c["name"])}{" " + icon("key", 11) if c["is_key"] else ""}</td><td>{esc(c.get("business_name") or c["description"])}</td>'
                                   f'<td class="mono faint">{type_text(c)}</td>'
                                   f'<td>{" ".join(badge(esc(u)) for u in c["usages"])}</td>'
                                   f'<td>{badge(c["status"], {"known": "ok", "unverified": "warn"}.get(c["status"], "bad"))}</td></tr>' for c in t["columns"])
                    ui.html(f'<div class="scroll" style="max-height:340px"><table class="tbl"><thead><tr><th>Column</th><th>Meaning</th><th>Type</th><th>Used in</th><th>Known</th></tr></thead>'
                            f'<tbody>{rows}</tbody></table></div>')
    with side:
        knowledge_card(a, pid)
        with ui.panel("pj3"):
            ui.heading("Selection screen", f"{len(a['params'])} input(s)", "sliders")
            if not a["params"]:
                st.caption("No inputs.")
            ui.html("".join(f'<div class="between" style="border-radius:8px;border:1px solid var(--c-line);background:var(--c-sunken);padding:7px 12px;margin-top:6px">'
                            f'<div style="min-width:0"><div class="mono fg" style="font-size:13px">{esc(x["name"].lower())}</div><div class="faint" style="font-size:11px">'
                            f'{esc(x["kind"].replace("_", "-"))} {("for " + esc(x["ref"])) if x.get("ref") else ""}</div></div><div class="row" style="gap:6px">'
                            f'{badge("= " + esc(x["default"])) if x.get("default") else ""}{"" if x.get("used") else badge("unused")}</div></div>' for x in a["params"]))
        with ui.panel("pj4"):
            ui.heading("Findings", "", "alert")
            sel = st.segmented_control("Severity", ["all", "error", "warning", "info"], default="all", key="ov_sev", label_visibility="collapsed") or "all"
            items = [f for f in a["findings"] if sel == "all" or f["severity"] == sel]
            body = "".join(f'<div class="row" style="gap:10px;align-items:flex-start;flex-wrap:nowrap;padding:10px 0;border-top:1px solid var(--c-line);font-size:12px">'
                           f'<span class="{SEV_CLASS.get(f["severity"], "info")}" style="margin-top:2px">{icon(SEV_ICON.get(f["severity"], "info"))}</span><div style="min-width:0;flex:1">'
                           f'<div class="between"><span class="mono faint" style="font-size:10.5px">{esc(f["code"])}</span>{badge(f["severity"], ui.SEV_TONE.get(f["severity"], "slate"))}</div>'
                           f'<div class="fg" style="margin-top:4px;font-size:12.5px;line-height:1.45">{esc(f["message"])}</div>'
                           f'{"<div class=muted style=margin-top:4px>" + esc(f["hint"]) + "</div>" if f.get("hint") else ""}<div style="margin-top:4px">{jump(pid, f.get("loc"))}</div></div></div>'
                           for f in items)
            ui.html(f'<div class="scroll" style="max-height:440px">{body or "<div class=faint style=padding:12px>Nothing here.</div>"}</div>')
    if out:
        rows = "".join(f'<tr><td class="mono faint tabular" style="padding-left:18px">{i + 1:02d}</td><td class="m">{esc(c["name"].lower())}</td><td>{esc(c.get("business_name") or c["label"])}</td>'
                       f'<td>{lineage_chips(c)}</td><td class="mono faint">{esc(c["ddic_type"])}</td></tr>'
                       for i, c in enumerate([c for c in out["columns"] if not c["hidden"]]))
        ui.html(ui.card("Report output", f'<div class="scroll"><table class="tbl"><thead><tr><th style="padding-left:18px">#</th><th>Column</th><th>Business name</th><th>Lineage</th><th>Type</th></tr></thead>'
                                         f'<tbody>{rows}</tbody></table></div>', "What the user sees in SAP, and where each column comes from", "monitor", pad=False, style="margin-top:16px"))


# ---------------------------------------------------------------------- data flow
NODE_W, NODE_H, GAP_X, GAP_Y = 220, 64, 120, 28


def layered(nodes: list[dict], edges: list[dict]) -> dict[str, tuple[float, float]]:
    ids = [n["id"] for n in nodes]
    known = set(ids)
    succ: dict[str, list[str]] = {i: [] for i in ids}
    for e in edges:
        if e["source"] in known and e["target"] in known and e["source"] != e["target"]:
            succ[e["source"]].append(e["target"])
    color, back = {i: 0 for i in ids}, set()
    for root in ids:
        if color[root]:
            continue
        stack = [(root, iter(succ[root]))]
        color[root] = 1
        while stack:
            node, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                color[node] = 2
                stack.pop()
            elif color[nxt] == 1:
                back.add((node, nxt))
            elif color[nxt] == 0:
                color[nxt] = 1
                stack.append((nxt, iter(succ[nxt])))
    dag = {i: [t for t in succ[i] if (i, t) not in back] for i in ids}
    indeg = {i: 0 for i in ids}
    for i in ids:
        for t in dag[i]:
            indeg[t] += 1
    level = {i: 0 for i in ids}
    queue = [i for i in ids if indeg[i] == 0]
    while queue:
        u = queue.pop(0)
        for t in dag[u]:
            level[t] = max(level[t], level[u] + 1)
            indeg[t] -= 1
            if indeg[t] == 0:
                queue.append(t)
    layers: dict[int, list[str]] = {}
    for i in ids:
        layers.setdefault(level[i], []).append(i)
    preds: dict[str, list[str]] = {i: [] for i in ids}
    for i in ids:
        for t in dag[i]:
            preds[t].append(i)
    order = {i: k for col in layers.values() for k, i in enumerate(col)}
    for _ in range(4):
        for lv in sorted(layers)[1:]:
            layers[lv].sort(key=lambda i: sum(order[x] for x in preds[i]) / len(preds[i]) if preds[i] else order[i])
            order.update({i: k for k, i in enumerate(layers[lv])})
        for lv in sorted(layers, reverse=True)[1:]:
            layers[lv].sort(key=lambda i: sum(order[x] for x in dag[i]) / len(dag[i]) if dag[i] else order[i])
            order.update({i: k for k, i in enumerate(layers[lv])})
    tallest = max((len(c) for c in layers.values()), default=1)
    pos = {}
    for lv, col in layers.items():
        offset = (tallest - len(col)) * (NODE_H + GAP_Y) / 2
        for k, i in enumerate(col):
            pos[i] = (24 + lv * (NODE_W + GAP_X), 24 + offset + k * (NODE_H + GAP_Y))
    return pos


def clip(text: str, n: int) -> str:
    text = text or ""
    return text if len(text) <= n else text[: n - 1] + "…"


def flow_svg(a: dict, show_biz: bool, hide_fm: bool, selected: str | None) -> str:
    nodes = [n for n in a["graph"]["nodes"] if not (hide_fm and n["kind"] == "fm")]
    keep = {n["id"] for n in nodes}
    edges = [e for e in a["graph"]["edges"] if e["source"] in keep and e["target"] in keep]
    pos = layered(nodes, edges)
    width = max((x for x, _ in pos.values()), default=0) + NODE_W + 48
    height = max((y for _, y in pos.values()), default=0) + NODE_H + 48
    parts = []
    for e in edges:
        sx, sy = pos[e["source"]][0] + NODE_W, pos[e["source"]][1] + NODE_H / 2
        tx, ty = pos[e["target"]][0], pos[e["target"]][1] + NODE_H / 2
        if tx <= sx:
            d = f"M{sx},{sy} C{sx + 60},{sy - 80} {tx - 60},{ty - 80} {tx},{ty}"
        else:
            d = f"M{sx},{sy} C{sx + 50},{sy} {tx - 50},{ty} {tx},{ty}"
        hot = selected in (e["source"], e["target"])
        stroke = "var(--c-accent)" if hot else "var(--c-line-strong)"
        parts.append(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{2 if hot else 1.4}" marker-end="url(#arr)"/>')
        if e.get("label"):
            mx, my = (sx + tx) / 2, (sy + ty) / 2
            lab = esc(clip(e["label"], 16))
            parts.append(f'<rect x="{mx - len(lab) * 3.3 - 5}" y="{my - 8}" width="{len(lab) * 6.6 + 10}" height="16" rx="4" fill="var(--c-surface)" stroke="var(--c-line)"/>'
                         f'<text x="{mx}" y="{my + 3.5}" text-anchor="middle" font-size="9.5" fill="var(--c-fg-muted)">{lab}</text>')
    for n in nodes:
        x, y = pos[n["id"]]
        color = KIND_COLOR.get(n["kind"], "var(--c-accent)")
        unresolved = n.get("status") == "unresolved"
        stroke = "var(--c-accent)" if n["id"] == selected else "var(--c-bad)" if unresolved else "var(--c-line-strong)"
        dash = ' stroke-dasharray="5 4"' if unresolved else ""
        sub = esc(clip(n.get("sub") or "", 34)) if show_biz else ""
        title = esc(n["label"]) + (" · " + esc(n["sub"]) if n.get("sub") else "")
        kind = esc(n["kind"].replace("_", " ").upper())
        parts.append(f'<g><title>{title}</title>'
                     f'<rect x="{x}" y="{y}" width="{NODE_W}" height="{NODE_H}" rx="10" fill="var(--c-surface)" stroke="{stroke}" stroke-width="{2 if n["id"] == selected else 1.2}"{dash}/>'
                     f'<rect x="{x}" y="{y}" width="5" height="{NODE_H}" rx="2.5" fill="{color}"/>'
                     f'<text x="{x + 16}" y="{y + 17}" font-size="9" letter-spacing="1.2" fill="{color}" font-weight="600">{kind}</text>'
                     f'<text x="{x + NODE_W - 12}" y="{y + 17}" text-anchor="end" font-size="9.5" fill="var(--c-fg-faint)">{len(n["columns"])} cols</text>'
                     f'<text x="{x + 16}" y="{y + 36}" font-size="12.5" font-weight="600" fill="var(--c-fg)">{esc(clip(n["label"], 26))}</text>'
                     f'<text x="{x + 16}" y="{y + 53}" font-size="10.5" fill="var(--c-fg-muted)" font-family="Inter, sans-serif">{sub}</text></g>')
    defs = ('<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M0,0 L10,5 L0,10 z" fill="var(--c-line-strong)"/></marker></defs>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
            f'font-family="JetBrains Mono, monospace">{defs}{"".join(parts)}</svg>')


def standalone_svg(svg: str) -> str:
    from frontend import theme

    t = theme.get(core.ui_prefs().get("theme"))
    root = ";".join(f"--c-{k}:{v}" for k, v in t.vars.items())
    return svg.replace("<svg ", f'<svg style="{root};background:{t.vars["sunken"]}" ', 1)


def edge_input(e: dict, nodes: dict) -> str:
    ed = e.get("data") or {}
    extra = ""
    if ed.get("on"):
        extra += f'<div class="mono muted" style="font-size:11px;margin-top:6px;word-break:break-all">ON {esc(" AND ".join(ed["on"]))}</div>'
    if ed.get("cond"):
        extra += f'<div class="mono muted" style="font-size:11px;margin-top:6px;word-break:break-all">{esc(ed["cond"])}</div>'
    if ed.get("dedup"):
        extra += f'<div class="warn" style="font-size:11px;margin-top:6px">first match per ({esc(", ".join(ed["dedup"]))})</div>'
    source = esc(nodes.get(e["source"], {}).get("label", e["source"]))
    return (f'<div class="inp"><div class="between"><span class="mono fg" style="font-size:13px">{source}</span>'
            f'{badge(esc(e.get("label") or e["kind"]), "info")}</div>{extra}</div>')


def column_row(c: dict) -> str:
    name = (icon("sparkles", 11) + " " if c.get("derived") else "") + esc(c["name"].lower())
    biz = f'<div class="muted" style="font-size:11.5px;margin-top:1px">{esc(c["business_name"])}</div>' if c.get("business_name") else ""
    expr = f'<div class="mono faint" style="font-size:10.5px;word-break:break-all;margin-top:2px">{esc(c["expression"])}</div>' if c.get("expression") and c.get("derived") else ""
    return (f'<div class="colrow"><div class="between" style="display:flex;justify-content:space-between;gap:8px"><span class="mono fg" style="font-size:12.5px">{name}</span>'
            f'<span class="mono faint" style="font-size:10.5px">{esc(c.get("ddic_type") or "")}</span></div>{biz}{expr}</div>')


def node_detail(p: dict, a: dict, node: dict, nodes: dict) -> str:
    incoming = [e for e in a["graph"]["edges"] if e["target"] == node["id"]]
    outgoing = [e for e in a["graph"]["edges"] if e["source"] == node["id"]]
    table = next((t for t in a["tables"] if t["name"] == node["label"]), None) if node["kind"] == "db_table" else None
    color = KIND_COLOR.get(node["kind"], "var(--c-accent)")
    data = node.get("data") or {}
    tags = ""
    if node.get("loc"):
        tags += f'<span class="chip" style="margin:0">{icon("file", 12)}{jump(p["id"], node["loc"])}</span>'
    if table:
        tags += badge(ui.prov_label(table["provenance"]), ui.prov_tone(table["provenance"]))
        if table.get("module"):
            tags += badge(esc(table["module"]))
        if table.get("mapped_to"):
            tags += badge("read from " + esc(table["mapped_to"]), "ai")
        if not table.get("physical", True):
            tags += badge("not physical in replica", "warn")
    if node.get("status") == "unresolved":
        tags += badge("needs context or AI", "bad")
    body = ""
    if incoming:
        body += f'<div class="lab">Inputs · {len(incoming)}</div>' + "".join(edge_input(e, nodes) for e in incoming)
    if outgoing:
        feeds = "".join(f'<span class="chip">→ {esc(nodes.get(e["target"], {}).get("label", e["target"]))}</span>' for e in outgoing)
        body += f'<div class="lab">Feeds · {len(outgoing)}</div><div>{feeds}</div>'
    if data.get("where"):
        body += '<div class="lab">Filters</div>' + "".join(f'<pre style="margin-top:6px">{esc(w)}</pre>' for w in data["where"])
    if node["columns"]:
        body += f'<div class="lab">Columns · {len(node["columns"])}</div><div class="colbox">{"".join(column_row(c) for c in node["columns"])}</div>'
    if data.get("notes"):
        body += '<div class="note">' + "<br>".join(esc(x) for x in data["notes"]) + "</div>"
    if data.get("sql"):
        body += f'<div class="lab">SQL · CTE {esc(data.get("cte"))}</div><pre>{esc(data["sql"])}</pre>'
    if data.get("abap"):
        body += f'<div class="lab">ABAP</div><pre>{esc(data["abap"])}</pre>'
    sub = f'<div class="subt">{esc(node["sub"])}</div>' if node.get("sub") else ""
    kind = esc(node["kind"].replace("_", " "))
    return (f'<div class="stripe" style="background:{color}"></div><div class="top"><div class="kind" style="color:{color}">'
            f'{icon(KIND_ICON.get(node["kind"], "layers"), 14)}{kind}</div><div class="title">{esc(node["label"])}</div>{sub}'
            f'<div class="tags">{tags}</div></div><div class="sec">{body}</div>')


def flow_data(p: dict, a: dict) -> dict:
    g = a["graph"]
    nodes = {n["id"]: n for n in g["nodes"]}
    return {
        "name": p["name"].lower(),
        "nodes": [{"id": n["id"], "kind": n["kind"], "label": n["label"], "sub": n.get("sub") or "", "op": n.get("op"), "status": n.get("status"),
                   "columns": [{"n": c["name"], "t": c.get("ddic_type") or "", "b": c.get("business_name") or "", "d": bool(c.get("derived"))} for c in n["columns"]]}
                  for n in g["nodes"]],
        "edges": [{"s": e["source"], "t": e["target"], "kind": e["kind"], "label": e.get("label") or "", "on": (e.get("data") or {}).get("on") or []} for e in g["edges"]],
        "detail": {n["id"]: node_detail(p, a, n, nodes) for n in g["nodes"]},
    }


def flow(p: dict, a: dict) -> None:
    canvas.flow_canvas(flow_data(p, a), key=f"flow_{p['id']}")


# ---------------------------------------------------------------------- call tree
TREE_CSS = """<style>
.tree details > summary { list-style: none; cursor: pointer; }
.tree details > summary::-webkit-details-marker { display: none; }
.tree .node { display: flex; align-items: center; gap: 8px; border-radius: 6px; padding: 4px 8px 4px 4px; font-size: 13px; }
.tree .node > a, .tree .node > span:last-child { white-space: nowrap; }
.tree .node:hover { background: var(--c-surface-2); }
.tree .chev { display: inline-flex; width: 14px; justify-content: center; color: var(--c-fg-faint); transition: transform .15s; }
.tree details[open] > summary .chev { transform: rotate(90deg); }
.tree .kids { margin-left: 13px; padding-left: 7px; border-left: 1px solid color-mix(in oklab, var(--c-line-strong) 70%, transparent); }
.tree .dim { opacity: .55; }
.tree .hit { border-radius: 4px; background: color-mix(in oklab, var(--c-warn) 22%, transparent); padding: 0 4px; }
</style>"""
TREE_KIND = {"event": ("event", "ok"), "form": ("branch", "accent"), "function": ("function", "warn"), "method": ("method", "ai"), "group": ("branch", "accent")}


def matches(n: dict, q: str) -> bool:
    return q in n["name"].lower() or any(matches(c, q) for c in n["children"])


def tree_html(n: dict, pid: str, depth: int, q: str, hide_unused: bool, expand: str) -> str:
    kids = [c for c in n["children"] if (not hide_unused or c["reachable"]) and (not q or matches(c, q))]
    ico, tone = TREE_KIND.get(n["kind"], ("method", "accent"))
    name = esc(n["name"])
    if q and q in n["name"].lower():
        name = f'<span class="hit">{name}</span>'
    tags = badge(esc(n["fm_kind"]), FM_TONE.get(n["fm_kind"], "slate")) if n.get("fm_kind") else ""
    tags += "" if n["reachable"] else badge("unused")
    tags += badge("recursive", "warn") if n.get("recursive") else ""
    more = f'<span class="faint" style="font-size:11px">+{len(kids)}</span>' if kids else ""
    loc = f'<span style="margin-left:auto">{jump(pid, n.get("loc"))}</span>' if n.get("loc") else ""
    chev = icon("chev", 13) if kids else ""
    row = (f'<span class="chev">{chev}</span><span class="{tone}">{icon(ico, 15)}</span><span class="mono fg">{name}</span>'
           f'<span class="faint" style="font-size:11px">{esc(n["kind"])}</span>{tags}{more}{loc}')
    cls = "node" if n["reachable"] else "node dim"
    if not kids:
        return f'<div class="{cls}">{row}</div>'
    opened = q or expand == "all" or (expand == "auto" and depth < 3 and n["id"] != "__unused__")
    inner = "".join(tree_html(c, pid, depth + 1, q, hide_unused, expand) for c in kids)
    return f'<details{" open" if opened else ""}><summary class="{cls}">{row}</summary><div class="kids">{inner}</div></details>'


def call_tree(p: dict, a: dict) -> None:
    st.markdown(TREE_CSS, unsafe_allow_html=True)
    with st.container(horizontal=True, gap="medium", key="ct_row"):
        with ui.panel("ct_main"):
            ui.heading("Execution order", "Events run top to bottom; greyed routines are never called", "branch")
            with st.container(horizontal=True, vertical_alignment="center", key="ct_tools"):
                q = st.text_input("Find routine", placeholder="Find routine", key="ct_q", label_visibility="collapsed", icon=":material/search:", width=240).strip().lower()
                hide = st.toggle("Hide unused routines", key="ct_hide")
                legend = "".join(f'<span class="row" style="gap:4px;flex-wrap:nowrap"><span class="{TREE_KIND[k][1]}">{icon(TREE_KIND[k][0], 13)}</span>{k}</span>'
                                 for k in ("event", "form", "method", "function"))
                ui.html(f'<div class="row faint" style="gap:12px;justify-content:flex-end;font-size:11px">{legend}</div>')
                if st.button("", icon=":material/unfold_more:", type="tertiary", key="ct_all", help="Expand all"):
                    st.session_state.ct_expand = "all"
                if st.button("", icon=":material/unfold_less:", type="tertiary", key="ct_none", help="Collapse all"):
                    st.session_state.ct_expand = "none"
            expand = st.session_state.get("ct_expand", "auto")
            roots = [n for n in a["call_tree"] if (not hide or n["reachable"]) and (not q or matches(n, q))]
            body = "".join(tree_html(n, p["id"], 0, q, hide, expand) for n in roots) or '<div class="faint" style="padding:30px;text-align:center">Nothing matches.</div>'
            ui.html(f'<div class="tree scroll" style="max-height:calc(100vh - 330px);min-height:360px;margin:0 -8px">{body}</div>')
        with st.container(key="ct_side"):
            kinds: dict[str, int] = {}
            for r in a["routines"]:
                kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
            unused = [r for r in a["routines"] if not r["reachable"]]
            reached = len(a["routines"]) - len(unused)
            ring = ui.ring(reached / len(a["routines"]) if a["routines"] else 0, 84, 8,
                           inner=f'<span class="tabular fg" style="font-size:18px;font-weight:600">{reached}</span><span class="faint" style="font-size:10px">reached</span>')
            rows = "".join(f'<div class="between" style="font-size:13px"><span class="muted">{esc(k)}</span><b class="tabular fg">{v}</b></div>'
                           for k, v in sorted(kinds.items(), key=lambda x: -x[1]))
            ui.html(ui.card("Routines", f'<div class="row" style="gap:16px;flex-wrap:nowrap">{ring}<div style="flex:1;display:grid;gap:6px">{rows}</div></div>'))
            fms = [c for c in a["calls"] if c["kind"] == "function"]
            fm_rows = "".join(f'<div class="between" style="padding:4px 6px;font-size:12px"><span class="mono fg" style="overflow:hidden;text-overflow:ellipsis">{esc(c["target"])}</span>'
                              f'{badge(esc(c.get("fm_kind") or "fm"), FM_TONE.get(c.get("fm_kind"), "slate"))}</div>' for c in fms[:60])
            ui.html(ui.card("Function module calls", f'<div class="scroll" style="max-height:220px">{fm_rows or "<span class=faint>None.</span>"}</div>',
                            f"{len(fms)} call(s)"))
            if unused:
                un = "".join(f'<div class="between" style="padding:4px 6px;font-size:12px"><span class="mono muted">{esc(r["name"])}</span><span class="row" style="gap:8px">'
                             f'<span class="faint" style="font-size:11px">{r["statements"]} stmts</span>{jump(p["id"], r.get("loc"))}</span></div>' for r in unused[:80])
                ui.html(ui.card("Never called", f'<div class="scroll" style="max-height:220px">{un}</div>', "Listed, not converted"))


# ---------------------------------------------------------------------- source
TOKEN = re.compile(r"('(?:[^']|'')*'|`[^`]*`|\|[^|]*\||\b\d+\b|[A-Za-z_][A-Za-z0-9_\-/]*)")


def highlight(line: str) -> str:
    if line.startswith("*"):
        return f'<span class="cm">{esc(line)}</span>'
    code, comment, quote = line, "", None
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "'`|":
            quote = ch
        elif ch == '"':
            code, comment = line[:i], line[i:]
            break
    out, last = [], 0
    for m in TOKEN.finditer(code):
        out.append(esc(code[last:m.start()]))
        tok = m.group(0)
        if tok[0] in "'`|":
            out.append(f'<span class="str">{esc(tok)}</span>')
        elif tok.isdigit():
            out.append(f'<span class="num">{tok}</span>')
        elif tok.upper() in ABAP_KEYWORDS:
            out.append(f'<span class="kw">{esc(tok)}</span>')
        else:
            out.append(esc(tok))
        last = m.end()
    out.append(esc(code[last:]))
    if comment:
        out.append(f'<span class="cm">{esc(comment)}</span>')
    return "".join(out)


@st.cache_data(show_spinner=False, max_entries=8)
def project_sources(pid: str, stamp: str) -> dict[str, str]:
    return core.sources(pid)


def source_view(p: dict, a: dict) -> None:
    sources = project_sources(p["id"], p["updated"])
    if not sources:
        ui.empty("No sources stored for this project.", "code")
        return
    files = list(sources)
    r = ui.route()
    focus_file = r.get("file")
    focus_line = int(r.get("line") or 0)
    slices = {f: [x for x in a["slice"] if x["file"] == f] for f in files}
    totals = {f: sum(x["end"] - x["start"] + 1 for x in slices[f]) for f in files}
    counts = {f: sources[f].count("\n") + 1 for f in files}
    with st.container(horizontal=True, gap="medium", key="src_row"):
        side = st.container(width=250, key="src_side")
        main = st.container(key="src_main")
    with side:
        with ui.panel("src_files"):
            ui.html(f'<div class="between"><span class="eyebrow faint">Files</span><span class="mono faint" style="font-size:11px">{len(files)}</span></div>')
            fq = st.text_input("Filter files", key="src_fq", placeholder="Filter files", label_visibility="collapsed") if len(files) > 6 else ""
            shown = [f for f in files if not fq or fq.lower() in f.lower()] or files
            file = st.radio("File", shown, index=shown.index(focus_file) if focus_file in shown else 0, key=f"src_file_{p['id']}_{focus_file or ''}",
                            label_visibility="collapsed", format_func=lambda f: f"{f}  ·  {totals[f]}/{counts[f]}")
            ui.html('<div class="faint" style="font-size:11px;margin-top:8px"><span style="display:inline-block;width:4px;height:10px;border-radius:2px;'
                    'background:var(--c-accent);vertical-align:middle;margin-right:6px"></span>Marked lines feed the output.</div>')
    with main:
        lines = sources[file].split("\n")
        marked = [False] * (len(lines) + 2)
        for x in slices[file]:
            for i in range(max(1, x["start"]), min(len(lines), x["end"]) + 1):
                marked[i] = True
        bar = st.container(horizontal=True, vertical_alignment="center", key="src_bar")
        bar.html(f"<div class='row' style='gap:10px;flex-wrap:nowrap'><span class='chip' style='background:var(--c-surface)'>{icon('code', 13)} {esc(file)}</span>"
                 f"<span class='muted' style='font-size:12px;white-space:nowrap'>{len(lines):,} lines · <b class='accent'>{totals[file]:,}</b> in slice</span></div>")
        only = bar.toggle("Only lines that affect the output", key="src_only")
        c3 = bar
        window, start = 1500, 1
        focused = focus_file == file and focus_line > 0
        if len(lines) > window:
            starts = list(range(1, len(lines) + 1, window))
            first = (focus_line - 1) // window if focused else 0
            start = c3.selectbox("Lines", starts, index=min(len(starts) - 1, first), key=f"src_win_{file}", label_visibility="collapsed", width=200,
                                 format_func=lambda s: f"lines {s:,}–{min(s + window - 1, len(lines)):,}")
        rows = []
        for no in range(start, min(len(lines), start + window - 1) + 1):
            if only and not marked[no]:
                continue
            cls = "hl" if focused and no == focus_line else "sl" if marked[no] else ""
            rows.append(f'<tr class="{cls}"><td class="n">{no}</td><td>{highlight(lines[no - 1]) or " "}</td></tr>')
        empty_row = '<tr><td class="n"></td><td class="faint">No lines in the slice for this file.</td></tr>'
        ui.html(f'<div class="code-view"><table>{"".join(rows) or empty_row}</table></div>')
        if focused:
            st.caption(f"Jumped to line {focus_line} (highlighted).")


# ---------------------------------------------------------------------- context
def name_rows(a: dict, ctx: dict, q: str) -> list[dict]:
    rows = []
    for t in a["tables"]:
        if t["reads"] or t["writes"]:
            rows.append({"SAP name": t["name"], "Kind": "table", "Current": t.get("business_name") or t["description"]})
            rows += [{"SAP name": f"{t['name']}-{c['name']}", "Kind": "column", "Current": c.get("business_name") or c["description"]} for c in t["columns"]]
    for c in (a.get("output") or {}).get("columns", []):
        if c.get("derived"):
            rows.append({"SAP name": f"OUTPUT-{c['name']}", "Kind": "calculated", "Current": c.get("business_name") or c["label"]})
    if q:
        rows = [r for r in rows if q.lower() in r["SAP name"].lower() or q.lower() in (r["Current"] or "").lower()]
    for r in rows:
        r["Business name"] = ctx["business_names"].get(r["SAP name"], "")
    return rows


def text_of(v) -> str:
    return v.strip() if isinstance(v, str) else ""


def review(p: dict, a: dict) -> None:
    pid = p["id"]
    ctx = p["context"]
    left, right = st.columns([2, 1])
    with left:
        with ui.panel("pj7"):
            ui.heading("Business names", "Plain-English glossary; pre-filled from the dictionary and the schema", "tag")
            q = st.text_input("Filter", placeholder="Filter", key="rv_filter", label_visibility="collapsed", icon=":material/search:")
            frame = pd.DataFrame(name_rows(a, ctx, q), columns=["SAP name", "Kind", "Current", "Business name"])
            edited = st.data_editor(frame, key=f"rv_names_{pid}_{q}", height=560, width="stretch", hide_index=True, disabled=["SAP name", "Kind", "Current"],
                                    column_config={"Business name": st.column_config.TextColumn(help="Your name for it; empty keeps the current one")})
    with right:
        missing = {c["target"]: c["fm_kind"] for c in a["calls"]
                   if c["kind"] == "function" and c["reachable"] and c.get("fm_kind") in ("unknown", "opaque", "lookup")}
        hints = dict(ctx["fm_hints"])
        sources = dict(ctx["fm_sources"])
        with ui.panel("pj8"):
            ui.heading("Function modules needing context", "", "upload")
            if not missing:
                st.caption("All function modules are understood.")
            for fm, kind in missing.items():
                state = '<div class="ok" style="font-size:12px">source provided</div>' if fm in sources else \
                    '<div class="faint" style="font-size:12px">Upload its source, or describe its result as a SQL expression:</div>'
                ui.html(f'<div class="between" style="margin-top:6px"><span class="mono fg" style="font-size:13px">{esc(fm)}</span>{badge(esc(kind), "warn")}</div>{state}')
                hints[fm] = st.text_input(f"Hint for {fm}", value=hints.get(fm, ""), placeholder="e.g. UPPER({INPUT})", key=f"rv_hint_{pid}_{fm}", label_visibility="collapsed")
            for f in st.file_uploader("Upload function module source (.abap)", type=["abap", "txt"], accept_multiple_files=True, key=f"rv_fm_{pid}") or []:
                text = f.getvalue().decode("utf-8", errors="replace")
                m = re.search(r"FUNCTION\s+([A-Za-z0-9_/]+)\s*\.", text, re.I)
                sources[(m.group(1) if m else re.sub(r"\.\w+$", "", f.name)).upper()] = text
            if sources:
                keep = st.multiselect("Stored FM sources (remove to drop)", list(sources), default=list(sources), key=f"rv_srcs_{pid}")
                sources = {k: v for k, v in sources.items() if k in keep}
        with ui.panel("pj9"):
            ui.heading("Table renames", "SAP table → physical object in Snowflake (overrides the pattern)", "database")
            ren = st.data_editor(pd.DataFrame([{"SAP table": k, "Snowflake object": v} for k, v in ctx["table_renames"].items()], columns=["SAP table", "Snowflake object"]),
                                 num_rows="dynamic", key=f"rv_ren_{pid}", width="stretch", hide_index=True,
                                 column_config={"SAP table": st.column_config.TextColumn(help="e.g. VBAK"),
                                                "Snowflake object": st.column_config.TextColumn(help="e.g. RAW.SAP.VBAK_V")})
        with ui.panel("pj10"):
            ui.heading("Result table", "Which internal table is the report's output", "monitor")
            cands = a.get("output_candidates") or []
            cur = ctx.get("output_table") or ""
            auto = (a.get("output") or {}).get("table") or "none found"
            output = st.selectbox("Result table", [""] + cands, index=([""] + cands).index(cur) if cur in cands else 0, key=f"rv_out_{pid}",
                                  label_visibility="collapsed", format_func=lambda x: x.lower() if x else f"automatic ({auto})")
        with ui.panel("pj11"):
            ui.heading("Notes for the AI (optional)", "", "sparkles")
            notes = st.text_area("Notes", value=ctx.get("notes") or "", height=110, key=f"rv_notes_{pid}", label_visibility="collapsed",
                                 placeholder="e.g. Z_GET_PRICE returns the latest KBETR from A305 for the material")
        if st.button("Save context and re-analyze", icon=":material/save:", type="primary", width="stretch", key=f"rv_save_{pid}"):
            names = dict(ctx["business_names"])
            for _, row in edited.iterrows():
                value = text_of(row["Business name"])
                if value:
                    names[row["SAP name"]] = value
                else:
                    names.pop(row["SAP name"], None)
            renames = {text_of(row["SAP table"]).upper(): text_of(row["Snowflake object"]) for _, row in ren.iterrows()
                       if text_of(row["SAP table"]) and text_of(row["Snowflake object"])}
            core.update_project(pid, context={"fm_sources": sources, "fm_hints": {k: v for k, v in hints.items() if v.strip()}, "business_names": names,
                                              "table_renames": renames, "notes": notes, "output_table": output or None})
            st.session_state[f"pending_{pid}"] = ("analyze", False)
            ui.notify("ok", "Context saved", "Re-analyzing with your additions…")
            st.rerun()


# ---------------------------------------------------------------------- SQL
def step_card(i: int, r: dict) -> str:
    stripe = "var(--c-ai)" if r.get("llm_model") else "var(--c-ok)" if r["status"] == "deterministic" else "var(--c-bad)" if r["status"] == "failed" else "var(--c-warn)"
    if r.get("llm_model"):
        tag = badge(icon("sparkles", 11) + esc(r["llm_model"]), "ai")
    else:
        tag = badge("rules" if r["status"] == "deterministic" else ui.status_label(r["status"]), ui.status_tone(r["status"]))
    inputs = ", ".join(x.split(".")[-1] for x in r["inputs"]) or "–"
    notes = f'<div class="warn" style="margin-top:4px;font-size:11px">{esc("; ".join(r["notes"][:2]))}</div>' if r["notes"] else ""
    return (f'<div style="position:relative;overflow:hidden;border-radius:10px;border:1px solid var(--c-line);background:var(--c-sunken);padding:10px 12px 10px 16px">'
            f'<span style="position:absolute;left:0;top:0;bottom:0;width:3px;background:{stripe}"></span><div class="between"><span class="row" style="gap:8px;min-width:0">'
            f'<span class="mono faint tabular" style="font-size:10.5px">{i + 1:02d}</span><span class="mono fg" style="font-size:13px;font-weight:500">{esc(r["cte"])}</span></span>{tag}</div>'
            f'<div class="muted" style="margin-top:2px;font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{esc(r["label"])} · from {esc(inputs)}</div>{notes}</div>')


def convert_panel(p: dict, a: dict) -> None:
    pid = p["id"]
    opts = dict(p["convert"])
    d = core.defaults()
    ms = [m for m in ui.models() if m["kind"] != "embedding"]
    ids = [m["id"] for m in ms]
    by_id = {m["id"]: m for m in ms}
    s = a["settings"]

    def model_name(i: str) -> str:
        if not i:
            return f"default ({d['model']})"
        m = by_id[i]
        return i + ("" if m["private"] else " · external") + ("" if m["available"] else " · no key")

    with st.container(horizontal=True, gap="medium", key="cv_row"):
        left = st.container(width=300, key="cv_left")
        right = st.container(key="flex_cv")
    with left:
        with ui.panel("pj12"):
            ui.heading("Output", "", "monitor")
            opts["mode"] = st.segmented_control("Output", ["select", "view"], default=opts["mode"], key=f"cv_mode_{pid}", label_visibility="collapsed", width="stretch",
                                                format_func=lambda x: {"select": "CTE query", "view": "CREATE VIEW"}[x]) or "select"
            if opts["mode"] == "view":
                target = ".".join(x for x in (s.get("view_database") or s.get("target_database"), s.get("view_schema") or s.get("target_schema")) if x)
                opts["view_name"] = st.text_input("View name", value=opts.get("view_name") or "", placeholder=f"{a['name']}_V", key=f"cv_view_{pid}",
                                                  help=f"Created in {target or 'the current schema'}; change it in project settings. A fully qualified name is kept as is.").upper() or None
            else:
                opts["view_name"] = None
        with ui.panel("pj13"):
            ui.heading("AI for unresolved steps", "", "sparkles")
            opts["use_llm"] = st.toggle("Use a model where rules are not enough", value=opts["use_llm"], key=f"cv_llm_{pid}")
            cur = opts.get("model") or ""
            opts["model"] = st.selectbox("Model", [""] + ids, index=([""] + ids).index(cur) if cur in ids else 0, key=f"cv_model_{pid}",
                                         label_visibility="collapsed", format_func=model_name) or None
            if p["settings"].get("confidential", s.get("confidential")):
                st.markdown("<div class='warn' style='font-size:11.5px'>Confidential project: only Cortex and private models are allowed.</div>", unsafe_allow_html=True)
            n = a["stats"]["llm_relations"]
            st.caption("This program converts with rules only; no model call is needed." if n == 0 else f"{n} step(s) go to the model, one small prompt each, each compile-checked.")
        if st.button("Convert", icon=":material/auto_fix_high:", type="primary", width="stretch", key=f"cv_go_{pid}"):
            core.update_project(pid, convert=opts)
            if run_stage(pid, "convert", p["name"], opts):
                st.rerun()
        unresolved = a.get("unresolved") or []
        if unresolved:
            ui.html(ui.callout("warn", "<b class='warn'>Still unresolved</b><br>" + "<br>".join(f"• {esc(u)}" for u in unresolved[:5])))
    with right:
        sql = a.get("sql") or ""
        with ui.panel("pj14"):
            meta = f"{len(sql.splitlines()):,} lines · {len(a['relations'])} CTE steps" if sql else ""
            ui.html(f'<div class="between"><div class="row" style="gap:8px"><span style="font-size:13.5px;font-weight:600;color:var(--c-fg)">Snowflake SQL</span>'
                    f'{badge(ui.status_label(a["sql_status"]), ui.status_tone(a["sql_status"]))}</div><span class="faint" style="font-size:12px">{meta}</span></div>')
            if sql:
                st.code(sql, language="sql", line_numbers=True, height=560)
                got = core.download(pid, "sql")
                if got:
                    st.download_button("Download .sql", data=got[1], file_name=got[0], mime=got[2], icon=":material/download:", key=f"cv_dl_{pid}")
            else:
                reason = next((f["message"] for f in a["findings"] if f["code"] in ("NO_DATA_READ", "SELECT_NOT_REACHED")),
                              "no output table was found. Choose a result table in Context.")
                ui.empty(f"No SQL: {esc(reason)}", "database")
        cards = "".join(step_card(i, r) for i, r in enumerate(a["relations"]))
        grid = f'<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:8px">{cards}</div>' if cards else '<span class="faint">No steps.</span>'
        ui.html(ui.card("Steps", grid, "One CTE per change of an internal table, in execution order", style="margin-top:14px"))


# ---------------------------------------------------------------------- validate
PLAN = ["SQL syntax (sqlglot)", "No leftover placeholders", "Referenced tables exist in the source", "Compile on Snowflake (EXPLAIN on stub tables)",
        "Row-by-row comparison to a reference"]


def check_row(i: int, name: str, ok, detail: str) -> str:
    if ok == "plan":
        mark, tag = f'<span class="dot">{i + 1}</span>', ""
    elif ok is True:
        mark, tag = f'<span class="ok">{icon("okcircle", 21)}</span>', badge("pass", "ok")
    elif ok is False:
        mark, tag = f'<span class="bad">{icon("xcircle", 21)}</span>', badge("fail", "bad")
    else:
        mark, tag = f'<span class="faint">{icon("slash", 21)}</span>', badge("skipped")
    det = f'<div class="mono muted" style="margin-top:4px;font-size:11.5px;line-height:1.55;word-break:break-word">{esc(detail)}</div>' if detail else ""
    return (f'<li><span style="position:relative;z-index:1;background:var(--c-surface);border-radius:99px;display:flex">{mark}</span>'
            f'<div style="flex:1;min-width:0;border-radius:10px;border:1px solid var(--c-line);background:var(--c-sunken);padding:9px 14px"><div class="between">'
            f'<span style="font-size:13.5px;font-weight:500;color:var(--c-fg)">{esc(name)}</span>{tag}</div>{det}</div></li>')


def comparison(res: dict | None) -> str:
    if not res:
        return '<span class="muted">Run validation first.</span>'
    if not res.get("gold_available"):
        return ('<div class="hatch muted" style="border-radius:10px;border:1px dashed var(--c-line-strong);padding:16px;font-size:13px">No reference SQL for this program. '
                "Put your team's manual conversion in a knowledge pack's <span class=\"mono fg\">gold/</span> folder to compare results row by row.</div>")
    cmp = res.get("compare") or {}
    if cmp.get("error"):
        return f'<div class="bad" style="font-size:13px">{esc(cmp["error"])}</div>'
    if cmp.get("ok"):
        verdict = f'<div class="row ok" style="gap:8px;font-size:17px;font-weight:600">{icon("okcircle", 22)}Identical results</div>'
    else:
        verdict = f'<div class="row bad" style="gap:8px;font-size:17px;font-weight:600">{icon("xcircle", 22)}Results differ</div>'
    cells = "".join(f'<div style="background:var(--c-surface);padding:12px"><div class="eyebrow faint" style="font-size:10px">{k}</div>'
                    f'<div class="tabular fg" style="font-size:22px;font-weight:600;margin-top:4px">{"–" if v is None else v}</div></div>'
                    for k, v in [("Generated rows", cmp.get("generated_rows")), ("Expected rows", cmp.get("expected_rows")),
                                 ("Missing", cmp.get("missing")), ("Extra", cmp.get("extra"))])
    return (f'{verdict}<div style="display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--c-line);border:1px solid var(--c-line);'
            f'border-radius:10px;overflow:hidden;margin-top:14px">{cells}</div>')


def validate_panel(p: dict) -> None:
    pid = p["id"]
    res = core.last_validation(pid)
    has_sql = bool(core.download(pid, "sql"))
    checks_ = (res or {}).get("checks", [])
    passed = sum(1 for c in checks_ if c["ok"] is True)
    failed = sum(1 for c in checks_ if c["ok"] is False)
    skipped = sum(1 for c in checks_ if c["ok"] is None)
    tone = "fg-faint" if not res else "ok" if res["ok"] else "bad"
    ico = "shield" if not res else "okcircle" if res["ok"] else "xcircle"
    title = "Not run yet" if not res else "All checks passed" if res["ok"] else "Some checks need attention"
    sub = f"{passed} passed · {failed} failed · {skipped} skipped" if res else "Compiles against empty stub tables built from the schema metadata, so no SAP data is needed."
    border = "var(--c-line)" if not res else f"color-mix(in oklab,var(--c-{tone}) 40%,transparent)"
    head, act = st.columns([4, 1], vertical_alignment="center")
    head.markdown(f'<div class="card" style="position:relative;overflow:hidden;padding:22px;border-color:{border}">'
                  f'<div class="dot-grid" style="position:absolute;inset:0;opacity:.4;-webkit-mask-image:linear-gradient(90deg,transparent 45%,black)"></div>'
                  f'<div class="row" style="position:relative;gap:20px;flex-wrap:nowrap"><span style="display:flex;width:60px;height:60px;align-items:center;justify-content:center;'
                  f'border-radius:12px;border:1px solid var(--c-line);color:var(--c-{tone});background:var(--c-surface-2)">{icon(ico, 30)}</span><div>'
                  f'<div class="eyebrow faint">Validation</div><div style="font-size:20px;font-weight:600;color:var(--c-fg);margin-top:4px">{title}</div>'
                  f'<div class="muted" style="font-size:13px;margin-top:4px">{sub}</div></div></div></div>', unsafe_allow_html=True)
    if act.button("Run again" if res else "Run validation", icon=":material/play_arrow:", type="primary", width="stretch", disabled=not has_sql,
                  key=f"vl_go_{pid}", help=None if has_sql else "Convert the project first"):
        if run_stage(pid, "validate", p["name"]):
            st.rerun()
    st.write("")
    left, right = st.columns([2, 1])
    items = [(c["name"], c["ok"], c.get("detail") or "") for c in checks_] if res else [(n, "plan", "") for n in PLAN]
    rows = "".join(check_row(i, *item) for i, item in enumerate(items))
    left.markdown(ui.card("Checks", f'<ol class="steps">{rows}</ol>', "In the order they run"), unsafe_allow_html=True)
    right.markdown(ui.card("Result comparison", comparison(res), "Generated SQL vs reference SQL"), unsafe_allow_html=True)
