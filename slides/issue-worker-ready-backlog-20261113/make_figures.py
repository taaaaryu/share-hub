#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data source (public-safe aggregates only, measured 2026-11-13 00:44 JST):
- Linear project issue list: 21 issues, status counts.
- Dependency relations between the 16 Backlog issues.

Issue identifiers, titles, bodies, comments, assignees, branch names, code and
customer data do not appear in the images. Nodes are anonymised; only counts,
state names, priority buckets and the shape of the dependency graph are drawn.
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
DARKBLUE = "#0043ce"
TEAL = "#007d79"
LIGHTTEAL = "#d9fbfb"
GREEN = "#198038"
LIGHTGREEN = "#defbe6"
AMBER = "#8a3800"
LIGHTAMBER = "#fff2e8"
GRAY = "#8d8d8d"
LIGHTGRAY = "#e0e0e0"
RED = "#da1e28"
LIGHTRED = "#fff1f1"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def box(draw, x, y, w, h, fill, border, width=2):
    draw.rectangle((x, y, x + w, y + h), fill=fill, outline=border, width=width)


def arrow(draw, x1, y1, x2, y2, color=GRAY, width=3):
    draw.line((x1, y1, x2, y2), fill=color, width=width)
    r = 7
    draw.polygon(
        [(x2, y2), (x2 - r, y2 - r * 0.7), (x2 - r, y2 + r * 0.7)],
        fill=color,
    )


def split(path: Path) -> None:
    W, H = 1400, 820
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (70, 44), "Backlog 16件を、依存関係で分ける", 46, INK, bold=True)
    text(d, (70, 110), "2026-11-13 00:44 JST。Linearの対象プロジェクトから取得した状態と依存関係の集計。", 21, SUB)

    cards = [
        ("依存が空", "7件", "すぐTodoに置ける。Highが3件。", GREEN, LIGHTGREEN),
        ("依存待ち", "8件", "未完了の前提課題がある。", AMBER, LIGHTAMBER),
        ("Epic", "1件", "まとめ役。単体では数えない。", GRAY, "#f4f4f4"),
    ]
    card_y, card_h, card_w, gap = 190, 250, 400, 30
    for i, (name, count, note, color, pale) in enumerate(cards):
        x = 70 + i * (card_w + gap)
        box(d, x, card_y, card_w, card_h, pale, color, 3)
        text(d, (x + 28, card_y + 30), name, 26, color, bold=True)
        text(d, (x + 28, card_y + 78), count, 64, INK, bold=True)
        text(d, (x + 28, card_y + 168), note, 20, SUB)

    # 16-cell strip
    strip_y, cell_w, cell_h, cell_gap = 540, 66, 66, 12
    start_x = 70
    order = [
        (GREEN, LIGHTGREEN),
    ] * 7 + [
        (AMBER, LIGHTAMBER),
    ] * 8 + [
        (GRAY, "#f4f4f4"),
    ] * 1
    for i, (color, pale) in enumerate(order):
        x = start_x + i * (cell_w + cell_gap)
        box(d, x, strip_y, cell_w, cell_h, pale, color, 2)
    text(d, (start_x, strip_y + 92), "16件を1マス1件で並べた図。緑＝依存が空、橙＝依存待ち、灰＝Epic。", 20, SUB)

    # Todo gate banner
    box(d, 70, 700, 1260, 76, LIGHTRED, RED, 3)
    text(d, (96, 714), "Todo 0件", 30, RED, bold=True)
    text(d, (300, 722), "workerが今日始められるのは0件。緑の7件は、人がTodoへ移したときだけ動き出す。", 23, INK)

    img.save(path)


