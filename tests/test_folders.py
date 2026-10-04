# STRIDE T4 - a name two live folders share is never a filing destination
# another team adds ' hr' next to our 'HR': folder_named finds nothing, tidy moves nothing into either one, preflight flags the clash before a live run
import unittest

from agent.safe_reads import folder_named
from agent.skills import triage
from harness import fixtures, preflight
from harness.fake_server import FOREIGN_USER
from helpers import FIXTURE_DIR, build_runtime, fake_server

INCOMING_FOLDER_ID = "6f8a3ed1-f2df-46a7-8dcb-275e9494c799"  # Incoming
HR_FOLDER_ID = "13c03c65-ddae-4d61-9e2f-b9167168277f"  # HR

# Incoming originals each have a 880 byte copy with the same name, hence the sizes
TIMESHEET_ID = "1ee27946-7064-42e1-afce-376068a545bf"  # timesheet_week33.xlsx (42,115 bytes)
KNOB_ID = "b45cecdd-9f14-491a-a0ee-2826d3fabb15"  # J-KNOB-09_RevA.dxf (61,208 bytes)
MILL_CERT_ID = "680e8af6-15f3-49c6-b70b-987316fa5775"  # Cert_MillCert_SS304_Heat90114.pdf (149,770 bytes)
W9_ID = "81857de6-e6e9-41c5-9da8-67cb5d1903c1"  # W9_JMillerWelding_2026.pdf (96,331 bytes)
PO_ID = "732439a0-7f36-4d31-ac3b-f406c41c00bd"  # PO_4471_ApexMetals_signed.pdf (218,044 bytes)

# other teams folder, only differs from 'HR' by case and a leading space
HR2_ID = "eeeeeeee-0000-4000-8000-00000000a77c"  # made up
HR2_NAME = " hr"
HR2_CREATED = "2026-10-01T09:00:00"  # newer than all fixture folders so server lists it first


def _add_hr_clone(server):
    # another team makes a live ' hr' folder on the fake server, same shape as the real HR one
    real_hr = server.tables["DriveFolder"][HR_FOLDER_ID]
    server.tables["DriveFolder"][HR2_ID] = dict(
        real_hr, id=HR2_ID, name=HR2_NAME, created_by=FOREIGN_USER,
        created_at=HR2_CREATED, updated_by=FOREIGN_USER, updated_at=HR2_CREATED)


def _updated_ids(server):
    return [write["id"] for write in server.write_log if write["tool"] == "FileAttachment.update"]


def _plan_entry(result, file_id):
    return next(entry for entry in result["plan"] if entry["id"] == file_id)


class SharedFolderNameTests(unittest.TestCase):

    def test_shared_name_no_folder(self):
        # 'HR' and ' hr' both live -> asking for HR finds nothing, not just the first listed
        folders = {
            "a": {"id": "a", "name": "HR", "is_archived": 0},
            "b": {"id": "b", "name": HR2_NAME, "is_archived": 0},
        }

        folder = folder_named(folders, "HR")
        self.assertIsNone(folder)

    def test_nothing_moved_into_hr(self):
        # with a 2nd ' hr' the timesheet has no destination, stays in Incoming and gets escalated
        server = fake_server()
        _add_hr_clone(server)
        rt, _ = build_runtime("apply", server=server)
        result = triage.run(rt.ctx, {})
        timesheet = _plan_entry(result, TIMESHEET_ID)
        self.assertEqual((timesheet["action"], timesheet["to_folder"]), ("escalate", None))
        self.assertEqual(timesheet["missing"], ["document type", "which folder it belongs in"])
        self.assertCountEqual(_updated_ids(server), [MILL_CERT_ID, KNOB_ID, W9_ID, PO_ID])
        self.assertEqual(server.tables["FileAttachment"][TIMESHEET_ID]["folder_id"], INCOMING_FOLDER_ID)
        in_hr = [f["id"] for f in server.tables["FileAttachment"].values() if f["folder_id"] in (HR_FOLDER_ID,HR2_ID)]
        self.assertEqual(in_hr, [])


class FolderPreflightTests(unittest.TestCase):

    def test_preflight_two_hr_folders(self):
        # preflight names the new folder + says 2 folders are named 'hr', so live run gets refused
        server = fake_server()
        _add_hr_clone(server)
        rt, _ = build_runtime("plan", server=server)
        problems, _warnings = preflight.assess(rt, fixtures.load("keystone", FIXTURE_DIR))
        self.assertEqual(problems, [
            f"folder 'hr' ({HR2_ID}) is not in the fixture (by {FOREIGN_USER} at {HR2_CREATED})",
            "2 folders are named 'hr'",
        ])


if __name__ == "__main__":
    unittest.main()
