"""Home, Projects, New conversion, Samples and Settings pages."""

from __future__ import annotations

import re

import streamlit as st

from backend import core
from frontend import guide, theme, ui
from frontend.ui import badge, esc, icon

RUN = [("read", "program + 6 includes", "12,480 lines"), ("parse", "statements, macros", "9,214 stmts"), ("schema", "RAW.SAP columns", "14 tables"),
       ("slice", "lines feeding output", "6.2%"), ("interp", "itab versions → CTEs", "22 steps"), ("emit", "CREATE VIEW", "rules only"),
       ("explain", "compile on Snowflake", "ok")]
CONSTRUCTS = ["SELECT … FOR ALL ENTRIES", "READ TABLE … BINARY SEARCH", "LOOP AT … APPEND", "COLLECT", "AT END OF / SUM", "MODIFY … TRANSPORTING",
              "DELETE … WHERE", "SORT / DELETE ADJACENT DUPLICATES", "CALL FUNCTION", "CLASS … METHODS", "DEFINE macros", "INCLUDE",
              "SELECT-OPTIONS / RANGES", "IF / CASE", "inline DATA(…)", "VALUE #( FOR … )", "ADD / SUBTRACT", "READ TABLE … INDEX", "sy-subrc"]
STEPS = [("code", "Bring the code", "Upload files or a zip, or paste. Includes are linked by name; renamed exports are matched."),
         ("network", "Analyze", "Tables, columns, joins, FORMs, methods and function calls in execution order."),
         ("tag", "Add context", "Optional: FM sources, business names, table renames and the result table."),
         ("wand", "Convert", "Rules first. A model fills only the steps rules cannot, one small prompt each."),
         ("shield", "Validate", "Syntax, placeholders, EXPLAIN on Snowflake and a row-by-row diff to a reference.")]
ABOUT = {
    "zsf01_carrier_list": ("Carrier master list", ["SELECT", "ALV"]),
    "zsf02_connections": ("Flight connections with carriers", ["JOIN", "select-options"]),
    "zsf03_flight_occupancy": ("Seat occupancy per flight", ["computed columns", "ROUND"]),
    "zsf04_booking_detail": ("Booking detail with lookups", ["FOR ALL ENTRIES", "READ TABLE"]),
    "zsf05_monthly_revenue": ("Monthly revenue", ["COLLECT", "GROUP BY"]),
    "zsf06_peak_flights": ("Peak flights", ["IF/CASE", "DELETE WHERE"]),
    "zsf07_customer_trips": ("Customer trips (includes)", ["INCLUDEs", "FORMs"]),
    "zsf08_connection_stats": ("Large program (5k lines)", ["slicing", "dead code"]),
    "zsf09_carrier_totals": ("Control-break totals", ["AT END OF", "SUM", "AI step"]),
    "zs4_goods_movements": ("Goods movements on S/4HANA", ["MATDOC remap", "S/4"]),
    "zs4_sales_status": ("Sales order status on S/4HANA", ["VBUK→VBAK", "inline DATA"]),
}
STAGE_ORDER = ["uploaded", "analyzed", "reviewed", "converted", "validated"]
PASTE_HINT = ("* Paste the ABAP of your T-code here: main program, includes and custom function modules.\n"
              "* For several objects in one paste, start each with a marker line:\n*** FILE: zmy_report.abap\nREPORT zmy_report.\n"
              "INCLUDE zmy_report_top.\n...\n*** FILE: zmy_report_top.abap\nDATA gt_out TYPE STANDARD TABLE OF ...")

PAGE_CSS = """<style>
.hero { position: relative; overflow: hidden; border-radius: 20px; margin-top: 28px; }
.hero .glow { position: absolute; right: -160px; top: -160px; width: 520px; height: 520px; border-radius: 99px; opacity: .25; filter: blur(60px);
  background: radial-gradient(circle, var(--c-side-accent), transparent 65%); pointer-events: none; }
.hero .gridbg { position: absolute; inset: 0; opacity: .6; pointer-events: none; -webkit-mask-image: radial-gradient(ellipse at 70% 20%, black 10%, transparent 70%); }
.hero-in { position: relative; display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.05fr); gap: 48px; align-items: center; padding: 52px 48px 40px; }
@media (max-width: 1100px) { .hero-in { grid-template-columns: 1fr; padding: 36px 28px; } }
.hero h1 { font-family: Fraunces, Georgia, serif; font-weight: 500; letter-spacing: -.02em; font-size: 50px; line-height: 1.04; color: var(--c-side-fg); margin: 24px 0 0; padding: 0; }
.hero h1 em { font-style: italic; font-weight: 400; color: var(--c-side-accent); }
.hero p.lead { margin-top: 22px; max-width: 560px; font-size: 16.5px; line-height: 1.6; color: var(--c-side-muted); }
.pill { display: inline-flex; align-items: center; gap: 8px; border-radius: 99px; border: 1px solid var(--c-side-line); background: color-mix(in oklab, var(--c-side-2) 70%, transparent);
  padding: 4px 12px; font-size: 12px; color: var(--c-side-muted); }
.hbtn { display: inline-flex; align-items: center; gap: 8px; border-radius: 9px; padding: 12px 20px; font-size: 15px; font-weight: 600; text-decoration: none !important; transition: filter .15s, background .15s; }
.hbtn.p { background: var(--c-ink-btn); color: var(--c-ink-btn-fg) !important; }
.hbtn.p:hover { filter: brightness(1.07); }
.hbtn.s { border: 1px solid var(--c-side-line); background: rgba(255,255,255,.04); color: var(--c-side-fg) !important; font-weight: 500; }
.hbtn.s:hover { background: rgba(255,255,255,.08); }
.console { position: relative; overflow: hidden; border-radius: 14px; border: 1px solid var(--c-side-line); background: rgba(0,0,0,.25); box-shadow: 0 40px 80px -40px rgba(0,0,0,.8); }
.console .bar1 { display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid var(--c-side-line); padding: 10px 16px; }
.console .dots span { display: inline-block; width: 10px; height: 10px; border-radius: 99px; background: rgba(255,255,255,.15); margin-right: 6px; }
.console .body { min-height: 216px; padding: 16px; font-family: "JetBrains Mono", monospace; font-size: 12px; line-height: 1.7; }
.console .ln { display: flex; align-items: center; gap: 12px; }
.console .sql { border-top: 1px solid var(--c-side-line); background: rgba(0,0,0,.2); padding: 12px 16px; font-family: "JetBrains Mono", monospace; font-size: 11.5px; line-height: 1.7;
  opacity: 0; animation: fadein .6s ease forwards; animation-delay: 4.8s; }
.proof { position: relative; display: grid; grid-template-columns: repeat(4, 1fr); border-top: 1px solid var(--c-side-line); }
.proof > div { padding: 22px 48px; }
.proof > div + div { border-left: 1px solid var(--c-side-line); }
@media (max-width: 1100px) { .proof { grid-template-columns: repeat(2, 1fr); } .proof > div { padding: 18px 28px; } }
.qs { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 22px; }
.qs a { position: relative; overflow: hidden; display: block; text-decoration: none !important; padding: 24px; }
.qs a .bar { position: absolute; left: 0; right: 0; bottom: 0; height: 3px; background: var(--c-accent); transform: scaleX(0); transform-origin: left; transition: transform .3s; border-radius: 0; }
.qs a:hover .bar { transform: scaleX(1); }
.qs .tile { display: inline-flex; width: 44px; height: 44px; align-items: center; justify-content: center; border-radius: 10px; background: var(--c-accent); color: var(--c-on-accent); }
.bento { display: grid; grid-template-columns: repeat(6, 1fr); gap: 16px; margin-top: 26px; }
.bento > div { padding: 24px; }
.s4 { grid-column: span 4; } .s3 { grid-column: span 3; } .s2 { grid-column: span 2; }
@media (max-width: 1100px) { .bento, .qs { grid-template-columns: 1fr; } .s4, .s3, .s2 { grid-column: span 1; } }
.sec-title { font-family: Fraunces, Georgia, serif; font-weight: 500; letter-spacing: -.02em; font-size: 30px; line-height: 1.15; color: var(--c-fg); margin: 6px 0 0; }
.flow-line { stroke-dasharray: 6 8; animation: dash 1.6s linear infinite; }
@keyframes dash { to { stroke-dashoffset: -28; } }
.pipe { position: relative; display: grid; grid-template-columns: repeat(5, 1fr); gap: 24px; margin-top: 30px; }
.pipe::before { content: ""; position: absolute; left: 10%; right: 10%; top: 24px; height: 1px; background: var(--c-line-strong); }
.pipe .c { position: relative; margin: 0 auto; display: flex; width: 48px; height: 48px; align-items: center; justify-content: center; border-radius: 99px; border: 1px solid var(--c-line-strong);
  background: var(--c-surface); color: var(--c-accent); }
.pipe .n { position: absolute; right: -4px; top: -4px; display: flex; width: 20px; height: 20px; align-items: center; justify-content: center; border-radius: 99px; background: var(--c-fg);
  color: var(--c-canvas); font-family: "JetBrains Mono", monospace; font-size: 10px; font-weight: 600; }
.ws { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 16px; margin-top: 60px; }
@media (max-width: 1100px) { .ws, .pipe { grid-template-columns: 1fr; } .pipe::before { display: none; } }
.pgrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 16px; }
.pcard { position: relative; overflow: hidden; display: block; padding: 22px 24px; text-decoration: none !important; }
.pcard .top { position: absolute; left: 0; right: 0; top: 0; height: 3px; background: var(--c-accent); opacity: 0; transition: opacity .2s; }
.pcard:hover .top { opacity: 1; }
.pdel { display: inline-flex; width: 26px; height: 26px; align-items: center; justify-content: center; border-radius: 7px; color: var(--c-fg-faint); opacity: 0; transition: opacity .15s, background .15s; cursor: pointer; }
.pcard:hover .pdel, .prow:hover .pdel { opacity: 1; }
.pdel:hover { background: color-mix(in oklab, var(--c-bad) 10%, transparent); color: var(--c-bad); }
.prow { display: flex; align-items: center; gap: 16px; padding: 12px 20px; border-top: 1px solid var(--c-line); text-decoration: none !important; transition: background .15s; }
.prow:first-child { border-top: 0; }
.prow:hover { background: color-mix(in oklab, var(--c-surface-2) 55%, transparent); }
.stats3 { margin-top: 18px; display: grid; grid-template-columns: repeat(3, 1fr); border: 1px solid var(--c-line); border-radius: 10px; overflow: hidden; background: var(--c-sunken); text-align: center; }
.stats3 > div { padding: 10px 0; } .stats3 > div + div { border-left: 1px solid var(--c-line); }
.stagebar { display: flex; gap: 6px; margin-top: 18px; } .stagebar span { flex: 1; height: 4px; border-radius: 99px; background: var(--c-line); } .stagebar span.on { background: var(--c-accent); }
.sample-head { position: relative; padding: 20px 20px 16px; border-radius: 13px 13px 0 0; min-height: 150px; }
[class*="st-key-pnl_smp_"] { padding: 0 0 18px !important; overflow: hidden; gap: 14px !important; height: 100%; }
[class*="st-key-smp_btns_"] { padding: 0 20px; margin-top: auto; }
.theme-prev { display: flex; height: 120px; border-radius: 12px 12px 0 0; overflow: hidden; }
</style>"""


