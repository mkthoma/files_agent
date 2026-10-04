# STRIDE S1 + T3 for escalations
# S1: escalation another seat made with our subject shouldnt stop ours. T3: a create that lands and then errors is recorded failed and never sent again
import unittest
from agent.skills import triage
from harness.fake_server import FOREIGN_USER, FakeServer, RpcError
from helpers import FIXTURE_DIR, build_runtime, fake_server

# with the live allowlist (9 originals) tidy escalates exactly these 4
IMG_ID = "8018a70b-47d5-472b-88b6-b1ced1ced8b0"  # IMG_20260814_093214.jpg (3,118,440 bytes)
PO_COPY_ID = "82f83d94-5a46-4df3-9ee1-61e8b3c79d6e"  # PO_4471_ApexMetals_signed (1).pdf (218,044 bytes)
UNTITLED_ID = "60f685c9-bcb5-43a3-a403-18b7e9d76368"  # Untitled.pdf (88,420 bytes)
SCAN_ID = "b1d3894c-12e9-4ee1-b1da-82c7191ed4a0"  # scan0042.pdf (511,903 bytes)

# subject is "[files-agent] <file id> <filename>", every team can see + copy that format
IMG_SUBJECT = f"[files-agent] {IMG_ID} IMG_20260814_093214.jpg"
PO_COPY_SUBJECT = f"[files-agent] {PO_COPY_ID} PO_4471_ApexMetals_signed (1).pdf"
UNTITLED_SUBJECT = f"[files-agent] {UNTITLED_ID} Untitled.pdf"
SCAN_SUBJECT = f"[files-agent] {SCAN_ID} scan0042.pdf"
ALL_SUBJECTS = [IMG_SUBJECT, PO_COPY_SUBJECT, UNTITLED_SUBJECT, SCAN_SUBJECT]

# planted on the fake server before the run, made up ids
FOREIGN_ESC_ID = "e0000000-0000-4000-8000-00000000f00d"  # created by another seat
NO_CREATOR_ESC_ID = "e0000000-0000-4000-8000-0000000000c0"  # platform doesnt say who made it
OWN_ESC_ID = "e0000000-0000-4000-8000-000000000a11"  # ours from an earlier run
PLANTED_AT = "2026-09-30T10:00:00"  # before this run

# what the fake platform says when it loses a reply, and what we're allowed to repeat of it
LOST_REPLY_TEXT = "upstream timeout after commit (stand-in)"
WITHHELD_TEXT = "the platform's message is withheld because it may quote record data"
NOT_RESENT_TEXT = "an earlier create of this escalation errored; not resent in this run"


class LostReplyServer(FakeServer):
    # slow platform: saves the Untitled.pdf escalation then answers with an error, and our next
    # look at the escalations fails too so we cant tell it landed

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reply_lost = False
        self.next_list_fails = False

    def _call(self, name, args):
        if name == "AgentEscalation.list" and self.next_list_fails:
            self.next_list_fails = False
            raise RpcError(-32603, LOST_REPLY_TEXT, "agent_error")
        result = super()._call(name, args)  # create gets saved here before the reply goes back
        if name == "AgentEscalation.create" and UNTITLED_ID in args["subject"] and not self.reply_lost:
            self.reply_lost = self.next_list_fails = True
            raise RpcError(-32603, LOST_REPLY_TEXT, "agent_error")
        return result


def _plant(server, escalation_id, subject, created_by):
    # closed escalation on the fake server like it was made before this run, created_by=None leaves it out
    row = {"id": escalation_id, "subject": subject, "reason": "Planted before the run.", "reason_code": "other",
           "status": "closed", "created_at": PLANTED_AT, "updated_at": PLANTED_AT}
    if created_by is not None:
        row["created_by"] = created_by
    server.tables.setdefault("AgentEscalation", {})[escalation_id] = row


def _live_capped_tidy(server):
    # one apply mode tidy with the live allowlist on this server, returns the runtime
    rt, _ = build_runtime("apply", server=server, live_allowlist=True)
    triage.run(rt.ctx, {})
    return rt


def _created_subjects(server):
    return [write["args"]["subject"] for write in server.write_log if write["tool"] == "AgentEscalation.create"]


def _escalate_records(rt, file_id):
    return [r for r in rt.ctx.records.all() if r.skill == "escalate" and r.target_id == file_id]


