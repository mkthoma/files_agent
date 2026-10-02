import unittest

from agent.runtime import build
from agent.skills import duplicates
from agent.skills.duplicates import find_groups, untrustworthy_hashes
from harness.fake_server import FakeServer


def row(file_id, filename, content_hash, size, created):
    return {"id": file_id, "filename": filename, "content_hash": content_hash,
            "size_bytes": size, "created_at": created}


class DuplicateGroupsTest(unittest.TestCase):
    def setUp(self):
        self.rows = [
            row("a", "A.pdf", "h", 100, "1"),
            row("a1", "A (1).pdf", "h", 100, "0"),
            row("b", "B.pdf", "h", 200, "2"),
        ]

    def test_hash_shared_by_different_files_is_untrusted(self):
        self.assertEqual(untrustworthy_hashes(self.rows), {"h"})

    def test_untrusted_hash_falls_back_to_name_and_size(self):
        groups = find_groups(self.rows)
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].original["id"], "a")
        self.assertEqual([c["id"] for c in groups[0].copies], ["a1"])
        self.assertEqual(groups[0].basis, "name + size (suspected)")

    def test_trusted_hash_groups_on_hash_size_and_name(self):
        rows = [row("x", "X.pdf", "k", 50, "0"), row("x1", "X (1).pdf", "k", 50, "1")]
        groups = find_groups(rows)
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].basis, "recorded hash + size + name")

    def test_original_is_the_plain_name_even_if_younger(self):
        rows = [row("x", "X.pdf", "k", 50, "1"), row("x1", "X (1).pdf", "k", 50, "0")]
        groups = find_groups(rows)
        self.assertEqual(groups[0].original["id"], "x")

    def test_answer_never_claims_byte_verification(self):
        server = FakeServer.from_fixture("keystone", None)
        server.armed = False
        rt = build("keystone", "fake", "plan", None, transport=server)
        text = duplicates.run(rt.ctx, {})["answer_text"]
        self.assertIn("not byte-verified", text)
        self.assertNotIn("byte-verified", text.replace("not byte-verified", ""))


if __name__ == "__main__":
    unittest.main()
