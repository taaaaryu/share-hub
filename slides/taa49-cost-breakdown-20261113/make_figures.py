#!/usr/bin/env python3
"""TAA-49 事前計測の図（集計値のみ。映像は使わない）。"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
INK = "#161616"; SUB = "#525252"; BLUE = "#0f62fe"; LBLUE = "#d0e2ff"
TEAL = "#007d79"; RED = "#da1e28"; GRAY = "#8d8d8d"; DGRAY = "#393939"; PALE = "#f4f4f4"
plt.rcParams["font.family"] = ["Hiragino Sans", "Hiragino Sans GB", "Arial Unicode MS"]

# ---- Figure 1: 1フレームあたりの内訳 ----
labels = ["クリップ1\n(23.6秒)", "クリップ2\n(24.4秒)"]
decode = [2.96, 3.03]
gate = [0.16, 0.16]
fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=200)
ypos = [1, 0]
ax.barh(ypos, decode, height=0.42, color=DGRAY)
ax.barh(ypos, gate, left=decode, height=0.42, color=BLUE)
for y, d, g in zip(ypos, decode, gate):
    total = d + g
    ax.text(d / 2, y, f"デコード {d:.2f} ms", ha="center", va="center", fontsize=12.5,
            fontweight="bold", color="white")
    ax.text(total + 0.12, y, f"ゲート {g:.2f} ms（{g / total * 100:.0f}%）", ha="left", va="center",
            fontsize=11, fontweight="bold", color=BLUE)
ax.set_yticks(ypos)
ax.set_yticklabels(["クリップ1\n23.6秒", "クリップ2\n24.4秒"], fontsize=11, color=SUB)
ax.set_xlim(0, 5.6)
ax.set_xlabel("1フレームあたりの処理時間 (ms)", fontsize=10.5, color=SUB)
ax.set_ylim(-0.6, 1.6)
for sp in ["top", "right"]:
    ax.spines[sp].set_visible(False)
for sp in ["left", "bottom"]:
    ax.spines[sp].set_color(GRAY)
ax.tick_params(colors=SUB, labelsize=10)
ax.set_title("デコードが約95%、変化検出は約5%", fontsize=14, fontweight="bold", color=INK, pad=12)
fig.text(0.5, 0.015, "1280x720 / 約60fps / OpenCV 5.0.0 / macOS arm64 CPU。各3回の中央値。ROIは x=460 y=28 576x100。",
         ha="center", fontsize=7.5, color=SUB)
fig.tight_layout(rect=[0, 0.05, 1, 1])
fig.savefig(ROOT / "cost_split.png", facecolor="white")
plt.close(fig)

# ---- Figure 2: 間引きと候補保持 ----
rates = ["全フレーム\n(59.9fps)", "30fps", "15fps", "10fps"]
gated_rel = [100, 50, 25, 17]
keep1 = [100, round(79 / 78 * 100), round(62 / 78 * 100), round(49 / 78 * 100)]
keep2 = [100, round(305 / 314 * 100), round(185 / 314 * 100), round(134 / 314 * 100)]
x = range(len(rates))
fig, ax = plt.subplots(figsize=(7.2, 4.3), dpi=200)
w = 0.26
ax.bar([i - w for i in x], gated_rel, width=w, color=LBLUE, edgecolor=BLUE, linewidth=1,
       label="ゲートをかけたコマ数（全フレーム=100）")
ax.bar([i for i in x], keep1, width=w, color=TEAL, label="残った変化候補（クリップ1）")
ax.bar([i + w for i in x], keep2, width=w, color=DGRAY, label="残った変化候補（クリップ2）")
for i, v in enumerate(gated_rel):
    ax.text(i - w, v + 3, f"{v}%", ha="center", fontsize=9, color=SUB)
for i, v in enumerate(keep1):
    ax.text(i, v + 3, f"{v}%", ha="center", fontsize=9, color=TEAL, fontweight="bold")
for i, v in enumerate(keep2):
    ax.text(i + w, v + 3, f"{v}%", ha="center", fontsize=9, color=DGRAY, fontweight="bold")
ax.set_xticks(list(x)); ax.set_xticklabels(rates, fontsize=10, color=SUB)
ax.set_ylim(0, 128); ax.set_yticks([])
for sp in ["top", "right", "left"]:
    ax.spines[sp].set_visible(False)
ax.spines["bottom"].set_color(GRAY)
ax.tick_params(colors=SUB)
ax.legend(frameon=False, fontsize=8.6, loc="upper right", ncol=1)
ax.set_title("30fpsまでは候補がほぼ残る。15fps以下で減り始める", fontsize=13.5, fontweight="bold", color=INK, pad=12)
fig.text(0.5, 0.015, "クリップ1=78件 / クリップ2=314件（全フレーム時の候補）。総処理時間はどの設定でも約4.2秒でほぼ同じ。",
         ha="center", fontsize=7.5, color=SUB)
fig.tight_layout(rect=[0, 0.05, 1, 1])
fig.savefig(ROOT / "fps_tradeoff.png", facecolor="white")
plt.close(fig)

# ---- Figure 3: バックエンド差 ----
names = ["FFMPEG\nread()\n2.95 ms/コマ", "FFMPEG\ngrab()\n2.13 ms/コマ",
         "AVFoundation\nread()\n1.40 ms/コマ", "AVFoundation\ngrab()\n1.08 ms/コマ"]
cpu = [19.55, 12.53, 3.94, 0.89]
fig, ax = plt.subplots(figsize=(7.2, 4.3), dpi=200)
bars = ax.bar(names, cpu, width=0.52, color=[RED, "#ff8389", TEAL, BLUE])
for bar, v in zip(bars, cpu):
    ax.text(bar.get_x() + bar.get_width() / 2, v + 0.5, f"{v:.1f}秒", ha="center",
            fontsize=12.5, fontweight="bold", color=INK)
ax.set_ylim(0, 23)
ax.set_ylabel("同じファイルを読むのに使ったCPU時間 (秒)", fontsize=10, color=SUB)
ax.set_yticks([0, 5, 10, 15, 20])
for sp in ["top", "right"]:
    ax.spines[sp].set_visible(False)
for sp in ["left", "bottom"]:
    ax.spines[sp].set_color(GRAY)
ax.tick_params(colors=SUB, labelsize=9)
ax.set_title("同じ動画でも読み方でCPUが4.9倍変わる", fontsize=14, fontweight="bold", color=INK, pad=12)
fig.text(0.5, 0.015, "クリップ1（1417コマ）を1回ずつ計測。AVFoundationはmacOS専用。ECS/Fargateのx86ではFFMPEG相当になる。",
         ha="center", fontsize=7.5, color=SUB)
fig.tight_layout(rect=[0, 0.04, 1, 1])
fig.savefig(ROOT / "backend_cost.png", facecolor="white")
plt.close(fig)
print("wrote 3 figures")
