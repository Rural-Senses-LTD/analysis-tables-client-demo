# Table changes from the 3 November 2026 TOV call

**Sources**
- Call: "TOV<>RS", 3 Nov 2026, 14:00 IST (1:04:28). Video from the calendar invite, saved as
  `Meeting recordings and Transcript\2026-11-03 TOV meeting.mp4`. Transcript:
  `2026-11-03 TOV meeting.he.speakers.txt` (ivrit.ai, GPU).
- Speakers (inferred, the transcript labels are anonymous): Speaker 2 = Eshel (shares the screen and
  builds the tables; mentions their donors); Speaker 3 = Yau (explains the design; "אני אכתוב לעצמי
  לאחד שאלות"). Speaker 1 says only "כן" / "סבבה". Eden was not on the call: Meet lists Eshel twice
  and Yau, and Eshel says "ונקווה שעדן גם יהיה" for next week. Speaker 1 is most likely Eshel's
  second device.
- Screen: Eshel shares the demo from 01:13 to 44:40. After that it is camera only, so items from
  44:40 on have no screen reference.
- Email, 28 Oct to 4 Nov: only scheduling. Eshel asked for the updated link before the call
  (1 Nov); Yau sent it the same day. No product feedback.

**Already done during the call** (merged 3 Nov, 14:02–15:23 IST): Variety back in Groups (#10),
sticky headers in full screen only (#11, #13), table name above the preview (#12), Woreda back in
Groups (#14).

## Built in this pass (9 items)

| # | What's asked | Source | On screen | Plan |
|---|---|---|---|---|
| 1 | Move Variety from Baseline to Endline | Yau 57:43 "השינוי העיקרי פה זה צריך להעביר את ה-Variety ל-endline"; Eshel 57:53 "בבייסלין, לדעתי, אין להם וראטי"; agreed 01:00:06–01:00:10 "נחבר אותו לאנדליין" | 19:36–20:35: Variety by Irrigation Type shows numbers under Baseline as well as Endline | Done. Eshel's `project & variety.xlsx` is now joined to Endline Farmer Name (it was joined to Baseline Name on 22 Oct). 236 of 241 Endline farmers now have a variety; on Baseline it was 208 of 254. Baseline no longer has Variety. Project stays as it was, since Endline has its own. |
| 2 | Irrigation Method (Baseline) and Irrigation Type (Endline) are the same question, so make them one | Yau 06:33 "אני אכתוב לעצמי לאחד שאלות"; recap 56:59 "זה בעצם אותה שאלה בניסוח שונה... מאחד אותם" | 06:52: Irrigation Method and Irrigation Type side by side, a Blank row under Endline; 10:04: Irrigation Type shows only Blank for Baseline | Done. Both now map to one "Irrigation Type" question; Baseline Name and Endline Farmer Name are also one question now, the only other pair worded differently. Saved tables that used the old questions are updated when they load, so nobody loses a table. |
| 3 | A way to close the left panel so the preview has room | Eshel 18:43 "לסגור את החלונית. סתם הערה קטנה"; Yau 18:56 "אפשרות לסגור את הפאנל"; again 23:39 "החלונית מסתירה לי" and 41:04 "החלונית הסתירה לי" (Yau: "כל החלונית אשמה היום") | Eshel's browser is about 960 px wide (22:55 "אני עם המסך של... עמית"). The left panel takes about a third of it, and the preview cuts off at Galilea 39 (22:43). | Done. "Hide settings" above the preview gives it the full width; "Show settings" brings the panel back with nothing lost. On a phone the panels stack, so the button isn't shown. |
| 4 | Find a group by typing an answer, e.g. "Galilea" | Eshel 39:22 "אני לא יודע שהשאלה הייתה ורעייתי, אבל אני יודע שגלילאה... אפשר לו לרשום פה גלילאה?"; Yau 39:47 "כן, לגמרי אפשרי" | 39:02: "+ Row" search for "wa" returns "No matching groups." | Done, in both group searches. Typing "galilea" lists Variety with "Has “Galilea 39”". If that group is already in the table, the search says so: "“Galilea 39” is an answer in Variety, which is already in your table." |
| 5 | The chart legend repeats itself and is too busy | Eshel 35:17 "יש פה too much information", 35:33 "זה מופיע פעמיים"; Yau 36:13 "משהו פה מבלבל קצת בלג'נד"; Yau 51:48 "ללייבלינג שם, שהם התערבבו"; recap 56:24 "הגרפים, לסדר אותם" | 35:33: every series is "Tomato · Gabi · Combined sources mean", once in the legend and again under every bar group with its N | Done. Parts every series shares are shown once above the chart ("All bars: Tomato · Combined sources mean"), and the legend keeps only what tells the series apart (Gabi, Galilea 39). Under the bars, each N has a colour dot that matches the legend. Default colours now follow the chosen series, so no two series share a colour; before, two could both be green. |
| 6 | Unhiding a column is hard to find, and a menu stays open | Eshel 26:31 "אני לא יודע איפה ה-unhide"; 27:03 "גם יש טיפה באג... משאיר אותו לחוץ" | 27:03: the column menu (Merge columns / Hide columns) stays open while the table ⋮ menu is open. The only way back is a plain "1 hidden groups" label. | Done. Opening a menu closes any other open menu, and a click outside closes it. Hidden columns are now behind a "Show 1 hidden group" button, and the table ⋮ menu has "Show hidden groups (1)" while any are hidden. |
| 7 | Dragging a header in the preview seems to pick up the whole header block | Eshel 22:27 "זה קצת מבלבל, כי... הוא תופס לי את כל ה-yield"; 25:28 "הגרירה האינטואטיבית היא לא של כל הקומפלקס"; Yau 25:38 "שתוכל לגרור רק את הגרור הרלוונטי" | 22:36: during the drag the whole column header area turns green | Done. The drag shows a chip with the group's name ("Variety"), that group's cells fade while it moves, and only the column-group headers light up; the Yield row under them no longer does. Medium confidence that this is the complaint Eshel meant; worth asking on the next call. |
| 8 | A colour bug in the preview header: "the Blank is in the irrigation colour" | Eshel 25:42 "יש פה בג טיפה בצבע. ה-blank הוא בצבע של ה... irrigation"; Yau 44:50 "הבאגים הזה בצבע" | 25:42: Banana / Blank, the first column header, has the lighter background of the Irrigation Type corner; the others are green | Done. Reproduced: the first column-group header in each header row took the corner cell's paler colour, in the preview and in saved tables. It now matches the other headers. |
| 9 | Picking Yield removed "Number of respondents" without saying why | Eshel 15:39 "למה זה הוריד לי אותו?"; Yau 15:39 "אקאונט יכול לבוא רק לבד"; Eshel 15:43 "למשתמש החדש..."; Yau 15:55 "מבלבל" | 15:39: the reason is only in small grey text: "Count-only table, replaces numeric measurements" | Done. A message now says what happened: "Number of respondents was removed. A table shows either counts or measurements." Choosing Number of respondents says which measurements it replaced. |

## Not in this pass

| What | Source | Why not now |
|---|---|---|
| Show which questionnaire each question comes from | Eshel 10:04, 17:37 "להוסיף אינדיקציה למאיזה שאלון הוא מגיע" | Yau 17:55: a question can appear in seven questionnaires; Eshel 17:58 "תשובה טובה. זה סבבה". Yau again at 57:17: "זה לא באג, זה פיצ'ר". Item 2 also removes the case that caused the confusion. |
| Stop people picking a group whose source isn't selected | Eshel 09:36 "טעות לוגית שאולי צריך לא לאפשר" | Yau 10:00: "יכול להיות שאתה צודק", so not agreed. The group already says "Select its source or remove this group" (19:36), and item 2 removes the Irrigation Method case. |
| Filters inside table creation | Eshel 41:32 "אולי שווה להכניס גם פה פילטר"; 55:01 | Yau 55:38: tables are created rarely, filters are used all the time; Eshel 56:09 "זה באמת נכון... להתקדם איתה". |
| Data source tab first | Eshel 49:44 "אולי הדאטה סורס צריך להיות ראשון" | Yau 50:06 disagrees (you start from yield and groups; the data source is usually Baseline + Endline). No agreement, so leave it. |
| Build your own measurements | Eshel 53:36 "המז'רמנט המורכבים לא אני אכלתי"; Yau 54:25 "אתה תהיה עצמאי... בבנייה של המז'רמנט"; recap 56:24 | Agreed for v1, but it needs its own design pass. Eshel will first double-check the existing measurements (53:36 "אני אעשה גם איזשהו דאבל צ'ק"). |
| Change a chart's settings from the chart | Eshel 36:23 "אתה לא יכול ממש לשנות את הגרף" | Part of the chart work Yau listed for later (44:50, 56:24). This pass only fixes the labels. |
| Right-click the table to add a measurement | Eshel 48:00 "לתת את הרייט קליק על הטבלה" | Raised in passing as an idea ("יכול להיות מעניין"). |
| Count farmers missing an answer (e.g. no total yield) | Eshel 33:49 "אין להם טוטל ילד"; 45:41 on double-checking against raw data | Yau 34:05: what matters is that the check is possible, and Raw data already shows it (31:39). Worth raising when the real data is connected. |
| Last year's dataset, control groups | Eshel 46:00, 01:03:08 | Yau 01:03:45: "אולי בואו קודם נעשה את הדברים האלה שאמרנו". |

Next call: Tuesday 10 Nov, 10:00 (01:02:29).
