#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data: stats.json, produced by a local, CPU-only run over the two shared
training-range clips (public-safe aggregates). No Linear text, no private
repository data and no personal data is drawn here.
"""
import json
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
RED = "#da1e28"
LIGHTRED = "#fff1f1"
GREEN = "#044317"
LIGHTGREEN = "#defbe6"

THRESHOLD = 0.015
W, H = 2000, 1125


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def box(draw, x, y, w, h, fill, border, width=2):
    draw.rectangle((x, y, x + w, y + h), fill=fill, outline=border, width=width)


def arrow(draw, start, end, color=GRAY, width=4):
    draw.line([start, end], fill=color, width=width)
    (x1, y1), (x2, y2) = start, end
    dx, dy = x2 - x1, y2 - y1
    length = max((dx * dx + dy * dy) ** 0.5, 1.0)
    ux, uy = dx / length, dy / length
    size = 18
    left = (x2 - ux * size - uy * size * 0.5, y2 - uy * size + ux * size * 0.5)
    right = (x2 - ux * size + uy * size * 0.5, y2 - uy * size - ux * size * 0.5)
    draw.polygon([(x2, y2), left, right], fill=color)


def baseline(path: Path) -> None:
    stats = json.loads((ROOT / "stats.json").read_text())
    clip1, clip2 = stats["clips"]

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (100, 64), "クリップ2（24.4秒）: しきい値超えは短い山の連続", 56, INK, bold=True)
    text(
        d,
        (100, 146),
        "前フレームとの差分が1.5%（点線）を超えた区間を色付け。背景の動きだけでも超えてしまう。",
        26,
        SUB,
    )

    # Plot area
    px, py, pw, ph = 100, 215, 1240, 560
    box(d, px, py, pw, ph, "#ffffff", BORDERGRAY, 2)
    ratios = clip2["ratios"]
    ymax = 0.20
    step = max(1, len(ratios) // pw)
    points = ratios[::step]
    n = len(points)

    def to_xy(i, value):
        x = px + 20 + (pw - 40) * i / max(n - 1, 1)
        y = py + ph - 40 - (ph - 80) * min(value, ymax) / ymax
        return x, y

    # shaded area under the curve
    curve = [to_xy(i, v) for i, v in enumerate(points)]
    poly = [(px + 20, py + ph - 40)] + curve + [(curve[-1][0], py + ph - 40)]
    d.polygon(poly, fill=LIGHTAMBER)
    d.line(curve, fill=BLUE, width=3)

    # threshold line (drawn after the fill so it stays visible)
    ty = to_xy(0, THRESHOLD)[1]
    for x in range(px + 20, px + pw - 20, 18):
        d.line([(x, ty), (x + 10, ty)], fill=AMBER, width=3)
    text(d, (px + 34, ty - 36), "しきい値 1.5%", 24, AMBER, bold=True)

    # axis labels
    text(d, (px + 20, py + ph - 34), "0秒", 20, SUB)
    text(d, (px + pw - 20, py + ph - 34), "24秒", 20, SUB, anchor="ra")
    text(d, (px + 24, py + 14), f"変化率の最大 {clip2['policy_a']['max_ratio']:.3f}", 22, SUB)

    # Right summary panel
    sx, sy, sw, sh = 1380, 215, 520, 560
    box(d, sx, sy, sw, sh, "#fafafa", BORDERGRAY, 2)
    text(d, (sx + 30, sy + 26), "しきい値を超えた回数", 26, INK, bold=True)
    rows = [
        ("クリップ1", "73回", f"{100 * clip1['policy_a']['firing_frames'] / clip1['frames']:.1f}% のフレーム", 73 / 288),
        ("クリップ2", "288回", f"{100 * clip2['policy_a']['firing_frames'] / clip2['frames']:.1f}% のフレーム", 1.0),
    ]
    for i, (name, count, note, frac) in enumerate(rows):
        y = sy + 88 + i * 158
        text(d, (sx + 30, y), name, 24, SUB)
        text(d, (sx + 30, y + 28), count, 50, RED if i else AMBER, bold=True)
        text(d, (sx + 30, y + 88), note, 20, SUB)
        d.rectangle((sx + 30, y + 120, sx + 30 + int(frac * 420), y + 140), fill=RED if i else AMBER)

    text(d, (sx + 30, sy + 404), "中央値はどちらも 0.01% 前後。", 22, INK)
    text(d, (sx + 30, sy + 440), "平均して数十フレームに1回の頻度で", 22, SUB)
    text(d, (sx + 30, sy + 472), "背景の動きがしきい値を越える。", 22, SUB)

    # Bottom banner
    box(d, 100, 820, 1800, 118, LIGHTRED, RED, 3)
    text(d, (130, 840), "毎秒 12回前後", 38, RED, bold=True)
    text(d, (450, 846), "クリップ2では、24秒間に288回。1秒あたり約12回が該当した。", 28, INK)
    text(d, (130, 896), "このままでは変化の有無に関係なくOCRを呼ぶ。しきい値調整だけでは足りない。", 22, SUB)

    box(d, 100, 962, 1800, 108, LIGHTGRAY, BORDERGRAY, 2)
    text(d, (130, 980), "計測条件: 共有クリップ2本 / ローカルCPU / OpenCV、HUD右上領域 576×100px / グレー190で二値化。", 22, INK)
    text(d, (130, 1014), "正解ラベルが無いため、この図は「誤検出が多い」ことの証明ではなく、発火頻度の実測である。", 21, SUB)

    img.save(path)


def state(path: Path) -> None:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    text(d, (100, 64), "状態は3つ。確定するまでOCRを呼ばない", 56, INK, bold=True)
    text(d, (100, 146), "比較の基準は「最後に確定した署名」。途中のアニメーションは候補にしない。", 26, SUB)

    # Three state boxes
    top = 270
    boxes = [
        (110, top, 460, 200, "STABLE", "確定済みの署名を持つ。\n比較の基準はこの署名。", PALE, BLUE),
        (770, top, 460, 200, "SETTLING", "変化を検出した直後。\n止まるまで待つ。", LIGHTAMBER, AMBER),
        (1430, top, 460, 200, "STABLE (new)", "止まったフレームを\n新しい基準にする。", LIGHTGREEN, GREEN),
    ]
    for x, y, w, h, head, body, fill, color in boxes:
        box(d, x, y, w, h, fill, color, 3)
        text(d, (x + w / 2, y + 52), head, 34, color, bold=True, anchor="mm")
        for i, line in enumerate(body.split("\n")):
            text(d, (x + w / 2, y + 108 + i * 34), line, 21, INK, anchor="mm")

    # main arrows
    arrow(d, (578, top + 100), (758, top + 100), AMBER)
    text(d, (668, top + 52), "変化率が", 20, AMBER, anchor="mm")
    text(d, (668, top + 78), "しきい値以上", 20, AMBER, anchor="mm")

    arrow(d, (1238, top + 100), (1418, top + 100), GREEN)
    text(d, (1328, top + 52), "0.25秒", 20, GREEN, anchor="mm")
    text(d, (1328, top + 78), "止まったら", 20, GREEN, anchor="mm")

    # self state note (STABLE keeps its signature)
    text(d, (340, top + 224), "変化なし → 何もしない（同じ値を二度読まない）", 21, SUB, anchor="mm")

    # branch panel
    bx, by, bw, bh = 110, 560, 1780, 300
    box(d, bx, by, bw, bh, "#ffffff", BORDERGRAY, 2)
    text(d, (bx + 28, by + 20), "SETTLING からの4つの分岐", 26, INK, bold=True)

    items = [
        ("止まった", "新しい値として候補を1回だけ出す。理由は settled。", GREEN, LIGHTGREEN),
        ("2秒たっても止まらない", "打ち切って1回出す。理由は timeout_forced。変化の証拠ではない。", RED, LIGHTRED),
        ("同じ値に戻った", "候補を出さない。理由は reverted。往復を数えない。", GRAY, LIGHTGRAY),
        ("比較できない", "変化として扱わない。連続したら1回だけ強制で読む。", AMBER, LIGHTAMBER),
    ]
    for i, (head, body, color, fill) in enumerate(items):
        col = i % 2
        row = i // 2
        x = bx + 28 + col * 872
        y = by + 70 + row * 108
        box(d, x, y, 848, 88, fill, color, 2)
        text(d, (x + 20, y + 14), head, 23, color, bold=True)
        text(d, (x + 20, y + 50), body, 20, INK)

    # bottom: periodic safety net
    box(d, 110, 890, 1780, 92, PALE, BLUE, 2)
    text(d, (140, 908), "保険: 5秒読まれなければ、変化が無くても1回読む（理由 periodic）", 24, INK, bold=True)
    text(d, (140, 944), "数字が変わらないまま長時間経過した場合と、検出そのものが壊れた場合の両方に効く。", 21, SUB)

    box(d, 110, 1000, 1780, 78, LIGHTGRAY, BORDERGRAY, 2)
    text(d, (140, 1020), "この設計でも、背景の動きで署名が変わり続けると timeout_forced が増える（試算では18回中10回）。", 22, INK)

    img.save(path)


if __name__ == "__main__":
    baseline(ROOT / "baseline.png")
    state(ROOT / "state.png")
    print("wrote baseline.png and state.png")
