"""Answer writer (T3.2): the final answer plus a record trail, and a check of every cited id."""
from __future__ import annotations

import re
from typing import Any

from agent.records import DecisionRecord
from agent.textsafe import one_line, printable

UUID_RE = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.IGNORECASE)
LABEL_CHARS = 200


def cited_ids(text: str) -> list[str]:
    return sorted({m.lower() for m in UUID_RE.findall(text or "")})


def _trail_line(r: DecisionRecord) -> str:
    # STRIDE S2: labels are platform names or model arguments, so control and bidi characters are removed.
    label = one_line(r.target_label or "-", LABEL_CHARS)
    return f"- [{r.status}] {r.action}: {label}" + (f" ({one_line(r.target_id, LABEL_CHARS)})" if r.target_id else "")


def compose(model_text: str, records: list[DecisionRecord], seen_ids: set[str], stop_note: str = "") -> dict[str, Any]:
    """Append a record trail so every statement can be traced to a decision record.

    The trail is always appended, last and with its count, even when empty, so text the model wrote to look
    like a trail can never be the only or the last one shown (STRIDE S4). A stop note from the code
    (budget, turn cap, model error) is shown apart from the model's own words (STRIDE R6)."""
    trail = [_trail_line(r) for r in records
             if r.status != "info" or r.action in ("current_drawing", "superseded_drawing", "contradiction", "list")]
    parts = [printable(model_text).strip(), printable(stop_note).strip()]  # STRIDE S2: no escapes reach the console
    answer = "\n\n".join(p for p in parts if p)
    header = f"Record trail (added by the agent code; {len(trail)} record(s)):"
    answer += ("\n\n" if answer else "") + header + ("\n" + "\n".join(trail) if trail else " none")
    ids = cited_ids(answer)
    seen = {s.lower() for s in seen_ids}
    return {"answer": answer, "cited_ids": ids, "unverified_ids": [i for i in ids if i not in seen]}
