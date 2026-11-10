#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data sources (public-safe aggregates only, measured 2026-11-11):
- open draft PR numbers, diff sizes, changed-file counts (GitHub API)
- per-PR changed file sets relative to main, and shared-file counts between PRs (git diff)
- base branch of each PR and commit ancestry (git merge-base --is-ancestor)

No issue bodies, comments, code content, branch contents or customer data are used.
Only counts, PR numbers and branch relationships appear in the images.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"

INK = "#161616"
SUB = "#525252"
BG = "#ffffff"
PANEL = "#f4f4f4"
BLUE = "#0f62fe"
DARKBLUE = "#0043ce"
LIGHTBLUE = "#d0e2ff"
MIDBLUE = "#78a9ff"
TEAL = "#007d79"
GRAY = "#8d8d8d"
RED = "#da1e28"

# number -> (additions, deletions, changed_files_vs_base, changed_files_vs_main)
PR = {
    1: (1317, 0, 13, 13),
    2: (2237, 1, 12, 12),
    3: (6359, 0, 27, 27),
    4: (521, 239, 19, 19),
    5: (718, 0, 10, 10),
    6: (155, 0, 6, 6),
    7: (939, 0, 11, 17),
    8: (615, 6, 10, 23),
}

# shared-file counts between two PRs (0 when they touch different files)
OVERLAP = {
    (1, 2): 2, (1, 4): 4, (2, 4): 1,
    (6, 7): 6, (6, 8): 6, (7, 8): 17,
}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def overlap_matrix(path: Path) -> None:
    W, H = 1400, 1180
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (70, 44), "PRどうしが同じファイルを触っている数", 46, INK, bold=True)
    text(d, (70, 106), "2026-11-11時点の草案8件。mainからの変更ファイルを比べた重複数。斜線のマスは各PR自身の変更数。", 21, SUB)

    prs = [1, 2, 3, 4, 5, 6, 7, 8]
    x0, y0, cell = 300, 210, 102

    def shade(n: int) -> str:
        if n == 0:
            return PANEL
        if n <= 3:
            return LIGHTBLUE
        if n <= 6:
            return MIDBLUE
        if n <= 16:
            return BLUE
        return DARKBLUE

    def text_color(n: int) -> str:
        return "#ffffff" if n >= 7 else INK

    for i, a in enumerate(prs):
        text(d, (x0 - 24, y0 + i * cell + cell / 2), f"#{a}", 28, INK, bold=True, anchor="rm")
        text(d, (x0 + i * cell + cell / 2, y0 - 26), f"#{a}", 28, INK, bold=True, anchor="mb")

    for i, a in enumerate(prs):
        for j, b in enumerate(prs):
            x, y = x0 + j * cell, y0 + i * cell
            if a == b:
                d.rectangle((x, y, x + cell - 4, y + cell - 4), fill="#e8e8e8")
                d.line((x, y, x + cell - 4, y + cell - 4), fill="#bdbdbd", width=2)
                text(d, (x + (cell - 4) / 2, y + (cell - 4) / 2), str(PR[a][3]), 30, SUB, bold=True, anchor="mm")
                continue
            n = OVERLAP.get((min(a, b), max(a, b)), 0)
            d.rectangle((x, y, x + cell - 4, y + cell - 4), fill=shade(n))
            if n:
                text(d, (x + (cell - 4) / 2, y + (cell - 4) / 2), str(n), 32, text_color(n), bold=True, anchor="mm")

    def box(a, b, color):
        i, j = prs.index(a), prs.index(b)
        x1, y1 = x0 + j * cell, y0 + i * cell
        x2, y2 = x1 + cell - 4, y1 + cell - 4
        d.rectangle((x1 - 3, y1 - 3, x2 + 3, y2 + 3), outline=color, width=5)

    box(6, 7, RED)
    box(7, 8, RED)
    box(6, 8, RED)
    box(1, 4, TEAL)

    text(d, (70, 1072), "共有ファイル数", 24, INK, bold=True)
    steps = [(0, "0"), (2, "1-3"), (5, "4-6"), (10, "7-16"), (20, "17以上")]
    for k, (n, label) in enumerate(steps):
        x = 300 + k * 168
        d.rectangle((x, 1066, x + 40, 1108), fill=shade(n))
        text(d, (x + 52, 1074), label, 22, SUB)
    x = 300 + 5 * 168
    d.rectangle((x, 1066, x + 40, 1108), fill="#e8e8e8")
    text(d, (x + 52, 1074), "自身の変更数", 22, SUB)

    text(d, (70, 1136), "赤枠の3件は同じ枝の積み木。緑枠の#1と#4は文書で4件重なる。0は『重ならない』の意味で、互換性の保証ではない。", 21, SUB)

    img.save(path)


