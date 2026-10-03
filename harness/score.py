"""Scoring (T4.6) and rescoring (T4.8). Reads only the run files; never calls the model or the platform.

A task passes only if every one of its runs passes (pass^k). Scores use the
task definition stored in each run's manifest, so rescoring is reproducible.
`expected.json` (written by `harness run` before each task starts) lists how many
runs each task should have; a run file that is missing counts as a failed run, and
so does one that can't be read or sits in another task's folder.
score.json also records where the runs came from (target, model, commit) and whether
each task's stored definition still matches its task file. Rescore proves the scorer
is deterministic; it can't prove the run files were never edited. That definition check
reads today's task files, so rescore leaves it out of the comparison and warns instead.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from agent.textsafe import md_cell, one_line
from harness.manifest import git_state
from harness.tasks import TASK_DIR, TASK_ID_RE, Task, load_task
from harness.verifiers import Run, RunFileError, load_run, verify

EXPECTED_FILE = "expected.json"
GRADED_FIELDS = ("question", "business", "mode", "repeat", "passes", "faults", "extra_files", "live_allowlist", "expect")
STALE_WARNING = "judged against a task definition that differs from today's file in harness/tasks"
DETAIL_LIMIT = 1000  # characters per failure detail in report.md (score.json keeps the full text)


def run_files(set_dir: Path) -> list[Path]:
    return sorted(p for p in set_dir.glob("*/*.jsonl"))


def load_expected(set_dir: Path) -> dict[str, int]:
    path = set_dir / EXPECTED_FILE
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def expect_runs(set_dir: Path, task_id: str, count: int) -> None:
    """Record, before a task runs, how many run files it must leave behind."""
    set_dir.mkdir(parents=True, exist_ok=True)
    expected = {**load_expected(set_dir), task_id: count}
    (set_dir / EXPECTED_FILE).write_text(json.dumps(expected, indent=2, sort_keys=True), encoding="utf-8")


def _new_entry() -> dict[str, Any]:
    return {"runs": 0, "passed": 0, "usd": 0.0, "failures": {}}


def _add_missing(set_dir: Path, tasks: dict[str, dict[str, Any]]) -> None:
    for task_id, count in load_expected(set_dir).items():
        entry = tasks.setdefault(task_id, _new_entry())
        for n in range(1, count + 1):
            if not (set_dir / task_id / f"{n}.jsonl").exists():
                entry["runs"] += 1
                entry["failures"][f"{n}.jsonl"] = ["missing: no run file was written (the run crashed)"]


def _misfiled(path: Path, run: Run, expected: dict[str, int]) -> list[str]:
    """STRIDE R2: a run counts only in its own task folder, under its own repeat number, for a task the set promised."""
    task_id, repeat = run.manifest["task"].get("id"), run.manifest.get("repeat_index")
    problems = []
    if task_id != path.parent.name:
        problems.append(f"misfiled: this run is of task {task_id!r}, not {path.parent.name}")
    if str(repeat) != path.stem:
        problems.append(f"misfiled: this run is repeat {repeat!r}, not {path.stem}")
    if expected and path.parent.name not in expected:
        problems.append(f"unexpected: {EXPECTED_FILE} promises no runs of {path.parent.name}")
    return problems


def _judge(path: Path, expected: dict[str, int]) -> tuple[list[str], float, dict[str, Any] | None]:
    """One run file's failed checks, cost and manifest. STRIDE D3: an unreadable file is one failed run."""
    try:
        run = load_run(path)
    except RunFileError as err:
        return [str(err)], 0.0, None
    failed = _misfiled(path, run, expected) + [f"{c.name}: {c.detail}" for c in verify(run) if not c.ok]
    usd = sum((p.get("ledger") or {}).get("usd", 0) for p in run.result.get("passes") or [])
    return failed, usd, run.manifest


def _graded(task: dict[str, Any]) -> str:
    """The task fields that decide how a run is judged, as canonical JSON (a notes edit doesn't count)."""
    full = Task.from_dict(task).to_dict()
    return json.dumps({k: full[k] for k in GRADED_FIELDS}, sort_keys=True, default=str)


