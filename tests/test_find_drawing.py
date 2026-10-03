# find_drawing tests: lookup by part number
import unittest

from agent.skills import find_drawing
from agent.skills.revisions import newest, parse_revision

from helpers import build_runtime, fake_server

J_BRKT_04_ITEM_ID = "bc49e18f-7a20-43e5-83ac-1b41dc7684ea"  # part J-BRKT-04
KJ_BRKT_04_ITEM_ID = "972ded4e-0d84-4ec9-9bb2-ebf098bbe9be"  # part KJ-BRKT-04
REV_B_ID = "91feaf59-c9b9-4e10-a603-ece98fa00e2b"  # J-BRKT-04_RevB_JigBracket.pdf
REV_C_ID = "2683b2c8-f700-4870-981c-1fb9c8d53393"  # J-BRKT-04_RevC_JigBracket.pdf
KJ_REV_A_ID = "e6010f05-1e88-47be-92a2-7ed2005b2c90"  # KJ-BRKT-04_RevA_BenchBracketSet.pdf

# extra file ids are made from filename so they never change
EXTRA_REV_A_ID = "b8f88faf-6492-5ff2-b558-7f28bc71f2a5"  # J-BRKT-04_RevA_JigBracket.pdf (extra file)
EXTRA_REV_D_ID = "fef7e36e-297e-5ed4-8c36-80cfba525af7"  # J-BRKT-04_RevD_JigBracket.pdf (extra file)
EXTRA_REV_1_ID = "04f39a89-7ebc-5dc3-b5ab-e4dd4a1d010a"  # J-BRKT-04_Rev1_JigBracket.pdf (extra file)

# expected current when RevC is current
REV_C_AS_CURRENT = {"id": REV_C_ID, "filename": "J-BRKT-04_RevC_JigBracket.pdf","revision": "C", "folder": "Jig & Fixture Drawings"}

# un-archives RevB and archives RevC
SWAP_REV_B_AND_C = f"swap_archived:{REV_B_ID}:{REV_C_ID}"


def _extra_drawing(filename, folder, tags):
    return {"filename": filename, "entity_type": "Item", "entity_id": J_BRKT_04_ITEM_ID,"folder": folder, "tags": tags}


def _records(rt, action):
    return [r for r in rt.ctx.records.all() if r.action == action]


def _drawings_by_id(result):
    return {d["id"]: d for d in result["drawings"]}


