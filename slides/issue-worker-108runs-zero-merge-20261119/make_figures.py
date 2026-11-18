#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data source (public-safe aggregates, checked 2026-11-19 JST):
- Run logs: state/logs/once-* -> 108 files, 2026-10-29 .. 2026-11-18.
- Published reports: share-hub catalog entries whose slug starts with
  "issue-worker" -> 54 before this deck.
- private remote taaaaryu/thumaster: main = single commit 0d852ae
  (2026-10-28), 8 open draft PRs, 0 closed PRs ever, 0 review comments.
- Linear project f7f3a327: Todo 0, Backlog 16, In Progress 4, In Review 1.

Only counts, identifiers and status names are drawn. Issue titles, bodies,
comments and customer data are not used.
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
TEAL = "#007d79"
LIGHTTEAL = "#d9fbfb"
AMBER = "#8a3800"
LIGHTAMBER = "#fff2e8"
RED = "#a2191f"
LIGHTRED = "#fff1f1"
GRAY = "#6f6f6f"
LIGHTGRAY = "#f4f4f4"
BORDERGRAY = "#c6c6c6"

W, H = 2000, 1125


def font(size, bold=False):
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def figure():
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)


def funnel():
    img, d = figure()
    text(d, (80, 54), "108回の起動でも、mergeは0本", 44, INK, True)
    text(d, (80, 116), "左から右へ、件数に比例した長さで並べた（2026-11-19 時点）", 24, SUB)

    rows = [
        ("起動（10/29-11/18）", 108, BLUE, LIGHTBLUE, "1日4〜6回、合計108回"),
        ("報告スライド", 54, TEAL, LIGHTTEAL, "すべて「実装せず」または「一部のみ」"),
        ("Draft PR", 8, AMBER, LIGHTAMBER, "追加12,861行・レビュー0件"),
        ("merge（mainへ合流）", 0, RED, LIGHTRED, "closed PRも0本"),
    ]

    bar_x = 700
    bar_max = 880
    scale = bar_max / 108.0
    y = 255
    row_h = 178
    for label, value, color, light, note in rows:
        box_y = y - 80
        d.rounded_rectangle((80, box_y, W - 80, box_y + 150),
                            radius=12, fill=light, outline="#e0e0e0", width=2)
        text(d, (116, y - 44), label, 30, INK, True)
        text(d, (116, y + 16), note, 22, SUB)
        width = int(value * scale) if value else 8
        d.rounded_rectangle((bar_x, y - 23, bar_x + width, y + 23), radius=6, fill=color)
        text(d, (bar_x + width + 30, y), str(value), 36, color, True, "lm")
        y += row_h

    text(d, (80, 978), "件数は Linear の状態・GitHub の PR メタデータ・ローカルの起動ログから集計。", 24, SUB)
    text(d, (80, 1018), "課題本文・コメント・顧客情報は使っていない。", 24, SUB)
    img.save(ROOT / "funnel.png")


RUNS = {
    (10, 29): 4, (10, 30): 6, (10, 31): 5,
    (11, 1): 5, (11, 2): 5, (11, 3): 5, (11, 4): 5, (11, 5): 5,
    (11, 6): 5, (11, 7): 5, (11, 8): 5, (11, 9): 5, (11, 10): 5,
    (11, 11): 6, (11, 12): 5, (11, 13): 5, (11, 14): 5, (11, 15): 5,
    (11, 16): 6, (11, 17): 5, (11, 18): 5, (11, 19): 1,
}  # once-*.log timestamps converted to JST dates, total 108


def day_index(month, day):
    """Oct 28 2026 = 0."""
    if month == 10:
        return day - 28
    return 3 + day  # Oct 28..31 -> 0..3, Nov 1 -> 4


def mainline():
    img, d = figure()
    text(d, (80, 50), "mainは10月28日の1コミットから動いていない", 44, INK, True)
    text(d, (80, 112), "PRは8本作られたが、mainへ合流した点は1つも無い", 24, SUB)

    left, right = 210, 1860
    total_days = day_index(11, 19)
    step = (right - left) / total_days

    def x(month, day):
        return left + day_index(month, day) * step

    # lane labels
    for label, y in (("PR", 210), ("main", 470), ("起動", 700)):
        text(d, (80, y), label, 26, SUB, True)

    # PR lane
    pr_marks = [((10, 28), 3, "3本"), ((11, 5), 5, "5本")]
    lane_y = 250
    d.line((left, lane_y, right, lane_y), fill="#e0e0e0", width=3)
    for (month, day), count, label in pr_marks:
        px = x(month, day)
        for i in range(count):
            offset = (i - (count - 1) / 2) * 34
            d.ellipse((px + offset - 11, lane_y - 11, px + offset + 11, lane_y + 11),
                      fill=AMBER, outline=BG, width=2)
        text(d, (px, lane_y - 74), f"{month}/{day}・{label}", 26, AMBER, True, "ma")

    # main lane
    main_y = 470
    d.line((left, main_y, right, main_y), fill=BLUE, width=6)
    d.ellipse((x(10, 28) - 16, main_y - 16, x(10, 28) + 16, main_y + 16), fill=BLUE)
    text(d, (x(10, 28), main_y - 46), "コミット1件（0d852ae）", 26, BLUE, True, "la")
    text(d, (right, main_y + 34), "22日間、変化なし", 26, BLUE, True, "ra")
    text(d, (right, main_y - 40), "merge 0件", 30, RED, True, "ra")

    # run lane
    base_y = 950
    max_runs = 6
    bar_h = 210
    text(d, (left, 666), "日ごとの起動回数（1日の上限は6回。日付はJST）", 22, SUB)
    days = ([(10, d) for d in range(29, 32)] +
            [(11, d) for d in range(1, 20)])
    for month, day in days:
        count = RUNS[(month, day)]
        px = x(month, day)
        h = int(bar_h * count / max_runs)
        color = RED if count == 0 else TEAL
        if count == 0:
            d.line((px, base_y, px, base_y - 6), fill=RED, width=5)
            text(d, (px, base_y - 16), "0", 20, RED, True, "md")
            continue
        d.rectangle((px - 26, base_y - h, px + 26, base_y), fill=color)
        if count >= 10:
            text(d, (px, base_y - h - 12), str(count), 22, color, True, "md")

    d.line((left - 30, base_y, right, base_y), fill=BORDERGRAY, width=3)

    # x labels
    for month, day in [(10, 28), (11, 1), (11, 5), (11, 9), (11, 13), (11, 17), (11, 19)]:
        px = x(month, day)
        text(d, (px, base_y + 54), f"{month}/{day}", 24, SUB, False, "ma")
        d.line((px, base_y, px, base_y + 12), fill=BORDERGRAY, width=2)

    text(d, (80, 1052), "上段: PR作成（GitHub）／中段: mainの履歴（git）／下段: 起動ログの日別件数。", 22, SUB)
    img.save(ROOT / "mainline.png")


if __name__ == "__main__":
    funnel()
    mainline()
    print("wrote funnel.png, mainline.png")
