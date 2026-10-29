#!/usr/bin/env python3
"""Small synthetic-HUD PoC for CPU Top-hat change-candidate extraction.

This script is intentionally self-contained. It generates only synthetic HUD
frames with OpenCV, compares three fixed-parameter methods, and writes
result.json plus a contact sheet. It does not read videos, secrets, network
resources, or Linear data.
"""

from __future__ import annotations

import hashlib
import json
import platform
import resource
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

# ---------------------------------------------------------------------------
# Fixed experiment parameters (set before the single run; not tuned afterwards)
# ---------------------------------------------------------------------------
SEED = 20261029
FRAME_W = 640
FRAME_H = 300
ROI = (40, 100, 240, 100)          # x, y, w, h: HUD number area
CONTROL_ROI = (340, 100, 240, 100) # adjacent background control ROI

PAIRS_PER_CONDITION = 20
A_GRAY_THRESHOLD = 190
TOPHAT_KERNEL_SIZE = (15, 15)
TOPHAT_THRESHOLD = 40
A_CHANGE_THRESHOLD = 0.005
B_CHANGE_THRESHOLD = 0.004
C_CHANGE_THRESHOLD = 0.003

FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 2.4
FONT_THICKNESS = 5
TEXT_RIGHT_MARGIN = 14
TEXT_BOTTOM_MARGIN = 14

OUT_DIR = Path(__file__).resolve().parent
RESULT_PATH = OUT_DIR / "result.json"
CONTACT_SHEET_PATH = OUT_DIR / "contact_sheet.png"


# ---------------------------------------------------------------------------
# Synthetic input generation
# ---------------------------------------------------------------------------
def make_background(rng: np.random.Generator) -> np.ndarray:
    """Create a smooth, bright-ish synthetic background (single channel)."""
    yy, xx = np.mgrid[0:FRAME_H, 0:FRAME_W].astype(np.float32)
    img = np.full((FRAME_H, FRAME_W), 135.0, dtype=np.float32)

    # Low-frequency illumination/texture.
    for _ in range(4):
        fx = float(rng.uniform(0.004, 0.020))
        fy = float(rng.uniform(0.004, 0.020))
        phase = float(rng.uniform(0.0, 2.0 * np.pi))
        amp = float(rng.uniform(10.0, 28.0))
        img += amp * np.sin(2.0 * np.pi * (fx * xx + fy * yy) + phase)

    # Smooth random texture.
    noise = rng.normal(0.0, 18.0, (FRAME_H, FRAME_W)).astype(np.float32)
    noise = cv2.GaussianBlur(noise, (0, 0), sigmaX=10.0, sigmaY=10.0)
    img += noise

    # Broad highlights. These are wide enough to be mostly suppressed by the
    # small Top-hat kernel, while still making the gray>190 baseline react.
    for _ in range(2):
        cx = float(rng.uniform(0.0, FRAME_W))
        cy = float(rng.uniform(0.0, FRAME_H))
        sx = float(rng.uniform(70.0, 140.0))
        sy = float(rng.uniform(50.0, 110.0))
        amp = float(rng.uniform(20.0, 55.0))
        img += amp * np.exp(-(((xx - cx) / sx) ** 2 + ((yy - cy) / sy) ** 2))

    return np.clip(img, 30.0, 205.0)


