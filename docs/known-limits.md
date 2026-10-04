# Known limits

This file holds these sections of the old README (before the split): 14. The ids, code, numbers and dates are from the old README. [The docs index](README.md#corrections-after-the-split) lists the facts that changed.

---

## 14. Known limits and open questions

**About the platform**

- **No file contents:** The agent makes its decisions from the metadata only. It refuses an action that it cannot justify.

- **The content hash is client-writable.** That is, a client can change the hash. The agent cannot calculate the hash again. Thus each duplicate match is "per recorded metadata" only, and no check compares the bytes. Thus a duplicate match never causes a write to the file (decision C, [triage step 3](architecture.md#triage_folder-evidence-scored-filing)). Only a read-only hash that the server calculates (request P10) can give a reason to examine this decision again.

- **No escalation assignees on Keystone.** No escalation has an assignee. If the record has a sender or an access-log uploader, the escalation names that person as the person to ask. `Untitled.pdf` has no sender and no access-log uploader. Thus its escalation names no person.

- **No compare-and-set (STRIDE T11).** `FileAttachment.update` has no `if_updated_at` check and no ETag check. Thus the agent's write can overwrite a change from another team, and nothing shows that this occurred. This occurs if another team changes a field that the agent sends, between the re-read and the write of the agent. The same risk applies to the write of restore.

  **Platform request:** Add an `if_updated_at` (or ETag) argument to `FileAttachment.update`. With this argument, the platform refuses the write if the row changed after that value.

  The agent finds these changes now:

  - The pre-read skips a row that changed after the plan (`stale_row`).
  - The read that confirms each write reports a write that another seat overwrote immediately after the agent's write (`write_not_confirmed`).
  - A field that the agent did *not* send can change inside the write window of the agent. The trace records this change as `concurrent_change`. The agent records this change on the `applied` decision record and names it in the answer.

- **Pre-flight fails closed on purpose (STRIDE D5).** Any person in the tenant can stop the live write run with one of these changes:

  - a change in Incoming
  - a change to any folder, even a folder that triage never uses. The change can be a new folder, or a folder that a person renames, moves or archives.
  - a change to a related file in any location. A related file has the same name, recorded hash or document kind as one of the 9.

  After such a change, pre-flight reports a problem, and the run writes nothing. This is deliberate. The live expectations come from 1 set of data, and they are correct only for that data. If the platform records who changed the row, the problem names that person. `harness preflight` prints the steps for recovery (see also [16](troubleshooting.md#16-troubleshooting)).

  The document-kind check of PR #4 examines each row as triage sees it:

  - If a row is from an app that this seat cannot open, the check uses only its placeholder name. Thus the real title cannot block the run. Also, nobody can use pre-flight to probe the real title (STRIDE I7).
  - A file row with no filename is not related.

  The checks of PR #4 have not run live yet. Thus, run the read-only `python -m harness preflight` command a long time before the write date.

- **Fixture capture keeps only what the agent reads (STRIDE I2).** The capture does these things:

  - In access-log rows, it keeps only the fields that the agent reads. It does not keep `share_token` or `actor_ip`.
  - It removes the title and the details from a row about a withheld file.
  - In the Drive overview, it lists only open files.

  The committed fixtures received the same changes, but they had no sensitive data in them:

  - The platform already returns `share_token` and `actor_ip` as null.
  - No committed row names a withheld file.

  The git history is clean.

- **The platform continues to change:** If the tool hash changes, capture the fixtures again. Then run the offline suite again.

- **The 880-byte copies and the Drive views (since 23 Sept).** The Drive screen and the storage overview now count only the 15 bare copies (15 files, 13,200 bytes). They do not count the 15 originals. Thus a person who uses the Drive screen sees copies with no tags, no sender and no description. Each copy has the name and the recorded hash of its original. This is why 14 hashes occur on more than 1 file, and why the agent trusts no hash.

  The agent reads the record list, so it sees the copies and the originals. It never deletes or merges the copies. On live, it leaves them as they are.

- **The Suryodaya fixture is stale.** The fixture is from 22 Sept, and it shows 208 tools. On 27 Sept, live Suryodaya had 212 tools. Before you trust a Suryodaya offline check such as T2.7, capture the fixture again (`python -m harness capture suryodaya`).

**About the agent (what the code does *not* do)**

- **The answers do not come only from records.** The model writes free text, and the code adds a record trail after it. The harness compares the text of the model with the expectations of each task. 14 tasks set `cited_ids_must_resolve` (TI2L and TI7 included). In these tasks, the harness also checks that each cited **id** exists on the platform. No automatic check examines the filenames and part codes in the answer.

- **The leak guard covers file rows, and the model's direct reads.** A direct `FileAttachment.list` call from the model can filter only by a fixed set of fields. It cannot use `search`, filename filters or text filters. Thus the model cannot use the server to test a withheld title. The direct `Party.list`, `DriveAccessLog.list` and `AgentEscalation.list` calls also have their own fixed sets of filters (`MODEL_FILTERS` in `agent/loop.py`).

  These limits also apply:

  - An access-log row names a file only through the leak-guarded file list.
  - An escalation of another seat shows no text.
  - A Party row has only basic contact fields.
  - The agent withholds a platform error message that it does not recognise.
  - The tool descriptions of the platform never reach the model. The model receives the input schemas of the platform only as structure.

- **Planted names still appear, as labelled data (STRIDE T2, partly fixed).** `agent/textsafe.py` changes platform text before the text reaches the console, permanent escalations, file notes and reports:

  - It removes control characters, format characters (bidi, zero-width, tag characters, soft hyphen), private-use characters and unassigned characters.
  - It cuts names to 1 short line.

  The agent labels an access-log name as a lead. But if another team planted a party name or an uploader name, that name still appears in an escalation. Pre-flight does not watch party names.

- **A real but wrong id can pass (STRIDE T5, partly fixed).** The harness checks that each cited id exists. It does not check that each id is the correct one. Thus an answer that cites a real but wrong id (for example RevB as current) can still pass D1.

- **Rescore proves determinism, not integrity (STRIDE R2, partly fixed).** If a person edits a run file and scores it again, the result is still IDENTICAL (see [3.6](harness.md#36-scoring)). Only a trust anchor outside the repo can find this edit. Examples are a re-run by a grader, or a hash that CI publishes.

- **The trace records what the model *saw*.** The agent writes each tool result that the model sees to the run file, as a `tool_result` event. The leak guard and the cap apply to each result before this. C3 checks that the planted title appears nowhere in the run, and this includes these events.

- **The fake server is simpler than the platform.** Its list filters use plain equality. Thus offline runs do not reproduce the filter traps of the platform. The code in `safe_reads.py` protects against the traps that the bug reports describe.

- **Safe reads protect the skills.** The model's own direct list calls do not use safe reads. The code sends their filter values unchanged. Only 4 of the 6 list tools of the model have a fixed set of filters (see above). The leak guard still applies to their results, and the results still receive a truncation flag.

- **Revisions come from filenames only.** The agent uses tags to check consistency. It does not report a "released" date.

- **Name resolution is exact.** The agent first matches a record id in the request. There is 1 exception to the exact match. If a request contains the word "duplicate", the agent matches duplicate copies by the words in the request. This is how "Delete the duplicate PO file" finds its candidates.

  A request for *"the copy of `<id>`"* names a different file. Thus the agent does not use that id to resolve the request. Since PR #3, the agent never reduces several matches to 1 match:

  - `remove_file` lists the matches and asks for an id (R2). R5 gives the id.
  - `file_contents` refuses each match and lists what each record holds (R3).

- **The duplicate rule has known limits** (decision C):

  - The rule does not find some copies at all.
  - The agent can move an original into a folder that holds its copy under another name.

  [triage step 3](architecture.md#triage_folder-evidence-scored-filing) lists these limits with the rule. Since 23 Sept, the agent trusts no Keystone hash. Thus only TI7 reaches a hash + size + name match. TI7 plants trusted pairs with `extra_files` (offline only). The calibration mistake `unarchived` applies to no task, because the agent archives nothing.

- **The same-name rule moves at most 1 file, and asks about the rest.** The agent never moves 2 files with the same name into 1 folder. It moves only the single highest scorer. It escalates each other file as a possible copy. Each escalation names the other ids and sizes, so that a person can compare the files. If there is a tie, or if the folder already holds that name, the agent escalates all of the files.

  On live, the copies are out of scope, so the agent only lists them and does not escalate them.

- **The agent de-duplicates escalations by subject** (file id + filename). The check includes open and closed escalations. It compares only with the escalations of this seat (the server-set `created_by`). An escalation of another seat with the same subject never prevents the escalation of this seat. If a person renames a file, the agent can make a second escalation for it. No check has shown yet if the seat can list its own escalations on live (offline, it can).

- **Restore covers file fields only.** Sessions and escalations are permanent.

- **Not built:** The code does not have these features:

  - scheduled triage (A13)
  - a revision report for the whole drive (A5)
  - the resolution of names to parties (for example "which W-9 is current for J Miller Welding?")
  - the record of goals in the Office view (T3.5, staff question Q5).

- **Unused faults:** The code has the faults `foreign_change`, `drift_updated_at`, `missing_tool` and `swap_archived`, but no task uses them yet.

- **Decisions confirmed.** The task headers record these items as confirmed team decisions:

  - Decision A: the live write run writes to and escalates only the 9 allow-listed originals (TI2L header).
  - Decision B: the same-name rule (TI1, TI2 and TI3 headers).
  - The ambiguity rule of PR #3 (R2 and R3 headers): the agent refuses a shared filename. It never picks one silently.

  **Decision C** (4 Oct: the duplicate rule, [triage step 3](architecture.md#triage_folder-evidence-scored-filing)) is in the TI7 header. The TI1, TI2, TI2L and TI3 headers also have a note about it. The expectations of TI7 are an AI-drafted proposal for the team to check.

**Open with staff** ([6.6](plan-and-status.md#66-questions-for-staff)): All 8 questions still have no answer (27 Sept 2026). These questions change the code or the plan:

- Q1: After the live write run, does the team leave Incoming tidied, or does the team restore it?
- Q3: AI-assisted code.
- Q4: The code uses some REST: login, `/api/auth/me`, the Drive overview, and `/api/agent/office` during `harness capture`.
- Q5: the record of goals.
- Q7: `actor_kind`.
