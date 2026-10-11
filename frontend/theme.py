"""Six themes from the React app, applied to Streamlit's native theme and to the custom HTML components."""

from __future__ import annotations

from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class Theme:
    id: str
    name: str
    tagline: str
    dark: bool
    swatch: tuple[str, str, str, str]
    palette: str

    @property
    def vars(self) -> dict[str, str]:
        out = {}
        for part in self.palette.split(";"):
            if ":" in part:
                k, v = part.split(":", 1)
                out[k.strip()] = v.strip()
        return out


THEMES = [
    Theme("ivory", "Warm Ivory", "Ivory paper, forest ink", False, ("#f2eee3", "#fffcf5", "#1a6640", "#10241a"),
          "ink-btn:#8fdcae;ink-btn-fg:#0d2016;canvas:#f2eee3;surface:#fffcf5;surface-2:#e9e3d3;sunken:#f7f3e9;line:#dcd3bf;line-strong:#c2b69b;"
          "fg:#15211a;fg-muted:#3f4b40;fg-faint:#757a66;accent:#1a6640;accent-strong:#12512f;accent-2:#c98a2b;accent-soft:#d9e8dc;on-accent:#ffffff;"
          "ok:#1a7a45;warn:#a3620a;bad:#b3352c;info:#1f5f80;ai:#6b4a9c;node-table:#1a6640;node-itab:#8a6224;node-param:#b0482c;node-output:#1f5f80;"
          "node-fm:#a3620a;side:#10241a;side-2:#1a3427;side-fg:#eef2ea;side-muted:#9fb3a5;side-line:rgba(255,255,255,0.09);side-accent:#86d6a6;"
          "glow:rgba(26,102,64,0.22);shadow:rgba(40,32,10,0.12);grid:#dcd3bf;grain:0.05"),
    Theme("signal", "Signal Orange", "Carbon black, signal orange", False, ("#efeeea", "#ffffff", "#e4520b", "#161514"),
          "ink-btn:#f25a0f;ink-btn-fg:#ffffff;canvas:#efeeea;surface:#ffffff;surface-2:#e7e5df;sunken:#f8f7f4;line:#d9d5cc;line-strong:#b9b2a5;"
          "fg:#111110;fg-muted:#3f3b36;fg-faint:#7a746b;accent:#e4520b;accent-strong:#c2430a;accent-2:#111110;accent-soft:#fde2d2;on-accent:#ffffff;"
          "ok:#1d7a50;warn:#b77400;bad:#c93224;info:#22609f;ai:#6d3ff0;node-table:#e4520b;node-itab:#3a3631;node-param:#6d3ff0;node-output:#1d7a50;"
          "node-fm:#b77400;side:#161514;side-2:#262422;side-fg:#f4f2ee;side-muted:#a29b90;side-line:rgba(255,255,255,0.08);side-accent:#ff7a33;"
          "glow:rgba(228,82,11,0.22);shadow:rgba(20,15,10,0.10);grid:#d9d5cc;grain:0.045"),
    Theme("burgundy", "Burgundy Reserve", "Cream, oxblood and brass", False, ("#f2e9e4", "#fffaf7", "#6b1530", "#23080f"),
          "ink-btn:#d9ae63;ink-btn-fg:#22070e;canvas:#f2e9e4;surface:#fffaf7;surface-2:#e8d9d2;sunken:#f8f1ed;line:#dbc5bc;line-strong:#c0a194;"
          "fg:#210b11;fg-muted:#553840;fg-faint:#8e7076;accent:#6b1530;accent-strong:#521024;accent-2:#b5873a;accent-soft:#efd8de;on-accent:#fff8f2;"
          "ok:#2f7350;warn:#9c6f1c;bad:#ad2219;info:#3d5f84;ai:#5f4392;node-table:#6b1530;node-itab:#9c6f1c;node-param:#5f4392;node-output:#2f7350;"
          "node-fm:#b5873a;side:#23080f;side-2:#36111b;side-fg:#f7ebe5;side-muted:#bf9aa1;side-line:rgba(255,235,225,0.09);side-accent:#dcb067;"
          "glow:rgba(107,21,48,0.22);shadow:rgba(50,15,20,0.12);grid:#dbc5bc;grain:0.05"),
    Theme("violet", "Royal Violet", "Lavender paper, deep indigo", False, ("#eeebf7", "#ffffff", "#5a1fd1", "#150c30"),
          "ink-btn:#b8a2ff;ink-btn-fg:#140b2e;canvas:#eeebf7;surface:#ffffff;surface-2:#e3ddf3;sunken:#f7f5fc;line:#d3caec;line-strong:#b2a3dd;"
          "fg:#120c27;fg-muted:#423a66;fg-faint:#7d74a3;accent:#5a1fd1;accent-strong:#4515a8;accent-2:#c2338a;accent-soft:#e6dcfd;on-accent:#ffffff;"
          "ok:#12763a;warn:#a64c05;bad:#b5103c;info:#0b6a87;ai:#b0179f;node-table:#5a1fd1;node-itab:#0b6a87;node-param:#c2338a;node-output:#12763a;"
          "node-fm:#a64c05;side:#150c30;side-2:#241749;side-fg:#f0ecff;side-muted:#a69ad6;side-line:rgba(255,255,255,0.09);side-accent:#b39bff;"
          "glow:rgba(90,31,209,0.22);shadow:rgba(30,15,70,0.12);grid:#d3caec;grain:0.045"),
    Theme("midnight", "Midnight Gold", "Charcoal dark, warm gold", True, ("#0b0c0f", "#13161b", "#e2b04a", "#07080a"),
          "ink-btn:#e2b04a;ink-btn-fg:#15100a;canvas:#0b0c0f;surface:#13161b;surface-2:#1a1e25;sunken:#0f1115;line:#262b34;line-strong:#384050;"
          "fg:#eef0f3;fg-muted:#a9b0bb;fg-faint:#6f7784;accent:#e2b04a;accent-strong:#f0c264;accent-2:#46c7b8;accent-soft:rgba(226,176,74,0.14);"
          "on-accent:#15100a;ok:#4ad387;warn:#f4bd38;bad:#f87171;info:#67a8f5;ai:#c48bfb;node-table:#e2b04a;node-itab:#67a8f5;node-param:#c48bfb;"
          "node-output:#4ad387;node-fm:#f4bd38;side:#07080a;side-2:#15181e;side-fg:#eef0f3;side-muted:#7d8591;side-line:rgba(255,255,255,0.07);"
          "side-accent:#e2b04a;glow:rgba(226,176,74,0.18);shadow:rgba(0,0,0,0.5);grid:#20252d;grain:0.06"),
    Theme("amethyst", "Amethyst Night", "Deep violet dark, orchid glow", True, ("#0e0a19", "#161026", "#a688ff", "#08050f"),
          "ink-btn:#b79cff;ink-btn-fg:#110a1f;canvas:#0e0a19;surface:#161026;surface-2:#1e1633;sunken:#120d20;line:#2d2346;line-strong:#43356a;"
          "fg:#f0ecfa;fg-muted:#b6abd2;fg-faint:#7e7399;accent:#a688ff;accent-strong:#bba4ff;accent-2:#f07ad8;accent-soft:rgba(166,136,255,0.16);"
          "on-accent:#120c20;ok:#3ad6a0;warn:#f8c13a;bad:#fb7189;info:#6be4f9;ai:#f0abfc;node-table:#a688ff;node-itab:#6be4f9;node-param:#f07ad8;"
          "node-output:#3ad6a0;node-fm:#f8c13a;side:#08050f;side-2:#171027;side-fg:#f0ecfa;side-muted:#8b80a8;side-line:rgba(255,255,255,0.07);"
          "side-accent:#b79cff;glow:rgba(166,136,255,0.22);shadow:rgba(0,0,0,0.55);grid:#241b38;grain:0.06"),
]
BY_ID = {t.id: t for t in THEMES}


