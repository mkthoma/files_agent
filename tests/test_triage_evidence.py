# STRIDE T7 - which rows get to vote on where a kind of file lives
# one row planted somewhere in the tenant cant decide a folder by itself (MIN_AGREEING_ROWS), and a '[Files Agent' note on a row another seat updated isnt our own filing so it still counts
import unittest
from agent.safe_reads import folder_named
from agent.skills import triage
from agent.skills.profiles import agent_filed, doc_type_of, load_rules, majority_folder, similar_file_folder
from harness.fake_server import FOREIGN_USER
from helpers import build_runtime, fake_server

HR_FOLDER_ID = "13c03c65-ddae-4d61-9e2f-b9167168277f"  # HR
JIG_FOLDER_ID = "0449912e-f8c2-406f-b983-a2beca76ea93"  # Jig & Fixture Drawings

TIMESHEET_ID = "1ee27946-7064-42e1-afce-376068a545bf"  # timesheet_week33.xlsx (42,115 bytes)
KNOB_ID = "b45cecdd-9f14-491a-a0ee-2826d3fabb15"  # J-KNOB-09_RevA.dxf (61,208 bytes)

# 4 J- drawings already in Jig & Fixture Drawings (each name is there twice)
JIG_DRAWING_IDS = [
    "0eb1563a-d389-466c-bf7e-c4c67c6243f2",  # J-PIN-07_RevB_LocatingPin.pdf
    "2fdbb5cd-a6f3-472e-aa88-09baf502f3df",  # J-PIN-07_RevB_LocatingPin.pdf
    "1304777f-81e3-4074-8422-90b9bc96ec6a",  # J-BRKT-04_RevC_JigBracket.pdf
    "2683b2c8-f700-4870-981c-1fb9c8d53393",  # J-BRKT-04_RevC_JigBracket.pdf
]

# extra files for fake server, ids come from filename so they dont change
PLANTED_TIMESHEET = {"filename": "timesheet_week40.xlsx", "folder": "Purchasing", "tags": ""}  # another teams upload
NEW_TIMESHEET = {"filename": "timesheet_week34.xlsx", "from_email": "sheila.rourke@keystoneprecision.com"}  # in Incoming
NEW_TIMESHEET_ID = "d48ba481-45d5-5c46-8523-ef6af7f2f138"  # timesheet_week34.xlsx

# note we add when filing something, anyone can type the same text into a description
OUR_NOTE = "[Files Agent 2026-09-01] Moved Incoming -> Jig & Fixture Drawings. Score: 3 (threshold 3)."
NOTE_AT = "2026-10-01T09:00:00"  # after fixture capture

# pure tests use short made up user/folder ids
OUR_SEAT = "our-seat"
OTHER_SEAT = "other-seat"


def _hr_timesheets(count, description, updated_by):
    # timesheets already in HR, each with this description and updated_by
    return [{"id": f"x{n}", "filename": f"timesheet_{n}.xlsx", "folder_id": "HR",
             "description": description, "updated_by": updated_by} for n in range(1, count + 1)]

def _plan(server):
    # plan mode tidy plan for Incoming on this server, by file id (nothing written)
    rt, _ = build_runtime("plan", server=server)
    incoming = folder_named(rt.ctx.folders(), "Incoming")
    return {item.row["id"]: item for item in triage.build_plan(rt.ctx, incoming, None)}


def _note_jigs(server, updated_by):
    # adds the provenance note to the 4 J- drawings as a write by updated_by
    for file_id in JIG_DRAWING_IDS:
        row = server.tables["FileAttachment"][file_id]
        row.update(description=f"{row.get('description') or ''}\n{OUR_NOTE}",
                   updated_by=updated_by, updated_at=NOTE_AT)


def _signals(item):
    return sorted({e.signal for e in item.evidence})


class FolderVoteTests(unittest.TestCase):

    def test_one_row_no_folder(self):
        # one timesheet in HR decides nothing, anyone can upload one row
        rows = _hr_timesheets(1, "Weekly timesheet.", OTHER_SEAT)
        folder = majority_folder(rows, skip_folder_ids=set())
        self.assertIsNone(folder)

    def test_two_rows_decide(self):
        rows = _hr_timesheets(2, "Weekly timesheet.", OTHER_SEAT)
        folder = majority_folder(rows, skip_folder_ids=set())
        self.assertEqual(folder, "HR")

    def test_planted_timesheet_no_conflict(self):
        # one timesheet another team put in Purchasing doesnt outvote HR, week 33 still goes to HR
        server = fake_server(extra_files=[PLANTED_TIMESHEET])
        plan = _plan(server)
        timesheet = plan[TIMESHEET_ID]
        self.assertEqual((timesheet.action, timesheet.to_folder, timesheet.score), ("move", HR_FOLDER_ID, 4))
        self.assertNotIn("similar_file_in_folder", _signals(timesheet))

    def test_planted_timesheet_new_file(self):
        # new timesheet w/o description goes to HR (default), not where the planted one is
        server = fake_server(extra_files=[NEW_TIMESHEET, PLANTED_TIMESHEET])
        plan = _plan(server)
        new_timesheet = plan[NEW_TIMESHEET_ID]
        self.assertEqual((new_timesheet.action, new_timesheet.to_folder, new_timesheet.score), ("move", HR_FOLDER_ID, 3))


class ProvenanceNoteTests(unittest.TestCase):

    def test_note_other_seat_not_ours(self):
        row = {"id": "x1", "description": f"Weekly timesheet.\n{OUR_NOTE}", "updated_by": OTHER_SEAT}
        self.assertFalse(agent_filed(row, OUR_SEAT))

    def test_note_our_seat_is_ours(self):
        row = {"id": "x1", "description": f"Weekly timesheet.\n{OUR_NOTE}", "updated_by": OUR_SEAT}
        self.assertTrue(agent_filed(row, OUR_SEAT))

    def test_other_seat_rows_still_count(self):
        # 2 HR timesheets with our note but updated by another seat still point to HR
        rules = load_rules()
        row = {"id": "r", "filename": "timesheet_1.xlsx"}
        others = _hr_timesheets(2, f"Weekly timesheet.\n{OUR_NOTE}", OTHER_SEAT)
        folder = similar_file_folder(row, doc_type_of(row["filename"], rules), others, rules, skip_folder_ids=set(), me=OUR_SEAT)
        self.assertEqual(folder, "HR")

    def test_typed_note_jig_still_votes(self):
        # another seat types our note on the 4 J- drawings, they still vote so J-KNOB-09 keeps score 8
        server = fake_server()
        _note_jigs(server, FOREIGN_USER)
        plan = _plan(server)
        knob = plan[KNOB_ID]
        self.assertEqual((knob.action, knob.to_folder, knob.score), ("move", JIG_FOLDER_ID, 8))
        self.assertIn("similar_file_in_folder", _signals(knob))

    def test_our_note_jig_not_evidence(self):
        # same note but our seat updated them = our own filing, J-KNOB-09 loses that point (7)
        server = fake_server()
        _note_jigs(server, server.me["id"])
        plan = _plan(server)
        knob = plan[KNOB_ID]
        self.assertEqual((knob.action, knob.to_folder, knob.score), ("move", JIG_FOLDER_ID, 7))
        self.assertNotIn("similar_file_in_folder", _signals(knob))


if __name__ == "__main__":
    unittest.main()
