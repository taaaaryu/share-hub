#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data sources (public-safe aggregates only, measured 2026-11-11):
- issue-worker run logs: one line per run (date, final status). Aggregated per JST day.
- GitHub API: open draft PR numbers, createdAt, isDraft.

No issue bodies, comments, code content or customer data are used.
Only counts, dates and PR numbers appear in the images.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"

INK = "#161616"
SUB = "#525252"
BG = "#ffffff"
PANEL = "#f4f4f4"
BLUE = "#0f62fe"
DARKBLUE = "#0043ce"
LIGHTBLUE = "#d0e2ff"
MIDBLUE = "#78a9ff"
TEAL = "#007d79"
GRAY = "#8d8d8d"
RED = "#da1e28"

# JST day -> (no_issue runs, stopped runs: blocked/timeout)
RUNS = {
    "11/08": (5, 0),
    "11/09": (4, 1),
    "11/10": (5, 0),
    "11/11": (6, 0),
}

# draft PR number -> (age_days, created, last_updated)
PR = {
    1: (14, "10-28", "10-28"),
    2: (14, "10-28", "11-03"),
    3: (14, "10-28", "10-29"),
    4: (6, "11-05", "11-05"),
    5: (6, "11-05", "11-05"),
    6: (6, "11-05", "11-05"),
    7: (6, "11-05", "11-05"),
    8: (6, "11-05", "11-05"),
}


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def runs_by_day(path: Path) -> None:
    W, H = 1400, 900
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (70, 44), "直近4日、21回動いて実装は0件", 46, INK, bold=True)
    text(d, (70, 106), "workerの実行ログを日本時間の日付で集計。青は『Todo 0件で停止』、赤は起動時の停止。", 21, SUB)

    left, top, width, base = 190, 210, 1120, 700
    max_v = 7
    for v in range(0, max_v + 1):
        y = base - (v / max_v) * (base - top)
        d.line((left, y, left + width, y), fill="#e0e0e0", width=1)
        text(d, (left - 22, y), str(v), 20, SUB, anchor="rm")

    slot = width / len(RUNS)
    bw = 96
    for i, (day, (ok, stop)) in enumerate(RUNS.items()):
        cx = left + slot * (i + 0.5)
        total = ok + stop
        bh_stop = (stop / max_v) * (base - top)
        bh_ok = (ok / max_v) * (base - top)
        d.rectangle((cx - bw / 2, base - bh_stop, cx + bw / 2, base), fill=RED)
        d.rectangle((cx - bw / 2, base - bh_ok - bh_stop, cx + bw / 2, base - bh_stop), fill=BLUE)
        text(d, (cx, base - bh_ok - bh_stop - 16), str(total), 32, INK, bold=True, anchor="mb")
        text(d, (cx, base + 18), day, 26, INK, bold=True, anchor="ma")
        text(d, (cx, base + 54), "回", 20, SUB, anchor="ma")

    # zero marker
    d.line((left, base, left + width, base), fill=INK, width=2)
    text(d, (left + width, top - 74), "実装に進んだ run：0件", 28, RED, bold=True, anchor="ra")

    d.rectangle((70, 790, 112, 828), fill=BLUE)
    text(d, (128, 800), "Todo 0件で停止（no_issue）", 22, SUB)
    d.rectangle((520, 790, 562, 828), fill=RED)
    text(d, (578, 800), "起動時の停止（接続・認証）", 22, SUB)
    text(d, (70, 850), "日付は日本時間。21回の内訳は 20回がTodo 0件、1回が起動時の停止。", 21, SUB)

    img.save(path)


def pr_wait(path: Path) -> None:
    W, H = 1400, 980
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (70, 44), "草案PR8件の待ち時間：最長14日・最短6日", 44, INK, bold=True)
    text(d, (70, 106), "GitHub APIの作成日から2026-11-11までの経過日数。8件すべて、いまも草案のまま。", 21, SUB)

    left, top, row_h = 190, 200, 78
    max_days = 14
    bar_max = 700
    for i, (pr, (days, created, updated)) in enumerate(PR.items()):
        y = top + i * row_h
        text(d, (left - 30, y + row_h / 2), f"#{pr}", 28, INK, bold=True, anchor="rm")
        w = (days / max_days) * bar_max
        color = DARKBLUE if days >= 14 else MIDBLUE
        d.rectangle((left, y + 14, left + w, y + row_h - 14), fill=color)
        text(d, (left + w + 16, y + row_h / 2), f"{days}日", 26, INK, bold=True, anchor="lm")
        text(d, (1030, y + row_h / 2), f"作成 {created} ・ 更新 {updated}", 20, SUB, anchor="lm")

    d.line((left, top - 6, left, top + len(PR) * row_h), fill="#c6c6c6", width=2)

    d.rounded_rectangle((70, 850, 1330, 930), radius=12, fill=PANEL)
    text(d, (100, 868), "8件すべて isDraft=true。merge されたものは0件。最終更新から6日以上たっている。", 22, INK)

    img.save(path)


if __name__ == "__main__":
    runs_by_day(ROOT / "runs_by_day.png")
    pr_wait(ROOT / "pr_wait.png")
