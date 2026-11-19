#!/usr/bin/env python3
"""Generate the timeline figure used by this deck.

Public-safe data only (checked 2026-11-20 JST):
- Linear project f7f3a327 (TAA): 21 issues. Backlog 17, In Progress 4,
  In Review 1, Todo 0.
- private remote taaaaryu/thumaster: 8 open PRs, all draft, 0 reviews.

Only PR numbers, dates, day counts and status names are drawn.
No issue titles, bodies, comments, code or customer data.
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
BORDERGRAY = "#c6c6c6"
GREEN = "#0e6027"
LIGHTGREEN = "#defbe6"

W, H = 2000, 1125


def font(size, bold=False):
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


# PR number, created date label, days open on 2026-11-20
PRS = [
    ("PR #1", "10/28", 23),
    ("PR #2", "10/28", 23),
    ("PR #3", "10/28", 23),
    ("PR #4", "11/05", 15),
    ("PR #5", "11/05", 15),
    ("PR #6", "11/05", 15),
    ("PR #7", "11/05", 15),
    ("PR #8", "11/05", 15),
]
MAX_DAYS = 24


def main() -> None:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Header
    text(d, (80, 64), "Draft PRの経過日数（2026-11-20 時点）", 52, INK, bold=True)
    text(d, (80, 138), "8本すべてが Draft のまま。レビューは 0 件。merge も 0 件。", 32, SUB)

    # Chart frame
    left, top = 300, 250
    bar_h, gap = 56, 26
    plot_w = 1180
    d.line((left, top - 18, left + plot_w, top - 18), fill=BORDERGRAY, width=2)

    for i, (label, created, days) in enumerate(PRS):
        y = top + i * (bar_h + gap)
        oldest = days >= 23
        bar_w = int(plot_w * days / MAX_DAYS)
        fill = AMBER if oldest else BLUE
        d.rectangle((left, y, left + bar_w, y + bar_h), fill=fill)
        text(d, (left - 28, y + bar_h / 2), label, 32, INK, bold=True, anchor="rm")
        text(d, (left + bar_w + 18, y + bar_h / 2), f"{days}日", 32,
             AMBER if oldest else INK, bold=oldest, anchor="lm")
        text(d, (left + 18, y + bar_h / 2), f"作成 {created}", 26, "#ffffff", anchor="lm")

    # Axis
    axis_y = top + len(PRS) * (bar_h + gap) - gap + 26
    d.line((left, axis_y, left + plot_w, axis_y), fill=BORDERGRAY, width=2)
    for tick in (0, 8, 16, 24):
        x = left + int(plot_w * tick / MAX_DAYS)
        d.line((x, axis_y, x, axis_y + 12), fill=BORDERGRAY, width=2)
        text(d, (x, axis_y + 26), f"{tick}日", 26, GRAY, anchor="ma")

    # Side cards
    cx, cw = 1560, 360
    cards = [
        ("Todo の課題", "0 件", "workerが着手できる入口", LIGHTAMBER, AMBER),
        ("Draft PR", "8 本", "すべて未レビューで open", LIGHTGRAY, INK),
        ("In Review", "1 件", "TAA-44 / PR #1", LIGHTBLUE, BLUE),
        ("merge 済み", "0 本", "この23日間", LIGHTGREEN, GREEN),
    ]
    for i, (name, value, note, bg, accent) in enumerate(cards):
        y = 250 + i * 178
        d.rectangle((cx, y, cx + cw, y + 148), fill=bg)
        d.rectangle((cx, y, cx + 10, y + 148), fill=accent)
        text(d, (cx + 34, y + 24), name, 26, SUB)
        text(d, (cx + 34, y + 58), value, 54, accent, bold=True)
        text(d, (cx + 34, y + 118), note, 22, SUB)

    # Footer
    text(d, (80, H - 74), "出典: Linear project f7f3a327（読み取り）と private remote のPR一覧。"
                          "課題本文・コード・顧客情報は描画していない。", 24, GRAY)

    img.save(ROOT / "timeline.png")
    print("wrote", ROOT / "timeline.png")


if __name__ == "__main__":
    main()
