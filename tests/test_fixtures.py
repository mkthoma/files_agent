# STRIDE T8 - the fixture baseline preflight trusts
# a hand edited or planted fixture must never become the 'unchanged' baseline. load() checks fixture.json against the manifest hashes, only YYYY-MM-DD folders (not future ones) count as captures, and live preflight refuses a fixture older than 24h
# every edited/planted fixture here is a copy in a temp folder, the committed one is only read
import contextlib
import dataclasses
import io
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock
from harness import fixtures, preflight
from helpers import FIXTURE_DIR, build_runtime

W9_ID = "81857de6-e6e9-41c5-9da8-67cb5d1903c1"  # W9_JMillerWelding_2026.pdf, one of the 9 allowlisted originals
EDITED_AT = "2026-10-02T00:00:00"  # someone hand editing would copy this in from a change they saw live
FAKE_TOOL_HASH = "0b9c265bbab700ab"  # matches no fixtures tools
CAPTURE_NAME = "2026-09-26"  # committed capture folder
FIXTURE_HASH = "df2a585221ef9f25"  # from the 26 Sept manifest.json
FUTURE_NAME = "2027-01-01"  # months after TODAY
BAD_NAMES = ("2026-09-26-fix", "20260925", "latest")  # sort after CAPTURE_NAME but arent YYYY-MM-DD

TODAY = datetime(2026, 9, 27, 12, 0, tzinfo=timezone.utc)  # "now" for the folder tests
CAPTURED_AT = datetime(2026, 9, 26, 5, 18, 37, tzinfo=timezone.utc)  # captured_at in the 26 Sept manifest.json
STALE_NOW = CAPTURED_AT + timedelta(hours=25)  # 1h past the 24h limit
FRESH_NOW = CAPTURED_AT + timedelta(hours=23)  # 1h inside
AGE_PROBLEM = "the fixture was captured at 2026-09-26T05:18:37+00:00, not within the last 24 hours: re-capture fixtures right before the live run"


def _clock_at(moment):
    # datetime class whose now() is always `moment`, to patch into the module under test

    class FrozenClock(datetime):

        @classmethod
        def now(cls, tz=None):
            return moment.astimezone(tz) if tz else moment.replace(tzinfo=None)

    return FrozenClock


def _tmp(test):
    folder = tempfile.TemporaryDirectory()
    test.addCleanup(folder.cleanup)
    return Path(folder.name)


def _copy_capture(root, name):
    # copy of the committed 26 Sept fixture as root/keystone/<name>
    return Path(shutil.copytree(FIXTURE_DIR, root / "keystone" / name))


def _rewrite_json(path, change):
    data = json.loads(path.read_text(encoding="utf-8"))
    path.write_text(json.dumps(change(data), indent=1,ensure_ascii=False, sort_keys=True), encoding="utf-8")


def _edit_w9(fixture, value):
    # copy of the fixture data with only the W-9 updated_at changed
    files = [{**row, "updated_at": value} if row["id"] == W9_ID else row for row in fixture["tables"]["FileAttachment"]]
    return {**fixture, "tables": {**fixture["tables"], "FileAttachment": files}}


def _refusal(folder, wrong):
    # what load() says when the recomputed hashes dont match the manifest
    return (f"{folder}: fixture.json does not match manifest.json ({wrong}); a hand-edited or half-written "
            "fixture is never used. Re-capture: python -m harness capture keystone")


class FixtureManifestCheckTests(unittest.TestCase):

    def test_untouched_copy_loads(self):
        # unedited copy loads fine, so the refusals below come from the edit alone
        folder = _copy_capture(_tmp(self), CAPTURE_NAME)
        data = fixtures.load("keystone", folder)
        self.assertEqual(data["_dir"], str(folder))
        self.assertEqual(data["_manifest"]["fixture_hash"], FIXTURE_HASH)

    def test_edited_row_refused(self):
        # W-9 updated_at edited in fixture.json with the old manifest.json kept -> refused on load
        folder = _copy_capture(_tmp(self), CAPTURE_NAME)
        _rewrite_json(folder / "fixture.json", lambda data: _edit_w9(data, EDITED_AT))
        with self.assertRaises(ValueError) as refused:
            fixtures.load("keystone", folder)
        self.assertEqual(str(refused.exception), _refusal(folder, "fixture_hash"))

    def test_planted_tool_hash_refused(self):
        # only the manifest tool_hash edited -> refused, load() recomputes it from the tools
        folder = _copy_capture(_tmp(self), CAPTURE_NAME)
        _rewrite_json(folder / "manifest.json", lambda manifest: {**manifest, "tool_hash": FAKE_TOOL_HASH})
        with self.assertRaises(ValueError) as refused:
            fixtures.load("keystone", folder)
        self.assertEqual(str(refused.exception), _refusal(folder, "tool_hash"))


class BaselineFolderChoiceTests(unittest.TestCase):

    def test_non_date_folder_ignored(self):
        # full copy in a folder that sorts later but isnt YYYY-MM-DD gets passed over
        for name in BAD_NAMES:
            with self.subTest(folder=name):
                root = _tmp(self)
                _copy_capture(root, CAPTURE_NAME)
                _copy_capture(root, name)
                with mock.patch("harness.fixtures.datetime", _clock_at(TODAY)):
                    chosen = fixtures.latest_dir("keystone", root)
                self.assertEqual(chosen.name, CAPTURE_NAME)

    def test_future_folder_skipped(self):
        # valid copy in a future dated folder is skipped and the skip gets printed, not silent
        root = _tmp(self)
        _copy_capture(root, CAPTURE_NAME)
        _copy_capture(root, FUTURE_NAME)
        stderr = io.StringIO()
        with mock.patch("harness.fixtures.datetime", _clock_at(TODAY)), contextlib.redirect_stderr(stderr):
            chosen = fixtures.latest_dir("keystone", root)
        self.assertEqual(chosen.name, CAPTURE_NAME)
        self.assertEqual(stderr.getvalue(), f"warning: skipped fixture folder(s) dated in the future: {FUTURE_NAME}; using {CAPTURE_NAME}\n")


class LiveFixtureAgeTests(unittest.TestCase):

    def setUp(self):
        rt, _ = build_runtime("plan")
        # preflight judged like the live run would, fake server still stands in for the platform
        self.live_rt = dataclasses.replace(rt, target="live")
        self.fixture = fixtures.load("keystone", FIXTURE_DIR)

    def test_stale_fixture_refused(self):
        # 25h after capture the fixture age is the only live preflight problem
        with mock.patch("harness.preflight.datetime", _clock_at(STALE_NOW)):
            problems, _ = preflight.assess(self.live_rt, self.fixture)
        self.assertEqual(problems, [AGE_PROBLEM])

    def test_fresh_fixture_ok(self):
        # 23h after the same capture, no problems
        with mock.patch("harness.preflight.datetime", _clock_at(FRESH_NOW)):
            problems, _ = preflight.assess(self.live_rt, self.fixture)
        self.assertEqual(problems, [])


if __name__ == "__main__":
    unittest.main()
