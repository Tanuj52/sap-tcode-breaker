"""Client for the Node.js abaplint parser bridge."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass

from ..config import get_settings
from .ast import Statement, build_statements


class ParserError(RuntimeError):
    pass


@dataclass
class ParsedProgram:
    name: str
    statements: list[Statement]
    error: str | None = None
    abaplint_version: str = ""

    @property
    def unknown_statements(self) -> list[Statement]:
        return [s for s in self.statements if s.type in ("Unknown", "NativeSQL")]


def parse_sources(sources: list[tuple[str, str]], version: str | None = None) -> list[ParsedProgram]:
    """Parse several (name, source) pairs in one bridge call."""
    settings = get_settings()
    if not sources:
        return []
    node = shutil.which(settings.node_bin) or settings.node_bin
    if not settings.parser_bridge.exists():
        raise ParserError(f"Parser bridge not found at {settings.parser_bridge}. Run `npm install` in parser-bridge/.")
    payload = json.dumps({"version": version or settings.abap_version, "programs": [{"name": n, "source": s} for n, s in sources]})
    try:
        proc = subprocess.run(
            [node, str(settings.parser_bridge)],
            input=payload,
            capture_output=True,
            text=True,
            timeout=settings.parser_timeout_s,
            check=False,
        )
    except FileNotFoundError as exc:
        raise ParserError(f"Node.js executable not found ({settings.node_bin}). Install Node 18+.") from exc
    except subprocess.TimeoutExpired as exc:
        raise ParserError(f"Parser timed out after {settings.parser_timeout_s}s") from exc
    if proc.returncode != 0:
        raise ParserError(f"Parser bridge failed: {proc.stderr.strip()[:2000]}")
    data = json.loads(proc.stdout)
    out = []
    for p in data.get("programs", []):
        out.append(
            ParsedProgram(
                name=p.get("name", ""),
                statements=build_statements(p.get("statements", [])),
                error=p.get("error"),
                abaplint_version=data.get("abaplint_version", ""),
            )
        )
    return out


def parse_source(name: str, source: str, version: str | None = None) -> ParsedProgram:
    return parse_sources([(name, source)], version)[0]
