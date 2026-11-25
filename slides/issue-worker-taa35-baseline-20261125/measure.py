#!/usr/bin/env python3
"""TAA-35 baseline measurement (plan-only run, no code change to the repo).

Two sources of numbers:

1. Recorded runs already in the repo (reports/battle-royale-damage-20261014/*):
   Bedrock token usage, chunk latency and pipeline stage timing. No paid API is
   called here; the script only reads the JSON/JSONL that previous runs left.
2. A local CPU-only run of the current ammo scanner over the two shared
   training-range clips, to get a decode/scan cost per frame that can be turned
   into Fargate cost with the task size from the repo's own task definition.

Unit prices are read from the public AWS Price List API for ap-northeast-1 and
written into stats.json together with the publication date, so the numbers can
be re-checked. Nothing private is written: only aggregates and clip names that
are already shared.

Outputs stats.json next to this file.
"""
from __future__ import annotations

import json
import os
import statistics
import sys
import time
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parent
REPO = Path(os.environ.get("REPO_ROOT", "/Users/taaaaryu/Desktop/thumaster/beta/thumaster/experiments"))
VIDEO_DIR = Path(os.environ.get("VIDEO_DIR", str(REPO / "shared" / "videos" / "training-range")))
CLIPS = ["demo_test_short1.mp4", "demo_test_short2.mp4"]

# --- unit prices (USD), ap-northeast-1, AWS Price List API, 2026-11-23 ---
# AmazonBedrockFoundationModels / AmazonECS offer files, "On-Demand" terms.
PRICE_SOURCE = {
    "bedrock": "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonBedrockFoundationModels/current/ap-northeast-1/index.json",
    "fargate": "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonECS/current/ap-northeast-1/index.json",
    "published": "2026-11-23",
}
PRICE_PER_MTOK = {
    "haiku-4.5": {"input": 1.10, "output": 5.50, "label": "Claude Haiku 4.5 (regional)"},
    "sonnet-4.6": {"input": 3.30, "output": 16.50, "label": "Claude Sonnet 4.6 (regional)"},
}
# Fargate ARM64, ap-northeast-1: 2 vCPU / 4 GB (analysis/docker/infra/ecs-task-definition*.json)
FARGATE_VCPU_USD_H = 0.04045
FARGATE_GB_USD_H = 0.00442
TASK_VCPU = 2
TASK_GB = 4
TASK_USD_H = TASK_VCPU * FARGATE_VCPU_USD_H + TASK_GB * FARGATE_GB_USD_H


def model_key(model: str | None) -> str | None:
    name = (model or "").lower()
    if "haiku-4-5" in name:
        return "haiku-4.5"
    if "sonnet-4-6" in name:
        return "sonnet-4.6"
    return None


def cost_usd(tokens_in: int, tokens_out: int, key: str) -> float:
    p = PRICE_PER_MTOK[key]
    return tokens_in * p["input"] / 1_000_000 + tokens_out * p["output"] / 1_000_000


def recorded_runs() -> list[dict]:
    runs = []
    for chunks_path in sorted(REPO.glob("reports/**/chunks/summary.json")):
        run_dir = chunks_path.parent.parent
        chunk_doc = json.loads(chunks_path.read_text())
        chunks = chunk_doc.get("chunks") or []
        tokens_in = sum(int(c.get("input_tokens") or 0) for c in chunks)
        tokens_out = sum(int(c.get("output_tokens") or 0) for c in chunks)
        key = model_key(chunk_doc.get("model") or (chunks[0]["model"] if chunks else None))
        if key is None or not tokens_in:
            continue
        summary_path = run_dir / "summary.json"
        summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
        timing = summary.get("stage_timing") or {}
        total_sec = timing.get("pipeline_total_sec")
        bedrock_usd = cost_usd(tokens_in, tokens_out, key)
        cpu_usd = (float(total_sec) * TASK_USD_H / 3600.0) if total_sec else None
        runs.append({
            "run": run_dir.relative_to(REPO).as_posix(),
            "model": key,
            "items": int(chunk_doc.get("total_items") or 0),
            "chunks": len(chunks),
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "llm_ms": round(sum(float(c.get("latency_ms") or 0) for c in chunks)),
            "frames": int(summary.get("total_frames") or 0),
            "fps": float(summary.get("fps") or 0),
            "stage_sec": {k: round(float(v), 3) for k, v in timing.items() if isinstance(v, (int, float))},
            "bedrock_usd": round(bedrock_usd, 6),
            "cpu_usd": round(cpu_usd, 6) if cpu_usd is not None else None,
        })
    return runs


