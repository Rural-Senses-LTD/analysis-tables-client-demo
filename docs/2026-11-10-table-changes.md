# Table changes from the 10 November 2026 TOV call

**Sources**
- Call: "TOV RS", 10 Nov 2026, 16:00 IST, with Yau and Eshel. Eden declined the invite.
- Audio, the whole call (54:36): Krisp recording, saved as
  `Meeting recordings and Transcript\2026-11-10 TOV meeting (Krisp).mp3`. Transcript:
  `2026-11-10 TOV meeting (Krisp).he.speakers.txt` (ivrit.ai, GPU). All timestamps below are Krisp times.
- Video, second half only (23:04): Meet recording from the calendar invite, saved as
  `Meeting recordings and Transcript\2026-11-10 TOV meeting.mp4`. Recording started late, so video
  0:00 is Krisp 31:34 (found by matching the two audio tracks). Anything said before 31:34 has
  no screen reference.
- Speakers (inferred, the transcript labels are anonymous): Speaker 2 = Eshel. He shares the screen,
  talks about Eden in the third person ("אדן זרק את כל המידע לנוטבוק"), mentions the Leaf fund and
  his gym class on the moshav, and closes with "בואו נתאם שגם עדן יהיה בלופ". Speaker 1 = Yau.
  Yau's side of the transcript is badly garbled, so his points are paraphrased with low confidence.
- Email, 4 to 11 Nov: Yau's 5 Nov update ("טבלאות מעודכנות") had no reply. Eden's emails were
  calendar declines. No product feedback by email.
- The Gemini notes on the invite are an English pass over Hebrew speech and are not usable.

**Screen in the second half:** Eshel works on one table the whole time, "Yield/Ha+count -
Tomato/variety/irrigation type (Endline)": Irrigation Type rows, Tomato by Variety columns, Yield
per hectare, then Baseline added side by side.

## Built in this pass (5 items)

| # | What's asked | Source | On screen | Plan |
|---|---|---|---|---|
| 1 | Categories & Measurements is not in A to Z order, so things are hard to find | Eshel 08:54 "לא יודע אם זה הוסדר לפי ה-ABC", 10:23 "זה לא לפי האבי-סי", 12:06 "גם קשה לנווט בתוך זה" | Not visible (before the video starts). Eshel says he is in "Categories and Measurements" (08:54) | Done. Both tabs, and both sections in each tab, now read A to Z. |
| 2 | Say which source question sits behind a measurement such as Net income or Household income | Eshel 13:46 "איך אתה מאפשר לי לדעת למה האינקאם הזה משתמש?", 16:40 "את הקונטקסט של השאלה... נט אינקאם, איך אני יודע אם זה הנט אינקאם שאני מתכוון?", 19:13 "האם זה אינטייר לנד סייז או שזה ה-plot לנד סייז?" Yau (16:52, garbled) suggests showing how it appears in the questions | Not visible | Done for project measurements. The line under each one used to say "Calculated from source questions". It now names the question in each source, e.g. Net income per hectare: "Baseline: Net income ÷ land area · Endline: Net Income ÷ land area". Search also finds these question names. |
| 3 | In the chart, the N values cannot be told apart. Each N should name its variety | Eshel 45:01 "במקום ה-N צריך להיות השם של הזן". Yau 45:45 suggests showing them above the bars ("מעל ה... עמודה"). Eshel 45:52 "כן, בדיוק" | Video 13:27 to 14:11: Create a bar chart, five series (Missing / Gabi / Galilea 39, Endline and Baseline). Under Drip and Furrow is a list of five "N=" values with only a coloured dot each | Done. With two or more series, each bar now has its own N just above its value, so it sits with its variety. The dot list under the category is gone. Count charts skip the N, because it would repeat the bar's value. Change-over-time charts keep the list, because their two-part sample text does not fit a bar. |
| 4 | Two Crop filters were on at once and nothing said so | Eshel 31:15 and 31:33 "אתה רואה, עשינו פעמיים קרופ", 31:44 "כמה עשינו את זה?", 31:54 "נאו פותח לי שוב קרופ" | Video 0:20: chips "Crop includes Tomato" and "Crop: 35 selected" both on. The second keeps every answer, so it does nothing | Done. When two filters use the same question, both cards say: "Another Crop filter is also on. Records must pass both." If one of them keeps every answer it adds: "This one keeps every answer, so it changes nothing." The note updates as answers are ticked. It does not block the second filter, because two can be deliberate. Eshel's final setup (video 1:28) was Crop includes Tomato plus Crop is the same in every data source. |
| 5 | The "Match across data sources" list is confusing | Eshel 31:54 "יכולתי לבחור קרופ שווה ל...", 32:21 "אבל אין לי פה תשובות" | Video 0:20 to 0:47: after choosing Match across data sources, a second list opens on Match_Notes, Outlier_Flag, Outlier_Reason, Review_Flag, Review_Notes, with Crop at the very bottom | Done. The question being filtered now comes first, labelled "Crop (same question in every data source)". Other farmer questions follow under "Another question", and Match_, Outlier_ and Review_ fields go last under "Data cleaning fields". Medium confidence on "אין לי פה תשובות": he may have expected an answer list in this mode. The hint under the list already explains it needs none. |

