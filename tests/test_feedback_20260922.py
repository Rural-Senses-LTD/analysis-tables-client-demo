"""Browser regressions for the 22 September TOV feedback.

Run: python -m unittest discover -s tests -v
Requires the already installed Python Playwright package and Chromium.
Screenshots go to the system temp directory, never into the demo data.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import gettempdir
from threading import Thread
import unittest

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = Path(gettempdir()) / "jdc-collab-20260922" / "verification"
DEFINITION = {"id": "custom-test-change", "kind": "measure", "label": "Same farmer income change", "unit": "%", "inputs": ["b:Net income", "e:Net Income"], "formula": "(VAR2 - VAR1) / VAR1 * 100"}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


class FeedbackBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ARTIFACTS.mkdir(parents=True, exist_ok=True)
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT)))
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}/?feedback=20260922"

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 1440, "height": 1000})
        self.page = self.context.new_page()
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.on("console", lambda message: self.errors.append(message.text) if message.type == "error" else None)
        self.page.goto(self.url)
        code = ROOT.joinpath("index.html").read_text(encoding="utf-8").split("<script>", 1)[1].rsplit("</script>", 1)[0]
        self.assertEqual(self.page.evaluate("document.querySelector('script').textContent.length"), len(code.encode("utf-16-le")) // 2)

    def tearDown(self):
        errors = list(self.errors)
        self.page.evaluate("localStorage.clear()")
        self.context.close()
        self.assertEqual(errors, [], "Browser errors")

    def add_definition(self):
        self.page.evaluate("d => state.definitions.push(d)", DEFINITION)

    def drag(self, source, target):
        self.page.evaluate("""([source,target])=>{
          const from=document.querySelector(source),to=document.querySelector(target),dt=new DataTransfer();
          for(const [type,el] of [['dragstart',from],['dragover',to],['drop',to],['dragend',from]])
            el.dispatchEvent(new DragEvent(type,{bubbles:true,cancelable:true,dataTransfer:dt}));
        }""", [source, target])

    def test_same_crop_filter_ui_and_persistence(self):
        p = self.page
        p.evaluate("openFilters('crops'); addFilterField('b:Baseline Crop')")
        p.get_by_label("Match answers", exact=True).select_option("eqField")
        p.get_by_label("Comparison field", exact=True).select_option("e:Crop")
        self.assertEqual(p.locator("#filter-error").inner_text(), "")
        p.screenshot(path=str(ARTIFACTS / "same-crop-filter.png"))
        p.locator('[data-action="apply-filters"]').click()
        result = p.evaluate("""()=>{
          const t=tableById('crops'),result=calculate(t);
          return {n:result.included.length,total:result.all.length,correct:result.included.every(r=>String(raw(r,'b:Baseline Crop')).trim().toLowerCase()===String(raw(r,'e:Crop')).trim().toLowerCase())};
        }""")
        self.assertTrue(result["correct"])
        self.assertGreater(result["n"], 0)
        self.assertLess(result["n"], result["total"])
        p.reload()
        self.assertEqual(p.evaluate("calculate(tableById('crops')).included.length"), result["n"])
        p.evaluate("openFilters('crops')")
        self.assertEqual(p.get_by_label("Comparison field").input_value(), "e:Crop")

    def test_comparison_rejects_blanks_mixed_crops_and_missing_source(self):
        result = self.page.evaluate("""()=>{
          const c={kind:'condition',id:'same',field:'b:Baseline Crop',op:'eqField',otherField:'e:Crop'};
          const test=(before,after)=>testCondition({b:{values:{'Baseline Crop':before}},e:{values:{Crop:after}}},c);
          const t=clone(tableById('crops'));t.sources=sourceSettings(t);t.sources.ids=['e'];t.change=false;t.filters.source.children=[c];
          let error='';try{filterRecords(t)}catch(e){error=e.message}
          return {matches:[test(' Onion ','onion'),test('', ''),test(null,'Onion'),test('Sorghum, Tomato','Tomato'),test('Cabbage','Onion'),test('  ',' ')],error};
        }""")
        self.assertEqual(result["matches"], [True, False, False, False, False, False])
        self.assertIn("Baseline", result["error"])

    def test_missing_source_cannot_be_applied_or_imported(self):
        p = self.page
        p.evaluate("openBuilder('crops')")
        p.locator('[data-builder-source="b"]').uncheck()
        p.locator('[data-action="apply-builder"]').click()
        p.evaluate("openFilters('crops');addFilterField('b:Baseline Crop')")
        p.get_by_label('Match answers', exact=True).select_option('eqField')
        p.get_by_label('Comparison field', exact=True).select_option('e:Crop')
        self.assertTrue(p.locator('[data-action="apply-filters"]').is_disabled())
        self.assertIn('Baseline', p.locator('#filter-preview').inner_text())
        self.assertEqual(p.evaluate("tableById('crops').filters.source.children.length"), 0)
        error = p.evaluate("""()=>{const saved=clone(state);saved.tables.find(t=>t.id==='crops').filters=clone(filterDraft);try{validateState(saved);return ''}catch(e){return e.message}}""")
        self.assertIn('Baseline', error)

    def test_per_farmer_formula_exclusions_and_value_only_builder(self):
        self.add_definition()
        result = self.page.evaluate("""()=>{
          const pair=(uid,b,e)=>({uid,matched:e!==null,b:{values:{'Net income':b}},...(e===null?{}:{e:{values:{'Net Income':e}}})});
          const rows=[pair('a',100,200),pair('b',400,400),pair('zero',0,50),pair('missing',100,null),pair('negative',-100,-50)];
          const perFarmer=aggregate(rows.slice(0,2),'custom-test-change','value','mean');
          const means=cell(rows.slice(0,2),'net',{stat:'change',from:'b',to:'e'});
          return {mean:perFarmer.value,changeInMeans:means.value,values:rows.map(r=>value(r,'custom-test-change')),n:aggregate(rows,'custom-test-change','value','mean').n};
        }""")
        self.assertEqual(result["mean"], 50)
        self.assertAlmostEqual(result["changeInMeans"], 20)
        self.assertEqual(result["values"], [100, 0, None, None, -50])
        self.assertEqual(result["n"], 3)
        p = self.page
        p.evaluate("openBuilder()")
        p.locator('[data-builder-metric="custom-test-change"]').check()
        p.locator('[data-builder-metric="yield"]').uncheck()
        self.assertEqual(p.evaluate("work.draft.periods"), ["value"])
        self.assertEqual(p.evaluate("work.draft.sources.ids"), ["b", "e"])
        self.assertFalse(p.evaluate("work.draft.change"))
        self.assertEqual(p.locator("#builder-preview thead .source-heading").count(), 0)
        p.locator("#builder-title").fill("Same farmer income change")
        p.locator('[data-action="apply-builder"]').click()
        p.reload()
        self.assertEqual(p.evaluate("state.tables[0].periods"), ["value"])
        p.locator('.table-card').first.screenshot(path=str(ARTIFACTS / "per-farmer-table.png"))

    def test_one_to_one_linking_excludes_duplicate_and_missing_identifiers(self):
        result = self.page.evaluate("""()=>{
          const previous=DATA.sources,record=(name,key)=>({values:{[key]:name}});
          try{
            DATA.sources=[{id:'b',label:'Baseline',records:['Alice','Duplicate','Duplicate',''].map(n=>record(n,'Name'))},{id:'e',label:'Endline',records:[' Alice ','Duplicate',''].map(n=>record(n,'Farmer Name'))}];
            const t=clone(tableById('crops'));t.sources={ids:['b','e'],mode:'separate',records:'matched',identifiers:{b:'b:Name',e:'e:Farmer Name'},changeFrom:'b',changeTo:'e'};
            const matched=recordPool(t);t.sources.records='all';const all=recordPool(t);
            return {matched:matched.length,name:matched[0].b.values.Name,total:all.length,duplicates:all.filter(r=>r.matchReason==='duplicate identifier').length,missing:all.filter(r=>r.matchReason==='missing identifier').length};
          }finally{if(previous===undefined)delete DATA.sources;else DATA.sources=previous;}
        }""")
        self.assertEqual(result, {'matched':1,'name':'Alice','total':6,'duplicates':3,'missing':2})

    def test_source_scope_names_and_retained_unavailable_selection(self):
        p = self.page
        p.evaluate("openBuilder()")
        self.assertEqual(p.locator('#fields-list [data-field="b:Name"]').count(), 1)
        p.locator('[data-builder-source="b"]').uncheck()
        self.assertEqual(p.locator('[data-builder-metric="b:Yield kg"]').count(), 0)
        self.assertEqual(p.locator('#fields-list [data-field="b:Name"]').count(), 0)
        self.assertEqual(p.locator('#fields-list [data-field="e:Farmer Name"]').count(), 1)
        p.locator('[data-builder-source="b"]').check()
        p.locator('#fields-list [data-field="b:Name"]').click()
        p.locator('[data-builder-source="b"]').uncheck()
        self.assertEqual(p.get_by_label("Row level 1").input_value(), "b:Name")
        self.assertIn("Select Baseline", p.locator('#work-error').inner_text())
        p.get_by_label("Remove rows level 1").click()
        self.assertEqual(p.locator('#work-error').inner_text(), "")

    def test_drag_success_and_rejection(self):
        p = self.page
        p.evaluate("openBuilder()")
        self.drag('#fields-list [data-field="e:Crop"]', '#builder-preview th.row-axis-header')
        self.assertEqual(p.evaluate("work.draft.rows"), ["e:Crop"])
        self.drag('#fields-list [data-field="b:Gender"]', '#builder-preview thead th.source-heading')
        self.assertEqual(p.evaluate("work.draft.columns"), ["b:Gender"])
        self.drag('[data-drag-kind="measurement"][data-field="net"]', '#builder-preview tbody td')
        self.assertIn("net", p.evaluate("work.draft.metrics"))
        before = p.evaluate("JSON.stringify(work.draft)")
        self.drag('#fields-list [data-field="e:Region"]', '#builder-preview tbody td')
        self.assertEqual(p.evaluate("JSON.stringify(work.draft)"), before)
        self.assertIn("Drop categories", p.locator('#toast').inner_text())

    def test_chart_order_colour_samples_save_reload(self):
        p = self.page
        p.evaluate("openChart('crops')")
        p.locator('#chart-order').select_option('desc')
        p.locator('#chart-sort-series').select_option(label='Endline mean')
        self.assertTrue(p.locator('#chart-sort-series option').nth(2).evaluate('el=>el.disabled'))
        names = lambda: p.locator('#chart-preview .chart-category-name').evaluate_all("els=>els.map(el=>el.firstChild.textContent)")
        self.assertEqual(names(), ['Cabbage', 'Pepper', 'Tomato', 'Onion'])
        p.locator('#chart-rank-direction').select_option('rtl')
        self.assertEqual(names(), ['Onion', 'Tomato', 'Pepper', 'Cabbage'])
        p.locator('[data-chart-color]').nth(1).fill('#8e3d8e')
        self.assertEqual(p.locator('#chart-preview .chart-bars').first.locator('.vertical-bar').nth(1).evaluate('el=>el.style.backgroundColor'), 'rgb(142, 61, 142)')
        self.assertIn('N=113', p.locator('#chart-preview .chart-samples').first.inner_text())
        p.locator('#chart-samples').select_option('percent')
        self.assertIn('% of', p.locator('#chart-preview .chart-samples').first.inner_text())
        p.screenshot(path=str(ARTIFACTS / 'chart-settings-desktop.png'))
        p.locator('[data-action="chart-save"]').click()
        p.reload()
        chart = p.evaluate("tableById('crops').charts[0]")
        self.assertEqual((chart['order'], chart['rankDirection'], chart['samples']), ('desc', 'rtl', 'percent'))
        self.assertIn('#8e3d8e', chart['colors'].values())

    def test_chart_rejects_mixed_units_and_empty_selection(self):
        p = self.page
        p.evaluate("openChart('crops')")
        p.locator('[data-chart-series]').nth(2).check()
        self.assertTrue(p.locator('[data-action="chart-save"]').is_disabled())
        self.assertIn('different units', p.locator('#chart-preview').inner_text())
        p.locator('[data-chart-series]').nth(0).uncheck()
        p.locator('[data-chart-series]').nth(1).uncheck()
        self.assertFalse(p.locator('[data-action="chart-save"]').is_disabled())
        self.assertEqual(p.locator('#chart-preview .chart-axis-title').inner_text(), 'Change (%)')
        p.locator('[data-chart-series]').nth(2).uncheck()
        self.assertTrue(p.locator('[data-action="chart-save"]').is_disabled())

    def test_sample_percentage_uses_unfiltered_valid_values(self):
        result = self.page.evaluate("""()=>{
          const rows=[100,200,null,0].map((n,i)=>({uid:String(i),e:{values:{'Net Income':n}}}));
          const h={period:'e',stat:'mean',sourceIds:['e']},c=aggregate(rows.slice(0,1),'net','e','mean');
          return {n:sampleText({},'net',h,c,rows,'count'),pct:sampleText({},'net',h,c,rows,'percent'),empty:sampleText({},'net',h,aggregate([],'net','e','mean'),[],'percent')};
        }""")
        self.assertEqual(result, {'n':'N=1', 'pct':'33.3% of 3', 'empty':'No valid records'})
        p = self.page
        p.locator('#table-crops [data-action="sample-display"]').click()
        self.assertIn('% of', p.locator('#table-crops .cell-button small').first.inner_text())
        p.reload()
        self.assertEqual(p.evaluate("tableById('crops').sampleDisplay"), 'percent')

    def test_filter_coverage_uses_each_cell_before_all_table_filters(self):
        self.add_definition()
        result = self.page.evaluate("""()=>{
          const previous=DATA.farmers;
          const record=(uid,crop,gender,b,e,excluded=false)=>({uid,matched:true,
            b:{values:{'Net income':b,'Baseline Crop':excluded?'Excluded':crop,Gender:gender}},
            e:{values:{'Net Income':e,Crop:crop}}});
          try{
            DATA.farmers=[
              ...Array.from({length:14},(_,i)=>record('onion'+i,'Onion','Female',i<3?10:100,i===0?null:20)),
              ...Array.from({length:5},(_,i)=>record('tomato'+i,'Tomato','Female',i<2?10:100,20)),
              record('male','Onion','Male',10,20),record('excluded','Onion','Female',10,20,true),
              {uid:'baseline-only',matched:false,b:{values:{'Net income':10,'Baseline Crop':'Onion',Gender:'Orphan'}}}
            ];
            const t=clone(tableById('overall'));t.metrics=['net'];t.stats=['mean'];t.rows=['b:Gender'];t.columns=['e:Crop'];
            t.sources=sourceSettings(t);t.sources.records='all';t.filters=emptyFilters();
            t.filters.source.children=[{kind:'condition',id:'category',field:'b:Baseline Crop',op:'neq',value:'Excluded'}];
            t.filters.measures.children=[{kind:'condition',id:'threshold',field:'m:net:b',op:'lt',value:50}];
            const read=(table,rowName,groupName,period)=>{
              const d=calculate(table),row=d.rows.find(r=>r.group.label===rowName),h=d.headers.find(h=>h.group.label===groupName&&h.period===period),c=row.cells[d.headers.indexOf(h)];
              const el=document.createElement('div');el.innerHTML=cellSampleHTML(table,row.metric,h,c,d);
              return {n:c.n,total:c.totalRecords,text:el.textContent,title:el.firstChild?.title||''};
            };
            const baseline=read(t,'Female','Onion','b'),endline=read(t,'Female','Onion','e');
            const tomato=read(t,'Female','Tomato','b'),male=read(t,'Male','Onion','b');
            const d=calculate(t),orphan=d.rows.find(r=>r.group.label==='Orphan'),empty=d.headers.find(h=>h.period==='e'&&orphan.cells[d.headers.indexOf(h)].totalRecords===0);
            const emptyEl=document.createElement('div');emptyEl.innerHTML=cellSampleHTML(t,'net',empty,orphan.cells[d.headers.indexOf(empty)],d);
            const combined=clone(t);combined.sources.mode='aggregate';combined.change=false;
            const aggregateResult=read(combined,'Female','Onion','aggregate');
            combined.stats=['count'];const count=read(combined,'Female','Onion','aggregate');
            const formula=clone(t);formula.metrics=['custom-test-change'];formula.periods=['value'];formula.change=false;
            const calculated=read(formula,'Female','Onion','value');
            const categoryOnly=clone(t);categoryOnly.filters.measures=group();
            const category=read(categoryOnly,'Female','Onion','b');
            const rawNumeric=clone(t);rawNumeric.filters.measures=group();rawNumeric.filters.source.children.push({kind:'condition',id:'raw-threshold',field:'b:Net income',op:'lt',value:50});
            const raw=read(rawNumeric,'Female','Onion','b');
            const noOp=clone(t);noOp.filters=emptyFilters();noOp.filters.source.children=[{kind:'condition',id:'present',field:'b:Baseline Crop',op:'present'}];
            const unchanged=read(noOp,'Female','Onion','b');
            return {baseline,endline,tomato,male,aggregateResult,count,calculated,category,raw,unchanged,empty:emptyEl.textContent};
          }finally{DATA.farmers=previous;}
        }""")
        self.assertEqual(result['baseline']['text'], 'N=3 20% of total records')
        self.assertEqual(result['endline']['text'], 'N=2 13% of total records')
        self.assertEqual(result['tomato']['text'], 'N=2 40% of total records')
        self.assertEqual(result['male']['text'], 'N=1 100% of total records')
        self.assertEqual(result['aggregateResult']['text'], 'N=5 17% of total records')
        self.assertEqual(result['count']['text'], 'N=6 20% of total records')
        self.assertEqual(result['calculated']['text'], 'N=2 13% of total records')
        self.assertEqual(result['category']['text'], 'N=14 93% of total records')
        self.assertEqual(result['raw']['text'], 'N=3 20% of total records')
        self.assertEqual(result['unchanged']['text'], 'N=15')
        self.assertEqual(result['empty'], 'N=0 no records before table filters')
        self.assertIn('3 of 15 total records', result['baseline']['title'])

    def test_measurement_filter_coverage_apply_reload_and_clear(self):
        p = self.page
        p.evaluate("openFilters('overall');addFilterField('m:net:e')")
        p.get_by_label('Maximum value', exact=True).fill('100000')
        p.locator('[data-action="apply-filters"]').click()
        samples = p.locator('#table-overall .cell-button:not(.change) small')
        self.assertGreater(samples.count(), 0)
        self.assertTrue(all('N=' in label and '% of total records' in label for label in samples.all_text_contents()))
        self.assertEqual(p.locator('#table-overall .cell-button.change small').count(), 0)
        self.assertEqual(p.locator('#table-overall [data-action="sample-display"]').count(), 0)
        self.assertIn('Sample size: N and %', p.locator('#table-overall .table-meta').inner_text())
        before = samples.all_text_contents()
        p.reload()
        self.assertEqual(samples.all_text_contents(), before)
        for width in [1280, 390, 320]:
            p.set_viewport_size({'width':width,'height':1000})
            overflow = samples.evaluate_all("""els=>els.filter(el=>{
              const cell=el.closest('td').getBoundingClientRect(),range=document.createRange();range.selectNodeContents(el);
              return [...range.getClientRects()].some(r=>r.left<cell.left-1||r.right>cell.right+1);
            }).map(el=>el.textContent)""")
            self.assertEqual(overflow, [])
            self.assertLessEqual(p.evaluate('document.documentElement.scrollWidth'), width)
            if width == 1280:
                p.locator('#table-overall').screenshot(path=str(ARTIFACTS / 'measurement-filter-coverage.png'))
        p.evaluate("openBuilder('overall')")
        self.assertIn('% of total records', p.locator('#builder-preview .cell-button small').first.inner_text())
        self.assertEqual(p.locator('#builder-preview .cell-button.change small').count(), 0)
        p.evaluate('closeWork()')
        p.locator('#table-overall [data-action="clear-filters"]').click()
        self.assertTrue(all(label.startswith('N=') and '%' not in label for label in samples.all_text_contents()))
        self.assertEqual(p.locator('#table-overall [data-action="sample-display"]').count(), 1)

    def test_category_filter_coverage_apply_reload_and_clear(self):
        p = self.page
        p.evaluate("openFilters('overall');addFilterField('e:Crop')")
        p.locator('[data-action="apply-filters"]').click()
        # Selecting all answers is a no-op, so the normal display remains available.
        self.assertEqual(p.locator('#table-overall [data-action="sample-display"]').count(), 1)
        p.evaluate("openFilters('overall')")
        p.locator('[data-action="filter-select-none"]').click()
        p.locator('[data-answer="Onion"]').check()
        p.locator('[data-action="apply-filters"]').click()
        samples = p.locator('#table-overall .cell-button:not(.change) small')
        self.assertTrue(all('N=' in label and '% of total records' in label for label in samples.all_text_contents()))
        self.assertEqual(p.locator('#table-overall .cell-button.change small').count(), 0)
        counts = p.evaluate("(()=>{const d=calculate(tableById('overall'));return {included:d.included.length,all:d.all.length,total:d.rows[0].cells[0].totalRecords}})()")
        self.assertLess(counts['included'], counts['all'])
        self.assertEqual(counts['total'], counts['all'])
        before = samples.all_text_contents()
        p.reload()
        self.assertEqual(samples.all_text_contents(), before)
        p.locator('#table-overall').screenshot(path=str(ARTIFACTS / 'category-filter-coverage.png'))
        p.locator('#table-overall [data-action="clear-filters"]').click()
        self.assertTrue(all(label.startswith('N=') and '%' not in label for label in samples.all_text_contents()))
        self.assertEqual(p.locator('#table-overall [data-action="sample-display"]').count(), 1)

    def test_chart_report_snapshot_and_destination_removal(self):
        p = self.page
        p.evaluate("openChart('crops')")
        p.locator('#chart-title').fill('First chart')
        p.locator('[data-action="chart-save"]').click()
        p.evaluate("openChart('crops')")
        p.locator('#chart-title').fill('Second chart')
        p.locator('[data-action="chart-save"]').click()
        p.locator('#table-crops .chart').first.locator('[data-action="add-chart-report"]').click()
        p.locator('#report-name').fill('Review snapshot')
        p.locator('[data-action="confirm-add-report"]').click()
        self.assertEqual(p.evaluate("state.reports[0].items[0].table.chart.title"), 'First chart')
        self.assertEqual(p.locator('#table-crops .chart').first.locator('.sent-to-report').count(), 1)
        self.assertEqual(p.locator('#table-crops .chart').nth(1).locator('.sent-to-report').count(), 0)
        p.locator('#work-dialog [data-action="close-work"]').last.click()
        p.locator('#table-crops .chart').first.locator('[data-action="chart"]').click()
        p.locator('#chart-title').fill('Edited after snapshot')
        p.locator('[data-action="chart-save"]').click()
        self.assertEqual(p.evaluate("state.reports[0].items[0].table.chart.title"), 'First chart')
        p.locator('#table-crops .chart').first.locator('.sent-to-report').click()
        self.assertEqual(p.locator('#work-dialog h2').inner_text(), 'Review snapshot')
        p.locator('[data-action="remove-snapshot"]').click()
        self.assertEqual(p.locator('#table-crops .sent-to-report').count(), 0)

    def test_keyboard_help_and_narrow_layout(self):
        p = self.page
        for width in [390, 320]:
            p.set_viewport_size({'width':width,'height':844})
            p.evaluate("openBuilder()")
            help_button = p.get_by_label('About categories')
            help_button.focus()
            self.assertTrue(p.locator('.concept-help [role="tooltip"]').first.is_visible())
            help_button.press('Enter')
            self.assertTrue(p.locator('.concept-help').first.evaluate('el=>el.hasAttribute("data-open")'))
            tip = p.locator('.concept-help [role="tooltip"]').first.bounding_box()
            self.assertGreaterEqual(tip['y'], 0)
            self.assertLess(tip['y'] + tip['height'], 774)
            self.assertLessEqual(p.evaluate('document.documentElement.scrollWidth'), width)
            p.screenshot(path=str(ARTIFACTS / f'builder-{width}.png'))
            p.evaluate('closeWork();openChart("crops")')
            self.assertLessEqual(p.locator('#work-dialog').bounding_box()['width'], width)
            p.screenshot(path=str(ARTIFACTS / f'chart-{width}.png'))
            p.evaluate('closeWork()')


if __name__ == '__main__':
    unittest.main()
