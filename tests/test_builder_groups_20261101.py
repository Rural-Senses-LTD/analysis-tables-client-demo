"""Regressions for the 1 November request: only clear, readable groups in "Create table".

Run with the existing suite: python -m unittest discover -s tests -v
"""
import unittest

import test_feedback_20260922 as previous

# Fewest distinct non-blank answers among the builder's selected sources, computed here without the app's helper.
INDEPENDENT_COUNTS = """(() => {
  const ids = work.draft.sources.ids, counts = {};
  for (const f of builderCategoryFields()) {
    const q = questionMap.get(f.id);
    const sizes = dataSources().filter(s => ids.includes(s.id) && (!q || q.fields[s.id])).map(s =>
      new Set(s.records.map(rec => value({[s.id]: rec}, q ? q.fields[s.id] : f.id))
        .filter(v => !blank(v)).map(v => String(v).trim())).size).filter(Boolean);
    counts[f.label] = Math.min(...sizes);
  }
  return counts;
})()"""


class BuilderGroupsTests(unittest.TestCase):
    setUpClass = classmethod(previous.FeedbackBrowserTests.setUpClass.__func__)
    tearDownClass = classmethod(previous.FeedbackBrowserTests.tearDownClass.__func__)
    setUp = previous.FeedbackBrowserTests.setUp
    tearDown = previous.FeedbackBrowserTests.tearDown

    def labels(self):
        return self.page.evaluate("builderCategoryFields().map(f => f.label)")

    def test_new_table_hides_name_like_and_unclear_groups(self):
        self.page.evaluate("openBuilder()")
        labels = self.labels()
        for gone in ["Name", "Farmer Name", "Officer Name", "Farmer_UID", "Income #1", "Income #2",
                     "Income #1 (standardized", "Income #2 (standardized"]:
            self.assertNotIn(gone, labels)
        self.assertFalse([x for x in labels if "#" in x], "enumerated labels are unclear")
        for kept in ["Crop", "Region", "Gender", "Project"]:
            self.assertIn(kept, labels)
        # The groups panel shows the same filtered list.
        shown = self.page.locator("[data-field-label]").evaluate_all("items => items.map(x => x.dataset.fieldLabel)")
        self.assertTrue(shown)
        self.assertFalse([x for x in shown if x in ("name", "farmer name", "officer name") or "#" in x])

    def test_every_listed_group_has_at_most_ten_values(self):
        self.page.evaluate("openBuilder()")
        counts = self.page.evaluate(INDEPENDENT_COUNTS)
        self.assertTrue(counts)
        self.assertEqual({k: v for k, v in counts.items() if v > 10}, {})

    def test_group_already_in_table_stays_listed(self):
        p = self.page
        p.evaluate("openBuilder()")
        self.assertNotIn("Officer Name", self.labels())
        p.evaluate("work.draft.rows.push('q:officer_name')")
        self.assertIn("Officer Name", self.labels())
        # A preset that groups by a source column (Wareda) keeps the shared question available.
        p.evaluate("openBuilder('area')")
        self.assertIn("e:Wareda", p.evaluate("work.draft.rows"))
        self.assertIn("q:woreda", p.evaluate("builderCategoryFields().map(f => f.id)"))

    def test_value_counts_follow_selected_sources(self):
        p = self.page
        p.evaluate("openBuilder()")
        self.assertIn("Crop", self.labels())
        # Baseline alone answers crop with many free-text combinations, so it is no longer a readable group there.
        p.evaluate("work.draft.sources.ids = ['b']")
        self.assertNotIn("Crop", self.labels())
        self.assertIn("Gender", self.labels())


if __name__ == "__main__":
    unittest.main()
