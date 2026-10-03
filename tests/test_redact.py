import json
import tempfile
import unittest
from pathlib import Path

from agent.auth import Session
from agent.redact import Redactor
from agent.trace import Trace


class StubTransport:
    def request(self, method, path, token=None, body=None, idempotent=True):
        if path == "/api/auth/login":
            return 200, {"token": "tok-abcdef123456"}
        return 200, {}


class RedactTest(unittest.TestCase):
    def test_login_and_call_leave_no_secret_on_disk(self):
        with tempfile.TemporaryDirectory() as d:
            trace = Trace(Path(d) / "t.jsonl", Redactor(["s3cret-pass"]))
            Session(StubTransport(), "a@b.c", "s3cret-pass", trace).login()
            trace.write("mcp_call", args={"password": "s3cret-pass"},
                        error="401 Bearer tok-abcdef123456", headers={"Authorization": "x"})
            text = (Path(d) / "t.jsonl").read_text(encoding="utf-8")
            self.assertNotIn("s3cret-pass", text)
            self.assertNotIn("tok-abcdef123456", text)
            self.assertIn("Bearer [REDACTED]", text)
            self.disk_text = text
            self.events_json = json.dumps(trace.events)

    def test_in_memory_events_are_redacted_too(self):
        with tempfile.TemporaryDirectory() as d:
            trace = Trace(Path(d) / "t.jsonl", Redactor(["s3cret-pass"]))
            Session(StubTransport(), "a@b.c", "s3cret-pass", trace).login()
            trace.write("mcp_call", args={"password": "s3cret-pass"},
                        error="401 Bearer tok-abcdef123456", headers={"Authorization": "x"})
            dumped = json.dumps(trace.events)
            self.assertNotIn("s3cret-pass", dumped)
            self.assertNotIn("tok-abcdef123456", dumped)

    def test_sensitive_keys_masked_whatever_the_value(self):
        self.assertEqual(Redactor()({"token": "anything", "note": "ok"}),
                         {"token": "[REDACTED]", "note": "ok"})

    def test_short_strings_are_not_secrets(self):
        self.assertEqual(Redactor(["abc"]).text("abc"), "abc")


if __name__ == "__main__":
    unittest.main()
