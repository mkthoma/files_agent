import unittest

from agent.runtime import build
from agent.safe_reads import folder_named
from agent.skills import triage
from harness.fake_server import FakeServer

MILL_CERT = "680e8af6-15f3-49c6-b70b-987316fa5775"
TIMESHEET = "1ee27946-7064-42e1-afce-376068a545bf"
UNTITLED = "60f685c9-bcb5-43a3-a403-18b7e9d76368"
QUALITY = "585da032-09fe-43cd-9440-c6f01824f5fc"
HR = "13c03c65-ddae-4d61-9e2f-b9167168277f"


def plan_with_extras():
    server = FakeServer.from_fixture("keystone", None, extra_files=[
        {"filename": "notes.pdf", "description": "Belongs in Quality"},
        {"filename": "timesheet_week40.xlsx", "description": "Belongs in Quality"},
    ])
    server.armed = False
    rt = build("keystone", "fake", "plan", None, transport=server)
    incoming = folder_named(rt.ctx.folders(), "Incoming")
    plan = triage.build_plan(rt.ctx, incoming, None)
    by_id = {p.row["id"]: p for p in plan}
    by_name = {p.row["filename"]: p for p in plan}
    return by_id, by_name


def writes_by_tool(rt):
    counts = {}
    for w in rt.guard.writes:
        counts[w["tool"]] = counts.get(w["tool"], 0) + 1
    return counts


class ScoringTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.by_id, cls.by_name = plan_with_extras()

    def test_mill_cert_moves_to_quality(self):
        item = self.by_id[MILL_CERT]
        self.assertEqual(item.action, "move")
        self.assertEqual(item.to_folder, QUALITY)
        self.assertEqual(item.score, 5)

    def test_timesheet_moves_to_hr(self):
        item = self.by_id[TIMESHEET]
        self.assertEqual(item.action, "move")
        self.assertEqual(item.to_folder, HR)
        self.assertEqual(item.score, 4)

    def test_file_with_no_evidence_is_refused(self):
        item = self.by_id[UNTITLED]
        self.assertEqual(item.action, "refuse")
        self.assertEqual(list(item.missing), ["file contents", "who sent it"])

    def test_description_alone_files_nothing(self):
        item = self.by_name["notes.pdf"]
        self.assertEqual(item.action, "escalate")
        self.assertIsNone(item.to_folder)
        self.assertEqual(list(item.missing), ["document type", "which folder it belongs in"])

    def test_disagreeing_description_is_a_conflict(self):
        item = self.by_name["timesheet_week40.xlsx"]
        self.assertEqual(item.action, "conflict")
        self.assertIn("HR", item.missing[0])
        self.assertIn("Quality", item.missing[0])


class SecondTidyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server = FakeServer.from_fixture("keystone", None)
        server.armed = False
        cls.first = build("keystone", "fake", "apply", None, transport=server)
        triage.run(cls.first.ctx, {})
        cls.second = build("keystone", "fake", "apply", None, transport=server)
        triage.run(cls.second.ctx, {})

    def test_first_pass_files_five_and_escalates_thirteen(self):
        self.assertEqual(writes_by_tool(self.first).get("FileAttachment.update", 0), 5)
        self.assertEqual(writes_by_tool(self.first).get("AgentEscalation.create", 0), 13)
        self.assertEqual(writes_by_tool(self.first).get("AgentSession.create", 0), 1)

    def test_second_pass_writes_nothing(self):
        self.assertEqual(writes_by_tool(self.second).get("FileAttachment.update", 0), 0)
        self.assertEqual(writes_by_tool(self.second).get("AgentEscalation.create", 0), 0)
        self.assertEqual(writes_by_tool(self.second).get("AgentSession.create", 0), 0)

    def test_second_pass_escalations_are_deduped(self):
        escalations = [r for r in self.second.ctx.records.all() if r.skill == "escalate"]
        self.assertTrue(escalations)
        for record in escalations:
            self.assertEqual(record.action, "already_escalated")


if __name__ == "__main__":
    unittest.main()