**Small consistency fix (not asked for):** the chart called an empty answer "Missing" while the table
called it "Blank" (video 13:27 shows both). The chart now says "Blank" too.

## Not in this pass

| What's asked | Source | Why not now |
|---|---|---|
| Hide Blank answers by default, or deal with them during cleaning | Eshel 26:43 "הייתי מפעל יותר החוצה את הבלנק", 26:56 the filter should open "נקי", 27:35 "endless problem... אולי בקלינינג" | Eshel and Yau disagreed in the call. Yau (27:50, garbled) calls hiding blanks by default "מסוכן מאוד". Later Eshel wanted them back himself (38:52 "עכשיו אני רוצה שהוא כן יחזיר את הבלנק") to find baseline farmers who did not know their variety. Needs a decision before building. |
| A more logical structure for Irrigation, Crop and Variety. Combined answers like "Cabbage, Onion" show as their own groups | Eshel 34:56 "יש פה מין פירמידה... זה קצת מבולגן" | Video 3:22: with Crop includes Tomato removed, the columns become Cabbage, "Cabbage, Onion", "Cabbage, Tomato" and so on. Fixing it means splitting multi-answer Crop into separate answers, which changes how every crop count works. Too big for a feedback pass, so it needs a spec first. |
| Jump from a chosen row or column to the raw data, with that column highlighted. Or open the questionnaire itself | Eshel 14:58 "תן לי גישה לשאלון עצמו", 15:35 the raw data, 17:11 "הוא ייתן לך Navigation ל-ROData, שכאילו מסמן את ה-colum שבחרת" | Eshel hedged it himself ("סתם עולה לי לראש, אני לא רוצה לזרוק אותנו לאיבוד"). Items 1 and 2 cover the immediate need. The raw-data links already exist in the table footer and the cell drill-down. |
| What "VAR1" means in a calculated measurement | Eshel 18:00 "מין value של var 1?" | Not visible, and the transcript does not show which measurement he opened. The definition view already lists VAR1 with its source. Worth asking on the next call. |
| Have AI build the table from a title and description | Eshel 36:00 "בסוף היה צריך לבקש מ-AI לבנות לך את זה", 47:08, 48:59 | A product direction, outside the scope of this mockup. Eshel agreed (48:35) the result must stay "בשימושיות עם לוגיקה מסוימת" that a person can control. |
| A home page with a live report, like the stand-alone notebook report Eden made | Eshel 04:56 "אם הייתי יכול לשים את זה כבר במערכת, אז היה לי הום פייג'" | Out of scope for the tables mockup. |
| Charts that cope with sub-groups and averages | Eshel 04:02 "אולי נגיע לזה..." | Raised as a possible future step. |
| Baseline has varieties (Galilea) it should not have. Baseline tomato farmer count looks wrong (59) | Eshel 38:24 "גם לא אמור להיות לו גלילאיה בבייסליין", 40:21 "אין לי חקלאי עגבנייה בבייסליין", 44:07 "והבייסלייב הוא 59, אז משהו בספירה" | These are data questions. Video 6:50 and 8:47: Baseline columns show Galilea 39 (N=2) and Galilea Classic (N=5). On 5 Nov, Variety moved to Endline only, so these come from matched records and need checking against the cleaned data. Flag to Eden. |
| Bring Rural Senses in as a research body for the Leaf fund proposal | Eshel 52:35 | Business follow-up for Yau. |

**Next meeting:** Eshel is busy Wednesday and Thursday this week, suggests next week, with Eden in the loop (54:00).

## Follow-up pass, 19 Nov 2026 (3 items)

Yau listed these from the same 10 Nov call. Yau's side of the transcript is badly garbled, so the quotes below are Eshel's asks plus Yau's garbled replies. Scope was settled with Yau on 19 Nov. No video check was done for this pass.

