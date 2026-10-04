# runaway model gets stopped by the turn cap, and running out of mcp calls aborts the run
import unittest

from agent.loop import run_agent
from agent.model import ScriptedModel
from helpers import build_runtime

MAX_MODEL_CALLS = 50  # fake model gives up after this many
TURN_CAP = 3
CALL_CAP = 2


class GreedyModel:
    # fake model, every answer asks for list_files again so it never finishes by itself

    def __init__(self):
        self.calls = 0

    def create(self, system, messages, tools):
        self.calls += 1
        if self.calls > MAX_MODEL_CALLS:
            # blow up instead of hanging if theres no turn cap at all
            raise RuntimeError(f"model called more than {MAX_MODEL_CALLS} times: the loop never stopped")
        block = {"type": "tool_use", "id": f"toolu_{self.calls}", "name": "list_files", "input": {}}
        return {"content": [block], "stop_reason": "tool_use", "usage": {"input_tokens": 0, "output_tokens": 0}}


class RunawayLoopTests(unittest.TestCase):  # BUDGET-2

    def test_turn_cap_stops_loop(self):
        # model always asking for a tool gets stopped after 3 turns, run says max_turns
        rt, _ = build_runtime("plan")
        rt.budget.max_turns = TURN_CAP
        model = GreedyModel()
        result = run_agent("List the files.", rt.ctx, model, rt.budget, rt.trace)
        self.assertEqual(result.aborted, "max_turns")
        self.assertEqual(result.turns, TURN_CAP)
        self.assertEqual(model.calls, TURN_CAP)

    def test_call_cap_aborts(self):
        # tidy with only 2 mcp calls left is aborted as budget with the call cap message
        rt, _ = build_runtime("plan")
        self.assertEqual(rt.budget.calls, 0)  # setup has its own unbudgeted client
        rt.budget.max_calls = CALL_CAP
        result = run_agent("Tidy the incoming folder.", rt.ctx, ScriptedModel(), rt.budget, rt.trace)
        self.assertEqual(result.aborted, "budget")
        self.assertEqual(result.stop, f"MCP call cap reached ({CALL_CAP})")


if __name__ == "__main__":
    unittest.main()
