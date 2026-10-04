# tidy rules: same name files + duplicates + scope + running twice
import unittest

from agent.config import KEYSTONE_INCOMING_ALLOWLIST
from agent.safe_reads import folder_named
from agent.skills import triage
from agent.skills.triage import PlanItem
from helpers import build_runtime

HR_FOLDER_ID = "13c03c65-ddae-4d61-9e2f-b9167168277f"  # HR
INCOMING_FOLDER_ID = "6f8a3ed1-f2df-46a7-8dcb-275e9494c799"  # Incoming

# every original in Incoming has a 880 byte copy with same name, so size is in the comments
MILL_CERT_ID = "680e8af6-15f3-49c6-b70b-987316fa5775"  # Cert_MillCert_SS304_Heat90114.pdf (149,770 bytes)
MILL_CERT_COPY_ID = "782cdca0-b02d-4735-936b-a75cfac15892"  # Cert_MillCert_SS304_Heat90114.pdf (880 bytes)
KNOB_ID = "b45cecdd-9f14-491a-a0ee-2826d3fabb15"  # J-KNOB-09_RevA.dxf (61,208 bytes)
KNOB_COPY_ID = "9b27de51-e04a-404c-b737-3d0133580b39"  # J-KNOB-09_RevA.dxf (880 bytes)
IMG_ID = "8018a70b-47d5-472b-88b6-b1ced1ced8b0"  # IMG_20260814_093214.jpg (3,118,440 bytes)
IMG_COPY_ID = "9af1955d-753e-4c7a-b8f9-6e885ca3057e"  # IMG_20260814_093214.jpg (880 bytes)

# 9 originals allowed by live cap: these 5 get filed, these 4 escalated
FILED_IDS = {
    MILL_CERT_ID,
    KNOB_ID,
    "732439a0-7f36-4d31-ac3b-f406c41c00bd",  # PO_4471_ApexMetals_signed.pdf (218,044 bytes)
    "81857de6-e6e9-41c5-9da8-67cb5d1903c1",  # W9_JMillerWelding_2026.pdf (96,331 bytes)
    "1ee27946-7064-42e1-afce-376068a545bf",  # timesheet_week33.xlsx (42,115 bytes)
}
ESCALATED_IDS = {
    IMG_ID,
    "82f83d94-5a46-4df3-9ee1-61e8b3c79d6e",  # PO_4471_ApexMetals_signed (1).pdf (218,044 bytes)
    "60f685c9-bcb5-43a3-a403-18b7e9d76368",  # Untitled.pdf (88,420 bytes)
    "b1d3894c-12e9-4ee1-b1da-82c7191ed4a0",  # scan0042.pdf (511,903 bytes)
}

# the 9 copies platform added next to originals, live cap leaves them out
COPY_IDS = {
    MILL_CERT_COPY_ID,
    KNOB_COPY_ID,
    IMG_COPY_ID,
    "c0c8b9c0-85c2-4528-b574-1f35665616b6",  # PO_4471_ApexMetals_signed (1).pdf (880 bytes)
    "3dd05bfb-f423-44bb-ad0f-fc94acca3ced",  # PO_4471_ApexMetals_signed.pdf (880 bytes)
    "30f72e5c-e340-4c9c-9495-06df2f0aa4f6",  # Untitled.pdf (880 bytes)
    "20d633ba-251f-494a-974d-e83d5e9d0695",  # W9_JMillerWelding_2026.pdf (880 bytes)
    "f6f748ab-6a24-4c76-ac54-39b24cf3bc9b",  # scan0042.pdf (880 bytes)
    "6477085f-2a2a-4da8-9009-a86af39e69a0",  # timesheet_week33.xlsx (880 bytes)
}

# extra file ids come from filename on fake server so they dont change
WEEK40_ID = "a9095b10-52dc-5657-8ed8-10cfcaa9205a"  # timesheet_week40.xlsx
WEEK40_COPY_ID = "8cc54863-7d02-50ce-a142-5c3fdd795cf1"  # timesheet_week40 (1).xlsx
WEEK40_FILES = [
    {"filename": "timesheet_week40.xlsx", "content_hash": "h40", "size_bytes": 5000, "from_email": "sheila.rourke@keystoneprecision.com"},
    {"filename": "timesheet_week40 (1).xlsx", "content_hash": "h40", "size_bytes": 5000},
]


class FakeCtx:
    # fake skill ctx, only the allowlist + folder_name that gives back the id as is

    def __init__(self, allowlist):
        self.allowlist = frozenset(allowlist)

    def folder_name(self, folder_id):
        return folder_id


