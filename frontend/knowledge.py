"""Knowledge module: overview, tables, function modules, add knowledge (six methods with preview), gaps and library files."""

from __future__ import annotations

import re

import pandas as pd
import streamlit as st

from backend import core
from backend import knowledge as kn
from frontend import ui
from frontend.ui import badge, esc, icon

TABS = [("overview", "Overview", ":material/local_library:"), ("tables", "Tables", ":material/database:"), ("fms", "Function modules", ":material/code:"),
        ("add", "Add knowledge", ":material/add:"), ("gaps", "Gaps", ":material/warning:"), ("files", "Library files", ":material/description:")]
DDIC_TYPES = ["CHAR", "NUMC", "DATS", "TIMS", "CURR", "QUAN", "DEC", "INT1", "INT2", "INT4", "INT8", "CUKY", "UNIT", "LANG", "CLNT", "FLTP", "D16N", "STRG",
              "SSTR", "RAW", "TIMESTAMP"]
FM_KIND_HELP = {
    "expression": "Pure function of its inputs; one Snowflake expression reproduces it",
    "lookup": "Reads master / customizing data; describe the equivalent join",
    "ui": "Dialogs, popups, progress indicators; no data effect",
    "output_sink": "Displays an internal table (ALV / list output)",
    "side_effect": "Writes, sends, locks or commits; flagged, no data",
    "opaque": "Real logic one SQL expression cannot reproduce; flagged for review",
    "custom": "Custom FM whose ABAP source you provide; translated like program code",
}
METHODS = [
    ("ddic", "layers", "SAP dictionary replica", "DD03L / DD04T / DD02T replicated in Snowflake: keys, types, lengths and labels exactly as in SE11.", ("exact", "ok"), ("tables",)),
    ("snowflake", "database", "Snowflake schema", "Read columns, types and comments of tables in any database.schema (your raw layer).", ("columns exact", "ok"), ("tables",)),
    ("paste", "upload", "Paste or upload", "SE11 / SE16 exports, CSV, Excel, JSON, YAML, markdown tables, FM source, zipped packs.", ("as provided", "info"), ("tables", "fms")),
    ("prompt", "clipboard", "Ask any AI", "Copy a ready prompt into ChatGPT, Copilot or Gemini (or send to an SAP colleague), paste the answer back.", ("review", "warn"), ("tables", "fms")),
    ("ai", "bot", "AI proposal", "Your configured model proposes definitions from the names alone. Marked AI-proposed, never complete.", ("review", "warn"), ("tables", "fms")),
    ("manual", "pen", "Write it yourself", "Table editor and function-module editor with every field the converter uses.", ("as written", "info"), ("tables", "fms")),
]
LADDER = [("snowflake_catalog", "database", "Snowflake schema", "Live columns of the raw layer, read at every analysis", "ok"),
          ("client_pack", "package", "Client packs", "Per-project folders: DD03L export, FM catalog, past conversions", "ai"),
          ("library", "library", "Your library", "Everything added on this page; loaded into every project", "accent"),
          ("builtin", "book", "SAP dictionary", "Built-in standard tables across FI, CO, SD, MM, PP, PM, PS, QM, HR, Basis", "info"),
          ("inferred", "code", "The code itself", "Fields inferred from wa-field / alias~field usage; marked “from code”", "warn")]
ACCEPT = ["csv", "tsv", "txt", "xlsx", "xlsm", "json", "yaml", "yml", "md", "abap", "zip"]


def split_names(s: str) -> list[str]:
    out = []
    for x in re.split(r"[\s,;|]+", (s or "").upper()):
        x = x.strip()
        if re.fullmatch(r"[A-Z0-9_/]{1,40}", x) and x not in out:
            out.append(x)
    return out


def fmt_type(f: dict) -> str:
    t = f.get("ddic_type") or "?"
    if f.get("length"):
        t += f"({f['length']}" + (f",{f['decimals']}" if f.get("decimals") else "") + ")"
    return t


@st.cache_data(ttl=30, show_spinner=False)
def load_all(rev: int) -> dict:
    return {"overview": kn.overview(), "tables": kn.tables(), "fms": kn.fms(), "gaps": kn.gaps()}


def changed() -> None:
    st.session_state.kn_rev = st.session_state.get("kn_rev", 0) + 1


def render(r: dict) -> None:
    tab = r.get("tab") if r.get("tab") in dict((t[0], t) for t in TABS) else "overview"
    data = load_all(st.session_state.get("kn_rev", 0))
    gaps = data["gaps"]
    open_gaps = sum(1 for g in gaps["tables"] if not g["filled"] and g["reason"] == "missing") + sum(1 for g in gaps["fms"] if not g["filled"])
    ui.page_header("Knowledge", "library", "Teach it any table, once",
                   "Nothing here is required: columns come live from your Snowflake raw layer. Add what the converter cannot see (descriptions, keys, custom function "
                   "modules, tables outside Snowflake) and every project uses it from the next analysis.", tools=True)
    counts = {"tables": len(data["tables"]), "fms": len(data["fms"]), "gaps": open_gaps or None}
    with ui.page_tools():
        for tid, label, ico in TABS:
            text = f"{label} · {counts[tid]}" if counts.get(tid) else label
            if st.button(text, key=f"kt_{tid}", icon=ico, type="tertiary"):
                ui.go("knowledge", tab=tid)
        ui.html('<div style="flex:1"></div>')
        st.download_button("Export library", data=kn.export_library(), file_name="tcb_knowledge_library.zip", mime="application/zip", icon=":material/download:",
                           key="kn_export")
        if st.button("Add knowledge", icon=":material/add:", type="primary", key="kn_add_top"):
            ui.go("knowledge", tab="add")
    st.markdown("<style>[class*='st-key-kt_'] button{white-space:nowrap;border:1px solid transparent}[class*='st-key-kt_'] p{font-size:13px}"
                ".st-key-kt_" + tab + " button{background:var(--c-surface)!important;color:var(--c-fg)!important;border-color:var(--c-line-strong)!important;"
                "box-shadow:0 1px 2px var(--c-shadow)}.st-key-kt_" + tab + " [data-testid='stIconMaterial']{color:var(--c-accent)}</style>",
                unsafe_allow_html=True)
    if tab == "overview":
        overview_tab(data, open_gaps)
    elif tab == "tables":
        tables_tab(data["tables"], r.get("t"))
    elif tab == "fms":
        fms_tab(data["fms"])
    elif tab == "add":
        add_tab(r, {t["name"]: t["source"] for t in data["tables"]})
    elif tab == "gaps":
        gaps_tab(gaps)
    else:
        files_tab(data["overview"])