def get(theme_id: str | None) -> Theme:
    return BY_ID.get(theme_id or "", THEMES[0])


def native_options(t: Theme) -> dict[str, object]:
    v = t.vars
    return {
        "theme.base": "dark" if t.dark else "light",
        "theme.primaryColor": v["accent"],
        "theme.backgroundColor": v["canvas"],
        "theme.secondaryBackgroundColor": v["sunken"],
        "theme.textColor": v["fg"],
        "theme.borderColor": v["line"],
        "theme.linkColor": v["accent"],
        "theme.codeBackgroundColor": v["sunken"],
        "theme.dataframeHeaderBackgroundColor": v["surface-2"],
        "theme.sidebar.backgroundColor": v["side"],
        "theme.sidebar.secondaryBackgroundColor": v["side-2"],
        "theme.sidebar.textColor": v["side-fg"],
        "theme.sidebar.primaryColor": v["side-accent"],
        "theme.sidebar.borderColor": v["side-2"],
    }


def sync_native(t: Theme) -> bool:
    """Point Streamlit's own theme at the palette. Returns True when it changed (a rerun sends it to the browser)."""
    changed = False
    for key, value in native_options(t).items():
        try:
            if st._config.get_option(key) != value:
                st._config.set_option(key, value)
                changed = True
        except Exception:  # noqa: BLE001
            continue
    return changed


NOISE = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180'%3E%3Cfilter id='n'%3E%3CfeTurbulence "
         "type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0.5 0 0 0 0 0.5 0 0 0 0 0.5 "
         "0 0 0 1.4 -0.2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")")
PAPER = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='240' height='240'%3E%3Cfilter id='n'%3E%3CfeTurbulence "
         "type='fractalNoise' baseFrequency='.8' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0.45 0 0 0 0 0.42 0 0 0 0 0.38 "
         "0 0 0 0.16 -0.04'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")")