def stage_bar(stage: str) -> str:
    i = STAGE_ORDER.index(stage) if stage in STAGE_ORDER else -1
    return '<div class="stagebar">' + "".join(f'<span class="{"on" if j <= i else ""}" title="{s}"></span>' for j, s in enumerate(STAGE_ORDER)) + "</div>"


# ---------------------------------------------------------------------- home
def home() -> None:
    st.markdown(PAGE_CSS, unsafe_allow_html=True)
    projects = core.projects()
    recent = sorted(projects, key=lambda p: p["updated"], reverse=True)[:6]
    counts = {"deterministic": 0, "needs_llm": 0, "partial": 0, "other": 0}
    for p in projects:
        s = (p.get("summary") or {}).get("sql_status")
        counts[s if s in counts else "other"] += 1
    total = len(projects)
    lines = sum(int((p.get("summary") or {}).get("lines") or 0) for p in projects)

    console = "".join(
        f'<div class="ln console-line" style="animation-delay:{i * 0.6:.1f}s"><span style="color:var(--c-side-accent)">{icon("okcircle", 14)}</span>'
        f'<span style="width:56px;color:var(--c-side-muted)">{t}</span><span style="flex:1;color:var(--c-side-fg);overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{x}</span>'
        f'<span style="color:var(--c-side-muted)">{m}</span></div>' for i, (t, x, m) in enumerate(RUN))
    proof = "".join(
        f'<div><div class="display tabular" style="font-size:32px;line-height:1;color:var(--c-side-fg)">{v}</div><div style="margin-top:8px;font-size:13px;color:var(--c-side-fg);opacity:.9">{l}</div>'
        f'<div class="mono" style="margin-top:2px;font-size:11px;color:var(--c-side-muted)">{s}</div></div>'
        for v, l, s in [("80", "public ABAP programs tested", "no knowledge pack"), ("220K", "lines parsed", "largest: abapGit, 159K in ~14 s"),
                        ("0", "crashes", "every program analyzes"), ("34 / 34", "complete outputs compile", "EXPLAIN on Snowflake")])
    chips = "".join(f'<span class="row" style="gap:8px"><span style="color:var(--c-side-accent)">{icon(i)}</span>{t}</span>'
                    for i, t in [("cpu", "Any model, even 8B"), ("lock", "Code stays in Snowflake with Cortex"), ("database", "Reads your raw schema live")])
    ui.html(f"""<section class="hero ink grain fade-up"><div class="gridbg ink-grid"></div><div class="glow"></div><div class="hero-in"><div>
<span class="pill"><span style="width:6px;height:6px;border-radius:99px;background:var(--c-side-accent)"></span>Deterministic first · AI only where rules stop</span>
<h1>Break any SAP T&#8209;code into <em>set&#8209;based</em> Snowflake SQL.</h1>
<p class="lead">Upload or paste the ABAP behind a transaction, standard or custom. Every table, column, join and call becomes an interactive map,
and the program becomes a CTE query or a <span class="mono" style="font-size:14px;color:var(--c-side-fg)">CREATE OR REPLACE VIEW</span> on your raw SAP layer.</p>
<div class="row" style="gap:12px;margin-top:34px"><a class="hbtn p" href="?page=new">Start a conversion {icon("arrow")}</a>
<a class="hbtn s" href="?page=samples">{icon("flask")}Try a sample</a></div>
<div class="row" style="gap:22px;margin-top:34px;font-size:13px;color:var(--c-side-muted)">{chips}</div></div>
<div class="console"><div class="bar1"><div class="dots"><span></span><span></span><span></span></div><div class="mono" style="font-size:10.5px">
<span style="border-radius:4px;background:var(--c-side-2);padding:2px 8px;color:var(--c-side-fg)">pipeline</span><span style="padding:2px 8px;color:var(--c-side-muted)">order_status.sql</span></div></div>
<div class="body">{console}</div><div class="sql">
<div><span style="color:var(--c-side-accent)">CREATE OR REPLACE VIEW</span> <span style="color:var(--c-side-fg)">GOLD.SALES.ORDER_STATUS</span> <span style="color:var(--c-side-accent)">AS</span></div>
<div><span style="color:var(--c-side-accent)">WITH</span> <span style="color:var(--c-side-fg)">gt_orders</span> <span style="color:var(--c-side-accent)">AS</span> <span style="color:var(--c-side-muted)">(SELECT vbak.vbeln, vbap.posnr … FROM RAW.SAP.SAP_VBAK vbak …)</span></div>
<div><span style="color:var(--c-side-muted)">&nbsp;&nbsp;&nbsp;, gt_status </span><span style="color:var(--c-side-accent)">AS</span> <span style="color:var(--c-side-muted)">(… LEFT JOIN … QUALIFY ROW_NUMBER() … = 1)</span></div>
<div><span style="color:var(--c-side-accent)">SELECT</span> <span style="color:var(--c-side-muted)">… FROM gt_status ORDER BY vbeln, posnr;</span></div></div></div></div>
<div class="proof">{proof}</div></section>""")

    steps_done = sum(1 for *_, ok in guide.checklist() if ok)
    st.markdown(guide.GUIDE_CSS, unsafe_allow_html=True)
    ui.html(f'<section style="margin-top:36px"><div class="between" style="align-items:flex-end"><div><div class="eyebrow accent">Getting started · {steps_done} of 4 done</div>'
            f'<div class="sec-title">Set up once, then convert in minutes</div></div><a class="plain row" style="gap:6px;font-size:13.5px;font-weight:500;color:var(--c-fg-muted)" '
            f'href="?page=guide">{icon("book")}Read the user guide{icon("arrow", 14)}</a></div><div style="margin-top:20px">{guide.quick_start()}</div></section>')

    marquee = "".join(f'<span class="chip" style="white-space:nowrap;background:var(--c-surface)"><span style="width:4px;height:4px;border-radius:99px;background:var(--c-accent)"></span>{esc(c)}</span>'
                      for c in CONSTRUCTS * 2)
    ui.html(f'<div class="marquee-wrap"><div class="marquee">{marquee}</div></div>')

    quick = "".join(
        f'<a class="card lift" href="{href}"><div class="between" style="align-items:flex-start"><span class="tile">{icon(ic, 20)}</span>'
        f'<span class="faint">{icon("arrowup", 20)}</span></div><div style="margin-top:20px;font-size:17px;font-weight:600;letter-spacing:-.01em;color:var(--c-fg)">{t}</div>'
        f'<div style="margin-top:6px;font-size:13.5px;line-height:1.55;color:var(--c-fg-muted)">{b}</div><div class="chip" style="margin-top:18px">{tag}</div><span class="bar"></span></a>'
        for ic, t, b, href, tag in [("upload", "Upload files", "Main program, includes, function modules, or a zip of the whole package.", "?page=new&source=upload", ".abap · .txt · .zip"),
                                    ("clipboard", "Paste code", "Drop in tens of thousands of lines. Mark several objects with *** FILE: lines.", "?page=new&source=paste", "any size"),
                                    ("flask", "Open a sample", "SFLIGHT and SD/MM programs with hand-written reference SQL for a row diff.", "?page=samples", f"{len(core.samples())} programs")])
    ui.html(f'<section style="margin-top:56px"><div class="between" style="align-items:flex-end"><div><div class="eyebrow accent">Quick start</div>'
            f'<div class="sec-title">Three ways in</div></div><a class="plain row" style="gap:6px;font-size:13.5px;font-weight:500;color:var(--c-fg-muted)" href="?page=projects">'
            f'{icon("folder")}All projects{icon("arrow", 14)}</a></div><div class="qs">{quick}</div></section>')

    abap = ('<div class="mono" style="display:grid;gap:8px;grid-template-columns:1fr 1fr;font-size:11px;line-height:1.7">'
            '<div style="border-radius:10px;border:1px solid var(--c-line);background:var(--c-sunken);padding:12px"><div class="eyebrow faint" style="margin-bottom:6px">ABAP</div>'
            '<div><span class="accent">LOOP AT</span> gt_items <span class="accent">INTO</span> ls.</div><div style="padding-left:12px"><span class="accent">AT END OF</span> matnr.</div>'
            '<div style="padding-left:24px"><span class="accent">SUM</span>.</div><div style="padding-left:24px"><span class="accent">APPEND</span> ls <span class="accent">TO</span> gt_tot.</div>'
            '<div style="padding-left:12px"><span class="accent">ENDAT</span>.</div><div><span class="accent">ENDLOOP</span>.</div></div>'
            '<div style="border-radius:10px;border:1px solid var(--c-line);background:var(--c-sunken);padding:12px"><div class="eyebrow faint" style="margin-bottom:6px">Snowflake SQL</div>'
            '<div>gt_tot <span class="accent">AS</span> (</div><div style="padding-left:12px"><span class="accent">SELECT</span> matnr,</div>'
            '<div style="padding-left:24px"><span class="accent">SUM</span>(menge) menge</div><div style="padding-left:12px"><span class="accent">FROM</span> gt_items</div>'
            '<div style="padding-left:12px"><span class="accent">GROUP BY</span> matnr)</div></div></div>')
    sources = "".join(f'<div class="between" style="border-radius:8px;border:1px solid var(--c-line);background:var(--c-sunken);padding:6px 12px;font-size:12px">'
                      f'<span class="muted">{l}</span>{badge(b, t)}</div>' for l, t, b in [("Snowflake schema", "ok", "live"), ("SAP dictionary", "info", "built-in"), ("inferred from code", "warn", "fallback")])
    bars = "".join(f'<span style="flex:1;border-radius:2px 2px 0 0;height:{h}%;background:{"var(--c-accent)" if i in (3, 5, 11) else "color-mix(in oklab,var(--c-line-strong) 60%,transparent)"}"></span>'
                   for i, h in enumerate([38, 62, 20, 80, 45, 92, 30, 55, 70, 25, 60, 85, 40, 66]))
    nodes = [(8, 14, "VBAK", "var(--c-node-table)"), (8, 62, "VBAP", "var(--c-node-table)"), (8, 110, "KNA1", "var(--c-node-table)"),
             (150, 38, "gt_orders", "var(--c-node-itab)"), (150, 98, "gt_customer", "var(--c-node-itab)"), (292, 68, "output", "var(--c-accent)")]
    links = [(0, 3), (1, 3), (2, 4), (3, 5), (4, 5)]
    paths = ""
    for a, b in links:
        sx, sy, tx, ty = nodes[a][0] + 110, nodes[a][1] + 15, nodes[b][0], nodes[b][1] + 15
        d = f"M{sx},{sy} C{sx + 24},{sy} {tx - 24},{ty} {tx},{ty}"
        paths += f'<path d="{d}" fill="none" stroke="var(--c-line-strong)" stroke-width="1.6"/><path d="{d}" fill="none" stroke="var(--c-accent)" stroke-width="1.6" class="flow-line"/>'
    rects = "".join(f'<rect x="{x}" y="{y}" width="110" height="30" rx="6" fill="var(--c-surface)" stroke="var(--c-line-strong)"/><rect x="{x}" y="{y}" width="4" height="30" rx="2" fill="{c}"/>'
                    f'<text x="{x + 13}" y="{y + 19.5}" font-size="11" fill="var(--c-fg)" font-family="JetBrains Mono, monospace">{l}</text>' for x, y, l, c in nodes)
    miniflow = ui.svg_img(f'<svg viewBox="0 0 410 150" width="410" height="150">{paths}{rects}</svg>', "width:100%;height:auto")
    layering = "".join(f'<div class="row mono" style="gap:12px;border-radius:8px;border:1px solid var(--c-line);background:var(--c-sunken);padding:8px 12px;font-size:11px;margin-left:{i * 18}px;margin-top:8px">'
                       f'<span style="width:4px;height:24px;border-radius:3px;background:{c}"></span><span style="width:40px;font-weight:600;color:var(--c-fg)">{k}</span>'
                       f'<span class="muted">{loc}</span><span class="faint" style="margin-left:auto">{obj}</span></div>'
                       for i, (k, loc, obj, c) in enumerate([("RAW", "SAP_DB.REPLICA", "SAP_{table}", "var(--c-node-table)"), ("VIEW", "GOLD.REPORTING", "ORDER_STATUS_V", "var(--c-accent)")]))
    provs = "".join(f'<span style="border-radius:6px;border:1px solid var(--c-line);background:var(--c-sunken);padding:4px 10px;font-size:12px;color:var(--c-fg-muted)">{m}</span>'
                    for m in ["Snowflake Cortex", "OpenAI", "Anthropic", "Mistral", "DeepSeek", "Groq", "Gemini", "Ollama", "OpenAI-compatible"])

    def tile(span, ic, eyebrow, title, body):
        return (f'<div class="card {span}"><div class="row accent" style="gap:8px">{icon(ic)}<span class="eyebrow">{eyebrow}</span></div>'
                f'<div style="margin-top:12px;font-size:17px;font-weight:600;letter-spacing:-.01em;color:var(--c-fg)">{title}</div>{body}</div>')

    bento = (tile("s4", "workflow", "Symbolic interpreter", "Each change of an internal table becomes one CTE",
                  '<p style="margin-top:6px;max-width:560px;font-size:13.5px;line-height:1.55;color:var(--c-fg-muted)">FOR ALL ENTRIES, READ TABLE, COLLECT, LOOP/APPEND, nested accumulation, '
                  'IF/CASE and control breaks map to joins, aggregates and window functions.</p><div style="margin-top:18px">' + abap + "</div>")
             + tile("s2", "database", "No knowledge base", "Metadata comes from your schema",
                    '<p style="margin-top:6px;font-size:13.5px;line-height:1.55;color:var(--c-fg-muted)">Columns and types are read live from the raw layer\'s INFORMATION_SCHEMA, then inferred '
                    f'from how the code uses each field.</p><div style="margin-top:18px;display:grid;gap:6px">{sources}</div>')
             + tile("s2", "braces", "Scales", "Only the slice that feeds the output",
                    '<p style="margin-top:6px;font-size:13.5px;line-height:1.55;color:var(--c-fg-muted)">Unused routines are listed, not converted. Programs with tens of thousands of lines '
                    f'analyze in seconds.</p><div style="margin-top:18px;display:flex;height:64px;align-items:flex-end;gap:4px">{bars}</div>')
             + tile("s4", "branch", "Every node explained", "An interactive data-flow map with the ABAP and SQL behind each step",
                    f'<div class="dot-grid" style="margin-top:16px;border-radius:10px;border:1px solid var(--c-line);background-color:var(--c-sunken);padding:12px">{miniflow}</div>')
             + tile("s3", "sparkles", "Bring any model", "Small prompts, each compile-checked", f'<div class="row" style="gap:6px;margin-top:16px">{provs}</div>')
             + tile("s3", "package", "Raw in, gold out", "Choose where SAP lives and where views go", f'<div style="margin-top:8px">{layering}</div>'))
    ui.html(f'<section style="margin-top:64px"><div class="eyebrow accent">Why it holds up</div><div class="sec-title" style="max-width:720px">The program is executed symbolically, '
            f'not summarized by a prompt</div><div class="bento">{bento}</div></section>')

    steps = "".join(f'<div style="text-align:center"><div class="c card">{icon(ic, 20)}<span class="n">{i + 1}</span></div><div style="margin-top:16px;font-weight:600;color:var(--c-fg)">{t}</div>'
                    f'<div style="margin:4px auto 0;max-width:220px;font-size:13px;line-height:1.55;color:var(--c-fg-muted)">{b}</div></div>' for i, (ic, t, b) in enumerate(STEPS))
    ui.html(f'<section style="margin-top:64px"><div class="eyebrow accent">How it works</div><div class="sec-title">A staged pipeline: run it end to end or stop at any step</div>'
            f'<div class="pipe">{steps}</div></section>')

    if recent:
        rows = "".join(
            f'<tr><td style="padding:12px 20px"><a class="plain row mono" style="gap:10px;font-size:13px;font-weight:500;color:var(--c-fg)" href="?page=p&pid={p["id"]}">'
            f'<span class="faint">{icon("code")}</span>{esc(p["name"])}</a></td><td class="muted">{esc(p["workspace"])}</td>'
            f'<td class="mono tabular" style="text-align:right">{ui.num((p.get("summary") or {}).get("lines")) if (p.get("summary") or {}).get("lines") else "–"}</td>'
            f'<td style="text-align:right;padding-right:20px">{badge(ui.status_label(p["summary"]["sql_status"]), ui.status_tone(p["summary"]["sql_status"])) if (p.get("summary") or {}).get("sql_status") else badge(p["stage"])}</td></tr>'
            for p in recent)
        table = (f'<table class="tbl"><thead><tr><th style="padding-left:20px;background:transparent">Project</th><th style="background:transparent">Workspace</th>'
                 f'<th style="text-align:right;background:transparent">Lines</th><th style="text-align:right;padding-right:20px;background:transparent">Status</th></tr></thead><tbody>{rows}</tbody></table>')
    else:
        table = '<div style="padding:40px;text-align:center;font-size:14px;color:var(--c-fg-muted)">No projects yet. <a class="tcb-link" href="?page=new">Start your first conversion</a>.</div>'
    pct = round(100 * counts["deterministic"] / total) if total else 0
    legend = "".join(f'<div class="row" style="gap:8px"><span style="width:8px;height:8px;border-radius:99px;background:{c}"></span><span style="color:var(--c-side-muted)">{l}</span>'
                     f'<span class="tabular" style="margin-left:auto;padding-left:16px;font-weight:600">{v}</span></div>'
                     for l, v, c in [("Rules only", counts["deterministic"], "var(--c-ok)"), ("Needs AI", counts["needs_llm"] + counts["partial"], "var(--c-warn)"),
                                     ("Not converted", counts["other"], "var(--c-side-muted)")])
    ws_ring = ui.ring(counts["deterministic"] / total if total else 0, 104, 10, "var(--c-side-accent)", "var(--c-side-2)",
                      f'<span class="display tabular" style="font-size:26px;line-height:1">{pct}%</span><span style="margin-top:4px;font-size:10px;color:var(--c-side-muted)">rules only</span>')
    ui.html(f'<section class="ws"><div class="card" style="overflow:hidden"><div class="between" style="border-bottom:1px solid var(--c-line);padding:14px 20px">'
            f'<div class="row" style="gap:8px"><span class="accent">{icon("layers")}</span><span style="font-size:13.5px;font-weight:600;color:var(--c-fg)">Recent projects</span></div>'
            f'<a class="tcb-link" style="font-size:12px" href="?page=projects">View all</a></div>{table}</div>'
            f'<div class="ink grain" style="position:relative;overflow:hidden;border-radius:14px;padding:24px"><div class="ink-grid" style="position:absolute;inset:0;opacity:.4"></div>'
            f'<div style="position:relative"><div class="eyebrow" style="color:var(--c-side-muted)">Workspace</div><div class="row" style="gap:20px;margin-top:16px;flex-wrap:nowrap">{ws_ring}'
            f'<div style="display:grid;gap:8px;font-size:13px">{legend}</div></div><div style="margin-top:24px;display:grid;grid-template-columns:1fr 1fr;gap:12px;border-top:1px solid var(--c-side-line);padding-top:20px">'
            f'<div><div class="display tabular" style="font-size:24px">{total}</div><div style="font-size:12px;color:var(--c-side-muted)">projects</div></div>'
            f'<div><div class="display tabular" style="font-size:24px">{ui.compact(lines)}</div><div style="font-size:12px;color:var(--c-side-muted)">lines of ABAP</div></div></div></div></div></section>')


