# Files Agent — AgentSwitch Seat 20 (Team 20)

This repo holds an AI agent for the **Files** seat of the AgentSwitch platform. A seat is 1 role on the platform, with its own login and apps. The repo also holds the **harness** (a test bench) that proves that the agent works.

> The graded request of Seat 20 is: *"Find the drawing for part J-BRKT-04, and tidy the incoming folder."*

The scenario data is on **Keystone** (`class.agentswitch.theschoolofai.in`). Seat 20 shares this platform with other teams.

- **Standard library only.** The code needs Python 3.11 or newer. There is nothing to install: no agent framework and no SDK.
- **The agent controls the platform through MCP**, the Model Context Protocol (JSON-RPC 2.0, with a hand-written client). It uses the team's own model key.
- **The harness writes each run to disk before it scores the run.** It scores the writes and the final state from the database. It scores the answer from the text of the model and its decision records. It never uses text that the code adds.

---

## The idea in one minute

**The platform.** AgentSwitch is a shared business system (an ERP) with a Drive. The *Files* seat can use the apps `drive`, `crm` and `agent`. It cannot delete anything.

**The problem.** New files arrive in an **Incoming** folder, and nobody sorts (triages) them. People ask *"which drawing is current for this part?"*. The platform does not store file contents or revision states. It has no guard against 2 people who edit the same file. Its screens do not agree about the number of files.

**The agent.** It is a language model (Claude) that can act **only** through 8 hand-written **skills** (plain Python) and 8 read-only lookups. The skills make the decisions, and the model explains them. The code records each decision as a **decision record**. If the evidence does not support an action, the agent refuses it or sends it to a person (it escalates). The agent never guesses.

**The harness.** It asks the agent the same questions many times. It can use a **fake copy of the platform** (offline) or the real platform. It scores each run from the database state before and after the run. It also tests itself: it plants mistakes in good runs and checks that it catches each one.

---

## Requirements

| Need | Check | Notes |
|---|---|---|
| Python 3.11 or newer | `python --version` | The checks in this README used Python 3.14.4 on Windows 11. On Windows, `python3` can be the Microsoft Store shortcut (*"Python was not found…"*). If so, use `python`. On macOS or Linux, if `python` is not available, use `python3`. |
| git | `git --version` | The repo is public on GitHub. To clone it, use `git clone https://github.com/mkthoma/files_agent.git`. |
| A password or a model key | — | The offline path below does **not** need them. The live platform needs the password. The real model (`--model anthropic`) needs the model key. |

**The default target of each command:**
- If you do not add `--target fake`, `python -m agent …` uses the **live** platform.
- If you do not add `--target live`, `python -m harness run …` uses the **fake** server.
- Each `python -m agent` command in the offline path below has `--target fake` and `--model scripted`.

---

## Run it offline in 10 minutes

Do steps 3 to 8 from the repo root. Use bash (Git Bash on Windows) or PowerShell. Steps 3 to 8 do not use the network or the live platform. You do not need a `.env` file. The times are from fresh clones on Windows 11 with Python 3.14.4 (3 and 4 Oct 2026).

1. Clone the code: `git clone https://github.com/mkthoma/files_agent.git`. This step takes a few seconds.
2. Open the repo folder: `cd files_agent`.
3. Set the output of Python to UTF-8. Do this again in each new shell window:
   - bash: `export PYTHONIOENCODING=utf-8`
   - PowerShell: `$env:PYTHONIOENCODING = "utf-8"`
4. Run the whole pipeline offline: `python -m harness smoke`. This step takes 2–3 s.

The command runs 3 tasks on the fake server and scores them. Then it calculates the score again from the files on disk. It also checks that the harness catches planted mistakes. The output is as follows (your run-set path and time are different):

```text
OK   run + score
OK   rescore identical
OK   calibration catches faults
run set: <repo>\runs\20261003-230831-smoke
```

CAUTION: Do not remove `--model scripted` from the offline `ask` commands in steps 5 and 6. If `.env` **or your shell** sets `ANTHROPIC_API_KEY`, `ask` then uses the real model. The real model needs the network and costs money.

5. Ask for the drawing (the first half of the request): `python -m agent --target fake ask "Find the drawing for part J-BRKT-04." --model scripted`. This step takes about 1 s. The output is:

