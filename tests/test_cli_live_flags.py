# STRIDE S3 - --live-apply never runs or restores quietly on the fake server
# each test runs the real operator command offline thru run_cli with AS_ALLOW_WRITES=1 set too, so only --target live is missing
import tempfile
import unittest
from pathlib import Path
from agent import snapshot
from agent.config import KEYSTONE_INCOMING_ALLOWLIST
from helpers import REPO_ROOT, build_runtime, new_set_name, offline_env, remove_run_set, run_cli

REFUSED = 3  # exit code for any harness refusal
RUN_REFUSAL = "refused: --live-apply writes to the live platform, so it needs --target live"
RESTORE_REFUSAL = "refused: --live-apply restores the live platform, so it needs --target live"
CLI_TRACE_DIR = REPO_ROOT / "runs" / "cli"  # harness restore puts its trace here


def _old_live_snapshot(folder):
    # undo files of a live TI2L run that wrote nothing - snapshot-1.json + empty writes-1.json
    # the 9 originals come from a fake server since we're offline. no snapshot-1.meta.json (like a pre S3 snapshot) so only the --live-apply check stops a fake replay
    rt, _ = build_runtime("plan")
    snap_path = folder / "snapshot-1.json"
    snapshot.save(snapshot.take(rt.admin_mcp, KEYSTONE_INCOMING_ALLOWLIST), snap_path)
    snapshot.save([], snapshot.writes_path(snap_path))
    return snap_path


def _contents(folder):
    return {path.name: path.read_bytes() for path in folder.iterdir() if path.is_file()}


def _traces():
    return set(CLI_TRACE_DIR.glob("*-restore.jsonl"))


def _cleanup_traces(before, folder_existed):
    # only matters if the refusal breaks, restore would leave its trace (and runs/cli) behind
    for path in _traces() - before:
        path.unlink(missing_ok=True)
    if not folder_existed and CLI_TRACE_DIR.is_dir() and not any(CLI_TRACE_DIR.iterdir()):
        CLI_TRACE_DIR.rmdir()


class LiveApplyFlagTests(unittest.TestCase):

    def setUp(self):
        # write switch on too so only --target live is missing
        self.env = offline_env(AS_ALLOW_WRITES="1")

    def test_run_live_apply_needs_target(self):
        # `harness run TI2L --live-apply` without --target live exits 3, no run set written
        set_name = new_set_name("s3-run")
        self.addCleanup(remove_run_set, set_name)
        result = run_cli("harness", "run", "TI2L", "--model", "scripted", "--live-apply", "--set", set_name, env=self.env)
        self.assertEqual(result.returncode, REFUSED, msg=result.stdout + result.stderr)
        self.assertEqual(result.stderr.strip(), RUN_REFUSAL)
        self.assertEqual(result.stdout, "")
        self.assertFalse((REPO_ROOT / "runs" / set_name).exists())

    def test_restore_live_apply_needs_target(self):
        # `harness restore <snapshot> --live-apply` without --target live exits 3, restores nothing, no trace
        folder = Path(self.enterContext(tempfile.TemporaryDirectory()))
        snap_path = _old_live_snapshot(folder)
        undo_files_before = _contents(folder)
        traces_before = _traces()
        self.addCleanup(_cleanup_traces, traces_before, CLI_TRACE_DIR.exists())
        result = run_cli("harness", "restore", str(snap_path), "--live-apply", env=self.env)
        self.assertEqual(result.returncode, REFUSED, msg=result.stdout + result.stderr)
        self.assertEqual(result.stderr.strip(), RESTORE_REFUSAL)
        self.assertEqual(result.stdout, "")  # no report printed
        self.assertEqual(_traces(), traces_before)
        self.assertEqual(_contents(folder), undo_files_before)


if __name__ == "__main__":
    unittest.main()
