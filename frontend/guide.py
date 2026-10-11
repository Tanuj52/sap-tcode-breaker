"""User guide: a getting-started checklist and a walkthrough of every module."""

from __future__ import annotations

import streamlit as st

from backend import core
from frontend import ui
from frontend.ui import badge, esc, icon

GUIDE_CSS = """<style>
.st-key-guide_row { gap: 40px !important; align-items: flex-start !important; flex-wrap: nowrap !important; }
.st-key-guide_toc { position: sticky; top: 24px; }
.toc a { display: flex; align-items: center; gap: 10px; padding: 6px 10px; border-radius: 8px; font-size: 13px; color: var(--c-fg-muted); text-decoration: none; }
.toc a:hover { background: var(--c-surface-2); color: var(--c-fg); }
.toc a span.n { width: 20px; font-family: "JetBrains Mono", monospace; font-size: 10.5px; color: var(--c-fg-faint); }
.gsec { scroll-margin-top: 24px; }
.gsec h2 { font-family: Fraunces, Georgia, serif; font-weight: 500; letter-spacing: -.02em; font-size: 26px; line-height: 1.2; color: var(--c-fg); margin: 6px 0 0; padding: 0; }
.gsec .lead { margin-top: 8px; max-width: 760px; font-size: 14.5px; line-height: 1.65; color: var(--c-fg-muted); }
.gsec p, .gsec li { font-size: 13.5px; line-height: 1.65; color: var(--c-fg-muted); }
.gsec b { color: var(--c-fg); font-weight: 600; }
.gsec ul { margin: 8px 0 0; padding-left: 18px; }
.gsec li { margin: 3px 0; }
.ggrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; margin-top: 18px; }
.gcard { padding: 18px 20px; }
.gcard .h { display: flex; align-items: center; gap: 10px; font-size: 14px; font-weight: 600; color: var(--c-fg); }
.gcard p { margin: 8px 0 0; font-size: 13px; }
.kbd { display: inline-flex; align-items: center; border-radius: 6px; border: 1px solid var(--c-line-strong); border-bottom-width: 2px; background: var(--c-surface);
  padding: 0 6px; font: 500 11px "JetBrains Mono", monospace; color: var(--c-fg); line-height: 18px; }
.qstep { position: relative; display: flex; gap: 14px; padding: 18px 20px; text-decoration: none !important; }
.qstep .num { display: flex; width: 30px; height: 30px; flex-shrink: 0; align-items: center; justify-content: center; border-radius: 99px; font: 600 12px "JetBrains Mono", monospace;
  border: 1px solid var(--c-line-strong); background: var(--c-surface); color: var(--c-fg-muted); }
.qstep.done .num { background: var(--c-accent); border-color: var(--c-accent); color: var(--c-on-accent); }
.qstep .t { font-size: 14px; font-weight: 600; color: var(--c-fg); }
.qstep .d { margin-top: 3px; font-size: 12.5px; line-height: 1.5; color: var(--c-fg-muted); }
.qstep .go { margin-top: 10px; display: flex; width: fit-content; align-items: center; gap: 6px; font-size: 12.5px; font-weight: 500; color: var(--c-accent); }
.qgrid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
@media (min-width: 1500px) { .qgrid { grid-template-columns: repeat(4, minmax(0, 1fr)); } }
.flowstrip { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-top: 16px; }
.flowstrip .s { display: inline-flex; align-items: center; gap: 8px; border-radius: 8px; border: 1px solid var(--c-line); background: var(--c-surface); padding: 6px 12px;
  font-size: 12.5px; font-weight: 500; color: var(--c-fg); }
.flowstrip .s .ico { color: var(--c-accent); }
.flowstrip .ar { color: var(--c-fg-faint); }
</style>"""

SECTIONS = [
    ("start", "Getting started"),
    ("idea", "How it works"),
    ("connect", "Connect Snowflake"),
    ("layers", "Data layers"),
    ("new", "Start a conversion"),
    ("understand", "Understand the program"),
    ("context", "Add context"),
    ("sql", "Generate SQL"),
    ("validate", "Validate"),
    ("knowledge", "Knowledge library"),
    ("downloads", "Downloads"),
    ("run", "Run and deploy"),
    ("faq", "Troubleshooting"),
]


@st.cache_data(ttl=120, show_spinner=False)
def demo_ready() -> bool:
    return bool(core.demo_data_status().get("ready"))


