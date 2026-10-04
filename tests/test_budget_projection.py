# STRIDE D2 - spend and tool calls inside one model turn
# cap was only checked after a model call was paid for so a run could go over by a whole turn, and one reply could ask for any number of tool calls
import unittest
from agent.budget import Budget, BudgetExceeded
from agent.loop import run_agent
from helpers import build_runtime

CAP_USD = 0.10  # cap used here
TURN_INPUT_TOKENS = 10_000  # each priced reply bills 10k in ($0.03)...
TURN_OUTPUT_TOKENS = 2_000  # ...and 2k out ($0.03), so $0.06 a turn at default $3/$15 per million
MAX_REPLY_TOKENS = 4_096  # stand-in max_tokens, a full reply alone could be $0.06144
SMALL_REQUEST = 1_000  # short request ($0.003)
# hardcoded on purpose (not imported from loop.py) so bumping MAX_TOOL_USES_PER_TURN there breaks these
TOOL_USE_LIMIT = 10
N_READS = 11  # limit + 1
SKIPPED = "skipped: too many tool calls in one turn (limit 10); ask again in the next turn"
NO_USAGE = {"input_tokens": 0, "output_tokens": 0}


def _list_one(n):
    return {"type": "tool_use", "id": f"toolu_{n}", "name": "mcp__FileAttachment__list", "input": {"limit": 1}}


def _half_spent_budget():
    # $0.10 budget thats already paid for one $0.06 turn
    budget = Budget(max_turns=12, max_calls=80,max_usd=CAP_USD)
    budget.add_usage(TURN_INPUT_TOKENS, TURN_OUTPUT_TOKENS)
    return budget


class PricedModel:
    # fake anthropic model with a max_tokens, asks for one read every turn and bills $0.06 per turn
    max_tokens = MAX_REPLY_TOKENS

    def __init__(self):
        self.calls = 0

    def create(self, system, messages, tools):
        self.calls += 1
        return {"content": [_list_one(self.calls)], "stop_reason": "tool_use",
                "usage": {"input_tokens": TURN_INPUT_TOKENS, "output_tokens": TURN_OUTPUT_TOKENS}}


class ElevenReadsModel:
    # model steered by planted text, asks for 11 reads in its first reply then answers
    def __init__(self):
        self.calls = 0
        self.tool_results = []

    def create(self, system, messages, tools):
        self.calls += 1
        if self.calls == 1:
            uses = [_list_one(n) for n in range(1, N_READS + 1)]
            return {"content": uses, "stop_reason": "tool_use", "usage": NO_USAGE}
        self.tool_results = list(messages[-1]["content"])  # what the loop sent back for the 11
        return {"content": [{"type": "text", "text": "Done."}], "stop_reason": "end_turn", "usage": NO_USAGE}


class ProjectedSpendTests(unittest.TestCase):

    def test_call_over_cap_refused(self):
        # $0.06 of $0.10 spent, a call that could cost $0.06444 more is refused and nothing charged
        budget = _half_spent_budget()
        with self.assertRaises(BudgetExceeded) as caught:
            budget.check_projected(SMALL_REQUEST, MAX_REPLY_TOKENS)

        self.assertEqual(str(caught.exception), "spend cap would be passed by the next model call ($0.06 spent, up to $0.06 more, cap $0.10)")
        self.assertEqual(budget.usd, 0.06)

    def test_call_under_cap_ok(self):
        # $0.06 spent, call that costs at most $0.033 more goes ahead, nothing charged yet
        budget = _half_spent_budget()
        budget.check_projected(SMALL_REQUEST, TURN_OUTPUT_TOKENS)
        self.assertEqual(budget.usd, 0.06)

    def test_run_stops_before_cap(self):
        # first $0.06 turn paid, 2nd one (could reach $0.12) never sent so run ends under $0.10
        rt, _ = build_runtime("plan")
        rt.budget.max_usd = CAP_USD
        model = PricedModel()
        result = run_agent("List the files.", rt.ctx, model, rt.budget, rt.trace)
        self.assertEqual(model.calls, 1)
        self.assertEqual(rt.budget.usd, 0.06)
        self.assertEqual(result.aborted, "budget")
        # 'up to' amount depends on how big the request got, so just check the shape
        self.assertRegex(result.stop, r"^spend cap would be passed by the next model call "
                                      r"\(\$0\.06 spent, up to \$0\.\d\d more, cap \$0\.10\)$")


class ToolBurstTests(unittest.TestCase):

    def test_eleventh_call_skipped(self):
        # 11 reads in one reply - first 10 run and reach the platform, 11th is skipped
        rt, _ = build_runtime("plan")
        self.assertEqual(rt.budget.calls, 0)  # setup uses its own unbudgeted client
        model = ElevenReadsModel()
        result = run_agent("List the files.", rt.ctx, model, rt.budget, rt.trace)
        self.assertEqual([call["error"] for call in result.tool_calls], [False] * TOOL_USE_LIMIT + [True])
        self.assertEqual(rt.budget.calls, TOOL_USE_LIMIT)  # calls that actually reached the fake server
        # every tool_use still needs a tool_result (api requires it), the 11th says why it didnt run
        self.assertEqual(len(model.tool_results), N_READS)
        eleventh = model.tool_results[-1]
        self.assertEqual(eleventh["tool_use_id"], "toolu_11")
        self.assertEqual(eleventh["content"], SKIPPED)
        self.assertTrue(eleventh["is_error"])
        self.assertIsNone(result.aborted)


if __name__ == "__main__":
    unittest.main()
