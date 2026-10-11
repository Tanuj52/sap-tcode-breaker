"""Shared UI building blocks: icons, badges, cards, rings, routing, notifications and the Snowflake location picker."""

from __future__ import annotations

import base64
import html as htmllib
import re
from datetime import datetime, timezone
from functools import lru_cache
from urllib.parse import parse_qsl

import streamlit as st

from backend import core

ICONS = {
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    "plus": '<path d="M5 12h14"/><path d="M12 5v14"/>',
    "database": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/>',
    "layers": '<path d="m12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83Z"/>'
              '<path d="m22 17.65-9.17 4.16a2 2 0 0 1-1.66 0L2 17.65"/><path d="m22 12.65-9.17 4.16a2 2 0 0 1-1.66 0L2 12.65"/>',
    "branch": '<line x1="6" x2="6" y1="3" y2="15"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M18 9a9 9 0 0 1-9 9"/>',
    "network": '<rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="9" y="2" width="6" height="6" rx="1"/>'
               '<path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3"/><path d="M12 12V8"/>',
    "code": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="m10 13-2 2 2 2"/><path d="m14 17 2-2-2-2"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    "tag": '<path d="M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z"/><circle cx="7.5" cy="7.5" r=".5" fill="currentColor"/>',
    "wand": '<path d="m21.64 3.64-1.28-1.28a1.21 1.21 0 0 0-1.72 0L2.36 18.64a1.21 1.21 0 0 0 0 1.72l1.28 1.28a1.2 1.2 0 0 0 1.72 0L21.64 5.36a1.2 1.2 0 0 0 0-1.72"/>'
            '<path d="m14 7 3 3"/><path d="M5 6v4"/><path d="M19 14v4"/><path d="M10 2v2"/><path d="M7 8H3"/><path d="M21 16h-4"/><path d="M11 3H9"/>',
    "sparkles": '<path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
    "xcircle": '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/>',
    "okcircle": '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    "slash": '<circle cx="12" cy="12" r="10"/><path d="m4.9 4.9 14.2 14.2"/>',
    "library": '<path d="m16 6 4 14"/><path d="M12 6v14"/><path d="M8 8v12"/><path d="M4 4v16"/>',
    "folder": '<path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/><path d="M8 10v4"/><path d="M12 10v2"/><path d="M16 10v6"/>',
    "flask": '<path d="M10 2v7.527a2 2 0 0 1-.211.896L4.72 20.55a1 1 0 0 0 .9 1.45h12.76a1 1 0 0 0 .9-1.45l-5.069-10.127A2 2 0 0 1 14 9.527V2"/><path d="M8.5 2h7"/><path d="M7 16h10"/>',
    "sliders": '<line x1="21" x2="14" y1="4" y2="4"/><line x1="10" x2="3" y1="4" y2="4"/><line x1="21" x2="12" y1="12" y2="12"/><line x1="8" x2="3" y1="12" y2="12"/>'
               '<line x1="21" x2="16" y1="20" y2="20"/><line x1="12" x2="3" y1="20" y2="20"/><line x1="14" x2="14" y1="2" y2="6"/><line x1="8" x2="8" y1="10" y2="14"/><line x1="16" x2="16" y1="18" y2="22"/>',
    "home": '<path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
    "play": '<polygon points="6 3 20 12 6 21 6 3"/>',
    "key": '<path d="M2.586 17.414A2 2 0 0 0 2 18.828V21a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h1a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h.172a2 2 0 0 0 1.414-.586l.814-.814a6.5 6.5 0 1 0-4-4z"/><circle cx="16.5" cy="7.5" r=".5" fill="currentColor"/>',
    "cpu": '<rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/>',
    "lock": '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    "workflow": '<rect width="8" height="8" x="3" y="3" rx="2"/><path d="M7 11v4a2 2 0 0 0 2 2h4"/><rect width="8" height="8" x="13" y="13" rx="2"/>',
    "braces": '<path d="M8 3H7a2 2 0 0 0-2 2v5a2 2 0 0 1-2 2 2 2 0 0 1 2 2v5c0 1.1.9 2 2 2h1"/><path d="M16 21h1a2 2 0 0 0 2-2v-5c0-1.1.9-2 2-2a2 2 0 0 1-2-2V5a2 2 0 0 0-2-2h-1"/>',
    "package": '<path d="M11 21.73a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73z"/><path d="M12 22V12"/><path d="m3.3 7 7.703 4.734a2 2 0 0 0 1.994 0L20.7 7"/><path d="m7.5 4.27 9 5.15"/>',
    "upload": '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/>',
    "clipboard": '<rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "book": '<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>',
    "history": '<path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/>',
    "pen": '<path d="M12 20h9"/><path d="M16.376 3.622a1 1 0 0 1 3.002 3.002L7.368 18.635a2 2 0 0 1-.855.506l-2.872.838a.5.5 0 0 1-.62-.62l.838-2.872a2 2 0 0 1 .506-.854z"/>',
    "monitor": '<path d="M10 7.75a.75.75 0 0 1 1.142-.638l3.664 2.249a.75.75 0 0 1 0 1.278l-3.664 2.25a.75.75 0 0 1-1.142-.64z"/><path d="M12 17v4"/><path d="M8 21h8"/><rect x="2" y="3" width="20" height="14" rx="2"/>',
    "function": '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><path d="M9 17c2 0 2.8-1 2.8-2.8V10c0-2 1-3.3 3.2-3"/><path d="M9 11.2h5.7"/>',
    "event": '<circle cx="12" cy="12" r="10"/><polygon points="10 8 16 12 10 16 10 8"/>',
    "method": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="1"/>',
    "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
    "bot": '<path d="M12 8V4H8"/><rect width="16" height="12" x="4" y="8" rx="2"/><path d="M2 14h2"/><path d="M20 14h2"/><path d="M15 13v2"/><path d="M9 13v2"/>',
    "arrow": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    "back": '<path d="m12 19-7-7 7-7"/><path d="M19 12H5"/>',
    "chev": '<path d="m9 18 6-6-6-6"/>',
    "dashboard": '<rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/>',
    "arrowup": '<path d="M7 7h10v10"/><path d="M7 17 17 7"/>',
    "rocket": '<path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/>'
              '<path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"/><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"/>',
    "plug": '<path d="M12 22v-5"/><path d="M9 8V2"/><path d="M15 8V2"/><path d="M18 8v5a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4V8Z"/>',
    "palette": '<circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/><circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/>'
               '<circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"/>',
    "logo": '<path d="M16 3.5 27 9.8v12.4L16 28.5 5 22.2V9.8z"/><path d="M5 9.8 16 16l11-6.2M16 16v12.5"/><path d="M10.5 6.7 21.5 13" stroke-dasharray="2.5 3" opacity=".7"/>',
}


