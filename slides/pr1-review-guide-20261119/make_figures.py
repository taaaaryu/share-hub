#!/usr/bin/env python3
"""Generate the two figures used by this deck.

Data source (public-safe, checked 2026-11-19 JST):
- private remote taaaaryu/thumaster, PR #1 at head 3369267:
  additions 1,317 / deletions 0 / 13 files / MERGEABLE / 0 review comments.
- Per-file additions from the GitHub pull request file list.
- Test re-run performed locally on a read-only copy of that head:
  python -m unittest discover -s analysis/tests -> 104 tests OK in 0.227s.
  The two new modules alone -> 24 tests OK.

Only file paths that the PR itself adds, counts and durations are drawn.
No issue bodies, comments, customer data or secrets are used.
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
TEAL = "#007d79"
LIGHTTEAL = "#d9fbfb"
AMBER = "#8a3800"
LIGHTAMBER = "#fff2e8"
GRAY = "#6f6f6f"
LIGHTGRAY = "#f4f4f4"
BORDERGRAY = "#c6c6c6"

W, H = 2000, 1125


def font(size, bold=False):
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def figure():
    img = Image.new("RGB", (W, H), BG)
    return img, ImageDraw.Draw(img)


def footprint():
    img, d = figure()
    text(d, (80, 54), "追加1,317行の内訳と、削除0行", 44, INK, True)
    text(d, (80, 116), "PR #1のファイル一覧から集計（2026-11-19 時点・head 3369267）", 24, SUB)

    segments = [
        ("新規の解析コード", 683, BLUE, "hud_change.py 359 + damage_timing.py 324"),
        ("テスト", 495, TEAL, "test_hud_change 257 + test_damage_timing 159 + benchmark 79"),
        ("新しいドキュメント", 114, AMBER, "hud-change-detector 43 + benchmark JSON 45 + plan 26"),
        ("既存ファイルの追記", 25, GRAY, ".gitignore と docs 4本、各5行"),
    ]
    total = sum(s[1] for s in segments)

    x0, x1, y0, h = 80, 1920, 190, 84
    span = x1 - x0
    cursor = x0
    for name, value, color, _ in segments:
        width = span * value / total
        d.rectangle([cursor, y0, cursor + width, y0 + h], fill=color)
        if width > 120:
            text(d, (cursor + width / 2, y0 + h / 2), str(value), 34, BG, True, "mm")
        cursor += width
    d.rectangle([x0, y0, x1, y0 + h], outline=BG, width=3)

    y = 330
    for name, value, color, detail in segments:
        d.rectangle([80, y + 8, 104, y + 32], fill=color)
        text(d, (124, y), name, 30, INK, True)
        text(d, (620, y + 2), f"+{value} 行", 30, color, True)
        text(d, (860, y + 4), detail, 24, SUB)
        y += 68

    d.rounded_rectangle([80, 640, 1920, 800], radius=14, fill=LIGHTBLUE, outline=BLUE, width=3)
    text(d, (120, 668), "削除は 0 行", 40, BLUE, True)
    text(d, (120, 730), "既存の解析ファイルは1本も書き換えていない。変えたのは .gitignore と docs の追記だけ。", 26, SUB)

    d.rounded_rectangle([80, 840, 1920, 1030], radius=14, fill=LIGHTGRAY, outline=BORDERGRAY, width=2)
    text(d, (120, 866), "13ファイルの内訳", 30, INK, True)
    text(d, (120, 920), "新規 11本（コード5・ドキュメント3・テスト3を含む）／既存の追記 5本（.gitignore + docs 4本）", 25, SUB)
    text(d, (120, 970), "解析パイプラインへの接続は含まない。mergeしても、本番の解析結果は今日と同じまま。", 25, INK)

    img.save(ROOT / "footprint.png")


def tests():
    img, d = figure()
    text(d, (80, 54), "PRのheadを手元で再実行：104件すべて成功", 44, INK, True)
    text(d, (80, 116), "CPUのみ・ネットワークなし・0.23秒。PR本文の申告とは別に、こちらの環境で測り直した", 24, SUB)

    d.rounded_rectangle([80, 180, 900, 470], radius=16, fill=LIGHTTEAL, outline=TEAL, width=3)
    text(d, (120, 210), "104", 96, TEAL, True)
    text(d, (360, 240), "passed", 40, TEAL, True)
    text(d, (120, 340), "failed 0 ・ error 0 ・ skip 0", 30, INK)
    text(d, (120, 400), "経過 0.227 秒", 26, SUB)

    d.rounded_rectangle([960, 180, 1920, 470], radius=16, fill=LIGHTBLUE, outline=BLUE, width=3)
    text(d, (1000, 210), "内訳", 30, INK, True)
    text(d, (1000, 270), "HUD変化検出（新規）  17件", 28, INK)
    text(d, (1000, 320), "damage時刻補正（新規）  7件", 28, INK)
    text(d, (1000, 370), "既存のレイアウト・イベント・契約  80件", 28, INK)
    text(d, (1000, 420), "新規2本だけで 24件", 26, BLUE, True)

    text(d, (80, 540), "何を確かめたか", 34, INK, True)
    rows = [
        ("空ROI・画面外・サイズ不一致", "変化ではなく「判定不能」として返る", TEAL),
        ("比較器・署名の差し替え", "関数を渡すと差し替わり、例外は判定不能に落ちる", TEAL),
        ("未知のmethod名・非有限スコア", "黙って画素差分に切り替えず、判定不能にする", TEAL),
        ("damage時刻補正の既存挙動", "参照版と同じ遷移・同じイベント選択になる", TEAL),
    ]
    y = 610
    for left, right, color in rows:
        d.ellipse([84, y + 12, 104, y + 32], fill=color)
        text(d, (124, y), left, 26, INK, True)
        text(d, (760, y + 2), right, 26, SUB)
        y += 66

    d.rectangle([80, 900, 1920, 906], fill=BORDERGRAY)
    text(d, (80, 930), "再現方法: PR headのtarを取り、experimentsのvenvで", 24, SUB)
    text(d, (80, 975), "python -m unittest discover -s analysis/tests -t . -p \"test_*.py\"", 26, INK, True)
    text(d, (80, 1020), "※ 動画2本・2,877フレームの一致比較（87候補）は素材が必要なため、この環境では再実行していない。", 23, AMBER)

    img.save(ROOT / "tests.png")


if __name__ == "__main__":
    footprint()
    tests()
    print("wrote footprint.png, tests.png")