def _planned_move(file_id, filename, score):
    row = {"id": file_id, "filename": filename, "size_bytes": 100}
    return PlanItem(row, "move", to_folder="D1", score=score)


def _writes(write_log, tool):
    return [entry for entry in write_log if entry["tool"] == tool]


def _capped_tidy():
    # apply tidy with the live allowlist (only the 9 originals)
    rt, server = build_runtime("apply", live_allowlist=True)
    triage.run(rt.ctx, {})
    return rt, server


def _tidy_week40():
    # apply tidy with week 40 timesheet and its trusted copy added
    rt, server = build_runtime("apply", extra_files=WEEK40_FILES)
    triage.run(rt.ctx, {})
    return rt, server


class SameNameTests(unittest.TestCase):

    def test_higher_score_filed(self):
        # SAME-1 two same name files into one folder, only the higher score gets filed
        higher = _planned_move("a", "r.pdf", 5)
        lower = _planned_move("b", "r.pdf", 3)
        triage._hold_name_collisions(FakeCtx({"a", "b"}), [higher, lower], [])
        self.assertEqual(higher.action, "move")
        self.assertEqual(lower.action, "escalate")
        self.assertEqual(lower.basis, "same filename in the destination")
        self.assertEqual(lower.original_id, "a")
        self.assertIn("possible_copy", [e.signal for e in lower.evidence])

    def test_tie_escalates_both(self):
        # SAME-1 same score -> both escalated, case dont matter
        first = _planned_move("a", "r.pdf", 3)
        second = _planned_move("b", "R.PDF", 3)
        triage._hold_name_collisions(FakeCtx({"a", "b"}), [first, second], [])
        self.assertEqual(first.action, "escalate")
        self.assertEqual(second.action, "escalate")

    def test_880_byte_copies_held(self):
        # SAME-2 880 byte copies of J-KNOB-09 and mill cert escalated, originals still move
        rt, _ = build_runtime("plan")
        incoming = folder_named(rt.ctx.folders(), "Incoming")
        plan = {item.row["id"]: item for item in triage.build_plan(rt.ctx, incoming, None)}
        for copy_id, original_id in [(KNOB_COPY_ID, KNOB_ID),(MILL_CERT_COPY_ID, MILL_CERT_ID)]:
            with self.subTest(copy=copy_id):
                held = plan[copy_id]
                self.assertEqual(held.action, "escalate")
                self.assertEqual(held.basis, "same filename in the destination")
                self.assertEqual(held.original_id, original_id)
                self.assertIn(original_id, held.missing[0])
                self.assertIn(f"{copy_id} (880 bytes", held.missing[0])
                self.assertEqual(plan[original_id].action, "move")


class PossibleCopyTests(unittest.TestCase):  # DUPC-2
    # decision C - a copy never gets filed, moved or archived, only one escalation

    def test_trusted_copy_stays(self):
        # original goes to HR, trusted copy stays in Incoming - not archived, not written
        _, server = _tidy_week40()
        original = server.tables["FileAttachment"][WEEK40_ID]
        copy = server.tables["FileAttachment"][WEEK40_COPY_ID]
        updated_ids = [entry["id"] for entry in _writes(server.write_log, "FileAttachment.update")]
        self.assertEqual(original["folder_id"], HR_FOLDER_ID)
        self.assertFalse(original["is_archived"])
        self.assertEqual(copy["folder_id"], INCOMING_FOLDER_ID)
        self.assertFalse(copy["is_archived"])
        self.assertIsNone(copy["description"])
        self.assertNotIn(WEEK40_COPY_ID, updated_ids)

    def test_copy_escalated_once(self):
        # no archive record, just one escalation asking someone to compare the 2 files
        rt, server = _tidy_week40()
        archived = [r for r in rt.ctx.records.all() if r.action == "archive_duplicate"]
        subject = f"[files-agent] {WEEK40_COPY_ID} timesheet_week40 (1).xlsx"
        reasons = [entry["args"]["reason"] for entry in _writes(server.write_log, "AgentEscalation.create") if entry["args"]["subject"] == subject]
        self.assertEqual(archived, [])
        self.assertEqual(len(reasons), 1)
        self.assertIn(WEEK40_ID, reasons[0])
        self.assertIn("file it, keep both, or have one removed", reasons[0])
        self.assertIn("not the file bytes", reasons[0])


