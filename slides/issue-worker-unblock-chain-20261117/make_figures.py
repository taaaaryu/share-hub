#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Public-safe data only (aggregated, checked 2026-11-17):
- Linear project f7f3a327-a06b-478f-bd88-c49fc2b79cef: 21 issues,
  per-status counts, priority names, and blockedBy edges between issues.
- Issue identifiers are kept because the reader needs them to act.
  Titles, descriptions, comments, assignees, and history are not drawn.
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


def box(draw, x, y, w, h, fill, border, width=2, radius=10):
    draw.rounded_rectangle((x, y, x + w, y + h), radius=radius, fill=fill, outline=border, width=width)


def arrow(draw, start, end, color=GRAY, width=4, dashed=False):
    if dashed:
        x1, y1 = start
        x2, y2 = end
        steps = 26
        for i in range(0, steps, 2):
            ax = x1 + (x2 - x1) * i / steps
            ay = y1 + (y2 - y1) * i / steps
            bx = x1 + (x2 - x1) * (i + 1) / steps
            by = y1 + (y2 - y1) * (i + 1) / steps
            draw.line((ax, ay, bx, by), fill=color, width=width)
    else:
        draw.line((start, end), fill=color, width=width)
    x, y = end
    px, py = start
    dx, dy = x - px, y - py
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / length, dy / length
    size = 14
    head = (x - ux * size - uy * size * 0.7, y - uy * size + ux * size * 0.7)
    other = (x - ux * size + uy * size * 0.7, y - uy * size - ux * size * 0.7)
    draw.polygon((end, head, other), fill=color)


def gates(path: Path) -> None:
    W, H = 2000, 1125
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (100, 66), "21件のうち、選べる列にいたのは0件", 62, INK, bold=True)
    text(d, (100, 158), "2026-11-17時点。棒の長さ＝課題数。workerが選べるのはTodoだけ。", 26, SUB)

    rows = [
        ("Backlog", 16, GRAY, LIGHTGRAY, "計画の列。workerは動かせない"),
        ("In Progress", 4, BLUE, PALE, "着手済み。Draft PRあり"),
        ("In Review", 1, AMBER, LIGHTAMBER, "レビュー待ち。下流6件を止めている"),
        ("Todo", 0, RED, LIGHTRED, "workerの入口。ここだけが空"),
    ]

    label_x = 100
    bar_x = 560
    unit = 52
    y = 232
    for label, count, color, pale, note in rows:
        text(d, (label_x, y + 37), label, 34, INK, bold=True, anchor="lm")
        width = count * unit if count else 26
        box(d, bar_x, y, width, 74, pale, color, width=3, radius=8)
        text(d, (bar_x + 20, y + 37), str(count), 34, color, bold=True, anchor="lm")
        note_x = bar_x + width + 26 if count else bar_x + 78
        text(d, (note_x, y + 37), note, 26, color if count == 0 else SUB, anchor="lm")
        y += 112

    text(d, (100, 716), "選定の門（上から順に適用）", 30, INK, bold=True)
    gate_rows = [
        ("1  状態がTodoか", "0件が通過", RED),
        ("2  依存が完了済みか", "対象0件のため未評価", SUB),
        ("3  担当・既存PR・作業ツリー", "対象0件のため未評価", SUB),
    ]
    gy = 768
    for name, result, color in gate_rows:
        box(d, 100, gy, 800, 74, BG, BORDERGRAY, width=2, radius=8)
        text(d, (128, gy + 37), name, 28, INK, anchor="lm")
        text(d, (930, gy + 37), result, 26, color, bold=(color != SUB), anchor="lm")
        gy += 86

    text(d, (100, 1052), "出典: Linear プロジェクトの課題21件を集計。タイトル・本文・担当者は描いていない。", 20, GRAY)
    img.save(path)


def chain(path: Path) -> None:
    W, H = 2000, 1125
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (60, 56), "レビュー待ち1件の下流に、Backlogの6件が並ぶ", 58, INK, bold=True)
    text(d, (60, 142), "矢印はblockedBy。前の課題が終わるまで、後の課題は着手しない。", 26, SUB)

    def node(x, y, w, h, head, tag, tone):
        border, pale = tone
        box(d, x, y, w, h, pale, border, width=3, radius=12)
        text(d, (x + 22, y + 36), head, 32, INK, bold=True, anchor="lm")
        text(d, (x + 22, y + 80), tag, 22, border, bold=True, anchor="lm")

    # TAA-44: In Review, blocks four issues directly.
    node(60, 500, 300, 120, "TAA-44", "In Review / 20日待ち", (AMBER, LIGHTAMBER))

    direct = [
        ("TAA-45", "Backlog / High", 230),
        ("TAA-46", "Backlog / High", 380),
        ("TAA-48", "Backlog / Medium", 530),
        ("TAA-49", "Backlog / Medium", 680),
    ]
    for head, tag, y in direct:
        node(470, y, 250, 100, head, tag, (GRAY, LIGHTGRAY))

    node(870, 240, 250, 100, "TAA-47", "Backlog / High", (GRAY, LIGHTGRAY))
    node(1350, 505, 270, 150, "TAA-50", "Backlog / High", (GRAY, LIGHTGRAY))
    node(60, 850, 320, 100, "TAA-35", "Backlog / High / 前提なし", (BLUE, PALE))

    for _, _, y in direct:
        arrow(d, (362, 560), (462, y + 50), GRAY)
    arrow(d, (720, 280), (862, 296), GRAY)
    arrow(d, (720, 430), (862, 330), GRAY)
    arrow(d, (1120, 300), (1342, 545), GRAY)
    arrow(d, (720, 580), (1342, 580), GRAY)
    arrow(d, (720, 730), (1342, 614), GRAY)
    arrow(d, (380, 900), (1342, 648), BLUE, dashed=True)

    # legend
    lx, ly = 1350, 170
    text(d, (lx, ly), "前提なしで着手できる候補", 24, SUB, bold=True)
    text(d, (lx, ly + 44), "TAA-35 / TAA-36 / TAA-43", 30, BLUE, bold=True)
    text(d, (lx, ly + 88), "いずれもHigh。この3件はレビューを待たずに着手できる。", 22, SUB)

    text(d, (60, 1052), "出典: Linear の blockedBy 関係を全Backlog課題について取得。タイトル・本文・担当者は描いていない。", 20, GRAY)
    img.save(path)


if __name__ == "__main__":
    gates(ROOT / "gates.png")
    chain(ROOT / "chain.png")
    print("wrote gates.png, chain.png")
