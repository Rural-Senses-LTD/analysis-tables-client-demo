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

    def example(self, name):
        self.open_panel('examples')
        self.page.locator(f'[data-action="builder-example"][data-example="{name}"]').click()

    def test_empty_draft_and_examples_use_real_records(self):
        p = self.page
        p.evaluate('openBuilder()')
        before = p.evaluate('state.tables.length')
        self.assertEqual(p.evaluate('work.draft.metrics'), [])
        self.assertEqual(p.locator('#work-error').inner_text(), '')
        p.locator('[data-action="apply-builder"]').click()
        self.assertEqual(p.evaluate('state.tables.length'), before)
        self.assertIn('measurement', p.locator('#work-error').inner_text())
        p.locator('#builder-title').fill('My unsaved analysis')
        original = p.evaluate('JSON.stringify(work.draft)')
        for name in ['respondents', 'age', 'income', 'officer', 'land']:
            self.example(name)
            self.assertEqual(p.locator('#work-error').inner_text(), '', name)
            self.assertGreater(p.locator('#builder-preview td').count(), 0)
        self.assertIn('Change in means (%)', p.locator('#builder-preview').inner_text())
        # Undo restores the draft from before the most recent example.
        p.evaluate('closeWork();openBuilder()')
        p.locator('#builder-title').fill('My unsaved analysis')
        original = p.evaluate('JSON.stringify(work.draft)')
        self.example('age')
        result = p.evaluate("""()=>{
          const data=calculate(builderCandidate());
          return data.rows.map(row=>({actual:row.cells[0].value,expected:row.group.records.reduce((s,r)=>s+raw(r,'b:Age'),0)/row.group.records.filter(r=>finite(raw(r,'b:Age'))).length}));
        }""")
        for row in result:
            self.assertAlmostEqual(row['actual'], row['expected'])
        p.locator('[data-action="builder-undo-example"]').click()
        self.assertEqual(p.evaluate('JSON.stringify(work.draft)'), original)
        self.example('respondents')
        self.assertEqual(p.evaluate('calculate(builderCandidate()).rows.reduce((n,r)=>n+r.cells[0].value,0)'), p.evaluate("dataSources().find(s=>s.id==='e').records.length"))
        p.locator('[data-action="apply-builder"]').click()
        p.reload()
        self.assertEqual(p.evaluate('state.tables[0].metrics'), ['count'])
        self.assertEqual(p.evaluate('state.tables[0].sources.ids'), ['e'])

    def test_groups_numbers_collapsing_and_search_survive_changes(self):
        p = self.page
        p.evaluate('openBuilder()')
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
        p.locator('#fields-list .field-row[data-field="e:Region"]').click()
        self.assertFalse(p.locator('[data-builder-panel="measurements"]').evaluate('el=>el.open'))
        self.assertEqual(p.locator('#fields-search').input_value(), 'region')

    def test_horizontal_drag_preview_headers_and_keyboard_alternative(self):
        p = self.page
        p.evaluate('openBuilder()')
        p.locator('[data-builder-metric="yield"]').check()
        self.drag('#fields-list .field-row[data-field="e:Crop"]', '[data-axis-card="rows"]')
        self.drag('[data-axis="rows"] .axis-drag-handle', '[data-axis-card="columns"]')
        self.assertEqual(p.evaluate('work.draft.rows'), [])
        self.assertEqual(p.evaluate('work.draft.columns'), ['e:Crop'])
        self.drag('#builder-preview th[data-preview-axis="columns"]', '[data-axis-card="rows"]')
        self.assertEqual(p.evaluate('work.draft.rows'), ['e:Crop'])
        self.drag('#builder-preview th[data-preview-axis="rows"]', '#builder-preview thead th.source-heading')
        self.assertEqual(p.evaluate('work.draft.columns'), ['e:Crop'])
        p.locator('[data-axis-card="columns"] [data-action="transfer-level"]').focus()
        p.keyboard.press('Enter')
        self.assertEqual(p.evaluate('work.draft.rows'), ['e:Crop'])
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

    def test_raw_data_round_trip_preserves_unsaved_draft(self):
        p = self.page
        p.evaluate('openBuilder()')
        self.example('age')
        p.locator('#builder-title').fill('Age draft to keep')
        p.locator('[data-builder-panel="examples"] > summary').click()
        original = p.evaluate('readBuilder();JSON.stringify(work.draft)')
        expected_url = p.evaluate("platformSourceRawDataURL('b')")
        # Verify the configured destination without depending on external authentication.
        self.context.route(expected_url, lambda route: route.fulfill(status=200, body='Raw data destination'))
        with self.context.expect_page() as opened:
            p.locator('[data-action="builder-raw-data"][data-source="b"]').click()
        external = opened.value
        external.wait_for_load_state()
        self.assertEqual(external.url, expected_url)
        self.assertEqual(p.evaluate('JSON.stringify(work.draft)'), original)
        external.close()
        # Sources without a configured URL use the local read-only fallback.
        p.evaluate("delete DATA.platform.sources.b.url")
        p.locator('[data-action="builder-raw-data"][data-source="b"]').click()
        self.assertTrue(p.locator('#raw-data-view').is_visible())
        self.assertIn('Age', p.locator('#raw-data-view').inner_text())
        p.locator('[data-action="raw-data-return"]').click()
        self.assertTrue(p.locator('#work-dialog').is_visible())
        self.assertEqual(p.evaluate('JSON.stringify(work.draft)'), original)
        self.assertFalse(p.locator('[data-builder-panel="examples"]').evaluate('el=>el.open'))
        self.assertEqual(p.locator('#builder-title').input_value(), 'Age draft to keep')
        self.assertEqual(p.evaluate('document.activeElement.dataset.action'), 'builder-raw-data')

    def test_guided_change_definition_returns_to_draft(self):
        p = self.page
        p.evaluate('openBuilder()')
        p.locator('#builder-title').fill('Individual changes')
        p.locator('[data-action="builder-define-change"]').click()
        self.assertEqual(p.locator('#definition-formula').input_value(), '(VAR2 - VAR1) / VAR1 * 100')
        self.assertEqual(p.locator('[data-definition-input]').count(), 2)
        p.locator('[data-action="save-definition"]').click()
        p.locator('[data-action="return-builder"]').click()
        self.assertEqual(p.locator('#builder-title').input_value(), 'Individual changes')
        custom_id = p.evaluate('state.definitions.at(-1).id')
        p.locator(f'[data-builder-metric="{custom_id}"]').check()
        self.assertEqual(p.evaluate('work.draft.periods'), ['value'])
        self.assertEqual(p.locator('#work-error').inner_text(), '')
        p.locator('[data-action="apply-builder"]').click()
        p.reload()
        self.assertEqual(p.evaluate('state.tables[0].metrics'), [custom_id])

    def test_mobile_keyboard_reduced_motion_and_preview_access(self):
        p = self.page
        p.emulate_media(reduced_motion='reduce')
        for width in [390, 320]:
            p.set_viewport_size({'width':width,'height':844})
            p.evaluate('openBuilder()')
            p.locator('[data-builder-metric="count"]').check()
            p.locator('[data-action="builder-jump-preview"]').focus()
            p.keyboard.press('Enter')
            self.assertEqual(p.evaluate('document.activeElement.id'), 'builder-title')
            self.assertLessEqual(p.evaluate('document.documentElement.scrollWidth'), width)
            self.assertLessEqual(p.locator('#work-dialog').evaluate('el=>el.scrollWidth'), width)
            for _ in range(8):
                p.keyboard.press('Tab')
                self.assertTrue(p.evaluate("document.activeElement.closest('#work-dialog')!==null"))
            p.screenshot(path=str(Path(gettempdir()) / f'jdc-question-first-{width}.png'))
            p.evaluate('closeWork()')


if __name__ == '__main__':
    unittest.main()
