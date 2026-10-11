import streamlit as st

st.set_page_config(page_title="T-code Breaker", page_icon=":material/deployed_code:", layout="wide", initial_sidebar_state="expanded")

from backend import core  # noqa: E402

ready, problem = core.engine_ready()
if not ready:
    st.error(problem)
    st.stop()

from frontend import guide, knowledge, pages, project, theme, ui  # noqa: E402

MODULES = [
    ("", "Home", ":material/home:", "Overview and quick start"),
    ("projects", "Projects", ":material/folder_open:", "All conversions"),
    ("samples", "Samples", ":material/science:", "Bundled programs"),
    ("knowledge", "Knowledge", ":material/local_library:", "Metadata sources"),
    ("settings", "Settings", ":material/settings:", "Connection, models, layers"),
    ("guide", "User guide", ":material/menu_book:", "How to use the app"),
]


def apply_theme(compact: bool, in_project: bool) -> theme.Theme:
    current = theme.get(core.ui_prefs().get("theme"))
    if theme.sync_native(current) and not st.session_state.get("theme_synced"):
        st.session_state.theme_synced = True
        st.rerun()
    st.session_state.theme_synced = True
    st.markdown(theme.css(current, compact, in_project), unsafe_allow_html=True)
    return current


def pick_theme(theme_id: str) -> None:
    core.save_ui_prefs(theme=theme_id)
    theme.sync_native(theme.get(theme_id))


def swatch_css(selector: str, sw: tuple[str, str, str, str], size: int) -> str:
    return (f"{selector}::before{{content:'';flex-shrink:0;width:{size}px;height:{size}px;border-radius:5px;box-shadow:inset 0 0 0 1px rgba(0,0,0,.18);"
            f"background:linear-gradient(180deg,transparent 22%,{sw[1]} 22%,{sw[1]} 52%,transparent 52%) 62% 0/50% 100% no-repeat,"
            f"linear-gradient(90deg,{sw[3]} 38%,{sw[0]} 38%)}}")


