# Files Agent — AgentSwitch Seat 20 (Team 20)

An AI agent for the **Files** seat of the AgentSwitch platform, and the **harness** (test bench) that proves it works.

> Seat 20's graded request: *"Find the drawing for part J-BRKT-04, and tidy the incoming folder."*
> The scenario data lives on **Keystone** (`class.agentswitch.theschoolofai.in`), a platform shared with other teams.

- **Standard library only.** Python 3.11 or newer. Nothing to install, no agent framework, no SDK.
- **The agent drives the platform over MCP** (JSON-RPC 2.0, a hand-written client) with the team's own model key.
- **Every run is written to disk before it is scored**, and the score is judged from the database, not from the agent's prose.

---

## The idea in one minute

**The platform.** AgentSwitch is a shared business system (an ERP) with a Drive. The *Files* seat may use the apps `drive`, `crm` and `agent`, and it cannot delete anything.

**The problem.** Files land in an **Incoming** folder, untriaged, and people ask *"which drawing is current for this part?"*. The platform stores no file contents and no revision states, has no guard against two people editing one file, and its screens disagree about how many files exist.

**The agent.** A language model (Claude) that can act **only** through 8 hand-written **skills** (plain Python) and 8 read-only lookups. Skills decide, the model explains, and every decision is written down as a **decision record**. What the evidence can't support is refused or handed to a person (escalated), never guessed.

**The harness.** Asks the agent the same questions many times, on a **fake copy of the platform** (offline) or on the real one, and judges each run from the database state before and after. It also tests itself: it plants known mistakes in good runs and checks that it catches every one.

---

## Requirements

| Need | Check | Notes |
|---|---|---|
| Python 3.11 or newer | `python --version` | Checked with Python 3.14.4 on Windows 11. On Windows, `python3` may be the Microsoft Store shortcut (*"Python was not found…"*); use `python`. On macOS or Linux, use `python3` if `python` is missing. |
| git | `git --version` | The repo is public on GitHub: `git clone https://github.com/mkthoma/files_agent.git` |
| A password or a model key | — | **Not needed** for the offline path below. Only the live platform needs them. |

**One habit for all commands:** `python -m agent …` talks to the **live** platform unless you add `--target fake`. `python -m harness run …` uses the **fake** server unless you add `--target live`. Every `python -m agent` command in the offline path below says `--target fake` and `--model scripted`.

---

## Run it offline in 10 minutes

Run everything from the repo root, in bash (Git Bash on Windows) or PowerShell. Nothing touches the network or the live platform, and no `.env` file is needed. The times are from fresh clones on Windows 11 with Python 3.14.4 (3 and 4 Oct 2026).

| Step | Command | Time |
|---|---|---|
| 1. Get the code | `git clone https://github.com/mkthoma/files_agent.git` then `cd files_agent` | a few seconds |
| 2. *(Git Bash, or when you pipe the output)* print UTF-8 | bash: `export PYTHONIOENCODING=utf-8` · PowerShell: `$env:PYTHONIOENCODING = "utf-8"` | — |
| 3. The whole pipeline, offline | `python -m harness smoke` | 2–3 s |
| 4. The drawing half of the request | `python -m agent --target fake ask "Find the drawing for part J-BRKT-04." --model scripted` | about 1 s |
| 5. The tidy half, plan only | `python -m agent --target fake ask "Tidy the incoming folder." --model scripted` | about 1 s |
| 6. The hand-written tests | `python -m unittest discover -s tests` | 9–15 s |
| 7. *(optional)* All 22 tasks, 5 runs each | `python -m harness run all --target fake --model scripted` | 30–60 s |

**Step 3** runs three tasks on the fake server, scores them, rebuilds the score from disk and checks that the harness catches planted mistakes. You should see (the run-set path and time differ):

```text
OK   run + score
OK   rescore identical
OK   calibration catches faults
run set: <repo>\runs\20261003-230831-smoke
```

**Step 4.** You should see:

