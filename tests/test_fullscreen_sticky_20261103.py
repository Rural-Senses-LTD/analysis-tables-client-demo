"""Full screen keeps the table's column headers at the top and its row headers at the left (3 November 2026).

Run with the existing suite: python -m unittest discover -s tests -v
"""
import unittest

import test_feedback_20260922 as previous


class FullscreenStickyHeaderTests(unittest.TestCase):
    setUpClass = classmethod(previous.FeedbackBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(previous.FeedbackBrowserTests.tearDownClass.__func__)
    setUp = previous.FeedbackBrowserTests.setUp
    tearDown = previous.FeedbackBrowserTests.tearDown

    def test_headers_stay_in_place_while_the_table_scrolls(self):
        p = self.page
        for width in [1000, 390]:
            p.set_viewport_size({'width': width, 'height': 800})
            # A wide, tall table: regions and crops down the side, projects with mean, median and change across.
            p.evaluate("const t=tableById('region');t.columns=['q:project'];t.stats=['mean','median'];t.change=true;t.changeStat='mean';render()")
            p.locator('#table-region [data-action="fullscreen"]').click()
            p.wait_for_function("document.fullscreenElement?.id === 'table-region'")
            before = p.evaluate("""(() => { const card = document.querySelector('#table-region');
              return {head: card.querySelector('.matrix thead').getBoundingClientRect().top, row: card.querySelector('.matrix tbody tr th').getBoundingClientRect().left}; })()""")
            moved = p.evaluate("""(() => { const card = document.querySelector('#table-region'), box = card.querySelector('.matrix-scroll');
              box.scrollTop = 600; box.scrollLeft = 300;
              return {scrolled: [box.scrollTop, box.scrollLeft], cardScroll: card.scrollTop,
                      head: card.querySelector('.matrix thead').getBoundingClientRect().top, row: card.querySelector('.matrix tbody tr th').getBoundingClientRect().left,
                      title: card.querySelector('.table-sticky-heading').getBoundingClientRect().top}; })()""")
            self.assertGreater(moved['scrolled'][0], 0, 'The table scrolls down inside its own box')
            self.assertGreater(moved['scrolled'][1], 0, 'The table scrolls sideways inside its own box')
            self.assertEqual(moved['cardScroll'], 0, 'The title stays put')
            self.assertAlmostEqual(moved['head'], before['head'], delta=1, msg='Column headers stay at the top')
            self.assertAlmostEqual(moved['row'], before['row'], delta=1, msg='Row headers stay at the left')
            self.assertGreaterEqual(moved['title'], 0)
            previous.ARTIFACTS.mkdir(parents=True, exist_ok=True)
            p.screenshot(path=str(previous.ARTIFACTS / f'20261103-fullscreen-sticky-{width}.png'))
            p.evaluate("document.exitFullscreen()")
            p.wait_for_function("!document.fullscreenElement")


    def test_regular_view_headers_are_not_sticky(self):
        p = self.page
        p.evaluate("const t=tableById('region');t.columns=['q:project'];t.stats=['mean','median'];t.change=true;t.changeStat='mean';render()")
        positions = p.evaluate("""(() => { const card = document.querySelector('#table-region');
          return [...new Set([card.querySelector('.matrix thead'), ...card.querySelectorAll('.matrix th:first-child, .matrix .row-axis-header')].map(el => getComputedStyle(el).position))]; })()""")
        self.assertEqual(positions, ['static'])
        before = p.evaluate("document.querySelector('#table-region .matrix tbody tr th').getBoundingClientRect().left")
        p.evaluate("document.querySelector('#table-region .matrix-scroll').scrollLeft = 300")
        after = p.evaluate("document.querySelector('#table-region .matrix tbody tr th').getBoundingClientRect().left")
        self.assertLess(after, before - 100, 'Row headers scroll with the table in the regular view')

if __name__ == '__main__':
    unittest.main()
