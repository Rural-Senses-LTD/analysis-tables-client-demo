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

    def axis_button(self, axis):
        return self.page.locator(f'#builder-preview thead th.row-axis-header [data-action="builder-focus-axis"][data-axis="{axis}"]')

    def test_add_axis_buttons_open_a_menu_at_the_button(self):
        p = self.page
        p.evaluate("openBuilder()")
        for axis, name, query, field in [('rows', '+ Row', 'reg', 'q:region'), ('columns', '+ Column', 'gend', 'q:gender')]:
            button = self.axis_button(axis)
            self.assertEqual(button.inner_text(), name)
            button.focus()
            p.keyboard.press('Enter')
            menu = p.locator('#builder-axis-menu')
            self.assertEqual(menu.count(), 1)
            self.assertEqual(p.evaluate("document.activeElement?.dataset.builderAxisMenuSearch"), axis)
            self.assertFalse(p.evaluate("document.querySelector('[data-builder-panel=\"groups\"]').open"), 'The left Groups panel stays as it was')
            expected = p.evaluate("builderCategoryFields().filter(f => ![...work.draft.rows, ...work.draft.columns].includes(f.id)).map(f => f.id)")
            self.assertEqual(menu.locator('[role=option]').evaluate_all('els => els.map(e => e.dataset.field)'), expected)
            # The menu sits next to the button that opened it.
            box, anchor = menu.bounding_box(), button.bounding_box()
            self.assertLess(abs(box['x'] - anchor['x']), 40)
            self.assertLess(abs(box['y'] - (anchor['y'] + anchor['height'])), 40)
            p.keyboard.type(query)
            self.assertEqual(menu.locator('[role=option]').evaluate_all('els => els.map(e => e.dataset.field)'), [field])
            p.keyboard.press('ArrowDown')
            p.keyboard.press('Enter')
            self.assertIn(field, p.evaluate(f"work.draft.{axis}"))
            self.assertEqual(p.locator('#builder-axis-menu').count(), 0)
            self.assertEqual(p.evaluate("document.activeElement?.dataset.action + ':' + document.activeElement?.dataset.axis"), f'builder-focus-axis:{axis}')
        # With a measurement the calculated table keeps the buttons in its top-left cell.
        p.evaluate("builderUseMeasurement('net'); builderSyncPeriods(work.draft); renderBuilder()")
        corner = p.locator('#builder-preview thead th.row-axis-header').first
        self.assertEqual(corner.locator('[data-action="builder-focus-axis"]').all_inner_texts(), ['+ Column', '+ Row'])
        self.assertNotIn('Measurement', corner.inner_text())
        self.axis_button('rows').click()
        self.screenshot('axis-menu-calculated')
        self.assertEqual(p.locator('#builder-axis-menu').count(), 1)

    def test_axis_menu_closes_without_changes(self):
        p = self.page
        p.evaluate("openBuilder()")
        before = p.evaluate("JSON.stringify([work.draft.rows, work.draft.columns])")
        self.axis_button('rows').click()
        p.keyboard.press('Escape')
        self.assertEqual(p.locator('#builder-axis-menu').count(), 0)
        self.assertTrue(p.locator('#work-dialog').evaluate('el => el.open'), 'Escape closes only the menu')
        self.assertEqual(p.evaluate("document.activeElement?.dataset.axis"), 'rows')
        self.axis_button('rows').click()
        p.locator('#builder-title').click()
        self.assertEqual(p.locator('#builder-axis-menu').count(), 0)
        self.axis_button('rows').click()
        self.axis_button('rows').click()
        self.assertEqual(p.locator('#builder-axis-menu').count(), 0, 'The same button toggles the menu closed')
        self.assertEqual(p.evaluate("JSON.stringify([work.draft.rows, work.draft.columns])"), before)

    def test_full_axis_button_explains_the_limit(self):
        p = self.page
        p.evaluate("openBuilder()")
        for axis, other, text in [('rows', 'columns', 'Rows can have up to 3 groups. Remove one in Groups first.'),
                                  ('columns', 'rows', 'Columns can have up to 3 groups. Remove one in Groups first.')]:
            p.evaluate(f"work.draft.rows = []; work.draft.columns = []; work.draft.{axis} = ['q:crop', 'q:region', 'q:gender']; renderBuilder()")
            full = self.axis_button(axis)
            self.assertEqual(full.get_attribute('aria-disabled'), 'true')
            self.assertEqual(full.get_attribute('title'), text)
            self.assertIsNone(full.get_attribute('disabled'), 'Stays focusable so the reason can be read')
            full.click(force=True)
            self.assertEqual(p.locator('#builder-axis-menu').count(), 0)
            self.axis_button(other).click()
            self.assertEqual(p.locator('#builder-axis-menu').count(), 1)
            p.keyboard.press('Escape')

    def test_axis_menu_fits_the_screen(self):
        p = self.page
        for width, height in [(1440, 900), (390, 844)]:
            p.set_viewport_size({'width': width, 'height': height})
            p.evaluate("openBuilder(); work.draft.rows = ['q:crop']; renderBuilder()")
            self.axis_button('columns').scroll_into_view_if_needed()
            self.axis_button('columns').click()
            box = p.locator('#builder-axis-menu').bounding_box()
            self.assertGreaterEqual(box['x'], 0)
            self.assertGreaterEqual(box['y'], 0)
            self.assertLessEqual(box['x'] + box['width'], width)
            self.assertLessEqual(box['y'] + box['height'], height)
            self.screenshot(f'axis-menu-{width}')
            p.keyboard.press('Escape')
            p.evaluate("closeWork()")

    def test_left_axis_search_reads_search_group(self):
        p = self.page
        p.evaluate("openBuilder()")
        # Round 3 replaced the per-axis searches with one search over all groups.
        self.assertEqual(p.locator('[data-builder-axis-search]').count(), 0)
        self.assertEqual(p.locator('#fields-search').get_attribute('placeholder'), 'Search groups')

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
