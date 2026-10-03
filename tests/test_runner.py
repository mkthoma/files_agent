# harness tests: task loading + runner + preflight + scoring + calibration
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from agent.runtime import WritesNotAllowed
from agent.trace import read_trace
from harness import fixtures, preflight
from harness.calibrate import calibrate
from harness.runner import RunRefused, planned_runs, run_once, run_task
from harness.score import expect_runs, rescore, score_set, write_score
from harness.tasks import load_all

from helpers import FIXTURE_DIR, REPO_ROOT, build_runtime, fake_server, new_set_name, remove_run_set, run_cli

QUALITY_FOLDER_ID = "585da032-09fe-43cd-9440-c6f01824f5fc"  # Quality

# 9 bare copies (880 bytes) the platform added to Incoming on 23 Sept, none of them on the allow-list
TIMESHEET_COPY_ID = "6477085f-2a2a-4da8-9009-a86af39e69a0"  # timesheet_week33.xlsx (880 bytes)
COPY_IDS = (
    "20d633ba-251f-494a-974d-e83d5e9d0695",  # W9_JMillerWelding_2026.pdf (880 bytes)
    "30f72e5c-e340-4c9c-9495-06df2f0aa4f6",  # Untitled.pdf (880 bytes)
    "3dd05bfb-f423-44bb-ad0f-fc94acca3ced",  # PO_4471_ApexMetals_signed.pdf (880 bytes)
    TIMESHEET_COPY_ID,
    "782cdca0-b02d-4735-936b-a75cfac15892",  # Cert_MillCert_SS304_Heat90114.pdf (880 bytes)
    "9af1955d-753e-4c7a-b8f9-6e885ca3057e",  # IMG_20260814_093214.jpg (880 bytes)
    "9b27de51-e04a-404c-b737-3d0133580b39",  # J-KNOB-09_RevA.dxf (880 bytes)
    "c0c8b9c0-85c2-4528-b574-1f35665616b6",  # PO_4471_ApexMetals_signed (1).pdf (880 bytes)
    "f6f748ab-6a24-4c76-ac54-39b24cf3bc9b",  # scan0042.pdf (880 bytes)
)

# fake server makes extra file ids from the filename so this one stays same
NEW_TIMESHEET_ID = "5500a822-b3e7-5277-9cce-5f889fc0f4c3"  # timesheet_week33 (1).xlsx (extra file)

OUT_OF_SCOPE_WARNING = "is in Incoming but outside the write allow-list: it will not be written or escalated"
LOOKALIKE_PROBLEM = "is new or changed since the fixture and is related to an allow-listed file (name, hash or document kind)"
MISSING_RUN_FILE = "missing: no run file was written (the run crashed)"

LIVE_WRITE_TASK = """\
id = "{task_id}"
question = "q"
mode = "apply"
live_write = true
live_allowlist = true
"""


def _preflight(rt):
    # (problems, warnings) against the pinned 26 Sept fixture
    return preflight.assess(rt, fixtures.load("keystone", FIXTURE_DIR))


def _run_d1_once(set_dir):
    # runner has no settings arg and would read local .env, so give it an empty one. no network or real model
    with mock.patch("agent.config.load_env", return_value={}):
        return run_task(load_all()["D1"], target="fake", model_kind="scripted", set_dir=set_dir, repeat=1, fixture_dir=FIXTURE_DIR)


def _crash_mid_run(*args, **kwargs):
    raise RuntimeError("boom mid-run")


class TaskLoaderTests(unittest.TestCase):  # HARNESS-1

    def test_two_live_write_tasks_refused(self):
        # 2 live_write tasks in one folder -> load fails and error names both
        folder = Path(self.enterContext(tempfile.TemporaryDirectory()))
        for task_id in ("A", "B"):
            (folder / f"{task_id}.toml").write_text(LIVE_WRITE_TASK.format(task_id=task_id), encoding="utf-8")

        with self.assertRaises(ValueError) as caught:
            load_all(folder)

        self.assertEqual(str(caught.exception), "only one task may set live_write = true (one live write run is planned), found ['A', 'B']")

    def test_only_ti2l_live_write(self):
        # in the real task folder only TI2L is live_write, and it has live_allowlist
        tasks = load_all()

        live_write_ids = [task.id for task in tasks.values() if task.live_write]

        self.assertEqual(live_write_ids, ["TI2L"])
        self.assertTrue(tasks["TI2L"].live_allowlist)


