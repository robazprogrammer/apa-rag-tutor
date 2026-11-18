"""Run with: python -m unittest"""

import unittest

from citations import CitationError, build_citation


class CitationTests(unittest.TestCase):
    def test_one_author(self):
        c = build_citation("Rivera", "2024")
        self.assertEqual(c.parenthetical, "(Rivera, 2024)")
        self.assertEqual(c.narrative, "Rivera (2024)")

    def test_two_authors_use_ampersand_and_and(self):
        c = build_citation("Rivera, Chen", "2024")
        self.assertEqual(c.parenthetical, "(Rivera & Chen, 2024)")
        self.assertEqual(c.narrative, "Rivera and Chen (2024)")

    def test_three_authors_use_et_al_with_page(self):
        c = build_citation("Rivera, Chen, and Patel", "2024", "page", "18", quote_words=42)
        self.assertEqual(c.parenthetical, "(Rivera et al., 2024, p. 18)")
        self.assertTrue(c.narrative.startswith("Rivera et al. (2024)"))
        self.assertIn("Block quote", c.placement)

    def test_block_quote_narrative_has_no_quotation_marks(self):
        c = build_citation("Rivera, Chen, Patel", "2024", "page", "18", quote_words=42)
        self.assertEqual(c.narrative, "Rivera et al. (2024) … [block quote, no quotation marks] (p. 18)")

    def test_short_quote_and_page_range(self):
        c = build_citation("Lee & Santos", "2023", "page", "27-28", quote_words=12)
        self.assertEqual(c.parenthetical, "(Lee & Santos, 2023, pp. 27–28)")
        self.assertIn("Short quote", c.placement)

    def test_paragraph_and_no_date(self):
        c = build_citation("American Psychological Association", "nd", "paragraph", "4", quote_words=10)
        self.assertEqual(c.parenthetical, "(American Psychological Association, n.d., para. 4)")

    def test_quote_without_locator_warns(self):
        c = build_citation("Rivera", "2024", quote_words=10)
        self.assertTrue(any("locator" in note for note in c.notes))

    def test_paraphrase_page_is_optional(self):
        c = build_citation("Rivera", "2024")
        self.assertIn("optional", c.placement)

    def test_organization_name_with_and_stays_whole(self):
        c = build_citation("U.S. Department of Health and Human Services", "2023")
        self.assertEqual(c.parenthetical, "(U.S. Department of Health and Human Services, 2023)")

    def test_and_after_comma_is_a_separator(self):
        c = build_citation("Rivera, Chen, and Patel", "2024")
        self.assertEqual(c.parenthetical, "(Rivera et al., 2024)")

    def test_bad_input(self):
        for authors, year in [("", "2024"), ("Rivera", "24"), ("Rivera", "last year")]:
            with self.assertRaises(CitationError):
                build_citation(authors, year)


if __name__ == "__main__":
    unittest.main()
