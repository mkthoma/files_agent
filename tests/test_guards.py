import unittest

from agent import snapshot
from agent.guards import StaleRow, WriteBlocked, WriteGuard, WriteNotConfirmed
from agent.mcp_client import McpError
from agent.redact import Redactor
from agent.trace import Trace


class StubMcp:
    def __init__(self):
        self.rows = {
            "f1": {"id": "f1", "folder_id": "A", "updated_at": "old",
                   "_permissions": {"write": True}, "_readonly_fields": ["is_trashed"]},
        }
        self.calls = []
        self.gets = 0
        self.fail_confirm = False
        self.clobber_confirm = False

    def call(self, tool, args):
        self.calls.append(tool)
        if tool == "FileAttachment.get":
            self.gets += 1
            row = dict(self.rows[args["id"]])
            if self.gets == 2 and self.fail_confirm:
                raise McpError("down")
            if self.gets == 2 and self.clobber_confirm:
                row["folder_id"] = "OTHER"
            return row
        if tool == "FileAttachment.update":
            row = self.rows[args["id"]]
            for key, value in args.items():
                if key != "id":
                    row[key] = value
            return {"id": args["id"]}
        raise AssertionError(tool)


def guard_for(stub, mode="apply"):
    return WriteGuard(stub, Trace(None, Redactor()), mode, frozenset({"f1"}))


class WriteGuardTest(unittest.TestCase):
    def test_plan_mode_sends_nothing(self):
        stub = StubMcp()
        with self.assertRaises(WriteBlocked):
            guard_for(stub, "plan").update_file("f1", {"folder_id": "B"})
        self.assertEqual(stub.calls, [])

    def test_id_outside_allowlist_is_blocked(self):
        stub = StubMcp()
        with self.assertRaises(WriteBlocked):
            guard_for(stub).update_file("f2", {"folder_id": "B"})
        self.assertEqual(stub.calls, [])

    def test_changed_row_is_skipped(self):
        stub = StubMcp()
        stub.rows["f1"]["updated_at"] = "new"
        with self.assertRaises(StaleRow) as ctx:
            guard_for(stub).update_file("f1", {"folder_id": "B"}, expect={"updated_at": "old"})
        self.assertEqual(stub.calls, ["FileAttachment.get"])
        self.assertEqual(ctx.exception.current["updated_at"], "new")

    def test_missing_permission_is_blocked(self):
        stub = StubMcp()
        stub.rows["f1"]["_permissions"] = {"write": False}
        with self.assertRaises(WriteBlocked):
            guard_for(stub).update_file("f1", {"folder_id": "B"})
        self.assertNotIn("FileAttachment.update", stub.calls)

    def test_readonly_field_is_blocked(self):
        stub = StubMcp()
        with self.assertRaises(WriteBlocked):
            guard_for(stub).update_file("f1", {"is_trashed": True})
        self.assertNotIn("FileAttachment.update", stub.calls)

    def test_failed_confirm_still_records_the_write(self):
        stub = StubMcp()
        stub.fail_confirm = True
        guard = guard_for(stub)
        with self.assertRaises(WriteNotConfirmed):
            guard.update_file("f1", {"folder_id": "B"})
        self.assertEqual(len(guard.writes), 1)

    def test_clobbered_write_is_not_confirmed(self):
        stub = StubMcp()
        stub.clobber_confirm = True
        with self.assertRaises(WriteNotConfirmed):
            guard_for(stub).update_file("f1", {"folder_id": "B"})

    def test_good_write_reads_writes_then_confirms(self):
        stub = StubMcp()
        result = guard_for(stub).update_file("f1", {"folder_id": "B"})
        self.assertIn("before", result)
        self.assertIn("after", result)
        self.assertEqual(stub.calls, ["FileAttachment.get", "FileAttachment.update", "FileAttachment.get"])


class PlanRestoreTest(unittest.TestCase):
    def test_our_change_is_put_back(self):
        snap = {"f1": {"folder_id": "A"}}
        current = {"f1": {"folder_id": "B"}}
        writes = [{"tool": "FileAttachment.update", "id": "f1", "changes": {"folder_id": "B"}}]
        todo, conflicts = snapshot.plan_restore(snap, current, writes, "me")
        self.assertEqual(todo, {"f1": {"folder_id": "A"}})
        self.assertEqual(conflicts, {})

    def test_another_team_change_is_left_alone(self):
        snap = {"f1": {"folder_id": "A"}}
        current = {"f1": {"folder_id": "C", "updated_by": "x"}}
        writes = [{"tool": "FileAttachment.update", "id": "f1", "changes": {"folder_id": "B"}}]
        todo, conflicts = snapshot.plan_restore(snap, current, writes, "me")
        self.assertEqual(todo, {})
        self.assertEqual(conflicts["f1"]["folder_id"], {"snapshot": "A", "now": "C", "updated_by": "x"})

    def test_no_journal_uses_last_writer(self):
        snap = {"f1": {"folder_id": "A"}}
        todo, _ = snapshot.plan_restore(snap, {"f1": {"folder_id": "B", "updated_by": "me"}}, None, "me")
        self.assertEqual(todo, {"f1": {"folder_id": "A"}})
        todo, conflicts = snapshot.plan_restore(snap, {"f1": {"folder_id": "B", "updated_by": "x"}}, None, "me")
        self.assertEqual(todo, {})
        self.assertIn("f1", conflicts)

    def test_snapshot_with_outside_id_is_refused(self):
        stub = StubMcp()
        with self.assertRaises(snapshot.RestoreRefused):
            snapshot.restore(stub, {"f9": {"folder_id": "A"}}, Trace(None, Redactor()), allowlist={"f1"})
        self.assertEqual(stub.calls, [])


if __name__ == "__main__":
    unittest.main()