def checklist() -> list[tuple[str, str, str, str, bool]]:
    d = core.defaults()
    connected = bool(ui.sf_status().get("connected"))
    return [
        ("Connect Snowflake", "One account, user and sign-in. Needed for Cortex, live schema reads and validation.", "?page=settings&section=connection", "Open connection",
         connected),
        ("Choose your data layers", "Where the replicated SAP tables live, and where generated views go.", "?page=settings&section=layers", "Set layers",
         bool(d.get("source_database") and d.get("source_schema"))),
        ("Load demo data (optional)", "Synthetic SFLIGHT / SD / MM tables so the samples compile and compare row by row.", "?page=samples", "Open samples",
         connected and demo_ready()),
        ("Convert a program", "Upload or paste the ABAP of a T-code, or open a sample, then Run all.", "?page=new", "New conversion", bool(core.projects())),
    ]


def quick_start() -> str:
    cards = "".join(f'<a class="card lift qstep{" done" if ok else ""}" href="{href}"><span class="num">{icon("check", 14, 3) if ok else i + 1}</span><div style="min-width:0">'
                    f'<div class="t">{t}</div><div class="d">{d}</div><div class="go">{"Done · " if ok else ""}{label}{icon("arrow", 13)}</div></div></a>'
                    for i, (t, d, href, label, ok) in enumerate(checklist()))
    return f'<div class="qgrid">{cards}</div>'


def section(sid: str, n: int, eyebrow: str, title: str, lead: str, body: str = "") -> str:
    return (f'<section class="gsec fade-up" id="{sid}" style="margin-top:{"0" if n == 1 else "52px"}"><div class="eyebrow accent">{n:02d} · {eyebrow}</div><h2>{title}</h2>'
            f'<p class="lead">{lead}</p>{body}</section>')


def cards(items: list[tuple[str, str, str]]) -> str:
    return '<div class="ggrid">' + "".join(f'<div class="card gcard"><div class="h"><span class="icon-tile">{icon(ic)}</span>{t}</div><p>{b}</p></div>'
                                           for ic, t, b in items) + "</div>"


def strip(items: list[tuple[str, str]]) -> str:
    arrow = f'<span class="ar">{icon("arrow", 14)}</span>'
    return '<div class="flowstrip">' + arrow.join(f'<span class="s">{icon(ic, 14)}{t}</span>' for ic, t in items) + "</div>"


def render() -> None:
    st.markdown(GUIDE_CSS, unsafe_allow_html=True)
    ui.page_header("User guide", "book", "How to use T-code Breaker",
                   "From a fresh install to validated Snowflake SQL. Follow the four steps below once, then every conversion is upload, review and Run all.")
    with st.container(horizontal=True, key="guide_row"):
        with st.container(width=230, key="guide_toc"):
            links = "".join(f'<a href="#{sid}"><span class="n">{i + 1:02d}</span>{t}</a>' for i, (sid, t) in enumerate(SECTIONS))
            ui.html(f'<div class="eyebrow faint" style="padding:22px 10px 8px">On this page</div><nav class="toc">{links}</nav>')
        with st.container(key="guide_body"):
            ui.html('<div style="height:14px"></div>' + body())


