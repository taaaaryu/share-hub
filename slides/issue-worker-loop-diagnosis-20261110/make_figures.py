#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data sources (public-safe aggregates only):
- state/logs/once-*.log file names in the issue-worker state directory (run counts per day)
- open draft PR list from the private repo (numbers and dates only)
- Linear issue status counts for the target project (counts only, no issue bodies)
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
GRAY = "#a8a8a8"
RED = "#da1e28"

DAYS = [
    ("10/29", 10), ("10/30", 5), ("10/31", 5), ("11/1", 5),
    ("11/2", 5), ("11/3", 5), ("11/4", 5), ("11/5", 5),
    ("11/6", 5), ("11/7", 5), ("11/8", 5), ("11/9", 2),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def box(draw, xy, fill=None, outline=None, width=2, radius=12):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def timeline(path: Path) -> None:
    W, H = 2000, 1125
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    text(d, (110, 62), "12日間で62回動いて、Doneは0件", 54, INK, bold=True)

    # legend
    ly = 168
    d.rectangle((110, ly - 18, 138, ly + 10), fill=BLUE)
    text(d, (154, ly - 20), "その日の実行回数", 26, SUB)
    d.line((470, ly - 4, 520, ly - 4), fill=PURPLE, width=6)
    text(d, (534, ly - 20), "オープンな草案PRの累計", 26, SUB)
    d.line((870, ly - 4, 920, ly - 4), fill=RED, width=5)
    text(d, (934, ly - 20), "完了（Done）した課題数", 26, SUB)

    x0, x1 = 150, 1860
    slot = (x1 - x0) / len(DAYS)

    # ---- panel A: runs per day
    a_base, a_top, a_max = 640, 250, 12
    text(d, (x0, 218), "実行回数（1日あたり）", 28, SUB, bold=True)
    for value in (0, 5, 10):
        y = a_base - (a_base - a_top) * value / a_max
        d.line((x0, y, x1, y), fill=LINE, width=2)
        text(d, (x0 - 24, y), str(value), 22, SUB, anchor="rm")
    for i, (_, runs) in enumerate(DAYS):
        cx = x0 + slot * i + slot / 2
        bh = (a_base - a_top) * runs / a_max
        d.rectangle((cx - slot * 0.28, a_base - bh, cx + slot * 0.28, a_base), fill=BLUE)
        text(d, (cx, a_base - bh - 14), str(runs), 24, INK, bold=True, anchor="mb")

    # ---- panel B: cumulative PRs and Done
    b_base, b_top, b_max = 960, 720, 10
    text(d, (x0, 690), "累計件数", 28, SUB, bold=True)
    for value in (0, 5, 10):
        y = b_base - (b_base - b_top) * value / b_max
        d.line((x0, y, x1, y), fill=LINE, width=2)
        text(d, (x0 - 24, y), str(value), 22, SUB, anchor="rm")

    def y_of(value: int) -> float:
        return b_base - (b_base - b_top) * value / b_max

    # step: 3 until 11/4, then 8
    step_x = [x0 + slot * 0 + slot / 2, x0 + slot * 7 + slot / 2]
    d.line((step_x[0], y_of(3), step_x[1], y_of(3)), fill=PURPLE, width=6)
    d.line((step_x[1], y_of(3), step_x[1], y_of(8)), fill=PURPLE, width=6)
    d.line((step_x[1], y_of(8), x1, y_of(8)), fill=PURPLE, width=6)
    for cx, val in ((step_x[0], 3), (step_x[1], 8)):
        d.ellipse((cx - 10, y_of(val) - 10, cx + 10, y_of(val) + 10), fill=PURPLE)
    text(d, (step_x[0] + 18, y_of(3) - 44), "3件（10/28に作成）", 24, PURPLE, bold=True)
    text(d, (x1, y_of(8) - 22), "8件（すべて確認待ち）", 24, PURPLE, bold=True, anchor="rb")

    # done flat at zero
    d.line((x0, y_of(0), x1, y_of(0)), fill=RED, width=5)
    text(d, (x1, y_of(0) - 18), "0件（10/28以降ずっと）", 24, RED, bold=True, anchor="rb")

    # x labels
    for i, (label, _) in enumerate(DAYS):
        cx = x0 + slot * i + slot / 2
        text(d, (cx, b_base + 18), label, 24, SUB, anchor="ma")

    text(d, (110, 1030), "毎日5回前後は動いています。それでも完了した課題は0件で、草案PRは8件のまま増え続けています。",
         30, INK)
    text(d, (110, 1078), "出典: 実行ログ62件のファイル名・private repoの草案PR一覧・Linear対象projectの状態（集計値のみ）",
         22, SUB)
    img.save(path)


def gates(path: Path) -> None:
    W, H = 2000, 1040
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    text(d, (110, 62), "詰まっているのは2か所：入口と出口", 54, INK, bold=True)
    text(d, (110, 142), "入口＝Todoが0件でworkerが選べない / 出口＝草案PR8件が未レビューでDoneにならない",
         28, SUB)

    card_w, gap = 420, 90
    text(d, (110, 216), "入口：課題の供給", 34, BLUE, bold=True)
    entry = [("計画", "16", GRAY, "Backlog"), ("前提なし", "8", BLUE, "すぐ着手できる"),
             ("Todo", "0", RED, "workerが選べる唯一")]
    x = 110
    for label, value, color, note in entry:
        box(d, (x, 262, x + card_w, 552), fill=PANEL)
        text(d, (x + 34, 298), label, 30, SUB, bold=True)
        text(d, (x + 34, 356), value, 112, color, bold=True)
        text(d, (x + 34, 496), note, 24, SUB)
        if label != "Todo":
            text(d, (x + card_w + 18, 386), "→", 52, SUB, bold=True)
        x += card_w + gap

    text(d, (110, 626), "出口：レビューと取り込み", 34, PURPLE, bold=True)
    exit_ = [("草案PR", "8", PURPLE, "10/28-11/05に作成"), ("レビュー済", "0", RED, "未着手"),
             ("Done", "0", RED, "未着手")]
    x = 110
    for label, value, color, note in exit_:
        box(d, (x, 672, x + card_w, 962), fill=PANEL)
        text(d, (x + 34, 708), label, 30, SUB, bold=True)
        text(d, (x + 34, 766), value, 108, color, bold=True)
        text(d, (x + 34, 906), note, 24, SUB)
        if label != "Done":
            text(d, (x + card_w + 18, 796), "→", 52, SUB, bold=True)
        x += card_w + gap

    # summary panel on the right
    px0, px1 = 1600, 1890
    box(d, (px0, 262, px1, 962), fill="#edf5ff", outline=BLUE, width=3)
    text(d, (px0 + 26, 296), "この12日間で", 24, SUB, bold=True)
    rows = [("62", "回の実行", BLUE), ("13", "枚の停止資料", RED), ("0", "件の完了", RED)]
    y = 344
    for value, label, color in rows:
        text(d, (px0 + 26, y), value, 72, color, bold=True)
        text(d, (px0 + 26, y + 86), label, 22, SUB)
        y += 176
    text(d, (px0 + 26, 886), "資料は増えるが、", 22, INK)
    text(d, (px0 + 26, 916), "課題は減らない。", 22, INK)

    text(d, (110, 986), "出典: Linear対象project 21件の状態とblockedBy、private repoの草案PR一覧、share-hubの公開資料一覧（集計値のみ）",
         22, SUB)
    img.save(path)


if __name__ == "__main__":
    timeline(ROOT / "timeline.png")
    gates(ROOT / "gates.png")
    print("generated")
