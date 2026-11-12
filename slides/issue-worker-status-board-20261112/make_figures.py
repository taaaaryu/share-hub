#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data source (public-safe aggregates only, measured 2026-11-12 02:08 JST):
- Linear project issue list: 21 issues, status counts only.

No issue titles, bodies, comments, assignees, branch names, code or customer
data appear in the images. Only counts, status names and the worker's rules
as written in the public policy are drawn.
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


def board(path: Path) -> None:
    W, H = 1400, 860
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (70, 44), "21件の状態ボード", 46, INK, bold=True)
    text(d, (70, 110), "2026-11-12 02:08 JST。Linearの対象プロジェクトを全件取得（続きのページ無し）。", 21, SUB)

    rows = [
        ("Todo", 0, "workerが選べる唯一の状態", RED, LIGHTRED),
        ("Backlog", 16, "計画の置き場", DARKBLUE, PALE),
        ("In Progress", 4, "すでに着手済み", TEAL, LIGHTTEAL),
        ("In Review", 1, "確認待ち", "#8a3800", "#fff2e8"),
        ("Done", 0, "取り込み完了", GRAY, "#f4f4f4"),
    ]

    bar_x, bar_max = 400, 700
    top, row_h, gap = 190, 104, 16
    for i, (name, count, note, color, pale) in enumerate(rows):
        y = top + i * (row_h + gap)
        box(d, 70, y, 1260, row_h, pale if count or name == "Todo" else BG, LIGHTGRAY, 1)
        text(d, (100, y + 14), name, 30, INK, bold=True)
        text(d, (100, y + 58), note, 18, SUB)
        if name == "Todo":
            box(d, bar_x, y + 18, 120, 68, LIGHTRED, RED, 3)
            text(d, (bar_x + 60, y + 52), "0件", 30, RED, bold=True, anchor="mm")
            text(d, (560, y + 40), "← ここが空なので、workerは1件も始められない", 24, RED, bold=True)
        else:
            width = int(bar_max * count / 16) if count else 4
            box(d, bar_x, y + 18, max(width, 4), 68, color, color, 1)
            text(d, (bar_x + max(width, 4) + 18, y + 52), f"{count}件", 30, INK, bold=True, anchor="lm")

    text(d, (70, 780), "合計21件 ／ Todo 0 ・ Backlog 16 ・ In Progress 4 ・ In Review 1 ・ Done 0", 22, SUB)
    img.save(path)


def gate(path: Path) -> None:
    W, H = 1400, 760
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (70, 44), "入口を開けられるのは人だけ", 46, INK, bold=True)
    text(d, (70, 110), "workerの権限と、人の判断が必要な作業を分けた図。", 21, SUB)

    left_x, right_x, panel_w = 70, 760, 570
    top, panel_h = 170, 470
    box(d, left_x, top, panel_w, panel_h, PALE, BLUE, 2)
    box(d, right_x, top, panel_w, panel_h, "#f4f4f4", GRAY, 2)

    text(d, (left_x + 28, top + 24), "workerができること", 27, DARKBLUE, bold=True)
    text(d, (right_x + 28, top + 24), "人だけができること", 27, SUB, bold=True)

    worker = [
        "Todoを1件だけ選ぶ",
        "issue番号のブランチを作る",
        "実装してテストを走らせる",
        "Draft PRを作る",
        "In Progress → In Review",
    ]
    human = [
        "BacklogをTodoへ移す",
        "担当者を決める",
        "ブランチをPRにする",
        "レビューしてmergeする",
        "課題をDoneにする",
    ]

    for i, item in enumerate(worker):
        y = top + 88 + i * 68
        box(d, left_x + 28, y, 22, 22, BLUE, BLUE, 1)
        text(d, (left_x + 66, y + 11), item, 22, INK, anchor="lm")

    for i, item in enumerate(human):
        y = top + 88 + i * 68
        box(d, right_x + 28, y, 22, 22, BG, SUB, 2)
        text(d, (right_x + 66, y + 11), item, 22, INK, anchor="lm")

    text(d, (700, 700), "今回はTodoが0件なので、左の最初の1手で止まった。", 24, RED, bold=True, anchor="mm")
    img.save(path)


if __name__ == "__main__":
    board(ROOT / "board.png")
    gate(ROOT / "gate.png")
    print("wrote board.png and gate.png")
