"""Checks that the search step finds every passage a correct answer needs.

These are the questions used to test the tutor in class. Run with: python -m unittest
"""

from pathlib import Path
import unittest

from rag import load_guides, retrieve_for_question

PASSAGES, _ = load_guides(Path(__file__).resolve().parent / "docs")

CASES = {
    "Canvas post with directions": (
        "My instructor requires APA 7 in-text citations and a reference list for a Canvas discussion "
        "post and explicitly says to skip the title page. I paraphrased a 2024 journal article by "
        "Rivera, Chen, and Patel. Show me the parenthetical and narrative in-text citations. Do I need "
        "a page number for the paraphrase? Do I need a title page?",
        ["Discussion post", "In-text citation", "Paraphrase"]),
    "42-word quote": (
        "I want to quote 42 words from page 18 of a 2024 article by Rivera, Chen, and Patel. How should "
        "I format the quotation, and what should the parenthetical citation look like? Would I need the "
        "page number if I paraphrased the passage instead?",
        ["Direct quote", "In-text citation", "Paraphrase"]),
    "two authors plus webpage with no date": (
        "For a Canvas discussion post, I paraphrased an idea from a 2022 journal article by Martinez and "
        "Kowalski. I also used a webpage from the Centers for Disease Control and Prevention that has no "
        "publication date. What are the parenthetical citations for each source, and do I need page numbers?",
        ["In-text citation", "Paraphrase", "Webpage"]),
    "title page": ("Do I need a title page?", ["Student title page"]),
    "paraphrase": ("Do I need a page number when I paraphrase?", ["Paraphrase"]),
    "hanging indent": ("hanging indent", ["Reference list"]),
    "website": ("How do I cite a website with no date?", ["Webpage"]),
    "book": ("How do I cite a book?", ["Book reference"]),
}


class RetrievalTests(unittest.TestCase):
    def test_every_needed_passage_is_found(self):
        for name, (question, needed) in CASES.items():
            with self.subTest(name):
                headings = [p.heading for p in retrieve_for_question(question, PASSAGES, limit=4)]
                for start in needed:
                    self.assertTrue(any(h.startswith(start) for h in headings),
                                    f"{name}: missing '{start}' in {headings}")


if __name__ == "__main__":
    unittest.main()