# ---------------------------------------------------------------------- projects
@st.dialog("Delete project")
def confirm_delete(p: dict) -> None:
    st.write(f"Delete **{p['name']}**? This removes its files and results.")
    c1, c2 = st.columns(2)
    if c1.button("Cancel", width="stretch"):
        st.rerun()
    if c2.button("Delete", type="primary", width="stretch", icon=":material/delete:"):
        core.delete_project(p["id"])
        ui.notify("ok", "Project deleted")
        st.rerun()


def project_card(p: dict) -> str:
    s = p.get("summary") or {}
    stat = badge(ui.status_label(s["sql_status"]), ui.status_tone(s["sql_status"])) if s.get("sql_status") else badge(esc(p["stage"]))
    cells = "".join(f'<div><div class="tabular" style="font-size:15px;font-weight:600;color:var(--c-fg)">{ui.num(v) if v is not None else "–"}</div>'
                    f'<div class="eyebrow faint" style="font-size:9.5px;margin-top:2px">{k}</div></div>' for k, v in [("lines", s.get("lines")), ("tables", s.get("tables")), ("steps", s.get("relations"))])
    return (f'<a class="card lift pcard" href="?page=p&pid={p["id"]}"><span class="top"></span><div class="between" style="align-items:flex-start">'
            f'<div style="min-width:0"><div class="mono" style="font-size:15px;font-weight:600;color:var(--c-fg);overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{esc(p["name"])}</div>'
            f'<div class="mono faint" style="margin-top:2px;font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{esc(s.get("program") or (p["files"] or [""])[0])}</div></div>'
            f'<div class="row" style="gap:6px;flex-wrap:nowrap">{stat}<span class="pdel" data-nav="?do=delete:{p["id"]}" title="Delete project">{icon("x", 14)}</span></div></div>'
            f'<div class="stats3">{cells}</div>{stage_bar(p["stage"])}<div class="faint" style="margin-top:14px;font-size:12px">{esc(p["stage"])} · {ui.when(p["updated"])}</div></a>')


