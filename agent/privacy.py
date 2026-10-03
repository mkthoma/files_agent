"""Leak guard (A11): rows owned by apps this seat can't open never show their titles.

A FileAttachment row whose entity_type belongs to an app outside the seat (e.g.
EsignDocument: offer letters, contracts) is replaced by a placeholder wherever
the model, a skill or a trace could see it. The row's id, entity type, size and
folder stay, so counts are still correct. Only the fields in KEEP_FIELDS survive
on such a row: any other field (today or added by the platform later) is None.

The model's own direct reads get a second, per-tool projection (`for_model_*`):
access-log rows name files only through the leak-guarded file list, other seats'
escalations show no text, and Party rows carry only the fields a question needs.
"""
from __future__ import annotations

from typing import Any, Callable, Iterable

OPEN_ENTITY_TYPES = {None, "", "Drive"}
PRIVATE_FIELDS = ("description", "tags", "storage_path", "from_email", "from_name", "message_subject", "thread_id", "party_id")
# STRIDE I1: allow-list, so a new `_<fk>_display` or title column on a withheld row fails closed.
KEEP_FIELDS = frozenset({
    "id", "entity_type", "entity_id", "folder_id", "_folder_id_display", "size_bytes", "content_hash",
    "is_archived", "is_trashed", "is_purged", "is_inline", "mime_type", "created_at", "updated_at",
    "created_by", "updated_by", "company_id", "_company_id_display", "_permissions", "_readonly_fields",
    "_can_create", "current_revision_number", "download_count",
})
LOG_FIELDS = ("id", "_display", "action", "actor_name", "actor_email", "file_id", "_file_id_display",
              "folder_id", "_folder_id_display", "details", "created_at")
PARTY_FIELDS = ("id", "_display", "name", "company_name", "email", "type", "contact_type", "company_id")
ESCALATION_PUBLIC_FIELDS = ("id", "status", "reason_code", "channel", "created_at", "updated_at", "created_by", "company_id")

CanList = Callable[[str], bool]


def is_withheld(row: dict[str, Any], can_list: CanList) -> bool:
    entity_type = row.get("entity_type")
    return entity_type not in OPEN_ENTITY_TYPES and not can_list(entity_type)


def sanitise_file(row: dict[str, Any], can_list: CanList) -> dict[str, Any]:
    """A withheld row keeps its shape, but only KEEP_FIELDS keep their values. A later feature that needs
    another field of a withheld row gets None."""
    if not is_withheld(row, can_list):
        return row
    placeholder = f"{row['entity_type']}-attachment-{str(row.get('id', ''))[:8]}.pdf"
    kept = {k: (v if k in KEEP_FIELDS else None) for k, v in row.items()}
    return {**kept, "filename": placeholder, "_display": placeholder}


def sanitise_payload(payload: Any, can_list: CanList) -> Any:
    """Sanitise a FileAttachment list page or a single FileAttachment row; anything else is returned as is."""
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return {**payload, "data": [sanitise_file(r, can_list) if _is_file_row(r) else r for r in payload["data"]]}
    return sanitise_file(payload, can_list) if _is_file_row(payload) else payload


def _is_file_row(row: Any) -> bool:
    return isinstance(row, dict) and "entity_type" in row and "filename" in row


def _map_rows(payload: Any, fn: Callable[[dict[str, Any]], dict[str, Any]]) -> Any:
    """Apply `fn` to every row of a list page, or to a single row."""
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return {**payload, "data": [fn(r) if isinstance(r, dict) else r for r in payload["data"]]}
    return fn(payload) if isinstance(payload, dict) else payload


def _pick(row: dict[str, Any], fields: Iterable[str]) -> dict[str, Any]:
    return {k: row.get(k) for k in fields if k in row}


def for_model_parties(payload: Any) -> Any:
    """STRIDE I8: Party rows reach the model with names and contact basics only (no bank, tax or birthday data)."""
    return _map_rows(payload, lambda r: _pick(r, PARTY_FIELDS))


def for_model_access_log(payload: Any, files: list[dict[str, Any]], can_list: CanList) -> Any:
    """STRIDE I5/I8: an access-log row names its file only through the leak-guarded file list. Its free text is
    dropped unless the file is known and open (an unknown id may be a withheld row created later)."""
    known = {f.get("id"): f for f in files}

    def guard(row: dict[str, Any]) -> dict[str, Any]:
        out = _pick(row, LOG_FIELDS)
        file_id = row.get("file_id")
        if file_id is None:  # STRIDE I5: a folder-level or bulk row names no file, so its free text is not vouched for
            return {**out, "_display": None, "_file_id_display": None, "details": None}
        file = known.get(file_id)
        name = file.get("filename") if file else None
        is_open = file is not None and not is_withheld(file, can_list)
        return {**out, "_display": name, "_file_id_display": name, "details": out.get("details") if is_open else None}

    return _map_rows(payload, guard)


def for_model_escalations(payload: Any, my_id: str | None) -> Any:
    """STRIDE I6: another seat's escalation keeps only its id, status and dates; its subject and reason
    (which may name that seat's documents) never reach this seat's model. No `my_id` hides every row."""

    def guard(row: dict[str, Any]) -> dict[str, Any]:
        if my_id and row.get("created_by") == my_id:
            return row
        return {**{k: None for k in row}, **_pick(row, ESCALATION_PUBLIC_FIELDS), "_withheld": "another seat's escalation"}

    return _map_rows(payload, guard)


def for_model_tool_search(payload: Any) -> Any:
    """STRIDE T10: tools.search returns tool names only, never other tools' platform-written descriptions."""
    page = payload if isinstance(payload, dict) else {}
    results = page.get("results") if isinstance(page.get("results"), list) else []
    status = page.get("status") if isinstance(page.get("status"), str) else None
    return {"results": [{"name": r.get("name")} for r in results if isinstance(r, dict)],
            **({"status": status[:20]} if status else {})}
