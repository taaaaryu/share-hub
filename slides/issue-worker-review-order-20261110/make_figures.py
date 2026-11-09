#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data sources (public-safe aggregates only):
- open draft PR numbers, diff sizes, file counts, test-file counts from the private repo
No issue bodies, comments, code or customer data are used.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"

INK = "#161616"
SUB = "#525252"
LINE = "#e0e0e0"
BG = "#ffffff"
PANEL = "#f4f4f4"
BLUE = "#0f62fe"
TEAL = "#007d79"
GRAY = "#6f6f6f"
RED = "#da1e28"

# (pr, added, deleted, files, test_files, age_days, theme)
QUEUE = [
    (6, 155, 0, 6, 0, 5, "DevEx"),
    (8, 615, 6, 10, 1, 5, "DevEx"),
    (5, 718, 0, 10, 2, 5, "Harness"),
    (4, 521, 239, 19, 11, 5, "解析"),
    (7, 939, 0, 11, 1, 5, "DevEx"),
    (1, 1317, 0, 13, 3, 13, "解析"),
    (2, 2237, 1, 12, 2, 13, "DevEx"),
    (3, 6359, 0, 27, 4, 13, "DevEx"),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def review_order(path: Path) -> None:
    W, H = 2000, 900
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    rows = sorted(QUEUE, key=lambda r: r[1] + r[2])
    totals = [r[1] + r[2] for r in rows]
    total = sum(totals)

    text(d, (110, 56), "確認待ち8件の変更行数（小さい順）", 50, INK, bold=True)
    text(d, (110, 130), "2026-11-10 時点の草案PR。行数は追加＋削除。棒の右の%は、ここまでの累計が全体に占める割合。", 24, SUB)

    x0, bar_max = 470, 1020
    top, bar_h, gap = 210, 52, 24
    scale = bar_max / max(totals)

    for i, row in enumerate(rows):
        pr, add, dele, files, tests, age, theme = row
        lines = add + dele
        y = top + i * (bar_h + gap)
        color = TEAL if theme == "解析" else BLUE
        text(d, (110, y + bar_h / 2 - 12), f"PR #{pr}", 30, INK, bold=True, anchor="lm")
        text(d, (110, y + bar_h / 2 + 18), f"{files}ファイル / テスト{tests}本", 20, SUB, anchor="lm")
        w = max(lines * scale, 10)
        d.rounded_rectangle((x0, y, x0 + w, y + bar_h), radius=8, fill=color)
        text(d, (x0 + w + 22, y + bar_h / 2), f"{lines:,}行", 28, INK, bold=True, anchor="lm")
        cum = sum(totals[: i + 1]) / total * 100
        text(d, (x0 + w + 210, y + bar_h / 2), f"累計 {cum:.0f}%", 22, GRAY, anchor="lm")

    note_y = top + 8 * (bar_h + gap) + 2
    text(d, (110, note_y), "合計 13,107行 / 最大 6,359行（PR #3）は全体の48%", 26, INK, bold=True)
    text(d, (110, note_y + 40), "小さい4件（#6 #8 #5 #4）を先に見ると、全体の17%で4件が片付きます。", 24, SUB)

    d.rounded_rectangle((96, 90, 1904, 950), radius=0, outline=LINE, width=0)
    img.save(path)


def queue_cards(path: Path) -> None:
    W, H = 2000, 780
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (110, 56), "8件を、小さい順に並べた確認カード", 50, INK, bold=True)
    text(d, (110, 130), "行数の少ない順。『テスト』はテスト用ファイルを含む件数で、品質の保証ではありません。", 24, SUB)

    cols, cw, ch, gx, gy = 4, 420, 240, 34, 40

    for i, row in enumerate(sorted(QUEUE, key=lambda r: r[1] + r[2])):
        pr, add, dele, files, tests, age, theme = row
        lines = add + dele
        cx = 110 + (i % cols) * (cw + gx)
        cy = 210 + (i // cols) * (ch + gy)
        color = TEAL if theme == "解析" else BLUE
        d.rounded_rectangle((cx, cy, cx + cw, cy + ch), radius=16, fill=PANEL)
        d.rounded_rectangle((cx, cy, cx + 8, cy + ch), radius=8, fill=color)
        text(d, (cx + 30, cy + 26), f"{i + 1}", 44, color, bold=True)
        text(d, (cx + 78, cy + 30), f"PR #{pr}", 34, INK, bold=True)
        text(d, (cx + 30, cy + 96), f"{lines:,}行", 40, INK, bold=True)
        text(d, (cx + 30, cy + 152), f"{files}ファイル / テスト{tests}本", 24, SUB)
        text(d, (cx + 30, cy + 186), f"作成から{age}日 / {theme}", 24, GRAY)

    img.save(path)


if __name__ == "__main__":
    review_order(ROOT / "review_order.png")
    queue_cards(ROOT / "queue_cards.png")
