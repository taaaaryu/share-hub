#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data source (public-safe aggregates only, checked 2026-11-16 JST):
- Linear project f7f3a327-a06b-478f-bd88-c49fc2b79cef: 21 issues, status counts
  and blockedBy relations.
- private remote thumaster: 8 open Draft PRs, creation dates only.

Issue titles, bodies, comments, assignees, branch names and customer data are
not drawn. Only counts, state names and the shape of the dependency graph.
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
    text(d, (100, 160), "2026-11-16時点。1マス＝課題1件。列の名前はLinearの状態。", 26, SUB)

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


def chain(path: Path) -> None:
    W, H = 2000, 1125
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (100, 70), "レビュー待ち1件が、後ろの6件を止めている", 62, INK, bold=True)
    text(d, (100, 160), "矢印は「先に終わらないと始められない」向き。数字は課題の件数。", 26, SUB)

    # Column 1
    box(d, 100, 250, 340, 260, LIGHTAMBER, AMBER, 3)
    text(d, (130, 272), "In Review", 24, AMBER, bold=True)
    text(d, (130, 310), "1件", 76, AMBER, bold=True)
    text(d, (130, 408), "Draft PRのまま", 22, SUB)
    text(d, (130, 440), "19日 未レビュー", 22, RED, bold=True)

    # Arrow 1
    d.line((452, 380, 528, 380), fill=GRAY, width=4)
    d.polygon([(540, 380), (520, 368), (520, 392)], fill=GRAY)

    # Column 2
    box(d, 552, 220, 430, 460, "#fafafa", BORDERGRAY, 2)
    text(d, (582, 242), "直接これを待つ", 24, INK, bold=True)
    text(d, (582, 280), "4件", 44, GRAY, bold=True)
    for i in range(4):
        y = 342 + i * 78
        box(d, 582, y, 370, 62, "#ffffff", BORDERGRAY, 2)
        text(d, (602, y + 10), f"待ち {i + 1}", 17, SUB)
        text(d, (602, y + 32), "Backlogの課題", 21, INK)

    # Arrow 2
    d.line((994, 380, 1068, 380), fill=GRAY, width=4)
    d.polygon([(1080, 380), (1060, 368), (1060, 392)], fill=GRAY)

    # Column 3
    box(d, 1092, 300, 320, 250, "#fafafa", BORDERGRAY, 2)
    text(d, (1122, 322), "さらにその先", 24, INK, bold=True)
    text(d, (1122, 360), "2件", 44, GRAY, bold=True)
    text(d, (1122, 428), "待ちの1件が終わると", 20, SUB)
    text(d, (1122, 458), "開始できる課題。", 20, SUB)
    text(d, (1122, 494), "合計 6件", 22, RED, bold=True)

    # Right panel: draft PR wait days
    px, py, pw = 1470, 220, 430
    box(d, px, py, pw, 520, "#ffffff", BORDERGRAY, 2)
    text(d, (px + 26, py + 22), "Draft PR 8本の待ち日数", 22, INK, bold=True)
    wait = [19, 19, 18, 11, 11, 11, 11, 11]
    for i, days in enumerate(wait):
        y = py + 70 + i * 54
        text(d, (px + 26, y + 8), f"PR {i + 1}", 18, SUB)
        bar = int(days / 19 * 230)
        color = RED if days >= 18 else AMBER
        d.rectangle((px + 100, y + 8, px + 100 + bar, y + 30), fill=color)
        text(d, (px + 100 + bar + 10, y + 8), f"{days}日", 18, INK)

    # Bottom banners
    box(d, 100, 726, 1260, 120, LIGHTRED, RED, 3)
    text(d, (130, 748), "合計6件", 40, RED, bold=True)
    text(d, (330, 752), "たった1本のレビューで止まっている。", 28, INK)
    text(d, (130, 804), "作業者はレビューもmergeもできない。ここは人が動かすしかない。", 22, SUB)

    box(d, 100, 876, 1800, 84, PALE, BLUE, 2)
    text(d, (130, 892), "依存の空いたBacklogは5件（＋見出しのEpic 1件）。", 24, INK, bold=True)
    text(d, (130, 922), "ただしどれもTodoではないので、作業者は今日も着手できない。", 22, SUB)

    box(d, 100, 990, 1800, 74, LIGHTGRAY, BORDERGRAY, 2)
    text(d, (130, 1004), "待ち日数は2026-11-16時点。PRの中身が今も正しいかは未確認。", 21, SUB)

    img.save(path)


if __name__ == "__main__":
    board(ROOT / "board.png")
    chain(ROOT / "chain.png")
    print("wrote board.png and chain.png")