def make_background_variant(base: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Apply a global translation plus brightness offset to the background."""
    # Force a non-zero translation so this condition really changes.
    dx = int(rng.choice(np.array([-12, -11, -10, -9, -8, -7, -6, -5, -4, -3,
                                  3, 4, 5, 6, 7, 8, 9, 10, 11, 12])))
    dy = int(rng.choice(np.array([-9, -8, -7, -6, -5, -4, -3, 3, 4, 5, 6, 7, 8, 9])))
    mat = np.float32([[1.0, 0.0, dx], [0.0, 1.0, dy]])
    shifted = cv2.warpAffine(
        base, mat, (FRAME_W, FRAME_H),
        flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT,
    )
    delta = float(rng.uniform(-28.0, 28.0))
    return np.clip(shifted + delta, 0.0, 255.0)


def render_frame(background: np.ndarray, digits: str) -> np.ndarray:
    """Render white HUD digits, right-aligned, on the synthetic background."""
    frame = cv2.cvtColor(np.clip(background, 0, 255).astype(np.uint8),
                         cv2.COLOR_GRAY2BGR)
    x, y, w, h = ROI
    (text_w, _text_h), _baseline = cv2.getTextSize(
        digits, FONT, FONT_SCALE, FONT_THICKNESS
    )
    org = (x + w - text_w - TEXT_RIGHT_MARGIN, y + h - TEXT_BOTTOM_MARGIN)
    cv2.putText(
        frame, digits, org, FONT, FONT_SCALE, (255, 255, 255),
        FONT_THICKNESS, cv2.LINE_AA,
    )
    return frame


# ---------------------------------------------------------------------------
# Three fixed comparison methods
# ---------------------------------------------------------------------------
def _gray(frame: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def _xor_fraction(bin1: np.ndarray, bin2: np.ndarray, roi: tuple[int, int, int, int]) -> float:
    x, y, w, h = roi
    a = bin1[y:y + h, x:x + w]
    b = bin2[y:y + h, x:x + w]
    changed = cv2.bitwise_xor(a, b)
    return float(np.count_nonzero(changed)) / float(w * h)


def method_a(frame1: np.ndarray, frame2: np.ndarray) -> float:
    """A: XOR fraction of gray>190 binary images in the HUD ROI."""
    g1 = _gray(frame1)
    g2 = _gray(frame2)
    b1 = (g1 > A_GRAY_THRESHOLD).astype(np.uint8)
    b2 = (g2 > A_GRAY_THRESHOLD).astype(np.uint8)
    return _xor_fraction(b1, b2, ROI)


def _tophat_binary(frame: np.ndarray) -> np.ndarray:
    gray = _gray(frame)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, TOPHAT_KERNEL_SIZE)
    top_hat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)
    return (top_hat > TOPHAT_THRESHOLD).astype(np.uint8)


def method_b(frame1: np.ndarray, frame2: np.ndarray) -> float:
    """B: XOR fraction of Top-hat binary images in the HUD ROI."""
    b1 = _tophat_binary(frame1)
    b2 = _tophat_binary(frame2)
    return _xor_fraction(b1, b2, ROI)


def method_c(frame1: np.ndarray, frame2: np.ndarray) -> float:
    """C: HUD Top-hat XOR fraction minus adjacent background control ROI."""
    b1 = _tophat_binary(frame1)
    b2 = _tophat_binary(frame2)
    hud = _xor_fraction(b1, b2, ROI)
    control = _xor_fraction(b1, b2, CONTROL_ROI)
    return hud - control


# ---------------------------------------------------------------------------
# Dataset definition
# ---------------------------------------------------------------------------
POSITIVE_TRANSITIONS = [
    ("1", "7", "1<->7"),
    ("7", "1", "1<->7"),
    ("1", "7", "1<->7"),
    ("7", "1", "1<->7"),
    ("0", "8", "0<->8"),
    ("8", "0", "0<->8"),
    ("0", "8", "0<->8"),
    ("8", "0", "0<->8"),
    ("6", "8", "6<->8"),
    ("8", "6", "6<->8"),
    ("6", "8", "6<->8"),
    ("8", "6", "6<->8"),
    ("9", "10", "digit_increase"),
    ("99", "100", "digit_increase"),
    ("7", "12", "digit_increase"),
    ("8", "10", "digit_increase"),
    ("2", "3", "other"),
    ("5", "6", "other"),
    ("3", "9", "other"),
    ("4", "0", "other"),
]

SAME_DIGITS = ["1", "7", "0", "8", "6", "9", "10", "12", "99", "100"]

CONDITIONS = [
    {
        "id": "digits_same_bg_change",
        "label_ja": "数字不変 + 背景変化",
        "digit_changed": False,
        "bg_changed": True,
        "contact_indices": (0, 1),
    },
    {
        "id": "digits_change_bg_same",
        "label_ja": "数字変化 + 背景不変",
        "digit_changed": True,
        "bg_changed": False,
        "contact_indices": (0, 4),
    },
    {
        "id": "both_change",
        "label_ja": "数字変化 + 背景変化",
        "digit_changed": True,
        "bg_changed": True,
        "contact_indices": (8, 12),
    },
    {
        "id": "neither",
        "label_ja": "数字不変 + 背景不変",
        "digit_changed": False,
        "bg_changed": False,
        "contact_indices": (0, 1),
    },
]


def build_pair(condition_index: int, condition: dict, pair_index: int):
    rng = np.random.default_rng(SEED + condition_index * 10000 + pair_index * 101)
    base = make_background(rng)

    if condition["digit_changed"]:
        digits1, digits2, transition = POSITIVE_TRANSITIONS[pair_index]
    else:
        digits1 = SAME_DIGITS[pair_index % len(SAME_DIGITS)]
        digits2 = digits1
        transition = "same"

    background2 = make_background_variant(base, rng) if condition["bg_changed"] else base.copy()
    frame1 = render_frame(base, digits1)
    frame2 = render_frame(background2, digits2)
    return frame1, frame2, digits1, digits2, transition


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def compute_metrics(records: list[dict], method: str) -> dict:
    tp = fp = tn = fn = 0
    for rec in records:
        detected = bool(rec["detected"][method])
        positive = bool(rec["digit_changed"])
        if positive and detected:
            tp += 1
        elif positive and not detected:
            fn += 1
        elif not positive and detected:
            fp += 1
        else:
            tn += 1
    positives = tp + fn
    negatives = fp + tn
    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "positives": positives,
        "negatives": negatives,
        "recall": (tp / positives) if positives else None,
        "false_positive_rate": (fp / negatives) if negatives else None,
    }


def make_contact_sheet(examples: list[tuple[str, str, np.ndarray, np.ndarray]]) -> None:
    tile_w, tile_h = 420, 197
    label_h, margin, header_h = 24, 10, 64
    cols, rows = 4, 4
    sheet_w = margin + cols * (tile_w + margin)
    sheet_h = header_h + margin + rows * (label_h + tile_h + margin)
    sheet = np.full((sheet_h, sheet_w, 3), 24, dtype=np.uint8)

    cv2.putText(sheet, "Synthetic HUD input contact sheet (raw frames, no video data)",
                (12, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.68, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(sheet,
                "C1 digits same + bg change | C2 digits change + bg same | C3 both change | C4 neither",
                (12, 52), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (210, 210, 210), 1, cv2.LINE_AA)

    # The examples list is ordered as 4 conditions x 2 examples x 2 frames.
    # Each tuple is (label, condition_id, before, after); we render the pair.
    for idx, (_label, _cond_id, before, after) in enumerate(examples):
        row = idx // 2
        example_in_row = idx % 2
        for j, (img, phase) in enumerate(((before, "before"), (after, "after"))):
            col = example_in_row * 2 + j
            tile = cv2.resize(img, (tile_w, tile_h), interpolation=cv2.INTER_AREA)
            x = margin + col * (tile_w + margin)
            y = header_h + margin + row * (label_h + tile_h + margin)
            sheet[y:y + label_h, x:x + tile_w] = 0
            text = f"C{row + 1} ex{example_in_row + 1} {phase}: {_label}"
            cv2.putText(sheet, text, (x + 5, y + 17), cv2.FONT_HERSHEY_SIMPLEX,
                        0.43, (255, 255, 255), 1, cv2.LINE_AA)
            sheet[y + label_h:y + label_h + tile_h, x:x + tile_w] = tile
            cv2.rectangle(sheet, (x, y), (x + tile_w - 1, y + label_h + tile_h - 1),
                          (90, 90, 90), 1)

    cv2.imwrite(str(CONTACT_SHEET_PATH), sheet)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    cv2.setNumThreads(1)
    cv2.setRNGSeed(SEED)

    run_start_cpu = time.process_time()
    run_start_wall = time.perf_counter()

    records: list[dict] = []
    contact_examples: list[tuple[str, str, np.ndarray, np.ndarray]] = []
    gen_cpu = 0.0
    method_cpu = {"A": 0.0, "B": 0.0, "C": 0.0}

    for c_idx, condition in enumerate(CONDITIONS):
        for pair_idx in range(PAIRS_PER_CONDITION):
            t0 = time.process_time()
            frame1, frame2, digits1, digits2, transition = build_pair(
                c_idx, condition, pair_idx
            )
            gen_cpu += time.process_time() - t0

            scores = {}
            detected = {}
            for method_name, method_fn, threshold in (
                ("A", method_a, A_CHANGE_THRESHOLD),
                ("B", method_b, B_CHANGE_THRESHOLD),
                ("C", method_c, C_CHANGE_THRESHOLD),
            ):
                t0 = time.process_time()
                score = method_fn(frame1, frame2)
                method_cpu[method_name] += time.process_time() - t0
                scores[method_name] = float(score)
                detected[method_name] = bool(score > threshold)

            records.append({
                "pair_id": f"c{c_idx + 1}_p{pair_idx + 1:02d}",
                "condition": condition["id"],
                "condition_index": c_idx + 1,
                "pair_index": pair_idx + 1,
                "digits_frame1": digits1,
                "digits_frame2": digits2,
                "transition": transition,
                "digit_changed": bool(digits1 != digits2),
                "bg_changed": bool(condition["bg_changed"]),
                "scores": scores,
                "detected": detected,
            })

            if pair_idx in condition["contact_indices"]:
                contact_examples.append((
                    f"{digits1} -> {digits2}" if digits1 != digits2 else digits1,
                    condition["id"],
                    frame1.copy(),
                    frame2.copy(),
                ))

    # Keep contact examples ordered by condition and pair index.
    # The loop above appends in that order, which matches the row layout.

    metrics = {
        method: compute_metrics(records, method)
        for method in ("A", "B", "C")
    }

    per_condition = {}
    for condition in CONDITIONS:
        subset = [r for r in records if r["condition"] == condition["id"]]
        per_condition[condition["id"]] = {
            "label_ja": condition["label_ja"],
            "pairs": len(subset),
            "digit_changed": condition["digit_changed"],
            "bg_changed": condition["bg_changed"],
            "detected": {
                method: sum(1 for r in subset if r["detected"][method])
                for method in ("A", "B", "C")
            },
        }

    positive_by_transition = {}
    for tag in ("1<->7", "0<->8", "6<->8", "digit_increase", "other"):
        subset = [r for r in records if r["digit_changed"] and r["transition"] == tag]
        positive_by_transition[tag] = {
            "pairs": len(subset),
            "detected": {
                method: sum(1 for r in subset if r["detected"][method])
                for method in ("A", "B", "C")
            },
        }

    run_cpu = time.process_time() - run_start_cpu
    run_wall = time.perf_counter() - run_start_wall
    rss_raw = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    if sys.platform == "darwin":
        rss_unit = "bytes"
        rss_mib = rss_raw / (1024.0 * 1024.0)
    elif sys.platform.startswith("linux"):
        rss_unit = "KiB"
        rss_mib = rss_raw / 1024.0
    else:
        rss_unit = "platform_units"
        rss_mib = None

    script_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

    result = {
        "meta": {
            "title": "Synthetic HUD change-candidate extraction PoC (CPU, Top-hat)",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "script": "reproduce.py",
            "script_sha256": script_sha256,
            "seed": SEED,
            "synthetic_only": True,
            "real_video_accuracy_claimed": False,
            "linear_updated": False,
            "issue_completed": False,
            "notes": [
                "Synthetic OpenCV HUD only; not a real-video accuracy claim.",
                "Frame-level columns and detection latency were not measured.",
                "Thresholds and kernel were fixed before the single run and not tuned afterwards.",
                "The three methods are independent implementations for CPU-time comparison; C recomputes Top-hat.",
            ],
        },
        "environment": {
            "platform": platform.platform(),
            "system": platform.system(),
            "machine": platform.machine(),
            "python_version": platform.python_version(),
            "opencv_version": cv2.__version__,
            "numpy_version": np.__version__,
            "cv2_threads": int(cv2.getNumThreads()),
        },
        "parameters": {
            "frame_width": FRAME_W,
            "frame_height": FRAME_H,
            "hud_roi": {"x": ROI[0], "y": ROI[1], "w": ROI[2], "h": ROI[3]},
            "control_roi": {"x": CONTROL_ROI[0], "y": CONTROL_ROI[1],
                             "w": CONTROL_ROI[2], "h": CONTROL_ROI[3]},
            "pairs_per_condition": PAIRS_PER_CONDITION,
            "method_a": {
                "gray_threshold": A_GRAY_THRESHOLD,
                "change_threshold_fraction": A_CHANGE_THRESHOLD,
            },
            "method_b": {
                "tophat_kernel_shape": "ellipse",
                "tophat_kernel_size": list(TOPHAT_KERNEL_SIZE),
                "tophat_threshold": TOPHAT_THRESHOLD,
                "change_threshold_fraction": B_CHANGE_THRESHOLD,
            },
            "method_c": {
                "tophat_kernel_shape": "ellipse",
                "tophat_kernel_size": list(TOPHAT_KERNEL_SIZE),
                "tophat_threshold": TOPHAT_THRESHOLD,
                "change_threshold_score": C_CHANGE_THRESHOLD,
                "score": "hud_xor_fraction - control_xor_fraction",
            },
            "font": "FONT_HERSHEY_SIMPLEX",
            "font_scale": FONT_SCALE,
            "font_thickness": FONT_THICKNESS,
        },
        "dataset": {
            "conditions": [
                {
                    "id": c["id"],
                    "label_ja": c["label_ja"],
                    "digit_changed": c["digit_changed"],
                    "bg_changed": c["bg_changed"],
                    "pairs": PAIRS_PER_CONDITION,
                }
                for c in CONDITIONS
            ],
            "positive_conditions": ["digits_change_bg_same", "both_change"],
            "negative_conditions": ["digits_same_bg_change", "neither"],
            "positive_transition_coverage": {
                "1<->7": sum(1 for t in POSITIVE_TRANSITIONS if t[2] == "1<->7"),
                "0<->8": sum(1 for t in POSITIVE_TRANSITIONS if t[2] == "0<->8"),
                "6<->8": sum(1 for t in POSITIVE_TRANSITIONS if t[2] == "6<->8"),
                "digit_increase": sum(1 for t in POSITIVE_TRANSITIONS if t[2] == "digit_increase"),
            },
        },
        "metrics": metrics,
        "per_condition": per_condition,
        "positive_by_transition": positive_by_transition,
        "timing": {
            "generation_cpu_s": gen_cpu,
            "method_cpu_s": method_cpu,
            "method_cpu_ms_per_pair": {
                method: (method_cpu[method] * 1000.0 / len(records))
                for method in ("A", "B", "C")
            },
            "total_cpu_s": run_cpu,
            "total_wall_s": run_wall,
        },
        "memory": {
            "max_rss_raw": rss_raw,
            "max_rss_unit": rss_unit,
            "max_rss_mib": rss_mib,
        },
        "pairs": records,
    }

    RESULT_PATH.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    make_contact_sheet(contact_examples)

    print(json.dumps({
        "result_json": str(RESULT_PATH),
        "contact_sheet": str(CONTACT_SHEET_PATH),
        "metrics": metrics,
        "timing": result["timing"],
        "memory": result["memory"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
