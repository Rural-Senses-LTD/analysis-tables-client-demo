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
