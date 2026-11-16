#!/usr/bin/env python3
"""Small CPU-only measurement for the TAA-46 plan (state machine trigger).

Reads the two shared training-range clips, runs the baseline signature
(gray > 190 binarisation inside the damage ROI) and compares two trigger
policies:

  A  per-frame diff  : fire whenever change_ratio >= 0.015 versus the
                       previous frame (the current baseline behaviour)
  B  state machine   : reference = last *confirmed stable* signature,
                       require a settle window before we accept a change,
                       then emit exactly one OCR candidate per change

Outputs JSON to stats.json. No repo files are modified; nothing paid is used.
"""
import json
import os
import time
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent
VIDEO_DIR = Path(os.environ.get("VIDEO_DIR", "shared/videos/training-range"))
CLIPS = ["demo_test_short1.mp4", "demo_test_short2.mp4"]
ROI = (460, 28, 1036, 128)  # x1, y1, x2, y2  (576x100 box, matches the 44 profile)
GRAY_THRESHOLD = 190
CHANGE_RATIO_THRESHOLD = 0.015
SETTLE_SEC = 0.25
RECHECK_SEC = 5.0


def signature(frame):
    x1, y1, x2, y2 = ROI
    crop = frame[y1:y2, x1:x2]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    return (gray > GRAY_THRESHOLD).astype(np.uint8)


def ratio(a, b):
    return float(np.count_nonzero(a != b)) / float(a.size)


def run_clip(name):
    path = VIDEO_DIR / name
    cap = cv2.VideoCapture(str(path))
    fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
    settle_frames = max(2, int(round(SETTLE_SEC * fps)))
    recheck_frames = max(10, int(round(RECHECK_SEC * fps)))

    frames = 0
    per_frame_events = []
    state_events = []

    prev_sig = None
    ref_sig = None          # last confirmed stable signature
    state = "STABLE"
    settling = []           # ratios inside the settle window
    changed_since = None    # frame where the candidate started
    last_emit = None        # frame of the last emitted candidate
    ratios_all = []
    cpu_sec = 0.0

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        t0 = time.perf_counter()
        sig = signature(frame)
        if prev_sig is not None:
            r_prev = ratio(prev_sig, sig)
        else:
            r_prev = 0.0
        cpu_sec += time.perf_counter() - t0
        ratios_all.append(r_prev)

        # --- Policy A: vs previous frame
        if r_prev >= CHANGE_RATIO_THRESHOLD:
            per_frame_events.append(frames)

        # --- Policy B: state machine vs last confirmed stable signature
        if ref_sig is None:
            ref_sig = sig
            last_emit = frames
        r_ref = ratio(ref_sig, sig)
        if state == "STABLE":
            if r_ref >= CHANGE_RATIO_THRESHOLD:
                state = "SETTLING"
                settling = [r_ref]
                changed_since = frames
            elif last_emit is not None and frames - last_emit >= recheck_frames:
                state_events.append({"frame": frames, "reason": "periodic"})
                last_emit = frames
                ref_sig = sig
        elif state == "SETTLING":
            settling.append(r_ref)
            window = settling[-settle_frames:]
            quiet = sum(1 for v in window if v < CHANGE_RATIO_THRESHOLD)
            if len(window) == settle_frames and quiet >= settle_frames * 0.6:
                state_events.append(
                    {
                        "frame": frames,
                        "reason": "settled",
                        "start_frame": changed_since,
                        "settle_frames": frames - changed_since,
                        "max_ratio": max(settling),
                    }
                )
                ref_sig = sig
                state = "STABLE"
                last_emit = frames
                settling = []
                changed_since = None
            elif frames - changed_since > int(2.0 * fps):
                state_events.append(
                    {
                        "frame": frames,
                        "reason": "timeout_forced",
                        "start_frame": changed_since,
                        "settle_frames": frames - changed_since,
                        "max_ratio": max(settling),
                    }
                )
                ref_sig = sig
                state = "STABLE"
                last_emit = frames
                settling = []
                changed_since = None

        prev_sig = sig
        frames += 1

    cap.release()

    def runs(indices):
        """Collapse consecutive frames into events."""
        out = []
        for i in indices:
            if out and i - out[-1][-1] <= 1:
                out[-1].append(i)
            else:
                out.append([i])
        return out

    a_runs = runs(per_frame_events)
    # dedupe A events that are closer than the settle window (same animation)
    a_deduped = []
    for r in a_runs:
        if a_deduped and r[0] - a_deduped[-1] < settle_frames:
            continue
        a_deduped.append(r[0])

    settled = [e for e in state_events if e["reason"] == "settled"]
    return {
        "clip": name,
        "fps": round(fps, 2),
        "frames": frames,
        "duration_sec": round(frames / fps, 2) if fps else None,
        "roi": list(ROI),
        "thresholds": {
            "gray": GRAY_THRESHOLD,
            "change_ratio": CHANGE_RATIO_THRESHOLD,
            "settle_sec": SETTLE_SEC,
            "recheck_sec": RECHECK_SEC,
            "settle_frames": settle_frames,
            "recheck_frames": recheck_frames,
        },
        "policy_a": {
            "firing_frames": len(per_frame_events),
            "bursts": len(a_runs),
            "deduped_events": len(a_deduped),
            "max_ratio": round(max(ratios_all), 3) if ratios_all else None,
            "median_ratio": round(float(np.median(ratios_all)), 4) if ratios_all else None,
        },
        "policy_b": {
            "events": len(state_events),
            "settled": len(settled),
            "periodic": sum(1 for e in state_events if e["reason"] == "periodic"),
            "timeout_forced": sum(1 for e in state_events if e["reason"] == "timeout_forced"),
            "settle_frames_avg": round(
                float(np.mean([e["settle_frames"] for e in settled])), 1
            )
            if settled
            else None,
            "settle_frames_max": max((e["settle_frames"] for e in settled), default=None),
            "detail": state_events,
        },
        "cpu": {
            "signature_and_compare_sec": round(cpu_sec, 3),
            "ms_per_frame": round(1000.0 * cpu_sec / frames, 3) if frames else None,
        },
        "ratios": [round(v, 4) for v in ratios_all],
        "a_burst_starts": [r[0] for r in a_runs],
        "a_deduped_starts": a_deduped,
    }


def main():
    stats = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "shared/videos/training-range (2 clips), local CPU, OpenCV 5.0.0",
        "clips": [run_clip(c) for c in CLIPS],
    }
    (ROOT / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n")
    for c in stats["clips"]:
        print(
            c["clip"],
            "frames", c["frames"],
            "A_fires", c["policy_a"]["firing_frames"],
            "A_bursts", c["policy_a"]["bursts"],
            "A_dedup", c["policy_a"]["deduped_events"],
            "B_events", c["policy_b"]["events"],
            "B_settled", c["policy_b"]["settled"],
            "B_periodic", c["policy_b"]["periodic"],
            "ms/frame", c["cpu"]["ms_per_frame"],
        )


if __name__ == "__main__":
    main()