| # | What's asked | Source | Built |
|---|---|---|---|
| 6 | Show each question exactly as it is named in the survey, without a "Baseline:" / "Endline:" label in front | Eshel 16:40 "נט אינקאם, איך אני יודע אם זה הנט אינקאם שאני מתכוון?", Yau 16:52 (garbled) "כשמראות את השאלה, איך זה מופיע בשאלות". Clarified by Yau, 19 Nov | Under each measurement in Categories & Measurements, the line lists the survey question names as they are, e.g. Net income per hectare: "Net income · Net Income ÷ Land Size Ha · Size of Land (Ha)". This replaces item 2's "Baseline: Net income ÷ land area". The land area is named too, instead of "land area". |
| 7 | Show the data sources each question appears in, and let people open them | Eshel 14:58 "תן לי גישה לשאלון עצמו", 15:35 "ובתוך הרודה, ללכת לקולום של... אני גורר ימינה, ימינה, ימינה, עד שאני מגיע לשאלה", 17:11 "Navigation ל-ROData, שכאילו מסמן את ה-colum שבחרת" | Every question name has a chip for each source it appears in. Clicking a chip opens that source's raw data, scrolled to the question's column, with the column highlighted. "Back to Categories & Measurements" returns to the same search. A question with the same name in two sources is now one row with two chips (Farmer_UID, Match_Notes, Match_Status and others). Names that differ, even only in capitals ("Net income" and "Net Income"), stay apart, because that is how the surveys name them. |
| 8 | In the cell drill-down, show the table's filters and let people remove them | Eshel 43:12 "אני רוצה את כל החקלאים, כאילו, גם אם החליפו קרופ", Yau 43:23 (garbled) "תוריד את ה... את קרופ". Low confidence on the anchor. The ask comes from Yau's notes | "Contributing source records" has a new "Filters on this table" panel. Remove previews the cell without that filter: the value, the record count and the list update, the added records are marked "Filtered out of table", and a note says the table has not changed. "Put back" and "Put all back" undo it. "Remove from table" applies it to the table. A table with no filters says so. |

**Assumptions:** On a merged row, View and Edit open the first source's question (Baseline when it has one). The chips give access to each source. Chips always open the in-app raw data, not the platform link, because only the in-app view can highlight the column.

## Second follow-up pass, 19 Nov 2026 (3 items)

Yau reviewed the first follow-up live and asked for these changes. Scope was settled with Yau on 19 Nov.

| # | What's asked | Built |
|---|---|---|
| 9 | When adding a new measurement, pick a variable by its question name alone. Once one is chosen, show which data sources have it, with a link, and a sample of its values in each source | The "Numeric question" list reads A to Z, with names only ("Net Income", not "Net Income · Endline"). A source is added only where two sources use exactly the same name, e.g. "Income per hectare · Baseline". Under each variable, "VAR1 appears in" lists each source with a link to that source's raw data at the column, "228 of 241 records answered", and the first five values. When the same name is in two sources, the panel says which one the calculation uses. A project measurement taken as an input, such as Income per hectare in Baseline, lists the questions it is calculated from (income ETB, Land Size Ha). The draft is kept when you go to the raw data and back. |
| 10 | In the cell drill-down, let people remove the cell's own categories (project, crop and so on), and show the records with no value | Each Row and Column category under "Selected cell" has Remove. It previews the same measurement across every answer of that question (e.g. Amhara, all crops instead of Amhara · Onion: 85 → 136 records), with the added records marked "Not in table". A category is never removed from the table itself, because that would change its rows or columns. Only filters keep "Remove from table". Records with no value are marked "No value", and a new "Show" list switches between All records, With a value and Without a value, with counts. |
| 11 | Change the identifier questions to the farmer's name in all tables: Baseline "Name", Endline "Farmer Name" | Done as the new default for every table. Saved tables still on the old Farmer_UID default move over once per browser. A later deliberate choice of Farmer_UID in the builder is kept. **Effect on the numbers:** tables now match Baseline and Endline farmers by name, which pairs 188 farmers instead of 240, because 52 names are spelled differently between the surveys. Every matched table count and mean changes. |

**Fix, 19 Nov 2026 (Yau):** the variable list for a new measurement also offered project measurements (Income per hectare, Land size, and their change and change %). It now offers only the 22 raw survey questions. A definition saved earlier with a project measurement as an input keeps it, labelled "(project measurement · Baseline)".

## Third follow-up, 19 Nov 2026: merge questions that are basically the same across sources (Yau)

- **Category questions** follow the question links the tables already use: Baseline Crop / Crop, Woreda / Wareda, Irrigation Method / Irrigation Type, Name / Farmer Name and so on. In Categories & Measurements each is now one row (e.g. "Crop") showing each source's own name next to its chip: "Baseline Crop [Baseline] · Crop [Endline]".
- **Numeric questions** that are the same are merged into one question. They are names that differ only in case or punctuation, plus the Baseline/Endline pairs the project measurements already treat as one. Five pairs:
  - Net income / Net Income
  - Total Expenses / Total expenses
  - Land Size Ha / Size of Land (Ha)
  - Yield kg / Total Yield per plot (in Kg per Season)
  - income ETB / Income per plot (in Birr)

  The merged question takes the Endline name, as the later survey.
- **In a new measurement**, a merged question is offered once. "VAR1 appears in" lists each source with its own question name, link, count and sample.
- **The calculation reads each source's own question for that source's column.** So a measurement on merged questions gets a Baseline column, an Endline column and change. Checked: Net Income ÷ Size of Land (Ha) gives the same numbers as the project measurement Net income per hectare in every column.
- **Older definitions:** a definition saved earlier that uses one source's question keeps it, labelled "(Baseline only)".
