"""Regressions for the 22 October TOV working session (field names, filters, numeric search hint).

Run with the existing suite: python -m unittest discover -s tests -v
"""
import re
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
          rows.forEach(v => { const n = String(v.Name || '').replace(/\\s+/g, ' ').trim().toLowerCase(); names[n] = (names[n] || 0) + 1; });
          const duplicated = rows.filter(v => names[String(v.Name || '').replace(/\\s+/g, ' ').trim().toLowerCase()] > 1);
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


    def test_questions_appear_once_without_data_source_names(self):
        p = self.page
        p.evaluate('openBuilder()')
        groups = p.evaluate("[...document.querySelectorAll('#fields-list .field-row')].map(e => e.dataset.field)")
        for question in ['q:crop', 'q:region', 'q:project', 'q:woreda', 'q:farmer_uid']:
            self.assertEqual(groups.count(question), 1, question)
        for member in ['b:Region', 'e:Region', 'e:Crop', 'b:Baseline Crop', 'e:Project', 'b:Project', 'e:Wareda', 'b:Woreda']:
            self.assertNotIn(member, groups, f'{member} is folded into its question')
        listed = p.evaluate("document.querySelector('#fields-list').innerText + ' ' + document.querySelector('#metric-options').innerText")
        self.assertNotRegex(listed.replace('Reported Baseline Period', ''), r'Baseline|Endline')
        metrics = p.evaluate("[...document.querySelectorAll('[data-builder-metric]')].map(e => e.dataset.builderMetric)")
        for covered in ['b:Net income', 'e:Net Income', 'b:Yield kg', 'e:Total expenses']:
            self.assertNotIn(covered, metrics, f'{covered} is already a project measurement')
        self.assertIn('yield', metrics)

    def test_each_source_column_groups_by_its_own_answers(self):
        p = self.page
        result = p.evaluate("""(() => {
          const t = clone(state.tables[0]);
          t.cohort = 'all'; t.rows = ['q:crop']; t.columns = []; t.metrics = ['count']; t.stats = ['count']; t.change = false; t.totals = false;
          validateState({version: 1, fingerprint: DATA.fingerprint, definitions: [], tables: [t]});
          const data = calculate(t), got = {b: {}, e: {}}, want = {b: {}, e: {}};
          for (const row of data.rows) row.cells.forEach((c, i) => { got[data.headers[i].period][row.group.label] = c.value; });
          for (const f of DATA.farmers) for (const [p, header] of [['b', 'Baseline Crop'], ['e', 'Crop']]) {
            if (!f[p]) continue; const v = f[p].values[header]; const k = v === null || v === undefined || v === '' ? 'Blank' : v;
            want[p][k] = (want[p][k] || 0) + 1;
          }
          const clean = o => Object.fromEntries(Object.entries(o).filter(([, n]) => n));
          return {got: {b: clean(got.b), e: clean(got.e)}, want};
        })()""")
        self.assertEqual(result['got'], result['want'])
        self.assertNotEqual(result['got']['b'], result['got']['e'], 'Baseline and endline crops differ, so the columns must too')

    def test_combined_columns_count_each_source_under_its_own_answer(self):
        p = self.page
        result = p.evaluate("""(() => {
          const t = clone(state.tables[0]);
          t.cohort = 'all'; t.rows = ['q:crop']; t.columns = []; t.metrics = ['count']; t.stats = ['count']; t.change = false; t.totals = false;
          t.sources = {...sourceSettings(t), mode: 'aggregate'};
          validateState({version: 1, fingerprint: DATA.fingerprint, definitions: [], tables: [t]});
          const data = calculate(t), count = {};
          data.rows.forEach(r => { count[r.group.label] = r.cells[0].value; });
          const want = {};
          for (const f of DATA.farmers) for (const [p, h] of [['b', 'Baseline Crop'], ['e', 'Crop']]) { if (!f[p]) continue; const k = f[p].values[h] || 'Blank'; want[k] = (want[k] || 0) + 1; }
          return {count, want, note: /Combined columns count each source under its own answer/.test(matrixHTML(t, data))};
        })()""")
        self.assertEqual(result['count']['Wheat'], 34, 'Baseline-only wheat is not mixed with endline crops')
        self.assertEqual(result['count']['Pepper'], result['want']['Pepper'])
        self.assertEqual({k: v for k, v in result['count'].items() if v}, result['want'])
        self.assertTrue(result['note'])

    def test_change_columns_keep_only_records_with_the_same_answer_in_both_sources(self):
        p = self.page
        result = p.evaluate("""(() => {
          const t = clone(state.tables[0]);
          t.cohort = 'all'; t.rows = ['q:crop']; t.columns = []; t.metrics = ['yield']; t.stats = ['mean']; t.change = true; t.totals = false;
          validateState({version: 1, fingerprint: DATA.fingerprint, definitions: [], tables: [t]});
          const data = calculate(t), i = data.headers.findIndex(h => h.stat === 'change'), got = {};
          data.rows.forEach(r => { got[r.group.label] = r.cells[i].cohort; });
          const same = {};
          for (const f of DATA.farmers) { if (!f.b || !f.e) continue; const b = f.b.values['Baseline Crop'], e = f.e.values['Crop']; if (b && b === e) same[b] = (same[b] || 0) + 1; }
          return {got, same, legacy: calculate({...t, rows: ['b:Baseline Crop']}).rowGroups.every(g => !g.recordsBy)};
        })()""")
        self.assertEqual(result['got']['Wheat'], 0, 'Nobody has wheat in both sources')
        for crop, n in result['same'].items():
            self.assertEqual(result['got'][crop], n, crop)
        self.assertTrue(result['legacy'], 'Tables built on a specific source field keep their old grouping')

    def test_question_matching_uses_the_projects_own_source_names(self):
        p = self.page
        result = p.evaluate("""(() => {
          const saved = DATA.sources;
          DATA.sources = [{id: 'r1', label: 'Round 1', records: []}, {id: 'r2', label: 'Round 2', records: []}, {id: 'r3', label: 'Round 3', records: []}];
          try { return [stripSourceWord('Round 1 Crop'), stripSourceWord('Crop (Round 3)'), stripSourceWord('Crop · Round 2'), stripSourceWord('Baseline Crop')]; }
          finally { DATA.sources = saved; }
        })()""")
        self.assertEqual(result, ['Crop', 'Crop', 'Crop', 'Baseline Crop'])

    def test_questions_have_ids_and_belong_to_the_project_not_a_source(self):
        p = self.page
        result = p.evaluate("""(() => {
          const q = questionMap.get('q:crop');
          const guess = suggestQuestionMapping();
          const suggested = Object.entries(guess).every(([p, cols]) => Object.entries(cols).every(([h, id]) => h === 'Wareda' || DATA.questionMapping[p][h] === id));
          const aliased = DATA.questionMapping.e.Wareda + '/' + DATA.questionMapping.b.Woreda;
          return {id: q.questionId, period: q.period, fields: q.fields, sourceLabel: q.sourceLabel, stored: Object.keys(DATA.questionMapping),
                  mapped: DATA.questionMapping.b['Baseline Crop'] + '/' + DATA.questionMapping.e['Crop'], suggested, aliased,
                  ids: DATA.questions.map(x => x.id).length === new Set(DATA.questions.map(x => x.id)).size};
        })()""")
        self.assertEqual(result['id'], 'q:crop')
        self.assertIsNone(result['period'])
        self.assertEqual(result['fields'], {'b': 'b:Baseline Crop', 'e': 'e:Crop'})
        self.assertEqual(result['mapped'], 'q:crop/q:crop')
        self.assertTrue(result['suggested'], 'Every name-matched pair is in the stored mapping (Wareda is the one manual decision)')
        self.assertEqual(result['aliased'], 'q:woreda/q:woreda', 'The Wareda spelling variant is stored as a mapping decision')
        self.assertTrue(result['ids'])

    def test_a_question_asked_in_one_source_leaves_the_other_source_empty(self):
        p = self.page
        result = p.evaluate("""(() => {
          const t = clone(state.tables[0]);
          t.cohort = 'all'; t.rows = ['q:gender']; t.columns = []; t.metrics = ['count']; t.stats = ['count']; t.change = false; t.totals = false;
          validateState({version: 1, fingerprint: DATA.fingerprint, definitions: [], tables: [t]});
          const data = calculate(t), b = data.headers.findIndex(h => h.period === 'b'), e = data.headers.findIndex(h => h.period === 'e');
          return {rows: data.rows.map(r => r.group.label), baseline: data.rows.map(r => r.cells[b].value), endline: data.rows.map(r => r.cells[e].value)};
        })()""")
        self.assertGreater(sum(result['baseline']), 200)
        self.assertEqual([v for v in result['endline'] if v], [], 'Endline never asked about gender, so no record borrows the baseline answer')

    def test_a_differently_spelled_column_can_be_mapped_to_an_existing_question(self):
        p = self.page
        html = (previous.ROOT / 'index.html').read_text(encoding='utf-8')
        self.assertEqual(html.count('"Irrigation Type":"q:irrigation_type"'), 1)
        changed = html.replace('"Irrigation Type":"q:irrigation_type"', '"Irrigation Type":"q:irrigation_method"')
        page = self.context.new_page()
        page.route(re.compile(r'^http://127\.0\.0\.1:\d+/(index\.html)?(\?.*)?$'), lambda route: route.fulfill(body=changed, content_type='text/html'))
        page.goto(self.url)
        result = page.evaluate("""(() => {
          const q = questionMap.get('q:irrigation_method');
          const t = clone(state.tables[0]);
          t.cohort = 'all'; t.rows = ['q:irrigation_method']; t.columns = []; t.metrics = ['count']; t.stats = ['count']; t.change = false; t.totals = false;
          validateState({version: 1, fingerprint: DATA.fingerprint, definitions: [], tables: [t]});
          const data = calculate(t), b = data.headers.findIndex(h => h.period === 'b'), e = data.headers.findIndex(h => h.period === 'e');
          return {fields: q.fields, gone: questionMap.has('q:irrigation_type'),
                  baseline: data.rows.reduce((n, r) => n + (r.cells[b].value || 0), 0), endline: data.rows.reduce((n, r) => n + (r.cells[e].value || 0), 0)};
        })()""")
        page.close()
        self.assertEqual(result['fields'], {'b': 'b:Irrigation Method', 'e': 'e:Irrigation Type'})
        self.assertFalse(result['gone'])
        self.assertGreater(result['baseline'], 0)
        self.assertGreater(result['endline'], 0)

    def test_question_saved_in_a_table_survives_a_reload(self):
        p = self.page
        p.evaluate("""(() => {
          const t = clone(state.tables[0]); t.id = 'question-table'; t.title = 'Crop by source'; t.rows = ['q:crop']; t.cohort = 'all';
          state.tables.push(t); commit(t.id);
        })()""")
        p.reload()
        self.assertEqual(p.evaluate("state.tables.find(t => t.id === 'question-table').rows"), ['q:crop'])
        self.assertIn('Crop', p.locator('#table-question-table').inner_text())


if __name__ == '__main__':
    unittest.main()