def sidebar(active: str, pid: str | None, compact: bool, forced: bool, current: theme.Theme) -> None:
    with st.sidebar:
        ui.html(f'<a class="plain side-brand" href="?" title="T-code Breaker"><span class="side-logo">{ui.icon("logo", 20, 2.1)}</span>'
                '<span class="txt" style="line-height:1.2;min-width:0"><span style="display:block;font-size:15px;font-weight:600;letter-spacing:-.01em;color:var(--c-side-fg)">'
                'T-code Breaker</span><span class="mono" style="display:block;font-size:10.5px;color:var(--c-side-muted)">ABAP → Snowflake SQL</span></span></a>')
        if st.button("New conversion", icon=":material/add:", type="primary", width="stretch", key="nav_new", help="New conversion" if compact else None):
            ui.go("new")
        ui.html('<div class="side-label">Modules</div>')
        for mid, label, ico, hint in MODULES:
            if st.button(label, icon=ico, type="tertiary", width="stretch", key=f"nav_{mid or 'home'}", help=label if compact else hint):
                ui.go(mid)
        rules = []
        if not compact:
            recent = sorted(core.projects(), key=lambda p: p["updated"], reverse=True)[:5]
            if recent:
                ui.html('<div class="side-label gap">Recent</div>')
            for p in recent:
                tone = ui.status_tone((p.get("summary") or {}).get("sql_status") or "pending")
                color = f"var(--c-{tone})" if tone in ("ok", "warn", "bad") else "var(--c-side-muted)"
                if st.button(p["name"], type="tertiary", width="stretch", key=f"recent_{p['id']}", icon=":material/fiber_manual_record:",
                             help=f"{p['workspace']} · {(p.get('summary') or {}).get('sql_status') or p['stage']}"):
                    ui.go("p", pid=p["id"])
                rules.append(f".st-key-recent_{p['id']} [data-testid='stIconMaterial']{{color:{color}}}")
                if pid == p["id"]:
                    rules.append(f".st-key-recent_{p['id']} button{{background:var(--c-side-2)!important;color:var(--c-side-fg)!important}}")
        with st.container(key="side_foot"):
            sf = ui.sf_status()
            dot = "var(--c-ok)" if sf.get("connected") else "var(--c-bad)"
            ping = '<span class="ping"></span>' if sf.get("connected") else ""
            title = ui.esc(sf.get("account")) if sf.get("connected") else "Not connected"
            sub = f"{ui.esc(sf.get('role'))} · {ui.esc(sf.get('warehouse') or 'no warehouse')}" if sf.get("connected") else "Settings → Connection"
            tip = f"{sf.get('account')} · {sf.get('user')} · {sf.get('role')}" if sf.get("connected") else (sf.get("error") or "")
            ui.html(f'<a class="plain side-status" href="?page=settings&section=connection" title="{ui.esc(tip)}"><span style="position:relative;display:flex;width:10px;height:10px;flex-shrink:0">'
                    f'{ping}<span style="position:relative;width:10px;height:10px;border-radius:99px;background:{dot}"></span></span>'
                    f'<span class="txt" style="min-width:0"><span class="t" style="display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{title}</span>'
                    f'<span class="s" style="display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{sub}</span></span></a>')
            with st.popover(current.name, width="stretch", key="theme_pop", help="Theme"):
                ui.html('<div class="eyebrow faint" style="padding:2px 4px 6px">Theme</div>')
                for t in theme.THEMES:
                    if st.button(t.name, key=f"tp_{t.id}", type="tertiary", width="stretch", help=t.tagline):
                        pick_theme(t.id)
                        st.rerun()
                    rules.append(swatch_css(f".st-key-tp_{t.id} button", t.swatch, 26))
                    rules.append(f".st-key-tp_{t.id} button{{justify-content:flex-start;gap:12px;padding:8px 10px}}"
                                 f".st-key-tp_{t.id} button > div{{justify-content:flex-start}}")
                rules.append(f".st-key-tp_{current.id} button{{background:var(--c-surface-2)}}")
            rules.append(swatch_css(".st-key-theme_pop button", current.swatch, 20).replace("::before{", "::before{margin-right:10px;"))
            if not forced:
                if st.button("Expand" if compact else "Collapse", type="tertiary", width="stretch", key="nav_collapse",
                             icon=":material/keyboard_double_arrow_right:" if compact else ":material/keyboard_double_arrow_left:",
                             help="Expand sidebar" if compact else "Collapse sidebar"):
                    core.save_ui_prefs(sidebar="open" if compact else "compact")
                    st.rerun()
    on = f".st-key-nav_{active or 'home'}"
    rules.append(f"{on} button{{position:relative;background:var(--c-side-2)!important;color:var(--c-side-fg)!important}}"
                 f"{on} [data-testid='stIconMaterial']{{color:var(--c-side-accent)}}"
                 f"{on} button::before{{content:'';position:absolute;left:{-10 if compact else -16}px;top:50%;width:3px;height:20px;transform:translateY(-50%);"
                 f"border-radius:0 3px 3px 0;background:var(--c-side-accent)}}")
    st.markdown("<style>" + "".join(rules) + "</style>", unsafe_allow_html=True)


r = ui.route()
page = r.get("page") or ""
pid = r.get("pid")
in_project = page == "p" and bool(pid)
compact = in_project or core.ui_prefs().get("sidebar") == "compact"
current = apply_theme(compact, in_project)
ui.nav_hook()
ui.flush_notifications()
sidebar("projects" if page == "p" else page, pid, compact, in_project, current)

if in_project:
    project.render(pid, r.get("view") or "overview", autorun=r.get("run") == "all")
elif page in ("projects", "p"):
    pages.projects()
elif page == "new":
    pages.new_conversion(r.get("source") or "upload")
elif page == "samples":
    pages.samples()
elif page == "knowledge":
    knowledge.render(r)
elif page == "settings":
    pages.settings(r.get("section") or "connection")
elif page == "guide":
    guide.render()
else:
    pages.home()
