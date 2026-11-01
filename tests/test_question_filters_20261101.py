"""Question-level filters (1 November 2026): a filter names a question, never a data source.

The main fixture is a synthetic project with ten data sources, none called Baseline or Endline,
and questions that are not about crops, so the rules are proven generic.

Run with the existing suite: python -m unittest discover -s tests -v
"""
import json
import re
import unittest

import test_feedback_20260922 as previous

SOURCES = ['Intake', 'Spring visit', 'Harvest check', 'Round A', 'Round B', 'Market day', 'Follow-up 1', 'Follow-up 2', 'Exit', 'Year two']
IDS = [f's{i}' for i in range(1, 11)]
# Each source names its columns its own way; the stored mapping links them to project questions.
WATER_HEADER = {sid: ('Water source' if i % 2 else f'Water source ({SOURCES[i]})') for i, sid in enumerate(IDS)}
HEAD_SOURCES = ['s1', 's4', 's7']        # "Head of household" is asked in 3 of 10 sources.
DRINKING_SOURCES = ['s2', 's3']          # "Drinking water" is asked in 2 sources.

# household -> {source id: {question: answer}}
HOUSEHOLDS = {
    'h1': {sid: {'water': 'Well'} for sid in IDS},                                          # same everywhere: kept
    'h2': {sid: {'water': 'River' if sid == 's5' else 'Well'} for sid in IDS},             # changed once: excluded
    'h3': {sid: {'water': ['Well', ' well ', 'WELL'][i % 3]} for i, sid in enumerate(IDS[:6])},  # 6 sources, case/space only: kept
    'h4': {'s1': {'water': 'Well', 'head': 'Female'}},                                      # one answer only: excluded
    'h5': {sid: {'water': '' if sid == 's3' else 'Tap'} for sid in IDS},                   # a blank is ignored: kept
    'h6': {'s2': {'water': 'Tap', 'drinking': 'Tap'}, 's3': {'water': 'Tap', 'drinking': 'Well'}},
    'h7': {'s2': {'water': 'River', 'drinking': 'River'}, 's3': {'water': 'Tap', 'drinking': 'Tap'}},
    'h8': {'s9': {'water': ''}, 's10': {'water': ''}},                                      # blank only
}
HOUSEHOLDS['h1']['s4']['head'] = 'Male'
HOUSEHOLDS['h1']['s7']['head'] = 'Male'


def fixture():
    sources, mapping = [], {}
    for sid, name in zip(IDS, SOURCES):
        headers = {'water': WATER_HEADER[sid], 'head': 'Head of household', 'drinking': 'Drinking water'}
        asked = ['water'] + (['head'] if sid in HEAD_SOURCES else []) + (['drinking'] if sid in DRINKING_SOURCES else [])
        records = [{'values': {'Household ID': uid, **{headers[q]: v for q, v in answers.items()}}}
                   for uid, by_source in HOUSEHOLDS.items() if sid in by_source for answers in [by_source[sid]]]
        options = {q: sorted({r['values'].get(headers[q]) for r in records} - {None, ''}) for q in asked}
        sources.append({'id': sid, 'label': name, 'records': records,
                        'fields': [{'header': 'Household ID', 'label': 'Household ID', 'type': 'text', 'options': []}] +
                                  [{'header': headers[q], 'label': headers[q], 'type': 'category', 'options': options[q]} for q in asked]})
        mapping[sid] = {'Household ID': 'q:household_id', **{headers[q]: 'q:' + q for q in asked}}
    return {'version': 'synthetic', 'fingerprint': 'synthetic-ten-sources', 'inputs': [], 'sources': sources, 'questionMapping': mapping,
            'questions': [{'id': 'q:water', 'text': 'Water source', 'type': 'category'}, {'id': 'q:head', 'text': 'Head of household', 'type': 'category'},
                          {'id': 'q:drinking', 'text': 'Drinking water', 'type': 'category'}]}


