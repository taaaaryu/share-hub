#!/usr/bin/env python3
"""Figures for the 2026-11-21 second idle-run deck.

Public-safe data only (read 2026-11-21 JST from the private Linear project and
the local worker state directory):
- 21 issues: Backlog 16 / Todo 0 / In Progress 4 / In Review 1 / Done 0.
- 8 open pull requests, all drafts, 0 merged.
- 2 of the 6 daily worker runs used; 0 code changes, 0 new PRs, 0 Linear updates.

Only aggregate counts are drawn. No issue titles, bodies, comments, code,
branch names or customer data.
"""
import math
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

W, H = 2000, 1125


def font(size, bold=False):
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def canvas(title, kicker):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 12), fill=BLUE)
    text(d, (90, 78), kicker, 30, BLUE, bold=True)
    text(d, (90, 126), title, 58, INK, bold=True)
    return img, d


def arrow(d, start, end, color=GRAY, width=3):
    d.line((start, end), fill=color, width=width)
    (x1, y1), (x2, y2) = start, end
    ang = math.atan2(y2 - y1, x2 - x1)
    size = 16
    for sign in (0.45, -0.45):
        d.line(
            (end, (x2 - size * math.cos(ang + sign), y2 - size * math.sin(ang + sign))),
            fill=color,
            width=width,
        )


def dashed_rect(d, box, color, width=4, dash=16):
    x1, y1, x2, y2 = box
    for x in range(x1, x2, dash * 2):
        d.line((x, y1, min(x + dash, x2), y1), fill=color, width=width)
        d.line((x, y2, min(x + dash, x2), y2), fill=color, width=width)
    for y in range(y1, y2, dash * 2):
        d.line((x1, y, x1, min(y + dash, y2)), fill=color, width=width)
        d.line((x2, y, x2, min(y + dash, y2)), fill=color, width=width)


