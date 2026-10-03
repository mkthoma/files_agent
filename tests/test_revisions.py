import unittest

from agent.skills.revisions import code_prefix, newest, parse_revision, part_code


class RevisionParserTest(unittest.TestCase):
    def test_letter_revision(self):
        rev = parse_revision("J-BRKT-04_RevC_JigBracket.pdf")
        self.assertEqual(rev.scheme, "letter")
        self.assertEqual(rev.ordinal, 3)
        self.assertEqual(rev.flags, ())

    def test_double_letters_sort_after_z(self):
        z = parse_revision("X_RevZ.pdf")
        aa = parse_revision("X_RevAA.pdf")
        top, problems = newest([z, aa])
        self.assertEqual(problems, [])
        self.assertEqual(top.raw, "AA")

    def test_numbers_sort_numerically(self):
        two = parse_revision("X_Rev2.pdf")
        ten = parse_revision("X_Rev10.pdf")
        top, problems = newest([ten, two])
        self.assertEqual(top.raw, "10")
        self.assertEqual(top.scheme, "number")
        self.assertEqual(problems, [])

    def test_no_marker_is_none(self):
        self.assertIsNone(parse_revision("Untitled.pdf"))

    def test_last_marker_wins_but_flagged(self):
        rev = parse_revision("X_RevB_RevC.pdf")
        self.assertEqual(rev.raw, "C")
        self.assertIn("several revision markers in the name", rev.flags)

    def test_o_flagged_as_confusable(self):
        rev = parse_revision("X_RevO.pdf")
        self.assertIn("uses I or O, which revision schemes usually skip", rev.flags)

    def test_mixed_schemes_pick_nothing(self):
        b = parse_revision("X_RevB.pdf")
        two = parse_revision("X_Rev2.pdf")
        self.assertEqual(newest([b, two]), (None, ["mixed letter and number revisions in one family"]))

    def test_kj_prefix_is_not_j(self):
        self.assertEqual(part_code("KJ-BRKT-04_RevA.pdf"), "KJ-BRKT-04")
        self.assertEqual(code_prefix("KJ-BRKT-04"), "KJ")
        self.assertNotEqual(code_prefix("KJ-BRKT-04"), "J")


if __name__ == "__main__":
    unittest.main()
