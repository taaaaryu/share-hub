#!/usr/bin/env python3
"""Figures for the 2026-11-24 queue-age deck.

Public-safe aggregate data only, read on 2026-11-24 00:1x JST:
- project: 21 issues = Backlog 16 / In Progress 4 / In Review 1 / Done 0 / Todo 0.
- of the 16 Backlog issues, 8 have no unfinished blocker (6 of them High/Medium).
- 2 of the blocked 8 wait only on the single In Review issue.
- the In Review issue has been in that state since 2026-10-28 (27 days).
- the 4 In Progress issues started on 2026-11-05 (19 days).
- the 8 unblocked Backlog issues were created on 2026-10-28 (27 days).
- private repo: 8 open pull requests, all drafts, 0 merged.
  3 were created 27 days ago, 5 were created 19 days ago (176 PR-days in total).

Only counts, state names, day counts and relation shapes are drawn. No issue
identifiers, titles, bodies, comments, branch names, PR titles or customer data.
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


def arrow(d, start, end, color=GRAY, width=5):
    d.line((start, end), fill=color, width=width)
    ax, ay = end
    d.polygon([(ax, ay), (ax - 24, ay - 13), (ax - 24, ay + 13)], fill=color)


def box(d, x, y, w, h, head, value, note, fill, border, value_color=None):
    d.rounded_rectangle((x, y, x + w, y + h), 14, fill=fill, outline=border, width=3)
    text(d, (x + 26, y + 22), head, 26, SUB, True)
    text(d, (x + 26, y + 60), value, 46, value_color or INK, True)
    if note:
        text(d, (x + 26, y + 118), note, 24, SUB)


def figure_funnel():
    """Entry is empty, exit is clogged."""
    img, d = canvas("入口は0件、出口は8本", "OVERVIEW / 流れの詰まり")

    text(d, (90, 236), "課題の入口", 32, BLUE, True)
    box(d, 90, 288, 380, 160, "Backlog", "16件", "計画はあるが着手前", LIGHTGRAY, BORDERGRAY)
    box(d, 90, 480, 380, 160, "前提なし", "8件", "うちHigh/Medium 6件", LIGHTGREEN, GREEN)
    box(d, 560, 288, 380, 160, "前提あり", "8件", "未完了のblockedByが残る", LIGHTGRAY, GRAY)
    box(d, 560, 480, 380, 160, "Todo", "0件", "workerが選べる状態", LIGHTRED, RED, RED)
    arrow(d, (470, 368), (556, 368))
    arrow(d, (280, 448), (280, 476))
    arrow(d, (470, 560), (556, 560), RED)
    text(d, (604, 660), "ここで停止", 26, RED, True)

    text(d, (1090, 236), "変更の出口", 32, AMBER, True)
    box(d, 1090, 288, 380, 160, "Draft PR", "8本", "open・競合なし", LIGHTBLUE, BLUE)
    box(d, 1090, 480, 380, 160, "merge", "0本", "最長27日が経過", LIGHTRED, RED, RED)
    box(d, 1560, 288, 340, 160, "本番反映", "0件", "workerの権限外", LIGHTGRAY, BORDERGRAY)
    arrow(d, (1470, 368), (1556, 368), GRAY)
    arrow(d, (1280, 448), (1280, 476), RED)
    text(d, (1324, 660), "ここで滞留", 26, RED, True)

    d.rounded_rectangle((90, 780, 1900, 940), 14, fill=LIGHTAMBER, outline=AMBER, width=3)
    text(d, (120, 806), "選べる課題が0件のまま、レビュー待ちの変更だけが積み上がっている。", 34, AMBER, True)
    text(d, (120, 862), "8本のDraft PRのうち3本は作成から27日、5本は19日。mergeは0本。", 28, INK)

    footer(d, "読み取り: 2026-11-24 JST / 件数と状態のみ。blockedByはLinearの関係、PRは非公開リポジトリのopen件数。")
    img.save(ROOT / "funnel.png")
    print("wrote funnel.png")


def figure_aging():
    """How long each group has stayed in the same state."""
    img, d = canvas("待ち行列は4週間分", "EVIDENCE / 滞留の年齢")

    # x axis: 2026-10-28 .. 2026-11-24 = 27 days
    x_start, x_end = 430, 1310
    days_total = 27
    day_w = (x_end - x_start) / days_total

    def x_of(day):
        return x_start + day * day_w

    ticks = [(0, "10/28"), (8, "11/5"), (15, "11/12"), (22, "11/19"), (27, "11/24（今日）")]
    for day, label in ticks:
        x = x_of(day)
        d.line((x, 240, x, 700), fill="#e0e0e0", width=2)
        text(d, (x, 790), label, 24, SUB, False, "ma")

    rows = [
        ("レビュー待ち 1件", 27, AMBER, "27日", "10/28から状態が変わらない"),
        ("進行中 4件", 19, BLUE, "19日", "11/5に着手したまま"),
        ("着手可能Backlog 8件", 27, GREEN, "27日", "Todoへ移っていない"),
    ]
    for i, (label, age, color, value, note) in enumerate(rows):
        y = 292 + i * 140
        text(d, (400, y + 34), label, 28, INK, True, "ra")
        x0 = x_of(days_total - age)
        d.rounded_rectangle((x0, y, x_end, y + 66), 12, fill=color)
        text(d, (x_end + 24, y + 33), value, 34, color, True, "lm")
        text(d, (x_end + 118, y + 35), note, 24, SUB, False, "lm")

    # Done row: empty by measurement
    y = 292 + 3 * 140
    text(d, (400, y + 33), "Done", 28, INK, True, "ra")
    d.rounded_rectangle((x_start, y, x_end, y + 66), 12, fill=LIGHTRED, outline=RED, width=3)
    text(d, (x_start + 24, y + 33), "0件（4週間で完了した課題なし）", 28, RED, True, "lm")

    # summary
    blocks = [
        ("課題", "21件", "Done・Canceledは0件", INK),
        ("Todo", "0件", "workerが選べる数", RED),
        ("open PR", "8本", "すべてDraft", BLUE),
        ("合計待ち", "176 PR日", "3本×27日 + 5本×19日", AMBER),
    ]
    for i, (head, value, note, color) in enumerate(blocks):
        x = 90 + i * 470
        d.rounded_rectangle((x, 872, x + 430, 1000), 12, fill="#f4f4f4", outline=BORDERGRAY, width=2)
        text(d, (x + 26, 886), head, 26, SUB, True)
        text(d, (x + 26, 920), value, 42, color, True)
        text(d, (x + 26, 972), note, 22, SUB)

    footer(d, "読み取り: 2026-11-24 JST / 経過日数は状態に入った日からの丸め。件数・日数のみで、課題番号と本文は含まない。")
    img.save(ROOT / "aging.png")
    print("wrote aging.png")


if __name__ == "__main__":
    figure_funnel()
    figure_aging()