# ---------------------------------------------------------------------- overview
def overview_tab(data: dict, open_gaps: int) -> None:
    ov, tables, gaps = data["overview"], data["tables"], data["gaps"]
    s = ov["stats"]
    lib = ov["by_source"].get("library", 0) + ov["by_source"].get("ai_generated", 0)
    stats = "".join(f'<div style="min-width:0"><div class="display tabular" style="font-size:40px;line-height:1;color:var(--c-side-fg)">{v}</div>'
                    f'<div style="margin-top:6px;font-size:12px;color:var(--c-side-muted)">{l}</div></div>'
                    for v, l in [(s["tables"], "tables"), (ui.compact(s["fields"]), "fields"), (s["function_modules"], "function modules"), (lib, "in your library")])
    top = [("table", g["name"], len(g["projects"])) for g in gaps["tables"] if not g["filled"] and g["reason"] == "missing"][:4]
    top += [("FM", g["name"], len(g["projects"])) for g in gaps["fms"] if not g["filled"]][:3]
    gap_rows = "".join(f'<div class="row" style="gap:8px;font-size:12px;flex-wrap:nowrap"><span style="width:40px;font-size:10px;text-transform:uppercase;letter-spacing:.1em;'
                       f'color:var(--c-side-muted)">{k}</span><span class="mono" style="color:var(--c-side-fg)">{esc(n)}</span><span style="margin-left:auto;color:var(--c-side-muted)">'
                       f'{ui.plural(p, "project")}</span></div>' for k, n, p in top)
    if not open_gaps:
        gap_rows = (f'<div class="row" style="gap:8px;font-size:12.5px;color:var(--c-side-muted)"><span style="color:var(--c-side-accent)">{icon("okcircle")}</span>'
                    'Every referenced table and FM resolves.</div>')
    fill = '<a class="hbtn p" style="margin-top:16px;padding:7px 12px;font-size:12.5px" href="?page=knowledge&tab=gaps">Fill gaps →</a>' if open_gaps else ""
    st.markdown("<style>.hbtn{display:inline-flex;align-items:center;gap:8px;border-radius:9px;font-weight:600;text-decoration:none!important}"
                ".hbtn.p{background:var(--c-ink-btn);color:var(--c-ink-btn-fg)!important}.hbtn.s{border:1px solid var(--c-side-line);color:var(--c-side-fg)!important}</style>",
                unsafe_allow_html=True)
    ui.html(f'<div class="ink grain fade-up" style="position:relative;overflow:hidden;border-radius:18px"><div class="ink-grid" style="position:absolute;inset:0;opacity:.6;'
            f'-webkit-mask-image:radial-gradient(ellipse at top right,black,transparent 70%)"></div><div style="position:relative;display:grid;grid-template-columns:1.3fr 1fr;gap:32px;padding:28px">'
            f'<div><div class="eyebrow" style="color:var(--c-side-accent)">Coverage</div><div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px 24px;margin-top:12px">{stats}</div>'
            f'<p style="margin-top:24px;max-width:560px;font-size:13.5px;line-height:1.6;color:var(--c-side-muted)">A new T-code with tables nobody has seen before still converts: columns '
            f'come from Snowflake or the code. Adding a table here makes its names, keys and types exact, for every project, without changing the product.</p>'
            f'<div class="row" style="gap:8px;margin-top:18px"><a class="hbtn p" style="padding:8px 14px;font-size:13px" href="?page=knowledge&tab=add">{icon("plus")}Add tables or FMs</a>'
            f'<a class="hbtn s" style="padding:8px 14px;font-size:13px" href="?page=knowledge&tab=tables">{icon("search")}Browse dictionary</a></div></div>'
            f'<div style="border-radius:14px;border:1px solid var(--c-side-line);background:rgba(0,0,0,.15);padding:20px"><div class="between"><span class="eyebrow" style="color:var(--c-side-muted)">'
            f'Open gaps</span><span style="font-size:11px;color:var(--c-side-muted)">{gaps["projects_scanned"]} analysed projects</span></div><div class="row" style="gap:8px;margin-top:8px;align-items:baseline">'
            f'<span class="display tabular" style="font-size:44px;line-height:1;color:var(--c-{"side-accent" if open_gaps else "side-fg"})">{open_gaps}</span>'
            f'<span style="font-size:12.5px;color:var(--c-side-muted)">tables / FMs no source could resolve</span></div><div style="display:grid;gap:6px;margin-top:14px">{gap_rows}</div>{fill}</div></div></div>')

    def ladder_badge(k: str) -> str:
        if k == "builtin":
            return f'{ov["by_source"].get("builtin", 0)} tables'
        if k == "library":
            return f"{lib} tables"
        if k == "client_pack":
            return ui.plural(len(ov["packs"]), "pack")
        return "live" if k == "snowflake_catalog" else "fallback"

    steps = "".join(f'<div style="background:var(--c-surface);padding:16px"><div class="between"><span class="mono faint" style="font-size:11px">0{i + 1}</span>{badge(ladder_badge(k), tone)}</div>'
                    f'<div class="accent" style="margin-top:12px">{icon(ico, 20)}</div><div style="margin-top:8px;font-size:13.5px;font-weight:600;color:var(--c-fg)">{t}</div>'
                    f'<div class="muted" style="margin-top:4px;font-size:12px;line-height:1.45">{d}</div></div>' for i, (k, ico, t, d, tone) in enumerate(LADDER))
    ui.html(f'<div style="margin-top:24px"><div class="between" style="margin-bottom:10px;align-items:baseline"><span style="font-size:15px;font-weight:600;color:var(--c-fg)">How a table is resolved</span>'
            f'<span class="faint" style="font-size:12px">first source that knows it wins; every column shows its source</span></div>'
            f'<div style="display:grid;grid-template-columns:repeat(5,1fr);gap:1px;background:var(--c-line);border:1px solid var(--c-line);border-radius:14px;overflow:hidden">{steps}</div></div>')
    modules: dict[str, int] = {}
    for t in tables:
        modules[t["module"] or "other"] = modules.get(t["module"] or "other", 0) + 1
    ranked = sorted(modules.items(), key=lambda x: -x[1])
    top_n = ranked[0][1] if ranked else 1
    bars = "".join(f'<div class="row" style="gap:12px;font-size:12px;flex-wrap:nowrap"><span class="mono fg" style="width:48px;font-weight:600">{esc(m)}</span>'
                   f'<span class="bar" style="flex:1;height:8px;border-radius:3px"><span style="width:{100 * n / top_n}%;background:var(--c-accent)"></span></span>'
                   f'<span class="tabular muted" style="width:32px;text-align:right">{n}</span></div>' for m, n in ranked)
    history = ov["history"]
    if history:
        events = "".join(f'<li style="position:relative;font-size:12px;margin-bottom:12px"><span style="position:absolute;left:-21px;top:4px;width:10px;height:10px;border-radius:99px;'
                         f'border:2px solid var(--c-surface);background:var(--c-accent)"></span><div class="row" style="gap:8px"><span class="fg" style="font-weight:500">{esc(h["action"])}</span>'
                         f'{"<span class=faint>· " + esc(ui.origin_label(h.get("origin"))) + "</span>" if h.get("origin") else ""}<span class="faint" style="margin-left:auto">{ui.ago(h.get("at"))}</span></div>'
                         f'<div class="mono muted" style="font-size:11px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{esc(", ".join(h["items"][:8]))}'
                         f'{" +" + str(h["count"] - 8) if h["count"] > 8 else ""}</div></li>' for h in history[:7])
        hist = f'<ol style="list-style:none;margin:16px 0 0;padding-left:16px;border-left:1px solid var(--c-line)">{events}</ol>'
    else:
        hist = ('<div class="muted" style="margin-top:14px;font-size:12.5px">Nothing added yet. Your library starts empty; the built-in dictionary and the Snowflake schema '
                'cover most programs.</div>')
    left, right = st.columns([1.2, 1])
    left.markdown(ui.card("Tables by module", f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px 32px">{bars}</div>', icon_name="layers", style="margin-top:24px"),
                  unsafe_allow_html=True)
    right.markdown(ui.card("Recent changes", hist, icon_name="history", style="margin-top:24px"), unsafe_allow_html=True)
    if ov["packs"]:
        packs = "".join(f'<div style="border-radius:10px;border:1px solid var(--c-line);background:var(--c-sunken);padding:14px"><div class="between"><span class="mono fg" style="font-weight:600">'
                        f'{esc(pk["name"])}</span>{badge(str(len(pk["issues"])) + " issue(s)", "warn") if pk["issues"] else ""}</div>'
                        f'<div class="muted" style="font-size:12px;margin-top:4px">{esc((pk.get("manifest") or {}).get("description") or "")}</div>'
                        f'<div class="row" style="gap:6px;margin-top:8px">{badge(str(pk["tables"]) + " tables")}{badge(str(len(pk["fm_sources"])) + " FM sources")}'
                        f'{badge(str(len(pk["gold_pairs"])) + " reference SQL")}</div></div>' for pk in ov["packs"])
        body = f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px">{packs}</div>'
    else:
        body = '<span class="muted" style="font-size:12.5px">No packs installed. None are needed.</span>'
    ui.html(ui.card("Client packs", body, "knowledge-packs/&lt;name&gt;/, chosen per project", "package", style="margin-top:16px"))


# ---------------------------------------------------------------------- field table + editors
def field_table(fields: list[dict], key_fields: list[str], height: int = 420) -> str:
    rows = "".join(f'<tr><td style="width:22px">{"<span class=accent>" + icon("key", 13) + "</span>" if f.get("is_key") or f["name"] in key_fields else ""}</td>'
                   f'<td class="m" style="font-weight:500">{esc(f["name"])}</td><td class="mono">{esc(fmt_type(f))}</td><td class="mono faint">{esc(f.get("ref_field") or "")}</td>'
                   f'<td>{esc(f.get("description"))}</td><td style="text-align:right">{badge(ui.prov_label(f.get("source")), ui.prov_tone(f.get("source"))) if f.get("source") else ""}</td></tr>'
                   for f in fields)
    return (f'<div class="scroll" style="max-height:{height}px"><table class="tbl"><thead><tr><th></th><th>Field</th><th>Type</th><th>Ref</th><th>Description</th>'
            f'<th style="text-align:right">Source</th></tr></thead><tbody>{rows}</tbody></table></div>')


@st.dialog("Table editor", width="large")
def table_editor(name: str | None = None, new_name: str = "") -> None:
    current = kn.table(name) if name else None
    if current and current["source"] == "builtin":
        st.info("This is the built-in definition. Saving stores your version in the library, which then takes precedence; remove it later to fall back to the built-in one.")
    a, b, c, d = st.columns([1.6, 3, 1, 1.2])
    tname = a.text_input("Table", value=(current or {}).get("name") or new_name, disabled=bool(current), placeholder="ZSD_ORDERS").upper().strip()
    desc = b.text_input("Description", value=(current or {}).get("description") or "", placeholder="Short text (used for business names)")
    module = c.text_input("Module", value=(current or {}).get("module") or "", placeholder="SD").upper()
    releases = ["both", "ecc", "s4"]
    release = d.selectbox("Exists in", releases, index=releases.index((current or {}).get("release") or "both") if (current or {}).get("release") in releases else 0,
                          format_func=lambda x: {"both": "ECC + S/4", "ecc": "ECC only", "s4": "S/4 only"}[x])
    if current:
        rows = [{"Key": bool(f.get("is_key") or f["name"] in current["key"]), "Field": f["name"], "Type": f.get("ddic_type") or "CHAR", "Length": f.get("length"),
                 "Decimals": f.get("decimals"), "Ref": f.get("ref_field") or "", "Description": f.get("description") or ""} for f in current["fields"]]
    else:
        rows = [{"Key": True, "Field": "MANDT", "Type": "CLNT", "Length": 3, "Decimals": None, "Ref": "", "Description": "Client"}]
    frame = st.data_editor(pd.DataFrame(rows, columns=["Key", "Field", "Type", "Length", "Decimals", "Ref", "Description"]), num_rows="dynamic", hide_index=True,
                           width="stretch", height=360, key=f"te_{name or 'new'}",
                           column_config={"Key": st.column_config.CheckboxColumn(width="small"), "Type": st.column_config.SelectboxColumn(options=DDIC_TYPES, required=True),
                                          "Length": st.column_config.NumberColumn(min_value=0, step=1, format="%d"),
                                          "Decimals": st.column_config.NumberColumn(min_value=0, step=1, format="%d")})
    complete = st.toggle("This is the complete field list", value=bool((current or {}).get("fields_complete")),
                         help="On: a column the code uses that is not listed is reported as an error. Off: it is reported as unverified.")
    x, y = st.columns(2)
    if x.button("Cancel", width="stretch"):
        st.rerun()
    valid = bool(re.fullmatch(r"[A-Z0-9_/]{1,40}", tname))
    if y.button("Save to library", type="primary", icon=":material/check:", width="stretch", disabled=not valid):
        fields = []
        for _, r in frame.iterrows():
            fname = str(r["Field"] or "").upper().strip() if isinstance(r["Field"], str) else ""
            if not fname:
                continue
            fields.append({"name": fname, "ddic_type": r["Type"] or "CHAR", "length": int(r["Length"]) if pd.notna(r["Length"]) else None,
                           "decimals": int(r["Decimals"]) if pd.notna(r["Decimals"]) else None, "ref_field": (str(r["Ref"]).upper() or None) if isinstance(r["Ref"], str) else None,
                           "description": r["Description"] if isinstance(r["Description"], str) else "", "is_key": bool(r["Key"])})
        if not fields:
            st.error("Add at least one field.")
            return
        res = kn.save([{"name": tname, "description": desc, "module": module, "release": release, "fields_complete": complete,
                        "key": [f["name"] for f in fields if f["is_key"]], "fields": fields}], origin="manual", mode="replace")
        if res["errors"]:
            st.error("; ".join(res["errors"]))
            return
        changed()
        ui.notify("ok", f"{tname} saved to your library")
        ui.go("knowledge", tab="tables", t=tname)


@st.dialog("Function module editor", width="large")
def fm_editor(name: str | None = None) -> None:
    current = next((f for f in kn.fms() if f["name"] == (name or "").upper()), None) if name else None
    a, b = st.columns([3, 1.3])
    fname = a.text_input("Name", value=(current or {}).get("name") or name or "", disabled=bool(current), placeholder="Z_GET_REGION_TEXT").upper().strip()
    sections = ["function_modules", "methods"]
    section = b.selectbox("Type", sections, index=sections.index((current or {}).get("section") or "function_modules"),
                          format_func=lambda x: {"function_modules": "Function module", "methods": "Class method"}[x])
    kinds = list(FM_KIND_HELP)
    kind = st.radio("Kind", kinds, index=kinds.index((current or {}).get("kind")) if (current or {}).get("kind") in kinds else 1, horizontal=True,
                    captions=[FM_KIND_HELP[k] for k in kinds])
    c, d = st.columns(2)
    output = c.text_input("Result parameter", value=(current or {}).get("output") or "", placeholder="EV_TEXT", help="EXPORTING/IMPORTING parameter that receives the value").upper()
    tables = d.text_input("Tables it reads", value=", ".join((current or {}).get("tables") or []), placeholder="T005U", help="lookup only")
    hint = {"expression": "Expression with {PARAMETER} placeholders, e.g. ROUND({IV_QTY}, 0)",
            "lookup": "Describe the join, e.g. T005U.BEZEI joined on LAND1 = {IV_LAND1} AND BLAND = {IV_REGIO}"}.get(kind, "Not needed for this kind")
    sql = st.text_area("Snowflake SQL", value=(current or {}).get("sql") or "", height=80, help=hint)
    note = st.text_input("Note", value=(current or {}).get("note") or "", placeholder="What it does, in one sentence")
    existing = kn.fm_source(fname) if current and current.get("has_source_code") else ""
    src = st.text_area("ABAP source (optional)", value=existing or "", height=150, placeholder="FUNCTION z_get_region_text.\n  ...\nENDFUNCTION.",
                       help="FUNCTION … ENDFUNCTION. With source, the FM body is translated like program code wherever it is called.")
    x, y = st.columns(2)
    if x.button("Cancel", width="stretch"):
        st.rerun()
    if y.button("Save to library", type="primary", icon=":material/check:", width="stretch", disabled=not re.fullmatch(r"[A-Za-z0-9_/=>-]{2,80}", fname or "")):
        res = kn.save(fms_=[{"name": fname, "section": section, "kind": kind, "output": output or None, "sql": sql or None, "note": note or None, "tables": split_names(tables)}],
                      fm_sources=[{"name": fname, "source": src}] if src.strip() and src != existing else [], origin="manual")
        if res["errors"]:
            st.error("; ".join(res["errors"]))
            return
        changed()
        ui.notify("ok", f"{fname} saved to your library")
        st.rerun()


@st.dialog("Remove from library")
def confirm_remove(detail: dict) -> None:
    builtin = detail.get("builtin")
    st.write("Your library version is removed and the built-in SAP dictionary definition is used again." if builtin else
             "The table is removed from your library. Projects fall back to the Snowflake schema or the code for it.")
    a, b = st.columns(2)
    if a.button("Cancel", width="stretch"):
        st.rerun()
    if b.button("Revert to built-in" if builtin else "Remove from library", type="primary", width="stretch"):
        if ui.guard(kn.delete_table, detail["name"], title="Could not remove") is not None:
            changed()
            ui.notify("ok", f"{detail['name']} reverted to the built-in definition" if builtin else f"{detail['name']} removed")
        ui.go("knowledge", tab="tables", t=detail["name"] if builtin else None)


# ---------------------------------------------------------------------- tables
def tables_tab(tables: list[dict], initial: str | None) -> None:
    left, right = st.columns([1, 2.2])
    with left:
        with ui.panel("kn1"):
            q = st.text_input("Search", placeholder=f"Search {len(tables)} tables", key="kt_q", label_visibility="collapsed", icon=":material/search:")
            src = st.segmented_control("Source", ["all", "builtin", "library", "ai_generated"], default="all", key="kt_src", label_visibility="collapsed",
                                       format_func=lambda x: {"all": "All", "builtin": "SAP dictionary", "library": "Your library", "ai_generated": "AI-proposed"}[x]) or "all"
            mods = sorted({t["module"] or "other" for t in tables})
            a, b = st.columns([2, 1], vertical_alignment="center")
            mod = a.selectbox("Module", ["all"] + mods, key="kt_mod", label_visibility="collapsed", format_func=lambda m: "All modules" if m == "all" else m)
            if b.button("New", icon=":material/add:", width="stretch", key="kt_new"):
                table_editor(None)
            shown = [t for t in tables if (src == "all" or t["source"] == src) and (mod == "all" or (t["module"] or "other") == mod)
                     and (not q or q.lower() in f"{t['name']} {t['description']}".lower())]
            st.caption(f"{len(shown)} shown")
            if not shown:
                st.caption("No table matches.")
                if st.button(f"Add {q.upper() if q else 'one'}", key="kt_add_missing"):
                    ui.go("knowledge", tab="add", tables=q.upper())
                return
            names = [t["name"] for t in shown]
            info = {t["name"]: t for t in shown}
            sel = st.radio("Table", names, index=names.index(initial) if initial in names else 0, key=f"kt_sel_{src}_{mod}_{q}_{initial or ''}", label_visibility="collapsed",
                           format_func=lambda n: f"{n}  ·  {info[n]['module'] or ''}  ·  {info[n]['fields']} f  ·  {(info[n]['description'] or '—')[:40]}"
                                                 + (f"  ·  {ui.prov_label(info[n]['source'])}" if info[n]["source"] != "builtin" else ""))
            st.markdown("<style>[class*='st-key-kt_sel_'] [role='radiogroup']{max-height:58vh;overflow:auto;flex-wrap:nowrap}"
                        "[class*='st-key-kt_sel_'] label p{font-size:12.5px}</style>", unsafe_allow_html=True)
    with right:
        detail = kn.table(sel)
        if not detail:
            ui.empty("Select a table", "database")
            return
        keys = "".join(f'<span class="chip" style="color:var(--c-fg)">{esc(k)}</span>' for k in detail["key"]) or '<span class="faint">no key recorded</span>'
        texts = ""
        if detail.get("text_table"):
            texts += f'<span class="faint" style="margin-left:8px">texts in <span class="mono accent">{esc(detail["text_table"])}</span></span>'
        if detail.get("text_of"):
            texts += f'<span class="faint" style="margin-left:8px">texts of <span class="mono accent">{esc(detail["text_of"])}</span></span>'
        meta = (f'{len(detail["fields"])} fields · {"complete field list" if detail["fields_complete"] else "common fields (others are reported as unverified, not errors)"}'
                + (f' · {esc(ui.origin_label(detail.get("origin")))}' if detail.get("origin") else "") + (f' · {ui.ago(detail.get("updated"))}' if detail.get("updated") else ""))
        release = badge(f'{detail["release"].upper()} only', "warn") if detail.get("release") not in (None, "both") else ""
        ui.html(f'<div class="card fade-up" style="overflow:hidden"><div style="position:relative;padding:22px;border-bottom:1px solid var(--c-line)">'
                f'<div class="dot-grid" style="position:absolute;inset:0;opacity:.4;-webkit-mask-image:linear-gradient(90deg,transparent 50%,black)"></div><div style="position:relative">'
                f'<div class="row" style="gap:8px"><span class="display" style="font-size:30px;line-height:1;color:var(--c-fg)">{esc(detail["name"])}</span>'
                f'{badge(ui.prov_label(detail["source"]), ui.prov_tone(detail["source"]))}{badge(esc(detail["module"])) if detail.get("module") else ""}{release}</div>'
                f'<div class="muted" style="margin-top:8px;font-size:14px">{esc(detail["description"] or "No description")}</div>'
                f'<div class="row" style="gap:6px;margin-top:12px;font-size:11.5px"><span class="accent">{icon("key", 14)}</span>{keys}{texts}</div>'
                f'<div class="faint" style="margin-top:8px;font-size:11.5px">{meta}</div></div></div>{field_table(detail["fields"], detail["key"], 520)}</div>')
        a, b, c, _ = st.columns([1, 1.6, 1, 2])
        if a.button("Edit" if detail["in_library"] else "Override", icon=":material/edit:", width="stretch", key="kt_edit"):
            table_editor(detail["name"])
        if b.button("Refresh from Snowflake", icon=":material/refresh:", width="stretch", key="kt_refresh"):
            ui.go("knowledge", tab="add", tables=detail["name"], method="snowflake")
        if detail["in_library"] and c.button("Revert" if detail["builtin"] else "Remove", icon=":material/undo:" if detail["builtin"] else ":material/delete:",
                                             width="stretch", key="kt_remove"):
            confirm_remove(detail)


# ---------------------------------------------------------------------- function modules
def fms_tab(fms: list[dict]) -> None:
    a, b, c, d = st.columns([2, 3, 1, 1.6], vertical_alignment="center")
    q = a.text_input("Search", placeholder=f"Search {len(fms)} function modules and methods", key="kf_q", label_visibility="collapsed", icon=":material/search:")
    kinds: dict[str, int] = {}
    for f in fms:
        kinds[f["kind"]] = kinds.get(f["kind"], 0) + 1
    kind = b.segmented_control("Kind", ["all"] + list(kinds), default="all", key="kf_kind", label_visibility="collapsed",
                               format_func=lambda k: "All" if k == "all" else f"{k} {kinds[k]}") or "all"
    if c.button("Import", icon=":material/upload:", width="stretch", key="kf_import"):
        ui.go("knowledge", tab="add", fms="", method="paste", kind="fms")
    if d.button("New function module", icon=":material/add:", type="primary", width="stretch", key="kf_new"):
        fm_editor(None)
    shown = [f for f in fms if (kind == "all" or f["kind"] == kind) and (not q or q.lower() in f"{f['name']} {f.get('note') or ''}".lower())]
    tone = {"expression": "ok", "lookup": "info", "opaque": "warn", "custom": "accent"}
    rows = "".join(f'<tr><td class="m" style="font-weight:600">{esc(f["name"])}{"<div class=faint style=font-size:10.5px>method</div>" if f["section"] == "methods" else ""}</td>'
                   f'<td>{badge(esc(f["kind"]), tone.get(f["kind"], "slate"))}</td><td><div>{esc(f.get("note") or ("→ " + f["output"] if f.get("output") else ""))}</div>'
                   f'{"<code class=mono style=font-size:11px;color:var(--c-fg-faint)>" + esc(f["sql"]) + "</code>" if f.get("sql") else ""}</td>'
                   f'<td>{badge(ui.prov_label(f.get("source")), ui.prov_tone(f.get("source")))} {"<span class=accent title=ABAP_source_stored>" + icon("code", 13) + "</span>" if f.get("has_source_code") else ""}</td></tr>'
                   for f in shown) or '<tr><td colspan="4" class="faint" style="text-align:center;padding:30px">Nothing matches.</td></tr>'
    ui.html(f'<div class="card" style="overflow:hidden;margin-top:6px"><div class="scroll" style="max-height:56vh"><table class="tbl"><thead><tr><th>Name</th><th>Kind</th><th>Behaviour</th>'
            f'<th>Source</th></tr></thead><tbody>{rows}</tbody></table></div></div>')
    names = [f["name"] for f in shown]
    lib = {f["name"] for f in shown if f.get("source") in ("library", "ai_generated")}
    if names:
        x, y, z, _ = st.columns([2, 1, 1, 2], vertical_alignment="bottom")
        pick = x.selectbox("Function module", names, key="kf_pick", help="Choose one to edit or remove")
        if y.button("Edit", icon=":material/edit:", width="stretch", key="kf_edit"):
            fm_editor(pick)
        if z.button("Remove", icon=":material/delete:", width="stretch", key="kf_rm", disabled=pick not in lib, help=None if pick in lib else "Only library entries can be removed"):
            if ui.guard(kn.delete_fm, pick, title="Could not remove") is not None:
                changed()
                ui.notify("ok", f"{pick} removed from your library")
            st.rerun()


# ---------------------------------------------------------------------- add knowledge
def step(n: int, title: str, sub: str) -> None:
    ui.html(f'<div class="row" style="gap:12px;margin-bottom:8px;flex-wrap:nowrap"><span class="lib-step">{n}</span><div><div style="font-size:13.5px;font-weight:600;color:var(--c-fg)">'
            f'{title}</div><div class="faint" style="font-size:12px">{sub}</div></div></div>')


def aside(title: str, body: str, tone: str = "") -> str:
    if tone == "warn":
        return (f'<div style="border-radius:12px;border:1px solid color-mix(in oklab,var(--c-warn) 30%,transparent);background:color-mix(in oklab,var(--c-warn) 6%,transparent);'
                f'padding:16px;font-size:12.5px;line-height:1.6;color:var(--c-fg-muted)"><div class="row warn" style="gap:8px;font-weight:600;margin-bottom:6px">{icon("alert")}{title}</div>{body}</div>')
    return (f'<div class="hatch" style="border-radius:12px;border:1px solid var(--c-line);padding:16px;font-size:12.5px;line-height:1.6;color:var(--c-fg-muted)">'
            f'<div class="eyebrow faint" style="margin-bottom:6px">{title}</div>{body}</div>')


def set_preview(p: dict | None) -> None:
    st.session_state.kn_preview = p
    st.session_state.pop("kn_saved", None)


def add_tab(r: dict, known: dict[str, str]) -> None:
    sig = f"{r.get('tables')}|{r.get('fms')}|{r.get('method')}|{r.get('from')}|{r.get('kind')}"
    if st.session_state.get("kn_sig") != sig:
        st.session_state.kn_sig = sig
        initial_kind = "fms" if (r.get("fms") is not None and not r.get("tables")) or r.get("kind") == "fms" else "tables"
        st.session_state.kn_kind = initial_kind
        st.session_state.kn_names = ", ".join(split_names(r.get("tables") or r.get("fms") or ""))
        st.session_state.kn_method = r.get("method") or ("paste" if initial_kind == "fms" else "snowflake")
        set_preview(None)
    pid = r.get("from")
    project = core.project(pid) if pid else None
    columns = {g["name"]: g["columns"] for g in kn.gaps(pid)["tables"]}
    if project:
        ui.html(f'<div class="callout ok" style="margin-bottom:14px">{icon("sparkles")}<div>Filling knowledge gaps for <a class="tcb-link mono" href="?page=p&pid={project["id"]}" '
                f'target="_self">{esc(project["name"])}</a>. <span class="muted">Save, then re-analyze the project to use it.</span></div></div>')
    with ui.panel("kn2"):
        a, b = st.columns([3, 1.4], vertical_alignment="center")
        with a:
            step(1, "What is missing?", "Names of tables or function modules, separated by commas, spaces or new lines")
        kind = b.segmented_control("Kind", ["tables", "fms"], key="kn_kind", label_visibility="collapsed", width="stretch",
                                   format_func=lambda k: {"tables": "Tables", "fms": "Function modules"}[k]) or "tables"
        text = st.text_area("Names", key="kn_names", height=68, label_visibility="collapsed",
                            placeholder="e.g. ZSD_ORDERS, ZMM_STOCK_AGING, J_1BNFDOC" if kind == "tables" else "e.g. Z_GET_REGION_TEXT, Z_CALC_DISCOUNT")
        names = split_names(text)
        if names:
            chips = ""
            for n in names:
                src = known.get(n) if kind == "tables" else None
                extra = f'<span class="faint" style="font-family:Inter;font-size:10px">· {ui.prov_label(src)}</span>' if src else ""
                extra += f'<span class="faint" style="font-family:Inter;font-size:10px">· {len(columns[n])} cols used</span>' if columns.get(n) else ""
                style = "" if src else "border-color:color-mix(in oklab,var(--c-accent) 30%,transparent);background:var(--c-accent-soft);color:var(--c-accent)"
                chips += f'<span class="chip" style="{style}">{esc(n)}{extra}</span>'
            ui.html(f'<div class="row" style="gap:6px">{chips}</div>')
    with ui.panel("kn3"):
        step(2, "Where should it come from?", "Ordered from most to least reliable. Nothing is saved until you confirm the preview.")
        usable = [m for m in METHODS if kind in m[5]]
        if st.session_state.kn_method not in [m[0] for m in usable]:
            st.session_state.kn_method = "paste"
        cols = st.columns(3)
        for i, (mid, ico, title, desc, quality, _) in enumerate(METHODS):
            enabled = kind in METHODS[i][5]
            on = st.session_state.kn_method == mid
            with cols[i % 3]:
                ui.html(f'<div class="card" style="padding:14px;min-height:118px;{"border-color:var(--c-accent);box-shadow:inset 3px 0 0 var(--c-accent);background:var(--c-accent-soft)" if on else ""}'
                        f'{"opacity:.45" if not enabled else ""}"><div class="row" style="gap:10px;flex-wrap:nowrap;align-items:flex-start"><span class="icon-tile" style="width:36px;height:36px">'
                        f'{icon(ico)}</span><div><div class="row" style="gap:8px"><span style="font-size:13.5px;font-weight:600;color:var(--c-fg)">{title}</span>{badge(quality[0], quality[1])}</div>'
                        f'<div class="muted" style="margin-top:4px;font-size:12px;line-height:1.45">{desc}</div></div></div></div>')
                if st.button("Selected" if on else "Use this", key=f"km_{mid}", width="stretch", disabled=not enabled or on, type="primary" if on else "secondary"):
                    st.session_state.kn_method = mid
                    set_preview(None)
                    st.rerun()
        st.divider()
        method = st.session_state.kn_method
        if method == "snowflake":
            snowflake_panel(names)
        elif method == "ddic":
            ddic_panel(names)
        elif method == "paste":
            paste_panel(kind, names)
        elif method == "prompt":
            prompt_panel(kind, names, columns)
        elif method == "ai":
            ai_panel(kind, names, columns)
        else:
            a, b = st.columns([1.4, 3], vertical_alignment="center")
            label = f"Open {'function module' if kind == 'fms' else 'table'} editor" + (f" for {names[0]}" if names else "")
            if a.button(label, icon=":material/edit:", type="primary", key="kn_manual"):
                if kind == "fms":
                    fm_editor(names[0] if names else None)
                else:
                    table_editor(names[0] if names and names[0] in known else None, names[0] if names else "")
            b.caption("Saved entries are marked manual and loaded into every project.")
    preview = st.session_state.get("kn_preview")
    if preview:
        preview_panel(preview, columns, project)


def location_defaults() -> dict:
    d = core.defaults()
    return {"db": d["source_database"], "schema": d["source_schema"], "pattern": d["table_pattern"] or "{table}", "language": d["language"] or "E"}


def snowflake_panel(names: list[str]) -> None:
    d = location_defaults()
    left, right = st.columns([2.4, 1])
    with left:
        db, sc = ui.location_picker("Database . schema", d["db"], d["schema"], "kn_sf")
        pattern = st.text_input("Table name pattern", value=d["pattern"], key="kn_sf_pattern", help="Physical name, e.g. SAP_{table}")
        scope = st.segmented_control("Scope", ["named", "all"], default="named", key="kn_sf_scope", label_visibility="collapsed",
                                     format_func=lambda x: {"named": f"Named tables ({len(names)})", "all": "Every table in the schema"}[x]) or "named"
        a, b, _ = st.columns([1, 1.3, 1.5])
        if a.button("Read columns", icon=":material/database:", type="primary", width="stretch", key="kn_sf_go",
                    disabled=not (db and sc) or (scope == "named" and not names)):
            with st.spinner("Reading INFORMATION_SCHEMA…"):
                p = ui.guard(kn.fetch_snowflake, db, sc, names, scope == "all", pattern, title="Could not read the schema")
            if p:
                set_preview(p)
            st.rerun()
        if b.button("List tables in schema", icon=":material/search:", width="stretch", key="kn_sf_list", disabled=not (db and sc)):
            st.session_state.kn_sf_tables = (db, sc, ui.guard(kn.schema_tables, db, sc, pattern, title="Could not list tables") or [])
        listing = st.session_state.get("kn_sf_tables")
        if listing and listing[:2] == (db, sc):
            chips = "".join(f'<span class="chip" style="background:var(--c-surface)">{esc(t)}</span>' for t in listing[2])
            ui.html(f'<div style="border-radius:10px;border:1px solid var(--c-line);background:var(--c-sunken);padding:10px"><div class="faint" style="font-size:11px;margin-bottom:6px">'
                    f'{len(listing[2])} tables in {esc(db)}.{esc(sc)}</div><div class="row scroll" style="gap:4px;max-height:130px">{chips}</div></div>')
    right.markdown(aside("What you get", "Column names, Snowflake types and comments; primary keys when the replication declared them. ABAP types and labels are borrowed from "
                         "same-named fields the dictionary knows (MATNR, WERKS, BUKRS ...). The column list is marked <b>complete</b>."), unsafe_allow_html=True)


def ddic_panel(names: list[str]) -> None:
    d = location_defaults()
    left, right = st.columns([2.4, 1])
    with left:
        db, sc = ui.location_picker("Schema holding DD03L", d["db"], d["schema"], "kn_dd")
        a, b = st.columns([3, 1])
        pattern = a.text_input("Name pattern", value=d["pattern"], key="kn_dd_pattern")
        lang = b.text_input("Language", value=d["language"][:1], max_chars=1, key="kn_dd_lang").upper()
        status = kn.ddic_status(db, sc, pattern) if db and sc else None
        chips = "".join(f'<span class="badge {"b-ok" if (status or {}).get("tables", {}).get(t) else ""} mono">{icon("check" if (status or {}).get("tables", {}).get(t) else "x", 11)}{t}</span>'
                        for t in ["DD03L", "DD04T", "DD03T", "DD02T"])
        note = ""
        if status and not status.get("available"):
            note = f'<span class="muted" style="font-size:12px">{esc(status.get("error") or "No DD03L in this schema.")}</span>'
        ui.html(f'<div class="row" style="gap:6px">{chips}{note}</div>')
        label = f"Look up {len(names) or ''} table{'' if len(names) == 1 else 's'} in DD03L"
        if st.button(label, icon=":material/layers:", type="primary", key="kn_dd_go", disabled=not (status or {}).get("available") or not names):
            with st.spinner("Reading DD03L / DD04T / DD02T…"):
                p = ui.guard(kn.fetch_ddic, db, sc, names, pattern, lang, title="DD03L lookup failed")
            if p:
                set_preview(p)
            st.rerun()
    right.markdown(aside("Best option at scale", "Ask the replication team to add <b>DD03L</b>, <b>DD04T</b> and <b>DD02T</b> (optionally DD03T) to the SAP replica once. "
                         "From then on any table, standard or custom, can be looked up here with the exact SE11 definition: keys, DDIC types, lengths, decimals, "
                         "currency/unit references and labels."), unsafe_allow_html=True)


def paste_panel(kind: str, names: list[str]) -> None:
    left, right = st.columns([2.4, 1])
    with left:
        placeholder = ("Paste FUNCTION ... ENDFUNCTION source, or YAML:\nfunction_modules:\n  Z_MY_FM:\n    kind: lookup\n    ..." if kind == "fms" else
                       "Paste rows copied from SE11 / SE16 / Excel / an AI answer, e.g.\nTABNAME\tFIELDNAME\tKEYFLAG\tDATATYPE\tLENG\tDECIMALS\tDDTEXT\n"
                       "ZSD_ORDERS\tVBELN\tX\tCHAR\t10\t0\tSales document")
        text = st.text_area("Paste", key="kn_paste", height=220, placeholder=placeholder, label_visibility="collapsed")
        upload = st.file_uploader("or choose a file", type=ACCEPT, key="kn_file")
        table = ""
        a, b = st.columns([2, 1.2], vertical_alignment="bottom")
        if kind == "tables":
            table = a.text_input("Table name (only if rows have no table column)", value=names[0] if len(names) == 1 else "", key="kn_default_table",
                                 placeholder="e.g. ZSD_ORDERS").upper()
        if b.button("Read and preview", icon=":material/auto_fix_high:", type="primary", width="stretch", key="kn_paste_go", disabled=not (text.strip() or upload)):
            if upload:
                p = ui.guard(kn.import_any, filename=upload.name, data=upload.getvalue(), default_table=table, title="Could not read the input")
            else:
                p = ui.guard(kn.import_any, text=text, default_table=table, title="Could not read the input")
            if p:
                set_preview(p)
            st.rerun()
    with right:
        ticks = "".join(f'<li class="row" style="gap:8px;flex-wrap:nowrap;align-items:flex-start;margin-top:6px"><span class="ok">{icon("check", 13)}</span>{x}</li>'
                        for x in ["SE11 field list (copy the grid)", "SE16 export of DD03L / DD03VT", "CSV · TSV · ; or | separated · Excel", "Markdown tables from an AI chat",
                                  "JSON or YAML (pack format)", "FUNCTION … ENDFUNCTION source", "A zipped knowledge pack"])
        ui.html(f'<div style="border-radius:12px;border:1px solid var(--c-line);background:var(--c-sunken);padding:16px;font-size:12px;color:var(--c-fg-muted)">'
                f'<div class="eyebrow faint">Recognised automatically</div><ul style="list-style:none;padding:0;margin:4px 0 0">{ticks}</ul></div>')
        st.caption("Templates")
        for name, (mime, body) in kn.TEMPLATES.items():
            st.download_button(name, data=body, file_name=f"tcb_template_{name}", mime=mime, icon=":material/download:", key=f"kn_tpl_{name}", type="tertiary")


def prompt_panel(kind: str, names: list[str], columns: dict[str, list[str]]) -> None:
    left, right = st.columns(2)
    with left:
        a, b = st.columns([2, 1], vertical_alignment="center")
        a.markdown("<div style='font-size:12.5px;font-weight:600;color:var(--c-fg)'>1 · Copy this prompt</div>", unsafe_allow_html=True)
        system = b.segmented_control("System", ["S/4HANA", "ECC 6.0"], default="S/4HANA", key="kn_pr_sys", label_visibility="collapsed",
                                     format_func=lambda x: "S/4" if x == "S/4HANA" else "ECC") or "S/4HANA"
        text = kn.prompt(kind, names, columns, system) if names else ""
        if text:
            st.code(text, language="yaml", height=320, wrap_lines=True)
        else:
            ui.html('<pre class="prompt-box">Enter names above to build the prompt.</pre>')
        st.caption(f"Only the names{' and the columns the code uses' if columns else ''} are in the prompt, never program source. Use the copy icon on the box.")
    with right:
        st.markdown("<div style='font-size:12.5px;font-weight:600;color:var(--c-fg)'>2 · Paste the answer</div>", unsafe_allow_html=True)
        answer = st.text_area("Answer", key="kn_answer", height=320, label_visibility="collapsed",
                              placeholder="Paste the whole reply here; surrounding text and ``` fences are fine.")
        a, b = st.columns([1.2, 2.4], vertical_alignment="center")
        if a.button("Read and preview", icon=":material/auto_fix_high:", type="primary", width="stretch", key="kn_pr_go", disabled=not answer.strip()):
            p = ui.guard(kn.import_any, text=answer, ai=True, title="Could not read the answer")
            if p:
                set_preview(p)
            st.rerun()
        b.caption("Saved as AI-proposed: never a complete list, never overriding verified fields.")


def ai_panel(kind: str, names: list[str], columns: dict[str, list[str]]) -> None:
    ms = [m for m in ui.models() if m["available"] and m["kind"] != "embedding"]
    ids = [m["id"] for m in ms]
    default = core.defaults()["model"]
    left, right = st.columns([2.2, 1])
    with left:
        a, b = st.columns(2, vertical_alignment="bottom")
        by_id = {m["id"]: m for m in ms}
        model = a.selectbox("Model", ids, index=ids.index(default) if default in ids else 0, key="kn_ai_model",
                            format_func=lambda i: i + ("  ·  stays in Snowflake" if by_id[i]["private"] else "")) if ids else None
        force = b.toggle("Also ask about names already known", key="kn_ai_force", help="Off: tables the dictionary or your library already define are skipped")
        label = f"Propose {len(names) or ''} {'function module' if kind == 'fms' else 'table'}{'' if len(names) == 1 else 's'}"
        if st.button(label, icon=":material/smart_toy:", type="primary", key="kn_ai_go", disabled=not names or not model):
            with st.spinner(f"Asking {model} in batches of {10 if kind == 'fms' else 4}; about 10 seconds per batch…"):
                p = ui.guard(kn.propose, kind, names, model, columns, "S/4HANA", force, title="AI proposal failed")
            if p:
                set_preview(p)
            st.rerun()
    right.markdown(aside("Last resort", "Models know common SAP tables reasonably well but regularly get less common ones wrong (wrong meaning, invented fields), and cannot know your "
                         "Z tables. Proposals are saved as <b>AI-proposed</b>: never a complete field list, never overriding fields from a verified source, and shown as such in every analysis.",
                         "warn"), unsafe_allow_html=True)


# ---------------------------------------------------------------------- preview + save
def preview_panel(p: dict, used: dict[str, list[str]], project: dict | None) -> None:
    is_ai = p["format"] == "ai" or (bool(p["tables"] or p["fms"]) and all(x.get("origin") == "ai" for x in p["tables"] + p["fms"]))
    counts = {s: sum(1 for t in p["tables"] if t["status"] == s) for s in ("new", "update", "same")}
    empty = not (p["tables"] or p["fms"] or p["fm_sources"] or p["s4"])
    pills = "".join(f'<span style="border-radius:6px;background:rgba(255,255,255,.1);padding:4px 8px"><b class="tabular">{n}</b> {label}</span>'
                    for n, label in [(counts["new"], "new"), (counts["update"], "update"), (counts["same"], "unchanged"), (len(p["fms"]), "FMs"), (len(p["fm_sources"]), "FM sources")] if n)
    origin = f'<span class="mono">{esc(p["source"])}</span>' if p.get("source") else f"format: {esc(p['format'])}"
    model = f" · {esc(p['model'])}" if p.get("model") else ""
    ui.html(f'<div class="ink grain fade-up" style="position:relative;border-radius:14px 14px 0 0;padding:16px 20px;margin-top:18px"><div class="between">'
            f'<div class="row" style="gap:12px;flex-wrap:nowrap"><span class="lib-step" style="background:var(--c-side-2)">3</span><div><div style="font-size:14px;font-weight:600;color:var(--c-side-fg)">'
            f'Review before saving</div><div style="font-size:12px;color:var(--c-side-muted)">{origin}{model}</div></div></div><div class="row" style="gap:6px;font-size:11.5px;color:var(--c-side-fg)">{pills}</div></div></div>')
    with ui.panel("kn4"):
        if is_ai and (p["tables"] or p["fms"]):
            ui.html(ui.callout("warn", "AI proposals: check names, keys and types against SE11 before saving. They are stored as <b>AI-proposed</b> and only add fields; they never "
                                       "replace fields from the dictionary or Snowflake."))
        missing = list(p.get("unknown") or []) + list(p.get("missing") or [])
        if missing:
            ui.html(ui.callout("info", f"<b>Not found:</b> <span class='mono'>{esc(', '.join(missing))}</span>"))
            cols = st.columns(4)
            options = [("snowflake", "Read from Snowflake", ":material/database:"), ("ddic", "Look up in DD03L", ":material/layers:"),
                       ("paste", "Paste an SE11 export", ":material/upload:"), ("manual", "Write it", ":material/edit:")]
            for col, (mid, label, ico) in zip(cols, [o for o in options if o[0] != p["format"]]):
                if col.button(label, icon=ico, width="stretch", key=f"pv_sw_{mid}"):
                    st.session_state.kn_names = ", ".join(missing)
                    st.session_state.kn_method = mid
                    set_preview(None)
                    st.rerun()
        if p.get("skipped_known"):
            ui.html(ui.callout("ok", f"Already known from a verified source, not sent to the model: <span class='mono'>{esc(', '.join(p['skipped_known']))}</span>"))
        if empty and not missing:
            ui.html(ui.callout("warn", "Nothing to save. " + esc((p.get("warnings") or [""])[0])))
        picks: dict[str, bool] = {}
        complete: dict[str, bool] = {}
        for t in p["tables"]:
            key = f"t:{t['name']}"
            delta = ""
            if t["status"] == "update":
                changed_note = f", {t['changed_fields']} changed" if t["changed_fields"] else ""
                delta = f" · +{t['added_fields']} field(s){changed_note} vs {ui.prov_label(t.get('current_source'))}"
            a, b, c = st.columns([0.5, 6, 1.6], vertical_alignment="center")
            picks[key] = a.checkbox("Save", value=t["status"] != "same", key=f"pv_{key}", label_visibility="collapsed")
            b.markdown(f"<span class='mono fg' style='font-weight:600'>{esc(t['name'])}</span> <span class='muted'>{esc(t['description'])}</span> "
                       f"{badge(t['status'], {'new': 'ok', 'update': 'accent'}.get(t['status'], 'slate'))} <span class='faint' style='font-size:11.5px'>"
                       f"{len(t['fields'])} fields · key {len(t['key']) or '—'}{delta}</span>", unsafe_allow_html=True)
            if not is_ai:
                complete[t["name"]] = c.checkbox("complete list", value=bool(t["fields_complete"]), key=f"pv_c_{t['name']}",
                                                 help="Complete = this is every field of the table; columns the code uses that are not listed become errors")
            absent = [x for x in used.get(t["name"], []) if x not in {f["name"] for f in t["fields"]}]
            if absent:
                tail = ("; with “complete list” on, these are reported as errors (likely a missing column in the replica or a typo in the code)"
                        if complete.get(t["name"]) and not is_ai else "")
                ui.html(ui.callout("warn", f"The analysed code uses <span class='mono fg'>{esc(', '.join(absent))}</span>, not in this definition{tail}."))
            with st.expander(f"Fields of {t['name']}", expanded=len(p["tables"]) == 1):
                ui.html(field_table(t["fields"], t["key"], 320))
        for f in p["fms"]:
            key = f"f:{f['name']}"
            a, b = st.columns([0.5, 8], vertical_alignment="center")
            picks[key] = a.checkbox("Save", value=True, key=f"pv_{key}", label_visibility="collapsed")
            b.markdown(f"<span class='mono fg' style='font-weight:600'>{esc(f['name'])}</span> {badge(esc(f['kind']), 'accent')} {badge(f['status'], 'ok' if f['status'] == 'new' else 'slate')}"
                       f"{' <span class=faint>→ ' + esc(f['output']) + '</span>' if f.get('output') else ''}"
                       f"{'<div class=muted style=font-size:12px>' + esc(f['note']) + '</div>' if f.get('note') else ''}"
                       f"{'<code class=mono style=font-size:11px>' + esc(f['sql']) + '</code>' if f.get('sql') else ''}", unsafe_allow_html=True)
        for s in p["fm_sources"]:
            key = f"s:{s['name']}"
            a, b = st.columns([0.5, 8], vertical_alignment="center")
            picks[key] = a.checkbox("Save", value=True, key=f"pv_{key}", label_visibility="collapsed")
            b.markdown(f"{icon('code', 14)} <span class='mono fg' style='font-weight:600'>{esc(s['name'])}</span> <span class='muted' style='font-size:11.5px'>"
                       f"{s['lines']} lines of ABAP · translated like program code wherever it is called</span>", unsafe_allow_html=True)
        if p.get("warning_count"):
            with st.expander(f"{p['warning_count']} note{'' if p['warning_count'] == 1 else 's'} while reading"):
                ui.html('<ul class="mono muted" style="font-size:11px;margin:0">' + "".join(f"<li>{esc(w)}</li>" for w in p["warnings"]) + "</ul>")
        if empty:
            return
        st.divider()
        saved = st.session_state.get("kn_saved")
        total = sum(picks.values()) + (1 if p["s4"] else 0)
        if saved is not None:
            a, b, c = st.columns([2.4, 1.6, 1.2], vertical_alignment="center")
            a.success(f"Saved {len(saved)} to your library.")
            if project:
                if b.button(f"Re-analyze {project['name']}", icon=":material/refresh:", type="primary", width="stretch", key="pv_reanalyze"):
                    st.session_state[f"pending_{project['id']}"] = ("analyze", False)
                    ui.go("p", pid=project["id"], view="overview")
            elif b.button("Re-analyze affected projects", icon=":material/refresh:", type="primary", width="stretch", key="pv_gaps"):
                ui.go("knowledge", tab="gaps")
            if c.button("Browse tables", icon=":material/menu_book:", width="stretch", key="pv_browse"):
                ui.go("knowledge", tab="tables")
            return
        a, b = st.columns([3, 1.2], vertical_alignment="center")
        a.caption(f"{total} of {len(p['tables']) + len(p['fms']) + len(p['fm_sources'])} selected · merged into existing entries, nothing is deleted")
        if b.button(f"Save {total} to library", icon=":material/check:", type="primary", width="stretch", disabled=not total, key="pv_save"):
            origin = "ai" if is_ai else {"snowflake": "snowflake", "ddic": "ddic"}.get(p["format"], "import")
            tables_ = [{**t, "fields_complete": complete.get(t["name"], False) and not is_ai} for t in p["tables"] if picks.get(f"t:{t['name']}")]
            res = kn.save(tables_, [f for f in p["fms"] if picks.get(f"f:{f['name']}")],
                          [{"name": s["name"], "source": s["source"]} for s in p["fm_sources"] if picks.get(f"s:{s['name']}")], p["s4"], origin, "merge")
            items = res["tables"] + res["fms"] + res["fm_sources"] + res["s4"]
            st.session_state.kn_saved = items
            changed()
            if res["errors"]:
                ui.notify("warn", f"Saved {len(items)}, {len(res['errors'])} skipped", "; ".join(res["errors"][:3]))
            else:
                ui.notify("ok", f"Saved {ui.plural(len(items), 'item')} to your library", "Every project uses it from the next analysis.")
            st.rerun()


# ---------------------------------------------------------------------- gaps
def gaps_tab(gaps: dict) -> None:
    if gaps["projects_scanned"] == 0:
        ui.empty("No analysed projects yet. Gaps appear here after an analysis.", "folder")
        if st.button("New conversion", type="primary"):
            ui.go("new")
        return
    if not gaps["tables"] and not gaps["fms"]:
        ui.empty(f"No gaps across {gaps['projects_scanned']} analysed projects: every referenced table and function module resolves.", "shield")
        return
    missing = [g for g in gaps["tables"] if g["reason"] == "missing"]
    nodesc = [g for g in gaps["tables"] if g["reason"] == "no_description"]
    filled_projects = {pr["id"]: pr for g in gaps["tables"] + gaps["fms"] if g["filled"] for pr in g["projects"]}
    selected = [k for k in st.session_state.get("gap_sel", [])]
    with ui.panel("kn5"):
        a, b, c, d, e = st.columns([0.9, 1.2, 1.3, 1.5, 2.6], vertical_alignment="center")
        a.markdown(f"<span class='muted' style='font-size:13px'><b class='fg'>{len(selected)}</b> selected</span>", unsafe_allow_html=True)
        tables_sel = [k[2:] for k in selected if k.startswith("t:")]
        fms_sel = [k[2:] for k in selected if k.startswith("f:")]

        def fill(method: str | None = None) -> None:
            if tables_sel:
                ui.go("knowledge", tab="add", tables=",".join(tables_sel), method=method)
            ui.go("knowledge", tab="add", fms=",".join(fms_sel), method=method, kind="fms")

        if b.button("Fill selected", icon=":material/auto_fix_high:", type="primary", width="stretch", disabled=not selected, key="gp_fill"):
            fill()
        if c.button("From Snowflake", icon=":material/database:", width="stretch", disabled=not tables_sel or bool(fms_sel), key="gp_sf"):
            fill("snowflake")
        if d.button("Prompt for any AI", icon=":material/content_copy:", width="stretch", disabled=not selected, key="gp_prompt"):
            fill("prompt")
        if filled_projects:
            if e.button(f"Re-analyze {ui.plural(len(filled_projects), 'project')} with new knowledge", icon=":material/refresh:", width="stretch", key="gp_re"):
                ok = 0
                with st.status(f"Re-analyzing {len(filled_projects)} project(s)…", expanded=True) as status:
                    for pr in filled_projects.values():
                        st.write(pr["name"])
                        if ui.guard(core.analyze, pr["id"], title=f"{pr['name']}: analysis failed") is not None:
                            ok += 1
                    status.update(label=f"Re-analyzed {ok} of {len(filled_projects)}", state="complete")
                changed()
                ui.notify("ok" if ok == len(filled_projects) else "warn", f"Re-analyzed {ok} of {ui.plural(len(filled_projects), 'project')}")
                st.rerun()
        else:
            e.caption(f"{gaps['projects_scanned']} analysed projects scanned")
    chosen = set(selected)
    chosen = gap_section("Tables with no definition", "Fields came only from how the code uses them. Add them to get exact types, keys and names.", "database",
                         [(f"t:{g['name']}", g, f"uses {', '.join(g['columns'])}" if g["columns"] else "", "feeds output" if g["in_slice"] else None) for g in missing], chosen)
    chosen = gap_section("Function modules with unknown behaviour", "Calls whose effect the converter cannot reproduce. Describe the behaviour or provide the source.", "code",
                         [(f"f:{g['name']}", g, "", f"{ui.plural(g['calls'], 'call')}" if g["reachable"] else "not reached") for g in gaps["fms"]], chosen)
    if nodesc:
        chosen = gap_section("Tables without a description", "Columns are known (from Snowflake), but there is no text for business names. Optional: type one and press Enter.",
                             "book", [(f"t:{g['name']}", g, "", None) for g in nodesc], chosen, describe=True)
    if chosen != set(selected):
        st.session_state.gap_sel = sorted(chosen)
        st.rerun()


def describe_table(name: str, key: str) -> None:
    text = (st.session_state.get(key) or "").strip()
    if not text:
        return
    res = kn.save([{"name": name, "description": text, "fields": []}], origin="manual", mode="merge")
    if res["errors"]:
        ui.notify("error", "Not saved", "; ".join(res["errors"]))
    else:
        changed()
        ui.notify("ok", f"{name}: description saved")


def gap_section(title: str, hint: str, ico: str, rows: list, chosen: set[str], describe: bool = False) -> set[str]:
    if not rows:
        return chosen
    with ui.panel("kn6"):
        ui.heading(f"{title} <span class='faint tabular'>({len(rows)})</span>", hint, ico)
        for key, g, extra, flag in rows:
            a, b, c, d = st.columns([0.4, 2, 3.4, 2.4], vertical_alignment="center")
            if g["filled"]:
                a.markdown(f"<span class='ok'>{icon('okcircle', 18)}</span>", unsafe_allow_html=True)
            elif a.checkbox("Select", value=key in chosen, key=f"gs_{key}_{describe}", label_visibility="collapsed"):
                chosen.add(key)
            else:
                chosen.discard(key)
            tag = badge("added · re-analyze to use", "ok") if g["filled"] else (badge(flag, "warn" if flag == "feeds output" else "slate") if flag else "")
            b.markdown(f"<span class='mono fg' style='font-weight:600'>{esc(g['name'])}</span> {tag}", unsafe_allow_html=True)
            if describe and not g["filled"]:
                field = f"gd_{g['name']}"
                c.text_input("Description", key=field, placeholder="Business description, e.g. Stock movements (custom)", label_visibility="collapsed",
                             on_change=describe_table, args=(g["name"], field))
            else:
                c.markdown(f"<span class='mono faint' style='font-size:11px'>{esc(extra)}</span>", unsafe_allow_html=True)
            links = " ".join(f"<a class='chip plain' href='?page=p&pid={pr['id']}'>{esc(pr['name'])}</a>" for pr in g["projects"][:3])
            more = f" <span class='faint' style='font-size:11px'>+{len(g['projects']) - 3}</span>" if len(g["projects"]) > 3 else ""
            d.markdown(links + more, unsafe_allow_html=True)
    return chosen


# ---------------------------------------------------------------------- library files
@st.dialog("Reset your library?")
def confirm_reset() -> None:
    st.write("Everything you added (tables, function modules, sources, remaps) stops being used. The folder is renamed to a timestamped backup, not deleted.")
    a, b = st.columns(2)
    if a.button("Cancel", width="stretch"):
        st.rerun()
    if b.button("Reset", type="primary", width="stretch"):
        kn.reset_library()
        changed()
        st.session_state.pop("raw_editor", None)
        ui.notify("ok", "Library reset", "A backup folder was kept next to it.")
        st.rerun()


def files_tab(ov: dict) -> None:
    side, main = st.columns([1, 3])
    with side:
        names = [f for f, _ in kn.RAW_FILES]
        desc = dict(kn.RAW_FILES)
        file = st.radio("File", names, key="raw_file", format_func=lambda f: f"{f} — {desc[f]}", label_visibility="collapsed")
        ui.html(f'<div style="border-radius:12px;border:1px solid var(--c-line);background:var(--c-sunken);padding:16px;font-size:12px;color:var(--c-fg-muted);margin-top:10px">'
                f'<div class="eyebrow faint" style="margin-bottom:6px">Location</div><div class="mono fg" style="font-size:11px;word-break:break-all">{esc(ov["library"]["path"])}</div>'
                f'<p style="margin-top:8px;line-height:1.55">Same layout as a knowledge pack. Export it to move the library to another machine, or import the zip on another '
                f'installation from Add knowledge → Paste or upload.</p></div>')
        st.download_button("Export as zip", data=kn.export_library(), file_name="tcb_knowledge_library.zip", mime="application/zip", icon=":material/download:",
                           width="stretch", key="raw_export")
        if st.button("Import a zip or pack", icon=":material/upload:", width="stretch", key="raw_import"):
            ui.go("knowledge", tab="add", method="paste")
        if st.button("Reset library", icon=":material/restart_alt:", width="stretch", key="raw_reset"):
            confirm_reset()
    with main:
        original = kn.raw_file(file)
        if st.session_state.get("raw_loaded") != file:
            st.session_state.raw_loaded = file
            st.session_state.raw_editor = original
            st.session_state.pop("raw_errors", None)
        dirty = st.session_state.get("raw_editor") != original
        a, b, c = st.columns([4, 1, 1], vertical_alignment="center")
        a.markdown(f"<span class='mono fg' style='font-weight:600'>{esc(file)}</span> {badge('unsaved', 'warn') if dirty else ''}", unsafe_allow_html=True)
        if b.button("Validate", icon=":material/verified_user:", width="stretch", key="raw_validate"):
            st.session_state.raw_errors = kn.validate_raw(file, st.session_state.get("raw_editor") or "")
        if c.button("Save", icon=":material/save:", type="primary", width="stretch", key="raw_save", disabled=not dirty):
            try:
                kn.write_raw(file, st.session_state.get("raw_editor") or "")
                st.session_state.raw_errors = []
                changed()
                ui.notify("ok", f"{file} saved")
                st.session_state.pop("raw_loaded", None)
                st.rerun()
            except core.ServiceError as exc:
                st.session_state.raw_errors = [str(exc)]
        errors = st.session_state.get("raw_errors")
        if errors:
            ui.html(ui.callout("bad", f"<b class='bad'>{ui.plural(len(errors), 'problem')}</b><ul class='mono' style='font-size:11px;margin:4px 0 0'>"
                                      + "".join(f"<li>{esc(e)}</li>" for e in errors[:8]) + "</ul>"))
        elif errors == []:
            ui.html(ui.callout("ok", "Valid; loads cleanly."))
        st.text_area("YAML", key="raw_editor", height=560, label_visibility="collapsed")
