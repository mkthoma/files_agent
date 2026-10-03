"""Hand-written MCP client: JSON-RPC 2.0 over POST /api/mcp (T1.2).

Rules this client enforces:
- An `error` inside the JSON-RPC envelope is a failure even though HTTP is 200.
- `result.isError == true` is also a failure, and so is a malformed result (data_code "bad_reply"),
  including a get, create or update whose payload is not an object.
- 401 is handled by the Session (one re-login).
- Only WRITE_TOOLS and read-only tools are ever sent; any other tool is refused locally
  (data_code "write_tool_refused"). Only a read-only tool is resent after a 5xx or a timeout.
- A transport failure becomes an McpError (data_code "transport_error").
- No streaming, no batching.
"""
from __future__ import annotations

import json
from typing import Any, Callable

from agent.auth import Session
from agent.config import EXPOSED_READ_TOOLS, REQUIRED_TOOLS, WRITE_TOOLS
from agent.http import TransportError
from agent.textsafe import one_line
from agent.trace import Trace

PROTOCOL_VERSION = "2025-11-25"
# The agent's own read tools: the only ones allowed before the catalogue is loaded.
KNOWN_READ_TOOLS = (frozenset(EXPOSED_READ_TOOLS) | frozenset(REQUIRED_TOOLS)) - WRITE_TOOLS
# The platform declares an object (with an id) as the reply of every get, create and update.
OBJECT_REPLY_SUFFIXES = (".get", ".create", ".update")
# STRIDE I12: platform error texts that quote no record data; any other platform text is withheld.
KNOWN_ERROR_TEXTS = frozenset({"Record not found", "Invalid tool arguments.", "Method not found",
                               "This tool is not available to your seat; it is not in your tools/list."})
WITHHELD_ERROR = "the platform's message is withheld because it may quote record data"


