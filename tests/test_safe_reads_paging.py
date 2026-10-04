# STRIDE D8 - list_all trusted the servers total, so a server ignoring offset kept it paging (with dupes) and a bad page crashed it
import unittest

from agent.mcp_client import McpError
from agent.safe_reads import list_all

TOOL = "DriveFolder.list"  # any .list tool works, list_all treats them the same
FIRST_PAGE = ({"id": "f1", "name": "HR"}, {"id": "f2", "name": "Finance"}, {"id": "f3", "name": "Incoming"})
BIG_TOTAL = 2_000_000  # tenant wide count, way more rows than the seat sees
PAGE_SIZE = 500  # PAGE in safe_reads.py
PAGE_CAP = 200  # MAX_PAGES in safe_reads.py
TABLE_SIZE = 1200  # 2 full pages + 1 short one


class NoOffsetMcp:
    # list tool that ignores offset, always gives back the first page

    def __init__(self, total):
        self.total = total
        self.offsets = []

    def call(self, tool, args):
        self.offsets.append(args["offset"])
        return {"data": [dict(row) for row in FIRST_PAGE], "total": self.total}


class CannedMcp:
    # same reply to every call whatever shape it is

    def __init__(self, page):
        self.page = page
        self.calls = 0

    def call(self, tool, args):
        self.calls += 1
        return self.page


class TableMcp:
    # TABLE_SIZE rows, honours limit/offset, reports total as given

    def __init__(self, total):
        self.total = total
        self.offsets = []

    def call(self, tool, args):
        self.offsets.append(args["offset"])
        ids = range(args["offset"], min(args["offset"] + args["limit"],TABLE_SIZE))
        return {"data": [{"id": f"row-{n}"} for n in ids], "total": self.total}


class EndlessMcp:
    # honours offset but never runs out of new rows

    def __init__(self):
        self.calls = 0

    def call(self, tool, args):
        self.calls += 1
        ids = range(args["offset"], args["offset"] + args["limit"])
        return {"data": [{"id": f"row-{n}"} for n in ids], "total": BIG_TOTAL}


class ListPagingGuardTests(unittest.TestCase):

    def test_offset_ignored_stops(self):
        # offset ignored -> repeated page raises no_progress after 2 calls instead of counting as more rows
        # big total kept the old loop paging, total=6 made it return 3 rows as if thats the whole table
        for total in (BIG_TOTAL, 6):
            with self.subTest(total=total):
                mcp = NoOffsetMcp(total)
                with self.assertRaises(McpError) as stopped:
                    list_all(mcp, TOOL)
                self.assertEqual(stopped.exception.data_code, "no_progress")
                self.assertEqual(str(stopped.exception), f"{TOOL} returned the same rows again at offset 3; stopped paging")
                self.assertEqual(mcp.offsets, [0, 3])

    def test_bad_page_shape(self):
        # bare list, no data list, or a row thats not an object -> bad_reply
        bad_pages = {
            "bare list": [dict(row) for row in FIRST_PAGE],
            "data is null": {"data": None, "total": 3},
            "data is an object": {"data": {"id": "f1"}, "total": 1},
            "row is a string": {"data": ["f1"], "total": 1},
            "page is text": "Internal Server Error",
        }
        for label, page in bad_pages.items():
            with self.subTest(page=label):
                mcp = CannedMcp(page)
                with self.assertRaises(McpError) as refused:
                    list_all(mcp, TOOL)
                self.assertEqual(refused.exception.data_code, "bad_reply")
                self.assertEqual(str(refused.exception), f"{TOOL} returned a page that is not a list of rows")
                self.assertEqual(mcp.calls, 1)

    def test_bad_total_ignored(self):
        # missing or garbage total (None, text, bool, negative, inf) gets ignored, reads till an empty page
        for total in (None, "many", True, -1, float("inf")):
            with self.subTest(total=total):
                mcp = TableMcp(total)
                rows = list_all(mcp, TOOL)
                self.assertEqual(len(rows), TABLE_SIZE)
                self.assertEqual(mcp.offsets, [0, PAGE_SIZE, 2 * PAGE_SIZE, TABLE_SIZE])

    def test_page_cap(self):
        # keeps getting new rows -> too_many_pages after 200 pages
        mcp = EndlessMcp()
        with self.assertRaises(McpError) as stopped:
            list_all(mcp, TOOL)
        self.assertEqual(stopped.exception.data_code, "too_many_pages")
        self.assertEqual(str(stopped.exception), f"{TOOL} still had rows after {PAGE_CAP} pages; stopped paging")
        self.assertEqual(mcp.calls, PAGE_CAP)


if __name__ == "__main__":
    unittest.main()
