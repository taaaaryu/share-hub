#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data source (public-safe aggregates only, checked 2026-11-15 15:30 JST):
- state/runs.json: today's run count (4 of 6) and the daily limit.
- state/cooldown.json: the 30 minute usage-limit stop at 2026-11-15T05:53Z.
- Linear project f7f3a327-a06b-478f-bd88-c49fc2b79cef: 21 issues, their
  statuses and the blockedBy direction of their relations.
- private remote thumaster: the 8 open Draft PRs.

Issue titles, bodies, comments, assignees, branch names, code and customer
data do not appear in the images. Only counts, dates and issue keys are drawn.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"

INK = "#161616"
SUB = "#525252"
BG = "#ffffff"
BLUE = "#0f62fe"
DARKBLUE = "#0043ce"
LIGHTBLUE = "#edf5ff"
TEAL = "#007d79"
LIGHTTEAL = "#d9fbfb"
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


def runs(path: Path) -> None:
    W, H = 1400, 780
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (70, 40), "今日の起動枠：6回のうち4回を使い、コードは0行", 40, INK, bold=True)
    text(d, (70, 100), "1回＝1課題。使った回数が増えても、選ぶ対象が0件なら実装は始まらない。", 19, SUB)

    left = 70
    slot_w, slot_h, gap = 180, 190, 26
    top = 170
    for index in range(6):
        x = left + index * (slot_w + gap)
        used = index < 4
        fill = LIGHTBLUE if used else "#f4f4f4"
        border = BLUE if used else "#c6c6c6"
        box(d, x, top, slot_w, slot_h, fill, border, 2)
        text(d, (x + 20, top + 18), f"{index + 1}回目", 24, DARKBLUE if used else GRAY, bold=True)
        if used:
            text(d, (x + 20, top + 62), "0 行", 40, RED, bold=True)
            text(d, (x + 20, top + 120), "コード変更なし", 18, SUB)
            text(d, (x + 20, top + 148), "Todo 0件で終了", 18, SUB)
        else:
            text(d, (x + 20, top + 62), "未使用", 32, GRAY, bold=True)
            text(d, (x + 20, top + 120), "残り", 18, SUB)

    # usage-limit stop
    y = 400
    box(d, 70, y, 1260, 74, LIGHTAMBER, "#ffb784", 2)
    text(d, (90, y + 14), "14:37の実行は利用上限に当たり、14:53から30分停止した（15:23に再開）", 22, AMBER, bold=True)
    text(d, (90, y + 44), "停止中もTodoは増えないので、待った先でも同じ0件だった。", 18, SUB)

    # outcome row
    y2 = 520
    text(d, (70, y2), "今日ここまでの合計", 22, SUB, bold=True)
    cells = [
        ("選んだ課題", "0 件", RED),
        ("コード変更", "0 行", RED),
        ("作ったPR", "0 本", RED),
        ("増えた報告", "3 本", DARKBLUE),
    ]
    cw = 300
    for index, (name, value, colour) in enumerate(cells):
        x = 70 + index * (cw + 20)
        box(d, x, y2 + 36, cw, 108, "#f4f4f4", LIGHTGRAY, 2)
        text(d, (x + 20, y2 + 50), name, 19, SUB)
        text(d, (x + 20, y2 + 82), value, 36, colour, bold=True)

    text(d, (70, 720), "報告＝workerが1回ごとに公開する説明資料。実装が無い回でも作る決まりのため、ここだけが増える。", 18, SUB)

    img.save(path)


def unlock(path: Path) -> None:
    W, H = 1400, 900
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (70, 40), "2件の未完了が5件を止め、7件はすぐ動かせる", 40, INK, bold=True)
    text(d, (70, 100), "矢印は「この課題が終わるまで着手しない」の向き。直接の依存だけを描いている。", 19, SUB)

    rows = [
        ("TAA-44", "In Review ・ PR #1", ["TAA-45", "TAA-46", "TAA-48", "TAA-49"], DARKBLUE, LIGHTBLUE, 4),
        ("TAA-52", "In Progress ・ PR #5", ["TAA-53"], TEAL, LIGHTTEAL, 1),
        ("なし", "未完了の前提が0件", ["TAA-35", "TAA-36", "TAA-38", "TAA-39", "TAA-40", "TAA-41", "TAA-43"], GRAY, "#f4f4f4", 7),
    ]

    top = 170
    row_h = 200
    for index, (key, note, targets, colour, fill, count) in enumerate(rows):
        y = top + index * row_h
        # blocker card
        box(d, 70, y, 260, 120, fill, colour, 3)
        text(d, (90, y + 16), key, 30, colour, bold=True)
        text(d, (90, y + 60), note, 17, SUB)
        text(d, (90, y + 88), f"待たせている: {count}件", 17, colour, bold=True)

        # arrow
        ax0, ax1 = 340, 420
        d.line((ax0, y + 60, ax1 - 12, y + 60), fill=colour, width=3)
        d.polygon([(ax1, y + 60), (ax1 - 14, y + 52), (ax1 - 14, y + 68)], fill=colour)

        # targets
        chip_w, chip_h, chip_gap = 118, 64, 14
        for chip_index, target in enumerate(targets):
            cx = 430 + chip_index * (chip_w + chip_gap)
            box(d, cx, y + 28, chip_w, chip_h, BG, colour, 2)
            text(d, (cx + chip_w / 2, y + 28 + chip_h / 2), target, 19, colour, bold=True, anchor="mm")

    # footnote
    y = 780
    box(d, 70, y, 1260, 88, LIGHTRED, "#ffb3b8", 2)
    text(d, (90, y + 12), "図は直接の依存だけ。TAA-45と49はTAA-43も、TAA-50はTAA-47・48・49・35も待つ。", 20, RED, bold=True)
    text(d, (90, y + 44), "そのためTAA-44がDoneになっても、先の全件がすぐ着手可能になるわけではない。", 18, SUB)

    img.save(path)


if __name__ == "__main__":
    runs(ROOT / "runs.png")
    unlock(ROOT / "unlock.png")
    print("generated runs.png unlock.png")