SHELL_CSS = """
html, body { background: var(--c-canvas); }
.stApp { background-color: var(--c-canvas); background-image: PAPER; color: var(--c-fg); font-feature-settings: "cv11", "ss01", "ss03"; -webkit-font-smoothing: antialiased; }
::selection { background: color-mix(in oklab, var(--c-accent) 28%, transparent); }
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb { background: var(--c-line-strong); border-radius: 8px; border: 3px solid transparent; background-clip: padding-box; }
::-webkit-scrollbar-track { background: transparent; }
[data-testid="stHeader"], [data-testid="stDecoration"], [data-testid="stToolbar"] { display: none !important; }
[data-testid="stMain"] { padding-top: 0; }
[data-testid="stMainBlockContainer"] { max-width: 1384px; padding: 0 32px 72px !important; }
[data-testid="stMainBlockContainer"] > div > [data-testid="stVerticalBlock"] { gap: 1rem; }
[data-testid="stVerticalBlock"] { gap: .9rem; }
.st-key-navhook { display: none !important; }
[data-testid="stElementContainer"]:has(> .stHtml:empty), [data-testid="stElementContainer"]:has(> [data-testid="stMarkdown"] style:only-child) { display: none; }

/* ------------------------------------------------------------------ sidebar */
section[data-testid="stSidebar"] { width: 252px !important; min-width: 252px !important; max-width: 252px !important; transform: none !important;
  background-color: var(--c-side); border-right: 1px solid var(--c-side-line); }
[data-testid="stSidebarHeader"], [data-testid="stSidebarResizeHandle"], [data-testid="stSidebarCollapseButton"], [data-testid="stExpandSidebarButton"] { display: none !important; }
[data-testid="stSidebarContent"] { position: relative; background: var(--c-side); overflow-x: hidden; padding: 0 !important; }
[data-testid="stSidebarContent"]::before { content: ""; position: absolute; inset: 0 0 auto 0; height: 340px; pointer-events: none; opacity: .4;
  background-image: linear-gradient(var(--c-side-line) 1px, transparent 1px), linear-gradient(90deg, var(--c-side-line) 1px, transparent 1px); background-size: 44px 44px;
  -webkit-mask-image: linear-gradient(to bottom, black, transparent); mask-image: linear-gradient(to bottom, black, transparent); }
[data-testid="stSidebarUserContent"] { position: relative; padding: 14px 16px 0 !important; min-height: 100vh; display: flex; flex-direction: column; }
[data-testid="stSidebarUserContent"] > div { flex: 1; display: flex; flex-direction: column; }
[data-testid="stSidebarUserContent"] > div > [data-testid="stVerticalBlock"] { flex: 1; gap: 2px; }
[data-testid="stSidebar"] [data-testid="stBaseButton-tertiary"] { width: 100%; justify-content: flex-start; padding: 8px 12px; border-radius: 8px; min-height: 0;
  color: var(--c-side-muted); font-weight: 500; transition: background .15s, color .15s; }
[data-testid="stSidebar"] [data-testid="stBaseButton-tertiary"] > div { width: 100%; justify-content: flex-start; gap: 12px; }
[data-testid="stSidebar"] [data-testid="stBaseButton-tertiary"]:hover { background: color-mix(in oklab, var(--c-side-2) 60%, transparent); color: var(--c-side-fg); }
[data-testid="stSidebar"] [data-testid="stBaseButton-tertiary"] p { font-size: 13.5px; }
[data-testid="stSidebar"] [data-testid="stBaseButton-tertiary"] [data-testid="stIconMaterial"] { font-size: 18px; }
[data-testid="stSidebar"] .st-key-nav_new { margin-bottom: 18px; }
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] { background-color: var(--c-ink-btn); color: var(--c-ink-btn-fg); border: 0; font-weight: 600; padding: 10px 12px;
  background-image: linear-gradient(180deg, rgba(255,255,255,.18), rgba(255,255,255,0) 55%); box-shadow: inset 0 1px 0 rgba(255,255,255,.2), 0 1px 2px rgba(0,0,0,.3); }
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"]:hover { filter: brightness(1.07); background-color: var(--c-ink-btn); color: var(--c-ink-btn-fg); }
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] p { font-size: 14px; }
[class*="st-key-recent_"] [data-testid="stBaseButton-tertiary"] { padding: 6px 8px; }
[class*="st-key-recent_"] p { font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 12.5px !important; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
[class*="st-key-recent_"] [data-testid="stIconMaterial"] { font-size: 8px !important; width: 8px; }
[class*="st-key-recent_"] [data-testid="stBaseButton-tertiary"] > div { gap: 10px; }
.st-key-side_foot { margin-top: auto; position: sticky; bottom: 0; z-index: 2; background: var(--c-side); border-top: 1px solid var(--c-side-line); padding: 10px 0 12px; gap: 2px !important; }
.st-key-side_foot [data-testid="stPopover"] button, .st-key-side_foot [data-testid="stPopoverButton"] { width: 100%; justify-content: flex-start; background: transparent; border: 0;
  color: var(--c-side-muted); padding: 8px 8px; box-shadow: none; }
.st-key-side_foot [data-testid="stPopoverButton"]:hover { background: var(--c-side-2); color: var(--c-side-fg); }
.st-key-side_foot [data-testid="stPopoverButton"] > div { width: 100%; justify-content: flex-start; }
.st-key-side_foot [data-testid="stPopoverButton"] [data-testid="stMarkdownContainer"] { flex: 1; text-align: left; }
.st-key-side_foot [data-testid="stPopoverButton"] p { font-size: 12.5px; }
.side-brand { display: flex; align-items: center; gap: 12px; height: 40px; padding: 0 4px; margin: 6px 0 18px; }
.side-logo { display: flex; width: 36px; height: 36px; align-items: center; justify-content: center; border-radius: 9px; background: var(--c-side-2); color: var(--c-side-accent);
  box-shadow: inset 0 0 0 1px var(--c-side-line); flex-shrink: 0; transition: transform .2s; }
.side-brand:hover .side-logo { transform: rotate(-8deg); }
.side-logo .ico { width: 20px; height: 20px; }
.side-label { font-size: 11px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; color: color-mix(in oklab, var(--c-side-muted) 80%, transparent); margin: 0 8px 6px; }
.side-label.gap { margin-top: 24px; }
.side-status { display: flex; align-items: center; gap: 10px; padding: 8px; border-radius: 8px; transition: background .15s; }
.side-status:hover { background: var(--c-side-2); }
.side-status .t { font-size: 12.5px; font-weight: 500; color: var(--c-side-fg); line-height: 1.25; }
.side-status .s { font-family: "JetBrains Mono", monospace; font-size: 10.5px; color: var(--c-side-muted); line-height: 1.3; }

/* ------------------------------------------------------------------ surfaces */
[class*="st-key-pnl_"] { background: var(--c-surface); border: 1px solid var(--c-line) !important; border-radius: 14px !important; padding: 18px 20px 20px !important; gap: .8rem !important;
  box-shadow: 0 1px 0 color-mix(in oklab, var(--c-line-strong) 50%, transparent), 0 10px 28px -18px var(--c-shadow); }
[class*="st-key-pnl_"] [class*="st-key-pnl_"] { box-shadow: none; background: var(--c-sunken); }
.panel-head { display: flex; align-items: center; gap: 12px; margin: -18px -20px 4px; padding: 12px 20px; border-bottom: 1px solid var(--c-line); }
.panel-head .t { font-size: 13.5px; font-weight: 600; letter-spacing: -.01em; color: var(--c-fg); }
.panel-head .s { font-size: 12px; color: var(--c-fg-faint); }
.panel-head .x { margin-left: auto; display: flex; align-items: center; gap: 8px; }
.panel-head.bare { margin: 0 0 2px; padding: 0; border: 0; }
[data-testid="stExpander"] details { background: var(--c-surface); border: 1px solid var(--c-line); border-radius: 12px; }
[data-testid="stExpander"] summary { padding: 10px 14px; }
[data-testid="stExpander"] summary:hover { color: var(--c-accent); }
[data-testid="stPopoverBody"] { background: var(--c-surface) !important; border: 1px solid var(--c-line) !important; border-radius: 12px !important; box-shadow: 0 24px 48px -20px var(--c-shadow) !important; }
div[role="dialog"] { background: var(--c-surface) !important; border: 1px solid var(--c-line); border-radius: 16px !important; }
[data-testid="stToast"] { background: var(--c-surface); border: 1px solid var(--c-line-strong); color: var(--c-fg); border-radius: 12px; box-shadow: 0 20px 40px -20px var(--c-shadow); }
[data-testid="stAlert"] { border-radius: 12px; }
[data-testid="stCode"] pre, .stCodeBlock pre { background: var(--c-sunken) !important; border: 1px solid var(--c-line); border-radius: 12px; }
[data-testid="stDataFrame"], [data-testid="stDataEditor"], [data-testid="stTable"] { border: 1px solid var(--c-line); border-radius: 12px; overflow: hidden; }
[data-testid="stFileUploaderDropzone"] { background: var(--c-sunken) !important; border: 1.5px dashed var(--c-line-strong) !important; border-radius: 12px !important; padding: 26px 20px !important; }
[data-testid="stFileUploaderDropzone"]:hover { border-color: var(--c-accent) !important; background: var(--c-accent-soft) !important; }
[data-testid="stStatusWidget"], [data-testid="stStatus"] { border-radius: 12px; }
[data-testid="stExpander"]:has([data-testid="stStatus"]) details, [data-testid="stStatus"] details { background: var(--c-side); color: var(--c-side-fg); border-color: var(--c-side); }

/* ------------------------------------------------------------------ form controls */
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label { font-size: 12px !important; font-weight: 500; color: var(--c-fg-muted); }
[data-testid="stTextInputRootElement"], [data-testid="stTextAreaRootElement"], [data-testid="stNumberInputContainer"], [data-testid="stSelectbox"] [data-testid="stWidgetLabel"] + div > div,
[data-testid="stMultiSelect"] [data-testid="stWidgetLabel"] + div > div, .stTextInput [data-baseweb="input"], .stTextArea [data-baseweb="textarea"], .stSelectbox [data-baseweb="select"] > div {
  background: var(--c-sunken) !important; border: 1px solid color-mix(in oklab, var(--c-line-strong) 70%, transparent) !important; border-radius: 8px !important;
  box-shadow: inset 0 1px 0 var(--c-line); transition: border-color .15s, box-shadow .15s, background .15s; }
[data-testid="stTextInputRootElement"]:focus-within, [data-testid="stTextAreaRootElement"]:focus-within, [data-testid="stNumberInputContainer"]:focus-within,
[data-testid="stSelectbox"] [data-testid="stWidgetLabel"] + div > div:focus-within, [data-testid="stMultiSelect"] [data-testid="stWidgetLabel"] + div > div:focus-within {
  border-color: var(--c-accent) !important; background: var(--c-surface) !important; box-shadow: 0 0 0 4px color-mix(in oklab, var(--c-accent) 15%, transparent); }
.stTextInput input, .stNumberInput input, .stTextArea textarea, [data-baseweb="base-input"] { background: transparent !important; color: var(--c-fg); font-size: 13.5px; }
.stTextInput input::placeholder, .stTextArea textarea::placeholder { color: var(--c-fg-faint); }
[data-baseweb="popover"] ul, [data-baseweb="menu"] { background: var(--c-surface) !important; }
[data-baseweb="popover"] li[aria-selected="true"] { background: var(--c-surface-2) !important; }
.mono-input textarea, .st-key-paste_text textarea, .st-key-raw_editor textarea, .st-key-kn_answer textarea, .st-key-kn_paste textarea { font-family: "JetBrains Mono", ui-monospace, monospace !important; font-size: 12.5px !important; line-height: 1.6; }

/* buttons, React variants: primary = accent with a top sheen, secondary = outline, tertiary = ghost */
[data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"] { background-color: var(--c-accent); color: var(--c-on-accent); border: 0; font-weight: 600; border-radius: 8px;
  background-image: linear-gradient(180deg, rgba(255,255,255,.16), rgba(255,255,255,0) 55%);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.18), inset 0 -1px 0 rgba(0,0,0,.18), 0 1px 2px rgba(0,0,0,.18); }
[data-testid="stBaseButton-primary"]:hover { background-color: var(--c-accent-strong); color: var(--c-on-accent); border: 0; }
[data-testid="stBaseButton-primary"]:active { transform: translateY(1px); }
[data-testid="stBaseButton-secondary"], [data-testid="stDownloadButton"] button, [data-testid="stPopoverButton"] { background: var(--c-surface); border: 1px solid var(--c-line-strong);
  color: var(--c-fg); font-weight: 500; border-radius: 8px; box-shadow: 0 1px 0 var(--c-line); }
[data-testid="stBaseButton-secondary"]:hover, [data-testid="stDownloadButton"] button:hover, [data-testid="stPopoverButton"]:hover { border-color: var(--c-fg-faint); background: var(--c-surface-2); color: var(--c-fg); }
[data-testid="stBaseButton-secondary"]:focus:not(:active), [data-testid="stPopoverButton"]:focus:not(:active) { border-color: var(--c-line-strong); color: var(--c-fg); }
[data-testid="stBaseButton-tertiary"] { color: var(--c-fg-muted); font-weight: 500; border-radius: 8px; padding: 6px 10px; }
[data-testid="stBaseButton-tertiary"]:hover { background: var(--c-surface-2); color: var(--c-fg); }
button p, [data-testid="stDownloadButton"] p { white-space: nowrap; font-size: 13px; }
[data-testid="stBaseButton-primary"] p, [data-testid="stBaseButton-secondary"] p { font-size: 13px; }
button:disabled { opacity: .5; }
[role="radiogroup"]:has(> button[data-variant="segmented_control"]) { background: var(--c-surface-2); border: 1px solid var(--c-line); border-radius: 8px; padding: 3px; gap: 3px; }
button[data-variant="segmented_control"] { border: 0 !important; border-radius: 6px !important; background: transparent !important; color: var(--c-fg-muted) !important;
  font-weight: 500; padding: 5px 12px; box-shadow: none !important; min-height: 30px; }
button[data-variant="segmented_control"]:hover { color: var(--c-fg) !important; }
button[data-variant="segmented_control"][aria-checked="true"] { background: var(--c-surface) !important; color: var(--c-fg) !important;
  box-shadow: 0 1px 2px var(--c-shadow), 0 0 0 1px var(--c-line-strong) !important; }
button[data-variant="segmented_control"] p { font-size: 13px; }
[data-testid="stButtonGroup"] [data-testid^="stBaseButton-pills"] { border-radius: 99px; }
[data-baseweb="tab-list"] { gap: 4px; border-bottom: 1px solid var(--c-line); }
[data-baseweb="tab"] { font-weight: 500; color: var(--c-fg-muted); }
[data-baseweb="tab"][aria-selected="true"] { color: var(--c-fg); }
[data-testid="stCheckbox"] label p, [data-testid="stToggle"] label p, .stCheckbox p { font-size: 13px; color: var(--c-fg); }
[data-testid="stRadio"] label p { font-size: 13px; }
[data-testid="stCaptionContainer"], .stCaption { color: var(--c-fg-faint) !important; font-size: 11.5px !important; }
[data-testid="stMarkdownContainer"] code { font-family: "JetBrains Mono", monospace; background: var(--c-surface-2); color: var(--c-fg); border-radius: 5px; padding: 1px 5px; }
hr { border-color: var(--c-line) !important; }

/* ------------------------------------------------------------------ page header (bleeds to the content edges, like the React PageHeader) */
.page-head { position: relative; margin: 0 -32px 4px; padding: 40px 32px 30px; border-bottom: 1px solid var(--c-line); overflow: hidden; }
.page-head::before { content: ""; position: absolute; inset: 0; pointer-events: none; opacity: .7;
  background-image: linear-gradient(color-mix(in oklab, var(--c-line) 70%, transparent) 1px, transparent 1px), linear-gradient(90deg, color-mix(in oklab, var(--c-line) 70%, transparent) 1px, transparent 1px);
  background-size: 32px 32px; -webkit-mask-image: linear-gradient(to bottom, black, transparent 95%); mask-image: linear-gradient(to bottom, black, transparent 95%); }
.page-head > * { position: relative; }
.page-head h1 { font-family: Fraunces, Georgia, serif; font-weight: 500; letter-spacing: -.02em; font-size: 38px; line-height: 1.05; margin: 8px 0 0; padding: 0; color: var(--c-fg); }
.page-head p { margin: 12px 0 0; max-width: 720px; color: var(--c-fg-muted); font-size: 15px; line-height: 1.6; }
.page-head .eyebrow { color: var(--c-accent); display: inline-flex; align-items: center; gap: 8px; }
.page-head .eyebrow .ico { width: 14px; height: 14px; }
.page-head.open { border-bottom: 0; padding-bottom: 18px; margin-bottom: 0; }
[data-testid="stLayoutWrapper"]:has(> .st-key-page_tools) { margin: -1rem -32px 6px; width: calc(100% + 64px) !important; max-width: none !important; }
.st-key-page_tools { padding: 0 32px 24px !important; border-bottom: 1px solid var(--c-line); }

/* ------------------------------------------------------------------ project shell */
.st-key-pshell { gap: 0 !important; align-items: stretch !important; flex-wrap: nowrap !important; }
[data-testid="stLayoutWrapper"]:has(> .st-key-prail) { flex: 0 0 248px !important; width: 248px !important; position: sticky; top: 0; height: 100vh; align-self: flex-start; z-index: 5; }
[data-testid="stLayoutWrapper"]:has(> .st-key-pbody) { flex: 1 1 0 !important; min-width: 0 !important; }
.st-key-prail { width: 248px !important; background: var(--c-surface); border-right: 1px solid var(--c-line); position: sticky; top: 0;
  height: 100vh; overflow-y: auto; overflow-x: hidden; gap: 0 !important; padding: 0 !important; }
.st-key-prail > [data-testid="stElementContainer"], .st-key-prail > [data-testid="stLayoutWrapper"] { padding: 0 12px; }
.rail-sec { margin: 0 -12px; padding: 18px 20px; border-bottom: 1px solid var(--c-line); }
.rail-sec.nav { padding: 14px 8px 6px; border: 0; }
.st-key-pbody { min-width: 0 !important; gap: 0 !important; }
.st-key-phead { position: sticky !important; top: 0; z-index: 30; height: 56px !important; min-height: 56px; padding: 0 20px !important; border-bottom: 1px solid var(--c-line); gap: 6px !important; flex-wrap: nowrap !important;
  background: color-mix(in oklab, var(--c-canvas) 82%, transparent); backdrop-filter: saturate(160%) blur(14px); -webkit-backdrop-filter: saturate(160%) blur(14px); }
[data-testid="stLayoutWrapper"]:has(> .st-key-phead) { position: sticky; top: 0; z-index: 30; }
.st-key-phead [data-testid="stBaseButton-tertiary"] { padding: 8px; color: var(--c-fg-muted); }
.st-key-phead [data-testid="stBaseButton-secondary"], .st-key-phead [data-testid="stPopoverButton"], .st-key-phead [data-testid="stBaseButton-primary"] { padding: 4px 10px; min-height: 32px; }
.st-key-phead button p { font-size: 12px !important; }
.st-key-phead [data-testid="stIconMaterial"] { font-size: 16px; }
.st-key-phead > [data-testid="stElementContainer"]:has(.stHtml) { flex: 1 1 0; min-width: 0; }
.st-key-hd_delete [data-testid="stBaseButton-tertiary"]:hover { background: color-mix(in oklab, var(--c-bad) 10%, transparent); color: var(--c-bad); }
.st-key-pcontent { padding: 28px 32px 56px !important; max-width: 1400px; width: 100%; margin: 0 auto; gap: 1.1rem !important; }
.st-key-ct_row { flex-wrap: wrap !important; align-items: flex-start !important; row-gap: 20px !important; }
[data-testid="stLayoutWrapper"]:has(> .st-key-pnl_ct_main) { flex: 1 1 560px !important; min-width: 0 !important; }
[data-testid="stLayoutWrapper"]:has(> .st-key-ct_side) { flex: 1 1 300px !important; max-width: 100%; }
.st-key-ct_side { width: 100% !important; }
[data-testid="stLayoutWrapper"]:has(> .st-key-ct_tools) { margin: -12px -20px 0; width: calc(100% + 40px) !important; max-width: none !important; }
.st-key-ct_tools { padding: 8px 20px !important; background: var(--c-sunken); border-bottom: 1px solid var(--c-line); flex-wrap: wrap !important; }
.st-key-ct_tools > [data-testid="stElementContainer"]:has(.stHtml) { flex: 1 1 160px; min-width: 0; }
.st-key-src_row, .st-key-cv_row { flex-wrap: nowrap !important; align-items: flex-start !important; }
[data-testid="stLayoutWrapper"]:has(> [class*="st-key-flex_"]) { flex: 1 1 0 !important; min-width: 0 !important; }
[data-testid="stLayoutWrapper"]:has(> .st-key-src_main) { flex: 1 1 0 !important; min-width: 0 !important; }
.st-key-src_files [data-testid="stRadio"] label { padding: 4px 6px; border-radius: 6px; }
.st-key-src_files [data-testid="stRadio"] p { font-family: "JetBrains Mono", monospace; font-size: 12px !important; word-break: break-all; }
.st-key-src_bar { flex-wrap: nowrap !important; }
.st-key-src_bar > [data-testid="stElementContainer"]:has(.stHtml) { flex: 1 1 auto; min-width: 0; }
[class*="st-key-sh_"][class*="_row"] { flex-wrap: nowrap !important; margin-bottom: 8px; }
[class*="st-key-sh_"][class*="_row"] > [data-testid="stElementContainer"]:has(.stHtml) { flex: 1 1 0; min-width: 0; }
.st-key-pnl_ov_ready [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; }
.st-key-pnl_ov_ready [data-testid="stHorizontalBlock"] > [data-testid="stElementContainer"] { flex: 0 0 auto !important; width: auto !important; }
.st-key-pnl_ov_ready [data-testid="stHorizontalBlock"] > [data-testid="stLayoutWrapper"] { flex: 1 1 0 !important; min-width: 0; }
.st-key-pnl_ov_ready button { width: fit-content; }
.tree .mono { white-space: nowrap; }
.st-key-pflowbox { padding: 0 !important; gap: 0 !important; }
[class*="st-key-sec_"] [data-testid="stBaseButton-tertiary"] { width: 100%; justify-content: flex-start; padding: 7px 10px; min-height: 0; position: relative; color: var(--c-fg-muted); }
[class*="st-key-sec_"] [data-testid="stBaseButton-tertiary"] > div { width: 100%; justify-content: flex-start; gap: 10px; }
[class*="st-key-sec_"] [data-testid="stIconMaterial"] { color: var(--c-fg-faint); font-size: 17px; }
[class*="st-key-sec_"] p { font-size: 13px !important; }
[class*="st-key-sec_"] [data-testid="stBaseButton-tertiary"]::after { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); border: 1px solid var(--c-line);
  background: var(--c-surface); border-radius: 5px; padding: 0 6px; font: 10.5px/18px "JetBrains Mono", monospace; color: var(--c-fg-faint); }
.st-key-prail [data-testid="stVerticalBlock"] { gap: 1px; }

/* ------------------------------------------------------------------ typography + atoms */
.mono { font-family: "JetBrains Mono", ui-monospace, Menlo, monospace; }
.display { font-family: Fraunces, "Iowan Old Style", Georgia, serif; letter-spacing: -0.02em; font-variation-settings: "SOFT" 30, "WONK" 0; font-weight: 500; }
.eyebrow { font-size: 11px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; }
.tabular { font-variant-numeric: tabular-nums; }
.fg { color: var(--c-fg); } .muted { color: var(--c-fg-muted); } .faint { color: var(--c-fg-faint); } .accent { color: var(--c-accent); }
.ok { color: var(--c-ok); } .warn { color: var(--c-warn); } .bad { color: var(--c-bad); } .info { color: var(--c-info); } .ai { color: var(--c-ai); }
.ink { background-color: var(--c-side); color: var(--c-side-fg); }
.ico { display: inline-block; flex-shrink: 0; background-color: currentColor; vertical-align: -0.18em; }
.grain { position: relative; isolation: isolate; }
.grain::after { content: ""; position: absolute; inset: 0; z-index: -1; pointer-events: none; border-radius: inherit; background-image: NOISE;
  opacity: calc(var(--c-grain) * 2.2); mix-blend-mode: overlay; }
.ink-grid { background-image: linear-gradient(var(--c-side-line) 1px, transparent 1px), linear-gradient(90deg, var(--c-side-line) 1px, transparent 1px); background-size: 44px 44px; }
.line-grid { background-image: linear-gradient(color-mix(in oklab, var(--c-line) 70%, transparent) 1px, transparent 1px), linear-gradient(90deg, color-mix(in oklab, var(--c-line) 70%, transparent) 1px, transparent 1px); background-size: 32px 32px; }
.dot-grid { background-image: radial-gradient(var(--c-grid) 1.1px, transparent 1.1px); background-size: 20px 20px; }
.hatch { background-image: repeating-linear-gradient(135deg, color-mix(in oklab, var(--c-line-strong) 45%, transparent) 0 1px, transparent 1px 7px); }
.card { background: var(--c-surface); border: 1px solid var(--c-line); border-radius: 14px;
  box-shadow: 0 1px 0 color-mix(in oklab, var(--c-line-strong) 50%, transparent), 0 10px 28px -18px var(--c-shadow); }
.card-pad { padding: 20px 22px; }
.card-head { display: flex; align-items: center; gap: 12px; padding: 12px 20px; border-bottom: 1px solid var(--c-line); }
.card-head .t { font-size: 13.5px; font-weight: 600; letter-spacing: -.01em; color: var(--c-fg); }
.card-head .s { font-size: 12px; color: var(--c-fg-faint); }
.icon-tile { display: inline-flex; width: 32px; height: 32px; align-items: center; justify-content: center; border-radius: 8px; border: 1px solid var(--c-line);
  background: var(--c-surface-2); color: var(--c-accent); flex-shrink: 0; }
.icon-tile .ico { width: 16px; height: 16px; }
.lift { transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease; }
.lift:hover { transform: translateY(-2px); border-color: var(--c-line-strong); box-shadow: 0 2px 0 color-mix(in oklab, var(--c-line-strong) 60%, transparent), 0 22px 40px -22px var(--c-shadow); }
.badge { display: inline-flex; align-items: center; gap: 4px; white-space: nowrap; border-radius: 6px; padding: 1px 7px; font-size: 11px; font-weight: 500; line-height: 18px;
  background: var(--c-surface-2); color: var(--c-fg-muted); box-shadow: inset 0 0 0 1px var(--c-line); }
.badge .ico { width: 11px; height: 11px; }
.b-accent { background: var(--c-accent-soft); color: var(--c-accent); box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--c-accent) 25%, transparent); }
.b-ok { background: color-mix(in oklab, var(--c-ok) 11%, transparent); color: var(--c-ok); box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--c-ok) 26%, transparent); }
.b-warn { background: color-mix(in oklab, var(--c-warn) 11%, transparent); color: var(--c-warn); box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--c-warn) 26%, transparent); }
.b-bad { background: color-mix(in oklab, var(--c-bad) 11%, transparent); color: var(--c-bad); box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--c-bad) 26%, transparent); }
.b-info { background: color-mix(in oklab, var(--c-info) 11%, transparent); color: var(--c-info); box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--c-info) 26%, transparent); }
.b-ai { background: color-mix(in oklab, var(--c-ai) 11%, transparent); color: var(--c-ai); box-shadow: inset 0 0 0 1px color-mix(in oklab, var(--c-ai) 26%, transparent); }
.chip { display: inline-flex; align-items: center; gap: 6px; border-radius: 6px; border: 1px solid var(--c-line); background: var(--c-sunken); padding: 2px 8px;
  font-family: "JetBrains Mono", monospace; font-size: 11.5px; color: var(--c-fg-muted); }
.row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.between { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.kpis { display: grid; grid-template-columns: repeat(var(--n, 6), minmax(0, 1fr)); gap: 1px; background: var(--c-line); border: 1px solid var(--c-line); border-radius: 14px; overflow: hidden;
  box-shadow: 0 1px 0 color-mix(in oklab, var(--c-line-strong) 50%, transparent), 0 10px 28px -18px var(--c-shadow); }
.kpis > div { background: var(--c-surface); padding: 16px 20px; min-width: 0; }
.kpis .v { font-size: 24px; font-weight: 600; line-height: 1; letter-spacing: -.01em; color: var(--c-fg); font-variant-numeric: tabular-nums; margin-top: 8px; }
.kpis .l { font-size: 11px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; color: var(--c-fg-faint); }
.kpis .s { font-size: 11.5px; color: var(--c-fg-muted); margin-top: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
@media (max-width: 1100px) { .kpis { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
.bar { height: 6px; border-radius: 99px; background: var(--c-surface-2); overflow: hidden; display: flex; }
.bar > span { display: block; height: 100%; }
.tbl { width: 100%; border-collapse: collapse; font-size: 12.5px; }
.tbl th { text-align: left; font-size: 10.5px; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; color: var(--c-fg-faint); padding: 8px 10px; border-bottom: 1px solid var(--c-line); background: var(--c-surface-2); position: sticky; top: 0; }
.tbl td { padding: 7px 10px; border-bottom: 1px solid color-mix(in oklab, var(--c-line) 70%, transparent); color: var(--c-fg-muted); vertical-align: top; }
.tbl tr:hover td { background: color-mix(in oklab, var(--c-surface-2) 55%, transparent); }
.tbl td.m { font-family: "JetBrains Mono", monospace; color: var(--c-fg); }
.scroll { overflow: auto; }
.callout { display: flex; gap: 10px; align-items: flex-start; border-radius: 12px; padding: 12px 14px; font-size: 12.5px; line-height: 1.5; color: var(--c-fg-muted); border: 1px solid; }
.callout.warn { border-color: color-mix(in oklab, var(--c-warn) 30%, transparent); background: color-mix(in oklab, var(--c-warn) 6%, transparent); }
.callout.info { border-color: color-mix(in oklab, var(--c-info) 30%, transparent); background: color-mix(in oklab, var(--c-info) 6%, transparent); }
.callout.ok { border-color: color-mix(in oklab, var(--c-ok) 30%, transparent); background: color-mix(in oklab, var(--c-ok) 6%, transparent); }
.callout.bad { border-color: color-mix(in oklab, var(--c-bad) 30%, transparent); background: color-mix(in oklab, var(--c-bad) 6%, transparent); }
.callout .ico { width: 16px; height: 16px; flex-shrink: 0; margin-top: 1px; }
.callout.warn > .ico { color: var(--c-warn); } .callout.info > .ico { color: var(--c-info); } .callout.ok > .ico { color: var(--c-ok); } .callout.bad > .ico { color: var(--c-bad); }
.empty { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; border-radius: 14px; border: 1px dashed var(--c-line-strong); padding: 40px;
  text-align: center; font-size: 13.5px; color: var(--c-fg-muted); }
.empty .tile { display: flex; width: 48px; height: 48px; align-items: center; justify-content: center; border-radius: 12px; border: 1px solid var(--c-line); background: var(--c-surface);
  color: var(--c-accent); box-shadow: 0 10px 28px -18px var(--c-shadow); }
.steps { list-style: none; margin: 0 !important; padding: 0 !important; }
.steps li { position: relative; display: flex; gap: 12px; padding: 0 0 12px !important; margin: 0 !important; }
.steps li:last-child { padding-bottom: 0 !important; }
.steps li:not(:last-child)::before { content: ""; position: absolute; left: 10px; top: 24px; bottom: 2px; width: 1px; background: var(--c-line-strong); }
.steps li.done:not(:last-child)::before { background: var(--c-accent); }
.dot { position: relative; z-index: 1; display: inline-flex; width: 21px; height: 21px; flex-shrink: 0; align-items: center; justify-content: center; border-radius: 99px;
  border: 1px solid var(--c-line-strong); background: var(--c-surface); color: var(--c-fg-faint); font-size: 10px; font-weight: 600; font-family: "JetBrains Mono", monospace; }
.done .dot { background: var(--c-accent); border-color: var(--c-accent); color: var(--c-on-accent); }
.dot .ico { width: 12px; height: 12px; }
.pipe-steps { list-style: none; margin: 0 !important; padding: 0 !important; }
.pipe-steps li { position: relative; display: flex; align-items: center; gap: 12px; padding: 0 0 10px !important; margin: 0 !important; }
.pipe-steps li:last-child { padding-bottom: 0 !important; }
.pipe-steps li:not(:last-child)::before { content: ""; position: absolute; left: 9px; top: 21px; height: calc(100% - 19px); width: 1px; background: var(--c-line-strong); }
.pipe-steps li.done:not(:last-child)::before { background: var(--c-accent); }
.pipe-steps .dot { width: 19px; height: 19px; font-size: 9px; }
.pipe-steps .l { flex: 1; min-width: 0; display: flex; align-items: baseline; justify-content: space-between; gap: 8px; }
.pipe-steps .l b { font-size: 12.5px; font-weight: 500; color: var(--c-fg-muted); }
.pipe-steps li.done .l b { color: var(--c-fg); }
.pipe-steps .l span { font-size: 10.5px; color: var(--c-fg-faint); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.marquee-wrap { overflow: hidden; border-block: 1px solid var(--c-line); background: color-mix(in oklab, var(--c-surface) 60%, transparent); padding: 10px 0;
  -webkit-mask-image: linear-gradient(90deg, transparent, black 8%, black 92%, transparent); margin: 8px -32px 0; }
.marquee { display: flex; width: max-content; gap: 10px; animation: marquee 38s linear infinite; }
@keyframes marquee { from { transform: translateX(0); } to { transform: translateX(-50%); } }
@keyframes fadeup { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
@keyframes fadein { from { opacity: 0; } to { opacity: 1; } }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes ping { 75%, 100% { transform: scale(2); opacity: 0; } }
.fade-up { animation: fadeup .5s cubic-bezier(.2,.7,.2,1) both; }
.console-line { opacity: 0; animation: fadein .35s ease forwards; }
.ping { position: absolute; inset: 0; border-radius: 99px; background: color-mix(in oklab, var(--c-ok) 60%, transparent); animation: ping 1.6s cubic-bezier(0,0,.2,1) infinite; }
.code-view { font-family: "JetBrains Mono", ui-monospace, monospace; font-size: 12px; line-height: 1.6; background: var(--c-sunken); border: 1px solid var(--c-line);
  border-radius: 12px; overflow: auto; max-height: calc(100vh - 230px); min-height: 420px; }
.code-view table { border-collapse: collapse; width: 100%; }
.code-view td { padding: 0 12px 0 0; white-space: pre; color: var(--c-fg); vertical-align: top; }
.code-view td.n { width: 1%; padding: 0 12px 0 14px; text-align: right; color: var(--c-fg-faint); user-select: none; border-right: 1px solid var(--c-line); }
.code-view tr.sl td { background: color-mix(in oklab, var(--c-accent) 10%, transparent); }
.code-view tr.sl td.n { box-shadow: inset 3px 0 0 var(--c-accent); color: var(--c-accent); }
.code-view tr.hl td { background: color-mix(in oklab, var(--c-warn) 24%, transparent); }
.code-view .kw { color: var(--c-accent); font-weight: 600; } .code-view .str { color: var(--c-ok); } .code-view .cm { color: var(--c-fg-faint); font-style: italic; }
.code-view .num { color: var(--c-warn); }
.pre { font-family: "JetBrains Mono", monospace; font-size: 11.5px; line-height: 1.6; white-space: pre-wrap; word-break: break-word; background: var(--c-sunken);
  border: 1px solid var(--c-line); border-radius: 10px; padding: 10px 12px; color: var(--c-fg); max-height: 300px; overflow: auto; margin: 0; }
.prompt-box { font-family: "JetBrains Mono", monospace; font-size: 11.5px; line-height: 1.6; white-space: pre-wrap; background: var(--c-side); color: var(--c-side-fg);
  border-radius: 12px; padding: 14px 16px; height: 300px; overflow: auto; margin: 0; }
.lib-step { display: inline-flex; width: 28px; height: 28px; align-items: center; justify-content: center; border-radius: 8px; background: var(--c-side); color: var(--c-side-fg);
  font-family: "JetBrains Mono", monospace; font-size: 12px; font-weight: 600; flex-shrink: 0; }
a.plain { color: inherit !important; text-decoration: none !important; }
a.plain:hover { color: var(--c-accent) !important; }
.tcb-link { color: var(--c-accent) !important; text-decoration: none !important; font-weight: 500; cursor: pointer; }
.tcb-link:hover { text-decoration: underline !important; }
.stHtml a { text-decoration: none; }
"""

