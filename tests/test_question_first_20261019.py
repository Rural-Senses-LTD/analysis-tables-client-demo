"""Question-first builder, calculation and recovery regressions.

Run with the existing suite: python -m unittest discover -s tests -v
"""
import unittest
from pathlib import Path
from tempfile import gettempdir

import test_feedback_20260922 as previous


class QuestionFirstTests(unittest.TestCase):
    setUpClass = classmethod(previous.FeedbackBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(previous.FeedbackBrowserTests.tearDownClass.__func__)
    setUp = previous.FeedbackBrowserTests.setUp
    tearDown = previous.FeedbackBrowserTests.tearDown
    drag = previous.FeedbackBrowserTests.drag

    def open_panel(self, name):
        panel = self.page.locator(f'[data-builder-panel="{name}"]')
        if not panel.evaluate('el => el.open'):
            panel.locator(':scope > summary').click()

    def test_empty_draft_and_built_table_use_real_records(self):
        p = self.page
        p.evaluate('openBuilder()')
        before = p.evaluate('state.tables.length')
        self.assertEqual(p.evaluate('work.draft.metrics'), [])
        self.assertEqual(p.locator('#work-error').inner_text(), '')
        p.locator('[data-action="apply-builder"]').click()
        self.assertEqual(p.evaluate('state.tables.length'), before)
        self.assertIn('measurement', p.locator('#work-error').inner_text())
        # Build "average age by gender" from Baseline only, through the left pane.
        p.locator('#builder-title').fill('Average age by gender')
        for name in ['measurements', 'groups', 'sources']:
            self.open_panel(name)
        p.locator('[data-builder-source="e"]').uncheck()
        p.locator('[data-builder-metric="b:Age"]').check()
        p.locator('[data-builder-axis-search="rows"]').fill('Gender')
        p.locator('[data-axis-results="rows"] [data-action="add-axis-field"]').first.click()
        self.assertEqual(p.locator('#work-error').inner_text(), '')
        self.assertGreater(p.locator('#builder-preview td').count(), 0)
        result = p.evaluate("""()=>{
          const data=calculate(builderCandidate());
          return data.rows.map(row=>({actual:row.cells[0].value,expected:row.group.records.reduce((s,r)=>s+(finite(raw(r,'b:Age'))?raw(r,'b:Age'):0),0)/row.group.records.filter(r=>finite(raw(r,'b:Age'))).length}));
        }""")
        self.assertTrue(result)
        for row in result:
            self.assertAlmostEqual(row['actual'], row['expected'])
        p.locator('[data-action="apply-builder"]').click()
        p.reload()
        self.assertEqual(p.evaluate('state.tables[0].metrics'), ['b:Age'])
        self.assertEqual(p.evaluate('state.tables[0].sources.ids'), ['b'])

    def test_groups_numbers_collapsing_and_search_survive_changes(self):
        p = self.page
        p.evaluate('openBuilder()')
        self.open_panel('measurements')
        self.open_panel('groups')
        self.assertEqual(p.locator('#fields-list .field-row[data-field="b:Age"]').count(), 0)
        self.assertEqual(p.locator('[data-builder-metric="b:Age"]').count(), 1)
        p.locator('#builder-numeric-groups').check()
        self.assertEqual(p.locator('#fields-list .field-row[data-field="b:Age"]').count(), 1)
        p.locator('#builder-numeric-groups').uncheck()
        p.locator('#fields-search').fill('region')
        p.locator('[data-builder-metric="yield"]').check()
        visible = p.locator('#fields-list .group-choice:visible').all_text_contents()
        self.assertTrue(all('Region' in text for text in visible))
        p.locator('[data-builder-panel="measurements"] > summary').click()
        p.locator('#fields-list .field-row[data-field="q:region"]').click()
        self.assertFalse(p.locator('[data-builder-panel="measurements"]').evaluate('el=>el.open'))
        self.assertEqual(p.locator('#fields-search').input_value(), 'region')

    def test_horizontal_drag_preview_headers_and_keyboard_alternative(self):
        p = self.page
        p.evaluate('openBuilder()')
        self.open_panel('measurements')
        self.open_panel('groups')
        p.locator('[data-builder-metric="yield"]').check()
        self.drag('#fields-list .field-row[data-field="q:crop"]', '[data-axis-card="rows"]')
        self.drag('[data-axis="rows"] .axis-drag-handle', '[data-axis-card="columns"]')
        self.assertEqual(p.evaluate('work.draft.rows'), [])
        self.assertEqual(p.evaluate('work.draft.columns'), ['q:crop'])
        self.drag('#builder-preview th[data-preview-axis="columns"]', '[data-axis-card="rows"]')
        self.assertEqual(p.evaluate('work.draft.rows'), ['q:crop'])
        self.drag('#builder-preview th[data-preview-axis="rows"]', '#builder-preview thead th.source-heading')
        self.assertEqual(p.evaluate('work.draft.columns'), ['q:crop'])
        p.locator('[data-axis-card="columns"] [data-action="transfer-level"]').focus()
        p.keyboard.press('Enter')
        self.assertEqual(p.evaluate('work.draft.rows'), ['q:crop'])
        # Reject a group in the values area without mutating either axis.
        snapshot = p.evaluate('JSON.stringify(work.draft)')
        self.drag('[data-preview-axis="rows"]', '#builder-preview tbody td')
        self.assertEqual(p.evaluate('JSON.stringify(work.draft)'), snapshot)
        # Reject a fourth level without removing it from its original axis.
        p.evaluate("work.draft.columns=['b:Gender','b:Region','b:Woreda'];renderBuilder()")
        snapshot = p.evaluate('JSON.stringify(work.draft)')
        self.drag('[data-axis="rows"] .axis-drag-handle', '[data-axis-card="columns"]')
        self.assertEqual(p.evaluate('JSON.stringify(work.draft)'), snapshot)
        self.assertIn('three group levels', p.locator('#toast').inner_text())

    def test_change_basis_explicit_and_persisted_in_table_and_export(self):
        p = self.page
        p.evaluate('openBuilder()')
        self.open_panel('measurements')
        p.locator('[data-builder-metric="net"]').check()
        self.open_panel('sources')
        p.locator('.builder-comparison > summary').click()
        p.locator('[data-builder-bool="change"]').check()
        self.assertEqual(p.locator('#builder-change-stat').input_value(), '')
        self.assertIn('Choose how', p.locator('#work-error').inner_text())
        p.locator('[data-action="apply-builder"]').click()
        self.assertTrue(p.locator('#work-dialog').is_visible())
        p.locator('#builder-change-stat').select_option('median')
        self.assertEqual(p.locator('#work-error').inner_text(), '')
        self.assertIn('Change in medians (%)', p.locator('#builder-preview').inner_text())
        p.locator('#builder-title').fill('Median comparison')
        p.locator('[data-action="apply-builder"]').click()
        p.reload()
        self.assertEqual(p.evaluate('state.tables[0].changeStat'), 'median')
        self.assertIn('Change in medians (%)', p.locator('.table-card').first.inner_text())
        self.assertIn('median of Endline / median of Baseline', p.evaluate('calculationNote(state.tables[0])'))
        with p.expect_download() as download:
            p.evaluate('exportCSV(state.tables[0])')
        csv = Path(download.value.path()).read_text(encoding='utf-8-sig')
        self.assertIn('Change in medians (%)', csv)
        error = p.evaluate("""()=>{const saved=clone(state);saved.tables[0].changeStat='not-a-statistic';try{validateState(saved);return ''}catch(e){return e.message}}""")
        self.assertIn('valid % change', error)

    def test_change_math_with_missing_records_and_zero_denominator(self):
        result = self.page.evaluate("""()=>{
          const row=(uid,b,e)=>({uid,b:{values:{'Net income':b}},...(e===null?{}:{e:{values:{'Net Income':e}}})});
          const rows=[row('a',100,400),row('b',300,null)];
          const value=(records,stat)=>cell(records,'net',{stat:'change',changeStat:stat,from:'b',to:'e'}).value;
          return {mean:value(rows,'mean'),sum:value(rows,'sum'),median:value([row('a',100,200),row('b',100,200),row('c',800,400)],'median'),zero:value([row('z',0,100)],'sum'),missing:value([row('m',100,null)],'sum'),legacy:cell(rows,'net',{stat:'change',from:'b',to:'e'}).value};
        }""")
        self.assertEqual(result, {'mean':100,'sum':0,'median':100,'zero':None,'missing':None,'legacy':100})

    def test_count_mode_switches_without_averaging_counts(self):
        p = self.page
        p.evaluate('openBuilder()')
        self.open_panel('measurements')
        p.locator('[data-builder-metric="count"]').check()
        self.assertEqual(p.evaluate('work.draft.stats'), ['count'])
        p.locator('[data-builder-metric="net"]').check()
        self.assertEqual(p.evaluate('work.draft.metrics'), ['net'])
        self.assertEqual(p.evaluate('work.draft.stats'), ['mean'])
        p.locator('[data-builder-metric="yield"]').check()
        self.assertEqual(p.evaluate('work.draft.metrics'), ['net', 'yield'])
        self.drag('[data-drag-kind="measurement"][data-field="count"]', '#builder-preview tbody td')
        self.assertEqual(p.evaluate('work.draft.metrics'), ['count'])
        self.drag('[data-drag-kind="measurement"][data-field="net"]', '#builder-preview tbody td')
        self.assertEqual(p.evaluate('work.draft.metrics'), ['net'])
        self.assertEqual(p.evaluate('work.draft.stats'), ['mean'])
        self.assertEqual(p.locator('#work-error').inner_text(), '')

    def test_advanced_measurements_round_trip_preserves_draft(self):
        p = self.page
        p.evaluate('openBuilder()')
        p.locator('#builder-title').fill('Individual changes')
        self.open_panel('measurements')
        p.get_by_role('button', name='Add and review measurements (Advanced)').click()
        self.assertEqual(p.locator('#work-title').inner_text(), 'Categories & Measurements')
        self.assertEqual(p.locator('[data-action="definition-tab"][aria-selected="true"]').get_attribute('data-tab'), 'measurements')
        p.locator('[data-action="return-builder"]').click()
        self.assertEqual(p.locator('#builder-title').input_value(), 'Individual changes')
        self.assertTrue(p.locator('[data-builder-panel="measurements"]').evaluate('el=>el.open'))

    def test_mobile_keyboard_reduced_motion_and_preview_access(self):
        p = self.page
        p.emulate_media(reduced_motion='reduce')
        for width in [390, 320]:
            p.set_viewport_size({'width':width,'height':844})
            p.evaluate('openBuilder()')
            self.open_panel('measurements')
            p.locator('[data-builder-metric="count"]').check()
            p.locator('[data-action="builder-jump-preview"]').focus()
            p.keyboard.press('Enter')
            self.assertTrue(p.evaluate("document.activeElement.classList.contains('builder-preview-panel')"))
            self.assertLessEqual(p.evaluate('document.documentElement.scrollWidth'), width)
            self.assertLessEqual(p.locator('#work-dialog').evaluate('el=>el.scrollWidth'), width)
            for _ in range(8):
                p.keyboard.press('Tab')
                self.assertTrue(p.evaluate("document.activeElement.closest('#work-dialog')!==null"))
            p.screenshot(path=str(Path(gettempdir()) / f'jdc-question-first-{width}.png'))
            p.evaluate('closeWork()')


if __name__ == '__main__':
    unittest.main()
