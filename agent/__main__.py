"""Command line (T3.3).

  python -m agent ask "Find the drawing for part J-BRKT-04."
  python -m agent --target fake ask "Tidy the incoming folder." --apply
  python -m agent smoke [--target live|fake]
  python -m agent whoami | tools

--target and --business may go before or after the command.
Plan-only is the default. --apply writes only on the fake server: live writes go
through the harness (`python -m harness run TI2L --target live --live-apply`), which
adds pre-flight, snapshot, write journal and restore.
"""
from __future__ import annotations

import argparse
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

from agent.config import RUNS_DIR, get_settings
from agent.loop import run_agent
from agent.runtime import Runtime, WritesNotAllowed, build, make_model
from agent.textsafe import one_line, printable
from agent.trace import git_state, now_iso


def _trace_path(name: str) -> Path:
    # STRIDE R7: a run id in the name, so two commands started in the same second never share a trace.
    return RUNS_DIR / "cli" / f"{datetime.now():%Y%m%d-%H%M%S}-{name}-{uuid.uuid4().hex[:6]}.jsonl"


def _attach_manifest(rt: Runtime, path: Path, args: argparse.Namespace, mode: str, model: str) -> None:
    """Rewrite the trace with a manifest first, like a harness run file (STRIDE R7: who, what, which code)."""
    rt.trace.attach(path, {
        "schema": 1, "run_id": path.stem, "command": args.command, "argv": args.argv, "target": args.target,
        "business": args.business, "mode": mode, "model": model, "git": git_state(), "tool_hash": rt.catalog.hash(),
        "user_id": rt.session.me().get("id"), "allowlist_size": len(rt.guard.allowlist), "started_at": now_iso(),
    })


def cmd_ask(args: argparse.Namespace) -> int:
    if args.apply and args.target == "live":
        print("refused: `ask --apply` writes only on the fake server. Live writes go through "
              "`python -m harness run TI2L --target live --live-apply` (pre-flight, snapshot and restore).", file=sys.stderr)
        return 3
    settings = get_settings(args.business)
    model_kind = args.model or ("anthropic" if settings.anthropic_api_key else "scripted")
    if model_kind == "scripted" and not args.model:
        print("note: no ANTHROPIC_API_KEY set, using the offline scripted model", file=sys.stderr)
    mode = "apply" if args.apply else "plan"
    path = _trace_path("ask")
    rt = build(args.business, args.target, mode, path, settings=settings)
    rt.ctx.run_id = path.stem  # STRIDE R3: the session title names this trace
    _attach_manifest(rt, path, args, mode, settings.model if model_kind == "anthropic" else "scripted")
    result = run_agent(args.question, rt.ctx, make_model(model_kind, settings), rt.budget, rt.trace)
    # STRIDE S2: the answer carries other teams' filenames; drop terminal escapes, bidi and other control characters.
    print(printable(result.answer))
    print(f"\n[{args.target} | {mode} | model {model_kind} | writes {len(rt.guard.writes)} | "
          f"cost {rt.budget.ledger()} | stop {result.stop}{' | ABORTED ' + result.aborted if result.aborted else ''}]")
    if result.unverified_ids:
        print(printable(f"[warning: ids in the answer not seen in any tool result: {result.unverified_ids}]"))
    print(f"[trace: {path}]")
    return 0 if not result.aborted else 2


def cmd_smoke(args: argparse.Namespace) -> int:
    path = _trace_path("smoke")
    rt = build(args.business, args.target, "plan", path)
    _attach_manifest(rt, path, args, "plan", "none")
    me = rt.session.me()
    total = (rt.admin_mcp.call("FileAttachment.list", {"limit": 1}) or {}).get("total")
    print(one_line(f"login ok: {me.get('email')} ({me.get('id')}), apps {me.get('allowed_apps')}", 500))
    print(f"tools: {rt.catalog.report()}")
    print(f"FileAttachment total: {total}; write allow-list size: {len(rt.guard.allowlist)}")
    return 0 if not rt.catalog.check_required() else 1


def cmd_whoami(args: argparse.Namespace) -> int:
    me = build(args.business, args.target, "plan", None).session.me()
    print(printable({k: me.get(k) for k in ("id", "email", "roles", "allowed_apps", "company_id")}))
    return 0


def cmd_tools(args: argparse.Namespace) -> int:
    rt = build(args.business, args.target, "plan", None)
    print(rt.catalog.report())
    for name in sorted(rt.catalog.names):
        print(("  [ro] " if rt.catalog.is_read_only(name) else "  [rw] ") + one_line(name))
    return 0


def _safe_stdout() -> None:
    """A character the console code page can't show is printed escaped instead of crashing the command."""
    # STRIDE D7: piped stdout on Windows is cp1252 and strict; an operator's own PYTHONIOENCODING still wins.
    if os.environ.get("PYTHONIOENCODING"):
        return
    try:
        sys.stdout.reconfigure(errors="backslashreplace")
    except (AttributeError, ValueError):
        pass


def main(argv: list[str] | None = None) -> int:
    _safe_stdout()
    parser = argparse.ArgumentParser(prog="agent", description="Files Agent (seat 20)")
    parser.add_argument("--business", default="keystone", choices=["keystone", "suryodaya"])
    parser.add_argument("--target", default="live", choices=["live", "fake"])
    # The same options after the command. SUPPRESS keeps the value given before it (argparse
    # otherwise lets a subcommand's default silently overwrite it).
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--business", choices=["keystone", "suryodaya"], default=argparse.SUPPRESS)
    common.add_argument("--target", choices=["live", "fake"], default=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="command", required=True)
    ask = sub.add_parser("ask", parents=[common], help="ask the agent a question")
    ask.add_argument("question")
    ask.add_argument("--apply", action="store_true", help="allow writes (fake server only)")
    ask.add_argument("--model", choices=["anthropic", "scripted"])
    sub.add_parser("smoke", parents=[common], help="log in, discover tools, one read")
    sub.add_parser("whoami", parents=[common], help="show the seat identity")
    sub.add_parser("tools", parents=[common], help="list the MCP tools this seat has")
    args = parser.parse_args(argv)
    args.argv = list(sys.argv[1:] if argv is None else argv)
    handlers = {"ask": cmd_ask, "smoke": cmd_smoke, "whoami": cmd_whoami, "tools": cmd_tools}
    try:
        return handlers[args.command](args)
    except WritesNotAllowed as err:
        print(f"refused: {err}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
