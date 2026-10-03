"""Snapshot and restore (T2.9 / A8): the undo log for live runs on the shared tenant.

- Before the first write, snapshot the writable fields of the allow-listed rows.
- While the run writes, a write journal (writes-N.json) records exactly what we sent and,
  for a file write, the values it replaced.
- Afterwards, restore puts back ONLY the fields we wrote (never more than RESTORE_FIELDS), and
  only where the value is still the one we wrote. A description goes back to the text our note was
  appended to, so an edit another team made between the snapshot and our write survives (reported as
  kept_foreign_edits); every other field goes back to its snapshot value.
  Anything another team changed after our write is reported as a conflict and left alone:
  the agent must never become the thing that overwrites other people's work.
- Restore refuses a malformed snapshot or journal, or one that holds ids outside the allow-list,
  and keeps going when one row fails for any reason, so one bad row can't leave the others un-restored.

Also usable on its own:
  AS_ALLOW_WRITES=1 python -m harness restore runs/<set>/<task>/snapshot-1.json --target live --live-apply
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from agent.config import WRITE_TOOLS
from agent.guards import UPDATE_FIELDS, WRITABLE_FIELDS, same_value
from agent.mcp_client import McpError
from agent.skills.profiles import PROVENANCE_MARKER
from agent.textsafe import one_line
from agent.trace import private_open

SNAPSHOT_FIELDS = (*WRITABLE_FIELDS, "updated_at", "updated_by")
# STRIDE T6: restore only ever puts back the fields the write guard lets the agent change.
RESTORE_FIELDS = UPDATE_FIELDS


class RestoreRefused(Exception):
    """The snapshot can't be trusted; nothing was restored."""


def take(mcp: Any, ids: frozenset[str] | set[str]) -> dict[str, dict[str, Any]]:
    snap = {}
    for file_id in sorted(ids):
        row = mcp.call("FileAttachment.get", {"id": file_id})
        if not isinstance(row, dict):  # STRIDE D6: a reply that is not a row is a failed read, not a crash
            raise McpError(f"FileAttachment.get {file_id} returned no row ({type(row).__name__})", data_code="bad_reply",
                           own=True)
        snap[file_id] = {f: row.get(f) for f in SNAPSHOT_FIELDS}
    return snap


