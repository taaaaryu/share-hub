#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data source (public-safe aggregates only, measured 2026-11-12 01:30 JST):
- Linear project issue list: status counts (21 issues).
- `git ls-remote --heads thumaster`: 5 issue branches reachable.
- `gh pr list --state all`: 0 pull requests for those branch heads.

No issue titles, bodies, comments, branch names, code or customer data
appear in the images. Only counts, status names and dates are drawn.
"""
from datetime import date
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
LIGHTBLUE = "#d0e2ff"
TEAL = "#007d79"
LIGHTTEAL = "#d9fbfb"
GRAY = "#8d8d8d"
LIGHTGRAY = "#e0e0e0"
RED = "#da1e28"
LIGHTRED = "#fff1f1"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def box(draw, x, y, w, h, fill, border, width=2):
    draw.rectangle((x, y, x + w, y + h), fill=fill, outline=border, width=width)


def funnel(path: Path) -> None:
    W, H = 1400, 860
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (70, 46), "着手済み5件 → ブランチ5本 → PR 0本", 46, INK, bold=True)
    text(d, (70, 112), "2026-11-12 01:30 JST。Linearの状態、リモートのブランチ、PRをそれぞれ別に数えた。", 21, SUB)

    stages = [
        ("Linear: 着手済み", "In Progress 4 + In Review 1", 5, DARKBLUE, PALE),
        ("リモート: ブランチ", "push済みで取得できた本数", 5, TEAL, LIGHTTEAL),
        ("GitHub: PR", "open / closed / merged の全件検索", 0, RED, LIGHTRED),
    ]

    top = 210
    row_h = 150
    for i, (label, note, value, color, fill) in enumerate(stages):
        y = top + i * (row_h + 30)
        text(d, (80, y + 18), label, 27, INK, bold=True)
        text(d, (80, y + 62), note, 20, SUB)
        box(d, 560, y, 760, row_h, fill, color, 3)
        text(d, (940, y + row_h / 2 - 8), f"{value}", 64, color, bold=True, anchor="ma")
        text(d, (1110, y + row_h / 2 + 4), "件", 26, color, bold=True, anchor="la")

    # connector arrows
    for i in range(2):
        y = top + i * (row_h + 30) + row_h
        d.line((940, y + 8, 940, y + 30), fill=GRAY, width=4)
        d.polygon([(932, y + 24), (948, y + 24), (940, y + 34)], fill=GRAY)

    text(d, (80, 772), "PRが0本なので、レビュー待ちの列にも、取り込み済みの列にも、この5件は入っていない。", 22, SUB)

    img.save(path)


def timeline(path: Path) -> None:
    W, H = 1400, 700
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (70, 46), "最後のコミットは10月28日と11月5日", 46, INK, bold=True)
    text(d, (70, 112), "5本のブランチの最終コミット日を、今日（11月12日）と並べた。", 21, SUB)

    left, right = 140, 1270
    axis_y = 400
    start = date(2026, 10, 26)
    end = date(2026, 11, 14)
    span = (end - start).days

    def x_of(day: date) -> float:
        return left + (right - left) * ((day - start).days / span)

    # axis
    d.line((left, axis_y, right, axis_y), fill=LIGHTGRAY, width=3)
    for day, label in [(date(2026, 10, 28), "10/28"), (date(2026, 11, 5), "11/5"),
                       (date(2026, 11, 12), "11/12")]:
        x = x_of(day)
        text(d, (x, axis_y + 26), label, 22, SUB, anchor="ma")

    # commit groups
    groups = [
        (date(2026, 10, 28), 1, "In Review 1件", RED, 60),
        (date(2026, 11, 5), 4, "In Progress 4件", DARKBLUE, -60),
    ]
    for day, count, label, color, dy in groups:
        x = x_of(day)
        for i in range(count):
            cx = x + (i - (count - 1) / 2) * 34
            d.ellipse((cx - 15, axis_y - 15, cx + 15, axis_y + 15), fill=color)
        text(d, (x, axis_y + dy), f"{count}本", 30, color, bold=True, anchor="ma")
        text(d, (x, axis_y + dy + (36 if dy > 0 else -36)), label, 20, SUB, anchor="ma")

    # today marker
    tx = x_of(date(2026, 11, 12))
    d.line((tx, 180, tx, 560), fill=BLUE, width=2)
    text(d, (tx + 14, 200), "今日 11/12", 22, BLUE, bold=True)

    # age spans
    d.line((x_of(date(2026, 10, 28)), 590, tx, 590), fill=RED, width=2)
    text(d, ((x_of(date(2026, 10, 28)) + tx) / 2, 600), "14日そのまま", 22, RED, bold=True, anchor="ma")
    d.line((x_of(date(2026, 11, 5)), 630, tx, 630), fill=DARKBLUE, width=2)
    text(d, ((x_of(date(2026, 11, 5)) + tx) / 2, 640), "6日そのまま", 22, DARKBLUE, bold=True, anchor="ma")

    text(d, (70, 190), "● ブランチの最終コミット（5本・PRは0本）", 23, INK, bold=True)

    img.save(path)


if __name__ == "__main__":
    funnel(ROOT / "funnel.png")
    timeline(ROOT / "timeline.png")
    print("figures written")
