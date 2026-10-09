"""Read-only fixture capture (T1.6) and loading.

  python -m harness capture keystone

Saves one dated snapshot of everything the agent reads, so the fake server can
replay it offline. Titles of files owned by apps this seat can't open (e-sign
offer letters, contracts) are replaced with placeholders before saving, in the
file rows, the access log and the drive overview. Loading checks the fixture
against its manifest, so a hand-edited or half-written capture is never used.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from agent.catalog import Catalog
from agent.config import REPO_ROOT, get_settings
from agent.http import HttpTransport
from agent.runtime import make_session
from agent.mcp_client import McpClient
from agent.privacy import is_withheld, sanitise_file
from agent.redact import Redactor
from agent.safe_reads import list_all
from agent.trace import Trace

FIXTURE_ROOT = REPO_ROOT / "harness" / "fixtures"
ITEM_FIELDS = ("id", "code", "name", "_display", "status", "design_file_id", "design_bom_id", "company_id", "_permissions", "_readonly_fields")
PARTY_FIELDS = ("id", "_display", "name", "company_id")
ME_FIELDS = ("id", "email", "name", "roles", "allowed_apps", "company_id")
# STRIDE I2: an allow-list, so share_token, actor_ip and any field the platform adds later are never saved.
ACCESS_LOG_FIELDS = ("id", "file_id", "folder_id", "action", "actor_name", "actor_email", "created_at", "created_by",
                     "details", "_display", "_file_id_display", "company_id", "_company_id_display", "_permissions",
                     "_can_create")
CAPTURE_NAME = re.compile(r"\d{4}-\d{2}-\d{2}")
MIN_TITLE_CHARS = 6         # shorter withheld filenames are too generic to search for
MIN_DESCRIPTION_CHARS = 20  # shorter descriptions ("Signed copy") would match unrelated text

CanList = Callable[[str], bool]


def _pick(row: dict[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
    return {f: row.get(f) for f in fields if f in row}


def capture(business: str, out_root: Path = FIXTURE_ROOT) -> Path:
    settings = get_settings(business)
    trace = Trace(None, Redactor(settings.secrets()))
    session = make_session(HttpTransport(settings.base_url), settings, trace, "live")
    mcp = McpClient(session, trace)
    mcp.initialize()
    tools = mcp.list_tools()
    _status, overview = session.request("GET", "/api/drive/records/overview")
    _status, office = session.request("GET", "/api/agent/office")
    seat = [s for s in (office or {}).get("seats", []) if s.get("seat_number") == 20] if isinstance(office, dict) else []
    people = mcp.call("endpoint.people_directory", {}) if "endpoint.people_directory" in {t["name"] for t in tools} else {}
    can_list = Catalog.from_tools(tools).can_list
    raw_files = list_all(mcp, "FileAttachment.list")
    open_ids = frozenset(r["id"] for r in raw_files if not is_withheld(r, can_list))
    placeholders = {r["id"]: sanitise_file(r, can_list)["filename"] for r in raw_files if r["id"] not in open_ids}
    fixture = {
        "business": business,
        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "me": _pick(session.me(), ME_FIELDS),
        "tools": tools,
        "tables": {
            "FileAttachment": [sanitise_file(r, can_list) for r in raw_files],
            "DriveFolder": list_all(mcp, "DriveFolder.list"),
            "Item": [_pick(r, ITEM_FIELDS) for r in list_all(mcp, "Item.list")],
            "Party": [_pick(r, PARTY_FIELDS) for r in list_all(mcp, "Party.list")],
            "DriveAccessLog": [sanitise_access_log(r, open_ids, placeholders) for r in list_all(mcp, "DriveAccessLog.list")],
            "AgentEscalation": [], "AgentSession": [],
        },
        "people_directory": ((people or {}).get("result") or {}).get("items", []),
        "rest": {"/api/drive/records/overview": sanitise_overview(overview, open_ids), "/api/agent/office": {"seats": seat}},
    }
    # STRIDE I2: mask our own secrets everywhere except the tool schemas (their `password` keys feed tool_hash).
    redact = Redactor([*settings.secrets(), session.token])
    fixture = {k: v if k == "tools" else redact(v) for k, v in fixture.items()}
    refuse_withheld_text(fixture, raw_files, can_list)
    return save(fixture, out_root / business / datetime.now(timezone.utc).strftime("%Y-%m-%d"))  # STRIDE T8: UTC date


def sanitise_access_log(row: dict[str, Any], open_ids: frozenset[str], placeholders: dict[str, str]) -> dict[str, Any]:
    """STRIDE I2: keep ACCESS_LOG_FIELDS only; a row about a withheld or unknown file loses its title and details."""
    out = _pick(row, ACCESS_LOG_FIELDS)
    file_id = row.get("file_id")
    if file_id in open_ids:
        return out
    placeholder = placeholders.get(file_id) or (f"withheld-attachment-{str(file_id)[:8]}.pdf" if file_id else None)
    return {**out, "_file_id_display": placeholder, "_display": placeholder, "details": None}


def sanitise_overview(overview: Any, open_ids: frozenset[str]) -> Any:
    """STRIDE I2: the overview's `largest` list names files; keep only files this seat may show."""
    if not isinstance(overview, dict) or not isinstance(overview.get("largest"), list):
        return overview
    return {**overview, "largest": [e for e in overview["largest"] if isinstance(e, dict) and e.get("id") in open_ids]}


