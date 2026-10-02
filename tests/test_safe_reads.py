import unittest

from agent.safe_reads import find_files_by_name, list_all, not_equal


class StubMcp:
    def __init__(self):
        self.sent = []

    def call(self, tool, args):
        self.sent.append(dict(args))
        total = 1200
        offset = args.get("offset", 0)
        limit = args.get("limit", 500)
        rows = [{"id": str(i)} for i in range(offset, min(offset + limit, total))]
        return {"total": total, "data": rows}


class SafeReadsTest(unittest.TestCase):
    def test_pages_through_everything(self):
        stub = StubMcp()
        rows = list_all(stub, "FileAttachment.list")
        self.assertEqual(len(rows), 1200)
        self.assertEqual(len(stub.sent), 3)
        self.assertEqual([a["offset"] for a in stub.sent], [0, 500, 1000])

    def test_only_safe_filters_reach_the_server(self):
        stub = StubMcp()
        rows = list_all(stub, "FileAttachment.list", folder_id="f", tags="a,b", entity_type="ne:Item")
        for args in stub.sent:
            extra = {k for k in args if k not in ("limit", "offset")}
            self.assertEqual(extra, {"folder_id"})
            for value in args.values():
                self.assertNotIn(",", str(value))
                self.assertFalse(str(value).startswith("ne:"))
        self.assertEqual(rows, [])

    def test_not_equal_keeps_empty_values(self):
        rows = [{"entity_type": "Item"}, {"entity_type": None}, {"entity_type": ""}, {"entity_type": "Drive"}]
        self.assertEqual(not_equal(rows, "entity_type", "Item"), rows[1:])

    def test_filename_match_is_never_a_substring(self):
        rows = [{"filename": "scan0042.pdf"}, {"filename": "SCAN0042.pdf"}]
        self.assertEqual(find_files_by_name(rows, "scan0042"), [])
        self.assertEqual(find_files_by_name(rows, "scan0042.pdf"), [{"filename": "scan0042.pdf"}])
        self.assertEqual(find_files_by_name(rows, "Scan0042.PDF"), rows)


if __name__ == "__main__":
    unittest.main()
