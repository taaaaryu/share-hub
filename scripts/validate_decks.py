#!/usr/bin/env python3
"""Validate catalog entries and basic slide content before publishing."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_KINDS = {"cover", "takeaway", "metrics", "comparison", "evidence", "closing", "steps", "number"}


def main() -> None:
    catalog = json.loads((ROOT / "catalog.json").read_text())
    seen = set()
    for entry in catalog:
        slug = entry["slug"]
        assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug), slug
        assert slug not in seen, f"duplicate slug: {slug}"
        seen.add(slug)
        folder = ROOT / "slides" / slug
        assert (folder / "index.html").is_file(), f"missing page: {slug}"
        deck = json.loads((folder / "deck.json").read_text())
        assert deck["title"] == entry["title"], f"title mismatch: {slug}"
        assert deck["slides"], f"empty deck: {slug}"
        for number, slide in enumerate(deck["slides"], 1):
            assert slide.get("kind") in ALLOWED_KINDS, f"invalid layout: {slug} #{number}"
            assert slide.get("title") and slide.get("body"), f"missing content: {slug} #{number}"
            assert len(slide["title"].replace("\n", "")) <= 38, f"title too long: {slug} #{number}"
            assert len(slide["body"]) <= 125, f"body too long: {slug} #{number}"
            for source in slide.get("sources", []):
                assert source.get("label") and re.match(r"^https?://", source.get("url", "")), f"invalid source: {slug} #{number}"
    print(f"Validated {len(catalog)} decks")


if __name__ == "__main__":
    main()
