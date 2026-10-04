# STRIDE T6 + T9 for restore
# T6: restore checks its inputs, needs the write journal and only puts back our 2 fields - folder + description
# T9: a description another team edited before our write goes back to their text, not the snapshot
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import harness.__main__ as harness_cli
from agent.redact import Redactor
from agent.skills import triage
from agent.snapshot import RestoreRefused, diff, plan_restore, restore, save, take
from agent.trace import Trace
from harness.fake_server import FOREIGN_USER
from helpers import build_runtime

INCOMING_FOLDER_ID = "6f8a3ed1-f2df-46a7-8dcb-275e9494c799"  # Incoming

# Incoming originals each have a 880 byte copy with the same name, so sizes are in the comments
TIMESHEET_ID = "1ee27946-7064-42e1-afce-376068a545bf"  # timesheet_week33.xlsx (42,115 bytes)
KNOB_ID = "b45cecdd-9f14-491a-a0ee-2826d3fabb15"  # J-KNOB-09_RevA.dxf (61,208 bytes)
MILL_CERT_ID = "680e8af6-15f3-49c6-b70b-987316fa5775"  # Cert_MillCert_SS304_Heat90114.pdf (149,770 bytes)
W9_ID = "81857de6-e6e9-41c5-9da8-67cb5d1903c1"  # W9_JMillerWelding_2026.pdf (96,331 bytes)
PO_ID = "732439a0-7f36-4d31-ac3b-f406c41c00bd"  # PO_4471_ApexMetals_signed.pdf (218,044 bytes)

# 5 files the Incoming tidy moves, in id order (thats how restore reports them)
MOVED_IDS = [TIMESHEET_ID, MILL_CERT_ID, PO_ID, W9_ID, KNOB_ID]

# stand-in tests restore one file f for our seat (people use this account in the web UI too)
FILE_ID = "f"  # only file on the allowlist
SEAT_ID = "me"  # our seat user id
# f before the run
SNAPSHOT = {FILE_ID: {"folder_id": "INC", "filename": "W9.pdf", "tags": "untriaged", "description": "d",
                      "is_archived": 0}}
# tags a teammate set on f in the web UI (under our seat account) after our run
TEAMMATE_TAGS = "untriaged,vendor-tax"

# note the AP seat adds between our snapshot and our write
AP_NOTE = "Vendor TIN verified by AP team on 2 Oct."
# provenance note like triage appends it (_note in triage.py)
OUR_NOTE = "[Files Agent 2026-10-02] Moved Incoming -> Purchasing. Evidence: description. Score: 4 (threshold 3)."


class FakeAdminClient:
    # fake admin mcp client - get from in memory rows, applies each update, logs every call with args

    def __init__(self, rows):
        self.rows = {file_id: dict(row) for file_id, row in rows.items()}
        self.calls = []

    def call(self, tool, args):
        self.calls.append((tool, dict(args)))
        row = self.rows[args["id"]]
        if tool == "FileAttachment.update":
            row.update({key: value for key, value in args.items() if key != "id"})
        return dict(row)


def _tmp_dir(test):
    folder = tempfile.TemporaryDirectory()
    test.addCleanup(folder.cleanup)
    return Path(folder.name)


def _updates(client):
    return [args for tool, args in client.calls if tool == "FileAttachment.update"]


def _restore_cmd(argv, runtime=None):
    # runs `python -m harness restore <argv>` in process -> (exit code, stdout, stderr, build calls)
    # build is swapped for one that returns `runtime` so nothing lands in runs/ even if a fix breaks
    build_calls = []

    def fake_build(*args, **kwargs):
        build_calls.append(args)
        return runtime

    orig_build = harness_cli.build
    harness_cli.build = fake_build
    out, err = io.StringIO(), io.StringIO()
    try:
        with redirect_stdout(out), redirect_stderr(err):
            code = harness_cli.main(["restore", *argv])
    finally:
        harness_cli.build = orig_build
    return code, out.getvalue(), err.getvalue(), build_calls