```text
The current drawing for part J-BRKT-04 is J-BRKT-04_RevC_JigBracket.pdf (2683b2c8-f700-4870-981c-1fb9c8d53393), revision C, in 'Jig & Fixture Drawings'. J-BRKT-04_RevB_JigBracket.pdf (91feaf59-c9b9-4e10-a603-ece98fa00e2b) is superseded (archived: True, folder 'Superseded'). Note: KJ-BRKT-04 (Machinist Bench Bracket Set) is a different part, not a revision of J-BRKT-04.

Record trail (added by the agent code; 2 record(s)):
- [info] superseded_drawing: J-BRKT-04_RevB_JigBracket.pdf (91feaf59-c9b9-4e10-a603-ece98fa00e2b)
- [info] current_drawing: J-BRKT-04_RevC_JigBracket.pdf (2683b2c8-f700-4870-981c-1fb9c8d53393)

[fake | plan | model scripted | writes 0 | cost {'turns': 2, 'mcp_calls': 3, 'input_tokens': 0, 'output_tokens': 0, 'usd': 0.0} | stop end_turn]
[trace: <repo>\runs\cli\<time>-ask-<id>.jsonl]
```

The first paragraph is the answer of the model. The code adds the *Record trail*. The status line shows where the command ran (`fake`). It also shows that the command wrote nothing (`plan`, `writes 0`), and what the command cost.

6. Ask for the tidy plan (the second half of the request): `python -m agent --target fake ask "Tidy the incoming folder." --model scripted`. This step takes about 1 s.

The output has 1 line for each file in Incoming, then 31 records. Incoming holds **18** files: the 9 originals, and an 880-byte copy of each original. The copies have no tags, no sender and no description. The platform added these copies on 23 Sept.

The plan moves 5 originals to their folders. It does not move the other 13 files. Part of the output is (only the first line, the 5 move lines and the status line):

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

7. Run the hand-written tests: `python -m unittest discover -s tests`. This step takes 9–15 s. The output ends with these lines (your time is different):

```text
----------------------------------------------------------------------
Ran 296 tests in <n>s

OK
```

8. *(Optional)* Run all 22 tasks, 5 runs each: `python -m harness run all --target fake --model scripted`. This step takes 30–60 s.

First, the output has 1 line for each task, for example `C1: 5 run file(s) written`. Then it has a header and 1 table row for each task. Then it shows `**22 of 22 tasks pass on every run.** Total cost $0.0000.` and the run-set path. The command also writes `score.json` and `report.md` in `runs/<set>/`.

**Things to know:**
- Ask the 2 halves of the request separately. The offline *scripted* model picks **1** skill for each question. If you ask the full request at the top of this page, it answers only the drawing half. The loop itself can run 2 skills in 1 turn (`tests/test_loop.py`). But no harness task asks the full request yet. Thus no check examines how the real model answers the full request.
- The scripted model is a substitute. It lets the harness run without a key and without cost. **Its passes tell you nothing about the judgement of the real model.**
- Each `ask` writes a trace to `runs/cli/`. Each harness run writes to `runs/<set>/`. Git ignores `runs/`.

---

## Live runs (team members with the seat password)

1. Make your `.env` file from the example:
   - bash: `cp .env.example .env && chmod 600 .env`
   - PowerShell: `Copy-Item .env.example .env`
   - On Windows, keep the repo in your own user folder. Other users cannot read files in that folder. To see who can read `.env`, use `icacls .env`.

CAUTION: Do not type the password or the key on a command line. The shell history keeps them.

2. In an editor, write your `AS_KEYSTONE_PASSWORD` in `.env`. For the real model, also write your `ANTHROPIC_API_KEY` in it.

WARNING: Do the next step only if you are a team member with the seat password. The commands use the live platform, which other teams also use.

3. Do the live, read-only checks:
   ```bash
   python -m agent smoke                                        # login, tool discovery, one read
   python -m agent ask "Find the drawing for part J-BRKT-04."   # plan-only
   ```
   If you have no password, both commands stop with a Python traceback. The traceback ends with `AuthError: No password configured: set AS_KEYSTONE_PASSWORD / AS_SURYODAYA_PASSWORD in .env`. The commands send nothing.

WARNING: **Never do the live write run without the approval of the repo owner.** It writes to the shared platform.

