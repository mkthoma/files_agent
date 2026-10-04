# undo after a tidy - full restore, and a restore that carries on past a failing row
import unittest
from agent.mcp_client import McpError
from agent.redact import Redactor
from agent.skills import triage
from agent.snapshot import diff, restore, take
from agent.trace import Trace
from helpers import build_runtime

# Incoming originals have 880 byte copies with the same names, so sizes are in the comments
TIMESHEET_ID = "1ee27946-7064-42e1-afce-376068a545bf"  # timesheet_week33.xlsx (42,115 bytes)
KNOB_ID = "b45cecdd-9f14-491a-a0ee-2826d3fabb15"  # J-KNOB-09_RevA.dxf (61,208 bytes)
MILL_CERT_ID = "680e8af6-15f3-49c6-b70b-987316fa5775"  # Cert_MillCert_SS304_Heat90114.pdf (149,770 bytes)
W9_ID = "81857de6-e6e9-41c5-9da8-67cb5d1903c1"  # W9_JMillerWelding_2026.pdf (96,331 bytes)
PO_ID = "732439a0-7f36-4d31-ac3b-f406c41c00bd"  # PO_4471_ApexMetals_signed.pdf (218,044 bytes)

# 5 files the tidy moves, in id order (same order restore reports)
MOVED_IDS = [TIMESHEET_ID, MILL_CERT_ID, PO_ID, W9_ID, KNOB_ID]
ALLOWLIST_SIZE = 18  # every file in Incoming
INJECTED_FAILURE = "Injected failure"


class FailOneClient:
    # fake mcp client, passes every call to the real one except an update of one file which fails

    def __init__(self, real_client, failing_id):
        self.real_client = real_client
        self.failing_id = failing_id

    def call(self, tool, args):
        if tool == "FileAttachment.update" and args.get("id") == self.failing_id:
            raise McpError(INJECTED_FAILURE)
        return self.real_client.call(tool, args)


def _snapshot_and_tidy():
    # apply runtime, snapshot the allowlist, tidy Incoming -> (rt, snapshot)
    rt, _ = build_runtime("apply")
    snapshot = take(rt.admin_mcp, rt.guard.allowlist)
    triage.run(rt.ctx, {})
    return rt, snapshot


class TidyThenRestoreTests(unittest.TestCase):

    def test_full_restore(self):
        # RESTORE-3 all 5 moved files put back, new snapshot matches the first one
        rt, snapshot = _snapshot_and_tidy()
        allowlist = rt.guard.allowlist
        self.assertEqual(len(allowlist), ALLOWLIST_SIZE)
        self.assertEqual(sorted(diff(snapshot, take(rt.admin_mcp, allowlist))), MOVED_IDS)
        report = restore(rt.admin_mcp, snapshot, rt.trace, allowlist=allowlist, writes=rt.guard.writes, me=rt.session.me()["id"])
        self.assertEqual(report["restored"], MOVED_IDS)
        self.assertEqual(report["failed"], {})
        self.assertEqual(report["remaining"], {})
        self.assertEqual(report["conflicts_left_alone"], {})
        self.assertEqual(diff(snapshot, take(rt.admin_mcp, allowlist)), {})

    def test_restore_past_failure(self):
        # RESTORE-4 timesheet restore fails, the other 4 still go back and the failure is reported
        rt, snapshot = _snapshot_and_tidy()
        client = FailOneClient(rt.admin_mcp, TIMESHEET_ID)
        trace = Trace(None, Redactor())
        with self.assertRaises(RuntimeError) as incomplete:
            restore(client, snapshot, trace, allowlist=rt.guard.allowlist,
                    writes=rt.guard.writes, me=rt.session.me()["id"])
        message = str(incomplete.exception)
        self.assertTrue(message.startswith(f"restore incomplete for ['{TIMESHEET_ID}']"), msg=message)
        restore_events = trace.of_kind("restore")
        self.assertEqual(len(restore_events), 1)
        self.assertEqual(restore_events[0]["failed"], {TIMESHEET_ID: INJECTED_FAILURE})
        self.assertEqual(restore_events[0]["restored"], [MILL_CERT_ID, PO_ID, W9_ID, KNOB_ID])
        still_different = diff(snapshot, take(rt.admin_mcp, rt.guard.allowlist))
        self.assertEqual(list(still_different), [TIMESHEET_ID])


if __name__ == "__main__":
    unittest.main()
