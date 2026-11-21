"""词族卡片与练习纸渲染。"""

from __future__ import annotations

import html
from typing import Dict, List, Optional, Sequence

from .model import FAMILIES, WordFamilyError, WordProblem, normalize_family

_COLORS = ("#ebf8ff", "#f0fff4", "#fffaf0", "#faf5ff", "#fff5f5", "#e6fffa")


def _css_for(index: int) -> str:
    return _COLORS[index % len(_COLORS)]


_CSS = """
@page { size: A4; margin: 12mm; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
       color: #1f2933; background: #fff; }
.sheet { padding: 4mm; }
h1 { margin: 0 0 2mm; font-size: 22px; text-align: center; letter-spacing: 2px; }
.meta { margin: 0 0 4mm; text-align: center; color: #616e7c; font-size: 12px; }
.families { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; }
.family { border: 1px solid #cbd2d9; border-radius: 3mm; padding: 3mm; page-break-inside: avoid; }
.family h2 { margin: 0 0 2mm; font-size: 20px; color: #2c5282; }
.chips { display: flex; flex-wrap: wrap; gap: 2mm; }
.chip { border: 1px solid #e2e8f0; border-radius: 2mm; padding: 1mm 2.5mm;
        font-family: "SFMono-Regular", Consolas, monospace; font-size: 16px; }
.cards { display: grid; grid-template-columns: 1fr 1fr; gap: 4mm; margin-top: 4mm; }
.card { border: 1px solid #cbd2d9; border-radius: 3mm; padding: 4mm; page-break-inside: avoid; }
.prompt { font-family: "SFMono-Regular", Consolas, monospace; font-size: 24px;
          letter-spacing: 3px; margin: 0 0 2mm; }
.hint { font-size: 12px; color: #9aa5b1; margin: 0; }
.answer-line { border-bottom: 1px dashed #9aa5b1; height: 26px; margin-top: 3mm; }
.answers { page-break-before: always; margin-top: 6mm; }
.answers h2 { font-size: 18px; border-left: 4px solid #2f855a; padding-left: 3mm; color: #276749; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { border: 1px solid #cbd2d9; padding: 2mm 3mm; text-align: left; }
th { background: #f5f7fa; }
@media print { .sheet { padding: 0; } }
""".strip()


def render_family_cards(
    families: Optional[Sequence[str]] = None,
    title: str = "英语词族卡片",
) -> str:
    """生成可打印的词族卡片页。"""
    names = (
        list(FAMILIES)
        if families is None
        else [normalize_family(name) for name in families]
    )
    if not names:
        raise WordFamilyError("至少需要一个词族")
    sections: List[str] = []
    for index, family in enumerate(names):
        chips = "".join(
            '<span class="chip">%s</span>' % html.escape(word) for word in FAMILIES[family]
        )
        sections.append(
            '<section class="family" style="background:%s"><h2>%s</h2>'
            '<div class="chips">%s</div></section>'
            % (_css_for(index), html.escape(family), chips)
        )
    return "\n".join(
        [
            "<!DOCTYPE html>",
            '<html lang="zh-CN"><head><meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            "<title>%s</title>" % html.escape(title),
            "<style>%s</style></head><body>" % _CSS,
            '<main class="sheet">',
            "<h1>%s</h1>" % html.escape(title),
            '<p class="meta">读一读，找出每组长得一样的结尾。</p>',
            '<section class="families">%s</section>' % "\n".join(sections),
            "</main></body></html>",
        ]
    )


def render_worksheet(
    problems: Sequence[WordProblem],
    title: str = "词族补全练习",
    answers: bool = False,
) -> str:
    """生成可打印的词族补全练习纸。"""
    items = list(problems)
    if not items:
        raise WordFamilyError("至少需要一道题")
    for item in items:
        if not isinstance(item, WordProblem):
            raise WordFamilyError("题目必须是 WordProblem")

    families: List[str] = []
    for item in items:
        if item.family not in families:
            families.append(item.family)

    cards = [
        '<div class="card"><p class="prompt">%d. %s</p><p class="hint">%s</p>'
        '<div class="answer-line"></div></div>'
        % (index, html.escape(item.prompt), html.escape(item.hint))
        for index, item in enumerate(items, 1)
    ]

    sections = [
        "<!DOCTYPE html>",
        '<html lang="zh-CN"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>%s</title>" % html.escape(title),
        "<style>%s</style></head><body>" % _CSS,
        '<main class="sheet">',
        "<h1>%s</h1>" % html.escape(title),
        '<p class="meta">姓名：__________　班级：__________　日期：__________</p>',
        '<p class="meta">本页词族：%s</p>' % html.escape("　".join(families)),
        '<section class="cards">',
        "\n".join(cards),
        "</section>",
    ]

    if answers:
        rows = [
            "<tr><td>%d</td><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (
                index,
                html.escape(item.prompt),
                html.escape(item.answer),
                html.escape(item.full),
            )
            for index, item in enumerate(items, 1)
        ]
        sections.append(
            '<section class="answers"><h2>参考答案</h2>'
            "<table><thead><tr><th>题号</th><th>题目</th><th>答案</th><th>单词</th></tr></thead>"
            "<tbody>%s</tbody></table></section>" % "\n".join(rows)
        )

    sections.append("</main></body></html>")
    return "\n".join(sections)


def render_family_map() -> Dict[str, List[str]]:
    """返回词族到单词列表的副本。"""
    return {family: list(words) for family, words in FAMILIES.items()}