COMPACT_CSS = """
section[data-testid="stSidebar"] { width: 68px !important; min-width: 68px !important; max-width: 68px !important; }
[data-testid="stSidebarUserContent"] { padding: 14px 10px 0 !important; }
.side-brand { justify-content: center; padding: 0; }
.side-brand .txt, .side-label, .side-status .txt, [class*="st-key-recent_"] { display: none !important; }
.side-status { justify-content: center; }
[data-testid="stSidebar"] button [data-testid="stMarkdownContainer"] { display: none; }
[data-testid="stSidebar"] [data-testid="stBaseButton-tertiary"], [data-testid="stSidebar"] [data-testid="stBaseButton-primary"],
.st-key-side_foot [data-testid="stPopoverButton"] { justify-content: center !important; padding-left: 0 !important; padding-right: 0 !important; height: 40px; }
[data-testid="stSidebar"] button > div { justify-content: center !important; gap: 0 !important; }
[data-testid="stSidebar"] .st-key-nav_new { margin-bottom: 22px; }
.st-key-side_foot [data-testid="stPopoverButton"] svg, .st-key-side_foot [data-testid="stPopoverButton"] [data-testid="stIconMaterial"] { display: none; }
"""

PROJECT_CSS = """
[data-testid="stMainBlockContainer"] { max-width: none !important; padding: 0 !important; }
[data-testid="stMainBlockContainer"] > div > [data-testid="stVerticalBlock"] { gap: 0 !important; }
"""


def css(t: Theme, compact: bool = False, project: bool = False) -> str:
    root = ";".join(f"--c-{k}:{v}" for k, v in t.vars.items())
    body = SHELL_CSS.replace("PAPER", PAPER).replace("NOISE", NOISE)
    return f"<style>:root{{{root}}}{body}{COMPACT_CSS if compact else ''}{PROJECT_CSS if project else ''}</style>"
