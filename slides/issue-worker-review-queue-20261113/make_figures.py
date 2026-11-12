#!/usr/bin/env python3
"""issue worker 2026-11-13 3回目の図。

公開可能な集計値だけを使う。課題本文・PR本文・映像・個人情報は使わない。
課題番号と PR 番号は伏せ、件数・状態・経過日数だけを描く。
"""
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parent
INK = "#161616"; SUB = "#525252"; BLUE = "#0f62fe"; TEAL = "#007d79"
RED = "#da1e28"; GRAY = "#8d8d8d"; DGRAY = "#393939"; PALE = "#f4f4f4"
plt.rcParams["font.family"] = ["Hiragino Sans", "Hiragino Sans GB", "Arial Unicode MS"]

NOW = datetime(2026, 11, 12, 17, 10, tzinfo=timezone.utc)  # 2026-11-13 02:10 JST

# ---------------------------------------------------------------- Figure 1
# 21件の課題を状態で積み上げ、着手できる Todo が 0 件であることを示す。
fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=200)
segs = [
    ("Backlog", 16, GRAY, "計画のみ・実装しない"),
    ("In Progress", 4, BLUE, "着手中"),
    ("In Review", 1, TEAL, "確認待ち"),
]
left = 0.0
for name, count, color, _note in segs:
    ax.add_patch(Rectangle((left, 1.9), count, 0.85, color=color, linewidth=0))
    if count >= 3:
        ax.text(left + count / 2, 2.32, f"{count}", ha="center", va="center",
                color="white", fontsize=12, fontweight="bold")
    left += count

ax.add_patch(Rectangle((0, 1.9), 21, 0.85, fill=False, edgecolor=DGRAY, linewidth=1.2))

ax.text(0, 3.00, "対象プロジェクトの課題 21件", fontsize=10.5, color=SUB)

# 凡例（棒の上、等間隔）
legend_x = [0, 7.2, 14.2]
for (name, count, color, note), x in zip(segs, legend_x):
    ax.add_patch(Rectangle((x, 3.45), 0.5, 0.24, color=color, linewidth=0))
    ax.text(x + 0.7, 3.50, f"{name} {count}件", fontsize=9.5, color=INK, va="bottom")
    ax.text(x + 0.7, 3.28, note, fontsize=8, color=SUB, va="bottom")

# Todo の行（0件）
ax.add_patch(Rectangle((0, 0.5), 21, 0.85, facecolor=PALE, edgecolor=RED,
                       linewidth=1.4, linestyle=(0, (4, 2))))
ax.text(0.35, 0.92, "Todo（着手してよい課題）", fontsize=10.5, color=INK,
        va="center", fontweight="bold")
ax.text(20.6, 0.92, "0 件", fontsize=15, color=RED, va="center", ha="right",
        fontweight="bold")
ax.annotate("ここが0なので、実装に進めない", xy=(10.5, 1.42), xytext=(10.5, 1.58),
            ha="center", fontsize=9, color=RED)

ax.set_xlim(-0.4, 21.4)
ax.set_ylim(0.2, 3.95)
ax.set_yticks([])
ax.set_xticks([0, 5, 10, 15, 20])
ax.set_xlabel("課題数", fontsize=9.5, color=SUB)
ax.set_title("着手できる Todo は 0 件。在庫は Backlog に偏っている",
             fontsize=13, fontweight="bold", color=INK, pad=30)
for sp in ["top", "right", "left"]:
    ax.spines[sp].set_visible(False)
ax.spines["bottom"].set_color(GRAY)
ax.tick_params(colors=SUB, labelsize=9)
fig.text(0.5, 0.02,
         "2026-11-13 02:10 JST に Linear から取得した件数。課題本文・担当者名は含まない。",
         ha="center", fontsize=7.5, color=SUB)
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(ROOT / "issue_states.png", facecolor="white")
plt.close(fig)

# ---------------------------------------------------------------- Figure 2
# レビュー待ちの Draft PR 8本。経過日数と CI の有無だけを示す。
prs = [
    ("Draft PR 1", "2026-10-28T10:41:36Z", False),
    ("Draft PR 2", "2026-10-28T11:00:09Z", False),
    ("Draft PR 3", "2026-10-28T11:21:45Z", False),
    ("Draft PR 4", "2026-11-05T10:38:11Z", False),
    ("Draft PR 5", "2026-11-05T11:10:20Z", True),
    ("Draft PR 6", "2026-11-05T11:33:12Z", True),
    ("Draft PR 7", "2026-11-05T12:01:11Z", True),
    ("Draft PR 8", "2026-11-05T12:21:35Z", True),
]
ages = [round((NOW - datetime.fromisoformat(t.replace("Z", "+00:00"))).total_seconds() / 86400, 1)
        for _, t, _ in prs]

fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=200)
ypos = list(range(len(prs)))[::-1]
colors = [TEAL if ci else GRAY for _, _, ci in prs]
ax.barh(ypos, ages, height=0.55, color=colors)
for y, a in zip(ypos, ages):
    ax.text(a + 0.25, y, f"{a:.1f}日", va="center", fontsize=9.5,
            color=INK, fontweight="bold")
ax.set_yticks(ypos)
ax.set_yticklabels([f"{p[0]}（{'CI通過' if p[2] else 'CI未設定'}）" for p in prs],
                   fontsize=9, color=INK)
ax.set_xlim(0, 20)
ax.set_ylim(-0.7, len(prs) - 0.3)
ax.set_xticks([0, 5, 10, 15, 20])
ax.set_xlabel("作成から経過した日数", fontsize=9.5, color=SUB)
ax.set_title("open・Draft 8本、レビュー 0 件、競合なし", fontsize=13,
             fontweight="bold", color=INK, pad=12)
for sp in ["top", "right"]:
    ax.spines[sp].set_visible(False)
for sp in ["left", "bottom"]:
    ax.spines[sp].set_color(GRAY)
ax.tick_params(colors=SUB, labelsize=9)
ax.tick_params(axis="y", labelcolor=INK)
fig.text(0.5, 0.115,
         "色は GitHub Actions の有無（teal=通過・gray=未設定）。8本とも mergeable は clean、コメント0件。",
         ha="center", fontsize=8, color=SUB)
fig.text(0.5, 0.02,
         "2026-11-13 02:10 JST に GitHub API から取得。PR 本文・課題番号・レビュー内容は含まない。",
         ha="center", fontsize=7.5, color=SUB)
fig.tight_layout(rect=(0, 0.13, 1, 1))
fig.savefig(ROOT / "pr_wait.png", facecolor="white")
plt.close(fig)

print("wrote issue_states.png, pr_wait.png")