def fig_gates():
    img, d = canvas("通過は2つ。実装の手前で停止した", "関門 / workerは上から順に確認する")
    gates = [
        ("1 接続確認", "team TAA と\nプロジェクトを照合", "通過", BLUE, LIGHTBLUE),
        ("2 作業ツリー", "未コミットの\n変更を確認", "通過", BLUE, LIGHTBLUE),
        ("3 Todo選択", "Todoを1件選ぶ\n候補0件", "停止", RED, LIGHTRED),
        ("4 実装とテスト", "コードを書いて\nローカルで検証", "未到達", GRAY, LIGHTGRAY),
        ("5 Draft PR", "push・PR作成\nLinearへ記録", "未到達", GRAY, LIGHTGRAY),
    ]
    box_w, gap = 330, 40
    start_x, top, box_h = 105, 330, 400
    for i, (name, note, state, accent, fill) in enumerate(gates):
        x = start_x + i * (box_w + gap)
        box = (x, top, x + box_w, top + box_h)
        if state == "未到達":
            dashed_rect(d, box, BORDERGRAY, 4)
        else:
            d.rectangle(box, fill=fill, outline=accent, width=4)
        text(d, (x + box_w // 2, top + 40), name, 32, accent, bold=True, anchor="ma")
        for n, line in enumerate(note.split("\n")):
            text(d, (x + box_w // 2, top + 120 + n * 44), line, 25, SUB, anchor="ma")
        if state == "通過":
            cy = top + 292
            d.ellipse((x + box_w // 2 - 34, cy - 34, x + box_w // 2 + 34, cy + 34), outline=BLUE, width=5)
            d.line((x + box_w // 2 - 15, cy + 2, x + box_w // 2 - 2, cy + 16), fill=BLUE, width=6)
            d.line((x + box_w // 2 - 2, cy + 16, x + box_w // 2 + 18, cy - 14), fill=BLUE, width=6)
        elif state == "停止":
            cy = top + 292
            d.ellipse((x + box_w // 2 - 34, cy - 34, x + box_w // 2 + 34, cy + 34), outline=RED, width=5)
            d.line((x + box_w // 2 - 14, cy - 14, x + box_w // 2 + 14, cy + 14), fill=RED, width=6)
            d.line((x + box_w // 2 + 14, cy - 14, x + box_w // 2 - 14, cy + 14), fill=RED, width=6)
        else:
            text(d, (x + box_w // 2, top + 292), "—", 46, GRAY, bold=True, anchor="mm")
        text(d, (x + box_w // 2, top + 360), state, 26, accent, bold=True, anchor="ma")
        if i < len(gates) - 1:
            ax = x + box_w + 4
            arrow(d, (ax, top + 190), (ax + gap - 10, top + 190), SUB, 4)
    d.rectangle((90, 800, W - 90, 900), fill=LIGHTAMBER)
    text(d, (120, 826), "Todoが0件なので、実装・テスト・PR作成には進んでいない。", 32, AMBER, bold=True)
    text(d, (120, 928), "関門4・5は「失敗」ではなく「未到達」。試してもいない作業を失敗と呼ばない。", 26, SUB)
    text(d, (120, 972), "対象プロジェクト21件の内訳は Backlog 16 / Todo 0 / In Progress 4 / In Review 1 / Done 0。", 26, SUB)
    img.save(ROOT / "gate_status.png")


def fig_budget():
    img, d = canvas("枠は2/6消費、成果物は0", "実行枠 / 今日すでに使った回数と残り")
    # left: six run slots
    text(d, (110, 250), "1日の実行枠（6回）", 32, INK, bold=True)
    slot, gap = 148, 18
    top = 310
    for i in range(6):
        x = 110 + i * (slot + gap)
        used = i < 2
        box = (x, top, x + slot, top + 140)
        if used:
            d.rectangle(box, fill=BLUE, outline=BLUE, width=4)
            text(d, (x + slot // 2, top + 70), "使用", 32, "#ffffff", bold=True, anchor="mm")
        else:
            d.rectangle(box, fill=BG, outline=BORDERGRAY, width=4)
            text(d, (x + slot // 2, top + 70), "残り", 32, GRAY, bold=True, anchor="mm")
    text(d, (110, 478), "今日の実行は00:13と00:43の2回。", 26, SUB)
    text(d, (110, 518), "どちらも同じ結論（Todo 0件）だった。", 26, SUB)
    # right: outputs
    text(d, (1230, 250), "今日の成果物", 32, INK, bold=True)
    rows = [("コード変更", "0行"), ("新規Draft PR", "0本"), ("Linear更新", "0件")]
    for n, (label, value) in enumerate(rows):
        y = 306 + n * 106
        d.rectangle((1210, y, 1890, y + 86), fill=LIGHTGRAY)
        text(d, (1236, y + 43), label, 29, SUB, anchor="lm")
        text(d, (1862, y + 43), value, 42, INK, bold=True, anchor="rm")
    # bottom: issue status pills
    d.line((110, 700, 1890, 700), fill=BORDERGRAY, width=2)
    text(d, (110, 722), "対象プロジェクトの21件", 30, INK, bold=True)
    pills = [
        ("Backlog 16", GRAY, LIGHTGRAY),
        ("Todo 0", RED, LIGHTRED),
        ("In Progress 4", BLUE, LIGHTBLUE),
        ("In Review 1", BLUE, LIGHTBLUE),
        ("Done 0", GRAY, LIGHTGRAY),
    ]
    x = 110
    for label, accent, fill in pills:
        width = 320
        d.rectangle((x, 776, x + width, 862), fill=fill, outline=accent, width=4)
        text(d, (x + width // 2, 819), label, 33, accent, bold=True, anchor="mm")
        x += width + 22
    d.rectangle((90, 900, W - 90, 985), fill=LIGHTAMBER)
    text(d, (120, 924), "選べるTodoが無いまま起動すると、枠とモデル利用量だけが減る。", 32, AMBER, bold=True)
    text(d, (120, 1012), "open中のDraft PRは8本、mergeは0本（今回変更していない）。", 25, SUB)
    text(d, (120, 1052), "※ 精度・速度・費用の改善は今回測定していない。", 25, SUB)
    img.save(ROOT / "run_budget.png")


if __name__ == "__main__":
    fig_gates()
    fig_budget()
    print("figures written")
