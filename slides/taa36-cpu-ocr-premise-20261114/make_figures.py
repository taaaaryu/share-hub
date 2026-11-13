"""Figures for the TAA-36 premise deck. Aggregate numbers only, no video frames."""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
M = json.loads((HERE / "measure.json").read_text())

INK = "#161616"
MUTED = "#525252"
BLUE = "#0f62fe"
GRAY = "#c6c6c6"
plt.rcParams.update({"font.family": ["Hiragino Sans", "DejaVu Sans"], "text.color": INK,
                     "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": INK})


def fig_cost():
    dec = M["decode"]["ms_per_frame_median"]
    roi = M["roi_extract"]["ms_per_frame_median"]
    ocr = M["tesseract"]["ms_per_crop_median"]
    labels = ["ダメージROIの切り出し", "1フレームのデコード", "Tesseract 1回（ROI 1枚）"]
    vals = [roi, dec, ocr]
    colors = [GRAY, BLUE, "#da1e28"]
    fig, ax = plt.subplots(figsize=(9.6, 4.5), dpi=150)
    bars = ax.barh(labels, vals, color=colors, height=0.5)
    ax.set_xscale("log")
    ax.set_xlim(0.05, 1200)
    ax.set_xlabel("1回あたりの処理時間 (ms, 対数軸)", fontsize=11)
    for b, v in zip(bars, vals):
        ax.text(v * 1.15, b.get_y() + b.get_height() / 2, f"{v:g} ms", va="center", fontsize=12, color=INK)
    ax.set_title("文字認識1回は、フレーム1枚のデコードの約192倍の時間がかかる", fontsize=13, loc="left", pad=14)
    ax.grid(axis="x", color="#e0e0e0", linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    fig.text(0.01, 0.02, "実測: 訓練場クリップ1本 1280x720 / 全1417フレーム / ローカルCPU (Apple silicon) / 1条件1回のみ",
             fontsize=9, color=MUTED)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(HERE / "cost_ladder.png", facecolor="white")
    plt.close(fig)


def fig_readout():
    texts = [t["text"].strip() for t in M["tesseract"]["sample_texts"]]
    clean = sum(1 for t in texts if t.isdigit())
    empty = sum(1 for t in texts if not t)
    splitn = len(texts) - clean - empty
    labels = ["1つの整数として読めた", "複数の数字に割れた", "何も返らなかった"]
    vals = [clean, splitn, empty]
    colors = ["#24a148", "#f1c21b", "#da1e28"]
    fig, ax = plt.subplots(figsize=(9.6, 4.2), dpi=150)
    bars = ax.bar(labels, vals, color=colors, width=0.5)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.6, f"{v}枚", ha="center", fontsize=13, color=INK)
    ax.set_ylim(0, max(vals) * 1.25)
    ax.set_ylabel("ROI 48枚のうち (枚)", fontsize=11)
    ax.set_title("累積ダメージを1つの数値として返せたのは48枚中9枚", fontsize=13, loc="left", pad=14)
    ax.grid(axis="y", color="#e0e0e0", linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    fig.text(0.01, 0.02, "実測: 同じクリップのダメージROIを30フレーム間隔で48枚抜き、Tesseract (数字のみ・2倍拡大) にかけた結果",
             fontsize=9, color=MUTED)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(HERE / "readout_result.png", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    fig_cost()
    fig_readout()
    print("ok")
