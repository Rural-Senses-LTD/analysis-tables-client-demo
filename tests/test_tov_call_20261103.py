"""Changes from the 3 November 2026 TOV call (Eshel building tables on a small screen).

Run with the existing suite: python -m unittest discover -s tests -v
"""
import json
import unittest

import test_feedback_20260922 as previous


class TovCall20261103Tests(unittest.TestCase):
    setUpClass = classmethod(previous.FeedbackBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(previous.FeedbackBrowserTests.tearDownClass.__func__)
    setUp = previous.FeedbackBrowserTests.setUp
    tearDown = previous.FeedbackBrowserTests.tearDown
    open_builder_panels = previous.FeedbackBrowserTests.open_builder_panels
    drag = previous.FeedbackBrowserTests.drag

    def toast(self):
        return self.page.locator('#toast').inner_text()

    # Items 1 and 2: saved tables that used the old IDs still load.
    def test_saved_tables_with_old_question_ids_still_load(self):
        p = self.page
        saved = p.evaluate("""(() => {
          const s = clone(state), t = s.tables.find(x => x.id === 'crops');
          t.rows = ['q:irrigation_method', 'q:irrigation_type']; t.columns = ['b:Variety'];
          return JSON.stringify(s);
        })()""")
        p.evaluate("([key, value]) => localStorage.setItem(key, value)", [p.evaluate("STORAGE_KEY"), saved])
        p.reload()
        table = p.evaluate("(() => { const t = tableById('crops'); return {rows: t.rows, columns: t.columns}; })()")
        self.assertEqual(table, {'rows': ['q:irrigation_type'], 'columns': ['e:Variety']})
        self.assertNotIn('could not be loaded', self.toast())

    # Item 3 (revised 5 Nov): an arrow on the settings pane folds it to a narrow rail and back.
    def test_settings_panel_folds_with_an_arrow_on_the_pane(self):
        p = self.page
        p.set_viewport_size({'width': 1000, 'height': 760})
        p.evaluate("openBuilder(); work.draft.rows = ['q:crop']; renderBuilder()")
        toggle = p.locator('.builder-settings [data-action="builder-toggle-settings"]')
        self.assertEqual(toggle.get_attribute('aria-label'), 'Hide settings')
        self.assertEqual(p.locator('.builder-preview-header [data-action="builder-toggle-settings"]').count(), 0)
        before = p.locator('.builder-preview-panel').bounding_box()['width']
        p.locator('#builder-title').fill('Kept while hidden')
        toggle.click()
        toggle = p.locator('.builder-settings [data-action="builder-toggle-settings"]')
        self.assertTrue(toggle.is_visible(), 'The arrow stays on the folded pane')
        self.assertEqual(toggle.get_attribute('aria-label'), 'Show settings')
        self.assertEqual(toggle.get_attribute('aria-expanded'), 'false')
        self.assertFalse(p.locator('.builder-heading').is_visible())
        self.assertLess(p.locator('.builder-settings').bounding_box()['width'], 60)
        self.assertGreater(p.locator('.builder-preview-panel').bounding_box()['width'], before + 250)
        self.assertEqual(p.locator('#builder-preview-title').inner_text(), 'Kept while hidden')
        p.screenshot(path=str(previous.ARTIFACTS / '20261105-settings-folded-1000.png'))
        toggle.click()
        self.assertTrue(p.locator('.builder-heading').is_visible())
        self.assertEqual(p.locator('#builder-title').input_value(), 'Kept while hidden')
        # On a phone the panels stack, so there is nothing to fold.
        p.set_viewport_size({'width': 390, 'height': 844})
        self.assertFalse(p.locator('.builder-settings [data-action="builder-toggle-settings"]').is_visible())

    # 5 Nov review: centred column headers, a clearer line between top-level groups, menus above the table.
    def test_column_groups_are_centred_and_separated(self):
        p = self.page
        p.evaluate("(() => { const t = tableById('area'); persist(); renderTable('area'); })()")
        result = p.evaluate("""(() => {
          const table = document.querySelector('#table-area .matrix');
          const heads = [...table.querySelectorAll('thead tr:first-child th.category-heading:not(.row-axis-header)')];
          const label = heads[1].querySelector('.header-label > span'), cell = heads[1].getBoundingClientRect(), box = label.getBoundingClientRect();
          const starts = heads.slice(1).map(th => th.classList.contains('group-start'));
          const firstBody = table.querySelector('tbody tr:not(.measurement-heading)');
          return {align: getComputedStyle(heads[1]).textAlign, offCentre: Math.abs((box.left + box.right) / 2 - (cell.left + cell.right) / 2),
                  starts, firstNotStart: !heads[0].classList.contains('group-start'),
                  bodyStarts: firstBody.querySelectorAll('td.group-start').length, groups: heads.length,
                  border: getComputedStyle(firstBody.querySelector('td.group-start')).borderLeftWidth};
        })()""")
        self.assertEqual(result['align'], 'center')
        self.assertLess(result['offCentre'], 20, 'The group name sits in the middle of its columns')
        self.assertTrue(all(result['starts']) and result['firstNotStart'])
        self.assertEqual(result['bodyStarts'], result['groups'] - 1, 'The group line runs through the body')
        self.assertEqual(result['border'], '1px')

    def test_open_table_menu_sits_above_the_floating_header(self):
        # 5 Nov review: once the table's header row scrolls under the title bar, the floating copy of the header
        # (z-index 9) covered the open table menu (inside the title bar, z-index 8).
        p = self.page
        p.set_viewport_size({'width': 1050, 'height': 870})
        p.evaluate("(() => { const c = document.querySelector('#table-transitions'); window.scrollTo(0, c.getBoundingClientRect().top + window.scrollY - 60); })()")
        p.wait_for_timeout(200)
        p.locator('#table-transitions .table-tools > details.menu summary').click()
        covered = p.evaluate("""(() => { const list = document.querySelector('#table-transitions .table-tools details.menu .menu-list'), r = list.getBoundingClientRect(), hits = [];
          for (let y = r.top + 8; y < Math.min(r.bottom, innerHeight) - 4; y += 12) { const el = document.elementFromPoint(r.left + 40, y); if (el && !list.contains(el)) hits.push(el.tagName); }
          return hits; })()""")
        self.assertEqual(covered, [])

    # Item 4: typing an answer finds the group it belongs to.
    def test_group_search_finds_a_group_by_its_answers(self):
        p = self.page
        p.evaluate("openBuilder()")
        self.open_builder_panels()
        p.locator('#fields-search').fill('galilea')
        visible = p.locator('.group-choice:visible')
        self.assertEqual(visible.count(), 1)
        self.assertIn('Variety', visible.inner_text())
        self.assertIn('Has “Galilea', visible.inner_text())
        p.locator('#fields-search').fill('variety')
        self.assertEqual(p.locator('.group-choice:visible .field-row-match').count(), 0, 'A name match needs no answer hint')
        p.locator('[data-builder-menu="rows"]').click()
        p.locator('[data-builder-axis-menu-search]').fill('drip')
        option = p.locator('#builder-axis-menu [role="option"]')
        self.assertEqual(option.count(), 1)
        self.assertIn('Irrigation Type', option.inner_text())
        self.assertIn('Has “Drip”', option.inner_text())
        # An answer whose group is already in the table points there instead of a dead end.
        p.keyboard.press('Escape')
        p.evaluate("readBuilder(); work.draft.columns = ['q:variety']; renderBuilder()")
        p.locator('[data-builder-menu="rows"]').click()
        p.locator('[data-builder-axis-menu-search]').fill('galilea')
        self.assertIn('is an answer in Variety, which is already in your table', p.locator('#builder-axis-menu').inner_text())

    # Item 5: shared parts of series names are said once.
    def test_chart_series_names_drop_the_parts_all_series_share(self):
        p = self.page
        names = p.evaluate("""(() => {
          const h = (variety, key) => ({group: {key, path: [['q:crop', 'Tomato'], ['q:variety', variety]]}, period: 'aggregate', stat: 'mean', label: 'Combined sources mean'});
          const r = chartSeriesNames([h('Gabi', 'a'), h('Galilea 39', 'b'), h(null, 'c')]);
          return {names: [...r.names.values()], common: r.common, single: [...chartSeriesNames([h('Gabi', 'a')]).names.values()]};
        })()""")
        self.assertEqual(names['names'], ['Gabi', 'Galilea 39', 'Blank'])
        self.assertEqual(names['common'], 'Tomato · Combined sources mean')
        self.assertEqual(names['single'], ['Tomato · Gabi · Combined sources mean'])
        html = p.evaluate("""(() => {
          const t = clone(tableById('crops')); t.columns = ['q:project'];
          const data = calculate(t), keys = data.headers.filter(h => h.stat === 'mean' && h.period === 'e' && h.group.path?.[0]?.[1]).map(chartSeriesKey);
          return chartHTML(t, data, {...chartDefaults(t, data), series: keys}, true);
        })()""")
        p.set_content(f'<div id="c">{html}</div>')
        self.assertEqual(p.locator('.chart-series-common').inner_text(), 'All bars: Endline mean')
        self.assertEqual(sorted(p.locator('.chart-legend span').all_inner_texts()), ['Demo Farmers', "TOV Le'isua"])
        # 10 Nov 2026: the N now sits on each bar rather than in a list under the category.
        samples = p.locator('.bar-n').first.inner_text()
        self.assertNotIn('Endline mean', samples, 'Sample sizes on the bars do not repeat series names')
        self.assertIn('N=', samples)

    def test_chosen_chart_series_get_distinct_default_colours(self):
        p = self.page
        p.evaluate("""(() => { const t = tableById('crops'); t.rows = ['q:irrigation_type']; t.columns = ['q:crop', 'q:variety']; persist(); render(); openChart('crops'); })()""")
        keys = p.evaluate("""(() => { const d = calculate(tableById('crops'));
          return d.headers.filter(h => h.stat === 'mean' && h.period === 'e' && h.group.path?.[0]?.[1] === 'Tomato').slice(0, 3).map(chartSeriesKey); })()""")
        self.assertEqual(len(keys), 3)
        p.evaluate("keys => { document.querySelectorAll('[data-chart-series]').forEach(el => el.checked = keys.includes(el.value)); updateChartPreview(); }", keys)
        colours = p.locator('#chart-preview .chart-legend i').evaluate_all('els => els.map(e => getComputedStyle(e).backgroundColor)')
        self.assertEqual(len(set(colours)), 3, 'Each chosen series has its own colour')
        self.assertEqual(p.evaluate("readChartConfig().colors"), {}, 'Default colours are not saved as choices')
        p.evaluate("keys => { const el = [...document.querySelectorAll('[data-chart-color]')].find(x => x.dataset.chartColor === keys[1]); el.value = '#000000'; updateChartPreview(); }", keys)
        self.assertEqual(list(p.evaluate("readChartConfig().colors").values()), ['#000000'])

    # Item 6: one menu at a time, and hidden groups are easy to bring back.
    def test_one_menu_at_a_time_and_hidden_groups_are_findable(self):
        p = self.page
        card = p.locator('#table-crops')
        header = card.locator('details.header-menu').first
        header.locator('summary').click()
        self.assertTrue(header.evaluate('el => el.open'))
        table_menu = card.locator('.table-tools > details.menu')
        table_menu.locator('summary').click()
        self.assertTrue(table_menu.evaluate('el => el.open'))
        self.assertFalse(header.evaluate('el => el.open'), 'Opening the table menu closes the column menu')
        p.locator('h1, .project-header').first.click()
        self.assertFalse(table_menu.evaluate('el => el.open'), 'A click outside closes the menu')
        p.evaluate("""(() => { const t = tableById('crops'), d = calculate(t), row = d.rows.find(r => !r.group.total);
          t.hidden.rows.push(row.group.path); persist(); renderTable('crops'); })()""")
        button = card.locator('.hidden-groups-button')
        self.assertEqual(button.inner_text().strip(), 'Show 1 hidden group')
        card.locator('.table-tools > details.menu summary').click()
        self.assertTrue(card.locator('.table-tools > details.menu [data-action="groups"]').is_visible())
        button.click()
        self.assertTrue(p.locator('[data-action="show-all-groups"]').is_visible())

    # Item 7: dragging a header shows the group's name and lights only the column-group headers.
    def test_preview_drag_marks_one_group_and_lights_only_group_headers(self):
        p = self.page
        p.evaluate("openBuilder(); work.draft.rows = ['q:region']; work.draft.columns = ['q:crop', 'q:gender']; readBuilder(); builderUseMeasurement('yield'); renderBuilder()")
        state = p.evaluate("""(() => {
          const source = document.querySelector('#builder-preview th[data-preview-axis="columns"][data-index="1"]');
          const target = document.querySelector('#builder-preview th[data-preview-axis="columns"][data-index="0"]');
          const dt = new DataTransfer(), fire = (type, el) => el.dispatchEvent(new DragEvent(type, {bubbles: true, cancelable: true, dataTransfer: dt}));
          fire('dragstart', source); fire('dragover', target);
          const marked = [...document.querySelectorAll('#builder-preview .drag-source')].every(el => el.dataset.index === '1');
          const lit = [...document.querySelectorAll('#builder-preview thead .field-drop-active')];
          const out = {marked, markedCount: document.querySelectorAll('#builder-preview .drag-source').length,
                       litOnlyGroups: lit.length > 0 && lit.every(el => el.dataset.previewAxis === 'columns'),
                       headLit: document.querySelector('#builder-preview thead').classList.contains('field-drop-active')};
          fire('dragend', source);
          out.cleared = !document.querySelector('#builder-preview .drag-source, #builder-preview .field-drop-active');
          return out;
        })()""")
        self.assertTrue(state['marked'])
        self.assertGreater(state['markedCount'], 1)
        self.assertTrue(state['litOnlyGroups'], 'The measurement row under the column groups is not lit')
        self.assertFalse(state['headLit'])
        self.assertTrue(state['cleared'])
        # Dropping a column group onto the row headers still moves it.
        self.drag('#builder-preview th[data-preview-axis="columns"][data-index="1"]', '#builder-preview th.row-axis-header[data-preview-axis="rows"]')
        self.assertEqual(p.evaluate("[work.draft.rows, work.draft.columns]"), [['q:region', 'q:gender'], ['q:crop']])

    # Item 9: swapping counts and measurements says so.
    def test_switching_between_counts_and_measurements_says_what_changed(self):
        p = self.page
        p.evaluate("openBuilder(); work.draft.metrics = ['count']; work.draft.stats = ['count']; builderUseMeasurement('yield')")
        self.assertIn('Number of respondents was removed', self.toast())
        p.evaluate("builderUseMeasurement('count')")
        self.assertIn('Number of respondents replaced', self.toast())
        self.assertIn('Yield per hectare', self.toast())
        self.assertEqual(p.evaluate("work.draft.metrics"), ['count'])


if __name__ == '__main__':
    unittest.main()