class PlannedRunsTests(unittest.TestCase):  # HARNESS-2

    def setUp(self):
        self.tasks = load_all()
        # write switch only comes from the shell, patch.dict puts env back after
        self.enterContext(mock.patch.dict(os.environ))
        os.environ.pop("AS_ALLOW_WRITES", None)

    def test_live_misuse_refused(self):
        # D4, TI2, TI2L refused on live. TI2L with live_apply still needs AS_ALLOW_WRITES
        with self.assertRaises(RunRefused):
            planned_runs(self.tasks["D4"], target="live")  # needs fake server faults
        with self.assertRaises(RunRefused):
            planned_runs(self.tasks["TI2"], target="live", live_apply=True)  # writes but its not live_write
        with self.assertRaises(RunRefused):
            planned_runs(self.tasks["TI2L"], target="live")
        with self.assertRaises(WritesNotAllowed) as caught:
            planned_runs(self.tasks["TI2L"], target="live", live_apply=True)
        self.assertIs(type(caught.exception), WritesNotAllowed)  # needs this exact class, not a subclass

    def test_planned_run_counts(self):
        # D1 live = 5 runs, D1 fake repeat 2 = 2, TI2L = 1 once writes are on
        self.assertEqual(planned_runs(self.tasks["D1"], target="live"), 5)
        self.assertEqual(planned_runs(self.tasks["D1"], target="fake", repeat=2), 2)

        os.environ["AS_ALLOW_WRITES"] = "1"

        self.assertEqual(planned_runs(self.tasks["TI2L"], target="live", live_apply=True), 1)


class PreflightTests(unittest.TestCase):

    def test_clean_data_warnings(self):
        # HARNESS-3 unchanged 26 Sept data, no problems and exactly 9 warnings (1 per copy)
        rt, _ = build_runtime("plan")

        problems, warnings = _preflight(rt)

        self.assertEqual(problems, [])
        self.assertEqual(len(warnings), 9)
        for copy_id in COPY_IDS:
            with self.subTest(copy_id=copy_id):
                warning_end = f"({copy_id}) {OUT_OF_SCOPE_WARNING}"
                naming_this_copy = [warning for warning in warnings if warning.endswith(warning_end)]
                self.assertEqual(len(naming_this_copy), 1)

    def test_new_lookalike_blocks(self):
        # HARNESS-4 new 'timesheet_week33 (1).xlsx' in Quality has same name as an allow-listed file
        rt, _ = build_runtime("plan", extra_files=[{"filename": "timesheet_week33 (1).xlsx", "folder": "Quality"}])

        problems, _ = _preflight(rt)

        self.assertIn(f"timesheet_week33 (1).xlsx ({NEW_TIMESHEET_ID}) {LOOKALIKE_PROBLEM}", problems)

    def test_copy_left_incoming_blocks(self):
        # HARNESS-4 timesheet copy moved to Quality = 2 problems, it left Incoming and it changed
        server = fake_server()
        server.tables["FileAttachment"][TIMESHEET_COPY_ID]["folder_id"] = QUALITY_FOLDER_ID
        rt, _ = build_runtime("plan", server=server)

        problems, _ = _preflight(rt)

        self.assertIn(f"timesheet_week33.xlsx ({TIMESHEET_COPY_ID}) has left Incoming since the fixture", problems)
        self.assertIn(f"timesheet_week33.xlsx ({TIMESHEET_COPY_ID}) {LOOKALIKE_PROBLEM}", problems)


class RunFileTests(unittest.TestCase):

    def setUp(self):
        # run_once reads settings itself so keep local .env out
        self.enterContext(mock.patch("agent.config.load_env", return_value={}))
        self.set_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.d1 = load_all()["D1"]

    def test_failed_setup_run_file(self):
        # HARNESS-5 fixture folder doesnt exist but D1/1.jsonl still gets written and scored as fail
        path = run_once(self.d1, 1, target="fake", model_kind="scripted", set_dir=self.set_dir, fixture_dir=self.set_dir / "no-such-fixture")
        d1_score = score_set(self.set_dir)["tasks"]["D1"]

        self.assertEqual(path, self.set_dir / "D1" / "1.jsonl")
        self.assertTrue(path.exists())
        events = read_trace(path)
        self.assertEqual(events[0]["kind"], "manifest")
        self.assertTrue(events[0]["setup_failed"])
        self.assertEqual(events[-1]["kind"], "result")
        self.assertTrue(events[-1]["error"].startswith("set-up failed: FileNotFoundError"), msg=events[-1]["error"])
        self.assertFalse(d1_score["pass_all"])
        first_failure = d1_score["failures"]["1.jsonl"][0]
        self.assertTrue(first_failure.startswith("completed: set-up failed: FileNotFoundError"), msg=first_failure)

    def test_crash_mid_run_file(self):
        # HARNESS-8 agent crashes mid run, run file still finished and D1 scored as fail
        with mock.patch("harness.runner.run_agent", _crash_mid_run):
            path = run_once(self.d1, 1, target="fake", model_kind="scripted", set_dir=self.set_dir, fixture_dir=FIXTURE_DIR)
        d1_score = score_set(self.set_dir)["tasks"]["D1"]

        events = read_trace(path)
        result = events[-1]
        self.assertEqual(events[0]["kind"], "manifest")
        self.assertNotIn("setup_failed", events[0])
        self.assertIn("run_error", [event["kind"] for event in events])
        self.assertEqual(result["kind"], "result")
        self.assertEqual(result["error"], "RuntimeError: boom mid-run")
        self.assertEqual(result["passes"], [])
        self.assertNotEqual(result["state_after"]["files"], {})
        self.assertFalse(d1_score["pass_all"])
        self.assertIn("completed: RuntimeError: boom mid-run", d1_score["failures"]["1.jsonl"])