def refuse_withheld_text(fixture: dict[str, Any], raw_files: list[dict[str, Any]], can_list: CanList) -> None:
    """STRIDE I2: last check before saving: no withheld title or description may appear anywhere outside `tools`."""
    body = json.dumps({k: v for k, v in fixture.items() if k != "tools"}, ensure_ascii=False)
    public = [str(r[f]) for r in raw_files if not is_withheld(r, can_list) for f in ("filename", "description") if r.get(f)]
    for row in (r for r in raw_files if is_withheld(r, can_list)):
        shown = sanitise_file(row, can_list)
        for field, minimum in (("filename", MIN_TITLE_CHARS), ("description", MIN_DESCRIPTION_CHARS)):
            text = str(row.get(field) or "")
            if len(text) < minimum or text == shown.get(field) or any(text in p for p in public):
                continue
            if json.dumps(text, ensure_ascii=False)[1:-1] in body:
                raise RuntimeError(f"capture refused: the {field} of withheld file {row.get('id')} would be saved; "
                                   "nothing was written")


def fixture_hash(fixture: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(_stable(fixture), sort_keys=True).encode()).hexdigest()[:16]


def tool_hash(fixture: dict[str, Any]) -> str:
    return Catalog.from_tools(fixture["tools"]).hash()


def save(fixture: dict[str, Any], folder: Path) -> Path:
    body = json.dumps(fixture, indent=1, ensure_ascii=False, sort_keys=True)
    manifest = {
        "business": fixture["business"], "captured_at": fixture["captured_at"],
        "counts": {k: len(v) for k, v in fixture["tables"].items()} | {"tools": len(fixture["tools"])},
        "tool_hash": tool_hash(fixture),
        "fixture_hash": fixture_hash(fixture),
    }
    folder.mkdir(parents=True, exist_ok=True)
    _write_all(folder, {"fixture.json": body, "manifest.json": json.dumps(manifest, indent=2)})
    return folder


def _write_all(folder: Path, files: dict[str, str]) -> None:
    """STRIDE D4: write every file in full beside its final name, then swap them all in.

    A crash leaves either the old files or a pair that load() refuses, never a half-written file."""
    staged = []
    for name, text in files.items():
        tmp = folder / f"{name}.tmp"
        tmp.write_text(text, encoding="utf-8")
        staged.append((tmp, folder / name))
    for tmp, final in staged:
        os.replace(tmp, final)


def _stable(fixture: dict[str, Any]) -> dict[str, Any]:
    """Content that should hash the same when nothing on the platform changed (load()'s _dir/_manifest excluded)."""
    return {k: v for k, v in fixture.items() if k not in ("captured_at", "rest") and not k.startswith("_")}


def latest_dir(business: str, root: Path = FIXTURE_ROOT) -> Path:
    dated = sorted(p for p in (root / business).glob("*") if _is_capture(p))
    if not dated:
        raise FileNotFoundError(f"No fixture for {business}. Run: python -m harness capture {business}")
    later = sorted(p.name for p in (root / business).glob("*") if _is_future(p) and p.name > dated[-1].name)
    if later:  # STRIDE T8: never fall back to an older capture without saying so
        print(f"warning: skipped fixture folder(s) dated in the future: {', '.join(later)}; using {dated[-1].name}",
              file=sys.stderr)
    return dated[-1]


def _is_capture(folder: Path) -> bool:
    """STRIDE T8: only folders named like capture() names them (YYYY-MM-DD, not in the future) are baselines.

    An incomplete one is still picked, so load() refuses it loudly instead of falling back to an older capture."""
    if not CAPTURE_NAME.fullmatch(folder.name) or _is_future(folder):
        return False
    try:
        date.fromisoformat(folder.name)
    except ValueError:
        return False
    return any((folder / name).exists() for name in ("fixture.json", "manifest.json"))


def _is_future(folder: Path) -> bool:
    """Dated after tomorrow (UTC). One day of slack: a teammate's capture may be named by a local date ahead of UTC."""
    try:
        return date.fromisoformat(folder.name) > datetime.now(timezone.utc).date() + timedelta(days=1)
    except ValueError:
        return False


def load(business: str, fixture_dir: Path | None = None) -> dict[str, Any]:
    folder = fixture_dir or latest_dir(business)
    data = _read_json(folder / "fixture.json", business)
    manifest = _read_json(folder / "manifest.json", business)
    _verify(folder, data, manifest, business)
    data["_dir"] = str(folder)
    data["_manifest"] = manifest
    return data


def _read_json(path: Path, business: str) -> Any:
    """STRIDE D4: a missing or cut-off file names itself and the fix, instead of a bare decode error."""
    fix = f"re-capture (python -m harness capture {business}) or delete {path.parent} if a capture was interrupted"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise FileNotFoundError(f"{path} is missing; {fix}") from None
    except ValueError as err:
        raise ValueError(f"{path} is not valid JSON ({err}); {fix}") from None


def _verify(folder: Path, data: Any, manifest: Any, business: str) -> None:
    """STRIDE T8: a fixture is a baseline only while it still matches the hashes saved beside it."""
    try:
        wrong = [name for name, stored, actual in (("fixture_hash", manifest.get("fixture_hash"), fixture_hash(data)),
                                                    ("tool_hash", manifest.get("tool_hash"), tool_hash(data)))
                 if stored != actual]
    except (AttributeError, KeyError, TypeError) as err:
        raise ValueError(f"{folder} does not hold a fixture ({type(err).__name__}: {err}); "
                         f"re-capture: python -m harness capture {business}") from None
    if wrong:
        raise ValueError(f"{folder}: fixture.json does not match manifest.json ({', '.join(wrong)}); a hand-edited or "
                         f"half-written fixture is never used. Re-capture: python -m harness capture {business}")
