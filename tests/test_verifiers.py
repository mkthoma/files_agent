import unittest
from pathlib import Path

from harness.tasks import Task
from harness.verifiers import Run, verify

F1 = "11111111-1111-1111-1111-111111111111"


def make_run(calls, records, model_text, before_files, after_files,
             before_esc=None, after_esc=None, mode="apply", expect=None):
    before_esc = before_esc if before_esc is not None else []
    after_esc = after_esc if after_esc is not None else []
    manifest = {"kind": "manifest",
                "task": Task(id="t", question="q", mode=mode, expect=expect or {}).to_dict(),
                "user_id": "me", "allowlist": [F1]}
    events = [manifest]
    events += [{"kind": "mcp_call", "tool": tool, "args": {"id": fid}, "ok": True} for tool, fid in calls]
    result = {"passes": [{"records": records, "model_text": model_text}],
              "state_before": {"files": before_files, "escalations": before_esc},
              "state_after": {"files": after_files, "escalations": after_esc}}
    events.append({"kind": "result", **result})
    return Run(Path("x"), manifest, events, result)


def applied_record(to_folder):
    return {"status": "applied", "target_id": F1, "target_label": "a.pdf", "action": "move",
            "details": {"to_folder_id": to_folder, "changes": {"folder_id": to_folder}}}


def filed_state(folder, by="me"):
    return {F1: {"folder_id": folder, "updated_by": by}}


class VerifierTest(unittest.TestCase):
    def check(self, run, name):
        return {c.name: c for c in verify(run)}[name].ok

    def test_writes_in_allowlist(self):
        broken = make_run([("FileAttachment.get", "f2"), ("FileAttachment.update", "f2")],
                          [], "", {}, {})
        fixed = make_run([("FileAttachment.get", F1), ("FileAttachment.update", F1)],
                         [], "", {}, {})
        self.assertFalse(self.check(broken, "writes_in_allowlist"))
        self.assertTrue(self.check(fixed, "writes_in_allowlist"))

    def test_read_before_write(self):
        broken = make_run([("FileAttachment.update", F1)], [], "", {}, {})
        fixed = make_run([("FileAttachment.get", F1), ("FileAttachment.update", F1)], [], "", {}, {})
        self.assertFalse(self.check(broken, "read_before_write"))
        self.assertTrue(self.check(fixed, "read_before_write"))

    def test_write_tools_allowed(self):
        broken = make_run([("AgentTask.create", F1)], [], "", {}, {})
        fixed = make_run([("AgentEscalation.create", F1)], [], "", {}, {})
        self.assertFalse(self.check(broken, "write_tools_allowed"))
        self.assertTrue(self.check(fixed, "write_tools_allowed"))

    def test_claims_vs_state_folder_mismatch(self):
        broken = make_run([], [applied_record("Q")], "",
                          filed_state("A", "x"), filed_state("P"))
        fixed = make_run([], [applied_record("Q")], "",
                         filed_state("A", "x"), filed_state("Q"))
        self.assertFalse(self.check(broken, "claims_vs_state"))
        self.assertTrue(self.check(fixed, "claims_vs_state"))

    def test_claims_vs_state_missing_record(self):
        broken = make_run([], [], "", filed_state("A", "x"), filed_state("Q"))
        fixed = make_run([], [applied_record("Q")], "", filed_state("A", "x"), filed_state("Q"))
        self.assertFalse(self.check(broken, "claims_vs_state"))
        self.assertTrue(self.check(fixed, "claims_vs_state"))

    def test_read_only_state(self):
        broken = make_run([], [], "", {}, {}, [], [{}], mode="read")
        fixed = make_run([], [], "", {}, {}, [], [], mode="read")
        self.assertFalse(self.check(broken, "read_only_state"))
        self.assertTrue(self.check(fixed, "read_only_state"))

    def test_answer_must_cite(self):
        expect = {"answer_must_cite": [F1]}
        broken = make_run([], [], "nothing", {}, {}, expect=expect)
        fixed = make_run([], [], f"see {F1}", {}, {}, expect=expect)
        self.assertFalse(self.check(broken, f"cites:{F1[:8]}"))
        self.assertTrue(self.check(fixed, f"cites:{F1[:8]}"))


if __name__ == "__main__":
    unittest.main()
