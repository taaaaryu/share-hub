#!/usr/bin/env python3
"""Figures for the 2026-11-20 "review first" deck.

Public-safe data only (read 2026-11-20 JST):
- share-hub slides created 2026-11-17..11-20: 3 / 4 / 5 / 4 = 16 decks.
- Pull requests on the private repo, all still open drafts: 8.
  merged pull requests ever: 0.
- Per PR changed files and added/removed lines, plus number of CI checks.

Only counts, PR numbers and aggregate sizes are drawn.
No issue titles, bodies, comments, code, branch names or customer data.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"

INK = "#161616"
SUB = "#525252"
BG = "#ffffff"
BLUE = "#0f62fe"
LIGHTBLUE = "#edf5ff"
AMBER = "#8a3800"
LIGHTAMBER = "#fff2e8"
GRAY = "#6f6f6f"
LIGHTGRAY = "#f4f4f4"
BORDERGRAY = "#b8b8b8"
GREEN = "#0e6027"
LIGHTGREEN = "#defbe6"

W, H = 2000, 1125

DECKS_BY_DAY = [("11/17", 3), ("11/18", 4), ("11/19", 5), ("11/20", 4)]
PRS = [
    (1, 13, 1317, 0, True),
    (2, 12, 2237, 0, False),
    (3, 27, 6359, 0, False),
    (4, 19, 521, 0, False),
    (5, 10, 718, 1, False),
    (6, 6, 155, 1, False),
    (7, 11, 939, 1, False),
    (8, 10, 615, 2, False),
]


def font(size, bold=False):
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def canvas(title, kicker):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 12), fill=BLUE)
    text(d, (90, 78), kicker, 30, BLUE, bold=True)
    text(d, (90, 126), title, 60, INK, bold=True)
    return img, d


def fig_decks_vs_merge():
    img, d = canvas("資料は増えている。mergeは増えていない。", "4日間の記録")
    base_y = 800
    left, right = 190, 1240
    max_h = 420
    for i, (label, n) in enumerate(DECKS_BY_DAY):
        x = left + i * 250
        h = int(max_h * n / 5)
        d.rectangle((x, base_y - h, x + 150, base_y), fill=LIGHTBLUE, outline=BLUE, width=3)
        text(d, (x + 75, base_y - h - 46), f"{n}", 40, BLUE, bold=True, anchor="ma")
        text(d, (x + 75, base_y + 18), label, 26, SUB, anchor="ma")
    d.line((left, base_y, left + 940, base_y), fill=INK, width=3)
    text(d, (left, base_y + 78), "share-hub に追加した資料（本）", 26, SUB)
    text(d, (left + 470, 900), "合計 16 本", 30, INK, bold=True)

    d.rectangle((right, 300, right + 570, 800), fill=LIGHTGRAY, outline=BORDERGRAY, width=3)
    text(d, (right + 285, 380), "merge された PR", 30, SUB, anchor="ma")
    text(d, (right + 285, 500), "0", 150, AMBER, bold=True, anchor="ma")
    text(d, (right + 285, 640), "本（これまで全期間）", 30, AMBER, anchor="ma")
    text(d, (right + 285, 690), "open の Draft PR は 8 本のまま", 26, SUB, anchor="ma")

    d.rectangle((90, 960, W - 90, 1040), fill=LIGHTAMBER)
    text(d, (120, 982), "資料を1本増やしても、レビューは1本も進まない。", 30, AMBER, bold=True)
    img.save(ROOT / "decks_vs_merge.png")


def fig_pr_queue():
    img, d = canvas("レビュー待ち8本は、重さが5倍ちがう", "PR キュー（すべて Draft・競合なし）")
    top = 250
    row_h = 88
    bar_left = 470
    max_files = 27
    scale = 620 / max_files
    for i, (num, files, adds, checks, hot) in enumerate(PRS):
        y = top + i * row_h
        accent = BLUE if hot else GRAY
        fill = LIGHTBLUE if hot else LIGHTGRAY
        text(d, (100, y + 16), f"PR #{num}", 34, accent, bold=True)
        w = int(files * scale)
        d.rectangle((bar_left, y + 8, bar_left + w, y + 62), fill=fill, outline=accent, width=3)
        if w > 210:
            text(d, (bar_left + 18, y + 24), f"{files} ファイル", 28, INK, bold=True)
        else:
            text(d, (bar_left + w + 18, y + 24), f"{files} ファイル", 28, INK, bold=True)
        text(d, (bar_left + 660, y + 12), f"+{adds:,} 行", 26, SUB)
        check_color = GREEN if checks else AMBER
        text(d, (bar_left + 660, y + 46), f"CI チェック {checks} 件", 24, check_color)
        if hot:
            d.rectangle((bar_left + 880, y + 14, bar_left + 1200, y + 58), fill=BLUE)
            text(d, (bar_left + 1040, y + 36), "後続4件を解禁", 24, "#ffffff", bold=True, anchor="mm")
    d.line((90, 990, W - 90, 990), fill=BORDERGRAY, width=2)
    text(d, (100, 1004), "PR #1 を merge すると、直接の後続4件（連鎖で6件）が動き出す。PR #3 は27ファイルで最も重い。", 26, SUB)
    img.save(ROOT / "pr_queue.png")


if __name__ == "__main__":
    fig_decks_vs_merge()
    fig_pr_queue()
    print("ok")
