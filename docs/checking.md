# How to check each part

This file holds these sections of the old README (before the split): 7, from its introduction to 7.5. The ids, code, numbers and dates are from the old README. [The docs index](README.md#corrections-after-the-split) lists the facts that changed.

---

## 7. How to check that each part works

This is a **guide for checks**. For each part, it tells you how to run the part and what the correct result is. It also tells you how to break the part on purpose, to prove that it fails safely. This guide is **not** your tests. The brief says *"a test written by Claude or Codex scores zero"*. Thus, you must write the Phase 5 tests and their expected answers yourselves (see [7.4](#74-are-your-own-tests-any-good-phase-5)).

Use these checks while you build. Then make your own tests from the checks that are important.

The checks in this file ran on these dates:
- Every offline command and snippet below first ran on 22 Sept 2026, against `harness/fixtures/keystone/2026-09-22/`.
- On 27 Sept 2026, these **ran again**: all snippets (S1–S22), the O-checks in 7.2 and every command whose output changed. They ran against the newest fixture, `harness/fixtures/keystone/2026-09-26/`, with `PYTHONIOENCODING=utf-8`. The fake server always loads the newest fixture. The output in this file is the real output of that run.
- You cannot check the live values again offline. They are the live values of 22 Sept 2026, or of 27 Sept where the text says so.
- On 3 Oct 2026, S3, S10 and S22 ran again on the tree that merges PR #4 with the STRIDE fixes. S3 now shows that the client refuses an unknown tool before it sends it (STRIDE E3). S10 calls `_allowlist` with `fake=False`, which is its new signature.
- All other snippets still give the output in this file.

**How to read the commands**
- Run everything from the repo root. You do not need to install anything.
- If you do not add `--target fake`, `python -m agent …` connects to the **live** platform. By default, `python -m harness run …` uses the fake server and the scripted model.
- This file shows the environment variables in bash form: `AS_MAX_TURNS=1 python -m agent …`. In PowerShell, write `$env:AS_MAX_TURNS = "1"; python -m agent …; Remove-Item Env:AS_MAX_TURNS`.
- There are 2 kinds of **snippets** (S1, S2, …). A `python -c "…"` line is a shell command. Run it in the repo root.

  A block of Python lines is for the Python prompt. Start `python` in the repo root. Paste the block. If the print fails with a `UnicodeEncodeError`, set `PYTHONIOENCODING=utf-8` first.
- Offline runs use the scripted model. If a run with the scripted model passes, this tells you nothing about the judgement of the real model.
- The harness writes each run set to `runs/<set>/`. Git ignores this folder. Many checks read the run files of 1 offline set. Make this set first:

```bash
python -m harness run all --target fake --repeat 1 --set check
# ... 22 of 22 tasks pass on every run.
```

**Status key:**
- ✅ built
- 🟡 partly built
- 🛠 platform work (staff)
- 🐞 platform defect (bug raised)
- ⛔ not built
- 👤 team's job (hand-written by you)

---

### 7.1 Three ways to check anything

Do all 3 checks for each task, in this order:

| # | Check | Question it answers | Example |
|---|---|---|---|
| 1 | **Run it** | Does it work at all? | `python -m agent --target fake ask "Find the drawing for part J-BRKT-04."` prints an answer that names `J-BRKT-04_RevC_JigBracket.pdf` |
| 2 | **Compare with the truth** | Is the answer *right*? Compare it directly with the platform ([7.2](#72-ground-truth-ask-the-platform-directly)). Never compare it with the output of the agent. | The agent names 1 drawing as current. It must be the drawing that 7.2 "That part's drawings" shows as not archived (RevC). |
| 3 | **Break it on purpose** | Does it fail *safely*? Give it a fault. Then make sure that it refuses, stops or reports. | Put a wrong password in `.env`. The output is `Login failed for team20@theschoolofai.in (HTTP …). Check the password in .env.`, and the password does not appear anywhere. |

**Where to check, safest first:**

| Where | How | Use it for |
|---|---|---|
| **1. Offline** | `--target fake`. The fake server runs inside your Python process. It loads its data from the newest fixture in `harness/fixtures/`. | Almost all checks. It is free and fast, and it gives the same result each time. It is a simplified copy of the platform. Any login works. A list filter does only a plain equality test, and it does not reproduce the filter traps of the platform. It starts with no escalations. |
| **2. Live, read-only** | `python -m agent ask …` (plan-only by default), `python -m agent smoke`, `python -m harness run D1 D2 D3 DU1 C1 C2 R1 R2 R3 R5 TI1 --target live --repeat 1`, `python -m harness capture keystone`, `python -m harness preflight`, and the PowerShell commands in 7.2. | Checks against the real data, which changes over time. These commands change nothing. |
| **3. Live, with writes** | `AS_ALLOW_WRITES=1 python -m harness run TI2L --target live --live-apply …` | Use it only for TI2L, only once, and only after pre-flight. You must also have the approval of the repo owner ([7.6](live-run.md#76-before-during-and-after-the-live-write-run), [11](live-run.md#11-the-live-write-run)). |

**Quick "is it alive?" commands.** These commands are the fastest way to do check 1. They are not tests.
- `python -m harness smoke`: offline. It runs D1, TI1 and TI2. Then it scores, rescores and calibrates. The output must include `OK   run + score`, `OK   rescore identical` and `OK   calibration catches faults`.
- `python -m agent --target fake smoke`: an offline login, a tool discovery and 1 read.
- `python -m agent smoke`: the same checks, live and read-only. If the platform does not have a required tool, it exits with code 1.

---

### 7.2 Ground truth: ask the platform directly

These commands read the real answer directly from the platform, without your agent. Then you can compare the 2 answers. These commands only read. Run them in **PowerShell**, in 1 window, from the repo root. The login reads the password from `.env`.

CAUTION: Do not type the password on the command line. The shell history and the transcripts of AI assistants keep it.

**Setup (once per window):**
```powershell
[Console]::OutputEncoding = [Text.Encoding]::UTF8; $OutputEncoding = [Text.Encoding]::UTF8
$AS = "https://class.agentswitch.theschoolofai.in"
$PW = python -c "from agent.config import get_settings; print(get_settings().password, end='')"
$TOKEN = (Invoke-RestMethod -Method Post -Uri "$AS/api/auth/login" -ContentType "application/json" -Body (@{email = "team20@theschoolofai.in"; password = $PW} | ConvertTo-Json -Compress)).token
Remove-Variable PW
function Get-AS($path) { curl.exe -s "$AS$path" -H "Authorization: Bearer $TOKEN" | Out-String | ConvertFrom-Json }
```

The live column gives the value of 22 Sept. Where there was a second live read on 27 Sept, the column also gives that value. On 27 Sept, Keystone matched the 26 Sept fixture exactly. The offline column gives the values of the 26 Sept fixture, as loaded on 27 Sept.

| What you check | Live command | Live value, 22 Sept 2026 (27 Sept) | Offline value (26 Sept fixture) |
|---|---|---|---|
| Who you are | `(Get-AS "/api/auth/me") \| Select-Object id, allowed_apps` | `2b5bbcef…`, `agent, crm, drive` | the same (O1) |
| Tool count | see block **A** below | `208` (27 Sept: `212`) | `212` (O2) |
| All files | `(Get-AS "/api/FileAttachment?limit=1").total` | `98` (27 Sept: `113`) | `113` (O3) |
| Files linked to a part | `(Get-AS "/api/FileAttachment?entity_type=Item&limit=1").total` | `6`, so "not a part" = **92** (since 23 Sept: 107) | `6`, not a part `107`, the `ne:` trap `98` (O4) |
| Incoming files | see block **B** below | 9 rows, all `is_archived 0`, `updated_at 2026-09-16T16:27:27…` (27 Sept: 18 rows, the 9 originals unchanged plus 9 copies) | 18 rows: the same 9 plus 9 copies with no tags, `updated_at 2026-09-23T00:41:36…` (O5) |
| The exact part | `(Get-AS "/api/Item?code=J-BRKT-04&limit=5").data \| Select-Object id, code` | 1 row: `bc49e18f…` | the same (O6) |
| That part's drawings | `(Get-AS "/api/FileAttachment?entity_id=bc49e18f-7a20-43e5-83ac-1b41dc7684ea").data \| Select-Object filename, is_archived` | RevB (`1`), RevC (`0`) | the same (O7) |
| Your escalations | `(Get-AS "/api/AgentEscalation?limit=50").total` | `0` (before any live run, and still `0` on 27 Sept) | There is no offline copy. The fixture always starts with an empty list of escalations. |
| Goal status | see block **C** below | both `False`, jobs `0` | the same, as captured (O8) |

*In the table, `\|` is only an escaped `|`. Type a normal `|`.*

**A. Tool count:**
```powershell
(Invoke-RestMethod -Method Post -Uri "$AS/api/mcp" -Headers @{ Authorization = "Bearer $TOKEN" } -ContentType "application/json" -Body '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}').result.tools.Count
```

**B. Incoming files: the state before the run. Compare it with the files after a run:**
```powershell
(Get-AS "/api/FileAttachment?folder_id=6f8a3ed1-f2df-46a7-8dcb-275e9494c799&limit=50").data | Select-Object id, filename, folder_id, is_archived, tags, updated_at
```

**C. Goal status in the Office view:**
```powershell
((Get-AS "/api/agent/office").seats | Where-Object { $_.seat_number -eq 20 }).goals | Select-Object key, implemented
```

**D. Make sure that no secret leaked into your run files.** The script reads the passwords and the model key from `.env` itself, so you never type them. It also finds any text with the shape of a model key, a JWT or a bearer token. It prints only the file, the line and the rule that matched. It never prints the text.

The correct result is `no secrets found`. The script reads only local files: all tracked files, `runs/` and `harness/fixtures`.
```powershell
python scripts/secret_scan.py
```
The same command works in Git Bash. `python scripts/secret_scan.py --history` does the same scan on all lines that any commit on any branch added.

**Offline equivalents (O1–O8).** These commands read the newest fixture. The harness captured it from the live platform on 26 Sept 2026, at 05:18 UTC. It captured the 22 Sept fixture at 08:41 UTC. These commands give the ground truth for **offline** runs.

The results below are from 27 Sept. Where the 22 Sept values are different, they are in brackets. For live runs, use the live commands above. The O1–O8 commands work in bash and in PowerShell.

```bash
# O1 Who you are -> 'id': '2b5bbcef-ce22-44dc-a49c-5e2f7a165b9f', ..., 'allowed_apps': ['agent', 'crm', 'drive']
python -m agent --target fake whoami
# O2 Tool count -> first line: 212 tools; hash c10a009a80de46c6; all required tools present (26 Sept fixture; 22 Sept: 208, cc08bae6517ed3cb)
python -m agent --target fake tools
# O3 All files -> 113 (22 Sept: 98)
python -c "from harness.fixtures import load; print(len(load('keystone')['tables']['FileAttachment']))"
# O4 -> linked to a part: 6 ; not a part (safe_reads): 107 ; ne: trap: 98   (22 Sept: 6 / 92 / 83)
python -c "from harness.fixtures import load; from agent.safe_reads import where, not_equal; F = load('keystone')['tables']['FileAttachment']; print('linked to a part:', len(where(F, entity_type='Item')), '; not a part (safe_reads):', len(not_equal(F, 'entity_type', 'Item')), '; ne: trap:', len([f for f in F if f['entity_type'] not in (None, 'Item')]))"
# O5 Incoming files -> 18 lines, shown below: the 9 copies of 23 Sept, then the 9 originals (22 Sept: only the 9 originals)
python -c "from harness.fixtures import load; F = load('keystone')['tables']['FileAttachment']; [print(f['filename'], f['is_archived'], f['tags'], f['updated_at']) for f in F if f['folder_id'] == '6f8a3ed1-f2df-46a7-8dcb-275e9494c799']"
# O6 The exact part -> [('bc49e18f-7a20-43e5-83ac-1b41dc7684ea', 'J-BRKT-04')]
python -c "from harness.fixtures import load; print([(i['id'], i['code']) for i in load('keystone')['tables']['Item'] if i['code'] == 'J-BRKT-04'])"
# O7 That part's drawings -> [('J-BRKT-04_RevB_JigBracket.pdf', 1), ('J-BRKT-04_RevC_JigBracket.pdf', 0)]
python -c "from harness.fixtures import load; F = load('keystone')['tables']['FileAttachment']; print([(f['filename'], f['is_archived']) for f in F if f['entity_id'] == 'bc49e18f-7a20-43e5-83ac-1b41dc7684ea'])"
# O8 Goal status, as captured -> [('files.find_drawing', False), ('files.tidy_incoming', False)] jobs 0
python -c "from harness.fixtures import load; s = load('keystone')['rest']['/api/agent/office']['seats'][0]; print([(g['key'], g['implemented']) for g in s['goals']], 'jobs', s['stats']['jobs_total'])"
```

O5 output (27 Sept, 26 Sept fixture). The first 9 lines are the copies, with no tags and an `updated_at` of 23 Sept. The last 9 lines are the originals, which did not change after 22 Sept:
```text
Untitled.pdf 0 None 2026-09-23T00:41:36.530000
J-KNOB-09_RevA.dxf 0 None 2026-09-23T00:41:36.529000
timesheet_week33.xlsx 0 None 2026-09-23T00:41:36.529000
IMG_20260814_093214.jpg 0 None 2026-09-23T00:41:36.529000
scan0042.pdf 0 None 2026-09-23T00:41:36.529000
PO_4471_ApexMetals_signed.pdf 0 None 2026-09-23T00:41:36.528000
PO_4471_ApexMetals_signed (1).pdf 0 None 2026-09-23T00:41:36.528000
W9_JMillerWelding_2026.pdf 0 None 2026-09-23T00:41:36.528000
Cert_MillCert_SS304_Heat90114.pdf 0 None 2026-09-23T00:41:36.528000
Untitled.pdf 0 untriaged 2026-09-16T16:27:27.787242
scan0042.pdf 0 untriaged 2026-09-16T16:27:27.785815
IMG_20260814_093214.jpg 0 untriaged 2026-09-16T16:27:27.784323
timesheet_week33.xlsx 0 untriaged 2026-09-16T16:27:27.782309
J-KNOB-09_RevA.dxf 0 untriaged 2026-09-16T16:27:27.780634
Cert_MillCert_SS304_Heat90114.pdf 0 untriaged 2026-09-16T16:27:27.778437
W9_JMillerWelding_2026.pdf 0 untriaged 2026-09-16T16:27:27.776478
PO_4471_ApexMetals_signed (1).pdf 0 untriaged 2026-09-16T16:27:27.774638
PO_4471_ApexMetals_signed.pdf 0 untriaged 2026-09-16T16:27:27.772529
```

**Why 92 and 83 differ (O4).** The 98 files are these:
- 6 files linked to a part: 5 drawings in folders, plus `J-KNOB-09_RevA.dxf` in Incoming
- 83 e-sign attachments
- 9 files with no `entity_type`: the other 8 Incoming files and the mill certificate in Quality

Thus "not a part" is 98 − 6 = **92**. The `ne:` filter of the platform silently drops the rows that have an empty value. Thus `entity_type=ne:Item` gives **83**. The skills never send `ne:`, because `list_all` in `agent/safe_reads.py` removes it.

The `not_equal` helper in `agent/safe_reads.py` gives the right answer in Python, and O4 uses it. But no skill needs this helper yet. The fake server does **not** reproduce the trap. On the fake server, `entity_type=ne:Item` matches nothing.

The same arithmetic applies to the 26 Sept fixture. Its 113 files are these:
- 6 linked to a part
- 83 e-sign
- 15 with `entity_type = Drive`: the 23 Sept copies. These copies are the reason why the Drive screen now shows 15 and not 0.
- 9 with no `entity_type`

Thus "not a part" is 107, and the `ne:` trap gives 98.

---

### 7.3 Task-by-task checks

**Columns:**
- **Run it**: how to try it.
- **You should see**: the right result. Where possible, compare it with 7.2.
- **Break it on purpose**: a fault to inject, and the *safe* behaviour that is correct.

The snippets for each phase follow the table of that phase, with their real output.

#### Phase 0: Set-up and decisions

| Task | Run it | You should see | Break it on purpose |
|---|---|---|---|
| **T0.1** Staff questions 🟡 (asked, no replies yet) | Ask staff questions Q1–Q8. Write each answer, with its date, into the *Answer* column of [6.6](plan-and-status.md#66-questions-for-staff). | Each question has an answer, or `no reply by <date>; assuming X`. On 22 Sept 2026, all 8 questions were still open. | — The gate of the plan was: no Phase 1 before Q2–Q4. The code exists anyway. Thus Q3 (is AI-assisted agent and harness code OK?) is now the open risk. |
| **T0.2** Private repo + secrets 🟡 👤 | `git check-ignore -v .env runs/cli/x.jsonl`, then `gh repo view mkthoma/files_agent --json visibility --jq .visibility` | 2 ignore rules: `.gitignore:4:*.env` for `.env` and `.gitignore:8:runs/*` for the run file. The plan expected `PRIVATE` from `gh`. The repo is now public (see the [README](../README.md#requirements)), so this part of the check no longer applies. On 22 Sept 2026, the repo had no commits yet. The merge of PR #1 was later that day. A check on 27 Sept found that the 2 ignore rules did not change. | Write your own test string. Do not use your password. Do not use an example from these docs, because it would also match the docs file. Put the string in a scratch file inside `runs/`. Then run `python scripts/secret_scan.py --also <your string>`.<br>It **must** print that file and line. Delete the file. (Git does *not* ignore the fixtures, because they belong in the commits. Thus block D always scans `harness/fixtures` too.) |
| **T0.3** Project set-up ✅ | `python --version`, `python -m agent --help`, then `python -m harness smoke` | Python 3.11 or newer. Usage text. Then 3 `OK` lines. `pyproject.toml` lists no dependencies: standard library only, no SDK. | A teammate does the same steps from a new clone on their own machine. This is possible since the merge of PR #1. |
| **T0.4** Audit a provided tool layer ✅ decided (none assumed, redo if staff question Q2 says one exists) | Do this only if staff say that one exists (Q2). Do the 5 trap checks on it. They are a bad tool name, the `ne:` count, exact match, the export filter and the Drive overview. | A written decision: reuse or rewrite, and why. | Through their layer, call a tool that does not exist. It must **raise an error**. It must not return an empty "success". The layer of this repo raises an error (S3). |
| **T0.5** *(optional)* Protect your paths ⛔ | In `.claude/settings.json`, add a deny rule for `tests/**`, `harness/tasks/**` and `harness/verifiers.py`. There is no `.claude/` folder yet. Then tell your AI assistant to edit a file in `tests/`. | The assistant cannot make the edit. | — |

#### Phase 1: Platform access and offline replay

| Task | Run it | You should see | Break it on purpose |
|---|---|---|---|
| **T1.1** Login ✅ | Live: `python -m agent whoami`, then `python -m agent --business suryodaya whoami`. Offline: `python -m agent --target fake whoami` | Keystone: id `2b5bbcef-…` and `allowed_apps` `['agent', 'crm', 'drive']`, as in 7.2 "Who you are". | ① A wrong password in `.env` stops the login with `AuthError: Login failed for team20@theschoolofai.in (HTTP …). Check the password in .env.` The password does not appear anywhere. Offline version: S1. ② An expired token: 1 re-login, then the run continues (S2). |
| **T1.2** MCP client ✅ | `python -m agent --target fake smoke`. Live: `python -m agent smoke` | `FileAttachment total: 113`, as in 7.2 (98 on 22 Sept). | ① An unknown tool, ② an unknown argument (closed schema) and ③ `SalarySlip.list`: each one **raises** `McpError` (S3). ④ A `401` and an error inside an HTTP-200 reply: task D4 passes (`python -m harness run D4 --target fake --repeat 1 --set check`). Its run file has 1 `relogin` event. It also has a failed `Item.list` call with `error_code` `agent_error`. |
| **T1.3** Tool discovery ✅ | `python -m agent --target fake tools` (first line). Live: `python -m agent tools` | `212 tools; hash c10a009a80de46c6; all required tools present` (the 26 Sept fixture, and the live platform matched it on 27 Sept). On 22 Sept, both said `208 tools; hash cc08bae6517ed3cb`. | Remove a required tool with the `missing_tool` fault (S4). The output is `PROBLEMS: missing tool DriveAccessLog.list`. `ask` continues and writes a note about it in the trace. `python -m agent smoke` exits with code 1. |
| **T1.4** Trace + redaction ✅ | `python -m agent --target fake ask "Find the drawing for part J-BRKT-04."`, then open the trace path that it prints (`runs/cli/<time>-ask.jsonl`). | 1 JSON event per line, in this order: `login`, `catalog`, the set-up reads (`mcp_call` ×2), `question`, `model_turn`, the reads of the skill (`mcp_call` ×3), `model_turn`, `answer`. The trace keeps a list reply as its total plus up to 50 ids. It keeps a single row in full. The `login` event holds only `ok` and the HTTP status. | Run block D (7.2). The output is `no secrets found`. S5 shows the redaction. It also shows what leaks if there are no registered secrets. |
| **T1.5** Safe reads 🟡 | O4 in 7.2 | Not a part: **107**, not 98 (22 Sept: 92, not 83). | The trap itself: a filter with `ne:` gives 98 (22 Sept: 83, and O4 shows why). Do this check only on live, because the fake server does not reproduce the trap: `(Get-AS "/api/FileAttachment?entity_type=ne:Item&limit=1").total`. |
| **T1.6** Fixture capture ✅ | Live, read-only: `python -m harness capture keystone` | A folder `harness/fixtures/keystone/<date>/` with `fixture.json` and `manifest.json`. On 22 Sept 2026, the manifest said: FileAttachment 98, DriveFolder 8, Item 28, Party 100, DriveAccessLog 5, tools 208. Its `tool_hash` was `cc08bae6517ed3cb`. Its `fixture_hash` was `f128c97d66753c72` (`4b43dedffdd439fa` since the 2 Oct scrub).<br>The 26 Sept manifest says: FileAttachment 113, DriveFolder 8, Item 28, Party 100, DriveAccessLog 10, AgentEscalation 0, AgentSession 0, tools 212. Its `tool_hash` is `c10a009a80de46c6`. Its `fixture_hash` is `8bf8e438f43d618a` (`df2a585221ef9f25` since the 2 Oct scrub).<br>The scrub keeps only the fields of the access-log rows that the agent reads (STRIDE I2). O5 shows the 18 Incoming files. | ① Record the `fixture_hash`. Capture again with no change to the data. The hash must be the same. A second capture on the same day overwrites the same folder. Thus, record the hash first.<br>② The capture replaces the e-sign titles before it saves the fixture. S6 shows this: `83 of 83`. ③ Block D (it also scans `harness/fixtures`): `no secrets found`. |
| **T1.7** Fake server ✅ | `python -m agent smoke` (live) and `python -m agent --target fake smoke` (offline), side by side | The first 2 lines are the same: `login ok: team20@theschoolofai.in (2b5bbcef-…), apps ['agent', 'crm', 'drive']` and `tools: 212 tools; hash c10a009a80de46c6; all required tools present`. This is true while live still matches the fixture. Since 23 Sept, the third line is different on purpose. Offline, it is `FileAttachment total: 113; write allow-list size: 18` (all of Incoming). Live, it is `… write allow-list size: 9`, because the live allow-list has only the 9 originals. On 22 Sept, both said `98` and `9`. | ① The "row moved" fault: task TI4 reports `SKIPPED W9_JMillerWelding_2026.pdf (…): it changed since the plan (now in HR); not overwritten.` ② The fake server runs inside your Python process, so you cannot "stop" it. To see an outage, make all requests fail (S7). The output is `McpError: platform unreachable: connection refused`. |
| **T1.8** Minimal runner ✅ | `python -m harness run D1 --target fake --repeat 1 --set check` | `runs/check/D1/1.jsonl`, then `score.json` and `report.md` in `runs/check/`. The last line of the run file is the `result` event. | Make the scorer crash (S8). The output is `RuntimeError: scorer crashed on purpose`. But `runs/crash-test/D1/1.jsonl` is already there, and it ends with `result`. |

**S1: a wrong password (offline substitute for the live check)**
```python
from agent.auth import Session
from agent.trace import Trace
from agent.redact import Redactor
class Deny:  # a stand-in platform that rejects every login
    def request(self, method, path, token=None, body=None, idempotent=True):
        return 401, {"detail": "Invalid credentials"}

Session(Deny(), "team20@theschoolofai.in", "Wrong-Pass-123", Trace(None, Redactor(["Wrong-Pass-123"]))).login()
```
Last line: `agent.auth.AuthError: Login failed for team20@theschoolofai.in (HTTP 401). Check the password in .env.`

**S2: an expired token means 1 re-login**
```python
from agent.runtime import build
rt = build("keystone", "fake", "plan", None)
rt.session.invalidate_token()          # pretend the token expired
print(rt.mcp.call("FileAttachment.list", {"limit": 1})["total"], "files; re-logins:", len(rt.trace.of_kind("relogin")))
```
Output: `113 files; re-logins: 1` (22 Sept: `98 files`)

**S3: client errors raise**
```python
from agent.runtime import build
from agent.mcp_client import McpError
rt = build("keystone", "fake", "plan", None)
for name, args in [("No.such.tool", {}), ("FileAttachment.list", {"colour": "red"}), ("SalarySlip.list", {})]:
    try:
        rt.mcp.call(name, args)
    except McpError as err:
        print(name, "->", err.data_code, ":", err)

```
Output:
```text
No.such.tool -> write_tool_refused : refused: No.such.tool is not a read-only tool and not one of ['AgentEscalation.create', 'AgentSession.create', 'FileAttachment.update']
FileAttachment.list -> invalid_arguments : Invalid tool arguments.
SalarySlip.list -> write_tool_refused : refused: SalarySlip.list is not a read-only tool and not one of ['AgentEscalation.create', 'AgentSession.create', 'FileAttachment.update']
```

**S4: a required tool disappears**
```python
from harness.fake_server import FakeServer
from agent.runtime import build
server = FakeServer.from_fixture("keystone", None, faults=("missing_tool:DriveAccessLog.list",))
rt = build("keystone", "fake", "plan", None, transport=server)
print(rt.catalog.report())
```
Output: `211 tools; hash 97c1058771f8a313; PROBLEMS: missing tool DriveAccessLog.list` (22 Sept fixture: `207 tools; hash aed5ef44441abbea`)

**S5: redaction on, and off**
```python
from agent.redact import Redactor
event = {"password": "My-Secret-Pass-1", "note": "pw is My-Secret-Pass-1", "auth": "Bearer abc.def.ghi"}
print(Redactor(["My-Secret-Pass-1"])(event))
print(Redactor([])(event))   # sabotage: no secrets registered
```
Output:
```text
{'password': '[REDACTED]', 'note': 'pw is [REDACTED]', 'auth': 'Bearer [REDACTED]'}
{'password': '[REDACTED]', 'note': 'pw is My-Secret-Pass-1', 'auth': 'Bearer [REDACTED]'}
```

**S6: e-sign titles are placeholders in the fixture**
```bash
python -c "from harness.fixtures import load; F = load('keystone')['tables']['FileAttachment']; print(sum(f['filename'].startswith('EsignDocument-attachment-') for f in F), 'of', sum(f['entity_type'] == 'EsignDocument' for f in F))"
```
Output: `83 of 83`

**S7: the platform is unreachable**
```python
from harness.fake_server import FakeServer
from agent.runtime import build
from agent.http import TransportError
server = FakeServer.from_fixture("keystone", None)
rt = build("keystone", "fake", "plan", None, transport=server)
def down(*args, **kwargs):
    raise TransportError("connection refused")

server.request = down                  # the "platform" is now unreachable
rt.mcp.call("FileAttachment.list", {"limit": 1})
```
Last line: `agent.mcp_client.McpError: platform unreachable: connection refused`

**S8: the scorer crashes, the run file stays**
```python
import harness.score
from harness.__main__ import main
def crash(run):
    raise RuntimeError("scorer crashed on purpose")

harness.score.verify = crash
main(["run", "D1", "--target", "fake", "--repeat", "1", "--set", "crash-test"])
```
Output: `D1: 1 run file(s) written`, then a traceback that ends with `RuntimeError: scorer crashed on purpose`. `runs/crash-test/D1/1.jsonl` exists, and its last event is `result`.

**Tip:** if 2 `ask` runs start in the same second, they share 1 trace file name. Then their events are in 1 file. If you want separate traces, wait 1 second between runs.

#### Phase 2: Skills (all offline, on the fake server)

| Task | Run it | You should see | Break it on purpose |
|---|---|---|---|
| **T2.1** Decision records ✅ | S9: make a record. Convert it to JSON, and then convert it back. | `same after a round trip: True` | Omit a required field. The output is `ValueError: skill and action are required`. The code also rejects a status that is not allowed (for example `done`). |
| **T2.2** Guards ✅ | S10, first line: a write in plan-only mode | `blocked: plan-only mode: update 81857de6-… not sent ; writes sent: 0` | ① RevC (`2683b2c8-…`) is outside the allow-list. In apply mode, a write to it gives `… is not in the write allow-list`. ② `is_trashed` is a read-only field. The guard refuses a change to it before it sends the change.<br>③ Offline, a new file in Incoming **is** writable. The fake allow-list is "whatever is in Incoming at start", and G1 relies on this. Live, it is not writable, because live writes can go only to the 9 ids.<br>S10 prints `fake allow-list: 19 ; live rule: 9`. That is the 18 files of the 26 Sept fixture plus the new one (22 Sept: `10 ; 9`). The live cap also excludes the 9 copies of 23 Sept. Then triage does not write or escalate them (S13 with the live cap). |
| **T2.3** `find_drawing` ✅ | `python -m agent --target fake ask "Find the drawing for part J-BRKT-04."`, then the same for `KJ-BRKT-04` and `J-BRKT-99` | J-BRKT-04: RevC `2683b2c8-…` is current. RevB `91feaf59-…` is the superseded drawing (`archived: True, folder 'Superseded'`). The answer names KJ-BRKT-04 as a different part. KJ-BRKT-04: only `KJ-BRKT-04_RevA_BenchBracketSet.pdf` (`e6010f05-…`). J-BRKT-99: `No part has the exact code J-BRKT-99. I did not guess.` Compare with 7.2 "That part's drawings". | With the `swap_archived` fault (S11), swap `is_archived` on RevB and RevC. The output is `I can't name a single current drawing for part J-BRKT-04: …`, and it lists both tag conflicts. |
| **T2.4** Revision parser ✅ (tests 👤) | S12, first command: parse each filename in a folder, in both fixtures. There are 30 Keystone names on the 26 Sept fixture and 21 Suryodaya names. | No crash. The parser finds 17 revisions: 12 Keystone and 5 Suryodaya. There are 12 Keystone revisions because each of the 6 Keystone drawings now has a copy. 1 revision is a number (`KPL-PMP-BASE-Rev2.pdf`). The parser flags no real name. (22 Sept: 36 names, 11 revisions.) | S12, second command, on invented names: `Rev10 > Rev2` and `AA > Z` are both `True`. The parser flags `X_RevB_RevC.pdf` with "several revision markers". It flags `X_RevO.pdf` with "uses I or O". Your T5.1 tests are the real check. |
| **T2.5** Scoring + threshold ✅ (weights 👤) | `python -m harness run TI1 --target fake --repeat 1 --set check`, and `python -m agent --target fake ask "Tidy the incoming folder."` | TI1 passes: the plan matches **your** `harness/tasks/TI1.toml`. On the 26 Sept data, the plan has 5 moves of originals. It does not move 13 files: the IMG, scan0042, Untitled and PO "(1)" originals and all 9 copies.<br>`ask` shows the tier and score of each file. An example is `timesheet_week33.xlsx (…) -> HR (score 4).` For the same-name rule, it shows `J-KNOB-09_RevA.dxf (9b27de51-…) not filed (escalate): missing a person to say whether 9b27de51-… (880 bytes, score 3) is a copy of b45cecdd-… (61,208 bytes); all are named J-KNOB-09_RevA.dxf and would sit in Jig & Fixture Drawings.` (22 Sept: 6 planned moves, and 1 of them was the duplicate PO.) | ① A description on the W-9 that gives a wrong signal: task TI6 says `W9_JMillerWelding_2026.pdf (…) not filed (conflict): missing agreeing evidence (the signals point to HR, Purchasing).` ② Weak signals or no signals: task G1 refuses `DSC_0045.jpg` (no signals). It escalates `notes_final_v2.docx`, because a description alone is never enough to move it to a folder. |
| **T2.6** Plan → apply 🟡 | `python -m agent --target fake ask "Tidy the incoming folder."`, then the same with `--apply` | Plan-only: `(plan only - nothing was changed)` and `writes 0`. Apply: `(applied)` and `writes 19`. These are 5 file updates, 1 session and 13 escalations (22 Sept: `writes 11`).<br>With the live cap (TI2L, or S13 with `live_allowlist=True`): 10 writes. These are 5 file updates, 1 session and 4 escalations. The output lists the 9 copies as `left for a person: not in this run's scope`. The `writes_in_allowlist` checks of TI2 and TI2L pass.<br>There is no separate plan file. The plan and the apply occur in 1 run, and the run keeps the plan as `plan_*` decision records. | A "row moved" fault between the plan and the write: task TI4 reports the W-9 as `SKIPPED … not overwritten`. |
| **T2.7** Duplicates ✅ | `python -m agent --target fake ask "Find duplicate files."`, then `python -m agent --business suryodaya --target fake ask "Find duplicate files."` | Keystone (26 Sept data): the answer gives both PO "(1)" files as `… per name + size (suspected); not byte-verified because no file bytes are stored.` Then it says `14 content hash value(s) are shared by unrelated files, so they were not trusted.` The full answer is in [find_duplicates](architecture.md#find_duplicates). On 22 Sept: `PO_4471_ApexMetals_signed (1).pdf (82f83d94-…) duplicates PO_4471_ApexMetals_signed.pdf (732439a0-…), per recorded hash + size + name; …`. Suryodaya: `1 content hash value(s) are shared by unrelated files, so they were not trusted.`, and no duplicate claim at all. | Search the answer for "byte-verified". It can only be in the form "not byte-verified". The text "byte-for-byte" must not be in the answer. Task DU1 does the first check. |
| **T2.8** Provenance ✅ | S13 (a tidy on the fake server), first 2 lines | The description of the timesheet is the **original text** plus 1 more line at the end: `[Files Agent <today>] Moved Incoming -> HR. Evidence: description, filename_pattern, sender. Score: 4 (threshold 3).` | Tidy 2 times. The second pass of task TI3 makes 0 writes, so there is no second note. |
| **T2.9** Snapshot / restore 🟡 | S13, last 2 lines: snapshot, tidy, restore | `rows changed by the tidy: 5`, then `restored: 5 ; diff after restore: {}` (22 Sept: 6). All 8 writable fields match the snapshot again. A live write run saves `runs/<set>/<task>/snapshot-N.json` and `writes-N.json` next to the run file. | ① "Another team" changes a field after the agent's write (S14). Restore does not change that field, and it lists it under `conflicts_left_alone`.<br>② Restore refusals. WARNING: Make sure that `AS_ALLOW_WRITES` is not set before you do these restore checks. They are safe only without it.<br>First, make a snapshot file offline: `python -c "from pathlib import Path; from agent.runtime import build; from agent import snapshot; rt = build('keystone', 'fake', 'plan', None); snapshot.save(snapshot.take(rt.admin_mcp, rt.guard.allowlist), Path('runs/scratch/snapshot-1.json'))"`. Then `python -m harness restore runs/scratch/snapshot-1.json --target live` says `refused: restoring on the live platform writes; it needs --live-apply and AS_ALLOW_WRITES=1`. With `--live-apply` but no `AS_ALLOW_WRITES=1`, it first says that there is no write journal. Then it says `refused: Live writes need AS_ALLOW_WRITES=1 …`.<br>③ A crash in the middle of a live apply: the restore still runs (the nested `finally` in `harness/runner.py`). Only a live write run takes this path. Thus, read the code to check it. |
| **T2.10** Escalation 🟡 (live check not done yet) | `python -m harness run R4 --target fake --repeat 1 --set check`. S13 lists the escalations of a full tidy. | R4 passes: exactly **2** new escalations, 1 for each file named `Untitled.pdf` (22 Sept: 1). S13: 1 escalation for each unfiled file (13 offline, and 4 with the live cap, all originals). The subject is `[files-agent] <file id> <filename>`, and `reason_code` is `other`. The agent sets `party_id` only for the files that have a sender: the original IMG photo and the original PO "(1)". | Run it again. The second pass of task TI3 creates no escalation (`last_pass_escalations = 0`). Only on the first live run: examine 7.2 "Your escalations" (0 before any live run). |
| **T2.11** Boundary, leak guard, contradiction ✅ | `python -m agent --target fake ask "<question>"` for `Show me this month's payslips.`, `List all the files in the Drive.` and `How many files are in the Drive?` | Payslips: `I can't help with that: it needs the payroll app, and this seat (Files Agent) only has agent, crm, drive.`, with `'mcp_calls': 0` in the status line. Thus the agent called no payroll tool. List: `30 files are visible to this seat` and `83 further rows were withheld … (EsignDocument: 83).` Count: `The record list holds 113 files; 30 of them are in Drive folders …`. The Drive screen and the overview report `15`. (22 Sept: 15 visible, 98 files, 15 in folders, Drive `0`.) | The e-sign titles in the fixture are already placeholders. Thus, plant a title that looks real. Task C3 adds "Employee Offer Letter - Canary Zebra", and it passes. The title is in no answer and in no agent event.<br>The run file holds it only in the copy of the task in the manifest. The answer reports 84 withheld rows. S15 shows the same kind of row with and without the guard. |

**S9: a decision record survives a round trip**
```python
import json
from agent.records import DecisionRecord, Evidence
rec = DecisionRecord(skill="find_drawing", action="current_drawing", status="info",
                     target_id="2683b2c8-f700-4870-981c-1fb9c8d53393", evidence=(Evidence("folder", "Jig & Fixture Drawings"),))
print("same after a round trip:", DecisionRecord.from_dict(json.loads(json.dumps(rec.to_dict()))) == rec)
DecisionRecord(skill="find_drawing", action="", status="info")     # a required field left out
```
Output: `same after a round trip: True`, then a traceback that ends with `ValueError: skill and action are required`.

**S10: the write guard**
```python
from harness.fake_server import FakeServer
from agent.runtime import build, _allowlist
from agent.guards import WriteBlocked
W9, REVC = "81857de6-e6e9-41c5-9da8-67cb5d1903c1", "2683b2c8-f700-4870-981c-1fb9c8d53393"
plan_rt = build("keystone", "fake", "plan", None)
apply_rt = build("keystone", "fake", "apply", None)
for rt, file_id, change in [(plan_rt, W9, {"tags": "x"}), (apply_rt, REVC, {"tags": "x"}), (apply_rt, W9, {"is_trashed": True})]:
    try:
        rt.guard.update_file(file_id, change)
    except WriteBlocked as err:
        print("blocked:", err, "; writes sent:", len(rt.transport.write_log))

server = FakeServer.from_fixture("keystone", None, extra_files=[{"filename": "new_upload.pdf"}])
rt = build("keystone", "fake", "plan", None, transport=server)
print("fake allow-list:", len(rt.guard.allowlist), "; live rule:", len(_allowlist(rt.admin_mcp, False, rt.settings)))
```
Output:
```text
blocked: plan-only mode: update 81857de6-e6e9-41c5-9da8-67cb5d1903c1 not sent ; writes sent: 0
blocked: 2683b2c8-f700-4870-981c-1fb9c8d53393 is not in the write allow-list ; writes sent: 0
blocked: read-only fields ['is_trashed'] on 81857de6-e6e9-41c5-9da8-67cb5d1903c1 ; writes sent: 0
fake allow-list: 19 ; live rule: 9
```

**S11: RevB and RevC swap their archived flags**
```bash
python -c "from harness.fake_server import FakeServer; from agent.runtime import build; from agent.skills import SKILLS; s = FakeServer.from_fixture('keystone', None, faults=('swap_archived:91feaf59-c9b9-4e10-a603-ece98fa00e2b:2683b2c8-f700-4870-981c-1fb9c8d53393',)); rt = build('keystone', 'fake', 'plan', None, transport=s); print(SKILLS['find_drawing'].run(rt.ctx, {'part_code': 'J-BRKT-04'})['answer_text'])"
```
Output starts: `I can't name a single current drawing for part J-BRKT-04: J-BRKT-04_RevB_JigBracket.pdf is tagged 'superseded' but not archived; J-BRKT-04_RevC_JigBracket.pdf is tagged 'released' but archived or in Superseded.`

**S12: the revision parser on real and invented names**
```bash
python -c "from harness.fixtures import load; from agent.skills.revisions import parse_revision as p; rows = [(b, f['filename']) for b in ('keystone', 'suryodaya') for f in load(b)['tables']['FileAttachment'] if f.get('folder_id')]; print(len(rows), 'names parsed'); [print(b, n, '->', r.raw, r.scheme, r.flags) for b, n in rows if (r := p(n))]"
python -c "from agent.skills.revisions import parse_revision as p; print(p('X-Rev10.pdf').ordinal > p('X-Rev2.pdf').ordinal, p('X_RevAA.pdf').ordinal > p('X_RevZ.pdf').ordinal, p('X_RevB_RevC.pdf').flags, p('X_RevO.pdf').flags)"
```
Output on the 26 Sept Keystone fixture. Each drawing name appears twice, once for the original and once for its 23 Sept copy:
```text
51 names parsed
keystone J-KNOB-09_RevA.dxf -> A letter ()
keystone KJ-BRKT-04_RevA_BenchBracketSet.pdf -> A letter ()
keystone J-PIN-07_RevB_LocatingPin.pdf -> B letter ()
keystone FG-HDR-1800_RevD_AugerBracketAssy.pdf -> D letter ()
keystone J-BRKT-04_RevC_JigBracket.pdf -> C letter ()
keystone J-BRKT-04_RevB_JigBracket.pdf -> B letter ()
keystone J-KNOB-09_RevA.dxf -> A letter ()
keystone FG-HDR-1800_RevD_AugerBracketAssy.pdf -> D letter ()
keystone J-PIN-07_RevB_LocatingPin.pdf -> B letter ()
keystone KJ-BRKT-04_RevA_BenchBracketSet.pdf -> A letter ()
keystone J-BRKT-04_RevB_JigBracket.pdf -> B letter ()
keystone J-BRKT-04_RevC_JigBracket.pdf -> C letter ()
suryodaya FAI-BT-2400-RevC.pdf -> C letter ()
suryodaya TFA-CRSS-MBR-RevB.pdf -> B letter ()
suryodaya KPL-PMP-BASE-Rev2.pdf -> 2 number ()
suryodaya BEV-BUSBAR-RevA.pdf -> A letter ()
suryodaya BEV-BT-2400-RevC.pdf -> C letter ()
True True ('several revision markers in the name',) ('uses I or O, which revision schemes usually skip',)
```

**S13: a tidy on the fake server, then restore**
```python
from harness.fake_server import FakeServer
from agent.runtime import build, make_model
from agent.loop import run_agent
from agent import snapshot
server = FakeServer.from_fixture("keystone", None)
rt = build("keystone", "fake", "apply", None, transport=server)
ids = rt.guard.allowlist
snap = snapshot.take(rt.admin_mcp, ids)
result = run_agent("Tidy the incoming folder.", rt.ctx, make_model("scripted", rt.settings), rt.budget, rt.trace)
print(server.tables["FileAttachment"]["1ee27946-7064-42e1-afce-376068a545bf"]["description"])
for e in server.tables["AgentEscalation"].values():
    print(e["subject"], "; reason_code:", e["reason_code"], "; party_id set:", bool(e.get("party_id")))

print("rows changed by the tidy:", len(snapshot.diff(snap, snapshot.take(rt.admin_mcp, ids))))
report = snapshot.restore(rt.admin_mcp, snap, rt.trace, allowlist=ids, writes=rt.guard.writes, me=rt.session.me()["id"])
print("restored:", len(report["restored"]), "; diff after restore:", snapshot.diff(snap, snapshot.take(rt.admin_mcp, ids)))
```
Output (27 Sept, 26 Sept fixture). The date in the output is the day when you run it. Offline, the allow-list is all 18 Incoming files. Thus the agent escalates all 13 unfiled files:
```text
Shop floor timesheet, week 33. Belongs in HR.
[Files Agent 2026-09-27] Moved Incoming -> HR. Evidence: description, filename_pattern, sender. Score: 4 (threshold 3).
[files-agent] 782cdca0-b02d-4735-936b-a75cfac15892 Cert_MillCert_SS304_Heat90114.pdf ; reason_code: other ; party_id set: False
[files-agent] 9af1955d-753e-4c7a-b8f9-6e885ca3057e IMG_20260814_093214.jpg ; reason_code: other ; party_id set: False
[files-agent] 8018a70b-47d5-472b-88b6-b1ced1ced8b0 IMG_20260814_093214.jpg ; reason_code: other ; party_id set: True
[files-agent] 9b27de51-e04a-404c-b737-3d0133580b39 J-KNOB-09_RevA.dxf ; reason_code: other ; party_id set: False
[files-agent] c0c8b9c0-85c2-4528-b574-1f35665616b6 PO_4471_ApexMetals_signed (1).pdf ; reason_code: other ; party_id set: False
[files-agent] 82f83d94-5a46-4df3-9ee1-61e8b3c79d6e PO_4471_ApexMetals_signed (1).pdf ; reason_code: other ; party_id set: True
[files-agent] 3dd05bfb-f423-44bb-ad0f-fc94acca3ced PO_4471_ApexMetals_signed.pdf ; reason_code: other ; party_id set: False
[files-agent] 30f72e5c-e340-4c9c-9495-06df2f0aa4f6 Untitled.pdf ; reason_code: other ; party_id set: False
[files-agent] 60f685c9-bcb5-43a3-a403-18b7e9d76368 Untitled.pdf ; reason_code: other ; party_id set: False
[files-agent] 20d633ba-251f-494a-974d-e83d5e9d0695 W9_JMillerWelding_2026.pdf ; reason_code: other ; party_id set: False
[files-agent] f6f748ab-6a24-4c76-ac54-39b24cf3bc9b scan0042.pdf ; reason_code: other ; party_id set: False
[files-agent] b1d3894c-12e9-4ee1-b1da-82c7191ed4a0 scan0042.pdf ; reason_code: other ; party_id set: False
[files-agent] 6477085f-2a2a-4da8-9009-a86af39e69a0 timesheet_week33.xlsx ; reason_code: other ; party_id set: False
rows changed by the tidy: 5
restored: 5 ; diff after restore: {}
```

**S13 with the live cap** (a rehearsal of the live write run, as TI2L does). Change the `build` line to `rt = build("keystone", "fake", "apply", None, transport=server, live_allowlist=True)`. Output (27 Sept):
```text
Shop floor timesheet, week 33. Belongs in HR.
[Files Agent 2026-09-27] Moved Incoming -> HR. Evidence: description, filename_pattern, sender. Score: 4 (threshold 3).
[files-agent] 8018a70b-47d5-472b-88b6-b1ced1ced8b0 IMG_20260814_093214.jpg ; reason_code: other ; party_id set: True
[files-agent] 82f83d94-5a46-4df3-9ee1-61e8b3c79d6e PO_4471_ApexMetals_signed (1).pdf ; reason_code: other ; party_id set: True
[files-agent] 60f685c9-bcb5-43a3-a403-18b7e9d76368 Untitled.pdf ; reason_code: other ; party_id set: False
[files-agent] b1d3894c-12e9-4ee1-b1da-82c7191ed4a0 scan0042.pdf ; reason_code: other ; party_id set: False
rows changed by the tidy: 5
restored: 5 ; diff after restore: {}
```
The agent escalates only the 4 unfiled originals. The 9 copies have no escalation and no write.

**S14: restore does not change another team's change**
```python
from harness.fake_server import FakeServer
from agent.runtime import build, make_model
from agent.loop import run_agent
from agent import snapshot
server = FakeServer.from_fixture("keystone", None)
rt = build("keystone", "fake", "apply", None, transport=server)
ids = rt.guard.allowlist
snap = snapshot.take(rt.admin_mcp, ids)
result = run_agent("Tidy the incoming folder.", rt.ctx, make_model("scripted", rt.settings), rt.budget, rt.trace)
# "another team" moves the timesheet from HR to Quality after our write
server.tables["FileAttachment"]["1ee27946-7064-42e1-afce-376068a545bf"].update(folder_id="585da032-09fe-43cd-9440-c6f01824f5fc", updated_by="another-team")
report = snapshot.restore(rt.admin_mcp, snap, rt.trace, allowlist=ids, writes=rt.guard.writes, me=rt.session.me()["id"])
print(report["conflicts_left_alone"])
```
Output: `{'1ee27946-7064-42e1-afce-376068a545bf': {'folder_id': {'snapshot': '6f8a3ed1-f2df-46a7-8dcb-275e9494c799', 'now': '585da032-09fe-43cd-9440-c6f01824f5fc', 'updated_by': 'another-team'}}}`. Restore still restores the old value of the description of the timesheet (a field that the agent writes).

**S15: 1 e-sign row, with and without the leak guard**
```python
from harness.fake_server import FakeServer
from agent.runtime import build
from agent.privacy import sanitise_file
server = FakeServer.from_fixture("keystone", None, extra_files=[{"filename": "Offer Letter - Canary.pdf", "entity_type": "EsignDocument", "folder": ""}])
rt = build("keystone", "fake", "plan", None, transport=server)
row = next(f for f in server.tables["FileAttachment"].values() if "Canary" in f["filename"])
print("stored:", row["filename"], "; what skills, the model and traces get:", sanitise_file(row, rt.catalog.can_list)["filename"])
```
Output: `stored: Offer Letter - Canary.pdf ; what skills, the model and traces get: EsignDocument-attachment-af1fc223.pdf`. The guard uses the tool list to decide. This seat has no `EsignDocument.list`, so the row is outside the seat.

#### Phase 3: Agent loop

| Task | Run it | You should see | Break it on purpose |
|---|---|---|---|
| **T3.0** The loop ✅ | `python -m agent --target fake ask "How many files are in the Drive?"`, then open the trace | `model_turn` events, the `mcp_call` events of the skill, then `answer`. The scripted model only calls skills. To see the model do its own direct reads, use `--model anthropic`. These reads use tools with names like `mcp__FileAttachment__list`. | ① An error inside an HTTP-200 reply: task D4. The model receives the error as a tool error (`Tool error (agent_error): Injected failure (fake server)`). It never counts as "no such part". ② The turn cap: `AS_MAX_TURNS=1 python -m agent --target fake ask "Find the drawing for part J-BRKT-04."` gives `No answer (turn limit reached).`, a status line that ends with `ABORTED max_turns`, and exit code 2. |
| **T3.1** Router ✅ (questions 👤) | `python -m harness routes` | `10 of 10 routed as expected.` This result is from the scripted model, and its router is specific to these questions. Thus the result tells you nothing about the real model. Real model: `python -m harness routes --model anthropic`. | A question outside the seat: `python -m agent --target fake ask "What is the weather in Paris?"` gives the answer `I can't map that request to anything this Files seat can do.` |
| **T3.2** Answer writer 🟡 | `python -m harness run D1 --target fake --repeat 1 --set check` | D1 passes, and its `cited_ids_resolve` check also passes: each id in the answer exists on the platform. If an id in the answer was not in any tool result, `ask` also prints `[warning: ids in the answer not seen in any tool result: …]`. The answer is the text of the model plus a *Record trail*. The agent does not make the answer only from records. | Plant an invented id (S16). The output lists it as unverified. `harness calibrate` also plants one (`invented_id`), and `cited_ids_resolve` catches it. If you remove a record, this does **not** remove a fact from the answer, because the model writes free text. No automatic check examines the filenames and part codes in the answer. |
| **T3.3** Command line ✅ | `python -m agent --target fake ask "Tidy the incoming folder."` | Plan-only by default: `(plan only - nothing was changed)` and `writes 0`. | WARNING: Make sure that `AS_ALLOW_WRITES` is not set in your shell. If it is set, command ② can start the live write run.<br>① `python -m agent ask "Tidy the incoming folder." --apply` says ``refused: `ask --apply` writes only on the fake server. Live writes go through `python -m harness run TI2L --target live --live-apply` …`` and exits 3. ② `python -m harness run TI2L --target live --live-apply` says `TI2L: SKIPPED - Live writes need AS_ALLOW_WRITES=1 set in the shell for this one command (the .env file is ignored for it) as well as --live-apply.` Without `--live-apply`, it says `TI2L: SKIPPED - TI2L writes; on the live platform it needs --live-apply and AS_ALLOW_WRITES=1`.<br>Any other write task, even with `--live-apply` and `AS_ALLOW_WRITES=1`: `TI2: SKIPPED - TI2 is not marked live_write = true, so it never writes on the live platform (only TI2L is: …)` (the same for TI3 and R4). These refusals occur before any connection. On 27 Sept, an offline check confirmed them with a direct call to `planned_runs` in `harness/runner.py`.<br>③ Keystone only (S17): `WritesNotAllowed: Live writes are only allowed on keystone.` is the error. `harness run` takes the business from the task file, so `--business` does not change it. |
| **T3.4** Budget guard ✅ | Any `ask`: read the status line, or `ledger` in the `result` of a run file | For D1 with the scripted model: `cost {'turns': 2, 'mcp_calls': 3, 'input_tokens': 0, 'output_tokens': 0, 'usd': 0.0}`. The scripted model uses no tokens. With `--model anthropic`, compare the tokens and $ with the usage page of your provider. The prices come from `AS_PRICE_IN_PER_MTOK` and `AS_PRICE_OUT_PER_MTOK`. The score report has a cost column. | ① `AS_MAX_TURNS=1` gives `ABORTED max_turns` (T3.0). ② `AS_MAX_MCP_CALLS=2 python -m agent --target fake ask "Find the drawing for part J-BRKT-04."` gives `Stopped: MCP call cap reached (2).`, a status line that ends with `ABORTED budget`, and exit code 2. ③ Only a run with the real model can reach the `AS_MAX_USD` cap. Defaults: 12 turns, 80 MCP calls, $0.50 per question. |
| **T3.5** The record of goals ⛔ | This task waits for the answer to staff question Q5. | 7.2 block C changes as expected, or the README explains why not. On 22 Sept 2026, both goals were `False`, with jobs 0. | — |

**S16: an id the agent never saw**
```bash
python -c "from agent.answer import compose; print(compose('The drawing is 12345678-aaaa-bbbb-cccc-1234567890ab.', [], set())['unverified_ids'])"
```
Output: `['12345678-aaaa-bbbb-cccc-1234567890ab']`

**S17: live writes are Keystone-only**
```bash
python -c "from agent.runtime import check_write_permission; from agent.config import get_settings; check_write_permission('live', 'apply', get_settings('suryodaya', env={'AS_ALLOW_WRITES': '1'}))"
```
Last line: `agent.runtime.WritesNotAllowed: Live writes are only allowed on keystone.` The check sends nothing, because it runs before any connection.

#### Phase 4: Harness

| Task | Run it | You should see | Break it on purpose |
|---|---|---|---|
| **T4.1** Task files ✅ (expectations 👤) | `python -m harness list` | 22 tasks load: C1–C3, D1–D4, DU1, G1, R1–R5, TI1–TI7, TI2L. Each task has an `[expect]` table. When a task loads, the loader refuses 2 `extra_files` with the same id (for example, 2 with 1 filename and no `id`). The refusal names both files. | ① A typo in an expectation key gives an error (S18). The typo does not silently disable the check. ② A teammate finds 2–3 expectations from live data (7.2) alone. These expectations must match yours. |
| **T4.2** Runner ✅ | `python -m harness run D1 --target fake --set check5` (5 repeats by default) | `runs/check5/D1/1.jsonl` to `5.jsonl`, plus `expected.json` (`{"D1": 5}`), `score.json` and `report.md`. | Crash the scorer (S8): the run files are still there. |
| **T4.3** Verifiers ✅ (checks 👤) | `python -m harness score runs/check` | Each task shows PASS. | ① A file ends in the wrong folder on the fake server (S19). The output is `final_folder:81857de6: expected cbb1441f-…, found 13c03c65-…`. ② `python -m harness calibrate runs/check` has 31 kinds of mistake. It plants the 30 kinds that apply now. No task expects an archive, so `unarchived` has nothing to plant. The output is `377 of 377 injected faults caught.` (4 Oct, with TI7).<br>Earlier results: `355 of 355` on 3 Oct, after the STRIDE fixes. `295 of 295` with 26 kinds on 27 Sept. `265 of 265` on 19 tasks on 22 Sept. |
| **T4.4** Claims vs state ✅ (👤) | Any apply task, for example TI2 | `claims_vs_state` passes. | ① A claimed move that never happened: this is the `liar` mistake of calibration. `claims_vs_state` catches it. ② A change by "another team" in TI4 and TI5: the check still passes. It records the change (S20). |
| **T4.5** Fault injection ✅ | `python -m harness run D4 --target fake --repeat 1 --set check` | D4 passes. | D4 enables `http401_once`: 1 re-login, then the run continues. It also enables `error_in_200:Item.list`: the agent handles the error and reports it. The docstring of `harness/fake_server.py` has the full list of faults. |
| **T4.6** Scoring ✅ | Make a set where 1 task passes 4 of 5. Run D1 ×5 (T4.2). Delete `runs/check5/D1/3.jsonl`. Then run `python -m harness score runs/check5`. | D1 shows 5 runs, 4 passed, `FAIL`, with `- D1/3.jsonl: missing: no run file was written (the run crashed)`. The cost column and the total are the sums of the `usd` values of each run. With the scripted model, all are 0. | — |
| **T4.7** Manifest ✅ | S21 reads the first line of a run file. | `git` gives the commit and whether the tree was dirty. Before the first commit, it is `no-commit`. Then come `model`, `tool_hash` `c10a009a80de46c6` and `fixture`. `fixture` gives the folder `…\2026-09-26` and the hash `df2a585221ef9f25` (`8bf8e438f43d618a` before the 2 Oct scrub).<br>Then come `business`, `user_id`, `started_at` and the allow-list. The allow-list has 18 ids offline (all of Incoming), and 9 for TI2L and on live. (22 Sept: `cc08bae6517ed3cb`, `f128c97d66753c72`, 9 ids.) | Change the tool list of the fake server (S4). The hash changes to `97c1058771f8a313` (22 Sept fixture: `aed5ef44441abbea`). |
| **T4.8** Rescore ✅ | `python -m harness rescore runs/check` | `rescore IDENTICAL to score.json` | ① Change a number in `score.json` by hand. The output is `rescore DIFFERS from score.json`, with exit code 1.<br>② CAUTION: Do not run `rescore` after you delete `score.json`. It has nothing to compare with, so it says `DIFFERS`.<br>Make the files again from nothing. Copy `score.json` and `report.md` to a different place. Delete them. Run `python -m harness score runs/check`. Compare the new files with the copies. The files are identical. |
| **T4.9** Pre-flight ✅ | Live: `python -m harness preflight`. Offline: S22. | Live (27 Sept): `pre-flight OK`, then `warnings (not blocking):` with 9 lines. There is 1 line for each 23 Sept copy, for example `W9_JMillerWelding_2026.pdf (20d633ba-…) is in Incoming but outside the write allow-list: it will not be written or escalated`. (The check from before 27 Sept failed live with 10 problems.) Offline: `unchanged: [] ; 9 warnings, …`. | S22 changes the `updated_at` of an Incoming row and removes a required tool. The output lists all 4 problems. A removed tool changes the tool hash and the text hash of the tools. S22 also adds an unknown file to Incoming. This is a problem, not a warning.<br>It also adds a new file in Quality with the same name as the mill certificate original. This is a problem, because under the same-name rule the agent would then not move the original.<br>In a live write run, any problem stops the run with `Pre-flight failed; nothing was written`. This occurs before the snapshot and before any write. The run prints and traces the warnings, and then it continues. |

**S18: a typo in a task file**
```python
import pathlib, tempfile
from harness.tasks import load_task
path = pathlib.Path(tempfile.mkdtemp()) / "X1.toml"
path.write_text('id = "X1"\nquestion = "q"\n[expect]\nwrites_typo = 0\n', encoding="utf-8")
load_task(path)
```
Last line: `ValueError: X1.toml: unknown expectation(s) ['writes_typo']`

**S19: a verifier catches a wrong final folder**
```python
from pathlib import Path
from harness.tasks import Task, load_all
from harness.runner import run_task
from harness.verifiers import load_run, verify
ti2 = load_all()["TI2"].to_dict()
# the same task, but "another team" first moves the W-9 into HR, so it ends in the wrong folder
broken = Task.from_dict({**ti2, "faults": ["moved_row:81857de6-e6e9-41c5-9da8-67cb5d1903c1:13c03c65-ddae-4d61-9e2f-b9167168277f"]})
path = run_task(broken, target="fake", model_kind="scripted", set_dir=Path("runs/check-broken"), repeat=1)[0]
print([f"{c.name}: {c.detail}" for c in verify(load_run(path)) if not c.ok])
```
Output: `['final_folder:81857de6: expected cbb1441f-5a73-4989-846b-775f6a1e9e70, found 13c03c65-ddae-4d61-9e2f-b9167168277f']`. Only that check fails. The move by the other team is a foreign change, not a change of the agent.

**S20: the check logs foreign changes, and does not fail**
```bash
python -c "from pathlib import Path; from harness.verifiers import load_run, verify; print([c.detail for c in verify(load_run(Path('runs/check/TI4/1.jsonl'))) if c.name == 'claims_vs_state'])"
```
Output: `[" (foreign changes ignored: ['81857de6'])"]`

**S21: the run manifest**
```bash
python -c "import json; m = json.loads(open('runs/check/D1/1.jsonl', encoding='utf-8').readline()); print({k: m[k] for k in ('git', 'model', 'tool_hash', 'fixture', 'business', 'user_id', 'started_at')}, len(m['allowlist']), 'allow-listed ids')"
```
Output (27 Sept, on the PR #3 branch with uncommitted changes): `{'git': {'commit': 'd17b7630371fc7de956d2aace2caba5a048ea56b', 'dirty': True}, 'model': 'scripted', 'tool_hash': 'c10a009a80de46c6', 'fixture': {'dir': '…\\harness\\fixtures\\keystone\\2026-09-26', 'hash': '8bf8e438f43d618a'}, 'business': 'keystone', 'user_id': '2b5bbcef-ce22-44dc-a49c-5e2f7a165b9f', 'started_at': '…'} 18 allow-listed ids`. Your commit, folder and time will be different. On 22 Sept, before the first commit and the data change, it said `'commit': 'no-commit'`, `cc08bae6517ed3cb`, `f128c97d66753c72` and 9 ids.

**S22: pre-flight on unchanged and drifted data**
```python
from harness.fake_server import FakeServer
from harness import fixtures, preflight
from agent.runtime import build
fixture = fixtures.load("keystone")
same = build("keystone", "fake", "plan", None)
problems, warnings = preflight.assess(same, fixture)
print("unchanged:", problems, ";", len(warnings), "warnings, e.g.", warnings[0])
drift = FakeServer.from_fixture("keystone", None, faults=("drift_updated_at:81857de6-e6e9-41c5-9da8-67cb5d1903c1", "missing_tool:DriveAccessLog.list"))
print("drifted:", preflight.check(build("keystone", "fake", "plan", None, transport=drift), fixture))
extra = FakeServer.from_fixture("keystone", None, extra_files=[{"filename": "new_upload.pdf"}])
print("unknown extra:", preflight.check(build("keystone", "fake", "plan", None, transport=extra), fixture))
elsewhere = FakeServer.from_fixture("keystone", None, extra_files=[{"filename": "Cert_MillCert_SS304_Heat90114.pdf", "folder": "Quality"}])
print("same name in Quality:", preflight.check(build("keystone", "fake", "plan", None, transport=elsewhere), fixture))
kind = FakeServer.from_fixture("keystone", None, extra_files=[{"filename": "MillCert_A36_Heat70.pdf", "folder": "Purchasing", "tags": ""}])
print("same kind in Purchasing:", preflight.check(build("keystone", "fake", "plan", None, transport=kind), fixture))
```
Output (3 Oct, 26 Sept fixture, with PR #4 and the STRIDE fixes):
```text
unchanged: [] ; 9 warnings, e.g. W9_JMillerWelding_2026.pdf (20d633ba-251f-494a-974d-e83d5e9d0695) is in Incoming but outside the write allow-list: it will not be written or escalated
drifted: ['missing tool DriveAccessLog.list', 'tool catalogue changed (fixture c10a009a80de46c6, live 97c1058771f8a313): re-capture fixtures', 'the description or read-only mark of a tool the agent uses changed since the fixture: re-capture fixtures', 'W9_JMillerWelding_2026.pdf changed since the fixture (updated_at 2026-10-03T…)']
unknown extra: ["new_upload.pdf (52723a65-f91b-56ad-992f-c3411125b9b7) is not in the fixture (outside the allow-list, but the live expectations assume the fixture's Incoming)"]
same name in Quality: ['Cert_MillCert_SS304_Heat90114.pdf (af68a7db-b02b-5802-ae4c-8386153cbbb2) is new or changed since the fixture and is related to an allow-listed file (name, hash or document kind)']
same kind in Purchasing: ['MillCert_A36_Heat70.pdf (d09988d8-6e1f-5103-a082-9c4815eb3ff0) is new or changed since the fixture and is related to an allow-listed file (name, hash or document kind)']
```
The fixture contains the 9 copies, and they did not change. Thus they are only warnings. The fixture does not contain the planted `new_upload.pdf`. Thus it is a problem.

A new file outside Incoming is important only if it has a relation to one of the 9 files. These are the relations:
- It has the same name or recorded hash as 1 of the 9. The planted mill certificate in Quality is an example.
- It is the same kind of document. The planted mill certificate in Purchasing is an example. 3 of those files are enough to change the move of the real mill certificate to Quality into a conflict. The reason is that the similar-file signal counts every mill certificate in the drive. 2 drawings are the same kind when they share a code prefix.

A change to a folder is also a problem. This includes a folder that is new, gone, renamed, moved or archived (`folder 'Quality' (585da032-…) was renamed, moved or archived since the fixture (now 'QA')`). It also includes any other update to a folder, and 2 folders with 1 name.

`preflight.check` returns only the problems. `preflight.assess` returns the problems and the warnings.

(The "same kind" check and the folder checks are from 2 Oct 2026. Before that date, pre-flight passed while 3 new mill certificates in Purchasing changed the plan.)

---

### 7.4 Are your own tests any good? (Phase 5)

This guide gives you no test cases. The test cases must be yours (T5.1–T5.10). [`tests/README.md`](../tests/README.md) lists what each test must cover and the module under test. It also lists parts that you can use: `FakeServer.from_fixture`, `agent.runtime.build`, the faults, the leak-guard canary and `snapshot.plan_restore`. But you can check if a test does its job:

**1. Break the code, and the test must fail.** Do these steps for each test:

1. For a short time, sabotage the code that the test checks.
2. Run the test. The test must fail.
3. Undo the change.

If the test still passes, the test is too weak.

| Your test | Sabotage to try | Where |
|---|---|---|
| T5.1 parser | Sort revisions as plain text, so "Rev10" comes before "Rev2" | `agent/skills/revisions.py` |
| T5.2 scoring | Let a description alone decide the folder | `agent/skills/triage.py` (`_score`) |
| T5.3 duplicates | Trust a hash that many files share | `agent/skills/duplicates.py` (`untrustworthy_hashes`) |
| T5.4 guards | Allow every id | `agent/guards.py` (`update_file`) |
| T5.5 client | Treat HTTP 200 as success, without a check for an error inside the reply | `agent/mcp_client.py` (`_rpc`) |
| T5.6 safe reads | Send `ne:` to the server | `agent/safe_reads.py` (`list_all`, `not_equal`) |
| T5.7 verifiers | Make a verifier always return "pass" | `harness/verifiers.py` |
| T5.8 idempotency | Skip the "already escalated?" check | `agent/skills/escalate.py` (`escalate`) |
| T5.9 redaction | Disable redaction (S5 shows the effect) | `agent/redact.py` |
| T5.10 budget | Remove the cap | `agent/budget.py`, `agent/loop.py` |

Know these 2 things when you write the tests:
- **T5.6:** the fake server does not reproduce the `ne:` trap. It returns 0 rows for `entity_type=ne:Item`. The live platform returns 98 since 23 Sept, and it returned 83 on 22 Sept. Thus, test what `list_all` *sends*. Or, give it your own small substitute that behaves like the platform.
- **T5.10:** the turn cap aborts the run with `max_turns`. The MCP-call cap and the $ cap abort the run with `budget`. The agent never starts a write without budget for its read, its write and the read that confirms it (`Budget.reserve(3)`).

**2. Offline, fast and repeatable.** Tests must not call the live platform or the model. Use the saved fixtures. The same input must always give the same result.

Some values change on each run. Be careful with them: the date in provenance notes, and the random ids of new sessions and escalations.

**3. One behaviour per test.** Give each test the name of its behaviour.

**4. Show that it is your work.** Write and commit the tests yourselves. The commit history is your evidence that AI did not write them.

(On 22 Sept 2026, there were no commits yet. The merge of PR #1 was later that day. On 2 Oct, PR #4 added the first 78 hand-written tests. On 3 Oct, PR #5 added 79 more.)

Run them with the standard library: `python -m unittest discover -s tests`. Staff question Q3 asks if you can use `pytest`. `python -m harness calibrate` checks the verifiers of the harness. But AI helped to write it, so it does not count as your tests. If you want harness checks to count, write your own versions in `tests/`.

---

### 7.5 Gates before moving on

Mark these gates as complete before you start the next phase.

| Gate | Tick when | State on 22 Sept 2026 (27 Sept where marked) |
|---|---|---|
| **M1** (end of Phase 1) | The agent signs in to both businesses (`python -m agent whoami`, with and without `--business suryodaya`). MCP errors raise (S3, D4). Redaction removes the secrets from the traces (block D says `no secrets found`). The fixture capture is complete. The fake server matches live (`smoke` side by side). A run file survives a crash of the scorer (S8). | ✅ built. The capture of the fixtures for both businesses was on 22 Sept 2026. The capture of Keystone was again on 26 Sept. Thus the Suryodaya fixture is now out of date. Phase 0 is still open: staff answers (T0.1). The secret scan of the git history (T0.2) ran on 2 Oct and found nothing. |
| **M2** | `python -m harness run D1 D2 D3 D4 --target fake` passes, and `ask` for `J-BRKT-99` says `No part has the exact code J-BRKT-99. I did not guess.` | ✅ offline |
| **M3** (end of Phase 2) | TI1 makes 0 writes. TI2 and TI2L write only allow-listed ids. TI2L does not write or escalate any of the 9 copies. Restore gives an empty diff (S13).<br>TI4 skips the moved row. TI5 reports FAILED. TI6 flags the conflict. TI3 makes no second escalation. | ✅ offline (27 Sept) · 🟡 restore did not run live yet |
| **M4** (end of Phase 3) | R1–R5 pass. `AS_MAX_TURNS=1` gives `ABORTED max_turns`, and `AS_MAX_MCP_CALLS=2` gives `ABORTED budget`. On live, `ask --apply` stops with a refusal. Without `AS_ALLOW_WRITES=1`, `harness run TI2L --target live --live-apply` stops with a refusal. On live, all other write tasks also stop with a refusal. | ✅ with the scripted model (27 Sept) · real-model runs not done yet |
| **M5** (end of Phase 4) | `harness calibrate` catches every planted mistake. Claims-vs-state catches a fake claim and ignores foreign changes (S20). `harness rescore` says IDENTICAL. Pre-flight reports drift (S22). Live, `python -m harness preflight` says `pre-flight OK`. | ✅ offline: 377 of 377 caught on the 22 tasks (4 Oct, see T4.3). 295 of 295 caught on the 21-task set (27 Sept). 265 of 265 caught on the 19 tasks of 22 Sept. Live pre-flight on 27 Sept: `pre-flight OK` with 9 warnings. Run it again yourselves immediately before the write run. |

To do a quick offline check of M2–M5, run `python -m harness run all --target fake`. Then run `python -m harness rescore runs/<set>` and `python -m harness calibrate runs/<set>`.
