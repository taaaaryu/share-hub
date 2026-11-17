#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data source (public-safe aggregates only, checked 2026-11-18 JST):
- Linear project f7f3a327-a06b-478f-bd88-c49fc2b79cef: 21 issues.
  Backlog 16 (1 epic + 7 with no blocker + 8 waiting on a blocker),
  In Progress 4, In Review 1, Todo 0.
- Blocking relations read from Linear (blockedBy / blocks).
- private remote thumaster: 8 open Pull Requests, all draft, all clean.

Issue titles, bodies, comments and customer data are not drawn. Only
identifiers, category words, status names and counts.
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
BORDERGRAY = "#c6c6c6"
GREEN = "#0e6027"
LIGHTGREEN = "#defbe6"
RED = "#da1e28"
LIGHTRED = "#fff1f1"


def font(size, bold=False):
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def box(draw, x, y, w, h, fill, border, width=2, radius=8, dashed=False):
    if dashed:
        # simple dashed rectangle: draw 4 sides as dashes
        step = 16
        def dash_line(x1, y1, x2, y2):
            length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
            if length == 0:
                return
            ux, uy = (x2 - x1) / length, (y2 - y1) / length
            pos = 0
            while pos < length:
                end = min(pos + step / 2, length)
                draw.line((x1 + ux * pos, y1 + uy * pos, x1 + ux * end, y1 + uy * end),
                          fill=border, width=width)
                pos += step
        draw.rectangle((x, y, x + w, y + h), fill=fill)
        dash_line(x, y, x + w, y)
        dash_line(x + w, y, x + w, y + h)
        dash_line(x + w, y + h, x, y + h)
        dash_line(x, y + h, x, y)
        return
    draw.rounded_rectangle((x, y, x + w, y + h), radius=radius, fill=fill, outline=border, width=width)


def arrow(draw, x1, y1, x2, y2, color=GRAY, width=5, dashed=False):
    if dashed:
        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        ux, uy = (x2 - x1) / length, (y2 - y1) / length
        pos = 0
        while pos < length - 14:
            end = min(pos + 9, length - 14)
            draw.line((x1 + ux * pos, y1 + uy * pos, x1 + ux * end, y1 + uy * end),
                      fill=color, width=width)
            pos += 18
    else:
        draw.line((x1, y1, x2, y2), fill=color, width=width)
    head = 11
    draw.polygon([(x2, y2), (x2 - head, y2 - head), (x2 - head, y2 + head)], fill=color)


READY = [
    ("TAA-35", "ベースライン計測", "High"),
    ("TAA-36", "OCRスパイク", "High"),
    ("TAA-43", "正解クリップ作成", "High"),
    ("TAA-38", "検出器の比較", "Medium"),
    ("TAA-39", "追跡の比較", "Medium"),
    ("TAA-40", "動画理解の研究", "Low"),
    ("TAA-41", "3D復元の研究", "Low"),
]

WAITING = [
    ("TAA-45", "43 と 44 待ち"),
    ("TAA-37", "35 と 36 待ち"),
    ("TAA-46", "44 待ち"),
    ("TAA-48", "44 待ち"),
    ("TAA-49", "45 と 44 待ち"),
    ("TAA-47", "45 と 46 待ち"),
    ("TAA-50", "35・47・48・49 待ち"),
    ("TAA-53", "52 待ち（52 は作業中）"),
]


def entry_map(path):
    W, H = 2000, 1125
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (90, 56), "21件のうち、今日そのまま着手できるのは7件", 56, INK, bold=True)
    text(d, (90, 138), "依存関係をLinearから読み取り、着手できる件と待っている件に分けた。2026-11-18 JST。", 25, SUB)

    # ---- left panel: ready
    px, py, pw, ph = 90, 210, 880, 760
    box(d, px, py, pw, ph, "#ffffff", GREEN, 3)
    text(d, (px + 28, py + 22), "着手できる 7件", 34, GREEN, bold=True)
    text(d, (px + 340, py + 32), "依存なし・担当なし", 22, SUB)
    for i, (ident, category, priority) in enumerate(READY):
        y = py + 84 + i * 94
        box(d, px + 24, y, pw - 48, 80, LIGHTGREEN, GREEN, 2)
        text(d, (px + 46, y + 16), ident, 30, GREEN, bold=True)
        text(d, (px + 210, y + 20), category, 25, INK)
        col = AMBER if priority == "High" else (SUB if priority == "Medium" else GRAY)
        text(d, (px + pw - 46, y + 24), priority, 21, col, anchor="ra")

    # ---- right panel: waiting
    qx, qy, qw, qh = 1030, 210, 880, 760
    box(d, qx, qy, qw, qh, "#ffffff", AMBER, 3)
    text(d, (qx + 28, qy + 22), "待っている 8件", 34, AMBER, bold=True)
    text(d, (qx + 268, qy + 30), "先に別の課題が終わる必要がある", 22, SUB)
    for i, (ident, why) in enumerate(WAITING):
        y = qy + 84 + i * 82
        box(d, qx + 24, y, qw - 48, 70, LIGHTGRAY, BORDERGRAY, 2, dashed=True)
        text(d, (qx + 46, y + 12), ident, 26, GRAY, bold=True)
        text(d, (qx + 210, y + 18), why, 22, SUB)

    # ---- bottom strip
    text(d, (90, 1010), "内訳: Todo 0件 / Backlog 16件（Epic 1・着手可 7・待ち 8）/ 作業中 4件 / レビュー待ち 1件", 23, SUB)
    text(d, (90, 1052), "Epic と、親課題を持つ子課題は単体では選ばない。", 23, SUB)

    img.save(path)