@lru_cache(maxsize=512)
def icon_mask(name: str, stroke: float) -> str:
    box = "0 0 32 32" if name == "logo" else "0 0 24 24"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{box}" fill="none" stroke="black" stroke-width="{stroke}" '
           f'stroke-linecap="round" stroke-linejoin="round">{ICONS.get(name, "").replace("currentColor", "black")}</svg>')
    return "url('data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode() + "')"


def icon(name: str, size: int = 16, stroke: float = 2, cls: str = "") -> str:
    mask = icon_mask(name, stroke)
    return (f'<span class="ico {cls}" style="width:{size}px;height:{size}px;-webkit-mask:{mask} center/contain no-repeat;'
            f'mask:{mask} center/contain no-repeat"></span>')


def svg_img(svg: str, style: str = "") -> str:
    from frontend import theme

    values = theme.get(core.ui_prefs().get("theme")).vars
    solid = re.sub(r"var\(--c-([a-z0-9-]+)\)", lambda m: values.get(m.group(1), "#888"), svg)
    if "xmlns=" not in solid:
        solid = solid.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
    return f'<img alt="" style="display:block;{style}" src="data:image/svg+xml;base64,{base64.b64encode(solid.encode()).decode()}">'


def esc(v) -> str:
    return htmllib.escape("" if v is None else str(v))


def html(markup: str, width="stretch") -> None:
    st.html(markup, width=width)


