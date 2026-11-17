#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data source (public-safe aggregates only, checked 2026-11-18 JST):
- worker execution history under the local issue-worker state directory:
  3 once-runs today, latest run about 12 minutes, 2 published decks.
- Linear project f7f3a327-a06b-478f-bd88-c49fc2b79cef: 21 issues, 0 in Todo.
- private remote thumaster: 8 open Draft PRs, all mergeable=clean.
- local experiments repo: 0 new commits since 2026-11-17 23:00 JST.

Issue titles, bodies, comments, branch names, PR titles and customer data are
not drawn. Only counts and state names.
"""
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
GRAY = "#6f6f6f"
LIGHTGRAY = "#f4f4f4"
BORDERGRAY = "#c6c6c6"
GREEN = "#0e6027"
LIGHTGREEN = "#defbe6"
RED = "#da1e28"
LIGHTRED = "#fff1f1"


def font(size, bold=False):
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def box(draw, x, y, w, h, fill, border, width=2, radius=None):
    if radius:
        draw.rounded_rectangle((x, y, x + w, y + h), radius=radius, fill=fill, outline=border, width=width)
    else:
        draw.rectangle((x, y, x + w, y + h), fill=fill, outline=border, width=width)


def arrow(draw, x1, y1, x2, y2, color=GRAY, width=5):
    draw.line((x1, y1, x2, y2), fill=color, width=width)
    head = 12
    if x2 >= x1:
        draw.polygon([(x2, y2), (x2 - head, y2 - head), (x2 - head, y2 + head)], fill=color)
    else:
        draw.polygon([(x2, y2), (x2 + head, y2 - head), (x2 + head, y2 + head)], fill=color)


def run_spend(path):
    """Left: 3 runs. Right: what they produced."""
    W, H = 2000, 1125
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (100, 70), "同じ日に4回動いて、残ったのは資料3本", 62, INK, bold=True)
    text(d, (100, 160), "2026-11-18 JST。1回＝workerの1実行。数字は今日の実測値。", 26, SUB)

    # ---- left: runs
    text(d, (100, 235), "起動した回", 28, SUB, bold=True)
    runs = [
        ("1回目", "Todo 0件で終了", "資料なし・記録のみ"),
        ("2回目", "Todo 0件で終了", "診断資料 1本"),
        ("3回目", "Todo 0件で終了", "手順資料 1本"),
        ("4回目", "Todo 0件で終了", "この資料"),
    ]
    for i, (name, result, out) in enumerate(runs):
        y = 285 + i * 160
        box(d, 100, y, 640, 136, "#fafafa", BORDERGRAY, 2, radius=8)
        text(d, (130, y + 18), name, 28, INK, bold=True)
        text(d, (130, y + 60), result, 22, RED)
        text(d, (130, y + 96), out, 20, SUB)

    text(d, (100, 985), "直近1回の所要は約12分（待ち時間を含む）", 22, SUB)

    # ---- arrow
    arrow(d, 790, 560, 900, 560, BLUE, 8)
    text(d, (845, 505), "成果", 24, BLUE, anchor="mm")

    # ---- right: outputs
    text(d, (940, 235), "残ったもの", 28, SUB, bold=True)
    items = [
        ("公開した資料", "3本", GREEN, LIGHTGREEN),
        ("書いたコード", "0行", RED, LIGHTRED),
        ("新しいブランチ", "0本", RED, LIGHTRED),
        ("新しいPR", "0件", RED, LIGHTRED),
    ]
    for i, (label, value, color, fill) in enumerate(items):
        y = 285 + i * 160
        box(d, 940, y, 470, 136, fill, color, 3, radius=8)
        text(d, (970, y + 26), label, 26, color, bold=True)
        text(d, (970, y + 68), value, 42, color, bold=True)

    # ---- note panel
    px, py, pw, ph = 1470, 290, 430, 560
    box(d, px, py, pw, ph, "#f4f4f4", BORDERGRAY, 2, radius=8)
    text(d, (px + 26, py + 26), "この形が続くと", 26, INK, bold=True)
    lines = [
        "入口のTodoは0件のまま",
        "診断資料だけが増える",
        "読む人の負担が増える",
        "実装は1行も進まない",
    ]
    for i, line in enumerate(lines):
        text(d, (px + 26, py + 90 + i * 58), "・" + line, 22, SUB)
    text(d, (px + 26, py + 92 + 4 * 58), "→ 回し方を決める", 24, RED, bold=True)

    img.save(path)


def loop_choice(path):
    """Two panels: today's loop vs the proposed loop."""
    W, H = 2000, 1125
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (100, 70), "Todoが0件の日、workerは何をするか", 60, INK, bold=True)
    text(d, (100, 158), "左がいまの動き。右が提案。提案は未承認で、効果もまだ測っていない。", 26, SUB)

    # ---- left panel: current
    lx, ly, lw, lh = 100, 235, 850, 820
    box(d, lx, ly, lw, lh, LIGHTRED, RED, 3, radius=10)
    text(d, (lx + 34, ly + 26), "いま（C）", 34, RED, bold=True)
    text(d, (lx + 34, ly + 74), "診断資料を作って終了", 26, INK, bold=True)

    steps = [
        ("起動する", "Todoを確認"),
        ("0件を確認", "21件を取り直す"),
        ("原因を調べる", "PR・依存を数える"),
        ("資料を公開", "同じ結論を図解"),
        ("翌日また同じ", "コードは0行のまま"),
    ]
    for i, (head, sub) in enumerate(steps):
        y = ly + 140 + i * 132
        box(d, lx + 60, y, 730, 96, "#ffffff", BORDERGRAY, 2, radius=8)
        text(d, (lx + 88, y + 22), head, 26, INK, bold=True)
        text(d, (lx + 88, y + 58), sub, 20, SUB)
        if i < len(steps) - 1:
            arrow(d, lx + 425, y + 96, lx + 425, y + 132, RED, 4)

    # ---- right panel: proposal
    rx, ry, rw, rh = 1050, 235, 850, 820
    box(d, rx, ry, rw, rh, LIGHTGREEN, GREEN, 3, radius=10)
    text(d, (rx + 34, ry + 26), "提案（A + B）", 34, GREEN, bold=True)
    text(d, (rx + 34, ry + 74), "空振りを1回で止める", 26, INK, bold=True)

    steps2 = [
        ("起動する", "前回と同じ検査だけ"),
        ("0件を確認", "ここで打ち切る"),
        ("起動をスキップ", "run数と時間を温存"),
        ("計画を1本だけ", "Backlogに案を残す"),
        ("人が入口を開ける", "Todo 1件 → 次回実装"),
    ]
    for i, (head, sub) in enumerate(steps2):
        y = ry + 140 + i * 132
        fill = LIGHTGREEN if i < 4 else "#ffffff"
        box(d, rx + 60, y, 730, 96, fill, GREEN if i == 4 else BORDERGRAY, 2, radius=8)
        text(d, (rx + 88, y + 22), head, 26, INK, bold=True)
        text(d, (rx + 88, y + 58), sub, 20, SUB)
        if i < len(steps2) - 1:
            arrow(d, rx + 425, y + 96, rx + 425, y + 132, GREEN, 4)

    img.save(path)


def main():
    run_spend(ROOT / "runspend.png")
    loop_choice(ROOT / "loop.png")
    print("wrote runspend.png, loop.png")


if __name__ == "__main__":
    main()
