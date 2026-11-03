"""Builder preview, round 3 of the 1 November feedback.

The preview pane is headed "Table preview", has no intro block, offers "+ Measurement" in the
table's bottom-right cell, and change columns explain their matching rule with a small "i"
instead of a "Grouping" note above the table.

Run with the existing suite: python -m unittest discover -s tests -v
"""
import unittest

import test_feedback_20260922 as previous

TOOLTIP = 'Change compares only records with the same answer in both sources.'


class BuilderRound3PreviewTests(unittest.TestCase):
    setUpClass = classmethod(previous.FeedbackBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(previous.FeedbackBrowserTests.tearDownClass.__func__)
    setUp = previous.FeedbackBrowserTests.setUp
    tearDown = previous.FeedbackBrowserTests.tearDown

    def screenshot(self, name, selector='.builder-preview-panel'):
        previous.ARTIFACTS.mkdir(parents=True, exist_ok=True)
        path = str(previous.ARTIFACTS / f"20261101-r3-{name}.png")
        if selector:
            self.page.locator(selector).first.screenshot(path=path)
        else:
            self.page.screenshot(path=path)

    def add_button(self):
        return self.page.locator('#builder-preview [data-builder-menu="measurements"]')

    def assert_add_button_in_bottom_right_cell(self):
        p = self.page
        self.assertEqual(self.add_button().count(), 1)
        self.assertEqual(self.add_button().inner_text(), '+ Measurement')
        self.assertTrue(p.evaluate("""(() => {
          const rows = [...document.querySelectorAll('#builder-preview table.matrix tbody tr')], last = rows.at(-1);
          return last.lastElementChild === document.querySelector('#builder-preview [data-builder-menu="measurements"]').closest('td');
        })()"""), 'The button sits in the last cell of the last row')

    def test_preview_heading_and_no_intro(self):
        p = self.page
        p.evaluate("openBuilder()")
        heading = p.locator('.builder-preview-panel .builder-preview-heading')
        self.assertEqual(heading.inner_text(), 'Table preview')
        self.assertTrue(heading.is_visible())
        self.assertEqual(p.locator('.builder-preview-panel').get_attribute('aria-labelledby'), 'builder-preview-heading builder-preview-title')
        for draft in ["", "work.draft.rows.push('q:crop'); renderBuilder()"]:
            p.evaluate(draft or "0")
            text = p.locator('#builder-preview').inner_text()
            for gone in ['Start with your groups', 'Your table is taking shape', 'Choose a measurement']:
                self.assertNotIn(gone, text)
            self.assertEqual(p.locator('.builder-skeleton-intro').count(), 0)

    def test_add_measurement_sits_in_the_bottom_right_cell(self):
        p = self.page
        p.evaluate("openBuilder()")
        # No groups yet: the skeleton's only value cell.
        self.assert_add_button_in_bottom_right_cell()
        p.evaluate("work.draft.rows.push('q:crop'); work.draft.columns.push('q:gender'); renderBuilder()")
        self.assert_add_button_in_bottom_right_cell()
        # After a measurement the calculated table keeps it, so more can be added.
        p.evaluate("builderUseMeasurement('net'); builderSyncPeriods(work.draft); renderBuilder()")
        self.assertGreater(p.locator('#builder-preview tbody .cell-button').count(), 0)
        self.assert_add_button_in_bottom_right_cell()
        p.evaluate("builderUseMeasurement('yield'); builderSyncPeriods(work.draft); renderBuilder()")
        self.assert_add_button_in_bottom_right_cell()

    def test_measurement_menu_filters_and_adds(self):
        p = self.page
        p.evaluate("openBuilder(); work.draft.rows.push('q:crop'); renderBuilder()")
        button = self.add_button()
        button.focus()
        p.keyboard.press('Enter')
        menu = p.locator('#builder-axis-menu')
        self.assertEqual(menu.count(), 1)
        self.assertEqual(button.get_attribute('aria-expanded'), 'true')
        self.assertEqual(menu.get_attribute('aria-label'), 'Add a measurement')
        search = menu.locator('input')
        self.assertEqual(search.get_attribute('placeholder'), 'Search measurements')
        self.assertTrue(search.evaluate('el => el === document.activeElement'))
        expected = p.evaluate("builderMetricChoices(work.draft).filter(m => !work.draft.metrics.includes(m.id) && fieldAvailableInBuilder(m)).map(m => m.id)")
        self.assertEqual(menu.locator('[role=option]').evaluate_all('els => els.map(e => e.dataset.field)'), expected)
        # The menu opens at the button.
        box, anchor = menu.bounding_box(), button.bounding_box()
        self.assertLess(abs((box['x'] + box['width']) - (anchor['x'] + anchor['width'])), 40)
        self.assertTrue(abs(box['y'] - (anchor['y'] + anchor['height'])) < 40 or abs((box['y'] + box['height']) - anchor['y']) < 40)
        p.keyboard.type('yield')
        options = menu.locator('[role=option]').evaluate_all('els => els.map(e => e.dataset.field)')
        self.assertIn('yield', options)
        self.assertTrue(all('yield' in p.evaluate(f"builderMeasurementName(metricInfo({o!r})).toLowerCase()") for o in options))
        self.assertEqual(options[0], 'yield')
        p.keyboard.press('Enter')
        self.assertEqual(p.evaluate("work.draft.metrics"), ['yield'])
        self.assertEqual(p.locator('#builder-axis-menu').count(), 0)
        self.assertEqual(p.evaluate("document.activeElement?.dataset.builderMenu"), 'measurements')
        self.assertTrue(p.locator('[data-builder-metric="yield"]').is_checked(), 'The left list follows')
        # Already chosen measurements are not offered again.
        self.add_button().click()
        self.assertNotIn('yield', p.locator('#builder-axis-menu [role=option]').evaluate_all('els => els.map(e => e.dataset.field)'))
        p.keyboard.press('Escape')

    def test_measurement_menu_closes_without_changes(self):
        p = self.page
        p.evaluate("openBuilder()")
        before = p.evaluate("JSON.stringify(work.draft)")
        self.add_button().click()
        p.keyboard.type('net')
        p.keyboard.press('Escape')
        self.assertEqual(p.locator('#builder-axis-menu').count(), 0)
        self.assertTrue(p.locator('#work-dialog').evaluate('el => el.open'), 'Escape closes only the menu')
        self.assertEqual(p.evaluate("document.activeElement?.dataset.builderMenu"), 'measurements')
        self.add_button().click()
        p.locator('#builder-title').click()
        self.assertEqual(p.locator('#builder-axis-menu').count(), 0)
        self.add_button().click()
        self.add_button().click()
        self.assertEqual(p.locator('#builder-axis-menu').count(), 0, 'The same button toggles the menu closed')
        # Opening one menu closes the other.
        self.add_button().click()
        p.locator('#builder-preview [data-builder-menu="rows"]').click()
        self.assertEqual(p.locator('#builder-axis-menu').get_attribute('data-kind'), 'rows')
        self.assertEqual(self.add_button().get_attribute('aria-expanded'), 'false')
        p.keyboard.press('Escape')
        self.assertEqual(p.evaluate("JSON.stringify(work.draft)"), before)

    def test_count_only_rule_applies(self):
        p = self.page
        p.evaluate("openBuilder(); builderUseMeasurement('net'); renderBuilder()")
        self.add_button().click()
        p.locator('#builder-axis-menu [data-field="count"]').click()
        self.assertEqual(p.evaluate("[work.draft.metrics, work.draft.stats]"), [['count'], ['count']])
        self.add_button().click()
        p.locator('#builder-axis-menu [data-field="yield"]').click()
        self.assertEqual(p.evaluate("[work.draft.metrics, work.draft.stats]"), [['yield'], ['mean']])

    def test_add_measurement_never_leaves_the_builder(self):
        p = self.page
        self.assertGreater(p.locator('#tables .matrix').count(), 0)
        self.assertEqual(p.locator('#tables [data-builder-menu]').count(), 0)
        p.evaluate("preparePrint()")
        self.assertGreater(p.locator('#print-output .matrix').count(), 0)
        self.assertEqual(p.locator('#print-output [data-builder-menu]').count(), 0)
        self.assertEqual(p.locator('#print-output .preview-add-measurement').count(), 0)
        p.evaluate("document.querySelector('#print-output').innerHTML=''")

    def test_change_info_replaces_grouping_note(self):
        p = self.page
        has_change = p.evaluate("visibleTables().map(t => [t.id, descriptors(t).some(h => h.stat === 'change')])")
        self.assertTrue(any(c for _, c in has_change) and not all(c for _, c in has_change))
        for table_id, change in has_change:
            card = p.locator(f'#table-{table_id}')
            self.assertEqual(card.locator('.matrix-scroll .change-info').count(), 1 if change else 0, table_id)
            self.assertNotIn('Each source column uses its own answers', card.inner_text())
            if change:
                info = card.locator('.matrix-scroll .change-info')
                self.assertEqual(info.get_attribute('aria-label'), 'About change')
                self.assertEqual(info.evaluate("el => el.closest('th').className"), 'source-heading')
                self.assertIn(' to ', info.evaluate("el => el.closest('th').textContent"))
        self.assertNotIn('Grouping', p.locator('#tables').inner_text())
        first = next(t for t, c in has_change if c)
        info = p.locator(f'#table-{first} .matrix-scroll .change-info')
        info.scroll_into_view_if_needed()
        # Hover shows the tooltip; moving away hides it.
        info.hover()
        tip = p.locator('#change-tooltip')
        self.assertEqual(tip.inner_text(), TOOLTIP)
        self.assertEqual(tip.get_attribute('role'), 'tooltip')
        self.assertEqual(tip.evaluate('el => getComputedStyle(el).position'), 'fixed')
        tbox, ibox = tip.bounding_box(), info.bounding_box()
        self.assertLess(abs(tbox['y'] - (ibox['y'] + ibox['height'])), 20)
        self.screenshot('change-tooltip-main', None)
        p.mouse.move(5, 5)
        self.assertEqual(tip.count(), 0)
        # Focus shows it; Escape dismisses.
        info.focus()
        self.assertEqual(tip.count(), 1)
        p.keyboard.press('Escape')
        self.assertEqual(tip.count(), 0)
        # Never in print.
        p.evaluate("preparePrint()")
        self.assertEqual(p.locator('#print-output .change-info').count(), 0)
        self.assertNotIn('Each source column uses its own answers', p.locator('#print-output').inner_html())
        p.evaluate("document.querySelector('#print-output').innerHTML=''")

    def test_change_info_in_the_builder_preview(self):
        p = self.page
        p.evaluate("openBuilder(); work.draft.rows.push('q:crop'); builderUseMeasurement('yield'); work.draft.change = false; renderBuilder()")
        self.assertEqual(p.locator('#builder-preview .change-info').count(), 0)
        p.evaluate("work.draft.change = true; work.draft.changeStat = 'mean'; renderBuilder()")
        self.assertTrue(p.evaluate("descriptors(builderCandidate()).some(h => h.stat === 'change')"))
        info = p.locator('#builder-preview .change-info')
        self.assertEqual(info.count(), 1)
        self.assertNotIn('Grouping', p.locator('#builder-preview').inner_text())
        info.focus()
        tip = p.locator('#work-dialog #change-tooltip')
        self.assertEqual(tip.inner_text(), TOOLTIP)
        self.screenshot('change-tooltip-builder', None)
        p.keyboard.press('Escape')
        self.assertEqual(tip.count(), 0)
        self.assertTrue(p.locator('#work-dialog').evaluate('el => el.open'), 'Escape closes only the tooltip')
        self.assert_add_button_in_bottom_right_cell()

    def test_menu_and_button_fit_the_screen(self):
        p = self.page
        for width, height in [(1440, 900), (390, 844)]:
            p.set_viewport_size({'width': width, 'height': height})
            for setup in ["", "builderUseMeasurement('net');"]:
                p.evaluate(f"openBuilder(); work.draft.rows = ['q:crop']; work.draft.columns = ['q:gender']; {setup} renderBuilder()")
                self.add_button().scroll_into_view_if_needed()
                self.assertTrue(self.add_button().is_visible())
                self.add_button().click()
                box = p.locator('#builder-axis-menu').bounding_box()
                self.assertGreaterEqual(box['x'], 0)
                self.assertGreaterEqual(box['y'], 0)
                self.assertLessEqual(box['x'] + box['width'], width)
                self.assertLessEqual(box['y'] + box['height'], height)
                self.screenshot(f"measurement-menu-{width}{'-calculated' if setup else ''}", None)
                p.keyboard.press('Escape')
                p.evaluate("closeWork()")
            p.evaluate("openBuilder()")
            self.screenshot(f'empty-{width}')
            p.evaluate("closeWork()")


if __name__ == "__main__":
    unittest.main()