def project_row(p: dict) -> str:
    s = p.get("summary") or {}
    stat = badge(ui.status_label(s["sql_status"]), ui.status_tone(s["sql_status"])) if s.get("sql_status") else badge(esc(p["stage"]))
    return (f'<a class="prow" href="?page=p&pid={p["id"]}"><span class="faint">{icon("code")}</span><span style="min-width:0;flex:1">'
            f'<span class="mono" style="display:block;font-size:13.5px;font-weight:600;color:var(--c-fg)">{esc(p["name"])}</span>'
            f'<span class="faint" style="display:block;font-size:12px">{esc(s.get("program") or "")} · {ui.num(s["lines"]) + " lines" if s.get("lines") else esc(p["stage"])}</span></span>'
            f'<span style="width:180px">{stage_bar(p["stage"]).replace("margin-top:14px", "margin-top:0")}</span><span style="width:110px;text-align:right">{stat}</span>'
            f'<span class="faint" style="width:150px;text-align:right;font-size:12px">{ui.when(p["updated"])}</span>'
            f'<span class="pdel" data-nav="?do=delete:{p["id"]}" title="Delete project">{icon("x", 14)}</span></a>')


def projects() -> None:
    st.markdown(PAGE_CSS, unsafe_allow_html=True)
    items = core.projects()
    target = ui.take_action("delete")
    if target:
        found = next((p for p in items if p["id"] == target), None)
        if found:
            confirm_delete(found)
    ui.page_header("Workspace", "folder", "Projects", f"{ui.plural(len(items), 'conversion project')}, grouped by workspace.", tools=True)
    with ui.page_tools():
        q = st.text_input("Search", placeholder="Search projects", label_visibility="collapsed", icon=":material/search:", width=350, key="proj_q")
        layout = st.segmented_control("Layout", ["grid", "list"], default="grid", key="proj_layout", label_visibility="collapsed",
                                      format_func=lambda x: {"grid": ":material/grid_view:", "list": ":material/view_list:"}[x]) or "grid"
        if st.button("New", icon=":material/add:", type="primary", key="proj_new"):
            ui.go("new")
    shown = [p for p in items if not q or q.lower() in f"{p['name']} {p['workspace']} {(p.get('summary') or {}).get('program', '')}".lower()]
    if not shown:
        ui.empty("No project matches your search." if q else "No projects yet. Upload or paste the ABAP of a T-code to begin.", "folder")
        if not q and st.button("Start a conversion", icon=":material/add:", type="primary"):
            ui.go("new")
        return
    groups: dict[str, list[dict]] = {}
    for p in shown:
        groups.setdefault(p["workspace"], []).append(p)
    out = ""
    for ws, ps in groups.items():
        out += (f'<div class="row faint" style="gap:8px;margin:26px 0 12px;font-size:12px;font-weight:600;letter-spacing:.08em;text-transform:uppercase">{icon("folder", 14)}{esc(ws)}'
                f'<span style="border-radius:6px;background:var(--c-surface-2);padding:0 7px;letter-spacing:0">{len(ps)}</span></div>')
        if layout == "grid":
            out += '<div class="pgrid">' + "".join(project_card(p) for p in ps) + "</div>"
        else:
            out += '<div class="card" style="overflow:hidden">' + "".join(project_row(p) for p in ps) + "</div>"
    ui.html(out)


