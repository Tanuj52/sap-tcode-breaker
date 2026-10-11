"""Execution-based comparison of generated SQL against a reference (gold) query."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class CompareResult:
    ok: bool
    generated_rows: int | None = None
    expected_rows: int | None = None
    missing: int | None = None  # rows in expected but not generated
    extra: int | None = None  # rows in generated but not expected
    error: str | None = None
    sample_missing: list[tuple] | None = None
    sample_extra: list[tuple] | None = None


def strip_select(sql: str) -> str:
    """Remove comments, trailing ';' and the final ORDER BY so the query can be used as a subquery."""
    body = "\n".join(line for line in sql.splitlines() if not line.strip().startswith("--"))
    body = body.strip().rstrip(";").strip()
    body = re.sub(r"^CREATE\s+(OR\s+REPLACE\s+)?(SECURE\s+)?VIEW\s+\S+\s+AS\s+", "", body, flags=re.I)
    m = re.search(r"\nORDER BY [^\n]+$", body)
    if m:
        body = body[: m.start()]
    return body


def compare(cursor, generated_sql: str, expected_sql: str, schema: str | None = None) -> CompareResult:
    gen = strip_select(generated_sql)
    exp = strip_select(expected_sql)
    try:
        if schema:
            cursor.execute(f"USE SCHEMA {schema}")
        cursor.execute(f"SELECT COUNT(*) FROM ({gen})")
        n_gen = cursor.fetchone()[0]
        cursor.execute(f"SELECT COUNT(*) FROM ({exp})")
        n_exp = cursor.fetchone()[0]
        cursor.execute(f"SELECT * FROM (({exp}) MINUS ({gen})) LIMIT 5")
        miss_rows = cursor.fetchall()
        cursor.execute(f"SELECT COUNT(*) FROM (({exp}) MINUS ({gen}))")
        missing = cursor.fetchone()[0]
        cursor.execute(f"SELECT * FROM (({gen}) MINUS ({exp})) LIMIT 5")
        extra_rows = cursor.fetchall()
        cursor.execute(f"SELECT COUNT(*) FROM (({gen}) MINUS ({exp}))")
        extra = cursor.fetchone()[0]
    except Exception as exc:  # noqa: BLE001 - report any SQL error as a failed comparison
        return CompareResult(False, error=str(exc).splitlines()[0][:500])
    ok = missing == 0 and extra == 0 and n_gen == n_exp
    return CompareResult(ok, generated_rows=n_gen, expected_rows=n_exp, missing=missing, extra=extra,
                         sample_missing=[tuple(str(v) for v in r) for r in miss_rows],
                         sample_extra=[tuple(str(v) for v in r) for r in extra_rows])