STATUS_TONE = {"deterministic": "ok", "needs_llm": "warn", "partial": "warn", "failed": "bad", "pending": "slate"}
STATUS_LABEL = {"deterministic": "rules only", "needs_llm": "needs AI", "partial": "partial", "failed": "failed", "pending": "pending"}
PROV_TONE = {"client_pack": "ai", "library": "accent", "ai_generated": "warn", "builtin": "info", "snowflake_catalog": "ok", "inferred": "warn", "unresolved": "bad"}
PROV_LABEL = {"client_pack": "client pack", "library": "your library", "ai_generated": "AI-proposed", "builtin": "SAP dictionary",
              "snowflake_catalog": "Snowflake schema", "inferred": "from code", "unresolved": "unresolved"}
SEV_TONE = {"error": "bad", "warning": "warn", "info": "info"}
TONE_ALIAS = {"emerald": "ok", "amber": "warn", "rose": "bad", "violet": "ai", "sky": "info", "fuchsia": "ai"}


def status_tone(s) -> str:
    return STATUS_TONE.get(s or "", "slate")


def status_label(s) -> str:
    return STATUS_LABEL.get(s or "", s or "")


def prov_tone(p) -> str:
    return PROV_TONE.get(p or "", "slate")


def prov_label(p) -> str:
    return PROV_LABEL.get(p or "", p or "")


def badge(text, tone: str = "slate", title: str = "") -> str:
    tone = TONE_ALIAS.get(tone, tone)
    cls = "" if tone in ("slate", "", None) else f" b-{tone}"
    t = f' title="{esc(title)}"' if title else ""
    return f'<span class="badge{cls}"{t}>{text}</span>'


def origin_label(o) -> str:
    if not o:
        return ""
    return {"ai": "AI proposal", "ddic": "DDIC replica", "snowflake": "Snowflake schema", "manual": "manual"}.get(o, f"import · {o[7:]}" if o.startswith("import:") else o)


def num(v) -> str:
    try:
        return f"{int(v):,}"
    except (TypeError, ValueError):
        return "–"


def compact(v) -> str:
    try:
        n = float(v)
    except (TypeError, ValueError):
        return "–"
    for div, suffix in ((1e6, "M"), (1e3, "K")):
        if abs(n) >= div:
            return f"{n / div:.1f}".rstrip("0").rstrip(".") + suffix
    return f"{int(n)}"


def plural(n: int, word: str, many: str | None = None) -> str:
    return f"{n} {word if n == 1 else (many or word + 's')}"


def ago(iso) -> str:
    if not iso:
        return ""
    try:
        t = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    except ValueError:
        return ""
    s = (datetime.now(timezone.utc) - (t if t.tzinfo else t.replace(tzinfo=timezone.utc))).total_seconds()
    if s < 60:
        return "just now"
    if s < 3600:
        return f"{int(s // 60)} min ago"
    if s < 86400:
        return f"{int(s // 3600)} h ago"
    return f"{int(s // 86400)} d ago"


def when(iso) -> str:
    try:
        return datetime.fromisoformat(str(iso).replace("Z", "+00:00")).astimezone().strftime("%d %b %Y, %H:%M")
    except (TypeError, ValueError):
        return ""


# ---------------------------------------------------------------------- composite blocks
def page_header(eyebrow: str, icon_name: str, title: str, desc: str = "", tools: bool = False) -> None:
    html(f'<div class="page-head{" open" if tools else ""} fade-up"><div class="eyebrow">{icon(icon_name, 14)}{esc(eyebrow)}</div><h1>{title}</h1>'
         + (f"<p>{desc}</p>" if desc else "") + "</div>")


def page_tools():
    return st.container(horizontal=True, vertical_alignment="center", key="page_tools", gap="small")


def panel(key: str, **kwargs):
    return st.container(border=True, key=f"pnl_{key}", **kwargs)


def card_head(title: str, subtitle: str = "", icon_name: str = "", extra: str = "") -> str:
    tile = f'<span class="icon-tile">{icon(icon_name)}</span>' if icon_name else ""
    sub = f'<div class="s">{subtitle}</div>' if subtitle else ""
    return f'<div class="card-head">{tile}<div style="min-width:0;flex:1"><div class="t">{title}</div>{sub}</div>{extra}</div>'


def card(title: str, body: str, subtitle: str = "", icon_name: str = "", pad: bool = True, extra: str = "", style: str = "") -> str:
    head = card_head(title, subtitle, icon_name, extra) if title else ""
    return f'<section class="card fade-up" style="{style}">{head}<div class="{"card-pad" if pad else ""}">{body}</div></section>'


