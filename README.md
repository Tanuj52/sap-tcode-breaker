# T-code Breaker (Streamlit)

Converts ABAP report programs into Snowflake SQL: analysis, data flow, call tree, context review,
conversion (rules first, a model only for unresolved steps), validation against Snowflake, and a
knowledge library for tables and function modules. Same features as the React app, in one folder.

```
streamlit_app.py        entry point, sidebar and router
frontend/               theme, shared UI pieces, pages, project workspace, data-flow canvas, knowledge pages, user guide
backend/core.py         service layer used by the UI
backend/knowledge.py    knowledge library operations
backend/tcode_breaker/  conversion engine
backend/abap_parser.js  ABAP parser (abaplint, bundled; runs on Node)
backend/samples/        sample programs and reference SQL
data/                   projects, settings and your library (created on first run)
```

The in-app **User guide** (sidebar) walks through setup and every module; Home shows a
getting-started checklist that ticks itself off as you connect, set layers and convert.

## Run locally

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/streamlit run streamlit_app.py
```

Then open Settings → Snowflake connection → *New connection* and enter the account identifier, user
and sign-in (password, programmatic access token, key pair or OAuth token; browser SSO works when the
app runs on your own machine). The app keeps exactly one connection: *Edit* changes it, *New
connection* replaces it, *Remove connection* deletes it and its saved secrets. Secrets are stored in
`data/app_settings.json` (owner-only) and never shown again. If an older setup points at a profile in
`~/.snowflake/connections.toml`, that profile is shown as the active connection until you replace or
remove it; the app never lists the other profiles. A system `node` is used when present; otherwise the
one from the `nodejs-wheel-binaries` package.

On a fresh account, open Samples → *Set up demo data* once to create `TCODE_BREAKER.SAP_DEMO`
(synthetic SFLIGHT / SD / MM data) so the samples can be compiled and compared row by row.
Validation creates its stub tables in `TCODE_BREAKER.STUBS` by default (Settings → Conversion).

## Deploy to Snowflake

Use the **container runtime** (Streamlit in Snowflake on a compute pool, or a Snowpark Container
Services service). Upload the whole folder; dependencies come from `requirements.txt`, including
Node through `nodejs-wheel-binaries`. Inside Snowflake, the app signs in with the session token the
platform mounts, so no credentials are needed: the connection page shows *Snowflake session* as the
active connection, where you can set the warehouse and role.
The container needs an external access integration for PyPI during build, and for any external
model provider you configure (Cortex models need none).

The **warehouse runtime** is not supported: it has no Node runtime for the ABAP parser and only
installs packages from the Snowflake Anaconda channel.

Projects and the library are stored under `data/`. In a container that directory is reset when the
service restarts; export the library (Knowledge → Export) or mount a stage volume to keep it.

## Deploy to Streamlit Community Cloud

At share.streamlit.io choose *Create app* → this repo, branch `main`, main file `streamlit_app.py`,
and Python 3.12 or 3.13 under *Advanced settings*. Node comes from `nodejs-wheel-binaries`, so no
system packages are needed. After it starts, open Settings → *New connection* and sign in with a
programmatic access token or key pair (browser SSO needs a local browser, and password sign-in may
be blocked by MFA). If the account has a network policy, it must allow Community Cloud's egress IPs.

Keep in mind:

- The app holds one connection for everyone who opens it. On a public app any visitor can run work
  through it, edit it or remove it. Limit viewers under the app's *Sharing* settings, or use a
  Snowflake user and role that only reach the demo and stub schemas.
- `data/` (projects, the saved connection, your library) lives on the app's disk and is lost when
  the app reboots or redeploys. Export the library before redeploying.
- `data/` is git-ignored, so local projects and secrets never reach the repo.

## Notes on the UI

The data-flow map is a Streamlit custom component (v2, inline HTML/CSS/JS, no build step): scroll to
zoom, drag to pan, +/−/fit controls, per-node or all-column expansion, a node detail panel, and
PNG/SVG export of the current layout. Links inside the app (cards, breadcrumbs, jump-to-line) are
handled by a small hidden component so they navigate within the session instead of reloading the page.
Both use custom components v2; the app is tested on Streamlit 1.65, which `requirements.txt` requires.
