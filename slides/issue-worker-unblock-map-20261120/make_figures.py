#!/usr/bin/env python3
"""Figures for the 2026-11-20 unblock map deck.

Public-safe data only (read 2026-11-20 JST):
- Linear project f7f3a327 (team TAA): 21 issues.
  Backlog 17, In Progress 4, In Review 1, Todo 0, Done 0.
- blockedBy relations: TAA-45 <- 43,44 / TAA-46 <- 44 / TAA-47 <- 45,46
  TAA-48 <- 44 / TAA-49 <- 44,45 / TAA-50 <- 35,47,48,49.
- Unblocked Backlog (epic excluded): 43, 35, 36, 38, 39, 40, 41.

Only identifiers, coarse category labels, counts and status names are drawn.
No issue titles, bodies, comments, code or customer data.
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
GREEN = "#0e6027"
LIGHTGREEN = "#defbe6"

W, H = 2000, 1125


def font(size, bold=False):
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def node(draw, x, y, w, h, label, name, status, fill, accent, dashed=False):
    if dashed:
        for x0 in range(x, x + w, 16):
            draw.line((x0, y, min(x0 + 9, x + w), y), fill=accent, width=3)
            draw.line((x0, y + h, min(x0 + 9, x + w), y + h), fill=accent, width=3)
        for y0 in range(y, y + h, 16):
            draw.line((x, y0, x, min(y0 + 9, y + h)), fill=accent, width=3)
            draw.line((x + w, y0, x + w, min(y0 + 9, y + h)), fill=accent, width=3)
    else:
        draw.rectangle((x, y, x + w, y + h), fill=fill, outline=accent, width=3)
    draw.rectangle((x, y, x + 8, y + h), fill=accent)
    text(draw, (x + 26, y + 14), label, 32, INK, bold=True)
    text(draw, (x + 26, y + 58), name, 22, SUB)
    text(draw, (x + 26, y + 86), status, 20, accent, bold=True)


def arrowhead(draw, xy, color):
    x, y = xy
    draw.polygon([(x, y), (x - 15, y - 9), (x - 15, y + 9)], fill=color)


def arrow_up(draw, xy, color):
    x, y = xy
    draw.polygon([(x, y), (x - 9, y + 15), (x + 9, y + 15)], fill=color)


def elbow(draw, sx, sy, tx, ty, offset=0, color=BORDERGRAY):
    """Route right -> gap -> target with an orthogonal elbow."""
    xm = (sx + tx) / 2 + offset
    draw.line((sx, sy, xm, sy), fill=color, width=3)
    draw.line((xm, sy, xm, ty), fill=color, width=3)
    draw.line((xm, ty, tx - 16, ty), fill=color, width=3)
    arrowhead(draw, (tx, ty), color)


def elbow_bottom(draw, sx, sy, tx, ty, y_route, color=BORDERGRAY):
    """Route down -> across the bottom margin -> up into the target."""
    draw.line((sx, sy, sx, y_route), fill=color, width=3)
    draw.line((sx, y_route, tx, y_route), fill=color, width=3)
    draw.line((tx, y_route, tx, ty + 16), fill=color, width=3)
    arrow_up(draw, (tx, ty), color)


def status_figure() -> None:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    text(d, (80, 64), "21件の状態内訳（2026-11-20 時点）", 52, INK, bold=True)
    text(d, (80, 138), "workerが実装を始められるのは Todo だけ。今日は 0 件だった。", 32, SUB)

    rows = [
        ("Backlog", 16, GRAY, LIGHTGRAY, "計画段階。workerは実装しない"),
        ("In Progress", 4, BLUE, LIGHTBLUE, "他のrunが実行中"),
        ("In Review", 1, AMBER, LIGHTAMBER, "PRがレビュー待ち"),
        ("Todo", 0, GREEN, LIGHTGREEN, "workerが着手できる唯一の状態"),
    ]
    left, top, plot_w, row_h, gap = 420, 240, 1180, 92, 34
    total = 21
    for i, (name, count, accent, fill, note) in enumerate(rows):
        y = top + i * (row_h + gap)
        text(d, (80, y + 16), name, 30, INK, bold=True)
        text(d, (80, y + 58), note, 21, SUB)
        bar_w = plot_w * count / total
        if count == 0:
            d.rectangle((left, y, left + 4, y + row_h), fill=accent)
            text(d, (left + 24, y + 24), "0 件", 36, accent, bold=True)
        else:
            d.rectangle((left, y, left + bar_w, y + row_h), fill=fill)
            d.rectangle((left, y, left + bar_w, y + 6), fill=accent)
            text(d, (left + bar_w + 20, y + 22), f"{count} 件", 36, accent, bold=True)

    d.rectangle((80, 800, 1920, 940), fill=LIGHTGRAY)
    d.rectangle((80, 800, 92, 940), fill=GRAY)
    text(d, (130, 824), "今日の実行で起きたこと", 26, SUB)
    text(d, (130, 868), "Todo が 0 件のため、選べる課題が無く、コード・PR・Linear の状態を変えずに終了した。", 28, INK, bold=True)

    text(d, (80, H - 70), "出典: Linear project f7f3a327 の読み取り値。課題本文・コード・顧客情報は描画していない。", 24, GRAY)
    img.save(ROOT / "status.png")
    print("wrote", ROOT / "status.png")


def deps_figure() -> None:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    text(d, (80, 60), "HUD変化検出まわりの依存関係", 52, INK, bold=True)
    text(d, (80, 132), "矢印の先は、手前の課題が完了するまで着手できない。", 30, SUB)

    bw, bh = 330, 120
    cols = {1: 60, 2: 520, 3: 980, 4: 1440}
    nodes = {
        "TAA-44": (cols[1], 200, "In Review", "共通部品 / PR #1", BLUE, LIGHTBLUE),
        "TAA-43": (cols[1], 640, "Backlog", "テストデータ", GRAY, LIGHTGRAY),
        "TAA-46": (cols[2], 200, "Backlog", "時系列トリガー", GRAY, LIGHTGRAY),
        "TAA-45": (cols[2], 420, "Backlog", "差分方式の比較", GRAY, LIGHTGRAY),
        "TAA-48": (cols[2], 640, "Backlog", "判断ログ", GRAY, LIGHTGRAY),
        "TAA-47": (cols[3], 260, "Backlog", "OCRゲート統合", GRAY, LIGHTGRAY),
        "TAA-49": (cols[3], 500, "Backlog", "処理費用の計測", GRAY, LIGHTGRAY),
        "TAA-50": (cols[4], 380, "Backlog", "段階有効化", GRAY, LIGHTGRAY),
    }
    for label, (x, y, status, name, accent, fill) in nodes.items():
        node(d, x, y, bw, bh, label, name, status, fill, accent)

    edges = [
        ("TAA-44", "TAA-46", 0),
        ("TAA-44", "TAA-45", 14),
        ("TAA-43", "TAA-45", 0),
        ("TAA-44", "TAA-48", 28),
        ("TAA-45", "TAA-47", 0),
        ("TAA-46", "TAA-47", 14),
        ("TAA-45", "TAA-49", 0),
        ("TAA-47", "TAA-50", 0),
        ("TAA-49", "TAA-50", 14),
    ]
    for a, b, off in edges:
        ax, ay, _, _, _, _ = nodes[a]
        bx, by, _, _, _, _ = nodes[b]
        elbow(d, ax + bw, ay + 26, bx, by + 26, offset=off)

    # TAA-48 sits one layer above TAA-50, so route that edge under the boxes.
    ax, ay, _, _, _, _ = nodes["TAA-48"]
    bx, by, _, _, _, _ = nodes["TAA-50"]
    elbow_bottom(d, ax + bw / 2, ay + bh, bx + bw / 2, by + bh, 830)

    node(d, 60, 880, bw, bh, "TAA-35", "ベースライン計測", "Backlog（図の外側）", LIGHTGRAY, GRAY, dashed=True)
    text(d, (430, 916), "TAA-50 は TAA-35 の完了も前提にしている。", 24, GRAY)
    text(d, (430, 954), "TAA-35 は未着手のため、TAA-50 は当面動かせない。", 24, GRAY)
    text(d, (60, 1010), "TAA-49 は TAA-44 にも直接依存するが、図では TAA-45 経由の経路で表現している。", 22, GRAY)

    d.rectangle((1470, 40, 1870, 180), fill=LIGHTAMBER)
    d.rectangle((1470, 40, 1482, 180), fill=AMBER)
    text(d, (1510, 62), "止まっている場所", 24, SUB)
    text(d, (1510, 100), "TAA-44 のレビュー", 28, AMBER, bold=True)
    text(d, (1510, 140), "Draft PR #1 / 23日経過", 20, SUB)

    text(d, (80, H - 66), "出典: Linear の blockedBy 関係（読み取り）。課題本文は描画していない。", 24, GRAY)
    img.save(ROOT / "deps.png")
    print("wrote", ROOT / "deps.png")


def candidates_figure() -> None:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    text(d, (80, 64), "blockerが無いBacklog 7件", 52, INK, bold=True)
    text(d, (80, 138), "Epic を除く。どれも依存課題が空なので、Todoへ移せば着手できる。", 30, SUB)

    items = [
        ("TAA-43", "テストデータ", "正解クリップの整備"),
        ("TAA-35", "ベースライン計測", "現行の精度と実費の記録"),
        ("TAA-36", "CPU OCR", "既存ROIへの適用検証"),
        ("TAA-38", "敵検出の比較", "RF-DETR と現行の比較"),
        ("TAA-39", "追跡の比較", "ByteTrack / BoT-SORT"),
        ("TAA-40", "動画理解", "短い戦闘クリップの説明"),
        ("TAA-41", "3D復元", "Depth Anything 3 / VGGT"),
    ]
    cw, ch, gap = 880, 140, 28
    for i, (label, name, note) in enumerate(items):
        if i == 6:
            x, y, w = 80, 250 + 3 * (ch + gap), 1840
        else:
            col, row = i % 2, i // 2
            x = 80 + col * (cw + 60)
            y = 250 + row * (ch + gap)
            w = cw
        d.rectangle((x, y, x + w, y + ch), fill=LIGHTGRAY)
        d.rectangle((x, y, x + 10, y + ch), fill=GRAY)
        text(d, (x + 36, y + 22), label, 30, INK, bold=True)
        text(d, (x + 240, y + 24), name, 28, BLUE, bold=True)
        text(d, (x + 36, y + 80), note, 24, SUB)
        text(d, (x + w - 30, y + 80), "Backlog", 22, GRAY, anchor="ra")

    d.rectangle((80, 930, 1920, 1030), fill=LIGHTAMBER)
    d.rectangle((80, 930, 92, 1030), fill=AMBER)
    text(d, (130, 952), "worker はこの7件を実装しない。", 27, AMBER, bold=True)
    text(d, (130, 994), "Backlog を勝手に Todo へ移すのは人の判断なので、状態を変えずに候補として提示する。", 23, SUB)

    img.save(ROOT / "candidates.png")
    print("wrote", ROOT / "candidates.png")


def main() -> None:
    status_figure()
    deps_figure()
    candidates_figure()


if __name__ == "__main__":
    main()
