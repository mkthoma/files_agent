# Docs

This folder holds the guides that were sections of the old README. It also holds the gap report and the STRIDE review. [history.md](history.md#old-to-new-section-map) gives the new place of each old README section.

- [architecture.md](architecture.md): how the agent, a question and a write work. It also has the skills, the agent commands, the repo layout and the MCP tools. Old README sections: 1, 2, the agent part of 9, 13 and Appendix B.
- [harness.md](harness.md): the harness, its 22 tasks, verifiers, scores, calibration and run files, and the harness commands. Old README sections: 3 and the harness part of 9.
- [gap-to-code.md](gap-to-code.md): each point of the gap report, the features A1–A14, the platform requests P1–P13 and the roadmap. Old README section: 4.
- [background.md](background.md): the platform, the 23 Sept data change, the graded scenario and the benchmarks. It also has the research and the id cheat sheet. Old README sections: 5 to 5.5 and Appendix A.
- [bugs.md](bugs.md): the bugs that the team raised. Old README section: 5.6.
- [plan-and-status.md](plan-and-status.md): the old status lines, the old Tests section and the Step 4 plan. It also has the results so far and the files you own. Old README sections: front matter, Tests, 6, 10 and 12.
- [checking.md](checking.md): how to check each part by hand. Old README sections: 7 to 7.5.
- [live-run.md](live-run.md): the single live write run, before, during and after. Old README sections: 7.6, 11 and the paragraph *Before the live write run*.
- [official-run.md](official-run.md): the official server run (Release 8.1): `agentswitch-harness.toml`, `python -m harness official`, the provided token and model, and the rehearsal steps.
- [safety.md](safety.md): the STRIDE changes to the behaviour, the ground rules and the safety rules 1–13. Old README sections: Security review, the ground rules of 6.1, and 8.
- [known-limits.md](known-limits.md): the known limits and the open questions. Old README section: 14.
- [history.md](history.md): the review rounds, the old Contents, Quick start and The idea in one minute, and the old-to-new section map. Old README section: 15.
- [troubleshooting.md](troubleshooting.md): the error messages and what to do. Old README section: 16.
- [gap_report.md](gap_report.md): the one-page gap report (Step 3). The team updated it on 27 Sept. On 4 Oct, 1 sentence changed for decision C.
- [security/stride-review.md](security/stride-review.md): the full STRIDE security review and its fixes.

## Corrections after the split

The guides keep the ids, code, numbers and dates of the old README. A check of the full set found these facts out of date, and the guides now give the correct value:

- **Helper name.** The access-log helper is `upload_lead` in `agent/skills/common.py`. Commit `dbace27` (3 Oct) gave it this name. The old README said `uploader_of`.
- **Offline results.** Some status rows now give the 4 Oct results: 22 of 22 tasks and 377 of 377. These rows are T6.1, M5 and the Must row "pass^5 offline" in [plan-and-status.md](plan-and-status.md), and gate M5 in [checking.md](checking.md). The 27 Sept values stay as history.
- **Dates.** Some text gave "today (27 Sept 2026)" but already described decision C. These places now say 4 Oct 2026: 5.3 in [background.md](background.md), 4.6 and 4.8 in [gap-to-code.md](gap-to-code.md), and 7.6 in [live-run.md](live-run.md).
- **Gap report.** Commit `9d6f962` (4 Oct) changed 1 sentence of the gap report. [gap-to-code.md](gap-to-code.md), [architecture.md](architecture.md#13-repo-layout) and this index now say so.
- **Repo visibility.** The repo is now public. T0.2 in [plan-and-status.md](plan-and-status.md) and in [checking.md](checking.md) says so.
- **Counts.** The Status column of T6.4 now says that this seat had 45 bugs by 27 Sept. The Task column keeps the 13 bugs of the plan. The cut line now gives 296 tests in 48 files (4 Oct 2026).
- **The live write command.** The full command is now only in [live-run.md](live-run.md#11-the-live-write-run). [harness.md](harness.md), [safety.md](safety.md) and [plan-and-status.md](plan-and-status.md) link to it.
- **Test count before the live write run.** Item 2 of [section 11](live-run.md#11-the-live-write-run) said "All 157 tests must pass". The count changes when the team adds tests (296 on 4 Oct 2026). Thus item 2 now links to [Tests](plan-and-status.md#tests) for the count.
- **Direct list calls of the model.** The agent sends the filter values of the direct calls of the model unchanged. For 4 list tools, it refuses a filter name outside `MODEL_FILTERS` (`agent/loop.py`). The text in [known-limits.md](known-limits.md) and in Round 6 of [history.md](history.md) now agrees with the code. Rows L2, L3, L5 and B1 of [bugs.md](bugs.md) and part E of [gap-to-code.md](gap-to-code.md) now also agree with it.
- **Decision C rows.** The introduction of 4.6 in [gap-to-code.md](gap-to-code.md) now says that decision C (4 Oct) changed the A6 and A9 rows.
- **The document-kind check of PR #4.** On PR #4 alone, the check read raw rows. On the merged tree, the check examines each row as triage sees it. Round 6 in [history.md](history.md) now says this.
