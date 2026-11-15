#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data source (public-safe aggregates only, checked 2026-11-15 14:40 JST):
- Linear project f7f3a327-a06b-478f-bd88-c49fc2b79cef: 21 issues and their
  status counts (Backlog 16 / In Progress 4 / In Review 1 / Todo 0 / Done 0).
- private remote thumaster: the 8 open Draft PRs, creation dates and diff sizes.
- share-hub: the number of issue-worker explanation decks published per day.

Issue titles, bodies, comments, assignees, branch names, code and customer data
do not appear in the images. Only counts, dates and diff line totals are drawn.
"""
import json
import re
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
HUB = ROOT.parents[1]
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


def report_counts() -> Counter:
    counts: Counter = Counter()
    for folder in (HUB / "slides").iterdir():
        if not folder.is_dir():
            continue
        if not folder.name.startswith("issue-worker-"):
            continue
        match = re.search(r"2026(\d{2})(\d{2})", folder.name)
        if match:
            counts[f"2026-{match.group(1)}-{match.group(2)}"] += 1
    return counts


def days() -> list:
    out = []
    for day in range(28, 32):
        out.append(f"2026-10-{day:02d}")
    for day in range(1, 16):
        out.append(f"2026-11-{day:02d}")
    return out


def timeline(path: Path) -> None:
    counts = report_counts()
    series = days()
    total = sum(counts.get(d, 0) for d in series)
    W, H = 1400, 830
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (70, 40), f"10/29 → 11/15：報告{total}本、Done 0件", 42, INK, bold=True)
    text(d, (70, 100), "棒＝その日に公開したworkerの説明資料。PR＝private remoteのopen Draft PR。Done＝Linearで完了した課題。", 19, SUB)

    left, right = 110, 1310
    cell = (right - left) / len(series)
    base, top = 560, 270
    per_unit = (base - top) / 5

    # gridlines
    for value in range(0, 6, 1):
        y = base - value * per_unit
        colour = "#c6c6c6" if value else INK
        d.line((left, y, right, y), fill=colour, width=2 if value == 0 else 1)
        text(d, (left - 18, y), str(value), 16, GRAY, anchor="rm")

    for index, day in enumerate(series):
        count = counts.get(day, 0)
        cx = left + index * cell + cell / 2
        label = f"{int(day[5:7])}/{int(day[8:10])}"
        if count:
            height = count * per_unit
            x0 = cx - 15
            box(d, x0, base - height, 30, height, LIGHTBLUE, BLUE, 2)
            text(d, (cx, base - height - 10), str(count), 20, DARKBLUE, bold=True, anchor="mb")
        if index % 2 == 0 or index == len(series) - 1:
            text(d, (cx, base + 16), label, 15, GRAY, anchor="ma")

    text(d, (left - 18, (base + top) / 2), "本数", 16, GRAY, anchor="mm")

    # PR batches
    for day, label, colour, fill in (
        ("2026-10-28", "PR 3本を作成", DARKBLUE, LIGHTBLUE),
        ("2026-11-05", "PR 5本を作成", TEAL, LIGHTTEAL),
    ):
        index = series.index(day)
        cx = left + index * cell + cell / 2
        d.line((cx, base + 44, cx, base + 72), fill=colour, width=2)
        w = 168
        x0 = min(max(cx - w / 2, left), right - w)
        box(d, x0, base + 72, w, 46, fill, colour, 2)
        text(d, (x0 + w / 2, base + 95), label, 19, colour, bold=True, anchor="mm")

    # Done is flat zero
    y = 730
    d.line((left, y, right, y), fill=RED, width=3)
    text(d, (left, y - 16), "Done（完了した課題）", 19, RED, bold=True, anchor="ls")
    text(d, (right, y + 14), "18日間ずっと0件", 21, RED, bold=True, anchor="ra")
    text(d, (left, y + 14), "10/28の着手開始から、完了した課題は1件も出ていない", 19, SUB)

    img.save(path)


def standing(path: Path) -> None:
    prs = [
        (1, "10/28", 17.8, 1317),
        (2, "10/28", 17.8, 2237),
        (3, "10/28", 17.8, 6359),
        (4, "11/05", 9.8, 521),
        (5, "11/05", 9.8, 718),
        (6, "11/05", 9.8, 155),
        (7, "11/05", 9.7, 939),
        (8, "11/05", 9.7, 615),
    ]
    added = sum(p[3] for p in prs)
    W, H = 1400, 980
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (70, 40), f"確認待ちの変更：8本・+{added:,}行", 42, INK, bold=True)
    text(d, (70, 100), "openのDraft PR 8本。すべてDraftで、レビュー0件・レビュー依頼0件。行数はPRの差分。", 19, SUB)

    label_w, bar_x, bar_max = 250, 70 + 250, 560
    top, row = 170, 82
    scale = bar_max / 6359

    for index, (number, created, age, lines) in enumerate(prs):
        y = top + index * row
        colour = DARKBLUE if created == "10/28" else TEAL
        fill = LIGHTBLUE if created == "10/28" else LIGHTTEAL
        box(d, 70, y, label_w - 20, 54, "#f4f4f4", LIGHTGRAY, 1)
        text(d, (80, y + 8), f"#{number}", 24, colour, bold=True)
        text(d, (80, y + 36), f"{created} ・ {age:.1f}日待ち", 16, SUB)
        width = max(lines * scale, 6)
        box(d, bar_x, y + 6, width, 42, fill, colour, 2)
        text(d, (bar_x + width + 12, y + 27), f"+{lines:,}行", 20, INK, bold=True, anchor="lm")

    # total panel
    px, py, pw, ph = 1050, 170, 300, 330
    box(d, px, py, pw, ph, "#f4f4f4", LIGHTGRAY, 2)
    text(d, (px + 24, py + 24), "合計", 20, SUB)
    text(d, (px + 24, py + 56), f"+{added:,}", 32, DARKBLUE, bold=True)
    text(d, (px + 24, py + 112), "行", 22, SUB)
    d.line((px + 24, py + 158, px + pw - 24, py + 158), fill="#c6c6c6", width=2)
    text(d, (px + 24, py + 176), "レビュー", 18, SUB)
    text(d, (px + 24, py + 202), "0 件", 34, RED, bold=True)
    text(d, (px + 24, py + 248), "merge", 18, SUB)
    text(d, (px + 24, py + 274), "0 件", 34, RED, bold=True)

    note_y = 880
    box(d, 70, note_y, 1260, 58, LIGHTAMBER, "#ffb784", 2)
    text(d, (90, note_y + 18), "レビュー依頼が0件なので、この8本は誰かの確認待ちリストに載っていない。", 21, AMBER, bold=True)

    img.save(path)


if __name__ == "__main__":
    timeline(ROOT / "timeline.png")
    standing(ROOT / "standing.png")
    print("generated", json.dumps({"reports": sum(report_counts().values())}, ensure_ascii=False))
