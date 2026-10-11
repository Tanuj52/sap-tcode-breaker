"""Thin Snowflake access layer.

The connection comes from the app settings (UI): a named connection from
~/.snowflake/connections.toml, or custom parameters. TCB_SNOWFLAKE_CONNECTION is the fallback.
"""

from __future__ import annotations

import json
import os
import threading
from contextlib import contextmanager
from typing import Any, Iterator

from .config import get_settings

_lock = threading.Lock()
_conn = None
_conn_sig: str | None = None
os.environ.setdefault("SF_SKIP_TOKEN_FILE_PERMISSIONS_VERIFICATION", "true")


SESSION_TOKEN = "/snowflake/session/token"


def in_snowflake() -> bool:
    """True inside Snowpark Container Services / Streamlit container runtime, where Snowflake mounts a login token."""
    return os.path.exists(SESSION_TOKEN) and bool(os.environ.get("SNOWFLAKE_HOST"))


def session_kwargs(warehouse: str = "", role: str = "") -> dict[str, Any]:
    with open(SESSION_TOKEN, encoding="utf-8") as fh:
        token = fh.read().strip()
    kw: dict[str, Any] = {"host": os.environ["SNOWFLAKE_HOST"], "account": os.environ.get("SNOWFLAKE_ACCOUNT", ""),
                          "authenticator": "oauth", "token": token}
    if os.environ.get("SNOWFLAKE_PORT"):
        kw["port"] = os.environ["SNOWFLAKE_PORT"]
    for key, env in (("database", "SNOWFLAKE_DATABASE"), ("schema", "SNOWFLAKE_SCHEMA")):
        if os.environ.get(env):
            kw[key] = os.environ[env]
    wh = warehouse or os.environ.get("SNOWFLAKE_WAREHOUSE") or os.environ.get("TCB_WAREHOUSE")
    if wh:
        kw["warehouse"] = wh
    if role:
        kw["role"] = role
    return kw


def connect_kwargs() -> dict[str, Any]:
    from . import app_settings

    s = app_settings.load().snowflake
    if s.mode == "none":
        return {}
    if s.mode == "session" or (s.mode == "named" and not (s.connection_name or get_settings().snowflake_connection) and in_snowflake()):
        if not in_snowflake():
            raise RuntimeError("No Snowflake session token here: this mode only works when the app runs inside Snowflake.")
        return session_kwargs(s.custom.warehouse, s.custom.role)
    if s.mode == "custom" and s.custom.account:
        c = s.custom
        kw: dict[str, Any] = {"account": c.account, "user": c.user, "authenticator": c.authenticator or "snowflake"}
        if c.authenticator in ("programmatic_access_token", "oauth") and c.token:
            kw["token"] = c.token
        elif c.authenticator == "snowflake_jwt" and c.private_key_file:
            kw["private_key_file"] = c.private_key_file
            if c.private_key_passphrase:
                kw["private_key_file_pwd"] = c.private_key_passphrase
        elif c.password:
            kw["password"] = c.password
        for k in ("role", "warehouse", "database"):
            if getattr(c, k):
                kw[k] = getattr(c, k)
        if c.schema_:
            kw["schema"] = c.schema_
        return kw
    name = s.connection_name or get_settings().snowflake_connection
    return {"connection_name": name} if name else {}


def reset() -> None:
    """Drop the cached connection (after the settings changed)."""
    global _conn, _conn_sig
    with _lock:
        if _conn is not None:
            try:
                _conn.close()
            except Exception:  # noqa: BLE001
                pass
        _conn, _conn_sig = None, None


def get_connection(connection_name: str | None = None):
    """Return a shared connection (lazy, re-created when the settings change)."""
    global _conn, _conn_sig
    import snowflake.connector  # imported lazily: analysis works without Snowflake

    kwargs = {"connection_name": connection_name} if connection_name else connect_kwargs()
    if not kwargs:
        raise RuntimeError("No Snowflake connection configured. Open Settings and choose a connection.")
    sig = json.dumps(kwargs, sort_keys=True, default=str)
    with _lock:
        if _conn is None or _conn.is_closed() or sig != _conn_sig:
            if _conn is not None:
                try:
                    _conn.close()
                except Exception:  # noqa: BLE001
                    pass
            _conn = snowflake.connector.connect(login_timeout=30, **kwargs)
            _conn_sig = sig
        return _conn


def test_connection(kwargs: dict[str, Any] | None = None) -> dict:
    """Open a connection (the configured one or `kwargs`) and report who/where we are."""
    import snowflake.connector

    conn = snowflake.connector.connect(login_timeout=30, **kwargs) if kwargs else get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_REGION(), CURRENT_VERSION()")
        acc, user, role, wh, region, ver = cur.fetchone()
        return {"ok": True, "account": acc, "user": user, "role": role, "warehouse": wh, "region": region, "version": ver}
    finally:
        if kwargs:
            conn.close()


@contextmanager
def cursor(connection_name: str | None = None) -> Iterator[Any]:
    cur = get_connection(connection_name).cursor()
    try:
        yield cur
    finally:
        cur.close()


def execute(sql: str, params: Any = None) -> list[tuple]:
    with cursor() as cur:
        cur.execute(sql, params)
        try:
            return cur.fetchall()
        except Exception:  # noqa: BLE001 - DDL statements have no result set
            return []


def query_dicts(sql: str, params: Any = None) -> tuple[list[str], list[dict]]:
    with cursor() as cur:
        cur.execute(sql, params)
        cols = [d[0] for d in cur.description or []]
        return cols, [dict(zip(cols, row)) for row in cur.fetchall()]


def available() -> bool:
    try:
        execute("SELECT 1")
        return True
    except Exception:  # noqa: BLE001
        return False
