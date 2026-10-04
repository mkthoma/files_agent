# write whose reply is an error - reported uncertain and the tidy carries on (STRIDE I12 partly)
# first FileAttachment.update of the tidy (the mill cert) comes back as an error inside a 200 reply
import unittest
from agent.skills import triage
from helpers import build_runtime

INCOMING_FOLDER_ID = "6f8a3ed1-f2df-46a7-8dcb-275e9494c799"  # Incoming

# every original in Incoming has a 880 byte copy with the same name, hence the sizes
TIMESHEET_ID = "1ee27946-7064-42e1-afce-376068a545bf"  # timesheet_week33.xlsx (42,115 bytes)
KNOB_ID = "b45cecdd-9f14-491a-a0ee-2826d3fabb15"  # J-KNOB-09_RevA.dxf (61,208 bytes)
MILL_CERT_ID = "680e8af6-15f3-49c6-b70b-987316fa5775"  # Cert_MillCert_SS304_Heat90114.pdf (149,770 bytes)
W9_ID = "81857de6-e6e9-41c5-9da8-67cb5d1903c1"  # W9_JMillerWelding_2026.pdf (96,331 bytes)
PO_ID = "732439a0-7f36-4d31-ac3b-f406c41c00bd"  # PO_4471_ApexMetals_signed.pdf (218,044 bytes)

FIRST_UPDATE_FAULT = "error_in_200:FileAttachment.update"  # one shot fault, first update only
# I12: a record only states error text we know or wrote ourselves
WITHHELD_ERROR = "the platform's message is withheld because it may quote record data"


def _records(rt, action):
    return [r for r in rt.ctx.records.all() if r.action == action]


def _updated_ids(server):
    return [entry["id"] for entry in server.write_log if entry["tool"] == "FileAttachment.update"]


def _folder_of(server, file_id):
    return server.tables["FileAttachment"][file_id]["folder_id"]


class UncertainWriteTests(unittest.TestCase):  # GUARD-7

    def test_errored_update_uncertain(self):
        # mill cert update comes back with an error so its write is uncertain, never 'not sent'
        rt, _ = build_runtime("apply", faults=(FIRST_UPDATE_FAULT,))
        answer = triage.run(rt.ctx, {})["answer_text"]
        failed_moves = [r for r in _records(rt, "move") if r.status == "failed"]
        self.assertEqual([r.target_id for r in failed_moves], [MILL_CERT_ID])
        self.assertEqual(failed_moves[0].details["write_sent"], "uncertain")
        self.assertEqual(failed_moves[0].details["error"], WITHHELD_ERROR)
        mill_cert_writes = [w for w in rt.guard.writes if w.get("id") == MILL_CERT_ID]
        self.assertEqual(len(mill_cert_writes), 1)
        self.assertEqual(mill_cert_writes[0]["tool"], "FileAttachment.update")
        self.assertIs(mill_cert_writes[0].get("uncertain"), True)
        self.assertIn("FAILED Cert_MillCert_SS304_Heat90114.pdf", answer)
        failed_calls = [e for e in rt.trace.of_kind("mcp_call") if e["tool"] == "FileAttachment.update" and not e["ok"]]
        self.assertEqual(len(failed_calls), 1)

    def test_tidy_carries_on(self):
        # mill cert stays in Incoming and the other 4 moves still happen
        rt, server = build_runtime("apply", faults=(FIRST_UPDATE_FAULT,))
        triage.run(rt.ctx, {})
        self.assertEqual(_folder_of(server, MILL_CERT_ID), INCOMING_FOLDER_ID)
        self.assertCountEqual(_updated_ids(server), [KNOB_ID, PO_ID, W9_ID, TIMESHEET_ID])


if __name__ == "__main__":
    unittest.main()
