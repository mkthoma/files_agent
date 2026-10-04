# write guard STRIDE fixes - T1 (write reply lost), E1 (live writes need the harness), E2 (field allowlist), T11 (another team changes something inside our write window)
import http.client
import json
import unittest
from urllib.parse import urlparse
import agent.http as agent_http
from agent.guards import WriteBlocked, WriteGuard
from agent.http import HttpTransport
from agent.redact import Redactor
from agent.runtime import build
from agent.skills import triage
from agent.trace import Trace
from harness.fake_server import FakeServer

from helpers import FIXTURE_DIR, build_runtime, fake_server, quiet_settings

INCOMING_FOLDER_ID = "6f8a3ed1-f2df-46a7-8dcb-275e9494c799"  # Incoming
JIG_FOLDER_ID = "0449912e-f8c2-406f-b983-a2beca76ea93"  # Jig & Fixture Drawings, knob gets filed here

# every original in Incoming has a 880 byte copy with same name so the size is in each comment
TIMESHEET_ID = "1ee27946-7064-42e1-afce-376068a545bf"  # timesheet_week33.xlsx (42,115 bytes)
KNOB_ID = "b45cecdd-9f14-491a-a0ee-2826d3fabb15"  # J-KNOB-09_RevA.dxf (61,208 bytes)
MILL_CERT_ID = "680e8af6-15f3-49c6-b70b-987316fa5775"  # Cert_MillCert_SS304_Heat90114.pdf (149,770 bytes)
W9_ID = "81857de6-e6e9-41c5-9da8-67cb5d1903c1"  # W9_JMillerWelding_2026.pdf (96,331 bytes)
PO_ID = "732439a0-7f36-4d31-ac3b-f406c41c00bd"  # PO_4471_ApexMetals_signed.pdf (218,044 bytes)

# fake address, nothing ever actually goes there
OFFLINE_URL = "https://offline.invalid"
# bytes of a cut off reply that arrive before the drop
CUT_AT = 40
# W-9 tags in the 26 Sept fixture + what another team sets while we move it
W9_TAGS = "untriaged"
THEIR_TAGS = "vendor-tax,on-hold"
# answer adds this to the line when another seat changed tags during our write
TAGS_NOTE = "Another seat changed its tags at the same moment; check the file by hand."


class RecordingClient:
    # fake mcp client, notes the name of every tool called
    # script maps tool -> answers given out in order, last one repeats. exceptions (ctrl-c too) get raised, no script = empty record

    def __init__(self, script=None):
        self.script = {tool: list(answers) for tool, answers in (script or {}).items()}
        self.calls = []

    def call(self, tool, args):
        self.calls.append(tool)
        answers = self.script.get(tool, [{}])
        answer = answers.pop(0) if len(answers) > 1 else answers[0]
        if isinstance(answer, BaseException):
            raise answer
        return answer


class CannedReply:
    # fake http response, gives back the fake servers reply or drops the connection mid body

    def __init__(self, status, raw, cut_off):
        self.status = status
        self.raw = raw
        self.cut_off = cut_off

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def read(self, amount=-1):
        if self.cut_off:
            raise http.client.IncompleteRead(self.raw[:CUT_AT], len(self.raw) - CUT_AT)
        out, self.raw = self.raw, b""
        return out


class CutReplyOpener:
    # network under the real HttpTransport: fake server applies every request but the reply to
    # the first update of one file gets cut off after the server applied it

    def __init__(self, server, cut_file_id):
        self.server = server
        self.cut_file_id = cut_file_id
        self.has_cut = False

    def open(self, req, timeout=None):
        auth = req.get_header("Authorization") or ""
        token = auth[len("Bearer "):] if auth.startswith("Bearer ") else None
        body = json.loads(req.data) if req.data else None
        status, data = self.server.request(req.get_method(), urlparse(req.full_url).path, token, body)
        cut_off = not self.has_cut and self._updates_cut_file(body)
        self.has_cut = self.has_cut or cut_off
        return CannedReply(status, json.dumps(data).encode("utf-8"), cut_off)

    def _updates_cut_file(self, body):
        params = (body or {}).get("params") or {}
        return params.get("name") == "FileAttachment.update" and (params.get("arguments") or {}).get("id") == self.cut_file_id


class OfflineHttpTransport(HttpTransport):
    # real HttpTransport code, marked fake since its opener is the fake server
    is_fake = True


class TransportProxy:
    # real (non fake) transport stand-in, passes requests to the fake server but doesnt say its fake
    def __init__(self, server):
        self.server = server
        self.requests = []

    def request(self, method, path, token=None, body=None, idempotent=True):
        self.requests.append((method, path))
        return self.server.request(method, path, token, body, idempotent)


class RetagServer(FakeServer):
    # another team retags the W-9 right when our move of it lands
    def _update_file(self, args):
        reply = super()._update_file(args)
        if args.get("id") == W9_ID:
            self.tables["FileAttachment"][W9_ID]["tags"] = THEIR_TAGS
        return reply


