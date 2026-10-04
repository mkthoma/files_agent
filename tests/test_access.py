# out of seat requests and requests to read a files contents
import unittest
from agent.skills.access import detect_app, explain_access, file_contents
from helpers import build_runtime

# Incoming originals each have a 880 byte copy with the same name, sizes to tell them apart
SCAN_ID = "b1d3894c-12e9-4ee1-b1da-82c7191ed4a0"  # scan0042.pdf (511,903 bytes)
SCAN_COPY_ID = "f6f748ab-6a24-4c76-ac54-39b24cf3bc9b"  # scan0042.pdf (880 bytes)

SEAT_APPS = ["agent", "crm", "drive"]  # apps this seat can use


def _records(rt, action):
    return [r for r in rt.ctx.records.all() if r.action == action]


class OutOfSeatTests(unittest.TestCase):  # ACCESS-1

    def test_payroll_refused(self):
        # payslip request refused as payroll, names the apps the seat does have
        rt, _ = build_runtime("plan")
        result = explain_access(rt.ctx, {"request": "Show me this month's payslips."})
        self.assertFalse(result["allowed"], msg=result["answer_text"])
        self.assertEqual(result["app"], "payroll")
        self.assertEqual(result["allowed_apps"], SEAT_APPS)
        self.assertIn("can't help", result["answer_text"])
        self.assertIn("payroll", result["answer_text"])
        refusals = _records(rt, "refuse_out_of_seat")
        self.assertEqual(len(refusals), 1)
        self.assertEqual(refusals[0].status, "refused")

    def test_drive_allowed(self):
        rt, _ = build_runtime("plan")
        result = explain_access(rt.ctx, {"request": "List the files", "app": "drive"})
        self.assertTrue(result["allowed"], msg=result["answer_text"])

    def test_design_word_not_an_app(self):
        # 'the design of the bracket' isnt an app, 'design files' means designreview
        self.assertIsNone(detect_app("the design of the bracket"))
        self.assertEqual(detect_app("Show me the design files for J-BRKT-04."), "designreview")


class FileContentsTests(unittest.TestCase):  # ACCESS-5

    def setUp(self):
        self.rt, _ = build_runtime("plan")

    def test_shared_name_refused(self):
        # asking what scan0042.pdf says -> both files with that name refused, nothing quoted
        answer = file_contents(self.rt.ctx, {"file": "scan0042.pdf"})["answer_text"]
        self.assertTrue(answer.startswith("2 files are named scan0042.pdf; none can be read."), msg=answer)
        refusals = _records(self.rt, "refuse_read_contents")
        self.assertCountEqual([record.target_id for record in refusals], [SCAN_ID, SCAN_COPY_ID])
        self.assertEqual([record.status for record in refusals], ["refused","refused"])
        per_file_lines = answer.splitlines()[1:]
        self.assertEqual(len(per_file_lines), 2)
        for line in per_file_lines:
            self.assertIn("stores no file contents", line)

    def test_unknown_name_no_guess(self):
        # no file named exactly 'timesheet' -> refused, no guess
        result = file_contents(self.rt.ctx, {"file": "timesheet"})
        self.assertEqual(result["answer_text"], "No file is named exactly 'timesheet'. I did not guess.")


if __name__ == "__main__":
    unittest.main()