class McpError(Exception):
    def __init__(self, message: str, code: int | None = None, data_code: str | None = None, data: Any = None,
                 own: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.data_code = data_code
        self.data = data
        self.own = own  # the message was written by this agent, so it quotes no platform text


class McpClient:
    def __init__(self, session: Session, trace: Trace, budget: Any = None) -> None:
        self.session = session
        self.trace = trace
        self.budget = budget
        self.sanitise: Callable[[Any], Any] | None = None  # leak guard for traced results; set by agent.runtime
        self._next_id = 0
        self._tools: list[dict[str, Any]] | None = None

    def _rpc(self, method: str, params: dict[str, Any], idempotent: bool = True) -> Any:
        self._next_id += 1
        envelope = {"jsonrpc": "2.0", "id": self._next_id, "method": method, "params": params}
        try:
            status, data = self.session.request("POST", "/api/mcp", envelope, idempotent=idempotent)
        except TransportError as err:
            raise McpError(f"platform unreachable: {err}", data_code="transport_error", own=True) from err
        if status != 200:
            raise McpError(f"HTTP {status} from /api/mcp", code=status, own=True)
        if not isinstance(data, dict):
            raise McpError(f"Non-JSON reply from /api/mcp: {one_line(data, 120)}")
        if "error" in data:
            # JSON-RPC allows `error` and `error.data` to be any value, so never assume dicts here.
            err = data["error"] if isinstance(data["error"], dict) else {"message": str(data["error"])}
            extra = err.get("data") if isinstance(err.get("data"), dict) else {"detail": err.get("data")}
            raise McpError(one_line(err.get("message", "MCP error")), err.get("code"), extra.get("code"), extra)
        return data.get("result")

    def initialize(self) -> dict[str, Any]:
        return self._rpc("initialize", {"protocolVersion": PROTOCOL_VERSION, "capabilities": {},
                                        "clientInfo": {"name": "team20-files-agent", "version": "0.1"}})

    def list_tools(self, refresh: bool = False) -> list[dict[str, Any]]:
        if self._tools is None or refresh:
            result = self._rpc("tools/list", {})
            self._tools = list((result or {}).get("tools", []))
        return self._tools

    def call(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        args = arguments or {}
        read_only = name not in WRITE_TOOLS and self._is_read_only(name)
        if name not in WRITE_TOOLS and not read_only:  # STRIDE E3: fail closed, so the 3-write-tool rule holds here too
            self.trace.write("write_blocked", reason="not read-only and not in WRITE_TOOLS", tool=name)
            raise McpError(f"refused: {name} is not a read-only tool and not one of {sorted(WRITE_TOOLS)}",
                           data_code="write_tool_refused", own=True)
        if self.budget is not None:
            self.budget.add_call()
        try:  # only a read-only tool is ever resent after an ambiguous failure (see agent/http.py)
            result = self._rpc("tools/call", {"name": name, "arguments": args}, idempotent=read_only)
        except McpError as err:  # STRIDE I12: the run file gets the same withheld text as the model
            self.trace.write("mcp_call", tool=name, args=args, ok=False, error=safe_error_text(err, 500),
                             error_code=err.data_code)
            raise
        except BaseException as err:  # STRIDE T1: any other failure (Ctrl-C included) still leaves an mcp_call event
            self.trace.write("mcp_call", tool=name, args=args, ok=False, error=f"{type(err).__name__}: {err}",
                             error_code="client_error")
            raise
        try:
            payload, is_error = _parse(result)
        except (AttributeError, TypeError, ValueError) as err:  # STRIDE T1: a malformed reply is a failure, not a crash
            self.trace.write("mcp_call", tool=name, args=args, ok=False, error=f"malformed reply: {err}", error_code="bad_reply")
            raise McpError(f"{name} returned a malformed reply ({type(err).__name__})", data_code="bad_reply",
                           own=True) from err
        if is_error:
            err = McpError(f"{name} returned isError: {one_line(payload, 200)}", data_code="is_error", data=payload)
            shown = one_line(payload, 500)
            self.trace.write("mcp_call", tool=name, args=args, ok=False,
                             error=shown if shown in KNOWN_ERROR_TEXTS else WITHHELD_ERROR)  # STRIDE I12
            raise err
        if name.endswith(OBJECT_REPLY_SUFFIXES) and not isinstance(payload, dict):
            # STRIDE T1/T3: a write that landed must not crash its caller; the guard journals it as uncertain
            problem = f"{name} returned a reply that is not an object ({type(payload).__name__})"
            self.trace.write("mcp_call", tool=name, args=args, ok=False, error=problem, error_code="bad_reply")
            raise McpError(problem, data_code="bad_reply", own=True)
        traced = self.sanitise(payload) if self.sanitise else payload
        self.trace.write("mcp_call", tool=name, args=args, ok=True, result=_summarise(traced))
        return payload

    def _is_read_only(self, name: str) -> bool:
        """Read-only per the loaded catalogue; before it is loaded, only the agent's own read tools count."""
        if self._tools is None:
            return name in KNOWN_READ_TOOLS
        return any(t.get("name") == name and (t.get("annotations") or {}).get("readOnlyHint") for t in self._tools)


def safe_error_text(err: McpError, limit: int = 300) -> str:
    """STRIDE I12: what the model, a record or an answer may say about a failed call. Platform text can quote a
    record (e.g. a withheld title), so only a known fixed message or one this client wrote itself is kept."""
    text = str(err)
    return one_line(text, limit) if getattr(err, "own", False) or text in KNOWN_ERROR_TEXTS else WITHHELD_ERROR


def _parse(result: Any) -> tuple[Any, bool]:
    """(payload, isError) of a tools/call result; raises on a result that is not an object."""
    if result is not None and not isinstance(result, dict):
        raise TypeError(f"result is a {type(result).__name__}, not an object")
    return _payload(result), bool((result or {}).get("isError"))


def _payload(result: Any) -> Any:
    """The full payload is JSON text in content[0].text; fall back to structuredContent."""
    if not isinstance(result, dict):
        return result
    for block in result.get("content") or []:
        if block.get("type") == "text":
            try:
                return json.loads(block.get("text", ""))
            except ValueError:
                return block.get("text")
    return result.get("structuredContent")


def _summarise(payload: Any) -> Any:
    """Keep traces readable: record list totals and ids, and full single objects."""
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        return {"total": payload.get("total"), "ids": [r.get("id") for r in payload["data"][:50]]}
    return payload
