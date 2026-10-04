# Troubleshooting

This file holds these sections of the old README (before the split), word for word: 16.

---

## 16. Troubleshooting

| Symptom | Fix |
|---|---|
| `Login failed` / `No password configured` | check `AS_KEYSTONE_PASSWORD` in `.env` |
| `ANTHROPIC_API_KEY is not set` | add it to `.env`, or use `--model scripted` |
| `No fixture for keystone` | `python -m harness capture keystone` |
| `SKIPPED - Live writes need AS_ALLOW_WRITES=1` (from `harness run`) or `refused: Live writes need AS_ALLOW_WRITES=1` (from `harness restore`) | intended; set it in the shell for the one command (`.env` is ignored for it). See [The live write run](live-run.md#11-the-live-write-run) |
| ``refused: `ask --apply` writes only on the fake server`` | intended; live writes go through `harness run ... --live-apply` |
| `SKIPPED - ... runs offline only` | the task uses fake-server faults or extra files; run it with `--target fake` |
| `restore incomplete for [...]` | `AS_ALLOW_WRITES=1 python -m harness restore runs/<set>/<task>/snapshot-1.json --target live --live-apply` |
| `conflicts_left_alone` in a restore report | another team changed those fields during the run; restore left them as they are. Check them by hand |
| `pre-flight FAILED` (from `harness preflight`) or `Pre-flight failed; nothing was written` (in a `harness run` report) | the platform changed; read the listed problems, re-capture if expected. `… is not in the fixture (outside the allow-list, …)` or `… changed since the fixture … (outside the allow-list, …)` means a row in Incoming that the fixture doesn't know, or that changed: re-capture and re-check TI2L offline before any live write |
| `warnings (not blocking):` after `pre-flight OK` (from `harness preflight`), or `pre-flight warnings (not blocking):` during a live write run | intended: a row in Incoming outside the write allow-list, known to the fixture and unchanged, `… will not be written or escalated`. Since 23 Sept you should see **exactly 9**, one per copy (O5). A different number means Incoming changed: stop and re-capture |
| `… is new or changed since the fixture and is related to an allow-listed file (name, hash or document kind)`, `… is gone since the fixture and is related …`, or `… has left Incoming since the fixture` (pre-flight problem) | something on the platform changed that could change how the 9 are judged. Stop. Find out what changed and who changed it, re-capture (`python -m harness capture keystone`), re-derive TI2L's expectations and run it offline before trying again |
| `folder '…' (…) was renamed, moved or archived since the fixture`, `… is not in the fixture`, `… is gone since the fixture`, `… changed since the fixture (updated_at …)` or `N folders are named '…'` (pre-flight problem) | a folder changed. Triage files by folder name, so the plan may change. Find out who changed it (the problem names them when the platform records it), re-capture and re-check TI2L offline before any live write. A folder another team made for its own work blocks the run too |
| `SKIPPED - TI2 is not marked live_write = true …` | intended; TI2 is offline-only since 27 Sept. The live write task is TI2L |
| `left for a person: not in this run's scope` in a tidy answer | intended; the file is outside the run's write allow-list (live: the 9 copies of 23 Sept), so it was neither written nor escalated |
| `aborted: budget` / `aborted: max_turns` | raise `AS_MAX_MCP_CALLS` / `AS_MAX_USD` / `AS_MAX_TURNS` in `.env` |
| `SKIPPED - TI2L already ran live and may have sent writes (...)` | intended: live write tasks run once. Undo that run with `python -m harness restore`; move its folder out of `runs/` only if a second live run has been approved |
| `TI2L: an earlier attempt here sent no write; moved ... to .../attempt-<time>` | intended: that attempt stopped before sending anything (set-up, login, pre-flight, or a model error before the first write), so its files were kept aside and the run went ahead |
| `the fixture was captured at ..., not within the last 24 hours` (pre-flight problem) | re-capture right before the live run (`python -m harness capture keystone`), rehearse TI2L offline, then `python -m harness preflight` |
| `the description or read-only mark of a tool the agent uses changed since the fixture` (pre-flight problem) | the platform changed a tool the agent relies on; re-capture and re-check TI2L offline before any live write |
| `refused: no write journal at ...` (from `harness restore`) | restore needs the `writes-N.json` beside the snapshot. Only if it is truly lost, add `--no-journal` (then the rows this seat changed last are put back) |
| `warning: stale definition: ...` (from `harness rescore`) | a file in `harness/tasks` changed after this set was scored. Rescore still compares only what the run files decide; re-run the set to judge it against today's task file |
| `Another seat changed its <fields> at the same moment; check the file by hand.` in a tidy answer | another team changed fields we did not write while our write was in flight (no compare-and-set, see [14](known-limits.md#14-known-limits-and-open-questions)); our move landed, so check the file |
| `N possible secret(s) found` (from `scripts/secret_scan.py`) | open the named file at that line. If it is a real secret, remove it, rotate the secret, and tell the team; if it is a harmless example, add it to `ALLOWED` in the script |