class LookalikeEscalationTests(unittest.TestCase):  # S1

    def test_other_seat_escalation_ignored(self):
        # closed escalation another seat made with the Untitled.pdf subject isnt ours, tidy still makes 4
        server = fake_server()
        _plant(server, FOREIGN_ESC_ID, UNTITLED_SUBJECT, FOREIGN_USER)
        rt = _live_capped_tidy(server)
        self.assertCountEqual(_created_subjects(server), ALL_SUBJECTS)
        records = _escalate_records(rt, UNTITLED_ID)
        self.assertEqual([(r.action, r.status) for r in records], [("escalate", "escalated")])
        self.assertEqual(records[0].details["lookalike_escalation_id"], FOREIGN_ESC_ID)
        lookalikes = [(e["escalation_id"], e["created_by"]) for e in rt.trace.of_kind("foreign_escalation_subject")]
        self.assertEqual(lookalikes, [(FOREIGN_ESC_ID, FOREIGN_USER)])

    def test_no_creator_ignored(self):
        # our subject but no created_by, cant show its ours so still 4
        server = fake_server()
        _plant(server, NO_CREATOR_ESC_ID, UNTITLED_SUBJECT, None)
        rt = _live_capped_tidy(server)
        self.assertCountEqual(_created_subjects(server), ALL_SUBJECTS)
        unknown = [(e["our_id_known"], e["rows_without_creator"]) for e in rt.trace.of_kind("escalation_owner_unknown")]
        self.assertEqual(unknown, [(True, 1)])

    def test_own_escalation_stops_new(self):
        # one our seat made earlier for Untitled.pdf stops a new one and the record names it
        server = fake_server()
        our_id = server.me["id"]
        _plant(server, OWN_ESC_ID, UNTITLED_SUBJECT, our_id)
        rt = _live_capped_tidy(server)
        self.assertCountEqual(_created_subjects(server), [IMG_SUBJECT, PO_COPY_SUBJECT, SCAN_SUBJECT])
        records = _escalate_records(rt, UNTITLED_ID)
        self.assertEqual([(r.action, r.status) for r in records], [("already_escalated", "skipped")])
        self.assertEqual(records[0].details["existing_escalation_id"], OWN_ESC_ID)
        self.assertEqual(records[0].details["created_by"], our_id)


class LostReplyEscalationTests(unittest.TestCase):  # T3

    def setUp(self):
        self.server = LostReplyServer.from_fixture("keystone", FIXTURE_DIR)
        self.rt, _ = build_runtime("apply", server=self.server, live_allowlist=True)

    def test_lost_reply_recorded_failed(self):
        # Untitled.pdf escalation gets saved but the reply is an error -> recorded failed, maybe sent
        answer = triage.run(self.rt.ctx, {})["answer_text"]
        records = _escalate_records(self.rt, UNTITLED_ID)
        self.assertEqual([(r.action, r.status) for r in records], [("escalate", "failed")])
        self.assertEqual(records[0].details["write_sent"], "uncertain")
        self.assertEqual(records[0].details["error"], WITHHELD_TEXT)
        not_confirmed = [(r.target_id, r.status) for r in self.rt.ctx.records.all() if r.action == "escalation_not_confirmed"]
        self.assertEqual(not_confirmed, [(UNTITLED_ID, "failed")])
        self.assertIn(f"- FAILED Untitled.pdf ({UNTITLED_ID}): the escalation was not confirmed: {WITHHELD_TEXT}", answer)
        uncertain = [write["args"]["subject"] for write in self.rt.guard.writes if write.get("uncertain")]
        self.assertEqual(uncertain, [UNTITLED_SUBJECT])

    def test_tidy_carries_on(self):
        # other 3 still get escalated after the lost reply, platform ends up with one of each
        triage.run(self.rt.ctx, {})
        self.assertCountEqual(_created_subjects(self.server), ALL_SUBJECTS)
        for file_id in (IMG_ID, PO_COPY_ID, SCAN_ID):
            with self.subTest(file_id=file_id):
                records = _escalate_records(self.rt, file_id)
                self.assertEqual([(r.action, r.status) for r in records], [("escalate", "escalated")])

    def test_second_tidy_no_resend(self):
        # triage twice in one run, the maybe-landed Untitled.pdf escalation isnt sent again
        triage.run(self.rt.ctx, {})
        triage.run(self.rt.ctx, {})
        self.assertEqual(_created_subjects(self.server).count(UNTITLED_SUBJECT), 1)
        on_platform = [e for e in self.server.tables["AgentEscalation"].values() if e["subject"] == UNTITLED_SUBJECT]
        self.assertEqual(len(on_platform), 1)
        second = _escalate_records(self.rt, UNTITLED_ID)[-1]
        self.assertEqual((second.action, second.status), ("escalate", "skipped"))
        self.assertEqual(second.details["write_sent"], "uncertain")
        self.assertEqual(second.details["error"], NOT_RESENT_TEXT)


if __name__ == "__main__":
    unittest.main()
