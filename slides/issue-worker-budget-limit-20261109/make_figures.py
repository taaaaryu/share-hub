#!/usr/bin/env python3
"""Generate the two figures used by this deck."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"

W, H = 2000, 1125
INK = "#161616"
SUB = "#525252"
LINE = "#e0e0e0"
BG = "#ffffff"
PANEL = "#f4f4f4"
BLUE = "#0f62fe"
PURPLE = "#8a3ffc"
GRAY = "#c6c6c6"
RED = "#da1e28"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    index = 1 if bold else 0
    return ImageFont.truetype(FONT, size, index=index)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def box(draw, xy, fill=None, outline=None, width=2, radius=12):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def footnote(draw, value):
    text(draw, (110, 1020), value, 26, SUB)


def status_figure(path: Path) -> None:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    text(d, (110, 80), "対象21件の内訳：着手できるTodoだけが0件", 52, INK, bold=True)
    text(d, (110, 160), "2026-11-09 02:39 JST に Linear から再取得", 28, SUB)

    cards = [
        ("Todo", "0", "着手できる課題。今回の候補", RED, True),
        ("In Progress", "4", "4件とも草案PRあり", BLUE, False),
        ("In Review", "1", "人の確認待ち", PURPLE, False),
        ("Backlog", "16", "計画。実装しない", GRAY, False),
    ]
    x = 110
    for label, value, note, color, highlight in cards:
        box(d, (x, 270, x + 400, 610), fill=BG if highlight else PANEL,
            outline=color if highlight else None, width=6 if highlight else 0)
        text(d, (x + 40, 320), label, 34, SUB, bold=True)
        text(d, (x + 40, 390), value, 120, SUB if color == GRAY else color, bold=True)
        text(d, (x + 40, 540), note, 26, SUB)
        x += 440

    # share bar: backlog 16, in progress 4, in review 1, todo 0
    bar_x0, bar_x1 = 110, 1890
    total = 21
    y0, y1 = 720, 800
    parts = [("Backlog 16", 16, GRAY), ("In Progress 4", 4, BLUE), ("In Review 1", 1, PURPLE)]
    cursor = bar_x0
    for label, count, color in parts:
        width = int((bar_x1 - bar_x0) * count / total)
        d.rectangle((cursor, y0, cursor + width, y1), fill=color)
        cursor += width
    d.rectangle((bar_x0, y0, bar_x1, y1), outline=INK, width=2)

    text(d, (110, 850), "Todo 0 / 21（0%）", 34, RED, bold=True)
    text(d, (110, 905), "workerが選ぶのは Todo だけ。計画は勝手にTodoへ変えない。", 32, INK)
    footnote(d, "出典: Linear 対象project の一覧を worker が読み取り集計 / 個人情報・本文は含まない")
    img.save(path)


def next_figure(path: Path) -> None:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    text(d, (110, 80), "今日の実行枠は上限。次に動かすのは人の1操作", 52, INK, bold=True)
    text(d, (110, 160), "6回の枠を使い切り、Todoが0件のまま停止した", 28, SUB)

    # run budget: 6 squares
    text(d, (110, 250), "今日の実行", 32, SUB, bold=True)
    for i in range(6):
        x = 110 + i * 90
        box(d, (x, 300, x + 70, 370), fill=BLUE)
    text(d, (690, 305), "6 / 6 使用（上限）", 34, INK, bold=True)

    # flow
    boxes = [
        ("人が1操作", "Backlog から1件を\nTodo へ上げる\n推奨: 基準計測 TAA-35", BLUE),
        ("worker 次回起動", "1件だけ選び\n実装してローカルテスト", INK),
        ("結果", "草案PRを作成\nIn Review で停止\nmergeはしない", PURPLE),
    ]
    x = 110
    y0, y1 = 500, 800
    for heading, body, color in boxes:
        box(d, (x, y0, x + 520, y1), fill=PANEL)
        d.rectangle((x, y0, x + 12, y1), fill=color)
        text(d, (x + 40, y0 + 30), heading, 32, color, bold=True)
        d.multiline_text((x + 40, y0 + 100), body, font=font(30), fill=INK, spacing=18)
        if x + 520 < 1600:
            d.line((x + 560, (y0 + y1) // 2, x + 620, (y0 + y1) // 2), fill=SUB, width=5)
            d.polygon([(x + 620, (y0 + y1) // 2), (x + 596, (y0 + y1) // 2 - 14),
                       (x + 596, (y0 + y1) // 2 + 14)], fill=SUB)
        x += 660

    text(d, (110, 870), "上限に達した今日は、ここから先へ進めない。", 32, INK, bold=True)
    text(d, (110, 925), "Todoが増えるまで、workerは計画にもコードにも触らない。", 30, SUB)
    footnote(d, "実行枠は worker の state/runs.json（本日の回数）を読んだ結果。効果や速度の測定値ではない")
    img.save(path)


if __name__ == "__main__":
    status_figure(ROOT / "status.png")
    next_figure(ROOT / "next.png")
    print("ok")
