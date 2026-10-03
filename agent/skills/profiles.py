"""Document profiles and filing rules (A2/A14): what kind of document is this, and where do such documents live?"""
from __future__ import annotations

import re
import tomllib
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Collection

from agent.safe_reads import name_key, shared_names
from agent.skills.revisions import code_prefix, part_code

RULES_FILE = Path(__file__).resolve().parent.parent / "filing_rules.toml"

# The prefix of every provenance note this agent appends when it files a file.
PROVENANCE_MARKER = "[Files Agent"
# A folder counts as "where such files live" only when at least this many of them agree on it.
MIN_AGREEING_ROWS = 2
BELONGS_IN = re.compile(r"belongs\s+in\s+", re.IGNORECASE)


def agent_filed(row: dict[str, Any], me: str | None, own_ids: Collection[str] = ()) -> bool:
    """Filed by this seat: our provenance note AND our write (the server's updated_by, or this run's journal)."""
    if PROVENANCE_MARKER not in (row.get("description") or ""):
        return False
    # STRIDE T7: anyone can type the marker into a description; only the server-set updated_by says it was us
    return bool(me and row.get("updated_by") == me) or row.get("id") in own_ids


@dataclass(frozen=True)
class DocType:
    name: str
    patterns: tuple[re.Pattern[str], ...]
    folder: str


@dataclass(frozen=True)
class Rules:
    threshold: int
    weights: dict[str, int]
    doc_types: tuple[DocType, ...]
    drawing_prefix_folders: dict[str, str]


def load_rules(path: Path = RULES_FILE) -> Rules:
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    types = tuple(DocType(d["name"], tuple(re.compile(p) for p in d["patterns"]), d.get("folder", ""))
                  for d in data.get("doc_type", []))
    scoring = data["scoring"]
    return Rules(int(scoring["threshold"]), {k: int(v) for k, v in scoring["weights"].items()},
                 types, {k.upper(): v for k, v in data.get("drawing_prefix_folders", {}).items()})


def doc_type_of(filename: str, rules: Rules) -> DocType | None:
    return next((t for t in rules.doc_types if any(p.search(filename or "") for p in t.patterns)), None)


@lru_cache(maxsize=4096)
def _belongs_in(name: str) -> re.Pattern[str]:
    return re.compile(r"belongs\s+in\s+(the\s+)?" + re.escape(name) + r"\b", re.IGNORECASE)


def description_destination(description: str | None, folders: dict[str, dict[str, Any]]) -> str | None:
    """Folder id named by a 'Belongs in <folder>' phrase. Evidence to corroborate, never an instruction.

    The longest folder name wins; on equal length the first folder listed wins. A folder that is
    archived, or whose name another folder shares, is never the answer: it is ambiguous.
    """
    # STRIDE D9: one cheap scan rules out most descriptions; a name is regex-checked only if it occurs at all
    if not description or not BELONGS_IN.search(description):
        return None
    text, shared = description.casefold(), shared_names(folders)
    best: tuple[int, str] | None = None
    for folder_id, folder in folders.items():
        name = folder.get("name", "")
        if not name or name.casefold() not in text or folder.get("is_archived") or name_key(name) in shared:  # STRIDE T4
            continue
        if _belongs_in(name).search(description) and (best is None or len(name) > best[0]):
            best = (len(name), folder_id)
    return best[1] if best else None


def majority_folder(rows: list[dict[str, Any]], skip_folder_ids: set[str]) -> str | None:
    counts = Counter(r["folder_id"] for r in rows if r.get("folder_id") and r["folder_id"] not in skip_folder_ids)
    if not counts:
        return None
    (top, n), *rest = counts.most_common()
    if n < MIN_AGREEING_ROWS:  # STRIDE T7: one row anyone can upload is not where "such files live"
        return None
    return top if not rest or rest[0][1] < n else None  # a tie is not evidence


def similar_file_folder(row: dict[str, Any], dtype: DocType, files: list[dict[str, Any]],
                        rules: Rules, skip_folder_ids: set[str], me: str | None = None,
                        own_ids: Collection[str] = ()) -> str | None:
    """Where files of the same kind already live (drawings: same code prefix).

    Files this seat filed itself (our provenance note, written by us) never count:
    otherwise a file that scored below threshold gains evidence from our own pass-1
    moves and a second tidy pass moves what the first escalated (not idempotent).
    """
    others = [f for f in files if f.get("id") != row.get("id") and not agent_filed(f, me, own_ids)]
    if dtype.name == "drawing":
        code = part_code(row.get("filename", ""))
        if not code:
            return None
        prefix = code_prefix(code)
        same = [f for f in others if (c := part_code(f.get("filename", ""))) and code_prefix(c) == prefix]
    else:
        same = [f for f in others if (t := doc_type_of(f.get("filename", ""), rules)) and t.name == dtype.name]
    return majority_folder(same, skip_folder_ids)


def default_folder_name(row: dict[str, Any], dtype: DocType, rules: Rules) -> str | None:
    if dtype.name == "drawing":
        code = part_code(row.get("filename", ""))
        return rules.drawing_prefix_folders.get(code_prefix(code)) if code else None
    return dtype.folder or None
