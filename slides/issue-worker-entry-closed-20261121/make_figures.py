#!/usr/bin/env python3
"""Figures for the 2026-11-21 "entry closed" deck.

Public-safe data only (read 2026-11-21 JST from the private Linear project):
- 21 issues: Backlog 16 / Todo 0 / In Progress 4 / In Review 1 / Done 0.
- 16 Backlog issues: 7 have no blockers, 8 are blocked, 1 is the epic.
- 8 open pull requests, all drafts, 0 merged.

Only aggregate counts, issue numbers and dependency shape are drawn.
No issue titles, bodies, comments, code, branch names or customer data.
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
    # small arrow head
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    size = 16
    for sign in (0.45, -0.45):
        d.line(
            (end, (x2 - size * math.cos(ang + sign), y2 - size * math.sin(ang + sign))),
            fill=color, width=width,
        )


def fig_pipeline():
    """Backlog -> Todo -> In Progress -> In Review -> Done."""
    img, d = canvas("ベルトの入口が0件だと、あとは動かない", "全体像 / 課題はどの段に何件あるか")
    stages = [
        ("Backlog", 16, "計画だけ。workerは着手しない", GRAY, LIGHTGRAY),
        ("Todo", 0, "workerが着手できる唯一の段", RED, LIGHTRED),
        ("In Progress", 4, "実装中（すべてDraft PRあり）", BLUE, LIGHTBLUE),
        ("In Review", 1, "PR作成済み・レビュー待ち", BLUE, LIGHTBLUE),
        ("Done", 0, "merge済みの完了", GRAY, LIGHTGRAY),
    ]
    box_w, gap = 320, 45
    start_x, top, box_h = 105, 330, 300
    for i, (name, count, note, accent, fill) in enumerate(stages):
        x = start_x + i * (box_w + gap)
        d.rectangle((x, top, x + box_w, top + box_h), fill=fill, outline=accent, width=4)
        text(d, (x + box_w // 2, top + 36), name, 30, accent, bold=True, anchor="ma")
        text(d, (x + box_w // 2, top + 154), str(count), 104, accent, bold=True, anchor="mm")
        text(d, (x + box_w // 2, top + 246), note, 20, SUB, anchor="ma")
        if i < len(stages) - 1:
            ax = x + box_w + 6
            arrow(d, (ax, top + 150), (ax + gap - 12, top + 150), SUB, 4)
    d.rectangle((90, 700, W - 90, 790), fill=LIGHTAMBER)
    text(d, (120, 724), "21件あるのに、workerが触れるのは Todo の0件だけ。入口が空なので、下流も止まる。",
         29, AMBER, bold=True)
    text(d, (105, 840), "Done が0件なのは、レビュー待ちの1件がまだmergeされていないため。",
         26, SUB)
    text(d, (105, 890), "Draft PRは8本open。うち4本は In Progress の4件、1本が In Review の1件に対応する。",
         26, SUB)
    img.save(ROOT / "pipeline_stages.png")


def fig_backlog_split():
    """16 Backlog: 7 unblocked, 8 blocked, 1 epic."""
    img, d = canvas("Backlog 16件のうち7件は、待たずに動ける", "内訳 / 依存関係を1件ずつ確認")
    bar_x, bar_y, bar_h = 120, 400, 170
    total_w = 1760
    unit = total_w / 16
    segments = [("依存なし 7件", 7, BLUE, LIGHTBLUE), ("依存あり 8件", 8, AMBER, LIGHTAMBER), ("Epic 1件", 1, GRAY, LIGHTGRAY)]
    x = bar_x
    for label, count, accent, fill in segments:
        w = unit * count
        d.rectangle((x, bar_y, x + w, bar_y + bar_h), fill=fill, outline=accent, width=4)
        if count == 1:
            text(d, (x + w / 2, bar_y + 78), str(count), 56, accent, bold=True, anchor="mm")
            text(d, (x + w / 2 - 150, bar_y - 46), label, 24, SUB, anchor="lm")
            d.line((x + w / 2 - 20, bar_y - 40, x + w / 2, bar_y - 6), fill=accent, width=2)
        else:
            text(d, (x + w / 2, bar_y + 66), str(count), 76, accent, bold=True, anchor="mm")
            text(d, (x + w / 2, bar_y + 130), label, 24, SUB, anchor="ma")
        x += w
    d.line((bar_x, bar_y + bar_h + 40, bar_x + total_w, bar_y + bar_h + 40), fill=INK, width=2)
    text(d, (bar_x, bar_y + bar_h + 60), "16件を依存の有無で分けたもの（1目盛り=1件）", 24, SUB)
    d.rectangle((120, 700, 1000, 960), fill=LIGHTBLUE, outline=BLUE, width=3)
    text(d, (150, 726), "依存なしの7件", 30, BLUE, bold=True)
    text(d, (150, 782), "・他課題の完了を待たない", 25, INK)
    text(d, (150, 826), "・今日そのまま着手できる内容", 25, INK)
    text(d, (150, 878), "・ただし状態は Backlog のまま", 25, AMBER, bold=True)
    d.rectangle((1040, 700, 1880, 960), fill=LIGHTAMBER, outline=AMBER, width=3)
    text(d, (1070, 726), "依存ありの8件", 30, AMBER, bold=True)
    text(d, (1070, 782), "・HUD系6件は In Review の1件待ち", 25, INK)
    text(d, (1070, 826), "・テストデータ1件が別の1件を止める", 25, INK)
    text(d, (1070, 878), "・最後の仕上げ1件は4件待ち", 25, INK)
    text(d, (120, 1005), "つまり「作る物が無い」のではなく「着手してよい印が付いていない」。", 28, INK, bold=True)
    img.save(ROOT / "backlog_split.png")


NODES = {
    "44": (150, 290, "In Review", BLUE, LIGHTBLUE, "起点"),
    "43": (150, 470, "Backlog", GRAY, LIGHTGRAY, "起点"),
    "35": (150, 650, "Backlog", GRAY, LIGHTGRAY, "起点"),
    "45": (620, 290, "Backlog", GRAY, LIGHTGRAY, "43・44 待ち"),
    "46": (620, 470, "Backlog", GRAY, LIGHTGRAY, "44 待ち"),
    "48": (620, 650, "Backlog", GRAY, LIGHTGRAY, "44 待ち"),
    "47": (1090, 380, "Backlog", GRAY, LIGHTGRAY, "45・46 待ち"),
    "49": (1090, 560, "Backlog", GRAY, LIGHTGRAY, "44・45 待ち"),
    "50": (1540, 460, "Backlog", GRAY, LIGHTGRAY, "4件待ち"),
}
NODE_W, NODE_H = 210, 130


def fig_dag():
    img, d = canvas("1件のレビューが、6件の入口をふさいでいる", "依存関係 / HUD改善まわりの6件")
    edges = [
        ("44", "45"), ("43", "45"), ("44", "46"), ("44", "48"),
        ("45", "47"), ("46", "47"), ("45", "49"), ("44", "49"),
        ("47", "50"), ("48", "50"), ("49", "50"), ("35", "50"),
    ]
    for src, dst in edges:
        sx, sy = NODES[src][0], NODES[src][1]
        dx, dy = NODES[dst][0], NODES[dst][1]
        if sx == dx:
            start = (sx + NODE_W // 2, sy + NODE_H)
            end = (dx + NODE_W // 2, dy)
        elif sx < dx and dx - sx > NODE_W * 2:
            start = (sx + NODE_W // 2, sy + NODE_H // 2)
            end = (dx, dy + NODE_H // 2)
        else:
            start = (sx + NODE_W, sy + NODE_H // 2)
            end = (dx, dy + NODE_H // 2)
        long_edge = dx - sx > NODE_W * 2.5 or sx == dx
        arrow(d, start, end, LIGHTGRAY if long_edge else BORDERGRAY, 4 if long_edge else 4)
    for key, (x, y, status, accent, fill, requires) in NODES.items():
        d.rectangle((x, y, x + NODE_W, y + NODE_H), fill=fill, outline=accent, width=4)
        text(d, (x + 18, y + 18), key, 40, accent, bold=True)
        text(d, (x + 18, y + 70), status, 22, accent, bold=True)
        text(d, (x + 18, y + 99), requires, 19, SUB)
    d.rectangle((90, 900, W - 90, 985), fill=LIGHTAMBER)
    text(d, (120, 922), "1件だけmergeしても全部は動かない。43のテストデータと35の計測も、途中で必要になる。",
         26, AMBER, bold=True)
    text(d, (120, 1008), "薄い線＝1段以上離れた依存。数字は課題の番号。", 23, SUB)
    img.save(ROOT / "dependency_map.png")


if __name__ == "__main__":
    fig_pipeline()
    fig_backlog_split()
    fig_dag()
    print("figures written")
