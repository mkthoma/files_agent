# How to check each part

This file holds these sections of the old README (before the split), word for word: 7, from its introduction to 7.5.

---

## 7. How to check that each part works

This is a **checking guide**. For each part it says how to run it, what you should see, and how to break it on purpose to prove it fails safely. It is **not** your tests. The brief says *"a test written by Claude or Codex scores zero"*, so the Phase 5 tests and their expected answers must be written by you (see [7.4](#74-are-your-own-tests-any-good-phase-5)). Use these checks while you build, then turn the ones that matter into your own tests.

Every offline command and snippet below was first run on 22 Sept 2026 against `harness/fixtures/keystone/2026-09-22/`. All snippets (S1–S22), the O-checks in 7.2 and every command whose output changed were **re-run on 27 Sept 2026** against the newest fixture, `harness/fixtures/keystone/2026-09-26/` (the fake server always loads the newest), with `PYTHONIOENCODING=utf-8`. The output shown is the real output of that run. Live values can't be re-checked offline: they are the values measured live on 22 Sept 2026, or on 27 Sept where the text says so. S3, S10 and S22 were re-run on 3 Oct 2026 on the tree that merges PR #4 with the STRIDE fixes: S3 now shows the client refusing an unknown tool before sending it (STRIDE E3), and S10 calls `_allowlist` with `fake=False` (its new signature). Every other snippet still gives the output shown.

**How to read the commands**
- Run everything from the repo root. There is nothing to install.
- `python -m agent …` talks to the **live** platform unless you add `--target fake`. `python -m harness run …` uses the fake server and the scripted model unless you say otherwise.
- Switches are shown in bash form: `AS_MAX_TURNS=1 python -m agent …`. In PowerShell write `$env:AS_MAX_TURNS = "1"; python -m agent …; Remove-Item Env:AS_MAX_TURNS`.
- **Snippets** (S1, S2, …) come in two kinds. A `python -c "…"` line is a shell command: run it in the repo root. A block of Python lines is for the Python prompt: start `python` in the repo root and paste it in. If printing fails with a `UnicodeEncodeError`, set `PYTHONIOENCODING=utf-8` first.
- Offline runs use the scripted model. Its passing runs say nothing about the real model's judgement.
- Run sets go to `runs/<set>/` (git-ignored). Many checks read the run files of one offline set, so make it first:

```bash
python -m harness run all --target fake --repeat 1 --set check
# ... 22 of 22 tasks pass on every run.
```

**Status key:** ✅ built · 🟡 partly built · 🛠 platform work (staff) · 🐞 platform defect (bug raised) · ⛔ not built · 👤 team's job (hand-written by you).

---

### 7.1 Three ways to check anything

Do all three for every task, in this order:

| # | Check | Question it answers | Example |
|---|---|---|---|
| 1 | **Run it** | Does it work at all? | `python -m agent --target fake ask "Find the drawing for part J-BRKT-04."` prints an answer that names `J-BRKT-04_RevC_JigBracket.pdf` |
| 2 | **Compare with the truth** | Is the answer *right*? Check it against the platform directly ([7.2](#72-ground-truth-ask-the-platform-directly)), never against the agent's own output. | The drawing the agent calls current must be the one 7.2 "That part's drawings" shows as not archived (RevC). |
| 3 | **Break it on purpose** | Does it fail *safely*? Feed it a fault and check that it refuses, stops or reports. | Put a wrong password in `.env`: you get `Login failed for team20@theschoolofai.in (HTTP …). Check the password in .env.`, and the password appears nowhere. |

**Where to check, safest first:**

| Where | How | Use it for |
|---|---|---|
| **1. Offline** | `--target fake`. The fake server runs inside your Python process, built from the newest fixture in `harness/fixtures/`. | Almost everything. It is free, fast and repeatable. It is a simplified copy: any login works, list filters are plain equality (the platform's filter traps are not copied), and it starts with no escalations. |
| **2. Live, read-only** | `python -m agent ask …` (plan-only by default), `python -m agent smoke`, `python -m harness run D1 D2 D3 DU1 C1 C2 R1 R2 R3 R5 TI1 --target live --repeat 1`, `python -m harness capture keystone`, `python -m harness preflight`, and the PowerShell commands in 7.2. | Checking against the real, changing data. It changes nothing. |
| **3. Live, with writes** | `AS_ALLOW_WRITES=1 python -m harness run TI2L --target live --live-apply …` | Only TI2L, only once, only after pre-flight and with the repo owner's go-ahead ([7.6](live-run.md#76-before-during-and-after-the-live-write-run), [11](live-run.md#11-the-live-write-run)). |

**Quick "is it alive?" commands.** They are the fastest way to do check 1, and they are not tests.
- `python -m harness smoke`: offline. It runs D1, TI1 and TI2, scores, rescores and calibrates. You should see `OK   run + score`, `OK   rescore identical` and `OK   calibration catches faults`.
- `python -m agent --target fake smoke`: offline login, tool discovery and one read.
- `python -m agent smoke`: the same, live and read-only. It exits 1 if a required tool is missing.

---

### 7.2 Ground truth: ask the platform directly

These commands read the real answer straight from the platform, without your agent, so you can compare. They only read. Run them in **PowerShell**, in one window, from the repo root. The login reads the password from `.env` (never type it on the command line: shell history and AI-assistant transcripts keep it).

**Setup (once per window):**
```powershell
[Console]::OutputEncoding = [Text.Encoding]::UTF8; $OutputEncoding = [Text.Encoding]::UTF8
$AS = "https://class.agentswitch.theschoolofai.in"
$PW = python -c "from agent.config import get_settings; print(get_settings().password, end='')"
$TOKEN = (Invoke-RestMethod -Method Post -Uri "$AS/api/auth/login" -ContentType "application/json" -Body (@{email = "team20@theschoolofai.in"; password = $PW} | ConvertTo-Json -Compress)).token
Remove-Variable PW
function Get-AS($path) { curl.exe -s "$AS$path" -H "Authorization: Bearer $TOKEN" | Out-String | ConvertFrom-Json }
```

The live column gives the 22 Sept value, and the 27 Sept value where it was re-read live (Keystone then matched the 26 Sept fixture exactly). The offline column is the 26 Sept fixture, as loaded on 27 Sept.

| What you're checking | Live command | Live value, 22 Sept 2026 (27 Sept) | Offline value (26 Sept fixture) |
|---|---|---|---|
| Who you are | `(Get-AS "/api/auth/me") \| Select-Object id, allowed_apps` | `2b5bbcef…`, `agent, crm, drive` | the same (O1) |
| Tool count | see block **A** below | `208` (27 Sept: `212`) | `212` (O2) |
| All files | `(Get-AS "/api/FileAttachment?limit=1").total` | `98` (27 Sept: `113`) | `113` (O3) |
| Files linked to a part | `(Get-AS "/api/FileAttachment?entity_type=Item&limit=1").total` | `6`, so "not a part" = **92** (since 23 Sept: 107) | `6`; not a part `107`; the `ne:` trap `98` (O4) |
| Incoming files | see block **B** below | 9 rows, all `is_archived 0`, `updated_at 2026-09-16T16:27:27…` (27 Sept: 18 rows, the 9 originals unchanged plus 9 copies) | 18 rows: the same 9 plus 9 copies with no tags, `updated_at 2026-09-23T00:41:36…` (O5) |
| The exact part | `(Get-AS "/api/Item?code=J-BRKT-04&limit=5").data \| Select-Object id, code` | 1 row: `bc49e18f…` | the same (O6) |
| That part's drawings | `(Get-AS "/api/FileAttachment?entity_id=bc49e18f-7a20-43e5-83ac-1b41dc7684ea").data \| Select-Object filename, is_archived` | RevB (`1`), RevC (`0`) | the same (O7) |
| Your escalations | `(Get-AS "/api/AgentEscalation?limit=50").total` | `0` (before any live run; still `0` on 27 Sept) | no offline copy: the fixture always starts with an empty escalation list |
| Goal status | see block **C** below | both `False`, jobs `0` | the same, as captured (O8) |

*In the table, `\|` is just an escaped `|`; type a normal `|`.*

**A. Tool count:**
```powershell
(Invoke-RestMethod -Method Post -Uri "$AS/api/mcp" -Headers @{ Authorization = "Bearer $TOKEN" } -ContentType "application/json" -Body '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}').result.tools.Count
```

**B. Incoming files: the "before" picture, to compare against after any run:**
```powershell
(Get-AS "/api/FileAttachment?folder_id=6f8a3ed1-f2df-46a7-8dcb-275e9494c799&limit=50").data | Select-Object id, filename, folder_id, is_archived, tags, updated_at
```

**C. Goal status in the Office view:**
```powershell
((Get-AS "/api/agent/office").seats | Where-Object { $_.seat_number -eq 20 }).goals | Select-Object key, implemented
```

**D. Check that no secret leaked into your run files.** It reads the passwords and the model key from `.env` itself, so you never type them, and also looks for anything shaped like a model key, a JWT or a bearer token. It prints only the file and line (and which rule matched), never the text. The correct result is `no secrets found`. It reads only local files: every tracked file, `runs/` and `harness/fixtures`.
```powershell
python scripts/secret_scan.py
```
The same command works in Git Bash. `python scripts/secret_scan.py --history` scans every line ever added in every commit of every branch the same way.

**Offline equivalents (O1–O8).** These read the newest fixture, captured from live on 26 Sept 2026 (05:18 UTC; the 22 Sept one was captured at 08:41 UTC). They are the ground truth for **offline** runs. The results below are from 27 Sept; the 22 Sept values are in brackets where they differ. For live runs, use the live commands above. They work in bash and PowerShell.

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

O5 output (27 Sept, 26 Sept fixture). The first 9 lines are the copies (no tags, `updated_at` 23 Sept); the last 9 are the originals, unchanged since 22 Sept:
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

**Why 92 and 83 differ (O4).** 98 files = 6 linked to a part (5 filed drawings, plus `J-KNOB-09_RevA.dxf` in Incoming) + 83 e-sign attachments + 9 files with no `entity_type` (the other 8 Incoming files and the mill cert in Quality). "Not a part" is 98 − 6 = **92**. The platform's `ne:` filter silently drops rows whose value is empty, so `entity_type=ne:Item` gives **83**. The skills never send `ne:` (`list_all` in `agent/safe_reads.py` drops it); its `not_equal` helper gives the right answer in Python (O4 uses it), though no skill needs it yet. The fake server does **not** copy the trap: there, `entity_type=ne:Item` simply matches nothing. (Same arithmetic on the 26 Sept fixture: 113 files = 6 linked to a part + 83 e-sign + 15 `entity_type = Drive` (the 23 Sept copies; these are why the Drive screen now shows 15 instead of 0) + 9 with no `entity_type`, so "not a part" is 107 and the `ne:` trap gives 98.)

---

### 7.3 Task-by-task checks

**Columns:**
- **Run it**: how to try it.
- **You should see**: the right result, compared with 7.2 where possible.
- **Break it on purpose**: a fault to inject, and the *safe* behaviour you should get.

Snippets are listed under each phase's table, with their real output.

#### Phase 0: Set-up and decisions

| Task | Run it | You should see | Break it on purpose |
|---|---|---|---|
| **T0.1** Staff questions 🟡 (asked; no replies yet) | Ask staff Q1–Q8. Write each answer, with its date, into the *Answer* column of [6.6](plan-and-status.md#66-questions-for-staff). | Every question has an answer, or "no reply by <date>; assuming X". On 22 Sept 2026 all 8 were still open. | — The plan's gate was: no Phase 1 before Q2–Q4. The code is built anyway, so Q3 (is AI-assisted agent and harness code OK?) is now the open risk. |
| **T0.2** Private repo + secrets 🟡 👤 | `git check-ignore -v .env runs/cli/x.jsonl`, then `gh repo view mkthoma/files_agent --json visibility --jq .visibility` | Two ignore rules: `.gitignore:4:*.env` for `.env` and `.gitignore:8:runs/*` for the run file. `gh` should print `PRIVATE`. On 22 Sept 2026 the repo had no commits yet; PR #1 was merged later that day (checked again on 27 Sept: the two ignore rules are unchanged). | Make up your own test string (never your password, and not an example from this README, which would also match `README.md`), put it in a scratch file inside `runs/`, then run `python scripts/secret_scan.py --also <your string>`: it **must** print that file and line. Delete the file. (Fixtures are *not* git-ignored, because they are meant to be committed, so block D always scans `harness/fixtures` too.) |
| **T0.3** Project set-up ✅ | `python --version`, `python -m agent --help`, then `python -m harness smoke` | Python 3.11 or newer. Usage text. Then three `OK` lines. `pyproject.toml` lists no dependencies: standard library only, no SDK. | A teammate does the same from a fresh clone on their own machine (possible since PR #1 was merged). |
| **T0.4** Audit a provided tool layer ✅ decided (none assumed; redo if staff Q2 says one exists) | Only if staff say one exists (Q2). Put it through the 5 trap checks: a bad tool name; the `ne:` count; exact matching; the export filter; the Drive overview. | A written decision: reuse or rewrite, and why. | Call a tool that doesn't exist through their layer: it must **raise an error**, not return an empty "success". Ours raises (S3). |
| **T0.5** *(optional)* Protect your paths ⛔ | Add a deny rule for `tests/**`, `harness/tasks/**` and `harness/verifiers.py` in `.claude/settings.json` (there is no `.claude/` folder yet). Then ask your AI assistant to edit a file in `tests/`. | The edit is refused. | — |

#### Phase 1: Platform access and offline replay

| Task | Run it | You should see | Break it on purpose |
|---|---|---|---|
| **T1.1** Login ✅ | Live: `python -m agent whoami`, then `python -m agent --business suryodaya whoami`. Offline: `python -m agent --target fake whoami` | Keystone: id `2b5bbcef-…` and `allowed_apps` `['agent', 'crm', 'drive']`, as in 7.2 "Who you are". | ① A wrong password in `.env` stops with `AuthError: Login failed for team20@theschoolofai.in (HTTP …). Check the password in .env.` The password appears nowhere. Offline version: S1. ② An expired token: one re-login, then it carries on (S2). |
| **T1.2** MCP client ✅ | `python -m agent --target fake smoke`; live: `python -m agent smoke` | `FileAttachment total: 113`, as in 7.2 (98 on 22 Sept). | ① A tool that doesn't exist, ② an argument the tool doesn't have (closed schema), ③ `SalarySlip.list`: each one **raises** `McpError` (S3). ④ A `401` and an error inside an HTTP-200 reply: task D4 (`python -m harness run D4 --target fake --repeat 1 --set check`) passes. Its run file has one `relogin` event and a failed `Item.list` call with `error_code` `agent_error`. |
| **T1.3** Tool discovery ✅ | `python -m agent --target fake tools` (first line); live: `python -m agent tools` | `212 tools; hash c10a009a80de46c6; all required tools present` (26 Sept fixture; live matched it on 27 Sept). On 22 Sept both said `208 tools; hash cc08bae6517ed3cb`. | Remove a required tool with the `missing_tool` fault (S4): `PROBLEMS: missing tool DriveAccessLog.list`. `ask` carries on and notes it in the trace; `python -m agent smoke` exits 1. |
| **T1.4** Trace + redaction ✅ | `python -m agent --target fake ask "Find the drawing for part J-BRKT-04."`, then open the trace path it prints (`runs/cli/<time>-ask.jsonl`). | One JSON event per line, in order: `login`, `catalog`, the set-up reads (`mcp_call` ×2), `question`, `model_turn`, the skill's reads (`mcp_call` ×3), `model_turn`, `answer`. A list reply is kept as its total plus up to 50 ids; a single row in full. The `login` event holds only `ok` and the HTTP status. | Run block D (7.2): `no secrets found`. S5 shows the masking, and what leaks when no secrets are registered. |
| **T1.5** Safe reads 🟡 | O4 in 7.2 | Not a part: **107**, not 98 (22 Sept: 92, not 83). | The trap itself: filtering with `ne:` gives 98 (22 Sept: 83; O4 shows why). Live only, since the fake server doesn't copy the trap: `(Get-AS "/api/FileAttachment?entity_type=ne:Item&limit=1").total`. |
| **T1.6** Fixture capture ✅ | Live, read-only: `python -m harness capture keystone` | A folder `harness/fixtures/keystone/<date>/` with `fixture.json` and `manifest.json`. On 22 Sept 2026 the manifest said FileAttachment 98, DriveFolder 8, Item 28, Party 100, DriveAccessLog 5, tools 208, `tool_hash` `cc08bae6517ed3cb`, `fixture_hash` `f128c97d66753c72` (`4b43dedffdd439fa` since the 2 Oct scrub). The 26 Sept manifest says FileAttachment 113, DriveFolder 8, Item 28, Party 100, DriveAccessLog 10, AgentEscalation 0, AgentSession 0, tools 212, `tool_hash` `c10a009a80de46c6`, `fixture_hash` `8bf8e438f43d618a` (`df2a585221ef9f25` since the 2 Oct scrub: access-log rows keep only the fields the agent reads, STRIDE I2). The 18 Incoming files: O5. | ① Note `fixture_hash`, capture again with nothing changed: same hash. A second capture on the same day overwrites the same folder, so note the hash first. ② E-sign titles are replaced before saving (S6: `83 of 83`). ③ Block D (it covers `harness/fixtures`): `no secrets found`. |
| **T1.7** Fake server ✅ | `python -m agent smoke` (live) and `python -m agent --target fake smoke` (offline), side by side | The same first two lines: `login ok: team20@theschoolofai.in (2b5bbcef-…), apps ['agent', 'crm', 'drive']` and `tools: 212 tools; hash c10a009a80de46c6; all required tools present` (while live still matches the fixture). The third line differs on purpose since 23 Sept: offline `FileAttachment total: 113; write allow-list size: 18` (all of Incoming), live `… write allow-list size: 9` (live is capped to the 9 originals). On 22 Sept both said `98` and `9`. | ① The "row moved" fault: task TI4 reports `SKIPPED W9_JMillerWelding_2026.pdf (…): it changed since the plan (now in HR); not overwritten.` ② The fake server runs inside your Python process, so you can't "stop" it. To see an outage, make every request fail (S7): `McpError: platform unreachable: connection refused`. |
| **T1.8** Minimal runner ✅ | `python -m harness run D1 --target fake --repeat 1 --set check` | `runs/check/D1/1.jsonl`, then `score.json` and `report.md` in `runs/check/`. The run file's last line is the `result` event. | Make scoring crash (S8): `RuntimeError: scorer crashed on purpose`, but `runs/crash-test/D1/1.jsonl` is already there and ends with `result`. |

**S1: a wrong password (offline stand-in for the live check)**
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

**S2: an expired token means one re-login**
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

**S7: the platform goes down**
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
Output: `D1: 1 run file(s) written`, then a traceback ending `RuntimeError: scorer crashed on purpose`. `runs/crash-test/D1/1.jsonl` exists and its last event is `result`.

**Tip:** two `ask` runs in the same second share one trace file name, so their events land in one file. Wait a second between runs if you want separate traces.

#### Phase 2: Skills (all offline, on the fake server)

| Task | Run it | You should see | Break it on purpose |
|---|---|---|---|
| **T2.1** Decision records ✅ | S9: make a record, turn it into JSON and back. | `same after a round trip: True` | Leave out a required field: `ValueError: skill and action are required`. A status that isn't allowed (e.g. `done`) is also rejected. |
| **T2.2** Guards ✅ | S10, first line: a write in plan-only mode | `blocked: plan-only mode: update 81857de6-… not sent ; writes sent: 0` | ① A file outside the allow-list (RevC `2683b2c8-…`) in apply mode: `… is not in the write allow-list`. ② The read-only field `is_trashed`: refused before sending. ③ A new file in Incoming: offline it **is** writable (the fake allow-list is "whatever is in Incoming at start"; G1 relies on this). Live it is not, because live writes are capped to the 9 ids: S10 prints `fake allow-list: 19 ; live rule: 9` (the 18 files of the 26 Sept fixture plus the new one; 22 Sept: `10 ; 9`). The live cap also shuts out the 9 copies of 23 Sept, and triage then neither writes nor escalates them (S13 with the live cap). |
| **T2.3** `find_drawing` ✅ | `python -m agent --target fake ask "Find the drawing for part J-BRKT-04."`, then the same for `KJ-BRKT-04` and `J-BRKT-99` | J-BRKT-04: RevC `2683b2c8-…` is current; RevB `91feaf59-…` is superseded (`archived: True, folder 'Superseded'`); KJ-BRKT-04 is named as a different part. KJ-BRKT-04: only `KJ-BRKT-04_RevA_BenchBracketSet.pdf` (`e6010f05-…`). J-BRKT-99: `No part has the exact code J-BRKT-99. I did not guess.` Compare with 7.2 "That part's drawings". | Swap `is_archived` on RevB and RevC with the `swap_archived` fault (S11): `I can't name a single current drawing for part J-BRKT-04: …`, listing both tag conflicts. |
| **T2.4** Revision parser ✅ (tests 👤) | S12, first command: parse every filename in a folder, in both fixtures (30 Keystone on the 26 Sept fixture, 21 Suryodaya). | No crash. 17 revisions found (12 Keystone, since each of the 6 Keystone drawings now has a copy, and 5 Suryodaya), one of them a number (`KPL-PMP-BASE-Rev2.pdf`). No real name is flagged. (22 Sept: 36 names, 11 revisions.) | S12, second command, on made-up names: `Rev10 > Rev2` and `AA > Z` are both `True`; `X_RevB_RevC.pdf` is flagged "several revision markers"; `X_RevO.pdf` is flagged "uses I or O". Your T5.1 tests are the real check. |
| **T2.5** Scoring + threshold ✅ (weights 👤) | `python -m harness run TI1 --target fake --repeat 1 --set check`; and `python -m agent --target fake ask "Tidy the incoming folder."` | TI1 passes: the plan matches **your** `harness/tasks/TI1.toml` (26 Sept data: 5 planned moves of originals; 13 not filed: the IMG, scan0042, Untitled and PO "(1)" originals and all 9 copies). `ask` shows each file's tier and score, e.g. `timesheet_week33.xlsx (…) -> HR (score 4).`, and for the same-name rule `J-KNOB-09_RevA.dxf (9b27de51-…) not filed (escalate): missing a person to say whether 9b27de51-… (880 bytes, score 3) is a copy of b45cecdd-… (61,208 bytes); all are named J-KNOB-09_RevA.dxf and would sit in Jig & Fixture Drawings.` (22 Sept: 6 planned moves, one of them the duplicate PO.) | ① A misleading description on the W-9: task TI6 says `W9_JMillerWelding_2026.pdf (…) not filed (conflict): missing agreeing evidence (the signals point to HR, Purchasing).` ② Weak or no clues: task G1 refuses `DSC_0045.jpg` (no clues) and escalates `notes_final_v2.docx` (a description alone never files). |
| **T2.6** Plan → apply 🟡 | `python -m agent --target fake ask "Tidy the incoming folder."`, then the same with `--apply` | Plan-only: `(plan only - nothing was changed)` and `writes 0`. Apply: `(applied)` and `writes 19` (5 file updates, 1 session, 13 escalations; 22 Sept: `writes 11`). With the live cap (TI2L, or S13 with `live_allowlist=True`): 10 writes (5 file updates, 1 session, 4 escalations), and the 9 copies are listed as `left for a person: not in this run's scope`. TI2's and TI2L's `writes_in_allowlist` checks pass. There is no separate plan file: plan and apply happen in one run, and the plan is kept as `plan_*` decision records. | "Row moved" between plan and write: task TI4 reports the W-9 as `SKIPPED … not overwritten`. |
| **T2.7** Duplicates ✅ | `python -m agent --target fake ask "Find duplicate files."`, then `python -m agent --business suryodaya --target fake ask "Find duplicate files."` | Keystone (26 Sept data): both PO "(1)" files as `… per name + size (suspected); not byte-verified because no file bytes are stored.`, then `14 content hash value(s) are shared by unrelated files, so they were not trusted.` (the full answer is in [find_duplicates](architecture.md#find_duplicates)). On 22 Sept: `PO_4471_ApexMetals_signed (1).pdf (82f83d94-…) duplicates PO_4471_ApexMetals_signed.pdf (732439a0-…), per recorded hash + size + name; …`. Suryodaya: `1 content hash value(s) are shared by unrelated files, so they were not trusted.` and no duplicate claim at all. | Search the answer for "byte-verified": it may only appear as "not byte-verified", and "byte-for-byte" must not appear. Task DU1 checks the first. |
| **T2.8** Provenance ✅ | S13 (a tidy on the fake server), first two lines | The timesheet's description is the **original text** plus one appended line: `[Files Agent <today>] Moved Incoming -> HR. Evidence: description, filename_pattern, sender. Score: 4 (threshold 3).` | Tidy twice: task TI3's second pass makes 0 writes, so no second note. |
| **T2.9** Snapshot / restore 🟡 | S13, last two lines: snapshot, tidy, restore | `rows changed by the tidy: 5`, then `restored: 5 ; diff after restore: {}` (22 Sept: 6). All 8 writable fields match the snapshot again. A live write run saves `runs/<set>/<task>/snapshot-N.json` and `writes-N.json` beside the run file. | ① "Another team" changes a field after our write (S14): restore leaves it and lists it under `conflicts_left_alone`. ② Restore refusals (safe only while `AS_ALLOW_WRITES` is **not** set). First make a snapshot file offline: `python -c "from pathlib import Path; from agent.runtime import build; from agent import snapshot; rt = build('keystone', 'fake', 'plan', None); snapshot.save(snapshot.take(rt.admin_mcp, rt.guard.allowlist), Path('runs/scratch/snapshot-1.json'))"`. Then `python -m harness restore runs/scratch/snapshot-1.json --target live` says `refused: restoring on the live platform writes; it needs --live-apply and AS_ALLOW_WRITES=1`; with `--live-apply` but no `AS_ALLOW_WRITES=1` it notes that there is no write journal, then says `refused: Live writes need AS_ALLOW_WRITES=1 …`. ③ A crash halfway through a live apply: the restore still runs (the nested `finally` in `harness/runner.py`). Only a live write run takes this path, so check it by reading the code. |
| **T2.10** Escalation 🟡 (live check pending) | `python -m harness run R4 --target fake --repeat 1 --set check`; S13 lists the escalations of a full tidy | R4 passes: exactly **two** new escalations, one for each file named `Untitled.pdf` (22 Sept: one). S13: one per unfiled file (13 offline; 4 with the live cap, all originals), subject `[files-agent] <file id> <filename>`, `reason_code` `other`, and `party_id` set only for the files that have a sender (the original IMG photo and the original PO "(1)"). | Run it again: task TI3's second pass creates no escalation (`last_pass_escalations = 0`). On the first live run only: check 7.2 "Your escalations" (0 before any live run). |
| **T2.11** Boundary, leak guard, contradiction ✅ | `python -m agent --target fake ask "<question>"` for `Show me this month's payslips.`, `List all the files in the Drive.` and `How many files are in the Drive?` | Payslips: `I can't help with that: it needs the payroll app, and this seat (Files Agent) only has agent, crm, drive.`, with `'mcp_calls': 0` in the status line, so no payroll tool was called. List: `30 files are visible to this seat` and `83 further rows were withheld … (EsignDocument: 83).` Count: `The record list holds 113 files; 30 of them are in Drive folders …`, and the Drive screen and overview report `15`. (22 Sept: 15 visible; 98 files, 15 in folders, Drive `0`.) | The fixture's e-sign titles are already placeholders, so plant a real-looking one: task C3 adds "Employee Offer Letter - Canary Zebra" and passes: the title is in no answer and in no agent event (the run file holds it only in the manifest's copy of the task); 84 withheld. S15 shows the same kind of row with and without the guard. |

**S9: a decision record survives a round trip**
```python
import json
from agent.records import DecisionRecord, Evidence
rec = DecisionRecord(skill="find_drawing", action="current_drawing", status="info",
                     target_id="2683b2c8-f700-4870-981c-1fb9c8d53393", evidence=(Evidence("folder", "Jig & Fixture Drawings"),))
print("same after a round trip:", DecisionRecord.from_dict(json.loads(json.dumps(rec.to_dict()))) == rec)
DecisionRecord(skill="find_drawing", action="", status="info")     # a required field left out
```
Output: `same after a round trip: True`, then a traceback ending `ValueError: skill and action are required`.

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

**S12: the revision parser on real and made-up names**
```bash
python -c "from harness.fixtures import load; from agent.skills.revisions import parse_revision as p; rows = [(b, f['filename']) for b in ('keystone', 'suryodaya') for f in load(b)['tables']['FileAttachment'] if f.get('folder_id')]; print(len(rows), 'names parsed'); [print(b, n, '->', r.raw, r.scheme, r.flags) for b, n in rows if (r := p(n))]"
python -c "from agent.skills.revisions import parse_revision as p; print(p('X-Rev10.pdf').ordinal > p('X-Rev2.pdf').ordinal, p('X_RevAA.pdf').ordinal > p('X_RevZ.pdf').ordinal, p('X_RevB_RevC.pdf').flags, p('X_RevO.pdf').flags)"
```
Output (26 Sept Keystone fixture: each drawing name appears twice, once for the original and once for its 23 Sept copy):
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
Output (27 Sept, 26 Sept fixture; the date is the day you run it). Offline the allow-list is all 18 Incoming files, so all 13 unfiled files are escalated:
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

**S13 with the live cap** (a rehearsal of the live run, as TI2L does): change the `build` line to `rt = build("keystone", "fake", "apply", None, transport=server, live_allowlist=True)`. Output (27 Sept):
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
Only the 4 unfiled originals are escalated; the 9 copies get no escalation and no write.

**S14: restore leaves another team's change alone**
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
Output: `{'1ee27946-7064-42e1-afce-376068a545bf': {'folder_id': {'snapshot': '6f8a3ed1-f2df-46a7-8dcb-275e9494c799', 'now': '585da032-09fe-43cd-9440-c6f01824f5fc', 'updated_by': 'another-team'}}}`. The timesheet's description (our field) is still put back.

**S15: one e-sign row, with and without the leak guard**
```python
from harness.fake_server import FakeServer
from agent.runtime import build
from agent.privacy import sanitise_file
server = FakeServer.from_fixture("keystone", None, extra_files=[{"filename": "Offer Letter - Canary.pdf", "entity_type": "EsignDocument", "folder": ""}])
rt = build("keystone", "fake", "plan", None, transport=server)
row = next(f for f in server.tables["FileAttachment"].values() if "Canary" in f["filename"])
print("stored:", row["filename"], "; what skills, the model and traces get:", sanitise_file(row, rt.catalog.can_list)["filename"])
```
Output: `stored: Offer Letter - Canary.pdf ; what skills, the model and traces get: EsignDocument-attachment-af1fc223.pdf`. The guard decides from the tool list: this seat has no `EsignDocument.list`, so the row is outside the seat.

#### Phase 3: Agent loop

| Task | Run it | You should see | Break it on purpose |
|---|---|---|---|
| **T3.0** The loop ✅ | `python -m agent --target fake ask "How many files are in the Drive?"`, then open the trace | `model_turn` events, the skill's `mcp_call` events, then `answer`. The scripted model only calls skills. To see the model make its own direct reads (tools named like `mcp__FileAttachment__list`), use `--model anthropic`. | ① An error inside an HTTP-200 reply: task D4. The error goes back to the model as a tool error (`Tool error (agent_error): Injected failure (fake server)`) and is never read as "no such part". ② The turn cap: `AS_MAX_TURNS=1 python -m agent --target fake ask "Find the drawing for part J-BRKT-04."` gives `No answer (turn limit reached).`, a status line ending `ABORTED max_turns`, and exit code 2. |
| **T3.1** Router ✅ (questions 👤) | `python -m harness routes` | `10 of 10 routed as expected.` This is the scripted model, whose router was written for these questions, so it says nothing about the real model. Real model: `python -m harness routes --model anthropic`. | A question outside the seat: `python -m agent --target fake ask "What is the weather in Paris?"` answers `I can't map that request to anything this Files seat can do.` |
| **T3.2** Answer writer 🟡 | `python -m harness run D1 --target fake --repeat 1 --set check` | D1 passes, including `cited_ids_resolve`: every id in the answer exists on the platform. `ask` also prints `[warning: ids in the answer not seen in any tool result: …]` when an id wasn't seen. The answer is the model's own text plus a *Record trail*; it is not built only from records. | Plant an invented id (S16): it is listed as unverified. `harness calibrate` plants one too (`invented_id`) and it is caught on `cited_ids_resolve`. Removing a record does **not** remove a fact from the answer, because the model writes free text. Filenames and part codes in the answer are not checked automatically. |
| **T3.3** Command line ✅ | `python -m agent --target fake ask "Tidy the incoming folder."` | Plan-only by default: `(plan only - nothing was changed)` and `writes 0`. | First make sure `AS_ALLOW_WRITES` is **not** set in your shell. ① `python -m agent ask "Tidy the incoming folder." --apply` says ``refused: `ask --apply` writes only on the fake server. Live writes go through `python -m harness run TI2L --target live --live-apply` …`` and exits 3. ② `python -m harness run TI2L --target live --live-apply` says `TI2L: SKIPPED - Live writes need AS_ALLOW_WRITES=1 set in the shell for this one command (the .env file is ignored for it) as well as --live-apply.` Without `--live-apply`: `TI2L: SKIPPED - TI2L writes; on the live platform it needs --live-apply and AS_ALLOW_WRITES=1`. Any other write task, even with both switches: `TI2: SKIPPED - TI2 is not marked live_write = true, so it never writes on the live platform (only TI2L is: …)` (the same for TI3 and R4). These refusals happen before any connection; on 27 Sept they were checked offline by calling `planned_runs` in `harness/runner.py` directly. ③ Keystone only (S17): `WritesNotAllowed: Live writes are only allowed on keystone.` `harness run` takes the business from the task file, so `--business` doesn't change it. |
| **T3.4** Budget guard ✅ | Any `ask`: read the status line, or `ledger` in a run file's `result` | For D1 with the scripted model: `cost {'turns': 2, 'mcp_calls': 3, 'input_tokens': 0, 'output_tokens': 0, 'usd': 0.0}` (the scripted model uses no tokens). With `--model anthropic`, compare tokens and $ with your provider's usage page; prices come from `AS_PRICE_IN_PER_MTOK` and `AS_PRICE_OUT_PER_MTOK`. The score report has a cost column. | ① `AS_MAX_TURNS=1` gives `ABORTED max_turns` (T3.0). ② `AS_MAX_MCP_CALLS=2 python -m agent --target fake ask "Find the drawing for part J-BRKT-04."` gives `Stopped: MCP call cap reached (2).`, a status line ending `ABORTED budget`, and exit code 2. ③ `AS_MAX_USD` can only trip with the real model. Defaults: 12 turns, 80 MCP calls, $0.50 per question. |
| **T3.5** Goal recording ⛔ | Waits on staff Q5. | 7.2 block C changes as expected, or the README explains why not. On 22 Sept 2026 both goals were `False`, jobs 0. | — |

**S16: an id the agent never saw**
```bash
python -c "from agent.answer import compose; print(compose('The drawing is 12345678-aaaa-bbbb-cccc-1234567890ab.', [], set())['unverified_ids'])"
```
Output: `['12345678-aaaa-bbbb-cccc-1234567890ab']`

**S17: live writes are Keystone-only**
```bash
python -c "from agent.runtime import check_write_permission; from agent.config import get_settings; check_write_permission('live', 'apply', get_settings('suryodaya', env={'AS_ALLOW_WRITES': '1'}))"
```
Last line: `agent.runtime.WritesNotAllowed: Live writes are only allowed on keystone.` (Nothing is sent: the check runs before any connection.)

#### Phase 4: Harness

| Task | Run it | You should see | Break it on purpose |
|---|---|---|---|
| **T4.1** Task files ✅ (expectations 👤) | `python -m harness list` | 22 tasks load: C1–C3, D1–D4, DU1, G1, R1–R5, TI1–TI7, TI2L. Each has an `[expect]` table. Two `extra_files` with the same id (for example two with one filename and no `id`) are refused when the task loads, naming both files. | ① A typo in an expectation key is an error, not a check that silently switches off (S18). ② A teammate works out 2–3 expectations from live data (7.2) on their own: they must match yours. |
| **T4.2** Runner ✅ | `python -m harness run D1 --target fake --set check5` (5 repeats by default) | `runs/check5/D1/1.jsonl` to `5.jsonl`, plus `expected.json` (`{"D1": 5}`), `score.json` and `report.md`. | Crash the scorer (S8): the run files are still there. |
| **T4.3** Verifiers ✅ (checks 👤) | `python -m harness score runs/check` | Every task PASS. | ① A file ends in the wrong folder on the fake server (S19): `final_folder:81857de6: expected cbb1441f-…, found 13c03c65-…`. ② `python -m harness calibrate runs/check` has 31 kinds of mistake and plants the 30 that apply today (no task expects an archive, so `unarchived` has nothing to plant): `377 of 377 injected faults caught.` (4 Oct, with TI7; 3 Oct, after the STRIDE fixes: `355 of 355`; 27 Sept: `295 of 295` with 26 kinds; 22 Sept: `265 of 265` on 19 tasks). |
| **T4.4** Claims vs state ✅ (👤) | Any apply task, e.g. TI2 | `claims_vs_state` passes. | ① A claimed move that never happened: calibration's `liar` mistake is caught on `claims_vs_state`. ② A change by "another team": in TI4 and TI5 the check still passes and notes it (S20). |
| **T4.5** Fault injection ✅ | `python -m harness run D4 --target fake --repeat 1 --set check` | D4 passes. | D4 turns on `http401_once` (one re-login, then it carries on) and `error_in_200:Item.list` (handled and reported). The full list of faults is in the docstring of `harness/fake_server.py`. |
| **T4.6** Scoring ✅ | Make a set where one task passes 4 of 5: run D1 ×5 (T4.2), delete `runs/check5/D1/3.jsonl`, then `python -m harness score runs/check5` | D1 shows 5 runs, 4 passed, `FAIL`, with `- D1/3.jsonl: missing: no run file was written (the run crashed)`. The cost column and the total are the sums of each run's `usd` (all 0 with the scripted model). | — |
| **T4.7** Manifest ✅ | S21 reads the first line of a run file. | `git` (the commit and whether the tree was dirty; `no-commit` before the first commit), `model`, `tool_hash` `c10a009a80de46c6`, `fixture` (folder `…\2026-09-26` and hash `df2a585221ef9f25`; `8bf8e438f43d618a` before the 2 Oct scrub), `business`, `user_id`, `started_at`, and the allow-list: 18 ids offline (all of Incoming), 9 for TI2L and on live. (22 Sept: `cc08bae6517ed3cb`, `f128c97d66753c72`, 9 ids.) | Change the fake server's tool list (S4): the hash becomes `97c1058771f8a313` (22 Sept fixture: `aed5ef44441abbea`). |
| **T4.8** Rescore ✅ | `python -m harness rescore runs/check` | `rescore IDENTICAL to score.json` | ① Change a number in `score.json` by hand: `rescore DIFFERS from score.json`, exit 1. ② Rebuild from nothing: copy `score.json` and `report.md` aside, delete them, run `python -m harness score runs/check`, and compare: the files are identical. (Don't run `rescore` after deleting `score.json`: it has nothing to compare with, so it says `DIFFERS`.) |
| **T4.9** Pre-flight ✅ | Live: `python -m harness preflight`. Offline: S22. | Live (27 Sept): `pre-flight OK`, then `warnings (not blocking):` with 9 lines, one per 23 Sept copy, e.g. `W9_JMillerWelding_2026.pdf (20d633ba-…) is in Incoming but outside the write allow-list: it will not be written or escalated`. (The pre-27 Sept check failed live with 10 problems.) Offline: `unchanged: [] ; 9 warnings, …`. | S22 changes an Incoming row's `updated_at` and removes a required tool: all four problems are listed (a removed tool changes the tool hash and the tools' text hash). It also adds an unknown file to Incoming (a problem, not a warning) and a new file in Quality named like the mill-cert original (a problem: it would hold the original back under the same-name rule). In a live write run any problem stops the run with `Pre-flight failed; nothing was written`, before the snapshot and before any write; warnings are printed and traced, and the run goes on. |

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
Output: `['final_folder:81857de6: expected cbb1441f-5a73-4989-846b-775f6a1e9e70, found 13c03c65-ddae-4d61-9e2f-b9167168277f']`. Only that check fails: the other team's move is a foreign change, not ours.

**S20: foreign changes are logged, not failed**
```bash
python -c "from pathlib import Path; from harness.verifiers import load_run, verify; print([c.detail for c in verify(load_run(Path('runs/check/TI4/1.jsonl'))) if c.name == 'claims_vs_state'])"
```
Output: `[" (foreign changes ignored: ['81857de6'])"]`

**S21: the run manifest**
```bash
python -c "import json; m = json.loads(open('runs/check/D1/1.jsonl', encoding='utf-8').readline()); print({k: m[k] for k in ('git', 'model', 'tool_hash', 'fixture', 'business', 'user_id', 'started_at')}, len(m['allowlist']), 'allow-listed ids')"
```
Output (27 Sept, on the PR #3 branch with uncommitted changes; your commit, folder and time will differ): `{'git': {'commit': 'd17b7630371fc7de956d2aace2caba5a048ea56b', 'dirty': True}, 'model': 'scripted', 'tool_hash': 'c10a009a80de46c6', 'fixture': {'dir': '…\\harness\\fixtures\\keystone\\2026-09-26', 'hash': '8bf8e438f43d618a'}, 'business': 'keystone', 'user_id': '2b5bbcef-ce22-44dc-a49c-5e2f7a165b9f', 'started_at': '…'} 18 allow-listed ids`. On 22 Sept (before the first commit and the data change) it said `'commit': 'no-commit'`, `cc08bae6517ed3cb`, `f128c97d66753c72` and 9 ids.

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
The 9 copies are known to the fixture and unchanged, so they are only warnings; the made-up `new_upload.pdf` is unknown, so it is a problem. A new file outside Incoming matters only if it is related to one of the 9: it shares a name or recorded hash (the made-up mill cert in Quality), or it is the same kind of document (the made-up mill cert in Purchasing: three of those are enough to turn the real mill cert's move to Quality into a conflict, because the similar-file signal counts every mill cert in the drive). Drawings count as the same kind when they share a code prefix. A folder that is new, gone, renamed, moved or archived is a problem too (`folder 'Quality' (585da032-…) was renamed, moved or archived since the fixture (now 'QA')`), and so is any other update to a folder, or two folders with one name. `preflight.check` returns only the problems; `preflight.assess` returns problems and warnings. (The "same kind" and folder checks were added on 2 Oct 2026; before that, pre-flight passed while three new mill certs in Purchasing changed the plan.)

---

### 7.4 Are your own tests any good? (Phase 5)

This guide gives you no test cases: those must be yours (T5.1–T5.10). [`tests/README.md`](../tests/README.md) lists what each test should cover, the module under test, and building blocks you can use (`FakeServer.from_fixture`, `agent.runtime.build`, the faults, the leak-guard canary, `snapshot.plan_restore`). But you can check whether a test does its job:

**1. Break the code, and the test must fail.** For each test, sabotage the thing it checks for a moment, run the test, and check that it goes red. Then undo the change. If it stays green, the test is too weak.

| Your test | Sabotage to try | Where |
|---|---|---|
| T5.1 parser | Sort revisions as plain text, so "Rev10" comes before "Rev2" | `agent/skills/revisions.py` |
| T5.2 scoring | Let a description alone decide the folder | `agent/skills/triage.py` (`_score`) |
| T5.3 duplicates | Trust a hash that's shared by many files | `agent/skills/duplicates.py` (`untrustworthy_hashes`) |
| T5.4 guards | Allow every id | `agent/guards.py` (`update_file`) |
| T5.5 client | Treat HTTP 200 as success without checking for an error inside | `agent/mcp_client.py` (`_rpc`) |
| T5.6 safe reads | Send `ne:` to the server | `agent/safe_reads.py` (`list_all`, `not_equal`) |
| T5.7 verifiers | Make a verifier always return "pass" | `harness/verifiers.py` |
| T5.8 idempotency | Skip the "already escalated?" check | `agent/skills/escalate.py` (`escalate`) |
| T5.9 redaction | Turn redaction off (S5 shows the effect) | `agent/redact.py` |
| T5.10 budget | Remove the cap | `agent/budget.py`, `agent/loop.py` |

Two things to know while you write them:
- **T5.6:** the fake server does not copy the `ne:` trap (it returns 0 rows for `entity_type=ne:Item`; the live platform returns 98 since 23 Sept, and returned 83 on 22 Sept). So test what `list_all` *sends*, or give it your own small stand-in that behaves like the platform.
- **T5.10:** the turn cap aborts with `max_turns`; the MCP-call and $ caps abort with `budget`. A write is never started without budget for its read, write and confirming read (`Budget.reserve(3)`).

**2. Offline, fast and repeatable.** Tests must not call the live platform or the model. Use the saved fixtures. The same input must always give the same result. Watch out for values that change on every run: the date in provenance notes, and the random ids of new sessions and escalations.

**3. One behaviour per test**, named after that behaviour.

**4. Show it's your work.** Write and commit the tests yourselves. The commit history is your evidence that they weren't AI-written. (On 22 Sept 2026 nothing was committed yet; PR #1 was merged later that day. On 2 Oct PR #4 added the first 78 hand-written tests, and on 3 Oct PR #5 added 79 more.)

Run them with the standard library: `python -m unittest discover -s tests`. Whether `pytest` is allowed is staff question Q3. `python -m harness calibrate` checks the harness's own verifiers, but it was written with AI help, so it doesn't count as your tests. If you want harness checks to count, write your own versions in `tests/`.

---

### 7.5 Gates before moving on

Tick these before moving to the next phase.

| Gate | Tick when | State on 22 Sept 2026 (27 Sept where marked) |
|---|---|---|
| **M1** (end of Phase 1) | Logs into both businesses (`python -m agent whoami`, with and without `--business suryodaya`) · MCP errors raise (S3, D4) · traces are redacted (block D says `no secrets found`) · fixtures captured · the fake server matches live (`smoke` side by side) · a run file survives a scoring crash (S8) | ✅ built; fixtures for both businesses were captured on 22 Sept 2026, and Keystone again on 26 Sept (the Suryodaya fixture is now stale). Phase 0 is still open: staff answers (T0.1). The history secret scan (T0.2) was done on 2 Oct and found nothing. |
| **M2** | `python -m harness run D1 D2 D3 D4 --target fake` passes, and `ask` for `J-BRKT-99` says `No part has the exact code J-BRKT-99. I did not guess.` | ✅ offline |
| **M3** (end of Phase 2) | TI1 makes 0 writes · TI2 and TI2L write only allow-listed ids · TI2L neither writes nor escalates any of the 9 copies · restore gives an empty diff (S13) · TI4 skips the moved row · TI5 reports FAILED · TI6 flags the conflict · TI3 makes no second escalation | ✅ offline (27 Sept) · 🟡 restore has not run live yet |
| **M4** (end of Phase 3) | R1–R5 pass · `AS_MAX_TURNS=1` gives `ABORTED max_turns` and `AS_MAX_MCP_CALLS=2` gives `ABORTED budget` · `ask --apply` is refused on live · `harness run TI2L --target live --live-apply` is refused without `AS_ALLOW_WRITES=1`, and every other write task is refused on live | ✅ with the scripted model (27 Sept) · real-model runs not done yet |
| **M5** (end of Phase 4) | `harness calibrate` catches every planted mistake · claims-vs-state catches a fake claim and ignores foreign changes (S20) · `harness rescore` says IDENTICAL · pre-flight reports drift (S22) and `python -m harness preflight` says `pre-flight OK` live | ✅ offline (295 of 295 caught on the 21-task set, 27 Sept; 265 of 265 on the 19 tasks of 22 Sept) · live pre-flight on 27 Sept: `pre-flight OK` with 9 warnings. Run it again yourselves right before the write run |

A quick offline pass over M2–M5: `python -m harness run all --target fake`, then `python -m harness rescore runs/<set>` and `python -m harness calibrate runs/<set>`.
