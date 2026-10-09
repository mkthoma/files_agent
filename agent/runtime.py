"""Builds everything one agent run needs, for the live platform or the offline fake server."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agent.auth import Session, TokenSession
from agent.budget import Budget
from agent.catalog import Catalog
from agent.config import KEYSTONE_INCOMING_ALLOWLIST, WRITE_BUSINESS, Settings, get_settings
from agent.guards import WriteGuard
from agent.http import HttpTransport
from agent.mcp_client import McpClient
from agent.model import AnthropicModel, OpenAICompatModel, ScriptedModel
from agent.privacy import sanitise_payload
from agent.redact import Redactor
from agent.safe_reads import folder_named, folders_by_id, where
from agent.skills.common import SkillContext
from agent.skills.escalate import Escalator
from agent.skills.profiles import load_rules
from agent.trace import Trace


class WritesNotAllowed(Exception):
    pass


@dataclass
class Runtime:
    settings: Settings
    target: str
    trace: Trace
    transport: Any
    session: Session
    mcp: McpClient          # budgeted; used by the agent
    admin_mcp: McpClient    # unbudgeted; used by the harness (snapshots, state capture)
    catalog: Catalog
    budget: Budget
    guard: WriteGuard
    ctx: SkillContext


def make_transport(target: str, settings: Settings, fixture_dir: Path | None = None, faults: tuple[str, ...] = (),
                   extra_files: list[dict[str, Any]] | None = None) -> Any:
    if target == "live":
        return HttpTransport(settings.base_url)
    if target == "fake":
        from harness.fake_server import FakeServer  # offline only
        return FakeServer.from_fixture(settings.business, fixture_dir, faults, extra_files or [])
    raise ValueError("target must be 'live' or 'fake'")


def make_model(kind: str, settings: Settings) -> Any:
    if kind == "scripted":
        return ScriptedModel()
    if kind == "openai":  # the official server run's model: OpenAI-compatible, from OPENAI_* env values
        return OpenAICompatModel.from_env()
    return AnthropicModel(settings.anthropic_api_key, settings.model)


def make_session(transport: Any, settings: Settings, trace: Trace, target: str) -> Session:
    """A password login, or (official server run) a session on the provided bearer token."""
    if settings.token:
        return TokenSession(transport, settings.email, settings.token, trace)
    # STRIDE I4: no plain `password` local, so a traceback printed with locals can't show it
    session = Session(transport, settings.email,
                      settings.password or ("fake-password" if target == "fake" else ""), trace)
    session.login()
    return session


def check_write_permission(target: str, mode: str, settings: Settings) -> None:
    if mode != "apply" or target == "fake":
        return
    if settings.business != WRITE_BUSINESS:
        raise WritesNotAllowed(f"Live writes are only allowed on {WRITE_BUSINESS}.")
    if not settings.allow_writes:
        raise WritesNotAllowed("Live writes need AS_ALLOW_WRITES=1 set in the shell for this one command "
                               "(the .env file is ignored for it) as well as --live-apply.")


def check_transport(target: str, transport: Any) -> None:
    """STRIDE E1: the label must match the transport in use; any transport that is not a fake counts as live."""
    if (target == "fake") != bool(getattr(transport, "is_fake", False)):
        raise ValueError(f"target {target!r} does not match the transport {type(transport).__name__}")


def build(business: str, target: str, mode: str, trace_path: Path | None, *, transport: Any = None,
          settings: Settings | None = None, trace: Trace | None = None, live_allowlist: bool = False) -> Runtime:
    """`live_allowlist` (offline only matters): cap the write allow-list exactly as the live target does."""
    if target not in ("live", "fake"):  # STRIDE E1: no third label can slip past the checks keyed on these two
        raise ValueError(f"target must be 'live' or 'fake', not {target!r}")
    settings = settings or get_settings(business)
    check_write_permission(target, mode, settings)
    trace = trace or Trace(trace_path, Redactor(settings.secrets()))
    transport = transport or make_transport(target, settings)
    check_transport(target, transport)
    session = make_session(transport, settings, trace, target)
    budget = Budget(settings.max_turns, settings.max_mcp_calls, settings.max_usd,
                    settings.price_in_per_mtok, settings.price_out_per_mtok)
    admin = McpClient(session, trace)
    admin.initialize()
    catalog = Catalog.from_tools(admin.list_tools())
    trace.write("catalog", report=catalog.report(), hash=catalog.hash(), problems=catalog.check_required())
    admin.sanitise = lambda payload: sanitise_payload(payload, catalog.can_list)
    allowlist = _allowlist(admin, bool(getattr(transport, "is_fake", False)), settings, live_allowlist)
    mcp = McpClient(session, trace, budget)
    mcp._tools = admin.list_tools()
    mcp.sanitise = admin.sanitise
    guard = WriteGuard(mcp, trace, mode, allowlist, live=not getattr(transport, "is_fake", False))
    ctx = SkillContext(mcp=mcp, session=session, guard=guard, trace=trace, catalog=catalog,
                       rules=load_rules(), settings=settings, allowlist=allowlist)
    ctx.escalator = Escalator(ctx)
    return Runtime(settings, target, trace, transport, session, mcp, admin, catalog, budget, guard, ctx)


def _allowlist(mcp: McpClient, fake: bool, settings: Settings, live_cap: bool = False) -> frozenset[str]:
    """Writable file ids = what is in Incoming right now; on any transport that is not the fake server (or with
    live_cap, to rehearse it offline) also capped to the verified 9."""
    incoming = folder_named(folders_by_id(mcp), "Incoming")
    if not incoming:
        return frozenset()
    page = mcp.call("FileAttachment.list", {"folder_id": incoming["id"], "limit": 500})
    ids = frozenset(r["id"] for r in where((page or {}).get("data", []), folder_id=incoming["id"]))
    if not fake or live_cap:  # STRIDE E1: the transport decides, not the label
        return ids & KEYSTONE_INCOMING_ALLOWLIST if settings.business == WRITE_BUSINESS else frozenset()
    return ids
