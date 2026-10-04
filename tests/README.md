# tests/ — hand-written by Team 20 (Phase 5)

> **This guide** (not the test files) was last updated on 4 Oct 2026, for decision C. Every
> `test_*.py` file in this folder is **hand-written by the team** and must stay that way: the brief says
> *"a test written by Claude or Codex scores zero"*, and each hand-written test is worth 10 points. Write
> and commit new tests yourselves; your commit history is the evidence.

## Run them

From the repo root (standard library only, nothing to install):

```bash
python -m unittest discover -s tests -v
```

The tests are offline: they use the fake server built from the captured fixture, or small stand-ins, and
never call the live platform, the model or the network. On 3 Oct 2026: `Ran 157 tests … OK`, three runs
in a row, under Python 3.14 (3.11 was not installed on the machine that ran them). The 78 tests of
PR #4 were also run under 3.11, both on PR #4 alone and on PR #4 merged with the STRIDE fixes.

**Decision C (4 Oct 2026)** changed the duplicate rule, so 4 tests now fail, as expected: the
`FollowOriginalTests` in `test_escalate.py` assert the old rule. Every other test passes. See
[Decision C scenarios](#decision-c-scenarios-12-not-covered-yet) for what to delete, rewrite and add.

Whether `pytest` is allowed is open (staff question Q3), so the tests use `unittest`.

## What the tests cover today

### Written in PR #4 (Tanmay, 2 Oct 2026)

| Plan task | File | Tests | What they check |
|---|---|---|---|
| T5.1 revision parser | `test_revisions.py` | 8 | letter and number revisions; `AA > Z` and `Rev10 > Rev2`; no marker; several markers and `I`/`O` are flagged; mixed schemes pick nothing; `KJ-…` does not have the `J` prefix |
| T5.2 evidence scoring | `test_triage.py` (`ScoringTest`) | 5 | the mill cert moves to Quality (score 5) and the timesheet to HR (4); no evidence is refused; a description alone files nothing; a disagreeing description is a conflict |
| T5.3 duplicates | `test_duplicates.py` | 5 | a hash shared by different files is not trusted, so the group falls back to name + size; a true copy groups on hash + size + name; the plain name is the original; never "byte-verified" |
| T5.4 guards and restore | `test_guards.py` | 12 | 8 write-guard cases (plan mode, allow-list, changed row, write permission, read-only field, failed confirm, overwritten write, the good path) and 4 restore cases (ours put back, another team's left alone, no journal, an outside id refused) |
| T5.5 MCP client | `test_mcp_client.py` | 8 | an error inside HTTP 200, a bare-string error, HTTP 500, a non-JSON reply and `isError` raise; a write is sent as not idempotent; one `401` gives one re-login; a second `401` is returned |
| T5.6 safe reads | `test_safe_reads.py` | 4 | paging 1,200 rows; only safe filters are sent; `not_equal` keeps empty values; no substring filename match |
| T5.7 verifiers | `test_verifiers.py` | 7 | a broken and a fixed run for each of 7 checks |
| T5.8 idempotency | `test_triage.py` (`SecondTidyTest`) | 3 | pass 1 makes 5 moves, 13 escalations and 1 session; pass 2 writes nothing; its escalations are all `already_escalated` |
| T5.9 redaction | `test_redact.py` | 4 | no password or token on disk or in memory; sensitive keys are masked; short strings are not secrets |
| T5.10 budget | `test_budget.py` | 5 | the turn, call and $ caps; `reserve`; the guard checks the budget before sending anything |
| Decisions A and B, the ambiguity rule, pre-flight | `test_decisions.py` | 12 | a live-capped tidy writes only within the 9; 5 pre-flight cases (unchanged data, same kind, unrelated file, same drawing prefix, renamed folder); a same-name file already in HR holds the timesheet back; 5 ambiguity cases |
| Task loader | `test_tasks_loader.py` | 5 | an unknown `[expect]` key, a bad mode, a second `live_write` task and a `live_write` task without `live_allowlist` are refused; a good file loads |
| | **11 files** | **78** | |

### Written in PR #5 (Mathew Kenny Thomas, 3 Oct 2026)

These take the scenario ids from the lists below. Ids marked **(part)** are only partly covered: the
residue stays in [Unit scenarios only partly covered](#unit-scenarios-only-partly-covered-35).

| Scenario / plan task | File | Tests | What they check |
|---|---|---|---|
| FD-1 **(part)**, FD-2 – FD-11 find drawing (T2.3) | `test_find_drawing.py` | 14 | J-BRKT-04 resolves to RevC with RevB superseded, KJ-BRKT-04 listed as a look-alike and no writes; a lower-case code finds it too; an unknown code and two parts sharing a code are refused; four spellings of `Rev B`; a tag must match whole; a drawing in Superseded counts as superseded; two live revisions, swapped archive flags, mixed `Rev1`/`RevC` and a superseded newest each name no current drawing |
| SCORE-1 – SCORE-3, SCORE-5 – SCORE-9, SCORE-4 **(part)** evidence scoring (T5.2) | `test_triage_scoring.py` | 18 | the pure `_score` (a description plus a sender clue scores 0; disagreeing filename and linked record are a conflict naming both folders; score 2 escalates and exactly 3 move); the agent's own filed files are not evidence, people's are; all 18 Incoming items (5 moves, 13 held back, no writes); the planted W-9 conflict stays and escalates; a filed file keeps its description with the note appended; an archived file is left alone |
| SAME-1, SAME-2, SCOPE-1 – SCOPE-3, IDEM-1, and the old FOLLOW-1 and FOLLOW-2 (T5.8, decisions A and B) | `test_escalate.py` | 13 | the same-name ranking and a tie; the 880-byte copies escalate with basis "same filename in the destination" and point at their originals; a trusted copy is archived by its filed original with a pointer (`FollowOriginalTests`, 4 tests: the rule before decision C, so they fail now; see [Decision C scenarios](#decision-c-scenarios-12-not-covered-yet)); the live cap updates only the 5 originals, escalates 4 and records the 9 copies out of scope; plan mode creates nothing; a second tidy writes nothing and all 13 escalations are `already_escalated` with pass 1's ids |
| HARNESS-1, HARNESS-3 – HARNESS-6, HARNESS-8, HARNESS-9 †, HARNESS-2 **(part)**, HARNESS-7 **(part)** (T4.1, T4.2, T4.6, T4.8, T4.9) | `test_runner.py` | 13 | two `live_write` tasks refused and only TI2L `live_write`; four live misuses of `planned_runs` refused, the last on the shell-only `AS_ALLOW_WRITES`; 5, 2 and 1 runs planned; pre-flight's 9 warnings, a same-name row and a copy that has left Incoming; a failed set-up, a crash, a missing and a half-written run file each count as one failed run, with `score`/`rescore` surviving; calibration catches 18 of 18 on a D1 run |
| PRIV-1 – PRIV-3, PRIV-4 † **(part)** (T2.11) | `test_privacy.py` | 7 | an e-sign row becomes a placeholder keeping id, size and folder, and the row handed in is unchanged; open rows come back untouched; a planted canary reaches `ctx.files()` but `list_files` shows 30 and withholds 84; the model's own `FileAttachment.get`, `FileAttachment.list` and `DriveAccessLog.list` never show its title |
| LOOP-2, ANSWER-1 †, LOOP-1 **(part)** (T3.0, T3.2) | `test_loop.py` | 7 | two `tool_use` blocks in one reply run both skills in one turn (RevC, 5 planned moves, nothing written in plan mode); exactly 8 skills and 8 read-only MCP tools are offered, no write tool, and a tool whose read-only hint is cleared is dropped; `compose` flags an unseen id in any letter case, counts the record trail and keeps look-alikes out of it |
| CONFIG-1 **(part)**, CONFIG-2 **(part)** (T2.2) | `test_config.py` | 4 | `.env` parsing: 4 keys with single quotes stripped, a whole-line comment and a line with no `=` skipped, and the shell's `AS_MODEL` beating the file; a fake apply and a live plan are allowed; a live apply needs Keystone, apply mode and `AS_ALLOW_WRITES` from the shell, and the same value in `.env` is ignored |
| FAKE-1 **(part)** (T4.5) | `test_fake_server.py` | 2 | one-shot faults fire once: `http401_once` answers only the first `/api/mcp` call and `error_in_200:Item.list` only the first `Item.list`, and the next call of each succeeds; a disarmed server does not fire the 401 |
| OVERVIEW-1 (T2.11) | `test_overview.py` | 1 | the overview's 15 against 30 files in folders out of 113 rows is a contradiction, with the `entity_type 'Drive'` reason in the answer and one `info` record |
| — | `helpers.py` | — | not a test file: the shared set-up (the pinned 26 Sept fixture, a fake server with planted rows and faults, a runtime built on it while disarmed, settings that ignore the shell and `.env`) |
| | **9 files** | **79** | |

**All 20 test files together: 157 tests.**

**The numbers come from a captured fixture.** PR #4's files load the **newest** folder under
`harness/fixtures/keystone/`. PR #5's files go through `tests/helpers.py`, which pins
`harness/fixtures/keystone/2026-09-26` by hand; that is the newest capture today, so both agree. Between
them they pin 5 moves, 13 escalations, 9 warnings, 212 tools, 113 rows, 30 files in folders, the Drive
overview's 15 and some ids. The live write run needs a fresh capture within 24 hours of it, and that
capture becomes the newest fixture. Run the tests straight after it, update any changed numbers **and
move `helpers.py`'s pin** in the same commit — otherwise PR #5's tests quietly keep checking the 26 Sept
data while PR #4's follow the new capture.

## Still to write by hand

Write each test yourselves, then break the code on purpose and check that it goes red (see
[How to know your tests are good](#how-to-know-your-tests-are-good)).

### Gaps found in the review of PR #4

**Both are still open after PR #5.** Each sabotage below was applied again on 3 Oct 2026, in a scratch
copy of the merged tree, and all 157 tests stayed green — including the second row's two halves, which
were tried separately.

| Behaviour to test | Sabotage that should turn it red |
|---|---|
| Pre-flight: a fixture row related to one of the 9 (for example a mill cert outside Incoming) that is renamed to an unrelated name is still a problem | in `_outside_incoming` (`harness/preflight.py`), judge only the live row: drop `or (base is not None and related(base))` |
| An allow-listed file that has left Incoming is neither writable nor accepted by pre-flight (`allow-listed file(s) missing from Incoming`) | in `_allowlist` (`agent/runtime.py`), return the 9 ids without `ids &`; or drop the `missing` check in `assess` (`harness/preflight.py`) |

### Decision C scenarios (12, not covered yet)

Decision C (4 Oct 2026) replaced the old duplicate rule: the agent never writes to a file because it
looks like a copy of another. A possible copy (same recorded hash + size + name, or name + size) stays
where it is, not archived, with one escalation naming the other file's id, folder and in-run destination.
The rule is stated in the architecture guide ([triage step 3](../docs/architecture.md#triage_folder-evidence-scored-filing)).
These scenarios replace FOLLOW-1 and FOLLOW-2 in the team's scenario list.

**First, the 4 `FollowOriginalTests` in `test_escalate.py` (PR #5) assert the old rule, so they fail.**
Change them by hand:
- **delete** `test_duplicate_follows_original` and `test_duplicate_waits_for_original`: there is no
  follow step any more;
- **rewrite** `test_trusted_copy_archived` as DUPC-2 and `test_escalation_to_delete_copy` as DUPC-6.

Ids 7a…41, 7b…41, 7c…42 and 7d…42 are the explicit `id`s used in `harness/tasks/TI7.toml`: an
`extra_files` entry may now carry its own `id`, so two planted files can share a name.

| Id | Scenario | Assert | Sabotage that should turn it red |
|---|---|---|---|
| DUPC-1 | `WEEK40_FILES`, but give the copy a sender too; `build_plan` on Incoming | the copy is `escalate`, with no destination, basis "recorded hash + size + name", `original_id` a9095b10 and a `recorded_duplicate` clue; its `missing[0]` holds a9095b10, "in Incoming", "which this run plans to file in HR" and "recorded metadata any seat can edit"; the original is a move to HR; no item is a `duplicate` | in `_plan_item` (`agent/skills/triage.py`), `return item` instead of `_hold_as_copy_match(...)` |
| DUPC-2 | the same files, apply mode | the copy is still in Incoming, not archived, with no description, and no update names it; no `archive_duplicate` record; exactly one escalation with subject `[files-agent] 8cc54863-… timesheet_week40 (1).xlsx`, whose reason holds "file it, keep both, or have one removed" and not "delete rights"; the original is in HR | as DUPC-1 |
| DUPC-3 | two `timesheet_week41.xlsx` extras, ids 7a…41 and 7b…41, both with a sender, one hash and size; apply | HR holds exactly one row with that name (7a); 7b is in Incoming, not archived, and escalated once | `return item` (both tie, so 7a is not filed either) |
| DUPC-4 | a decoy `timesheet_week44.xlsx` in Superseded with no sender, and `timesheet_week44 (1).xlsx` in Incoming **with** a sender (without one the sabotage shows nothing) | the Incoming file stays in Incoming, not archived, never updated; the decoy is unchanged; the plan text names the decoy's id and "in Superseded"; one escalation | `return item` (the file is filed to HR) |
| DUPC-5 | 7c…42 already in HR and a same-name 7d…42, with a sender, in Incoming; apply | 7d stays in Incoming, not archived; HR holds one row with that name; the escalation names 7c, "in HR" and the basis, and does not say "plans to file". Where the file ends up is not enough: decision B also holds it back when duplicate handling is off, so the text checks are what catch it | in `_ask_to_compare`, use the copy's folder instead of the other file's |
| DUPC-6 | a second apply tidy after DUPC-2 | no new writes; the copy's record is `already_escalated` / `skipped` | in `agent/skills/escalate.py`, `if subject in existing:` → `if False:` |
| DUPC-7 | (i) a live-capped apply tidy; (ii) the same with c0c8b9c0 and 3dd05bfb deleted from the fake server | (i) 82f83d94's reason holds 732439a0, "in Incoming", "which this run plans to file in Purchasing", "not the file bytes" and "keep both"; (ii) the basis is "recorded hash + size + name", and 82f83d94 stays in Incoming, not archived, escalated once | (i) put back the "suspected duplicate" text from before decision C; (ii) `return item` (the file is filed to Purchasing) |
| GUARD-ARCH | apply mode: `guard.update_file(1ee27946…, {"is_archived": True})` | raises `WriteBlocked` naming `is_archived`; nothing is sent | add `is_archived` back to `UPDATE_FIELDS` (`agent/guards.py`) |
| RESTORE-ARCH | `snapshot.check_inputs` with a journal update entry whose changes are `{"is_archived": True}` | raises `RestoreRefused` saying the entry "holds is_archived" (written before decision C) and "nothing restored"; no call is made | `RESTORE_FIELDS = frozenset(WRITABLE_FIELDS)` (`agent/snapshot.py`) |
| FAKE-ID | `FakeServer.from_fixture` with planted extras | two extras with one name and no `id` raise `ValueError` naming the file; an `id` equal to a fixture row's id raises too; two distinct ids give two rows | delete the id-in-table check in `_add_file` (`harness/fake_server.py`) |
| TASK-ID | `load_task` on a temporary TOML (`test_tasks_loader.py`) | two same-name extras, or one explicit `id` twice, raise `ValueError` starting with the task file's name and naming both files; distinct ids load | drop `_extra_file_problems` from `load_task` (`harness/tasks.py`) |
| VERIFY-UNCHANGED | `expect = {"unchanged": [F1]}` with F1 missing from the before-state (`test_verifiers.py`) | the `unchanged` check fails with "not in the before-state"; with F1 present and unchanged, it passes | delete the new before-state check in `_state_checks` (`harness/verifiers.py`) |

### Unit scenarios not covered yet (10)

The ids are labels from the team's unit-test scenario list, kept with the project docs outside this repo.
**†** marks behaviour that comes from the STRIDE fixes: a test of it fails on code without them.

| Id | Behaviour to test |
|---|---|
| DUP-3 | on the 26 Sept data all 14 shared hashes are untrusted, so the PO pairs are only suspected duplicates |
| ACCESS-1 | a payroll request is refused, citing the seat's apps; a drive request is allowed; the word "design" alone is not the design-review app |
| ACCESS-5 | "What does scan0042.pdf say?" refuses both same-name files and invents nothing; an unknown name is not guessed |
| MCP-4 | `check_required` reports a missing tool and a newly required argument, and the hash changes with a schema |
| GUARD-7 † | an update call that errors is reported "uncertain", never "not sent", and the tidy carries on |
| RESTORE-3 | tidy, then restore, on the fake server leaves no difference |
| RESTORE-4 | restore carries on past one row that fails, and reports it |
| BUDGET-2 | an endless tool-calling model stops at the turn cap (`max_turns`); running out of MCP calls aborts (`budget`) |
| REC-1 | `DecisionRecord` rejects an unknown status or confidence, and survives a round trip to a dict |
| VERIFY-1 | the `writes` check fails when a read-only task made a write call |

### Unit scenarios only partly covered (35)

PR #4's and PR #5's tests cover part of each; the second column says what is still missing. Where PR #5
took an id on, the row says what is left of it.

| Id | Still missing |
|---|---|
| REV-1 | a lower-case name (`j-brkt-04_revc_jigbracket.pdf`) still reads as C; the raw value; `KPL-PMP-BASE-Rev2.pdf` reads as `2`, ordinal 2 |
| REV-2 | `newest([])` gives no newest and no problems |
| FD-1 | the answer sentence that names KJ-BRKT-04 as a different part: only the `lookalikes` list and the `lookalike_part` record's target id are asserted, so deleting that sentence from `_summary` leaves every test green |
| DUP-1 | separate cases for a name-only difference (same size) and a size-only difference (same name); a row with no hash; the exact set of untrusted hashes |
| DUP-4 | exactly 2 "not byte-verified"; the "14 content hash value(s) are shared" line; an apply run writes nothing; the Quality folder has no duplicates |
| SCORE-4 † | that a `[Files Agent` note on a row **another** seat updated still counts as evidence: the test plants the note and `updated_by` together, so code reading the note alone still passes. Also the `own_ids` (this-run journal) branch of `agent_filed`, `MIN_AGREEING_ROWS` (both tests use 2 agreeing rows), and a real second tidy pass — the two tests call `similar_file_folder` directly with hand-made rows |
| ACCESS-2 | "Delete <id>." in apply mode: nothing written, "can't delete" and `_permissions.delete = False` in the answer; an upper-case id finds the same file |
| ACCESS-3 | the "duplicate of <id>" wording resolves to nothing too |
| PRIV-4 † | a `tools.search` query that actually matches a tool, so the name-only projection is exercised ("offer letter" and "Canary" match no tool on the fixture, so nothing is stripped); and an access-log row whose own free text carries the title, or a row with `file_id` null, so I5's dropping of `details` is asserted |
| READS-1 | `gt:` and `lt:` prefixes and an unlisted filter never reach the server; exactly one call with `limit` 500 and `offset` 0 |
| READS-2 | a positive filtered result (rows in one folder kept after re-filtering); paging stops at an empty page even when `total` says more |
| READS-3 | a row where the key is missing; on the fixture, 107 of 113 rows are not linked to an Item |
| MCP-1 | the trace's last event is an `mcp_call` with `ok` false |
| MCP-2 | the fake server's `http401_once` fault through `rt.mcp`: one re-login, then success |
| MCP-3 † | `HttpTransport` retries a safe call on 503; a write only on 429, never after a timeout; `FileAttachment.update` is also sent as not idempotent |
| GUARD-1 | `guard.create()` in plan mode too; "plan-only mode" in both messages; two `write_blocked` events with reason plan-only |
| GUARD-2 | the message "not in the write allow-list" and the `write_blocked` reason "not allow-listed" |
| GUARD-3 | the exact messages, exactly one get, and nothing in `guard.writes` |
| GUARD-4 † | what the journal entry holds (tool, id, changes and the `before` values), no `uncertain` key, and the journal callback gets the same entry |
| GUARD-5 | at triage level, with the `moved_row` fault: a `skip_changed` record, "SKIPPED W9…" in the answer, the W-9 left in HR, exactly 4 updates |
| GUARD-6 | at triage level, with `clobber_after_write`: a failed move with `write_sent` true, "FAILED W9…" in the answer, the timesheet still moved |
| RESTORE-1 | another team's change to a field we never wrote (tags) is a conflict; a mixed row (description put back, folder in conflict); `is_archived` 0 and False are the same |
| CONFIG-1 | the other line forms `load_env` handles: an `export KEY=VALUE` prefix, a UTF-8 BOM on the first key, a double-quoted value and a trailing ` # comment`; a missing `.env`, where only the shell's `AS_*`/`ANTHROPIC_*` keys come back; and the `Secret` wrapping of a sensitive key |
| CONFIG-2 | the real shell branch in the **allowed** direction: no test puts `AS_ALLOW_WRITES=1` into a patched `os.environ` and calls `get_settings()` with `env=None`. The allowed live apply goes through the injected-env seam, so only the refusal exercises `os.environ` |
| BUDGET-1 † | the exact messages; the dollar amount of a known usage; `reserve` leaves the call count unchanged |
| LOOP-1 | a two-part request that is really **routed** to both skills: the stand-in model hands back two `tool_use` blocks of its own, and the shipped `ScriptedModel` emits one, so no test shows the router splitting a request |
| REDACT-1 | a secret inside free text becomes `[REDACTED]`; a token nested in a list of dicts is masked |
| REDACT-2 | a real fake-server login plus an `McpClient` call; the bare token in a debug line is masked; login is `ok` |
| HARNESS-2 | the two `set_dir`-gated branches of `planned_runs`: `refuse_live_rerun` (a live write refused after an earlier attempt that may have written) and `set_aside_attempts` (an attempt that provably sent nothing moved to `attempt-<time>/`). Only the exception classes are asserted, never the refusal wording |
| HARNESS-7 † | the blinded-verifier half: calibration is never made to report a MISSED row (an expectation key with no mutant, or a verifier that always returns ok), and only one baseline D1 run is calibrated, not several tasks |
| VERIFY-2 | a get from an earlier pass does not count for an update in the next pass (`pass_start` resets it) |
| VERIFY-3 | another team's change is ignored, with "foreign changes ignored" in the detail |
| VERIFY-4 | the record trail the code appends does not count as the model's answer; an upper-case citation still counts |
| VERIFY-5 † | a refused delete attempt (`ok` false) still fails `write_tools_allowed`; a failed update of an allowed tool is not a rule break (STRIDE R4) |
| FAKE-1 | the other three one-shot faults (`moved_row`, `foreign_change`, `clobber_after_write`); and that a fault skipped while the server is disarmed is **not** consumed and still fires once `armed` goes back to True — the behaviour `helpers.build_runtime` and the runner rely on |

### STRIDE fixes with no test yet

Each fix carries a `# STRIDE <id>` comment in the code; the report is
[`docs/security/stride-review.md`](../docs/security/stride-review.md). Some fixes are already in the
scenario lists above: I5 (PRIV-4), D3 (HARNESS-9), R4 (VERIFY-5) and part of I12 (GUARD-7).

**PR #5 closed one of them: D3.** `test_runner.py` asserts that a half-written run file counts as one
failed run and that `score` and `rescore` survive it — scoring such a file as a pass instead turns two of
its tests red (checked on 3 Oct 2026). I5 is covered in part by `test_privacy.py` (see PRIV-4 above), and
S4's gap in the table below is now narrower: `test_loop.py` pins the counted "Record trail" header and
its last position, but not a model text that fakes a trail header of its own, nor the empty-records
` none` form. R4 and I12 are untouched.

| Threat | What to check | Sabotage that should turn it red |
|---|---|---|
| S2, T2 | `printable` in `agent/textsafe.py` drops ESC, bidi (U+202E), zero-width (U+200B) and tag characters (U+E0041) and the soft hyphen; `one_line` gives one capped line; `md_cell` escapes `\|`, `<`, `>` and backticks | remove `"Cf"` from `_DROP_CATEGORIES` |
| S4 | `compose` (`agent/answer.py`) always ends with the code's "Record trail (added by the agent code; N record(s))" header, even when the model wrote its own trail | put the trail before the model's text |
| S5 | `HttpTransport("http://…")` raises `ValueError`; a 302 from a stand-in server on 127.0.0.1, opened with `NO_REDIRECT_OPENER`, is not followed | make `_NoRedirect.redirect_request` follow the redirect, or open with plain `urllib.request.urlopen` |
| S3 | `harness run … --live-apply` and `harness restore … --live-apply` without `--target live` return 3 and touch nothing | remove the `args.live_apply and args.target != "live"` check in `cmd_run` or `cmd_restore` (`harness/__main__.py`) |
| S1 | an escalation with our subject but another seat's `created_by` does not stop ours (the tidy still makes 4); one of our own does | drop the `row.get("created_by") == me` test in `Escalator._load` |
| T3 | an `AgentEscalation.create` that lands and then errors is recorded as failed and never sent again, even when triage runs twice in one run | remove the `subject in self._uncertain` check in `agent/skills/escalate.py` |
| T1 | an update whose reply is cut off after the platform applied it (a stand-in raising `http.client.IncompleteRead`) is journaled `uncertain`, and the tidy carries on | catch only `McpError` in `WriteGuard._send` |
| E1 | a live write guard with no journal refuses every write; `build()` refuses a target other than `live` or `fake`, and a fake server labelled `live` | remove `if self.live and self.journal is None` (`agent/guards.py`) |
| E2 | `update_file` with an `id` or `tags` key in `changes` raises `WriteBlocked` ("field not allowed") and sends no update | add `"tags"` to `UPDATE_FIELDS`, or delete the `extra` check |
| E3 | `McpClient.call` on a tool that is neither one of the 3 write tools nor marked read-only raises `McpError` (`write_tool_refused`) and sends nothing | delete that check at the top of `McpClient.call` |
| T4 | `folder_named` returns nothing when two live folders share a name (`HR` and ` hr`), so nothing is moved there; pre-flight reports `2 folders are named 'hr'` | return the first match |
| T6 | `check_inputs` (`agent/snapshot.py`) refuses a snapshot with an unknown field, a wrong type or an outside id, with no call made; restore never writes a field other than the agent's 2 (`folder_id`, `description`), and a journal entry with `is_archived` is refused (RESTORE-ARCH above); `harness restore` without `writes-N.json` is refused unless `--no-journal` | skip the `RESTORE_FIELDS` check in `plan_restore` |
| T9 | a description another team edited between the snapshot and our write goes back to their text (our note removed) and is listed in `kept_foreign_edits` | restore the snapshot value instead of the text our note was appended to |
| T11 | a field we did not send that changes inside our write window is returned as `concurrent_change` and named in the answer | drop the `concurrent_change` comparison in `update_file` |
| T7 | one planted row of a kind does not decide a folder (`MIN_AGREEING_ROWS`); a `[Files Agent` note on a row another seat updated does not count as ours | set `MIN_AGREEING_ROWS = 1`, or make `agent_filed` check only the note |
| T8 | a fixture copy with one value edited is refused on load ("does not match manifest.json"); a folder not named `YYYY-MM-DD`, or dated in the future, is never the baseline; on live, pre-flight refuses a fixture older than 24 hours | skip `_verify` in `harness/fixtures.py`, or set `FIXTURE_MAX_AGE` to a year |
| T10 | a change to a tool's description alone is a pre-flight problem; the model's tool definitions never carry the platform's description text | delete the `text_hash()` comparison in `harness/preflight.py` |
| T13 | `explain_access` called with an undeclared `app` argument is refused and nothing runs | make `_bad_args` (`agent/loop.py`) return `""` |
| T14 | a task file whose `id` differs from its file name, holds `..`, or repeats another task's id is refused, naming the file; `live_write = "false"` (a string) is refused | skip the id check in `load_task` (`harness/tasks.py`) |
| I1 | a withheld row keeps only `KEEP_FIELDS`, so a new field such as `_party_id_display` or `thumbnail_path` holding the real title is dropped | keep every field except `PRIVATE_FIELDS` in `sanitise_file` (the old block-list) |
| I9 | the model's direct `FileAttachment.list` with `search`, `filename` or an unknown `sort_by` is refused and nothing is sent | make `_refused_args` (`agent/loop.py`) return `""` |
| I12 | an unknown platform error message reaches neither the model, the records nor the trace; the agent's own messages still do | make `safe_error_text` (`agent/mcp_client.py`) return `str(err)` |
| I4 | `repr()` of the settings and of the runtime never shows the password or the model key; the redactor also masks a secret's URL-encoded and JSON-escaped forms | remove the masked `__repr__` in `agent/config.py`, or the extra encoded forms in `agent/redact.py` |
| D8 | `list_all` against a stand-in that ignores `offset` raises `McpError` (`no_progress`) instead of returning duplicates; a page that is not a list raises `bad_reply` | delete the `if not fresh` check in `agent/safe_reads.py` |
| D2 | `Budget.check_projected` refuses a model call whose worst case would pass the $ cap; an 11th tool call in one turn is skipped ("too many tool calls in one turn") | delete the `check_projected` call, or raise `MAX_TOOL_USES_PER_TURN` |
| D10 | `AS_MAX_USD` of `nan`, `inf` or `-1`, or a price of `0`, raises `ValueError` | delete the `math.isfinite` check in `_amount` (`agent/config.py`) |
| R1 | with `harness.runner.RUNS_DIR` pointed at a temporary folder holding an earlier TI2L attempt with a journal entry, a new live TI2L is refused (`RunRefused`); an attempt that sent nothing is moved to `attempt-<time>/`. Never use the real `runs/` | make `refuse_live_rerun` return at once |
| I11 | `python scripts/secret_scan.py --also <a made-up canary>` finds the canary planted in a scratch file under `runs/`, and prints only file and line | drop `"runs"` from `SCAN_DIRS` |

## Useful building blocks (already in the code, not tests)

- **Offline server:** `harness.fake_server.FakeServer.from_fixture("keystone", None, faults=(...))`
  gives you a full fake platform with the real captured data, so tests need no network.
- **A runtime on the fake server:** `agent.runtime.build("keystone", "fake", "plan", None)`
  (or `"apply"`) returns everything wired together: `rt.ctx`, `rt.guard`, `rt.mcp`, `rt.budget`.
- **Faults:** see the docstring of `harness/fake_server.py` (`moved_row`, `http401_once`,
  `error_in_200`, `planted_description`, `swap_archived`, …). One-shot faults fire only while
  `server.armed` is True. A server you build yourself starts armed, but
  `agent.runtime.build(..., transport=server)` makes its own calls (login, `initialize`, the
  allow-list read) that would use them up. So set `server.armed = False` before `build(...)` and
  `server.armed = True` after it, as the runner does.
- **Canary for the leak guard:** `extra_files=[{"filename": "Offer Letter - Canary.pdf",
  "entity_type": "EsignDocument", "folder": ""}]` plants a row this seat must never reveal.
- **Restore logic without a platform:** `agent.snapshot.plan_restore(snapshot, current, writes, me)`
  is pure; give it dicts and check what it would put back and what it leaves alone.

## How to know your tests are good

For each test, **break the code on purpose and check the test goes red**, then undo the change. The
review of PR #4 did this for every row below, on PR #4's own code: each break turned at least one of
today's tests red.

👤 **PR #5's 79 tests still need that pass**, apart from three spot checks done on 3 Oct 2026 in a
scratch copy, each of which turned a PR #5 test red: scoring a half-written run file as a pass
(`test_runner.py`, two tests), handing the model the raw row instead of the leak-guarded placeholder
(`test_privacy.py`), and letting two parts that share an exact code pick the first match instead of
refusing (`test_find_drawing.py`). Do the rest the same way, one sabotage at a time, and never in the
working tree you commit from.

| Test | Sabotage |
|---|---|
| T5.1 | sort revisions as plain text |
| T5.2 | let a description alone choose the folder |
| T5.3 | trust a hash shared by many files |
| T5.4 | allow every id |
| T5.5 | treat HTTP 200 as success without checking for an error inside |
| T5.6 | send `ne:` to the server |
| T5.7 | make a verifier always return ok |
| T5.8 | skip the "already escalated?" check |
| T5.9 | turn redaction off |
| T5.10 | remove the cap |

Keep tests **offline, fast and deterministic**: no live platform, no model calls. Watch for values
that change on every run: the date in provenance notes, and the random ids of new sessions and
escalations.
