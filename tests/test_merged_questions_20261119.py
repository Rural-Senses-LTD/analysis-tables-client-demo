"""Questions that are basically the same across data sources are merged (Yau, 19 November 2026, third pass).

Numeric pairs come from names that differ only in case or punctuation, and from the Baseline/Endline pairs the project
measurements already treat as one. Category questions use the existing question links (Baseline Crop / Crop and so on).

Run with the existing suite: python -m unittest discover -s tests -v
"""
import unittest

import test_feedback_20260922 as previous


class MergedQuestionsTests(unittest.TestCase):
    setUpClass = classmethod(previous.FeedbackBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(previous.FeedbackBrowserTests.tearDownClass.__func__)
    setUp = previous.FeedbackBrowserTests.setUp
    tearDown = previous.FeedbackBrowserTests.tearDown

    def test_numeric_questions_that_are_the_same_are_merged(self):
        merged = self.page.evaluate("Object.fromEntries([...numericQuestionMap.values()].map(q => [q.label, q.fields]))")
        self.assertEqual(merged["Net Income"], {"b": "b:Net income", "e": "e:Net Income"})
        self.assertEqual(merged["Total expenses"], {"b": "b:Total Expenses", "e": "e:Total expenses"})
        self.assertEqual(merged["Size of Land (Ha)"], {"b": "b:Land Size Ha", "e": "e:Size of Land (Ha)"})
        self.assertEqual(merged["Total Yield per plot (in Kg per Season)"], {"b": "b:Yield kg", "e": "e:Total Yield per plot (in Kg per Season)"})
        self.assertEqual(merged["Income per plot (in Birr)"], {"b": "b:income ETB", "e": "e:Income per plot (in Birr)"})
        self.assertEqual(len(merged), 5)

    def test_variable_list_offers_each_merged_question_once(self):
        p = self.page
        p.evaluate("openDefinition('measure')")
        texts = p.locator('[data-definition-input="0"] option').all_inner_texts()
        for name in ("Net income", "Total Expenses", "Land Size Ha", "Yield kg", "income ETB"):
            self.assertNotIn(name, texts)  # the Baseline names are folded into the merged question
        self.assertEqual(texts.count("Net Income"), 1)

    def test_library_merges_category_and_numeric_questions(self):
        rows = self.page.evaluate(
            """() => { const read = tab => { openDefinitions(tab); return Object.fromEntries([...document.querySelectorAll('[data-def-section="source"] .def-library-row')]
                .map(r => [r.querySelector('strong').textContent, [...r.querySelectorAll('[data-action="def-source-raw"]')].map(b => b.dataset.source + ':' + b.dataset.field)])); };
              return {categories: read('categories'), measurements: read('measurements')}; }"""
        )
        self.assertEqual(rows["categories"]["Crop"], ["b:Baseline Crop", "e:Crop"])
        self.assertEqual(rows["categories"]["Woreda"], ["b:Woreda", "e:Wareda"])
        self.assertNotIn("Baseline Crop", rows["categories"])
        self.assertEqual(rows["measurements"]["Size of Land (Ha)"], ["b:Land Size Ha", "e:Size of Land (Ha)"])
        self.assertNotIn("Land Size Ha", rows["measurements"])

    def test_measurement_on_merged_questions_has_a_value_in_each_source(self):
        result = self.page.evaluate(
            """() => { state.definitions.push({id: 'custom-merged', kind: 'measure', label: 'Merged net per ha', unit: 'ETB/ha',
                formula: 'VAR1 / VAR2', inputs: ['qn:net_income', 'qn:size_of_land_ha'], mapping: {}});
              const t = clone(state.tables[0]); t.metrics = ['netha', 'custom-merged']; const d = calculate(t);
              const row = id => d.rows.find(r => r.metric === id).cells.map(c => c.value === null ? null : Math.round(c.value));
              return {project: row('netha'), merged: row('custom-merged'), headers: d.headers.map(h => h.label)}; }"""
        )
        # Same calculation as the project measurement Net income per hectare, so every column matches, change included.
        self.assertEqual(result["merged"], result["project"])
        self.assertTrue(all(v is not None for v in result["merged"]), result)

    def test_measurement_on_merged_questions_survives_save_and_reload(self):
        p = self.page
        p.evaluate("openDefinition('measure')")
        p.locator('#definition-name').fill('Merged net income')
        p.locator('#definition-unit').fill('ETB')
        p.locator('[data-definition-input="0"]').select_option('qn:net_income')
        self.assertIn("Net income", p.locator('.def-var-sources').first.inner_text())
        self.assertIn("Net Income", p.locator('.def-var-sources').first.inner_text())
        p.locator('[data-action="save-definition"]').click()
        p.reload()
        self.assertEqual(p.evaluate("state.definitions.find(d => d.label === 'Merged net income')?.inputs"), ["qn:net_income"])


if __name__ == "__main__":
    unittest.main()
