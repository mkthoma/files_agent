"""Read-only secret scan (STRIDE I11). It prints only WHERE a possible secret is (file, line, rule), never the text.

  python scripts/secret_scan.py                  # tracked files, runs/ and harness/fixtures
  python scripts/secret_scan.py --staged         # the lines a commit would add (.githooks/pre-commit runs this)
  python scripts/secret_scan.py --history        # every line ever added, in every commit of every branch
  python scripts/secret_scan.py --also CANARY    # also look for a dummy test string (docs/checking.md, T0.2)

What it looks for: the exact values of the passwords and the model key in .env (6+ characters, as agent/redact.py
masks them), plus the shapes of a model key, a JWT, a long bearer token, and a password or key written out in
KEY=value or "password": "..." form. Exit code 1 if anything is found. Standard library only.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from agent.config import load_env  # noqa: E402
from agent.redact import CREDENTIAL_RE, MIN_SECRET_LEN, is_sensitive_key  # noqa: E402

SHAPES = {
    "model key": re.compile(r"sk-ant-[A-Za-z0-9_-]{16,}"),
    "JWT": re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}"),
    "bearer token": CREDENTIAL_RE,
    "password or key assignment": re.compile(r"\b(?:AS_[A-Z]+_PASSWORD|ANTHROPIC_API_KEY)\s*=\s*['\"]?[^\s'\"$<(]{6,}"),
    "password in JSON": re.compile(r"(?i)\"password\"\s*:\s*\"[^\"$<]{6,}\""),
}
# Known non-secrets: the redaction example (S5 in docs/checking.md), placeholders and the fake server's own
# values, and the dummy password of the hand-written tests/test_redact.py (PR #4), quoted so that only that exact
# value is allowed.
ALLOWED = ("My-Secret-Pass-1", "abc.def.ghi", "YOUR_KEYSTONE_PASSWORD", "fake-token-", "fake-password", "[REDACTED]",
           '"s3cret-pass"')
SCAN_DIRS = ("runs", "harness/fixtures")
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)")


def secrets_from_env(extra: list[str]) -> list[str]:
    """The secret values in .env and the shell (never printed), plus any dummy strings given with --also."""
    values = [v for k, v in load_env().items() if is_sensitive_key(k) and len(v) >= MIN_SECRET_LEN]
    return sorted({*values, *extra}, key=len, reverse=True)


def rules_hit(line: str, secrets: list[str]) -> list[str]:
    hits = ["a value from .env (or --also)" for s in secrets if s in line][:1]
    for name, pattern in SHAPES.items():
        if any(not any(ok in m.group(0) for ok in ALLOWED) for m in pattern.finditer(line)):
            hits.append(name)
    return hits


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", check=True).stdout


def scan_tree(secrets: list[str]) -> list[str]:
    paths = {REPO_ROOT / p for p in _git("ls-files").splitlines()}
    for folder in SCAN_DIRS:
        paths.update(p for p in (REPO_ROOT / folder).rglob("*") if p.is_file())
    found = []
    for path in sorted(paths):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for n, line in enumerate(text.splitlines(), 1):
            found += [f"{path.relative_to(REPO_ROOT).as_posix()}:{n}: {rule}" for rule in rules_hit(line, secrets)]
    return found


def scan_diff(diff: str, secrets: list[str]) -> list[str]:
    """Added lines of a unified diff (`git diff -U0` or `git log -p -U0`), located by commit, file and line."""
    found, commit, path, line_no = [], "", "", 0
    for line in diff.splitlines():
        if line.startswith("commit "):
            commit = line.split()[1][:12] + ":"
        elif line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else line[4:]
        elif HUNK.match(line):
            line_no = int(HUNK.match(line).group(1))
        elif line.startswith("+"):
            found += [f"{commit}{path}:{line_no}: {rule}" for rule in rules_hit(line[1:], secrets)]
            line_no += 1
    return found


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--staged", action="store_true", help="scan what the next commit would add")
    mode.add_argument("--history", action="store_true", help="scan every commit of every branch")
    p.add_argument("--also", action="append", default=[], help="a dummy string to look for too (never a real secret)")
    args = p.parse_args(argv)
    secrets = secrets_from_env(args.also)
    if args.staged:
        found = scan_diff(_git("diff", "--cached", "-U0", "--no-color"), secrets)
    elif args.history:
        found = scan_diff(_git("log", "-p", "--all", "-U0", "--no-color", "--format=commit %H"), secrets)
    else:
        found = scan_tree(secrets)
    for where in found:
        print(where)
    print(f"{len(found)} possible secret(s) found" if found else "no secrets found", file=sys.stderr)
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