# ---------------------------------------------------------------------- new conversion
def new_conversion(initial: str) -> None:
    d = core.defaults()
    samples_ = core.samples()
    ui.page_header("New conversion", "rocket", "Bring the ABAP of a T-code", "Standard, custom (Z/Y) or mixed. Upload files or a zip, paste the code, or start from a bundled sample.")
    left, right = st.columns([1.4, 1], gap="large")
    with left:
        source = st.segmented_control("Source", ["upload", "paste", "sample"], default=initial if initial in ("upload", "paste", "sample") else "upload",
                                      key="nc_source", label_visibility="collapsed", width="stretch",
                                      format_func=lambda x: {"upload": ":material/drive_folder_upload: Upload files", "paste": ":material/content_paste: Paste code",
                                                             "sample": ":material/science: Sample"}[x]) or "upload"
        files, text, sample = [], "", None
        with ui.panel("pg2"):
            if source == "upload":
                ui.heading("Source files", "Includes are linked by name; renamed exports are matched automatically", "code")
                files = st.file_uploader("Drop .abap / .txt files or a .zip", type=["abap", "txt", "zip", "src", "inc", "prog"], accept_multiple_files=True,
                                         key="nc_files", help="Up to 20 MB per file. FUNCTION … ENDFUNCTION files are used as function module source.") or []
                if files:
                    rows = "".join(f'<div class="between" style="border-radius:10px;background:var(--c-surface-2);padding:7px 12px;margin-top:4px">'
                                   f'<span class="row mono" style="gap:8px;font-size:12px;color:var(--c-fg)"><span class="accent">{icon("code", 14)}</span>{esc(f.name)}</span>'
                                   f'<span class="faint" style="font-size:12px">{f.size / 1024:.1f} KB</span></div>' for f in files)
                    ui.html(rows)
            elif source == "paste":
                t = st.session_state.get("paste_text", "")
                line_count = len(t.splitlines()) or 1
                ui.heading("Paste ABAP", f"{ui.num(line_count)} lines" if t else "Any size: tens of thousands of lines are fine", "clipboard")
                text = st.text_area("ABAP source", key="paste_text", height=460, placeholder=PASTE_HINT, label_visibility="collapsed")
                if text and st.button("Clear", icon=":material/delete:", type="tertiary"):
                    st.session_state.pop("paste_text", None)
                    st.rerun()
            else:
                ui.heading("Bundled samples", "SFLIGHT and SD/MM demo programs with reference SQL for validation", "flask")
                names = [s["name"] for s in samples_]
                info = {s["name"]: s for s in samples_}
                sample = st.radio("Sample", names, key="nc_sample", label_visibility="collapsed",
                                  format_func=lambda n: f"{n}  ·  {len(info[n]['files'])} file(s) · {ui.num(info[n]['lines'])} lines")
    with right:
        with ui.panel("pg3"):
            ui.heading("Project", "", "layers")
            name = st.text_input("Name", placeholder=sample or "e.g. ZMM_STOCK_REPORT", key="nc_name")
            c1, c2 = st.columns(2)
            workspace = c1.text_input("Workspace / client", value="default", key="nc_ws")
            system = c2.selectbox("SAP system", ["ecc", "s4"], index=1 if d["source_system"] == "s4" else 0, key="nc_sys", format_func=lambda x: {"ecc": "ECC", "s4": "S/4HANA"}[x])
        raw_db, raw_sc, pattern = d["source_database"], d["source_schema"], d["table_pattern"] or "{table}"
        if source != "sample":
            with ui.panel("pg4"):
                ui.heading("Snowflake layers", "Defaults come from Settings", "database")
                raw_db, raw_sc = ui.location_picker("Source (raw SAP layer)", d["source_database"], d["source_schema"], "nc_raw",
                                                    "Where the replicated SAP tables live. Columns are read from here; the SQL reads from here.")
                pattern = st.text_input("Physical table name pattern", value=d["table_pattern"] or "{table}", key="nc_pattern",
                                        help="{table} is the SAP name, e.g. SAP_{table} or {table}_RAW") or "{table}"
        with ui.panel("pg5"):
            ui.heading("Output", "", "monitor")
            mode = st.segmented_control("Output", ["select", "view"], default=d["mode"], key="nc_mode", label_visibility="collapsed", width="stretch",
                                        format_func=lambda x: {"select": "CTE query", "view": "CREATE VIEW"}[x]) or "select"
            view_db, view_sc, view_name = d["view_database"], d["view_schema"], ""
            if mode == "view":
                if source != "sample":
                    view_db, view_sc = ui.location_picker("Target (gold layer)", d["view_database"], d["view_schema"], "nc_gold",
                                                          "Where the view is created. Empty = same as the source.", "e.g. SAP_GOLD", "e.g. SALES")
                view_name = st.text_input("View name", placeholder="e.g. V_ORDER_STATUS", key="nc_view", help="Default: <program>_V").upper()
            run_mode = st.radio("Pipeline", ["guided", "streamlined"], key="nc_run", horizontal=True,
                                format_func=lambda x: {"guided": "Guided", "streamlined": "Streamlined"}[x],
                                captions=["Stop after analysis to review and add context", "Analyze, convert and validate in one go"])
        ready = bool(files) if source == "upload" else bool((text or "").strip()) if source == "paste" else bool(sample)
        label = "Create and run all" if run_mode == "streamlined" else "Create and analyze"
        if st.button(label, type="primary", icon=":material/rocket_launch:", width="stretch", disabled=not ready, key="nc_create"):
            settings_ = {"source_system": system, "table_pattern": pattern}
            for k, v in (("target_database", raw_db), ("target_schema", raw_sc), ("view_database", view_db), ("view_schema", view_sc)):
                if v:
                    settings_[k] = v
            with st.spinner("Creating the project…"):
                try:
                    if source == "upload":
                        p = core.create_from_uploads(name or re.sub(r"\.\w+$", "", files[0].name), workspace, settings_, [(f.name, f.getvalue()) for f in files])
                    elif source == "paste":
                        m = re.search(r"^\s*(?:REPORT|PROGRAM|FUNCTION|CLASS)\s+([A-Za-z0-9_/]+)", text, re.I | re.M)
                        guess = m.group(1) if m else None
                        p = core.create_from_paste(name or guess or "pasted_program", text, guess, workspace, settings_)
                    else:
                        p = core.create_from_sample(sample, settings_={})
                    core.update_project(p["id"], convert={"mode": mode, "view_name": (view_name or None) if mode == "view" else None,
                                                          "use_llm": d["use_llm"], "model": d["model"]})
                except core.ServiceError as exc:
                    st.error(f"Could not create the project: {exc}")
                    return
            ui.notify("ok", "Project created", "Running the full pipeline…" if run_mode == "streamlined" else "Analyzing…")
            st.session_state.pop("paste_text", None)
            ui.go("p", pid=p["id"], run="all" if run_mode == "streamlined" else None)
        ui.html(f'<div class="faint" style="text-align:center;font-size:12px">AI for leftover steps: {badge(esc(d["model"] if d["use_llm"] else "off"), "ai")} · change in Settings</div>')