```text
The current drawing for part J-BRKT-04 is J-BRKT-04_RevC_JigBracket.pdf (2683b2c8-f700-4870-981c-1fb9c8d53393), revision C, in 'Jig & Fixture Drawings'. J-BRKT-04_RevB_JigBracket.pdf (91feaf59-c9b9-4e10-a603-ece98fa00e2b) is superseded (archived: True, folder 'Superseded'). Note: KJ-BRKT-04 (Machinist Bench Bracket Set) is a different part, not a revision of J-BRKT-04.

Record trail (added by the agent code; 2 record(s)):
- [info] superseded_drawing: J-BRKT-04_RevB_JigBracket.pdf (91feaf59-c9b9-4e10-a603-ece98fa00e2b)
- [info] current_drawing: J-BRKT-04_RevC_JigBracket.pdf (2683b2c8-f700-4870-981c-1fb9c8d53393)

[fake | plan | model scripted | writes 0 | cost {'turns': 2, 'mcp_calls': 3, 'input_tokens': 0, 'output_tokens': 0, 'usd': 0.0} | stop end_turn]
[trace: <repo>\runs\cli\<time>-ask-<id>.jsonl]
```

The first paragraph is the model's answer. The *Record trail* is added by the code, and the status line says where it ran (`fake`), that nothing was written (`plan`, `writes 0`) and what it cost.

**Step 5** prints one line per file in Incoming, then 31 records. Incoming holds **18** files: the 9 originals, and a bare 880-byte copy of each that the platform added on 23 Sept. The plan files 5 originals and holds back the other 13:

```text
Triage of 'Incoming' (plan only - nothing was changed):
...
- Cert_MillCert_SS304_Heat90114.pdf (680e8af6-15f3-49c6-b70b-987316fa5775) -> Quality (score 5).
- J-KNOB-09_RevA.dxf (b45cecdd-9f14-491a-a0ee-2826d3fabb15) -> Jig & Fixture Drawings (score 8).
- PO_4471_ApexMetals_signed.pdf (732439a0-7f36-4d31-ac3b-f406c41c00bd) -> Purchasing (score 4).
- W9_JMillerWelding_2026.pdf (81857de6-e6e9-41c5-9da8-67cb5d1903c1) -> Purchasing (score 4).
- timesheet_week33.xlsx (1ee27946-7064-42e1-afce-376068a545bf) -> HR (score 4).
...
[fake | plan | model scripted | writes 0 | cost {'turns': 2, 'mcp_calls': 14, 'input_tokens': 0, 'output_tokens': 0, 'usd': 0.0} | stop end_turn]
```

**Step 6.** The test output ends with `OK` (the count and the time differ):

```text
----------------------------------------------------------------------
Ran <n> tests in <n>s

OK
```

