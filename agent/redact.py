"""Remove secrets from anything before it is written to disk."""
from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import quote, quote_plus

MASK = "[REDACTED]"
MIN_SECRET_LEN = 6
SENSITIVE_KEYS = {"password", "token", "authorization", "x-api-key", "api_key", "apikey", "access_token"}
# STRIDE I4: also client_secret, set-cookie, share_token, password_hash...; never input_tokens or max_tokens.
SENSITIVE_KEY_RE = re.compile(r"(^|[_-])(password|passwd|secret|token|api[_-]?key|authorization|cookie)([_-]hash)?$", re.I)
# STRIDE R8: any "Bearer <token>" is masked only under a header-like key. In free text (filenames,
# descriptions, model text) only a credential-shaped token is: a JWT, or 20+ token characters with a digit.
HEADER_KEYS = {"auth", "authorization", "headers"}
BEARER_RE = re.compile(r"Bearer\s+[A-Za-z0-9\-._~+/]+=*")
CREDENTIAL_RE = re.compile(r"Bearer\s+(?:eyJ[\w-]+\.[\w-]+\.[\w-]+|(?=[A-Za-z0-9\-._~+/]*\d)[A-Za-z0-9\-._~+/]{20,}=*)")


class Secret(str):
    """A secret value whose repr is masked, so a traceback printed with its locals (unittest --locals, pytest -l)
    can't show it (STRIDE I4). Everything else is a plain str: json.dumps and HTTP headers still send the value."""

    __slots__ = ()

    def __repr__(self) -> str:
        return repr(MASK)


def is_sensitive_key(key: object) -> bool:
    name = str(key).lower()
    return name in SENSITIVE_KEYS or bool(SENSITIVE_KEY_RE.search(name))


class Redactor:
    """Masks known secret values anywhere, plus any value stored under a sensitive key."""

    def __init__(self, secrets: list[str] | None = None) -> None:
        self._secrets: list[str] = []
        for secret in secrets or []:
            self.add(secret)

    def add(self, secret: str) -> None:
        if not secret or len(secret) < MIN_SECRET_LEN:
            return
        # STRIDE I4: the JSON-escaped and URL-encoded forms too, so an echoed body or query string is masked.
        forms = {secret, json.dumps(secret)[1:-1], json.dumps(secret, ensure_ascii=False)[1:-1],
                 quote(secret, safe=""), quote_plus(secret)}
        self._secrets = sorted(set(self._secrets) | forms, key=lambda s: (-len(s), s))

    def text(self, value: str, header: bool = False) -> str:
        return self._text(value, header)[0]

    def masked(self, obj: Any, header: bool = False) -> tuple[Any, int]:
        """A redacted copy of `obj` and how many values were masked in it."""
        if isinstance(obj, str):
            return self._text(obj, header)
        if isinstance(obj, dict):
            pairs = {k: self._item(k, v, header) for k, v in obj.items()}
            return {k: p[0] for k, p in pairs.items()}, sum(p[1] for p in pairs.values())
        if isinstance(obj, (list, tuple)):
            pairs = [self.masked(v, header) for v in obj]
            return [p[0] for p in pairs], sum(p[1] for p in pairs)
        return obj, 0

    def __call__(self, obj: Any) -> Any:
        return self.masked(obj)[0]

    def _item(self, key: object, value: Any, header: bool) -> tuple[Any, int]:
        if value and is_sensitive_key(key):
            return MASK, 1
        return self.masked(value, header or str(key).lower() in HEADER_KEYS)

    def _text(self, value: str, header: bool) -> tuple[str, int]:
        out, count = value, 0
        for secret in self._secrets:  # STRIDE I4: exact secrets first, so a bearer match can't leave a tail
            if secret in out:
                count += out.count(secret)
                out = out.replace(secret, MASK)
        out, n = (BEARER_RE if header else CREDENTIAL_RE).subn(f"Bearer {MASK}", out)
        return out, count + n