def heading(title: str, subtitle: str = "", icon_name: str = "", extra: str = "") -> None:
    tile = f'<span class="icon-tile">{icon(icon_name)}</span>' if icon_name else ""
    sub = f'<div class="s">{subtitle}</div>' if subtitle else ""
    side = f'<div class="x">{extra}</div>' if extra else ""
    html(f'<div class="panel-head">{tile}<div style="min-width:0"><div class="t">{title}</div>{sub}</div>{side}</div>')


def kpis(items: list[tuple[str, object, str]]) -> str:
    cells = "".join(f'<div><div class="v">{esc(v)}</div><div class="l">{esc(l)}</div><div class="s">{esc(s)}</div></div>' for l, v, s in items)
    return f'<div class="kpis fade-up" style="--n:{len(items)}">{cells}</div>'


def ring(value: float, size: int = 104, stroke: int = 10, color: str = "var(--c-accent)", track: str = "var(--c-surface-2)", inner: str = "") -> str:
    v = max(0.0, min(1.0, value or 0))
    hole = f"radial-gradient(farthest-side,transparent calc(100% - {stroke}px),#000 calc(100% - {stroke - 1}px))"
    return (f'<div style="position:relative;width:{size}px;height:{size}px;flex-shrink:0"><div style="position:absolute;inset:0;border-radius:50%;'
            f'background:conic-gradient({color} {v * 360:.1f}deg,{track} 0);-webkit-mask:{hole};mask:{hole}"></div>'
            f'<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center">{inner}</div></div>')


def callout(tone: str, body: str, icon_name: str | None = None) -> str:
    name = icon_name or {"warn": "alert", "info": "search", "ok": "okcircle", "bad": "xcircle"}[tone]
    return f'<div class="callout {tone}">{icon(name)}<div style="min-width:0;flex:1">{body}</div></div>'


def empty(message: str, icon_name: str = "info") -> None:
    html(f'<div class="empty hatch fade-up"><span class="tile">{icon(icon_name, 22)}</span><div>{message}</div></div>')


def swatch(sw: tuple[str, str, str, str], size: int = 28) -> str:
    return (f'<span style="position:relative;display:inline-flex;width:{size}px;height:{size}px;border-radius:6px;overflow:hidden;background:{sw[0]};'
            f'box-shadow:inset 0 0 0 1px rgba(0,0,0,.15);flex-shrink:0"><span style="width:38%;height:100%;background:{sw[3]}"></span>'
            f'<span style="position:relative;flex:1"><span style="position:absolute;left:18%;right:18%;top:22%;height:30%;border-radius:2px;background:{sw[1]}"></span>'
            f'<span style="position:absolute;left:18%;bottom:18%;width:50%;height:18%;border-radius:2px;background:{sw[2]}"></span></span></span>')


# ---------------------------------------------------------------------- routing and notifications
def route() -> dict[str, str]:
    return {k: st.query_params.get(k) for k in st.query_params.keys()}


def set_route(page: str = "", **params) -> None:
    st.query_params.clear()
    if page:
        st.query_params["page"] = page
    for k, v in params.items():
        if v not in (None, ""):
            st.query_params[k] = str(v)


def go(page: str = "", **params) -> None:
    set_route(page, **params)
    st.rerun()


NAV_JS = """
export default function (component) {
  window.tcbNav = component.setTriggerValue;
  if (window.tcbNavBound) return;
  window.tcbNavBound = true;
  document.addEventListener("click", (e) => {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    const path = e.composedPath ? e.composedPath() : [e.target];
    for (const el of path) {
      if (!el || !el.getAttribute) continue;
      const target = el.getAttribute("data-nav") || (el.tagName === "A" && (el.getAttribute("href") || "").startsWith("?") ? el.getAttribute("href") : null);
      if (target) {
        e.preventDefault();
        e.stopPropagation();
        window.tcbNav && window.tcbNav("go", target + "#" + Date.now());
        return;
      }
    }
  }, true);
}
"""
NAV = st.components.v2.component("tcb_nav", js=NAV_JS, isolate_styles=False)


