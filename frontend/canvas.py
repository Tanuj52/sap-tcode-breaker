"""Interactive data-flow canvas: a Streamlit custom component (v2) with pan, zoom, fit, column expansion, node details and PNG/SVG export."""

from __future__ import annotations

import streamlit as st

HTML = """
<div class="fl">
  <div class="bar">
    <span class="cnt"></span><span class="sep"></span>
    <label class="tg"><input type="checkbox" data-k="biz" checked><span class="sw"></span>Business names</label>
    <label class="tg"><input type="checkbox" data-k="fm"><span class="sw"></span>Hide function modules</label>
    <span class="sp"></span>
    <button class="btn" data-a="png"><i data-i="image"></i>PNG</button>
    <button class="btn" data-a="svg"><i data-i="image"></i>SVG</button>
  </div>
  <div class="main">
    <div class="pane">
      <div class="vp"><svg class="edges"></svg><div class="nodes"></div></div>
      <div class="tl"><button class="btn" data-a="expand"><i data-i="expand"></i><span>Expand all columns</span></button><span class="shown"></span></div>
      <div class="legend"></div>
      <div class="ctl"><button data-a="in" title="Zoom in"><i data-i="plus"></i></button><button data-a="out" title="Zoom out"><i data-i="minus"></i></button>
        <button data-a="fit" title="Fit view"><i data-i="fit"></i></button></div>
      <div class="hint">Scroll to zoom · drag to pan · click a node for details</div>
    </div>
    <aside class="detail"><button class="close" title="Close"><i data-i="x"></i></button><div class="body"></div></aside>
  </div>
</div>
"""

