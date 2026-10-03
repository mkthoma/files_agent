"""Make text that other teams control safe to print, store or put in a report (STRIDE S2, T2).

Platform text (filenames, descriptions, party and folder names) can hold terminal escape
sequences, bidi or zero-width characters and markup. Clean it where it leaves the agent:
the console, permanent escalations and file notes, and report.md.
"""
from __future__ import annotations

import re
import unicodedata

# Control (Cc), format (Cf: bidi overrides, zero-width, tag characters, the BOM), private-use,
# surrogate and unassigned characters, plus line and paragraph separators: they hide, reorder
# or break text. Hangul fillers render as blank space, so they are dropped too.
_DROP_CATEGORIES = {"Cc", "Cf", "Co", "Cs", "Cn", "Zl", "Zp"}
_INVISIBLE = {0x115F, 0x1160, 0x3164, 0xFFA0}
_SPACES = re.compile(r"\s+")


def _keep(ch: str, keep_newlines: bool) -> bool:
    if ch in "\n\t":
        return keep_newlines
    return unicodedata.category(ch) not in _DROP_CATEGORIES and ord(ch) not in _INVISIBLE


def printable(text: object) -> str:
    """Drop control characters (ESC included) and invisible characters; keep tabs and newlines."""
    return "".join(ch for ch in str(text or "") if _keep(ch, keep_newlines=True))


def one_line(text: object, limit: int = 200) -> str:
    """printable(), then fold every run of whitespace into one space and cap the length."""
    cleaned = _SPACES.sub(" ", "".join(ch if _keep(ch, keep_newlines=False) else " " for ch in str(text or ""))).strip()
    return cleaned if len(cleaned) <= limit else cleaned[: limit - 1] + "…"


def md_cell(text: object, limit: int = 300) -> str:
    """one_line() for a Markdown table cell: escape the pipe, angle brackets and backticks."""
    return one_line(text, limit).replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;").replace("`", "\\`")