class ScopeTests(unittest.TestCase):

    def test_live_cap_copies_out_of_scope(self):
        # SCOPE-1 live cap: all 9 copies recorded out_of_scope and skipped
        rt, _ = _capped_tidy()
        # only count triage records, escalator adds its own if a copy got thru
        out_of_scope = [r for r in rt.ctx.records.all() if r.skill == "triage_folder" and r.action == "out_of_scope"]
        self.assertEqual(rt.ctx.allowlist, KEYSTONE_INCOMING_ALLOWLIST)
        self.assertEqual(len(out_of_scope), 9)
        self.assertEqual({r.status for r in out_of_scope}, {"skipped"})
        self.assertCountEqual([r.target_id for r in out_of_scope], COPY_IDS)

    def test_live_cap_only_originals(self):
        # SCOPE-1 live cap: only 5 originals moved and only 4 escalated
        rt, server = _capped_tidy()

        updated_ids = [entry["id"] for entry in _writes(server.write_log, "FileAttachment.update")]
        subjects = [entry["args"]["subject"] for entry in _writes(server.write_log, "AgentEscalation.create")]
        self.assertCountEqual(updated_ids, FILED_IDS)
        self.assertEqual(len(_writes(server.write_log, "AgentSession.create")), 1)
        self.assertEqual(len(subjects), 4)
        # subject is "[files-agent] <file id> <filename>"
        self.assertCountEqual([s.split()[1] for s in subjects], ESCALATED_IDS)
        self.assertEqual(rt.trace.of_kind("write_blocked"), [])

    def test_escalator_refuses_outside_allowlist(self):
        # SCOPE-2 copy outside allowlist -> escalator skips it, nothing written
        rt, server = build_runtime("apply", live_allowlist=True)
        row = server.tables["FileAttachment"][IMG_COPY_ID]
        record = rt.ctx.escalator.escalate(row, "why", "insufficient_evidence", ["x"])
        self.assertEqual(record.action, "out_of_scope")
        self.assertEqual(record.status, "skipped")
        self.assertEqual(server.write_log, [])

    def test_plan_mode_no_creates(self):
        # SCOPE-3 plan only tidy plans 13 escalations, never tries to create session or escalation
        rt, server = build_runtime("plan")
        summary = triage.run(rt.ctx, {})
        escalations = [r for r in rt.ctx.records.all() if r.skill == "escalate"]
        not_moved = [item["id"] for item in summary["plan"] if item["action"] != "move"]
        self.assertEqual(summary["mode"], "plan only - nothing was changed")
        self.assertEqual(len(escalations), 13)
        self.assertEqual({(r.action, r.status) for r in escalations}, {("escalate", "planned")})
        self.assertCountEqual([r.target_id for r in escalations], not_moved)
        self.assertEqual(rt.ctx.records.with_status("escalated"), [])
        self.assertEqual(server.write_log, [])
        self.assertNotIn("AgentSession.create", server.calls)
        self.assertNotIn("AgentEscalation.create", server.calls)
        self.assertEqual(rt.trace.of_kind("write_blocked"), [])

    def test_plan_mode_escalator(self):
        # SCOPE-3 escalator called directly in plan mode gives planned record with the subject
        rt, server = build_runtime("plan")
        row = server.tables["FileAttachment"][IMG_ID]
        record = rt.ctx.escalator.escalate(row, "why", "insufficient_evidence", ["x"])
        self.assertEqual(record.action, "escalate")
        self.assertEqual(record.status, "planned")
        self.assertEqual(record.details["subject"], f"[files-agent] {IMG_ID} IMG_20260814_093214.jpg")


class RunTwiceTests(unittest.TestCase):  # IDEM-1

    def test_second_tidy_no_writes(self):
        # 2nd tidy on same server writes nothing, all 13 skipped as already escalated
        first, server = build_runtime("apply")
        triage.run(first.ctx, {})
        first_pass = list(server.write_log)
        escalated_ids = [r.target_id for r in first.ctx.records.with_status("escalated")]
        second, _ = build_runtime("apply", server=server)
        triage.run(second.ctx, {})
        already = [r for r in second.ctx.records.all() if r.action == "already_escalated"]
        self.assertEqual(len(_writes(first_pass, "FileAttachment.update")), 5)
        self.assertEqual(len(_writes(first_pass, "AgentSession.create")), 1)
        self.assertEqual(len(_writes(first_pass, "AgentEscalation.create")), 13)
        self.assertEqual(server.write_log[len(first_pass):], [])
        self.assertEqual(len(already), 13)
        self.assertEqual({r.status for r in already}, {"skipped"})
        self.assertCountEqual([r.target_id for r in already], escalated_ids)


if __name__ == "__main__":
    unittest.main()