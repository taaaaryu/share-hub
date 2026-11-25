#!/usr/bin/env python3
"""Figures for the TAA-35 baseline plan deck.

All values come from stats.json (recorded repo runs + a local CPU-only scan of
the two shared training-range clips). No Linear text, no private repo data and
no personal data is drawn here.
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

W, H = 2000, 1125


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)


def text(draw, xy, value, size, color=INK, bold=False, anchor="la"):
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def box(draw, x, y, w, h, fill, border, width=2, radius=0):
    if radius:
        draw.rounded_rectangle((x, y, x + w, y + h), radius=radius, fill=fill, outline=border, width=width)
    else:
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


def header(draw, title, note):
    text(draw, (80, 70), title, 52, INK, bold=True)
    text(draw, (80, 138), note, 26, SUB)


def money(stats):
    runs = {r["run"].split("/")[-1]: r for r in stats["recorded_runs"]}
    verified = runs["verified-pipeline"]
    bedrock = verified["bedrock_usd"]
    cpu = verified["cpu_usd"] or 0.0
    share = bedrock / (bedrock + cpu)

    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    header(draw, "1本の解析で、お金はどこへ消えるか",
           "既存の記録済み実行（Sonnet 4.6 / 14イベント / 192フレーム）と東京リージョンの公開単価から算出")

    # ---- panel A: share of one run ----
    text(draw, (80, 230), "A  1本あたりの内訳", 34, INK, bold=True)
    text(draw, (80, 285), "AIの読解（トークン）と、CPUの処理時間を同じUSDで並べた", 24, SUB)
    bx, by, bw, bh = 80, 340, 850, 130
    bed_w = int(bw * share)
    box(draw, bx, by, bw, bh, BG, BORDERGRAY)
    draw.rectangle((bx, by, bx + bed_w, by + bh), fill=BLUE)
    draw.rectangle((bx + bed_w, by, bx + bw, by + bh), fill=AMBER)
    text(draw, (bx + 24, by + 46), "AIの読解", 30, "#ffffff", bold=True)
    text(draw, (bx + 24, by + 86), f"${bedrock:.4f}", 30, "#ffffff")
    text(draw, (bx + bw - 16, by + bh + 18), f"CPU ${cpu:.4f}", 24, AMBER, anchor="ra")
    text(draw, (bx, by + bh + 60), f"費用の {share*100:.1f}% がトークン。CPUは {100-share*100:.1f}%。", 30, INK, bold=True)

    text(draw, (80, 590),
         "注: CPU費用は pipeline_total_sec 12.9秒 × Fargate ARM 2vCPU/4GB（$0.0986/時）で計算。",
         22, SUB)
    text(draw, (80, 625),
         "実際のFargate上の秒数ではなく、同じ処理を同じタスクサイズで動かした場合の換算値。",
         22, SUB)

    # ---- panel B: per event by model ----
    text(draw, (1040, 230), "B  イベント1件あたりの費用", 34, INK, bold=True)
    text(draw, (1040, 285), "記録済み7実行をモデル別に整理（点は各実行、棒は平均）", 24, SUB)

    groups = {"haiku-4.5": [], "sonnet-4.6": []}
    for r in stats["recorded_runs"]:
        groups[r["model"]].append(r["bedrock_usd"] / r["items"])
    labels = {"haiku-4.5": "Haiku 4.5", "sonnet-4.6": "Sonnet 4.6"}
    colors = {"haiku-4.5": GREEN, "sonnet-4.6": RED}
    fills = {"haiku-4.5": LIGHTGREEN, "sonnet-4.6": LIGHTRED}

    base_y, max_h = 790, 360
    vmax = 0.0014
    slot_w = 300
    for i, key in enumerate(["haiku-4.5", "sonnet-4.6"]):
        vals = groups[key]
        avg = sum(vals) / len(vals)
        x0 = 1080 + i * 380
        h = int(base_y - max_h * avg / vmax) if False else int(max_h * avg / vmax)
        top = base_y - h
        box(draw, x0, top, slot_w, h, fills[key], colors[key], width=3)
        text(draw, (x0 + slot_w / 2, top - 46), f"${avg:.5f}", 30, colors[key], bold=True, anchor="ma")
        text(draw, (x0 + slot_w / 2, base_y + 20), labels[key], 28, INK, bold=True, anchor="ma")
        text(draw, (x0 + slot_w / 2, base_y + 58), f"{len(vals)}実行の平均", 22, SUB, anchor="ma")
        for v in vals:
            vh = int(max_h * v / vmax)
            cy = base_y - vh
            draw.ellipse((x0 + slot_w / 2 - 9, cy - 9, x0 + slot_w / 2 + 9, cy + 9), fill=colors[key], outline="#ffffff", width=2)

    draw.line((1050, base_y, 1900, base_y), fill=INK, width=3)
    text(draw, (1050, base_y + 100), "同じ1件でも、読むモデルで約3.5倍の差。", 30, INK, bold=True)
    text(draw, (1050, base_y + 145), "Haiku 4.5 は入力$1.10 / 出力$5.50、Sonnet 4.6 は $3.30 / $16.50（100万トークン）。",
         22, SUB)

    img.save(ROOT / "fig_money.png")
    print("fig_money.png", round(share, 3), round(bedrock, 6), round(cpu, 6))


def time_split(stats):
    runs = [r for r in stats["recorded_runs"] if r["stage_sec"].get("pipeline_total_sec")]
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    header(draw, "時間の大半はCPU、お金の大半はトークン",
           "記録済み5実行の stage_timing。棒の長さは実測の処理時間（秒）")

    parts = [("scan_sec", "弾数スキャン", BLUE), ("llm_events_sec", "LLM待ち", AMBER),
             ("enrich_sec", "後処理", GRAY)]
    x0, x1 = 600, 1900
    vmax = 27.0
    top, rowh, gap = 300, 96, 34
    for i, run in enumerate(runs):
        t = run["stage_sec"]
        total = t["pipeline_total_sec"]
        y = top + i * (rowh + gap)
        name = run["run"].split("/")[-1].replace("-pipeline", "").replace("full-", "full ")
        text(draw, (x0 - 24, y + rowh / 2), name, 24, INK, anchor="rm")
        text(draw, (x0 - 24, y + rowh / 2 + 30), f"{run['items']}件 / {run['frames']}f", 20, SUB, anchor="rm")
        x = x0
        used = 0.0
        for key, _label, color in parts:
            v = t.get(key, 0.0)
            used += v
            wpx = max(2, int((x1 - x0) * v / vmax))
            draw.rectangle((x, y, x + wpx, y + rowh), fill=color)
            if wpx > 90:
                text(draw, (x + wpx / 2, y + rowh / 2), f"{v:.1f}s", 22, "#ffffff", bold=True, anchor="mm")
            x += wpx
        rest = max(0.0, total - used)
        if rest > 0.05:
            wpx = int((x1 - x0) * rest / vmax)
            draw.rectangle((x, y, x + wpx, y + rowh), fill=LIGHTGRAY, outline=BORDERGRAY)
        text(draw, (x1 + 18, y + rowh / 2), f"{total:.1f}s", 26, INK, bold=True, anchor="lm")

    # legend
    ly = 940
    lx = 600
    for _key, label, color in parts:
        draw.rectangle((lx, ly, lx + 34, ly + 34), fill=color)
        text(draw, (lx + 46, ly + 17), label, 26, INK, anchor="lm")
        lx += 300
    text(draw, (600, 1010), "処理時間の20%から45%がLLM待ち。残りはローカルCPUの画像処理で、費用はごく小さい。", 26, INK, bold=True)

    img.save(ROOT / "fig_time.png")
    print("fig_time.png", len(runs))


def plan(stats):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    header(draw, "ベースラインを残す手順（この資料は計画のみ）",
           "コードは変更していない。次に実装するときの記録項目と順番")

    steps = [
        ("1  同じ動画を固定", ["評価動画IDとハッシュ、解像度、", "ROIを1か所に書く。以後の", "比較はこのIDで行う。"], BLUE, PALE),
        ("2  1本を最後まで記録", ["トークン数・呼出回数・失敗と", "再試行・stage_timing・", "総フレームを1つのJSONへ。"], BLUE, PALE),
        ("3  同じGit SHAで再実行", ["変更前後を同じコマンドで回し、", "差分だけを比較する。"], AMBER, LIGHTAMBER),
        ("4  費用・精度・戻し方", ["採否とロールバック手順を", "Issueへ追記。未達なら採用", "しない理由も残す。"], AMBER, LIGHTAMBER),
    ]
    x, y, w, h = 80, 250, 400, 310
    for i, (title, lines, color, fill) in enumerate(steps):
        box(draw, x, y, w, h, fill, color, width=3, radius=8)
        text(draw, (x + 26, y + 36), title, 32, color, bold=True)
        for j, ln in enumerate(lines):
            text(draw, (x + 26, y + 112 + j * 36), ln, 24, INK)
        if i < 3:
            arrow(draw, (x + w + 10, y + h / 2), (x + w + 64, y + h / 2))
        x += w + 75

    text(draw, (80, 640), "今日わかっていること", 32, INK, bold=True)
    facts = [
        f"記録済み7実行の中央値: 1本 ${stats['summary']['bedrock_usd_median']:.4f}（トークンのみ）",
        f"費用に占めるトークンの割合: 中央値 {stats['summary']['bedrock_share_median']*100:.1f}%",
        f"イベント1件あたり: 中央値 ${stats['summary']['usd_per_event_median']:.5f}",
        "共有クリップ2本のローカルCPUスキャン: 30-32ミリ秒/フレーム（2vCPU換算で約$0.0012/本）",
    ]
    for i, f in enumerate(facts):
        text(draw, (80, 705 + i * 46), "・" + f, 26, INK)

    text(draw, (80, 930), "まだ決められないこと", 32, AMBER, bold=True)
    text(draw, (80, 995), "CPU OCRに置き換えたときの精度と実費。PP-OCRv6の評価（TAA-36）と、同じ動画での正解ラベルが必要。",
         26, SUB)

    img.save(ROOT / "fig_plan.png")
    print("fig_plan.png")


def main() -> None:
    stats = json.loads((ROOT / "stats.json").read_text())
    money(stats)
    time_split(stats)
    plan(stats)


if __name__ == "__main__":
    main()