class RestoreInputTests(unittest.TestCase):  # T6

    def test_bad_snapshot_or_journal_refused(self):
        # unknown field, wrong type, outside id, or a journal entry we never write -> refused before any call
        snapshot_row = SNAPSHOT[FILE_ID]
        cases = [
            ("unknown snapshot field", {FILE_ID: {**snapshot_row, "content_hash": "x"}}, None,
             "snapshot row f has unexpected fields ['content_hash']; nothing restored"),
            ("is_archived that is text", {FILE_ID: {**snapshot_row, "is_archived": "yes"}}, None,
             "snapshot row f has an is_archived that is not true or false; nothing restored"),
            ("folder_id that is a number", {FILE_ID: {**snapshot_row, "folder_id": 42}}, None,
             "snapshot row f has a folder_id that is not text; nothing restored"),
            ("id outside the allow-list", {"outside-id": snapshot_row}, None,
             "snapshot holds ids outside the write allow-list ['outside-id']; nothing restored"),
            ("journal update of tags", SNAPSHOT, [{"tool": "FileAttachment.update", "id": FILE_ID, "changes": {"tags": "x"}}],
             "write journal entry for f changes has unexpected fields ['tags']; nothing restored"),
            ("journal tool the agent never uses", SNAPSHOT, [{"tool": "DriveShare.share_file", "id": FILE_ID, "args": {}}],
             "write journal entry for f names 'DriveShare.share_file', a tool the agent never writes with; nothing restored"),
        ]
        for label, snapshot, writes, message in cases:
            with self.subTest(label):
                client = FakeAdminClient({FILE_ID: {**snapshot_row, "folder_id": "HR", "updated_by": SEAT_ID}})

                with self.assertRaises(RestoreRefused) as refused:
                    restore(client, snapshot, Trace(None, Redactor()), allowlist=frozenset({FILE_ID}), writes=writes, me=SEAT_ID)

                self.assertEqual(str(refused.exception), message)
                self.assertEqual(client.calls, [])

    def test_no_journal_only_our_fields(self):
        # no journal: folder goes back but teammates tags + a filename edited into the snapshot never get written
        snap = {FILE_ID: {**SNAPSHOT[FILE_ID], "filename": "W9_renamed.pdf"}}
        now = {**SNAPSHOT[FILE_ID], "folder_id": "HR", "tags": TEAMMATE_TAGS, "updated_by": SEAT_ID}
        client = FakeAdminClient({FILE_ID: now})
        report = restore(client, snap, Trace(None, Redactor()), allowlist=frozenset({FILE_ID}), writes=None, me=SEAT_ID)
        self.assertEqual(_updates(client), [{"folder_id": "INC", "id": FILE_ID}])
        self.assertEqual(client.rows[FILE_ID]["tags"], TEAMMATE_TAGS)
        self.assertEqual(client.rows[FILE_ID]["filename"], "W9.pdf")
        self.assertEqual(report["restored"], [FILE_ID])
        self.assertEqual(report["conflicts_left_alone"], {FILE_ID: {
            "filename": {"snapshot": "W9_renamed.pdf", "now": "W9.pdf", "updated_by": SEAT_ID},
            "tags": {"snapshot": "untriaged", "now": TEAMMATE_TAGS, "updated_by": SEAT_ID},
        }})
        self.assertEqual(report["mode"], "updated_by-fallback")

    def test_cli_restore_no_journal_refused(self):
        # harness restore without writes-1.json next to the snapshot is refused, it cant guess which fields are ours
        folder = _tmp_dir(self)
        snapshot_path = save(SNAPSHOT, folder / "snapshot-1.json")
        code, out, err, build_calls = _restore_cmd([str(snapshot_path), "--target", "fake"])
        self.assertEqual(code, 3, msg=err)
        self.assertTrue(err.startswith(f"refused: no write journal at {folder / 'writes-1.json'}"), msg=err)
        self.assertIn("nothing restored", err)
        self.assertEqual(out, "")
        self.assertEqual(build_calls, [])

    def test_cli_restore_no_journal_flag(self):
        # --no-journal runs, falls back to updated_by and puts back the 5 files the tidy moved
        rt, _ = build_runtime("apply")
        snapshot = take(rt.admin_mcp, rt.guard.allowlist)
        triage.run(rt.ctx, {})
        snapshot_path = save(snapshot, _tmp_dir(self) / "snapshot-1.json")
        code, out, err, build_calls = _restore_cmd([str(snapshot_path), "--target", "fake", "--no-journal"], runtime=rt)
        self.assertEqual(code, 0, msg=err)
        self.assertEqual(len(build_calls), 1)
        self.assertIn("note: no write journal at", err)
        report = json.loads(out)
        self.assertEqual(report["mode"], "updated_by-fallback")
        self.assertEqual(report["restored"], MOVED_IDS)
        self.assertEqual(diff(snapshot, take(rt.admin_mcp, rt.guard.allowlist)), {})


class ForeignEditBeforeOurWriteTests(unittest.TestCase):  # T9

    def test_plan_restores_their_text(self):
        # description goes back to the AP teams text (journal before), not the older snapshot text
        their_text = f"d\n{AP_NOTE}"
        ours = f"{their_text}\n{OUR_NOTE}"
        snapshot = {FILE_ID: {"folder_id": "INC", "description": "d"}}
        now = {FILE_ID: {"folder_id": "PUR", "description": ours, "updated_by": SEAT_ID}}
        writes = [{"tool": "FileAttachment.update", "id": FILE_ID, "changes": {"folder_id": "PUR", "description": ours},
                   "before": {"folder_id": "INC", "description": their_text}}]
        
        to_put_back, conflicts = plan_restore(snapshot, now, writes, SEAT_ID)
        self.assertEqual(to_put_back, {FILE_ID: {"folder_id": "INC", "description": their_text}})
        self.assertEqual(conflicts, {})

    def test_tidy_restore_keeps_their_note(self):
        # AP team adds a note after our snapshot, restore only takes off our note and lists it in kept_foreign_edits
        rt, server = build_runtime("apply")
        snapshot = take(rt.admin_mcp, rt.guard.allowlist)
        w9 = server.tables["FileAttachment"][W9_ID]
        their_text = f"{w9['description']}\n{AP_NOTE}"
        w9.update(description=their_text, updated_by=FOREIGN_USER)
        triage.run(rt.ctx, {})
        # our tidy put its note after their text (it read the row after they edited)
        self.assertTrue(w9["description"].startswith(f"{their_text}\n[Files Agent"), msg=w9["description"])
        report = restore(rt.admin_mcp, snapshot, Trace(None, Redactor()), allowlist=rt.guard.allowlist,
                         writes=rt.guard.writes, me=rt.session.me()["id"])

        self.assertEqual(w9["description"], their_text)
        self.assertEqual(w9["folder_id"], INCOMING_FOLDER_ID)
        self.assertEqual(report["kept_foreign_edits"],
                         {W9_ID: {"description": {"snapshot": snapshot[W9_ID]["description"], "restored_to": their_text}}})
        self.assertEqual(report["restored"], MOVED_IDS)
        self.assertEqual(report["conflicts_left_alone"], {})


if __name__ == "__main__":
    unittest.main()
