"""Reads that avoid the platform's filter traps (T1.5).

Traps avoided (all verified 21-22 Sept 2026, bugs L2/L3/L5/F4/F5):
- `ne:` silently drops rows whose value is NULL      -> negate in code
- a comma in a filter value becomes an OR list       -> never send it; filter in code
- REST sort_order is not validated                   -> sort in code
- /api/export ignores unknown filters                -> never used
- /api/search stops at 5 results per type            -> page the entity list instead
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from agent.mcp_client import McpError

PAGE = 500
MAX_PAGES = 200  # 100,000 rows; every table today fits in one page
SAFE_SERVER_FILTERS = {"id", "folder_id", "entity_id", "entity_type", "code", "file_id", "content_hash", "parent_id"}


def list_all(mcp: Any, tool: str, **filters: Any) -> list[dict[str, Any]]:
    """Page through a .list tool. Only exact, comma-free filters go to the server; all are re-checked here."""
    server = {k: v for k, v in filters.items()
              if k in SAFE_SERVER_FILTERS and v is not None and "," not in str(v) and not str(v).startswith(("ne:", "gt:", "lt:"))}
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    offset = 0
    for _ in range(MAX_PAGES):  # STRIDE D8: a server that ignores offset can't keep us paging forever
        page = mcp.call(tool, {**server, "limit": PAGE, "offset": offset})
        batch = _page_rows(tool, page)
        if not batch:
            return where(rows, **filters)
        fresh = [r for r in batch if r.get("id") is None or str(r["id"]) not in seen]
        if not fresh:  # STRIDE D8: the same rows again means offset is ignored; never keep duplicates
            raise McpError(f"{tool} returned the same rows again at offset {offset}; stopped paging",
                           data_code="no_progress", own=True)
        seen.update(str(r["id"]) for r in fresh if r.get("id") is not None)
        rows.extend(fresh)
        offset += len(batch)
        total = _total(page)
        if total is not None and offset >= total:
            return where(rows, **filters)
    raise McpError(f"{tool} still had rows after {MAX_PAGES} pages; stopped paging", data_code="too_many_pages",
                   own=True)


def _page_rows(tool: str, page: Any) -> list[dict[str, Any]]:
    """The rows of one list page; a reply of any other shape is an error, never an empty table."""
    data = page.get("data") if isinstance(page, dict) else None
    if not isinstance(data, list) or not all(isinstance(r, dict) for r in data):
        raise McpError(f"{tool} returned a page that is not a list of rows", data_code="bad_reply", own=True)  # STRIDE D8
    return data


def _total(page: dict[str, Any]) -> int | None:
    """The server's row count, or None when it is missing or not a count (then page until an empty page)."""
    total = page.get("total")
    return total if isinstance(total, int) and not isinstance(total, bool) and total >= 0 else None


def where(rows: list[dict[str, Any]], **equals: Any) -> list[dict[str, Any]]:
    """Exact equality in code; `None` means 'field is empty'."""
    return [r for r in rows if all(_same(r.get(k), v) for k, v in equals.items())]


def not_equal(rows: list[dict[str, Any]], field: str, value: Any) -> list[dict[str, Any]]:
    """Correct 'not equal': rows with an empty value are included (unlike the platform's ne:)."""
    return [r for r in rows if not _same(r.get(field), value)]


def _same(actual: Any, wanted: Any) -> bool:
    if wanted is None:
        return actual in (None, "")
    if isinstance(wanted, bool):
        return bool(actual) == wanted
    return str(actual) == str(wanted)


def folders_by_id(mcp: Any) -> dict[str, dict[str, Any]]:
    return {f["id"]: f for f in list_all(mcp, "DriveFolder.list")}


def name_key(name: Any) -> str:
    """How folder names are compared: trimmed and case-folded."""
    return str(name or "").strip().casefold()


def shared_names(folders: dict[str, dict[str, Any]]) -> set[str]:
    """Folder names (as name_key) that more than one live folder carries."""
    counts = Counter(name_key(f.get("name")) for f in folders.values() if not f.get("is_archived"))
    return {key for key, n in counts.items() if n > 1}


def folder_named(folders: dict[str, dict[str, Any]], name: str) -> dict[str, Any] | None:
    """The one live folder with this name; None if there is none or several (a shared name is ambiguous)."""
    wanted = name_key(name)
    # STRIDE T4: a second folder with the same name (another team's 'HR') must never win silently
    matches = [f for f in folders.values() if not f.get("is_archived") and name_key(f.get("name")) == wanted]
    return matches[0] if len(matches) == 1 else None


def find_files_by_name(files: list[dict[str, Any]], name: str) -> list[dict[str, Any]]:
    """Exact filename first; otherwise a case-insensitive exact match; never a loose substring."""
    exact = [f for f in files if f.get("filename") == name]
    return exact or [f for f in files if (f.get("filename") or "").lower() == name.lower()]
