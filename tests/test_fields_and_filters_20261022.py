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
        options = p.locator('.filter-mode label span').all_inner_texts()
        self.assertEqual(options, ['Keep selected', 'Remove selected', 'Same as another field'])
        self.assertEqual(p.locator('.filter-mode legend').inner_text(), 'Match answers')

    def test_equal_field_filter_still_matches_same_crop_after_rename(self):
        p = self.page
        p.evaluate('openFilters(state.tables[0].id)')
        self.add_filter('Baseline Crop')
        p.get_by_label('Same as another field', exact=True).check()
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
        result = p.evaluate(r"""(() => {
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


    def test_result_block_chips_collapse_and_zero_state(self):
        p = self.page
        p.evaluate('openFilters(state.tables[0].id)')
        self.assertIn('240', p.locator('#filter-result').inner_text())
        chips = p.locator('.suggest-chip').all_inner_texts()
        self.assertTrue(any(c.startswith('Crop') for c in chips) and any(c.startswith('Region') for c in chips))
        self.assertFalse([c for c in chips if c.startswith(('Name', 'Farmer_UID', 'Match_', 'Outlier_'))])
        p.locator('.suggest-chip', has_text='Region').first.click()
        card = p.locator('.filter-condition').first
        self.assertEqual(card.locator('.condition-summary').inner_text(), 'All answers kept')
        # The result block stays in view while the panel scrolls.
        p.evaluate("document.querySelector('#filter-body').scrollTop = 9999")
        self.assertTrue(p.locator('#filter-result').is_visible())
        # Unselect everything: zero-match state and live summary.
        card.get_by_role('button', name='Unselect all').click()
        self.assertIn('No records match', p.locator('#filter-result').inner_text())
        self.assertEqual(card.locator('.condition-summary').inner_text(), 'No answers selected')
        card.get_by_role('button', name='Select all', exact=True).click()
        card.locator('input[data-answer]').first.uncheck()
        self.assertRegex(card.locator('.condition-summary').inner_text(), r'^Keeping \d+ of \d+ answers$')
        self.assertRegex(card.locator('.answer-count').inner_text(), r'^\d+ of \d+ selected$')
        # Collapse and expand in place.
        toggle = card.locator('.condition-toggle')
        toggle.click()
        self.assertEqual(toggle.get_attribute('aria-expanded'), 'false')
        self.assertTrue(card.locator('.condition-body').is_hidden())
        toggle.click()
        self.assertTrue(card.locator('.condition-body').is_visible())

    def test_adding_a_third_filter_collapses_the_others(self):
        p = self.page
        p.evaluate('openFilters(state.tables[0].id)')
        for name in ['Crop', 'Region', 'Wareda']:
            self.add_filter(name)
        states = p.locator('.condition-toggle').evaluate_all('els => els.map(e => e.getAttribute("aria-expanded"))')
        self.assertEqual(states, ['false', 'false', 'true'])

    def test_match_control_is_keyboard_operable(self):
        p = self.page
        p.evaluate('openFilters(state.tables[0].id)')
        self.add_filter('Crop')
        p.get_by_label('Remove selected', exact=True).focus()
        p.keyboard.press('Space')
        self.assertRegex(p.locator('.condition-summary').first.inner_text(), r'^(Nothing removed|Removing \d+ of \d+ answers)$')
        self.assertTrue(p.get_by_label('Remove selected', exact=True).is_checked())
        self.assertTrue(p.get_by_label('Remove selected', exact=True).evaluate('el => document.activeElement === el'))

    def test_picker_puts_data_quality_fields_last(self):
        p = self.page
        p.evaluate('openFilters(state.tables[0].id)')
        p.locator('[data-action="toggle-filter-picker"]').first.click()
        p.locator('#field-search').fill('')
        p.locator('#field-search').click()
        options = p.locator('#field-results [role=option]').all_inner_texts()
        self.assertTrue(options[0].startswith(('Region', 'Crop')), options[0])
        self.assertTrue(any('Review_Flag' in o and 'data quality' in o for o in options))
        first_admin = next(i for i, o in enumerate(options) if 'data quality' in o)
        self.assertTrue(all('data quality' in o for o in options[first_admin:]))


    def region_cells(self, minimum):
        return self.page.evaluate("""(minimum) => {
          const t = clone(state.tables.find(x => x.id === 'region'));
          if (minimum) t.filters.measures.children = [{kind: 'condition', id: 'min-n', field: 'n:count', op: 'gte', value: String(minimum), high: '', refs: [], values: []}];
          return calculate(t).rows.flatMap(r => r.cells.map(c => ({stat: c.stat, n: c.n, value: c.value, hidden: c.suppressedN || 0})));
        }""", minimum)

    def test_n_count_hides_cells_below_threshold_and_keeps_threshold(self):
        base = self.region_cells(0)
        self.assertFalse([c for c in base if c['hidden']])
        thin = [c for c in base if c['n'] and c['n'] < 5]
        self.assertTrue(thin, 'Fixture needs cells with fewer than 5 records')
        cells = self.region_cells(5)
        for before, after in zip(base, cells):
            if before['n'] and before['n'] < 5 and before['stat'] != 'change':
                self.assertEqual((after['hidden'], after['value']), (5, None))
            elif before['n'] and before['n'] >= 5:
                self.assertEqual((after['hidden'], after['value']), (0, before['value']), 'A cell at the threshold stays visible')

    def test_n_count_filter_screen_csv_and_persistence_agree(self):
        p = self.page
        p.evaluate("openFilters('region')")
        p.locator('.suggest-chip', has_text='N count').click()
        p.locator('[data-action="apply-filters"]').click()
        screen = p.locator('#table-region .cell-suppressed').count()
        self.assertGreater(screen, 0)
        self.assertIn('N count at least 5 valid records per cell', p.locator('#table-region').inner_text())
        p.evaluate("window.__csv = ''; download = (name, text) => { window.__csv = text; }")
        p.evaluate("exportCSV(tableById('region'))")
        csv_hidden = p.evaluate("(window.__csv.match(/\"N<5\"/g) || []).length")
        self.assertEqual(csv_hidden, screen, 'CSV and screen must hide the same cells')
        saved = p.evaluate("JSON.stringify(state.tables.find(t => t.id === 'region').filters.measures.children.map(c => [c.field, c.value]))")
        self.assertEqual(saved, '[["n:count","5"]]')

    def test_n_count_validation_and_listing(self):
        p = self.page
        for bad in ['0', 'abc', '2.5', '']:
            message = p.evaluate("""(value) => { try { validateFilters({source: emptyGroupForTest(), measures: {kind: 'group', mode: 'all', children: [{kind: 'condition', id: 'x', field: 'n:count', op: 'gte', value, high: '', refs: [], values: []}]}}); return ''; } catch (e) { return e.message; } }""".replace('emptyGroupForTest()', "{kind: 'group', mode: 'all', children: []}"), bad)
            self.assertIn('whole number', message, bad)
        p.evaluate('openFilters(state.tables[0].id)')
        self.assertIn('N count', p.locator('.suggest-row').inner_text())
        p.locator('[data-action="toggle-filter-picker"]').first.click()
        options = p.locator('#field-results [role=option]').all_inner_texts()
        index = next(i for i, o in enumerate(options) if o.startswith('N count'))
        first_admin = next(i for i, o in enumerate(options) if 'data quality' in o)
        self.assertLess(index, first_admin)


if __name__ == '__main__':
    unittest.main()
