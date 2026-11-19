#!/usr/bin/env python3
"""Figures for the 2026-11-20 TAA-43 preparation-plan deck.

Public-safe data only (read 2026-11-20 JST):
- Linear project f7f3a327 (team TAA): 21 issues.
  Backlog 16, In Progress 4, In Review 1, Todo 0.
- open Draft PRs on taaaaryu/thumaster: 8, reviews 0, merges 0.
- shared/videos/training-range: 2 mp4 files, measured with ffprobe.
  1280x720, 59.94 fps, 23.64 s + 24.36 s = 48.00 s, 1417 + 1460 frames.
- analysis/core/layout.py bases HUD rectangles on 1920x1080 and scales by ratio.

Only identifiers, counts, durations, resolutions and category labels are drawn.
No issue titles, issue bodies, comments, gameplay frames, code or customer data.
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


def card(draw, x, y, w, h, accent, fill=LIGHTGRAY, width=10):
    draw.rectangle((x, y, x + w, y + h), fill=fill)
    draw.rectangle((x, y, x + width, y + h), fill=accent)


def status_figure() -> None:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    text(d, (80, 64), "課題21件の状態内訳（2026-11-20 時点）", 52, INK, bold=True)
    text(d, (80, 138), "workerが実装を始められるのは Todo だけ。今日も 0 件だった。", 32, SUB)

    rows = [
        ("Backlog", 16, GRAY, LIGHTGRAY, "計画段階。workerは勝手に実装しない"),
        ("In Progress", 4, BLUE, LIGHTBLUE, "別の作業が進行中"),
        ("In Review", 1, AMBER, LIGHTAMBER, "PRがレビュー待ち"),
        ("Todo", 0, GREEN, LIGHTGREEN, "workerが着手できる唯一の状態"),
    ]
    left, top, plot_w, row_h, gap = 470, 250, 1080, 92, 36
    total = 21
    for i, (name, count, accent, fill, note) in enumerate(rows):
        y = top + i * (row_h + gap)
        text(d, (80, y + 14), name, 30, INK, bold=True)
        text(d, (80, y + 56), note, 21, SUB)
        if count == 0:
            d.rectangle((left, y, left + 4, y + row_h), fill=accent)
            text(d, (left + 26, y + 24), "0 件", 36, accent, bold=True)
        else:
            bar_w = plot_w * count / total
            d.rectangle((left, y, left + bar_w, y + row_h), fill=fill)
            d.rectangle((left, y, left + bar_w, y + 6), fill=accent)
            text(d, (left + bar_w + 20, y + 22), f"{count} 件", 36, accent, bold=True)

    card(d, 80, 830, 1840, 170, GREEN, LIGHTGREEN)
    text(d, (130, 858), "今日の実行で起きたこと", 26, SUB)
    text(
        d,
        (130, 900),
        "Todo が 0 件なので、実装も branch も PR も作っていない。代わりに次の一歩の計画を書いた。",
        30,
        INK,
        bold=True,
    )

    text(
        d,
        (80, H - 66),
        "出典: Linear project f7f3a327 の読み取り値。課題本文・コード・顧客情報は描画していない。",
        24,
        GRAY,
    )
    img.save(ROOT / "status.png")
    print("wrote", ROOT / "status.png")


def materials_figure() -> None:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    text(d, (80, 60), "手元の素材と、TAA-43が必要とする条件", 52, INK, bold=True)
    text(d, (80, 132), "素材は既存の2本だけ。条件の数に対して量・種類が足りない。", 30, SUB)

    # Left: measured inventory.
    text(d, (80, 200), "手元の素材（実測）", 28, SUB)
    rows = [
        ("demo_test_short1.mp4", "23.64 秒", "1,417 フレーム"),
        ("demo_test_short2.mp4", "24.36 秒", "1,460 フレーム"),
    ]
    x, y, w = 80, 244, 840
    for i, (name, dur, frames) in enumerate(rows):
        yy = y + i * 104
        d.rectangle((x, yy, x + w, yy + 92), fill=LIGHTGRAY)
        d.rectangle((x, yy, x + 8, yy + 92), fill=GRAY)
        text(d, (x + 28, yy + 14), name, 27, INK, bold=True)
        text(d, (x + 28, yy + 54), f"{dur} / {frames}", 23, SUB)
        text(d, (x + w - 24, yy + 52), "1280x720", 23, GRAY, anchor="ra")

    card(d, 80, 470, 840, 230, AMBER, LIGHTAMBER)
    text(d, (124, 496), "合計と偏り", 24, SUB)
    text(d, (124, 534), "48.0 秒 / 2 本 / 解像度 1 種類", 34, AMBER, bold=True)
    text(d, (124, 588), "fps は 59.94 で共通。撮影状況は 1 種類しかない。", 24, SUB)
    text(d, (124, 626), "既存パイプラインのROI基準は 1920x1080 で、比率で拡縮する。", 24, SUB)

    # Right: conditions required by the issue.
    text(d, (1000, 200), "TAA-43が求める 10 条件", 28, SUB)
    conditions = [
        "静止",
        "ゆっくり移動",
        "急回転",
        "背景の明暗",
        "スモーク / 発光",
        "銃撃エフェクト",
        "数字の桁変更",
        "表示リセット",
        "HUDの一時非表示",
        "解像度差",
    ]
    cw, ch = 430, 74
    for i, name in enumerate(conditions):
        col, row = i % 2, i // 2
        cx = 1000 + col * (cw + 22)
        cy = 244 + row * (ch + 18)
        d.rectangle((cx, cy, cx + cw, cy + ch), fill=BG, outline=BORDERGRAY, width=2)
        text(d, (cx + 22, cy + 20), f"{i + 1:02d}", 24, GRAY)
        text(d, (cx + 78, cy + 18), name, 26, INK, bold=True)

    card(d, 1000, 740, 882, 210, AMBER, LIGHTAMBER)
    text(d, (1044, 766), "計画上の結論（未計測）", 24, SUB)
    text(d, (1044, 804), "48 秒の素材では 10 条件を網羅できない", 29, AMBER, bold=True)
    text(d, (1044, 852), "桁変更・リセット・非表示・解像度差は、狙って撮る必要がある。", 23, SUB)
    text(d, (1044, 890), "同じ場面の使い回しは正解データの偏りになる。", 23, SUB)

    text(
        d,
        (80, H - 62),
        "出典: ffprobe による実測値と、TAA-43 の作業条件。映像フレームは公開していない。",
        24,
        GRAY,
    )
    img.save(ROOT / "materials.png")
    print("wrote", ROOT / "materials.png")


def plan_figure() -> None:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    text(d, (80, 60), "TAA-43 の進め方（計画のみ・未実装）", 52, INK, bold=True)
    text(d, (80, 132), "最初の関門は撮影。素材が揃うまで、ラベル付けも評価も始められない。", 30, SUB)

    phases = [
        ("段階1", "素材を揃える", "追加収録", "人（撮影）", AMBER, LIGHTAMBER, "条件ごとに短いクリップを撮る"),
        ("段階2", "正解ラベルを作る", "frame / roi_kind / 値", "worker", BLUE, LIGHTBLUE, "7項目のラベルをJSONで固定"),
        ("段階3", "評価に使う", "Recall / 誤発火", "worker", GREEN, LIGHTGREEN, "TAA-45 の比較にそのまま渡す"),
    ]
    bw, bh, gap = 540, 300, 70
    for i, (step, title, detail, owner, accent, fill, note) in enumerate(phases):
        x = 80 + i * (bw + gap)
        y = 250
        d.rectangle((x, y, x + bw, y + bh), fill=fill, outline=accent, width=3)
        d.rectangle((x, y, x + bw, y + 64), fill=accent)
        text(d, (x + 26, y + 16), step, 30, BG, bold=True)
        text(d, (x + 26, y + 88), title, 32, INK, bold=True)
        text(d, (x + 26, y + 140), detail, 24, SUB)
        text(d, (x + 26, y + 196), "担当: " + owner, 24, accent, bold=True)
        text(d, (x + 26, y + 238), note, 22, SUB)
        if i < 2:
            ax = x + bw + 12
            d.polygon(
                [(ax + 46, y + bh / 2), (ax + 10, y + bh / 2 - 22), (ax + 10, y + bh / 2 + 22)],
                fill=GRAY,
            )

    card(d, 80, 620, 1840, 200, GRAY, LIGHTGRAY)
    text(d, (124, 646), "この計画で決めていないこと", 24, SUB)
    text(d, (124, 686), "どの条件を何秒撮るか、誰が撮るかは、まだ決まっていない。", 30, INK, bold=True)
    text(d, (124, 736), "workerは撮影できないため、段階1は人の作業として残る。", 26, SUB)
    text(d, (124, 776), "段階2以降は、TAA-43 が Todo になってから着手する。", 26, SUB)

    card(d, 80, 860, 1840, 140, BLUE, LIGHTBLUE)
    text(d, (124, 886), "この資料の位置づけ", 24, SUB)
    text(
        d,
        (124, 924),
        "実装ではなく計画。コード・branch・PR・Linear の状態は、この run で変えていない。",
        28,
        INK,
        bold=True,
    )

    text(
        d,
        (80, H - 56),
        "出典: TAA-43 の作業条件と、既存素材の実測値。効果の測定は行っていない。",
        24,
        GRAY,
    )
    img.save(ROOT / "plan.png")
    print("wrote", ROOT / "plan.png")


def main() -> None:
    status_figure()
    materials_figure()
    plan_figure()


if __name__ == "__main__":
    main()