# ---------------------------------------------------------------------- samples
def samples() -> None:
    st.markdown(PAGE_CSS, unsafe_allow_html=True)
    ui.page_header("Samples", "flask", "Try it on bundled programs",
                   "Each sample ships with a hand-written reference SQL and demo data in Snowflake, so validation compares results row by row.")
    items = core.samples()
    demo = demo_status()
    if not demo.get("ready"):
        with ui.panel("pg6"):
            a, b = st.columns([4, 1.3], vertical_alignment="center")
            a.markdown(ui.callout("info", "<b>Demo data is not in this Snowflake account yet.</b> Samples still analyze and convert; to compile them against real tables "
                                  "and compare results row by row, load the synthetic SFLIGHT / SD / MM data into <span class='mono'>TCODE_BREAKER.SAP_DEMO</span> once."),
                       unsafe_allow_html=True)
            if b.button("Set up demo data", icon=":material/database:", type="primary", width="stretch", disabled=not ui.sf_status().get("connected")):
                with st.spinner("Creating TCODE_BREAKER.SAP_DEMO and loading 11 tables…"):
                    counts = ui.guard(core.setup_demo_data, title="Demo data setup failed")
                if counts:
                    demo_status.clear()
                    ui.settings_changed()
                    ui.notify("ok", "Demo data loaded", f"{sum(counts.values()):,} rows in {len(counts)} tables")
                st.rerun()
    for i in range(0, len(items), 3):
        cols = st.columns(3)
        for col, (idx, s) in zip(cols, list(enumerate(items))[i:i + 3]):
            title, tags = ABOUT.get(s["name"], (s["name"], []))
            with col, ui.panel(f"smp_{s['name']}"):
                tagline = "".join(f'<span class="chip">{esc(t)}</span>' for t in tags)
                ui.html(f'<div class="ink grain sample-head"><div class="ink-grid" style="position:absolute;inset:0;opacity:.4"></div>'
                        f'<div style="position:relative"><div class="between mono" style="font-size:11px;color:var(--c-side-muted)"><span>{idx + 1:02d} / {len(items):02d}</span>'
                        f'<span>{ui.plural(len(s["files"]), "file")} · {ui.num(s["lines"])} lines</span></div><div class="mono" style="margin-top:22px;font-size:13px;color:var(--c-side-accent)">{esc(s["name"])}</div>'
                        f'<div class="display" style="margin-top:4px;font-size:22px;line-height:1.2;color:var(--c-side-fg)">{esc(title)}</div></div></div>'
                        f'<div class="row" style="gap:6px;min-height:24px;padding:14px 20px 0">{tagline}</div>')
                with st.container(horizontal=True, key=f"smp_btns_{s['name']}"):
                    if st.button("Open", key=f"s_open_{s['name']}", icon=":material/arrow_forward:", width="stretch"):
                        p = ui.guard(core.create_from_sample, s["name"], title="Could not open sample")
                        if p:
                            ui.go("p", pid=p["id"])
                    if st.button("Run all", key=f"s_run_{s['name']}", icon=":material/play_arrow:", type="primary", width="stretch"):
                        p = ui.guard(core.create_from_sample, s["name"], title="Could not open sample")
                        if p:
                            ui.go("p", pid=p["id"], run="all")


@st.cache_data(ttl=300, show_spinner=False)
def demo_status() -> dict:
    return core.demo_data_status()


# ---------------------------------------------------------------------- settings
SECTIONS = [("connection", "Snowflake connection", "Account, user, role, warehouse", ":material/power:"),
            ("models", "Models & API keys", "Default model, providers, keys", ":material/memory:"),
            ("layers", "Data layers", "Raw source and gold target", ":material/layers:"),
            ("conversion", "Conversion defaults", "Output, AI use, validation", ":material/tune:"),
            ("appearance", "Appearance", "Themes", ":material/palette:")]


def save(patch: dict, message: str = "Settings saved") -> None:
    try:
        core.save_settings(patch)
        ui.settings_changed()
        ui.notify("ok", message)
    except core.ServiceError as exc:
        ui.notify("error", "Save failed", str(exc))
    st.rerun()


SETTINGS_CSS = """<style>
[class*="st-key-set_"] button { position: relative; width: 100%; justify-content: flex-start; padding: 10px 12px 26px; min-height: 58px; border: 1px solid transparent;
  background: transparent; box-shadow: none; border-radius: 10px; }
[class*="st-key-set_"] button:hover { background: var(--c-surface-2); }
[class*="st-key-set_"] button > div { width: 100%; justify-content: flex-start; gap: 12px; align-items: flex-start; }
[class*="st-key-set_"] [data-testid="stIconMaterial"] { display: flex !important; width: 32px !important; height: 32px !important; min-width: 32px; align-items: center; justify-content: center;
  border-radius: 7px; border: 1px solid var(--c-line); background: var(--c-surface); color: var(--c-fg-faint); font-size: 17px !important; margin: 0; }
[class*="st-key-set_"] button span:has(> [data-testid="stIconMaterial"]) { display: flex; width: 32px !important; height: 32px; flex-shrink: 0; margin: 1px 0 0 0; }
[class*="st-key-set_"] p { font-size: 14px !important; font-weight: 500; color: var(--c-fg); }
[class*="st-key-set_"] button::after { position: absolute; left: 56px; top: 33px; font-size: 11px; font-weight: 400; color: var(--c-fg-faint); }
.st-key-settings_body { gap: 1.4rem !important; }
</style>"""


def settings(section: str) -> None:
    section = section if section in {x[0] for x in SECTIONS} else "connection"
    ui.page_header("Settings", "sliders", "Configure your workspace",
                   f"Stored locally with the app ({esc(core.DATA_DIR.name)}/app_settings.json, owner-only). Secrets are never shown again after saving.")
    s = core.settings()
    rules = [SETTINGS_CSS, "<style>"]
    rules += [f'.st-key-set_{sid} button::after{{content:"{sub}"}}' for sid, _, sub, _ in SECTIONS]
    rules.append(f".st-key-set_{section} button{{background:var(--c-surface)!important;border-color:var(--c-line-strong)!important;"
                 f"box-shadow:0 1px 0 color-mix(in oklab,var(--c-line-strong) 50%,transparent),0 10px 28px -18px var(--c-shadow)!important}}"
                 f".st-key-set_{section} button::before{{content:'';position:absolute;left:0;top:10px;bottom:10px;width:3px;border-radius:0 3px 3px 0;background:var(--c-accent)}}"
                 f".st-key-set_{section} [data-testid='stIconMaterial']{{background:var(--c-accent);border-color:color-mix(in oklab,var(--c-accent) 30%,transparent);color:var(--c-on-accent)}}</style>")
    st.markdown("".join(rules), unsafe_allow_html=True)
    with st.container(horizontal=True, gap="large", key="settings_row"):
        with st.container(width=260, key="settings_nav", gap=None):
            for sid, label, sub, ico in SECTIONS:
                if st.button(label, key=f"set_{sid}", icon=ico, type="tertiary", width="stretch"):
                    ui.go("settings", section=sid)
        with st.container(key="settings_body"):
            {"connection": settings_connection, "models": settings_models, "layers": settings_layers,
             "conversion": settings_conversion, "appearance": settings_appearance}[section](s)


def conn_grid(r: dict) -> str:
    return "".join(f'<div><div class="eyebrow faint" style="font-size:10px">{k}</div><div class="mono fg" style="font-size:13px;margin-top:2px;overflow:hidden;text-overflow:ellipsis">{esc(v)}</div></div>'
                   for k, v in [("Account", r.get("account")), ("User", r.get("user")), ("Role", r.get("role")), ("Warehouse", r.get("warehouse") or "none"),
                                ("Region", r.get("region")), ("Version", r.get("version"))])


def conn_result(r: dict | None) -> None:
    if not r:
        return
    if r.get("ok") or r.get("connected"):
        ui.html(ui.callout("ok", f'<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px 24px">{conn_grid(r)}</div>'))
    else:
        ui.html(ui.callout("bad", esc(r.get("error"))))


@st.dialog("Remove connection")
def confirm_remove(label: str) -> None:
    st.markdown(f"Remove **{label}** from this app? Cortex models, live schema reads and validation stop working until you add a connection again. "
                "Saved secrets for it are deleted from the app settings.")
    a, b = st.columns(2)
    if a.button("Cancel", width="stretch"):
        st.rerun()
    if b.button("Remove", type="primary", icon=":material/link_off:", width="stretch"):
        core.remove_connection()
        st.session_state.pop("conn_test", None)
        st.session_state.pop("conn_form", None)
        ui.settings_changed()
        ui.notify("ok", "Connection removed")
        st.rerun()