class FindDrawingTests(unittest.TestCase):

    def test_j_brkt_04_resolves_to_rev_c(self):
        # FD-1 RevC current, RevB superseded
        rt, server = build_runtime("plan")

        result = find_drawing.run(rt.ctx, {"part_code": "J-BRKT-04"})

        self.assertTrue(result["found"])
        self.assertEqual(result["current"], REV_C_AS_CURRENT)
        self.assertEqual(len(result["drawings"]), 2)
        self.assertTrue(_drawings_by_id(result)[REV_B_ID]["superseded"])
        self.assertEqual(result["conflicts"], [])
        self.assertEqual(result["lookalikes"], ["KJ-BRKT-04"])
        self.assertEqual(server.write_log, [])

    def test_j_brkt_04_records(self):
        # FD-1 records: RevC current, RevB superseded, KJ-BRKT-04 as lookalike
        rt, _ = build_runtime("plan")

        find_drawing.run(rt.ctx, {"part_code": "J-BRKT-04"})

        self.assertEqual([r.target_id for r in _records(rt, "current_drawing")], [REV_C_ID])
        self.assertEqual([r.target_id for r in _records(rt, "superseded_drawing")], [REV_B_ID])
        self.assertEqual([r.target_id for r in _records(rt, "lookalike_part")], [KJ_BRKT_04_ITEM_ID])

    def test_lowercase_part_code(self):
        # FD-1 lowercase j-brkt-04 gives same RevC
        rt, _ = build_runtime("plan")

        result = find_drawing.run(rt.ctx, {"part_code": "j-brkt-04"})

        self.assertTrue(result["found"])
        self.assertEqual(result["current"], REV_C_AS_CURRENT)

    def test_unknown_part_refused(self):
        # FD-2 unknown part code -> plain no such part, no guessing
        rt, _ = build_runtime("plan")

        result = find_drawing.run(rt.ctx, {"part_code": "J-BRKT-99"})

        self.assertFalse(result["found"])
        self.assertEqual(result["answer_text"], "No part has the exact code J-BRKT-99. I did not guess.")
        refused = rt.ctx.records.with_status("refused")
        self.assertEqual(len(refused), 1)
        self.assertEqual(refused[0].action, "part_not_found")

    def test_revision_question(self):
        # FD-3 asking about Rev B says superseded, asking C says current
        rt_b, _ = build_runtime("plan")
        rt_c, _ = build_runtime("plan")

        about_b = find_drawing.run(rt_b.ctx, {"part_code": "J-BRKT-04", "revision": "Rev B"})
        about_c = find_drawing.run(rt_c.ctx, {"part_code": "J-BRKT-04", "revision": "C"})

        self.assertIn("Revision B: not current - it is superseded.", about_b["answer_text"])
        self.assertIn("Revision C: current.", about_c["answer_text"])

    def test_revision_spellings(self):
        # FD-3 all these spellings = B, no revision = ''
        for spelling in ("Rev B", "rev-b", "Rev. B", "revision B"):
            with self.subTest(spelling=spelling):
                self.assertEqual(find_drawing.normalise_revision(spelling), "B")
        self.assertEqual(find_drawing.normalise_revision(None), "")

    def test_two_released_no_current(self):
        # FD-4 RevC and a released RevD both look current so neither is named
        rev_d = _extra_drawing("J-BRKT-04_RevD_JigBracket.pdf", "Jig & Fixture Drawings", "drawing,released")
        rt, _ = build_runtime("plan", extra_files=[rev_d])

        result = find_drawing.run(rt.ctx, {"part_code": "J-BRKT-04"})

        self.assertIn(EXTRA_REV_D_ID, _drawings_by_id(result), msg="the extra RevD file was not loaded")
        self.assertIsNone(result["current"])
        clash = [c for c in result["conflicts"] if c.startswith("more than one revision looks current")]
        self.assertEqual(len(clash), 1, msg=result["conflicts"])
        self.assertIn("J-BRKT-04_RevD_JigBracket.pdf", clash[0])
        self.assertIn("J-BRKT-04_RevC_JigBracket.pdf", clash[0])
        answer = result["answer_text"]
        self.assertTrue(answer.startswith("I can't name a single current drawing for part J-BRKT-04"), msg=answer)
        self.assertEqual(_records(rt, "current_drawing"), [])

    def test_kj_brkt_04_own_rev_a(self):
        # FD-5 KJ-BRKT-04 gets its own RevA + warns J-BRKT-04 is a diffrent part
        rt, _ = build_runtime("plan")

        result = find_drawing.run(rt.ctx, {"part_code": "KJ-BRKT-04"})

        self.assertEqual(result["current"], {"id": KJ_REV_A_ID, "filename": "KJ-BRKT-04_RevA_BenchBracketSet.pdf","folder": "Production Drawings", "revision": "A"})
        self.assertEqual(result["lookalikes"], ["J-BRKT-04"])
        self.assertNotIn(REV_C_ID, _drawings_by_id(result))
        self.assertNotIn(REV_B_ID, _drawings_by_id(result))

    def test_swapped_archive_flags(self):
        # FD-6 RevB/RevC archive flags swapped -> both conflicts reported, nothing current
        rt, _ = build_runtime("plan", faults=(SWAP_REV_B_AND_C,))

        result = find_drawing.run(rt.ctx, {"part_code": "J-BRKT-04"})

        self.assertIsNone(result["current"])
        self.assertIn("J-BRKT-04_RevB_JigBracket.pdf is tagged 'superseded' but not archived", result["conflicts"])
        self.assertIn("J-BRKT-04_RevC_JigBracket.pdf is tagged 'released' but archived or in Superseded",result["conflicts"])
        answer = result["answer_text"]
        self.assertTrue(answer.startswith("I can't name a single current drawing"), msg=answer)

    def test_duplicate_part_code_refused(self):
        # FD-7 two parts share code J-BRKT-04 -> refuse, dont pick one
        server = fake_server()
        server.tables["Item"]["dup-item"] = {"id": "dup-item", "code": "J-BRKT-04", "name": "dup"}
        rt, _ = build_runtime("plan", server=server)

        result = find_drawing.run(rt.ctx, {"part_code": "J-BRKT-04"})

        self.assertFalse(result["found"])
        answer = result["answer_text"]
        self.assertTrue(answer.startswith("2 parts share the exact code J-BRKT-04"), msg=answer)
        self.assertTrue(answer.endswith("I did not guess which one you mean."), msg=answer)
        ambiguous = _records(rt, "ambiguous_part")
        self.assertEqual(len(ambiguous), 1)
        self.assertEqual(ambiguous[0].status, "refused")

    def test_unreleased_tag(self):
        # FD-8 tags match whole so old unreleased drawing should not hide RevC
        self.assertIn("unreleased", find_drawing.tag_set("drawing,Unreleased"))
        self.assertNotIn("released", find_drawing.tag_set("drawing,Unreleased"))
        self.assertEqual(find_drawing.tag_set("drawing, Released"), {"drawing", "released"})

        rev_a = _extra_drawing("J-BRKT-04_RevA_JigBracket.pdf", "Superseded", "drawing,unreleased")
        rt, _ = build_runtime("plan", extra_files=[rev_a])
        result = find_drawing.run(rt.ctx, {"part_code": "J-BRKT-04"})

        self.assertEqual(result["current"], REV_C_AS_CURRENT)
        self.assertEqual(result["conflicts"], [])
        self.assertEqual(len(result["drawings"]), 3)
        self.assertTrue(_drawings_by_id(result)[EXTRA_REV_A_ID]["superseded"])

    def test_superseded_folder_only(self):
        # FD-9 being in Superseded folder is enough, even if not archived or tagged
        rev_a = _extra_drawing("J-BRKT-04_RevA_JigBracket.pdf", "Superseded", "drawing")
        rt, _ = build_runtime("plan", extra_files=[rev_a])

        result = find_drawing.run(rt.ctx, {"part_code": "J-BRKT-04"})

        self.assertEqual(result["current"], REV_C_AS_CURRENT)
        self.assertEqual(result["conflicts"], [])
        old_drawing = _drawings_by_id(result)[EXTRA_REV_A_ID]
        self.assertTrue(old_drawing["superseded"])
        self.assertEqual(old_drawing["folder"], "Superseded")
        self.assertIn(EXTRA_REV_A_ID, [r.target_id for r in _records(rt, "superseded_drawing")])
        superseded_line = (f"J-BRKT-04_RevA_JigBracket.pdf ({EXTRA_REV_A_ID}) is superseded (archived: False, folder 'Superseded').")
        self.assertIn(superseded_line, result["answer_text"])

    def test_mixed_revisions_no_current(self):
        # FD-10 Rev1 vs RevC cant be ranked so no current
        top, problems = newest([parse_revision("X_RevC.pdf"), parse_revision("X_Rev1.pdf")])
        self.assertIsNone(top)
        self.assertEqual(problems, ["mixed letter and number revisions in one family"])

        rev_1 = _extra_drawing("J-BRKT-04_Rev1_JigBracket.pdf", "Superseded", "drawing")
        rt, _ = build_runtime("plan", extra_files=[rev_1])
        result = find_drawing.run(rt.ctx, {"part_code": "J-BRKT-04"})

        self.assertIn(EXTRA_REV_1_ID, _drawings_by_id(result), msg="the extra Rev1 file was not loaded")
        self.assertIsNone(result["current"])
        self.assertEqual(result["conflicts"], ["mixed letter and number revisions in one family"])
        answer = result["answer_text"]
        self.assertTrue(answer.startswith("I can't name a single current drawing for part J-BRKT-04: mixed letter and number revisions in one family."), msg=answer)
        self.assertEqual(_records(rt, "current_drawing"), [])

    def test_newest_superseded_no_current(self):
        # FD-11 RevD filed as superseded but older RevC looks current -> nothing named current
        rev_d = _extra_drawing("J-BRKT-04_RevD_JigBracket.pdf", "Superseded", "drawing")
        rt, _ = build_runtime("plan", extra_files=[rev_d])

        result = find_drawing.run(rt.ctx, {"part_code": "J-BRKT-04"})

        self.assertIsNone(result["current"])
        self.assertEqual(result["conflicts"],["the newest revision (RevD) is marked superseded while an older one looks current"])
        answer = result["answer_text"]
        self.assertTrue(answer.startswith("I can't name a single current drawing for part J-BRKT-04: the newest revision (RevD) is marked superseded while an older one looks current."),msg=answer)
        self.assertIn(REV_C_ID, [r.target_id for r in _records(rt, "candidate_drawing")])
        self.assertEqual(_records(rt, "current_drawing"), [])


if __name__ == "__main__":
    unittest.main()