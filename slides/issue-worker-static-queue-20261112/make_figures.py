#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data source (public-safe aggregates only, measured 2026-11-12 JST):
- Linear project issue list: status counts and updatedAt for 21 issues.
- Two read-only checks: 2026-11-12 00:19 JST and 00:51 JST.

No issue titles, bodies, comments, code or customer data appear in the images.
Only aggregate counts, age buckets and timestamps are drawn.
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
PALE = "#edf5ff"
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


def aging(path: Path) -> None:
    W, H = 1400, 860
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (70, 40), "21件の中央値は、14日間更新されていない", 44, INK, bold=True)
    text(d, (70, 100), "LinearのupdatedAtを2026-11-12 00:51 JSTに取得。状態ごとに、最後の更新からの日数で数えた。", 20, SUB)

    # Table geometry
    top = 170
    label_x = 80
    cols = [(340, 630), (650, 940), (960, 1250)]
    headers = ["0-2日", "3-10日", "11日以上"]
    rows = [
        ("Backlog 16件", [3, 3, 10], DARKBLUE),
        ("In Progress 4件", [0, 4, 0], TEAL),
        ("In Review 1件", [0, 0, 1], RED),
    ]

    for (x0, x1), head in zip(cols, headers):
        text(d, ((x0 + x1) / 2, top - 46), head, 22, SUB, bold=True, anchor="ma")

    row_h = 120
    for index, (label, values, color) in enumerate(rows):
        y = top + index * (row_h + 14)
        text(d, (label_x, y + 46), label, 24, INK, bold=True)
        for (x0, x1), value in zip(cols, values):
            if value:
                fill = PALE if color == DARKBLUE else (LIGHTTEAL if color == TEAL else LIGHTRED)
                box(d, x0, y, x1 - x0, row_h, fill, color, 2)
                text(d, ((x0 + x1) / 2, y + row_h / 2 - 6), f"{value}件", 34, color, bold=True, anchor="ma")
            else:
                box(d, x0, y, x1 - x0, row_h, "#fafafa", LIGHTGRAY, 1)
                text(d, ((x0 + x1) / 2, y + row_h / 2 - 6), "0", 30, GRAY, bold=True, anchor="ma")

    # Summary band
    band_y = 590
    box(d, 80, band_y, 1240, 110, PANEL, LIGHTGRAY, 1)
    text(d, (110, band_y + 20), "11日以上動いていない 11件", 26, INK, bold=True)
    text(d, (110, band_y + 62), "うちIn Review 1件・Backlog 10件。4件のIn Progressも、最後の更新は6日前（11月5日）。", 21, SUB)

    # Median callout
    text(d, (80, 736), "最後の更新からの日数の中央値", 20, SUB)
    text(d, (80, 768), "14.2日", 40, RED, bold=True)
    text(d, (400, 748), "21件の半分以上が、2週間前の記録のまま。", 22, INK)
    text(d, (400, 786), "※ updatedAtは機械的な更新も含むため、『誰も見ていない』証明ではない。", 19, SUB)
    text(d, (80, 822), "箱は件数。青はBacklog、緑はIn Progress、赤はIn Review。0の箱は薄い灰色。", 18, SUB)

    img.save(path)


def two_checks(path: Path) -> None:
    W, H = 1400, 760
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (70, 40), "32分あけて2回読んでも、数字は同じだった", 44, INK, bold=True)
    text(d, (70, 100), "同じLinearを、人ではなくworkerが読み取りだけで2回確認した。", 20, SUB)

    states = [
        ("Todo（着手できる）", "0", BLUE),
        ("Backlog", "16", INK),
        ("In Progress", "4", INK),
        ("In Review", "1", INK),
        ("Done", "0", GRAY),
    ]
    panels = [(70, "1回目 00:19 JST"), (730, "2回目 00:51 JST")]
    for x, header in panels:
        box(d, x, 160, 600, 390, "#ffffff", LIGHTGRAY, 2)
        text(d, (x + 30, 182), header, 24, DARKBLUE, bold=True)
        for i, (name, value, color) in enumerate(states):
            y = 235 + i * 58
            text(d, (x + 30, y), name, 21, SUB if name == "Done" else INK)
            text(d, (x + 560, y - 6), value, 32, color, bold=True, anchor="ra")
            if i < len(states) - 1:
                d.line((x + 30, y + 42, x + 570, y + 42), fill="#f0f0f0", width=1)

    # Delta band
    box(d, 70, 590, 1260, 80, PALE, BLUE, 2)
    text(d, (100, 610), "差分", 22, DARKBLUE, bold=True)
    text(d, (100, 640), "0件", 30, DARKBLUE, bold=True)
    text(d, (230, 616), "5つの数字はすべて同じ。状態を書き換えた記録も、workerの実装もありません。", 22, INK)
    text(d, (230, 646), "workerが選べるのはTodoだけ。0件なので、実装の手前で止まります。", 20, SUB)

    text(d, (70, 706), "確認したのは件数と更新時刻だけ。課題の優先度やPRの正しさは見ていない。", 19, SUB)

    img.save(path)


if __name__ == "__main__":
    aging(ROOT / "queue_aging.png")
    two_checks(ROOT / "two_checks.png")
    print("done")