def body() -> str:
    out = section("start", 1, "Start here", "Getting started", "Four steps take you from an empty install to a converted program. Steps already done are ticked; "
                  "each card opens the right screen.", f'<div style="margin-top:18px">{quick_start()}</div>')
    out += section("idea", 2, "Concept", "How it works",
                   "The program is executed symbolically, not summarized by a prompt. Every change of an internal table becomes one CTE; FOR ALL ENTRIES, READ TABLE, "
                   "COLLECT, LOOP/APPEND and control breaks map to joins, aggregates and window functions. A model is used only for the few steps rules cannot "
                   "translate, one small prompt each, and every result is compile-checked.",
                   strip([("upload", "Upload"), ("network", "Analyze"), ("tag", "Context"), ("wand", "Convert"), ("shield", "Validate")])
                   + cards([("cpu", "Rules first", "Most programs convert with rules only. The project shows a <b>rules only</b> badge when no model was needed."),
                            ("lock", "Confidential by default", "Projects are confidential: only Snowflake Cortex and private models may see the code."),
                            ("database", "Live metadata", "Columns and types are read from your raw layer's INFORMATION_SCHEMA at every analysis; no knowledge pack is required.")]))
    out += section("connect", 3, "Settings → Snowflake connection", "Connect Snowflake",
                   "The app keeps exactly one connection. Open <b>Settings → Snowflake connection</b>, choose <b>New connection</b>, enter the account identifier "
                   "(orgname-accountname), user and sign-in method, then <b>Test</b> and <b>Save and connect</b>. The sidebar footer turns green with the account, role and warehouse.",
                   cards([("key", "Sign-in methods", "Password, programmatic access token (PAT), key pair (.p8 file) or OAuth token. SSO in a browser works when you run the app on your own machine."),
                          ("plug", "Change or remove", "<b>Edit</b> updates the saved details, <b>New connection</b> replaces it, <b>Remove connection</b> deletes it and its secrets."),
                          ("shield", "Inside Snowflake", "Deployed on the Streamlit container runtime or SPCS, the app signs in with the Snowflake session automatically; you only pick the warehouse and role."),
                          ("lock", "Where secrets live", "In <span class='mono'>data/app_settings.json</span> next to the app, owner-only (0600). They are masked after saving and never sent back to the page.")]))
    out += section("layers", 4, "Settings → Data layers", "Data layers",
                   "Tell the converter where SAP lives in Snowflake and where views should go. These are defaults for new projects; each project can override them "
                   "from the <b>project settings</b> button in its header.",
                   cards([("database", "Source: raw SAP layer", "The database.schema with the replicated tables (VBAK, MARA, Z tables …). The SQL reads from here."),
                          ("layers", "Target: gold layer", "Where <span class='mono'>CREATE OR REPLACE VIEW</span> puts the view. Empty means the same as the source."),
                          ("braces", "Table name pattern", "If replicated tables are renamed, e.g. <span class='mono'>SAP_{table}</span> or <span class='mono'>{table}_RAW</span>."),
                          ("sliders", "Client and language", "Optional MANDT filter and SY-LANGU value used for text tables.")]))
    out += section("new", 5, "New conversion", "Start a conversion",
                   "Use <b>New conversion</b> in the sidebar. Bring the code one of three ways, name the project, and pick <b>Guided</b> (stop after analysis to review) "
                   "or <b>Streamlined</b> (analyze, convert and validate in one go).",
                   cards([("upload", "Upload files", "Main program, includes and function modules, or one .zip of the whole package. Includes are linked by name."),
                          ("clipboard", "Paste code", "Any size. For several objects in one paste, start each with a line like <span class='mono'>*** FILE: zmy_report_top.abap</span>."),
                          ("flask", "Open a sample", "Bundled SFLIGHT and SD/MM programs with hand-written reference SQL, so validation compares results row by row.")]))
    out += section("understand", 6, "Project → Understand", "Understand the program",
                   "Every project opens on the <b>Overview</b>. The left panel shows the pipeline status and the sections; hide it with the panel button in the header for more room.",
                   cards([("layers", "Overview", "Conversion readiness, the program slice that feeds the output, SAP tables and columns, inputs, findings and the report output with column lineage."),
                          ("network", "Data flow", "An interactive map of tables, internal tables and steps. Click a node for its inputs, filters, columns, notes, SQL and ABAP."),
                          ("branch", "Call tree", "Events in execution order with every FORM, method and function module they call. Greyed routines are never called."),
                          ("code", "Source", "The uploaded ABAP. Marked lines are the slice that feeds the output; links on findings and nodes jump to the exact line.")])
                   + '<div class="card" style="margin-top:14px;padding:16px 20px"><div class="eyebrow faint">Data flow controls</div><ul>'
                   '<li><span class="kbd">scroll</span> zooms around the pointer; <span class="kbd">drag</span> the background to pan.</li>'
                   '<li>The <b>+</b>, <b>−</b> and <b>fit</b> buttons sit bottom left; fit brings the whole diagram back into view.</li>'
                   '<li><b>Expand all columns</b> (top left) or a node\'s <b>N columns</b> row lists its fields; the layout re-flows around them.</li>'
                   '<li><b>Business names</b> and <b>Hide function modules</b> in the toolbar change the map instantly; <b>PNG</b> and <b>SVG</b> download what you see.</li>'
                   '</ul></div>')
    out += section("context", 7, "Project → Context", "Add context (optional)",
                   "A checkpoint before conversion. Everything here is optional; the converter uses it from the next analysis.",
                   cards([("tag", "Business names", "Plain-English names for tables, columns and calculated fields; they appear in the map, the report and the SQL comments."),
                          ("function", "Function modules", "Upload a custom FM's source, or describe its result as a SQL expression such as <span class='mono'>UPPER({INPUT})</span>."),
                          ("database", "Table renames", "Map an SAP table to a physical Snowflake object when it does not follow the name pattern."),
                          ("monitor", "Result table", "Pick the internal table that is the report's output if the automatic choice is wrong.")]))
    out += section("sql", 8, "Project → SQL", "Generate SQL",
                   "Choose <b>CTE query</b> (WITH … SELECT) or <b>CREATE VIEW</b>, decide whether a model may fill unresolved steps, and press <b>Convert</b>. "
                   "Each step card shows whether rules or a model produced it.",
                   cards([("wand", "One CTE per step", "Steps follow the program's execution order, so the SQL reads like the ABAP it came from."),
                          ("sparkles", "AI for leftovers", "Off means rules only: unresolved steps stay as clearly marked placeholders. The default model is set in Settings → Models.")]))
    out += section("validate", 9, "Project → Validate", "Validate",
                   "Validation runs five checks in order and needs no SAP data: empty stub tables are built from the schema metadata in "
                   "<span class='mono'>TCODE_BREAKER.STUBS</span> (configurable in Settings → Conversion defaults).",
                   '<div class="card" style="margin-top:18px;padding:18px 20px"><ol class="steps">'
                   + "".join(f'<li><span class="dot">{i + 1}</span><div><b>{t}</b><div style="font-size:12.5px">{d}</div></div></li>' for i, (t, d) in enumerate([
                       ("SQL syntax", "parsed with sqlglot in the Snowflake dialect"), ("No leftover placeholders", "every step resolved by rules, context or a model"),
                       ("Referenced tables exist", "each table is found in the source layer"), ("Compile on Snowflake", "EXPLAIN against the stub tables"),
                       ("Row-by-row comparison", "against a reference SQL, when one exists (samples ship with one)")]))
                   + "</ol></div>")
    out += section("knowledge", 10, "Knowledge", "Knowledge library",
                   "Nothing here is required. Add what the converter cannot see in Snowflake (descriptions, keys, custom function modules, tables that live outside Snowflake) "
                   "and every project uses it from its next analysis.",
                   cards([("database", "Six ways to add", "SAP dictionary replica, Snowflake schema, paste or upload (CSV, Excel, JSON, YAML, SE11 exports), ask any AI, AI proposal, or write it yourself."),
                          ("alert", "Gaps", "Tables and function modules that analyzed projects reference but nothing resolves, with one-click fixes."),
                          ("package", "Export", "<b>Export library</b> downloads everything as a zip you can share or version.")]))
    out += section("downloads", 11, "Project header → Download", "Downloads",
                   "The <b>Download</b> menu in a project's header offers the SQL file, a conversion report (markdown), column lineage (CSV), the full analysis and "
                   "validation (JSON), a diagram (SVG) and a full bundle with the sources (zip).")
    out += section("run", 12, "Operations", "Run and deploy",
                   "The whole tool is this one folder: the Streamlit front end, the conversion engine, the ABAP parser and the knowledge packs.",
                   cards([("monitor", "On your machine", "<span class='mono'>pip install -r requirements.txt</span>, then <span class='mono'>streamlit run streamlit_app.py</span>. "
                           "Node.js is used for parsing; a bundled copy is installed from requirements if none is on PATH."),
                          ("rocket", "In Snowflake", "Deploy to the Streamlit container runtime or Snowpark Container Services; the app then uses the Snowflake session. "
                           "The warehouse runtime is not supported because the parser needs Node.js."),
                          ("history", "Your data", "Projects, settings and the library live in the <span class='mono'>data/</span> folder; back it up or mount it on persistent storage when deployed.")]))
    faq = [("The sidebar says Not connected", "Open Settings → Snowflake connection. The error under the account explains why (expired token, wrong account, missing role); "
            "use Edit or New connection, then Test."),
           ("Schema not read", "The project's source layer is empty or the role cannot read it. Field lists are then inferred from the code; set the layer in project settings and Re-analyze."),
           ("Validation skipped the comparison", "Only programs with a reference SQL compare row by row. Samples include one; add yours to a knowledge pack's gold/ folder."),
           ("A model call failed", "Check Settings → Models (Test model). Confidential projects may only use Cortex or private models."),
           ("The data flow looks crowded", "Hide function modules, collapse columns, use fit, and hide the project panel from the header for more width.")]
    out += section("faq", 13, "Help", "Troubleshooting", "Common situations and what to do.",
                   '<div class="card" style="margin-top:18px;overflow:hidden">' + "".join(
                       f'<div style="padding:14px 20px;border-top:{"0" if i == 0 else "1px solid var(--c-line)"}"><div class="row" style="gap:8px;font-size:13.5px;font-weight:600;color:var(--c-fg)">'
                       f'<span class="warn">{icon("info", 15)}</span>{esc(q)}</div><div style="margin-top:4px;font-size:13px;line-height:1.6;color:var(--c-fg-muted)">{esc(a)}</div></div>'
                       for i, (q, a) in enumerate(faq)) + "</div>")
    return out + f'<div class="faint" style="margin-top:40px;font-size:12px">T-code Breaker {badge(esc(core.VERSION))}</div>'
