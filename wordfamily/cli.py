"""命令行入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .model import (
    FAMILIES,
    HIDES,
    WordFamilyError,
    family_words,
    generate_problems,
    normalize_family,
    rhymes,
    word_family,
)
from .render import render_family_cards, render_worksheet


def build_parser() -> argparse.ArgumentParser:
    """构造命令行解析器。"""
    parser = argparse.ArgumentParser(
        prog="wordfamily",
        description="英语词族：卡片、单词查询与补全练习纸",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("families", help="列出全部词族")

    words = subparsers.add_parser("words", help="列出一个词族的单词")
    words.add_argument("family", help="词族，如 -at 或 at")

    rhyme = subparsers.add_parser("rhyme", help="判断两个单词是否押韵")
    rhyme.add_argument("first", help="第一个单词")
    rhyme.add_argument("second", help="第二个单词")

    cards = subparsers.add_parser("cards", help="输出词族卡片 HTML")
    cards.add_argument("--families", default=None, help="词族列表，逗号分隔，默认全部")
    cards.add_argument("--title", default="英语词族卡片", help="标题")
    cards.add_argument("-o", "--output", default=None, help="输出文件")

    sheet = subparsers.add_parser("sheet", help="生成 A4 补全练习纸")
    sheet.add_argument("--count", type=int, default=8, help="题目数量，默认 8")
    sheet.add_argument("--families", default=None, help="词族列表，逗号分隔，默认全部")
    sheet.add_argument("--hides", default=",".join(HIDES), help="隐藏位置，逗号分隔：onset、rime")
    sheet.add_argument("--seed", type=int, default=None, help="随机种子")
    sheet.add_argument("--title", default="词族补全练习", help="练习纸标题")
    sheet.add_argument("--answers", action="store_true", help="追加参考答案")
    sheet.add_argument("-o", "--output", default=None, help="输出文件")
    return parser


def _write_output(text: str, output: Optional[str]) -> None:
    if not output:
        print(text)
        return
    path = Path(output)
    if path.parent and str(path.parent) not in ("", "."):
        path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("已写入 %s" % path)


def _split_list(text: Optional[str]) -> Optional[List[str]]:
    if not text:
        return None
    parts = [part.strip() for part in text.split(",") if part.strip()]
    if not parts:
        raise WordFamilyError("列表不能为空")
    return parts


def _normalize_argv(argv: List[str]) -> List[str]:
    """把 -at、-at,-an 这类词族参数去掉前导连字符，避免被当成选项。"""
    result: List[str] = []
    for token in argv:
        if (
            token.startswith("-")
            and not token.startswith("--")
            and token not in ("-h", "-o")
        ):
            parts = [part.strip() for part in token.split(",")]
            if parts and all(
                part.startswith("-") and part[1:].isalpha() for part in parts
            ):
                token = ",".join(part.lstrip("-") for part in parts)
        result.append(token)
    return result


def main(argv: Optional[List[str]] = None) -> int:
    """命令行主函数，返回进程退出码。"""
    parser = build_parser()
    raw = list(sys.argv[1:]) if argv is None else list(argv)
    args = parser.parse_args(_normalize_argv(raw))
    try:
        if args.command == "families":
            for family, words in FAMILIES.items():
                print("%-4s %d 个：%s" % (family, len(words), ", ".join(words)))
            return 0
        if args.command == "words":
            family = normalize_family(args.family)
            print("%s：%s" % (family, ", ".join(family_words(family))))
            return 0
        if args.command == "rhyme":
            same = rhymes(args.first, args.second)
            print("%s 与 %s %s押韵" % (args.first, args.second, "" if same else "不"))
            print("词族：%s / %s" % (word_family(args.first), word_family(args.second)))
            return 0 if same else 1
        if args.command == "cards":
            _write_output(
                render_family_cards(_split_list(args.families), args.title), args.output
            )
            return 0
        problems = generate_problems(
            args.count,
            _split_list(args.families),
            _split_list(args.hides) or [],
            args.seed,
        )
        _write_output(render_worksheet(problems, args.title, args.answers), args.output)
        return 0
    except WordFamilyError as exc:
        print("错误：%s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("写入失败：%s" % exc, file=sys.stderr)
        return 1
