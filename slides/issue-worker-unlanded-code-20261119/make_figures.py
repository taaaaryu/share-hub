#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data source (public-safe aggregates only, checked 2026-11-19 JST):
- Linear project f7f3a327 (TAA): 21 issues. Backlog 16, In Progress 4,
  In Review 1, Todo 0.
- private remote taaaaryu/thumaster: 8 open Pull Requests, all draft,
  all mergeable=clean, 0 review comments, 0 approvals.
- Per-PR additions / changed_files / created_at from the GitHub API.
- blockedBy / blocks read from Linear (TAA-44 -> 45,46,48,49).

Issue titles, bodies, comments and customer data are not drawn. Only
identifiers, category words, status names and measured counts.
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
TEAL = "#005d5d"
LIGHTTEAL = "#d9fbfb"


def font(size, bold=False):
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def box(draw, x, y, w, h, fill, border, width=3, radius=8, dashed=False):
    if not dashed:
        draw.rounded_rectangle((x, y, x + w, y + h), radius=radius,
                               fill=fill, outline=border, width=width)
        return
    draw.rectangle((x, y, x + w, y + h), fill=fill)

    def dash_line(x1, y1, x2, y2):
        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        if not length:
            return
        ux, uy = (x2 - x1) / length, (y2 - y1) / length
        pos = 0
        while pos < length:
            end = min(pos + 8, length)
            draw.line((x1 + ux * pos, y1 + uy * pos, x1 + ux * end, y1 + uy * end),
                      fill=border, width=width)
            pos += 16

    dash_line(x, y, x + w, y)
    dash_line(x + w, y, x + w, y + h)
    dash_line(x + w, y + h, x, y + h)
    dash_line(x, y + h, x, y)


def arrow(draw, x1, y1, x2, y2, color=GRAY, width=5, dashed=False):
    if dashed:
        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        ux, uy = (x2 - x1) / length, (y2 - y1) / length
        pos = 0
        while pos < length - 16:
            end = min(pos + 10, length - 16)
            draw.line((x1 + ux * pos, y1 + uy * pos, x1 + ux * end, y1 + uy * end),
                      fill=color, width=width)
            pos += 20
    else:
        draw.line((x1, y1, x2, y2), fill=color, width=width)
    head = 11
    draw.polygon([(x2, y2), (x2 - head, y2 - head), (x2 - head, y2 + head)], fill=color)


# number, 変更先, additions, days waiting, kind
PRS = [
    ("PR #3", "ダッシュボード", 6359, 22, "devex"),
    ("PR #2", "issue worker", 2237, 22, "devex"),
    ("PR #1", "HUD変化検出", 1317, 22, "product"),
    ("PR #7", "スマホ管理", 939, 14, "devex"),
    ("PR #5", "検証ハーネス", 718, 14, "harness"),
    ("PR #8", "利用枠の自動停止", 615, 14, "devex"),
    ("PR #4", "HP読み取り修正", 521, 14, "product"),
    ("PR #6", "オーケストレーター", 155, 14, "devex"),
]

STYLE = {
    "product": (BLUE, LIGHTBLUE),
    "harness": (TEAL, LIGHTTEAL),
    "devex": (GRAY, LIGHTGRAY),
}


def pr_ledger(path):
    W, H = 2000, 1125
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (90, 44), "未mergeのDraft PRに、12,861行が載っている", 58, INK, bold=True)
    text(d, (90, 126), "private remoteのopen PR 8本。棒の長さは追加行数、右端は作成からの経過日数。2026-11-19 JST。", 24, SUB)

    text(d, (96, 190), "PR / 変更先", 21, SUB, bold=True)
    text(d, (760, 190), "追加行数", 21, SUB, bold=True)
    text(d, (1660, 190), "作成からの経過", 21, SUB, bold=True)

    x0, bar_x, bar_max = 90, 700, 720
    scale = bar_max / 6359
    for i, (pr, where, adds, days, kind) in enumerate(PRS):
        y = 228 + i * 91
        main, light = STYLE[kind]
        box(d, x0, y, 1820, 78, "#ffffff", "#e0e0e0", 2, radius=6)
        box(d, x0, y, 8, 78, main, main, 0, radius=0)
        text(d, (x0 + 30, y + 12), pr, 27, INK, bold=True)
        text(d, (x0 + 30, y + 48), where, 20, SUB)
        d.rounded_rectangle((bar_x, y + 26, bar_x + max(6, adds * scale), y + 52),
                            radius=4, fill=main)
        text(d, (bar_x + max(6, adds * scale) + 18, y + 26), f"{adds:,} 行", 24, INK)
        if days >= 14:
            d.rounded_rectangle((1690, y + 20, 1810, y + 58), radius=18,
                                fill=LIGHTAMBER, outline=AMBER, width=2)
            text(d, (1750, y + 39), f"{days}日", 24, AMBER, bold=True, anchor="mm")
        else:
            text(d, (1750, y + 39), f"{days}日", 24, SUB, anchor="mm")

    legend_y = 984
    for label, kind, lx in (("製品の解析コード 2本", "product", 90),
                            ("解析の検証基盤 1本", "harness", 470),
                            ("開発基盤（worker/ダッシュボード）5本", "devex", 810)):
        main, _ = STYLE[kind]
        d.rounded_rectangle((lx, legend_y + 6, lx + 26, legend_y + 26), radius=4, fill=main)
        text(d, (lx + 38, legend_y), label, 22, SUB)

    text(d, (90, 1030), "合計 追加12,861行 / 削除246行 / 変更108ファイル。8本すべて mergeable=clean、レビューコメント0件・承認0件。", 24, INK)
    text(d, (90, 1068), "PR #6→#7→#8 は積み上げ。#7の土台が#6、#8の土台が#7なので、下から順にmergeする。", 22, SUB)

    img.save(path)


