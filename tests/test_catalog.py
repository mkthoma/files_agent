# tool catalogue check that preflight relies on
import copy
import unittest
from agent.catalog import Catalog
from harness import fixtures
from helpers import FIXTURE_DIR

TOOL_COUNT = 212  # tools this seat had in the 26 Sept capture
CATALOGUE_HASH = "c10a009a80de46c6"  # 26 Sept catalogue hash


class CatalogueTests(unittest.TestCase):  # MCP-4

    def setUp(self):
        self.tools = fixtures.load("keystone", FIXTURE_DIR)["tools"]

    def test_unchanged_catalogue(self):
        # 212 tools from 26 Sept pass, hash to c10a009a80de46c6, can list Item but not EsignDocument
        catalog = Catalog.from_tools(self.tools)
        self.assertEqual(len(self.tools), TOOL_COUNT)
        self.assertEqual(catalog.check_required(), [])
        self.assertEqual(catalog.hash(), CATALOGUE_HASH)
        self.assertTrue(catalog.can_list("Item"))
        self.assertFalse(catalog.can_list("EsignDocument"))

    def test_missing_tool(self):
        # no FileAttachment.update -> exactly 'missing tool FileAttachment.update'
        without_update = [tool for tool in self.tools if tool["name"] != "FileAttachment.update"]
        problems = Catalog.from_tools(without_update).check_required()
        self.assertEqual(problems, ["missing tool FileAttachment.update"])

    def test_new_required_arg(self):
        # AgentEscalation.create starts requiring 'priority' -> reported and the hash changes
        changed = copy.deepcopy(self.tools)
        escalation = next(tool for tool in changed if tool["name"] == "AgentEscalation.create")
        escalation["inputSchema"]["required"] = ["session_id", "reason", "priority"]
        catalog = Catalog.from_tools(changed)
        self.assertEqual(catalog.check_required(), ["AgentEscalation.create now requires ['priority']"])
        self.assertNotEqual(catalog.hash(), Catalog.from_tools(self.tools).hash())


if __name__ == "__main__":
    unittest.main()
