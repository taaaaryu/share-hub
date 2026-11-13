#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data source (public-safe aggregates only, checked 2026-11-14 01:29 JST):
- Linear project f7f3a327-a06b-478f-bd88-c49fc2b79cef: 21 issues, status counts,
  and blockedBy relations between Backlog issues.
- private remote thumaster: 8 open Draft PRs, creation dates only.

Issue titles, bodies, comments, assignees, branch names, code and customer data
do not appear in the images. Only counts, state names and the shape of the
dependency graph are drawn.
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
TEAL = "#007d79"
LIGHTTEAL = "#d9fbfb"
GREEN = "#198038"
LIGHTGREEN = "#defbe6"
AMBER = "#8a3800"
LIGHTAMBER = "#fff2e8"
GRAY = "#6f6f6f"
LIGHTGRAY = "#e0e0e0"
RED = "#da1e28"
LIGHTRED = "#fff1f1"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def box(draw, x, y, w, h, fill, border, width=2):
    draw.rectangle((x, y, x + w, y + h), fill=fill, outline=border, width=width)


def queue(path: Path) -> None:
    W, H = 1400, 900
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (70, 44), "着手できる課題0件、出したままのPR 8本", 44, INK, bold=True)
    text(d, (70, 108), "2026-11-14 01:29 JST。Linearの対象プロジェクト21件と、private remoteのopen PR。", 20, SUB)

    # Left: issue inventory
    px, py, pw, ph = 70, 170, 640, 560
    box(d, px, py, pw, ph, "#fafafa", LIGHTGRAY, 2)
    text(d, (px + 28, py + 22), "課題21件の状態", 26, INK, bold=True)
    text(d, (px + 28, py + 64), "1本＝課題の件数。Todoだけがworkerの作業台。", 18, SUB)

    rows = [
        ("Backlog", 16, GRAY, "#f4f4f4", "計画の置き場。実装対象ではない"),
        ("In Progress", 4, BLUE, PALE, "すでに着手済み"),
        ("In Review", 1, AMBER, LIGHTAMBER, "人の確認待ち"),
        ("Todo", 0, RED, LIGHTRED, "着手してよい唯一の状態"),
        ("Done", 0, GREEN, LIGHTGREEN, "完了"),
    ]
    top, row_h = py + 108, 82
    bar_x, bar_max = px + 190, 330
    for i, (name, count, color, pale, note) in enumerate(rows):
        y = top + i * row_h
        text(d, (px + 28, y + 2), name, 21, INK, bold=True)
        w = 0 if count == 0 else max(int(bar_max * count / 16), 12)
        box(d, bar_x, y, bar_max, 34, "#f4f4f4", LIGHTGRAY, 1)
        if count:
            box(d, bar_x, y, w, 34, pale, color, 2)
        text(d, (bar_x + bar_max + 16, y - 4), f"{count}件", 26, color if count else GRAY, bold=True)
        text(d, (px + 28, y + 38), note, 16, SUB)

    # Right: PR queue
    qx, qy, qw, qh = 750, 170, 580, 560
    box(d, qx, qy, qw, qh, PALE, BLUE, 2)
    text(d, (qx + 28, qy + 22), "open の Draft PR 8本", 26, INK, bold=True)
    text(d, (qx + 28, qy + 64), "すべて下書きのまま。レビューは0件。", 18, SUB)

    text(d, (qx + 28, qy + 118), "作成からの経過", 20, SUB, bold=True)
    groups = [
        ("#1 - #3", 3, 16.2, "10/28 作成。3本とも同じ日。"),
        ("#4 - #8", 5, 8.2, "11/05 作成。5本とも同じ週。"),
    ]
    gy = qy + 168
    for name, count, days, note in groups:
        text(d, (qx + 28, gy), name, 22, INK, bold=True)
        text(d, (qx + 130, gy - 4), f"{count}本", 22, BLUE, bold=True)
        bar_w = int(300 * days / 16.2)
        box(d, qx + 28, gy + 40, 300, 30, "#ffffff", LIGHTGRAY, 1)
        box(d, qx + 28, gy + 40, bar_w, 30, "#a6c8ff", DARKBLUE, 2)
        text(d, (qx + 28 + 300 + 14, gy + 38), f"{days}日", 24, INK, bold=True)
        text(d, (qx + 28, gy + 78), note, 17, SUB)
        gy += 150

    box(d, qx + 28, qy + 448, qw - 56, 84, "#ffffff", LIGHTGRAY, 1)
    text(d, (qx + 46, qy + 462), "最長待ち", 18, SUB)
    text(d, (qx + 46, qy + 486), "16.2 日", 34, AMBER, bold=True)
    text(d, (qx + 220, qy + 492), "review 0件 / merge 0件", 18, SUB)

    # Bottom banner
    box(d, 70, 762, 1260, 86, LIGHTRED, RED, 3)
    text(d, (96, 774), "Todo 0件", 30, RED, bold=True)
    text(d, (300, 782), "workerが今日始められる課題は0件。PRもレビュー待ちのまま増えていません。", 22, INK)

    img.save(path)