On this branch, the 4 `FollowOriginalTests` in `tests/test_escalate.py` fail until the team rewrites them by hand: they assert the duplicate rule from before decision C. [`tests/README.md`](tests/README.md#decision-c-scenarios-12-not-covered-yet) says which to delete and which to rewrite.

**Step 7** prints one table row per task, then `**22 of 22 tasks pass on every run.** Total cost $0.0000.` and the run-set path, and writes `score.json` and `report.md` under `runs/<set>/`.

**Things to know:**
- Ask the two halves of the request separately. The offline *scripted* model picks **one** skill per question, so the full sentence *"Find the drawing for part J-BRKT-04, and tidy the incoming folder."* answers only the drawing half. The loop itself can run two skills in one turn (`tests/test_loop.py`), but no harness task asks the full sentence yet, so the real model's answer to it is unchecked.
- The scripted model is a stand-in so that the harness runs without a key or cost. **Its passing runs say nothing about the real model's judgement.**
- Keep `--model scripted` on offline `ask` commands. Without it, `ask` uses the real model whenever `ANTHROPIC_API_KEY` is set in `.env` **or in your shell**, which needs the network and costs money.
- Every `ask` writes a trace to `runs/cli/`, and every harness run writes to `runs/<set>/`. `runs/` is git-ignored.

---

## Live runs (team members with the seat password)

1. Make your `.env`. Bash: `cp .env.example .env && chmod 600 .env`. PowerShell: `Copy-Item .env.example .env`. Fill in `AS_KEYSTONE_PASSWORD`, and `ANTHROPIC_API_KEY` for the real model, in an editor. Never type them on a command line: shell history keeps them.
2. Live, read-only checks:
   ```bash
   python -m agent smoke                                        # login, tool discovery, one read
   python -m agent ask "Find the drawing for part J-BRKT-04."   # plan-only
   ```
   Without a password both stop with a Python traceback ending in `AuthError: No password configured: set AS_KEYSTONE_PASSWORD / AS_SURYODAYA_PASSWORD in .env`. Nothing is sent.
3. Real-model runs, live read-only runs, pre-flight and the single live write run (TI2L) have their own runbook: [docs/live-run.md](docs/live-run.md). **Never run the live write without the repo owner's go-ahead.**

---

## Safety rules in brief

Keystone is shared with other teams. These rules are enforced in code; the numbered list (rules 1–13, cited by the STRIDE review) is in [docs/safety.md](docs/safety.md#8-safety-on-the-shared-platform).

- **Plan-only by default.** `ask --apply` writes only on the fake server; on live it is refused.
- **Live writes go through the harness only:** task TI2L, run once, with `--target live --live-apply` and `AS_ALLOW_WRITES=1` set in the shell for that one command (`.env` is ignored for it).
- **Only the 9 allow-listed Incoming files** can be written, and nothing outside that list is written or escalated.
- **Three write tools, no delete.** `FileAttachment.update`, `AgentSession.create` and `AgentEscalation.create`; the agent changes only `folder_id` and `description` (a note is appended). It never archives: a possible copy is escalated, not moved (decision C).
- **Pre-flight, snapshot, journal, restore.** A live write run stops if the platform drifted from a fixture captured within 24 hours, and restores only this seat's own changes afterwards.
- **No secrets on disk.** `.env` and `runs/` are git-ignored and traces are redacted. `python scripts/secret_scan.py` should print `no secrets found`; enable the pre-commit scan once with `git config core.hooksPath .githooks`.

---

## Tests

- **Hand-written tests** in `tests/test_*.py`, plus `tests/helpers.py` (shared set-up, no tests). Plain `unittest`: offline, no platform, no model, no network.
- Run: `python -m unittest discover -s tests` (add `-v` to see each test's name). The output ends with `OK`.
- On this branch, decision C makes the 4 `FollowOriginalTests` in `tests/test_escalate.py` fail: they assert the old duplicate rule. The team deletes two of them and rewrites two by hand.
- [`tests/README.md`](tests/README.md) says what each file covers, which plan task it checks, and what is still to write.
- The tests pin numbers from the newest fixture, `harness/fixtures/keystone/2026-09-26` (212 tools, 113 file rows, 5 moves and 13 escalations). After a re-capture, run them again, update any changed numbers and move the fixture pin in `tests/helpers.py` in the same commit.
- The harness tasks, `python -m harness calibrate` and the checks in [docs/checking.md](docs/checking.md) are **not** these tests.

---

## Results

On commit `9d6f962` (decision C), offline, re-run on 4 Oct 2026 with Python 3.14.4. Re-run them on the commit that merges this README and put that commit here.

| Check | Command | Result |
|---|---|---|
| Pipeline smoke | `python -m harness smoke` | 3 × `OK` |
| All 22 tasks × 5, scripted model | `python -m harness run all --target fake --model scripted` | **22 of 22 pass on every run** (110 run files) |
| Rescore from disk | `python -m harness rescore runs/<set>` | `rescore IDENTICAL to score.json` |
| Calibration | `python -m harness calibrate runs/<set>` | `377 of 377 injected faults caught.` |
| Routing, scripted model | `python -m harness routes` | `10 of 10 routed as expected.` |
| Hand-written tests | `python -m unittest discover -s tests` | all pass except the 4 `FollowOriginalTests` (see [Tests](#tests)) |
| Secret scan of the clone | `python scripts/secret_scan.py` | `no secrets found` |

**Not done yet:** any run with the real model (all 22 tasks offline × 5; the 11 read-only tasks live × 5); the single live write run (TI2L); the re-check of the bugs raised. Live, only the 10 read-only tasks of the time ran once, with the scripted model, on 22 Sept (10 of 10). Dated history: [docs/plan-and-status.md](docs/plan-and-status.md#10-results-so-far).

**Live pre-flight fails today, for two reasons:** the newest fixture (26 Sept) is older than 24 hours, and the live tool list was reported on 3 Oct to have 214 tools against the fixture's 212 (not checked offline). Re-capture before any live check, and again on the day of the live write. See [docs/live-run.md](docs/live-run.md).

---

## Where to read next

| If you want to… | Read |
|---|---|
| see every guide in one list | [docs/README.md](docs/README.md) |
| see how the agent, a question and a write work | [docs/architecture.md](docs/architecture.md) (old README 1, 2, the agent part of 9, 13, Appendix B) |
| see how the harness, the 22 tasks, scoring and calibration work | [docs/harness.md](docs/harness.md) (old 3, the harness part of 9) |
| check a part by hand, or break it on purpose | [docs/checking.md](docs/checking.md) (old 7 to 7.5) |
| run anything live, or the single write run | [docs/live-run.md](docs/live-run.md) (old 7.6, 11, and *Before the live write run*) |
| read every safety rule and the STRIDE changes | [docs/safety.md](docs/safety.md) (old 8, the ground rules of 6.1, Security review) and [docs/security/stride-review.md](docs/security/stride-review.md) |
| see the plan, task status, staff questions and dated results | [docs/plan-and-status.md](docs/plan-and-status.md) (old 6, 10, 12, the old status lines and the old Tests section) |
| map the gap report to the code (A1–A14, P1–P13) | [docs/gap-to-code.md](docs/gap-to-code.md) (old 4) and [docs/gap_report.md](docs/gap_report.md) |
| learn the platform, the scenario, the ids and the research | [docs/background.md](docs/background.md) (old 5 to 5.5, Appendix A) |
| see the bugs raised and how the agent works around them | [docs/bugs.md](docs/bugs.md) (old 5.6) |
| know what the code does not do | [docs/known-limits.md](docs/known-limits.md) (old 14) |
| read the review rounds and the old-to-new section map | [docs/history.md](docs/history.md) (old 15, Contents, Quick start, The idea in one minute) |
| fix an error message | [docs/troubleshooting.md](docs/troubleshooting.md) (old 16) |

---

## Repo layout

```
agent/            the Files Agent: command line, MCP client, guards, loop, models
  skills/         the 8 skills the model can call, and their helpers
  filing_rules.toml   team-owned scoring rules for the tidy
harness/          fake server, runner, verifiers, scoring, calibration, pre-flight, capture
  tasks/          team-owned task files (22) and routes.toml
  fixtures/       captured platform data (keystone/2026-09-22, keystone/2026-09-26, suryodaya/2026-09-22)
tests/            hand-written unittest tests, helpers.py and the tests guide
scripts/          secret_scan.py (prints file and line, never the text)
.githooks/        pre-commit: runs that scan on staged lines (git config core.hooksPath .githooks)
docs/             gap report, STRIDE review and the guides above
runs/             run output (git-ignored)
```

---

## Troubleshooting (first run)

| You see | Do this |
|---|---|
| `The token '&&' is not a valid statement separator in this version.` | You are in Windows PowerShell 5.1. Use the PowerShell form of the command. |
| `Python was not found; run without arguments to install from the Microsoft Store…` | You typed `python3` on Windows. Use `python`, or install Python 3.11+ from python.org. |
| A traceback ending in `AuthError: No password configured…` | You ran a live command. Add `--target fake` (and `--model scripted`), or fill in `.env`. |
| `�` where a dash should be | Set `PYTHONIOENCODING=utf-8` (step 2). |
| `note: no ANTHROPIC_API_KEY set, using the offline scripted model` | Expected on an offline `ask` without `--model scripted`. |
| `warning: rescore may not use the code that made these runs: … modified working tree` after `harness smoke` | Harmless: you have uncommitted changes. Commit or stash them to make it go away. |

Every other message: [docs/troubleshooting.md](docs/troubleshooting.md#16-troubleshooting).
