#!/usr/bin/env python3
"""Figures for the 2026-11-18 issue-worker report.

Public-safe data only (aggregated, checked 2026-11-18):
- Linear project f7f3a327-a06b-478f-bd88-c49fc2b79cef: 21 issues,
  per-status counts, and blockedBy edges between issues.
- GitHub private repo: number of open draft PRs, rounded added lines,
  age in days, and whether GitHub Actions reported checks.
Issue identifiers are kept because the reader needs them to act.
Titles, descriptions, comments, assignees, code, and history are not drawn.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"

INK = "#161616"
SUB = "#525252"
BG = "#ffffff"
PALE = "#edf5ff"
BLUE = "#0f62fe"
DARKBLUE = "#0043ce"
AMBER = "#8a3800"
LIGHTAMBER = "#fff2e8"
BORDERAMBER = "#d97706"
GRAY = "#6f6f6f"
LIGHTGRAY = "#f4f4f4"
BORDERGRAY = "#c6c6c6"
GREEN = "#198038"
W = 2000
H = 1125


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def box(draw, x, y, w, h, fill, border, width=2, radius=14):
    draw.rounded_rectangle((x, y, x + w, y + h), radius=radius, fill=fill, outline=border, width=width)


def canvas():
    image = Image.new("RGB", (W, H), BG)
    return image, ImageDraw.Draw(image)


def pipeline():
    image, draw = canvas()
    text(draw, (70, 74), "4つの関門と、今日の通過数", 58, INK, bold=True)
    text(draw, (70, 152), "入口で0件、出口で8件。同じ流れの両端が止まっている。", 32, SUB)

    cards = [
        ("01", "入力", "21件", "Linearの課題を取得", BLUE, PALE),
        ("02", "状態の門", "0件", "Todoだけが通れる", DARKBLUE, LIGHTGRAY),
        ("03", "実装とDraft PR", "8件", "追加 約1.3万行", BLUE, PALE),
        ("04", "レビューとmerge", "0件", "人が確認して初めて通る", AMBER, LIGHTAMBER),
    ]
    x0, y0, cw, ch, gap = 70, 270, 420, 470, 60
    for index, (number, label, count, note, color, fill) in enumerate(cards):
        x = x0 + index * (cw + gap)
        box(draw, x, y0, cw, ch, fill, color, 4)
        draw.ellipse((x + 34, y0 + 34, x + 106, y0 + 106), fill=color)
        text(draw, (x + 70, y0 + 70), number, 30, "#ffffff", bold=True, anchor="mm")
        text(draw, (x + 34, y0 + 148), label, 34, SUB, bold=True)
        text(draw, (x + 34, y0 + 214), count, 110, color, bold=True)
        text(draw, (x + 34, y0 + 356), note, 26, SUB)
        if index < len(cards) - 1:
            ax = x + cw + 12
            draw.line([(ax, y0 + ch // 2), (ax + gap - 24, y0 + ch // 2)], fill=GRAY, width=4)
            draw.polygon(
                [(ax + gap - 24, y0 + ch // 2), (ax + gap - 44, y0 + ch // 2 - 12), (ax + gap - 44, y0 + ch // 2 + 12)],
                fill=GRAY,
            )

    box(draw, 70, 800, 1860, 80, LIGHTAMBER, BORDERAMBER, 2)
    text(draw, (100, 826), "Todoが1件も無いので 01→02 で止まり、作った8件は 04 の前で待っている。", 30, AMBER, bold=True)
    text(draw, (70, 936), "件数は2026-11-18時点。Draft PRはGitHubのopenかつdraftの8件。", 26, SUB)
    image.save(ROOT / "pipeline.png")


def pr_queue():
    image, draw = canvas()
    text(draw, (70, 74), "Draft PR 8件：大きさと待ち日数", 58, INK, bold=True)
    text(draw, (70, 142), "古い3件は21日、新しい5件は13日。CIが緑なのは新しい4件だけ。", 30, SUB)

    rows = [
        (1, 1300, 21, False),
        (2, 2200, 21, False),
        (3, 6400, 21, False),
        (4, 500, 13, False),
        (5, 700, 13, True),
        (6, 200, 13, True),
        (7, 900, 13, True),
        (8, 600, 13, True),
    ]
    top, row_h, bar_h = 258, 88, 52
    left, bar_x, bar_max = 70, 240, 1040
    scale = bar_max / 6400
    for index, (number, lines, days, ci) in enumerate(rows):
        y = top + index * row_h
        if index % 2 == 0:
            draw.rectangle((left - 16, y - 8, 1930, y + row_h - 20), fill="#fafafa")
        text(draw, (left, y + bar_h // 2), f"PR #{number}", 32, INK, bold=True, anchor="lm")
        width = max(10, int(lines * scale))
        color = BLUE if ci else BORDERGRAY
        draw.rounded_rectangle((bar_x, y, bar_x + width, y + bar_h), radius=6, fill=color)
        text(draw, (bar_x + width + 16, y + bar_h // 2), f"約{lines / 1000:.1f}k行" if lines >= 1000 else f"約{lines}行", 28, INK, anchor="lm")
        text(draw, (1560, y + bar_h // 2), f"{days}日", 28, SUB, anchor="lm")
        badge = "CI 緑" if ci else "CI なし"
        badge_color = GREEN if ci else AMBER
        bw = 138
        box(draw, 1700, y + 8, bw, 38, "#ffffff", badge_color, 2, 8)
        text(draw, (1700 + bw // 2, y + 27), badge, 22, badge_color, bold=True, anchor="mm")

    draw.line([(bar_x, 214), (bar_x, 1004)], fill=BORDERGRAY, width=2)
    text(draw, (bar_x, 204), "追加行数（概算）", 24, SUB, anchor="ls")
    text(draw, (1560, 204), "経過", 24, SUB, anchor="ls")
    text(draw, (1700, 204), "GitHub Actions", 24, SUB, anchor="ls")
    text(draw, (70, 1046), "行数は追加行数の概算。8件すべて draft かつ mergeable=CLEAN。", 26, SUB)
    image.save(ROOT / "pr_queue.png")


def unlock():
    image, draw = canvas()
    text(draw, (70, 74), "TAA-44を終えたとき、何件が空くか", 58, INK, bold=True)
    text(draw, (70, 152), "直接ブロックされた4件のうち、すぐ候補になるのは2件。", 30, SUB)

    # source node
    box(draw, 70, 240, 470, 150, LIGHTAMBER, AMBER, 4)
    text(draw, (100, 272), "TAA-44", 40, AMBER, bold=True)
    text(draw, (100, 326), "In Review / Draft PRが21日待ち", 24, SUB)

    # arrow
    draw.line([(540, 315), (620, 315)], fill=GRAY, width=5)
    draw.polygon([(620, 315), (596, 302), (596, 328)], fill=GRAY)

    # left card: immediately free
    box(draw, 620, 240, 600, 430, PALE, BLUE, 4)
    text(draw, (650, 272), "すぐ候補になる", 32, DARKBLUE, bold=True)
    text(draw, (650, 322), "2件", 60, BLUE, bold=True)
    text(draw, (650, 400), "blockedByがTAA-44だけ", 24, SUB)
    for index, name in enumerate(["TAA-46", "TAA-48"]):
        cy = 470 + index * 84
        box(draw, 650, cy, 250, 62, "#ffffff", BLUE, 3, 10)
        text(draw, (775, cy + 31), name, 30, DARKBLUE, bold=True, anchor="mm")

    # right card: still blocked
    box(draw, 1270, 240, 660, 430, LIGHTAMBER, BORDERAMBER, 4)
    text(draw, (1300, 272), "別の依存が残る", 32, AMBER, bold=True)
    text(draw, (1300, 322), "4件", 60, BORDERAMBER, bold=True)
    text(draw, (1300, 400), "blockedBy に他の課題が残る", 24, SUB)
    rows = [
        ("TAA-45", "TAA-43 待ち"),
        ("TAA-49", "TAA-45 待ち"),
        ("TAA-47", "TAA-45 待ち"),
        ("TAA-50", "TAA-35 / 47 / 48 / 49 待ち"),
    ]
    for index, (name, why) in enumerate(rows):
        ry = 448 + index * 52
        text(draw, (1300, ry), name, 28, INK, bold=True)
        text(draw, (1450, ry), f"← {why}", 24, SUB)

    box(draw, 70, 700, 1860, 148, LIGHTGRAY, BORDERGRAY, 2)
    text(draw, (100, 740), "「1件レビューすれば6件動く」は言い過ぎ。", 32, INK, bold=True)
    text(draw, (100, 794), "正しくは「1件の完了で2件が動き、残り4件は連鎖で解ける」。", 28, SUB)
    text(draw, (70, 900), "依存はLinearのblockedBy（2026-11-18時点）をそのまま数えた。", 26, SUB)
    image.save(ROOT / "unlock.png")


if __name__ == "__main__":
    pipeline()
    pr_queue()
    unlock()
    print("wrote pipeline.png, pr_queue.png, unlock.png")
