# STRIDE I1 - fields the leak guard keeps on a withheld row
# sanitise_file used to blank a fixed list and pass the rest through, so display fields the platform fills later (_party_id_display etc) or thumbnail_path could leak the real title or candidate name
# now only KEEP_FIELDS stay, everything else is None
import json
import unittest
from agent.loop import _execute, tool_definitions
from agent.privacy import sanitise_file
from helpers import build_runtime, fake_server

# fake esign row (no server), after the esign team added rev 1 and linked the candidates Party
OFFER_ID = "c0ffee00-1111-4222-8333-444455556666"  # attachment row
OFFER_ENTITY_ID = "39074d17-67c0-4622-8ef6-53fa259cbd18"  # its EsignDocument
OFFER_HASH = "1209a87083d2f78b1401579e5948819442dd3d1c1d32fe803cd8289c554e2588"
OFFER_CREATED_AT = "2026-09-16T16:45:20.992312+00:00"  # created_at + updated_at
OFFER_TITLE = "Offer Letter - Canary Zebra - salary 95k.pdf"  # real title, must never show up
PLACEHOLDER = "EsignDocument-attachment-c0ffee00.pdf"  # what leak guard shows instead
CANDIDATE = "Canary Zebra"  # name on the Party
REVISION_ID = "rev-0001"  # rev added by esign team
PARTY_ID = "party-0001"

# canary the fake server plants, id comes from the filename
CANARY_FILE = {"filename": "Offer Letter - Canary.pdf", "entity_type": "EsignDocument", "folder": ""}
CANARY_ID = "af1fc223-b5ff-5959-93e1-68eb365c5d64"  # Offer Letter - Canary.pdf (extra file)
CANARY_PERSON = "Canary Person"  # Party name planted on canary
PLANTED_FIELDS = ("_current_revision_id_display", "_party_id_display", "thumbnail_path")  # fields I1 names


def _never_listable(entity_type):
    return False


def _offer():
    # fresh copy of the fake esign row, title + candidate name sitting in non private fields
    return {"id": OFFER_ID, "entity_type": "EsignDocument", "entity_id": OFFER_ENTITY_ID,
            "filename": OFFER_TITLE, "_display": OFFER_TITLE, "folder_id": None, "size_bytes": 1391.0,
            "content_hash": OFFER_HASH, "mime_type": "application/pdf",
            "created_at": OFFER_CREATED_AT, "updated_at": OFFER_CREATED_AT,
            "current_revision_id": REVISION_ID, "current_revision_number": 1.0,
            "_current_revision_id_display": OFFER_TITLE,
            "party_id": PARTY_ID, "_party_id_display": CANDIDATE,
            "thumbnail_path": f"thumbs/{OFFER_TITLE}.png"}


class WithheldRowAllowListTests(unittest.TestCase):

    def test_display_fields_blanked(self):
        # revision/Party display fields + thumbnail lose title and name, KEEP_FIELDS stay
        row = _offer()
        safe = sanitise_file(row, _never_listable)

        expected = {"id": OFFER_ID, "entity_type": "EsignDocument", "entity_id": OFFER_ENTITY_ID,
                    "filename": PLACEHOLDER, "_display": PLACEHOLDER, "folder_id": None,
                    "size_bytes": 1391.0, "content_hash": OFFER_HASH, "mime_type": "application/pdf",
                    "created_at": OFFER_CREATED_AT, "updated_at": OFFER_CREATED_AT,
                    "current_revision_id": None, "current_revision_number": 1.0,
                    "_current_revision_id_display": None, "party_id": None, "_party_id_display": None,
                    "thumbnail_path": None}
        self.assertEqual(safe, expected)
        self.assertNotIn("Canary", json.dumps(safe))

    def test_new_field_blanked(self):
        # field nobody knows about yet (like _signer_id_display) comes back None but stays in the row
        row = {**_offer(), "_signer_id_display": CANDIDATE, "title": OFFER_TITLE}

        safe = sanitise_file(row, _never_listable)

        self.assertIsNone(safe["_signer_id_display"])
        self.assertIsNone(safe["title"])
        self.assertEqual(set(safe), set(row), msg="a withheld row keeps its shape")


class CanaryDisplayFieldTests(unittest.TestCase):

    def setUp(self):
        server = fake_server(extra_files=[CANARY_FILE])
        canary = server.tables["FileAttachment"][CANARY_ID]
        # platform fills these in once canary gets a revision + linked Party
        server.tables["FileAttachment"][CANARY_ID] = {
            **canary, "current_revision_id": REVISION_ID, "_current_revision_id_display": canary["filename"],
            "party_id": PARTY_ID, "_party_id_display": CANARY_PERSON, "thumbnail_path": f"thumbs/{canary['filename']}.png",
        }
        self.server = server
        self.rt, _ = build_runtime("plan", server=server)

    def test_model_read_and_trace(self):
        # models own FileAttachment.get on canary + the trace show none of the planted values
        _, mapping = tool_definitions(self.rt.catalog)
        # sanity check: raw row does have the title and name
        raw = json.dumps(self.server.tables["FileAttachment"][CANARY_ID])
        self.assertEqual(raw.count("Canary"), 4)
        output, is_error = _execute(self.rt.ctx, "mcp__FileAttachment__get", {"id": CANARY_ID}, mapping)
        self.assertFalse(is_error, msg=output)
        row = json.loads(output)
        self.assertEqual({field: row[field] for field in PLANTED_FIELDS}, dict.fromkeys(PLANTED_FIELDS))
        self.assertNotIn("Canary", output)
        # trace keeps the whole row for a single get, so theres actually a row for the check below
        traced = [event["result"] for event in self.rt.trace.of_kind("mcp_call") if event["tool"] == "FileAttachment.get"]
        self.assertEqual([result["id"] for result in traced], [CANARY_ID])
        self.assertNotIn("Canary", json.dumps(self.rt.trace.events))

    def test_skill_rows(self):
        # canary row in ctx.files (every skill reads this) has planted fields as None
        rows = self.rt.ctx.files()
        canary = next(row for row in rows if row["id"] == CANARY_ID)
        self.assertEqual({field: canary[field] for field in PLANTED_FIELDS}, dict.fromkeys(PLANTED_FIELDS))
        self.assertNotIn("Canary", json.dumps(rows))


if __name__ == "__main__":
    unittest.main()
