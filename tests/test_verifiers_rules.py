# harness verifiers - a write in a read only task fails the writes check
import unittest
from pathlib import Path
from harness.verifiers import Run, verify

FILE_ID = "A"  # only allowlisted file in every hand built run
MY_ID = "ME"  # agents own seat


def _call(tool):
    # one ok mcp_call event on file A, like the agent trace records it
    return {"kind": "mcp_call", "tool": tool, "args": {"id": FILE_ID}, "ok": True}


def _fake_run(expect, events):
    # run built by hand, no server: manifest, agent events, then the result
    manifest = {"kind": "manifest", "allowlist": [FILE_ID], "user_id": MY_ID,
                "task": {"id": "X", "question": "q", "mode": "read", "expect": expect}}
    last_pass = {"model_text": "x", "records": [], "aborted": None}
    result = {"kind": "result", "passes": [last_pass], "error": None,
              "state_before": {"files": {}, "escalations": []},
              "state_after": {"files": {}, "escalations": []},
              "resolved_ids": {}, "fake_write_log": None}
    # path is just a label, verify() never opens it
    return Run(Path("hand-built.jsonl"), manifest, [manifest, *events, result], result)


def _failing_checks(run):
    return {check.name: check.detail for check in verify(run) if not check.ok}


class WritesCheckTests(unittest.TestCase):  # VERIFY-1

    def test_write_in_read_only_task(self):
        # update in a task expecting 0 writes fails only the writes check, without it nothing fails
        read_only = {"writes": 0}
        get = _call("FileAttachment.get")
        update = _call("FileAttachment.update")
        broken = _fake_run(read_only, [get, update])
        clean = _fake_run(read_only, [get])
        self.assertEqual(_failing_checks(broken), {"writes": "1 write call(s) in the last pass, expected 0"})
        self.assertEqual(_failing_checks(clean), {})


if __name__ == "__main__":
    unittest.main()
