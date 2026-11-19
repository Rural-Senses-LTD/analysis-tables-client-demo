"""Changes from the 10 November 2026 TOV call (Eshel building a tomato yield table by variety and irrigation type).

Run with the existing suite: python -m unittest discover -s tests -v
"""
import unittest

import test_feedback_20260922 as previous


class TovCall20261110Tests(unittest.TestCase):
    setUpClass = classmethod(previous.FeedbackBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(previous.FeedbackBrowserTests.tearDownClass.__func__)
    setUp = previous.FeedbackBrowserTests.setUp
    tearDown = previous.FeedbackBrowserTests.tearDown

    def library_rows(self, tab: str) -> list[dict]:
        """Rows of one Categories & Measurements tab, source section only."""
        return self.page.evaluate(
            """tab => { openDefinitions(tab);
              return [...document.querySelectorAll('[data-def-section="source"] .def-library-row')]
                .map(r => ({label: r.querySelector('strong').textContent, sub: r.querySelector('p').textContent})); }""",
            tab,
        )

    # Item 1: "זה לא לפי האבי-סי" - both library tabs read A to Z.
    def test_library_lists_are_alphabetical(self):
        for tab in ("categories", "measurements"):
            labels = [r["label"] for r in self.library_rows(tab)]
            self.assertEqual(labels, sorted(labels, key=str.casefold), tab)

    # Item 2: project measurements name the source question per data source instead of a generic line.
    def test_project_measurements_name_their_source_questions(self):
        rows = {r["label"]: r["sub"] for r in self.library_rows("measurements")}
        self.assertIn("Baseline: Net income", rows["Plot net income"])
        self.assertIn("Endline: Net Income", rows["Plot net income"])
        self.assertIn("÷ land area", rows["Net income per hectare"])
        self.assertNotIn("Calculated from source questions", rows.values())

    # Item 3: with several series, each bar carries its own N; the dot list under the category is gone.
    def test_chart_puts_n_on_each_bar(self):
        result = self.page.evaluate("""(() => {
          const t = state.tables.find(x => x.title === 'Region × crop'), d = document.createElement('div');
          d.innerHTML = chartHTML(t, calculate(t), null, true);
          return {series: d.querySelectorAll('.chart-legend span').length, bars: d.querySelectorAll('.chart-bar-slot').length,
                  labelled: d.querySelectorAll('.bar-n').length, lists: d.querySelectorAll('.chart-samples').length,
                  first: d.querySelector('.bar-n')?.textContent};
        })()""")
        self.assertGreater(result["series"], 1)
        self.assertEqual(result["labelled"], result["bars"])
        self.assertEqual(result["lists"], 0)
        self.assertRegex(result["first"], r"^N=\d")

    # Item 4: an empty answer is "Blank" in the chart, as in the table.
    def test_chart_calls_empty_answers_blank(self):
        label = self.page.evaluate("chartSeriesLabel({group: {path: [['b:Variety', null]]}, label: 'Endline mean'})")
        self.assertEqual(label, "Blank · Endline mean")

    def open_crop_filters(self, count: int) -> list:
        return self.page.evaluate(
            """count => { const t = state.tables.find(x => x.title === 'Region × crop'); openFilters(t.id);
              const crop = filterFields('source').find(f => /^crop$/i.test(plainFieldLabel(f)));
              for (let i = 0; i < count; i++) addFilterField(crop.id);
              return [...document.querySelectorAll('#filter-body .filter-condition')]
                .map(c => c.querySelector('.filter-overlap-note')?.textContent || null); }""",
            count,
        )

    # Item 5: "עשינו פעמיים קרופ" - a second filter on the same question is said out loud; a single new filter stays quiet.
    def test_single_filter_has_no_overlap_note(self):
        self.assertEqual(self.open_crop_filters(1), [None])

    def test_two_filters_on_one_question_are_flagged(self):
        notes = self.open_crop_filters(2)
        self.assertEqual(len(notes), 2)
        for note in notes:
            self.assertIn("Another Crop filter is also on", note)
            self.assertIn("changes nothing", note)

    def test_overlap_note_updates_when_an_answer_is_unticked(self):
        self.open_crop_filters(2)
        self.page.locator('#filter-body .filter-condition').first.locator('input[data-answer]').first.click()
        first = self.page.locator('#filter-body .filter-condition').first.locator('.filter-overlap-note').inner_text()
        self.assertIn("Another Crop filter is also on", first)
        self.assertNotIn("changes nothing", first)

    # Item 6: the match-across list starts with the question itself; data-cleaning fields come last.
    def test_match_across_list_puts_cleaning_fields_last(self):
        self.open_crop_filters(1)
        self.page.locator('#filter-body input[data-prop="op"][value="eqField"]').first.click()
        result = self.page.evaluate("""(() => {
          const sel = document.querySelector('#filter-body select[data-prop="otherField"]');
          return {selected: sel.options[sel.selectedIndex].text, first: sel.options[0].text,
                  groups: [...sel.querySelectorAll('optgroup')].map(g => g.label),
                  cleaning: [...(sel.querySelector('optgroup[label="Data cleaning fields"]')?.children || [])].map(o => o.text)};
        })()""")
        self.assertEqual(result["first"], "Crop (same question in every data source)")
        self.assertEqual(result["selected"], result["first"])
        self.assertEqual(result["groups"], ["Another question", "Data cleaning fields"])
        self.assertIn("Outlier_Flag", result["cleaning"])
        self.assertIn("Match_Notes", result["cleaning"])


if __name__ == "__main__":
    unittest.main()