def save(data: Any, path: Path) -> Path:
    """Write JSON through a temporary file, so a crash mid-save never leaves a truncated file (STRIDE T6)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, ensure_ascii=False)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", opener=private_open) as fh:  # STRIDE I10: owner-only on POSIX
        fh.write(text)
    try:
        os.replace(tmp, path)
    except PermissionError:  # Windows: a virus scanner can hold the old file open for a moment
        path.write_text(text, encoding="utf-8")
        tmp.unlink(missing_ok=True)
    return path


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def writes_path(snapshot_path: Path) -> Path:
    """snapshot-1.json -> writes-1.json (the write journal saved beside it)."""
    return snapshot_path.with_name(snapshot_path.name.replace("snapshot", "writes", 1))


class WriteJournal:
    """Every write of a live run, saved to disk as soon as its call ends."""

    def __init__(self, path: Path | None) -> None:
        self.path = path
        self.entries: list[dict[str, Any]] = []

    def add(self, entry: dict[str, Any]) -> None:
        self.entries.append(entry)
        if self.path is not None:
            save(self.entries, self.path)


def check_inputs(snap: Any, writes: Any, allowlist: frozenset[str] | set[str]) -> None:
    """Refuse a snapshot or journal this agent could not have written; raises RestoreRefused (STRIDE T6)."""
    if not isinstance(snap, dict) or not all(isinstance(row, dict) for row in snap.values()):
        raise RestoreRefused("snapshot is not a mapping of file id to fields; nothing restored")
    outside = sorted(set(snap) - set(allowlist))
    if outside:
        raise RestoreRefused(f"snapshot holds ids outside the write allow-list {outside}; nothing restored")
    for file_id, row in snap.items():
        problem = _field_problem(row, SNAPSHOT_FIELDS)
        if problem:
            raise RestoreRefused(f"snapshot row {file_id} {problem}; nothing restored")
    if writes is None:
        return
    if not isinstance(writes, list) or not all(isinstance(w, dict) for w in writes):
        raise RestoreRefused("write journal is not a list of entries; nothing restored")
    for entry in writes:
        problem = _journal_problem(entry)
        if problem:
            raise RestoreRefused(f"write journal entry for {one_line(entry.get('id'), 40)} {problem}; nothing restored")


def _journal_problem(entry: dict[str, Any]) -> str | None:
    if entry.get("tool") not in WRITE_TOOLS:
        return f"names {str(entry.get('tool'))[:60]!r}, a tool the agent never writes with"
    if entry["tool"] != "FileAttachment.update":
        return None
    if not isinstance(entry.get("id"), str):
        return "has no file id"
    for key in ("changes", "before"):
        part = entry.get(key, {})
        problem = _field_problem(part, RESTORE_FIELDS) if isinstance(part, dict) else "is not an object"
        if problem:
            return f"{key} {problem}"
    return None


def _field_problem(fields: dict[str, Any], allowed: Any) -> str | None:
    """Unknown field names, or a restorable field whose value has the wrong type."""
    extra = sorted(str(k) for k in set(fields) - set(allowed))
    if extra:
        return f"has unexpected fields {extra[:5]}"
    for key in ("folder_id", "description"):
        if not isinstance(fields.get(key), (str, type(None))):
            return f"has a {key} that is not text"
    if fields.get("is_archived") not in (None, True, False, 0, 1):
        return "has an is_archived that is not true or false"
    return None


def diff(snap: dict[str, dict[str, Any]], current: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """{file_id: {field: (snapshot_value, current_value)}} for writable fields that differ."""
    out = {}
    for file_id, original in snap.items():
        now = current.get(file_id) or {}
        changed = {f: (original.get(f), now.get(f)) for f in WRITABLE_FIELDS if not same_value(original.get(f), now.get(f))}
        if changed:
            out[file_id] = changed
    return out


def _ours(writes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """{file_id: {field: the value we last wrote}} from the write journal."""
    out: dict[str, dict[str, Any]] = {}
    for w in writes:
        if w.get("tool") == "FileAttachment.update":
            out.setdefault(w["id"], {}).update(w.get("changes") or {})
    return out


def _replaced(writes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """{file_id: {"description": the text our first write of it appended its note to}}.

    STRIDE T6: the journal is a local file, so its `before` is honoured only where our own write shows it: the
    description we sent must be exactly that text plus our provenance note. Every other field, and any
    `before` that fails this check, goes back to the snapshot value.
    """
    out: dict[str, dict[str, Any]] = {}
    seen: set[str] = set()
    for w in writes:
        if w.get("tool") != "FileAttachment.update" or w["id"] in seen:
            continue
        seen.add(w["id"])
        before, sent = (w.get("before") or {}).get("description"), (w.get("changes") or {}).get("description")
        if _appended_to(before, sent):
            out[w["id"]] = {"description": before}
    return out


def _appended_to(before: Any, sent: Any) -> bool:
    """Is `sent` exactly `before` with our provenance note appended (as triage writes it)?"""
    if not isinstance(sent, str) or not isinstance(before, (str, type(None))):
        return False
    head = f"{before}\n" if before else ""
    return sent.startswith(head) and sent[len(head):].startswith(PROVENANCE_MARKER)


def plan_restore(snap: dict[str, dict[str, Any]], current: dict[str, dict[str, Any]],
                 writes: list[dict[str, Any]] | None, me: str | None) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """Split every difference into (fields we may put back, with the value to write; fields someone else changed).

    Only RESTORE_FIELDS can be ours; any other difference is someone else's.
    With the write journal: a field is ours only if we wrote it and it still holds our value. It goes back
    to its snapshot value, except a description our note was appended to (see _replaced).
    Without it (journal lost): a row is ours only if this seat was the last to change it.
    """
    ours = _ours(writes) if writes is not None else None
    replaced = _replaced(writes) if writes is not None else {}
    todo: dict[str, dict[str, Any]] = {}
    conflicts: dict[str, dict[str, Any]] = {}
    for file_id, fields in diff(snap, current).items():
        row = current.get(file_id) or {}
        for field, (old, now) in fields.items():
            if field not in RESTORE_FIELDS:  # STRIDE T6: the agent never writes it, so it is never ours to undo
                mine = False
            elif ours is not None:
                mine = field in ours.get(file_id, {}) and same_value(ours[file_id][field], now)
            else:
                mine = bool(me) and row.get("updated_by") == me
            if not mine:
                conflicts.setdefault(file_id, {})[field] = {"snapshot": old, "now": now, "updated_by": row.get("updated_by")}
                continue
            target = replaced.get(file_id, {}).get(field, old)  # STRIDE T9: the text our note was appended to
            if not same_value(target, now):
                todo.setdefault(file_id, {})[field] = target
    return todo, conflicts


def restore(mcp: Any, snap: dict[str, dict[str, Any]], trace: Any, *, allowlist: frozenset[str] | set[str],
            writes: list[dict[str, Any]] | None = None, me: str | None = None) -> dict[str, Any]:
    """Put back what we changed. Raises RestoreRefused (nothing done) or RuntimeError (incomplete)."""
    check_inputs(snap, writes, allowlist)
    todo: dict[str, dict[str, Any]] = {}
    conflicts: dict[str, dict[str, Any]] = {}
    failed: dict[str, str] = {}
    remaining: dict[str, dict[str, Any]] = {}
    overtaken: dict[str, dict[str, Any]] = {}
    finished = False
    try:
        for file_id in sorted(snap):
            try:
                # Decide from a read taken right before this row's write, not from an earlier batch read,
                # so an edit another team made meanwhile is seen as a conflict. (The platform has no
                # compare-and-set, so only a change landing inside this one round trip could slip through.)
                mine, theirs = plan_restore({file_id: snap[file_id]}, take(mcp, {file_id}), writes, me)
                conflicts.update(theirs)
                if mine:
                    todo.update(mine)
                    mcp.call("FileAttachment.update", {**mine[file_id], "id": file_id})
            except Exception as err:  # STRIDE D6: any failure on one row must not stop the others
                failed[file_id] = _reason(err)
        remaining, overtaken, unreadable = _confirm(mcp, snap, todo, set(failed), me)
        failed.update(unreadable)
        finished = True
    finally:
        for fid, fields in overtaken.items():
            conflicts.setdefault(fid, {}).update(fields)
        report = {"restored": sorted(set(todo) - set(failed) - set(remaining) - set(overtaken)), "failed": failed,
                  "remaining": remaining, "conflicts_left_alone": conflicts, "kept_foreign_edits": _kept(snap, todo, failed),
                  "mode": "journal" if writes is not None else "updated_by-fallback"}  # STRIDE R7
        if not finished:
            report["interrupted"] = True
        trace.write("restore", **report)
    if failed or remaining:
        raise RuntimeError(f"restore incomplete for {sorted(set(failed) | set(remaining))}; fix the cause, then re-run "
                           "`python -m harness restore <snapshot> --target live --live-apply`")
    return report


def _confirm(mcp: Any, snap: dict[str, dict[str, Any]], todo: dict[str, dict[str, Any]], skip: set[str],
             me: str | None) -> tuple[dict[str, Any], dict[str, Any], dict[str, str]]:
    """Read each restored row back: (remaining, overtaken by another team, unreadable).

    A row is compared with the values restore wrote (STRIDE T9), and read on its own (STRIDE D6).
    """
    remaining: dict[str, Any] = {}
    overtaken: dict[str, Any] = {}
    unreadable: dict[str, str] = {}
    for fid in sorted(set(todo) - skip):
        try:
            row = take(mcp, {fid})[fid]
        except Exception as err:  # STRIDE D6: report the row, keep confirming the others
            unreadable[fid] = f"confirming read failed: {_reason(err)}"
            continue
        off = {f: (want, row.get(f)) for f, want in todo[fid].items() if not same_value(row.get(f), want)}
        if not off:
            continue
        if me and row.get("updated_by") not in (None, me):  # another team changed it after our restore
            overtaken[fid] = {f: {"snapshot": snap[fid].get(f), "now": now, "updated_by": row.get("updated_by")}
                              for f, (_, now) in off.items()}
        else:
            remaining[fid] = off
    return remaining, overtaken, unreadable


def _kept(snap: dict[str, dict[str, Any]], todo: dict[str, dict[str, Any]], failed: dict[str, str]) -> dict[str, Any]:
    """Fields put back to a value someone set between the snapshot and our write, not to the snapshot (STRIDE T9)."""
    out: dict[str, Any] = {}
    for fid, fields in todo.items():
        for field, value in fields.items():
            if fid not in failed and not same_value(value, snap[fid].get(field)):
                out.setdefault(fid, {})[field] = {"snapshot": snap[fid].get(field), "restored_to": value}
    return out


def _reason(err: BaseException) -> str:
    return str(err) if isinstance(err, McpError) else f"{type(err).__name__}: {err}"
