#!/usr/bin/env python3
from pathlib import Path
import yaml
import re

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
CONFIG = ROOT / "config"

def load_glossary():
    data = yaml.safe_load((CONFIG / "glossary.yaml").read_text(encoding="utf-8"))
    return data.get("terms", {})

def inject_into_file(path, terms):
    text = path.read_text(encoding="utf-8")
    for term, definition in terms.items():
        pattern = r"\b" + re.escape(term) + r"\b"
        replacement = f"{term} (*{definition}*)"
        text = re.sub(pattern, replacement, text, count=1)
    path.write_text(text, encoding="utf-8")

def main():
    terms = load_glossary()
    for md in DOCS.rglob("*.md"):
        if md.name.lower() in {"glossary.md"}:
            continue
        inject_into_file(md, terms)

if __name__ == "__main__":
    main()