def _guard(client, live=False):
    # apply mode guard on the stand-in client, in memory trace, only file 'a' allowed
    return WriteGuard(client, Trace(None, Redactor()), "apply", frozenset({"a"}),live=live)

def _row_a(**fields):
    # file 'a' the way the pre-read returns it, seat can write it
    return {"id": "a", "_permissions": {"write": True}, **fields}


def _records(rt, action, status):
    return [r for r in rt.ctx.records.all() if r.action == action and r.status == status]


def _blocked_reasons(guard):
    return [event["reason"] for event in guard.trace.of_kind("write_blocked")]


class CutOffReplyTests(unittest.TestCase):  # T1

    def test_cut_off_reply_uncertain(self):
        # update reply cut off mid body -> journaled uncertain since platform may have applied it
        client = RecordingClient({
            "FileAttachment.get": [_row_a(folder_id="INC")],
            "FileAttachment.update": [http.client.IncompleteRead(b'{"jsonrpc": "2.0"', 200)],
        })
        guard = _guard(client)
        journal = []
        guard.journal = journal.append
        with self.assertRaises(http.client.IncompleteRead):
            guard.update_file("a", {"folder_id": "HR"})

        expected = {"tool": "FileAttachment.update", "id": "a", "changes": {"folder_id": "HR"}, "before": {"folder_id": "INC"}, "uncertain": True}
        self.assertEqual(guard.writes, [expected])
        self.assertEqual(journal, [expected])
        self.assertEqual(client.calls, ["FileAttachment.get", "FileAttachment.update"])

    def test_ctrl_c_create_uncertain(self):
        # ctrl-c while a session create waits still leaves it in the journal as uncertain
        client = RecordingClient({"AgentSession.create": [KeyboardInterrupt()]})
        guard = _guard(client)
        journal = []
        guard.journal = journal.append
        with self.assertRaises(KeyboardInterrupt):
            guard.create("AgentSession.create", {"title": "files-agent run"})
        expected = {"tool": "AgentSession.create", "args": {"title": "files-agent run"}, "uncertain": True}
        self.assertEqual(guard.writes, [expected])
        self.assertEqual(journal, [expected])

    def test_tidy_carries_on(self):
        # knob move lands but reply gets cut -> FAILED + uncertain, other 4 moves still happen
        server = fake_server()
        old_opener = agent_http.NO_REDIRECT_OPENER
        agent_http.NO_REDIRECT_OPENER = CutReplyOpener(server, KNOB_ID)
        self.addCleanup(setattr, agent_http, "NO_REDIRECT_OPENER", old_opener)
        rt, _ = build_runtime("apply", server=OfflineHttpTransport(OFFLINE_URL, retries=0))
        journal = []
        rt.guard.journal = journal.append
        answer = triage.run(rt.ctx, {})["answer_text"]
        # platform did apply the knob move, its in Jig & Fixture Drawings and last changed by us
        knob = server.tables["FileAttachment"][KNOB_ID]
        self.assertEqual(knob["folder_id"], JIG_FOLDER_ID)
        self.assertEqual(knob["updated_by"], server.me["id"])
        knob_writes = [w for w in journal if w.get("id") == KNOB_ID]
        self.assertEqual(len(knob_writes), 1)
        self.assertIs(knob_writes[0]["uncertain"], True)
        self.assertEqual(journal, rt.guard.writes)
        failed_moves = _records(rt, "move", "failed")
        self.assertEqual([r.target_id for r in failed_moves], [KNOB_ID])
        self.assertEqual(failed_moves[0].details["write_sent"], "uncertain")
        self.assertTrue(failed_moves[0].details["error"].startswith("platform unreachable: POST /api/mcp failed: IncompleteRead"), msg=failed_moves[0].details["error"])
        self.assertIn("FAILED J-KNOB-09_RevA.dxf", answer)
        applied_moves = [r.target_id for r in _records(rt, "move", "applied")]
        self.assertCountEqual(applied_moves, [MILL_CERT_ID, PO_ID, W9_ID, TIMESHEET_ID])


