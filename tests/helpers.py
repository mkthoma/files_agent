# shared setup for the tests, nothing in here is a test
# run from the files_agent repo root so agent and harness can be imported
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import agent
from agent.config import get_settings
from agent.runtime import build
from harness.fake_server import FakeServer

REPO_ROOT = Path(agent.__file__).resolve().parent.parent

# always pin 26 Sept fixture. without it fake server loads newest capture and all the expected values in the tests change
FIXTURE_DIR = REPO_ROOT / "harness" / "fixtures" / "keystone" / "2026-09-26"


def quiet_settings(**env):
    return get_settings("keystone", env=dict(env))


def fake_server(faults=(), extra_files=None):
    # new one for each test, dont share between tests
    return FakeServer.from_fixture("keystone", FIXTURE_DIR, tuple(faults), extra_files or [])


def build_runtime(mode="plan", server=None, faults=(), extra_files=None, live_allowlist=False, settings=None):
    # returns (runtime, server)
    if server is None:
        server = fake_server(faults, extra_files)
    server.armed = False  # disarm during build so one-shot faults are left for the test
    rt = build("keystone", "fake", mode, None, transport=server,settings=settings or quiet_settings(), live_allowlist=live_allowlist)
    server.armed = True
    return rt, server


def offline_env(**extra):
    # env for cli runs in tests - creds blanked and proxy goes to 127.0.0.1:9 so nothing gets out
    env = {k: v for k, v in os.environ.items() if not k.startswith(("AS_", "ANTHROPIC_"))}
    env.update({
        "PYTHONIOENCODING": "utf-8",
        "PYTHONDONTWRITEBYTECODE": "1",
        "AS_KEYSTONE_PASSWORD": "",
        "AS_SURYODAYA_PASSWORD": "",
        "ANTHROPIC_API_KEY": "",
        "AS_EMAIL": "team20@theschoolofai.in",
        "AS_MODEL": "claude-sonnet-5",
        "AS_MAX_TURNS": "12",
        "AS_MAX_MCP_CALLS": "80",
        "AS_MAX_USD": "0.50",
        "AS_PRICE_IN_PER_MTOK": "3.0",
        "AS_PRICE_OUT_PER_MTOK": "15.0",
        "AS_ACTOR_KIND": "",
        "HTTP_PROXY": "http://127.0.0.1:9",
        "HTTPS_PROXY": "http://127.0.0.1:9",
        "NO_PROXY": "",
    })
    env.update(extra)
    return env


def run_cli(*args, env=None, cwd=None, timeout=600):
    # python -m <args> from repo root unless cwd given
    return subprocess.run([sys.executable, "-m", *args], cwd=cwd or REPO_ROOT, env=env or offline_env(),capture_output=True, text=True, encoding="utf-8", timeout=timeout)


def new_set_name(label):
    return f"test-{label}-{uuid.uuid4().hex[:8]}"


def remove_run_set(name, repo=None):
    # use with addCleanup so the test leaves nothing behind
    shutil.rmtree((repo or REPO_ROOT) / "runs" / name, ignore_errors=True)