"""英语词族的数据模型。"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

FAMILIES: Dict[str, Tuple[str, ...]] = {
    "-at": ("cat", "bat", "hat", "mat", "rat", "sat", "fat", "pat"),
    "-an": ("can", "fan", "man", "pan", "ran", "tan", "van"),
    "-ap": ("cap", "gap", "map", "nap", "tap", "lap"),
    "-ig": ("big", "dig", "fig", "pig", "rig", "wig"),
    "-in": ("bin", "fin", "pin", "sin", "tin", "win"),
    "-ip": ("dip", "hip", "lip", "rip", "sip", "tip", "zip"),
    "-op": ("cop", "hop", "mop", "pop", "top", "stop"),
    "-ot": ("cot", "dot", "hot", "lot", "not", "pot", "rot"),
    "-ug": ("bug", "dug", "hug", "jug", "mug", "rug", "tug"),
    "-un": ("bun", "fun", "run", "sun"),
    "-ed": ("bed", "fed", "led", "red", "ted", "wed"),
    "-en": ("den", "hen", "men", "pen", "ten", "when"),
}

WORD_FAMILY: Dict[str, str] = {
    word: family for family, words in FAMILIES.items() for word in words
}

HIDES = ("onset", "rime")


class WordFamilyError(ValueError):
    """词族相关的输入错误。"""


def normalize_family(value: str) -> str:
    """把 at、-at、AT 统一成 -at。"""
    if not isinstance(value, str):
        raise WordFamilyError("词族必须是字符串")
    text = value.strip().lower()
    if not text:
        raise WordFamilyError("词族不能为空")
    if not text.startswith("-"):
        text = "-" + text
    if text not in FAMILIES:
        raise WordFamilyError("未知词族：%s" % value)
    return text


def check_hide(hide: str) -> str:
    """校验隐藏位置。"""
    if hide not in HIDES:
        raise WordFamilyError("隐藏位置只能是 onset 或 rime")
    return hide


def family_words(family: str) -> List[str]:
    """返回词族的全部单词。"""
    return list(FAMILIES[normalize_family(family)])


def word_family(word: str) -> str:
    """返回单词所属词族。"""
    if not isinstance(word, str):
        raise WordFamilyError("单词必须是字符串")
    text = word.strip().lower()
    if text not in WORD_FAMILY:
        raise WordFamilyError("未知单词：%s" % word)
    return WORD_FAMILY[text]


def split_word(word: str) -> Tuple[str, str]:
    """把单词拆成声母部分与词族韵脚。"""
    family = word_family(word)
    text = word.strip().lower()
    onset = text[: len(text) - (len(family) - 1)]
    return onset, family


def rhymes(first: str, second: str) -> bool:
    """判断两个单词是否押韵（同属一个词族）。"""
    return word_family(first) == word_family(second)


@dataclass(frozen=True)
class WordProblem:
    """一道词族补全题。"""

    word: str
    hide: str

    def __post_init__(self) -> None:
        check_hide(self.hide)
        onset, family = split_word(self.word)
        if not onset:
            raise WordFamilyError("%s 缺少词首部分" % self.word)
        if not family:
            raise WordFamilyError("%s 缺少词族" % self.word)

    @property
    def family(self) -> str:
        """所属词族。"""
        return word_family(self.word)

    @property
    def onset(self) -> str:
        """词首部分。"""
        return split_word(self.word)[0]

    @property
    def rime(self) -> str:
        """韵脚部分（不含连字符）。"""
        return self.family[1:]

    @property
    def prompt(self) -> str:
        """题干，隐藏部分用下划线表示。"""
        if self.hide == "onset":
            return "____" + self.rime
        return self.onset + "____"

    @property
    def answer(self) -> str:
        """题目答案。"""
        return self.onset if self.hide == "onset" else self.rime

    @property
    def full(self) -> str:
        """完整单词。"""
        return self.onset + self.rime

    @property
    def hint(self) -> str:
        """词族提示。"""
        return "词族 %s" % self.family


def generate_problems(
    count: int = 8,
    families: Optional[Sequence[str]] = None,
    hides: Sequence[str] = HIDES,
    seed: Optional[int] = None,
) -> List[WordProblem]:
    """随机生成不重复的词族补全题。"""
    if isinstance(count, bool) or not isinstance(count, int):
        raise WordFamilyError("题目数量必须是整数")
    if count < 1:
        raise WordFamilyError("题目数量至少为 1")
    chosen_families = (
        [normalize_family(family) for family in families]
        if families
        else list(FAMILIES)
    )
    chosen_hides = list(hides)
    if not chosen_hides:
        raise WordFamilyError("至少需要一种隐藏位置")
    for hide in chosen_hides:
        check_hide(hide)
    words = [
        (word, hide)
        for family in chosen_families
        for word in FAMILIES[family]
        for hide in chosen_hides
    ]
    if count > len(words):
        raise WordFamilyError("题目数量不能超过 %d" % len(words))
    rng = random.Random(seed)
    rng.shuffle(words)
    return [WordProblem(word, hide) for word, hide in words[:count]]


def check_answer(problem: WordProblem, answer: str) -> bool:
    """判断作答是否正确。"""
    if not isinstance(problem, WordProblem):
        raise WordFamilyError("题目必须是 WordProblem")
    if not isinstance(answer, str):
        raise WordFamilyError("答案必须是字符串")
    return problem.answer == answer.strip().lower()
