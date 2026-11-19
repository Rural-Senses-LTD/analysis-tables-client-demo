"""Second follow-up pass, 19 November 2026 (Yau, after reviewing #17 live).

1. New measurement: the variable picker lists question names only. Under each variable, the data sources
   that hold it, linked to the raw data, with a count of answers and a sample of values per source.
2. Cell drill-down: the cell's own categories (Crop = Onion...) can be taken out of the preview, and records
   without a value are marked and can be shown on their own.
3. Every table identifies and matches records by name: Baseline "Name", Endline "Farmer Name".

Run with the existing suite: python -m unittest discover -s tests -v
"""
import unittest

import test_feedback_20260922 as previous


class Followup20261119bTests(unittest.TestCase):
    setUpClass = classmethod(previous.FeedbackBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(previous.FeedbackBrowserTests.tearDownClass.__func__)
    setUp = previous.FeedbackBrowserTests.setUp
    tearDown = previous.FeedbackBrowserTests.tearDown

    def pick(self, index: int, text: str) -> None:
        """Choose a variable by its visible option text, like a person would."""
        select = self.page.locator(f'[data-definition-input="{index}"]')
        value = select.evaluate("(el, text) => [...el.options].find(o => o.textContent === text).value", text)
        select.select_option(value)

    def test_variable_picker_lists_question_names_without_sources(self):
        p = self.page
        p.evaluate("openDefinition('measure')")
        options = p.locator('[data-definition-input="0"] option').all_inner_texts()
        self.assertIn("Net Income", options)
        self.assertIn("Size of Land (Ha)", options)
        self.assertFalse(any(o.endswith(" · Endline") and o.replace(" · Endline", "") not in [x.replace(" · Baseline", "") for x in options] for o in options))
        self.assertTrue(p.evaluate(
            "o => { o = o.map(x => x.replace(/ · (Baseline|Endline)$/, ''));"
            " return o.every((x, i) => !i || o[i-1].localeCompare(x, undefined, {numeric: true, sensitivity: 'base'}) <= 0); }", options))

    def test_each_variable_shows_its_sources_count_and_sample(self):
        p = self.page
        p.evaluate("openDefinition('measure')")
        self.pick(0, "Net Income")
        panel = p.locator('.def-var-sources').first.inner_text()
        self.assertIn("Endline", panel)
        self.assertRegex(panel, r"\d+ of 241 records answered")
        self.assertIn("Sample:", panel)
        p.locator('[data-action="add-definition-input"]').click()
        self.pick(1, "Income per hectare · Baseline")
        second = p.locator('.def-var-sources').nth(1).inner_text()
        self.assertIn("income ETB", second)
        self.assertIn("Land Size Ha", second)

    def test_variable_chip_opens_raw_data_and_keeps_the_draft(self):
        p = self.page
        p.evaluate("openDefinition('measure')")
        p.locator('#definition-name').fill('Net income check')
        self.pick(0, "Net Income")
        p.locator('.def-var-sources [data-action="def-source-raw"]').first.click()
        self.assertEqual(p.locator('th.raw-focus-column').inner_text(), "Net Income")
        p.locator('[data-action="raw-data-return"]').click()
        self.assertEqual(p.locator('#definition-name').input_value(), 'Net income check')
        self.assertEqual(p.evaluate("work.draft.inputs"), ["e:Net Income"])

    def open_region_crop_cell(self) -> None:
        self.page.evaluate(
            """() => { const t = state.tables.find(t => t.title === 'Region × crop'), d = cache.get(t.id) || calculate(t);
              const ri = d.rows.findIndex(r => r.metric === 'yield' && pathJSON(r.group.path) === pathJSON([['e:Region', 'Amhara'], ['e:Crop', 'Onion']]));
              openCell(t.id, ri, 1); }"""
        )

    def test_removing_a_cell_category_previews_all_its_answers(self):
        self.open_region_crop_cell()
        result = self.page.evaluate(
            """() => { const t = state.tables.find(t => t.title === 'Region × crop'), before = work.records.length;
              document.querySelector('[data-action="cell-category-toggle"][data-key="row:e:Crop"]').click();
              const after = {records: work.records.length, added: work.addedUids.length,
                note: document.querySelector('.cell-filter-preview').textContent,
                apply: !!document.querySelector('[data-action="cell-filter-apply"]'), rows: [...t.rows]};
              document.querySelector('[data-action="cell-filter-restore"]').click();
              return {before, ...after, restored: work.records.length}; }"""
        )
        self.assertGreater(result["records"], result["before"])
        self.assertEqual(result["added"], result["records"] - result["before"])
        self.assertIn("The table has not changed", result["note"])
        self.assertFalse(result["apply"])  # a category is never removed from the table itself
        self.assertEqual(result["rows"], ["e:Region", "e:Crop"])
        self.assertEqual(result["restored"], result["before"])

    def test_records_without_a_value_are_marked_and_can_be_shown_alone(self):
        self.open_region_crop_cell()
        result = self.page.evaluate(
            """() => { const status = document.querySelector('#contributor-status'), options = [...status.options].map(o => o.textContent);
              const missing = work.records.filter(r => !contributorHasValues(r)).length;
              status.value = 'missing'; status.dispatchEvent(new Event('change', {bubbles: true}));
              return {options, missing, rows: document.querySelectorAll('#source-records tbody tr.cell-no-value').length,
                all: document.querySelectorAll('#source-records tbody tr').length,
                badges: document.querySelectorAll('#source-records .no-value-badge').length}; }"""
        )
        self.assertGreater(result["missing"], 0)
        self.assertIn(f"Without a value ({result['missing']})", result["options"])
        self.assertEqual(result["rows"], result["missing"])
        self.assertEqual(result["all"], result["missing"])
        self.assertEqual(result["badges"], result["missing"])

    def test_tables_identify_records_by_name(self):
        result = self.page.evaluate(
            """() => ({ids: [...new Set(state.tables.map(t => JSON.stringify(sourceSettings(t).identifiers)))],
              header: (() => { const t = state.tables[0]; openCell(t.id, 0, 0);
                return [...document.querySelectorAll('.contributor-field-headers th')].map(th => th.textContent); })()})"""
        )
        self.assertEqual(result["ids"], ['{"b":"b:Name","e":"e:Farmer Name"}'])
        self.assertTrue(any(h.startswith("Name") for h in result["header"]))
        self.assertTrue(any(h.startswith("Farmer Name") for h in result["header"]))

    def test_saved_uid_tables_move_to_names_once(self):
        p = self.page
        p.evaluate(
            """() => { const t = state.tables[0], s = sourceSettings(t);
              t.sources = {...s, identifiers: {b: 'b:Farmer_UID', e: 'e:Farmer_UID'}}; persist();
              localStorage.removeItem(IDENTIFIER_MIGRATION_KEY); }"""
        )
        p.reload()
        self.assertEqual(p.evaluate("sourceSettings(state.tables[0]).identifiers"), {"b": "b:Name", "e": "e:Farmer Name"})
        # A deliberate choice made after the move is kept on the next load.
        p.evaluate(
            """() => { const t = state.tables[0]; t.sources.identifiers = {b: 'b:Farmer_UID', e: 'e:Farmer_UID'}; persist(); }"""
        )
        p.reload()
        self.assertEqual(p.evaluate("sourceSettings(state.tables[0]).identifiers"), {"b": "b:Farmer_UID", "e": "e:Farmer_UID"})


if __name__ == "__main__":
    unittest.main()
