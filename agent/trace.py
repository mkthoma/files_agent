"""Append-only JSONL trace. Every event is redacted before it touches the disk."""
from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agent.config import REPO_ROOT
from agent.redact import Redactor


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def private_open(path: str | os.PathLike[str], flags: int) -> int:
    """Opener for open(): a new file is created owner-only (0600) on POSIX; Windows keeps it writable."""
    # STRIDE I10: 0600 at creation, so other users on a shared machine never get a window to read it.
    return os.open(path, flags, 0o600)


def git_state() -> dict[str, Any]:
    """The commit that produced a run. A failed git command (e.g. no commits yet) gives "no-commit", never junk."""
    def git(*args: str) -> str | None:
        try:
            r = subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, timeout=10)
        except (OSError, subprocess.SubprocessError):
            return None
        return r.stdout.strip() if r.returncode == 0 else None
    status = git("status", "--porcelain")
    return {"commit": git("rev-parse", "--verify", "HEAD") or "no-commit", "dirty": status is None or bool(status)}


class Trace:
    """Writes one JSON object per line and keeps a redacted in-memory copy."""

    def __init__(self, path: Path | None, redactor: Redactor) -> None:
        self.path = path
        self.redact = redactor
        self.events: list[dict[str, Any]] = []
        if path is not None:
            path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, kind: str, **data: Any) -> dict[str, Any]:
        event = self._redacted({"t": now_iso(), "kind": kind, **data})
        self.events.append(event)
        if self.path is not None:
            with open(self.path, "a", encoding="utf-8", opener=private_open) as fh:
                fh.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")
        return event

    def of_kind(self, kind: str) -> list[dict[str, Any]]:
        return [e for e in self.events if e["kind"] == kind]

    def attach(self, path: Path, header: dict[str, Any]) -> None:
        """Start writing to `path`: the header (manifest) first, then any events buffered so far."""
        path.parent.mkdir(parents=True, exist_ok=True)
        first = self._redacted({"t": now_iso(), "kind": "manifest", **header})
        with open(path, "w", encoding="utf-8", opener=private_open) as fh:
            for event in [first, *self.events]:
                fh.write(json.dumps(event, ensure_ascii=False, default=str) + "\n")
        self.events.insert(0, first)
        self.path = path

    def _redacted(self, raw: dict[str, Any]) -> dict[str, Any]:
        event, masked = self.redact.masked(raw)
        # STRIDE R8: say how many values were masked, so a reader knows the event differs from what was sent.
        return {**event, "_redacted": masked} if masked else event


def read_trace(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]