class ScoringTests(unittest.TestCase):

    def setUp(self):
        self.set_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        _run_d1_once(self.set_dir)

    def test_missing_run_file(self):
        # HARNESS-6 2nd D1 run expected but never written -> D1 fails and rescore doesnt match anymore
        first = score_set(self.set_dir)
        write_score(self.set_dir, first)
        first_rescore_matches, _ = rescore(self.set_dir)

        expect_runs(self.set_dir, "D1", 2)
        second = score_set(self.set_dir)
        second_rescore_matches, _ = rescore(self.set_dir)

        self.assertEqual(first["tasks"]["D1"]["runs"], 1)
        self.assertEqual(first["tasks"]["D1"]["passed"], 1)
        self.assertTrue(first_rescore_matches)
        self.assertEqual(second["tasks"]["D1"]["failures"], {"2.jsonl": [MISSING_RUN_FILE]})
        self.assertFalse(second["tasks"]["D1"]["pass_all"])
        self.assertFalse(second_rescore_matches)

    def test_half_written_run_file(self):
        # HARNESS-9 (STRIDE D3 fix) run file cut mid line = one failed run, scorer shouldnt crash
        run_file = self.set_dir / "D1" / "1.jsonl"
        run_file.write_bytes(run_file.read_bytes()[:-500])

        try:
            score = score_set(self.set_dir)
        except json.JSONDecodeError as err:
            self.fail(f"score_set crashed on the half-written run file: {err}")

        d1_score = score["tasks"]["D1"]
        self.assertEqual(d1_score["runs"], 1)
        self.assertEqual(d1_score["passed"], 0)
        self.assertFalse(d1_score["pass_all"])
        self.assertEqual(list(d1_score["failures"]), ["1.jsonl"])
        run_failures = d1_score["failures"]["1.jsonl"]
        self.assertEqual(len(run_failures), 1)
        # exact wording is up to the fix, just check it says could not be read
        self.assertIn("could not be read", run_failures[0])


class ScoreCommandTests(unittest.TestCase):  # HARNESS-9

    def setUp(self):
        self.set_name = new_set_name("harness9")
        self.addCleanup(remove_run_set, self.set_name)
        # setup problems show up as errors here, so the fail below can only come from scoring
        run = run_cli("harness", "run", "D1", "TI2", "--target", "fake", "--model", "scripted", "--repeat", "1", "--set", self.set_name)
        self.assertEqual(run.returncode, 0, msg=run.stdout + run.stderr)
        run_file = REPO_ROOT / "runs" / self.set_name / "TI2" / "1.jsonl"
        run_file.write_bytes(run_file.read_bytes()[:-500])

    def test_score_cmds_half_written_file(self):
        # STRIDE D3 fix - TI2/1.jsonl cut off, harness score shows TI2 failed and rescore still matches
        score_command = run_cli("harness", "score", f"runs/{self.set_name}")
        rescore_command = run_cli("harness", "rescore", f"runs/{self.set_name}")

        self.assertEqual(score_command.returncode, 0, msg=score_command.stderr)
        self.assertIn("| D1 | 1 | 1 | PASS | 0.0000 |", score_command.stdout)
        self.assertIn("| TI2 | 1 | 0 | FAIL | 0.0000 |", score_command.stdout)
        self.assertIn("- TI2/1.jsonl: ", score_command.stdout)
        self.assertIn("rescore IDENTICAL to score.json", rescore_command.stdout)


class CalibrationTests(unittest.TestCase):  # HARNESS-7

    def test_calibration_catches_all(self):
        # real D1 run, every mutant gets caught incl sneaky_write, trespass and liar
        set_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        _run_d1_once(set_dir)

        rows = calibrate(set_dir)

        missed = [row["mutant"] for row in rows if not row["caught"]]
        self.assertEqual(missed, [])
        mutants = [row["mutant"] for row in rows]
        for name in ("sneaky_write", "trespass", "liar", "invented_id"):
            self.assertIn(name, mutants)
        # 18 = expect keys in D1.toml, change both together
        # R4 fix added refused_delete, refused_trespass and uncertain_write for D1
        self.assertEqual(len(rows), 18)


if __name__ == "__main__":
    unittest.main()