"""Layered, plug-and-play SAP knowledge base.

Resolution order (highest wins):  client packs (in the order given)  ->  your library  ->  built-in base.
Anything not found is reported as UNRESOLVED by callers; nothing is guessed.

The library (data/knowledge/, edited from the Knowledge page) uses the same layout as a pack and is
loaded into every project, so a table or FM added once is known everywhere from then on.

Pack layout (every part optional):

    knowledge-packs/<pack>/
      manifest.yaml                project defaults (source_system, target db/schema, client, ...)
      tables.yaml                  same format as base/sap_tables.yaml
      ddic/DD03L.csv               SE16 export: TABNAME, FIELDNAME, KEYFLAG, DATATYPE, LENG, DECIMALS, REFFIELD [, DDTEXT]
      ddic/DD02L.csv | DD02T.csv   TABNAME [, DDTEXT]
      fm_catalog.yaml              same format as base/fm_catalog.yaml
      s4_mappings.yaml             extra ECC -> S/4 table remaps (same format as base/s4_simplification.yaml)
      function_modules/*.abap      source of custom function modules (FUNCTION ... ENDFUNCTION)
      gold/<program>.abap + .sql   past manual conversions (benchmark + few-shot examples)
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .models import (
    FieldInfo,
    FieldStatus,
    FMInfo,
    fm_from_spec,
    ProjectSettings,
    Provenance,
    S4Mapping,
    TableInfo,
    TypeSpec,
    parse_field_spec,
)

BASE_DIR = Path(__file__).resolve().parent / "base"

_FM_HEADER = re.compile(r"^\s*FUNCTION\s+([A-Za-z0-9_/]+)\s*\.", re.IGNORECASE | re.MULTILINE)


@dataclass
class PackIssue:
    pack: str
    file: str
    message: str
    severity: str = "warning"


@dataclass
class PackSummary:
    name: str
    path: str
    manifest: dict = field(default_factory=dict)
    tables: int = 0
    ddic_fields: int = 0
    function_modules: int = 0
    fm_sources: list[str] = field(default_factory=list)
    gold_pairs: list[str] = field(default_factory=list)
    issues: list[PackIssue] = field(default_factory=list)


@dataclass
class GoldPair:
    name: str
    abap_files: dict[str, str]
    sql: str
    pack: str


class KnowledgeBase:
    def __init__(self) -> None:
        self.tables: dict[str, TableInfo] = {}
        self.fms: dict[str, FMInfo] = {}
        self.methods: dict[str, FMInfo] = {}
        self.fm_sources: dict[str, str] = {}
        self.s4_mappings: list[S4Mapping] = []
        self.field_length_changes: list[dict] = []
        self.types: dict[str, TypeSpec] = {}
        self.abap_types: dict[str, dict] = {}
        self.system_fields: dict[str, dict] = {}
        self.packs: list[PackSummary] = []
        self.library: PackSummary | None = None
        self.gold: list[GoldPair] = []

    # ------------------------------------------------------------------ loading
    @classmethod
    def load(cls, pack_dirs: list[Path] | None = None, library: bool | Path = False) -> "KnowledgeBase":
        """library=True loads the user's library (data/knowledge/) between the built-in base and the packs."""
        kb = cls()
        kb._load_base()
        if library:
            from .library import library_dir

            lib = library_dir() if library is True else Path(library)
            if lib.is_dir():
                kb.library = kb._load_pack(lib, Provenance.LIBRARY, register=False)
        # Later packs override earlier ones; caller passes them in priority order (lowest first).
        for pack_dir in pack_dirs or []:
            kb._load_pack(Path(pack_dir))
        return kb

    def _load_base(self) -> None:
        # sap_tables.yaml (curated core) first, then base/tables/*.yaml (one file per module); the core wins on overlap.
        for path in [BASE_DIR / "sap_tables.yaml", *sorted((BASE_DIR / "tables").glob("*.yaml"))]:
            for name, spec in (_read_yaml(path).get("tables") or {}).items():
                self.tables.setdefault(name.upper(), _table_from_spec(name, spec, Provenance.BUILTIN))

        fm_doc = _read_yaml(BASE_DIR / "fm_catalog.yaml")
        for name, spec in (fm_doc.get("function_modules") or {}).items():
            self.fms[name.upper()] = fm_from_spec(name, spec, Provenance.BUILTIN)
        for name, spec in (fm_doc.get("methods") or {}).items():
            self.methods[name.upper()] = fm_from_spec(name, spec, Provenance.BUILTIN)

        s4_doc = _read_yaml(BASE_DIR / "s4_simplification.yaml")
        self.s4_mappings = [S4Mapping(**m) for m in s4_doc.get("mappings") or []]
        self.field_length_changes = s4_doc.get("field_length_changes") or []

        type_doc = _read_yaml(BASE_DIR / "ddic_type_map.yaml")
        self.types = {k.upper(): TypeSpec(**v) for k, v in (type_doc.get("types") or {}).items()}
        self.abap_types = {k.lower(): v for k, v in (type_doc.get("abap_types") or {}).items()}
        self.system_fields = {k.upper(): v for k, v in (type_doc.get("system_fields") or {}).items()}

    def _load_pack(self, pack_dir: Path, prov: Provenance = Provenance.CLIENT_PACK, register: bool = True) -> PackSummary:
        summary = PackSummary(name=pack_dir.name, path=str(pack_dir))
        if not pack_dir.is_dir():
            summary.issues.append(PackIssue(pack_dir.name, str(pack_dir), "Pack directory not found", "error"))
            if register:
                self.packs.append(summary)
            return summary

        manifest_path = pack_dir / "manifest.yaml"
        if manifest_path.exists():
            try:
                summary.manifest = _read_yaml(manifest_path)
                ProjectSettings(**{k: v for k, v in summary.manifest.items() if k in ProjectSettings.model_fields})
            except Exception as exc:  # noqa: BLE001 - surface any manifest problem to the user
                summary.issues.append(PackIssue(pack_dir.name, "manifest.yaml", f"Invalid manifest: {exc}", "error"))

        tables_path = pack_dir / "tables.yaml"
        if tables_path.exists():
            try:
                for name, spec in (_read_yaml(tables_path).get("tables") or {}).items():
                    try:
                        self._merge_table(_table_from_spec(name, spec or {}, prov), replace_fields=prov == Provenance.LIBRARY)
                        summary.tables += 1
                    except Exception as exc:  # noqa: BLE001 - one bad entry must not hide the rest
                        summary.issues.append(PackIssue(pack_dir.name, "tables.yaml", f"{name}: {exc}", "error"))
            except Exception as exc:  # noqa: BLE001
                summary.issues.append(PackIssue(pack_dir.name, "tables.yaml", f"Could not read: {exc}", "error"))

        ddic_dir = pack_dir / "ddic"
        if ddic_dir.is_dir():
            n_tables, n_fields = self._load_ddic(ddic_dir, summary, prov)
            summary.tables += n_tables
            summary.ddic_fields = n_fields

        fm_path = pack_dir / "fm_catalog.yaml"
        if fm_path.exists():
            try:
                doc = _read_yaml(fm_path)
                for section, target in (("function_modules", self.fms), ("methods", self.methods)):
                    for name, spec in (doc.get(section) or {}).items():
                        try:
                            target[name.upper()] = fm_from_spec(name, spec or {}, prov)
                            summary.function_modules += section == "function_modules"
                        except Exception as exc:  # noqa: BLE001
                            summary.issues.append(PackIssue(pack_dir.name, "fm_catalog.yaml", f"{name}: {exc}", "error"))
            except Exception as exc:  # noqa: BLE001
                summary.issues.append(PackIssue(pack_dir.name, "fm_catalog.yaml", f"Could not read: {exc}", "error"))

        s4_path = pack_dir / "s4_mappings.yaml"
        if s4_path.exists():
            try:
                for m in _read_yaml(s4_path).get("mappings") or []:
                    mapping = S4Mapping(**m)
                    self.s4_mappings = [x for x in self.s4_mappings if x.id != mapping.id and not set(x.old_tables) & set(mapping.old_tables)]
                    self.s4_mappings.insert(0, mapping)
            except Exception as exc:  # noqa: BLE001
                summary.issues.append(PackIssue(pack_dir.name, "s4_mappings.yaml", f"Could not read: {exc}", "error"))

        fm_src_dir = pack_dir / "function_modules"
        if fm_src_dir.is_dir():
            for path in sorted(fm_src_dir.glob("*.abap")):
                text = path.read_text(encoding="utf-8", errors="replace")
                names = _FM_HEADER.findall(text)
                if not names:
                    summary.issues.append(PackIssue(pack_dir.name, path.name, "No FUNCTION ... statement found"))
                    continue
                for fm_name in names:
                    self.add_fm_source(fm_name, text, prov)
                    summary.fm_sources.append(fm_name.upper())

        gold_dir = pack_dir / "gold"
        if gold_dir.is_dir():
            for pair in _discover_gold(gold_dir, pack_dir.name):
                self.gold.append(pair)
                summary.gold_pairs.append(pair.name)

        if register:
            self.packs.append(summary)
        return summary

    def _load_ddic(self, ddic_dir: Path, summary: PackSummary, prov: Provenance = Provenance.CLIENT_PACK) -> tuple[int, int]:
        texts: dict[str, str] = {}
        for name in ("DD02T.csv", "DD02L.csv"):
            path = ddic_dir / name
            if path.exists():
                for row in _read_csv(path):
                    tab = (row.get("TABNAME") or "").upper()
                    if tab and row.get("DDTEXT"):
                        texts[tab] = row["DDTEXT"]

        path = ddic_dir / "DD03L.csv"
        if not path.exists():
            return 0, 0
        rows = _read_csv(path)
        required = {"TABNAME", "FIELDNAME", "DATATYPE"}
        if rows and not required.issubset(rows[0].keys()):
            summary.issues.append(
                PackIssue(summary.name, "ddic/DD03L.csv", f"Missing columns: {sorted(required - rows[0].keys())}", "error")
            )
            return 0, 0

        by_table: dict[str, TableInfo] = {}
        n_fields = 0
        for row in rows:
            tab = (row.get("TABNAME") or "").upper()
            fname = (row.get("FIELDNAME") or "").upper()
            if not tab or not fname or fname.startswith((".INCLU", ".APPEND")):
                continue
            info = by_table.setdefault(
                tab,
                TableInfo(
                    name=tab,
                    description=texts.get(tab, ""),
                    fields_complete=True,  # a DD03L export lists every field
                    source=prov,
                ),
            )
            is_key = (row.get("KEYFLAG") or "").strip().upper() == "X"
            if is_key:
                info.key.append(fname)
            info.fields[fname] = FieldInfo(
                name=fname,
                ddic_type=(row.get("DATATYPE") or "CHAR").upper(),
                length=_to_int(row.get("LENG")),
                decimals=_to_int(row.get("DECIMALS")),
                ref_field=(row.get("REFFIELD") or None),
                description=row.get("DDTEXT") or row.get("SCRTEXT_M") or "",
                is_key=is_key,
                source=prov,
            )
            n_fields += 1
        for info in by_table.values():
            self._merge_table(info, replace_fields=True)
        return len(by_table), n_fields

    def _merge_table(self, incoming: TableInfo, replace_fields: bool = False) -> None:
        existing = self.tables.get(incoming.name)
        if existing is None or replace_fields:
            if existing is not None:
                # keep curated descriptions/relations the DDIC export does not carry
                incoming.description = incoming.description or existing.description
                incoming.module = incoming.module or existing.module
                incoming.text_table = incoming.text_table or existing.text_table
                incoming.text_of = incoming.text_of or existing.text_of
                incoming.release = existing.release if incoming.release == "both" else incoming.release
                for fname, finfo in incoming.fields.items():
                    if not finfo.description and fname in existing.fields:
                        finfo.description = existing.fields[fname].description
            self.tables[incoming.name] = incoming
            return
        existing = existing.model_copy(deep=True)  # base entries are shared; never mutate them in place
        existing.fields.update(incoming.fields)
        existing.fields_complete = existing.fields_complete or incoming.fields_complete
        existing.source = incoming.source
        self.tables[incoming.name] = existing
        for attr in ("description", "module", "text_table", "text_of", "key", "origin", "updated"):
            value = getattr(incoming, attr)
            if value:
                setattr(existing, attr, value)

    def add_fm_source(self, name: str, source: str, provenance: Provenance) -> None:
        key = name.upper()
        self.fm_sources[key] = source
        current = self.fms.get(key)
        if current is None or current.kind == "opaque":
            self.fms[key] = FMInfo(name=key, kind="custom", source=provenance, has_source_code=True)
        else:
            current.has_source_code = True

    # ------------------------------------------------------------------ lookups
    def table(self, name: str) -> TableInfo | None:
        return self.tables.get(name.upper())

    def field(self, table: str, field_name: str) -> tuple[FieldInfo | None, FieldStatus]:
        info = self.table(table)
        if info is None:
            return None, FieldStatus.NO_TABLE
        f = info.fields.get(field_name.upper())
        if f is not None:
            return f, FieldStatus.KNOWN
        return None, FieldStatus.UNKNOWN if info.fields_complete else FieldStatus.UNVERIFIED

    def fm(self, name: str) -> FMInfo | None:
        return self.fms.get(name.upper())

    def method(self, name: str) -> FMInfo | None:
        return self.methods.get(name.upper())

    def fm_source(self, name: str) -> str | None:
        return self.fm_sources.get(name.upper())

    def type_spec(self, ddic_type: str | None) -> TypeSpec | None:
        return self.types.get(ddic_type.upper()) if ddic_type else None

    def apply_catalog(self, catalog: dict) -> None:
        """Merge live Snowflake metadata: the column list becomes authoritative (fields_complete),
        descriptions and ABAP types from the dictionary are kept where the field is known."""
        for name, entry in (catalog.get("tables") or {}).items():
            base = self.tables.get(name.upper())
            info = TableInfo(name=name.upper(), description=(base.description if base else "") or entry.get("comment", ""),
                             module=base.module if base else "", key=list(base.key) if base else [],
                             text_table=base.text_table if base else None, text_of=base.text_of if base else None,
                             fields_complete=True, source=Provenance.CATALOG)
            for c in entry.get("columns", []):
                fname = c["name"].upper()
                known = base.fields.get(fname) if base else None
                if known is not None:
                    f = known.model_copy()
                    f.source = Provenance.CATALOG
                    if not f.description and c.get("comment"):
                        f.description = c["comment"]
                else:
                    f = FieldInfo(name=fname, ddic_type=c.get("ddic"), length=c.get("length") or c.get("precision"),
                                  decimals=c.get("scale"), description=c.get("comment") or "", source=Provenance.CATALOG,
                                  is_key=fname in (base.key if base else []))
                info.fields[fname] = f
            self.tables[info.name] = info

    def fork(self) -> "KnowledgeBase":
        """Per-run copy: tables can be extended (catalog, inference) without touching the shared KB."""
        other = KnowledgeBase()
        other.__dict__.update(self.__dict__)
        other.tables = dict(self.tables)
        other.fms = dict(self.fms)
        return other

    def s4_mapping_for(self, table: str) -> S4Mapping | None:
        t = table.upper()
        for m in self.s4_mappings:
            if t in m.old_tables:
                return m
        return None

    def gold_for(self, program: str) -> GoldPair | None:
        for g in self.gold:
            if g.name.upper() == program.upper():
                return g
        return None

    def settings_from_packs(self, **overrides) -> ProjectSettings:
        merged: dict = {}
        for pack in self.packs:
            merged.update({k: v for k, v in pack.manifest.items() if k in ProjectSettings.model_fields})
        merged["packs"] = [p.name for p in self.packs]
        merged.update({k: v for k, v in overrides.items() if v is not None})
        return ProjectSettings(**merged)

    def stats(self) -> dict:
        return {
            "tables": len(self.tables),
            "fields": sum(len(t.fields) for t in self.tables.values()),
            "function_modules": len(self.fms),
            "fm_sources": len(self.fm_sources),
            "s4_mappings": len(self.s4_mappings),
            "gold_pairs": len(self.gold),
            "packs": [p.name for p in self.packs],
        }