def _definition(task_id: str, manifests: list[dict[str, Any]]) -> str:
    """STRIDE R2: does every run's stored definition match harness/tasks/<id>.toml today? Shown, never scored."""
    if not manifests or not TASK_ID_RE.fullmatch(task_id):
        return "unknown"
    try:
        current = _graded(load_task(TASK_DIR / f"{task_id}.toml").to_dict())
    except (OSError, ValueError):
        return "unknown"
    return "current" if all(_graded(m["task"]) == current for m in manifests) else "stale"


def _distinct(values: Any) -> list[str]:
    return sorted({str(v) for v in values if v not in (None, "")})


def _warnings(prov: dict[str, Any], tasks: dict[str, dict[str, Any]]) -> list[str]:
    out = [f"MIXED {key}: {', '.join(prov[key])}" for key in ("targets", "models", "commits") if len(prov[key]) > 1]
    if prov["dirty_runs"]:
        changed = ", ".join(prov["changed_files"][:10]) or "not recorded"
        out.append(f"{prov['dirty_runs']} of {prov['runs']} runs came from a working tree that differs from its commit "
                   f"(changed: {changed})")
    stale = [tid for tid, e in tasks.items() if e["definition"] == "stale"]
    if stale:
        out.append(f"{STALE_WARNING} (an older definition, or an edited run file): {', '.join(sorted(stale))}")
    return out