def dependency(path: Path) -> None:
    W, H = 1400, 900
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (70, 44), "1件のレビュー待ちが、6件の前提になっている", 46, INK, bold=True)
    text(d, (70, 110), "依存待ち8件のうち6件は、同じレビュー待ち1件から連鎖している。", 21, SUB)

    # Chain panel
    panel_x, panel_y, panel_w, panel_h = 70, 170, 800, 590
    box(d, panel_x, panel_y, panel_w, panel_h, "#fafafa", LIGHTGRAY, 2)
    text(d, (panel_x + 26, panel_y + 20), "依存の鎖（1つの丸＝1件の課題）", 24, INK, bold=True)

    def node(cx, cy, label, state, color, pale, w=160, h=62):
        box(d, cx - w // 2, cy - h // 2, w, h, pale, color, 3)
        text(d, (cx, cy - 12), label, 20, INK, bold=True, anchor="mm")
        text(d, (cx, cy + 14), state, 16, color, anchor="mm")

    # Longest chain: review -> A -> B -> final
    text(d, (panel_x + 26, panel_y + 78), "最長の鎖：4件が一直線に待つ", 20, SUB, bold=True)
    y1 = panel_y + 160
    xs = [panel_x + 125, panel_x + 310, panel_x + 495, panel_x + 680]
    labels = [("レビュー待ち", "In Review", AMBER, LIGHTAMBER),
              ("依存A", "Backlog", AMBER, LIGHTAMBER),
              ("依存B", "Backlog", AMBER, LIGHTAMBER),
              ("最終工程", "Backlog", AMBER, LIGHTAMBER)]
    for cx, (label, state, color, pale) in zip(xs, labels):
        node(cx, y1, label, state, color, pale, w=150)
    for i in range(3):
        arrow(d, xs[i] + 75, y1, xs[i + 1] - 75, y1)

    # Branch row
    text(d, (panel_x + 270, panel_y + 250), "同じレビュー待ちから分岐する3件", 20, SUB, bold=True)
    y2 = panel_y + 355
    bx = [panel_x + 200, panel_x + 400, panel_x + 600]
    for i, cx in enumerate(bx):
        node(cx, y2, f"分岐{i + 1}", "Backlog", AMBER, LIGHTAMBER, w=150)
    # curvy-ish connectors from the review node down to the branch row
    for cx in bx:
        d.line((xs[0], y1 + 31, xs[0], y2 - 60, cx, y2 - 60, cx, y2 - 31), fill=GRAY, width=3)
        d.polygon([(cx, y2 - 31), (cx - 6, y2 - 42), (cx + 6, y2 - 42)], fill=GRAY)

    text(d, (panel_x + 26, panel_y + 470), "合計6件が、レビュー待ち1件を起点にしている。", 22, INK, bold=True)
    text(d, (panel_x + 26, panel_y + panel_h - 42), "丸の位置と本数だけを示す図。課題番号・題名・担当者は描いていない。", 18, SUB)

    # Breakdown panel
    bx0, by, bw, bh = 910, 170, 420, 590
    box(d, bx0, by, bw, bh, PALE, BLUE, 2)
    text(d, (bx0 + 26, by + 20), "依存待ち8件の内訳", 24, INK, bold=True)

    rows = [
        ("レビュー待ちの連鎖", 6, AMBER),
        ("先行作業待ち", 1, BLUE),
        ("進行中タスク待ち", 1, TEAL),
    ]
    top, row_h = by + 100, 110
    for i, (name, count, color) in enumerate(rows):
        y = top + i * row_h
        text(d, (bx0 + 26, y), name, 22, INK)
        bar_w = max(int(190 * count / 6), 6)
        box(d, bx0 + 26, y + 38, bar_w, 34, color, color, 1)
        text(d, (bx0 + 26 + bar_w + 14, y + 46), f"{count}件", 30, INK, bold=True)

    box(d, bx0 + 26, by + 430, bw - 52, 120, BG, LIGHTGRAY, 1)
    text(d, (bx0 + 46, by + 448), "依存が空の7件のうち", 20, SUB)
    text(d, (bx0 + 46, by + 480), "High優先度は 3件", 32, GREEN, bold=True)
    text(d, (bx0 + 46, by + 520), "Medium 2件 ／ Low 2件", 18, SUB)

    img.save(path)


if __name__ == "__main__":
    split(ROOT / "backlog_split.png")
    dependency(ROOT / "dependency.png")
    print("wrote backlog_split.png and dependency.png")
