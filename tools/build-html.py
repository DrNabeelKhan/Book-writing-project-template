#!/usr/bin/env python3
from pathlib import Path
import subprocess
import glob

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BUILD = ROOT / "build"
CONFIG = ROOT / "config"

def collect_sections():
    patterns = [
        "front-matter/*.md",
        "chapters/*.md",
        "appendices/*.md",
        "back-matter/*.md",
    ]
    files = []
    for pattern in patterns:
        files.extend(sorted(glob.glob(str(DOCS / pattern))))
    return files

def consolidate():
    BUILD.mkdir(exist_ok=True)
    out = BUILD / "full-manuscript.md"
    with out.open("w", encoding="utf-8") as f_out:
        for f in collect_sections():
            f_out.write(f"\n\n<!-- FILE: {Path(f).name} -->\n\n")
            f_out.write(Path(f).read_text(encoding="utf-8"))
            f_out.write("\n\n")
    return out

def build_html(md_path):
    out_html = BUILD / "full-manuscript.html"
    cmd = [
        "pandoc",
        str(md_path),
        "--defaults", str(CONFIG / "pandoc-html.yaml"),
        "-o", str(out_html),
    ]
    subprocess.run(cmd, check=True)
    print(f"Created: {out_html}")

if __name__ == "__main__":
    md = consolidate()
    build_html(md)
