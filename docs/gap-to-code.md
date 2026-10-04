# From gap report to code

This file holds section 4 of the old README (before the split). The ids, code, numbers and dates are from the old README. [The docs index](README.md#corrections-after-the-split) lists the facts that changed.

---

## 4. From gap report to code

The one-page gap report is [`docs/gap_report.md`](gap_report.md). It answers 3 questions. The team updated it after Step 3, in PR #2 on 27 Sept 2026. The update added the later bugs, the 23 Sept data change and the hash gap. On 4 Oct, commit `9d6f962` changed 1 sentence for decision C. The git tag `step3-submitted` (commit `ea776d6`) holds the version that the team submitted for Step 3.

For each point in the gap report, this section shows:
- **what the agent does about it**
- **how the agent does it**
- **which files do it**
- **which task proves it**

The ids A1–A14 are the agent features ([4.6](#46-the-agents-features-a1a14)). The ids P1–P13 are the platform requests ([4.7](#47-platform-change-requests-p1p13)).

**Status key:**
- ✅ built
- 🟡 partly built (the rest is platform work or a known limit)
- 🛠 platform work (staff)
- 🐞 platform defect, reported as a bug
- ⛔ not built

### 4.1 At a glance

| Gap report item | Status | Files | Proved by |
|---|---|---|---|
| **Q1.1** Read file contents | 🛠 P1 · the agent refuses with evidence | `skills/access.py`, `skills/triage.py` | R3, R4, TI1, TI2, TI2L |
| **Q1.2** Enforce revision state | 🟡 the agent reads 3 signals and flags tag conflicts · P2 | `skills/find_drawing.py`, `skills/revisions.py` | D1, D3 |
| **Q1.3** Link part to drawing as data | 🟡 resolver A1 · P2 | `skills/find_drawing.py`, `safe_reads.py` | D1, D2 |
| **Q1.4** File by typed metadata | 🟡 the type comes from the filename. The agent does not store it · P7 | `skills/profiles.py`, `filing_rules.toml` | TI1, TI2, G1 |
| **Q1.5** Search completely | 🐞 F5, B2, B6, B22 / P9 · the agent reads all pages of the full list. It never sends `search` or date filters | `safe_reads.py`, `skills/overview.py` | C1, C2 |
| **Q1.6** Edit safely, with an undo trail | 🟡 guard + notes + restore · P6, P8, P3 | `guards.py`, `snapshot.py`, `skills/triage.py`, `harness/runner.py` | TI4, TI5, TI2, TI2L, TI3, R2, R5 |
| **Q1.7** Trust file hashes | 🐞 B4 / P10 · the agent does not trust shared hashes. It never writes to a possible copy, even on a trusted hash. It asks a person (decision C, A6) | `skills/duplicates.py`, `skills/triage.py` | DU1, TI2, TI2L, TI7 |
| **Q2** Part → drawing resolver | ✅ A1 (A5 in part: there is no drive-wide revision report) | `skills/find_drawing.py`, `skills/revisions.py` | D1–D4 |
| **Q2** Evidence-scored Incoming triage | ✅ A3, A6, A7, A9, A14 (A2 in part: the document type comes only from the filename) | `skills/triage.py`, `profiles.py`, `duplicates.py`, `escalate.py`, `filing_rules.toml` | TI1–TI7, TI2L, G1, R4, DU1 |
| **Q2** Undo log and clobber check | ✅ checks + notes · 🟡 restore: built and checked offline (S13 in 7.3), but not run live yet · A8 | `guards.py`, `snapshot.py`, `harness/runner.py`, `harness/preflight.py` | TI4, TI5 |
| **Q2** Scheduled triage via `AgentTask` | ⛔ not in this build (A13) | — | — |
| **Q2** Call the MCP tools safely | ✅ the skills send only exact, comma-free filters. They never send date filters, `search` or advertised defaults. The agent finds tools by exact name (T1.5) | `safe_reads.py`, `catalog.py`, `config.py` | C1, C2, O4 in 7.2 |
| **Q2 platform** Gate by the app that owns the data (Q1.7 in the Step 3 report) | 🐞 F1, F2, B20, B21 / P5 · leak guard A11 | `privacy.py` (+ the places that use it) | C2, C3 |
| **Q2 platform** Merge the 23 Sept repair copies back | 🐞 B18 / P12 · pre-flight, scope and same-name rules | `harness/preflight.py`, `skills/triage.py` | TI2, TI2L |
| **Q3.1** Cross-check surfaces. Do not trust one surface alone | ✅ A12 | `skills/overview.py` | C1 |
| **Q3.2** Refuse with evidence | ✅ A3, A9, A10 | `skills/triage.py`, `skills/escalate.py`, `skills/access.py` | R1–R5, TI1–TI3, TI2L |
| **Q3.3** Catch a write that lands on ours | ✅ detect (not prevent) | `guards.py`, `skills/triage.py` | TI5 (after the agent's write), TI4 (before it) |

### 4.2 What the agent builds (Q2 "ours to build")

#### A. Part → drawing resolver (gaps 2–3) ✅
- **Why:**
  - On 22 Sept, a search for any text that contains `BRKT-04` returned 3 drawings. One of them belongs to a different part (`KJ-BRKT-04`).
  - Since 23 Sept, the search returns 6 rows: the 3 drawings and a bare copy of each.
  - `Item.design_file_id` is empty on all 28 parts.
  - The platform's own built-in agent used a filename search instead.
- **What:** the `find_drawing` skill.
- **How:**
  - The skill finds the part with an exact `Item.code` match. Then it reads the files that link to the part by `entity_id`.
  - It examines each drawing for the archived flag, the folder and the tags. Any one of these signals can mark the drawing as superseded.
  - It reports tag conflicts and unusual revision names.
  - It names a current drawing only when exactly 1 drawing does not count as superseded and nothing conflicts.
  - It reads the revision from the filename.
  - It names look-alike codes as different parts.
  - See [`find_drawing`](architecture.md#find_drawing-part--current-drawing).
- **Files:** `agent/skills/find_drawing.py`, `agent/skills/revisions.py`, `agent/safe_reads.py`, `agent/privacy.py`.
- **Proved by:**
  - D1: RevC is current, RevB is a superseded revision, and the agent flags KJ.
  - D2: KJ-BRKT-04 never cites the J drawings.
  - D3: revision B is a superseded revision.
  - D4: the agent never reads a platform error as "no such part".

#### B. Evidence-scored Incoming triage (gap 4) ✅
- **Why:** the platform has no document-type field. The only signals are the filename, the sender, links and a free-text description. Anyone can edit the description.
- **What:** the `triage_folder` skill, plus `find_duplicates`.
- **How:**
  - The skill scores independent signals. The weights are in a rules file that the team owns.
  - A description counts only when another signal agrees. The skill escalates a conflict.
  - The skill never moves or archives a possible copy. A possible copy is a duplicate match, trusted or not. 1 escalation asks a person to compare it with the other file (decision C, [triage step 3](architecture.md#triage_folder-evidence-scored-filing)).
  - The skill never moves 2 files with the same name into 1 folder. It escalates the file with the lower score as a possible copy. On a tie, it escalates both (same-name rule, 27 Sept).
  - The skill does not write or escalate a file outside the write allow-list of the run (scope rule, 27 Sept).
  - The skill escalates all other files that have no justification. The escalation names the evidence that is not there. If the records name a person, the escalation also names who to ask.
  - See [triage_folder](architecture.md#triage_folder-evidence-scored-filing) and [How the agent scores a file](architecture.md#how-a-file-is-scored).
- **Files:** `agent/skills/triage.py`, `profiles.py`, `duplicates.py`, `escalate.py`, `agent/filing_rules.toml`, `agent/guards.py`.
- **Proved by:**
  - TI1: the plan.
  - TI2: offline, with all 18 Incoming files. The agent moves 5, escalates 13 and archives nothing.
  - TI2L: a rehearsal of the live write run on the 9 originals. The agent moves 5, escalates 4 and does not change the 9 copies.
  - TI3: a re-run does nothing new.
  - TI6: a description that misleads cannot move a file.
  - TI7: trusted duplicate pairs. Every copy stays in place and has 1 escalation.
  - G1: unseen names.
  - R4: the agent refuses both `Untitled.pdf` files and escalates them.
  - DU1: duplicates.

  The gap report gives these figures: 5 of 9 filed, the duplicate archived, 3 escalated. They describe the 22 Sept data and the rule before decision C.

#### C. Undo log and clobber check (gap 6) ✅ checks · 🟡 restore not yet run live
- **Why:** the platform has no ETag or `If-Match`. Thus the last write wins, without a warning. There is no delete, and the server does not write a move history.
- **What:**
  - Before every write, the agent re-reads the row. It skips a row that changed.
  - After every write, the agent re-reads the row. It reports a change of the agent that is no longer there.
  - The agent appends a dated note to the file.
  - On live runs, the agent makes a snapshot. It saves every write when it sends it. After the run, it restores the old values of **only the fields that this seat changed**.
- **How:** see [The life of one write](architecture.md#13-the-life-of-one-write) and [Safety](safety.md#8-safety-on-the-shared-platform).
- **Files:** `agent/guards.py`, `agent/snapshot.py`, `agent/skills/triage.py`, `harness/runner.py`, `harness/preflight.py`, `harness/__main__.py`.
- **Proved by:**
  - TI4: if a row changes before the agent's write, the agent skips the row (SKIPPED).
  - TI5: if a change overwrites the agent's change right after the agent's write, the agent reports FAILED.

  Restore itself runs only in a live write run. A person can also run `harness restore` by hand.

#### D. Scheduled triage via `AgentTask` ⛔
The team did not build this feature. To create a task, the agent must write outside its 3 allowed write tools. The Step 4 plan (A13) moved the feature out of Step 4. An `AgentTask` would run the **platform's built-in agent**, not this agent. The team proposed it as platform work (P7, Automations access). The same triage runs on demand (plan-only): `python -m agent ask "Tidy the incoming folder."`

#### E. Calling the MCP tools safely ✅ (skills) · 🟡 (the model's own calls)
- **Why:** some traps in the list tools return 0 rows or wrong rows without an error (bugs B1, B2, B5, B6, L2, L5). The traps are:
  - advertised filter defaults
  - `%` and `_` in `search`
  - date-only filters, which the platform compares as text
  - comparison values that the platform cannot parse
  - `ne:`, which drops empty values
  - commas, which become OR lists
- **What:** every skill reads through `list_all` in `agent/safe_reads.py`.
- **How:**
  - The skills send only exact, comma-free filters to the server, and only on a short list of id-like fields. They also send `limit` and `offset`.
  - The code of the agent applies all other filters and does all the sorts.
  - The skills never send `search`, date filters, `ne:`/`gt:`/`lt:` values or the advertised defaults of a tool.
  - The agent finds tools by exact name from `tools/list`. It never uses `tools.search` (bug B16).
- **Files:** `agent/safe_reads.py`, `agent/catalog.py`, `agent/config.py`.
- **Proved by:** C1 and C2 (they read all pages), O4 in [7.2](checking.md#72-ground-truth-ask-the-platform-directly) (the not-Item count).
- **Limit:** the model can call some read tools directly (Appendix B). The agent sends the filter values of the direct calls of the model unchanged. For 4 list tools, it refuses a filter name outside `MODEL_FILTERS` (`agent/loop.py`).

### 4.3 The seven gaps (Q1): what the benchmarks do, and our answer

| # | Benchmarks do | AgentSwitch today | What our agent does | Still needs the platform |
|---|---|---|---|---|
| 1 | Box extracts fields with OCR | The platform stores no bytes. Suryodaya downloads give `409`. Keystone's original rows have 0 revisions, and the 23 Sept copies have 1 each | `file_contents` refuses to quote. Triage refuses files with no signals and escalates them | **P1:** give Drive the email app's `extracted_text`, or store bytes |
| 2 | Onshape blocks obsolete revisions. Vault has Released/Obsolete states | "Superseded" is only tags, `is_archived` and a description. All of them are editable | `find_drawing` treats a drawing as superseded if any one of 3 signals says so: archived, the Superseded folder, or the `superseded` tag. It flags tag conflicts. It names a current drawing only when exactly 1 drawing does not count as superseded and nothing conflicts | **P2:** connect Drive to the release flow of design review |
| 3 | Onshape tracks revisions per part number | `Item.design_file_id` is empty. Files link through the untyped `entity_id` | An exact-code resolver. It flags look-alikes | **P2** |
| 4 | SharePoint has autofill. M-Files files by metadata | There are no fields for document type, expiry or tax year | The agent takes the document type from the filename (5 types in `filing_rules.toml`). It uses the type only to choose a folder. It never stores the type | **P7:** custom fields + Automations |
| 5 | Search returns everything, or says that it cut the results | `/api/search` stops at 5 per type and ignores `limit`/`offset` (bugs **F5**, **B22**). `search=` treats `%` and `_` as wildcards (**B2**). Date-only filters compare as text (**B6**) | The agent never uses `/api/search` or `search=`. It never sends date filters. It reads all pages of the full list and filters in code | **P9** |
| 6 | Box `If-Match`/412, Vault check-out, Drive Activity log | The last write wins. There is no delete. The browser writes the access log (bug L8). The 23 Sept repair gave its events new dates (**B19**). The platform records API agent sessions as anonymous (**B7**) | A write guard, appended notes, and snapshot/journal/restore on live runs | **P6** guard, **P8** history, **P3** trash/restore |
| 7 | A content hash identifies the bytes of the file. Thus 2 files with the same hash are duplicates | The hash is client-writable. All 21 Suryodaya files have 1 hash. Keystone has a mix of 16- and 64-character hashes. Since 23 Sept, 14 hash values each belong to an original and its copy (bug **B4**) | `find_duplicates` does not trust a hash on files with different names or sizes. It never says "byte-verified". Triage never writes to a possible copy, even on a trusted hash. It escalates the copy, so that a person can compare the files (decision C) | **P10:** server-side hashes |

The Step 3 report had a seventh gap: the seat can see data of other apps. This data was 83 e-sign titles and 92 notices (bugs **F1**, **F2**, submitted again as **B20**, **B21**). The updated report puts this gap under platform work. See the P5 row in [4.4](#44-platform-work-we-asked-for-q2-platform-work). The answer of the agent did not change. It uses the leak guard, and it never reads `Notification` or `/api/search`.

### 4.4 Platform work we asked for (Q2 "platform work")

These are the 8 requests in the one-page report. The plan has the full list of 13 requests (P1–P13). [4.7](#47-platform-change-requests-p1p13) gives this list and how to build each request.

| Request in the report | Plan id | What the agent does until then |
|---|---|---|
| Store bytes, or pass the email app's `extracted_text` into Drive | P1 | The agent refuses and escalates. Note: `scan0042.pdf` and `Untitled.pdf` did **not** come by email. Thus only stored bytes or OCR can help with those 2 files. |
| Connect Drive to the release flow of design review | P2 | The agent infers "current" from 3 editable signals. It reports conflicts. |
| Trash/restore for rows without revisions (not delete) | P3 | The agent refuses delete. It never archives a possible copy. It escalates the copy, so that a person can move it to a folder, keep both, or have 1 removed (decision C). On 4 Oct 2026, this applies to both PO "(1)" files. On live, it applies only to the original "(1)", 82f83d94. |
| An `expect_updated_at` guard on file updates | P6 | The agent **does the same check on the client side**. Before every write, it re-reads the row and compares `updated_at`. It cannot close the gap between that read and the write. |
| Gate `FileAttachment`, `Notification` and search by the app that owns the data | P5 | The leak guard hides e-sign rows after they arrive. The board marks this as fixed (N179, N180). But on 25 Sept, the fix was not in effect (B20, B21). |
| Merge the 23 Sept Drive repair copies back into the originals | P12 | Pre-flight warns about the 9 Incoming copies. The live write run does not write or escalate them. The agent never moves 2 files with the same name into 1 folder (B18). |
| A document-type custom field, and Automations access | P7 | The agent keeps the filing rules as data in `agent/filing_rules.toml` (A14). |
| Make the `AgentTask` scheduler execute runs, time out stuck ones, and reject schedules that it cannot parse | P7 (schedules) | The agent does not use it. The team did not build scheduled triage (A13). Bugs: B11, B12. |

### 4.5 What our agent can do that theirs can't (Q3)

| Claim | How | Proof | Honest limit |
|---|---|---|---|
| **1. Cross-check surfaces. Do not trust one surface alone.** | `drive_overview` reads the overview and the record list. It reports both numbers and the reason. It says which number it used. Every skill reads files through the record API. | C1 (on 22 Sept: 0 against 15 in folders, and since 23 Sept: 15 against 30) | The agent does not query the Drive screen itself. The agent uses the overview endpoint in place of the screen. The report says "search still returns 5 of 32 file matches". This is a live measurement of 25 Sept. No task checks it. |
| **2. Refuse with evidence** | Refusal is a rule in code (the triage thresholds). Each refusal lists what is not there. If the records name a person, the refusal also says who to ask. In apply mode, each refused file in scope has exactly 1 escalation, even after re-runs. | R1–R5, TI1–TI3, TI2L | For R1–R3 and R5, the real model must choose the refusal skill. Only the scripted model routes by fixed rules. Escalations have no assignee (Keystone has no assignees). |
| **3. Catch a write that lands on ours** | The agent re-reads the row after every write. If the change of the agent is no longer there, the agent reports **FAILED**. It keeps the value that the other seat wrote. If a row changes before the agent's write, the agent skips it (**SKIPPED**). | TI5, TI4 | This is detection, not prevention. Without a server guard (P6), a change can land *between* the re-read and the write of the agent. The write of the agent then overwrites that change, and nobody sees it. |

### 4.6 The agent's features A1–A14

The plan listed 14 features that this agent adds to the platform. This table shows the built features, how they work, and which harness task proves each one. A check on 22 Sept 2026 compared each status with the code.

The 23 Sept data change and the 27 Sept rules changed some rows (A3, A4, A6, A8, A9, A12). A second check examined these rows on 27 Sept 2026. Decision C (4 Oct) changed the A6 and A9 rows. File paths are under `agent/`, unless they start with `harness/`.

Key:
- ✅ built
- 🟡 partly built
- ⛔ not built
- 👤 your job (you write it by hand)

| Id | Feature | Borrowed from | What was built | Done when (the plan's test) | Status | Files | Proved by |
|---|---|---|---|---|---|---|---|
| A1 | Part → drawing resolver | Onshape | `find_drawing` keeps the single part whose `code` matches exactly. Then it reads the files that link to that part by `entity_id`. It names a current drawing only if exactly 1 drawing does not count as superseded and nothing conflicts. It flags look-alike codes (`KJ-BRKT-04`) as different parts. | It returns the current drawing. It explains the superseded drawing and the look-alike. It cites record ids | ✅ | `skills/find_drawing.py`, `skills/revisions.py`, `safe_reads.py` | D1, D2, D3, D4 |
| A2 | Document profiles | Box, SharePoint | The document type (timesheet, W-9, PO, mill certificate, drawing) comes from the filename. The agent uses patterns in `filing_rules.toml` for this. It scores the sender, the part link and the description as separate signals. The plan record of each file lists them. | Every Incoming file has a profile, with the evidence behind each field | 🟡 the type comes only from the filename. There are no typed fields (expiry, tax year…). The agent stores nothing on the file | `skills/profiles.py`, `skills/triage.py`, `filing_rules.toml` | TI1, TI2, G1 |
| A3 | Evidence-scored triage with a refusal threshold | SharePoint, M-Files | `triage_folder` adds the scores of independent signals. It moves a file only if every signal that names a folder agrees and the score reaches 3. A description counts only when another signal agrees. If there are no signals, the agent refuses. Files that the agent moved itself do not count as similar-file evidence (PR #3).<br>**Same-name rule** (27 Sept): the agent never moves a file into a folder that already holds a file of the same name. The rule also applies to a folder that receives a file of the same name in the same run. The agent moves only the single file with the highest score. It moves none on a tie, or if the folder already holds that name. It escalates the others as possible copies, and names the other ids and sizes. | The behaviour matches the task expectations that **you** wrote | ✅ built · 👤 the weights, the threshold, the same-name rule and the task files are AI-drafted proposals (decision B confirmed). You review them and you own them | `skills/triage.py`, `skills/profiles.py`, `filing_rules.toml` | TI1, TI2, TI2L, TI3, TI6, G1, R4 |
| A4 | Plan → apply | SharePoint, Onshape | Plan-only is the default. In plan-only mode, triage records a plan (`plan_move`, `plan_refuse`, …) and writes nothing. In apply mode, the same run makes the plan first. Before each write, it re-reads the row. It skips the row if its folder, description or `updated_at` changed.<br>In both modes, triage records `out_of_scope` for a file outside the write allow-list of the run (27 Sept). It never writes or escalates that file. | A plan-only run makes 0 writes | 🟡 0 writes ✅. There is no separate plan file. Plan and apply happen in 1 run, and the agent keeps the plan as decision records. Offline, the plan covers all 18 Incoming files. On live (and in TI2L), the 9 copies are out of scope | `skills/triage.py`, `guards.py` | TI1 (0 writes), TI4 (changed row SKIPPED), TI2L (9 out of scope) |
| A5 | Families and supersession | Onshape, Vault | The agent reads revisions from filenames (A < … < Z < AA, Rev10 > Rev2). It flags unusual names. It never puts mixed letter and number schemes in order. A drawing counts as superseded if it has the archived flag, is in *Superseded*, or has the tag `superseded`. A family is the set of files that link to 1 part. | A request for a superseded revision names the revision that replaced it | 🟡 it works per part (D3 names RevC as current). There is no drive-wide revision report | `skills/revisions.py`, `skills/find_drawing.py` | D1, D3 · 👤 your revision-parser tests |
| A6 | Duplicates with a pointer | Egnyte | The agent matches copies on recorded hash + size + name. It does not trust a hash on files with different names or sizes. A name + size match is "suspected".<br>**Decision C (4 Oct):** triage never writes to a possible copy on either kind of match. It escalates the copy once. The escalation, not the file, holds a pointer to the other file: the id, the folder, and the folder to which this run moves it. The agent archives nothing (the rule: [triage step 3](architecture.md#triage_folder-evidence-scored-filing)).<br>Since 23 Sept, 14 hash values are on more than 1 file. For 13 of them, the files are an original and its 880-byte copy. For 1, the files are both PO originals and their copies. Thus the agent trusts none of these hashes. Both PO "(1)" files match on name + size.<br>A file with the same name that goes to the same folder is also a possible copy. The agent escalates it (same-name rule, A3). | The agent finds the PO pair and reports it as not byte-verified. It escalates the removal | ✅ it always says "not byte-verified". It rejects the shared Suryodaya hash and the 14 Keystone hashes. TI7 plants trusted pairs offline. Until 4 Oct, triage archived a hash-matched copy next to its original (TI2 expected this until 22 Sept) | `skills/duplicates.py`, `skills/triage.py` | DU1, TI1, TI2, TI7 |
| A7 | Provenance notes | M-Files | Every write **appends** a dated note to the description. For example: `[Files Agent 2026-09-22] Moved Incoming -> HR. Evidence: description, filename_pattern, sender. Score: 4 (threshold 3).` Sessions have the `actor_label` "Files Agent (team20)". The agent sends `actor_kind` only if `AS_ACTOR_KIND` has a value. It never sends `actor_roles` or `tool_policy_id`. | Every change by the agent is visible on the file, with an explanation | ✅ but no task checks the note text yet. You can see the note in the after-state of TI2. `AS_ACTOR_KIND` stays blank until the staff answer Q7 | `skills/triage.py`, `skills/escalate.py`, `config.py` | TI2 |
| A8 | Undo log and clobber check | Box `If-Match` (in spirit) | Before each write, the agent re-reads the row. It skips the row if it changed (SKIPPED). After the write, it re-reads the row again. It reports FAILED if the change of the agent is no longer there.<br>Live write runs also save `snapshot-N.json` and a `writes-N.json` journal. Then they restore the old values of only the fields that this seat changed, in a `finally` block. `python -m harness restore` does the same by hand. | You can fully reverse a run. The agent reports an overwrite by another person | 🟡 the checks are ✅. Restore exists, but it runs only in a live write run (TI2L). There has been no live write run yet. Restore restores only file fields (sessions and escalations stay) | `guards.py`, `snapshot.py`, `harness/runner.py`, `harness/__main__.py` | TI4, TI5 · restore: no task yet. There were one-off offline checks. On 22 Sept 2026, all 6 changed rows returned to their old values. On 27 Sept (S13 in 7.3), all 5 returned to their old values |
| A9 | Routed escalation | Box Automate | In apply mode, the agent makes 1 `AgentSession` per run. Then it makes 1 `AgentEscalation` for each file that it refuses, escalates or finds in conflict. This includes a possible copy (decision C). But the agent **never makes one for a file outside the write allow-list of the run**. (27 Sept: escalations are permanent, so the live write run escalates only originals.)<br>The subject `[files-agent] <file id> <filename>` is the de-duplication key. If the file has a Party, `party_id` is that Party. For an unfiled file, the reason names the person to ask: the sender, or else the uploader in the access log. Of the 4 live (TI2L) escalations, only the one for `Untitled.pdf` names no person. Offline, 8 of the 9 bare copies also name no person (no sender, no upload record). | Each refusal makes 1 escalation that names who can answer. Re-runs do not make a duplicate | ✅ escalations have no assignee (Keystone has no assignees). `reason_code` is always `other`, because the agent answers out-of-seat refusals and does not escalate them. The agent does not use `endpoint.people_directory` | `skills/escalate.py`, `skills/triage.py` | R4, TI2, TI2L, TI3, TI6, TI7 |
| A10 | Boundary explainer | — | `explain_access` reads `allowed_apps` from `/api/auth/me`. It maps the request to an app with word patterns (payslips → payroll, design files → designreview, …). If that app is outside the seat, it refuses and says who to ask. | "Show payslips" → the agent says that payroll is not in its seat | ✅ keyword-based. The agent does not refuse a request that matches no pattern | `skills/access.py` | R1, the route questions (`harness/tasks/routes.toml`) |
| A11 | Leak guard | Glean (pattern) | If the `entity_type` of a file row has no `<Entity>.list` tool in this seat, the row becomes a placeholder (`EsignDocument-attachment-1a2b3c4d.pdf`). The agent blanks its private fields. This applies to skills, the model's own reads, traces and fixtures. `list_files` counts the hidden rows. | "List all files" hides the 83 e-sign rows and says so | ✅ it uses the tool list, not a 403 probe | `privacy.py`, `catalog.py`, `loop.py`, `skills/access.py` | C2, C3 |
| A12 | Contradiction detector | — | `drive_overview` compares the total of the storage overview (`GET /api/drive/records/overview`) with the full record list. It gives both numbers and the reason. The reason: the overview counts only rows with `entity_type = 'Drive'`. There were 0 such rows on 22 Sept. Since 23 Sept, there are 15: the bare copies. It also says which number it used. | It explains why Drive says 0 while 15 files are in folders (since 23 Sept: 15 while 30 are in folders) | ✅ the agent does not query the Drive screen itself. The agent uses the overview in place of the screen | `skills/overview.py` | C1 |
| A13 | Scheduled triage | Box Relay / Automate | Nothing. An `AgentTask` cron runs the built-in agent of the platform, not this agent. You run the same triage on demand (plan-only by default). | — | ⛔ the team moved it out of Step 4 and proposed it as platform work (P7) | — | — |
| A14 | Filing rules stored as data | M-Files | Document types, weights, the threshold and the drawing-prefix folders are in 1 TOML file. The agent loads this file at start-up. It does not use `AgentMemory`. | The rules come from 1 editable place | ✅ · 👤 the values are a draft that you own | `filing_rules.toml`, `skills/profiles.py` | TI1, TI2, G1 |

Every task named here passes offline with the scripted model (4 Oct 2026, on the 26 Sept fixture). D1–D3, DU1, C1, C2, R1–R3 and TI1 also passed once live on 22 Sept 2026, before the data change. The scripted model picks skills by fixed rules. Thus these passes say nothing yet about the choices of the real model.

### 4.7 Platform change requests P1–P13

The agent cannot close these gaps alone. Each row says what the platform does not have, a concrete way to add it, and what this agent does until then. "Connection" or "access" means that the feature already exists in a different part of the platform. The tool schemas come from the fixture of 22 Sept 2026. The other platform facts are live measurements of 22 Sept 2026.

Type key: 🛠 platform work (staff) · 🐞 platform defect (the team raised a bug).

| Id | What the platform does not have | How to add it | Type | What it unlocks | What our agent does meanwhile |
|---|---|---|---|---|---|
| P1 | **File contents.** No bytes, no OCR, no text search | (a) **Short term:** when `save-from-email` creates a file, copy `EmailAttachment.extracted_text` into a new `FileAttachment.extracted_text`. 7 of the 9 original Incoming files have a sender email. `scan0042.pdf` and `Untitled.pdf` do not, and none of the 23 Sept copies has one. Thus only (b) helps those 2 files. (b) Store bytes on upload and run an OCR job. (c) Index `extracted_text`, `tags` and `description` in `/api/search` and `FileAttachment?search=`. | 🛠 connection, then build | Classification of `scan0042.pdf` and `Untitled.pdf` · search by content | `file_contents` refuses to quote and lists what the record holds. Triage refuses files with no signals and escalates them (R3, TI2). |
| P2 | **Enforced revision / lifecycle state** | Add 3 fields to `FileAttachment`. `document_key` is the family, for example the part code. `revision` is text, with a scheme that sets the order. `lifecycle_state` (draft → in_review → released → superseded → obsolete) is a real `flow` with role rules. The release of a revision supersedes the old current one.<br>**Cheaper:** fill `Item.design_file_id` (empty on all 28 Keystone parts). Then give the Files seat read access to the release flow that design review already has (`DesignFile`: "Approve Release"). | 🛠 build, or connection + access | "Current drawing" becomes a database fact | `find_drawing` infers "current" from 3 editable signals. It flags conflicts. It names no drawing when the signals do not agree (D1, D3). |
| P3 | **Trash/restore for this seat** | First, confirm whether `POST /api/drive/files/{id}/trash` works on Keystone rows. Then make it and `/restore` work on any `FileAttachment` with a `folder_id`. Make both available as MCP tools. **Keep delete admin-only**, because every seat can write these tables. | 🛠 confirm, then build | Removal of the duplicate PO | `remove_file` always refuses. It cites `_permissions.delete` and the tool that is not there. If 2 candidates have the same name, it first asks which id (R2, R5).<br>Triage never archives a possible copy. It escalates the copy, so that a person can decide (decision C). On 4 Oct 2026, these are the PO "(1)" files (TI2). On live, it is only 82f83d94 (TI2L). |
| P4 | **Rename for files with revisions** | `POST /api/drive/files/{id}/rename`. It creates a revision with `operation='rename'`, so the history stays. | 🛠 build | Correction of misnamed files | — (the agent never renames. It writes only `folder_id` and `description`.) |
| P5 | **Permissions on shared tables** (bugs F1, F2: the seat can see notices and e-sign titles of other apps) | Map each `entity_type` to the app that owns it. Apply this map to list, get, search, export and aggregate on `FileAttachment` and `Notification`. Limit `Notification` to its recipient. **Remove these fields from the `FileAttachment.create/update` input schemas (and ignore them in REST):** `content_hash`, `size_bytes`, `storage_path`, `current_revision_id`, `current_revision_number`, `download_count`, `received_at`, `from_email`, `from_name`, `message_subject`, `thread_id`, `company_id`. | 🐞 build (security) | It closes the leaks. It makes hashes trustworthy | The leak guard (A11) hides e-sign rows after they arrive. The agent never reads `Notification` or `/api/search`. The agent calls hashes "recorded", never "verified" (C2, C3, DU1). |
| P6 | **Concurrency guard** | `FileAttachment.update` (MCP) and the REST update accept an optional `expect_updated_at` (the exact `updated_at` from get or list). If it differs from the stored value, write nothing and return `409 {"error":"stale_write","current_updated_at":"…"}` (MCP: an error with the same body). Do the same for `DriveFolder.update`. *Precedent:* MCP `endpoint.agent_governance.escalations.update` already takes `expect_status`. *Acceptance:* 2 updates with the same `expect_updated_at` → the second receives 409. | 🛠 small build | Safe edits on a shared database | It does the same check on the client side. It re-reads before every write. It skips the row if `folder_id`, `description` or `updated_at` changed (SKIPPED). It re-reads after the write. It reports FAILED if the change of the agent is no longer there. The agent still misses a change that lands between its re-read and its write (TI4, TI5). |
| P7 | **Typed metadata and rules** | Use the `/api/custom-fields` route that already exists to define custom fields on `FileAttachment` (`document_type` select, `expiry_date`, `tax_year`). Add MCP tools for them. Give the Files seat the Automations app for rules (for example, `on_create` in Incoming → run triage). This also covers scheduled triage (A13). | 🛠 configuration + access | "Which W-9s expire this year?" · triage as soon as a file arrives | The document type comes from the filename (A2). The agent uses the rules in `agent/filing_rules.toml` for this (A14). The agent stores nothing on the file. There is no schedule: you run the triage yourself. |
| P8 | **A trustworthy move/rename history** (bug L8: the browser writes the access log) | The server writes a governance event on every move, rename and archive, with the from/to folder and the session actor. Remove client `create` on the audit tables. | 🐞 build | An undo trail that nobody can fake | It appends a dated note to each moved file. It logs every write in the run trace (and, on live write runs, in `writes-N.json`). It uses the access log only as a lead ("uploader per access log"). |
| P9 | **Complete search** (bug F5: search stops at 5 hits per type) | Honour `limit`. Return per-type totals or `has_more`. Add pagination. | 🐞 small build | A search that finds all files, and does not miss some without a warning | It never calls `/api/search`. It reads all pages of the full list and filters in code (`safe_reads.py`) (C1, C2). |
| P10 | **Server-side duplicate detection** | Compute a full 64-hex SHA-256 on upload, and make it read-only. Add a **new**, drive-scoped `/api/drive/duplicates` that lists clusters. Filter the clusters by tenant and by `drive` in `allowed_apps`. **Do not extend the current `/api/duplicates`**. It scans the Party contact directory. It also has an "unscoped" flag. | 🛠 build | Proven duplicates, not inferred ones | `find_duplicates` (A6) matches on recorded hash + size + name. It does not trust shared hashes, and it never says "byte-verified" (DU1). |
| P11 | **Collections** | A many-to-many `DriveCollection` entity, or a server-side filter on `tags`. | 🛠 build | A quality pack for heat 88213, with no need to move files | — |
| P12 | **Fix the Keystone seed** (bug F3: the Drive routes cannot see the scenario files) | **Backfill in place, and keep every id that exists now:** set `entity_type = 'Drive'` and create revision 1 for the 15 foldered rows. Announce when this happens. **Do not upload again during Step 4**, because new ids would break the fixtures of every team.<br>*Acceptance:* the Drive view lists the same 9 Incoming ids. *Careful:* 6 of the 15 rows link to their part through `entity_type = 'Item'` + `entity_id`. The backfill must keep that link. If not, `find_drawing` and the `linked_record` signal of triage lose it.<br>**What happened (23 Sept):** instead, the platform's repair added a second, bare copy of all 15 rows with new ids. (See the note at the top of [section 5](background.md#5-background-the-platform-the-scenario-and-the-research).) The Drive routes still cannot see the originals. A teammate (Tanmay) submitted that as a bug. | 🐞 data fix | The graded task becomes visible on the Drive screen | Every skill reads files through the record API, not the Drive routes. `drive_overview` explains the gap (C1: 0 against 15 on 22 Sept, and 15 against 30 since 23 Sept). |
| P13 | **Escalation targets** | Link Keystone sign-ins to Parties, so that `escalations/assignees` is not empty. On 22 Sept 2026, it returned `noLinkedSignIns`. Add `entity_type/entity_id` to `AgentEscalation`, so that an escalation can point to a file. | 🛠 data + small build | Refusals reach a real person and a real record | Escalations have no assignee. The file id goes in the subject, which is also the de-duplication key. The reason names the person to ask, and `party_id` is the Party of the file (TI2, R4). |

### 4.8 Roadmap

Read each row from left to right. The columns are:
- **Now:** what the agent does on 4 Oct 2026.
- **Next:** this needs only cheap platform connections or access.
- **Later:** this needs the platform to build something new.

| Now (agent, Step 4) | Next (cheap platform connections) | Later (platform builds) |
|---|---|---|
| **Revisions:** A1 ✅ part → drawing resolver · A5 🟡 supersession, per part only | P2 🛠 fill `Item.design_file_id` + read access to design review's release flow | P2 🛠 native lifecycle states on `FileAttachment` |
| **Triage:** A2 🟡 type from the filename · A3 ✅ scored triage, with the same-name and scope rules · A14 ✅ rules file | P7 🛠 custom fields + Automations access (scheduled triage, A13, goes here) | P1 🛠 bytes and OCR |
| **Safe edits:** A4 🟡 plan-only default, re-read before each write · A7 ✅ notes · A8 🟡 checks built, restore not run live yet | P6 🛠 `expect_updated_at` guard | P3/P4 🛠 trash/restore and rename · P8 🐞 server-written history |
| **Duplicates:** A6 ✅ recorded-hash match. Since 23 Sept, the agent trusts no hash of a scenario file. The agent never writes to a possible copy. It only escalates it (decision C) | — | P10 🛠 server-side hashes and a drive-scoped duplicates route |
| **What this seat sees:** A11 ✅ leak guard · A12 ✅ contradiction detector | P5 🐞 permissions by the app that owns the data · P12 🐞 seed backfill · P9 🐞 complete search | P11 🛠 collections |
| **Refusals:** A9 ✅ routed escalation · A10 ✅ boundary explainer | — | P13 🛠 escalation targets |
| **Not built:** A13 ⛔ scheduled triage (now part of P7) | — | — |
| **Still to do:** **Tests (👤):** write more tests by hand. There are 157 tests now: 78 in PR #4 and 79 in PR #5. They fully cover 37 of the 94 planned scenarios. `tests/README.md` lists the tests that are still to write for the STRIDE fixes, decision C and the other scenarios.<br>**Old tests (👤):** delete 2 of the 4 `FollowOriginalTests`. Rewrite the other 2. They assert the duplicate rule before decision C.<br>**Review (👤):** review the AI-drafted rules, task files and verifiers. The team confirmed decisions A and B and the ambiguity rule. TI7, the task for decision C, is a draft. Also review the AI-assisted STRIDE fixes ([Security review](safety.md#security-review-stride)).<br>**Real model:** do runs with the real model.<br>**Live write:** do the single live write run (TI2L). The team chooses the date, and the repo owner must approve it. See [11](live-run.md#11-the-live-write-run). | — | — |
