"""Lightweight navigable view over the abaplint JSON tree."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator

# Tokens that bind tightly to their neighbours when rendering text (no surrounding spaces).
_TIGHT = {"-", "~", "->", "=>", "(", ")"}


class Node:
    """Expression or token node. Tokens have `value`; expressions have `type` and `children`."""

    __slots__ = ("type", "value", "children", "row", "col", "token_type")

    def __init__(self, raw: dict) -> None:
        if "v" in raw:
            self.type = "Token"
            self.value: str | None = raw["v"]
            self.token_type: str | None = raw.get("tt")
            self.row: int = raw.get("r", 0)
            self.col: int = raw.get("c", 0)
            self.children: list[Node] = []
        else:
            self.type = raw.get("e", "")
            self.value = None
            self.token_type = None
            self.children = [Node(c) for c in raw.get("ch", [])]
            first = self.first_token()
            self.row = first.row if first else 0
            self.col = first.col if first else 0

    # ------------------------------------------------------------------ navigation
    @property
    def is_token(self) -> bool:
        return self.value is not None

    def tokens(self) -> list["Node"]:
        if self.is_token:
            return [self]
        out: list[Node] = []
        for c in self.children:
            out.extend(c.tokens())
        return out

    def first_token(self) -> "Node | None":
        if self.is_token:
            return self
        for c in self.children:
            t = c.first_token()
            if t is not None:
                return t
        return None

    def walk(self) -> Iterator["Node"]:
        yield self
        for c in self.children:
            yield from c.walk()

    def find_all(self, etype: str) -> list["Node"]:
        """All descendants (excluding self) of the given expression type, depth-first, outermost first."""
        out: list[Node] = []
        for c in self.children:
            if c.type == etype:
                out.append(c)
            out.extend(c.find_all(etype))
        return out

    def find_all_outer(self, etype: str) -> list["Node"]:
        """Descendants of type etype that are not nested inside another etype."""
        out: list[Node] = []
        for c in self.children:
            if c.type == etype:
                out.append(c)
            else:
                out.extend(c.find_all_outer(etype))
        return out

    def first(self, etype: str) -> "Node | None":
        for c in self.children:
            if c.type == etype:
                return c
            hit = c.first(etype)
            if hit is not None:
                return hit
        return None

    def direct(self, etype: str) -> list["Node"]:
        return [c for c in self.children if c.type == etype]

    def child(self, etype: str) -> "Node | None":
        for c in self.children:
            if c.type == etype:
                return c
        return None

    def keywords(self) -> list[str]:
        """Upper-cased direct token children (keywords at this level)."""
        return [c.value.upper() for c in self.children if c.is_token]

    def has_keyword(self, *words: str) -> bool:
        kws = self.keywords()
        return all(w in kws for w in words)

    def text(self) -> str:
        toks = self.tokens()
        out = ""
        prev = None
        for t in toks:
            v = t.value or ""
            if prev is None:
                out = v
            elif v in _TIGHT or (prev.value in _TIGHT and prev.value not in (")",)):
                # keep "a-b", "a~b", "x->y", "f(" tight; ")" followed by word gets a space
                if v == "(" and prev.value not in ("-", "~", "->", "=>") and _needs_space_before_paren(prev):
                    out += " " + v
                else:
                    out += v
            else:
                out += " " + v
            prev = t
        return out

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Node({self.type}{'=' + repr(self.value) if self.is_token else ''})"


def _needs_space_before_paren(prev: Node) -> bool:
    # ABAP requires "func( x )" without space but keywords like "IN (" with space; we only render text.
    return prev.value is not None and prev.value.upper() in {"IN", "AND", "OR", "NOT", "=", "WHERE", "ON"}


@dataclass
class Statement:
    index: int
    type: str
    row: int
    col: int
    end_row: int
    end_col: int
    text: str
    node: Node
    # filled by analysis
    routine: str | None = None
    block_path: list[int] = field(default_factory=list)
    origin: str = ""  # program / function module the statement belongs to

    @property
    def upper(self) -> str:
        return self.text.upper()

    def tokens(self) -> list[str]:
        return [t.value for t in self.node.tokens() if t.value is not None]

    def first(self, etype: str) -> Node | None:
        return self.node.first(etype)

    def find_all(self, etype: str) -> list[Node]:
        return self.node.find_all(etype)


def build_statements(raw_statements: list[dict]) -> list[Statement]:
    out = []
    for s in raw_statements:
        node = Node({"e": s["t"], "ch": s.get("ch", [])})
        out.append(
            Statement(
                index=s["i"],
                type=s["t"],
                row=s["r"],
                col=s["c"],
                end_row=s["er"],
                end_col=s["ec"],
                text=s["x"],
                node=node,
            )
        )
    return out
