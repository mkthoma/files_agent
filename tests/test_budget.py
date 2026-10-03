import unittest

from agent.budget import Budget, BudgetExceeded
from agent.guards import WriteGuard
from agent.redact import Redactor
from agent.trace import Trace


class StubMcp:
    def __init__(self, budget):
        self.budget = budget
        self.rows = {"f1": {"id": "f1", "folder_id": "A", "updated_at": "old",
                            "_permissions": {"write": True}, "_readonly_fields": []}}
        self.calls = []

    def call(self, tool, args):
        self.calls.append(tool)
        if tool == "FileAttachment.get":
            return dict(self.rows[args["id"]])
        if tool == "FileAttachment.update":
            return {"id": args["id"]}
        raise AssertionError(tool)


class BudgetTest(unittest.TestCase):
    def test_turn_cap(self):
        budget = Budget(max_turns=3, max_calls=10, max_usd=1.0)
        raised = False
        for _ in range(100):
            try:
                budget.add_turn()
            except BudgetExceeded:
                raised = True
                break
        self.assertTrue(raised)
        self.assertEqual(budget.turns, 4)

    def test_call_cap(self):
        budget = Budget(max_turns=9, max_calls=10, max_usd=1.0)
        for _ in range(10):
            budget.add_call()
        with self.assertRaises(BudgetExceeded):
            budget.add_call()

    def test_spend_cap(self):
        budget = Budget(max_turns=9, max_calls=10, max_usd=1.0)
        with self.assertRaises(BudgetExceeded):
            budget.add_usage(1_000_000, 0)

    def test_reserve_refuses_a_write_it_cannot_finish(self):
        budget = Budget(max_turns=9, max_calls=10, max_usd=1.0)
        budget.calls = 8
        with self.assertRaises(BudgetExceeded):
            budget.reserve(3)
        budget.calls = 7
        budget.reserve(3)

    def test_guard_checks_budget_before_sending_anything(self):
        stub = StubMcp(Budget(max_turns=9, max_calls=2, max_usd=1.0))
        guard = WriteGuard(stub, Trace(None, Redactor()), "apply", frozenset({"f1"}))
        with self.assertRaises(BudgetExceeded):
            guard.update_file("f1", {"folder_id": "B"})
        self.assertEqual(stub.calls, [])


if __name__ == "__main__":
    unittest.main()
