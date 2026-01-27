#!/usr/bin/env python3
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DIAGRAMS = ROOT / "docs" / "shared-assets" / "diagrams"
OUT_DIR = ROOT / "build" / "diagrams"

def render():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for mmd in DIAGRAMS.rglob("*.mmd"):
        out_svg = OUT_DIR / (mmd.stem + ".svg")
        cmd = [
            "mmdc",
            "-i", str(mmd),
            "-o", str(out_svg),
        ]
        subprocess.run(cmd, check=True)
        print(f"Rendered: {out_svg}")

if __name__ == "__main__":
    render()
