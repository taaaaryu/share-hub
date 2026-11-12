#!/usr/bin/env python3
"""issue worker 2026-11-13 の図（公開可能な集計値のみ。映像・課題本文は使わない）。"""
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
INK = "#161616"; SUB = "#525252"; BLUE = "#0f62fe"; LBLUE = "#d0e2ff"
TEAL = "#007d79"; RED = "#da1e28"; GRAY = "#8d8d8d"; DGRAY = "#393939"; PALE = "#f4f4f4"
plt.rcParams["font.family"] = ["Hiragino Sans", "Hiragino Sans GB", "Arial Unicode MS"]

NOW = datetime(2026, 11, 12, 16, 25, tzinfo=timezone.utc)

# ---- Figure 1: 課題の状態と、Draft PR の待ち時間 ----
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.2, 5.0), dpi=200,
                               gridspec_kw={"height_ratios": [1, 1.5], "hspace": 0.6})

states = ["Backlog", "In Progress", "In Review", "Todo", "Done"]
counts = [16, 4, 1, 0, 0]
colors = [GRAY, BLUE, TEAL, RED, DGRAY]
ypos = list(range(len(states)))[::-1]
ax1.barh(ypos, counts, height=0.55, color=colors)
for y, c in zip(ypos, counts):
    ax1.text(c + 0.45, y, f"{c}件", va="center", fontsize=11.5, fontweight="bold",
             color=RED if c == 0 else INK)
ax1.set_yticks(ypos)
ax1.set_yticklabels(states, fontsize=10.5, color=SUB)
ax1.set_xlim(0, 20)
ax1.set_ylim(-0.6, len(states) - 0.4)
ax1.set_xlabel("課題数（計21件）", fontsize=9.5, color=SUB)
ax1.set_title("着手できる Todo は 0 件", fontsize=12.5, fontweight="bold", color=INK, pad=10)
for sp in ["top", "right"]:
    ax1.spines[sp].set_visible(False)
for sp in ["left", "bottom"]:
    ax1.spines[sp].set_color(GRAY)
ax1.tick_params(colors=SUB, labelsize=9.5)

prs = [
    ("#1  TAA-44 HUD変化", "2026-10-28T10:41:36Z", "issue"),
    ("#2  worker 本体", "2026-10-28T11:00:09Z", "infra"),
    ("#3  dashboard", "2026-10-28T11:21:45Z", "infra"),
    ("#4  TAA-33", "2026-11-05T10:38:11Z", "issue"),
    ("#5  TAA-52 ハーネス", "2026-11-05T11:10:20Z", "infra"),
    ("#6  TAA-54 進行役", "2026-11-05T11:33:12Z", "infra"),
    ("#7  TAA-55 スマホ", "2026-11-05T12:01:11Z", "infra"),
    ("#8  TAA-56 上限停止", "2026-11-05T12:21:35Z", "infra"),
]
ages = [round((NOW - datetime.fromisoformat(t.replace("Z", "+00:00"))).total_seconds() / 86400, 1)
        for _, t, _ in prs]
labels = [n for n, _, _ in prs]
bar_colors = [TEAL if g == "issue" else BLUE for _, _, g in prs]
ypos2 = list(range(len(prs)))[::-1]
ax2.barh(ypos2, ages, height=0.55, color=bar_colors)
for y, a in zip(ypos2, ages):
    ax2.text(a + 0.3, y, f"{a:.1f}日", va="center", fontsize=10, fontweight="bold", color=INK)
ax2.set_yticks(ypos2)
ax2.set_yticklabels(labels, fontsize=9)
ax2.set_xlim(0, 19.5)
ax2.set_ylim(-0.6, len(prs) - 0.4)
ax2.set_xlabel("作成から経過した日数（すべて open・Draft・レビュー0件）", fontsize=9.5, color=SUB)
ax2.set_title("Draft PR 8本の待ち時間", fontsize=12.5, fontweight="bold", color=INK, pad=10)
for sp in ["top", "right"]:
    ax2.spines[sp].set_visible(False)
for sp in ["left", "bottom"]:
    ax2.spines[sp].set_color(GRAY)
ax2.tick_params(colors=SUB, labelsize=9.5)

fig.text(0.5, 0.03,
         "2026-11-13 01:25 JST 時点。課題21件は Linear の状態、PR は GitHub の open/draft とレビュー件数。",
         ha="center", fontsize=7.5, color=SUB)
fig.subplots_adjust(left=0.24, right=0.97, top=0.94, bottom=0.15)
fig.savefig(ROOT / "queue_and_prs.png", facecolor="white")
plt.close(fig)

# ---- Figure 2: 本日の3回の実行 ----
runs = [
    ("1回目 00:01", 0.0, 11.0, "TAA-49 事前計測\n資料1枚を公開", TEAL),
    ("2回目 00:42", 41.0, 8.0, "Backlog 16件を集計\n資料1枚を公開", TEAL),
    ("3回目 01:21", 80.0, 9.0, "今回（同じ確認）\nコード変更なし", GRAY),
]
fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=200)
for i, (name, start, dur, note, color) in enumerate(runs):
    y = len(runs) - i
    ax.barh(y, dur, left=start, height=0.45, color=color)
    ax.text(start + dur + 1.5, y, note, va="center", fontsize=9.5, color=INK, linespacing=1.4)
ax.set_yticks([len(runs) - i for i in range(len(runs))])
ax.set_yticklabels([r[0] for r in runs], fontsize=10.5, color=SUB)
ax.set_xlim(0, 118)
ax.set_ylim(0.4, len(runs) + 0.6)
ax.set_xticks([0, 30, 60, 90, 120])
ax.set_xticklabels(["00:00", "00:30", "01:00", "01:30", "02:00"], fontsize=9.5, color=SUB)
ax.set_xlabel("2026-11-13 の時刻（JST）", fontsize=9.5, color=SUB)
for sp in ["top", "right"]:
    ax.spines[sp].set_visible(False)
for sp in ["left", "bottom"]:
    ax.spines[sp].set_color(GRAY)
ax.tick_params(colors=SUB, labelsize=9.5)
ax.set_title("3回の実行で増えたコードは 0 行、公開資料は 2 枚", fontsize=13, fontweight="bold",
             color=INK, pad=12)
ax.text(0, -0.55, "棒の長さは実行時間（分）。1回目は TAA-49 の事前計測、2回目は Backlog の依存集計。",
        fontsize=7.8, color=SUB, transform=ax.transData)
fig.text(0.5, 0.012,
         "worker のログと share-hub のコミット時刻から作成。実装・状態変更は行っていない。",
         ha="center", fontsize=7.5, color=SUB)
fig.tight_layout(rect=(0, 0.045, 1, 1))
fig.savefig(ROOT / "runs_today.png", facecolor="white")
plt.close(fig)

print("wrote queue_and_prs.png, runs_today.png")