def follow_link() -> None:
    state = st.session_state.get("navhook")
    target = state.get("go") if isinstance(state, dict) else getattr(state, "go", None)
    if not target:
        return
    params = dict(parse_qsl(target.split("#", 1)[0].lstrip("?"), keep_blank_values=False))
    action = params.pop("do", None)
    if action:
        st.session_state.nav_do = action
    if params or not action:
        page = params.pop("page", "")
        set_route(page, **params)


def nav_hook() -> None:
    NAV(key="navhook", on_go_change=follow_link)


def take_action(prefix: str) -> str | None:
    action = st.session_state.get("nav_do") or ""
    if action.startswith(prefix + ":"):
        st.session_state.pop("nav_do", None)
        return action[len(prefix) + 1:]
    return None


def link(page: str = "", **params) -> str:
    parts = ([f"page={page}"] if page else []) + [f"{k}={v}" for k, v in params.items() if v not in (None, "")]
    return "?" + "&".join(parts) if parts else "?"


def notify(kind: str, title: str, body: str = "") -> None:
    st.session_state.setdefault("flash", []).append((kind, title, body))


def flush_notifications() -> None:
    icons = {"ok": ":material/check_circle:", "error": ":material/error:", "warn": ":material/warning:", "info": ":material/info:"}
    for kind, title, body in st.session_state.pop("flash", []):
        st.toast(f"**{title}**" + (f"  \n{body}" if body else ""), icon=icons.get(kind, ":material/info:"))


def guard(fn, *args, title: str = "Something went wrong", **kwargs):
    try:
        return fn(*args, **kwargs)
    except core.ServiceError as exc:
        notify("error", title, str(exc))
    except Exception as exc:  # noqa: BLE001
        notify("error", title, core.clean(exc))
    return None


# ---------------------------------------------------------------------- Snowflake data (cached)
@st.cache_data(ttl=60, show_spinner=False)
def sf_status() -> dict:
    return core.snowflake_status()


@st.cache_data(ttl=120, show_spinner=False)
def sf_databases() -> list[str] | None:
    try:
        return core.databases()
    except Exception:  # noqa: BLE001
        return None


@st.cache_data(ttl=120, show_spinner=False)
def sf_schemas(database: str) -> list[str] | None:
    try:
        return core.schemas(database)
    except Exception:  # noqa: BLE001
        return None


@st.cache_data(ttl=60, show_spinner=False)
def models() -> list[dict]:
    return core.models()


def settings_changed() -> None:
    sf_status.clear()
    sf_databases.clear()
    sf_schemas.clear()
    models.clear()


def location_picker(label: str, database: str, schema: str, key: str, hint: str = "", db_placeholder: str = "e.g. SAP_RAW",
                    schema_placeholder: str = "e.g. ECC") -> tuple[str, str]:
    dbs = sf_databases()
    st.markdown(f"<div style='font-size:12px;font-weight:500;color:var(--c-fg-muted);margin-bottom:-4px'>{esc(label)}</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if dbs is None:
        with c1:
            db = st.text_input("Database", value=database or "", placeholder=db_placeholder, key=f"{key}_db", label_visibility="collapsed").upper()
        with c2:
            sc = st.text_input("Schema", value=schema or "", placeholder=schema_placeholder, key=f"{key}_sc", label_visibility="collapsed").upper()
        st.caption(hint or "Snowflake not reachable: type the names.")
        return db.strip(), sc.strip()
    opts = sorted(set(dbs) | ({database} if database else set()))
    with c1:
        db = st.selectbox("Database", [""] + opts, index=([""] + opts).index(database) if database in opts else 0, key=f"{key}_db",
                          placeholder=db_placeholder, accept_new_options=True, label_visibility="collapsed",
                          format_func=lambda x: x or "— database —")
    db = (db or "").upper()
    schemas = sf_schemas(db) if db else []
    sopts = sorted(set(schemas or []) | ({schema} if schema else set()))
    with c2:
        sc = st.selectbox("Schema", [""] + sopts, index=([""] + sopts).index(schema) if schema in sopts else 0, key=f"{key}_sc_{db}",
                          placeholder=schema_placeholder, accept_new_options=True, label_visibility="collapsed",
                          format_func=lambda x: x or "— schema —")
    if hint:
        st.caption(hint)
    return db, (sc or "").upper()
