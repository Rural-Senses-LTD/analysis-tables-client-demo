"""Regressions for the 22 October TOV working session (field names, filters, numeric search hint).

Run with the existing suite: python -m unittest discover -s tests -v
"""
import unittest

import test_feedback_20260922 as previous


class FieldsAndFiltersTests(unittest.TestCase):
    setUpClass = classmethod(previous.FeedbackBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(previous.FeedbackBrowserTests.tearDownClass.__func__)
    setUp = previous.FeedbackBrowserTests.setUp
    tearDown = previous.FeedbackBrowserTests.tearDown

    def add_filter(self, search):
        p = self.page
        p.locator('[data-action="toggle-filter-picker"]').first.click()
        p.locator('#field-search').fill(search)
        p.locator('#field-results [role=option]').first.click()

    def test_new_filter_is_brought_into_view_and_marked(self):
        p = self.page
        p.evaluate('openFilters(state.tables[0].id)')
        for name in ['Baseline Crop', 'Crop', 'Region', 'Wareda']:
            self.add_filter(name)
            visible = p.evaluate("""(() => {
              const body = document.querySelector('#filter-body');
              const items = [...body.querySelectorAll('.filter-condition')];
              const last = items[items.length - 1];
              const box = last.getBoundingClientRect(), view = body.getBoundingClientRect();
              return {inView: box.top >= view.top - 1 && box.bottom <= view.bottom + 1, marked: last.classList.contains('just-added'),
                      focusInside: last.contains(document.activeElement), count: items.length};
            })()""")
            self.assertTrue(visible['inView'], f'{name} filter is below the fold')
            self.assertTrue(visible['marked'])
            self.assertTrue(visible['focusInside'])

    def test_filter_operator_wording_is_plain(self):
        p = self.page
        p.evaluate('openFilters(state.tables[0].id)')
        self.add_filter('Crop')
        options = p.get_by_label('Match answers', exact=True).locator('option').all_inner_texts()
        self.assertEqual(options, ['Keep only the selected answers', 'Remove the selected answers', 'Same answer as another field'])

    def test_equal_field_filter_still_matches_same_crop_after_rename(self):
        p = self.page
        p.evaluate('openFilters(state.tables[0].id)')
        self.add_filter('Baseline Crop')
        p.get_by_label('Match answers', exact=True).select_option('eqField')
        p.get_by_label('Comparison field', exact=True).select_option('e:Crop')
        preview = p.locator('#filter-preview').inner_text()
        self.assertRegex(preview, r'^\d+ of \d+ records match')

    def test_same_question_shows_one_name_with_a_source_tag(self):
        p = self.page
        labels = p.evaluate("""filterFields('source').filter(f => /crop/i.test(f.label)).map(fieldOptionLabel)""")
        self.assertIn('Crop · Baseline', labels)
        self.assertIn('Crop · Endline', labels)
        self.assertIn('Crop group · Baseline', labels)
        self.assertFalse([x for x in labels if 'Baseline Crop · Baseline' in x or 'Crop · Endline · Endline' in x])

    def test_group_search_for_a_number_points_to_measurements(self):
        p = self.page
        p.evaluate('openBuilder()')
        panel = p.locator('[data-builder-panel="groups"]')
        if not panel.evaluate('el => el.open'):
            panel.locator(':scope > summary').click()
        p.locator('#fields-search').fill('yield')
        empty = p.locator('#fields-empty')
        self.assertTrue(empty.is_visible())
        self.assertIn('is a number, not a group', empty.inner_text())
        self.assertIn('Measurements', empty.inner_text())
        p.locator('#fields-search').fill('zzzz-no-such')
        self.assertEqual(empty.inner_text(), 'No groups match your search.')

    def test_source_mode_wording(self):
        p = self.page
        p.evaluate('openBuilder()')
        options = p.locator('#builder-source-mode option').evaluate_all('els => els.map(e => e.textContent)')
        self.assertEqual(options, ['Side by side: one column per source', 'Combined: pool all sources into one result'])


    def test_variety_and_project_join_exact_names_only(self):
        p = self.page
        result = p.evaluate("""(() => {
          const rows = DATA.farmers.filter(f => f.b).map(f => f.b.values);
          const names = {};
          rows.forEach(v => { const n = String(v.Name || '').replace(/\s+/g, ' ').trim().toLowerCase(); names[n] = (names[n] || 0) + 1; });
          const duplicated = rows.filter(v => names[String(v.Name || '').replace(/\s+/g, ' ').trim().toLowerCase()] > 1);
          const fields = ['b:Variety', 'b:Project'].map(id => fieldInfo(id));
          return {variety: rows.filter(v => v.Variety).length, project: rows.filter(v => v.Project).length, total: rows.length,
                  duplicatedFilled: duplicated.filter(v => v.Variety || v.Project).length, fields: fields.map(f => f && f.type),
                  varietyOptions: fieldInfo('b:Variety').options.length};
        })()""")
        self.assertEqual((result['variety'], result['project'], result['total']), (208, 208, 254))
        self.assertEqual(result['duplicatedFilled'], 0, 'Duplicate farmer names must stay blank')
        self.assertEqual(result['fields'], ['category', 'category'])
        self.assertGreater(result['varietyOptions'], 5)

    def test_project_from_profile_list_matches_endline_project(self):
        p = self.page
        mismatches = p.evaluate("""DATA.farmers.filter(f => f.b && f.e && f.b.values.Project && f.e.values.Project && f.b.values.Project !== f.e.values.Project).length""")
        self.assertLessEqual(mismatches, 1)

    def test_table_can_group_by_variety_and_original_values_unchanged(self):
        p = self.page
        counts = p.evaluate("""(() => {
          const t = clone(state.tables[0]);
          t.rows = ['b:Variety'];
          const data = calculate(t);
          return {rows: data.rows.length, sources: DATA.inputs.length, fingerprint: DATA.fingerprint};
        })()""")
        self.assertGreater(counts['rows'], 5)
        self.assertEqual(counts['sources'], 3)
        self.assertEqual(counts['fingerprint'], '626fc710f90d3f6d4b50ad3d966d35eba9ba244065fdfb377342cb369ef289a3')


if __name__ == '__main__':
    unittest.main()