def node(d, x, y, w, h, ident, caption, style, dashed=False):
    main, light = STYLE[style]
    box(d, x, y, w, h, light, main, 4, dashed=dashed)
    text(d, (x + 20, y + 14), ident, 27, main, bold=True)
    text(d, (x + 20, y + h - 32), caption, 20, main)


def small(d, x, y, w, h, label, caption, dashed=True):
    box(d, x, y, w, h, "#ffffff", GREEN if not dashed else GRAY, 3, radius=6, dashed=dashed)
    text(d, (x + 16, y + 10), label, 24, GREEN if not dashed else SUB, bold=not dashed)
    text(d, (x + 16, y + 42), caption, 18, SUB)


def review_order(path):
    W, H = 2000, 1125
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (90, 40), "レビューは1本目から。順番に理由がある", 58, INK, bold=True)
    text(d, (90, 120), "矢印は「先に入れると次へ進める」の向き。点線は、いまはまだ着手できない課題。", 24, SUB)

    lane_x, lane_w = 90, 1820

    # Lane A
    y = 176
    box(d, lane_x, y, lane_w, 236, "#fafafa", "#e0e0e0", 2, radius=6)
    text(d, (lane_x + 26, y + 18), "A", 30, BLUE, bold=True)
    text(d, (lane_x + 62, y + 22), "まず #1（製品の解析コード）", 26, BLUE, bold=True)
    text(d, (lane_x + 620, y + 26), "4件が同時に解禁される（依存関係からの予測）", 20, SUB)
    node(d, 250, y + 76, 250, 96, "PR #1", "HUD変化検出 1,317行", "product")
    arrow(d, 510, y + 124, 586, y + 124)
    box(d, 596, y + 76, 172, 96, "#ffffff", BLUE, 3)
    text(d, (682, y + 96), "TAA-44", 26, BLUE, bold=True, anchor="ma")
    text(d, (682, y + 136), "完了へ", 20, SUB, anchor="ma")
    arrow(d, 778, y + 124, 846, y + 124, color=GREEN, width=6)
    for i, ident in enumerate(["TAA-45", "TAA-46", "TAA-48", "TAA-49"]):
        small(d, 860 + i * 248, y + 92, 228, 74, ident, "いまは着手できない")

    # Lane B
    y = 436
    box(d, lane_x, y, lane_w, 200, "#fafafa", "#e0e0e0", 2, radius=6)
    text(d, (lane_x + 26, y + 18), "B", 30, SUB, bold=True)
    text(d, (lane_x + 62, y + 22), "次に #4 と #5", 26, INK, bold=True)
    node(d, 250, y + 66, 250, 92, "PR #4", "HP読み取り 521行", "product")
    arrow(d, 510, y + 112, 566, y + 112)
    small(d, 576, y + 75, 190, 74, "TAA-33", "HP読み取りの課題")
    node(d, 850, y + 66, 250, 92, "PR #5", "検証ハーネス 718行", "harness")
    arrow(d, 1110, y + 112, 1166, y + 112)
    small(d, 1176, y + 75, 190, 74, "TAA-53", "固定フレームで検証")
    text(d, (1420, y + 76), "#5は解析の道具。製品の出力そのものは", 20, SUB)
    text(d, (1420, y + 106), "変えないので、影響範囲が読みやすい。", 20, SUB)

    # Lane C
    y = 664
    box(d, lane_x, y, lane_w, 250, "#fafafa", "#e0e0e0", 2, radius=6)
    text(d, (lane_x + 26, y + 18), "C", 30, SUB, bold=True)
    text(d, (lane_x + 62, y + 22), "最後に #6 → #7 → #8（この順）", 26, INK, bold=True)
    text(d, (lane_x + 780, y + 26), "積み上げ。#7の土台が#6、#8の土台が#7。", 20, AMBER)
    node(d, 250, y + 92, 240, 100, "PR #6", "worker改修 155行", "devex")
    arrow(d, 500, y + 142, 566, y + 142, color=AMBER, width=6)
    node(d, 576, y + 92, 240, 100, "PR #7", "スマホ管理 939行", "devex")
    arrow(d, 826, y + 142, 892, y + 142, color=AMBER, width=6)
    node(d, 902, y + 92, 240, 100, "PR #8", "利用枠停止 615行", "devex")
    text(d, (1200, y + 96), "下から順にmergeしないと、上の差分に", 20, SUB)
    text(d, (1200, y + 126), "下の未merge分が混ざって読めなくなる。", 20, SUB)
    text(d, (1200, y + 170), "#2（worker）と #3（ダッシュボード）は main 起点で独立。", 20, SUB)

    text(d, (90, 958), "8本の内訳: 製品の解析コード 2本 / 解析の検証基盤 1本 / 開発基盤 5本。レビューコメントは全8本で0件。", 24, INK)
    text(d, (90, 1000), "行数の合計は 12,861行（追加）、246行（削除）。最古は10月28日作成の3本で、今日で22日。", 22, SUB)
    text(d, (90, 1042), "merge後に何件動くかは、LinearのblockedByから数えた予測であり、まだ実測していない。", 22, SUB)

    img.save(path)


if __name__ == "__main__":
    pr_ledger(ROOT / "pr-ledger.png")
    review_order(ROOT / "review-order.png")
    print("generated")
