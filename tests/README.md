# tests/: the Phase 5 unit tests

This guide tells you how to run the tests and what each test file checks. It also tells you how to prove that a test finds a bug, and what is not tested yet. The guide holds no test code. It was last updated on 4 Oct 2026, after the decision C tests.

NOTE: The brief says *"a test written by Claude or Codex scores zero"*. Each hand-written test gives 10 points. Write each test file by hand. Commit it yourselves. Your commit history is the evidence.

## Run the tests

Run this command from the repository root. It uses only the Python standard library, so you do not install anything.

```bash
python -m unittest discover -s tests -v
```

The last lines of the output must be these lines. The time changes from run to run.

```text
----------------------------------------------------------------------
Ran 296 tests in 12.163s

OK
```

On 4 Oct 2026, the suite gave this result three times in a row, with Python 3.14.4. One run takes approximately 12 seconds.

The tests are offline. They use the fake server that the harness makes from the captured fixture, or small stand-ins. They never use the live platform, the model or an outside network. `test_http_transport.py` opens two local servers on 127.0.0.1. `test_cli_live_flags.py` and `test_secrets.py` start a harness command or `scripts/secret_scan.py` as a separate process. `test_secrets.py` writes a scratch file under `runs/` and deletes it at the end. `test_runner.py` also starts harness commands as a separate process. It writes a run set under `runs/` and deletes it at the end.

Staff question Q3 asks if `pytest` is permitted. Until the staff answer, the tests use `unittest`.

### The fixture data in the tests

The tests compare results with numbers from a captured fixture. These numbers include 5 moves, 13 escalations, 9 warnings, 212 tools, 113 rows, 30 files in folders and the Drive overview's 15. Most test files use `tests/helpers.py`, which pins `harness/fixtures/keystone/2026-09-26`. `test_decisions.py`, `test_duplicates.py` and `test_triage.py` load the newest folder under `harness/fixtures/keystone/`. Today the newest folder is `2026-09-26`, so all files use the same data.

CAUTION: The live write run needs a fresh capture, less than 24 hours before the run. That capture becomes the newest fixture. If you do not move the pin, most test files continue to check the 26 Sept data.

After each new capture, do these steps:

1. Move the pin in `tests/helpers.py` to the new folder.
2. Run the tests.
3. Change each number that changed in the new data.
4. Run the tests again.
5. Commit all of these changes in one commit.

## Test files

There are 48 test files with 296 tests. The table gives each file, its number of tests and what the tests check.

