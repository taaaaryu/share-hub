#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data sources (public-safe aggregates only, measured 2026-11-12 JST):
- Linear: 21 issues in the target project (status counts, blockedBy relations).
- GitHub: open draft PRs (number, createdAt, isDraft).

No issue bodies, titles, comments, code or customer data appear in the images.
Issue names are replaced by neutral letters; only counts and relations are drawn.
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
LIGHTRED = "#fff1f1"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def box(draw, x, y, w, h, fill, border, width=2):
    draw.rectangle((x, y, x + w, y + h), fill=fill, outline=border, width=width)


def arrow(draw, x1, y1, x2, y2, color, width=3, dashed=False):
    import math

    if dashed:
        total = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        steps = max(1, int(total // 14))
        for i in range(steps):
            if i % 2:
                continue
            ax = x1 + (x2 - x1) * i / steps
            ay = y1 + (y2 - y1) * i / steps
            bx = x1 + (x2 - x1) * (i + 1) / steps
            by = y1 + (y2 - y1) * (i + 1) / steps
            draw.line((ax, ay, bx, by), fill=color, width=width)
    else:
        draw.line((x1, y1, x2, y2), fill=color, width=width)
    angle = math.atan2(y2 - y1, x2 - x1)
    size = 13
    p1 = (x2 - size * math.cos(angle - 0.42), y2 - size * math.sin(angle - 0.42))
    p2 = (x2 - size * math.cos(angle + 0.42), y2 - size * math.sin(angle + 0.42))
    draw.polygon([(x2, y2), p1, p2], fill=color)


def dependency(path: Path) -> None:
    W, H = 1400, 900
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (70, 44), "レビュー待ち1件が、Backlog 6件の前提になっている", 44, INK, bold=True)
    text(d, (70, 104), "LinearのblockedByを2026-11-12に取得。課題名は伏せ、つながりと件数だけを描いた。", 21, SUB)

    text(d, (90, 160), "いま詰まっている所", 20, RED, bold=True)
    text(d, (470, 160), "それを前提にしている課題", 20, DARKBLUE, bold=True)
    text(d, (1130, 160), "さらに先", 20, SUB, bold=True)

    box(d, 90, 300, 240, 180, LIGHTRED, RED, 3)
    text(d, (210, 340), "In Review", 30, RED, bold=True, anchor="ma")
    text(d, (210, 382), "1件", 34, INK, bold=True, anchor="ma")
    text(d, (210, 428), "草案PR・作成15日", 20, SUB, anchor="ma")

    l1 = [("課題A", 210), ("課題B", 315), ("課題C", 420), ("課題D", 525)]
    for name, y in l1:
        box(d, 470, y, 210, 80, "#edf5ff", DARKBLUE, 2)
        text(d, (575, y + 24), name, 26, DARKBLUE, bold=True, anchor="ma")
        text(d, (575, y + 54), "Backlog", 18, SUB, anchor="ma")
        arrow(d, 334, 390, 466, y + 40, DARKBLUE)

    box(d, 830, 250, 220, 80, LIGHTBLUE, MIDBLUE, 2)
    text(d, (940, 274), "課題E", 26, DARKBLUE, bold=True, anchor="ma")
    text(d, (940, 304), "Backlog", 18, SUB, anchor="ma")
    arrow(d, 684, 250, 826, 286, MIDBLUE)
    arrow(d, 684, 355, 826, 300, MIDBLUE)

    box(d, 1130, 385, 220, 80, "#f0f4ff", "#a6c8ff", 2)
    text(d, (1240, 409), "課題F", 26, DARKBLUE, bold=True, anchor="ma")
    text(d, (1240, 439), "Backlog", 18, SUB, anchor="ma")
    arrow(d, 1054, 290, 1126, 405, "#a6c8ff")
    arrow(d, 684, 462, 1126, 430, "#a6c8ff")
    arrow(d, 684, 560, 1126, 452, "#a6c8ff")

    box(d, 830, 640, 220, 80, PANEL, GRAY, 2)
    text(d, (940, 664), "別の課題G", 26, SUB, bold=True, anchor="ma")
    text(d, (940, 694), "Backlog・今回の対象外", 17, SUB, anchor="ma")
    arrow(d, 1054, 680, 1126, 455, GRAY, 2, dashed=True)

    text(d, (90, 500), "直接の下流", 20, SUB)
    text(d, (90, 532), "4件", 40, DARKBLUE, bold=True)
    text(d, (240, 500), "連鎖を含む", 20, SUB)
    text(d, (240, 532), "6件", 40, INK, bold=True)

    text(d, (70, 800), "ただし、最後の1件（課題F）は別の前提（課題G）も残る。レビュー1件だけでは全部は動かない。", 21, SUB)
    text(d, (70, 838), "図の箱は1件＝1課題。赤はレビュー待ち、青はそれを前提にするBacklog、灰色は今回の対象外の前提。", 19, SUB)

    img.save(path)


def composition(path: Path) -> None:
    W, H = 1400, 780
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (70, 44), "21件のうち、着手できるTodoは0件", 44, INK, bold=True)
    text(d, (70, 104), "対象プロジェクトの全21件を2026-11-12に数えた。Backlog 16件の半分は依存待ち。", 21, SUB)

    tile_w, tile_h, gap, group_gap = 42, 62, 6, 44
    pitch = tile_w + gap
    left = 150
    y1 = 250

    def tiles(x, n, color):
        for i in range(n):
            d.rectangle((x + i * pitch, y1, x + i * pitch + tile_w, y1 + tile_h), fill=color)
        return x + n * pitch - gap

    def caption(x, name, count, color):
        text(d, (x, y1 - 52), name, 21, SUB, bold=True)
        text(d, (x, y1 - 22), count, 24, color, bold=True)

    d.rectangle((left, y1, left + tile_w, y1 + tile_h), fill=BG, outline=GRAY, width=2)
    text(d, (left + tile_w / 2, y1 + tile_h / 2), "0", 26, GRAY, bold=True, anchor="mm")
    caption(left - 4, "Todo", "0件", GRAY)

    x = left + tile_w + group_gap
    right = tiles(x, 16, BLUE)
    caption(x, "Backlog", "16件", DARKBLUE)

    x = right + group_gap
    right = tiles(x, 4, TEAL)
    caption(x, "In Progress", "4件", TEAL)

    x = right + group_gap
    right = tiles(x, 1, RED)
    caption(x, "In Review", "1件", RED)

    y2 = 470
    text(d, (131, y2 - 46), "Backlog 16件の内訳", 23, INK, bold=True)

    def row2_tiles(x, n, color):
        for i in range(n):
            d.rectangle((x + i * pitch, y2, x + i * pitch + tile_w, y2 + tile_h), fill=color)
        return x + n * pitch - gap

    r2a = row2_tiles(left, 8, DARKBLUE)
    text(d, (left, y2 + tile_h + 22), "8件", 26, DARKBLUE, bold=True)
    text(d, (left, y2 + tile_h + 54), "未完了の前提がある", 19, SUB)

    x2 = r2a + group_gap
    r2b = row2_tiles(x2, 8, MIDBLUE)
    text(d, (x2, y2 + tile_h + 22), "8件", 26, MIDBLUE, bold=True)
    text(d, (x2, y2 + tile_h + 54), "前提がなく、Todoにできる", 19, SUB)

    d.rectangle((70, 690, 98, 714), fill=BG, outline=GRAY, width=2)
    text(d, (110, 690), "Todo（空き）", 20, SUB)
    d.rectangle((300, 690, 328, 714), fill=RED)
    text(d, (340, 690), "レビュー待ち", 20, SUB)
    d.rectangle((500, 690, 528, 714), fill=DARKBLUE)
    text(d, (540, 690), "依存待ちのBacklog", 20, SUB)
    d.rectangle((760, 690, 788, 714), fill=MIDBLUE)
    text(d, (800, 690), "前提のないBacklog", 20, SUB)
    text(d, (70, 744), "四角1つ＝課題1件。前提のない8件のうち1件はEpicで、Todoへ移すかは人が決める（workerは自動昇格しない）。", 19, SUB)

    img.save(path)


if __name__ == "__main__":
    dependency(ROOT / "dependency_chain.png")
    composition(ROOT / "issue_composition.png")
    print("wrote figures")
