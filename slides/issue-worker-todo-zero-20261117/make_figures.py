#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data source (public-safe aggregates only, checked 2026-11-17 JST):
- Linear project f7f3a327-a06b-478f-bd88-c49fc2b79cef: 21 issues, status counts,
  state-history timestamps of the 5 active issues, blockedBy relations.
- private remote thumaster: 8 open Draft PRs, creation dates only.

Issue titles, bodies, comments, assignees, branch names and customer data are
not drawn. Only counts, state names and elapsed days.
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
AMBER = "#8a3800"
LIGHTAMBER = "#fff2e8"
GRAY = "#6f6f6f"
LIGHTGRAY = "#f4f4f4"
BORDERGRAY = "#c6c6c6"
RED = "#da1e28"
LIGHTRED = "#fff1f1"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def box(draw, x, y, w, h, fill, border, width=2):
    draw.rectangle((x, y, x + w, y + h), fill=fill, outline=border, width=width)


def board(path: Path) -> None:
    W, H = 2000, 1125
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (100, 70), "21件のうち、作業者の入口にいたのは0件", 62, INK, bold=True)
    text(d, (100, 160), "2026-11-17時点。1マス＝課題1件。列の名前はLinearの状態。", 26, SUB)

    cell, gap = 150, 18
    x0, y0 = 100, 245
    cells = (
        [("In Progress", BLUE, PALE) for _ in range(4)]
        + [("In Review", AMBER, LIGHTAMBER) for _ in range(1)]
        + [("Backlog", GRAY, LIGHTGRAY) for _ in range(16)]
    )
    for i, (label, color, pale) in enumerate(cells):
        col, row = i % 7, i // 7
        x = x0 + col * (cell + gap)
        y = y0 + row * (cell + gap)
        box(d, x, y, cell, cell, pale, color, 3)
        text(d, (x + cell / 2, y + cell / 2 - 12), label, 18, color, bold=True, anchor="mm")
        text(d, (x + cell / 2, y + cell / 2 + 18), f"{i + 1:02d}", 16, SUB, anchor="mm")

    text(d, (100, 745), "4件が着手済み、1件がレビュー待ち、16件が計画の列。順序は意味を持たない。", 20, SUB)

    # Right panel: the worker's entrance
    px, py, pw, ph = 1360, 245, 540, 486
    box(d, px, py, pw, ph, "#fafafa", BORDERGRAY, 2)
    text(d, (px + 30, py + 24), "作業者の入口", 24, INK, bold=True)
    text(d, (px + 30, py + 62), "Todo（やると決めた列）", 20, SUB)
    text(d, (px + 30, py + 100), "0件", 96, RED, bold=True)
    rows = [
        ("Backlog", "16件", GRAY),
        ("In Progress", "4件", BLUE),
        ("In Review", "1件", AMBER),
    ]
    for i, (name, count, color) in enumerate(rows):
        y = py + 236 + i * 62
        d.rectangle((px + 30, y + 6, px + 48, y + 24), fill=color)
        text(d, (px + 62, y), name, 22, INK)
        text(d, (px + pw - 40, y - 4), count, 26, color, bold=True, anchor="ra")
    text(d, (px + 30, py + 430), "Draft PRは8本（すべてdraft）", 20, SUB)

    # Bottom banner
    box(d, 100, 900, 1800, 130, LIGHTRED, RED, 3)
    text(d, (130, 920), "選べる課題 0件", 38, RED, bold=True)
    text(d, (430, 926), "Todoが空なので、今日できたのは状態の棚卸しだけ。", 28, INK)
    text(d, (130, 984), "コードは1行も変えていない。新しいPRも作っていない。", 22, SUB)

    img.save(path)


def frozen(path: Path) -> None:
    W, H = 2000, 1125
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (100, 70), "着手済み5件は12日から20日、止まったまま", 62, INK, bold=True)
    text(d, (100, 160), "2026-11-17時点。日数はLinearの状態変更時刻とGitHubのPR作成日から計算。", 26, SUB)

    # Left: active issues, days since state change
    lx, ly, lw, lh = 100, 235, 830, 470
    box(d, lx, ly, lw, lh, "#ffffff", BORDERGRAY, 2)
    text(d, (lx + 28, ly + 22), "状態が変わってからの経過日数", 24, INK, bold=True)
    active = [
        ("In Review の1件", 20, AMBER),
        ("In Progress の1件", 12, BLUE),
        ("In Progress の1件", 12, BLUE),
        ("In Progress の1件", 12, BLUE),
        ("In Progress の1件", 12, BLUE),
    ]
    for i, (label, days, color) in enumerate(active):
        y = ly + 72 + i * 68
        text(d, (lx + 28, y + 6), label, 19, SUB)
        bar = int(days / 20 * 520)
        d.rectangle((lx + 28, y + 32, lx + 28 + bar, y + 58), fill=color)
        text(d, (lx + 36 + bar, y + 30), f"{days}日", 22, INK, bold=True)
    text(d, (lx + 28, ly + 420), "この期間に状態が変わった課題は0件。", 21, RED, bold=True)

    # Right: draft PR wait days
    px, py, pw, ph = 1010, 235, 890, 470
    box(d, px, py, pw, ph, "#ffffff", BORDERGRAY, 2)
    text(d, (px + 28, py + 22), "Draft PR 8本の待ち日数", 24, INK, bold=True)
    wait = [20, 20, 20, 12, 12, 12, 12, 12]
    for i, days in enumerate(wait):
        y = py + 68 + i * 46
        text(d, (px + 28, y + 8), f"PR {i + 1}", 18, SUB)
        bar = int(days / 20 * 480)
        color = RED if days >= 20 else AMBER
        d.rectangle((px + 110, y + 8, px + 110 + bar, y + 30), fill=color)
        text(d, (px + 120 + bar, y + 6), f"{days}日", 19, INK)
    text(d, (px + 28, py + 438), "8本すべてdraft。チェック結果があるのは4本だけ。", 20, SUB)

    # Bottom banners
    box(d, 100, 736, 1800, 118, LIGHTRED, RED, 3)
    text(d, (130, 758), "状態変更 0件", 38, RED, bold=True)
    text(d, (400, 762), "入口が空なだけでなく、着手済みの列も止まっている。", 28, INK)
    text(d, (130, 814), "作業者はレビューもmergeもできない。ここを動かせるのは人だけ。", 22, SUB)

    box(d, 100, 878, 1800, 84, PALE, BLUE, 2)
    text(d, (130, 894), "今日の成果物: この資料のみ。コード0行・新規PR 0本。", 24, INK, bold=True)
    text(d, (130, 924), "事実は数えたが、8本のPRの中身が今も正しいかは確かめていない。", 22, SUB)

    box(d, 100, 986, 1800, 78, LIGHTGRAY, BORDERGRAY, 2)
    text(d, (130, 1002), "次に人がやること: Draft PRを1本レビューする、またはTodoを1件用意する。", 22, INK)
    text(d, (130, 1032), "どちらかが起きるまで、次の実行も同じ結果になる。", 20, SUB)

    img.save(path)


if __name__ == "__main__":
    board(ROOT / "board.png")
    frozen(ROOT / "frozen.png")
    print("wrote board.png and frozen.png")
