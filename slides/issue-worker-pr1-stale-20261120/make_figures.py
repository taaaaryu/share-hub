#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data source (public-safe aggregates only, checked 2026-11-20 JST):
- private remote thumaster: PR #1 is still open, Draft, mergeable=CLEAN,
  0 reviews, 0 comments, no CI checks. 13 changed files, +1317 / -0.
- Linear project f7f3a327-a06b-478f-bd88-c49fc2b79cef: 21 issues.
  Todo 0, Backlog 16, In Progress 4, In Review 1 (TAA-44).
- Tests run locally on 2026-11-20 in the experiments venv:
  thumaster/main 80 passed, PR #1 head 104 passed (git archive + pytest).

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


def font(size, bold=False):
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def box(draw, x, y, w, h, fill, border, width=2, radius=8, dashed=False):
    if dashed:
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


def arrow(draw, x1, y1, x2, y2, color=GRAY, width=5):
    draw.line((x1, y1, x2, y2), fill=color, width=width)
    if y1 == y2:
        head = 13
        draw.polygon([(x2, y2), (x2 - head, y2 - head), (x2 - head, y2 + head)], fill=color)
    else:
        draw.ellipse((x2 - 7, y2 - 7, x2 + 7, y2 + 7), fill=color)


# ---------------------------------------------------------------- figure 1

FILES = [
    ("core/hud_change.py", 359, "共通部品（新規）"),
    ("detail/damage_timing.py", 324, "呼び出し側の切り出し"),
    ("tests/test_hud_change.py", 257, "新規テスト"),
    ("tests/test_damage_timing.py", 159, "移行テスト"),
    ("tests/benchmark_hud_change.py", 79, "再現用ベンチ"),
    ("docs/ 6ファイル", 134, "設計・計測記録"),
    (".gitignore", 5, "設定"),
]


def diff_card(path):
    W, H = 2000, 1125
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (90, 52), "PR #1の中身：消した行は0、足したテストは24本", 52, INK, bold=True)
    text(d, (90, 128), "変更13ファイル・+1317行を、役割ごとに並べた。数値は2026-11-20時点のPR #1（Draft）。", 24, SUB)

    # left: file bars
    px, py = 90, 196
    text(d, (px, py), "どのファイルに、何行入ったか", 30, INK, bold=True)
    text(d, (px + 560, py + 8), "追加行数", 20, SUB)
    max_lines = 360.0
    bar_x = px + 470
    bar_max = 250
    for i, (name, lines, role) in enumerate(FILES):
        y = py + 62 + i * 78
        text(d, (px, y + 2), name, 23, INK if i < 5 else SUB, bold=i < 3)
        text(d, (px, y + 32), role, 19, SUB)
        w = int(bar_max * lines / max_lines)
        fill = LIGHTBLUE if i < 5 else LIGHTGRAY
        border = BLUE if i < 5 else BORDERGRAY
        box(d, bar_x, y + 4, max(w, 6), 30, fill, border, 2, radius=4)
        text(d, (bar_x + max(w, 6) + 14, y + 6), f"{lines}行", 21, INK if i < 5 else SUB)

    # right: before/after tests
    rx, ry, rw, rh = 1010, 196, 900, 452
    box(d, rx, ry, rw, rh, "#ffffff", BORDERGRAY, 2)
    text(d, (rx + 30, ry + 24), "手元で今朝流したテスト", 30, INK, bold=True)
    text(d, (rx + 30, ry + 66), "venv の pytest。git archive で取り出した2つの時点を同じ手順で実行。", 21, SUB)

    # before
    text(d, (rx + 30, ry + 122), "main", 24, SUB, bold=True)
    text(d, (rx + 30, ry + 154), "80 passed", 34, SUB, bold=True)
    box(d, rx + 220, ry + 146, 300, 24, LIGHTGRAY, BORDERGRAY, 2, radius=4)

    # after
    text(d, (rx + 30, ry + 212), "PR #1 の head", 24, BLUE, bold=True)
    text(d, (rx + 30, ry + 244), "104 passed", 34, BLUE, bold=True)
    box(d, rx + 260, ry + 236, 380, 24, LIGHTBLUE, BLUE, 2, radius=4)
    text(d, (rx + 652, ry + 238), "+24本", 24, GREEN, bold=True)

    text(d, (rx + 30, ry + 312), "失敗0。テストの追加だけで、既存80本は変わらず通る。", 23, INK)
    text(d, (rx + 30, ry + 352), "ただしこれは手元の結果で、CIは未設定（checks 0件）。", 22, SUB)
    text(d, (rx + 30, ry + 388), "本番有効化・GUI確認・実費評価はPR本文でも未実施と書かれている。", 22, SUB)

    # bottom: merge state
    bx, by, bw, bh = 90, 812, 1820, 228
    box(d, bx, by, bw, bh, LIGHTAMBER, AMBER, 3)
    text(d, (bx + 30, by + 22), "マージできる状態か", 28, AMBER, bold=True)
    facts = [
        ("mergeable", "CLEAN"),
        ("レビュー", "0件"),
        ("コメント", "0件"),
        ("CIチェック", "0件（未設定）"),
        ("Draft", "はい"),
    ]
    cx = bx + 30
    for label, value in facts:
        text(d, (cx, by + 84), label, 20, SUB)
        text(d, (cx, by + 116), value, 26, INK, bold=True)
        cx += 340
    text(d, (bx + 30, by + 190), "競合はなく、レビューが入ればDraft解除できる。止めているのは技術的な詰まりではなく、レビューの順番待ち。", 23, AMBER)

    img.save(path)