class LiveWriteGateTests(unittest.TestCase):  # E1

    def test_live_no_journal_refused(self):
        # live transport: update and create refused till the harness attaches its journal
        client = RecordingClient({"FileAttachment.get": [_row_a()]})
        guard = _guard(client, live=True)
        with self.assertRaises(WriteBlocked) as update_refused:
            guard.update_file("a", {"folder_id": "HR"})
        with self.assertRaises(WriteBlocked) as create_refused:
            guard.create("AgentSession.create", {"title": "files-agent run"})
        self.assertEqual(str(update_refused.exception),
                         "live write without a write journal: update a not sent (run it through the harness)")
        self.assertEqual(str(create_refused.exception),
                         "live write without a write journal: AgentSession.create not sent (run it through the harness)")
        self.assertEqual(client.calls, [])
        self.assertEqual(guard.writes, [])
        self.assertEqual(_blocked_reasons(guard), ["no write journal", "no write journal"])

    def test_bad_target_label(self):
        # 'LIVE' and 'staging' refused before the transport is used so no label sneaks past the live checks
        for label in ("LIVE", "staging"):
            with self.subTest(label=label):
                proxy = TransportProxy(fake_server())
                with self.assertRaises(ValueError) as refused:
                    build("keystone", label, "apply", None, transport=proxy, settings=quiet_settings())
                self.assertEqual(str(refused.exception), f"target must be 'live' or 'fake', not {label!r}")
                self.assertEqual(proxy.requests, [])

    def test_label_transport_mismatch(self):
        # fake server labelled live + real transport labelled fake, both refused before any request
        proxy = TransportProxy(fake_server())
        with self.assertRaises(ValueError) as fake_called_live:
            build("keystone", "live", "plan", None, transport=fake_server(), settings=quiet_settings())
        with self.assertRaises(ValueError) as real_called_fake:
            build("keystone", "fake", "apply", None, transport=proxy, settings=quiet_settings())
        self.assertEqual(str(fake_called_live.exception), "target 'live' does not match the transport FakeServer")
        self.assertEqual(str(real_called_fake.exception), "target 'fake' does not match the transport TransportProxy")
        self.assertEqual(proxy.requests, [])


class UpdateFieldAllowListTests(unittest.TestCase):  # E2

    def test_id_in_changes_refused(self):
        # 'id' in changes could retarget the write to another file, refused and no update sent
        client = RecordingClient({"FileAttachment.get": [_row_a(folder_id="INC")]})
        guard = _guard(client)
        with self.assertRaises(WriteBlocked) as refused:
            guard.update_file("a", {"id": "outside-id", "folder_id": "HR"})
        self.assertEqual(str(refused.exception), "fields ['id'] may not be written by this agent")
        self.assertEqual(client.calls, ["FileAttachment.get"])
        self.assertEqual(guard.writes, [])
        blocked = guard.trace.of_kind("write_blocked")
        self.assertEqual([(e["reason"], e["file_id"], e["fields"]) for e in blocked], [("field not allowed", "a", ["id"])])

    def test_tags_refused(self):
        # tags isnt one of our 2 fields (folder, description, archived) so its refused unsent
        client = RecordingClient({"FileAttachment.get": [_row_a(folder_id="INC")]})
        guard = _guard(client)
        with self.assertRaises(WriteBlocked) as refused:
            guard.update_file("a", {"folder_id": "HR", "tags": "moved-by-agent"})
        self.assertEqual(str(refused.exception), "fields ['tags'] may not be written by this agent")
        self.assertEqual(client.calls, ["FileAttachment.get"])
        self.assertEqual(guard.writes, [])
        self.assertEqual(_blocked_reasons(guard), ["field not allowed"])


class WriteWindowTests(unittest.TestCase):  # T11

    def test_concurrent_change_returned(self):
        # tags we didnt send differ between pre-read and confirming read -> come back as concurrent_change
        before_our_write = _row_a(folder_id="INC", tags="untriaged")
        after_our_write = _row_a(folder_id="HR", tags="untriaged,on-hold")
        client = RecordingClient({"FileAttachment.get": [before_our_write, after_our_write]})
        guard = _guard(client)
        result = guard.update_file("a", {"folder_id": "HR"})
        expected_change = {"tags": {"before": "untriaged", "after": "untriaged,on-hold"}}
        self.assertEqual(result["concurrent_change"], expected_change)
        events = guard.trace.of_kind("concurrent_change")
        self.assertEqual([(e["file_id"], e["changed"]) for e in events], [("a", expected_change)])
        self.assertEqual(client.calls, ["FileAttachment.get", "FileAttachment.update", "FileAttachment.get"])

    def test_tidy_names_concurrent_change(self):
        # another team retags the W-9 while we move it, move applied but record + answer name the tags
        server = RetagServer.from_fixture("keystone", FIXTURE_DIR)
        rt, _ = build_runtime("apply", server=server)
        answer = triage.run(rt.ctx, {})["answer_text"]
        applied_moves = _records(rt, "move", "applied")
        w9_moves = [r for r in applied_moves if r.target_id == W9_ID]
        self.assertEqual(len(w9_moves), 1)
        self.assertEqual(w9_moves[0].details.get("concurrent_change"), ["tags"])
        w9_line = next(line for line in answer.splitlines() if f"({W9_ID})" in line)
        self.assertTrue(w9_line.endswith(TAGS_NOTE), msg=w9_line)
        events = rt.trace.of_kind("concurrent_change")
        self.assertEqual([(e["file_id"], e["changed"]) for e in events], [(W9_ID, {"tags": {"before": W9_TAGS, "after": THEIR_TAGS}})])
        self.assertEqual(len(applied_moves), 5)


if __name__ == "__main__":
    unittest.main()