def connection_form(s: dict, mode: str) -> None:
    c = dict(s["snowflake"]["custom"]) if mode == "edit" else {"authenticator": "snowflake"}
    title = "Edit connection" if mode == "edit" else "New connection"
    with ui.panel("conn_form"):
        ui.heading(title, "Saved in this app's settings, owner-only. Secrets are never shown again after saving.", "plug")
        a, b = st.columns(2)
        c["account"] = a.text_input("Account identifier", value=c.get("account", ""), placeholder="orgname-accountname", key=f"cf_acc_{mode}",
                                    help="orgname-accountname, or locator.region (e.g. xy12345.eu-central-1)")
        c["user"] = b.text_input("User", value=c.get("user", ""), key=f"cf_user_{mode}")
        keys = list(core.AUTH_LABEL)
        auth = c.get("authenticator") or "snowflake"
        c["authenticator"] = a.selectbox("Authentication", keys, index=keys.index(auth) if auth in keys else 0, format_func=core.AUTH_LABEL.get, key=f"cf_auth_{mode}")
        keep = "saved; leave as is to keep it"
        if c["authenticator"] == "snowflake":
            c["password"] = b.text_input("Password", value=c.get("password", ""), type="password", key=f"cf_pw_{mode}", help=keep if c.get("has_password") else None)
        elif c["authenticator"] in ("programmatic_access_token", "oauth"):
            c["token"] = b.text_input("Token", value=c.get("token", ""), type="password", key=f"cf_tok_{mode}", help=keep if c.get("has_token") else None)
        elif c["authenticator"] == "snowflake_jwt":
            c["private_key_file"] = b.text_input("Private key file (.p8)", value=c.get("private_key_file", ""), placeholder="/path/to/rsa_key.p8", key=f"cf_pk_{mode}")
            c["private_key_passphrase"] = a.text_input("Key passphrase (optional)", value=c.get("private_key_passphrase", ""), type="password", key=f"cf_pp_{mode}")
        else:
            b.caption("A browser window opens on the machine running the app (local use only).")
        c["role"] = a.text_input("Role", value=c.get("role", ""), placeholder="default role", key=f"cf_role_{mode}")
        c["warehouse"] = b.text_input("Warehouse", value=c.get("warehouse", ""), placeholder="default warehouse", key=f"cf_wh_{mode}")
        form = {"mode": "custom", "connection_name": "", "custom": c}
        ready = bool(c["account"].strip() and c["user"].strip())
        with st.container(horizontal=True):
            if st.button("Test", icon=":material/power:", disabled=not ready, key="cf_test"):
                with st.spinner("Connecting…"):
                    st.session_state.conn_test = core.test_snowflake(form)
            if st.button("Save and connect", icon=":material/save:", type="primary", disabled=not ready, key="cf_save"):
                st.session_state.pop("conn_test", None)
                st.session_state.pop("conn_form", None)
                save({"snowflake": form}, "Connection saved")
            if st.session_state.get("conn_form") and core.connection_profile()["kind"] != "none" and st.button("Cancel", type="tertiary", key="cf_cancel"):
                st.session_state.pop("conn_form", None)
                st.session_state.pop("conn_test", None)
                st.rerun()
        conn_result(st.session_state.get("conn_test"))


def session_form(s: dict) -> None:
    c = dict(s["snowflake"]["custom"])
    with ui.panel("conn_session"):
        ui.heading("Snowflake session", "The app runs inside Snowflake and signs in with the token Snowflake mounts into the container", "shield")
        a, b = st.columns(2)
        c["warehouse"] = a.text_input("Warehouse", value=c.get("warehouse", ""), placeholder="service default", key="cs_wh")
        c["role"] = b.text_input("Role", value=c.get("role", ""), placeholder="service role", key="cs_role")
        with st.container(horizontal=True):
            if st.button("Save", icon=":material/save:", type="primary", key="cs_save"):
                st.session_state.pop("conn_form", None)
                save({"snowflake": {"mode": "session", "connection_name": "", "custom": c}}, "Session settings saved")
            if st.button("Cancel", type="tertiary", key="cs_cancel"):
                st.session_state.pop("conn_form", None)
                st.rerun()


def settings_connection(s: dict) -> None:
    prof = core.connection_profile()
    form = st.session_state.get("conn_form")
    inside = core.in_snowflake()
    if prof["kind"] != "none":
        sf = ui.sf_status()
        ok = bool(sf.get("connected"))
        tone = "ok" if ok else "bad"
        how = {"custom": "Credentials saved in this app", "profile": "Local Snowflake CLI profile on this machine",
               "session": "Signed in by Snowflake (app runs inside Snowflake)"}[prof["kind"]]
        with ui.panel("conn_active"):
            ui.heading("Active connection", "Used for Cortex models, live schema metadata and validation", "database",
                       badge("connected" if ok else "not reachable", tone))
            body = (f'<div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px 24px;margin-top:4px">{conn_grid(sf)}</div>' if ok
                    else ui.callout("bad", f"<b class='bad'>Could not connect.</b> {esc(sf.get('error') or '')}"))
            ui.html(f'<div class="row" style="gap:16px;flex-wrap:nowrap;align-items:flex-start"><span class="icon-tile" style="width:44px;height:44px;border-radius:12px;color:var(--c-{tone})">'
                    f'{icon("plug", 20)}</span><div style="min-width:0;flex:1"><div class="mono fg" style="font-size:15px;font-weight:600">{esc(prof["label"])}</div>'
                    f'<div class="muted" style="font-size:12.5px;margin-top:2px">{how} · {esc(prof.get("auth") or "")}</div></div></div>'
                    f'<div style="margin-top:14px">{body}</div>')
            with st.container(horizontal=True):
                if st.button("Test again", icon=":material/refresh:", key="ca_test"):
                    ui.settings_changed()
                    st.rerun()
                if prof["kind"] == "custom" and st.button("Edit", icon=":material/edit:", key="ca_edit"):
                    st.session_state.conn_form = "edit"
                    st.rerun()
                if prof["kind"] == "session" and st.button("Warehouse and role", icon=":material/edit:", key="ca_sess"):
                    st.session_state.conn_form = "session"
                    st.rerun()
                if st.button("New connection", icon=":material/add_link:", key="ca_new"):
                    st.session_state.conn_form = "new"
                    st.session_state.pop("conn_test", None)
                    st.rerun()
                if prof["kind"] != "session" and st.button("Remove connection", icon=":material/link_off:", type="tertiary", key="ca_remove"):
                    confirm_remove(prof["label"])
    else:
        with ui.panel("conn_none"):
            ui.heading("No connection", "Analysis works offline; Cortex models, live schema reads and validation need Snowflake", "database", badge("not connected", "bad"))
            ui.html(ui.callout("info", "Add a connection below. The app keeps exactly one: the account, user and sign-in you enter here."
                               + (" It is running inside Snowflake, so it can also use the Snowflake session instead." if inside else "")))
            if inside and st.button("Use the Snowflake session", icon=":material/shield:", type="primary", key="cn_session"):
                save({"snowflake": {"mode": "session", "connection_name": "", "custom": {}}}, "Using the Snowflake session")
        form = form or "new"
    if form == "session":
        session_form(s)
    elif form in ("new", "edit"):
        connection_form(s, form)


def model_label(m: dict, private_word: str = "private") -> str:
    return f"{m['id']}  ·  {private_word if m['private'] else 'external'}" + ("" if m["available"] else "  ·  no key")