def _provenance(manifests: list[dict[str, Any]], tasks: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """STRIDE R9: which target, model, commit, fixture and tools made the runs, so a report describes itself."""
    gits = [m.get("git") or {} for m in manifests]
    prov = {
        "runs": len(manifests),
        "targets": _distinct(m.get("target") for m in manifests),
        "models": _distinct(m.get("model") for m in manifests),
        "commits": _distinct(g.get("commit") for g in gits),
        "dirty_runs": sum(1 for g in gits if g.get("dirty", True)),
        "changed_files": _distinct(f for m in manifests for f in m.get("changed_files") or [])[:50],
        "fixtures": _distinct((m.get("fixture") or {}).get("hash") for m in manifests),
        "tool_hashes": _distinct(m.get("tool_hash") for m in manifests),
    }
    prov["warnings"] = _warnings(prov, tasks)
    return prov


def score_set(set_dir: Path) -> dict[str, Any]:
    tasks: dict[str, dict[str, Any]] = {}
    manifests: dict[str, list[dict[str, Any]]] = {}
    expected = load_expected(set_dir)
    for path in run_files(set_dir):
        entry = tasks.setdefault(path.parent.name, _new_entry())
        failed, usd, manifest = _judge(path, expected)
        entry["runs"] += 1
        entry["passed"] += int(not failed)
        entry["usd"] = round(entry["usd"] + usd, 6)
        if failed:
            entry["failures"][path.name] = failed
        if manifest is not None:
            manifests.setdefault(path.parent.name, []).append(manifest)
    _add_missing(set_dir, tasks)
    for task_id, entry in tasks.items():
        entry["pass_all"] = entry["runs"] > 0 and entry["passed"] == entry["runs"]
        entry["definition"] = _definition(task_id, manifests.get(task_id, []))
    total = {"tasks": len(tasks), "tasks_passing_all": sum(e["pass_all"] for e in tasks.values()),
             "usd": round(sum(e["usd"] for e in tasks.values()), 6)}
    every = [m for ms in manifests.values() for m in ms]
    return {"set": set_dir.name, "tasks": dict(sorted(tasks.items())), "total": total,
            "provenance": _provenance(every, tasks)}


def write_score(set_dir: Path, score: dict[str, Any]) -> Path:
    (set_dir / "score.json").write_text(json.dumps(score, indent=2, sort_keys=True), encoding="utf-8")
    (set_dir / "report.md").write_text(render(score), encoding="utf-8")
    return set_dir / "score.json"


def _provenance_lines(prov: dict[str, Any]) -> list[str]:
    def short(values: list[str], width: int) -> str:
        return md_cell(", ".join(v[:width] for v in values) or "none")
    line = (f"Target: {short(prov['targets'], 40)}. Model: {short(prov['models'], 40)}. "
            f"Commit: {short(prov['commits'], 12)} ({prov['dirty_runs']} of {prov['runs']} runs from a modified tree). "
            f"Fixture: {short(prov['fixtures'], 16)}. Tools: {short(prov['tool_hashes'], 16)}.")
    return [line, *[f"**Warning:** {md_cell(w, DETAIL_LIMIT)}" for w in prov["warnings"]], ""]


def render(score: dict[str, Any]) -> str:
    lines = [f"# Score: {one_line(score['set'])}", ""]
    if score.get("provenance"):
        lines += _provenance_lines(score["provenance"])
    lines += ["| Task | Runs | Passed | pass^k | Cost (USD) |", "|---|---|---|---|---|"]
    for tid, e in score["tasks"].items():
        lines.append(f"| {md_cell(tid)} | {e['runs']} | {e['passed']} | {'PASS' if e['pass_all'] else 'FAIL'} | {e['usd']:.4f} |")
    t = score["total"]
    lines += ["", f"**{t['tasks_passing_all']} of {t['tasks']} tasks pass on every run.** Total cost ${t['usd']:.4f}.", ""]
    for tid, e in score["tasks"].items():
        for run_name, failed in e["failures"].items():
            # STRIDE S2: platform text in a failure can't add lines, markup or terminal escapes to the report
            lines.append(f"- {md_cell(tid)}/{md_cell(run_name)}: " + "; ".join(md_cell(f, DETAIL_LIMIT) for f in failed))
    return "\n".join(lines) + "\n"


def _warn_if_code_moved(score: dict[str, Any]) -> None:
    """STRIDE R9: say so (stderr, not a failure) when the rescoring code may differ from the code that ran."""
    prov, now = score.get("provenance") or {}, git_state()
    reasons = []
    if prov.get("commits") and prov["commits"] != [now["commit"]]:
        reasons.append(f"the runs came from {', '.join(c[:12] for c in prov['commits'])}, HEAD is {now['commit'][:12]}")
    if prov.get("dirty_runs"):
        reasons.append(f"{prov['dirty_runs']} run(s) came from a modified working tree")
    if now["dirty"]:
        reasons.append("the working tree is modified now")
    if reasons:
        print("warning: rescore may not use the code that made these runs: " + "; ".join(reasons), file=sys.stderr)


def _from_runs_only(score: Any) -> Any:
    """STRIDE R2: a score without the parts that read today's task files (each task's `definition` flag and the
    stale-definition warning), so a later task-file edit never makes an untouched set rescore as DIFFERENT."""
    data = json.loads(json.dumps(score, sort_keys=True))
    if not isinstance(data, dict):
        return data
    for entry in (data.get("tasks") or {}).values():
        if isinstance(entry, dict):
            entry.pop("definition", None)
    prov = data.get("provenance")
    if isinstance(prov, dict) and isinstance(prov.get("warnings"), list):
        prov["warnings"] = [w for w in prov["warnings"] if not str(w).startswith(STALE_WARNING)]
    return data


def rescore(set_dir: Path) -> tuple[bool, dict[str, Any]]:
    """Recompute from disk and compare with the saved score.json (see _from_runs_only)."""
    fresh = score_set(set_dir)
    saved_path = set_dir / "score.json"
    saved = json.loads(saved_path.read_text(encoding="utf-8")) if saved_path.exists() else None
    _warn_if_code_moved(fresh)
    stale = sorted(tid for tid, e in fresh["tasks"].items() if e.get("definition") == "stale")
    if stale:
        print(f"warning: stale definition: {', '.join(stale)} differ from today's harness/tasks files", file=sys.stderr)
    return saved is not None and _from_runs_only(saved) == _from_runs_only(fresh), fresh
