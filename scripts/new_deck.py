#!/usr/bin/env python3
"""Create a new public slide deck from the shared viewer."""
import json
import re
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("使い方: python3 scripts/new_deck.py <英数字のslug> <タイトル>")
    slug, title = sys.argv[1:]
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise SystemExit("slugは小文字英数字とハイフンのみ使用できます")
    folder = ROOT / "slides" / slug
    if folder.exists():
        raise SystemExit(f"すでに存在します: {folder}")
    folder.mkdir(parents=True)
    shell = (ROOT / "slides" / "analysis-template" / "index.html").read_text()
    shell = shell.replace("解析資料の共通テンプレート", escape(title, quote=True))
    (folder / "index.html").write_text(shell)
    deck = json.loads((ROOT / "templates" / "analysis.json").read_text())
    deck["title"] = title
    deck["slides"][0]["title"] = title
    (folder / "deck.json").write_text(json.dumps(deck, ensure_ascii=False, indent=2) + "\n")
    catalog_path = ROOT / "catalog.json"
    catalog = json.loads(catalog_path.read_text())
    catalog.insert(0, {"slug": slug, "title": title, "description": f"解析資料 · {len(deck['slides'])}枚"})
    catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    print(f"作成しました: slides/{slug}/")


if __name__ == "__main__":
    main()