def readiness(path: Path) -> None:
    W, H = 1400, 950
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (70, 44), "Backlog 16件は、すぐ動かせる7件と待ち8件", 44, INK, bold=True)
    text(d, (70, 108), "未完了の前提課題を除いた集計。Epic 1件は見出しなので、実装の単位には数えない。", 20, SUB)

    cards = [
        ("依存が空", "7件", "人がTodoへ移せば、すぐ着手できる。", GREEN, LIGHTGREEN),
        ("依存待ち", "8件", "未完了の前提課題がある。", AMBER, LIGHTAMBER),
        ("Epic", "1件", "複数をまとめる見出し。単体では数えない。", GRAY, "#f4f4f4"),
    ]
    card_y, card_h, card_w, gap = 168, 206, 400, 30
    for i, (name, count, note, color, pale) in enumerate(cards):
        x = 70 + i * (card_w + gap)
        box(d, x, card_y, card_w, card_h, pale, color, 3)
        text(d, (x + 28, card_y + 26), name, 24, color, bold=True)
        text(d, (x + 28, card_y + 68), count, 56, INK, bold=True)
        text(d, (x + 28, card_y + 148), note, 18, SUB)

    # 16-cell strip
    strip_y, cell_w, cell_h, cell_gap = 418, 64, 64, 12
    start_x = 70
    order = [(GREEN, LIGHTGREEN)] * 7 + [(AMBER, LIGHTAMBER)] * 8 + [(GRAY, "#f4f4f4")]
    for i, (color, pale) in enumerate(order):
        x = start_x + i * (cell_w + cell_gap)
        box(d, x, strip_y, cell_w, cell_h, pale, color, 2)
    text(d, (start_x, strip_y + 84), "16件を1マス1件で並べた図。緑＝依存が空、橙＝依存待ち、灰＝Epic。", 18, SUB)

    # Blocked breakdown
    bx, by, bw, bh = 70, 580, 700, 250
    box(d, bx, by, bw, bh, "#fafafa", LIGHTGRAY, 2)
    text(d, (bx + 26, by + 20), "待ち8件の内訳", 24, INK, bold=True)
    rows = [
        ("In Review 1件から連鎖", 6, AMBER),
        ("In Progress 1件待ち", 1, TEAL),
        ("Backlog 2件待ち", 1, BLUE),
    ]
    top, row_h = by + 72, 56
    for i, (name, count, color) in enumerate(rows):
        y = top + i * row_h
        text(d, (bx + 26, y), name, 20, INK)
        bar_w = max(int(260 * count / 6), 8)
        box(d, bx + 380, y + 2, bar_w, 28, color, color, 1)
        text(d, (bx + 380 + bar_w + 12, y - 2), f"{count}件", 24, INK, bold=True)

    # Candidate chips
    cx, cy, cw, chh = 810, 580, 520, 250
    box(d, cx, cy, cw, chh, PALE, BLUE, 2)
    text(d, (cx + 26, cy + 20), "すぐTodoへ移せる7件", 24, INK, bold=True)
    text(d, (cx + 26, cy + 60), "依存が空のBacklog。番号だけを示す。", 17, SUB)
    chips = ["TAA-35", "TAA-36", "TAA-38", "TAA-39", "TAA-40", "TAA-41", "TAA-43"]
    for i, chip in enumerate(chips):
        row, col = divmod(i, 3)
        x = cx + 26 + col * 160
        y = cy + 108 + row * 52
        box(d, x, y, 140, 40, "#ffffff", BLUE, 2)
        text(d, (x + 70, y + 20), chip, 18, DARKBLUE, bold=True, anchor="mm")

    box(d, 70, 858, 1260, 64, LIGHTGREEN, GREEN, 2)
    text(d, (94, 872), "ただし、Todoへ移すのは人の判断。workerはBacklogの状態を変えない。", 22, INK, bold=True)

    img.save(path)


if __name__ == "__main__":
    queue(ROOT / "queue.png")
    readiness(ROOT / "readiness.png")
    print("wrote queue.png and readiness.png")
