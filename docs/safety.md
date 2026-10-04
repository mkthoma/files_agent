# Safety

This file holds these parts of the old README, from before the split:

- the Security review (STRIDE) section, without its last paragraph
- the ground rules of section 6.1
- section 8.

The ids, code, numbers and dates are from the old README. [The docs index](README.md#corrections-after-the-split) lists the facts that changed.

---

## Security review (STRIDE)

> **The team must review this** before the team trusts it. The full report is [`docs/security/stride-review.md`](security/stride-review.md).

On 2–3 Oct 2026, a **STRIDE** review examined the agent and the harness. STRIDE has 6 types of threat: Spoofing, Tampering, Repudiation, Information disclosure, Denial of service and Elevation of privilege. The review did these steps for each threat:

1. A proof-of-concept script reproduced the threat offline, against the real code.
2. A skeptical reviewer challenged the threat.
3. If a fix was safe, the review added the fix to the code.
4. The same script checked the threat again.

The review did not use the live platform.

- **54 threats:** 5 S, 14 T, 10 R, 12 I, 10 D and 3 E. **None is critical.** The highest verified risk is 4 out of 16 (Medium). The main cause is that these controls already made attacks hard to reach:
  - plan-only mode
  - the 9-file allow-list
  - the 2 live-write settings (`--live-apply` and `AS_ALLOW_WRITES`)
  - the leak guard.
- **49 fixed, 4 partly fixed, 1 accepted by design.**
  - Partly fixed:
    - **T2:** A name that another team planted still appears in an escalation. The code cleans the name to a single labelled line.
    - **T5:** A model that cites a real but wrong id still passes.
    - **T11:** The platform has no compare-and-set. This is a platform request.
    - **R2:** If a person edits a run file and scores it again, the result is still IDENTICAL. A fix needs a trust anchor outside the repo.
  - By design: **D5**. Pre-flight fails closed. As a result, any tenant user can block the live write run.
- Every guard in the code has a `# STRIDE <id>` comment. [Round 6](history.md#15-changes-after-review) lists the changes by area.
- **The graded behaviour did not change.** These are the offline results on the tree after the merge of PR #4:
  - 21 of 21 tasks pass ×5.
  - The rescore is IDENTICAL.
  - Routes are 10 / 10.
  - Calibration is 355 of 355. It grew from 295 with the new checks.
  - The 78 hand-written tests pass.

  On the tree that added the tests of PR #5 (3 Oct), all 157 tests passed. Decision C (4 Oct) then added TI7. After that, the tasks were 22 of 22 and calibration was 377 of 377 (see [Round 7](history.md#15-changes-after-review)).

**Behaviour changes that operators must know:**

| Area | What changed |
|---|---|
| Live write gate | The harness refuses `--live-apply` without `--target live` (exit 3), for `run` and `restore`. The harness refuses a live write task if an earlier live attempt possibly sent a write. It moves an attempt that provably sent nothing to `attempt-<time>/`. `--set` must be a plain folder name under `runs/`. A live write needs the write journal. |
| Pre-flight | Pre-flight needs a fixture that you captured **within the last 24 hours**. Thus, capture the fixture on the day of the live write run. Pre-flight also stops if a tool description or a read-only mark changed. It stops if somebody added, removed, renamed, moved or archived a folder, or changed a folder in another way. It also stops if 2 folders have the same name.<br>With PR #4, it also stops on a new or changed file in any folder. This applies if the file has the same document kind (or drawing code prefix) as 1 of the 9. Each problem says who made the change. Pre-flight also prints the recovery steps. Pre-flight refuses a fixture that does not match the hashes in its manifest. |
| Writes | The guard writes only `folder_id` and `description` (since decision C, 4 Oct). Before decision C, it also wrote `is_archived`. It never writes an `id` inside the changes. The MCP client refuses any tool that is not one of the 3 write tools and has no read-only mark. If the reply to a write is not a JSON object, the journal records the write as **uncertain**. Only escalations that this seat created (the server-set `created_by`) prevent a new escalation. |
| Restore | Restore needs `writes-N.json`. `--no-journal` is the last resort. Restore restores the old values of only the 2 fields of the agent: `folder_id` and `description`. Restore refuses, on purpose, a journal from before decision C that holds `is_archived`. Its message names the commit to use for the restore of that journal.<br>If another team edited a description between the snapshot and the agent's write, restore keeps their text (`kept_foreign_edits`). Restore refuses a malformed, cut-off or edited snapshot or journal. It also refuses a snapshot or journal from the other target. |
| Network and budget | The code uses HTTPS only. It follows no redirect for the platform or the model API. Every request has a wall-clock limit and a size cap. If the worst case of a model call is more than the $ cap, the code does not send the call.<br>At most 10 tool calls run in each turn. The Drive-overview read counts against the call cap (C1 now uses 3 calls). The code refuses `nan`, `inf`, 0 and negative values for caps and prices. |
| What the model sees | The model sees fixed tool descriptions and structure-only schemas. The code checks skill arguments against their schemas. A direct `FileAttachment.list` call from the model accepts only a fixed set of filters. The code refuses `search`.<br>Withheld rows keep only an allow-list of fields. The code reduces the content of access-log, party and escalation rows. The code withholds unknown platform error text. |
| Run files and scores | Run files also hold the data that the model saw (`tool_result` events). Thus, run files are bigger. `score.json` and `report.md` hold provenance: target, model, commit, fixture and tools. A cut-off run file counts as 1 failed run, not as a crash. The session title names its run file. |
| Secrets | `python scripts/secret_scan.py` (block D in 7.2) and `--history` print only the file and the line. Enable the pre-commit hook once with `git config core.hooksPath .githooks`. On POSIX, only the owner has access to `.env` and run files. The steps in section 7.2 never type a secret into the shell. |
| Team-owned task files | TI2, TI2L and TI3 now set `cited_ids_must_resolve`. TI2L also checks `no_events` for `write_blocked`. |

The last paragraph of this section, **Before the live write run**, is now in [live-run.md](live-run.md#before-the-live-write-run).

---

## Ground rules (old section 6.1)

These rules were part of section 6.1 of the old README. The rest of 6.1 is in [plan-and-status.md](plan-and-status.md#61-whats-graded-and-the-ground-rules).

**Ground rules**

1. **Build your own loop.** The agent calls the model through the plain Messages API over HTTPS. It uses only the standard library of Python (`urllib`). There is no SDK and no agent framework. Thus, there is nothing to install. The MCP client is hand-written. ✅ `agent/model.py`, `agent/mcp_client.py`
2. **Only skills write.** The model plans and explains. Code in the 8 skills does every agent write, through the write guard (`agent/guards.py`). The harness tasks and your hand-written tests in `tests/` run these skills. The only other writes come from the restore after a live write run (`agent/snapshot.py`). The restore restores the old values of only the fields that this seat wrote.

   The agent has only 3 write tools: `FileAttachment.update`, `AgentSession.create` and `AgentEscalation.create`. **Plan-only is the default.** ✅
3. **Keystone is a shared platform.** Live writes can change only the 9 allow-listed Incoming files. They can change these files only if the files are still in Incoming when the run starts. The agent does not write or escalate any other file. Since 27 Sept, this includes the 9 copies of 23 Sept.

   Only the harness does live writes, as the single run of TI2L. The command and the full steps are in [7.6](live-run.md#76-before-during-and-after-the-live-write-run) and [11](live-run.md#11-the-live-write-run).

   - Set `AS_ALLOW_WRITES=1` in the shell only for the live write command in [11](live-run.md#11-the-live-write-run). The harness ignores the value in `.env` for `AS_ALLOW_WRITES`.
   - `python -m agent ask --apply` works only with `--target fake`.
   - The harness runs pre-flight. It saves `snapshot-N.json` and a write journal, `writes-N.json`. It does the restore in a `finally` block. ✅
4. **Tests and the definition of "correct" are yours.** You write `tests/` by hand. These files exist now as **AI-written drafts**:
   - the task expectations (`harness/tasks/*.toml`, `harness/tasks/routes.toml`)
   - the rules for the score (`agent/filing_rules.toml`)
   - the checks (`harness/verifiers.py`).

   Review these files. Make your own changes to them. Commit them yourselves.

   AI help is only for the support code of the agent and the harness. Use AI help only if staff say yes to Q3. The code assumes that the answer is yes. If you want, block AI edits to your paths (T0.5, not done yet). 👤

---

## 8. Safety on the shared platform

The code enforces these rules, because other teams also use Keystone. The STRIDE review of 2–3 Oct checked each rule against the code (see [Security review (STRIDE)](#security-review-stride)).

1. **Plan-only by default.** If you do not ask for a write, the code writes nothing. `python -m agent ask --apply` writes **only on the fake server**. On live, the agent refuses this command.
2. **Only the harness does live writes.** A live write needs `--target live`, `--live-apply` **and** `AS_ALLOW_WRITES=1`. Set `AS_ALLOW_WRITES=1` in the shell for that one command only. A live `harness restore` needs the same 3 items: `--target live`, `--live-apply` and `AS_ALLOW_WRITES=1`.
   - The harness refuses `--live-apply` without `--target live`. It never runs the command quietly on the fake server.
   - The harness ignores the `.env` file for `AS_ALLOW_WRITES`. Thus, `AS_ALLOW_WRITES` cannot remain set by accident.
   - The code allows live writes only on Keystone.
   - The write guard in the code refuses any live write while it has no write journal.
   - The runtime accepts only the targets `live` and `fake`.
   - Any transport that is not the fake server receives the 9-id cap. The name of the transport has no effect.
3. **Row-id allow-list.** Writes can change only the 9 verified Incoming files (`agent/config.py`). Writes can change these files only if they are still in Incoming when the run starts. The code cannot write a new file that appears in Incoming.
4. **The agent writes and escalates nothing outside the allow-list** (since 27 Sept). Triage records such a file as `out_of_scope` and lists it for a person. The Escalator refuses to escalate it, because escalations are permanent. On live Keystone, this rule keeps the 9 copies of 23 Sept unchanged. TI2L tests this rule offline.
5. **Only 3 write tools exist for the agent:** `FileAttachment.update`, `AgentSession.create` and `AgentEscalation.create`. There is no delete path. The MCP client refuses any other tool that the catalogue does not mark read-only. The guard writes only `folder_id` and `description`. The agent never archives. It escalates a possible copy and never writes to it (decision C, [triage step 3](architecture.md#triage_folder-evidence-scored-filing)).
6. **Pre-flight before live writes.** The harness stops the run (aborts) if one of these conditions is true:
   - The tool catalogue changed. This includes the description or the read-only mark of a tool that the agent uses.
   - You did not capture the fixture within the last 24 hours.
   - Since the fixture, somebody added, removed, renamed, moved or archived a folder, or changed a folder in another way.
   - 2 folders have the same name.
   - One of the 9 files is not in Incoming, or it changed since the fixture.
   - One of the 9 files no longer has the tag `untriaged`.

   Pre-flight also examines every other row in Incoming:
   - If the fixture contains the row and the row did not change, the result is only a **warning**. The harness prints the warning and records it in the trace. Now, these rows are the 9 copies.
   - If the row is unknown or changed, the result is a **problem**, and the run stops. The reason is that such a row can change the decisions of the agent about the 9 files.

   For the same reason, pre-flight also examines the rows in all folders. A related row has the same name, recorded hash or document kind as one of the 9 files. The document kind is the document type, or the drawing code prefix. These are also problems:
   - A related row that is new, changed or gone since the fixture.
   - A changed row that related to one of the 9 files before the change.
   - A fixture row that left Incoming.
   - A fixture without a tool hash or a folder table.

   If the platform records who changed the row, the problem names that person. If this seat cannot open the app of a row, the problem names that row only by its placeholder. Pre-flight fails closed on purpose (see [14](known-limits.md#14-known-limits-and-open-questions)).
7. **Snapshot, write journal and restore.** A live write run does these steps:
   - It makes a snapshot of the 9 rows.
   - It saves an empty `writes-N.json` before the first write.
   - It saves each write as soon as its call ends. It saves a write with an error as `uncertain`.
   - It does the restore in a `finally` block. It does the restore even if the collection of the after-state fails.
8. **Restore does not overwrite other teams' changes that it can see.**
   - Restore reads each row again immediately before it restores the row.
   - Restore can restore only the fields that the agent writes (`folder_id`, `description`). It restores the old value of a field only if the field still holds the value that the agent wrote. Restore does not change anything else, and it reports it under `conflicts_left_alone`.
   - Restore restores a description to the text to which the agent appended its note. Thus an edit that another team made between the snapshot and the agent's write stays. Restore reports it under `kept_foreign_edits`. Restore restores every other field to its snapshot value.
   - Restore refuses a snapshot or journal that its own code cannot make. These are: ids outside the allow-list, unknown fields, wrong types, a cut-off file, and a snapshot from the other target. One failed row does not stop the other rows.
   - A journal from before decision C holds `is_archived`. Restore refuses such a journal on purpose and restores nothing. Its message says to restore with the commit that made the run. That commit is the git commit in the run manifest: 8202cf8 or earlier.
   - For this reason, merge decision C before the live write run. Do not merge it between that run and a later standalone restore.
   - If the write journal (`writes-N.json`) does not exist, `harness restore` refuses. Only `--no-journal` makes it restore the rows that this seat changed last.
9. **Only TI2L can write live. Fake-server-only tasks never run live.** A write task runs live only if its task file says `live_write = true`. Only TI2L has this setting. Since 27 Sept, TI2 runs offline only. The harness refuses tasks with `faults` or `extra_files` on `--target live`.
10. **Escalations and sessions are permanent.** This seat cannot delete them. Thus, live write tasks run **once**, and all repeated runs are offline. The harness enforces this rule. It refuses a live write task while any earlier live attempt (in any run set) possibly sent a write.

    An earlier attempt provably sent nothing if its set-up or pre-flight failed, or if it stopped before its first write. The harness moves such an attempt to `runs/<set>/<task>/attempt-<time>/`, and the run continues.
11. **The code never resends a write after an unclear failure.** After a 5xx or a timeout, the write possibly occurred already. Thus, the transport retries writes only on `429`. A write can receive an error from its call, or a malformed reply. In both cases, the journal records the write as `uncertain` and does not forget it, because the write possibly landed.

    If the creation of an escalation or a session fails, the code reads the list again to find it. If the code cannot find it, the code never sends it again in the same run. The fresh listing of the next run gives the answer.
12. **Secrets never reach disk.** The code redacts passwords, tokens and keys from every trace. It also masks their `repr`. Thus, a traceback that prints its locals cannot show them either. Block D (7.2) and `.githooks/pre-commit` check for leaks.
13. **The code cleans the text of other teams before it prints or stores the text.** The code cuts file, folder, party and uploader names to a single printable line (`agent/textsafe.py`). It does this before the names reach the console, a permanent escalation, a file note or `report.md`. It labels an access-log name as a lead, not a fact.
