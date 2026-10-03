# leak guard tests: other apps data must not leak to the model
import json
import unittest

from agent.loop import _execute, tool_definitions
from agent.privacy import is_withheld, sanitise_file
from agent.skills.access import list_files

from helpers import build_runtime, fake_server

# id is made from filename by fake server so its stable
CANARY_ID = "af1fc223-b5ff-5959-93e1-68eb365c5d64"  # Offer Letter - Canary.pdf (extra file)
CANARY_PLACEHOLDER = "EsignDocument-attachment-af1fc223"  # model should see this not the real title
CANARY_LOG_ID = "aaaaaaaa-0000-0000-0000-000000000001"  # fake DriveAccessLog row for canary upload
JANE_OFFER_ID = "abcdef12-0000-0000-0000-000000000000"  # Offer Letter - Jane.pdf, made up row (no server)
CANARY_FILE = {
    "filename": "Offer Letter - Canary.pdf",
    "entity_type": "EsignDocument",
    "folder": "",
    "description": "Offer for Canary Person",
}


def _jane_offer_row():
    return {"id": JANE_OFFER_ID, "entity_type": "EsignDocument", "filename": "Offer Letter - Jane.pdf",
            "description": "salary", "tags": "hr", "from_email": "a@b.c", "party_id": "p1",
            "size_bytes": 10, "folder_id": "F"}


# stand-ins for Catalog.can_list
def _never_listable(entity_type):
    return False


def _always_listable(entity_type):
    return True


def _call_as_model(rt, tool_name, args):
    # same path the agent loop uses when model calls a tool
    _, mapping = tool_definitions(rt.catalog)
    return _execute(rt.ctx, tool_name, args, mapping)


def _file_ids(output):
    return [row["file_id"] for row in json.loads(output)["data"]]


class PlaceholderTests(unittest.TestCase):  # PRIV-1

    def test_esign_row_placeholder(self):
        # esign row loses title + private fields but keeps id, size and folder
        row = _jane_offer_row()
        before = dict(row)

        safe = sanitise_file(row, _never_listable)

        self.assertEqual(safe["filename"], "EsignDocument-attachment-abcdef12.pdf")
        self.assertEqual(safe["_display"], "EsignDocument-attachment-abcdef12.pdf")
        for field in ("description", "tags", "from_email", "party_id"):
            self.assertIsNone(safe[field], msg=field)
        self.assertEqual(safe["id"], JANE_OFFER_ID)
        self.assertEqual(safe["size_bytes"], 10)
        self.assertEqual(safe["folder_id"], "F")
        self.assertEqual(row, before, msg="the input row must not be changed")
        self.assertTrue(is_withheld(row, _never_listable))

    def test_open_rows_untouched(self):
        # None, '', 'Drive' or app the seat can list -> same object back
        cases = [(None, _never_listable), ("", _never_listable), ("Drive", _never_listable), ("Item", _always_listable)]
        for entity_type, can_list in cases:
            with self.subTest(entity_type=entity_type):
                row = {**_jane_offer_row(), "entity_type": entity_type}
                self.assertIs(sanitise_file(row, can_list), row)
                self.assertFalse(is_withheld(row, can_list))


class SkillReadsTests(unittest.TestCase):  # PRIV-2

    def setUp(self):
        self.rt, _ = build_runtime("plan", extra_files=[CANARY_FILE])

    def test_ctx_rows_hide_canary(self):
        # canary row is kept in ctx.files but 'Canary' never shows in filename or description
        rows = self.rt.ctx.files()

        self.assertIn(CANARY_ID, [row["id"] for row in rows], msg="the canary row must be planted and kept")
        leaked = [row for row in rows if "Canary" in str(row.get("filename")) or "Canary" in str(row.get("description"))]
        self.assertEqual(leaked, [])

    def test_list_files_withheld(self):
        # 30 shown, 84 esign rows withheld (83 + canary) and canary never named
        result = list_files(self.rt.ctx, {})

        self.assertEqual(result["shown"], 30)
        self.assertEqual(result["withheld"], {"EsignDocument": 84})
        self.assertTrue(result["answer_text"].endswith(
            "84 further rows were withheld because they belong to apps this seat can't open (EsignDocument: 84)."),
            msg=result["answer_text"])
        self.assertNotIn("Canary", json.dumps(result))


class ModelFileReadTests(unittest.TestCase):  # PRIV-3

    def test_model_reads_placeholder_only(self):
        # models own FileAttachment.get/list calls only see the placeholder for canary
        rt, server = build_runtime("plan", extra_files=[CANARY_FILE])
        # sanity check, raw row on server does have the real title
        self.assertIn("Canary", server.tables["FileAttachment"][CANARY_ID]["filename"])

        # newest rows come first and canary is the newest so its on a page of 5
        calls = [("mcp__FileAttachment__get", {"id": CANARY_ID}), ("mcp__FileAttachment__list", {"limit": 5})]
        for tool_name, args in calls:
            with self.subTest(tool=tool_name):
                output, is_error = _call_as_model(rt, tool_name, args)
                self.assertFalse(is_error, msg=output)
                self.assertNotIn("Canary", output)
                self.assertIn(CANARY_PLACEHOLDER, output)


class ModelAccessLogAndSearchTests(unittest.TestCase):  # PRIV-4

    def setUp(self):
        server = fake_server(extra_files=[CANARY_FILE])
        # same shape as fixture access log rows (_display and _file_id_display hold the filename)
        server.tables["DriveAccessLog"][CANARY_LOG_ID] = {
            "id": CANARY_LOG_ID, "action": "upload", "file_id": CANARY_ID,
            "_display": "Offer Letter - Canary.pdf", "_file_id_display": "Offer Letter - Canary.pdf",
            "details": "Uploaded by HR.", "created_at": "2026-09-26T09:00:00",
        }
        self.rt, _ = build_runtime("plan", server=server)

    def test_access_log_hides_canary(self):
        filtered, filtered_error = _call_as_model(self.rt, "mcp__DriveAccessLog__list", {"file_id": CANARY_ID})
        latest, latest_error = _call_as_model(self.rt, "mcp__DriveAccessLog__list", {"limit": 20})

        # first 4 checks make sure canary row is actually returned, else the title checks pass for nothing
        self.assertFalse(filtered_error, msg=filtered)
        self.assertFalse(latest_error, msg=latest)
        self.assertEqual(_file_ids(filtered), [CANARY_ID])
        self.assertIn(CANARY_ID, _file_ids(latest), msg="the canary's log row must be on the unfiltered page")
        self.assertNotIn("Canary", filtered)
        self.assertNotIn("Canary", latest)

    def test_tool_search_hides_canary(self):
        # tools.search only returns tools, never the canary title
        for query in ("offer letter", "Canary"):
            with self.subTest(query=query):
                output, is_error = _call_as_model(self.rt, "mcp__tools__search", {"query": query})
                self.assertFalse(is_error, msg=output)
                self.assertNotIn("Canary", output)
                self.assertEqual(json.loads(output), {"results": [], "status": "ok"})


if __name__ == "__main__":
    unittest.main()