CSS = """
:host { display: block; }
* { box-sizing: border-box; }
.fl { display: flex; flex-direction: column; height: max(560px, calc(100vh - 57px)); font-family: Inter, ui-sans-serif, system-ui, sans-serif; color: var(--c-fg); }
.bar { display: flex; align-items: center; gap: 18px; flex-wrap: wrap; padding: 8px 20px; background: var(--c-surface); border-bottom: 1px solid var(--c-line); font-size: 12.5px; }
.cnt { color: var(--c-fg-muted); } .cnt b { color: var(--c-fg); font-variant-numeric: tabular-nums; }
.sep { width: 1px; height: 16px; background: var(--c-line); }
.sp { flex: 1; }
.tg { display: inline-flex; align-items: center; gap: 10px; cursor: pointer; font-size: 12px; color: var(--c-fg); user-select: none; }
.tg input { display: none; }
.tg .sw { position: relative; width: 36px; height: 20px; border-radius: 99px; background: var(--c-line-strong); transition: background .15s; }
.tg .sw::after { content: ""; position: absolute; left: 2px; top: 2px; width: 16px; height: 16px; border-radius: 99px; background: #fff; box-shadow: 0 1px 2px rgba(0,0,0,.25); transition: left .15s; }
.tg input:checked + .sw { background: var(--c-accent); }
.tg input:checked + .sw::after { left: 18px; }
.btn { display: inline-flex; align-items: center; gap: 6px; border: 1px solid var(--c-line-strong); background: var(--c-surface); color: var(--c-fg); border-radius: 8px;
  padding: 6px 10px; font: 500 12px Inter, sans-serif; cursor: pointer; box-shadow: 0 1px 0 var(--c-line); white-space: nowrap; }
.btn:hover { border-color: var(--c-fg-faint); background: var(--c-surface-2); }
i[data-i] { display: inline-flex; width: 14px; height: 14px; }
i[data-i] svg { width: 100%; height: 100%; }
.main { position: relative; flex: 1; min-height: 0; display: flex; }
.pane { position: relative; flex: 1; min-width: 0; overflow: hidden; background-color: var(--c-sunken); cursor: grab; touch-action: none;
  background-image: radial-gradient(var(--c-grid) 1.4px, transparent 1.4px); background-size: 22px 22px; }
.pane.drag { cursor: grabbing; }
.vp { position: absolute; left: 0; top: 0; transform-origin: 0 0; }
.edges { position: absolute; left: 0; top: 0; overflow: visible; pointer-events: none; }
.edges path { fill: none; stroke-width: 1.7; transition: opacity .2s, stroke-width .2s; }
.edges path.hot { stroke-width: 2.6; }
.edges.dim path:not(.hot) { opacity: .22; }
.edges path.anim { stroke-dasharray: 6 6; animation: dash 1.2s linear infinite; }
@keyframes dash { to { stroke-dashoffset: -24; } }
.nodes { position: absolute; left: 0; top: 0; }
.elab { position: absolute; transform: translate(-50%, -50%); background: var(--c-surface); border: 1px solid var(--c-line); border-radius: 6px; padding: 1px 6px;
  font-size: 10px; color: var(--c-fg-muted); white-space: nowrap; max-width: 260px; overflow: hidden; text-overflow: ellipsis; pointer-events: none; transition: opacity .2s; }
.dimmed .elab:not(.hot) { opacity: .25; }
.node { position: absolute; width: 260px; border-radius: 12px; border: 1px solid; background: var(--c-surface); overflow: hidden; cursor: pointer;
  box-shadow: 0 1px 0 var(--c-line), 0 12px 24px -16px var(--c-shadow); transition: box-shadow .2s, opacity .2s; }
.node:hover { box-shadow: 0 1px 0 var(--c-line), 0 18px 32px -16px var(--c-shadow); }
.node.sel { box-shadow: 0 0 0 4px color-mix(in oklab, var(--c-accent) 30%, transparent), 0 18px 32px -16px var(--c-shadow); }
.dimmed .node:not(.sel):not(.near) { opacity: .45; }
.node .hd { position: relative; padding: 9px 12px 9px 14px; }
.node .hd::before { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: var(--k); }
.node .r1 { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.node .nm { display: flex; align-items: center; gap: 8px; min-width: 0; }
.node .nm i { color: var(--k); width: 16px; height: 16px; flex-shrink: 0; }
.node .nm b { font: 600 13px "JetBrains Mono", ui-monospace, monospace; color: var(--c-fg); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.node .kd { font-size: 10px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--c-fg-faint); white-space: nowrap; }
.node .sub { margin-top: 2px; font-size: 11px; color: var(--c-fg-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.node .warnl { margin-top: 4px; display: flex; align-items: center; gap: 4px; font-size: 10px; color: var(--c-bad); }
.node .warnl i { width: 12px; height: 12px; }
.badge { display: inline-flex; align-items: center; white-space: nowrap; border-radius: 6px; padding: 1px 6px; font-size: 10.5px; font-weight: 500; line-height: 16px; }
.b-accent { background: var(--c-accent-soft); color: var(--c-accent); box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--c-accent) 25%, transparent); }
.b-ai { background: color-mix(in oklab, var(--c-ai) 11%, transparent); color: var(--c-ai); box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--c-ai) 26%, transparent); }
.b-warn { background: color-mix(in oklab, var(--c-warn) 11%, transparent); color: var(--c-warn); box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--c-warn) 26%, transparent); }
.node .cols { display: flex; width: 100%; align-items: center; justify-content: space-between; gap: 8px; border: 0; border-top: 1px solid var(--c-line); background: transparent;
  padding: 6px 12px; font: 11px Inter, sans-serif; color: var(--c-fg-muted); cursor: pointer; text-align: left; }
.node .cols:hover { background: var(--c-surface-2); color: var(--c-fg); }
.node .cols span:first-child { display: inline-flex; align-items: center; gap: 4px; white-space: nowrap; }
.node .cols i { width: 12px; height: 12px; }
.node .cols .pv { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-family: "JetBrains Mono", monospace; color: var(--c-fg-faint); }
.node .list { max-height: 320px; overflow-y: auto; padding-bottom: 4px; }
.node .c { display: flex; align-items: center; justify-content: space-between; gap: 10px; border-top: 1px solid var(--c-line); padding: 4px 12px; font-size: 11px; }
.node .c .cn { display: flex; align-items: center; gap: 6px; min-width: 0; font-family: "JetBrains Mono", monospace; color: var(--c-fg); }
.node .c .cn span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.node .c .cn i { width: 12px; height: 12px; color: var(--c-ai); }
.node .c .cb { font-size: 10px; color: var(--c-fg-faint); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.node .c .ct { flex-shrink: 0; font: 10px "JetBrains Mono", monospace; color: var(--c-fg-faint); }
.handle { position: absolute; top: 50%; width: 10px; height: 10px; border-radius: 99px; border: 2px solid var(--c-surface); background: var(--k); transform: translateY(-50%); }
.handle.l { left: -5px; } .handle.r { right: -5px; }
.tl { position: absolute; left: 16px; top: 16px; display: flex; gap: 8px; align-items: center; }
.tl .btn { box-shadow: 0 1px 0 color-mix(in oklab, var(--c-line-strong) 50%, transparent), 0 10px 28px -18px var(--c-shadow); color: var(--c-fg-muted); }
.shown { border-radius: 8px; border: 1px solid var(--c-line); background: var(--c-surface); padding: 5px 10px; font-size: 12px; color: var(--c-fg-faint); }
.shown:empty { display: none; }
.legend { position: absolute; right: 16px; top: 16px; max-width: 55%; display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 4px 12px; border-radius: 8px; border: 1px solid var(--c-line);
  background: color-mix(in oklab, var(--c-surface) 95%, transparent); padding: 8px 12px; font-size: 10.5px; color: var(--c-fg-muted); pointer-events: none;
  box-shadow: 0 10px 28px -18px var(--c-shadow); }
.legend span { display: inline-flex; align-items: center; gap: 6px; }
.legend .ln { display: inline-block; width: 20px; height: 0; border-top: 2px solid; }
.legend i { width: 12px; height: 12px; color: var(--c-ai); }
.ctl { position: absolute; left: 16px; bottom: 16px; display: flex; flex-direction: column; border-radius: 12px; overflow: hidden; border: 1px solid var(--c-line);
  box-shadow: 0 4px 16px var(--c-shadow); }
.ctl button { display: flex; width: 32px; height: 32px; align-items: center; justify-content: center; border: 0; border-bottom: 1px solid var(--c-line); background: var(--c-surface);
  color: var(--c-fg-muted); cursor: pointer; }
.ctl button:last-child { border-bottom: 0; }
.ctl button:hover { background: var(--c-surface-2); color: var(--c-fg); }
.hint { position: absolute; right: 16px; bottom: 14px; font-size: 11px; color: var(--c-fg-faint); pointer-events: none; }
.detail { position: relative; width: 0; flex-shrink: 0; overflow: hidden; background: var(--c-surface); border-left: 1px solid var(--c-line); transition: width .25s cubic-bezier(.2,.7,.2,1); }
.detail.open { width: min(440px, 46%); }
.detail .close { position: absolute; right: 12px; top: 14px; z-index: 2; display: flex; width: 30px; height: 30px; align-items: center; justify-content: center; border-radius: 8px;
  border: 0; background: transparent; color: var(--c-fg-muted); cursor: pointer; }
.detail .close:hover { background: var(--c-surface-2); color: var(--c-fg); }
.detail .body { height: 100%; overflow-y: auto; min-width: 320px; }
.detail .stripe { height: 4px; }
.detail .top { padding: 18px 20px 16px; border-bottom: 1px solid var(--c-line); }
.detail .kind { display: flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; }
.detail .kind i { width: 14px; height: 14px; }
.detail .title { margin-top: 6px; font: 600 18px "JetBrains Mono", monospace; color: var(--c-fg); word-break: break-all; padding-right: 30px; }
.detail .subt { margin-top: 2px; font-size: 13px; color: var(--c-fg-muted); }
.detail .tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
.detail .sec { padding: 0 20px 20px; }
.detail .lab { margin: 18px 0 8px; font-size: 11px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; color: var(--c-fg-faint); }
.detail .inp { border-radius: 10px; border: 1px solid var(--c-line); background: var(--c-sunken); padding: 10px 12px; margin-top: 8px; }
.detail .inp .between { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.detail .mono { font-family: "JetBrains Mono", monospace; }
.detail .chip { display: inline-flex; align-items: center; gap: 6px; border-radius: 6px; border: 1px solid var(--c-line); background: var(--c-sunken); padding: 2px 8px;
  font: 11.5px "JetBrains Mono", monospace; color: var(--c-fg-muted); margin: 0 6px 6px 0; }
.detail pre { font: 11.5px/1.6 "JetBrains Mono", monospace; white-space: pre-wrap; word-break: break-word; background: var(--c-sunken); border: 1px solid var(--c-line);
  border-radius: 10px; padding: 10px 12px; color: var(--c-fg); max-height: 300px; overflow: auto; margin: 0; }
.detail .colbox { border: 1px solid var(--c-line); border-radius: 10px; overflow: hidden; }
.detail .colrow { padding: 7px 12px; border-top: 1px solid var(--c-line); }
.detail .colrow:first-child { border-top: 0; }
.detail .note { border-radius: 10px; border: 1px solid color-mix(in oklab, var(--c-warn) 30%, transparent); background: color-mix(in oklab, var(--c-warn) 6%, transparent);
  padding: 10px 12px; font-size: 12px; color: var(--c-fg-muted); margin-top: 14px; }
.detail .badge { background: var(--c-surface-2); color: var(--c-fg-muted); box-shadow: inset 0 0 0 1px var(--c-line); }
.detail .b-ok { background: color-mix(in oklab, var(--c-ok) 11%, transparent); color: var(--c-ok); }
.detail .b-info { background: color-mix(in oklab, var(--c-info) 11%, transparent); color: var(--c-info); }
.detail .b-bad { background: color-mix(in oklab, var(--c-bad) 11%, transparent); color: var(--c-bad); }
.detail .b-warn { background: color-mix(in oklab, var(--c-warn) 11%, transparent); color: var(--c-warn); }
.detail .b-ai { background: color-mix(in oklab, var(--c-ai) 11%, transparent); color: var(--c-ai); }
.detail .b-accent { background: var(--c-accent-soft); color: var(--c-accent); }
.detail a { color: var(--c-accent); text-decoration: none; font: 500 11.5px "JetBrains Mono", monospace; }
.detail a:hover { text-decoration: underline; }
.faint { color: var(--c-fg-faint); } .muted { color: var(--c-fg-muted); } .fg { color: var(--c-fg); } .warn { color: var(--c-warn); }
.ico { display: inline-block; flex-shrink: 0; background-color: currentColor; vertical-align: -0.18em; }
"""

