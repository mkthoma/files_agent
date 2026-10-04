# decision records - what each skill reports about its work
import unittest
from agent.records import DecisionRecord, Evidence


class DecisionRecordTests(unittest.TestCase):  # REC-1

    def test_bad_status_or_confidence(self):
        # status 'done' and confidence 'high' both get refused
        with self.assertRaisesRegex(ValueError, "status must be one of"):
            DecisionRecord(skill="s", action="a", status="done")
        with self.assertRaisesRegex(ValueError, "confidence must be one of"):
            DecisionRecord(skill="s", action="a", status="info", confidence="high")

    def test_dict_round_trip(self):
        # full record -> dict -> back is equal to the original, evidence too
        record = DecisionRecord(skill="s", action="a", status="info", evidence=(Evidence("x", "y", "p", "q"),), missing=("m",), details={"k": 1})
        self.assertEqual(DecisionRecord.from_dict(record.to_dict()), record)


if __name__ == "__main__":
    unittest.main()