def settings_models(s: dict) -> None:
    d = s["defaults"]
    ms = ui.models()
    ids = [m["id"] for m in ms]
    by_id = {m["id"]: m for m in ms}
    with ui.panel("pg8"):
        ui.heading("Default model", "Used only for steps the rules cannot translate", "cpu")
        a, b = st.columns([4, 1], vertical_alignment="bottom")
        model = a.selectbox("Model", ids, index=ids.index(d["model"]) if d["model"] in ids else 0, format_func=lambda i: model_label(by_id[i]), label_visibility="collapsed")
        if b.button("Test model", width="stretch", key="tm_default"):
            with st.spinner("Calling the model…"):
                st.session_state.model_test = (model, core.test_model(model))
        mt = st.session_state.get("model_test")
        if mt and mt[0] == model:
            (st.success if mt[1]["ok"] else st.error)(f'Replied "{mt[1]["reply"]}" in {mt[1]["seconds"]}s' if mt[1]["ok"] else mt[1]["error"])
        use_llm = st.toggle("Use AI for unresolved steps", value=d["use_llm"], help="Off = rules only; unresolved steps stay as clearly marked placeholders.")
        if st.button("Save", icon=":material/save:", type="primary", key="save_model"):
            save({"defaults": {"model": model, "use_llm": use_llm}})
    with ui.panel("pg9"):
        ui.heading("API keys", "For external providers. Cortex models use the Snowflake connection.", "key")
        envs = sorted({m["key_env"] for m in ms if m["key_env"]})
        entered = {}
        cols = st.columns(2)
        for i, k in enumerate(envs):
            with cols[i % 2]:
                saved = s["api_keys"].get(k)
                a, b = st.columns([5, 1], vertical_alignment="bottom")
                entered[k] = a.text_input(k, type="password", placeholder="•••• saved" if saved else "paste key", help=f"saved ({saved})" if saved else "not set", key=f"key_{k}")
                if saved and b.button("", icon=":material/delete:", key=f"rmkey_{k}", help="Remove key"):
                    save({"api_keys": {k: ""}}, f"{k} removed")
        if st.button("Save keys", icon=":material/save:", type="primary", key="save_keys"):
            save({"api_keys": {k: v for k, v in entered.items() if v}}, "Keys saved")
    with ui.panel("pg10"):
        ui.heading("Custom OpenAI-compatible endpoint", "vLLM, LM Studio, Azure proxy, OpenRouter, an internal gateway…", "network")
        for p in s["providers"]:
            a, b = st.columns([8, 1], vertical_alignment="center")
            a.markdown(f"<span class='mono fg' style='font-weight:600'>{esc(p['name'])}</span> <span class='faint'>{esc(p['base_url'])}</span> "
                       f"<span class='muted'>{esc(', '.join(p['models']))}</span> {badge('private', 'ok') if p.get('private') else ''}", unsafe_allow_html=True)
            if b.button("", icon=":material/delete:", key=f"rmprov_{p['name']}", help="Remove endpoint"):
                save({"providers": [x for x in s["providers"] if x["name"] != p["name"]]}, "Endpoint removed")
        a, b = st.columns(2)
        pname = re.sub(r"[^a-z0-9_-]", "", a.text_input("Name", placeholder="e.g. mygateway", key="np_name").lower())
        url = b.text_input("Base URL", placeholder="https://host/v1", key="np_url")
        key = a.text_input("API key (optional)", type="password", key="np_key")
        mlist = b.text_input("Models (comma separated)", placeholder="qwen2.5-coder-32b, llama-3.3-70b", key="np_models")
        private = st.toggle("Runs inside our network", key="np_private", help="Private endpoints may receive code from projects marked confidential.")
        if st.button("Add endpoint", icon=":material/add:", disabled=not (pname and url and mlist), key="np_add"):
            save({"providers": [*s["providers"], {"name": pname, "base_url": url, "api_key": key, "models": [x.strip() for x in mlist.split(",") if x.strip()],
                                                   "private": private}]}, "Endpoint added")
    with ui.panel("pg11"):
        ui.heading("Available models", "", "cpu")
        providers: dict[str, list[dict]] = {}
        for m in ms:
            providers.setdefault(m["provider"], []).append(m)
        cols = st.columns(2)
        for i, (prov, items) in enumerate(providers.items()):
            with cols[i % 2].container(border=True, key=f"pnl_prov_{i}"):
                st.markdown(f"<div class='between'><span style='font-weight:600;text-transform:capitalize;color:var(--c-fg)'>{esc(prov)}</span>"
                            f"{badge('private', 'ok') if items[0]['private'] else badge('external')}</div>", unsafe_allow_html=True)
                for m in items:
                    a, b = st.columns([5, 1.2], vertical_alignment="center")
                    a.markdown(f"<span class='mono muted' style='font-size:12px'>{esc(m['model'])}</span> {'' if m['available'] else badge('no key', 'warn')}", unsafe_allow_html=True)
                    if b.button("test", key=f"tm_{m['id']}", type="tertiary"):
                        with st.spinner("Calling…"):
                            st.session_state.model_test = (m["id"], core.test_model(m["id"]))
                mt = st.session_state.get("model_test")
                if mt and any(m["id"] == mt[0] for m in items):
                    res = mt[1]
                    text = f"OK in {res['seconds']}s" if res["ok"] else esc(res["error"])
                    st.markdown(f"<div class='{'ok' if res['ok'] else 'bad'}' style='font-size:11.5px'>{esc(mt[0])}: {text}</div>", unsafe_allow_html=True)


def settings_layers(s: dict) -> None:
    d = s["defaults"]
    with ui.panel("pg12"):
        ui.heading("Data layers", "Defaults for new projects; each project can override them", "layers")
        src_db, src_sc = ui.location_picker("Source: raw SAP layer", d["source_database"], d["source_schema"], "set_raw",
                                            "The schema where SAP tables are replicated (VBAK, MARA, Z tables …). The SQL reads from here and table/column metadata is read live from it.")
        gold_db, gold_sc = ui.location_picker("Target: gold layer for views", d["view_database"], d["view_schema"], "set_gold",
                                              "Where CREATE OR REPLACE VIEW puts the view. Empty = same as the source.", "e.g. SAP_GOLD", "e.g. REPORTING")
        a, b, c, e = st.columns(4)
        pattern = a.text_input("Physical table name pattern", value=d["table_pattern"], help="{table} = SAP name. Examples: SAP_{table}, {table}_RAW") or "{table}"
        system = b.selectbox("SAP system", ["ecc", "s4"], index=1 if d["source_system"] == "s4" else 0, format_func=lambda x: {"ecc": "ECC", "s4": "S/4HANA"}[x])
        client = c.text_input("Client (MANDT) filter", value=d["client"], help="Empty = no client filter")
        lang = e.text_input("Logon language (SY-LANGU)", value=d["language"], max_chars=2).upper()
        use_catalog = st.toggle("Read table and column metadata from the source schema", value=d["use_catalog"], help="Recommended. No knowledge pack is needed for custom tables.")
        infer = st.toggle("Infer fields from how the code uses them", value=d["infer_fields"],
                          help="Fallback when a table is not in Snowflake or the dictionary. Inferred fields are marked as such.")
        if st.button("Save", icon=":material/save:", type="primary", key="save_layers"):
            save({"defaults": {"source_database": src_db, "source_schema": src_sc, "view_database": gold_db, "view_schema": gold_sc, "table_pattern": pattern,
                               "source_system": system, "client": client, "language": lang, "use_catalog": use_catalog, "infer_fields": infer}})


def settings_conversion(s: dict) -> None:
    d = s["defaults"]
    with ui.panel("pg13"):
        ui.heading("Conversion defaults", "", "sliders")
        mode = st.segmented_control("Default output", ["select", "view"], default=d["mode"], key="set_mode",
                                    format_func=lambda x: {"select": "CTE query", "view": "CREATE OR REPLACE VIEW"}[x]) or d["mode"]
        conf = st.toggle("Treat code as confidential", value=d["confidential"], help="Only Snowflake Cortex and private/local models may see source code.")
        v_db, v_sc = ui.location_picker("Validation stub schema", d["validation_database"], d["validation_schema"], "set_val",
                                        "Empty stub tables are created here to compile the SQL with EXPLAIN (no SAP data needed).")
        if st.button("Save", icon=":material/save:", type="primary", key="save_conv"):
            save({"defaults": {"mode": mode, "confidential": conf, "validation_database": v_db, "validation_schema": v_sc}})


def settings_appearance(s: dict) -> None:
    current = theme.get(core.ui_prefs().get("theme")).id
    with ui.panel("pg14"):
        ui.heading("Theme", "Applies instantly; remembered for this app", "palette")
        for i in range(0, len(theme.THEMES), 3):
            cols = st.columns(3)
            for col, t in zip(cols, theme.THEMES[i:i + 3]):
                sw = t.swatch
                faint = "#ffffff40" if t.dark else "#00000030"
                bars = "".join(f'<div style="height:6px;border-radius:99px;margin-top:6px;background:{sw[2] if j == 1 else "#ffffff26"};width:{80 - j * 10}%"></div>' for j in range(4))
                with col:
                    ui.html(f'<div class="card" style="overflow:hidden;{"box-shadow:0 0 0 3px color-mix(in oklab,var(--c-accent) 35%,transparent);border-color:var(--c-accent)" if t.id == current else ""}">'
                            f'<div class="theme-prev" style="background:{sw[0]};display:flex;height:120px"><div style="width:30%;padding:10px;background:{sw[3]}">'
                            f'<div style="width:12px;height:12px;border-radius:3px;background:{sw[2]};margin-bottom:4px"></div>{bars}</div><div style="flex:1;padding:12px">'
                            f'<div style="height:8px;width:64px;border-radius:99px;background:{faint}"></div><div style="margin-top:10px;border-radius:6px;padding:8px;background:{sw[1]};'
                            f'border:1px solid {"#ffffff14" if t.dark else "#0000001a"}"><div style="height:6px;width:80px;border-radius:99px;background:{"#ffffff26" if t.dark else "#0000001a"}"></div>'
                            f'<div style="margin-top:6px;height:6px;width:56px;border-radius:99px;background:{"#ffffff1a" if t.dark else "#00000012"}"></div>'
                            f'<div style="margin-top:10px;height:20px;width:64px;border-radius:4px;background:{sw[2]}"></div></div></div></div>'
                            f'<div class="row" style="gap:12px;padding:12px;border-top:1px solid var(--c-line)">{ui.swatch(sw, 24)}<span style="min-width:0;flex:1">'
                            f'<span style="display:block;font-size:14px;font-weight:600;color:var(--c-fg)">{t.name}</span><span class="faint" style="display:block;font-size:11px">{t.tagline}</span></span>'
                            f'{"<span class=accent>" + icon("okcircle") + "</span>" if t.id == current else ""}</div></div>')
                    if st.button("In use" if t.id == current else "Use theme", key=f"theme_{t.id}", width="stretch", disabled=t.id == current,
                                 type="primary" if t.id == current else "secondary"):
                        core.save_ui_prefs(theme=t.id)
                        theme.sync_native(t)
                        st.rerun()
