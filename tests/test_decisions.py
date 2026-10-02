import unittest
import uuid

from agent.config import KEYSTONE_INCOMING_ALLOWLIST
from agent.runtime import build
from agent.safe_reads import folder_named
from agent.skills import access, triage
from harness import fixtures, preflight
from harness.fake_server import FakeServer

TIMESHEET = "1ee27946-7064-42e1-afce-376068a545bf"
PO_ONE = "82f83d94-5a46-4df3-9ee1-61e8b3c79d6e"
PO_COPY = "c0c8b9c0-85c2-4528-b574-1f35665616b6"
SCAN_A = "b1d3894c-12e9-4ee1-b1da-82c7191ed4a0"
SCAN_B = "f6f748ab-6a24-4c76-ac54-39b24cf3bc9b"
EXTRA_TIMESHEET = str(uuid.uuid5(uuid.NAMESPACE_URL, "extra-file:timesheet_week33.xlsx"))


def plan_runtime(extra_files=None, mode="plan", live_allowlist=False):
    server = FakeServer.from_fixture("keystone", None, extra_files=extra_files or [])
    server.armed = False
    return build("keystone", "fake", mode, None, transport=server, live_allowlist=live_allowlist)


class LiveScopeTest(unittest.TestCase):
    def test_live_run_touches_only_the_nine(self):
        server = FakeServer.from_fixture("keystone", None)
        server.armed = False
        rt = build("keystone", "fake", "apply", None, transport=server, live_allowlist=True)
        triage.run(rt.ctx, {})
        self.assertEqual(len(rt.ctx.allowlist), 9)
        tools = [w["tool"] for w in rt.guard.writes]
        self.assertEqual(tools.count("FileAttachment.update"), 5)
        self.assertEqual(tools.count("AgentEscalation.create"), 4)
        skipped = [r for r in rt.ctx.records.all()
                   if r.skill == "triage_folder" and r.action == "out_of_scope"]
        self.assertEqual(len(skipped), 9)
        updated = [w.get("id") for w in rt.guard.writes if w["tool"] == "FileAttachment.update"]
        self.assertTrue(updated)
        for file_id in updated:
            self.assertIn(file_id, KEYSTONE_INCOMING_ALLOWLIST)


class PreflightTest(unittest.TestCase):
    def test_quiet_when_nothing_changed(self):
        rt = plan_runtime()
        problems, warnings = preflight.assess(rt, fixtures.load("keystone"))
        self.assertEqual(problems, [])
        self.assertEqual(len(warnings), 9)

    def test_new_file_of_same_kind_is_a_problem(self):
        rt = plan_runtime([{"filename": "MillCert_A36_Heat70.pdf", "folder": "Purchasing", "tags": ""}])
        problems = preflight.check(rt, fixtures.load("keystone"))
        self.assertEqual(len(problems), 1)
        self.assertIn("related to an allow-listed file", problems[0])

    def test_unrelated_file_is_ignored(self):
        rt = plan_runtime([{"filename": "holiday_rota.docx", "folder": "HR"}])
        self.assertEqual(preflight.check(rt, fixtures.load("keystone")), [])

    def test_new_drawings_with_same_prefix_are_problems(self):
        extras = [{"filename": f"J-BASE-0{n}_RevA.dxf", "folder": "Purchasing", "tags": ""} for n in range(3)]
        rt = plan_runtime(extras)
        self.assertEqual(len(preflight.check(rt, fixtures.load("keystone"))), 3)

    def test_renamed_folder_is_a_problem(self):
        server = FakeServer.from_fixture("keystone", None)
        server.tables["DriveFolder"]["585da032-09fe-43cd-9440-c6f01824f5fc"]["name"] = "QA"
        server.armed = False
        rt = build("keystone", "fake", "plan", None, transport=server)
        problems = preflight.check(rt, fixtures.load("keystone"))
        self.assertEqual(len(problems), 1)
        self.assertIn("renamed, moved or archived", problems[0])


class SameNameTest(unittest.TestCase):
    def test_second_timesheet_holds_back_the_first(self):
        rt = plan_runtime([{"filename": "timesheet_week33.xlsx", "folder": "HR", "tags": ""}],
                          live_allowlist=True)
        incoming = folder_named(rt.ctx.folders(), "Incoming")
        item = next(p for p in triage.build_plan(rt.ctx, incoming, None) if p.row["id"] == TIMESHEET)
        self.assertEqual(item.action, "escalate")
        self.assertEqual(item.basis, "same filename in the destination")
        self.assertEqual(item.original_id, EXTRA_TIMESHEET)


class AmbiguityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rt = plan_runtime()

    def ids_for(self, text):
        return {r["id"] for r in access.resolve_file(self.rt.ctx, text)}

    def test_duplicate_po_matches_both(self):
        self.assertEqual(self.ids_for("Delete the duplicate PO file"), {PO_COPY, PO_ONE})

    def test_shared_name_matches_both_scans(self):
        self.assertEqual(self.ids_for("scan0042.pdf"), {SCAN_A, SCAN_B})

    def test_id_picks_exactly_one(self):
        self.assertEqual(self.ids_for(PO_ONE), {PO_ONE})

    def test_copy_of_id_picks_nothing(self):
        self.assertEqual(self.ids_for(f"the copy of {PO_ONE}"), set())

    def test_pick_by_id_then_refuse(self):
        rt = plan_runtime()
        result = access.remove_file(rt.ctx, {"file": PO_ONE})
        self.assertNotIn(PO_COPY, result["answer_text"])
        records = rt.ctx.records.all()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].action, "refuse_remove")


if __name__ == "__main__":
    unittest.main()
