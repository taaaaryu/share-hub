#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data sources (public-safe aggregates only):
- Linear issue status counts for the target project (counts and identifiers only, no bodies)
- open draft PR numbers and dates from the private repo
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
PURPLE = "#8a3ffc"
GRAY = "#6f6f6f"
RED = "#da1e28"

STATUS_ROWS = [
    ("Todo", "0", "workerが着手できる唯一の状態", RED, True),
    ("In Progress", "4", "着手済み。4件とも草案PRが作成済み", BLUE, False),
    ("In Review", "1", "PR作成済みで確認待ち", PURPLE, False),
    ("Backlog", "16", "計画のみ。workerは着手しない", GRAY, False),
    ("Done", "0", "2026-10-28以降の完了", GRAY, False),
]

AGING = [
    ("TAA-44", "In Review", "PR #1", 13, PURPLE),
    ("TAA-52", "In Progress", "PR #5", 5, BLUE),
    ("TAA-54", "In Progress", "PR #6", 5, BLUE),
    ("TAA-55", "In Progress", "PR #7", 5, BLUE),
    ("TAA-56", "In Progress", "PR #8", 5, BLUE),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def status_board(path: Path) -> None:
    W, H = 2000, 900
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (110, 60), "対象21件のうち、着手できるTodoは0件", 52, INK, bold=True)
    text(d, (110, 134), "2026-11-10 時点。状態はLinearから再取得した件数です。", 26, SUB)

    text(d, (110, 200), "21件の状態内訳", 28, SUB, bold=True)

    x0, width, top, height = 110, 1780, 250, 90
    total = 21
    segments = [
        ("Backlog 16", 16, GRAY),
        ("In Progress 4", 4, BLUE),
        ("In Review 1", 1, PURPLE),
    ]
    x = x0
    for label, count, color in segments:
        w = width * count / total
        d.rectangle((x, top, x + w, top + height), fill=color)
        if w > 200:
            text(d, (x + w / 2, top + height / 2), label, 28, BG, bold=True, anchor="mm")
        x += w

    text(d, (x0, top + height + 28), "Todo（workerが着手できる唯一の状態）は 0 件", 30, RED, bold=True)
    text(d, (x0 + width, top + height + 30), "In Review 1", 24, PURPLE, bold=True, anchor="ra")

    row_top = 450
    for i, (name, count, meaning, color, highlight) in enumerate(STATUS_ROWS):
        y = row_top + i * 76
        if highlight:
            d.rounded_rectangle((96, y - 12, 1904, y + 60), radius=10, fill="#fff1f1")
        text(d, (120, y + 24), name, 30, INK if not highlight else RED, bold=True, anchor="lm")
        text(d, (560, y + 24), count, 40, color, bold=True, anchor="rm")
        text(d, (610, y + 25), meaning, 26, SUB, anchor="lm")
        d.line((120, y + 68, 1880, y + 68), fill=LINE, width=2)

    text(d, (120, 850), "件数の合計は21。TodoとDoneが0のため、workerが開始できる課題はありません。", 22, SUB)

    img.save(path)


def aging(path: Path) -> None:
    W, H = 2000, 900
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (110, 60), "止まっている5件は、すべて確認待ち", 52, INK, bold=True)
    text(d, (110, 134), "起算は各課題が In Progress / In Review になった日。今日 2026-11-10 時点の日数。", 26, SUB)

    x0, x1 = 380, 1780
    day = (x1 - x0) / 14
    base_top, bar_h, gap = 240, 56, 34
    for tick in range(0, 15, 5):
        gx = x0 + day * tick
        d.line((gx, base_top - 16, gx, base_top + 5 * (bar_h + gap) + 4), fill=LINE, width=2)
        text(d, (gx, base_top + 5 * (bar_h + gap) + 22), f"{tick}日", 22, SUB, anchor="ma")

    for i, (ident, state, pr, days, color) in enumerate(AGING):
        y = base_top + i * (bar_h + gap)
        text(d, (120, y + 4), ident, 30, INK, bold=True)
        text(d, (120, y + 36), f"{state} / {pr}", 22, SUB)
        d.rounded_rectangle((x0, y, x0 + day * days, y + bar_h), radius=8, fill=color)
        text(d, (x0 + day * days + 20, y + bar_h / 2), f"{days}日", 30, INK, bold=True, anchor="lm")

    note_y = base_top + 5 * (bar_h + gap) + 78
    text(d, (110, note_y), "In Progress の4件は、いずれも草案PRが作成済みです。", 26, INK, bold=True)
    text(d, (110, note_y + 42), "workerの手順ではPR作成後に In Review へ移すため、状態が置き忘れられていると判断できます。", 26, SUB)

    img.save(path)


if __name__ == "__main__":
    status_board(ROOT / "status.png")
    aging(ROOT / "aging.png")
    print("wrote status.png / aging.png")