# ---------------------------------------------------------------- figure 2

WAITING = [
    ("TAA-45", "検出方式の比較", "TAA-44 と TAA-43 待ち"),
    ("TAA-46", "時系列トリガーの実装", "TAA-44 待ち"),
    ("TAA-48", "判断ログの記録", "TAA-44 待ち"),
    ("TAA-49", "CPU費用の計測", "TAA-44 と TAA-45 待ち"),
]


def timeline(path):
    W, H = 2000, 1125
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (90, 52), "23日間、レビューは0件。その後ろに4件が並ぶ", 52, INK, bold=True)
    text(d, (90, 128), "PR #1は2026-10-28にDraftで作成され、2026-11-20時点でも同じ状態のまま。箱は、その完了を待つ課題。", 24, SUB)

    # timeline
    tx0, tx1, ty = 120, 1180, 330
    d.line((tx0, ty, tx1, ty), fill=BORDERGRAY, width=6)
    marks = [("10/28", 0.0, "Draftで作成"), ("11/04", 7 / 23, ""), ("11/11", 14 / 23, ""),
             ("11/18", 21 / 23, ""), ("11/20", 1.0, "今日")]
    for label, ratio, note in marks:
        x = int(tx0 + (tx1 - tx0) * ratio)
        d.line((x, ty - 14, x, ty + 14), fill=GRAY, width=4)
        text(d, (x, ty + 26), label, 22, SUB, anchor="ma")
        if note:
            text(d, (x, ty + 58), note, 21, BLUE if ratio else AMBER, anchor="ma", bold=True)

    # day counter bracket
    d.line((tx0, ty - 62, tx1, ty - 62), fill=AMBER, width=4)
    d.line((tx0, ty - 78, tx0, ty - 46), fill=AMBER, width=4)
    d.line((tx1, ty - 78, tx1, ty - 46), fill=AMBER, width=4)
    text(d, ((tx0 + tx1) // 2, ty - 118), "23日", 46, AMBER, bold=True, anchor="ma")

    # PR node at start
    box(d, tx0 - 40, ty + 110, 300, 150, LIGHTAMBER, AMBER, 4)
    text(d, (tx0 - 14, ty + 130), "PR #1", 32, AMBER, bold=True)
    text(d, (tx0 - 14, ty + 176), "TAA-44", 24, AMBER)
    text(d, (tx0 - 14, ty + 210), "レビュー 0 / コメント 0", 21, SUB)

    # zero-review callout
    arrow(d, tx0 + 270, ty + 185, tx1 - 60, ty + 185, AMBER, 4)
    text(d, ((tx0 + tx1) // 2 - 20, ty + 196), "この間ずっと同じ状態", 22, AMBER, anchor="ma")

    # right panel: waiting issues
    qx, qy, qw = 1240, 200, 680
    box(d, qx, qy, qw, 640, "#ffffff", BORDERGRAY, 2)
    text(d, (qx + 28, qy + 22), "PR #1 が終わると動く4件", 30, INK, bold=True)
    text(d, (qx + 28, qy + 66), "すべてBacklog。blockedByにTAA-44が入っている。", 21, SUB)
    for i, (ident, what, why) in enumerate(WAITING):
        y = qy + 118 + i * 126
        box(d, qx + 24, y, qw - 48, 108, LIGHTGRAY, BORDERGRAY, 2, dashed=True)
        text(d, (qx + 46, y + 14), ident, 28, GRAY, bold=True)
        text(d, (qx + 46, y + 52), what, 22, INK)
        text(d, (qx + 46, y + 80), why, 19, SUB)

    # board counts, bottom-left
    sx, sy, sw, sh = 120, 600, 1040, 250
    box(d, sx, sy, sw, sh, "#ffffff", BORDERGRAY, 2)
    text(d, (sx + 28, sy + 20), "同じ時点のボード（21件）", 28, INK, bold=True)
    counts = [("Todo", "0件", "workerが選べる唯一の状態"), ("Backlog", "16件", "計画のみ・実装しない"),
              ("In Progress", "4件", "PRはDraftで止まっている"), ("In Review", "1件", "PR #1 = TAA-44")]
    for i, (label, value, note) in enumerate(counts):
        cx = sx + 28 + i * 250
        text(d, (cx, sy + 78), label, 19, SUB)
        text(d, (cx, sy + 104), value, 30, AMBER if i in (0, 3) else INK, bold=True)
        text(d, (cx, sy + 150), note, 17, SUB)
    text(d, (sx + 28, sy + 206), "前日のrunから件数は変わらず、状態の移動もない。", 21, SUB)

    # bottom note
    bx, by, bw, bh = 90, 900, 1820, 130
    box(d, bx, by, bw, bh, LIGHTBLUE, BLUE, 3)
    text(d, (bx + 30, by + 20), "今日の実行では、merge・Draft解除・担当変更・Linearの状態変更はしていない。", 24, INK)
    text(d, (bx + 30, by + 66), "workerはmergeしない決まりなので、この4件を開ける操作は人のレビュー（またはTodo追加の判断）になる。", 23, SUB)

    img.save(path)


if __name__ == "__main__":
    diff_card(ROOT / "pr1-diff.png")
    timeline(ROOT / "pr1-wait.png")
    print("wrote pr1-diff.png, pr1-wait.png")
