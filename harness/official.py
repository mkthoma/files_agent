"""The official server run (Release 8.1): `python -m harness official`.

The AgentSwitch runner checks out the saved branch, runs this command against a FRESH copy
of the instance (writes are thrown away afterwards), and reads `results.json`. It provides:
  AGENTSWITCH_BASE_URL, AGENTSWITCH_TOKEN, AGENTSWITCH_INSTANCE   (platform; no password)
  OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL                   (model; no own key)

What this command does:
1. Captures a fresh fixture from the instance copy (read-only), so pre-flight's
   "fixture older than 24 hours" rule can never block the write task.
2. Runs every live-safe task once with the platform model: the read-mode tasks without
   fake-server faults, plus TI2L (the one `live_write = true` task). The write guard,
   allow-list, pre-flight, snapshot and restore all stay on, exactly as in a live run.
3. Maps the score to the runner's schema and writes `results.json`.

Rehearse locally, offline and without any key: `python -m harness official --dry-run`.
"""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from agent.config import REPO_ROOT, RUNS_DIR
from agent.runtime import WritesNotAllowed
from agent.textsafe import one_line, printable
from harness import fixtures
from harness.runner import RunRefused, run_task
from harness.score import score_set, write_score
from harness.tasks import Task, load_all

RESULTS_PATH = REPO_ROOT / "results.json"
MAX_EVIDENCE = 450


def pick_tasks(tasks: dict[str, Task]) -> list[Task]:
    """Every task a live(-like) run accepts: read mode without fake-server faults or planted
    files, plus the live_write task. The offline-only tasks stay out by design, not by error."""
    return [t for t in tasks.values()
            if not t.faults and not t.extra_files and (t.mode == "read" or t.live_write)]


def to_results(score: dict[str, Any], tasks: dict[str, Task], instance: str, model: str,
               skipped: dict[str, str]) -> dict[str, Any]:
    rows = []
    for tid, entry in score["tasks"].items():
        failures = "; ".join(f"{run}: {why}" for run, why in entry["failures"].items())
        passed = bool(entry["pass_all"])
        task = tasks.get(tid)
        rows.append({
            "id": f"{instance}:{tid}",
            "title": one_line(f"{task.question} — {task.notes}" if task and task.notes else
                              (task.question if task else tid), 120),
            "passed": passed,
            "score": round(entry["passed"] / entry["runs"], 3) if entry["runs"] else 0.0,
            "evidence": one_line(failures, MAX_EVIDENCE) if failures else
                        f"verified from database state after the run ({entry['runs']} run(s), "
                        f"{entry['passed']} passed)",
        })
    for tid, why in skipped.items():
        rows.append({"id": f"{instance}:{tid}", "title": tasks[tid].question, "passed": False,
                     "score": 0.0, "evidence": one_line(f"did not run: {why}", MAX_EVIDENCE)})
    total = score["total"]
    summary = (f"{instance}: {total['tasks_passing_all']}/{total['tasks']} tasks pass on every run "
               f"(model {model}; pass/fail judged from database state, not from the agent's text)")
    return {"tasks": rows, "summary": summary}


def check_results(results: dict[str, Any]) -> list[str]:
    """The runner's format, checked before writing: wrong shapes show up here, not on the server."""
    problems = []
    rows = results.get("tasks")
    if not isinstance(rows, list) or not 1 <= len(rows) <= 200:
        problems.append("tasks must be a list of 1-200 entries")
    for n, row in enumerate(rows or []):
        if not isinstance(row.get("id"), str) or not row.get("id"):
            problems.append(f"tasks[{n}].id must be a non-empty string")
        if not isinstance(row.get("passed"), bool):
            problems.append(f"tasks[{n}].passed must be true or false")
        score = row.get("score")
        if score is not None and not (isinstance(score, (int, float)) and 0 <= score <= 1):
            problems.append(f"tasks[{n}].score must be 0-1")
    if not isinstance(results.get("summary"), str):
        problems.append("summary must be a string")
    return problems


def run_official(dry_run: bool, model_kind: str | None) -> int:
    if dry_run:
        target, model = "fake", model_kind or "scripted"
        instance = "keystone"
    else:
        missing = [k for k in ("AGENTSWITCH_BASE_URL", "AGENTSWITCH_TOKEN") if not os.environ.get(k)]
        if missing:
            print(f"refused: {', '.join(missing)} not set. This command is for the official runner; "
                  "rehearse with --dry-run.")
            return 2
        target, model = "live", model_kind or "openai"
        instance = os.environ.get("AGENTSWITCH_INSTANCE", "keystone")
        # The official copy is disposable (writes are thrown away server-side), so the second
        # write switch is deliberately on for this one command. Every other guard stays active.
        os.environ["AS_ALLOW_WRITES"] = "1"
    tasks = load_all()
    if instance != "keystone":
        results = {"tasks": [{"id": f"{instance}:scenario", "title": "Seat 20 scenario data exists here",
                              "passed": False, "score": 0.0,
                              "evidence": "Seat 20's graded scenario (Incoming, part J-BRKT-04) lives on keystone only"}],
                   "summary": f"{instance}: not applicable; run the keystone instance"}
        RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(results["summary"])
        return 0
    if not dry_run:
        try:
            print(f"fixture: capturing a fresh one from {instance}...", flush=True)
            fixtures.capture(instance)
        except Exception as err:  # the read-only tasks can still run and score
            print(printable(f"fixture capture failed ({type(err).__name__}: {err}); "
                            "the write task may be blocked by pre-flight"), flush=True)
    set_dir = RUNS_DIR / f"{datetime.now():%Y%m%d-%H%M%S}-official"
    skipped: dict[str, str] = {}
    for task in pick_tasks(tasks):
        try:
            run_task(task, target=target, model_kind=model, set_dir=set_dir, repeat=1, live_apply=True)
            print(f"{task.id}: done", flush=True)
        except (RunRefused, WritesNotAllowed) as err:
            skipped[task.id] = str(err)
            print(printable(f"{task.id}: SKIPPED - {err}"), flush=True)
        except Exception as err:  # keep going; the missing run file scores as failed
            print(printable(f"{task.id}: ERROR - {type(err).__name__}: {err}"), flush=True)
    score = score_set(set_dir)
    write_score(set_dir, score)
    results = to_results(score, tasks, instance, model, skipped)
    problems = check_results(results)
    if problems:
        print(printable("results.json would be malformed:\n  - " + "\n  - ".join(problems)))
        return 1
    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    for row in results["tasks"]:
        print(printable(f"[{'PASS' if row['passed'] else 'FAIL'}] {row['id']}: {row['evidence'][:160]}"), flush=True)
    print(printable(results["summary"]))
    print(f"results: {RESULTS_PATH}")
    print(f"run set: {set_dir}")
    return 0
