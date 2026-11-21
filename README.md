# wordfamily

[![CI](https://github.com/eastyou/wordfamily/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/wordfamily/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)

把 -at、-an、-ig 这类词族整理成可打印卡片，再生成“补词首 / 补词尾”的练习纸，帮助初学者建立拼读规律。

## 安装

```bash
pip install -e .
```

只需要 Python 3.9+，零第三方依赖。

## 用法

```bash
# 列出全部词族
wordfamily families

# 查看某个词族的单词
wordfamily words -at
# -at：cat, bat, hat, mat, rat, sat, fat, pat

# 判断两个单词是否押韵
wordfamily rhyme cat hat
# cat 与 hat 押韵
# 词族：-at / -at

# 打印词族卡片
wordfamily cards -o cards.html

# 生成 10 道补全练习，附答案
wordfamily sheet --count 10 --seed 1 --answers -o sheet.html

# 只练 -at、-an 两个词族，只补词尾
wordfamily sheet --count 8 --families -at,-an --hides rime -o rime.html
```

## 功能

- 12 个常见词族、76 个单词
- 词族写法兼容 `at`、`-at`、`AT`
- 两种题型：补词首（`____at`）、补词尾（`c____`）
- 押韵判断与词族查询
- 支持按词族、按题型筛选
- 题目去重，随机种子可复现
- A4 打印排版，答案单独一页

## 测试

```bash
python -m unittest discover -s tests -v
```

## 许可

[MIT](LICENSE) © 2026 eastyou
