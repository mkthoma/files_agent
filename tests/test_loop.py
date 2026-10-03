# tests for agent loop + tools offered to model + final answer
import copy
import unittest

from agent.answer import cited_ids, compose
from agent.catalog import Catalog
from agent.config import WRITE_TOOLS
from agent.loop import run_agent, tool_definitions
from agent.records import DecisionRecord

from helpers import build_runtime

REV_C_ID = "2683b2c8-f700-4870-981c-1fb9c8d53393"  # J-BRKT-04_RevC_JigBracket.pdf
FAKE_ID = "00000000-0000-0000-0000-000000000001"  # doesnt exist anywhere
PO_1_ID = "82f83d94-5a46-4df3-9ee1-61e8b3c79d6e"  # PO_4471_ApexMetals_signed (1).pdf

SKILL_NAMES = ["drive_overview", "explain_access", "file_contents", "find_drawing", "find_duplicates", "list_files", "remove_file", "triage_folder"]
READ_ONLY_MCP_TOOLS = ["mcp__AgentEscalation__list", "mcp__DriveAccessLog__list", "mcp__DriveFolder__list", "mcp__FileAttachment__get", "mcp__FileAttachment__list", "mcp__Item__list", "mcp__Party__list", "mcp__tools__search"]


def _reply(content, stop_reason):
    return {"content": content, "stop_reason": stop_reason, "usage": {"input_tokens": 0, "output_tokens": 0}}


# fake model, first call asks find_drawing + triage_folder then just says done
class TwoToolsThenDoneModel:
    def __init__(self):
        self.calls = 0

    def create(self, system, messages, tools):
        self.calls += 1
        if self.calls == 1:
            return _reply([
                {"type": "tool_use", "id": "toolu_1", "name": "find_drawing", "input": {"part_code": "J-BRKT-04"}},
                {"type": "tool_use", "id": "toolu_2", "name": "triage_folder", "input": {"folder_name": "Incoming"}},
            ], "tool_use")
        return _reply([{"type": "text", "text": "done"}], "end_turn")


class AgentLoopTests(unittest.TestCase):  # LOOP-1

    def test_drawing_and_triage_same_turn(self):
        rt, server = build_runtime("plan")
        question = "Find the drawing for part J-BRKT-04, and tidy the incoming folder."

        result = run_agent(question, rt.ctx, TwoToolsThenDoneModel(), rt.budget, rt.trace)

        self.assertEqual([call["tool"] for call in result.tool_calls], ["find_drawing", "triage_folder"])
        current_drawings = [r["target_id"] for r in result.records if r["action"] == "current_drawing"]
        self.assertEqual(current_drawings, [REV_C_ID])
        planned_moves = [r for r in result.records if r["action"] == "plan_move"]
        self.assertEqual(len(planned_moves), 5)
        self.assertIn(REV_C_ID, result.cited_ids)
        self.assertIsNone(result.aborted)
        self.assertEqual(result.turns, 2)
        # plan mode so nothing should be written
        self.assertEqual(server.write_log, [])


class OfferedToolsTests(unittest.TestCase):  # LOOP-2

    def test_16_tools_offered(self):
        # 8 skills + 8 read only mcp tools
        rt, _ = build_runtime("plan")
        tools, _ = tool_definitions(rt.catalog)
        names = [tool["name"] for tool in tools]
        self.assertEqual(len(names), 16)
        self.assertCountEqual([n for n in names if not n.startswith("mcp__")], SKILL_NAMES)
        self.assertCountEqual([n for n in names if n.startswith("mcp__")], READ_ONLY_MCP_TOOLS)

    def test_no_write_tools_offered(self):
        # seat does have some write tools (DriveShare.share_file, AgentTask.create) but model shouldnt see any
        rt, _ = build_runtime("plan")

        tools, mapping = tool_definitions(rt.catalog)

        self.assertCountEqual(mapping, READ_ONLY_MCP_TOOLS)
        for platform_name in mapping.values():
            self.assertNotIn(platform_name, WRITE_TOOLS)
            self.assertTrue(rt.catalog.is_read_only(platform_name), msg=platform_name)
        names = [tool["name"] for tool in tools]
        for write_tool in ("mcp__DriveShare__share_file", "mcp__FileAttachment__update", "mcp__AgentTask__create"):
            self.assertNotIn(write_tool, names)
        self.assertIn("DriveShare.share_file", rt.catalog.names)
        self.assertIn("AgentTask.create", rt.catalog.names)

    def test_not_readonly_tool_dropped(self):
        # set readOnlyHint false on FileAttachment.list -> should get droped, 15 left
        rt, _ = build_runtime("plan")
        all_tools = copy.deepcopy(list(rt.catalog.tools.values()))
        self.assertEqual(len(all_tools), 212)
        file_list = next(tool for tool in all_tools if tool["name"] == "FileAttachment.list")
        file_list["annotations"]["readOnlyHint"] = False

        tools, _ = tool_definitions(Catalog.from_tools(all_tools))

        names = [tool["name"] for tool in tools]
        self.assertEqual(len(names), 15)
        self.assertNotIn("mcp__FileAttachment__list", names)


class ComposeAnswerTests(unittest.TestCase):  # ANSWER-1

    def setUp(self):
        self.records = [
            DecisionRecord(skill="s", action="current_drawing", status="info", target_id="id1", target_label="f"),
            DecisionRecord(skill="s", action="lookalike_part", status="info", target_id="id2", target_label="g"),
            DecisionRecord(skill="s", action="plan_move", status="planned", target_id="id3", target_label="h"),
        ]
        self.model_text = f"The current drawing is {REV_C_ID}. Also see {FAKE_ID}."

    def test_unverified_ids(self):
        # seen id is upper case here, should still count as seen. only fake id is unverified
        result = compose(self.model_text, self.records, {REV_C_ID.upper()})
        self.assertEqual(result["unverified_ids"], [FAKE_ID])

    def test_record_trail(self):
        result = compose(self.model_text, self.records, {REV_C_ID.upper()})

        # header changed in S4 fix, it has the count now
        trail = result["answer"].partition("Record trail (added by the agent code; 2 record(s)):\n")[2].splitlines()
        self.assertEqual(trail, ["- [info] current_drawing: f (id1)", "- [planned] plan_move: h (id3)"])
        # lookalike_part not suppose to show up
        self.assertNotIn("lookalike_part", result["answer"])

    def test_cited_ids_case(self):
        # same id in upper and lower case, should be cited once (lowercase)
        text = "A 82F83D94-5A46-4DF3-9EE1-61E8B3C79D6E b 82f83d94-5a46-4df3-9ee1-61e8b3c79d6e"
        self.assertEqual(cited_ids(text), [PO_1_ID])


if __name__ == "__main__":
    unittest.main()