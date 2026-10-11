"""Project storage: one folder per project (plain JSON + uploaded files), grouped by workspace (client)."""

from __future__ import annotations

import json
import re
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

from ..config import get_settings

STAGES = ["uploaded", "analyzed", "reviewed", "converted", "validated"]


class ProjectContext(BaseModel):
    """User-provided context; editable between pipeline stages."""

    fm_sources: dict[str, str] = Field(default_factory=dict)
    fm_hints: dict[str, str] = Field(default_factory=dict)
    business_names: dict[str, str] = Field(default_factory=dict)
    table_renames: dict[str, str] = Field(default_factory=dict)
    notes: str = ""
    output_table: str | None = None


class ConvertOptions(BaseModel):
    mode: str = "select"  # select | view
    view_name: str | None = None
    use_llm: bool = True
    model: str | None = None


class StageEvent(BaseModel):
    stage: str
    at: str
    detail: str = ""


class Project(BaseModel):
    id: str
    name: str
    workspace: str = "default"
    created: str
    updated: str
    stage: str = "uploaded"
    packs: list[str] = Field(default_factory=list)
    settings: dict = Field(default_factory=dict)  # ProjectSettings overrides
    context: ProjectContext = Field(default_factory=ProjectContext)
    convert: ConvertOptions = Field(default_factory=ConvertOptions)
    main: str | None = None
    files: list[str] = Field(default_factory=list)
    history: list[StageEvent] = Field(default_factory=list)
    summary: dict = Field(default_factory=dict)  # small stats for lists


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _safe(name: str) -> str:
    n = re.sub(r"[^A-Za-z0-9_.\-/]", "_", name).strip("/")
    n = n.replace("..", "_")
    return n or "file.abap"


class ProjectStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or get_settings().data_dir) / "projects"
        self.root.mkdir(parents=True, exist_ok=True)

    def _dir(self, pid: str) -> Path:
        if not re.fullmatch(r"[a-z0-9]{8,32}", pid):
            raise KeyError(pid)
        return self.root / pid

    def create(self, name: str, files: dict[str, str], workspace: str = "default", packs: list[str] | None = None,
               settings: dict | None = None) -> Project:
        pid = uuid.uuid4().hex[:12]
        d = self._dir(pid)
        (d / "files").mkdir(parents=True)
        p = Project(id=pid, name=name, workspace=workspace or "default", created=_now(), updated=_now(), packs=packs or [],
                    settings=settings or {})
        self.save(p)
        self.add_files(p, files)
        return p

    def add_files(self, p: Project, files: dict[str, str]) -> Project:
        d = self._dir(p.id) / "files"
        for name, content in files.items():
            rel = _safe(name)
            path = (d / rel).resolve()
            if not str(path).startswith(str(d.resolve())):
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            if rel not in p.files:
                p.files.append(rel)
        p.updated = _now()
        self.save(p)
        return p

    def remove_file(self, p: Project, name: str) -> Project:
        rel = _safe(name)
        path = self._dir(p.id) / "files" / rel
        if path.exists():
            path.unlink()
        p.files = [f for f in p.files if f != rel]
        self.save(p)
        return p

    def files(self, p: Project) -> dict[str, str]:
        d = self._dir(p.id) / "files"
        return {f: (d / f).read_text(encoding="utf-8") for f in p.files if (d / f).exists()}

    def save(self, p: Project) -> None:
        p.updated = _now()
        (self._dir(p.id) / "project.json").write_text(p.model_dump_json(indent=2), encoding="utf-8")

    def get(self, pid: str) -> Project:
        path = self._dir(pid) / "project.json"
        if not path.exists():
            raise KeyError(pid)
        return Project.model_validate_json(path.read_text(encoding="utf-8"))

    def list(self, workspace: str | None = None) -> list[Project]:
        out = []
        for d in sorted(self.root.iterdir()):
            f = d / "project.json"
            if f.exists():
                try:
                    p = Project.model_validate_json(f.read_text(encoding="utf-8"))
                except ValueError:
                    continue
                if workspace is None or p.workspace == workspace:
                    out.append(p)
        return sorted(out, key=lambda p: p.updated, reverse=True)

    def delete(self, pid: str) -> None:
        shutil.rmtree(self._dir(pid), ignore_errors=True)

    def write_artifact(self, p: Project, name: str, data: str | dict) -> None:
        path = self._dir(p.id) / name
        path.write_text(data if isinstance(data, str) else json.dumps(data, indent=2, default=str), encoding="utf-8")

    def read_artifact(self, p: Project, name: str) -> str | None:
        path = self._dir(p.id) / name
        return path.read_text(encoding="utf-8") if path.exists() else None

    def mark(self, p: Project, stage: str, detail: str = "") -> None:
        p.stage = stage
        p.history.append(StageEvent(stage=stage, at=_now(), detail=detail))
        self.save(p)
