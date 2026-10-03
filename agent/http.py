"""Tiny HTTP transport (standard library only) with retry and backoff.

A transport exposes `request(method, path, token=None, body=None) -> (status, data)`.
`harness.fake_server.FakeServer` implements the same interface, so the agent
cannot tell whether it is talking to the live platform or to the offline replay.

- Only https is accepted, and redirects are never followed: a 3xx comes back as that status.
- One request, retries and backoff included, has a wall-clock limit, and a reply larger
  than MAX_REPLY_BYTES is refused instead of buffered.
"""
from __future__ import annotations

import http.client
import json
import time
import urllib.error
import urllib.request
from typing import Any

from agent.redact import Secret

RETRY_STATUSES = {429, 500, 502, 503, 504}
MAX_REPLY_BYTES = 16 * 1024 * 1024
CHUNK_BYTES = 64 * 1024


class TransportError(Exception):
    """The platform could not be reached after retries."""


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuse every redirect, so a 3xx surfaces as an HTTPError instead of being followed."""

    def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


# STRIDE S5: urlopen's default opener re-sends Authorization / x-api-key to any host a 3xx names.
NO_REDIRECT_OPENER = urllib.request.build_opener(_NoRedirect)


class HttpTransport:
    def __init__(self, base_url: str, timeout: float = 60.0, retries: int = 3, max_seconds: float = 180.0) -> None:
        if not base_url.lower().startswith("https://"):  # STRIDE S5: the bearer token never travels in clear text
            raise ValueError(f"base_url must start with https:// (got {base_url!r})")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.max_seconds = max_seconds  # wall-clock cap for one request, retries and backoff included

    def request(self, method: str, path: str, token: str | None = None, body: Any = None,
                idempotent: bool = True) -> tuple[int, Any]:
        """Send one request. A non-idempotent request (a write) is retried only on 429, which means
        "not processed". After a 5xx or a timeout the write may already have happened, so resending it
        could create a second escalation or session that this seat can never remove."""
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = Secret(f"Bearer {token}")
        if body is not None:
            headers["Content-Type"] = "application/json"
        what, last_error = f"{method} {path}", ""
        deadline = time.monotonic() + self.max_seconds  # STRIDE D9: a slow or trickled reply can't hang the run
        for attempt in range(self.retries + 1):
            # STRIDE I4: the encoded body (a login holds the password) is never kept in a local a traceback could print
            req = urllib.request.Request(self.base_url + path, None if body is None else json.dumps(body).encode("utf-8"),
                                         headers=headers, method=method)
            try:
                with NO_REDIRECT_OPENER.open(req, timeout=self._socket_timeout(deadline)) as resp:
                    return resp.status, _decode(read_capped(resp, deadline, what))
            except urllib.error.HTTPError as err:
                retryable = err.code in RETRY_STATUSES if idempotent else err.code == 429
                if not (retryable and self._may_retry(attempt, deadline)):
                    return err.code, _error_body(err, deadline, what)
                last_error = f"HTTP {err.code}"
            except (OSError, http.client.HTTPException) as err:  # STRIDE T1: a reply cut off mid-body is no OSError
                last_error = f"{type(err).__name__}: {err}"
                if not (idempotent and self._may_retry(attempt, deadline)):
                    # STRIDE I4: the cause is in the message; its http.client frames hold the body and headers
                    raise TransportError(f"{what} failed: {last_error}") from None
            time.sleep(2 ** attempt)
        raise TransportError(f"{what} failed: {last_error}")

    def _socket_timeout(self, deadline: float) -> float:
        return max(0.1, min(self.timeout, deadline - time.monotonic()))

    def _may_retry(self, attempt: int, deadline: float) -> bool:
        """Another attempt only if one is left and its backoff ends before the deadline."""
        return attempt < self.retries and time.monotonic() + 2 ** attempt < deadline


def read_capped(resp: Any, deadline: float, what: str, limit: int = MAX_REPLY_BYTES) -> bytes:
    """Read a reply in chunks; refuse one larger than `limit` or one still arriving at the deadline (STRIDE D9)."""
    read = getattr(resp, "read1", None) or resp.read
    chunks: list[bytes] = []
    size = 0
    while True:
        if chunks and time.monotonic() > deadline:
            raise TransportError(f"{what} failed: reply still arriving at the time limit")
        chunk = read(CHUNK_BYTES)
        if not chunk:
            return b"".join(chunks)
        size += len(chunk)
        if size > limit:
            raise TransportError(f"{what} failed: reply larger than {limit} bytes")
        chunks.append(chunk)


def _error_body(err: urllib.error.HTTPError, deadline: float, what: str) -> Any:
    try:
        return _decode(read_capped(err, deadline, what))
    except (OSError, http.client.HTTPException):
        return ""


def _decode(raw: bytes) -> Any:
    text = raw.decode("utf-8", "replace")
    try:
        return json.loads(text)
    except ValueError:
        return text
