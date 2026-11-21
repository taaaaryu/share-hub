#!/usr/bin/env python3
"""Figures for the 2026-11-22 issue-worker run deck.

Public-safe aggregate data only, read on 2026-11-22:
- project: 21 issues = Backlog 16 / Todo 0 / In Progress 4 / In Review 1.
- Backlog 16 = 3 (no dependency, High) / 4 (no dependency, Medium or Low) /
  8 (waiting on an unfinished issue) / 1 (parent epic).
- private repo: 8 open pull requests, all drafts, all MERGEABLE/CLEAN, 0 merged.

Only counts, gate names and state names are drawn. No issue titles, bodies,
comments, branch names, PR titles or customer data.
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


def figure_state():
    img, d = canvas("課題21件はTodoが0件、PRは8本がDraftのまま", "STATE / 2026-11-22")

    # --- left: issue states as a 21-cell grid, 7 per row ---
    text(d, (90, 210), "対象プロジェクトの課題 21件", 34, INK, True)
    cells = (["Backlog"] * 16) + (["In Progress"] * 4) + (["In Review"] * 1)
    colors = {
        "Backlog": (LIGHTGRAY, GRAY, "Backlog 16"),
        "In Progress": (LIGHTBLUE, BLUE, "In Progress 4"),
        "In Review": (LIGHTAMBER, AMBER, "In Review 1"),
    }
    size, gap = 104, 16
    x0, y0 = 90, 268
    for index in range(21):
        row, col = divmod(index, 7)
        x = x0 + col * (size + gap)
        y = y0 + row * (size + gap)
        state = cells[index]
        fill, line, _ = colors[state]
        d.rounded_rectangle((x, y, x + size, y + size), radius=12, fill=fill, outline=line, width=3)
    # one empty Todo slot, drawn as a dashed outline
    x = x0 + 7 * (size + gap) + 24
    for i in range(0, size, 22):
        d.line((x + i, y0, x + min(i + 12, size), y0), fill=RED, width=4)
        d.line((x + i, y0 + size, x + min(i + 12, size), y0 + size), fill=RED, width=4)
        d.line((x, y0 + i, x, y0 + min(i + 12, size)), fill=RED, width=4)
        d.line((x + size, y0 + i, x + size, y0 + min(i + 12, size)), fill=RED, width=4)
    text(d, (x + size / 2, y0 + size / 2), "0", 56, RED, True, anchor="mm")
    text(d, (x + size / 2, y0 + size + 18), "Todo（空）", 28, RED, True, anchor="ma")

    # legend
    legend_y = y0 + 3 * (size + gap) + 16
    lx = 90
    for state in ("Backlog", "In Progress", "In Review"):
        fill, line, label = colors[state]
        d.rounded_rectangle((lx, legend_y, lx + 34, legend_y + 34), radius=8, fill=fill, outline=line, width=3)
        text(d, (lx + 48, legend_y + 3), label, 28, INK)
        lx += 300
    text(d, (90, legend_y + 62), "workerが実装できるのは Todo 状態だけ。今日は1件も無い。", 30, SUB)

    note_y = legend_y + 140
    d.rounded_rectangle((90, note_y, 1210, note_y + 250), radius=16, fill=LIGHTGRAY, outline=BORDERGRAY, width=2)
    text(d, (126, note_y + 30), "なぜ止まるのか", 30, INK, True)
    text(d, (126, note_y + 88), "・Todoへ移すのは人の判断。workerは自分でBacklogを動かさない。", 27, SUB)
    text(d, (126, note_y + 136), "・Backlogは計画案まで。コードを書く対象にはならない。", 27, SUB)
    text(d, (126, note_y + 184), "・進行中4件とレビュー待ち1件は、選ぶ対象から外れている。", 27, SUB)

    # --- right: PR panel ---
    px, py, pw, ph = 1290, 210, 620, 560
    d.rounded_rectangle((px, py, px + pw, py + ph), radius=20, fill=LIGHTBLUE, outline=BLUE, width=3)
    text(d, (px + 40, py + 34), "非公開リポジトリのPR", 32, BLUE, True)
    text(d, (px + 40, py + 96), "8", 150, INK, True)
    text(d, (px + 190, py + 168), "本すべて Draft", 34, INK, True)
    text(d, (px + 40, py + 250), "merge済み  0本", 34, AMBER, True)
    text(d, (px + 40, py + 312), "MERGEABLE / CLEAN  8本", 28, GREEN, True)
    text(d, (px + 40, py + 360), "（2026-11-22 に gh で確認）", 24, SUB)
    d.line((px + 40, py + 404, px + pw - 40, py + 404), fill=BORDERGRAY, width=2)
    text(d, (px + 40, py + 428), "レビュー待ちのまま 17-25日経過", 28, INK)
    text(d, (px + 40, py + 472), "最終更新: 10/28 - 11/05", 26, SUB)

    footer(d, "出典: Linear の状態別件数と gh pr list（読み取りのみ）。課題名・本文・コードは描いていない。")
    img.save(ROOT / "state_breakdown.png")


def figure_unlock():
    img, d = canvas("Backlog 16件のうち、今日動かせるのは3件", "UNLOCK / 依存の内訳")

    rows = [
        ("今すぐTodoへ移せる（依存なし・高）", 3, BLUE, LIGHTBLUE),
        ("依存なし・中/低（GPUや研究が前提）", 4, GRAY, LIGHTGRAY),
        ("未完了の依存で停止", 8, AMBER, LIGHTAMBER),
        ("Epic（親課題。単体では実装しない）", 1, GRAY, LIGHTGRAY),
    ]
    bar_x, bar_w, row_h = 760, 1040, 96
    y = 220
    unit = bar_w / 16
    for label, count, line, fill in rows:
        text(d, (90, y + 26), label, 32, INK)
        width = max(unit * count, 8)
        d.rounded_rectangle((bar_x, y, bar_x + width, y + 64), radius=10, fill=fill, outline=line, width=3)
        text(d, (bar_x + width + 24, y + 8), f"{count}件", 40, line, True)
        y += row_h + 26

    # dependency example
    y += 24
    d.line((90, y, W - 90, y), fill=BORDERGRAY, width=2)
    y += 34
    text(d, (90, y), "レビュー待ちのPR 1本をmergeすると", 32, INK, True)
    y += 60
    boxes = [
        ("PR #1（レビュー待ち）", BLUE, LIGHTBLUE),
        ("依存が解ける 2件", GREEN, LIGHTGREEN),
        ("この先の連鎖は未確定", GRAY, LIGHTGRAY),
    ]
    bx = 90
    for index, (label, line, fill) in enumerate(boxes):
        width = 520
        d.rounded_rectangle((bx, y, bx + width, y + 96), radius=14, fill=fill, outline=line, width=3)
        text(d, (bx + width / 2, y + 34), label, 30, line, True, anchor="ma")
        bx += width
        if index < 2:
            text(d, (bx + 26, y + 22), "→", 44, GRAY, True, anchor="ma")
            bx += 110

    footer(d, "出典: Linear の blockedBy / blocks 関係。件数は今日のスナップショット。連鎖の件数は数えていない。")
    img.save(ROOT / "unlock_map.png")


if __name__ == "__main__":
    figure_state()
    figure_unlock()
    print("wrote state_breakdown.png, unlock_map.png")
