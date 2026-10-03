"""Harness command line.

  python -m harness list
  python -m harness capture keystone                   read-only fixture capture
  python -m harness run D1 TI1 [--target fake] [--model scripted] [--repeat 5] [--set NAME]
  python -m harness run all --target fake --model scripted
  python -m harness score [runs/<set>]                  (default: newest set)
  python -m harness rescore runs/<set>                  rebuild from disk; must match score.json
  python -m harness calibrate [runs/<set>]              does the harness catch injected faults?
  python -m harness smoke                               whole pipeline, offline, in one command
  python -m harness preflight                           live checks before a write run
  AS_ALLOW_WRITES=1 python -m harness restore runs/<set>/<task>/snapshot-1.json --target live --live-apply

Live write tasks need --target live, --live-apply AND AS_ALLOW_WRITES=1 (set in the shell,
not .env), run once, and are wrapped in pre-flight + snapshot + write journal + restore.
Tasks with fake-server faults or extra files never run live. Restore needs the write
journal saved beside the snapshot; --no-journal is the last resort when it is lost.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from agent import snapshot
from agent.config import KEYSTONE_INCOMING_ALLOWLIST, RUNS_DIR
from agent.runtime import WritesNotAllowed, build
from agent.textsafe import printable
from harness import fixtures, preflight
from harness.calibrate import calibrate
from harness.runner import RunRefused, planned_runs, run_task
from harness.score import expect_runs, load_expected, render, rescore, run_files, score_set, write_score
from harness.tasks import load_all

SET_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}")


def _newest_set() -> Path:
    sets = sorted((p for p in RUNS_DIR.glob("*") if p.is_dir() and p.name != "cli"), key=lambda p: p.stat().st_mtime)
    if not sets:
        raise SystemExit("No run sets yet. Run: python -m harness run all --target fake --model scripted")
    return sets[-1]


def cmd_list(_args: argparse.Namespace) -> int:
    for t in load_all().values():
        print(f"{t.id:5s} [{t.mode:5s}] x{t.repeat} passes={t.passes} {t.question}")
    return 0


def cmd_capture(args: argparse.Namespace) -> int:
    folder = fixtures.capture(args.business)
    print(f"fixture saved: {folder}")
    print((folder / "manifest.json").read_text(encoding="utf-8"))
    return 0


def _set_dir(args: argparse.Namespace) -> Path:
    """STRIDE R1: a run set is a plain folder name under runs/, so --set can never write anywhere else."""
    if not args.set:
        return RUNS_DIR / f"{datetime.now():%Y%m%d-%H%M%S}-{args.target}-{args.model}"
    set_dir = RUNS_DIR / args.set
    if not SET_NAME.fullmatch(args.set) or not set_dir.resolve().is_relative_to(RUNS_DIR.resolve()):
        raise SystemExit(f"--set must be a plain folder name under runs/ (letters, digits, '.', '_' or '-'), got {args.set!r}")
    return set_dir


def cmd_run(args: argparse.Namespace) -> int:
    if args.live_apply and args.target != "live":  # STRIDE S3: --live-apply never runs quietly on the fake server
        print("refused: --live-apply writes to the live platform, so it needs --target live", file=sys.stderr)
        return 3
    tasks = load_all()
    chosen = list(tasks) if args.tasks == ["all"] else args.tasks
    unknown = [t for t in chosen if t not in tasks]
    if unknown:
        raise SystemExit(f"Unknown task(s): {unknown}. See: python -m harness list")
    set_dir = _set_dir(args)
    for tid in chosen:
        try:
            count = planned_runs(tasks[tid], target=args.target, repeat=args.repeat, live_apply=args.live_apply,
                                 set_dir=set_dir)
        except (RunRefused, WritesNotAllowed) as err:
            print(printable(f"{tid}: SKIPPED - {err}"))
            continue
        expect_runs(set_dir, tid, count)  # a run that never writes its file will count as failed
        try:
            paths = run_task(tasks[tid], target=args.target, model_kind=args.model, set_dir=set_dir,
                             repeat=args.repeat, live_apply=args.live_apply)
            print(f"{tid}: {len(paths)} run file(s) written")
        except Exception as err:  # keep going: the other tasks still run and the score is still written
            print(printable(f"{tid}: ERROR - {type(err).__name__}: {err}"), file=sys.stderr)
    if not run_files(set_dir) and not load_expected(set_dir):
        print("No runs written (every task was skipped).")
        return 1
    score = score_set(set_dir)
    write_score(set_dir, score)
    print(printable(render(score)))
    print(f"run set: {set_dir}")
    return 0 if score["total"]["tasks_passing_all"] == score["total"]["tasks"] else 1


def cmd_score(args: argparse.Namespace) -> int:
    set_dir = Path(args.set) if args.set else _newest_set()
    score = score_set(set_dir)
    write_score(set_dir, score)
    print(printable(render(score)))
    return 0


def cmd_rescore(args: argparse.Namespace) -> int:
    same, fresh = rescore(Path(args.set))
    print("rescore IDENTICAL to score.json" if same else "rescore DIFFERS from score.json")
    if not same:
        print(printable(render(fresh)))
    return 0 if same else 1


def cmd_calibrate(args: argparse.Namespace) -> int:
    rows = calibrate(Path(args.set) if args.set else _newest_set())
    if not rows:
        print("No passing runs to calibrate against. Run some tasks first.")
        return 1
    for r in rows:
        print(f"{'caught ' if r['caught'] else 'MISSED '} {r['task']:5s} {r['mutant']:20s} expected {r['expected']}")
    missed = [r for r in rows if not r["caught"]]
    print(f"\n{len(rows) - len(missed)} of {len(rows)} injected faults caught.")
    return 0 if not missed else 1


def cmd_smoke(_args: argparse.Namespace) -> int:
    tasks = load_all()
    set_dir = RUNS_DIR / f"{datetime.now():%Y%m%d-%H%M%S}-smoke"
    steps = []
    for tid in ("D1", "TI1", "TI2"):
        run_task(tasks[tid], target="fake", model_kind="scripted", set_dir=set_dir, repeat=1)
    score = score_set(set_dir)
    write_score(set_dir, score)
    steps.append(("run + score", score["total"]["tasks_passing_all"] == score["total"]["tasks"]))
    steps.append(("rescore identical", rescore(set_dir)[0]))
    rows = calibrate(set_dir)
    steps.append(("calibration catches faults", bool(rows) and all(r["caught"] for r in rows)))
    for name, ok in steps:
        print(f"{'OK  ' if ok else 'FAIL'} {name}")
    print(f"run set: {set_dir}")
    return 0 if all(ok for _n, ok in steps) else 1


def cmd_routes(args: argparse.Namespace) -> int:
    """T3.1: does each question in harness/tasks/routes.toml reach the skill YOU expect? (offline, first turn only)"""
    import tomllib
    from agent.loop import SYSTEM_PROMPT, tool_definitions
    from agent.runtime import make_model
    from harness.tasks import TASK_DIR
    routes = tomllib.loads((TASK_DIR / "routes.toml").read_text(encoding="utf-8"))["route"]
    rt = build(args.business, "fake", "plan", None)
    tools, _ = tool_definitions(rt.catalog)
    model = make_model(args.model, rt.settings)
    ok = 0
    for r in routes:
        resp = model.create(SYSTEM_PROMPT, [{"role": "user", "content": r["question"]}], tools)
        got = next((b["name"] for b in resp.get("content", []) if b.get("type") == "tool_use"), "(no tool)")
        ok += got == r["expected_skill"]
        print(f"{'OK  ' if got == r['expected_skill'] else 'MISS'} {r['expected_skill']:16s} got {got:16s} | {r['question']}")
    print(f"\n{ok} of {len(routes)} routed as expected.")
    return 0 if ok == len(routes) else 1


def cmd_preflight(args: argparse.Namespace) -> int:
    try:
        fixture = fixtures.load(args.business)
    except (OSError, ValueError) as err:  # STRIDE T8: a broken or hand-edited fixture is a clean refusal
        print(printable(f"pre-flight FAILED:\n  - the fixture can't be used: {err}"))
        return 1
    rt = build(args.business, "live", "plan", None)
    problems, warnings = preflight.assess(rt, fixture)
    print(printable("pre-flight OK" if not problems else "pre-flight FAILED:\n  - " + "\n  - ".join(problems)))
    if warnings:
        print(printable("warnings (not blocking):\n  - " + "\n  - ".join(warnings)))
    if problems:
        print(f"next: {preflight.RECOVERY}")
    return 0 if not problems else 1


def _restore_inputs(snap_path: Path, target: str, no_journal: bool) -> tuple[dict[str, Any], list[dict[str, Any]] | None]:
    """The snapshot and its journal, checked before anything is built; raises RestoreRefused."""
    journal_path = snapshot.writes_path(snap_path)
    meta_path = snap_path.with_name(f"{snap_path.stem}.meta.json")
    try:
        snap = snapshot.load(snap_path)
        writes = snapshot.load(journal_path) if journal_path.exists() else None
        meta = snapshot.load(meta_path) if meta_path.exists() else None
    except (OSError, ValueError) as err:  # STRIDE T6: a cut-off or unreadable file refuses cleanly
        raise snapshot.RestoreRefused(f"cannot read the snapshot or its journal ({type(err).__name__}: {err}); "
                                      "nothing restored") from None
    if not isinstance(snap, dict) or not all(isinstance(v, dict) for v in snap.values()):
        raise snapshot.RestoreRefused(f"{snap_path} is not a snapshot (file id -> fields); nothing restored")
    if writes is not None and not (isinstance(writes, list) and all(isinstance(w, dict) for w in writes)):
        raise snapshot.RestoreRefused(f"{journal_path} is not a write journal (a list of writes); nothing restored")
    if meta is not None and (not isinstance(meta, dict) or meta.get("target") != target):  # STRIDE S3
        taken = meta.get("target") if isinstance(meta, dict) else "?"
        raise snapshot.RestoreRefused(f"{snap_path} was taken on the {taken} target, not {target}; nothing restored"
                                      + ("; use --target live --live-apply" if taken == "live" else ""))
    if writes is None and not no_journal:  # STRIDE T6: without the journal, restore can't tell our fields from others'
        raise snapshot.RestoreRefused(f"no write journal at {journal_path}, so restore can't tell which fields this seat "
                                      "wrote; nothing restored. Only if it is truly lost, re-run with --no-journal "
                                      "(then rows this seat changed last are put back)")
    return snap, writes


def _digests(snap_path: Path) -> dict[str, str | None]:
    """STRIDE R7: sha256 of the snapshot, its journal and its meta as read, so the run file says which inputs were used."""
    paths = {"snapshot": snap_path, "journal": snapshot.writes_path(snap_path),
             "meta": snap_path.with_name(f"{snap_path.stem}.meta.json")}
    return {k: hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None for k, p in paths.items()}


def cmd_restore(args: argparse.Namespace) -> int:
    if args.target == "live" and not args.live_apply:
        print("refused: restoring on the live platform writes; it needs --live-apply and AS_ALLOW_WRITES=1", file=sys.stderr)
        return 3
    if args.live_apply and args.target != "live":  # STRIDE S3: --live-apply never selects the live platform by itself
        print("refused: --live-apply restores the live platform, so it needs --target live", file=sys.stderr)
        return 3
    snap_path = Path(args.snapshot)
    try:
        snap, writes = _restore_inputs(snap_path, args.target, getattr(args, "no_journal", False))
    except snapshot.RestoreRefused as err:
        print(printable(f"refused: {err}"), file=sys.stderr)
        return 3
    if writes is None:
        print(f"note: no write journal at {snapshot.writes_path(snap_path)}; restoring only rows this seat changed last",
              file=sys.stderr)
    trace_path = RUNS_DIR / "cli" / f"{datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:6]}-restore.jsonl"  # STRIDE R7
    rt = build(args.business, args.target, "apply", trace_path)
    allowlist = KEYSTONE_INCOMING_ALLOWLIST if args.target == "live" else frozenset(snap)
    journal_path = snapshot.writes_path(snap_path)
    rt.trace.write("restore_cli", target=args.target, snapshot=str(snap_path.resolve()),
                   journal=str(journal_path.resolve()) if writes is not None else None,
                   mode="journal" if writes is not None else "updated_by-fallback", sha256=_digests(snap_path))
    try:
        report = snapshot.restore(rt.admin_mcp, snap, rt.trace, allowlist=allowlist, writes=writes,
                                  me=rt.session.me().get("id"))
    except snapshot.RestoreRefused as err:
        print(printable(f"refused: {err}"), file=sys.stderr)
        return 3
    if args.target != "live":
        print("note: fake target: replayed against the fixture; nothing on the live platform was touched", file=sys.stderr)
    print(json.dumps({"target": args.target, **report}, indent=2, default=str))
    return 0


def _safe_stdout() -> None:
    """STRIDE D7: a name the console code page can't encode prints as an escape instead of crashing the command."""
    if os.environ.get("PYTHONIOENCODING"):
        return
    try:
        sys.stdout.reconfigure(errors="backslashreplace")
    except (AttributeError, ValueError):
        pass


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="harness", description="Files Agent harness")
    p.add_argument("--business", default="keystone", choices=["keystone", "suryodaya"])
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    cap = sub.add_parser("capture")
    cap.add_argument("business", choices=["keystone", "suryodaya"])
    run = sub.add_parser("run")
    run.add_argument("tasks", nargs="+")
    run.add_argument("--target", default="fake", choices=["fake", "live"])
    run.add_argument("--model", default="scripted", choices=["scripted", "anthropic"])
    run.add_argument("--repeat", type=int)
    run.add_argument("--set")
    run.add_argument("--live-apply", action="store_true")
    for name in ("score", "calibrate"):
        sp = sub.add_parser(name)
        sp.add_argument("set", nargs="?")
    sub.add_parser("rescore").add_argument("set")
    sub.add_parser("smoke")
    sub.add_parser("preflight")
    rs = sub.add_parser("restore")
    rs.add_argument("snapshot")
    rs.add_argument("--target", default="fake", choices=["fake", "live"])
    rs.add_argument("--live-apply", action="store_true")
    rs.add_argument("--no-journal", action="store_true", help="last resort when writes-N.json is lost")
    ro = sub.add_parser("routes")
    ro.add_argument("--model", default="scripted", choices=["scripted", "anthropic"])
    _safe_stdout()
    args = p.parse_args(argv)
    handlers = {"list": cmd_list, "capture": cmd_capture, "run": cmd_run, "score": cmd_score, "rescore": cmd_rescore,
                "calibrate": cmd_calibrate, "smoke": cmd_smoke, "preflight": cmd_preflight, "restore": cmd_restore,
                "routes": cmd_routes}
    try:
        return handlers[args.command](args)
    except WritesNotAllowed as err:
        print(f"refused: {err}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
