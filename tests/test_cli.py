"""命令行行为测试。"""

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from wordfamily.cli import main


def run(args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(args)
    return code, out.getvalue(), err.getvalue()


class CliTest(unittest.TestCase):
    def test_help(self):
        with self.assertRaises(SystemExit) as ctx:
            main(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_families(self):
        code, out, _ = run(["families"])
        self.assertEqual(code, 0)
        self.assertEqual(len(out.strip().splitlines()), 12)
        self.assertIn("-at", out)

    def test_words(self):
        code, out, _ = run(["words", "-at"])
        self.assertEqual(code, 0)
        self.assertIn("cat", out)
        self.assertIn("hat", out)

    def test_words_bare(self):
        code, out, _ = run(["words", "ig"])
        self.assertEqual(code, 0)
        self.assertIn("pig", out)

    def test_words_unknown(self):
        code, _, err = run(["words", "-ab"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_rhyme_true(self):
        code, out, _ = run(["rhyme", "cat", "hat"])
        self.assertEqual(code, 0)
        self.assertIn("押韵", out)

    def test_rhyme_false(self):
        code, out, _ = run(["rhyme", "cat", "can"])
        self.assertEqual(code, 1)
        self.assertIn("不押韵", out)

    def test_rhyme_unknown(self):
        code, _, err = run(["rhyme", "cat", "dog"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_cards_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "cards.html"
            code, out, _ = run(["cards", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())
            self.assertIn("已写入", out)

    def test_cards_subset(self):
        code, out, _ = run(["cards", "--families", "-at,-an"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count('class="family"'), 2)

    def test_sheet_stdout(self):
        code, out, _ = run(["sheet", "--count", "3", "--seed", "1"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count('class="card"'), 3)

    def test_sheet_family_filter(self):
        code, out, _ = run(["sheet", "--count", "4", "--families", "-at", "--seed", "2"])
        self.assertEqual(code, 0)
        self.assertIn("本页词族：-at", out)

    def test_sheet_hide_filter(self):
        code, out, _ = run(["sheet", "--count", "4", "--hides", "rime", "--seed", "3"])
        self.assertEqual(code, 0)
        self.assertEqual(out.count('class="card"'), 4)
        self.assertGreaterEqual(out.count("____"), 4)

    def test_sheet_answers(self):
        code, out, _ = run(["sheet", "--count", "3", "--seed", "4", "--answers"])
        self.assertEqual(code, 0)
        self.assertIn("参考答案", out)

    def test_sheet_bad_family(self):
        code, _, err = run(["sheet", "--families", "-ab"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_sheet_bad_hide(self):
        code, _, err = run(["sheet", "--hides", "middle"])
        self.assertEqual(code, 2)
        self.assertIn("隐藏位置", err)

    def test_sheet_empty_hides(self):
        code, _, err = run(["sheet", "--hides", " , "])
        self.assertEqual(code, 2)
        self.assertIn("不能为空", err)

    def test_sheet_too_many(self):
        code, _, err = run(["sheet", "--count", "999"])
        self.assertEqual(code, 2)
        self.assertIn("错误", err)

    def test_sheet_to_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "sheet.html"
            code, _, _ = run(["sheet", "--count", "4", "--seed", "5", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertEqual(target.read_text(encoding="utf-8").count('class="card"'), 4)

    def test_nested_output(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "a" / "cards.html"
            code, _, _ = run(["cards", "-o", str(target)])
            self.assertEqual(code, 0)
            self.assertTrue(target.exists())


if __name__ == "__main__":
    unittest.main()
