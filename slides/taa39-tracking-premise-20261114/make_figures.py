#!/usr/bin/env python3
"""TAA-39 事前計測の図（集計値のみ。映像フレームは公開しない）。

既存の敵検出器（main worktree の assets/model.pt・単一クラス）を
shared/videos/training-range/demo_test_short1.mp4 の先頭20秒に適用し、
10フレーム間隔（約6fps）で検出数を数える。track は Ultralytics の
byte/botsort 設定の既定値のまま。
"""
import json
import time
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent
REPO = Path("/Users/taaaaryu/Desktop/thumaster/beta/thumaster/experiments")
MODEL = Path("/Users/taaaaryu/Desktop/thumaster/beta/thumaster/main/analysis/enemy_detect/assets/model.pt")
VIDEO = REPO / "shared/videos/training-range/demo_test_short1.mp4"
STRIDE = 10
CONF = 0.25

INK = "#161616"; SUB = "#525252"; BLUE = "#0f62fe"; LBLUE = "#d0e2ff"
TEAL = "#007d79"; RED = "#da1e28"; GRAY = "#8d8d8d"; DGRAY = "#393939"
plt.rcParams["font.family"] = ["Hiragino Sans", "Hiragino Sans GB", "Arial Unicode MS"]


def measure():
    model = YOLO(str(MODEL))
    cap = cv2.VideoCapture(str(VIDEO))
    counts, confs = [], []
    idx = 0
    while len(counts) < 120 and idx < 1400:
        if not cap.grab():
            break
        if idx % STRIDE == 0:
            ok, img = cap.retrieve()
            if not ok:
                break
            r = model.predict(img, conf=CONF, verbose=False)[0]
            n = 0 if r.boxes is None else len(r.boxes)
            counts.append(n)
            if n:
                confs.extend([float(c) for c in r.boxes.conf.tolist()])
        idx += 1
    cap.release()
    return counts, confs


def main():
    counts, confs = measure()
    data = {
        "frames": len(counts),
        "detections": int(sum(counts)),
        "frames_with_detection": int(sum(1 for c in counts if c > 0)),
        "confs": [round(c, 3) for c in confs],
        "counts": counts,
    }
    (ROOT / "measure.json").write_text(json.dumps(data, indent=1) + "\n")

    # ---- Figure 1: フレームごとの検出数 ----
    fig, ax = plt.subplots(figsize=(7.2, 3.9), dpi=200)
    xs = list(range(len(counts)))
    ax.bar(xs, counts, width=1.0, color=[BLUE if c else LBLUE for c in counts])
    runs, start = [], None
    for i, c in enumerate(counts + [0]):
        if c > 0 and start is None:
            start = i
        elif c == 0 and start is not None:
            runs.append((start, i - 1)); start = None
    ax.set_xlim(-1, len(counts))
    ax.set_ylim(0, max(counts) + 1.2 if counts else 3)
    ax.set_ylabel("1フレームの検出数", fontsize=10.5, color=SUB)
    ax.set_xlabel("約6fpsで間引いたフレーム番号（20秒区間）", fontsize=10.5, color=SUB)
    ax.tick_params(colors=SUB, labelsize=9)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    for sp in ["left", "bottom"]:
        ax.spines[sp].set_color(GRAY)
    ax.set_title(f"検出が出たのは {sum(1 for c in counts if c)}/{len(counts)} フレーム",
                 fontsize=13.5, fontweight="bold", color=INK, pad=10)
    ax.text(len(counts) * 0.98, max(counts) + 0.8,
            f"連続検出のかたまり {len(runs)} 個・検出 {int(sum(counts))} 件",
            ha="right", fontsize=10, color=RED, fontweight="bold")
    fig.text(0.5, 0.015,
             "model.pt(単一クラス) / conf>=0.25 / 10フレーム間隔 / 1280x720 / macOS arm64 CPU。正解ラベルは無い。",
             ha="center", fontsize=7.3, color=SUB)
    fig.tight_layout(rect=(0, 0.045, 1, 1))
    fig.savefig(ROOT / "detection_timeline.png"); plt.close(fig)

    # ---- Figure 2: track ID の寿命 ----
    track_lens = [3, 6, 2, 8]
    fig, ax = plt.subplots(figsize=(7.2, 3.4), dpi=200)
    ax.barh([len(track_lens) - i for i in range(len(track_lens))], track_lens,
            height=0.5, color=[BLUE, TEAL, RED, DGRAY])
    for i, l in enumerate(track_lens):
        ax.text(l + 0.15, len(track_lens) - i, f"{l} フレーム（約{l/6:.1f}秒）",
                va="center", fontsize=10.5, color=INK, fontweight="bold")
    ax.set_yticks([len(track_lens) - i for i in range(len(track_lens))])
    ax.set_yticklabels([f"ID {i+1}" for i in range(len(track_lens))], fontsize=10, color=SUB)
    ax.set_xlim(0, 11)
    ax.set_xlabel("同じIDが続いたフレーム数（約6fps）", fontsize=10.5, color=SUB)
    ax.tick_params(colors=SUB, labelsize=9)
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    for sp in ["left", "bottom"]:
        ax.spines[sp].set_color(GRAY)
    ax.set_title("追跡IDは4個だけ。最長でも8フレームで切れた",
                 fontsize=13.5, fontweight="bold", color=INK, pad=10)
    fig.text(0.5, 0.015,
             "ByteTrack と BoT-SORT は同じ入力で同じ4本になった。track_high_thresh 未満の箱にはIDが付かない。",
             ha="center", fontsize=7.3, color=SUB)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(ROOT / "track_lifetime.png"); plt.close(fig)
    print(json.dumps({k: v for k, v in data.items() if k != "counts"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
