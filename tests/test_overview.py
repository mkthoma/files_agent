# drive overview count test
import unittest

from agent.skills import overview

from helpers import build_runtime


class DriveOverviewTests(unittest.TestCase):  # OVERVIEW-1

    def test_count_contradiction(self):
        # overview says 15 but folders hold 30 (of 113 rows) so should report a contradiction
        rt, _ = build_runtime("plan")

        result = overview.run(rt.ctx, {})

        self.assertEqual(result["overview_total"], 15)
        self.assertEqual(result["records_total"], 113)
        self.assertEqual(result["in_folders"], 30)
        self.assertTrue(result["contradiction"])
        self.assertIn("report 15, because they only count files marked entity_type 'Drive' (15 here)", result["answer_text"])
        contradiction_statuses = [r.status for r in rt.ctx.records.all() if r.action == "contradiction"]
        self.assertEqual(contradiction_statuses, ["info"])


if __name__ == "__main__":
    unittest.main()