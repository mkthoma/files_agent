# Bugs raised

This file holds these sections of the old README (before the split): 5.6. The ids, code, numbers and dates are from the old README. [The docs index](README.md#corrections-after-the-split) lists the facts that changed.

---

### 5.6 Bugs raised

- **When and how.** The first 13 reports went to the platform on **22 Sept 2026** through `POST /api/bug-report`. Each request returned HTTP 201 with `delivery: local`. This value means that the platform saved the report and did not open a GitHub issue. On 22 Sept, each report had the status **`new`**.
- **How to check them.** Use the MCP tool `BugReport.list` or `GET /api/bug-report/mine`. For the full text of a report, use `BugReport.get`.
- **Do not submit them again.** Another report of the same bug is a duplicate.
- **Since then:** On 24–25 Sept, 32 more reports went to the platform (see the second table). On 27 Sept 2026, a live read with `BugReport.list` showed **45** reports for this seat (Keystone 31, Suryodaya 14). The status of all 45 was still `new`. Before you submit a new report, check `BugReport.list`.
- **On the class bug board:** The board shows 12 of the first 13 bugs as N179–N190. For example: F1 = N179, F2 = N180, F3 = N182, L8 = N185, F5 = N186. L3 was the same bug as N144 from Team 4. On 25 Sept, 3 of those fixes (N179, N180, N186) did not work. B20–B22 are the new reports for these 3 bugs.

| Id | Severity | Submitted on | Bug | Report id | How the agent avoids it |
|---|---|---|---|---|---|
| F1 🐞 | Major | Keystone (also seen on Suryodaya) | Notification shows records from other apps and notifications for other users. | `32de63dc-278e-4b07-a156-472a8465397f` | The agent never reads `Notification`. |
| F2 🐞 | Major | Keystone (also seen on Suryodaya) | The file list and the search show document titles from apps that you cannot open. | `14765361-120a-41b0-b73a-993a7745d9e4` | A leak guard changes the 83 e-sign rows into placeholders (`agent/privacy.py`, tasks C2 and C3). |
| F3 🐞 | Major | Keystone | The Incoming files of Keystone are not Drive files, so Drive shows them as empty. | `c3f8b9f4-3bad-4260-b108-bf0e8af70705` | The agent reads `FileAttachment`. `drive_overview` gives the reason why the Drive screen shows 15 files while 30 files are in folders (task C1). On 22 Sept, the numbers were 0 and 15. |
| F4 🐞 | Major | Keystone | Export ignores misspelled filters and returns the whole table. | `aa8bafc4-2bcb-499c-9fce-438a883a5811` | The agent never uses `/api/export`. |
| F5 🐞 | Major | Keystone | Global search stops at 5 results for each type and does not tell you. | `78ece447-9659-4b17-a67f-83232d3a0728` | The agent never uses `/api/search`. It reads all pages of the full list (`agent/safe_reads.py`). |
| L1 🐞 | Minor | **Suryodaya** | The Suryodaya menu shows apps that the seat cannot open. | `c8589e53-a9e3-48a5-b7ba-0d2a61e3ec76` | No effect. The agent uses no menu. |
| L2 🐞 | Minor | Keystone | "Not equal" filters drop empty values and give no warning. | `2230cbcb-04bd-4ed3-8bda-2d3fbfe90f38` | The skills never send `ne:` (`list_all` in `agent/safe_reads.py` removes it). The agent sends the filter values of the direct calls of the model unchanged. For 4 list tools, it refuses a filter name outside `MODEL_FILTERS` (`agent/loop.py`). |
| L3 🐞 | Minor | Keystone | An invalid sort order sorts from low to high and gives no warning. | `d7dfda01-12bc-4f8f-a285-55310d371eb7` | The skills never send a sort order. They sort in Python. The agent sends the filter values and the sort order of the direct calls of the model unchanged. For 4 list tools, it refuses a filter name outside `MODEL_FILTERS` (`agent/loop.py`). |
| L4 🐞 | Minor | Keystone | The sum of a text field gives a meaningless result, not an error. | `95f30102-2d7c-46e4-87aa-8a165fb60cdc` | The agent never uses `aggregate`. |
| L5 🐞 | Minor | Keystone | A comma in a filter value changes the filter to "A or B" and gives no warning. | `d9ade348-2d8f-464e-85d3-81e5fc650d0c` | The skills never send a filter value that has a comma. They filter in Python. The agent sends the filter values of the direct calls of the model unchanged. For 4 list tools, it refuses a filter name outside `MODEL_FILTERS` (`agent/loop.py`). |
| L6 🐞 | Minor | Keystone | Records show workflow actions that you cannot do. | `e085b62e-e5fb-4149-a5b0-de44e50fbffe` | The agent never reads `_transitions`. It checks `_permissions` instead. |
| L7 🐞 | Note | Keystone (also seen on Suryodaya) | 4 methods use the same API operation ID. | `f66032c1-9d63-4f0e-a64d-f9f8dd6a02aa` | No effect. The tools come from `tools/list`, not from OpenAPI. |
| L8 🐞 | Minor | Keystone | The browser writes the Drive access log, not the server. | `b086167d-3ef6-4fe1-9cbf-42264e0869c1` | The agent uses the uploader in the log as a lead, never as proof (`upload_lead` in `agent/skills/common.py`). |

**Submitted on 24–25 Sept 2026** (32 reports). The numbers B1–B32 are the same as in the list of the gap report. Tanmay made that list in PR #2. The table shows a severity only where the report gives one.

| Id | Severity | Business | Submitted | Bug | Report id | How the agent avoids it |
|---|---|---|---|---|---|---|
| B1 🐞 | — | Keystone (also Suryodaya) | 24 Sept | MCP list tools declare filter defaults that return 0 rows. | `192a52b8-3840-4a14-8c54-4d8cb0323cda` | The skills send only exact filters without commas, plus `limit`/`offset` (`list_all` in `agent/safe_reads.py`). The agent sends the filter values of the direct calls of the model unchanged. For 4 list tools, it refuses a filter name outside `MODEL_FILTERS` (`agent/loop.py`). |
| B2 🐞 | — | Keystone (also Suryodaya) | 24 Sept | Search treats `%` and `_` as wildcards. | `43cbed22-69cc-4dc1-9284-cff64d2b8f1b` | The skills never send `search`. They filter names in code. |
| B3 🐞 | — | Keystone (also Suryodaya) | 24 Sept | Every Drive revision download returns 409. | `d4517000-6e5e-4aab-b0a4-006457ae172d` | The agent never downloads. `file_contents` refuses and lists what the record holds (R3). |
| B4 🐞 | — | **Suryodaya** (also Keystone) | 24 Sept | `content_hash` does not identify content. | `8e468c1b-93c0-463e-9009-3d3b283aa573` | `find_duplicates` does not trust a hash that files with different names or sizes share. It never says "byte-verified" (DU1). Triage never writes to a possible copy, even with a trusted hash. Thus, a planted hash cannot cause a move or an archive (decision C, TI7). |
| B5 🐞 | — | **Suryodaya** (also Keystone) | 24 Sept | Filter values that the server cannot parse return 0, not 400. | `6ea99771-3c95-4c53-8651-56d5caf4877e` | `list_all` never sends `gt:`, `lt:` or `ne:` values. |
| B6 🐞 | — | Keystone (also Suryodaya) | 24 Sept | The server compares date-only filters as text against timestamps. | `6b23e10f-115d-4d1a-801a-e749a464f20d` | The agent never sends a date filter. |
| B7 🐞 | — | **Suryodaya** (also Keystone) | 24 Sept | The platform records API agent sessions as anonymous. | `828f5def-114e-407b-b8a9-318e2a0cd66a` | The agent sessions have the `actor_label` "Files Agent (team20)" (A7). |
| B8 🐞 | — | **Suryodaya** (also Keystone) | 24 Sept | AgentProvider accepts out-of-range settings, with 2 defaults. | `41c1dbf3-abbe-4a46-98f8-c37c45be0a2f` | The agent does not use it. The agent calls its model directly. |
| B9 🐞 | — | **Suryodaya** (also Keystone) | 24 Sept | MCP enums do not include some values that the server writes. | `174a5bb4-15ff-483c-adce-1ad166bdf391` | No effect. The agent never filters on those status values. |
| B10 🐞 | — | Keystone | 24 Sept | Keystone AccountPlan rows do not have their required links. | `aa2a5403-552a-4356-b2e8-ffad8f97bd59` | The agent does not use it. |
| B11 🐞 | — | **Suryodaya** | 24 Sept | Scheduled tasks count runs that produce nothing. | `46a4c0e6-bccc-4f4d-aa3a-cf6964dcfff7` | The agent does not use it. The agent has no scheduled triage (A13). |
| B12 🐞 | — | **Suryodaya** | 24 Sept | The platform does not validate AgentTask schedules. | `cd16012b-ca54-435e-8fa3-bf89516f6a80` | The agent does not use it (A13). |
| B13 🐞 | — | **Suryodaya** (also Keystone) | 24 Sept | SalesOrder.list declares computed totals as filters, but then refuses them. | `d001977c-ad30-47f3-b7e7-95a6a5c41a97` | The agent does not use it. |
| B14 🐞 | High | **Suryodaya** | 24 Sept | The daily token counter of an agent never resets. | `a1ae4a9b-1005-41a9-a4a8-ce3921f0008a` | The agent does not use it. The agent is not a platform persona. |
| B15 🐞 | Medium | Keystone | 24 Sept | The job ledger and the mission control tools show jobs that the seat's AgentJob access refuses. | `5abc24c7-d5c2-459a-b94e-269de65247c8` | The agent does not use it. |
| B16 🐞 | Low | Keystone | 24 Sept | `tools.search` tags most Drive tools as module `core`. | `75f45f3a-7ad1-4582-9aee-04ae1f1406d5` | The skills find their tools by exact name from `tools/list` (`agent/catalog.py`, `agent/config.py`). |
| B17 🐞 | Low | **Suryodaya** | 24 Sept | The Suryodaya people directory shows companies as employees. | `ac4fb1ea-f6fb-404f-a3ed-34d4836c6dd1` | The agent does not use it (A9). |
| B18 🐞 | High | Keystone | 25 Sept | The Keystone Drive repair (the N182 fix) made bare copies of all 15 scenario files. | `f6d1dfdc-1e9a-4ddd-8e71-aa5b507c769c` | Pre-flight warns about the 9 Incoming copies. The live write run does not write or escalate them (scope rule). Triage never moves 2 files that have the same name into 1 folder (same-name rule). See the note at the top of section 5 (in [background.md](background.md#5-background-the-platform-the-scenario-and-the-research)). |
| B19 🐞 | Medium | Keystone | 25 Sept | The same repair wrote 5 events in the Drive access log again, with 23 Sep dates. | `7545038f-15fb-411d-a121-468d748e6014` | The agent uses the uploader from the log as a lead, never as proof (as for L8). |
| B20 🐞 | High | Keystone | 25 Sept | N180 is not in effect. E-sign attachments still show in lists, with their titles, and they are writable. | `bba655a6-6f2b-435e-a3b2-d5023fb6a5c3` | The agent uses the leak guard, as for F2. "Writable" means that the rows declare `_permissions.write = true`. No check tried a write. |
| B21 🐞 | Medium | Keystone | 25 Sept | N179 is not in effect on Keystone. The notifications of other people are visible. | `ca64133f-2bd7-4c01-8586-19f7c1ee6a39` | The agent never reads `Notification`, as for F1. |
| B22 🐞 | Low | Keystone | 25 Sept | Global search still gives 5 results for each type. It ignores `limit` and `offset` (the N186 fix is partial). | `46ace9e3-04d5-45f0-bb55-20d2b93067a4` | The agent never uses `/api/search`, as for F5. |
| B23 🐞 | Low | **Suryodaya** | 25 Sept | The Suryodaya storefront publishes a ₹0 "test" product. | `00ce75cd-167b-49a1-9945-b9738df17cbe` | The agent does not use it. |
| B24 🐞 | Low | Keystone | 25 Sept | The platform offers `endpoint.inventory.shipping_board` to seats that can never use it. | `25071f1a-94a2-4dcd-b7e2-d301a634603a` | The agent does not use it. |
| B25 🐞 | — | Keystone | 25 Sept | Keystone goals: company-wide goals stay at 0, and "new opportunities" counts deals by close date. | `cd791408-ac3d-4e71-9e8a-7370086da7eb` | The agent does not use it. |
| B26 🐞 | — | Keystone | 25 Sept | Keystone account plans: the endpoint says that there is no read permission, but REST and MCP return all 20. | `02923400-876c-409d-a640-4d38ff69e00b` | The agent does not use it. |
| B27 🐞 | Medium | Keystone | 25 Sept | `endpoint.make.orders` never marks a line as late. | `a454db2e-6357-4ce4-a19b-bb7688d77ff7` | The agent does not use it. |
| B28 🐞 | Low | Keystone | 25 Sept | `endpoint.make.orders` stops at 200 rows and does not give more pages. | `e08e6517-0da3-4551-b714-1ae8f94c3604` | The agent does not use it. |
| B29 🐞 | Medium | Keystone | 25 Sept | `endpoint.manufacturing.demand_forecast` does not include overdue open orders. | `26876a42-ed44-4757-a704-3502276b78ed` | The agent does not use it. |
| B30 🐞 | Medium | **Suryodaya** | 25 Sept | `endpoint.mission_control.staffing_forecast` measures service time on jobs that failed immediately. | `68adc788-edc3-4817-8721-de9419075ff1` | The agent does not use it. |
| B31 🐞 | Low | **Suryodaya** | 25 Sept | `supplier_scorecard` reports "insufficient history" and 0 orders when the platform did not give it the data. | `c45fdf5e-03f7-41de-bf25-5a5ebe08e26b` | The agent does not use it. |
| B32 🐞 | Low | Keystone | 25 Sept | The Keystone access log records a share of J-BRKT-04 Rev C that does not exist. | `372c34f5-c6df-49f4-afdb-6e5f864ee5e6` | `find_drawing` never reads shares. The log is a lead, never proof. |

**Found but not raised**

*Suspected, untested.* Each one needs a write as proof, so no check tried any of them:
- The built-in chat agent bypasses the app gate.
- `/api/agent/chat` accepts a `tool_policy_id` from the caller.
- The e-sign attachments in F2 and B20 are "writable". The rows declare `_permissions.write = true`. No check tried a write.
- **new:** `AgentSession.create` lets the client set `actor_kind`, `actor_user_id`, `actor_label`, `actor_roles` and `tool_policy_id`. The 22 Sept tool schema lists all 5. Staff question Q7 asks whether to report it. This agent sets only `title` and `actor_label`. It also sets `actor_kind` if you set `AS_ACTOR_KIND`.

*Raised later:* Every Drive revision download returns `409 Revision bytes are unavailable` (B3, 24 Sept). Possibly, this is still intentional (seed data without file bytes).

*Checked, but not raised, because staff would probably reject them:*

| Finding | Why not |
|---|---|
| The storage overview showed 0 files on Keystone (22 Sept). Since 23 Sept, it counts only the 15 bare copies. | This is a symptom of F3. F3 already covers it. |
| MCP gives the same error for forbidden tools and for tools that do not exist. | The brief documents this as intended behaviour. |
| 7 entities say "Generic reads are disabled". | A 403 on the data of another app is on the known list in the brief. |
| You can use share tokens and password hashes as filters. | There are 0 shares on each business, so there is nothing to show. |
| No ETag / `If-Match` on updates | This is a feature gap, not a defect. It is platform request P6. |
| Agent memory rows and session rows: shared and writable. | This is close to the known "shared book" item in the brief. |
| The access log disagrees with the share list. | The seed data made these rows. This is not a system defect. Later, on 25 Sept, B32 reported a share of J-BRKT-04 Rev C that does not exist. |
