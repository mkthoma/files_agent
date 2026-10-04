# History

This file maps each section of the old README (before the split) to its new place, and holds these sections of the old README, word for word: 15, Contents, Quick start and The idea in one minute.

---

## Old-to-new section map

Each row is one heading of the old README, in the old order. *Old lines* are line numbers in `README.md` at commit `9d6f962`, the last commit before the split. The README line numbers in [security/stride-review.md](security/stride-review.md) come from an earlier README, so they can differ from these: use the section numbers and titles.

| Old README section | Old lines | Now in |
|---|---|---|
| Files Agent — AgentSwitch Seat 20 (Team 20) (title and front matter) | 1–15 | [README.md](../README.md) (title); [plan-and-status.md#old-readme-front-matter-before-the-split](plan-and-status.md#old-readme-front-matter-before-the-split) (lines 3–15) |
| Contents | 19–26 | [history.md#contents](history.md#contents) |
| Quick start | 30–42 | [history.md#quick-start](history.md#quick-start) |
| The idea in one minute | 46–59 | [history.md#the-idea-in-one-minute](history.md#the-idea-in-one-minute) |
| Tests | 63–105 | [plan-and-status.md#tests](plan-and-status.md#tests) |
| Security review (STRIDE) | 109–134 | [safety.md#security-review-stride](safety.md#security-review-stride) |
| &nbsp;&nbsp;*Before the live write run* (last paragraph) | 136 | [live-run.md#before-the-live-write-run](live-run.md#before-the-live-write-run) |
| 1. Architecture | 140 | [architecture.md#1-architecture](architecture.md#1-architecture) |
| &nbsp;&nbsp;1.1 The big picture | 142–180 | [architecture.md#11-the-big-picture](architecture.md#11-the-big-picture) |
| &nbsp;&nbsp;1.2 The life of one question | 182–195 | [architecture.md#12-the-life-of-one-question](architecture.md#12-the-life-of-one-question) |
| &nbsp;&nbsp;1.3 The life of one write | 197–210 | [architecture.md#13-the-life-of-one-write](architecture.md#13-the-life-of-one-write) |
| &nbsp;&nbsp;1.4 The building blocks | 212–232 | [architecture.md#14-the-building-blocks](architecture.md#14-the-building-blocks) |
| &nbsp;&nbsp;The two models | 234–237 | [architecture.md#the-two-models](architecture.md#the-two-models) |
| &nbsp;&nbsp;The system prompt, in short | 239–241 | [architecture.md#the-system-prompt-in-short](architecture.md#the-system-prompt-in-short) |
| 2. The skills | 245–260 | [architecture.md#2-the-skills](architecture.md#2-the-skills) |
| &nbsp;&nbsp;`find_drawing`: part → current drawing | 262–283 | [architecture.md#find_drawing-part--current-drawing](architecture.md#find_drawing-part--current-drawing) |
| &nbsp;&nbsp;`triage_folder`: evidence-scored filing | 285–311 | [architecture.md#triage_folder-evidence-scored-filing](architecture.md#triage_folder-evidence-scored-filing) |
| &nbsp;&nbsp;&nbsp;&nbsp;How a file is scored | 313–330 | [architecture.md#how-a-file-is-scored](architecture.md#how-a-file-is-scored) |
| &nbsp;&nbsp;`find_duplicates` | 332–342 | [architecture.md#find_duplicates](architecture.md#find_duplicates) |
| &nbsp;&nbsp;`drive_overview`: the platform contradicts itself | 344–353 | [architecture.md#drive_overview-the-platform-contradicts-itself](architecture.md#drive_overview-the-platform-contradicts-itself) |
| &nbsp;&nbsp;`explain_access`, `remove_file`, `file_contents`: refusing with evidence | 355–367 | [architecture.md#explain_access-remove_file-file_contents-refusing-with-evidence](architecture.md#explain_access-remove_file-file_contents-refusing-with-evidence) |
| &nbsp;&nbsp;`list_files`: the leak guard in action | 369–372 | [architecture.md#list_files-the-leak-guard-in-action](architecture.md#list_files-the-leak-guard-in-action) |
| &nbsp;&nbsp;Helper modules (not callable by the model) | 374–381 | [architecture.md#helper-modules-not-callable-by-the-model](architecture.md#helper-modules-not-callable-by-the-model) |
| 3. The harness | 385 | [harness.md#3-the-harness](harness.md#3-the-harness) |
| &nbsp;&nbsp;3.1 Why a harness | 387–389 | [harness.md#31-why-a-harness](harness.md#31-why-a-harness) |
| &nbsp;&nbsp;3.2 The life of one run | 391–403 | [harness.md#32-the-life-of-one-run](harness.md#32-the-life-of-one-run) |
| &nbsp;&nbsp;3.3 The parts | 405–420 | [harness.md#33-the-parts](harness.md#33-the-parts) |
| &nbsp;&nbsp;3.4 The tasks (22) | 422–467 | [harness.md#34-the-tasks-22](harness.md#34-the-tasks-22) |
| &nbsp;&nbsp;3.5 The verifiers (always on) | 469–481 | [harness.md#35-the-verifiers-always-on](harness.md#35-the-verifiers-always-on) |
| &nbsp;&nbsp;3.6 Scoring | 483–485 | [harness.md#36-scoring](harness.md#36-scoring) |
| &nbsp;&nbsp;3.7 Calibration: does the harness catch mistakes? | 487–505 | [harness.md#37-calibration-does-the-harness-catch-mistakes](harness.md#37-calibration-does-the-harness-catch-mistakes) |
| &nbsp;&nbsp;3.8 The fake server's faults | 507–521 | [harness.md#38-the-fake-servers-faults](harness.md#38-the-fake-servers-faults) |
| &nbsp;&nbsp;3.9 Run files | 523–529 | [harness.md#39-run-files](harness.md#39-run-files) |
| 4. From gap report to code | 533–537 | [gap-to-code.md#4-from-gap-report-to-code](gap-to-code.md#4-from-gap-report-to-code) |
| &nbsp;&nbsp;4.1 At a glance | 539–559 | [gap-to-code.md#41-at-a-glance](gap-to-code.md#41-at-a-glance) |
| &nbsp;&nbsp;4.2 What the agent builds (Q2 "ours to build") | 561 | [gap-to-code.md#42-what-the-agent-builds-q2-ours-to-build](gap-to-code.md#42-what-the-agent-builds-q2-ours-to-build) |
| &nbsp;&nbsp;&nbsp;&nbsp;A. Part → drawing resolver (gaps 2–3) ✅ | 563–568 | [gap-to-code.md#a-part--drawing-resolver-gaps-23-](gap-to-code.md#a-part--drawing-resolver-gaps-23-) |
| &nbsp;&nbsp;&nbsp;&nbsp;B. Evidence-scored Incoming triage (gap 4) ✅ | 570–582 | [gap-to-code.md#b-evidence-scored-incoming-triage-gap-4-](gap-to-code.md#b-evidence-scored-incoming-triage-gap-4-) |
| &nbsp;&nbsp;&nbsp;&nbsp;C. Undo log and clobber check (gap 6) ✅ checks · 🟡 restore not yet run live | 584–593 | [gap-to-code.md#c-undo-log-and-clobber-check-gap-6--checks---restore-not-yet-run-live](gap-to-code.md#c-undo-log-and-clobber-check-gap-6--checks---restore-not-yet-run-live) |
| &nbsp;&nbsp;&nbsp;&nbsp;D. Scheduled triage via `AgentTask` ⛔ | 595–596 | [gap-to-code.md#d-scheduled-triage-via-agenttask-](gap-to-code.md#d-scheduled-triage-via-agenttask-) |
| &nbsp;&nbsp;&nbsp;&nbsp;E. Calling the MCP tools safely ✅ (skills) · 🟡 (the model's own calls) | 598–603 | [gap-to-code.md#e-calling-the-mcp-tools-safely--skills---the-models-own-calls](gap-to-code.md#e-calling-the-mcp-tools-safely--skills---the-models-own-calls) |
| &nbsp;&nbsp;4.3 The seven gaps (Q1): what the benchmarks do, and our answer | 605–617 | [gap-to-code.md#43-the-seven-gaps-q1-what-the-benchmarks-do-and-our-answer](gap-to-code.md#43-the-seven-gaps-q1-what-the-benchmarks-do-and-our-answer) |
| &nbsp;&nbsp;4.4 Platform work we asked for (Q2 "platform work") | 619–632 | [gap-to-code.md#44-platform-work-we-asked-for-q2-platform-work](gap-to-code.md#44-platform-work-we-asked-for-q2-platform-work) |
| &nbsp;&nbsp;4.5 What our agent can do that theirs can't (Q3) | 634–640 | [gap-to-code.md#45-what-our-agent-can-do-that-theirs-cant-q3](gap-to-code.md#45-what-our-agent-can-do-that-theirs-cant-q3) |
| &nbsp;&nbsp;4.6 The agent's features A1–A14 | 642–665 | [gap-to-code.md#46-the-agents-features-a1a14](gap-to-code.md#46-the-agents-features-a1a14) |
| &nbsp;&nbsp;4.7 Platform change requests P1–P13 | 667–687 | [gap-to-code.md#47-platform-change-requests-p1p13](gap-to-code.md#47-platform-change-requests-p1p13) |
| &nbsp;&nbsp;4.8 Roadmap | 689–702 | [gap-to-code.md#48-roadmap](gap-to-code.md#48-roadmap) |
| 5. Background: the platform, the scenario and the research | 706–727 | [background.md#5-background-the-platform-the-scenario-and-the-research](background.md#5-background-the-platform-the-scenario-and-the-research) |
| &nbsp;&nbsp;5.1 Five facts that shape Step 4 | 729–745 | [background.md#51-five-facts-that-shape-step-4](background.md#51-five-facts-that-shape-step-4) |
| &nbsp;&nbsp;5.2 Platform facts (Keystone, measured live 22 Sept 2026) | 747–779 | [background.md#52-platform-facts-keystone-measured-live-22-sept-2026](background.md#52-platform-facts-keystone-measured-live-22-sept-2026) |
| &nbsp;&nbsp;5.3 The graded scenario | 781–823 | [background.md#53-the-graded-scenario](background.md#53-the-graded-scenario) |
| &nbsp;&nbsp;5.4 Benchmark products and what we borrow | 825–857 | [background.md#54-benchmark-products-and-what-we-borrow](background.md#54-benchmark-products-and-what-we-borrow) |
| &nbsp;&nbsp;5.5 Research behind the design | 859–869 | [background.md#55-research-behind-the-design](background.md#55-research-behind-the-design) |
| &nbsp;&nbsp;5.6 Bugs raised | 871–952 | [bugs.md#56-bugs-raised](bugs.md#56-bugs-raised) |
| 6. The Step 4 plan: tasks, status and open questions | 956–960 | [plan-and-status.md#6-the-step-4-plan-tasks-status-and-open-questions](plan-and-status.md#6-the-step-4-plan-tasks-status-and-open-questions) |
| &nbsp;&nbsp;6.1 What's graded, and the ground rules | 962–973 | [plan-and-status.md#61-whats-graded-and-the-ground-rules](plan-and-status.md#61-whats-graded-and-the-ground-rules) |
| &nbsp;&nbsp;&nbsp;&nbsp;*Ground rules* 1–4 | 975–982 | [safety.md#ground-rules-old-section-61](safety.md#ground-rules-old-section-61) |
| &nbsp;&nbsp;6.2 Task list and status | 984–991 | [plan-and-status.md#62-task-list-and-status](plan-and-status.md#62-task-list-and-status) |
| &nbsp;&nbsp;&nbsp;&nbsp;Phase 0 — Set-up and decisions (0.5 day) | 993–1001 | [plan-and-status.md#phase-0--set-up-and-decisions-05-day](plan-and-status.md#phase-0--set-up-and-decisions-05-day) |
| &nbsp;&nbsp;&nbsp;&nbsp;Phase 1 — Platform access and offline replay (2 days) | 1003–1014 | [plan-and-status.md#phase-1--platform-access-and-offline-replay-2-days](plan-and-status.md#phase-1--platform-access-and-offline-replay-2-days) |
| &nbsp;&nbsp;&nbsp;&nbsp;Phase 2 — Skills (4 days) | 1016–1030 | [plan-and-status.md#phase-2--skills-4-days](plan-and-status.md#phase-2--skills-4-days) |
| &nbsp;&nbsp;&nbsp;&nbsp;Phase 3 — Agent loop (1.5 days) | 1032–1041 | [plan-and-status.md#phase-3--agent-loop-15-days](plan-and-status.md#phase-3--agent-loop-15-days) |
| &nbsp;&nbsp;&nbsp;&nbsp;Phase 4 — Harness (3 days) | 1043–1057 | [plan-and-status.md#phase-4--harness-3-days](plan-and-status.md#phase-4--harness-3-days) |
| &nbsp;&nbsp;&nbsp;&nbsp;Phase 5 — Your tests (hand-written; 1.5 days spread across Phases 1–4) | 1059–1074 | [plan-and-status.md#phase-5--your-tests-hand-written-15-days-spread-across-phases-14](plan-and-status.md#phase-5--your-tests-hand-written-15-days-spread-across-phases-14) |
| &nbsp;&nbsp;&nbsp;&nbsp;Phase 6 — Evaluate and submit (1.5 days) | 1076–1085 | [plan-and-status.md#phase-6--evaluate-and-submit-15-days](plan-and-status.md#phase-6--evaluate-and-submit-15-days) |
| &nbsp;&nbsp;6.3 Milestones | 1087–1098 | [plan-and-status.md#63-milestones](plan-and-status.md#63-milestones) |
| &nbsp;&nbsp;6.4 Must / Should / Could | 1100–1127 | [plan-and-status.md#64-must--should--could](plan-and-status.md#64-must--should--could) |
| &nbsp;&nbsp;6.5 Risks and how the code handles them | 1129–1140 | [plan-and-status.md#65-risks-and-how-the-code-handles-them](plan-and-status.md#65-risks-and-how-the-code-handles-them) |
| &nbsp;&nbsp;6.6 Questions for staff | 1142–1155 | [plan-and-status.md#66-questions-for-staff](plan-and-status.md#66-questions-for-staff) |
| 7. How to check that each part works | 1159–1178 | [checking.md#7-how-to-check-that-each-part-works](checking.md#7-how-to-check-that-each-part-works) |
| &nbsp;&nbsp;7.1 Three ways to check anything | 1182–1203 | [checking.md#71-three-ways-to-check-anything](checking.md#71-three-ways-to-check-anything) |
| &nbsp;&nbsp;7.2 Ground truth: ask the platform directly | 1207–1301 | [checking.md#72-ground-truth-ask-the-platform-directly](checking.md#72-ground-truth-ask-the-platform-directly) |
| &nbsp;&nbsp;7.3 Task-by-task checks | 1305–1312 | [checking.md#73-task-by-task-checks](checking.md#73-task-by-task-checks) |
| &nbsp;&nbsp;&nbsp;&nbsp;Phase 0: Set-up and decisions | 1314–1322 | [checking.md#phase-0-set-up-and-decisions](checking.md#phase-0-set-up-and-decisions) |
| &nbsp;&nbsp;&nbsp;&nbsp;Phase 1: Platform access and offline replay | 1324–1434 | [checking.md#phase-1-platform-access-and-offline-replay](checking.md#phase-1-platform-access-and-offline-replay) |
| &nbsp;&nbsp;&nbsp;&nbsp;Phase 2: Skills (all offline, on the fake server) | 1436–1604 | [checking.md#phase-2-skills-all-offline-on-the-fake-server](checking.md#phase-2-skills-all-offline-on-the-fake-server) |
| &nbsp;&nbsp;&nbsp;&nbsp;Phase 3: Agent loop | 1606–1627 | [checking.md#phase-3-agent-loop](checking.md#phase-3-agent-loop) |
| &nbsp;&nbsp;&nbsp;&nbsp;Phase 4: Harness | 1629–1705 | [checking.md#phase-4-harness](checking.md#phase-4-harness) |
| &nbsp;&nbsp;7.4 Are your own tests any good? (Phase 5) | 1709–1738 | [checking.md#74-are-your-own-tests-any-good-phase-5](checking.md#74-are-your-own-tests-any-good-phase-5) |
| &nbsp;&nbsp;7.5 Gates before moving on | 1742–1754 | [checking.md#75-gates-before-moving-on](checking.md#75-gates-before-moving-on) |
| &nbsp;&nbsp;7.6 Before, during and after the live write run | 1758–1768 | [live-run.md#76-before-during-and-after-the-live-write-run](live-run.md#76-before-during-and-after-the-live-write-run) |
| 8. Safety on the shared platform | 1772–1788 | [safety.md#8-safety-on-the-shared-platform](safety.md#8-safety-on-the-shared-platform) |
| 9. Commands | 1792 | [architecture.md#9-commands](architecture.md#9-commands) (agent part) and [harness.md#9-commands](harness.md#9-commands) (harness part) |
| &nbsp;&nbsp;Agent | 1794–1802 | [architecture.md#agent](architecture.md#agent) |
| &nbsp;&nbsp;Harness | 1804–1820 | [harness.md#harness](harness.md#harness) |
| 10. Results so far | 1824–1852 | [plan-and-status.md#10-results-so-far](plan-and-status.md#10-results-so-far) |
| 11. The live write run | 1856–1892 | [live-run.md#11-the-live-write-run](live-run.md#11-the-live-write-run) |
| 12. Files you own | 1896–1910 | [plan-and-status.md#12-files-you-own](plan-and-status.md#12-files-you-own) |
| 13. Repo layout | 1914–1949 | [architecture.md#13-repo-layout](architecture.md#13-repo-layout) |
| 14. Known limits and open questions | 1953–1985 | [known-limits.md#14-known-limits-and-open-questions](known-limits.md#14-known-limits-and-open-questions) |
| 15. Changes after review | 1989–2089 | [history.md#15-changes-after-review](history.md#15-changes-after-review) |
| 16. Troubleshooting | 2093–2119 | [troubleshooting.md#16-troubleshooting](troubleshooting.md#16-troubleshooting) |
| Appendix A. Id cheat sheet (Keystone) | 2123–2175 | [background.md#appendix-a-id-cheat-sheet-keystone](background.md#appendix-a-id-cheat-sheet-keystone) |
| Appendix B. MCP tools the agent uses | 2177–2216 | [architecture.md#appendix-b-mcp-tools-the-agent-uses](architecture.md#appendix-b-mcp-tools-the-agent-uses) |

---

## 15. Changes after review

**Round 1: three independent reviewers** (correctness, safety, harness vs. the brief). Every finding was fixed:

| Area | What changed |
|---|---|
| Live restore | Restore runs in a nested `finally`, even if collecting the after-state fails. It puts back only this seat's own changes (write journal). Each row is re-read just before its write, so an edit another team made meanwhile is left alone and reported. It refuses snapshots with non-allow-listed ids and keeps going past a failed row. `harness restore` defaults to the fake target and needs `--live-apply` for live. |
| Write safety | `agent ask --apply` can't write live. `AS_ALLOW_WRITES` is read from the shell only. Every write is recorded before its confirming read. A failed confirm or pre-read becomes a `failed` record, and the rest of the tidy carries on. |
| Lost updates | The stale-row check covers `description` and `updated_at`, not only `folder_id`. |
| Duplicates | Only hash-matched duplicates are archived. Name + size matches are escalated as "suspected". A duplicate whose original isn't filed is escalated, not archived. Rows already archived are left alone. *(Superseded by decision C, Round 7: nothing is archived.)* |
| Drawings | `Rev B`, `rev-b`, `Rev. B` and `revision B` all mean B. Tags are matched whole. A found-but-unconfirmed revision is no longer reported as "not found". |
| Leak guard | E-sign rows are placeholders for skills, direct MCP reads and traces (`agent/privacy.py`). New canary task C3. |
| Loop | Turn cap = abort. Over-long tool results are valid JSON marked `truncated`. Malformed JSON-RPC errors still raise `McpError`. |
| Harness | Answer checks use the model's own text. Read tasks are checked against the database. The server write log is cross-checked. `records_must_include` and `run_must_not_contain` were added. One-shot faults are armed only for the agent. Fake-only tasks never run live. Set-up failures and missing run files count as failures. Calibration grew from 8 to 26 kinds of mistake, with exact-name matching. |

**Round 2: while mapping the gap report to the code** (a 9-agent read of the code and docs; every gap-to-code claim was checked by a skeptic reviewer). Fixes:

| Area | What changed |
|---|---|
| Out-of-seat check | "design" no longer matches "e-sign". Design-file requests are now recognised as the design-review app. |
| `drive_overview` | If the overview can't be read, it says so, instead of "the overview agrees (None)". |
| `find_drawing` | Odd revision names are reported (the flags were computed but never shown). Two parts sharing one code are refused. The wording is now right when every drawing is superseded. |
| Provenance notes | A duplicate's note says how it was matched and "not byte-verified", instead of "Score: 0". Notes give the threshold. *(Since decision C, Round 7, a possible copy gets no note; its escalation says how it was matched.)* |
| Wording | FAILED and conflict lines say what happened in plain words. |
| New tests of claims | Fault `clobber_after_write`. New tasks **TI5** (Q3 claim 3), **TI6** (a description is not an order), **D4** (401 + an error inside HTTP 200), **DU1** (`find_duplicates`). Two new routing questions. |
| Harness | `scope_ids` no longer mistakes folder ids in fault strings for file ids. |

**Round 3: fact-check of this README** (three reviewers checked 456 claims against the code; 44 needed fixing, mostly wording). Code fixes that came out of it:

| Area | What changed |
|---|---|
| No double writes | `agent/http.py` never resends a write after a 5xx or a timeout, only after a `429`. Before, a retry could have created a second permanent escalation or session. |
| Uncertain writes | A write whose call errored is journaled as `uncertain` (it may have landed), so restore and the records still treat it as ours. |
| Transport errors | Dropped connections (`ConnectionAbortedError` and friends) are caught. An unreachable platform becomes an `McpError`. State capture fails the run on an outage instead of treating it as a missing file. |

**Round 4: merging the Step 4 plan and the checking guide into this README.** The plan and guide were written before the code, so every statement was checked against the code before it moved here. Three more reviewers then checked the merged README (367 claims checked, 29 fixed). One code change came out of it:

| Area | What changed |
|---|---|
| Only TI2 writes live | A write task now runs on the live platform only if its task file says `live_write = true`, and only TI2 does. Before, TI3 or R4 could also have been run live, creating permanent escalations that would spoil the one TI2 run. (Since round 5 that task is TI2L.) |

After round 2, the live read-only check (22 Sept 2026, scripted model, 1 repeat) gave **10 / 10 pass with 0 write calls**. Re-run it with `python -m harness run D1 D2 D3 DU1 C1 C2 R1 R2 R3 R5 TI1 --target live --model scripted --repeat 1` (R5 was added in round 5). (The live command in [Commands](harness.md#9-commands) uses the real model and 5 repeats.)

**Round 5 (27 Sept): PR #3 and the follow-up, after the 23 Sept platform data change** (see the note at the top of [section 5](background.md#5-background-the-platform-the-scenario-and-the-research)). The follow-up was checked offline with `PYTHONIOENCODING=utf-8`: 21 / 21 tasks pass ×5, rescore identical, calibration 295 / 295 (296 before TI2L's wording check was dropped, see below), routes 10 / 10, smoke OK. Live (read-only): the new pre-flight says `pre-flight OK` with 9 warnings, where the old one failed with 10 problems.

| Area | What changed |
|---|---|
| New fixture (PR #3, Ashwani, 26 Sept) | `harness/fixtures/keystone/2026-09-26/`: 113 file rows, 10 access-log rows, 212 tools. The harness and fake server use it as the newest. |
| Re-derived tasks (PR #3) | C1, R2, R3, R4, TI1, TI2 and TI3 re-derived from the new fixture. The AI-help notes in their headers were restored on 27 Sept. |
| Idempotency (PR #3) | Files the agent filed itself (a `[Files Agent` note in the description) no longer count as `similar_file_in_folder` evidence, so a second tidy pass stays at 0 writes (`agent/skills/profiles.py`). |
| Ambiguous names (PR #3) | `resolve_file` returns every match; a filename shared by several files is refused with every candidate id listed, never silently picked (`remove_file`, `file_contents`). |
| Id lookup (27 Sept) | A record id in the request is matched first, so after *"Say which id you mean"* the user can give the id. New task **R5** (*"Delete 82f83d94-…"*) reaches the real delete refusal. |
| Pre-flight (27 Sept, decision A) | The 9 allow-listed originals must be in Incoming, unchanged and still `untriaged`. Other rows the fixture knows that haven't changed are **warnings** (printed, traced, not blocking); unknown or changed extras stay **problems** (`harness/preflight.py`, `python -m harness preflight`). |
| Scope rule (27 Sept, decision A) | Triage and the Escalator never write or escalate a file outside the run's allow-list: it is recorded `out_of_scope` and listed as *"left for a person: not in this run's scope"* (`agent/skills/triage.py`, `agent/skills/escalate.py`). |
| Live task (27 Sept, decision A) | New task field `live_allowlist` (offline rehearsal of the live cap; `agent/runtime.py`, `harness/tasks.py`, `harness/runner.py`). New task **TI2L** is the only `live_write` task: 5 moves of originals, 4 escalations (originals only), 9 out of scope, no `write_blocked`. TI2 is offline-only. `agent/__main__.py` now points at `python -m harness run TI2L --target live --live-apply`, and the runner's refusal names TI2L as the only live write task. |
| Same-name rule (27 Sept, decision B) | `_hold_name_collisions` in `agent/skills/triage.py`: a file is never filed into a folder that already holds, or is also getting, a file of the same name. The higher scorer is filed. The others (all of them on a tie, or when the folder already holds a file of that name) are escalated as possible copies, naming the other same-name ids and sizes. TI2 and TI3 now expect 5 moves and 13 escalations offline, and TI1 plans 5 moves and 13 not filed. The J-KNOB-09 and mill-cert 880-byte copies are escalated, not filed. |
| Review fixes (27 Sept) | An independent review of the whole change and a fact-check of this README found no blocker; these were fixed. **Triage:** a duplicate follows its original only when the original is filed in this run (the same-name and scope rules now run first; decision C, Round 7, later removed the follow step); only files the run may write take part in the same-name rule; an archived file in Incoming is reported "left alone" (it was wrongly reported SKIPPED). **Pre-flight:** also a problem now is a row in any folder that is new, changed or gone and shares a name or recorded hash with one of the 9, a fixture row that has left Incoming, a row moved into Incoming, and a fixture without a tool hash. Live on 27 Sept it still says `pre-flight OK` with the 9 copy warnings. **Tasks:** the loader refuses a second `live_write` task, or one without `live_allowlist`; TI2L checks an `out_of_scope` record for each of the 9 copies instead of the answer's wording (so calibration plants one mistake fewer: 295); the TI1–TI3 and TI2L headers mark decisions A and B as proposals and describe 23 Sept correctly. **Names:** *"the copy of <id>"* is not resolved by that id; a refusal for files with different names lists each name. |
| This README (27 Sept) | Section 5's note rewritten as an account of the platform's F3 repair (it had described the change as a forged hash); every "TI2 is the live write task" changed to TI2L; new safety rules; commands and snippet outputs re-run on the 26 Sept fixture. |

**Round 6: STRIDE security review (2 Oct 2026).** A STRIDE threat model of the agent and the harness found 54 threats (S1–S5, T1–T14, R1–R10, I1–I12, D1–D10, E1–E3). Each was reproduced offline with a proof-of-concept script, checked by a skeptic reviewer, fixed in code where that was safe, and re-checked with the same script; two more reviewers (security and regressions) then checked the combined change, and their findings were fixed too. Nothing here touched the live platform. The ids below are the threat ids; each guard in the code carries a `# STRIDE <id>` comment. The full report is [`docs/security/stride-review.md`](security/stride-review.md); it and the fixes need the team's review (see [12](plan-and-status.md#12-files-you-own)).

| Area | What changed |
|---|---|
| Live write gate (E1, E2, E3, S3) | `build()` accepts only the targets `live` and `fake`, refuses a fake server labelled `live` (and anything else labelled `fake`), and caps the allow-list to the 9 for any transport that is not the fake server. The write guard refuses a live write while no write journal is attached, refuses an `id` or any field other than `folder_id`, `description` and `is_archived` (since decision C, Round 7, only `folder_id` and `description`), and refuses an escalation about a file outside the allow-list. The MCP client refuses any tool that is neither one of the 3 write tools nor marked read-only. `--live-apply` without `--target live` is refused for `run` and `restore`, and restore refuses a snapshot taken on the other target. |
| Writes that may have landed (T1, T3) | Every write is journaled however its call ends (a cut-off reply, a malformed one, Ctrl-C), as `uncertain` when it errored. A get, create or update whose reply is not an object is a failed call (`bad_reply`), never a crash. An escalation or session create that failed in any way is read back; if it can't be found it is never sent again in the run, and a failed session stops further escalations. A failed escalation never stops the tidy, and the answer says so. A second tidy in one run plans from a fresh read. |
| Restore (T6, T9, D6) | Restore writes only the agent's 3 fields (2 since decision C, Round 7: `folder_id` and `description`), and only where they still hold our value. A description goes back to the text our note was appended to, so another team's edit made between the snapshot and our write survives (`kept_foreign_edits`); every other field goes back to its snapshot value, so an edited journal can't name a new value. Restore refuses a malformed, cut-off or edited snapshot or journal, refuses to run without a journal unless `--no-journal` is given, and carries on past any failed row. Snapshot and journal are written atomically. |
| Run once (R1) | A live write task is refused while any earlier live attempt (in any run set) may have sent a write. An attempt that provably sent nothing (set-up, login or pre-flight failed, or it stopped before its first write) is moved to `runs/<set>/<task>/attempt-<time>/` and the run goes ahead. `--set` must be a plain folder name under `runs/`. |
| Pre-flight and fixtures (T4, T8, T10, D4, D5, I7) | Pre-flight also fails on any folder added, removed, renamed, moved, archived or otherwise updated (one check, shared with PR #4), on two folders sharing a name, on a fixture older than 24 hours, and on a changed description or read-only mark of a tool the agent uses. Problems name who changed the row and print the recovery steps; rows of apps this seat can't open are named by their placeholder. A fixture is used only while it matches its manifest's hashes, capture folders are named by the UTC date, and a half-written capture or task file is refused with its name. Pre-flight still fails closed on purpose (14). |
| Triage and escalations (S1, T2, T7, D1, D9) | Only this seat's own escalations suppress a new one. Party, folder and uploader names are cleaned to one short printable line before they reach notes, escalations or the model, and the access log is called a lead. A "filed by us" note counts only when our own write made it, and one row is not enough to say where a kind of file lives. Uploaders are looked up only for files the run may act on. |
| What the model sees (T10, T13, I1, I5, I6, I8, I9, I12) | The platform's tool descriptions never reach the model and its input schemas only as structure (no titles, examples, comments or long enum text, at any depth). Skill arguments are checked against their schemas, and `explain_access` judges the user's own words. The leak guard keeps only an allow-list of fields on withheld rows; access-log rows name a file only through the leak-guarded list; other seats' escalations show no text; Party rows carry contact basics only; direct list calls may use only a fixed set of filters; a platform error message the agent doesn't know is withheld from the model, from records, from answers and from the MCP client's trace events. |
| Transport and model API (S5, D2, D9) | https only, and no redirect is ever followed, so the token and the model key can't be sent elsewhere. Each request and each model call has a wall-clock limit and a reply-size cap. A model call whose worst-case cost would pass the $ cap is not sent, at most 10 tool calls run per turn, and the storage overview is read once per run and counted against the call cap. |
| Secrets (I3, I4, I10, I11, R8) | Passwords, tokens and keys have a masked `repr`, so a traceback printed with its locals can't show them, and the login body is never kept in a local. The redactor masks encoded forms and more key names, and a `Bearer` value only where it is a credential. `.env` and run files are created owner-only on POSIX, with a warning if `.env` is readable by others. 7.2 reads the password from `.env` instead of the command line, block D is now `python scripts/secret_scan.py` (prints file and line, never the text), `.githooks/pre-commit` runs it on staged lines, and `.gitignore` also covers `.claude/settings.local.json` and `.envrc`. A read-only scan of the full git history found nothing (2 Oct). |
| Run files and scoring (R2, R3, R4, R5, R6, R7, R9, R10, D3, T5, T12, T14) | A run file that can't be read is one failed run, and a run counts only in its own folder. score.json records target, model, commit, fixture and tool hash, and flags runs judged against a task definition that differs from today's file (rescore warns about it but compares only what the run files decide). Errored and refused write attempts count in the write checks. A failed or interrupted pass keeps its records and writes; a stopped run's note says what was already written; every tool result the model saw is traced. The session is recorded, and its title names the run file it belongs to (`<set>/<task>/<n>`, also the manifest's `run_id`). CLI traces get a manifest and a run id, and a standalone restore records the paths and sha256 of its snapshot and journal and which ownership rule it used (`mode`). `escalation_for` matches the exact file id. Task files are validated (id = file name, types, no duplicates). TI2, TI2L and TI3 also check that every cited id exists, and TI2L checks for `write_blocked` by event kind. |
| Console and reports (S2, S4, D7, D10) | Platform text is printed without terminal escapes, bidi or zero-width characters (`agent/textsafe.py`), and report.md escapes table markup. The record trail is always last, with its count. Output the console can't encode is escaped instead of crashing. `.env` parsing handles a BOM, `export` and comments, and `nan`, `inf`, negative or zero caps and prices are refused. |
| Documented limits (T11, D5, I2) | Still no compare-and-set (platform request: `if_updated_at` or an ETag on `FileAttachment.update`); a field we did not send that changed inside our write window is now reported as `concurrent_change`. Pre-flight fails closed on purpose. Fixture capture now keeps only the access-log fields the agent reads; the committed rows were already clean (the platform returns `share_token` and `actor_ip` as null, and no row names a withheld file). See [14](known-limits.md#14-known-limits-and-open-questions). |

Fixed after the two reviews of the combined change: a create whose reply is not an object no longer escapes the escalation's error handling (T3, T1); restore no longer trusts a journal's `before` except for a description our note was appended to (T6); nested schema text is dropped (T10); a target label other than `live` or `fake` is refused (E1); the login body and headers no longer show in traceback locals (I4); records and answers no longer quote platform error text (I12); access-log rows without a file keep no details (I5); concurrent changes are reported (T11, partial); the run-once guard no longer blocks a re-run after an attempt that sent nothing (R1); rescore no longer reads today's task files (R2); fixture dates use UTC (T8); access-log and user ids resolve in the cited-id check (T5); `.gitignore`, the secret scan and the docs (I3, I11). Completed in the final check, from the skeptics' refined fixes: the overview read is counted (D2), the session title names its run (R3), restore records its inputs (R7), and the MCP client's trace events no longer keep platform error text (I12). Completed by hand: `agent/textsafe.py` now drops every invisible format character, tag characters included (T2). Still open (T2): a planted party or uploader name still appears in an escalation, as one labelled line.

Checked offline afterwards (3 Oct 2026, scripted model, 26 Sept fixture, Python 3.14; the harness checks were repeated under Python 3.11): `harness smoke` OK; all 21 tasks ×5 pass on every run; rescore IDENTICAL; calibration catches 355 of 355 planted mistakes (30 of the 31 kinds apply); routes 10 / 10; every threat's proof-of-concept script was re-run. The live platform was not used.

**Merged with PR #4 (3 Oct 2026).** PR #4 (Tanmay, 2 Oct: the 78 hand-written tests in `tests/`, the "same kind" and folder pre-flight checks, and decisions A, B and the ambiguity rule confirmed) and these fixes were combined. PR #4's folder check and STRIDE T4's are now one check in `harness/preflight.py`: a folder added, gone, renamed, moved or archived (`was renamed, moved or archived since the fixture`), any other update to a folder, two folders with one name, and a fixture with no folder table (one problem, not one per folder). The "same kind" problems name rows by their placeholder and say who changed them, like every other pre-flight problem. `scripts/secret_scan.py` now allows the exact dummy password used in `tests/test_redact.py` (and only that value), so block D, `--history` and the pre-commit hook say `no secrets found` again on the merged tree. No test file was changed for the merge: where a PR #4 test expected `renamed, moved or archived`, pre-flight's wording was changed instead. PR #4's document-kind check reads raw rows, so it judges withheld rows by their real titles (see [14](known-limits.md#14-known-limits-and-open-questions)). Re-checked offline on the merged tree (Python 3.14, and 3.11 for the tests and the harness checks): the 78 tests in `tests/` pass; `harness smoke` OK; all 21 tasks ×5 pass on every run; rescore IDENTICAL; calibration 355 of 355; routes 10 / 10; every threat's proof-of-concept script was re-run. The README gained the [Tests](plan-and-status.md#tests) and [Security review (STRIDE)](safety.md#security-review-stride) parts, `tests/README.md` now says what PR #4's tests cover and what is still to write, and the report is in `docs/security/stride-review.md`.

**Round 7: decision C (duplicates), 4 Oct 2026.** The duplicate rule changed: the agent never writes to a file because it looks like a copy of another, and it never archives. The rule and its known limits are in [triage step 3](architecture.md#triage_folder-evidence-scored-filing). It replaces the design in the Step 3 gap report and Rounds 1 and 5 (a hash-matched copy follows its original, is archived with a pointer, and its removal is escalated), for three reasons:
- **Bug B4.** The recorded hash is client-writable, so any seat could plant a file that steers a move or an archive. TI7's case 3 is that attack: a decoy in *Superseded* with the same recorded hash would have pulled a fileable Incoming file next to it and archived it.
- **Decision B.** The old follow step bypassed the same-name rule, so it could put two files with one name into one folder.
- **The live run.** If the platform removes the 880-byte PO copies, the PO hash becomes trusted again, and the old code would archive `82f83d94` during TI2L: a write the live plan does not expect, on a shared row.

Revisit it only if the platform computes a read-only hash on the server (request P10).

| Area | What changed |
|---|---|
| Triage (`agent/skills/triage.py`) | A file in a duplicate group (hash + size + name, or name + size) is planned as `escalate`, with a `recorded_duplicate` or `suspected_duplicate` clue naming the other file. Its escalation is written after the same-name rule, naming the other file's id and folder and its destination in this run. The follow step, the archive, the duplicate note, the `archive_duplicate` record, the "needs delete rights" escalation and `plan_duplicate` were removed. The module docstring states the rule and its known limits. |
| Write guard (`agent/guards.py`) | `UPDATE_FIELDS` is `folder_id` and `description`, so the guard refuses an archive on its own, before anything is sent. |
| Restore (`agent/snapshot.py`) | `RESTORE_FIELDS` follows the guard. A journal entry holding `is_archived` (written by older code) is still refused, nothing restored, but the message now says so and names the commit to restore it with (the run manifest's git commit, 8202cf8 or earlier). |
| Escalator (`agent/skills/escalate.py`) | The unused `needs_permission` reason was dropped; it mapped to `other`, the default, so nothing sent changes. |
| Fake server and task loader (`harness/fake_server.py`, `harness/tasks.py`) | An `extra_files` entry may give its own `id`, so two planted files can share a name. Two extras with one id are refused when the task loads, naming both files, and an extra whose id is already a row is refused by the fake server, never silently replaced. |
| Verifier (`harness/verifiers.py`, `harness/calibrate.py`) | An `unchanged` id that is not in the before-state now fails ("not in the before-state"). `plan_duplicate` and the `archived` key stay, so run files from before decision C rescore the same (all 1,221 local run files kept their verdicts). |
| Tasks | New **TI7** (4 planted trusted pairs, 2 passes; see [3.4](harness.md#34-the-tasks-22)). TI1, TI2, TI2L and TI3 gained a "decision C" header comment only; their graded fields are unchanged. |
| Docs | This README, `tests/README.md` (the 4 `FollowOriginalTests` and the new scenarios to write), `docs/security/stride-review.md` (E2, T6 and the counts) and one sentence of `docs/gap_report.md`. |

No test file was changed. The 4 `FollowOriginalTests` in `tests/test_escalate.py` assert the old rule and now fail; the team deletes two and rewrites two by hand (see [`tests/README.md`](../tests/README.md#decision-c-scenarios-12-not-covered-yet)). Checked offline on 4 Oct 2026 (scripted model, 26 Sept fixture, Python 3.14): `python -m unittest discover -s tests` runs 157 tests, and only those 4 fail; `harness smoke` OK; all 22 tasks ×5 pass on every run (110 run files); rescore IDENTICAL; calibration 377 of 377 (30 of the 31 kinds apply); routes 10 / 10; `secret_scan.py` finds nothing. With duplicate handling switched off, TI7 fails on 8 checks. The live platform was not used.

---

## Old README sections that the new README replaces

These sections were near the top of the old README. The new [README.md](../README.md) replaces them.

---

## Contents

- [Quick start](#quick-start) · [The idea in one minute](#the-idea-in-one-minute) · [Tests](plan-and-status.md#tests) · [Security review (STRIDE)](safety.md#security-review-stride)
- **How it works:** 1 · [Architecture](architecture.md#1-architecture) · 2 · [The skills](architecture.md#2-the-skills) · 3 · [The harness](harness.md#3-the-harness)
- **Why it exists:** 4 · [From gap report to code](gap-to-code.md#4-from-gap-report-to-code) (features A1–A14, platform requests P1–P13, roadmap) · 5 · [Background: platform, scenario, research, bugs](background.md#5-background-the-platform-the-scenario-and-the-research)
- **The plan and checking it:** 6 · [Step 4 plan: tasks, status, milestones, risks, staff questions](plan-and-status.md#6-the-step-4-plan-tasks-status-and-open-questions) · 7 · [How to check that each part works](checking.md#7-how-to-check-that-each-part-works)
- **Running it safely:** 8 · [Safety](safety.md#8-safety-on-the-shared-platform) · 9 · [Commands](harness.md#9-commands) · 10 · [Results](plan-and-status.md#10-results-so-far) · 11 · [The live write run](live-run.md#11-the-live-write-run)
- **Reference:** 12 · [Files you own](plan-and-status.md#12-files-you-own) · 13 · [Repo layout](architecture.md#13-repo-layout) · 14 · [Known limits](known-limits.md#14-known-limits-and-open-questions) · 15 · [Changes after review](#15-changes-after-review) · 16 · [Troubleshooting](troubleshooting.md#16-troubleshooting) · [Appendix A: ids](background.md#appendix-a-id-cheat-sheet-keystone) · [Appendix B: MCP tools](architecture.md#appendix-b-mcp-tools-the-agent-uses)

---

## Quick start

```bash
cp .env.example .env && chmod 600 .env   # then fill in AS_KEYSTONE_PASSWORD (and ANTHROPIC_API_KEY for the real model)
python -m harness smoke       # offline: run + score + rescore + calibrate, in one command
python -m agent --target fake ask "Find the drawing for part J-BRKT-04."   # offline answer
python -m agent smoke         # live, read-only: login, tool discovery, one read
python -m agent ask "Find the drawing for part J-BRKT-04."                 # live, read-only
```

`ask` never writes unless you ask for it: **plan-only is the default**. With no `ANTHROPIC_API_KEY`, it uses the offline *scripted* model (see [Models](architecture.md#the-two-models)).

`.env` holds the seat password and your model key, so keep it private to you. On Linux or macOS, `chmod 600 .env` does that, and the agent warns if other users can read it. On Windows, `copy .env.example .env` is enough when the repo is inside your own user folder (other users can't read it there); `icacls .env` shows who can.

---

## The idea in one minute

**The platform.** AgentSwitch is a shared business system (an ERP) with a Drive. Our seat, *Files*, may use the apps `drive`, `crm` and `agent`, and it cannot delete anything.

**The problem.** Files land in an **Incoming** folder, untriaged. People ask things like *"which drawing is current for this part?"*. The platform makes this hard:
- it stores **no file contents**;
- it has **no revision states**;
- it has **no guard against two people editing the same file**;
- different screens **disagree about how many files exist**;
- it **shows this seat titles of files from apps it isn't allowed to open**.

**The agent.** A language model (Claude) that can act **only** through a small set of hand-written **skills**, plus a few read-only lookups. Skills are plain Python. Skills decide, the model explains, and every decision is written down as a **decision record**. Anything the evidence can't support is **refused or handed to a person** (escalated), never guessed.

**The harness.** A test bench that asks the agent the same questions many times, on a **fake copy of the platform** (offline) or on the real one. It judges each run from the **database state before and after**. It also tests itself (**calibration**): it plants known mistakes in good runs and checks it catches every one.
