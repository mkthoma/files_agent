# The official server run (Release 8.1)

Since Release 8.1 (9 Oct 2026), the course grades the harness on the AgentSwitch server:
**Our harness → Submit for a run**. The server checks out the exact commit on the saved
branch, runs it against a **fresh copy** of the instance, throws the writes away afterwards,
and shows pass/fail per task. One run per team every 3 days, so rehearse first.

## What the server provides

No passwords, no `.env`, no own keys. The runner sets:

| Variable | Use in this repo |
|---|---|
| `AGENTSWITCH_BASE_URL` | overrides the instance URL (`get_settings` in `agent/config.py`) |
| `AGENTSWITCH_TOKEN` | a ready bearer token: `TokenSession` in `agent/auth.py` uses it instead of a login; a 401 is fatal because the token cannot be refreshed |
| `AGENTSWITCH_INSTANCE` | `keystone` (Seat 20's scenario data exists only there; `agentswitch-harness.toml` lists only keystone) |
| `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `OPENAI_MODEL` | the platform model. `OpenAICompatModel` in `agent/model.py` speaks the OpenAI chat-completions API over plain HTTPS — still standard library only, no SDK |

## What `python -m harness official` does

1. **Captures a fresh fixture** from the instance copy (read-only), so pre-flight's
   "fixture older than 24 hours" rule cannot block the write task.
2. **Runs every live-safe task once** with the platform model: the read-mode tasks without
   fake-server faults or planted files, plus **TI2L**, the one `live_write = true` task.
   Nothing is weakened: the write guard, the 9-id allow-list, pre-flight, snapshot, the
   write journal and restore all run exactly as in a live write run. The only switch this
   command flips is `AS_ALLOW_WRITES=1`, inside its own process, because the server copy
   is disposable by design.
3. **Writes `results.json`** in the runner's format (id, title, passed, score, evidence),
   checked against that format before writing. Evidence states that pass/fail comes from
   the database state after the run, or quotes the verifier's failure reasons.

The offline-only tasks (fault injection, planted files, the 18-file TI2/TI3 variants)
stay out **by design**: their faults need the fake server. They are graded by the offline
`pass^5` evidence, not by the official run.

## Rehearse before submitting (the run quota is 1 per 3 days)

- Offline, no keys, no network: `python -m harness official --dry-run`
  (fake server + scripted model; 12 of 12 tasks passed on 9 Oct 2026, `results.json` valid).
- Against the real platform with your own token: export `AGENTSWITCH_BASE_URL`,
  `AGENTSWITCH_TOKEN` (from a normal login) and any OpenAI-compatible model endpoint,
  then run `python -m harness official`.

## Before the first submission (checklist)

1. Merge this branch and **save the repo + branch in "Our harness"** on the platform.
2. `python -m harness official --dry-run` passes on the saved commit.
3. `python -m unittest discover -s tests` and `python -m harness smoke` pass.
4. Expect drift: the fresh copy is seeded by the course, and the platform data changed
   mid-course once already (23 Sept). Treat the first run partly as reconnaissance; the
   per-task evidence in the panel says exactly which expectation disagreed.
