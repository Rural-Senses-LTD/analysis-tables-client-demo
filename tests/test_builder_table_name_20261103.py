"""Table creation always shows the table's name above the preview (3 November 2026).

Run with the existing suite: python -m unittest discover -s tests -v
"""
import unittest

import test_feedback_20260922 as previous


class BuilderTableNameTests(unittest.TestCase):
    setUpClass = classmethod(previous.FeedbackBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(previous.FeedbackBrowserTests.tearDownClass.__func__)
    setUp = previous.FeedbackBrowserTests.setUp
    tearDown = previous.FeedbackBrowserTests.tearDown

    def name(self):
        return self.page.locator('#builder-preview-title')

    def test_name_follows_the_title_field(self):
        p = self.page
        p.evaluate("openBuilder()")
        self.assertTrue(self.name().is_visible())
        self.assertEqual(self.name().inner_text(), 'New analysis')
        p.locator('#builder-title').fill('Yield by crop')
        self.assertEqual(self.name().inner_text(), 'Yield by crop')
        # Before and after a measurement, and with a message instead of a table, the name stays.
        p.evaluate("work.draft.rows.push('q:crop'); renderBuilder()")
        self.assertEqual(self.name().inner_text(), 'Yield by crop')
        p.evaluate("readBuilder(); builderUseMeasurement('yield'); renderBuilder()")
        self.assertEqual(self.name().inner_text(), 'Yield by crop')
        p.locator('#builder-title').fill('   ')
        self.assertEqual(self.name().inner_text(), 'Untitled table')
        self.assertIn('is-empty', self.name().get_attribute('class'))
        p.locator('#builder-title').fill('Yield by crop')
        self.assertNotIn('is-empty', self.name().get_attribute('class'))

    def test_editing_a_saved_table_shows_its_name(self):
        p = self.page
        p.evaluate("openBuilder('crops')")
        self.assertEqual(self.name().inner_text(), p.evaluate("tableById('crops').title"))

    def test_name_stays_visible_while_the_preview_scrolls(self):
        p = self.page
        p.set_viewport_size({'width': 1440, 'height': 800})
        p.evaluate("openBuilder(); work.draft.rows = ['q:crop']; work.draft.columns = ['q:gender']; renderBuilder()")
        panel = p.locator('.builder-preview-panel')
        top = panel.bounding_box()['y']
        p.evaluate("document.querySelector('.builder-preview-panel').scrollTop = 800")
        box = self.name().bounding_box()
        self.assertGreater(p.evaluate("document.querySelector('.builder-preview-panel').scrollTop"), 0)
        self.assertGreaterEqual(box['y'], top - 1, 'The name is pinned at the top of the preview')
        self.assertLess(box['y'], top + 80)
        previous.ARTIFACTS.mkdir(parents=True, exist_ok=True)
        p.screenshot(path=str(previous.ARTIFACTS / '20261103-builder-name-1440.png'))
        p.set_viewport_size({'width': 390, 'height': 844})
        p.evaluate("renderBuilder()")
        self.assertTrue(self.name().is_visible() or self.name().count() == 1)
        p.screenshot(path=str(previous.ARTIFACTS / '20261103-builder-name-390.png'), full_page=False)


if __name__ == '__main__':
    unittest.main()