def chain(path):
    W, H = 2000, 1125
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (90, 50), "出口の1件が、4件を同時に止めている", 56, INK, bold=True)
    text(d, (90, 132), "箱は課題、矢印は「終わらないと次へ進めない」の向き。点線の箱はまだ着手できない課題。", 25, SUB)

    NW, NH = 250, 96

    def node(x, y, ident, caption, style):
        if style == "review":
            box(d, x, y, NW, NH, LIGHTAMBER, AMBER, 4)
            text(d, (x + NW // 2, y + 20), ident, 30, AMBER, bold=True, anchor="ma")
            text(d, (x + NW // 2, y + 62), caption, 21, AMBER, anchor="ma")
        elif style == "ready":
            box(d, x, y, NW, NH, LIGHTGREEN, GREEN, 4)
            text(d, (x + NW // 2, y + 20), ident, 30, GREEN, bold=True, anchor="ma")
            text(d, (x + NW // 2, y + 62), caption, 21, GREEN, anchor="ma")
        else:
            box(d, x, y, NW, NH, LIGHTGRAY, BORDERGRAY, 3, dashed=True)
            text(d, (x + NW // 2, y + 20), ident, 30, GRAY, bold=True, anchor="ma")
            text(d, (x + NW // 2, y + 62), caption, 21, SUB, anchor="ma")

    # column x anchors
    c0, c1, c2, c3 = 120, 520, 920, 1320

    # row A
    node(c0, 250, "TAA-43", "Backlog・着手可", "ready")
    node(c1, 250, "TAA-45", "差分方式の比較", "blocked")
    node(c2, 250, "TAA-49", "費用の計測", "blocked")
    # row B
    node(c0, 470, "TAA-44", "In Review（PR #1）", "review")
    node(c1, 470, "TAA-46", "時系列トリガー", "blocked")
    node(c2, 470, "TAA-47", "shadow統合", "blocked")
    # row C
    node(c1, 690, "TAA-48", "判断ログ", "blocked")
    node(c3, 470, "TAA-50", "段階有効化", "blocked")

    # arrows
    arrow(d, c0 + NW, 298, c1, 298, GRAY, 5)                 # 43 -> 45
    arrow(d, c0 + NW, 518, c1, 518, AMBER, 6)                # 44 -> 46
    arrow(d, c0 + NW - 10, 500, c1 + 10, 340, AMBER, 6)      # 44 -> 45 (diagonal up)
    arrow(d, c0 + NW - 10, 540, c1 + 10, 700, AMBER, 6)      # 44 -> 48 (diagonal down)
    arrow(d, c1 + NW, 298, c2, 298, GRAY, 5)                 # 45 -> 49
    arrow(d, c1 + NW, 518, c2, 518, GRAY, 5)                 # 46 -> 47
    arrow(d, c1 + NW - 10, 330, c2 + 10, 490, GRAY, 5)       # 45 -> 47
    arrow(d, c2 + NW, 298, c3, 470, GRAY, 5)                 # 49 -> 50
    arrow(d, c2 + NW, 518, c3, 518, GRAY, 5)                 # 47 -> 50
    arrow(d, c1 + NW + 4, 738, c3 + 30, 566, GRAY, 5)        # 48 -> 50
    text(d, (c3 + NW // 2, 582), "※ TAA-35 も待つ", 21, SUB, anchor="ma")

    # annotation
    ax, ay, aw, ah = 120, 850, 1760, 190
    box(d, ax, ay, aw, ah, LIGHTBLUE, BLUE, 3)
    text(d, (ax + 30, ay + 22), "今日の1手で変わること", 28, BLUE, bold=True)
    text(d, (ax + 30, ay + 74), "TAA-44 のPRをマージする  →  TAA-46 と TAA-48 が着手できる（待ち 8件 → 6件）", 26, INK)
    text(d, (ax + 30, ay + 122), "さらに TAA-43 をTodoへ移して終える  →  TAA-45 も着手できる（待ち 6件 → 5件）", 26, INK)

    img.save(path)


if __name__ == "__main__":
    entry_map(ROOT / "entrymap.png")
    chain(ROOT / "chain.png")
    print("wrote entrymap.png, chain.png")
