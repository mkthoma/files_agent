# tests/ — hand-written by Team 20 (Phase 5)

> **This guide** (not the test files) was updated with AI assistance (Claude Code) on 3 Oct 2026. Every
> `test_*.py` file in this folder is **hand-written by the team** and must stay that way: the brief says
> *"a test written by Claude or Codex scores zero"*, and each hand-written test is worth 10 points. Write
> and commit new tests yourselves; your commit history is the evidence.

## Run them

From the repo root (standard library only, nothing to install):

```bash
python -m unittest discover -s tests -v
```

The tests are offline: they use the fake server built from the captured fixture, or small stand-ins, and
never call the live platform, the model or the network. On 3 Oct 2026: `Ran 78 tests … OK` under
Python 3.14 and 3.11, both on PR #4 alone and on PR #4 merged with the STRIDE fixes.

Whether `pytest` is allowed is open (staff question Q3), so the tests use `unittest`.

## What the tests cover today (PR #4, Tanmay, 2 Oct 2026)

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

**The numbers come from the newest fixture.** The tests load the newest folder under
`harness/fixtures/keystone/` and pin its numbers (5 moves, 13 escalations, 9 warnings, some ids). The
live write run needs a fresh capture within 24 hours of it, and that capture becomes the newest fixture.
Run the tests straight after it and update any changed numbers in the same commit.

## Still to write by hand

