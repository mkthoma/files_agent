# The live write run

This file holds these parts of the old README (before the split):

- the paragraph *Before the live write run* from the Security review (STRIDE) section
- section 7.6
- section 11.

The ids, code, numbers and dates are from the old README. [The docs index](README.md#corrections-after-the-split) lists the facts that changed.

---

## Before the live write run

This text was the last paragraph of the *Security review (STRIDE)* section of the old README. The rest of that section is in [safety.md](safety.md#security-review-stride).

**Before the live write run** (see [11](#11-the-live-write-run) and section 11 of the report), do these steps:

1. Run `python -m harness preflight` a long time before the write date. Up to 4 Oct 2026, the stricter checks of PR #4 did not run against live.
2. On live (read-only), make sure that the 3 write tools reply with a JSON object.
3. On live (read-only), make sure that `created_by` and `updated_by` have values.
4. Re-capture the fixture within 24 hours of the run.

---

### 7.6 Before, during and after the live write run

Only **TI2L** runs live with writes, and it runs only **once**. Since 27 Sept, TI2 is offline-only. TI2L makes escalations and a session that this seat can never delete.

Up to 4 Oct 2026, this run did not occur. The team will choose the date of the run. The run needs the explicit approval of the repo owner. The full list of preconditions is in [11](#11-the-live-write-run).

| When | Do this |
|---|---|
| **Before** | ① Check every precondition in [11](#11-the-live-write-run). These include the real-model read-only runs, your hand-written tests (PR #4) and the approval of the repo owner. Your tests must pass again after the fresh capture in ②.<br>Staff question Q1 (leave Incoming tidied, or restore it?) is still open. Now, the harness **always** restores. To leave Incoming tidied, the code must change.<br>② Capture a fresh fixture **within 24 hours of the run**. Pre-flight refuses an older fixture.<br>Run `python -m harness capture keystone`.<br>Then run `python -m harness run TI2L --target fake --model scripted --set ti2l-check`. It must pass against the fresh fixture.<br>Then do a live read-only TI1 run: `python -m harness run TI1 --target live --model anthropic --repeat 1`. It must plan 5 moves and 4 escalations. It must list 9 files as out of scope.<br>Then run `python -m harness preflight`. It must print `pre-flight OK` with **exactly 9 warnings**, 1 for each 23 Sept copy. If there is a problem, or if the number of warnings is not 9, stop.<br>③ Save the state of Incoming before the run (block B, plus the description) to a git-ignored file.<br>Use this command: `(Get-AS "/api/FileAttachment?folder_id=6f8a3ed1-f2df-46a7-8dcb-275e9494c799&limit=50").data \| Select-Object id, filename, folder_id, is_archived, tags, description, updated_at \| ConvertTo-Json \| Out-File -Encoding utf8 runs\incoming-before.json`<br>④ Record the 7.2 "Your escalations" number (0 before any live run).<br>⑤ Tell your teammates. Make sure that nobody else has `AS_ALLOW_WRITES` set. |
| **Run** | **WARNING:** Do not do this step until you complete the Before row. It writes to the live platform. It makes escalations and a session that this seat cannot delete.<br>Bash: `AS_ALLOW_WRITES=1 python -m harness run TI2L --target live --model anthropic --live-apply --set live-write`.<br>PowerShell: `$env:AS_ALLOW_WRITES = "1"; python -m harness run TI2L --target live --model anthropic --live-apply --set live-write; Remove-Item Env:AS_ALLOW_WRITES`.<br>The harness runs pre-flight again. It prints the 9 warnings and continues. If there is a problem, the harness stops.<br>The harness saves `runs/live-write/TI2L/snapshot-1.json`.<br>It saves each write to `writes-1.json` at the time that it sends the write.<br>It runs the task once and records the state after the task.<br>Then it restores in a `finally` block. |
| **During** | Watch the run file while it grows. In PowerShell, use `Get-Content runs\live-write\TI2L\1.jsonl -Wait`. In bash, use `tail -f runs/live-write/TI2L/1.jsonl`.<br>Every `FileAttachment.update` must name 1 of the 9 allow-listed ids.<br>Every `AgentEscalation.create` must name 1 of the 4 unfiled originals.<br>`writes-1.json` receives 1 new entry for each write. The total is 10: 5 file updates, 1 session and 4 escalations. |
| **After** | ① Read the score that the run prints (TI2L PASS or FAIL, with reasons).<br>List the ids that the run updated: `python -c "import json; print(sorted({e['args']['id'] for e in map(json.loads, open('runs/live-write/TI2L/1.jsonl', encoding='utf-8')) if e.get('kind') == 'mcp_call' and e.get('tool') == 'FileAttachment.update'}))"`.<br>The list must have 5 ids, all from the 9. These are the originals of the timesheet, J-KNOB-09, mill certificate, W-9 and PO.<br>② Find the `restore` event, and the last line, `post_restore`. The lines between them are the reads that record the state after the restore.<br>Print the restore report with `python -c "import json; [print({k: e.get(k) for k in ('restored', 'failed', 'remaining', 'conflicts_left_alone', 'kept_foreign_edits')}) for e in map(json.loads, open('runs/live-write/TI2L/1.jsonl', encoding='utf-8')) if e.get('kind') == 'restore']"`.<br>In the report, `failed`, `remaining` and `conflicts_left_alone` must be empty.<br>Another team changed each item under `conflicts_left_alone`. Examine these items by hand.<br>Each item under `kept_foreign_edits` is a description that another team edited between the snapshot and the agent's write. For these items, the restore kept the text of the other team and removed the note of the agent from it. It did not use the text of the snapshot. Thus these items also differ from the state before the run that you saved in ③.<br>A second restore lists these fields under `conflicts_left_alone` and does not change them.<br>An item under `failed` or `remaining` means that the restore of this seat did not complete. In this case, the run also printed `restore incomplete`. Follow the last row of this table.<br>③ Run the Before ③ command again, but write to `runs\incoming-after.json`.<br>Compare the 2 files: `Compare-Object (Get-Content runs\incoming-before.json) (Get-Content runs\incoming-after.json)`.<br>The folders, archived flags, tags and descriptions must match the state before the run. Only `updated_at` is different, and only for the 5 files that the run wrote. The 9 copies must be exactly as before.<br>④ Examine the escalations. The "Your escalations" number must be exactly 4 higher. All 4 new escalations must be about originals:<br>- `Untitled.pdf` (`60f685c9-…`)<br>- `scan0042.pdf` (`b1d3894c-…`)<br>- `IMG_20260814_093214.jpg` (`8018a70b-…`)<br>- `PO_4471_ApexMetals_signed (1).pdf` (`82f83d94-…`, a possible copy of the PO original, decision C).<br>Each of these 4 files must have only 1 new escalation. The new escalations must not be about any of the 9 copies. The escalations stay, because this seat cannot delete them.<br>⑤ Run block D (7.2). The output is: `no secrets found`.<br>⑥ **Re-capture the fixture:** `python -m harness capture keystone`. The tidy and the restore gave a new `updated_at` to each file that they wrote. Without a new capture, the next pre-flight will fail against the old fixture. |
| **If the restore is incomplete** | The run prints `restore incomplete for [...]`.<br>Fix the cause. Then run the restore on its own. The restore reads `writes-1.json` next to the snapshot.<br>WARNING: Do this step only to complete an incomplete live restore. The command writes to the live platform.<br>Bash: `AS_ALLOW_WRITES=1 python -m harness restore runs/live-write/TI2L/snapshot-1.json --target live --live-apply`.<br>PowerShell: `$env:AS_ALLOW_WRITES = "1"; python -m harness restore runs/live-write/TI2L/snapshot-1.json --target live --live-apply; Remove-Item Env:AS_ALLOW_WRITES`. |

---

## 11. The live write run

**Status (4 Oct 2026): not run.** The live write run will be the single run of **TI2L**. The team will choose the date. The run needs the explicit approval of the repo owner. Since 27 Sept, TI2 is offline-only.

**Before the run, complete all of these items** (the step-by-step version is in [7.6](#76-before-during-and-after-the-live-write-run)):

1. Do read-only runs with the real model (`--model anthropic`).
2. Make sure that the team's hand-written tests for the new rules (pre-flight, scope and same-name) pass. PR #4 added these tests (`tests/test_decisions.py`). All the hand-written tests must pass again on the fresh fixture of step 3 (for the count, see [Tests](plan-and-status.md#tests)). If a number changes, update it in the same commit.
3. Run a fresh `python -m harness capture keystone` within 24 hours of the run. Pre-flight refuses an older fixture.
4. Make sure that TI2L passes offline against that fresh fixture.
5. Do a live read-only TI1 run. It must plan 5 moves and 4 escalations. It must list 9 files as out of scope.
6. Run `python -m harness preflight`. It must print `pre-flight OK` with exactly the 9 copy warnings.
7. Review the STRIDE fixes as a team. Then do 2 read-only checks on live (section 11 of [the report](security/stride-review.md)):
   - The 3 write tools reply with a JSON object.
   - `created_by` and `updated_by` have values.
8. Merge decision C before the run. Then the run and any later restore use the same code. The current restore refuses a journal from the older code that archived files (rule 8 in [8](safety.md#8-safety-on-the-shared-platform)).

Staff question Q1 (leave Incoming tidied, or restore it?) is still open. The harness always restores. This is the assumption in [6.6](plan-and-status.md#66-questions-for-staff).

**WARNING:** Do not run the last command until all 8 items above are complete. It writes to the live platform. It makes escalations and a session that this seat cannot delete.

```bash
python -m harness capture keystone                              # fresh baseline (within 24 hours of the run)
python -m harness run TI2L --target fake --model scripted       # must pass against it
python -m harness preflight                                     # must say OK, with exactly 9 warnings
AS_ALLOW_WRITES=1 python -m harness run TI2L --target live --model anthropic --live-apply --set live-write
```

The harness does these steps:

1. It runs pre-flight again.
2. It makes a snapshot of the 9 files.
3. It saves each write to `writes-1.json` at the time that it sends the write.
4. It runs the task and records the state.
5. It **restores** the old values of only the fields that this seat changed (see rule 8 in [8](safety.md#8-safety-on-the-shared-platform), which also covers `kept_foreign_edits`).

An earlier attempt can fail before it sends anything, for example at login or pre-flight. In this case, you can run the same command again. The harness moves the files of that attempt to a different location and prints a message about it.

**Expected live changes** (from the offline rehearsal, TI2L and S13 with the live cap):

- **5 moves of originals**. After the run, the restore restores the old values, so the 5 files are in Incoming again. The 5 moves are:
  - the timesheet to HR
  - J-KNOB-09 to Jig & Fixture Drawings
  - the mill certificate to Quality
  - the W-9 and the PO to Purchasing.
- **4 permanent escalations, all about originals**: `Untitled.pdf`, `scan0042.pdf`, `IMG_20260814_093214.jpg` and `PO_4471_ApexMetals_signed (1).pdf`.
- **1 session**. It is permanent.
- **nothing on the 9 copies**: no write and no escalation. The answer lists them as not in the scope of this run.

**Only TI2L writes live, and only once.** It is the only task that has `live_write = true`. The harness refuses any other write task on live. After the run, re-capture the fixture. The run and its restore change the `updated_at` of each file that they write. If you do not re-capture, the next pre-flight will fail.

If the restore reports `restore incomplete`, fix the cause. Then run the restore again on its own.

WARNING: Do this step only to complete an incomplete live restore. The command writes to the live platform.

```bash
AS_ALLOW_WRITES=1 python -m harness restore runs/live-write/TI2L/snapshot-1.json --target live --live-apply
```
