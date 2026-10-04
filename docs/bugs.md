# Bugs raised

This file holds these sections of the old README (before the split), word for word: 5.6.

---

### 5.6 Bugs raised

- **When and how.** The first 13 were filed on **22 Sept 2026** through `POST /api/bug-report`. Every filing returned HTTP 201 with `delivery: local`: the report was saved on the platform, with no GitHub issue. On 22 Sept every report had status **`new`**.
- **Checking them.** Use the MCP tool `BugReport.list` (or `BugReport.get` for the full text), or `GET /api/bug-report/mine`.
- **Don't file them again**, or you'll create duplicates.
- **Since then:** 32 more were filed on 24–25 Sept (second table). On 27 Sept 2026 (read live with `BugReport.list`) this seat had **45** reports (Keystone 31, Suryodaya 14), all still status `new`. Check `BugReport.list` before filing anything new.
- **On the class bug board:** 12 of the first 13 are listed as N179–N190 (for example F1 = N179, F2 = N180, F3 = N182, L8 = N185, F5 = N186); L3 duplicated Team 4's N144. Three of those fixes (N179, N180, N186) did not hold on 25 Sept and were re-filed as B20–B22.

| Id | Severity | Filed on | Bug | Report id | How the agent works around it |
|---|---|---|---|---|---|
| F1 🐞 | Major | Keystone (also seen on Suryodaya) | Notification shows other apps' records and other users' notifications | `32de63dc-278e-4b07-a156-472a8465397f` | never reads `Notification` |
| F2 🐞 | Major | Keystone (also seen on Suryodaya) | File list and search show document titles from apps you can't open | `14765361-120a-41b0-b73a-993a7745d9e4` | leak guard: the 83 e-sign rows become placeholders (`agent/privacy.py`; tasks C2, C3) |
| F3 🐞 | Major | Keystone | Keystone's Incoming files aren't Drive files, so Drive shows them as empty | `c3f8b9f4-3bad-4260-b108-bf0e8af70705` | reads `FileAttachment`; `drive_overview` explains why the Drive screen shows 15 while 30 files sit in folders (task C1; on 22 Sept it was 0 vs 15) |
| F4 🐞 | Major | Keystone | Export ignores misspelled filters and returns the whole table | `aa8bafc4-2bcb-499c-9fce-438a883a5811` | never uses `/api/export` |
| F5 🐞 | Major | Keystone | Global search stops at 5 results per type without saying so | `78ece447-9659-4b17-a67f-83232d3a0728` | never uses `/api/search`; pages the full list (`agent/safe_reads.py`) |
| L1 🐞 | Minor | **Suryodaya** | Suryodaya's menu shows apps the seat can't open | `c8589e53-a9e3-48a5-b7ba-0d2a61e3ec76` | no effect (the agent uses no menu) |
| L2 🐞 | Minor | Keystone | "Not equal" filters silently drop empty values | `2230cbcb-04bd-4ed3-8bda-2d3fbfe90f38` | the skills never send `ne:` (`list_all` in `agent/safe_reads.py` drops it); the model's own direct `.list` calls are passed through as they are |
| L3 🐞 | Minor | Keystone | An invalid sort order silently sorts ascending | `d7dfda01-12bc-4f8f-a285-55310d371eb7` | the skills never send a sort order; they sort in Python (the model's direct calls are not filtered) |
| L4 🐞 | Minor | Keystone | Summing a text field returns nonsense instead of an error | `95f30102-2d7c-46e4-87aa-8a165fb60cdc` | never uses `aggregate` |
| L5 🐞 | Minor | Keystone | A comma in a filter value silently becomes "A or B" | `d9ade348-2d8f-464e-85d3-81e5fc650d0c` | the skills never send a filter value with a comma; they filter in Python (the model's direct calls are not filtered) |
| L6 🐞 | Minor | Keystone | Records offer workflow actions you can't perform | `e085b62e-e5fb-4149-a5b0-de44e50fbffe` | never reads `_transitions`; checks `_permissions` instead |
| L7 🐞 | Note | Keystone (also seen on Suryodaya) | One API operation ID shared by four methods | `f66032c1-9d63-4f0e-a64d-f9f8dd6a02aa` | no effect (tools come from `tools/list`, not OpenAPI) |
| L8 🐞 | Minor | Keystone | The Drive access log is written by the browser, not the server | `b086167d-3ef6-4fe1-9cbf-42264e0869c1` | the uploader in the log is a lead, never proof (`uploader_of` in `agent/skills/common.py`) |

**Filed on 24–25 Sept 2026** (32 reports; numbered B1–B32 as in the gap report's list, which Tanmay compiled in PR #2). Severity is shown only where the report states one.

| Id | Severity | Business | Filed | Bug | Report id | How the agent works around it |
|---|---|---|---|---|---|---|
| B1 🐞 | — | Keystone (also Suryodaya) | 24 Sept | MCP list tools advertise filter defaults that return 0 rows | `192a52b8-3840-4a14-8c54-4d8cb0323cda` | the skills send only exact, comma-free filters plus `limit`/`offset` (`list_all` in `agent/safe_reads.py`); the model's own direct `.list` calls are passed through as they are |
| B2 🐞 | — | Keystone (also Suryodaya) | 24 Sept | Search treats `%` and `_` as wildcards | `43cbed22-69cc-4dc1-9284-cff64d2b8f1b` | the skills never send `search`; they filter names in code |
| B3 🐞 | — | Keystone (also Suryodaya) | 24 Sept | Every Drive revision download returns 409 | `d4517000-6e5e-4aab-b0a4-006457ae172d` | never downloads; `file_contents` refuses and lists what the record holds (R3) |
| B4 🐞 | — | **Suryodaya** (also Keystone) | 24 Sept | `content_hash` does not identify content | `8e468c1b-93c0-463e-9009-3d3b283aa573` | `find_duplicates` distrusts any hash shared by different names or sizes and never says "byte-verified" (DU1); triage never writes to a possible copy, even on a trusted hash, so a planted hash can't steer a move or an archive (decision C, TI7) |
| B5 🐞 | — | **Suryodaya** (also Keystone) | 24 Sept | Unparseable filter values return 0 instead of 400 | `6ea99771-3c95-4c53-8651-56d5caf4877e` | `list_all` never sends `gt:`, `lt:` or `ne:` values |
| B6 🐞 | — | Keystone (also Suryodaya) | 24 Sept | Date-only filters compared as text against timestamps | `6b23e10f-115d-4d1a-801a-e749a464f20d` | never sends a date filter |
| B7 🐞 | — | **Suryodaya** (also Keystone) | 24 Sept | API agent sessions recorded as anonymous | `828f5def-114e-407b-b8a9-318e2a0cd66a` | sessions carry the `actor_label` "Files Agent (team20)" (A7) |
| B8 🐞 | — | **Suryodaya** (also Keystone) | 24 Sept | AgentProvider accepts out-of-range settings, with two defaults | `41c1dbf3-abbe-4a46-98f8-c37c45be0a2f` | not used (the agent calls its model directly) |
| B9 🐞 | — | **Suryodaya** (also Keystone) | 24 Sept | MCP enums omit values the server writes | `174a5bb4-15ff-483c-adce-1ad166bdf391` | no effect: the agent never filters on those status values |
| B10 🐞 | — | Keystone | 24 Sept | Keystone AccountPlan rows missing their required links | `aa2a5403-552a-4356-b2e8-ffad8f97bd59` | not used |
| B11 🐞 | — | **Suryodaya** | 24 Sept | Scheduled tasks count runs that produce nothing | `46a4c0e6-bccc-4f4d-aa3a-cf6964dcfff7` | not used (scheduled triage is not built, A13) |
| B12 🐞 | — | **Suryodaya** | 24 Sept | AgentTask schedules not validated | `cd16012b-ca54-435e-8fa3-bf89516f6a80` | not used (A13) |
| B13 🐞 | — | **Suryodaya** (also Keystone) | 24 Sept | SalesOrder.list advertises computed totals as filters, then refuses them | `d001977c-ad30-47f3-b7e7-95a6a5c41a97` | not used |
| B14 🐞 | High | **Suryodaya** | 24 Sept | Agent daily token counter never resets | `a1ae4a9b-1005-41a9-a4a8-ce3921f0008a` | not used (the agent is not a platform persona) |
| B15 🐞 | Medium | Keystone | 24 Sept | Job ledger and mission control tools show jobs the seat's AgentJob access refuses | `5abc24c7-d5c2-459a-b94e-269de65247c8` | not used |
| B16 🐞 | Low | Keystone | 24 Sept | `tools.search` tags most Drive tools as module `core` | `75f45f3a-7ad1-4582-9aee-04ae1f1406d5` | the skills find their tools by exact name from `tools/list` (`agent/catalog.py`, `agent/config.py`) |
| B17 🐞 | Low | **Suryodaya** | 24 Sept | Suryodaya people directory lists companies as employees | `ac4fb1ea-f6fb-404f-a3ed-34d4836c6dd1` | not used (A9) |
| B18 🐞 | High | Keystone | 25 Sept | The Keystone Drive repair (N182 fix) duplicated all 15 scenario files as bare copies | `f6d1dfdc-1e9a-4ddd-8e71-aa5b507c769c` | pre-flight warns about the 9 Incoming copies; the live run neither writes nor escalates them (scope rule); two same-named files are never filed into one folder (same-name rule). See the note at the top of section 5 |
| B19 🐞 | Medium | Keystone | 25 Sept | The same repair re-wrote five Drive access-log events with 23 Sep dates | `7545038f-15fb-411d-a121-468d748e6014` | the uploader from the log is a lead, never proof (as L8) |
| B20 🐞 | High | Keystone | 25 Sept | N180 not in effect: e-sign attachments still listed, titled and writable | `bba655a6-6f2b-435e-a3b2-d5023fb6a5c3` | leak guard, as F2. "Writable" means the rows declare `_permissions.write = true`; no write was attempted |
| B21 🐞 | Medium | Keystone | 25 Sept | N179 not in effect on Keystone: other people's notifications visible | `ca64133f-2bd7-4c01-8586-19f7c1ee6a39` | never reads `Notification`, as F1 |
| B22 🐞 | Low | Keystone | 25 Sept | Global search still 5 per type; `limit` and `offset` ignored (N186 partial) | `46ace9e3-04d5-45f0-bb55-20d2b93067a4` | never uses `/api/search`, as F5 |
| B23 🐞 | Low | **Suryodaya** | 25 Sept | Suryodaya storefront publishes a ₹0 "test" product | `00ce75cd-167b-49a1-9945-b9738df17cbe` | not used |
| B24 🐞 | Low | Keystone | 25 Sept | `endpoint.inventory.shipping_board` offered to seats that can never use it | `25071f1a-94a2-4dcd-b7e2-d301a634603a` | not used |
| B25 🐞 | — | Keystone | 25 Sept | Keystone goals: company-wide goals stay at 0, and "new opportunities" counts deals by close date | `cd791408-ac3d-4e71-9e8a-7370086da7eb` | not used |
| B26 🐞 | — | Keystone | 25 Sept | Keystone account plans: the endpoint says no read permission, while REST and MCP return all 20 | `02923400-876c-409d-a640-4d38ff69e00b` | not used |
| B27 🐞 | Medium | Keystone | 25 Sept | `endpoint.make.orders` never marks a line late | `a454db2e-6357-4ce4-a19b-bb7688d77ff7` | not used |
| B28 🐞 | Low | Keystone | 25 Sept | `endpoint.make.orders` stops at 200 rows with no paging | `e08e6517-0da3-4551-b714-1ae8f94c3604` | not used |
| B29 🐞 | Medium | Keystone | 25 Sept | `endpoint.manufacturing.demand_forecast` drops overdue open orders | `26876a42-ed44-4757-a704-3502276b78ed` | not used |
| B30 🐞 | Medium | **Suryodaya** | 25 Sept | `endpoint.mission_control.staffing_forecast` measures service time on instantly failed jobs | `68adc788-edc3-4817-8721-de9419075ff1` | not used |
| B31 🐞 | Low | **Suryodaya** | 25 Sept | `supplier_scorecard` reports "insufficient history" and zero orders when it was denied the data | `c45fdf5e-03f7-41de-bf25-5a5ebe08e26b` | not used |
| B32 🐞 | Low | Keystone | 25 Sept | Keystone access log records a share of J-BRKT-04 Rev C that exists nowhere | `372c34f5-c6df-49f4-afdb-6e5f864ee5e6` | `find_drawing` never reads shares; the log is a lead, never proof |

**Found but not raised**

*Suspected, untested.* Each needs a write to prove, so none was tried:
- the built-in chat agent bypassing the app gate;
- `/api/agent/chat` accepting a caller-supplied `tool_policy_id`;
- the "writable" e-sign attachments in F2 and B20 (the rows declare `_permissions.write = true`; no write was attempted);
- **new:** `AgentSession.create` accepts client-set `actor_kind`, `actor_user_id`, `actor_label`, `actor_roles` and `tool_policy_id`. The 22 Sept tool schema lists all five. Staff question Q7 asks whether to report it. Our agent sets only `title` and `actor_label`, plus `actor_kind` if you set `AS_ACTOR_KIND`.

*Filed later after all:* every Drive revision download returns `409 Revision bytes are unavailable` (B3, 24 Sept). It may still be on purpose (seed data without file bytes).

*Checked, and not raised because staff would likely reject them:*

| Finding | Why not |
|---|---|
| The storage overview showed 0 files on Keystone (22 Sept; since 23 Sept it counts only the 15 bare copies) | A symptom of F3, already covered |
| MCP gives the same error for forbidden and nonexistent tools | The brief documents this as intended |
| 7 entities say "Generic reads are disabled" | A 403 on another app's data is on the brief's known list |
| Share tokens and password hashes can be used as filters | 0 shares exist on either business, so nothing can be shown |
| No ETag / `If-Match` on updates | A missing feature, not a defect; it is platform request P6 |
| Shared, writable agent memory and session rows | Close to the brief's known "shared book" item |
| The access log disagrees with the share list | Seeded rows, not a system defect (a share of J-BRKT-04 Rev C that exists nowhere was filed later, 25 Sept, as B32) |
