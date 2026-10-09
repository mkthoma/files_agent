"""Model clients.

- AnthropicModel:   the real model, via the Messages API over plain HTTPS (no SDK, no framework).
- OpenAICompatModel: the official server run's model (Release 8.1), via the OpenAI-compatible
  chat-completions API over plain HTTPS. It translates between the loop's message format and
  the OpenAI one, so `agent/loop.py` needs no change.
- ScriptedModel:    a deterministic stand-in for offline work and harness calibration. It routes a
  question to one skill with simple rules and returns that skill's `answer_text`. It is NOT the
  graded agent; it exists so the harness can run without an API key.
"""
from __future__ import annotations

import http.client
import json
import os
import re
import time
import urllib.error
import urllib.request
from typing import Any

from agent.http import CHUNK_BYTES, NO_REDIRECT_OPENER, TransportError, read_capped
from agent.redact import Secret

API_URL = "https://api.anthropic.com/v1/messages"
API_VERSION = "2023-06-01"
SOCKET_TIMEOUT = 120.0


class ModelError(Exception):
    pass


class AnthropicModel:
    name = "anthropic"

    def __init__(self, api_key: str, model: str, max_tokens: int = 2048, temperature: float | None = 0.0, retries: int = 3,
                 max_seconds: float = 300.0) -> None:
        if not api_key:
            raise ModelError("ANTHROPIC_API_KEY is not set in .env (use --model scripted to run offline)")
        self.api_key, self.model, self.max_tokens, self.temperature, self.retries = Secret(api_key), model, max_tokens, temperature, retries
        self.max_seconds = max_seconds  # wall-clock cap for one create(), retries and backoff included

    def create(self, system: str, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]:
        body: dict[str, Any] = {"model": self.model, "max_tokens": self.max_tokens, "system": system, "messages": messages, "tools": tools}
        if self.temperature is not None:
            body["temperature"] = self.temperature
        headers = {"x-api-key": self.api_key, "anthropic-version": API_VERSION, "content-type": "application/json"}
        deadline = time.monotonic() + self.max_seconds  # STRIDE D9: a slow or trickled reply can't hang the run
        for attempt in range(self.retries + 1):
            req = urllib.request.Request(API_URL, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
            try:
                timeout = max(0.1, min(SOCKET_TIMEOUT, deadline - time.monotonic()))
                with NO_REDIRECT_OPENER.open(req, timeout=timeout) as resp:  # STRIDE S5: the key never follows a redirect
                    return json.loads(read_capped(resp, deadline, "Messages API").decode("utf-8"))
            except urllib.error.HTTPError as err:
                detail = err.read(CHUNK_BYTES).decode("utf-8", "replace")[:300]
                if err.code in (429, 500, 502, 503, 529) and self._may_retry(attempt, deadline):
                    time.sleep(2 ** (attempt + 1))
                    continue
                raise ModelError(f"Messages API HTTP {err.code}: {detail}") from err
            except (OSError, http.client.HTTPException) as err:  # URLError, timeouts, a reply cut off mid-body
                if self._may_retry(attempt, deadline):
                    time.sleep(2 ** (attempt + 1))
                    continue
                raise ModelError(f"Messages API unreachable: {err}") from None  # STRIDE I4: its frames hold the key
            except TransportError as err:
                raise ModelError(f"Messages API reply refused: {err}") from err
        raise ModelError("Messages API failed after retries")

    def _may_retry(self, attempt: int, deadline: float) -> bool:
        return attempt < self.retries and time.monotonic() + 2 ** (attempt + 1) < deadline


class OpenAICompatModel:
    """The platform-provided model of the official server run: OpenAI-compatible chat completions,
    tool calls included, spoken over plain HTTPS (no SDK). The loop keeps its own message format;
    this class translates each call in both directions."""

    name = "openai"

    def __init__(self, base_url: str, api_key: str, model: str, max_tokens: int = 2048,
                 temperature: float | None = 0.0, retries: int = 3, max_seconds: float = 300.0) -> None:
        if not base_url or not api_key:
            raise ModelError("OPENAI_BASE_URL and OPENAI_API_KEY are not set (they come from the official runner)")
        self.url = base_url.rstrip("/") + "/chat/completions"
        self.api_key, self.model, self.max_tokens, self.temperature = Secret(api_key), model, max_tokens, temperature
        self.retries, self.max_seconds = retries, max_seconds

    @classmethod
    def from_env(cls) -> "OpenAICompatModel":
        env = os.environ
        return cls(env.get("OPENAI_BASE_URL", ""), env.get("OPENAI_API_KEY", ""),
                   env.get("OPENAI_MODEL", "agentswitch-default"))

    def create(self, system: str, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]:
        body: dict[str, Any] = {"model": self.model, "max_tokens": self.max_tokens,
                                "messages": _to_openai(system, messages)}
        if tools:
            body["tools"] = [{"type": "function", "function": {"name": t["name"], "description": t["description"],
                                                               "parameters": t["input_schema"]}} for t in tools]
        if self.temperature is not None:
            body["temperature"] = self.temperature
        headers = {"Authorization": "Bearer " + self.api_key, "content-type": "application/json"}
        deadline = time.monotonic() + self.max_seconds
        for attempt in range(self.retries + 1):
            req = urllib.request.Request(self.url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
            try:
                timeout = max(0.1, min(SOCKET_TIMEOUT, deadline - time.monotonic()))
                with NO_REDIRECT_OPENER.open(req, timeout=timeout) as resp:  # STRIDE S5: the key never follows a redirect
                    return _from_openai(json.loads(read_capped(resp, deadline, "chat completions").decode("utf-8")))
            except urllib.error.HTTPError as err:
                detail = err.read(CHUNK_BYTES).decode("utf-8", "replace")[:300]
                if err.code in (429, 500, 502, 503, 529) and self._may_retry(attempt, deadline):
                    time.sleep(2 ** (attempt + 1))
                    continue
                raise ModelError(f"chat completions HTTP {err.code}: {detail}") from err
            except (OSError, http.client.HTTPException) as err:
                if self._may_retry(attempt, deadline):
                    time.sleep(2 ** (attempt + 1))
                    continue
                raise ModelError(f"chat completions unreachable: {err}") from None  # STRIDE I4: frames hold the key
            except TransportError as err:
                raise ModelError(f"chat completions reply refused: {err}") from err
        raise ModelError("chat completions failed after retries")

    _may_retry = AnthropicModel._may_retry


def _to_openai(system: str, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The loop's messages (Anthropic-style content blocks) as OpenAI chat messages."""
    out: list[dict[str, Any]] = [{"role": "system", "content": system}]
    for msg in messages:
        content = msg["content"]
        if isinstance(content, str):
            out.append({"role": msg["role"], "content": content})
            continue
        if msg["role"] == "assistant":
            text = "\n".join(b.get("text", "") for b in content if b.get("type") == "text")
            calls = [{"id": b["id"], "type": "function",
                      "function": {"name": b["name"], "arguments": json.dumps(b.get("input") or {})}}
                     for b in content if b.get("type") == "tool_use"]
            entry: dict[str, Any] = {"role": "assistant", "content": text or None}
            if calls:
                entry["tool_calls"] = calls
            out.append(entry)
            continue
        for block in content:  # a user turn of tool_result blocks: one OpenAI tool message per result
            if block.get("type") == "tool_result":
                prefix = "TOOL ERROR: " if block.get("is_error") else ""
                out.append({"role": "tool", "tool_call_id": block["tool_use_id"], "content": prefix + str(block["content"])})
    return out


def _from_openai(resp: dict[str, Any]) -> dict[str, Any]:
    """An OpenAI chat-completions reply as the Anthropic-style dict the loop expects."""
    choices = resp.get("choices") or []
    if not choices:
        raise ModelError(f"chat completions reply has no choices: {json.dumps(resp)[:300]}")
    msg = choices[0].get("message") or {}
    content: list[dict[str, Any]] = []
    if msg.get("content"):
        content.append({"type": "text", "text": str(msg["content"])})
    for call in msg.get("tool_calls") or []:
        fn = call.get("function") or {}
        try:
            args = json.loads(fn.get("arguments") or "{}")
        except ValueError:
            args = fn.get("arguments")  # not JSON: the loop reports invalid_arguments back to the model
        content.append({"type": "tool_use", "id": call.get("id") or f"call_{len(content)}",
                        "name": fn.get("name") or "?", "input": args})
    usage = resp.get("usage") or {}
    has_tools = any(b["type"] == "tool_use" for b in content)
    finish = choices[0].get("finish_reason") or "stop"
    return {"content": content, "stop_reason": "tool_use" if has_tools else ("end_turn" if finish == "stop" else finish),
            "usage": {"input_tokens": usage.get("prompt_tokens", 0), "output_tokens": usage.get("completion_tokens", 0)}}


PART = r"([A-Za-z0-9]+(?:-[A-Za-z0-9]+)+)"
ROUTES: list[tuple[str, str, Any]] = [
    (r"\b(delete|remove|trash|get rid of)\b(.*)", "remove_file", lambda m, q: {"file": _clean(m.group(2))}),
    (r"what does (.+?) (say|contain)|contents? of (.+?)\??$|quote (.+)", "file_contents",
     lambda m, q: {"file": _clean(next(g for g in (m.group(1), m.group(3), m.group(4)) if g))}),
    (r"pay ?slips?|salar|payroll|net pay|contracts?\b|\be-?sign|design (?:file|review)s?|invoices?", "explain_access",
     lambda m, q: {"request": q}),
    (r"rev(?:ision)?\s+([A-Za-z0-9]{1,3})\b.*?" + PART + r".*current", "find_drawing",
     lambda m, q: {"part_code": m.group(2), "revision": m.group(1)}),
    (r"drawing.*?\bpart\s+" + PART, "find_drawing", lambda m, q: {"part_code": m.group(1)}),
    (r"^\s*file\s+(.+?)\s+(?:into|in|to)\b", "triage_folder", lambda m, q: {"folder_name": "Incoming", "file": _clean(m.group(1))}),
    (r"\btidy\b|\btriage\b|sort (?:out )?the incoming", "triage_folder", lambda m, q: {"folder_name": "Incoming"}),
    (r"how many files", "drive_overview", lambda m, q: {}),
    (r"\blist\b.*\bfiles\b", "list_files", lambda m, q: {}),
    (r"duplicate", "find_duplicates", lambda m, q: {}),
]


def _clean(text: str) -> str:
    return re.sub(r"^(the|a|an)\s+|\s*(file)?\s*[?.!]*$", "", (text or "").strip(), flags=re.IGNORECASE).strip()


def route(question: str) -> tuple[str, dict[str, Any]] | None:
    for pattern, skill, make_args in ROUTES:
        m = re.search(pattern, question, re.IGNORECASE)
        if m:
            return skill, make_args(m, question)
    return None


class ScriptedModel:
    """Deterministic offline stand-in: one skill call, then that skill's answer_text."""

    name = "scripted"

    def create(self, system: str, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> dict[str, Any]:
        last = messages[-1]
        if last["role"] == "user" and isinstance(last["content"], str):
            picked = route(last["content"])
            if picked is None:
                return _text("I can't map that request to anything this Files seat can do.")
            skill, args = picked
            return {"content": [{"type": "tool_use", "id": "toolu_scripted_1", "name": skill, "input": args}],
                    "stop_reason": "tool_use", "usage": {"input_tokens": 0, "output_tokens": 0}}
        texts = []
        for block in last["content"]:
            if block.get("type") == "tool_result":
                try:
                    texts.append(json.loads(block["content"]).get("answer_text", block["content"]))
                except (ValueError, AttributeError):
                    texts.append(str(block["content"]))
        return _text("\n".join(texts) or "No result.")


def _text(text: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": text}], "stop_reason": "end_turn", "usage": {"input_tokens": 0, "output_tokens": 0}}
