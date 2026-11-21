#!/usr/bin/env python3
"""Figures for the 2026-11-22 review-hub deck.

Public-safe aggregate data only, read on 2026-11-22:
- project: 21 issues = Backlog 16 / In Progress 4 / In Review 1 / Todo 0.
- the single In Review issue is a direct blocker of 4 issues.
- 2 of those 4 have no other unfinished blocker; 2 still wait on another issue.
- private repo: 8 open pull requests, all drafts, 0 merged.

Only counts, state names and relation shapes are drawn. No issue identifiers,
titles, bodies, comments, branch names, PR titles or customer data.
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
BORDERGRAY = "#b8b8b8"
RED = "#a2191f"
LIGHTRED = "#fff1f1"
GREEN = "#0e6027"
LIGHTGREEN = "#defbe6"

W, H = 2000, 1125


def font(size, bold=False):
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def canvas(title, kicker):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 12), fill=BLUE)
    text(d, (90, 70), kicker, 30, BLUE, True)
    text(d, (90, 118), title, 54, INK, True)
    return img, d


def footer(d, note):
    d.line((90, H - 92, W - 90, H - 92), fill=BORDERGRAY, width=2)
    text(d, (90, H - 74), note, 26, SUB)


def arrow(d, start, end, color=GRAY, width=4):
    d.line((start, end), fill=color, width=width)
    ax, ay = end
    d.polygon(
        [(ax, ay), (ax - 20, ay - 11), (ax - 20, ay + 11)],
        fill=color,
    )


def figure_state():
    img, d = canvas("21件のうちTodoは0件", "EVIDENCE / 状態の内訳")

    cell, gap = 96, 14
    x0, y0 = 110, 260
    fills = []
    for _ in range(16):
        fills.append((LIGHTGRAY, BORDERGRAY))
    for _ in range(4):
        fills.append((BLUE, BLUE))
    fills.append(("#ffd7a8", AMBER))

    for i, (fill, border) in enumerate(fills):
        r, c = divmod(i, 7)
        x = x0 + c * (cell + gap)
        y = y0 + r * (cell + gap)
        d.rounded_rectangle((x, y, x + cell, y + cell), 10, fill=fill, outline=border, width=3)

    legend = [
        ("Backlog 16", LIGHTGRAY, BORDERGRAY),
        ("進行中 4", BLUE, BLUE),
        ("レビュー待ち 1", "#ffd7a8", AMBER),
    ]
    for i, (label, fill, border) in enumerate(legend):
        x = 110 + i * 240
        d.rounded_rectangle((x, 640, x + 28, 668), 6, fill=fill, outline=border, width=2)
        text(d, (x + 40, 642), label, 28, SUB)

    # Todo has no cell, because no issue is in that state
    d.rounded_rectangle((110, 700, 460, 788), 12, fill=LIGHTRED, outline=RED, width=3)
    text(d, (134, 718), "Todo", 28, RED, True)
    text(d, (134, 752), "該当する課題なし（0件）", 24, RED)

    # right panel: horizontal bars
    text(d, (1060, 236), "状態ごとの件数", 30, SUB, True)
    rows = [
        ("Backlog", 16, LIGHTGRAY, BORDERGRAY, 500),
        ("進行中", 4, BLUE, BLUE, 125),
        ("レビュー待ち", 1, "#ffd7a8", AMBER, 34),
        ("Todo", 0, LIGHTRED, RED, 0),
    ]
    for i, (label, count, fill, border, width) in enumerate(rows):
        y = 300 + i * 120
        text(d, (1290, y + 28), label, 30, INK, False, "rm")
        if width == 0:
            d.rounded_rectangle((1310, y, 1310 + 120, y + 56), 8, fill=LIGHTRED, outline=RED, width=3)
            text(d, (1310 + 140, y + 28), "0件", 30, RED, True, "lm")
        else:
            d.rounded_rectangle((1310, y, 1310 + width, y + 56), 8, fill=fill, outline=border, width=3)
            text(d, (1310 + width + 24, y + 28), f"{count}件", 30, INK, True, "lm")

    d.line((1060, 780, 1900, 780), fill=BORDERGRAY, width=2)
    text(d, (1060, 810), "Backlog 16件のうち 8件は、未完了の課題が前提", 30, INK, True)
    text(d, (1060, 860), "Todoへ上げられるのは、前提が全部外れた課題だけ", 28, SUB)
    footer(d, "出典: 対象プロジェクトの課題21件を2026-11-22に読み取り。課題番号は非公開のため伏せている。")
    img.save(ROOT / "state_breakdown.png")


def figure_blocking():
    img, d = canvas("レビュー待ち1件が、4件の前提になっている", "EVIDENCE / 依存の内訳")

    # hub
    hx0, hy0, hx1, hy1 = 110, 380, 580, 700
    d.rounded_rectangle((hx0, hy0, hx1, hy1), 20, fill=LIGHTAMBER, outline=AMBER, width=4)
    text(d, (hx0 + 34, hy0 + 32), "レビュー待ち", 30, AMBER, True)
    text(d, (hx0 + 34, hy0 + 74), "1件", 64, INK, True)
    text(d, (hx0 + 34, hy0 + 168), "Draft PR 1本", 28, SUB)
    text(d, (hx0 + 34, hy0 + 210), "25日そのまま", 28, SUB)
    text(d, (hx0 + 34, hy0 + 252), "merge 0本", 28, SUB)

    boxes = [
        ("対象1", "もう1件のBacklogが前提", "追加の前提あり", LIGHTAMBER, AMBER),
        ("対象2", "これだけで着手できる", "すぐ動ける", LIGHTGREEN, GREEN),
        ("対象3", "これだけで着手できる", "すぐ動ける", LIGHTGREEN, GREEN),
        ("対象4", "対象1の完了が前提", "追加の前提あり", LIGHTAMBER, AMBER),
    ]
    bx0, bx1 = 940, 1880
    bh, bgap = 120, 50
    by0 = 190
    for i, (name, note, badge, fill, border) in enumerate(boxes):
        y = by0 + i * (bh + bgap)
        d.rounded_rectangle((bx0, y, bx1, y + bh), 16, fill=fill, outline=border, width=4)
        text(d, (bx0 + 34, y + 18), name, 34, INK, True)
        text(d, (bx0 + 34, y + 68), note, 28, SUB)
        bw = 250
        d.rounded_rectangle((bx1 - bw - 28, y + 32, bx1 - 28, y + 88), 28, fill=BG, outline=border, width=3)
        text(d, ((bx1 - bw - 28 + bx1 - 28) / 2, y + 60), badge, 24, border, True, "mm")
        arrow(d, (hx1 + 6, (hy0 + hy1) / 2), (bx0 - 12, y + bh / 2), AMBER, 4)

    d.line((110, 830, 1880, 830), fill=BORDERGRAY, width=2)
    text(d, (110, 858), "別ルート: 依存の無い高優先度3件をTodoへ移すと、別の1件か2件の前提が外れる", 30, INK, True)
    text(d, (110, 902), "どちらのルートも、workerではなく人の操作でしか開かない", 28, SUB)
    footer(d, "出典: 2026-11-22時点のLinear上の blockedBy 関係。依存先は直接の1段のみを数えている。")
    img.save(ROOT / "blocking_graph.png")


if __name__ == "__main__":
    figure_state()
    figure_blocking()
    print("wrote state_breakdown.png, blocking_graph.png")