4. For all other live work, use these guides:
   - real-model runs and live read-only runs: [docs/harness.md](docs/harness.md#harness)
   - pre-flight and the single live write run (TI2L): [docs/live-run.md](docs/live-run.md)

---

## Safety rules in brief

The code enforces the rules below, because other teams also use Keystone. The numbered list of rules 1–13 is in [docs/safety.md](docs/safety.md#8-safety-on-the-shared-platform). The STRIDE review refers to these numbers.

- **Plan-only by default.** `ask --apply` writes only on the fake server. On live, the agent refuses it.
- **Only the harness writes on live.** It writes only for task TI2L, and only once. That run needs `--target live --live-apply`. It also needs `AS_ALLOW_WRITES=1` in the shell, for that command only. For `AS_ALLOW_WRITES`, the code ignores `.env`.
- **On live Keystone, the agent writes only to the 9 allow-listed Incoming files.** It does not write to or escalate any other file. Offline, the allow-list is all of Incoming, so step 6 also plans escalations for the 9 copies.
- **3 write tools, no delete.** The write tools are `FileAttachment.update`, `AgentSession.create` and `AgentEscalation.create`. The agent changes only `folder_id` and `description` (it adds a note to the end). It never archives a file. If a file is possibly a copy, the agent escalates it and never writes to it (decision C).
- **Pre-flight, snapshot, journal, restore.** A live write run stops if the platform is different from the fixture (the captured platform data in `harness/fixtures/`). The fixture must be less than 24 hours old. After the run, the harness restores the old values of only the fields that this seat changed.
- **No secrets on disk.** Git ignores `.env` and `runs/`. The code removes secrets from the traces. The expected output of `python scripts/secret_scan.py` is `no secrets found`. To enable the pre-commit scan, run `git config core.hooksPath .githooks` once. On GitHub, CI also scans the full git history with this script and with gitleaks.

---

## Tests

- The **hand-written tests** are in `tests/test_*.py`. The file `tests/helpers.py` holds the shared set-up and no tests.
- The tests use plain `unittest`. They run offline, with no platform, no model and no network.
- There are 296 tests in 48 files (4 Oct 2026). All of them pass. `PossibleCopyTests` in `tests/test_escalate.py` checks the duplicate rule of decision C.
- To run the tests, type `python -m unittest discover -s tests`. To see the name of each test, add `-v`. The output ends with `Ran 296 tests` and `OK`.
- [`tests/README.md`](tests/README.md) tells you what each file checks and how to prove that a test finds a bug. It also tells you what has no test yet.
- The tests check fixed numbers from the newest fixture, `harness/fixtures/keystone/2026-09-26`: 212 tools, 113 file rows, 5 moves and 13 escalations. After each new capture of the fixture, do these steps in 1 commit:
  1. Move the fixture pin in `tests/helpers.py` to the new fixture.
  2. Run the tests again.
  3. Update the numbers that changed.
- The harness tasks, `python -m harness calibrate` and the checks in [docs/checking.md](docs/checking.md) are **not** part of these tests.
- **CI.** `.github/workflows/ci.yml` runs on every push to `main` and on every pull request. It runs the tests and the offline harness gates (`routes`, `smoke`, `run all`, `rescore` and `calibrate`) on Ubuntu and Windows, with Python 3.11 and 3.14. It also scans the full git history with `scripts/secret_scan.py --history` and with gitleaks. CI uses no secrets and no live platform. When you add or remove a task, change `EXPECTED_TASKS` in `ci.yml`.

---

## Results

These results are from commit `9d6f962` (decision C). They ran offline on 4 Oct 2026 with Python 3.14.4. The test row is from the same code with the 48 test files of 4 Oct.

NOTE (for the team): Run these checks again on the commit that merges this README. Write the id of that commit here.

| Check | Command | Result |
|---|---|---|
| Pipeline smoke | `python -m harness smoke` | 3 × `OK` |
| All 22 tasks × 5, scripted model | `python -m harness run all --target fake --model scripted` | **22 of 22 pass on every run** (110 run files) |
| Rescore from disk | `python -m harness rescore runs/<set>` | `rescore IDENTICAL to score.json` |
| Calibration | `python -m harness calibrate runs/<set>` | `377 of 377 injected faults caught.` |
| Routes, scripted model | `python -m harness routes` | `10 of 10 routed as expected.` |
| Hand-written tests | `python -m unittest discover -s tests` | `Ran 296 tests`, then `OK` (48 files, see [Tests](#tests)). |
| Secret scan of the clone | `python scripts/secret_scan.py` | `no secrets found` |

The calibrate output calls the planted mistakes "injected faults".

**Not done yet:**
- Runs with the real model: all 22 tasks offline × 5, and the 11 read-only tasks live × 5.
- The single live write run (TI2L).
- The re-check of the bugs that the team raised.

On 22 Sept, only the 10 read-only tasks of that date ran live (R5 did not exist yet), once each, with the scripted model. The result was 10 of 10. For the dated history, see [docs/plan-and-status.md](docs/plan-and-status.md#10-results-so-far).

**On 4 Oct 2026, live pre-flight fails for 2 reasons:**
- The newest fixture (26 Sept) is older than 24 hours.
- A report from 3 Oct says that the live tool list has 214 tools, but the fixture has 212. No offline check confirms this number.

Capture the fixture again before any live check. Capture it again on the day of the live write run. See [docs/live-run.md](docs/live-run.md).

---

## Where to read next

| If you want to… | Read |
|---|---|
| see every guide in 1 list | [docs/README.md](docs/README.md) |
| see how the agent, a question and a write work | [docs/architecture.md](docs/architecture.md) |
| see how the harness, its tasks, scores and calibration work, and find the commands for real-model and live read-only runs | [docs/harness.md](docs/harness.md) |
| check a part by hand, or break it on purpose | [docs/checking.md](docs/checking.md) |
| do pre-flight or the single live write run | [docs/live-run.md](docs/live-run.md) |
| read every safety rule and the STRIDE changes | [docs/safety.md](docs/safety.md) and [docs/security/stride-review.md](docs/security/stride-review.md) |
| see the plan, the task status, the staff questions and the dated results | [docs/plan-and-status.md](docs/plan-and-status.md) |
| map the gap report to the code (A1–A14, P1–P13) | [docs/gap-to-code.md](docs/gap-to-code.md) and [docs/gap_report.md](docs/gap_report.md) |
| learn about the platform, the scenario, the ids and the research | [docs/background.md](docs/background.md) |
| see the bugs that the team raised, and how the agent avoids them | [docs/bugs.md](docs/bugs.md) |
| know what the code does not do | [docs/known-limits.md](docs/known-limits.md) |
| read the review rounds and the old-to-new section map | [docs/history.md](docs/history.md) |
| find what to do about an error message | [docs/troubleshooting.md](docs/troubleshooting.md) |

---

## Repo layout

```
agent/            the Files Agent: command line, MCP client, guards, loop, models
  skills/         the 8 skills the model can call, and their helpers
  filing_rules.toml   team-owned scoring rules for the tidy of Incoming
harness/          fake server, runner, verifiers, scoring, calibration, pre-flight, capture
  tasks/          team-owned task files (22) and routes.toml
  fixtures/       captured platform data (keystone/2026-09-22, keystone/2026-09-26, suryodaya/2026-09-22)
tests/            hand-written unittest tests, helpers.py and the tests guide
scripts/          secret_scan.py (prints file and line, never the text)
.githooks/        pre-commit: runs that scan on staged lines (git config core.hooksPath .githooks)
.github/          workflows/ci.yml: tests, harness gates and secret scans on every push to main and every PR
.gitleaks.toml    gitleaks config: the default rules, plus 3 reviewed false positives
docs/             gap report, STRIDE review and the guides above
runs/             run output (git-ignored)
```

---

## Troubleshooting (first run)

| You see | Do this |
|---|---|
| `The token '&&' is not a valid statement separator in this version.` | You are in Windows PowerShell 5.1. Use the PowerShell form of the command. |
| `Python was not found; run without arguments to install from the Microsoft Store…` | You typed `python3` on Windows. Use `python`, or install Python 3.11+ from python.org. |
| A traceback that ends with `AuthError: No password configured…` | You ran a live command. Add `--target fake` (and `--model scripted`), or write the values in `.env`. |
| `�` in place of a dash | Set `PYTHONIOENCODING=utf-8` (step 3). |
| `note: no ANTHROPIC_API_KEY set, using the offline scripted model` | This message is normal for an offline `ask` without `--model scripted`. |
| `warning: rescore may not use the code that made these runs: … the working tree is modified now` when you run `harness smoke` | The message is harmless. It shows that you have changes that you did not commit. To remove the message, commit or stash the changes. |

For all other messages, see [docs/troubleshooting.md](docs/troubleshooting.md#16-troubleshooting).