class QuestionFilterTests(unittest.TestCase):
    setUpClass = classmethod(previous.FeedbackBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(previous.FeedbackBrowserTests.tearDownClass.__func__)
    setUp = previous.FeedbackBrowserTests.setUp
    tearDown = previous.FeedbackBrowserTests.tearDown

    def open_fixture(self):
        html = (previous.ROOT / 'index.html').read_text(encoding='utf-8')
        changed, count = re.subn(r'const DATA = .*?;\n', lambda _: 'const DATA = ' + json.dumps(fixture()) + ';\n', html, count=1, flags=re.S)
        self.assertEqual(count, 1)
        page = self.context.new_page()
        page.on('pageerror', lambda error: self.errors.append(str(error)))
        page.on('console', lambda message: self.errors.append(message.text) if message.type == 'error' else None)
        page.route(re.compile(r'^http://127\.0\.0\.1:\d+/(index\.html)?(\?.*)?$'), lambda route: route.fulfill(body=changed, content_type='text/html'))
        page.goto(self.url)
        self.assertEqual(page.evaluate('dataSources().length'), 10)
        return page

    def count(self, page, conditions, sources=None):
        return page.evaluate("""([conditions, sources]) => {
          const t = clone(state.tables[0]); t.sources = sourceSettings(t); if (sources) t.sources.ids = sources;
          t.filters = emptyFilters(); t.filters.source.children = conditions.map((c, i) => ({kind: 'condition', id: 'c' + i, values: [], ...c}));
          validateFilters(t.filters);
          const r = filterRecords(t);
          return r.included.map(x => Object.values(x).find(v => v?.values)?.values['Household ID']).sort();
        }""", [conditions, sources])

    def test_answer_rules_hold_across_ten_sources(self):
        page = self.open_fixture()
        self.assertEqual(self.count(page, [{'field': 'q:water', 'op': 'in', 'values': ['River'], 'includeBlank': False}]), ['h2', 'h7'])
        self.assertEqual(self.count(page, [{'field': 'q:water', 'op': 'notin', 'values': ['River'], 'includeBlank': False}]), ['h1', 'h3', 'h4', 'h5', 'h6', 'h8'])
        self.assertEqual(self.count(page, [{'field': 'q:water', 'op': 'notin', 'values': ['River'], 'includeBlank': True}]), ['h1', 'h3', 'h4', 'h6'])
        self.assertEqual(self.count(page, [{'field': 'q:water', 'op': 'missing'}]), ['h8'])
        page.close()

    def test_same_question_means_the_answer_never_changed(self):
        page = self.open_fixture()
        self.assertEqual(self.count(page, [{'field': 'q:water', 'op': 'eqField', 'otherField': 'q:water'}]), ['h1', 'h3', 'h5', 'h6'])
        page.close()

    def test_different_questions_are_compared_within_each_source(self):
        page = self.open_fixture()
        self.assertEqual(self.count(page, [{'field': 'q:water', 'op': 'eqField', 'otherField': 'q:drinking'}]), ['h7'])
        page.close()

    def test_validation_names_the_question_not_a_source(self):
        page = self.open_fixture()
        messages = page.evaluate("""() => {
          const run = (c, ids) => { const t = clone(state.tables[0]); t.sources = sourceSettings(t); t.sources.ids = ids;
            t.filters = emptyFilters(); t.filters.source.children = [{kind: 'condition', id: 'x', values: [], ...c}];
            try { validateFilters(t.filters); validateFilterSources(t); return ''; } catch (e) { return e.message; } };
          return [run({field: 'q:head', op: 'eqField', otherField: 'q:head'}, ['s1', 's2']),
                  run({field: 'q:water', op: 'eqField', otherField: 'q:head'}, ['s2', 's3']),
                  run({field: 'q:head', op: 'in', values: ['Male']}, ['s2', 's3']),
                  run({field: 'q:water', op: 'in', values: ['Well'], scope: 'every'}, ['s1']),
                  run({field: 's1:Water source (Intake)', op: 'in', values: ['Well']}, ['s1'])];
        }""")
        self.assertEqual(messages, [
            'Select at least two data sources that ask Head of household to compare its answers.',
            'No selected data source asks both Water source and Head of household.',
            'None of the selected data sources ask Head of household.',
            'Filter on the question name. Filters do not choose a data source.',
            'Filter on the question name. Filters do not choose a data source.'])
        page.close()

    def test_filter_ui_shows_question_names_and_coverage_only(self):
        page = self.open_fixture()
        page.evaluate('openFilters(state.tables[0].id)')
        names = page.evaluate("filterFields('source').filter(f => f.question).map(fieldOptionLabel)")
        self.assertEqual(sorted(names), ['Drinking water', 'Head of household', 'Household ID', 'Water source'])
        page.locator('[data-action="toggle-filter-picker"]').first.click()
        page.locator('#field-search').fill('Head')
        page.locator('#field-results [role=option]').first.click()
        card = page.locator('.filter-condition').last
        self.assertEqual(card.locator('.condition-title').inner_text(), 'Head of household')
        self.assertEqual(card.locator('.filter-source-note').inner_text(), 'Asked in 3 of 10 selected data sources.')
        page.locator('[data-action="toggle-filter-picker"]').first.click()
        page.locator('#field-search').fill('Water source')
        page.locator('#field-results [role=option]').first.click()
        card = page.locator('.filter-condition').last
        self.assertEqual(card.locator('.filter-source-note').count(), 0, 'Asked everywhere, so no coverage note')
        card.get_by_label('Match across data sources', exact=True).check()
        card = page.locator('.filter-condition').last
        self.assertEqual(card.get_by_label('Comparison field', exact=True).input_value(), 'q:water')
        self.assertEqual(card.locator('.condition-summary').inner_text(), 'Same answer in every data source')
        page.evaluate("filterDraft.source.children.splice(0, 1); renderFilters()")
        self.assertRegex(page.locator('#filter-preview').inner_text(), r'^4 of 8 records match')
        body = page.locator('#filter-body').inner_text()
        self.assertFalse([name for name in SOURCES if name in body], 'No source name appears in the filter panel')
        page.locator('[data-action="apply-filters"]').click()
        self.assertEqual(page.evaluate('conditionText(state.tables[0].filters.source.children[0])'), 'Water source is the same in every data source')
        for width in [1440, 390]:
            page.set_viewport_size({'width': width, 'height': 900})
            page.evaluate('openFilters(state.tables[0].id)')
            self.assertLessEqual(page.evaluate("document.querySelector('#filter-body').scrollWidth - document.querySelector('#filter-body').clientWidth"), 0)
            page.screenshot(path=str(previous.ARTIFACTS / f'question-filter-ten-sources-{width}.png'))
            page.evaluate("document.querySelector('#filter-dialog').close()")
        page.close()

    def test_suggestions_and_changing_question_keep_the_comparison(self):
        page = self.open_fixture()
        page.evaluate('openFilters(state.tables[0].id)')
        self.assertEqual(page.evaluate('filterSuggestedFields().map(f => f.label)')[0], 'Water source')
        page.evaluate("addFilterField('q:water')")
        page.get_by_label('Match across data sources', exact=True).check()
        page.get_by_label('Filter field', exact=True).select_option('q:head')
        self.assertEqual(page.evaluate('filterDraft.source.children[0]').get('otherField'), 'q:head')
        self.assertEqual(page.evaluate('filterDraft.source.children[0].op'), 'eqField')
        page.close()

    def test_saved_per_source_filters_are_dropped_not_blocking(self):
        p = self.page
        p.evaluate("""() => { const saved = clone(state); saved.tables[0].filters.source.children = [{kind: 'condition', id: 'old', field: 'b:Baseline Crop', op: 'in', values: ['Onion'], value: '', high: '', refs: []}];
          saved.tables[0].title = 'Kept title'; localStorage.setItem(STORAGE_KEY, JSON.stringify(saved)); }""")
        p.reload()
        self.assertEqual(p.evaluate('state.tables[0].title'), 'Kept title')
        self.assertEqual(p.evaluate('state.tables[0].filters.source.children.length'), 0)
        self.assertIn('Older filters on a single data source were removed', p.locator('#toast').inner_text())

    def test_filter_code_has_no_project_specific_names(self):
        sources = self.page.evaluate("""[answersOf, testQuestion, testCondition, matches, validateFilterSources, validateFilters, filterFields, filterChoices,
          filterSourceNote, filterSuggestedFields, filterSummary, renderCondition, filterChange, conditionText, searchFields].map(f => f.toString())""")
        for code in sources:
            self.assertIsNone(re.search(r'crop|baseline|endline', code, re.I), code[:60])


if __name__ == '__main__':
    unittest.main()
