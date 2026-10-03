"""Shared skill types and the per-run context every skill receives."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import date
from typing import Any, Callable

from agent.mcp_client import McpError, safe_error_text
from agent.privacy import sanitise_file
from agent.records import DecisionRecord, Evidence, RecordBook
from agent.safe_reads import folders_by_id, list_all
from agent.textsafe import one_line

NAME_LIMIT = 100  # folder, party and uploader names other teams can edit
UNVERIFIED_UPLOADER = "per the access log, which anyone can write; unverified"


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    input_schema: dict[str, Any]
    run: Callable[["SkillContext", dict[str, Any]], dict[str, Any]]


class SkillContext:
    """Everything a skill may use. Writes are only possible through `guard`."""

    def __init__(self, *, mcp: Any, session: Any, guard: Any, trace: Any, catalog: Any,
                 rules: Any, settings: Any, allowlist: frozenset[str]) -> None:
        self.mcp = mcp
        self.session = session
        self.guard = guard
        self.trace = trace
        self.catalog = catalog
        self.rules = rules
        self.settings = settings
        self.allowlist = allowlist
        self.records = RecordBook()
        self.seen_ids: set[str] = set()
        self.escalator: Any = None  # wired by agent.runtime
        self.question: str | None = None  # the user's own words, if the loop sets them (explain_access uses them)
        # STRIDE R3: names this run in the session title; the harness and the CLI set it to their run file's name
        self.run_id = uuid.uuid4().hex[:8]
        self._files: list[dict[str, Any]] | None = None
        self._folders: dict[str, dict[str, Any]] | None = None
        self._uploads: dict[str, tuple[str | None, str]] = {}
        self._overview: tuple[int, Any] | None = None

    def me(self) -> dict[str, Any]:
        return self.session.me()

    def files(self, refresh: bool = False) -> list[dict[str, Any]]:
        """Every file row; rows of apps this seat can't open come back as placeholders (leak guard)."""
        if self._files is None or refresh:
            self._files = [sanitise_file(r, self.catalog.can_list) for r in list_all(self.mcp, "FileAttachment.list")]
            self.note_ids(*(f.get("id") for f in self._files))
        return self._files

    def overview(self) -> tuple[int, Any]:
        """(status, body) of GET /api/drive/records/overview, read once per run."""
        if self._overview is None:
            budget = getattr(self.mcp, "budget", None)
            if budget is not None:  # STRIDE D2: this REST read counts against the same call cap as the MCP reads
                budget.add_call()
            self._overview = self.session.request("GET", "/api/drive/records/overview")
        return self._overview

    def folders(self, refresh: bool = False) -> dict[str, dict[str, Any]]:
        if self._folders is None or refresh:
            self._folders = folders_by_id(self.mcp)
            self.note_ids(*self._folders)
        return self._folders

    def folder_name(self, folder_id: str | None) -> str:
        if not folder_id:
            return "(not in a folder)"
        # STRIDE T2: any team can rename a folder; its name reaches notes, escalations and the model as one plain line
        return one_line(self.folders().get(folder_id, {}).get("name", folder_id), NAME_LIMIT)

    def note_ids(self, *ids: Any) -> None:
        self.seen_ids.update(str(i) for i in ids if i)

    def record(self, **kwargs: Any) -> DecisionRecord:
        if "evidence" in kwargs:
            kwargs["evidence"] = tuple(kwargs["evidence"])
        if "missing" in kwargs:
            kwargs["missing"] = tuple(kwargs["missing"])
        return self.records.add(DecisionRecord(**kwargs))

    @staticmethod
    def today() -> str:
        return date.today().isoformat()


def error_text(err: BaseException) -> str:
    """An error as a record or an answer may state it (STRIDE I12: platform error text is withheld)."""
    return safe_error_text(err) if isinstance(err, McpError) else one_line(err, 300)


def ev(signal: str, detail: str, points_to: str | None = None, source_id: str | None = None) -> Evidence:
    return Evidence(signal=signal, detail=detail, points_to=points_to, source_id=source_id)


def upload_lead(ctx: SkillContext, file_id: str) -> tuple[str | None, str]:
    """(uploader, where that came from) per DriveAccessLog. Client-written (bug L8), so a lead, not proof.

    Looked up once per file per run. Upload rows naming different people name no one.
    """
    if file_id not in ctx._uploads:
        rows = list_all(ctx.mcp, "DriveAccessLog.list", file_id=file_id)
        actors = sorted({who for r in rows if r.get("action") == "upload" and (who := _actor(r))})
        if len(actors) > 1:  # STRIDE T2: a planted upload row must not override the genuine one; name no one
            ctx.trace.write("conflicting_upload_records", file_id=file_id, count=len(actors))
            ctx._uploads[file_id] = (None, "conflicting upload records in the access log")
        else:
            ctx._uploads[file_id] = (actors[0], "access log") if actors else (None, "no upload record")
    return ctx._uploads[file_id]


def _actor(row: dict[str, Any]) -> str | None:
    name, email = one_line(row.get("actor_name"), NAME_LIMIT), one_line(row.get("actor_email"), NAME_LIMIT)
    return f"{name} ({email})" if name and email else (name or email or None)
