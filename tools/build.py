#!/usr/bin/env python3
"""
Unified Build Script for the Book Project

Pipeline:
1. Inject glossary definitions into manuscript files
2. Render Mermaid diagrams to SVG
3. Consolidate all manuscript sections into full-manuscript.md
4. Generate Lunr.js search index
5. Generate chapter index for navigation
6. Generate PDF using Pandoc
7. Generate HTML using Pandoc
"""

import os
import glob
import subprocess
import yaml
import json
import re
from pathlib import Path

# -----------------------------
# Paths
# -----------------------------
ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BUILD = ROOT / "build"
CONFIG = ROOT / "config"
TOOLS = ROOT / "tools"
TEMPLATES = TOOLS / "templates"
DIAGRAMS = DOCS / "shared-assets" / "diagrams"
DIAGRAMS_OUT = BUILD / "diagrams"

OUTPUT_MD = BUILD / "full-manuscript.md"
OUTPUT_PDF = BUILD / "full-manuscript.pdf"
OUTPUT_HTML = BUILD / "full-manuscript.html"


# -----------------------------
# Helpers
# -----------------------------
def banner(msg):
    print("\n" + "=" * 70)
    print(msg)
    print("=" * 70 + "\n")


# -----------------------------
# 1. Glossary Injection
# -----------------------------
def load_glossary():
    glossary_file = CONFIG / "glossary.yaml"
    if not glossary_file.exists():
        print("No glossary.yaml found — skipping glossary injection.")
        return {}

    data = yaml.safe_load(glossary_file.read_text(encoding="utf-8"))
    return data.get("terms", {})


def inject_glossary():
    banner("Injecting glossary terms into manuscript files")

    terms = load_glossary()
    if not terms:
        return

    for md in DOCS.rglob("*.md"):
        if md.name.lower() == "glossary.md":
            continue

        text = md.read_text(encoding="utf-8")
        original = text

        for term, definition in terms.items():
            pattern = r"\b" + re.escape(term) + r"\b"
            replacement = f"{term} (*{definition}*)"
            text = re.sub(pattern, replacement, text, count=1)

        if text != original:
            md.write_text(text, encoding="utf-8")
            print(f"Updated glossary terms in: {md}")


# -----------------------------
# 2. Render Mermaid Diagrams
# -----------------------------
def render_diagrams():
    banner("Rendering Mermaid diagrams")

    DIAGRAMS_OUT.mkdir(parents=True, exist_ok=True)

    for mmd in DIAGRAMS.rglob("*.mmd"):
        out_svg = DIAGRAMS_OUT / (mmd.stem + ".svg")

        cmd = [
            "mmdc",
            "-i", str(mmd),
            "-o", str(out_svg),
        ]

        try:
            subprocess.run(cmd, check=True)
            print(f"Rendered: {out_svg}")
        except FileNotFoundError:
            print("ERROR: Mermaid CLI (mmdc) not found. Install via:")
            print("npm install -g @mermaid-js/mermaid-cli")
            return


# -----------------------------
# 3. Consolidate Markdown
# -----------------------------
def collect_sections():
    patterns = [
        "front-matter/*.md",
        "chapters/*.md",
        "appendices/*.md",
        "back-matter/*.md",
    ]

    files = []
    for pattern in patterns:
        files.extend(sorted((DOCS / pattern).glob()))

    return files


def consolidate_markdown():
    banner("Consolidating manuscript into full-manuscript.md")

    BUILD.mkdir(exist_ok=True)
    files = collect_sections()

    with open(OUTPUT_MD, "w", encoding="utf-8") as out:
        for f in files:
            out.write(f"\n\n<!-- FILE: {f.name} -->\n\n")
            out.write(f.read_text(encoding="utf-8"))
            out.write("\n\n")

    print(f"Created: {OUTPUT_MD}")


# -----------------------------
# 4. Build Lunr.js Search Index
# -----------------------------
def build_search_index():
    banner("Building Lunr.js search index")

    index_data = []
    for md in DOCS.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        index_data.append({
            "id": md.name,
            "title": md.stem,
            "body": text
        })

    (BUILD / "search-index.json").write_text(
        json.dumps(index_data, indent=2),
        encoding="utf-8"
    )

    print("Created: build/search-index.json")


# -----------------------------
# 5. Build Chapter Index
# -----------------------------
def build_chapter_index():
    banner("Generating chapter index")

    chapters = sorted((DOCS / "chapters").glob("*.md"))
    index = [c.name for c in chapters]

    (BUILD / "chapter-index.json").write_text(
        json.dumps(index, indent=2),
        encoding="utf-8"
    )

    print("Created: build/chapter-index.json")


# -----------------------------
# 6. Build PDF
# -----------------------------
def build_pdf():
    banner("Generating PDF via Pandoc")

    cmd = [
        "pandoc",
        str(OUTPUT_MD),
        "--defaults", str(CONFIG / "pandoc.yaml"),
        "--output", str(OUTPUT_PDF),
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"Created: {OUTPUT_PDF}")
    except FileNotFoundError:
        print("ERROR: Pandoc not found. Install it and ensure it's on PATH.")
    except subprocess.CalledProcessError:
        print("ERROR: Pandoc PDF build failed.")


# -----------------------------
# 7. Build HTML
# -----------------------------
def build_html():
    banner("Generating HTML via Pandoc")

    cmd = [
        "pandoc",
        str(OUTPUT_MD),
        "--defaults", str(CONFIG / "pandoc-html.yaml"),
        "--output", str(OUTPUT_HTML),
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"Created: {OUTPUT_HTML}")
    except FileNotFoundError:
        print("ERROR: Pandoc not found. Install it and ensure it's on PATH.")
    except subprocess.CalledProcessError:
        print("ERROR: Pandoc HTML build failed.")


# -----------------------------
# Main Pipeline
# -----------------------------
def main():
    banner("BOOK PROJECT — FULL BUILD STARTED")

    inject_glossary()
    render_diagrams()
    consolidate_markdown()
    build_search_index()
    build_chapter_index()
    build_pdf()
    build_html()

    banner("BUILD COMPLETE")


if __name__ == "__main__":
    main()
