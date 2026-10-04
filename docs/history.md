# History

This file has 2 types of content:

- The [old-to-new section map](#old-to-new-section-map). It gives the new place of each section of the old README.
- These sections of the old README: 15, Contents, Quick start and The idea in one minute.

In this file, "the old README" is the README before the split. The ids, code, numbers and dates are from the old README. [The docs index](README.md#corrections-after-the-split) lists the facts that changed.

---

## Old-to-new section map

Each row is 1 heading of the old README. The rows are in the old order. *Old lines* are the line numbers in `README.md` at commit `9d6f962`. That commit is the last commit before the split. 1 arrow (↳) shows a subsection. 2 arrows (↳↳) show a subsection of a subsection.

In 3 rows, the title has no contraction and no semicolon, to keep it simple. The links of these rows go to the headings with the exact old text.

The README line numbers in [security/stride-review.md](security/stride-review.md) come from an earlier README. Thus, they can be different from the line numbers in this table. To find a section from that file, use its section number and title.

| Old README section | Old lines | Now in |
|---|---|---|
| Files Agent — AgentSwitch Seat 20 (Team 20) (title and front matter) | 1–15 | [README.md](../README.md) (title) and [plan-and-status.md#old-readme-front-matter-before-the-split](plan-and-status.md#old-readme-front-matter-before-the-split) (lines 3–15) |
| Contents | 19–26 | [history.md#contents](history.md#contents) |
| Quick start | 30–42 | [history.md#quick-start](history.md#quick-start) |
| The idea in one minute | 46–59 | [history.md#the-idea-in-one-minute](history.md#the-idea-in-one-minute) |
| Tests | 63–105 | [plan-and-status.md#tests](plan-and-status.md#tests) |
| Security review (STRIDE) | 109–134 | [safety.md#security-review-stride](safety.md#security-review-stride) |
| ↳ *Before the live write run* (last paragraph) | 136 | [live-run.md#before-the-live-write-run](live-run.md#before-the-live-write-run) |
| 1. Architecture | 140 | [architecture.md#1-architecture](architecture.md#1-architecture) |
| ↳ 1.1 The big picture | 142–180 | [architecture.md#11-the-big-picture](architecture.md#11-the-big-picture) |
| ↳ 1.2 The life of one question | 182–195 | [architecture.md#12-the-life-of-one-question](architecture.md#12-the-life-of-one-question) |
| ↳ 1.3 The life of one write | 197–210 | [architecture.md#13-the-life-of-one-write](architecture.md#13-the-life-of-one-write) |
| ↳ 1.4 The building blocks | 212–232 | [architecture.md#14-the-building-blocks](architecture.md#14-the-building-blocks) |
| ↳ The two models | 234–237 | [architecture.md#the-two-models](architecture.md#the-two-models) |
| ↳ The system prompt, in short | 239–241 | [architecture.md#the-system-prompt-in-short](architecture.md#the-system-prompt-in-short) |
| 2. The skills | 245–260 | [architecture.md#2-the-skills](architecture.md#2-the-skills) |
| ↳ `find_drawing`: part → current drawing | 262–283 | [architecture.md#find_drawing-part--current-drawing](architecture.md#find_drawing-part--current-drawing) |
| ↳ `triage_folder`: evidence-scored filing | 285–311 | [architecture.md#triage_folder-evidence-scored-filing](architecture.md#triage_folder-evidence-scored-filing) |
| ↳↳ How a file is scored | 313–330 | [architecture.md#how-a-file-is-scored](architecture.md#how-a-file-is-scored) |
| ↳ `find_duplicates` | 332–342 | [architecture.md#find_duplicates](architecture.md#find_duplicates) |
| ↳ `drive_overview`: the platform contradicts itself | 344–353 | [architecture.md#drive_overview-the-platform-contradicts-itself](architecture.md#drive_overview-the-platform-contradicts-itself) |
| ↳ `explain_access`, `remove_file`, `file_contents`: refusing with evidence | 355–367 | [architecture.md#explain_access-remove_file-file_contents-refusing-with-evidence](architecture.md#explain_access-remove_file-file_contents-refusing-with-evidence) |
| ↳ `list_files`: the leak guard in action | 369–372 | [architecture.md#list_files-the-leak-guard-in-action](architecture.md#list_files-the-leak-guard-in-action) |
| ↳ Helper modules (not callable by the model) | 374–381 | [architecture.md#helper-modules-not-callable-by-the-model](architecture.md#helper-modules-not-callable-by-the-model) |
| 3. The harness | 385 | [harness.md#3-the-harness](harness.md#3-the-harness) |
| ↳ 3.1 Why a harness | 387–389 | [harness.md#31-why-a-harness](harness.md#31-why-a-harness) |
| ↳ 3.2 The life of one run | 391–403 | [harness.md#32-the-life-of-one-run](harness.md#32-the-life-of-one-run) |
| ↳ 3.3 The parts | 405–420 | [harness.md#33-the-parts](harness.md#33-the-parts) |
| ↳ 3.4 The tasks (22) | 422–467 | [harness.md#34-the-tasks-22](harness.md#34-the-tasks-22) |
| ↳ 3.5 The verifiers (always on) | 469–481 | [harness.md#35-the-verifiers-always-on](harness.md#35-the-verifiers-always-on) |
| ↳ 3.6 Scoring | 483–485 | [harness.md#36-scoring](harness.md#36-scoring) |
| ↳ 3.7 Calibration: does the harness catch mistakes? | 487–505 | [harness.md#37-calibration-does-the-harness-catch-mistakes](harness.md#37-calibration-does-the-harness-catch-mistakes) |
| ↳ 3.8 The fake server's faults | 507–521 | [harness.md#38-the-fake-servers-faults](harness.md#38-the-fake-servers-faults) |
| ↳ 3.9 Run files | 523–529 | [harness.md#39-run-files](harness.md#39-run-files) |
| 4. From gap report to code | 533–537 | [gap-to-code.md#4-from-gap-report-to-code](gap-to-code.md#4-from-gap-report-to-code) |
| ↳ 4.1 At a glance | 539–559 | [gap-to-code.md#41-at-a-glance](gap-to-code.md#41-at-a-glance) |
| ↳ 4.2 What the agent builds (Q2 "ours to build") | 561 | [gap-to-code.md#42-what-the-agent-builds-q2-ours-to-build](gap-to-code.md#42-what-the-agent-builds-q2-ours-to-build) |
| ↳↳ A. Part → drawing resolver (gaps 2–3) ✅ | 563–568 | [gap-to-code.md#a-part--drawing-resolver-gaps-23-](gap-to-code.md#a-part--drawing-resolver-gaps-23-) |
| ↳↳ B. Evidence-scored Incoming triage (gap 4) ✅ | 570–582 | [gap-to-code.md#b-evidence-scored-incoming-triage-gap-4-](gap-to-code.md#b-evidence-scored-incoming-triage-gap-4-) |
| ↳↳ C. Undo log and clobber check (gap 6) ✅ checks · 🟡 restore not yet run live | 584–593 | [gap-to-code.md#c-undo-log-and-clobber-check-gap-6--checks---restore-not-yet-run-live](gap-to-code.md#c-undo-log-and-clobber-check-gap-6--checks---restore-not-yet-run-live) |
| ↳↳ D. Scheduled triage via `AgentTask` ⛔ | 595–596 | [gap-to-code.md#d-scheduled-triage-via-agenttask-](gap-to-code.md#d-scheduled-triage-via-agenttask-) |
| ↳↳ E. Calling the MCP tools safely ✅ (skills) · 🟡 (the model's own calls) | 598–603 | [gap-to-code.md#e-calling-the-mcp-tools-safely--skills---the-models-own-calls](gap-to-code.md#e-calling-the-mcp-tools-safely--skills---the-models-own-calls) |
| ↳ 4.3 The seven gaps (Q1): what the benchmarks do, and our answer | 605–617 | [gap-to-code.md#43-the-seven-gaps-q1-what-the-benchmarks-do-and-our-answer](gap-to-code.md#43-the-seven-gaps-q1-what-the-benchmarks-do-and-our-answer) |
| ↳ 4.4 Platform work we asked for (Q2 "platform work") | 619–632 | [gap-to-code.md#44-platform-work-we-asked-for-q2-platform-work](gap-to-code.md#44-platform-work-we-asked-for-q2-platform-work) |
| ↳ 4.5 What our agent can do that theirs cannot (Q3) | 634–640 | [gap-to-code.md#45-what-our-agent-can-do-that-theirs-cant-q3](gap-to-code.md#45-what-our-agent-can-do-that-theirs-cant-q3) |
| ↳ 4.6 The agent's features A1–A14 | 642–665 | [gap-to-code.md#46-the-agents-features-a1a14](gap-to-code.md#46-the-agents-features-a1a14) |
| ↳ 4.7 Platform change requests P1–P13 | 667–687 | [gap-to-code.md#47-platform-change-requests-p1p13](gap-to-code.md#47-platform-change-requests-p1p13) |
| ↳ 4.8 Roadmap | 689–702 | [gap-to-code.md#48-roadmap](gap-to-code.md#48-roadmap) |
| 5. Background: the platform, the scenario and the research | 706–727 | [background.md#5-background-the-platform-the-scenario-and-the-research](background.md#5-background-the-platform-the-scenario-and-the-research) |
| ↳ 5.1 Five facts that shape Step 4 | 729–745 | [background.md#51-five-facts-that-shape-step-4](background.md#51-five-facts-that-shape-step-4) |
| ↳ 5.2 Platform facts (Keystone, measured live 22 Sept 2026) | 747–779 | [background.md#52-platform-facts-keystone-measured-live-22-sept-2026](background.md#52-platform-facts-keystone-measured-live-22-sept-2026) |
| ↳ 5.3 The graded scenario | 781–823 | [background.md#53-the-graded-scenario](background.md#53-the-graded-scenario) |
| ↳ 5.4 Benchmark products and what we borrow | 825–857 | [background.md#54-benchmark-products-and-what-we-borrow](background.md#54-benchmark-products-and-what-we-borrow) |
| ↳ 5.5 Research behind the design | 859–869 | [background.md#55-research-behind-the-design](background.md#55-research-behind-the-design) |
| ↳ 5.6 Bugs raised | 871–952 | [bugs.md#56-bugs-raised](bugs.md#56-bugs-raised) |
| 6. The Step 4 plan: tasks, status and open questions | 956–960 | [plan-and-status.md#6-the-step-4-plan-tasks-status-and-open-questions](plan-and-status.md#6-the-step-4-plan-tasks-status-and-open-questions) |
| ↳ 6.1 What is graded, and the ground rules | 962–973 | [plan-and-status.md#61-whats-graded-and-the-ground-rules](plan-and-status.md#61-whats-graded-and-the-ground-rules) |
| ↳↳ *Ground rules* 1–4 | 975–982 | [safety.md#ground-rules-old-section-61](safety.md#ground-rules-old-section-61) |
| ↳ 6.2 Task list and status | 984–991 | [plan-and-status.md#62-task-list-and-status](plan-and-status.md#62-task-list-and-status) |
| ↳↳ Phase 0 — Set-up and decisions (0.5 day) | 993–1001 | [plan-and-status.md#phase-0--set-up-and-decisions-05-day](plan-and-status.md#phase-0--set-up-and-decisions-05-day) |
| ↳↳ Phase 1 — Platform access and offline replay (2 days) | 1003–1014 | [plan-and-status.md#phase-1--platform-access-and-offline-replay-2-days](plan-and-status.md#phase-1--platform-access-and-offline-replay-2-days) |
| ↳↳ Phase 2 — Skills (4 days) | 1016–1030 | [plan-and-status.md#phase-2--skills-4-days](plan-and-status.md#phase-2--skills-4-days) |
| ↳↳ Phase 3 — Agent loop (1.5 days) | 1032–1041 | [plan-and-status.md#phase-3--agent-loop-15-days](plan-and-status.md#phase-3--agent-loop-15-days) |
| ↳↳ Phase 4 — Harness (3 days) | 1043–1057 | [plan-and-status.md#phase-4--harness-3-days](plan-and-status.md#phase-4--harness-3-days) |
| ↳↳ Phase 5 — Your tests (hand-written, 1.5 days spread across Phases 1–4) | 1059–1074 | [plan-and-status.md#phase-5--your-tests-hand-written-15-days-spread-across-phases-14](plan-and-status.md#phase-5--your-tests-hand-written-15-days-spread-across-phases-14) |
| ↳↳ Phase 6 — Evaluate and submit (1.5 days) | 1076–1085 | [plan-and-status.md#phase-6--evaluate-and-submit-15-days](plan-and-status.md#phase-6--evaluate-and-submit-15-days) |
| ↳ 6.3 Milestones | 1087–1098 | [plan-and-status.md#63-milestones](plan-and-status.md#63-milestones) |
| ↳ 6.4 Must / Should / Could | 1100–1127 | [plan-and-status.md#64-must--should--could](plan-and-status.md#64-must--should--could) |
| ↳ 6.5 Risks and how the code handles them | 1129–1140 | [plan-and-status.md#65-risks-and-how-the-code-handles-them](plan-and-status.md#65-risks-and-how-the-code-handles-them) |
| ↳ 6.6 Questions for staff | 1142–1155 | [plan-and-status.md#66-questions-for-staff](plan-and-status.md#66-questions-for-staff) |
| 7. How to check that each part works | 1159–1178 | [checking.md#7-how-to-check-that-each-part-works](checking.md#7-how-to-check-that-each-part-works) |
| ↳ 7.1 Three ways to check anything | 1182–1203 | [checking.md#71-three-ways-to-check-anything](checking.md#71-three-ways-to-check-anything) |
| ↳ 7.2 Ground truth: ask the platform directly | 1207–1301 | [checking.md#72-ground-truth-ask-the-platform-directly](checking.md#72-ground-truth-ask-the-platform-directly) |
| ↳ 7.3 Task-by-task checks | 1305–1312 | [checking.md#73-task-by-task-checks](checking.md#73-task-by-task-checks) |
| ↳↳ Phase 0: Set-up and decisions | 1314–1322 | [checking.md#phase-0-set-up-and-decisions](checking.md#phase-0-set-up-and-decisions) |
| ↳↳ Phase 1: Platform access and offline replay | 1324–1434 | [checking.md#phase-1-platform-access-and-offline-replay](checking.md#phase-1-platform-access-and-offline-replay) |
| ↳↳ Phase 2: Skills (all offline, on the fake server) | 1436–1604 | [checking.md#phase-2-skills-all-offline-on-the-fake-server](checking.md#phase-2-skills-all-offline-on-the-fake-server) |
| ↳↳ Phase 3: Agent loop | 1606–1627 | [checking.md#phase-3-agent-loop](checking.md#phase-3-agent-loop) |
| ↳↳ Phase 4: Harness | 1629–1705 | [checking.md#phase-4-harness](checking.md#phase-4-harness) |
| ↳ 7.4 Are your own tests any good? (Phase 5) | 1709–1738 | [checking.md#74-are-your-own-tests-any-good-phase-5](checking.md#74-are-your-own-tests-any-good-phase-5) |
| ↳ 7.5 Gates before moving on | 1742–1754 | [checking.md#75-gates-before-moving-on](checking.md#75-gates-before-moving-on) |
| ↳ 7.6 Before, during and after the live write run | 1758–1768 | [live-run.md#76-before-during-and-after-the-live-write-run](live-run.md#76-before-during-and-after-the-live-write-run) |
| 8. Safety on the shared platform | 1772–1788 | [safety.md#8-safety-on-the-shared-platform](safety.md#8-safety-on-the-shared-platform) |
| 9. Commands | 1792 | [architecture.md#9-commands](architecture.md#9-commands) (agent part) and [harness.md#9-commands](harness.md#9-commands) (harness part) |
| ↳ Agent | 1794–1802 | [architecture.md#agent](architecture.md#agent) |
| ↳ Harness | 1804–1820 | [harness.md#harness](harness.md#harness) |
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

**Round 1: 3 independent reviewers.** The reviewers examined correctness, safety, and the harness against the brief. They found problems, and each problem has a fix in the table below:

| Area | What changed |
|---|---|
| Live restore | Restore runs in a nested `finally`. It runs even when the step that collects the after-state fails. It restores only the fields that this seat changed, as the write journal records them.<br>Restore reads each row again just before it writes the row. If another team edited the row in that time, restore keeps that edit and reports it. Restore refuses a snapshot that has an id outside the allow-list. If a row fails, restore continues with the next row. By default, `harness restore` uses the fake target. For the live target, it needs `--live-apply`. |
| Write safety | `agent ask --apply` cannot write on the live platform. The value of `AS_ALLOW_WRITES` comes only from the shell. The agent records each write before the read that confirms it. A failed confirm or pre-read becomes a `failed` record. The rest of the tidy continues. |
| Lost updates | The stale-row check covers `description` and `updated_at`, not only `folder_id`. |
| Duplicates | The agent archives only the duplicates that match by hash. The agent escalates a match on name + size as "suspected". If this run does not move the original of a duplicate to a folder, the agent escalates the duplicate and does not archive it. The agent does not change an archived row. *(Decision C, Round 7, replaces this rule. Now the agent archives nothing.)* |
| Drawings | `Rev B`, `rev-b`, `Rev. B` and `revision B` all mean B. The match uses whole tags only. If the agent finds a revision but cannot confirm it, it no longer reports the revision as "not found". |
| Leak guard | Skills, direct MCP reads and traces receive a placeholder in place of each E-sign row (`agent/privacy.py`). C3 is a new canary task. |
| Loop | The turn cap now causes an abort. A tool result that is too long becomes valid JSON with the mark `truncated`. A malformed JSON-RPC error still raises `McpError`. |
| Harness | Answer checks use the text that the model wrote. The harness checks read tasks against the database. The harness also cross-checks the write log of the server. The harness has the new keys `records_must_include` and `run_must_not_contain`. The harness arms one-shot faults only for the agent.<br>Fake-only tasks never run on the live platform. A set-up failure counts as a failure. A run file that does not exist also counts as a failure. Calibration grew from 8 to 26 kinds of mistake, and it uses exact-name matches. |

**Round 2: the map of the gap report to the code.** 9 agents read the code and the docs. A skeptical reviewer checked every gap-to-code claim. The fixes are:

| Area | What changed |
|---|---|
| Out-of-seat check | "design" no longer matches "e-sign". The check now recognises a request about a design file as a request for the design-review app. |
| `drive_overview` | If it cannot read the overview, it says so. Before, it said "the overview agrees (None)". |
| `find_drawing` | It reports unusual revision names. Before, it computed the flags but did not show them. If 2 parts share 1 code, it refuses them. The text is now correct when every drawing is superseded. |
| Provenance notes | The note on a duplicate says how the agent matched it, and it says "not byte-verified". Before, the note said "Score: 0". Notes give the threshold. *(Since decision C, Round 7, a possible copy has no note. Its escalation says how the agent matched it.)* |
| Wording | FAILED lines and conflict lines say what happened in plain words. |
| New tests of claims | There is a new fault, `clobber_after_write`. The new tasks are **TI5** (Q3 claim 3), **TI6** (a description is not an order), **D4** (401 + an error inside HTTP 200) and **DU1** (`find_duplicates`). There are 2 new route questions. |
| Harness | `scope_ids` no longer reads a folder id in a fault string as a file id. |

**Round 3: fact-check of the old README.** 3 reviewers checked 456 claims against the code. 44 claims needed a fix, and most of these fixes changed only words. The code fixes from this round are:

| Area | What changed |
|---|---|
| No double writes | `agent/http.py` never sends a write again after a 5xx or a timeout. It sends a write again only after a `429`. Before this fix, a retry could make a second permanent escalation or a second session. |
| Uncertain writes | If the call for a write ends in an error, the journal records the write as `uncertain`. Possibly, the platform did the write. Thus, restore and the records still treat the write as a write of this seat. |
| Transport errors | The code now catches dropped connections (`ConnectionAbortedError` and similar errors). If the platform is unreachable, the result is an `McpError`. If there is an outage, the capture of the state fails the run. It does not treat the outage as a file that does not exist. |

**Round 4: the merge of the Step 4 plan and the guide for checks into the old README.** The plan and the guide are older than the code. Thus, a check compared every statement with the code before the move into the README. Then 3 more reviewers checked the merged README. They checked 367 claims, and the reviewers fixed 29 of these claims. Round 4 made 1 code change:

| Area | What changed |
|---|---|
| Only TI2 writes live | A write task now runs on the live platform only if its task file says `live_write = true`. Only TI2 says this. Before, TI3 or R4 could also run on the live platform. They could make permanent escalations, and these escalations would make the single TI2 run not valid. (Since round 5, that task is TI2L.) |

After round 2, the live read-only check gave **10 / 10 pass with 0 write calls**. It ran on 22 Sept 2026, with the scripted model and 1 repeat. To do this check again, use `python -m harness run D1 D2 D3 DU1 C1 C2 R1 R2 R3 R5 TI1 --target live --model scripted --repeat 1`. Round 5 added R5. The live command in [Commands](harness.md#9-commands) uses the real model and 5 repeats.

**Round 5 (27 Sept): PR #3 and the follow-up, after the change to the platform data on 23 Sept.** For the data change, refer to the note at the top of [section 5](background.md#5-background-the-platform-the-scenario-and-the-research). An offline check of the follow-up used `PYTHONIOENCODING=utf-8`. The results were:

- 21 / 21 tasks pass ×5.
- Rescore is identical.
- Calibration is 295 / 295. It was 296 before TI2L lost its check on the words of the answer (refer to the table below).
- Routes are 10 / 10.
- Smoke is OK.

On the live platform (read-only), the new pre-flight says `pre-flight OK` with 9 warnings. The old pre-flight failed with 10 problems.

| Area | What changed |
|---|---|
| New fixture (PR #3, Ashwani, 26 Sept) | `harness/fixtures/keystone/2026-09-26/` has 113 file rows, 10 access-log rows and 212 tools. The harness and the fake server use it as the newest fixture. |
| Re-derived tasks (PR #3) | PR #3 re-derived C1, R2, R3, R4, TI1, TI2 and TI3 from the new fixture. On 27 Sept, the follow-up added the AI-help notes again to their headers. |
| Idempotency (PR #3) | A file that the agent moved itself has a `[Files Agent` note in its description. Such a file no longer counts as `similar_file_in_folder` evidence. Thus, a second tidy pass stays at 0 writes (`agent/skills/profiles.py`). |
| Ambiguous names (PR #3) | `resolve_file` returns every match. If several files share a filename, the agent refuses the request and lists every candidate id. It never picks one file silently (`remove_file`, `file_contents`). |
| Id lookup (27 Sept) | The agent first tries to match a record id in the request. Thus, after *"Say which id you mean"*, the user can give the id. The new task **R5** (*"Delete 82f83d94-…"*) reaches the real delete refusal. |
| Pre-flight (27 Sept, decision A) | The 9 allow-listed originals must be in Incoming, unchanged and still `untriaged`. Other rows that the fixture contains and that did not change are **warnings**. Pre-flight prints and traces a warning, but a warning does not block the run. Unknown or changed extra rows stay **problems** (`harness/preflight.py`, `python -m harness preflight`). |
| Scope rule (27 Sept, decision A) | Triage and the Escalator never write or escalate a file outside the allow-list of the run. They record such a file as `out_of_scope`. They list it as *"left for a person: not in this run's scope"* (`agent/skills/triage.py`, `agent/skills/escalate.py`). |
| Live task (27 Sept, decision A) | There is a new task field, `live_allowlist`. It rehearses the live cap offline (`agent/runtime.py`, `harness/tasks.py`, `harness/runner.py`). The new task **TI2L** is the only `live_write` task. It has 5 moves of originals, 4 escalations (originals only), 9 files out of scope and no `write_blocked`.<br>TI2 is offline-only. `agent/__main__.py` now points to `python -m harness run TI2L --target live --live-apply`. The refusal of the runner names TI2L as the only live write task. |
| Same-name rule (27 Sept, decision B) | This rule is `_hold_name_collisions` in `agent/skills/triage.py`. The agent never moves a file into a folder that already holds a file of the same name. The rule also applies to a folder that receives a file of the same name in the same run. The file with the higher score moves into the folder. The agent escalates the others as possible copies, and names the ids and sizes of the other files with that name.<br>On a tie, the agent escalates all of the files. It also escalates all of them when the folder already holds a file of that name.<br>Offline, TI2 and TI3 now expect 5 moves and 13 escalations. TI1 plans 5 moves and 13 files not filed. The agent escalates the 880-byte copies of J-KNOB-09 and of the mill certificate, and does not move them. |
| Review fixes (27 Sept) | An independent review of the whole change found no blocker. A fact-check of the old README also found no blocker. The fixes below resolved the findings.<br>**Triage:** A duplicate follows its original only when this run moves the original to a folder. The same-name and scope rules now run first. Decision C, Round 7, later removed the follow step. The same-name rule applies only to the files that the run can write. The agent reports an archived file in Incoming as `left alone: it is already archived.` Before, it reported the file as SKIPPED, which was wrong.<br>**Pre-flight:** Pre-flight now finds a problem in 4 more cases. Case 1: a new, changed or gone row in any folder shares a name or a recorded hash with one of the 9. Case 2: a fixture row is no longer in Incoming. Case 3: a row moved into Incoming. Case 4: the fixture has no tool hash. On 27 Sept, the live pre-flight still said `pre-flight OK` with the 9 copy warnings.<br>**Tasks:** The loader refuses a second `live_write` task. It also refuses a `live_write` task without `live_allowlist`. TI2L now checks for an `out_of_scope` record for each of the 9 copies. Before, it checked the words of the answer. Thus, calibration plants 1 mistake fewer: 295.<br>The headers of TI1–TI3 and TI2L mark decisions A and B as proposals. They also describe 23 Sept correctly.<br>**Names:** The agent does not resolve *"the copy of `<id>`"* by that id. If the agent refuses a request for files with different names, the refusal lists each name. |
| The old README (27 Sept) | The note of section 5 is now an account of the F3 repair of the platform. Before, the note described the change as a forged hash. Each "TI2 is the live write task" changed to TI2L. There are new safety rules. The commands and the snippet outputs are from a new run on the 26 Sept fixture. |

**Round 6: STRIDE security review (2 Oct 2026).** A STRIDE threat model of the agent and the harness found 54 threats. Their ids are S1–S5, T1–T14, R1–R10, I1–I12, D1–D10 and E1–E3. For each threat, the review did these steps:

1. A proof-of-concept script reproduced the threat offline.
2. A skeptical reviewer checked it.
3. Where a fix in code was safe, the review added the fix to the code.
4. The same script checked the threat again.

Then 2 more reviewers (security and regressions) checked the combined change. The round also fixed their findings. Nothing in this round used the live platform.

The ids in the table below are the threat ids. Each guard in the code has a `# STRIDE <id>` comment. The full report is [`docs/security/stride-review.md`](security/stride-review.md). The report and the fixes need a review by the team (refer to [12](plan-and-status.md#12-files-you-own)).

| Area | What changed |
|---|---|
| Live write gate (E1, E2, E3, S3) | `build()` accepts only the targets `live` and `fake`. It refuses a fake server with the label `live`. It also refuses anything else with the label `fake`. For any transport that is not the fake server, it caps the allow-list to the 9. The write guard refuses a live write if there is no attached write journal.<br>It refuses an `id`. It refuses any field other than `folder_id`, `description` and `is_archived` (since decision C, Round 7, only `folder_id` and `description`). It refuses an escalation about a file outside the allow-list. The MCP client refuses any tool that is not one of the 3 write tools and does not have the read-only mark.<br>`run` and `restore` refuse `--live-apply` without `--target live`. Restore refuses a snapshot from the other target. |
| Writes that may have landed (T1, T3) | The journal records every write, however its call ends (a cut-off reply, a malformed reply or Ctrl-C). If the call gave an error, the journal records the write as `uncertain`. If the reply to a get, create or update is not an object, the call counts as failed (`bad_reply`). It never causes a crash.<br>If the creation of an escalation or a session fails in any way, the agent reads the list again to find it. If the agent cannot find it, the agent never sends it again in the run. A failed session stops all further escalations. A failed escalation never stops the tidy, and the answer says so. A second tidy in one run makes its plan from a new read. |
| Restore (T6, T9, D6) | Restore writes only the 3 fields of the agent (2 since decision C, Round 7: `folder_id` and `description`). It writes a field only where the field still holds the value of the agent. Restore restores a description to the text to which the agent added its note. Thus, if another team edited the description between the snapshot and the agent's write, that edit stays (`kept_foreign_edits`). Restore restores every other field to its value in the snapshot. Thus, an edited journal cannot name a new value.<br>Restore refuses a malformed, cut-off or edited snapshot or journal. It refuses to run without a journal, unless you give `--no-journal`. It continues past any failed row. The snapshot and the journal have atomic writes. |
| Run once (R1) | The harness refuses a live write task if any earlier live attempt (in any run set) possibly sent a write. Some attempts provably sent nothing: set-up, login or pre-flight failed, or the attempt stopped before its first write. The harness moves such an attempt to `runs/<set>/<task>/attempt-<time>/`. Then the run starts. `--set` must be a plain folder name under `runs/`. |
| Pre-flight and fixtures (T4, T8, T10, D4, D5, I7) | Pre-flight also fails if someone added, removed, renamed, moved, archived or otherwise updated a folder. This is 1 check that PR #4 also uses. Pre-flight also fails if 2 folders have the same name. It fails on a fixture older than 24 hours. It fails if the description or the read-only mark of a tool that the agent uses changed.<br>A problem names who changed the row, and it prints the recovery steps. If this seat cannot open the app of a row, the problem names the row by its placeholder.<br>The harness uses a fixture only while the fixture matches the hashes of its manifest. Each capture folder has the UTC date as its name. The harness refuses a half-written capture or task file, and gives its name. Pre-flight still fails closed on purpose (14). |
| Triage and escalations (S1, T2, T7, D1, D9) | Only escalations from this seat suppress a new escalation. Before a Party, folder or uploader name reaches notes, escalations or the model, the agent cleans it to 1 short printable line. The agent calls the access log a lead. A note that says that the agent moved the file counts only when the agent's own write made it. 1 row is not enough to say where a kind of file belongs. The agent finds the uploaders only for the files that the run can act on. |
| What the model sees (T10, T13, I1, I5, I6, I8, I9, I12) | The tool descriptions of the platform never reach the model. The input schemas reach the model only as structure, with no titles, examples, comments or long enum text, at any depth. The agent checks skill arguments against their schemas. `explain_access` examines the words of the user.<br>The leak guard keeps only an allow-list of fields on withheld rows. Access-log rows name a file only through the leak-guarded list. The escalations of other seats show no text.<br>Party rows have only basic contact data. 4 of the 6 direct list tools accept only a fixed set of filters. The agent withholds a platform error message that it does not recognise. That message does not go to the model, the records, the answers or the trace events of the MCP client. |
| Transport and model API (S5, D2, D9) | All connections use https only, and they never follow a redirect. Thus, the token and the model key cannot go to a different place. Each request and each model call has a wall-clock limit and a reply-size cap. If the worst-case cost of a model call is more than the $ cap, the agent does not send the call. At most 10 tool calls run in each turn. The agent reads the storage overview once per run, and it counts this read against the call cap. |
| Secrets (I3, I4, I10, I11, R8) | Passwords, tokens and keys have a masked `repr`. Thus, a traceback that prints its locals cannot show them. The code never keeps the login body in a local variable. The redactor masks encoded forms and more key names. It masks a `Bearer` value only where the value is a credential.<br>On POSIX, new `.env` files and new run files are owner-only. If other users can read `.env`, there is a warning. 7.2 reads the password from `.env`, not from the command line.<br>Block D is now `python scripts/secret_scan.py`. It prints the file and the line, never the text. `.githooks/pre-commit` runs it on staged lines. `.gitignore` also covers `.claude/settings.local.json` and `.envrc`. A read-only scan of the full git history found nothing (2 Oct). |
| Run files and scoring (R2, R3, R4, R5, R6, R7, R9, R10, D3, T5, T12, T14) | If the harness cannot read a run file, that is 1 failed run. A run counts only in its own folder. score.json records the target, model, commit, fixture and tool hash. It flags runs that the harness scored against a task definition that is different from the current task file. Rescore warns about this, but it compares only what the run files decide.<br>Write attempts that gave an error or a refusal count in the write checks. A failed or interrupted pass keeps its records and writes. The note of a stopped run says what the run already wrote.<br>The trace has every tool result that the model saw. The run records the session. The title of the session names the run file of the session (`<set>/<task>/<n>`, also the `run_id` of the manifest). CLI traces receive a manifest and a run id.<br>A standalone restore records the paths and sha256 of its snapshot and journal. It also records which ownership rule it used (`mode`). `escalation_for` matches the exact file id.<br>The harness validates the task files (id = file name, types, no duplicates). TI2, TI2L and TI3 also check that every cited id exists. TI2L checks for `write_blocked` by event kind. |
| Console and reports (S2, S4, D7, D10) | Printed platform text has no terminal escapes, bidi characters or zero-width characters (`agent/textsafe.py`). report.md escapes table markup. The record trail is always last, with its count. If the console cannot encode some output, the agent escapes that output and does not crash. The `.env` parser accepts a BOM, `export` and comments. It refuses `nan`, `inf`, negative or zero caps and prices. |
| Documented limits (T11, D5, I2) | There is still no compare-and-set. The platform request is `if_updated_at` or an ETag on `FileAttachment.update`. If a field that the agent did not send changed inside the write window of the agent, the agent now reports it as `concurrent_change`. Pre-flight fails closed on purpose.<br>Fixture capture now keeps only the access-log fields that the agent reads. The committed rows were already clean: the platform returns `share_token` and `actor_ip` as null, and no row names a withheld file. Refer to [14](known-limits.md#14-known-limits-and-open-questions). |

These fixes came from the 2 reviews of the combined change:

- A create whose reply is not an object no longer escapes the error handler of the escalation (T3, T1).
- Restore no longer trusts the `before` of a journal, except for a description to which the agent added its note (T6).
- The agent drops nested schema text (T10).
- A target label other than `live` or `fake` now causes a refusal (E1).
- The login body and headers no longer show in traceback locals (I4).
- Records and answers no longer quote platform error text (I12).
- Access-log rows without a file keep no details (I5).
- The agent now reports concurrent changes (T11, partial).
- The run-once guard no longer blocks a new run after an attempt that sent nothing (R1).
- Rescore no longer reads the current task files (R2).
- Fixture dates use UTC (T8).
- Access-log ids and user ids resolve in the cited-id check (T5).
- Fixes to `.gitignore`, the secret scan and the docs (I3, I11).

The final check completed these fixes. They come from the refined fixes of the skeptical reviewers:

- The call cap counts the overview read (D2).
- The session title names its run (R3).
- Restore records its inputs (R7).
- The trace events of the MCP client no longer keep platform error text (I12).

A person completed 1 fix by hand: `agent/textsafe.py` now drops every invisible format character, and tag characters too (T2).

Still open (T2): a planted party or uploader name still appears in an escalation, as 1 labelled line.

An offline check on 3 Oct 2026 examined the change afterwards. The check used the scripted model, the 26 Sept fixture and Python 3.14. The harness checks ran again under Python 3.11. The results were:

- `harness smoke` OK.
- All 21 tasks ×5 pass on every run.
- Rescore IDENTICAL.
- Calibration catches 355 of 355 planted mistakes (30 of the 31 kinds apply).
- Routes 10 / 10.
- The proof-of-concept script of every threat ran again.

Nothing used the live platform.

**Merged with PR #4 (3 Oct 2026).** The merge combined PR #4 (2 Oct) with these fixes. PR #4 had these parts:

- the 78 hand-written tests in `tests/`
- the "same kind" pre-flight check and the folder pre-flight check
- the confirmation of decisions A, B and the ambiguity rule

The folder check of PR #4 and the folder check of STRIDE T4 are now 1 check in `harness/preflight.py`. It finds these problems:

- a folder that is new or gone, or that someone renamed, moved or archived (`was renamed, moved or archived since the fixture`)
- any other update to a folder
- 2 folders with 1 name
- a fixture with no folder table (1 problem, not 1 problem for each folder)

The "same kind" problems name rows by their placeholder and say who changed them. Every other pre-flight problem does the same.

`scripts/secret_scan.py` now allows the exact dummy password in `tests/test_redact.py`, and only that value. Thus, on the merged tree, block D, `--history` and the pre-commit hook say `no secrets found` again.

The merge changed no test file. Where a PR #4 test expected `renamed, moved or archived`, the merge changed the words of pre-flight instead. On PR #4 alone, the document-kind check read raw rows. Thus, it examined withheld rows by their real titles. On the merged tree, the check examines each row as triage sees it. A withheld row has only its placeholder name (refer to [14](known-limits.md#14-known-limits-and-open-questions)).

An offline check examined the merged tree again with Python 3.14. The tests and the harness checks also ran under Python 3.11. The results were:

- The 78 tests in `tests/` pass.
- `harness smoke` OK.
- All 21 tasks ×5 pass on every run.
- Rescore IDENTICAL.
- Calibration 355 of 355.
- Routes 10 / 10.
- The proof-of-concept script of every threat ran again.

The old README received the [Tests](plan-and-status.md#tests) part and the [Security review (STRIDE)](safety.md#security-review-stride) part. `tests/README.md` now says what the tests of PR #4 cover. It also says which tests do not exist yet. The report is in `docs/security/stride-review.md`.

**Round 7: decision C (duplicates), 4 Oct 2026.** The duplicate rule changed. If a file looks like a copy of another file, the agent does not write to it. The agent never archives. The rule and its known limits are in [triage step 3](architecture.md#triage_folder-evidence-scored-filing).

The new rule replaces the design in the Step 3 gap report and in Rounds 1 and 5. In that design, a hash-matched copy followed its original. The agent archived the copy with a pointer and escalated its removal. There are 3 reasons for the change:

- **Bug B4.** Any client can write the recorded hash. Thus, any seat can plant a file that steers a move or an archive. Case 3 of TI7 is that attack. In it, a decoy in *Superseded* has the same recorded hash as a fileable Incoming file. The old rule would move that file next to the decoy and archive it.
- **Decision B.** The old follow step bypassed the same-name rule. Thus, it could put 2 files with the same name into 1 folder.
- **The live write run.** If the platform removes the 880-byte PO copies, the agent trusts the PO hash again. Then the old code would archive `82f83d94` during TI2L. That is a write on a shared row, and the live plan does not expect it.

Examine this rule again only when the platform computes a read-only hash on the server (request P10).

| Area | What changed |
|---|---|
| Triage (`agent/skills/triage.py`) | The agent plans a file in a duplicate group (hash + size + name, or name + size) as `escalate`. The plan has a `recorded_duplicate` or `suspected_duplicate` signal that names the other file. The agent writes the escalation after the same-name rule. The escalation names the id and the folder of the other file, and where this run puts the other file. The change removed the follow step, the archive, the duplicate note, the `archive_duplicate` record, the "needs delete rights" escalation and `plan_duplicate`. The module docstring gives the rule and its known limits. |
| Write guard (`agent/guards.py`) | `UPDATE_FIELDS` is `folder_id` and `description`. Thus, the guard itself refuses an archive, before the agent sends anything. |
| Restore (`agent/snapshot.py`) | `RESTORE_FIELDS` follows the guard. Restore still refuses a journal entry that holds `is_archived` (from older code), and it restores nothing. But the message now says this. It also names the commit to use for the restore: the git commit in the run manifest, 8202cf8 or earlier. |
| Escalator (`agent/skills/escalate.py`) | The change removed the unused `needs_permission` reason. It mapped to `other`, the default. Thus, nothing that the agent sends changes. |
| Fake server and task loader (`harness/fake_server.py`, `harness/tasks.py`) | An `extra_files` entry can give its own `id`. Thus, 2 planted files can have the same name. If 2 extras have 1 id, the loader refuses the task when it loads it, and names both files. If the id of an extra is already a row, the fake server refuses the extra. It never replaces the row silently. |
| Verifier (`harness/verifiers.py`, `harness/calibrate.py`) | An `unchanged` id that is not in the state before the run now fails ("not in the before-state"). `plan_duplicate` and the `archived` key stay. Thus, a rescore of run files from before decision C gives the same result. All 1,221 local run files kept their verdicts. |
| Tasks | There is a new task, **TI7**, with 4 planted trusted pairs and 2 passes (refer to [3.4](harness.md#34-the-tasks-22)). TI1, TI2, TI2L and TI3 received only a "decision C" header comment. Their graded fields did not change. |
| Docs | The old README, `tests/README.md` (the 4 `FollowOriginalTests` and the new scenarios to write), `docs/security/stride-review.md` (E2, T6 and the counts) and 1 sentence of `docs/gap_report.md`. |

Round 7 changed no test file. The 4 `FollowOriginalTests` in `tests/test_escalate.py` assert the old rule, and now they fail. The team will delete 2 of them and rewrite the other 2 by hand (refer to [`tests/README.md`](../tests/README.md#decision-c-scenarios-12-not-covered-yet)).

An offline check on 4 Oct 2026 examined the change. The check used the scripted model, the 26 Sept fixture and Python 3.14. The results were:

- `python -m unittest discover -s tests` runs 157 tests, and only those 4 tests fail.
- `harness smoke` OK.
- All 22 tasks ×5 pass on every run (110 run files).
- Rescore IDENTICAL.
- Calibration 377 of 377 (30 of the 31 kinds apply).
- Routes 10 / 10.
- `secret_scan.py` finds nothing.

When the code for duplicates is off, TI7 fails on 8 checks. Nothing used the live platform.

**Later on 4 Oct 2026:** a commit deleted 2 of the `FollowOriginalTests` and changed the other 2 into `PossibleCopyTests`. It also added 28 test files. Now `python -m unittest discover -s tests` runs 296 tests, and all of them pass.

---

## Old README sections that the new README replaces

These sections were near the top of the old README. The new [README.md](../README.md) replaces them.

---

## Contents

- [Quick start](#quick-start) · [The idea in one minute](#the-idea-in-one-minute) · [Tests](plan-and-status.md#tests) · [Security review (STRIDE)](safety.md#security-review-stride)
- **How it works:** 1 · [Architecture](architecture.md#1-architecture) · 2 · [The skills](architecture.md#2-the-skills) · 3 · [The harness](harness.md#3-the-harness)
- **Why it exists:** 4 · [From gap report to code](gap-to-code.md#4-from-gap-report-to-code) (features A1–A14, platform requests P1–P13, roadmap) · 5 · [Background: platform, scenario, research, bugs](background.md#5-background-the-platform-the-scenario-and-the-research)
- **The plan and how to check it:** 6 · [Step 4 plan: tasks, status, milestones, risks, staff questions](plan-and-status.md#6-the-step-4-plan-tasks-status-and-open-questions) · 7 · [How to check that each part works](checking.md#7-how-to-check-that-each-part-works)
- **How to run it safely:** 8 · [Safety](safety.md#8-safety-on-the-shared-platform) · 9 · [Commands](harness.md#9-commands) · 10 · [Results](plan-and-status.md#10-results-so-far) · 11 · [The live write run](live-run.md#11-the-live-write-run)
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

`ask` does not write unless you ask it to write. **Plan-only is the default.** If there is no `ANTHROPIC_API_KEY`, `ask` uses the offline *scripted* model (refer to [Models](architecture.md#the-two-models)).

`.env` holds the seat password and your model key. Keep it private to you:

- On Linux or macOS, `chmod 600 .env` makes it private. If other users can read `.env`, the agent warns you.
- On Windows, if the repo is in your own user folder, `copy .env.example .env` is enough. Other users cannot read files in that folder. To see who can read `.env`, use `icacls .env`.

---

## The idea in one minute

**The platform.** AgentSwitch is a shared business system (an ERP) with a Drive. The *Files* seat of this team can use the apps `drive`, `crm` and `agent`. It cannot delete anything.

**The problem.** Files arrive untriaged in an **Incoming** folder. People ask questions such as *"which drawing is current for this part?"*. The platform makes this hard:

- It stores **no file contents**.
- It has **no revision states**.
- It has **no guard for when 2 people edit the same file**.
- Different screens **disagree about how many files exist**.
- It **shows this seat titles of files from apps that the seat has no permission to open**.

**The agent.** It is a language model (Claude) that can act **only** through a small set of hand-written **skills** and a few read-only lookups. Skills are plain Python. Skills decide, and the model explains. Every decision becomes a **decision record**. If the evidence cannot support something, the agent **refuses it or gives it to a person** (escalates it), and it never guesses.

**The harness.** The harness is a test bench. It asks the agent the same questions many times, on a **fake copy of the platform** (offline) or on the real platform. It scores each run from the **database state before and after**. It also tests itself (**calibration**). It plants mistakes in good runs and checks that it catches each one.
