# Start table creation with the question

Eshel's October 19 feedback describes difficulty building tables after an hour of use. This revision puts measurements first, makes the table structure directly editable, and keeps calculation choices visible.

## Sources

- Primary: Eshel Lev Or, October 19, 2026, 17:32 UTC, “Re: TOV - עדכון לדמו הטבלאות”, Gmail message `1a15538ca6847a63`, thread `1a0c994cd2916f23`. Yau supplied the same text on October 20. No attachments.
- Email check: October 13-20, Eden, Eshel and Lior individually. Eshel's thread contains the feedback. Eden's only result is a calendar acceptance. No messages from Lior.
- Background: `TOV  Rural Senses 22-9-26.webm`, modified September 22, 2026, 11:32 local time. This is the newest recording and is stale. Its earlier requests are already represented in main PR #1. The existing anonymous ivrit.ai transcript is used for context.
- Speaker inference from the September transcript: Speaker 1 is likely Lior (addressed at 05:29), Speaker 2 is likely Yau (drives the demo and is addressed at 06:55), Speaker 5 is likely Eshel (greeted at 05:18), Speaker 6 is likely Eden (joins at 17:36 and is addressed at 01:19:39). Speakers 3 and 4 cannot be assigned confidently. Labels remain anonymous in the source.

## Changes and decisions

All primary quotes below are from Eshel's October 19 email.

| # | Request and source quote | Result |
|---|---|---|
| 1 | Begin with the question: “מה אני רוצה לבדוק?” | Put measurements and common example tables first. Leave source selection accessible below, with selected sources visible beside the preview. |
| 2 | Sketch the table: “לשרטט או לבנות את מבנה הטבלה בצורה פשוטה” | Show editable row and column groups beside the live preview, including a useful empty structure before a measurement is chosen. |
| 3 | Simple and complex tables: “מספר נסקרים לפי קטגוריה, גיל ממוצע, שינוי בגודל השטח, מספר חקלאים לכל מדריך או הכנסה ממוצעת לפי אזור/גידול” | Provide examples using the existing dataset and a guided per-farmer change definition. Keep saved measurements and custom definitions available. Define each example's sources and summary explicitly. |
| 4 | “חישוב אחוז השינוי לוקח ממוצע כברירת מחדל” | Require a calculation basis when adding a new change column. Offer mean, median and sum. Preserve legacy tables' mean-based results and label the basis in tables and exports. Keep per-farmer change distinct from change between group summaries. |
| 5 | “צריך רפרנס נגיש למבנה השאלון, למשל קישור ל-raw data” | Add source-labelled raw-data access in the builder. Configured platform links open a new tab. A local read-only fallback restores the unsaved draft when returning. Raw data exposes the original column headings available in this demo. |
| 6 | “כדאי לשנות את השם Field ל-Group” and “יש בלבול בין Fields ל-Measurement” | Rename the builder's Fields list to Groups. Put numeric variables in Measurements by default. Keep numeric grouping as an explicit option for existing and expert use. Explain groups as the people compared and measurements as the values calculated. |
| 7 | “החלונית קטנה מאוד” and “לאפשר למזער את ה-dropdowns” | Use more of the viewport. Add collapsible measurement, group and source sections with persistent state. Keep the table workspace beside the selectors on desktop and stack it on narrow screens. |
| 8 | “drag & drop לרוחב בין Choose Rows, Choose Columns וה-Preview” | Allow moves between row and column controls and preview headers, including groups already selected. Add button alternatives, duplicate prevention and a three-level limit that rejects a move without losing its source. |
| 9 | AI table request: “אבל זה להמשך” | Deferred as explicitly requested. This includes interpreting the cereal-to-vegetable example from free text and deciding its baseline denominator. No simulated AI control. |
| 10 | “עוד סשן אחד מעמיק ורגוע” | Prepare a short task script for the next session. Scheduling remains deferred because participants and a time have not been agreed. |

## Design choice and assumptions

Working brief: programme staff with a reporting question → choose a measurement and comparison groups → see a real table before saving → use existing records and visible calculation settings → create or revise the table. The intended experience is calm and capable.

Three directions were considered: a sequential wizard, a free-form sketch canvas, and a question-led selector beside an editable table. The third keeps cause and effect visible and retains direct access for experienced users. A wizard adds backtracking when groups and measurements affect each other. A free-form canvas needs more placement rules. On mobile, the chosen layout becomes one column with a direct jump to the preview and button alternatives to dragging.

The October feedback supersedes September's sources-first order. September 22 at 18:26 describes the earlier sequence. Eshel's observed difficulty is stronger evidence for this revision than Eden's positive first impression at 54:47, which he explicitly gave before trying it himself.

The request does not specify a replacement for mean-based change. New change columns require a choice of mean, median or sum. Existing saved tables retain their calculation. The land-size example explicitly selects change in means and names it in the title. Per-farmer change remains a separate measurement, consistent with September 22 at 25:53-32:21. The guided definition starts with net income and lets users replace either input.

The officer example uses the actual “Officer Name” column. The source material does not establish that officers are instructors, so the example uses the source's terminology. Income uses plot net income and is labelled accordingly. Respondent examples count source records. Count-only tables switch to numeric summaries when a numeric measurement is chosen, avoiding an average of counts equal to 1. Numeric grouping remains available through “Group by individual numeric values”, including previously saved numeric groups.

## Next session task script

1. Build respondent counts by crop without guidance, then move crop from rows to columns.
2. Build average age by gender and explain the selected source and summary.
3. Build income by region, inspect raw data, and return to the same draft.
4. Build land-size change, then explain the difference between change in group means and the mean of individual changes.
5. Create a saved measurement and use it in a new table.

Observe completion, incorrect choices, backtracking and whether each person can explain the resulting number. These observations have yet to be collected.

## Verification and status

Eight product changes are implemented. AI generation and meeting scheduling are deferred. The task script above is ready for the proposed session.

- JavaScript syntax check passed.
- All 24 browser regressions passed: 15 existing checks and 9 new checks. Existing selectors were updated for the new layout while retaining their assertions.
- Verified all five example tables, empty-draft rejection, example undo, numeric grouping, search and collapse state, new custom measurements, save/reload, and CSV output.
- Dispatched HTML drag events against the row/column controls and actual preview headers. Verified cross-axis moves, keyboard alternatives, wrong-target rejection, and rejection of a fourth level without losing the original group.
- Checked change calculations against independent examples with unequal source coverage, zero denominators, missing values and legacy defaults.
- Verified configured raw-data link destinations using an intercepted browser request. Verified the local fallback and restoration of the draft and focus. Authenticated content on the external platform was not tested.
- Inspected desktop and narrow-screen screenshots. Keyboard and reduced-motion checks passed at 320px and 390px widths. No browser console or page errors occurred in the passing suite. Test storage was cleared after each case.
- The embedded dataset is byte-for-byte unchanged. `watch/`, the original clone's existing edits and its untracked `mockups/` are outside this change. Work is isolated on `feedback/2026-10-20-question-first`, based on current `origin/main` (`1c7333c`).
- Speech-to-text segments from the September recording were reused. Speaker separation completed on CUDA and produced six anonymous labels. A cuDNN library version mismatch required disabling cuDNN for that process while keeping CUDA enabled. The initial default CPU attempt was stopped. The completed refresh used the GPU. The inferred speaker mappings above still match the refreshed transcript.

Local review: http://localhost:8766/
