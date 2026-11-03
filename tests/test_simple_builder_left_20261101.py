"""Simple table builder (1 November): plain left pane, collapsed sections, preview-only right pane.

Run with the existing suite: python -m unittest discover -s tests -v
"""
import unittest
from pathlib import Path
from tempfile import gettempdir

import test_feedback_20260922 as previous

MEASUREMENTS_SUBTITLE = 'Measurements are the numbers inside the table, such as yield or income.'
GROUPS_SUBTITLE = "Groups are the table's rows and columns, such as Crop or Region. You can drag groups directly to the table preview."


class SimpleBuilderLeftTests(unittest.TestCase):
    setUpClass = classmethod(previous.FeedbackBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(previous.FeedbackBrowserTests.tearDownClass.__func__)
    setUp = previous.FeedbackBrowserTests.setUp
    tearDown = previous.FeedbackBrowserTests.tearDown

    def panel(self, name):
        return self.page.locator(f'[data-builder-panel="{name}"]')

    def open_panel(self, name):
        if not self.panel(name).evaluate('el => el.open'):
            self.panel(name).locator(':scope > summary').click()

    def test_heading_title_and_section_subtitles(self):
        p = self.page
        p.evaluate('openBuilder()')
        settings = p.locator('.builder-settings')
        self.assertEqual(settings.locator('.builder-heading').inner_text(), 'Build your table.')
        self.assertEqual(settings.locator('#builder-title').count(), 1)
        self.assertEqual(p.evaluate('document.activeElement.id'), 'builder-title')
        self.assertEqual(self.panel('measurements').locator(':scope > summary small').inner_text(), MEASUREMENTS_SUBTITLE)
        self.assertEqual(self.panel('groups').locator(':scope > summary small').inner_text(), GROUPS_SUBTITLE)
        text = settings.inner_text()
        for gone in ['What do you want to check?', 'Need a custom calculation?', 'Change for each farmer', 'Saved & custom measurements',
                     'Start with an example', 'Summarise as', 'Measurement definitions']:
            self.assertNotIn(gone, text)
        self.assertEqual(p.locator('#work-dialog [data-action="concept-help"], #work-dialog .builder-step').count(), 0)
        # No extra help lines inside Measurements or Groups.
        self.open_panel('measurements')
        self.open_panel('groups')
        for name in ['measurements', 'groups']:
            self.assertEqual(self.panel(name).locator('.builder-panel-content > p.help:visible').count(), 0, name)

    def test_sections_collapsed_for_new_and_edit_but_subtitles_visible(self):
        p = self.page
        for call in ['openBuilder()', "openBuilder('crops')"]:
            p.evaluate(call)
            for name in ['measurements', 'groups', 'sources']:
                self.assertFalse(self.panel(name).evaluate('el => el.open'), f'{call} {name}')
                self.assertTrue(self.panel(name).locator(':scope > summary small').is_visible(), f'{call} {name}')
            self.assertEqual(p.locator('[data-builder-panel="examples"]').count(), 0)
            # The title is the only visible field before a section is opened.
            visible = p.locator('.builder-settings').locator('input:visible, select:visible')
            self.assertEqual(visible.count(), 1)
            self.assertEqual(visible.first.get_attribute('id'), 'builder-title')
            p.evaluate('closeWork()')

    def test_examples_are_removed(self):
        p = self.page
        p.evaluate('openBuilder()')
        self.assertEqual(p.locator('[data-action="builder-example"], [data-action="builder-undo-example"], .builder-examples').count(), 0)
        self.assertTrue(p.evaluate("typeof builderExamples === 'undefined' && typeof builderExamplesHTML === 'undefined'"))

    def test_present_keeps_at_least_one_statistic(self):
        p = self.page
        p.evaluate('openBuilder()')
        self.open_panel('measurements')
        self.assertEqual(p.locator('.builder-statistics > span').inner_text(), 'Present')
        p.locator('[data-builder-metric="yield"]').check()
        mean, median = p.locator('[data-builder-stat="mean"]'), p.locator('[data-builder-stat="median"]')
        self.assertTrue(mean.is_checked())
        self.assertTrue(mean.is_disabled(), 'The only statistic cannot be unchecked')
        median.check()
        self.assertFalse(mean.is_disabled())
        mean.uncheck()
        self.assertEqual(p.evaluate('work.draft.stats'), ['median'])
        self.assertTrue(median.is_disabled())
        self.assertFalse(mean.is_disabled())
        # Even a forced change event cannot leave the table without a statistic.
        p.evaluate("""() => {const box = document.querySelector('[data-builder-stat="median"]'); box.disabled = false; box.checked = false;
          box.dispatchEvent(new Event('change', {bubbles: true}));}""")
        self.assertEqual(p.locator('[data-builder-stat]:checked').count(), 1)
        self.assertEqual(p.evaluate('readBuilder(), work.draft.stats.length'), 1)
        self.assertEqual(p.locator('#work-error').inner_text(), '')
        # Count-only tables keep their fixed statistic.
        p.locator('[data-builder-metric="count"]').check()
        self.assertEqual(p.evaluate('work.draft.stats'), ['count'])
        self.assertEqual(p.locator('[data-builder-stat]:not([disabled])').count(), 0)

    def test_renamed_buttons(self):
        p = self.page
        p.evaluate('openBuilder()')
        self.open_panel('measurements')
        advanced = self.panel('measurements').locator('[data-action="builder-definitions"]')
        self.assertEqual(advanced.inner_text(), 'Add and review measurements (Advanced)')
        self.open_panel('sources')
        comparison = p.locator('.builder-comparison')
        self.assertTrue(comparison.locator(':scope > summary').inner_text().startswith('Advanced comparison settings'))
        self.assertFalse(comparison.evaluate('el => el.open'))
        self.assertNotIn('Comparing', self.panel('sources').inner_text())
        chevron = comparison.locator(':scope > summary').evaluate("el => getComputedStyle(el, '::before').content")
        self.assertNotIn(chevron, ['none', 'normal', '""'])
        comparison.locator(':scope > summary').click()
        self.assertTrue(comparison.evaluate('el => el.open'))
        self.assertTrue(p.locator('#builder-source-mode').is_visible())

    def test_groups_start_from_one_list_without_axis_boxes(self):
        # Round 3: the separate Rows / Columns boxes (each with its own search) became one list of all groups.
        p = self.page
        p.evaluate('openBuilder()')
        groups = self.panel('groups')
        self.assertEqual(p.locator('[data-axis-card], [data-builder-axis-search]').count(), 0)
        self.assertEqual(groups.locator('input[type=search]').count(), 1)
        self.open_panel('groups')
        p.locator('#fields-search').fill('Region')
        p.locator('#fields-list .group-choice:visible [data-action="add-axis-field"]').first.click()
        self.assertEqual(len(p.evaluate('work.draft.rows')), 1)
        self.assertTrue(groups.evaluate('el => el.open'))
        # The narrow pane holds the editors without horizontal overflow.
        overflow = p.locator('.builder-settings').evaluate('el => el.scrollWidth - el.clientWidth')
        self.assertLessEqual(overflow, 0)

    def test_new_table_selects_every_source_and_edit_keeps_saved(self):
        p = self.page
        p.evaluate('openBuilder()')
        all_ids = p.evaluate('dataSources().map(s => s.id)')
        self.assertGreater(len(all_ids), 1)
        self.assertEqual(p.evaluate('work.draft.sources.ids'), all_ids)
        self.open_panel('sources')
        self.assertEqual(p.locator('[data-builder-source]:checked').count(), len(all_ids))
        p.evaluate('closeWork()')
        p.evaluate("const t = tableById('crops'); t.sources = sourceSettings(t); t.sources.ids = ['e']; t.change = false; persist()")
        p.evaluate("openBuilder('crops')")
        self.assertEqual(p.evaluate('work.draft.sources.ids'), ['e'])

    def test_right_pane_is_only_the_preview(self):
        p = self.page
        p.evaluate('openBuilder()')
        pane = p.locator('.builder-preview-panel')
        self.assertTrue(pane.locator('#builder-preview').is_visible())
        visible_children = pane.evaluate("el => [...el.children].filter(c => !c.hidden && getComputedStyle(c).display !== 'none').map(c => c.id)")
        self.assertEqual(visible_children, ['builder-preview-header', 'builder-preview'])
        text = p.locator('#work-dialog').inner_text()
        for gone in ['Shape your table', 'Choose measurements', 'Live preview', 'Refresh', 'Survey questions & raw data',
                     'Create the table when its structure', 'Choose a measurement, then add groups']:
            self.assertNotIn(gone, text)
        self.assertEqual(p.locator('.builder-preview-slots, .preview-slot, [data-action="builder-raw-data"], .builder-save-note').count(), 0)
        actions = p.locator('#work-actions button:visible').all_inner_texts()
        self.assertEqual(actions, ['Cancel', 'Create table'])

    def test_layouts_at_desktop_and_phone_widths(self):
        p = self.page
        for width, height in [(1440, 1000), (390, 844)]:
            p.set_viewport_size({'width': width, 'height': height})
            p.evaluate('openBuilder()')
            for name in ['measurements', 'groups', 'sources']:
                self.open_panel(name)
            p.locator('[data-builder-metric="yield"]').check()
            p.locator('#fields-list .field-row[data-field="q:crop"]').click()
            self.assertLessEqual(p.evaluate('document.documentElement.scrollWidth'), width)
            self.assertLessEqual(p.locator('#work-dialog').evaluate('el => el.scrollWidth'), width)
            settings, preview = p.locator('.builder-settings').bounding_box(), p.locator('.builder-preview-panel').bounding_box()
            if width == 1440:
                self.assertLess(settings['width'], 420, 'The left pane stays narrow')
                self.assertGreater(preview['width'], settings['width'] * 2, 'The preview owns the dialog')
            else:
                self.assertGreaterEqual(preview['y'], settings['y'] + settings['height'] - 1, 'The preview stacks below')
                jump = p.locator('[data-action="builder-jump-preview"]')
                self.assertTrue(jump.is_visible())
                jump.click()
                self.assertTrue(p.evaluate("document.activeElement.classList.contains('builder-preview-panel')"))
            p.screenshot(path=str(Path(gettempdir()) / f'jdc-simple-builder-left-{width}.png'))
            p.evaluate('closeWork()')


if __name__ == '__main__':
    unittest.main()
