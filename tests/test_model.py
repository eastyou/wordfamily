"""词族模型测试。"""

import unittest

from wordfamily.model import (
    FAMILIES,
    HIDES,
    WORD_FAMILY,
    WordFamilyError,
    WordProblem,
    check_answer,
    check_hide,
    family_words,
    generate_problems,
    normalize_family,
    rhymes,
    split_word,
    word_family,
)


class FamilyDataTest(unittest.TestCase):
    """逐一检查十二个词族。"""


def _make_family_test(family, words):
    def test(self):
        rime = family[1:]
        self.assertEqual(normalize_family(family), family)
        self.assertEqual(normalize_family(rime), family)
        self.assertEqual(family_words(family), list(words))
        for word in words:
            self.assertTrue(word.endswith(rime))
            self.assertGreater(len(word), len(rime))
            self.assertEqual(word_family(word), family)

    test.__doc__ = "%s 词族数据" % family
    return test


for _family, _words in FAMILIES.items():
    setattr(FamilyDataTest, "test_%s" % _family.lstrip("-"), _make_family_test(_family, _words))


class WordSplitTest(unittest.TestCase):
    """逐一检查每个单词的拆分。"""


def _make_word_test(word, family):
    def test(self):
        onset, found = split_word(word)
        self.assertEqual(found, family)
        self.assertEqual(onset + family[1:], word)
        self.assertTrue(onset)
        self.assertEqual(word_family(word), family)

    test.__doc__ = "%s 的拆分" % word
    return test


for _word, _family in WORD_FAMILY.items():
    setattr(WordSplitTest, "test_%s" % _word, _make_word_test(_word, _family))


class ProblemTest(unittest.TestCase):
    """逐一检查两种挖空形式。"""


def _make_problem_test(word, index):
    hide = HIDES[index % len(HIDES)]
    family = WORD_FAMILY[word]

    def test(self):
        problem = WordProblem(word, hide)
        self.assertEqual(problem.family, family)
        self.assertEqual(problem.full, word)
        self.assertEqual(problem.hint, "词族 %s" % family)
        self.assertEqual(problem.prompt.count("____"), 1)
        if hide == "onset":
            self.assertEqual(problem.prompt, "____" + family[1:])
            self.assertEqual(problem.answer, split_word(word)[0])
        else:
            self.assertEqual(problem.prompt, split_word(word)[0] + "____")
            self.assertEqual(problem.answer, family[1:])
        self.assertEqual(problem.onset + problem.rime, word)

    test.__doc__ = "%s 挖空 %s" % (word, hide)
    return test


for _index, _word in enumerate(WORD_FAMILY):
    setattr(WordSplitTest, "test_problem_%s" % _word, _make_problem_test(_word, _index))


class RhymeTest(unittest.TestCase):
    def test_same_family(self):
        self.assertTrue(rhymes("cat", "hat"))

    def test_different_family(self):
        self.assertFalse(rhymes("cat", "can"))

    def test_same_word(self):
        self.assertTrue(rhymes("sun", "sun"))

    def test_unknown(self):
        with self.assertRaises(WordFamilyError):
            rhymes("cat", "dog")

    def test_stop(self):
        self.assertTrue(rhymes("stop", "top"))
        self.assertEqual(split_word("stop"), ("st", "-op"))


class ValidationTest(unittest.TestCase):
    def test_normalize_bare(self):
        self.assertEqual(normalize_family("at"), "-at")

    def test_normalize_upper(self):
        self.assertEqual(normalize_family(" AT "), "-at")

    def test_normalize_unknown(self):
        with self.assertRaises(WordFamilyError):
            normalize_family("-ab")

    def test_normalize_empty(self):
        with self.assertRaises(WordFamilyError):
            normalize_family("  ")

    def test_normalize_not_string(self):
        with self.assertRaises(WordFamilyError):
            normalize_family(3)  # type: ignore[arg-type]

    def test_hide_valid(self):
        for hide in HIDES:
            self.assertEqual(check_hide(hide), hide)

    def test_hide_invalid(self):
        with self.assertRaises(WordFamilyError):
            check_hide("middle")

    def test_unknown_word(self):
        with self.assertRaises(WordFamilyError):
            word_family("dog")

    def test_word_not_string(self):
        with self.assertRaises(WordFamilyError):
            word_family(12)  # type: ignore[arg-type]

    def test_bad_hide(self):
        with self.assertRaises(WordFamilyError):
            WordProblem("cat", "middle")

    def test_bad_word(self):
        with self.assertRaises(WordFamilyError):
            WordProblem("dog", "onset")

    def test_frozen(self):
        problem = WordProblem("cat", "onset")
        with self.assertRaises(AttributeError):
            problem.hide = "rime"  # type: ignore[misc]

    def test_total_words(self):
        self.assertEqual(len(WORD_FAMILY), 76)
        self.assertEqual(len(FAMILIES), 12)


class GenerateTest(unittest.TestCase):
    def test_count(self):
        self.assertEqual(len(generate_problems(10, seed=1)), 10)

    def test_unique(self):
        items = generate_problems(20, seed=2)
        keys = [(item.word, item.hide) for item in items]
        self.assertEqual(len(keys), len(set(keys)))

    def test_single_family(self):
        items = generate_problems(10, ["-at"], seed=3)
        self.assertTrue(all(item.family == "-at" for item in items))

    def test_bare_family_name(self):
        items = generate_problems(5, ["at"], seed=4)
        self.assertTrue(all(item.family == "-at" for item in items))

    def test_single_hide(self):
        items = generate_problems(8, hides=["rime"], seed=5)
        self.assertTrue(all(item.hide == "rime" for item in items))

    def test_seed_reproducible(self):
        self.assertEqual(generate_problems(8, seed=6), generate_problems(8, seed=6))

    def test_seed_differs(self):
        self.assertNotEqual(generate_problems(8, seed=6), generate_problems(8, seed=7))

    def test_zero_count(self):
        with self.assertRaises(WordFamilyError):
            generate_problems(0)

    def test_bool_count(self):
        with self.assertRaises(WordFamilyError):
            generate_problems(True)

    def test_empty_hides(self):
        with self.assertRaises(WordFamilyError):
            generate_problems(3, hides=[])

    def test_bad_hide(self):
        with self.assertRaises(WordFamilyError):
            generate_problems(3, hides=["middle"])

    def test_too_many(self):
        with self.assertRaises(WordFamilyError):
            generate_problems(500)

    def test_family_capacity(self):
        self.assertEqual(len(generate_problems(16, ["-at"], seed=8)), 16)

    def test_both_hides_present(self):
        items = generate_problems(20, seed=9)
        self.assertEqual({item.hide for item in items}, set(HIDES))


class AnswerTest(unittest.TestCase):
    def test_correct_onset(self):
        self.assertTrue(check_answer(WordProblem("cat", "onset"), "c"))

    def test_correct_rime(self):
        self.assertTrue(check_answer(WordProblem("cat", "rime"), "at"))

    def test_case_insensitive(self):
        self.assertTrue(check_answer(WordProblem("cat", "onset"), "C"))

    def test_incorrect(self):
        self.assertFalse(check_answer(WordProblem("cat", "onset"), "b"))

    def test_bad_problem(self):
        with self.assertRaises(WordFamilyError):
            check_answer("cat", "c")

    def test_bad_answer(self):
        with self.assertRaises(WordFamilyError):
            check_answer(WordProblem("cat", "onset"), 3)


if __name__ == "__main__":
    unittest.main()