def local_scan() -> list[dict]:
    from analysis.detail.scan import VideoAmmoScanner

    out = []
    for name in CLIPS:
        path = VIDEO_DIR / name
        if not path.exists():
            continue
        capture = cv2.VideoCapture(str(path))
        if not capture.isOpened():
            continue
        frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        fps = float(capture.get(cv2.CAP_PROP_FPS) or 0.0)

        started = time.perf_counter()
        decoded = 0
        while True:
            ok, _frame = capture.read()
            if not ok:
                break
            decoded += 1
        decode_sec = time.perf_counter() - started

        capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
        scanner = VideoAmmoScanner(scan_workers=1)
        started = time.perf_counter()
        _samples, _intervals, fine, candidates = scanner.scan(capture=capture, total_frames=frames)
        scan_sec = time.perf_counter() - started
        capture.release()

        out.append({
            "clip": name,
            "frames": frames,
            "fps": round(fps, 2),
            "decoded": decoded,
            "decode_sec": round(decode_sec, 3),
            "scan_sec": round(scan_sec, 3),
            "ms_per_frame": round(scan_sec / frames * 1000, 2) if frames else None,
            "candidates": len(candidates),
            "fine_intervals": len(fine),
            "scan_usd_on_fargate": round(scan_sec * TASK_USD_H / 3600.0, 6),
            "decode_usd_on_fargate": round(decode_sec * TASK_USD_H / 3600.0, 6),
        })
    return out


def main() -> None:
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    runs = recorded_runs()
    clips = local_scan()

    totals = [r["bedrock_usd"] + (r["cpu_usd"] or 0.0) for r in runs]
    shares = [r["bedrock_usd"] / t for r, t in zip(runs, totals) if t]
    per_item = [r["bedrock_usd"] / r["items"] for r in runs if r["items"]]

    stats = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "host": {"python": sys.version.split()[0], "opencv": cv2.__version__, "cpu": os.uname().machine},
        "price_source": PRICE_SOURCE,
        "prices": {
            "per_mtok_usd": {k: {"input": v["input"], "output": v["output"], "label": v["label"]} for k, v in PRICE_PER_MTOK.items()},
            "fargate_arm_usd_per_hour": {
                "vcpu": FARGATE_VCPU_USD_H,
                "gb": FARGATE_GB_USD_H,
                "task_2vcpu_4gb": round(TASK_USD_H, 5),
            },
        },
        "recorded_runs": runs,
        "summary": {
            "runs": len(runs),
            "bedrock_usd_median": round(statistics.median(r["bedrock_usd"] for r in runs), 6),
            "bedrock_usd_max": round(max(r["bedrock_usd"] for r in runs), 6),
            "bedrock_share_median": round(statistics.median(shares), 3),
            "usd_per_event_median": round(statistics.median(per_item), 6),
            "cpu_usd_max": round(max(r["cpu_usd"] or 0 for r in runs), 6),
        },
        "local_scan": clips,
    }
    (ROOT / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(stats["summary"], ensure_ascii=False, indent=2))
    for r in runs:
        print(r["run"], r["model"], r["items"], "items", r["tokens_in"], r["tokens_out"], r["bedrock_usd"], r["cpu_usd"])
    for c in clips:
        print(c)


if __name__ == "__main__":
    main()
