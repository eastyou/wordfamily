"""词族渲染测试。"""

import unittest

from wordfamily.model import FAMILIES, WORD_FAMILY, WordFamilyError, generate_problems
from wordfamily.render import render_family_cards, render_family_map, render_worksheet


class CardsTest(unittest.TestCase):
    def test_skeleton(self):
        page = render_family_cards()
        self.assertIn("<!DOCTYPE html>", page)
        self.assertTrue(page.rstrip().endswith("</html>"))

    def test_family_count(self):
        page = render_family_cards()
        self.assertEqual(page.count('class="family"'), 12)

    def test_all_words(self):
        page = render_family_cards()
        self.assertEqual(page.count('class="chip"'), 76)

    def test_family_headers(self):
        page = render_family_cards()
        for family in FAMILIES:
            self.assertIn(">%s</h2>" % family, page)

    def test_subset(self):
        page = render_family_cards(["-at", "at"])
        self.assertEqual(page.count('class="family"'), 2)

    def test_bad_family(self):
        with self.assertRaises(WordFamilyError):
            render_family_cards(["-ab"])

    def test_empty(self):
        with self.assertRaises(WordFamilyError):
            render_family_cards([])

    def test_custom_title(self):
        page = render_family_cards(title="一年级词族")
        self.assertIn("一年级词族", page)

    def test_escaping(self):
        page = render_family_cards(title="A & B")
        self.assertIn("A &amp; B", page)

    def test_family_map_copy(self):
        mapping = render_family_map()
        self.assertEqual(mapping["-at"][0], "cat")
        mapping["-at"].append("zzz")
        self.assertNotIn("zzz", FAMILIES["-at"])


class WorksheetTest(unittest.TestCase):
    def setUp(self):
        self.items = generate_problems(8, seed=11)

    def test_skeleton(self):
        page = render_worksheet(self.items)
        self.assertIn("<!DOCTYPE html>", page)
        self.assertTrue(page.rstrip().endswith("</html>"))

    def test_cards(self):
        page = render_worksheet(self.items)
        self.assertEqual(page.count('class="card"'), 8)

    def test_family_hints(self):
        page = render_worksheet(self.items)
        self.assertIn("本页词族", page)
        for item in self.items:
            self.assertIn(item.hint, page)

    def test_no_answers(self):
        self.assertNotIn("参考答案", render_worksheet(self.items))

    def test_answers(self):
        page = render_worksheet(self.items, answers=True)
        self.assertIn("参考答案", page)
        self.assertEqual(page.count("<tr>"), 9)

    def test_answer_words(self):
        page = render_worksheet(self.items, answers=True)
        for item in self.items:
            self.assertIn(item.full, page)

    def test_custom_title(self):
        page = render_worksheet(self.items, title="二班词族")
        self.assertIn("二班词族", page)

    def test_empty(self):
        with self.assertRaises(WordFamilyError):
            render_worksheet([])

    def test_bad_item(self):
        with self.assertRaises(WordFamilyError):
            render_worksheet(["cat"])

    def test_all_prompts_present(self):
        page = render_worksheet(self.items)
        for item in self.items:
            self.assertIn(item.prompt, page)


if __name__ == "__main__":
    unittest.main()