| File | Tests | What the tests check |
|---|---|---|
| `test_access.py` | 5 | The agent refuses a payroll request and allows a drive request. The word "design" alone is not an app. The agent refuses a name that two files share, and it does not guess an unknown name. |
| `test_answer_trail.py` | 5 | The code always adds its own record trail last, with its count, also when the model writes a false trail. With no records, the trail says `none`. |
| `test_budget.py` | 5 | The turn, call and spend caps stop a run. `reserve` refuses a write that the run cannot complete. The write guard checks the budget before it sends a write. |
| `test_budget_projection.py` | 4 | `check_projected` refuses a model call that can go past the spend cap. The loop does not run the 11th tool call of one model turn. |
| `test_budget_stops.py` | 2 | A model that always asks for a tool stops at the turn cap. A tidy with too few MCP calls stops with the call cap message. |
| `test_catalog.py` | 3 | The 26 Sept catalogue has 212 tools and no problem. A removed tool is a problem. A new required argument is a problem and changes the hash. |
| `test_cli_live_flags.py` | 2 | `harness run` and `harness restore` with `--live-apply` but without `--target live` stop with exit code 3. They write and restore nothing. |
| `test_config.py` | 4 | The `.env` parser strips quotes and skips comments and bad lines. A live apply needs Keystone, apply mode and `AS_ALLOW_WRITES` from the shell, not from `.env`. |
| `test_config_amounts.py` | 5 | An `AS_MAX_USD` of `nan`, `inf` or `-1`, or a price of `0`, causes a `ValueError`. A cap of `0.50` loads. |
| `test_decisions.py` | 12 | A live-capped tidy writes only to the 9 allow-listed files (decision A). The file also checks 5 pre-flight cases, 1 same-name case (decision B) and 5 ambiguity cases. |
| `test_duplicates.py` | 5 | A hash that different files share is not trusted, so the group uses name and size. The plain name is the original. The answer never says "byte-verified". |
| `test_duplicates_trust.py` | 2 | On the 26 Sept data, all 14 shared hashes are untrusted. The two PO pairs are the only duplicate groups, and both are only suspected. |
| `test_escalate.py` | 11 | Of two files with one name, the agent files only the file with the higher score. A tie stops both files (decision B). A trusted copy stays in Incoming with one escalation (decision C). The file also checks the live cap, plan mode and a second tidy. |
| `test_escalate_ownership.py` | 6 | An escalation with our subject from another seat, or with no creator, does not stop ours. The tidy records an escalation that errors after it lands as failed, and never sends it again. |
| `test_fake_server.py` | 2 | A one-shot fault fires one time only. A disarmed server does not fire it. |
| `test_find_drawing.py` | 14 | J-BRKT-04 resolves to RevC, and KJ-BRKT-04 is a different part. The file also checks unknown and shared part codes, revision spellings, and 4 cases with no current drawing. |
| `test_fixtures.py` | 7 | A fixture with one changed value or a false tool hash does not load. A folder name that is not a date, or a future date, is never the baseline. Live pre-flight refuses a fixture older than 24 hours. |
| `test_folders.py` | 3 | When two live folders share the name HR (`HR` and ` hr`), `folder_named` finds no folder. The tidy moves nothing there, and pre-flight reports the two folders. |
| `test_guards.py` | 12 | The file checks 8 write guard cases: plan mode, allow-list, permission, read-only field, changed row, failed confirm, overwritten write and the good path. It also checks 4 restore cases. |
| `test_http_transport.py` | 3 | `HttpTransport` refuses a base URL that is not `https://`. It does not follow a 302 redirect, so the token does not go to the other host. |
| `test_loop.py` | 7 | Two `tool_use` blocks in one reply run both skills in one turn. The model gets 8 skills and 8 read-only tools, and no write tool. `compose` flags an id that no tool showed. |
| `test_loop_args.py` | 10 | A skill call with an undeclared, absent or wrong-type argument does not run. A direct `FileAttachment.list` with `search`, `filename`, `description` or `sort_by=filename` sends nothing. |
| `test_mcp_client.py` | 8 | The client raises `McpError` for an error inside HTTP 200, a bare-string error, HTTP 500, a non-JSON reply and `isError`. One `401` causes one new login only. |
| `test_mcp_client_stride.py` | 9 | The client refuses a tool that is not read-only and not one of the 3 write tools. Platform error text that can quote a record never gets to the model, the records or the trace. |
| `test_overview.py` | 1 | The Drive overview says 15 files, but 30 of 113 rows are in folders. The answer reports this contradiction. |
| `test_preflight_catalogue.py` | 4 | Pre-flight finds a changed description or read-only mark on a tool that the agent uses. The model never gets the platform's tool text, and `tools.search` shows only names. |
| `test_privacy.py` | 7 | An e-sign row becomes a placeholder that keeps its id, size and folder. The title of a planted canary row never gets to the model. |
| `test_privacy_fields.py` | 4 | A withheld row keeps values only in `KEEP_FIELDS`. A new field, a display field or `thumbnail_path` that holds the real title becomes `None`. |
| `test_records.py` | 2 | `DecisionRecord` refuses an unknown status or confidence. A record stays the same after a round trip to a dict. |
| `test_redact.py` | 4 | A login and a call leave no password or token on disk or in memory. The redactor masks sensitive keys, whatever the value. Short strings are not secrets. |
| `test_restore.py` | 2 | A tidy, then a restore, on the fake server leaves no difference. A restore continues after one row fails, and reports that row. |
| `test_restore_stride.py` | 6 | Restore refuses a bad snapshot or journal before it makes a call. Without a journal, it writes only our fields. It keeps a description that another team changed before our write. `harness restore` refuses to run without `writes-1.json`, unless you give `--no-journal`. |
| `test_revisions.py` | 8 | Letter and number revisions sort correctly (`AA > Z`, `Rev10 > Rev2`). Mixed schemes give no newest revision. The parser flags several markers and a confusable `O`, and `KJ-` is not the `J` prefix. |
| `test_runner.py` | 13 | The file checks the `live_write` rules, `planned_runs`, pre-flight warnings, failed and half-written run files, `score`, `rescore` and calibration on a D1 run. |
| `test_runner_rerun.py` | 4 | A live TI2L attempt that can have sent a write stops a new live TI2L run in any run set. An earlier attempt that sent nothing moves to `attempt-<time>/`. |
| `test_safe_reads.py` | 4 | `list_all` reads all pages of 1,200 rows. Only safe filters get to the server, `not_equal` keeps empty values, and a filename never matches as a substring. |
| `test_safe_reads_paging.py` | 4 | `list_all` stops with `no_progress` when the server ignores `offset`, and with `bad_reply` on a bad page. It ignores a bad `total` and stops after 200 pages. |
| `test_secrets.py` | 6 | The `repr()` of the settings and the runtime, and a traceback with locals, show no secret. The redactor masks encoded secrets. `secret_scan.py --also` finds a planted canary. |
| `test_task_ids.py` | 6 | The loader refuses a task id that differs from its file name, holds `..`, repeats another id or differs only in case. It also refuses `live_write = "false"` and `passes = 0`. |
| `test_tasks_loader.py` | 5 | The loader refuses an unknown `[expect]` key, a bad mode, a second `live_write` task and a `live_write` task with no `live_allowlist`. A good file loads. |
| `test_textsafe.py` | 15 | `printable`, `one_line` and `md_cell` remove terminal escapes and invisible characters, and escape Markdown. Names that other teams control get to escalations, notes, reports and the model as one clean line. |
| `test_triage.py` | 8 | The mill cert moves to Quality and the timesheet to HR. If the evidence is weak or does not agree, the agent files nothing. A second tidy writes nothing and finds its escalations already made. |
| `test_triage_evidence.py` | 9 | One row of a kind does not decide a folder, but two rows do. A provenance note counts as our own work only on a row that our seat changed. |
| `test_triage_scoring.py` | 18 | The file checks `_score` and the evidence from similar files. It also checks the plan for all 18 Incoming items, the planted W-9, the note after a move and archived files. |
| `test_verifiers.py` | 7 | Each of 7 verifier checks fails on a broken run and passes on a fixed run. |
| `test_verifiers_rules.py` | 1 | The `writes` check fails when a read-only task makes a write call. |
| `test_write_guard.py` | 2 | When an update gets an error reply, the tidy records the write as `uncertain`, never as not sent. The tidy then makes the other 4 moves. |
| `test_write_guard_stride.py` | 10 | A cut-off reply or Ctrl-C goes in the journal as `uncertain`. The guard refuses a live write with no journal, and an `id` or `tags` change. `build` refuses a bad target label. If another team changes a field that we did not send, the write records `concurrent_change`, and the answer names it (T11). |
| `helpers.py` | — | This file is not a test file. Refer to [Shared helpers](#shared-helpers). |
| **48 files** | **296** | |

## Prove that a test finds a bug

A test is good only if it fails when the code is wrong. Do this check for each new test.

CAUTION: Do the check in a scratch copy of the repository. Do not change the code in the working tree that you commit from.

1. Make a scratch copy of the repository.
2. In the scratch copy, make one change that breaks the behaviour that the test checks.
3. Run the tests. Make sure that the test fails.
4. Undo the change.
5. Run the tests again. Make sure that all tests pass.
6. Delete the scratch copy.

Make only one change at a time.

### Changes that make a test fail

Each change in this table made at least one test in the given file fail. The review of PR #4 did the checks for T5.1 to T5.10, on the code of PR #4. The other checks are from 4 Oct 2026, in a scratch copy with all 48 test files.

| Id | Change to the code | File with a test that fails |
|---|---|---|
| T5.1 | Sort revisions as plain text. | `test_revisions.py` |
| T5.2 | Let a description alone choose the folder. | `test_triage.py` |
| T5.3 | Trust a hash that many files share. | `test_duplicates.py` |
| T5.4 | Allow every id. | `test_guards.py` |
| T5.5 | Treat HTTP 200 as success, with no check for an error inside. | `test_mcp_client.py` |
| T5.6 | Send `ne:` to the server. | `test_safe_reads.py` |
| T5.7 | Make a verifier always return ok. | `test_verifiers.py` |
| T5.8 | Skip the "already escalated?" check. | `test_triage.py` |
| T5.9 | Turn redaction off. | `test_redact.py` |
| T5.10 | Remove the cap. | `test_budget.py` |
| DUPC-2 | In `_plan_item` (`agent/skills/triage.py`), `return item` instead of `_hold_as_copy_match(...)`. | `test_escalate.py` and others |
| DUPC-6 | In `agent/skills/escalate.py`, change `if subject in existing:` to `if False:`. | `test_escalate.py`, `test_triage.py` |
| S2 | Remove `"Cf"` from `_DROP_CATEGORIES` (`agent/textsafe.py`). | `test_textsafe.py` |
| S4 | Put the record trail before the model's text in `compose` (`agent/answer.py`). | `test_answer_trail.py`, `test_textsafe.py` |
| S5 | Make `_NoRedirect.redirect_request` follow the redirect. | `test_http_transport.py` |
| S3 | Remove the `args.live_apply and args.target != "live"` check in `cmd_run`, or in `cmd_restore`. | `test_cli_live_flags.py` |
| S1 | Remove the `row.get("created_by") == me` test in `Escalator._load`. | `test_escalate_ownership.py` |
| T3 | Remove the `subject in self._uncertain` check in `agent/skills/escalate.py`. | `test_escalate_ownership.py` |
| T1 | Catch only `McpError` in `WriteGuard._send`. | `test_write_guard_stride.py` |
| E1 | Remove `if self.live and self.journal is None` (`agent/guards.py`). | `test_write_guard_stride.py` |
| E2 | Remove the `extra` check in `update_file`. | `test_write_guard_stride.py` |
| E3 | Remove the check at the top of `McpClient.call`. | `test_mcp_client_stride.py` |
| T4 | Let `folder_named` return the first match. | `test_folders.py` |
| T6 | Skip the `RESTORE_FIELDS` check in `plan_restore`. | `test_restore_stride.py` |
| T9 | Restore the snapshot value instead of the text before our note. | `test_restore_stride.py` |
| T11 | Remove the `concurrent_change` comparison in `update_file`. | `test_write_guard_stride.py` |
| T7 | Set `MIN_AGREEING_ROWS = 1`, or make `agent_filed` check only the note. | `test_triage_evidence.py` |
| T8 | Skip `_verify` in `harness/fixtures.py`, or set `FIXTURE_MAX_AGE` to a year. | `test_fixtures.py` |
| T10 | Remove the `text_hash()` comparison in `harness/preflight.py`. | `test_preflight_catalogue.py` |
| T13 | Make `_bad_args` (`agent/loop.py`) return `""`. | `test_loop_args.py` |
| T14 | Skip the id check in `load_task` (`harness/tasks.py`). | `test_task_ids.py` |
| I1 | Keep every field except `PRIVATE_FIELDS` in `sanitise_file` (the old block-list). | `test_privacy_fields.py` |
| I9 | Make `_refused_args` (`agent/loop.py`) return `""`. | `test_loop_args.py` |
| I12 | Make `safe_error_text` (`agent/mcp_client.py`) return `str(err)`. | `test_mcp_client_stride.py`, `test_write_guard.py`, `test_escalate_ownership.py` |
| I4 | Show the password and the model key in the `repr` of the settings (`agent/config.py`). | `test_secrets.py` |
| D8 | Remove the `if not fresh` check in `agent/safe_reads.py`. | `test_safe_reads_paging.py` |
| D2 | Remove the `check_projected` call, or raise `MAX_TOOL_USES_PER_TURN`. | `test_budget_projection.py` |
| D10 | Remove the `math.isfinite` check in `_amount` (`agent/config.py`). | `test_config_amounts.py` |
| R1 | Make `refuse_live_rerun` return at once. | `test_runner_rerun.py` |
| I11 | Remove `"runs"` from `SCAN_DIRS` (`scripts/secret_scan.py`). | `test_secrets.py` |
| CONFIG-2 | In `get_settings`, read `AS_ALLOW_WRITES` only from an injected `env`, never from the shell. | `test_runner_rerun.py`, `test_runner.py` |

On 3 Oct 2026, three more checks made a test fail:

- Score a half-written run file as a pass (`test_runner.py`, two tests).
- Give the model the raw row instead of the placeholder (`test_privacy.py`).
- Let two parts that share an exact code pick the first match (`test_find_drawing.py`).

These test files have no targeted check yet: `test_access.py`, `test_budget_stops.py`, `test_catalog.py`, `test_config.py`, `test_duplicates_trust.py`, `test_fake_server.py`, `test_loop.py`, `test_overview.py`, `test_records.py`, `test_restore.py`, `test_tasks_loader.py`, `test_triage_scoring.py` and `test_verifiers_rules.py`. `test_find_drawing.py` and `test_privacy.py` have one check each. Do the check for each test in these files.

## What is not tested yet

This section compares the planned scenarios and the STRIDE list with the 48 test files. It keeps only the items that no test covers, or that a test covers only in part. The ids are labels from the team's unit-test scenario list. The team keeps that list with the project docs, outside this repository. **†** marks behaviour that comes from the STRIDE fixes.

For each item, write the test by hand. Then do the check in [Prove that a test finds a bug](#prove-that-a-test-finds-a-bug).

### Gaps from the review of PR #4

Both gaps are still open. On 4 Oct 2026, all 296 tests passed with each change below, in a scratch copy. Each half of the second change got its own run.

| Behaviour to test | Change that must make the test fail |
|---|---|
| Pre-flight: a fixture row that relates to one of the 9 is still a problem after someone gives it an unrelated name. An example is a mill cert outside Incoming. | In `_outside_incoming` (`harness/preflight.py`), judge only the live row: remove `or (base is not None and related(base))`. |
| An allow-listed file that is not in Incoming now is not writable. Pre-flight reports it (`allow-listed file(s) missing from Incoming`). | In `_allowlist` (`agent/runtime.py`), return the 9 ids without `ids &`. Or remove the `missing` check in `assess` (`harness/preflight.py`). |

<a id="decision-c-scenarios-12-not-covered-yet"></a>

### Decision C scenarios that are still open

Decision C (4 Oct 2026) changed the duplicate rule. The agent never writes to a file because the file looks like a copy of another file. A possible copy has the same recorded hash, size and name as another file, or the same name and size. It stays where it is, and the agent does not archive it. The agent makes one escalation that names the other file's id, its folder and its destination in this run. The rule is in [triage step 3](../docs/architecture.md#triage_folder-evidence-scored-filing).

These scenarios replace FOLLOW-1 and FOLLOW-2. Tests now cover these scenarios:

- DUPC-2: `PossibleCopyTests` in `test_escalate.py`. No test checks yet that the reason does not say "delete rights".
- DUPC-6: `RunTwiceTests` in `test_escalate.py` and `SecondTidyTest` in `test_triage.py`. In the second tidy, the escalations of the two possible copies on the 26 Sept data (`82f83d94…` and `c0c8b9c0…`) are `already_escalated`.
- DUPC-7 (i): `test_renamed_party_in_escalation` in `test_textsafe.py`. It compares the full escalation text of `82f83d94…`.

Ids 7a…41, 7b…41, 7c…42 and 7d…42 are the explicit `id` values in [`harness/tasks/TI7.toml`](../harness/tasks/TI7.toml). An `extra_files` entry can have its own `id`, so two planted files can have the same name.

NOTE: The `return item` change makes many tests fail already, because the 26 Sept data has two possible copies. A new DUPC test must also fail with it.

| Id | Scenario | What to assert | Change that must make the test fail |
|---|---|---|---|
| DUPC-1 | `WEEK40_FILES`, but give the copy a sender too. Call `build_plan` on Incoming. | The copy is `escalate`, with no destination and the basis "recorded hash + size + name". Its `original_id` is a9095b10, and it has a `recorded_duplicate` clue. Its `missing[0]` holds a9095b10, "in Incoming", "which this run plans to file in HR" and "recorded metadata any seat can edit". The original is a move to HR. No item is a `duplicate`. | In `_plan_item` (`agent/skills/triage.py`), `return item` instead of `_hold_as_copy_match(...)`. |
| DUPC-3 | Two `timesheet_week41.xlsx` extras, ids 7a…41 and 7b…41, both with a sender, one hash and one size. Apply mode. | HR holds exactly one row with that name (7a). 7b is in Incoming, not archived, with one escalation. | `return item`: both files tie, so the agent does not file 7a either. |
| DUPC-4 | A decoy `timesheet_week44.xlsx` in Superseded with no sender. `timesheet_week44 (1).xlsx` in Incoming **with** a sender. Without a sender, the change shows nothing. | The Incoming file stays in Incoming, not archived, with no update. The decoy does not change. The plan text names the decoy's id and "in Superseded". There is one escalation. | `return item`: the agent files the Incoming file to HR. |
| DUPC-5 | 7c…42 is already in HR. A file with the same name, 7d…42, with a sender, is in Incoming. Apply mode. | 7d stays in Incoming, not archived. HR holds one row with that name. The escalation names 7c, "in HR" and the basis, and does not say "plans to file". Decision B also holds the file when the duplicate rule is off, so only the text checks find this change. | In `_ask_to_compare`, use the folder of the copy instead of the folder of the other file. |
| DUPC-7 (ii) | A live-capped apply tidy, with c0c8b9c0 and 3dd05bfb deleted from the fake server. | The basis is "recorded hash + size + name". 82f83d94 stays in Incoming, not archived, with one escalation. | `return item`: the agent files the file to Purchasing. |
| GUARD-ARCH | Apply mode: `guard.update_file(1ee27946…, {"is_archived": True})`. | It raises `WriteBlocked`, which names `is_archived`. Nothing goes to the server. | Add `is_archived` back to `UPDATE_FIELDS` (`agent/guards.py`). |
| RESTORE-ARCH | `snapshot.check_inputs` with a journal update entry whose changes are `{"is_archived": True}`. | It raises `RestoreRefused` with "holds is_archived" (an entry from before decision C) and "nothing restored". No call goes out. | In `_journal_problem` (`agent/snapshot.py`), remove the branch that returns `PRE_DECISION_C`. |
| FAKE-ID | `FakeServer.from_fixture` with planted extras. | Two extras with one name and no `id` raise `ValueError`, which names the file. An `id` equal to the id of a fixture row also raises. Two different ids give two rows. | Remove the id-in-table check in `_add_file` (`harness/fake_server.py`). |
| TASK-ID | `load_task` on a temporary TOML file. | Two extras with the same name, or one explicit `id` two times, raise `ValueError`. The message starts with the task file name and names both files. Different ids load. | Remove `_extra_file_problems` from `load_task` (`harness/tasks.py`). |
| VERIFY-UNCHANGED | `expect = {"unchanged": [F1]}` when F1 is not in the before-state. | The `unchanged` check fails with "not in the before-state". When F1 is in the before-state and does not change, the check passes. | Remove the before-state check in `_state_checks` (`harness/verifiers.py`). |

### Unit scenarios that are covered only in part

A test covers part of each scenario. The second column gives the part that no test covers yet.

| Id | Part that is not covered yet |
|---|---|
| REV-1 | A lower-case name (`j-brkt-04_revc_jigbracket.pdf`) still reads as C. The raw value. `KPL-PMP-BASE-Rev2.pdf` reads as `2`, with ordinal 2. |
| REV-2 | `newest([])` gives no newest revision and no problems. |
| FD-1 | The answer sentence that names KJ-BRKT-04 as a different part. The tests assert only the `lookalikes` list and the target id of the `lookalike_part` record. If you delete that sentence from `_summary`, all tests pass. |
| DUP-1 | A name-only difference (same size) and a size-only difference (same name), as two cases. A row with no hash. |
| DUP-4 | Exactly 2 "not byte-verified". The line `14 content hash value(s) are shared`. An apply run writes nothing. The Quality folder has no duplicates. |
| SCORE-4 † | The `own_ids` branch of `agent_filed` (this run's journal). A real second tidy pass, in which the files of the first pass are not evidence. |
| ACCESS-2 | "Delete <id>." in apply mode writes nothing. The answer has `can't delete` and `_permissions.delete = False`. An upper-case id finds the same file. |
| ACCESS-3 | The text "duplicate of <id>" resolves to no file. |
| PRIV-4 † | An access-log row whose free text holds the title, or a row with `file_id` null. This test shows that the I5 fix drops `details`. |
| READS-1 | The `gt:` and `lt:` prefixes and an unlisted filter never get to the server. There is exactly one call, with `limit` 500 and `offset` 0. |
| READS-2 | A positive filtered result: the rows in one folder stay after the second filter. |
| READS-3 | A row with no key. On the fixture, 107 of 113 rows have no link to an Item. |
| MCP-1 | The last event of the trace is an `mcp_call` with `ok` false. |
| MCP-2 | The `http401_once` fault of the fake server through `rt.mcp`: one new login, then success. |
| MCP-3 † | `HttpTransport` sends a safe call again after a 503. It sends a write again only after a 429, and never after a timeout. |
| GUARD-1 | `guard.create()` in plan mode too. "plan-only mode" in both messages. Two `write_blocked` events with the reason plan-only. |
| GUARD-2 | The message "not in the write allow-list", and the `write_blocked` reason "not allow-listed". |
| GUARD-3 | The exact messages, exactly one get, and nothing in `guard.writes`. |
| GUARD-4 † | The journal entry of a write that lands, or of a write whose check read fails, has no `uncertain` key. |
| GUARD-5 | At triage level, with the `moved_row` fault: a `skip_changed` record, "SKIPPED W9…" in the answer, the W-9 stays in HR, and exactly 4 updates. |
| GUARD-6 | At triage level, with `clobber_after_write`: a failed move with `write_sent` true, "FAILED W9…" in the answer, and the timesheet still moves. |
| RESTORE-1 | Another team's change to a field that we never wrote (tags) is a conflict. A mixed row: restore returns the description to its old value, and the folder is in conflict. `is_archived` 0 and False are the same. |
| CONFIG-1 | The other line forms of `load_env`. These are an `export KEY=VALUE` prefix, a UTF-8 BOM on the first key, a value in double quotes, and a ` # comment` at the end. A `.env` that does not exist, so only the shell's `AS_*` and `ANTHROPIC_*` keys come back. |
| BUDGET-1 † | The exact turn cap, spend cap and `reserve` messages. `reserve` does not change the call count. |
| LOOP-1 | A two-part request that the router really sends to both skills. The stand-in model gives two `tool_use` blocks itself, and `ScriptedModel` gives one. So no test shows that the router splits a request. |
| REDACT-1 | The redactor masks a token in a list of dicts. |
| REDACT-2 | A real fake-server login and an `McpClient` call. The redactor masks the bare token in a debug line, and the login is `ok`. |
| HARNESS-7 † | The blinded-verifier half. No test makes calibration report a MISSED row: an expectation key with no mutant, or a verifier that always returns ok. Calibration runs only on one baseline D1 run, not on several tasks. |
| VERIFY-2 | A get from an earlier pass does not count for an update in the next pass (`pass_start` resets it). |
| VERIFY-3 | The verifier ignores another team's change, with "foreign changes ignored" in the detail. |
| VERIFY-4 | The record trail that the code adds does not count as the model's answer. An upper-case citation still counts. |
| VERIFY-5 † | A refused delete attempt (`ok` false) still fails `write_tools_allowed`. A failed update of a permitted tool does not break the rule (STRIDE R4). |
| FAKE-1 | The other three one-shot faults: `moved_row`, `foreign_change` and `clobber_after_write`. A fault that the server skips while disarmed stays available, and fires when `armed` is True again. |

### STRIDE fixes

Each fix has a `# STRIDE <id>` comment in the code. The report is [`docs/security/stride-review.md`](../docs/security/stride-review.md). Each of the 28 STRIDE checks that this guide listed before now has a test. The table in [Changes that make a test fail](#changes-that-make-a-test-fail) gives the change and the file for each one.

These STRIDE items are still open:

- R4: refer to VERIFY-5 above.
- I5: refer to PRIV-4 above, the access-log part.
- The part of T6 for a journal entry that holds `is_archived`: refer to RESTORE-ARCH above.
- The other rows with **†** above: SCORE-4, MCP-3, GUARD-4, BUDGET-1 and HARNESS-7.

## Shared helpers

`tests/helpers.py` is not a test file. Many test files import it.

| Name | What it does |
|---|---|
| `REPO_ROOT` | The root folder of the repository. |
| `FIXTURE_DIR` | The pinned fixture folder, `harness/fixtures/keystone/2026-09-26`. Without this pin, the fake server loads the newest capture. |
| `quiet_settings(**env)` | Settings that use only the values that you give. They ignore the shell and `.env`. |
| `fake_server(faults, extra_files)` | A new fake server on the pinned fixture, with optional faults and planted rows. Make a new one for each test. |
| `build_runtime(mode, server, faults, extra_files, live_allowlist, settings)` | A runtime on a fake server. It disarms the server during the build, then arms it, so the one-shot faults stay for the test. It returns the runtime and the server. |
| `offline_env(**extra)` | The environment for a command-line test. It removes the real credentials and sends all proxy traffic to 127.0.0.1:9. |
| `run_cli(*args, env, cwd, timeout)` | Runs `python -m <args>` from the repository root and returns the result. |
| `new_set_name(label)` | A unique run set name that starts with `test-`. |
| `remove_run_set(name, repo)` | Deletes a run set under `runs/`. Use it with `addCleanup`, so a test leaves nothing behind. |

### Other building blocks in the code

- Offline server: `harness.fake_server.FakeServer.from_fixture` gives a full fake platform with the captured data.
- Runtime: `agent.runtime.build` returns `rt.ctx`, `rt.guard`, `rt.mcp` and `rt.budget`, all connected.
- Faults: the docstring of `harness/fake_server.py` lists them (`moved_row`, `http401_once`, `error_in_200`, `planted_description`, `swap_archived` and more). A one-shot fault fires only while `server.armed` is True. `agent.runtime.build` makes its own calls, which can use up a fault. Thus, use `build_runtime`. As an alternative, disarm the server before the build. Then arm it after the build.
- Canary: an extra file with the name `Offer Letter - Canary.pdf`, the entity type `EsignDocument` and no folder. This seat must never show it.
- Restore without a platform: `agent.snapshot.plan_restore(snapshot, current, writes, me)` is a pure function. Give it dicts. Then check what it restores and what it does not change.

Keep each test offline, fast and deterministic. Do not use the live platform or the model. Some values change on each run: the date in provenance notes, and the random ids of new sessions and escalations.