# ---------------------------------------------------------------------- helpers
def _read_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _read_csv(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(text.splitlines(), dialect=dialect)
    rows = []
    for row in reader:
        rows.append({(k or "").strip().upper(): (v or "").strip() for k, v in row.items()})
    return rows


def _to_int(value: str | None) -> int | None:
    try:
        return int(str(value).strip()) if value not in (None, "") else None
    except ValueError:
        return None


def _table_from_spec(name: str, spec: dict, source: Provenance) -> TableInfo:
    if spec.get("origin") == "ai":
        source = Provenance.AI
    key = [k.upper() for k in spec.get("key") or []]
    fields = {
        fname.upper(): parse_field_spec(fname, fspec, source, key) for fname, fspec in (spec.get("fields") or {}).items()
    }
    return TableInfo(
        name=name.upper(),
        description=spec.get("description", ""),
        module=spec.get("module", ""),
        release=spec.get("release", "both"),
        key=key,
        key_note=spec.get("key_note"),
        fields=fields,
        fields_complete=bool(spec.get("fields_complete", False)),
        text_table=spec.get("text_table"),
        text_of=spec.get("text_of"),
        source=source,
        origin=spec.get("origin"),
        updated=str(spec["updated"]) if spec.get("updated") else None,
    )


def _discover_gold(gold_dir: Path, pack: str) -> list[GoldPair]:
    pairs: list[GoldPair] = []
    # Layout A: gold/<name>.abap + gold/<name>.sql
    for sql_path in sorted(gold_dir.glob("*.sql")):
        abap = gold_dir / f"{sql_path.stem}.abap"
        if abap.exists():
            pairs.append(GoldPair(sql_path.stem, {abap.name: abap.read_text(encoding="utf-8")}, sql_path.read_text(encoding="utf-8"), pack))
    # Layout B: gold/<name>/ with *.abap files (main + includes) and expected.sql
    for sub in sorted(p for p in gold_dir.iterdir() if p.is_dir()):
        sql_files = list(sub.glob("*.sql"))
        abap_files = {p.name: p.read_text(encoding="utf-8") for p in sorted(sub.glob("*.abap"))}
        if sql_files and abap_files:
            pairs.append(GoldPair(sub.name, abap_files, sql_files[0].read_text(encoding="utf-8"), pack))
    return pairs
