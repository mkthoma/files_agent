# The live write run

This file holds these sections of the old README (before the split), word for word: the paragraph *Before the live write run* from the Security review (STRIDE) section, 7.6 and 11.

---

## Before the live write run

This paragraph was the last paragraph of the old README's *Security review (STRIDE)* section. The rest of that section is in [safety.md](safety.md#security-review-stride).

**Before the live write run** (see [11](#11-the-live-write-run) and section 11 of the report): re-capture within 24 hours; check on live (read-only) that the 3 write tools reply with a JSON object and that `created_by` and `updated_by` are filled in; and run `python -m harness preflight` well before the write date, because PR #4's stricter checks have not run against live yet.

---

### 7.6 Before, during and after the live write run

Only **TI2L** runs live with writes, and only **once** (TI2 is offline-only since 27 Sept). It creates escalations and a session that this seat can never delete. On 27 Sept 2026 this run had not happened yet. It happens on a date the team fixes, and only with the repo owner's explicit go-ahead. The full list of preconditions is in [11](#11-the-live-write-run).

| When | Do this |
|---|---|
| **Before** | ① Check every precondition in [11](#11-the-live-write-run): real-model read-only runs done, your hand-written tests (PR #4) passing again after the fresh capture in ②, the repo owner's go-ahead given. Staff Q1 (leave Incoming tidied, or restore it?) is still open; today the harness **always** restores, and leaving it tidied would need a code change. ② Fresh baseline, **within 24 hours of the run** (pre-flight refuses an older fixture): `python -m harness capture keystone`, then `python -m harness run TI2L --target fake --model scripted --set ti2l-check` must pass against it, then a live read-only TI1 (`python -m harness run TI1 --target live --model anthropic --repeat 1`) must plan 5 moves and 4 escalations and list 9 files as out of scope. Then `python -m harness preflight` must print `pre-flight OK` with **exactly 9 warnings**, one per 23 Sept copy (any problem, or any other number of warnings, means stop). ③ Save the "before" picture (block B, plus the description) to a git-ignored file: `(Get-AS "/api/FileAttachment?folder_id=6f8a3ed1-f2df-46a7-8dcb-275e9494c799&limit=50").data \| Select-Object id, filename, folder_id, is_archived, tags, description, updated_at \| ConvertTo-Json \| Out-File -Encoding utf8 runs\incoming-before.json` ④ Note 7.2 "Your escalations" (0 before any live run). ⑤ Tell your teammates, and check that nobody else has `AS_ALLOW_WRITES` set. |
| **Run** | Bash: `AS_ALLOW_WRITES=1 python -m harness run TI2L --target live --model anthropic --live-apply --set live-write`. PowerShell: `$env:AS_ALLOW_WRITES = "1"; python -m harness run TI2L --target live --model anthropic --live-apply --set live-write; Remove-Item Env:AS_ALLOW_WRITES`. The harness runs pre-flight again (it prints the 9 warnings and goes on; any problem stops it), saves `runs/live-write/TI2L/snapshot-1.json`, saves each write to `writes-1.json` the moment it is sent, runs the task once, records the state after, and then restores in a `finally` block. |
| **During** | Watch the run file grow: `Get-Content runs\live-write\TI2L\1.jsonl -Wait` (PowerShell) or `tail -f runs/live-write/TI2L/1.jsonl` (bash). Every `FileAttachment.update` must name one of the 9 allow-listed ids, and every `AgentEscalation.create` one of the 4 unfiled originals. `writes-1.json` grows by one entry per write: 10 in all (5 file updates, 1 session, 4 escalations). |
| **After** | ① Read the score it prints (TI2L PASS or FAIL, with reasons). List the ids that were updated: `python -c "import json; print(sorted({e['args']['id'] for e in map(json.loads, open('runs/live-write/TI2L/1.jsonl', encoding='utf-8')) if e.get('kind') == 'mcp_call' and e.get('tool') == 'FileAttachment.update'}))"`. There must be 5, all among the 9 (the originals of the timesheet, J-KNOB-09, mill cert, W-9 and PO). ② Find the `restore` event, and the last line, `post_restore` (the lines between them are the reads that record the state after the restore). Print the restore report with `python -c "import json; [print({k: e.get(k) for k in ('restored', 'failed', 'remaining', 'conflicts_left_alone', 'kept_foreign_edits')}) for e in map(json.loads, open('runs/live-write/TI2L/1.jsonl', encoding='utf-8')) if e.get('kind') == 'restore']"`. In it, `failed`, `remaining` and `conflicts_left_alone` should be empty. Anything under `conflicts_left_alone` was changed by another team, so check it by hand. Anything under `kept_foreign_edits` is a description another team edited between the snapshot and our write: restore put back their text with our note removed, not the snapshot's text, so it also differs from your "before" picture in ③. A second restore lists those fields under `conflicts_left_alone` and leaves them alone. Anything under `failed` or `remaining` means our own restore did not land: the run also printed `restore incomplete`, so follow the last row of this table. ③ Run the Before ③ command again, but write to `runs\incoming-after.json`, then compare: `Compare-Object (Get-Content runs\incoming-before.json) (Get-Content runs\incoming-after.json)`. Folders, archived flags, tags and descriptions must match the "before" picture. Only `updated_at` differs, and only for the 5 files that were written; the 9 copies must be exactly as before. ④ Escalations: "Your escalations" is up by exactly 4, all about originals: `Untitled.pdf` (`60f685c9-…`), `scan0042.pdf` (`b1d3894c-…`), `IMG_20260814_093214.jpg` (`8018a70b-…`) and `PO_4471_ApexMetals_signed (1).pdf` (`82f83d94-…`, a possible copy of the PO original, decision C), with none doubled and none about one of the 9 copies. They stay, because this seat can't delete them. ⑤ Run block D (7.2): `no secrets found`. ⑥ **Re-capture the fixture:** `python -m harness capture keystone`. Every file that was written now has a new `updated_at` (from the tidy and from the restore), so the next pre-flight would fail against the old fixture. |
| **If the restore is incomplete** | The run prints `restore incomplete for [...]`. Fix the cause, then restore on its own. It reads `writes-1.json` beside the snapshot. Bash: `AS_ALLOW_WRITES=1 python -m harness restore runs/live-write/TI2L/snapshot-1.json --target live --live-apply`. PowerShell: `$env:AS_ALLOW_WRITES = "1"; python -m harness restore runs/live-write/TI2L/snapshot-1.json --target live --live-apply; Remove-Item Env:AS_ALLOW_WRITES`. |

---

## 11. The live write run

**Status (4 Oct 2026): not run.** It will be the single run of **TI2L**, on a date the team fixes, and only with the repo owner's explicit go-ahead. TI2 is offline-only since 27 Sept.

**Before it, all of these must be done** (the step-by-step version is in [7.6](#76-before-during-and-after-the-live-write-run)):
1. read-only runs with the real model (`--model anthropic`);
2. the team's hand-written tests for the new rules (pre-flight, scope and same-name): written in PR #4 (`tests/test_decisions.py`). All 157 tests must pass again on the fresh fixture of step 3, with any changed numbers updated in the same commit;
3. a fresh `python -m harness capture keystone`, within 24 hours of the run (pre-flight refuses an older fixture);
4. TI2L passing offline against that fresh fixture;
5. a live read-only TI1 that plans 5 moves and 4 escalations and lists 9 files as out of scope;
6. `python -m harness preflight` printing `pre-flight OK` with exactly the 9 copy warnings;
7. the team's review of the STRIDE fixes, and two read-only checks on live: the 3 write tools reply with a JSON object, and `created_by` and `updated_by` are filled in (section 11 of [the report](security/stride-review.md));
8. decision C merged before the run, so the run and any later restore use the same code: today's restore refuses a journal written by older code that archived (rule 8 in [8](safety.md#8-safety-on-the-shared-platform)).

Staff question Q1 (leave Incoming tidied, or restore it?) is still open; the harness always restores, which is the assumption in [6.6](plan-and-status.md#66-questions-for-staff).

```bash
python -m harness capture keystone                              # fresh baseline (within 24 hours of the run)
python -m harness run TI2L --target fake --model scripted       # must pass against it
python -m harness preflight                                     # must say OK, with exactly 9 warnings
AS_ALLOW_WRITES=1 python -m harness run TI2L --target live --model anthropic --live-apply --set live-write
```

The harness runs pre-flight again, snapshots the 9 files, saves every write to `writes-1.json` as it is sent, runs the task and records the state. It then **restores** only the changes this seat made (see rule 8 in [8](safety.md#8-safety-on-the-shared-platform), including `kept_foreign_edits`). If an earlier attempt failed before sending anything (for example at login or pre-flight), the same command can simply be run again: the harness moves that attempt's files aside and says so.

**Expected live footprint** (from the offline rehearsal, TI2L and S13 with the live cap):
- **5 moves of originals**, restored afterwards: the timesheet to HR, J-KNOB-09 to Jig & Fixture Drawings, the mill cert to Quality, the W-9 and the PO to Purchasing;
- **4 permanent escalations, all about originals**: `Untitled.pdf`, `scan0042.pdf`, `IMG_20260814_093214.jpg` and `PO_4471_ApexMetals_signed (1).pdf`;
- **1 session** (permanent);
- **nothing on the 9 copies**: no write, no escalation; the answer lists them as not in this run's scope.

**Only TI2L writes live, and only once.** It is the only task marked `live_write = true`; the harness refuses any other write task on live. Afterwards, re-capture the fixture. The run and its restore change the `updated_at` of every file they write, so the next pre-flight would otherwise abort.

If the restore reports `restore incomplete`, fix the cause and run it again on its own:
```bash
AS_ALLOW_WRITES=1 python -m harness restore runs/live-write/TI2L/snapshot-1.json --target live --live-apply
```
