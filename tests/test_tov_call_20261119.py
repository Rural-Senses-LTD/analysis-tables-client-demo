"""Follow-up to the 10 November 2026 TOV call, agreed with Yau on 19 November.

1. Source questions show exactly as named in the survey, without a "Baseline:" / "Endline:" label.
2. Each question lists the data sources it appears in, as chips that open the raw data at that column.
   A question with the same name in two sources is one row.
3. The cell drill-down lists the table's filters. Removing one previews the cell without it,
   leaving the table unchanged, and "Remove from table" applies it.

Run with the existing suite: python -m unittest discover -s tests -v
"""
import unittest

import test_feedback_20260922 as previous


class TovCall20261119Tests(unittest.TestCase):
    setUpClass = classmethod(previous.FeedbackBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(previous.FeedbackBrowserTests.tearDownClass.__func__)
    setUp = previous.FeedbackBrowserTests.setUp
    tearDown = previous.FeedbackBrowserTests.tearDown

    def library(self, tab: str) -> list[dict]:
        """Source-section rows of one library tab: title, question names, and chip sources."""
        return self.page.evaluate(
            """tab => { openDefinitions(tab);
              return [...document.querySelectorAll('[data-def-section="source"] .def-library-row')].map(r => ({
                label: r.querySelector('strong').textContent,
                text: r.querySelector('.def-vars')?.textContent || '',
                names: [...r.querySelectorAll('.def-q-name')].map(n => n.textContent),
                chips: [...r.querySelectorAll('[data-action="def-source-raw"]')].map(b => b.dataset.source + ':' + b.dataset.field),
              })); }""",
            tab,
        )

    def test_no_source_label_inside_question_names(self):
        for row in self.library("measurements"):
            self.assertNotIn("Baseline:", row["text"], row["label"])
            self.assertNotIn("Endline:", row["text"], row["label"])
        rows = {r["label"]: r for r in self.library("measurements")}
        self.assertEqual(rows["Net income per hectare"]["names"], ["Net income", "Net Income", "Land Size Ha", "Size of Land (Ha)"])

    def test_same_question_in_two_sources_is_one_row_with_both_chips(self):
        rows = self.library("categories")
        uid = [r for r in rows if r["label"] == "Farmer_UID"]
        self.assertEqual(len(uid), 1)
        self.assertEqual(uid[0]["chips"], ["b:Farmer_UID", "e:Farmer_UID"])
        # Since the later 19 Nov pass, names that are basically the same merge too: "Net income" (Baseline) and "Net Income"
        # (Endline) are one row, each source's own name next to its chip.
        rows = [r for r in self.library("measurements") if r["label"] in ("Net income", "Net Income")]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["chips"], ["b:Net income", "e:Net Income"])

    def test_chip_opens_raw_data_at_that_column_and_returns_to_library(self):
        result = self.page.evaluate(
            """() => { openDefinitions('measurements');
              document.querySelector('#definition-search').value = 'per hectare'; filterDefinitionLibrary();
              const chip = [...document.querySelectorAll('[data-action="def-source-raw"]')].find(b => b.dataset.field === 'Size of Land (Ha)');
              chip.focus(); chip.click();
              const th = document.querySelector('th.raw-focus-column'), scroller = document.querySelector('.raw-data-scroll');
              const a = th.getBoundingClientRect(), s = scroller.getBoundingClientRect();
              const out = {header: th.textContent, cells: document.querySelectorAll('td.raw-focus-column').length,
                visible: a.left >= s.left && a.right <= s.right, source: document.querySelector('#raw-data-source').value};
              document.querySelector('[data-action="raw-data-return"]').click();
              out.back = document.querySelector('#work-dialog').open && work.kind === 'library';
              out.query = document.querySelector('#definition-search').value;
              out.focus = document.activeElement.dataset.field;
              return out; }"""
        )
        self.assertEqual(result["header"], "Size of Land (Ha)")
        self.assertEqual(result["source"], "e")
        self.assertGreater(result["cells"], 0)
        self.assertTrue(result["visible"])
        self.assertTrue(result["back"])
        self.assertEqual(result["query"], "per hectare")
        self.assertEqual(result["focus"], "Size of Land (Ha)")

    def add_filters_and_open_cell(self) -> None:
        self.page.evaluate(
            """() => { const t = state.tables.find(t => t.title === 'Results by crop');
              const make = (field, values) => ({kind:'condition', id:field, field, op:'in', values, value:'', high:'', refs:[], includeBlank:false});
              t.filters.source.children.push(make('b:Gender', ['Female']), make('e:Region', ['Oromia', 'Amhara']));
              commit(t.id); const d = cache.get(t.id) || calculate(t);
              openCell(t.id, d.rows.findIndex(r => r.group.label === 'Onion' && r.metric === 'yield'), 1); }"""
        )

    def test_drilldown_lists_filters_and_previews_without_one(self):
        self.add_filters_and_open_cell()
        result = self.page.evaluate(
            """() => { const t = state.tables.find(t => t.title === 'Results by crop');
              const filters = [...document.querySelectorAll('.cell-filter-text')].map(x => x.textContent);
              const before = work.records.length;
              document.querySelector('[data-action="cell-filter-toggle"][data-key="source:0"]').click();
              return {filters, before, after: work.records.length, added: work.addedUids.length,
                badges: document.querySelectorAll('.preview-added-badge').length,
                preview: document.querySelector('.cell-filter-preview').textContent,
                tableFilters: t.filters.source.children.length}; }"""
        )
        self.assertEqual(result["filters"], ["Gender includes Female", "Region includes Oromia, Amhara"])
        self.assertGreater(result["after"], result["before"])
        self.assertEqual(result["added"], result["after"] - result["before"])
        self.assertEqual(result["badges"], result["added"])
        self.assertIn("The table has not changed", result["preview"])
        self.assertEqual(result["tableFilters"], 2)

    def test_put_back_and_remove_from_table(self):
        self.add_filters_and_open_cell()
        result = self.page.evaluate(
            """() => { const t = state.tables.find(t => t.title === 'Results by crop'), base = work.records.length;
              document.querySelector('[data-action="cell-filter-toggle"][data-key="source:0"]').click();
              const preview = work.records.length;
              document.querySelector('[data-action="cell-filter-restore"]').click();
              const restored = work.records.length;
              document.querySelector('[data-action="cell-filter-toggle"][data-key="source:0"]').click();
              document.querySelector('[data-action="cell-filter-apply"]').click();
              return {base, preview, restored, applied: work.records.length, open: document.querySelector('#work-dialog').open,
                left: t.filters.source.children.map(appliedFilterText), stillPreviewing: !!document.querySelector('.cell-filter-preview')}; }"""
        )
        self.assertEqual(result["restored"], result["base"])
        self.assertEqual(result["applied"], result["preview"])
        self.assertTrue(result["open"])
        self.assertEqual(result["left"], ["Region includes Oromia, Amhara"])
        self.assertFalse(result["stillPreviewing"])

    def test_table_without_filters_says_so(self):
        text = self.page.evaluate(
            """() => { const t = state.tables.find(t => t.title === 'Overall results'); openCell(t.id, 0, 0);
              return document.querySelector('.cell-filters').textContent; }"""
        )
        self.assertIn("No filters", text)


if __name__ == "__main__":
    unittest.main()
