"""Builder preview for the 1 November "simplify table creation" request.

The preview shows the table's shape before a measurement is chosen, offers "+ Column" / "+ Row"
shortcuts in its top-left cell, and accepts groups dropped straight onto its headers.

Run with the existing suite: python -m unittest discover -s tests -v
"""
import unittest

import test_feedback_20260922 as previous


class SimpleBuilderPreviewTests(unittest.TestCase):
    setUpClass = classmethod(previous.FeedbackBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(previous.FeedbackBrowserTests.tearDownClass.__func__)
    setUp = previous.FeedbackBrowserTests.setUp
    tearDown = previous.FeedbackBrowserTests.tearDown
    drag = previous.FeedbackBrowserTests.drag

    def screenshot(self, name):
        previous.ARTIFACTS.mkdir(parents=True, exist_ok=True)
        self.page.locator('.builder-preview-panel').screenshot(path=str(previous.ARTIFACTS / f"20261101-{name}.png"))

    def test_preview_without_measurement_shows_group_values(self):
        p = self.page
        p.evaluate("openBuilder()")
        # A new table starts as an inviting, empty table, not an error.
        self.assertEqual(p.evaluate("work.draft.metrics"), [])
        self.assertEqual(p.locator('#builder-preview table.builder-skeleton').count(), 1)
        self.assertIn('Start with your groups', p.locator('#builder-preview').inner_text())
        self.assertEqual(p.locator('#builder-preview .builder-preview-empty').count(), 0)
        self.screenshot('empty')

        p.evaluate("work.draft.rows.push('q:crop'); work.draft.columns.push('q:gender'); renderBuilder()")
        before = p.evaluate("JSON.stringify(work.draft)")
        # The same groups a finished table would show, calculated on a copy.
        expected = p.evaluate("""(() => {const t=clone(work.draft);t.metrics=['net'];t.stats=['mean'];const r=calculate(t);
          return {rows:r.rowGroups.map(g=>g.label), columns:r.columnGroups.map(g=>g.label)};})()""")
        self.assertGreater(len(expected['rows']), 1)
        rows = p.locator('#builder-preview tbody th.category-cell').all_inner_texts()
        columns = p.locator('#builder-preview thead th.category-heading:not(.row-axis-header)').all_inner_texts()
        self.assertEqual([r.strip() for r in rows], expected['rows'][:40])
        self.assertEqual([c.strip() for c in columns], expected['columns'][:12])
        self.assertIn('Crop', p.locator('#builder-preview thead th.row-axis-header').inner_text())
        # Empty value cells, no numbers, and the draft is untouched.
        self.assertEqual(p.locator('#builder-preview tbody .cell-button').count(), 0)
        self.assertEqual(p.locator('#builder-preview tbody td.skeleton-cell').count(), min(len(expected['rows']), 40) * min(len(expected['columns']), 12))
        self.assertEqual(p.evaluate("JSON.stringify(work.draft)"), before)
        self.assertIn('Your table is taking shape', p.locator('#builder-preview').inner_text())
        self.screenshot('skeleton')

    def test_preview_survives_missing_title_and_summary(self):
        p = self.page
        p.evaluate("openBuilder(); document.querySelector('#builder-preview-title')?.remove(); document.querySelector('#builder-preview-summary')?.remove(); work.draft.rows.push('q:crop'); builderPreview()")
        self.assertEqual(p.locator('#builder-preview table.builder-skeleton').count(), 1)
        p.evaluate("""builderUseMeasurement('net'); builderSyncPeriods(work.draft); renderBuilder();
          document.querySelector('#builder-preview-title')?.remove(); document.querySelector('#builder-preview-summary')?.remove(); builderPreview()""")
        self.assertGreater(p.locator('#builder-preview tbody .cell-button').count(), 0)

    def test_add_axis_buttons_focus_group_search(self):
        p = self.page
        p.evaluate("openBuilder()")
        for axis, name in [('columns', '+ Column'), ('rows', '+ Row')]:
            p.evaluate("document.querySelector('[data-builder-panel=\"groups\"]').open=false")
            button = p.locator(f'#builder-preview thead th.row-axis-header [data-action="builder-focus-axis"][data-axis="{axis}"]')
            self.assertEqual(button.inner_text(), name)
            button.focus()
            p.keyboard.press('Enter')
            self.assertTrue(p.evaluate("document.querySelector('[data-builder-panel=\"groups\"]').open"))
            self.assertEqual(p.evaluate("document.activeElement?.dataset.builderAxisSearch"), axis)
        # With a measurement the calculated table keeps the shortcuts in its top-left cell.
        p.evaluate("builderUseMeasurement('net'); builderSyncPeriods(work.draft); renderBuilder()")
        corner = p.locator('#builder-preview thead th.row-axis-header').first
        self.assertEqual(corner.locator('[data-action="builder-focus-axis"]').all_inner_texts(), ['+ Column', '+ Row'])
        self.assertNotIn('Measurement', corner.inner_text())
        self.screenshot('calculated')
        p.evaluate("work.draft.rows.push('q:crop'); renderBuilder()")
        self.assertEqual(p.locator('#builder-preview thead [data-action="builder-focus-axis"]').count(), 2)

    def test_add_axis_buttons_never_leave_the_builder(self):
        p = self.page
        self.assertGreater(p.locator('#tables .matrix').count(), 0)
        self.assertEqual(p.locator('#tables [data-action="builder-focus-axis"]').count(), 0)
        self.assertEqual(p.evaluate("document.querySelector('#tables').innerHTML.includes('preview-add-axis')"), False)
        p.evaluate("preparePrint()")
        self.assertEqual(p.locator('#print-output [data-action="builder-focus-axis"]').count(), 0)
        p.evaluate("document.querySelector('#print-output').innerHTML=''")

    def test_drop_groups_on_preview_headers(self):
        p = self.page
        p.evaluate("openBuilder()")
        self.drag('#fields-list [data-field="q:crop"]', '#builder-preview tbody th.row-axis-header')
        self.assertEqual(p.evaluate("work.draft.rows"), ['q:crop'])
        self.assertEqual(p.evaluate("work.draft.metrics"), [])
        self.drag('#fields-list [data-field="q:gender"]', '#builder-preview thead th.skeleton-hint')
        self.assertEqual(p.evaluate("work.draft.columns"), ['q:gender'])
        # A group moves from columns to rows by dropping its level handle on the preview's row headers.
        self.drag('.axis-level[data-axis="columns"] .axis-drag-handle', '#builder-preview tbody th.row-axis-header')
        self.assertEqual(p.evaluate("work.draft.rows"), ['q:crop', 'q:gender'])
        self.assertEqual(p.evaluate("work.draft.columns"), [])
        # Measurements still drop onto the empty value cells.
        self.drag('[data-drag-kind="measurement"][data-field="net"]', '#builder-preview tbody td.skeleton-cell')
        self.assertIn('net', p.evaluate("work.draft.metrics"))
        self.assertGreater(p.locator('#builder-preview tbody .cell-button').count(), 0)


if __name__ == "__main__":
    unittest.main()
