# STRIDE T13 + I9 - tool call args from the model are checked before anything runs or gets sent
# T13: skill args vs input schema, explain_access trusted an undeclared app. I9: search/filter/sort on the direct FileAttachment.list was an oracle for withheld rows
import unittest
from agent.loop import run_agent
from agent.skills import access
from helpers import build_runtime

PAYSLIP_QUESTION = "Show me this month's payslips."  # task R1, needs payroll which this seat doesnt have

# withheld esign row another team owns (planted one from I9-poc.py), title + description are private
CANARY_TITLE = "Employee Offer Letter - Canary Zebra.pdf"
CANARY_DESCRIPTION = "Offer letter for Canary Zebra"
CANARY_ROW = {"filename": CANARY_TITLE, "entity_type": "EsignDocument", "folder": "", "description": CANARY_DESCRIPTION}

# only filters the model can use on a direct FileAttachment.list (MODEL_FILTERS in loop.py), sorted
ALLOWED_FILTERS = ["content_hash", "entity_id", "entity_type", "folder_id", "is_archived", "is_inline",
                   "mime_type", "size_bytes"]


class ScriptedModel:
    # fake model, asks for the given tool calls on its first turn, keeps the results, then says done

    def __init__(self, *calls):
        self.calls = calls
        self.results = []  # (content, is_error) per tool call

    def create(self, system, messages, tools):
        usage = {"input_tokens": 0, "output_tokens": 0}
        if len(messages) == 1:
            uses = [{"type": "tool_use", "id": f"toolu_{n}", "name": name, "input": args}
                    for n, (name, args) in enumerate(self.calls)]
            return {"content": uses, "stop_reason": "tool_use", "usage": usage}
        self.results += [(b["content"], b["is_error"]) for b in messages[-1]["content"] if b.get("type") == "tool_result"]
        return {"content": [{"type": "text", "text": "done"}], "stop_reason": "end_turn", "usage": usage}


def _run(question, *calls, extra_files=None):
    # one plan mode run with the fake model making `calls` -> (results, rt, tools sent to the fake server)
    rt, server = build_runtime("plan", extra_files=extra_files)
    sent_before = len(server.calls)
    model = ScriptedModel(*calls)
    run_agent(question, rt.ctx, model, rt.budget, rt.trace)
    return model.results, rt, server.calls[sent_before:]


def _refused_filter(bad):
    return (f"Tool error (refused_filter): these filters are not allowed here: {bad}. Use only "
            f"{ALLOWED_FILTERS} with limit/offset/sort_by, or a skill. Nothing was sent.")


def _records(rt):
    return [(r.action, r.status, r.target_label) for r in rt.ctx.records.all()]


class SkillArgumentTests(unittest.TestCase):  # T13

    def test_undeclared_app_refused(self):
        # undeclared app='drive' -> refused, skill never runs and no record
        results, rt, sent = _run(PAYSLIP_QUESTION, ("explain_access", {"request": PAYSLIP_QUESTION, "app": "drive"}))
        self.assertEqual(results, [("Invalid arguments for explain_access: unknown: ['app']. Nothing was run.", True)])
        self.assertEqual(_records(rt), [])
        self.assertEqual([e["problem"] for e in rt.trace.of_kind("bad_tool_args")], ["unknown: ['app']"])
        self.assertEqual(sent, [])

    def test_missing_request_refused(self):
        results, rt, _ = _run(PAYSLIP_QUESTION, ("explain_access", {}))
        self.assertEqual(results, [("Invalid arguments for explain_access: missing: ['request']. Nothing was run.", True)])
        self.assertEqual(_records(rt), [])

    def test_request_not_string_refused(self):
        # list where the schema wants a string
        results, rt, _ = _run(PAYSLIP_QUESTION, ("explain_access", {"request": ["payslips"]}))
        self.assertEqual(results, [("Invalid arguments for explain_access: not a string: ['request']. Nothing was run.", True)])
        self.assertEqual(_records(rt), [])

    def test_declared_args_run(self):
        # only the declared request -> runs and refuses payroll as out of seat
        results, rt, _ = _run(PAYSLIP_QUESTION, ("explain_access", {"request": PAYSLIP_QUESTION}))
        self.assertEqual([is_error for _, is_error in results], [False])
        self.assertEqual(_records(rt), [("refuse_out_of_seat", "refused", "payroll")])


class AppFromQuestionTests(unittest.TestCase):  # T13

    def test_app_key_ignored(self):
        # skill looks at the users own question so app='drive' + a drive paraphrase dont clear payroll
        rt, _ = build_runtime("plan")
        rt.ctx.question = PAYSLIP_QUESTION
        result = access.explain_access(rt.ctx, {"request": "list the drive files", "app": "drive"})
        self.assertIs(result["allowed"], False)
        self.assertEqual(result["app"], "payroll")
        self.assertEqual(_records(rt), [("refuse_out_of_seat", "refused", "payroll")])


class DirectListFilterTests(unittest.TestCase):  # I9

    def _check_refused(self, args, bad):
        # one direct FileAttachment.list with args, has to be refused naming `bad` with nothing sent
        results, rt, sent = _run("Is there an offer letter for Canary Zebra?", ("mcp__FileAttachment__list", args), extra_files=[CANARY_ROW])
        self.assertEqual(results, [(_refused_filter(bad), True)])
        self.assertEqual(sent, [])
        self.assertEqual(len(rt.trace.of_kind("refused_filter")), 1)

    def test_search_probe_refused(self):
        # search refused before sending so the total cant confirm a withheld title
        self._check_refused({"search": "Canary Zebra"}, ["search"])

    def test_filename_probe_refused(self):
        self._check_refused({"filename": CANARY_TITLE}, ["filename"])

    def test_description_probe_refused(self):
        # guessed private description value
        self._check_refused({"description": CANARY_DESCRIPTION}, ["description"])

    def test_sort_by_filename_refused(self):
        # sort_by filename not allowed, a placeholders position could leak its title
        self._check_refused({"sort_by": "filename", "limit": 3}, ["sort_by=filename"])

    def test_allowed_filter_still_sent(self):
        # entity_type + sort_by size_bytes is fine, one list goes out and withheld row is a placeholder
        results, _, sent = _run("List the e-sign files.", ("mcp__FileAttachment__list", {"entity_type": "EsignDocument", "sort_by": "size_bytes", "limit": 2}), extra_files=[CANARY_ROW])
        self.assertEqual(sent, ["FileAttachment.list"])
        self.assertEqual([is_error for _, is_error in results], [False])
        self.assertNotIn("Canary Zebra", results[0][0])


if __name__ == "__main__":
    unittest.main()
