#!/usr/bin/env python3
"""Figures for the 2026-11-18 issue-worker resume runbook.

Public-safe data only (aggregated, checked 2026-11-18):
- Linear project f7f3a327: 21 issues, per-status counts (16 backlog / 4 in progress
  / 1 in review / 0 todo).
- GitHub private repo taaaryu/thumaster: 8 open draft PRs, 0 merged, 3 created
  2026-10-28 (21 days old), 5 created 2026-11-05 (13 days old), 4 with green CI.
No issue titles, descriptions, comments, code, or personal data are drawn.
"""
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"

INK = "#161616"
SUB = "#525252"
BG = "#ffffff"
PALE = "#edf5ff"
BLUE = "#0f62fe"
AMBER = "#8a3800"
LIGHTAMBER = "#fff2e8"
BORDERAMBER = "#d97706"
GRAY = "#6f6f6f"
LIGHTGRAY = "#f4f4f4"
BORDERGRAY = "#c6c6c6"
GREEN = "#198038"
RED = "#a2191f"
W = 2000
H = 1125


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


NO_LINE_START = "、。，．・）)]」』／/：:"


def wrap(draw, value, size, max_width, bold=False):
    """Split one paragraph into lines, keeping ASCII words whole and avoiding
    lines that begin with punctuation."""
    face = font(size, bold)
    tokens = re.findall(r"[A-Za-z0-9_./:+#-]+|\s+|.", value)
    lines = []
    current = ""
    for token in tokens:
        if token.isspace():
            if current:
                current += token
            continue
        trial = current + token
        if draw.textlength(trial.rstrip(), font=face) <= max_width or not current.strip():
            current = trial
            continue
        if token and token[0] in NO_LINE_START:
            # keep punctuation attached to the previous line
            current += token
            continue
        lines.append(current.rstrip())
        current = token
    if current.strip():
        lines.append(current.rstrip())
    return lines


def box(draw, x, y, w, h, fill, border, width=2, radius=14):
    draw.rounded_rectangle((x, y, x + w, y + h), radius=radius, fill=fill, outline=border, width=width)


def canvas():
    image = Image.new("RGB", (W, H), BG)
    return image, ImageDraw.Draw(image)


def arrow(draw, x, y, length, color=GRAY):
    draw.line((x, y, x + length, y), fill=color, width=4)
    draw.polygon([(x + length, y), (x + length - 16, y - 10), (x + length - 16, y + 10)], fill=color)


def jam():
    image, draw = canvas()
    text(draw, (70, 70), "入口は0件、出口は8件。同じ流れの両端で止まっている", 56, INK, bold=True)
    text(draw, (70, 146), "2026-11-18 に Linear と GitHub を実際に数えた結果", 30, SUB)

    cards = [
        (70, "入口 / Linear", "人の判断が要る", [
            ("Todo（着手してよい）", "0件", RED, True),
            ("Backlog（計画だけ）", "16件", INK, False),
            ("In Progress（作業中）", "4件", INK, False),
            ("In Review（確認待ち）", "1件", INK, False),
        ]),
        (720, "レーン / worker", "今日の実行", [
            ("選べた課題", "0件", RED, True),
            ("書いたコード", "0行", INK, False),
            ("作ったPR", "0件", INK, False),
            ("エラー・失敗", "0件", GREEN, False),
        ]),
        (1370, "出口 / GitHub", "人のレビューが要る", [
            ("Draft PR（未merge）", "8件", AMBER, True),
            ("merge 済み", "0件", INK, False),
            ("最長の待ち", "21日", INK, False),
            ("CI が緑", "4 / 8件", INK, False),
        ]),
    ]

    for x, heading, sub, rows in cards:
        box(draw, x, 232, 560, 500, BG, BORDERGRAY, 2, 16)
        text(draw, (x + 34, 262), heading, 34, INK, bold=True)
        text(draw, (x + 34, 306), sub, 24, SUB)
        draw.line((x + 34, 348, x + 526, 348), fill=BORDERGRAY, width=2)
        y = 380
        for name, value, color, strong in rows:
            text(draw, (x + 34, y), name, 27, SUB)
            text(draw, (x + 526, y - 2), value, 40 if strong else 34, color, bold=strong, anchor="ra")
            y += 84

    arrow(draw, 645, 482, 60)
    arrow(draw, 1295, 482, 60)

    box(draw, 70, 790, 1860, 200, LIGHTGRAY, BORDERGRAY, 2, 16)
    text(draw, (110, 822), "止まっているのは自動化ではない", 34, INK, bold=True)
    text(draw, (110, 878), "worker は「Todo から1件選ぶ」以外の入口を持たない設計。入口が空なら、正しく動いても仕事は生まれない。", 28, SUB)
    text(draw, (110, 928), "出口の8件も、merge の判断を人に残しているため、レビューが無い間は同じ場所で待ち続ける。", 28, SUB)

    image.save(ROOT / "jam.png")
    print("jam.png")


def runbook():
    image, draw = canvas()
    text(draw, (70, 70), "再開するための4手順。かかる時間の目安つき", 56, INK, bold=True)
    text(draw, (70, 146), "上から順に進めれば、次の自動実行で1件目の実装が始まる", 30, SUB)

    steps = [
        ("01", "出口を1件ひらく",
         "Draft PR を1件えらび、差分を読んで merge する。21日待っている3件のどれか1件でよい。",
         "人 / 約45分", AMBER, LIGHTAMBER, BORDERAMBER),
        ("02", "入口を1件ひらく",
         "依存の無い Backlog を1件だけ Todo へ動かす。2件以上動かしても worker は1件しか見ない。",
         "人 / 2分", BLUE, PALE, BLUE),
        ("03", "自動実行を1回まわす",
         "worker が Todo を1件取り、作業中にして、実装・テスト・Draft PR まで進める。",
         "worker / 自動", BLUE, PALE, BLUE),
        ("04", "結果をレビューする",
         "PR の説明資料とテスト結果を読み、merge するか戻すかを決める。merge と公開は worker にやらせない。",
         "人 / 約30分", AMBER, LIGHTAMBER, BORDERAMBER),
    ]

    x = 70
    width = 440
    gap = 40
    for number, title, body, owner, ink, fill, border in steps:
        box(draw, x, 232, width, 470, fill, border, 3, 18)
        text(draw, (x + 30, 258), number, 52, ink, bold=True)
        text(draw, (x + 30, 336), title, 32, ink, bold=True)
        y = 400
        for line in wrap(draw, body, 24, width - 60):
            text(draw, (x + 30, y), line, 24, INK)
            y += 38
        box(draw, x + 30, 612, 250, 56, BG, border, 2, 28)
        text(draw, (x + 155, 641), owner, 24, ink, bold=True, anchor="mm")
        x += width + gap

    box(draw, 70, 752, 1860, 250, LIGHTGRAY, BORDERGRAY, 2, 16)
    text(draw, (110, 784), "うまくいかないときの見かた", 30, INK, bold=True)
    notes = [
        "手順2のあと Todo が0件に戻っている → 手順2が保存されていない。",
        "手順3が30分を超えて終わらない → ログで失敗理由を確認し、同じ課題を2回までで打ち切る。",
        "手順1で衝突が出る → その PR の担当分だけを戻し、他の1件で試す。",
    ]
    y = 838
    for note in notes:
        text(draw, (110, y), note, 25, SUB)
        y += 44

    image.save(ROOT / "runbook.png")
    print("runbook.png")


if __name__ == "__main__":
    jam()
    runbook()