JS = r"""
const I = {
  db: '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/>',
  layers: '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/><path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>',
  sliders: '<line x1="21" x2="14" y1="4" y2="4"/><line x1="10" x2="3" y1="4" y2="4"/><line x1="21" x2="12" y1="12" y2="12"/><line x1="8" x2="3" y1="12" y2="12"/><line x1="21" x2="16" y1="20" y2="20"/><line x1="12" x2="3" y1="20" y2="20"/><line x1="14" x2="14" y1="2" y2="6"/><line x1="8" x2="8" y1="10" y2="14"/><line x1="16" x2="16" y1="18" y2="22"/>',
  monitor: '<path d="M10 7.75a.75.75 0 0 1 1.142-.638l3.664 2.249a.75.75 0 0 1 0 1.278l-3.664 2.25a.75.75 0 0 1-1.142-.64z"/><path d="M12 17v4"/><path d="M8 21h8"/><rect x="2" y="3" width="20" height="14" rx="2"/>',
  fn: '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><path d="M9 17c2 0 2.8-1 2.8-2.8V10c0-2 1-3.3 3.2-3"/><path d="M9 11.2h5.7"/>',
  sparkles: '<path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/>',
  right: '<path d="m9 18 6-6-6-6"/>', down: '<path d="m6 9 6 6 6-6"/>',
  alert: '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
  plus: '<path d="M5 12h14"/><path d="M12 5v14"/>', minus: '<path d="M5 12h14"/>',
  fit: '<path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M21 8V5a2 2 0 0 0-2-2h-3"/><path d="M3 16v3a2 2 0 0 0 2 2h3"/><path d="M16 21h3a2 2 0 0 0 2-2v-3"/>',
  expand: '<path d="M15 3h6v6"/><path d="M9 21H3v-6"/><path d="M21 3l-7 7"/><path d="M3 21l7-7"/>',
  collapse: '<path d="M4 14h6v6"/><path d="M20 10h-6V4"/><path d="M14 10l7-7"/><path d="M3 21l7-7"/>',
  image: '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>',
  x: '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
};
const svgIcon = (n) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">${I[n] || ""}</svg>`;
const KIND = { db_table: ["--c-node-table", "db", "SAP table"], itab: ["--c-node-itab", "layers", "Internal table"], param: ["--c-node-param", "sliders", "Inputs"],
  output: ["--c-node-output", "monitor", "Output"], fm: ["--c-node-fm", "fn", "Function module"] };
const OP = { db_read: "SELECT", fae_read: "FOR ALL ENTRIES", filter: "DELETE WHERE", dedup: "DEDUP", loop_build: "LOOP + APPEND", collect: "COLLECT", modify: "LOOP modify",
  union: "UNION", values: "VALUES", value_for: "VALUE FOR", copy: "COPY", empty: "EMPTY", llm: "AI step" };
const EDGE = { read: ["--c-node-table", "", "read"], join: ["--c-accent", "", "join"], lookup: ["--c-ai", "6 4", "READ TABLE / lookup"], fae: ["--c-node-param", "4 4", "FOR ALL ENTRIES"],
  flow: ["--c-fg-faint", "", "next step"], param: ["--c-node-param", "2 4", "input"], output: ["--c-node-output", "", "output"], aggregate: ["--c-warn", "6 3", "aggregate"] };
const W = 260, GX = 88, GY = 36;
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

function layers(nodes, edges) {
  const ids = nodes.map((n) => n.id), known = new Set(ids), succ = new Map(ids.map((i) => [i, []]));
  edges.forEach((e) => { if (known.has(e.s) && known.has(e.t) && e.s !== e.t) succ.get(e.s).push(e.t); });
  const color = new Map(ids.map((i) => [i, 0])), back = new Set();
  for (const root of ids) {
    if (color.get(root)) continue;
    const stack = [[root, 0]];
    color.set(root, 1);
    while (stack.length) {
      const top = stack[stack.length - 1], kids = succ.get(top[0]);
      if (top[1] >= kids.length) { color.set(top[0], 2); stack.pop(); continue; }
      const nxt = kids[top[1]++];
      if (color.get(nxt) === 1) back.add(top[0] + "\u0000" + nxt);
      else if (color.get(nxt) === 0) { color.set(nxt, 1); stack.push([nxt, 0]); }
    }
  }
  const dag = new Map(ids.map((i) => [i, succ.get(i).filter((t) => !back.has(i + "\u0000" + t))]));
  const indeg = new Map(ids.map((i) => [i, 0]));
  dag.forEach((ts) => ts.forEach((t) => indeg.set(t, indeg.get(t) + 1)));
  const level = new Map(ids.map((i) => [i, 0])), queue = ids.filter((i) => indeg.get(i) === 0);
  while (queue.length) {
    const u = queue.shift();
    for (const t of dag.get(u)) { level.set(t, Math.max(level.get(t), level.get(u) + 1)); indeg.set(t, indeg.get(t) - 1); if (!indeg.get(t)) queue.push(t); }
  }
  const cols = new Map();
  ids.forEach((i) => { const l = level.get(i); if (!cols.has(l)) cols.set(l, []); cols.get(l).push(i); });
  const preds = new Map(ids.map((i) => [i, []]));
  dag.forEach((ts, s) => ts.forEach((t) => preds.get(t).push(s)));
  const order = new Map();
  cols.forEach((c) => c.forEach((i, k) => order.set(i, k)));
  const keys = [...cols.keys()].sort((a, b) => a - b);
  const bary = (i, list) => (list.length ? list.reduce((s, x) => s + order.get(x), 0) / list.length : order.get(i));
  for (let r = 0; r < 4; r++) {
    for (const k of keys.slice(1)) { cols.get(k).sort((a, b) => bary(a, preds.get(a)) - bary(b, preds.get(b))); cols.get(k).forEach((i, n) => order.set(i, n)); }
    for (const k of keys.slice(0, -1).reverse()) { cols.get(k).sort((a, b) => bary(a, dag.get(a)) - bary(b, dag.get(b))); cols.get(k).forEach((i, n) => order.set(i, n)); }
  }
  return { cols, keys, preds };
}

function nodeHtml(n, st) {
  const k = KIND[n.kind] || KIND.itab, open = st.expanded.has(n.id);
  const status = n.status === "unresolved" ? "var(--c-bad)" : n.status === "llm" ? "var(--c-ai)" : n.status === "warning" ? "var(--c-warn)" : `var(${k[0]})`;
  const tag = n.kind === "itab" && n.op ? `<span class="badge ${n.status === "ok" ? "b-accent" : n.status === "llm" ? "b-ai" : "b-warn"}">${esc(OP[n.op] || n.op)}</span>`
    : `<span class="kd">${k[2]}</span>`;
  const sub = n.sub ? `<div class="sub">${esc(n.sub)}</div>` : "";
  const warn = n.status === "unresolved" ? `<div class="warnl"><i>${svgIcon("alert")}</i>needs context or AI</div>` : "";
  let cols = "";
  if (n.columns.length) {
    const preview = open ? "" : `<span class="pv">${esc(n.columns.slice(0, 3).map((c) => c.n.toLowerCase()).join(", "))}${n.columns.length > 3 ? "…" : ""}</span>`;
    cols = `<button class="cols" data-toggle="${esc(n.id)}"><span><i>${svgIcon(open ? "down" : "right")}</i>${n.columns.length} column${n.columns.length === 1 ? "" : "s"}</span>${preview}</button>`;
    if (open) cols += `<div class="list">${n.columns.map((c) => `<div class="c"><div style="min-width:0"><div class="cn">${c.d ? `<i>${svgIcon("sparkles")}</i>` : ""}<span>${esc(c.n.toLowerCase())}</span></div>${st.biz && c.b ? `<div class="cb">${esc(c.b)}</div>` : ""}</div><span class="ct">${esc(c.t || "")}</span></div>`).join("")}</div>`;
  }
  return `<div class="node${st.selected === n.id ? " sel" : ""}" data-id="${esc(n.id)}" style="--k:var(${k[0]});border-color:color-mix(in oklab, ${status} 55%, var(--c-line-strong))">`
    + `<span class="handle l"></span><div class="hd" style="background:color-mix(in oklab, var(${k[0]}) 11%, var(--c-surface))"><div class="r1"><div class="nm"><i>${svgIcon(k[1])}</i><b>${esc(n.label)}</b></div>${tag}</div>${st.biz ? sub : ""}${warn}</div>`
    + `${cols}<span class="handle r"></span></div>`;
}

function edgeLabel(e) {
  const on = e.on || [];
  if (e.label && on.length) return `${e.label}: ${on.map((s) => s.replace(/COALESCE\((.*?), [^)]*\)/g, "$1")).join(" AND ").slice(0, 60)}`;
  return e.label || "";
}

function render(root, st) {
  const data = st.data, hide = st.hideFm;
  const nodes = data.nodes.filter((n) => !(hide && n.kind === "fm"));
  const keep = new Set(nodes.map((n) => n.id));
  const edges = data.edges.filter((e) => keep.has(e.s) && keep.has(e.t));
  st.visible = { nodes, edges };
  root.querySelector(".cnt").innerHTML = `<b>${data.nodes.length}</b> nodes · <b>${data.edges.length}</b> links`;
  root.querySelector(".shown").textContent = nodes.length !== data.nodes.length ? `${nodes.length} of ${data.nodes.length} shown` : "";
  const box = root.querySelector(".nodes");
  box.innerHTML = nodes.map((n) => nodeHtml(n, st)).join("");
  const h = new Map();
  box.querySelectorAll(".node").forEach((el) => h.set(el.dataset.id, el.offsetHeight));
  const { cols, keys } = layers(nodes, edges);
  const heights = keys.map((k) => cols.get(k).reduce((s, i) => s + h.get(i), 0) + (cols.get(k).length - 1) * GY);
  const tallest = Math.max(0, ...heights);
  const pos = new Map();
  keys.forEach((k, ci) => {
    let y = (tallest - heights[ci]) / 2;
    cols.get(k).forEach((i) => { pos.set(i, { x: ci * (W + GX), y, h: h.get(i) }); y += h.get(i) + GY; });
  });
  st.pos = pos;
  box.querySelectorAll(".node").forEach((el) => { const p = pos.get(el.dataset.id); el.style.left = p.x + "px"; el.style.top = p.y + "px"; });
  const svg = root.querySelector(".edges");
  const width = keys.length * (W + GX), height = tallest + 40;
  svg.setAttribute("width", width); svg.setAttribute("height", height);
  let defs = "<defs>";
  Object.entries(EDGE).forEach(([kind, v]) => { defs += `<marker id="m-${kind}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" style="fill:var(${v[0]})"/></marker>`; });
  defs += "</defs>";
  let paths = "", labels = "";
  st.paths = [];
  edges.forEach((e) => {
    const a = pos.get(e.s), b = pos.get(e.t), v = EDGE[e.kind] || EDGE.flow;
    const sx = a.x + W, sy = a.y + a.h / 2, tx = b.x, ty = b.y + b.h / 2;
    let d, mx, my;
    if (tx <= sx) {
      const lift = Math.max(a.h, b.h) / 2 + 40;
      d = `M${sx},${sy} C${sx + 90},${sy - lift} ${tx - 90},${ty - lift} ${tx},${ty}`; mx = (sx + tx) / 2; my = Math.min(sy, ty) - lift * 0.75;
    } else {
      const dx = Math.max(40, (tx - sx) / 2);
      d = `M${sx},${sy} C${sx + dx},${sy} ${tx - dx},${ty} ${tx},${ty}`; mx = (sx + tx) / 2; my = (sy + ty) / 2;
    }
    const hot = st.selected && (e.s === st.selected || e.t === st.selected);
    paths += `<path d="${d}" class="${hot ? "hot " : ""}${e.kind === "output" ? "anim" : ""}" style="stroke:var(${v[0]})${v[1] ? `;stroke-dasharray:${v[1]}` : ""}" marker-end="url(#m-${e.kind in EDGE ? e.kind : "flow"})"/>`;
    st.paths.push({ d, color: v[0], dash: v[1], kind: e.kind });
    const text = edgeLabel(e);
    if (text) { labels += `<div class="elab${hot ? " hot" : ""}" style="left:${mx}px;top:${my}px">${esc(text)}</div>`; st.paths[st.paths.length - 1].label = { text, x: mx, y: my }; }
  });
  svg.innerHTML = defs + paths;
  svg.classList.toggle("dim", !!st.selected);
  box.insertAdjacentHTML("beforeend", labels);
  root.querySelector(".pane").classList.toggle("dimmed", !!st.selected);
  if (st.selected) {
    const near = new Set();
    edges.forEach((e) => { if (e.s === st.selected) near.add(e.t); if (e.t === st.selected) near.add(e.s); });
    box.querySelectorAll(".node").forEach((el) => el.classList.toggle("near", near.has(el.dataset.id)));
  }
  st.bounds = { w: width - GX, h: tallest };
  const btn = root.querySelector('[data-a="expand"]');
  const allOpen = st.expanded.size > 0;
  btn.querySelector("span").textContent = allOpen ? "Collapse all" : "Expand all columns";
  btn.querySelector("i").innerHTML = svgIcon(allOpen ? "collapse" : "expand");
}

function apply(root, st) {
  root.querySelector(".vp").style.transform = `translate(${st.view.x}px, ${st.view.y}px) scale(${st.view.k})`;
}

function fit(root, st) {
  const pane = root.querySelector(".pane"), pw = pane.clientWidth, ph = pane.clientHeight;
  if (!pw || !ph || !st.bounds.w) return;
  const k = Math.max(0.1, Math.min(1.2, (pw - 80) / st.bounds.w, (ph - 120) / Math.max(1, st.bounds.h)));
  st.view = { k, x: (pw - st.bounds.w * k) / 2, y: Math.max(64, (ph - st.bounds.h * k) / 2 + 20) };
  apply(root, st);
}

function zoomAt(root, st, factor, cx, cy) {
  const k = Math.max(0.1, Math.min(1.8, st.view.k * factor));
  const f = k / st.view.k;
  st.view = { k, x: cx - (cx - st.view.x) * f, y: cy - (cy - st.view.y) * f };
  apply(root, st);
}

function showDetail(root, st) {
  const panel = root.querySelector(".detail");
  const html = st.selected ? st.data.detail[st.selected] : "";
  panel.classList.toggle("open", !!html);
  if (html) panel.querySelector(".body").innerHTML = html;
}

function resolve(host, v) { return getComputedStyle(host).getPropertyValue(v).trim() || "#888"; }

function exportSvg(root, st, host) {
  const c = (v) => resolve(host, v);
  const { nodes } = st.visible;
  const pad = 40, w = st.bounds.w + pad * 2, h = st.bounds.h + pad * 2 + 40;
  let out = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" font-family="JetBrains Mono, ui-monospace, monospace"><rect width="100%" height="100%" fill="${c("--c-canvas")}"/><g transform="translate(${pad},${pad})"><defs>`;
  Object.entries(EDGE).forEach(([kind, v]) => { out += `<marker id="m-${kind}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="${c(v[0])}"/></marker>`; });
  out += "</defs>";
  st.paths.forEach((p) => { out += `<path d="${p.d}" fill="none" stroke="${c(p.color)}" stroke-width="1.7"${p.dash ? ` stroke-dasharray="${p.dash}"` : ""} marker-end="url(#m-${p.kind in EDGE ? p.kind : "flow"})"/>`; });
  st.paths.forEach((p) => {
    if (!p.label) return;
    const tw = Math.min(260, p.label.text.length * 6 + 12);
    out += `<rect x="${p.label.x - tw / 2}" y="${p.label.y - 9}" width="${tw}" height="18" rx="6" fill="${c("--c-surface")}" stroke="${c("--c-line")}"/><text x="${p.label.x}" y="${p.label.y + 3.5}" text-anchor="middle" font-size="10" fill="${c("--c-fg-muted")}">${esc(p.label.text.slice(0, 42))}</text>`;
  });
  nodes.forEach((n) => {
    const p = st.pos.get(n.id), k = KIND[n.kind] || KIND.itab, kc = c(k[0]);
    out += `<g><rect x="${p.x}" y="${p.y}" width="${W}" height="${p.h}" rx="12" fill="${c("--c-surface")}" stroke="${kc}" stroke-opacity=".55"/>`
      + `<rect x="${p.x}" y="${p.y}" width="${W}" height="${n.sub && st.biz ? 52 : 36}" rx="12" fill="${kc}" fill-opacity=".11"/><rect x="${p.x}" y="${p.y}" width="4" height="${n.sub && st.biz ? 52 : 36}" fill="${kc}"/>`
      + `<text x="${p.x + 14}" y="${p.y + 22}" font-size="13" font-weight="600" fill="${c("--c-fg")}">${esc(n.label.slice(0, 26))}</text>`
      + `<text x="${p.x + W - 12}" y="${p.y + 22}" text-anchor="end" font-size="9.5" font-family="Inter, sans-serif" fill="${c("--c-fg-faint")}">${esc(n.kind === "itab" && n.op ? OP[n.op] || n.op : k[2].toUpperCase())}</text>`
      + (n.sub && st.biz ? `<text x="${p.x + 14}" y="${p.y + 40}" font-size="11" font-family="Inter, sans-serif" fill="${c("--c-fg-muted")}">${esc(n.sub.slice(0, 40))}</text>` : "")
      + (n.columns.length ? `<text x="${p.x + 14}" y="${p.y + (n.sub && st.biz ? 70 : 54)}" font-size="10.5" fill="${c("--c-fg-faint")}">${n.columns.length} columns: ${esc(n.columns.slice(0, 3).map((x) => x.n.toLowerCase()).join(", ").slice(0, 30))}</text>` : "")
      + "</g>";
  });
  return out + "</g></svg>";
}

function download(url, name) {
  const a = document.createElement("a");
  a.href = url; a.download = name;
  document.body.appendChild(a); a.click(); a.remove();
}

export default function (component) {
  const { data, parentElement } = component;
  const root = parentElement;
  const host = parentElement.host || parentElement;
  let st = root.tcbFlow;
  const sig = (data.nodes || []).map((n) => n.id).join("|");
  if (!st) {
    st = { expanded: new Set(), selected: null, biz: true, hideFm: false, view: { x: 0, y: 0, k: 1 }, sig: null, touched: false };
    root.tcbFlow = st;
    root.querySelectorAll("i[data-i]").forEach((el) => { el.innerHTML = svgIcon(el.dataset.i === "expand" ? "expand" : el.dataset.i); });
    root.querySelector(".legend").innerHTML = ["read", "join", "lookup", "fae", "flow", "output"].map((k) => `<span><span class="ln" style="border-color:var(${EDGE[k][0]});${EDGE[k][1] ? "border-top-style:dashed" : ""}"></span>${EDGE[k][2]}</span>`).join("")
      + `<span><i>${svgIcon("sparkles")}</i>derived column</span>`;
    const pane = root.querySelector(".pane");
    new ResizeObserver(() => { if (!st.touched) fit(root, st); }).observe(pane);
    let drag = null;
    pane.addEventListener("pointerdown", (e) => {
      if (e.button !== 0 || e.target.closest(".node, .tl, .ctl, .legend")) return;
      drag = { x: e.clientX, y: e.clientY, vx: st.view.x, vy: st.view.y, moved: false };
      pane.setPointerCapture(e.pointerId);
      pane.classList.add("drag");
    });
    pane.addEventListener("pointermove", (e) => {
      if (!drag) return;
      const dx = e.clientX - drag.x, dy = e.clientY - drag.y;
      if (Math.abs(dx) + Math.abs(dy) > 3) { drag.moved = true; st.touched = true; }
      st.view.x = drag.vx + dx; st.view.y = drag.vy + dy; apply(root, st);
    });
    const end = (e) => {
      if (!drag) return;
      pane.classList.remove("drag");
      if (!drag.moved && st.selected) { st.selected = null; render(root, st); showDetail(root, st); }
      drag = null;
    };
    pane.addEventListener("pointerup", end);
    pane.addEventListener("pointercancel", end);
    pane.addEventListener("wheel", (e) => {
      e.preventDefault();
      st.touched = true;
      const r = pane.getBoundingClientRect();
      zoomAt(root, st, Math.exp(-e.deltaY * (e.ctrlKey ? 0.01 : 0.0015)), e.clientX - r.left, e.clientY - r.top);
    }, { passive: false });
    root.querySelector(".nodes").addEventListener("click", (e) => {
      const t = e.target.closest("[data-toggle]");
      if (t) { const id = t.dataset.toggle; st.expanded.has(id) ? st.expanded.delete(id) : st.expanded.add(id); render(root, st); return; }
      const n = e.target.closest(".node");
      if (n) { st.selected = st.selected === n.dataset.id ? null : n.dataset.id; render(root, st); showDetail(root, st); }
    });
    root.querySelector(".detail .close").addEventListener("click", () => { st.selected = null; render(root, st); showDetail(root, st); });
    root.querySelector(".detail").addEventListener("click", (e) => {
      const a = e.target.closest('a[href^="?"]');
      if (a && window.tcbNav) { e.preventDefault(); e.stopPropagation(); window.tcbNav("go", a.getAttribute("href") + "#" + Date.now()); }
    });
    root.querySelectorAll(".tg input").forEach((inp) => inp.addEventListener("change", () => {
      if (inp.dataset.k === "biz") st.biz = inp.checked; else st.hideFm = inp.checked;
      render(root, st);
      if (inp.dataset.k === "fm") fit(root, st);
    }));
    root.addEventListener("click", (e) => {
      const b = e.target.closest("[data-a]");
      if (!b) return;
      const a = b.dataset.a, pane2 = root.querySelector(".pane");
      if (a === "in" || a === "out") st.touched = true;
      if (a === "in" || a === "out") zoomAt(root, st, a === "in" ? 1.25 : 0.8, pane2.clientWidth / 2, pane2.clientHeight / 2);
      else if (a === "fit") fit(root, st);
      else if (a === "expand") { st.expanded = st.expanded.size ? new Set() : new Set(st.visible.nodes.map((n) => n.id)); render(root, st); }
      else if (a === "svg") download(URL.createObjectURL(new Blob([exportSvg(root, st, host)], { type: "image/svg+xml" })), `${st.data.name}_dataflow.svg`);
      else if (a === "png") {
        const svg = exportSvg(root, st, host), img = new Image();
        img.onload = () => {
          const cv = document.createElement("canvas");
          cv.width = img.width * 2; cv.height = img.height * 2;
          const ctx = cv.getContext("2d"); ctx.scale(2, 2); ctx.drawImage(img, 0, 0);
          cv.toBlob((blob) => download(URL.createObjectURL(blob), `${st.data.name}_dataflow.png`), "image/png");
        };
        img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
      }
    });
  }
  st.data = data;
  if (st.selected && !(data.detail || {})[st.selected]) st.selected = null;
  render(root, st);
  showDetail(root, st);
  if (st.sig !== sig) { st.sig = sig; st.touched = false; requestAnimationFrame(() => fit(root, st)); } else apply(root, st);
}
"""

FLOW = st.components.v2.component("tcb_flow", html=HTML, css=CSS, js=JS)


def flow_canvas(data: dict, key: str) -> None:
    FLOW(data=data, key=key)