def stack_map(path: Path) -> None:
    W, H = 1400, 860
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (70, 44), "8件の積み方：3段の塔と、単独2件", 46, INK, bold=True)
    text(d, (70, 106), "各PRのbaseブランチと、ブランチの含み関係から作成。矢印は『上のPRが下の変更をすべて含む』ことを示す。", 21, SUB)

    tx, tw = 70, 620
    cards = [
        (8, 170, "自身の差分 +615行 / 6行削除・10ファイル", "mainとの差 23ファイル・base=#7", TEAL),
        (7, 310, "自身の差分 +939行 / 11ファイル", "mainとの差 17ファイル・base=#6", MIDBLUE),
        (6, 450, "自身の差分 +155行 / 6ファイル", "mainとの差 6ファイル・base=main", BLUE),
    ]
    for pr, y, line1, line2, color in cards:
        d.rounded_rectangle((tx, y, tx + tw, y + 96), radius=12, fill=PANEL)
        d.rounded_rectangle((tx, y, tx + 9, y + 96), radius=5, fill=color)
        text(d, (tx + 28, y + 8), f"PR #{pr}", 30, INK, bold=True)
        text(d, (tx + 28, y + 46), line1, 21, SUB)
        text(d, (tx + 28, y + 72), line2, 20, GRAY)

    d.rounded_rectangle((tx, 610, tx + tw, 680), radius=10, fill="#161616")
    text(d, (tx + 24, 645), "main（本流）", 26, "#ffffff", bold=True, anchor="lm")
    text(d, (tx + 220, 628), "最終更新 2026-10-28", 20, "#c6c6c6")
    text(d, (tx + 220, 656), "以降14日間 追加コミット 0件", 20, "#f4c7c3", bold=True)

    for start_y, end_y in ((450, 410), (310, 270), (610, 550)):
        d.line((tx + 50, start_y, tx + 50, end_y), fill=GRAY, width=4)
        d.polygon([(tx + 50, end_y - 2), (tx + 41, end_y + 15), (tx + 59, end_y + 15)], fill=GRAY)

    rx, rw = 730, 600
    text(d, (rx, 172), "塔の意味", 28, INK, bold=True)
    text(d, (rx, 214), "#8は#6と#7の変更をすべて含む。", 22, SUB)
    text(d, (rx, 252), "いきなり#8をmergeすると3件分が", 22, RED, bold=True)
    text(d, (rx, 280), "同時に本流へ入る。", 22, RED, bold=True)

    d.rounded_rectangle((rx, 330, rx + rw, 520), radius=14, fill="#e8f4f4")
    text(d, (rx + 28, 348), "単独で判断できる2件（共有0）", 24, TEAL, bold=True)
    text(d, (rx + 28, 396), "PR #3", 28, INK, bold=True)
    text(d, (rx + 150, 402), "6,359行 / 27ファイル", 21, SUB)
    text(d, (rx + 28, 442), "PR #5", 28, INK, bold=True)
    text(d, (rx + 150, 448), "718行 / 10ファイル", 21, SUB)
    text(d, (rx + 28, 486), "他の7件と同じファイルを触っていない。", 21, SUB)

    d.rounded_rectangle((rx, 550, rx + rw, 730), radius=14, fill=PANEL)
    text(d, (rx + 28, 568), "文書だけで重なる3件", 24, INK, bold=True)
    text(d, (rx + 28, 612), "PR #1・#2・#4", 26, INK, bold=True)
    text(d, (rx + 28, 656), "共有は最大4ファイル（文書と設定）", 21, SUB)
    text(d, (rx + 28, 688), "順番を決めれば衝突は小さい", 21, BLUE, bold=True)

    img.save(path)


if __name__ == "__main__":
    overlap_matrix(ROOT / "overlap_matrix.png")
    stack_map(ROOT / "stack_map.png")
