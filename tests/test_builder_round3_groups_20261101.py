"""Builder round 3 (1 November): Groups start from one list of all groups; rows or columns is a switch afterwards.

Client feedback: "the user will prefer to start from all groups, and decide later if columns or rows",
and the "Group by individual numeric values" checkbox is removed.

Run with the existing suite: python -m unittest discover -s tests -v
"""
import unittest
from pathlib import Path
from tempfile import gettempdir

import test_feedback_20260922 as previous

GROUPS_SUBTITLE = "Groups are the table's rows and columns, such as Crop or Region. You can drag groups directly to the table preview."
ARTIFACTS = Path(gettempdir()) / "jdc-collab-20261101" / "round3-groups"


class BuilderRound3GroupsTests(unittest.TestCase):
    setUpClass = classmethod(previous.FeedbackBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(previous.FeedbackBrowserTests.tearDownClass.__func__)
    setUp = previous.FeedbackBrowserTests.setUp
    tearDown = previous.FeedbackBrowserTests.tearDown
    drag = previous.FeedbackBrowserTests.drag

    def open_groups(self, table=None):
        p = self.page
        p.evaluate(f"openBuilder({repr(table) if table else ''})")
        panel = p.locator('[data-builder-panel="groups"]')
        if not panel.evaluate('el => el.open'):
            panel.locator(':scope > summary').click()
        return panel

    def add(self, field):
        self.page.locator(f'#fields-list .field-row[data-field="{field}"]').click()

    def item(self, field):
        return self.page.locator(f'.table-group[data-field="{field}"]')

    def axes(self):
        return self.page.evaluate('[work.draft.rows, work.draft.columns]')

    def test_one_list_of_all_groups(self):
        p = self.page
        panel = self.open_groups()
        self.assertEqual(panel.locator(':scope > summary small').inner_text(), GROUPS_SUBTITLE)
        # No separate Rows / Columns boxes: one search and one list holding every allowed group.
        self.assertEqual(p.locator('[data-axis-card], [data-builder-axis-search], .group-to-column').count(), 0)
        self.assertEqual(panel.locator('input[type=search]').count(), 1)
        listed = p.locator('#fields-list .field-row').evaluate_all('els => els.map(e => e.dataset.field)')
        self.assertEqual(sorted(listed), sorted(p.evaluate('builderCategoryFields().map(f => f.id)')))
        # Each group has one Add action, which is also the drag handle.
        for row in p.locator('#fields-list .field-row').all()[:5]:
            self.assertEqual(row.get_attribute('data-action'), 'add-axis-field')
            self.assertEqual(row.get_attribute('draggable'), 'true')
            self.assertTrue(row.get_attribute('aria-label').startswith('Add '))
        self.assertEqual(p.locator('#fields-list .group-choice').first.locator('button').count(), 1)
        # Nothing is in the table yet, so "In your table" is not shown.
        self.assertEqual(p.locator('.table-groups').count(), 0)
        # Search filters the one list.
        p.locator('#fields-search').fill('region')
        visible = p.locator('#fields-list .group-choice:visible .field-row-label').all_inner_texts()
        self.assertTrue(visible)
        self.assertTrue(all('region' in text.lower() for text in visible))

    def test_add_puts_group_in_rows_and_switch_moves_it(self):
        p = self.page
        self.open_groups()
        self.add('q:crop')
        self.assertEqual(self.axes(), [['q:crop'], []])
        self.assertEqual(p.locator('#fields-list [data-field="q:crop"]').count(), 0, 'An added group leaves the list')
        self.assertEqual(p.locator('#table-groups-heading').inner_text(), 'In your table')
        switch = self.item('q:crop').locator('.axis-switch')
        self.assertEqual(switch.get_attribute('role'), 'group')
        self.assertEqual(switch.locator('button').all_inner_texts(), ['Rows', 'Columns'])
        self.assertEqual(switch.locator('[aria-pressed="true"]').inner_text(), 'Rows')
        # Switching to Columns moves it, and keyboard focus stays on the switch.
        switch.locator('[data-to="columns"]').click()
        self.assertEqual(self.axes(), [[], ['q:crop']])
        self.assertEqual(self.item('q:crop').locator('[aria-pressed="true"]').inner_text(), 'Columns')
        self.assertEqual(p.evaluate('document.activeElement.dataset.to'), 'columns')
        # Pressing the side already chosen changes nothing; the keyboard can switch back.
        self.item('q:crop').locator('[data-to="columns"]').click()
        self.assertEqual(self.axes(), [[], ['q:crop']])
        self.item('q:crop').locator('[data-to="rows"]').focus()
        p.keyboard.press('Enter')
        self.assertEqual(self.axes(), [['q:crop'], []])
        self.assertEqual(p.locator('#work-error').inner_text(), '')
        # The preview follows: crop is the row header.
        self.assertGreater(p.locator('#builder-preview th[data-preview-axis="rows"]').count(), 0)
        self.assertEqual(p.locator('#builder-preview th[data-preview-axis="columns"]').count(), 0)

    def test_order_and_remove(self):
        p = self.page
        self.open_groups()
        for field in ['q:crop', 'q:region', 'q:gender']:
            self.add(field)
        self.assertEqual(self.axes(), [['q:crop', 'q:region', 'q:gender'], []])
        # Rows come first in the list, in table order; each item has clear labels.
        self.assertEqual(p.locator('.table-group').evaluate_all('els => els.map(e => e.dataset.field)'), ['q:crop', 'q:region', 'q:gender'])
        self.assertTrue(self.item('q:crop').locator('[data-direction="-1"]').is_disabled())
        self.assertTrue(self.item('q:gender').locator('[data-direction="1"]').is_disabled())
        self.item('q:gender').get_by_label('Move Gender up (row 3)').click()
        self.assertEqual(self.axes()[0], ['q:crop', 'q:gender', 'q:region'])
        self.assertEqual(p.evaluate('document.activeElement.closest(".table-group")?.dataset.field'), 'q:gender')
        self.item('q:crop').get_by_label('Move Crop down (row 1)').click()
        self.assertEqual(self.axes()[0], ['q:gender', 'q:crop', 'q:region'])
        # Order is within an axis: a column moves among columns only.
        self.item('q:region').locator('[data-to="columns"]').click()
        self.assertEqual(self.axes(), [['q:gender', 'q:crop'], ['q:region']])
        self.assertTrue(self.item('q:region').locator('[data-direction="-1"]').is_disabled())
        self.assertTrue(self.item('q:region').locator('[data-direction="1"]').is_disabled())
        # Remove puts the group back in the list.
        self.item('q:crop').get_by_label('Remove Crop from the table').click()
        self.assertEqual(self.axes(), [['q:gender'], ['q:region']])
        self.assertEqual(p.locator('#fields-list .field-row[data-field="q:crop"]').count(), 1)
        self.assertEqual(p.evaluate('document.activeElement.dataset.action'), 'remove-level')

    def test_three_per_axis_limit_message(self):
        p = self.page
        self.open_groups()
        for field in ['q:crop', 'q:region', 'q:gender']:
            self.add(field)
        note = p.locator('.table-groups-note')
        self.assertEqual(note.inner_text(), 'Rows are full (3). New groups go to columns.')
        # With rows full, Add goes to columns.
        nxt = p.locator('#fields-list .field-row').first.get_attribute('data-field')
        p.locator('#fields-list .field-row').first.click()
        self.assertEqual(self.axes()[1], [nxt])
        # A row cannot switch into full columns, and nothing moves.
        p.evaluate("work.draft.columns=[...work.draft.columns, ...builderAxisChoices('columns').slice(0, 2).map(f => f.id)]; renderBuilder()")
        self.assertEqual(len(self.axes()[1]), 3)
        self.assertEqual(note.inner_text(), 'Rows and columns are full (3 each). Remove a group to add another.')
        before = self.axes()
        self.item('q:crop').locator('[data-to="columns"]').click()
        self.assertEqual(self.axes(), before)
        self.assertIn('three group levels', p.locator('#work-error').inner_text())
        # Add says plainly why it cannot add.
        p.locator('#fields-list .field-row').first.click()
        self.assertEqual(self.axes(), before)
        self.assertEqual(p.locator('#work-error').inner_text(), 'Rows and columns each hold up to 3 groups. Remove a group to add another.')

    def test_drag_from_list_to_preview_still_adds(self):
        p = self.page
        self.open_groups()
        self.drag('#fields-list .field-row[data-field="q:crop"]', '#builder-preview tbody th.row-axis-header')
        self.assertEqual(self.axes(), [['q:crop'], []])
        self.drag('#fields-list .field-row[data-field="q:gender"]', '#builder-preview thead th.skeleton-hint')
        self.assertEqual(self.axes(), [['q:crop'], ['q:gender']])
        # A chosen group's handle drags it from "In your table" to the other axis in the preview.
        self.drag('.table-group[data-field="q:gender"] .axis-drag-handle', '#builder-preview tbody th.row-axis-header')
        self.assertEqual(self.axes(), [['q:crop', 'q:gender'], []])
        # Dropping one chosen group on another reorders within that axis.
        self.drag('.table-group[data-field="q:gender"] .axis-drag-handle', '.table-group[data-field="q:crop"]')
        self.assertEqual(self.axes(), [['q:gender', 'q:crop'], []])

    def test_numeric_groups_checkbox_gone_and_saved_numeric_group_edits(self):
        p = self.page
        panel = self.open_groups()
        self.assertEqual(p.locator('#builder-numeric-groups').count(), 0)
        self.assertNotIn('numeric values', panel.inner_text())
        self.assertEqual(p.locator('#fields-list [data-field="b:Age"]').count(), 0, 'Numbers are measurements, not new groups')
        p.evaluate('closeWork()')
        # A saved table that already groups by a number keeps it, and it still edits.
        p.evaluate("const t = tableById('crops'); t.rows = ['e:Crop', 'b:Age']; persist()")
        self.open_groups('crops')
        self.assertEqual(self.item('b:Age').count(), 1)
        self.assertIn('Age', self.item('b:Age').inner_text())
        self.item('b:Age').locator('[data-to="columns"]').click()
        self.assertEqual(self.axes(), [['e:Crop'], ['b:Age']])
        self.assertEqual(p.locator('#work-error').inner_text(), '')
        p.locator('[data-action="apply-builder"]').click()
        self.assertEqual(p.evaluate("tableById('crops').columns"), ['b:Age'])
        self.assertEqual(p.evaluate("tableById('crops').rows"), ['e:Crop'])

    def test_layout_at_desktop_and_phone_widths(self):
        p = self.page
        ARTIFACTS.mkdir(parents=True, exist_ok=True)
        for width, height in [(1440, 1000), (390, 844)]:
            p.set_viewport_size({'width': width, 'height': height})
            panel = self.open_groups()
            for field in ['q:crop', 'q:region']:
                self.add(field)
            self.item('q:region').locator('[data-to="columns"]').click()
            self.assertLessEqual(p.evaluate('document.documentElement.scrollWidth'), width)
            self.assertLessEqual(p.locator('.builder-settings').evaluate('el => el.scrollWidth - el.clientWidth'), 0)
            # Every control in an item is inside the pane and big enough to hit.
            pane = p.locator('.builder-settings').bounding_box()
            for button in self.item('q:crop').locator('button').all():
                box = button.bounding_box()
                self.assertLessEqual(box['x'] + box['width'], pane['x'] + pane['width'] + 0.5)
                self.assertGreaterEqual(box['height'], 26 if width == 1440 else 34)
            panel.scroll_into_view_if_needed()
            panel.screenshot(path=str(ARTIFACTS / f'groups-{width}.png'))
            p.screenshot(path=str(ARTIFACTS / f'builder-{width}.png'))
            p.evaluate('closeWork()')


if __name__ == '__main__':
    unittest.main()
