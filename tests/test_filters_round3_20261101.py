"""Filters drawer, round 3 (1 November 2026): less on screen, plainer words.

- The empty drawer shows only Add filter and the record count, no suggestion helper.
- "Match answers" offers Keep selected and Match across data sources; "Remove selected" is gone,
  but saved filters that remove answers (op notin) still load, apply and render.
- The comparison card has no "Has the same answer as" heading above its select.

Run with the existing suite: python -m unittest discover -s tests -v
"""
import unittest

import test_feedback_20260922 as previous

# A saved table whose filter removes the first crop answer, as older versions could save.
SAVE_NOTIN = """() => {
  openFilters(state.tables[0].id);
  const saved = clone(state), crop = filterChoices('q:crop').values[0];
  saved.tables[0].filters.source.children = [{kind: 'condition', id: 'old-notin', field: 'q:crop', op: 'notin', values: [crop], value: '', high: '', refs: []}];
  localStorage.setItem(STORAGE_KEY, JSON.stringify(saved));
  return crop;
}"""


class FiltersRoundThreeTests(unittest.TestCase):
    setUpClass = classmethod(previous.FeedbackBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(previous.FeedbackBrowserTests.tearDownClass.__func__)
    setUp = previous.FeedbackBrowserTests.setUp
    tearDown = previous.FeedbackBrowserTests.tearDown

    def test_empty_drawer_shows_only_add_filter_and_count(self):
        p = self.page
        p.evaluate('openFilters(state.tables[0].id)')
        body = p.locator('#filter-body')
        text = body.inner_text()
        for gone in ['Narrow this table', 'Or choose Add filter', 'N count', 'minimum records per cell']:
            self.assertNotIn(gone, text)
        self.assertEqual(body.locator('.filter-empty, .suggest-chip, [aria-label="Suggested filters"]').count(), 0)
        self.assertTrue(body.locator('[data-action="toggle-filter-picker"]').is_visible())
        self.assertRegex(p.locator('#filter-result').inner_text(), r'\d')
        self.assertEqual(p.locator('.filter-list').evaluate('el => el.children.length'), 0)
        self.assertEqual(p.evaluate('typeof filterSuggestionsHTML'), 'undefined')
        # Suggested questions still rank first in the Add filter search.
        p.locator('[data-action="toggle-filter-picker"]').click()
        p.locator('#field-search').click()
        first = p.locator('#field-results [role=option]').first.inner_text()
        self.assertTrue(first.startswith(tuple(p.evaluate('filterSuggestedFields().map(fieldOptionLabel)'))), first)

    def test_match_answers_offers_keep_and_match_across_sources(self):
        p = self.page
        p.evaluate("openFilters(state.tables[0].id); addFilterField('q:crop')")
        card = p.locator('.filter-condition').last
        self.assertEqual(card.locator('.filter-mode label span').all_inner_texts(), ['Keep selected', 'Match across data sources'])
        self.assertEqual(card.get_by_label('Remove selected', exact=True).count(), 0)
        self.assertEqual(p.evaluate('filterOperatorLabels.eqField'), 'Match across data sources')
        self.assertNotIn('Same as another field', p.locator('#filter-body').inner_text())

    def test_comparison_card_has_no_heading_above_the_select(self):
        p = self.page
        p.evaluate("openFilters(state.tables[0].id); addFilterField('q:crop')")
        p.get_by_label('Match across data sources', exact=True).check()
        card = p.locator('.filter-condition').last
        self.assertNotIn('Has the same answer as', card.inner_text())
        self.assertEqual(card.get_by_label('Comparison field', exact=True).input_value(), 'q:crop')
        self.assertIn('same answer in every data source', card.locator('.filter-compare-hint').inner_text())

    def test_saved_remove_filter_still_loads_applies_and_renders(self):
        p = self.page
        crop = p.evaluate(SAVE_NOTIN)
        p.reload()
        table = p.evaluate('state.tables[0].filters.source.children[0]')
        self.assertEqual((table['op'], table['values']), ('notin', [crop]))
        p.evaluate('validateFilters(state.tables[0].filters)')
        result = p.evaluate("""(crop) => { const r = calculate(state.tables[0]), key = v => blank(v) ? '' : String(v).trim().toLowerCase();
          const has = rec => answersOf(rec, 'q:crop').some(a => key(a.value) === key(crop));
          return {n: r.included.length, total: r.all.length, leaked: r.included.filter(has).length, removed: r.all.filter(has).length}; }""", crop)
        self.assertEqual(result['leaked'], 0)
        self.assertGreater(result['removed'], 0)
        self.assertLess(result['n'], result['total'])
        # The drawer shows the current choice in the select instead of an unchecked radio group.
        p.evaluate('openFilters(state.tables[0].id)')
        card = p.locator('.filter-condition').first
        self.assertEqual(card.locator('.filter-mode').count(), 0)
        select = card.get_by_label('Match answers', exact=True)
        self.assertEqual(select.input_value(), 'notin')
        self.assertEqual(select.locator('option').all_inner_texts(), ['Keep only the selected answers', 'Match across data sources', 'Remove the selected answers'])
        self.assertEqual(card.locator('.filter-operator-note').count(), 0, 'The select already names the choice')
        self.assertRegex(card.locator('.condition-summary').inner_text(), r'^Removing 1 of \d+ answers$')
        self.assertTrue(card.locator(f'input[data-answer="{crop}"]').is_checked())
        self.assertRegex(p.locator('#filter-preview').inner_text(), rf"^{result['n']} of {result['total']} records match")
        self.assertFalse(p.locator('[data-action="apply-filters"]').is_disabled())
        # Choosing Keep moves the card back to the two plain choices.
        select.select_option('in')
        self.assertEqual(p.locator('.filter-condition').first.locator('.filter-mode label span').all_inner_texts(), ['Keep selected', 'Match across data sources'])

    def test_drawer_fits_at_desktop_and_phone_widths(self):
        p = self.page
        p.evaluate(SAVE_NOTIN)
        p.reload()
        for width in [1440, 390]:
            p.set_viewport_size({'width': width, 'height': 900})
            p.evaluate("openFilters(state.tables[0].id); addFilterField('q:crop')")
            p.locator('.filter-condition').last.get_by_label('Match across data sources', exact=True).check()
            self.assertLessEqual(p.evaluate("document.querySelector('#filter-body').scrollWidth - document.querySelector('#filter-body').clientWidth"), 0)
            p.screenshot(path=str(previous.ARTIFACTS / f'filters-round3-{width}.png'))
            p.evaluate("document.querySelector('#filter-dialog').close()")
            p.evaluate("openFilters(state.tables[1].id)")
            p.screenshot(path=str(previous.ARTIFACTS / f'filters-round3-empty-{width}.png'))
            p.evaluate("document.querySelector('#filter-dialog').close()")


if __name__ == '__main__':
    unittest.main()
