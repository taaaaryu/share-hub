#!/usr/bin/env python3
"""Figures for the 2026-11-23 review-pile deck.

Public-safe aggregate data only, read on 2026-11-23 00:11 JST:
- project: 21 issues = Backlog 16 / In Progress 4 / In Review 1 / Todo 0.
- of the 16 Backlog issues, 8 have no unfinished blocker (5 of them High/Medium).
- 8 of the 16 are blocked; 4 of those wait on the single In Review issue.
- no issue was updated within the last 24 hours (latest update 5 days ago).
- private repo: 8 open pull requests, all drafts, 0 merged.
  3 were created 26 days ago, 5 were created 18 days ago (168 PR-days in total).

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
    d.polygon(
        [(ax, ay), (ax - 24, ay - 13), (ax - 24, ay + 13)],
        fill=color,
    )


def figure_state():
    """21 issue cells split by state, with the Backlog cells split by blocker."""
    img, d = canvas("21件のうちTodoは0件", "EVIDENCE / 状態の内訳")

    cell, gap = 92, 12
    x0, y0 = 100, 250
    # 8 ready backlog, 8 blocked backlog, 4 in progress, 1 in review
    fills = [(LIGHTGREEN, GREEN)] * 8 + [(LIGHTGRAY, GRAY)] * 8
    fills += [(BLUE, BLUE)] * 4 + [("#ffd7a8", AMBER)]

    for i, (fill, border) in enumerate(fills):
        r, c = divmod(i, 7)
        x = x0 + c * (cell + gap)
        y = y0 + r * (cell + gap)
        d.rounded_rectangle((x, y, x + cell, y + cell), 10, fill=fill, outline=border, width=3)
    # stripe the blocked cells so the split is visible without colour alone
    for i in range(8, 16):
        r, c = divmod(i, 7)
        x = x0 + c * (cell + gap)
        y = y0 + r * (cell + gap)
        for k in range(6, cell - 6, 16):
            d.line((x + k, y + cell - 8, x + cell - 8, y + k), fill=GRAY, width=3)

    legend = [
        ("前提なし 8", LIGHTGREEN, GREEN),
        ("前提あり 8", LIGHTGRAY, GRAY),
        ("進行中 4", BLUE, BLUE),
        ("レビュー待ち 1", "#ffd7a8", AMBER),
    ]
    for i, (label, fill, border) in enumerate(legend):
        x = 100 + i * 250
        d.rounded_rectangle((x, 596, x + 26, 622), 6, fill=fill, outline=border, width=2)
        text(d, (x + 38, 597), label, 26, SUB)

    # Todo has no cell, because no issue is in that state
    d.rounded_rectangle((100, 664, 470, 760), 12, fill=LIGHTRED, outline=RED, width=3)
    text(d, (124, 680), "Todo", 30, RED, True)
    text(d, (124, 720), "該当する課題なし（0件）", 26, RED)

    text(d, (100, 806), "最終更新からの経過", 28, SUB, True)
    text(d, (100, 848), "21件すべてが5日以上前。24時間以内の更新は0件。", 28, INK)

    # right panel: horizontal bars, split backlog
    text(d, (1090, 236), "状態ごとの件数", 30, SUB, True)
    rows = [
        ("Backlog（前提なし）", 8, LIGHTGREEN, GREEN, 260),
        ("Backlog（前提あり）", 8, LIGHTGRAY, GRAY, 260),
        ("進行中", 4, BLUE, BLUE, 130),
        ("レビュー待ち", 1, "#ffd7a8", AMBER, 33),
    ]
    for i, (label, count, fill, border, width) in enumerate(rows):
        y = 300 + i * 118
        text(d, (1300, y + 26), label, 28, INK, False, "rm")
        d.rounded_rectangle((1320, y, 1320 + width, y + 52), 8, fill=fill, outline=border, width=3)
        text(d, (1320 + width + 22, y + 26), f"{count}件", 30, INK, True, "lm")

    y = 300 + 4 * 118
    text(d, (1300, y + 26), "Todo", 28, INK, False, "rm")
    d.rounded_rectangle((1320, y, 1320 + 110, y + 52), 8, fill=LIGHTRED, outline=RED, width=3)
    text(d, (1320 + 132, y + 26), "0件", 30, RED, True, "lm")

    d.line((1090, 900, 1900, 900), fill=BORDERGRAY, width=2)
    text(d, (1090, 920), "進行中4件は17日前、レビュー待ち1件は25日前から同じ状態。", 26, SUB)

    footer(d, "読み取り: 2026-11-23 00:11 JST / 課題21件。件数と状態のみで、課題番号・本文は含まない。")
    img.save(ROOT / "state_breakdown.png")
    print("wrote state_breakdown.png")


def figure_pr_aging():
    """Eight open drafts as bars from creation date to today."""
    img, d = canvas("open PR 8本、mergeは0本", "EVIDENCE / 出口の滞留")

    # x axis: 2026-10-28 .. 2026-11-23 = 26 days
    x_start, x_end = 380, 1660
    days_total = 26
    day_w = (x_end - x_start) / days_total

    def x_of(day):
        return x_start + day * day_w

    # axis ticks
    ticks = [(0, "10/28"), (8, "11/5"), (15, "11/12"), (22, "11/19"), (26, "11/23（今日）")]
    for day, label in ticks:
        x = x_of(day)
        d.line((x, 232, x, 800), fill="#e0e0e0", width=2)
        text(d, (x, 812), label, 24, SUB, False, "ma")

    text(d, (90, 236), "PR", 28, SUB, True)
    text(d, (200, 236), "作成日 → 今日", 24, SUB)

    # 3 drafts at 26 days, 5 drafts at 18 days
    rows = [(26, 0, AMBER, "26日")] * 3 + [(18, 0, BLUE, "18日")] * 5
    bar_h = 44
    for i, (age, _, color, label) in enumerate(rows):
        y = 288 + i * 62
        x0 = x_of(days_total - age)
        d.rounded_rectangle((x0, y, x_end, y + bar_h), 10, fill=color)
        text(d, (x_end + 24, y + bar_h / 2), label, 30, color, True, "lm")

    d.line((x_end, 260, x_end, 800), fill=INK, width=4)

    # summary blocks
    blocks = [
        ("open PR", "8本", "すべてDraft", BLUE),
        ("merge済み", "0本", "リポジトリ全体", RED),
        ("最長待ち", "26日", "3本が該当", AMBER),
        ("合計待ち", "168 PR日", "8本の合計", INK),
    ]
    for i, (head, value, note, color) in enumerate(blocks):
        x = 90 + i * 470
        d.rounded_rectangle((x, 862, x + 430, 1000), 12, fill="#f4f4f4", outline=BORDERGRAY, width=2)
        text(d, (x + 26, 878), head, 26, SUB, True)
        text(d, (x + 26, 914), value, 44, color, True)
        text(d, (x + 26, 968), note, 24, SUB)

    footer(d, "読み取り: 2026-11-23 00:11 JST / 非公開リポジトリのopen PR。件数・日数のみで、PR名とbranch名は含まない。")
    img.save(ROOT / "pr_aging.png")
    print("wrote pr_aging.png")


def figure_funnel():
    """Entry is empty, exit is clogged."""
    img, d = canvas("入口は空、出口は詰まる", "OVERVIEW / 流れの詰まり")

    def box(x, y, w, h, head, value, note, fill, border, value_color=None):
        d.rounded_rectangle((x, y, x + w, y + h), 14, fill=fill, outline=border, width=3)
        text(d, (x + 26, y + 22), head, 26, SUB, True)
        text(d, (x + 26, y + 62), value, 46, value_color or INK, True)
        if note:
            text(d, (x + 26, y + 120), note, 24, SUB)

    # entry column
    text(d, (90, 236), "課題の入口", 32, BLUE, True)
    box(90, 288, 380, 160, "Backlog", "16件", "計画はあるが着手前", LIGHTGRAY, BORDERGRAY)
    box(90, 480, 380, 160, "前提なし", "8件", "うちHigh/Medium 5件", LIGHTGREEN, GREEN)
    box(560, 288, 380, 160, "前提あり", "8件", "未完了のblockedByが残る", LIGHTGRAY, GRAY)
    box(560, 480, 380, 160, "Todo", "0件", "workerが選べる状態", LIGHTRED, RED, RED)
    arrow(d, (470, 368), (556, 368))
    arrow(d, (280, 448), (280, 476))
    arrow(d, (470, 560), (556, 560), RED)
    text(d, (600, 660), "ここで停止", 26, RED, True)

    # exit column
    text(d, (1090, 236), "変更の出口", 32, AMBER, True)
    box(1090, 288, 380, 160, "Draft PR", "8本", "open・競合なし", LIGHTBLUE, BLUE)
    box(1090, 480, 380, 160, "merge", "0本", "26日と18日が経過", LIGHTRED, RED, RED)
    box(1560, 288, 340, 160, "本番反映", "0件", "workerの権限外", LIGHTGRAY, BORDERGRAY)
    arrow(d, (1470, 368), (1556, 368), GRAY)
    arrow(d, (1280, 448), (1280, 476), RED)
    text(d, (1320, 660), "ここで滞留", 26, RED, True)

    # centre message
    d.rounded_rectangle((90, 780, 1900, 940), 14, fill=LIGHTAMBER, outline=AMBER, width=3)
    text(d, (120, 806), "選べる課題が0件のまま、レビュー待ちの変更だけが積み上がっている。", 34, AMBER, True)
    text(d, (120, 862), "24時間で状態が変わった課題は0件。workerは次回も同じ場所で止まる。", 28, INK)

    footer(d, "読み取り: 2026-11-23 00:11 JST / 件数と状態のみ。blockedByはLinearの関係、PRは非公開リポジトリのopen件数。")
    img.save(ROOT / "funnel.png")
    print("wrote funnel.png")


if __name__ == "__main__":
    figure_state()
    figure_pr_aging()
    figure_funnel()