Write each test yourselves, then break the code on purpose and check that it goes red (see
[How to know your tests are good](#how-to-know-your-tests-are-good)).

### Gaps found in the review of PR #4

| Behaviour to test | Sabotage that should turn it red |
|---|---|
| Pre-flight: a fixture row related to one of the 9 (for example a mill cert outside Incoming) that is renamed to an unrelated name is still a problem | in `_outside_incoming` (`harness/preflight.py`), judge only the live row: drop `or (base is not None and related(base))` |
| An allow-listed file that has left Incoming is neither writable nor accepted by pre-flight (`allow-listed file(s) missing from Incoming`) | in `_allowlist` (`agent/runtime.py`), return the 9 ids without `ids &`; or drop the `missing` check in `assess` (`harness/preflight.py`) |

### Unit scenarios not covered yet (46)

The ids are labels from the team's unit-test scenario list, kept with the project docs outside this repo.
**†** marks behaviour that comes from the STRIDE fixes: a test of it fails on code without them.

| Id | Behaviour to test |
|---|---|
| FD-1 | J-BRKT-04 resolves to RevC, with RevB superseded and KJ-BRKT-04 named as a different part; a lower-case part code finds the same drawing |
| FD-2 | an unknown part code is refused, never guessed |
| FD-3 | a revision question names RevB as superseded and RevC as current; `Rev B`, `rev-b`, `Rev. B` and `revision B` all mean B |
| FD-4 | two drawings that both look current: no current drawing is named |
| FD-5 | KJ-BRKT-04 resolves to its own RevA and names J-BRKT-04 as a look-alike |
| FD-6 | swapped archive flags are reported as conflicts, and no current drawing is named |
| FD-7 | two parts with the same exact code are refused as ambiguous |
| FD-8 | a tag must match whole: `unreleased` is not `released` |
| FD-9 | a drawing in the Superseded folder that is not archived still counts as superseded |
| FD-11 | the newest revision is superseded while an older one looks current: no current drawing is named |
| DUP-3 | on the 26 Sept data all 14 shared hashes are untrusted, so the PO pairs are only suspected duplicates |
| SCORE-3 | the threshold is inclusive: score 2 escalates (`score 2 < threshold 3`), exactly 3 moves; a linked record pointing nowhere adds no points |
| SCORE-4 † | files the agent filed itself are not evidence for the next tidy; files people filed are |
| SCORE-7 | "File Untitled.pdf into the right folder" refuses both same-name files and moves nothing; the name matches ignoring case; an unknown name changes nothing |
| SCORE-8 | a filed file keeps its description; the agent's note is appended |
| SCORE-9 | an archived file in Incoming is left alone: not moved, not escalated |
| FOLLOW-1 | a duplicate follows its original only when the original is filed in this run; otherwise it waits for a person |
| FOLLOW-2 | a trusted duplicate is archived next to its filed original with a pointer, and a person is asked to delete it |
| SCOPE-2 | the Escalator refuses a file outside the allow-list |
| SCOPE-3 | in plan mode the Escalator records "planned" and never tries to create anything |
| ACCESS-1 | a payroll request is refused, citing the seat's apps; a drive request is allowed; the word "design" alone is not the design-review app |
| ACCESS-5 | "What does scan0042.pdf say?" refuses both same-name files and invents nothing; an unknown name is not guessed |
| PRIV-1 | an e-sign row becomes a placeholder that keeps id, size and folder; open rows come back untouched |
| PRIV-2 | a planted e-sign canary never reaches skill rows, and `list_files` counts it as withheld |
| PRIV-3 | the model's own `FileAttachment.get` and `.list` show only the placeholder |
| PRIV-4 † | the model's own `DriveAccessLog.list` and `tools.search` never show a planted e-sign title (STRIDE I5) |
| OVERVIEW-1 | `drive_overview` reports the contradiction: 15 from the overview, 30 in folders, 113 rows |
| MCP-4 | `check_required` reports a missing tool and a newly required argument, and the hash changes with a schema |
| GUARD-7 † | an update call that errors is reported "uncertain", never "not sent", and the tidy carries on |
| RESTORE-3 | tidy, then restore, on the fake server leaves no difference |
| RESTORE-4 | restore carries on past one row that fails, and reports it |
| CONFIG-1 | `.env` lines are parsed, and the shell's value wins |
| CONFIG-2 | offline and plan-only are always allowed; a live write needs Keystone, apply mode and `AS_ALLOW_WRITES` from the shell (a value in `.env` is ignored) |
| BUDGET-2 | an endless tool-calling model stops at the turn cap (`max_turns`); running out of MCP calls aborts (`budget`) |
| LOOP-1 | the graded two-part request runs both skills in one turn and writes nothing in plan mode |
| LOOP-2 | the model is offered exactly 8 skills and 8 read-only MCP tools, no write tool, and no tool the catalogue doesn't mark read-only |
| ANSWER-1 † | `compose` flags ids no tool showed, case-insensitively; the record trail lists decisions but not look-alikes; one id in two cases is cited once |
| REC-1 | `DecisionRecord` rejects an unknown status or confidence, and survives a round trip to a dict |
| HARNESS-2 | `planned_runs` refuses every live misuse before anything happens, and otherwise says how many run files a run makes |
| HARNESS-5 | a run whose set-up fails still leaves a run file with a failed result |
| HARNESS-6 | a missing run file counts as a failure, and rescore notices |
| HARNESS-7 † | calibration catches every planted mistake on a real D1 run, and exposes a blinded verifier |
| HARNESS-8 | an agent crash mid-run still leaves a complete run file that scores as a failure |
| HARNESS-9 † | a half-written run file counts as one failed run; `score` and `rescore` survive it (STRIDE D3) |
| VERIFY-1 | the `writes` check fails when a read-only task made a write call |
| FAKE-1 | one-shot faults fire once, and only while the server is armed |

### Unit scenarios only partly covered (38)

PR #4's tests cover part of each; the second column says what is still missing.

| Id | Still missing |
|---|---|
| REV-1 | a lower-case name (`j-brkt-04_revc_jigbracket.pdf`) still reads as C; the raw value; `KPL-PMP-BASE-Rev2.pdf` reads as `2`, ordinal 2 |
| REV-2 | `newest([])` gives no newest and no problems |
| FD-10 | through `find_drawing`: an extra `J-BRKT-04_Rev1` drawing gives no current drawing, one conflict and no `current_drawing` record |
| DUP-1 | separate cases for a name-only difference (same size) and a size-only difference (same name); a row with no hash; the exact set of untrusted hashes |
| DUP-4 | exactly 2 "not byte-verified"; the "14 content hash value(s) are shared" line; an apply run writes nothing; the Quality folder has no duplicates |
| SCORE-1 | the pure `_score` with a sender clue: score 0 and no folder |
| SCORE-2 | a filename and a linked record that disagree are a conflict; `to_folder` is empty and the "agreeing evidence" text names both folders |
| SCORE-5 | all 18 items: exactly 5 moves (with the scores of each), the full refuse and escalate id sets, no `duplicate` item, an empty write log |
| SCORE-6 | the planted description on the W-9: a conflict, never moved in apply mode, escalated, while the other four moves still happen |
| SAME-1 | the ranking itself: the higher scorer stays a move and the lower one escalates as a possible copy; a tie (in any letter case) holds back both |
| SAME-2 | the 880-byte copies `9b27de51` and `782cdca0` escalate with basis "same filename in the destination", pointing at `b45cecdd` and `680e8af6` |
| SCOPE-1 | the allow-list is exactly the verified 9; the exact 9 copy ids and 5 updated ids; 1 session; escalation subjects name the 4 originals; no `write_blocked` |
| IDEM-1 | exactly 13 `already_escalated` records, with the same ids as pass 1, read from the fake server's write log |
| ACCESS-2 | "Delete <id>." in apply mode: nothing written, "can't delete" and `_permissions.delete = False` in the answer; an upper-case id finds the same file |
| ACCESS-3 | the "duplicate of <id>" wording resolves to nothing too |
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
| BUDGET-1 † | the exact messages; the dollar amount of a known usage; `reserve` leaves the call count unchanged |
| REDACT-1 | a secret inside free text becomes `[REDACTED]`; a token nested in a list of dicts is masked |
| REDACT-2 | a real fake-server login plus an `McpClient` call; the bare token in a debug line is masked; login is `ok` |
| HARNESS-1 | the error names both `live_write` tasks; in the real task folder only TI2L is `live_write`, and it sets `live_allowlist` |
| HARNESS-3 | each of the 9 warnings names one copy id and says it will not be written or escalated |
| HARNESS-4 | a new row outside Incoming that shares a name (`timesheet_week33 (1).xlsx`); a fixture copy that has left Incoming |
| VERIFY-2 | a get from an earlier pass does not count for an update in the next pass (`pass_start` resets it) |
| VERIFY-3 | another team's change is ignored, with "foreign changes ignored" in the detail |
| VERIFY-4 | the record trail the code appends does not count as the model's answer; an upper-case citation still counts |
| VERIFY-5 † | a refused delete attempt (`ok` false) still fails `write_tools_allowed`; a failed update of an allowed tool is not a rule break (STRIDE R4) |

### STRIDE fixes with no test yet

Each fix carries a `# STRIDE <id>` comment in the code; the report is
[`docs/security/stride-review.md`](../docs/security/stride-review.md). Some fixes are already in the
scenario lists above: I5 (PRIV-4), D3 (HARNESS-9), R4 (VERIFY-5) and part of I12 (GUARD-7).

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
| T6 | `check_inputs` (`agent/snapshot.py`) refuses a snapshot with an unknown field, a wrong type or an outside id, with no call made; restore never writes a field other than the agent's 3; `harness restore` without `writes-N.json` is refused unless `--no-journal` | skip the `RESTORE_FIELDS` check in `plan_restore` |
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
