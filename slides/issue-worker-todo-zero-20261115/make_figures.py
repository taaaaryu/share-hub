#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data source (public-safe aggregates only, checked 2026-11-15 14:00 JST):
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
    text(d, (70, 108), "2026-11-15 14:00 JST。Linearの対象プロジェクト21件と、private remoteのopen PR。", 20, SUB)

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
        ("#1 - #3", 3, 17.8, "10/28 作成。3本とも同じ日。"),
        ("#4 - #8", 5, 9.8, "11/05 作成。5本とも同じ週。"),
    ]
    gy = qy + 168
    for name, count, days, note in groups:
        text(d, (qx + 28, gy), name, 22, INK, bold=True)
        text(d, (qx + 130, gy - 4), f"{count}本", 22, BLUE, bold=True)
        bar_w = int(300 * days / 17.8)
        box(d, qx + 28, gy + 40, 300, 30, "#ffffff", LIGHTGRAY, 1)
        box(d, qx + 28, gy + 40, bar_w, 30, "#a6c8ff", DARKBLUE, 2)
        text(d, (qx + 28 + 300 + 14, gy + 38), f"{days}日", 24, INK, bold=True)
        text(d, (qx + 28, gy + 78), note, 17, SUB)
        gy += 150

    box(d, qx + 28, qy + 448, qw - 56, 84, "#ffffff", LIGHTGRAY, 1)
    text(d, (qx + 46, qy + 462), "最長待ち", 18, SUB)
    text(d, (qx + 46, qy + 486), "17.8 日", 34, AMBER, bold=True)
    text(d, (qx + 240, qy + 492), "review 0件 / merge 0件", 18, SUB)

    # Bottom banner
    box(d, 70, 762, 1260, 86, LIGHTRED, RED, 3)
    text(d, (96, 774), "Todo 0件", 30, RED, bold=True)
    text(d, (300, 782), "workerが今日始められる課題は0件。PRもレビュー待ちのまま増えていません。", 22, INK)

    img.save(path)


def chain(path: Path) -> None:
    W, H = 1400, 950
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (70, 44), "Backlog 16件のうち、動けるのは7件だけ", 44, INK, bold=True)
    text(d, (70, 108), "未完了の前提課題を除いた集計。Epic 1件は見出しなので、実装の単位には数えない。", 20, SUB)

    cards = [
        ("In Review の1件", "6件が待つ", "TAA-44の確認待ち。済むと一気に空く。", AMBER, LIGHTAMBER),
        ("In Progress の1件", "1件が待つ", "TAA-52が終わるのを待っている。", TEAL, LIGHTTEAL),
        ("Backlog の2件", "1件が待つ", "TAA-35 と TAA-36 が先に必要。", BLUE, PALE),
    ]
    card_y, card_h, card_w, gap = 168, 230, 400, 30
    for i, (name, count, note, color, pale) in enumerate(cards):
        x = 70 + i * (card_w + gap)
        box(d, x, card_y, card_w, card_h, pale, color, 3)
        text(d, (x + 28, card_y + 24), "待ち先", 18, SUB)
        text(d, (x + 28, card_y + 54), name, 26, INK, bold=True)
        text(d, (x + 28, card_y + 104), count, 46, color, bold=True)
        text(d, (x + 28, card_y + 174), note, 18, SUB)

    # Summary strip
    box(d, 70, 428, 1260, 84, "#fafafa", LIGHTGRAY, 2)
    text(d, (94, 446), "Backlog 16件 = 依存が空 7件 ＋ 依存待ち 8件（6＋1＋1） ＋ Epic 1件", 24, INK, bold=True)
    text(d, (94, 480), "待ちの数だけを見ると「8件」だが、止めている原因は3つに集まる。", 18, SUB)

    # Free panel
    fx, fy, fw, fh = 70, 542, 1260, 262
    box(d, fx, fy, fw, fh, LIGHTGREEN, GREEN, 3)
    text(d, (fx + 28, fy + 22), "依存が空の 7件", 26, INK, bold=True)
    text(d, (fx + 28, fy + 62), "人がTodoへ移せば、すぐ着手できる。workerは状態を変えない。", 18, SUB)
    chips = ["TAA-35", "TAA-36", "TAA-38", "TAA-39", "TAA-40", "TAA-41", "TAA-43"]
    for i, chip in enumerate(chips):
        col, row = i % 4, i // 4
        x = fx + 28 + col * 180
        y = fy + 108 + row * 66
        box(d, x, y, 160, 50, "#ffffff", GREEN, 2)
        text(d, (x + 80, y + 25), chip, 20, GREEN, bold=True, anchor="mm")

    box(d, 70, 858, 1260, 64, LIGHTAMBER, AMBER, 2)
    text(d, (94, 872), "移す順番を決めるのは人。workerはBacklogもレビューも動かさない。", 22, INK, bold=True)

    img.save(path)


if __name__ == "__main__":
    queue(ROOT / "queue.png")
    chain(ROOT / "chain.png")
    print("wrote queue.png and chain.png")
