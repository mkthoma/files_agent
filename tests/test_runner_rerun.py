# STRIDE R1 - a live write task runs once so a rerun cant overwrite the first runs evidence
# each test points runner.RUNS_DIR at a temp folder with an earlier live TI2L attempt (hand written like the runner leaves one) then plans a new live TI2L run. real runs/ never used
import contextlib
import io
import json
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from harness import runner
from harness.runner import RunRefused, planned_runs
from harness.tasks import load_all

TASK_ID = "TI2L"  # the only live_write task
SET_NAME = "live-write"  # set name from the README live command
NEW_SET_NAME = "live-write-2"  # new set name someone might try instead

INCOMING_FOLDER_ID = "6f8a3ed1-f2df-46a7-8dcb-275e9494c799"  # Incoming
HR_FOLDER_ID = "13c03c65-ddae-4d61-9e2f-b9167168277f"  # HR
TIMESHEET_ID = "1ee27946-7064-42e1-afce-376068a545bf"  # timesheet_week33.xlsx (original, allow-listed)

# journal entry the write guard saves when it moves the timesheet Incoming -> HR
TIMESHEET_MOVE = {"tool": "FileAttachment.update", "id": TIMESHEET_ID, "changes": {"folder_id": HR_FOLDER_ID},
                  "before": {"folder_id": INCOMING_FOLDER_ID}}

MODEL_ERROR = "ModelError: Messages API HTTP 529: overloaded"  # model failed before asking for any write

# run file of a live attempt that stopped on a model error, reads but never calls a write tool
NO_WRITE_RUN = [
    {"kind": "manifest", "schema": 1, "task": {"id": TASK_ID}, "repeat_index": 1, "target": "live"},
    {"kind": "pass_start", "index": 0},
    {"kind": "mcp_call", "tool": "FileAttachment.get", "ok": True},
    {"kind": "run_error", "error": MODEL_ERROR},
    {"kind": "result", "passes": [], "error": MODEL_ERROR},
]
# live attempt killed mid pass, never got as far as a result
KILLED_RUN = NO_WRITE_RUN[:3]

ATTEMPT_FILES = ["1.jsonl", "snapshot-1.json", "snapshot-1.meta.json", "writes-1.json"]  # what one live attempt leaves
ATTEMPT_FOLDER = re.compile(r"attempt-\d{8}-\d{6}-\d{6}")  # attempt-<date>-<time>-<microseconds>

REFUSAL = ("TI2L already ran live and may have sent writes ({path}), and live write tasks run once; nothing was "
           "overwritten. To undo that run use `python -m harness restore`; move its folder out of runs/ only if a "
           "second live run has been approved")
MOVED_NOTE = ("TI2L: an earlier attempt here sent no write; moved 1.jsonl, snapshot-1.json, snapshot-1.meta.json, "
              "writes-1.json to {dest}\n")


def _write_attempt(task_folder, events, journal):
    # files one live attempt leaves - run file, snapshot, snapshot meta and write journal
    task_folder.mkdir(parents=True)
    run_lines = "".join(json.dumps(event) + "\n" for event in events)
    (task_folder / "1.jsonl").write_text(run_lines, encoding="utf-8")
    snap = {TIMESHEET_ID: {"folder_id": INCOMING_FOLDER_ID}}
    (task_folder / "snapshot-1.json").write_text(json.dumps(snap), encoding="utf-8")
    meta = {"target": "live","business": "keystone"}
    (task_folder / "snapshot-1.meta.json").write_text(json.dumps(meta), encoding="utf-8")
    (task_folder / "writes-1.json").write_text(json.dumps(journal), encoding="utf-8")


def _contents(folder):
    return {path.name: path.read_bytes() for path in folder.iterdir() if path.is_file()}


class LiveRerunTests(unittest.TestCase):

    def setUp(self):
        self.runs_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.enterContext(mock.patch.object(runner, "RUNS_DIR", self.runs_dir))
        # runner reads settings itself so keep local .env out. both write switches are on so
        # the once-only rule is the only thing that can stop the new run
        self.enterContext(mock.patch("agent.config.load_env", return_value={}))
        self.enterContext(mock.patch.dict(os.environ, {"AS_ALLOW_WRITES": "1"}))
        self.ti2l = load_all()[TASK_ID]
        self.earlier = self.runs_dir / SET_NAME / TASK_ID

    def _plan(self, set_name):
        # plan a new live TI2L run in this set, like `harness run TI2L --target live --live-apply` does first
        return planned_runs(self.ti2l, target="live", live_apply=True, set_dir=self.runs_dir / set_name)

    def test_journal_entry_blocks_rerun(self):
        # earlier live TI2L with a write in its journal blocks a new one in the same set, files left as they were
        # same run file as the moved aside test below, only the journal entry is different
        _write_attempt(self.earlier, NO_WRITE_RUN, [TIMESHEET_MOVE])
        files_before = _contents(self.earlier)
        with self.assertRaises(RunRefused) as caught:
            self._plan(SET_NAME)
        self.assertEqual(str(caught.exception), REFUSAL.format(path=(self.earlier / "1.jsonl").resolve()))
        self.assertEqual(sorted(path.name for path in self.earlier.iterdir()), ATTEMPT_FILES)
        self.assertEqual(_contents(self.earlier), files_before)

    def test_journal_entry_blocks_new_set(self):
        # once-only rule looks across every run set so a new set name gets refused too and never created
        _write_attempt(self.earlier, NO_WRITE_RUN, [TIMESHEET_MOVE])
        files_before = _contents(self.earlier)
        with self.assertRaises(RunRefused) as caught:
            self._plan(NEW_SET_NAME)
        self.assertEqual(str(caught.exception), REFUSAL.format(path=(self.earlier / "1.jsonl").resolve()))
        self.assertFalse((self.runs_dir / NEW_SET_NAME).exists())
        self.assertEqual(_contents(self.earlier), files_before)

    def test_killed_mid_pass_blocks(self):
        # run file with no result cant prove nothing was sent, so even an empty journal doesnt let a rerun start
        _write_attempt(self.earlier, KILLED_RUN, [])
        files_before = _contents(self.earlier)
        with self.assertRaises(RunRefused) as caught:
            self._plan(SET_NAME)
        self.assertEqual(str(caught.exception), REFUSAL.format(path=(self.earlier / "1.jsonl").resolve()))
        self.assertEqual(sorted(path.name for path in self.earlier.iterdir()), ATTEMPT_FILES)
        self.assertEqual(_contents(self.earlier), files_before)

    def test_no_write_attempt_moved_aside(self):
        # earlier attempt that stopped before any write with an empty journal moves to attempt-<time>/ and the new run goes ahead
        _write_attempt(self.earlier, NO_WRITE_RUN, [])
        files_before = _contents(self.earlier)
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            planned = self._plan(SET_NAME)
        self.assertEqual(planned, 1)  # a live write task runs once
        left = list(self.earlier.iterdir())
        self.assertEqual(len(left), 1)
        attempt_folder = left[0]
        self.assertTrue(attempt_folder.is_dir())
        self.assertIsNotNone(ATTEMPT_FOLDER.fullmatch(attempt_folder.name), msg=attempt_folder.name)
        self.assertEqual(_contents(attempt_folder), files_before)
        self.assertEqual(printed.getvalue(), MOVED_NOTE.format(dest=attempt_folder))


if __name__ == "__main__":
    unittest.main()
