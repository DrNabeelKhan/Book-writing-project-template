# Concatenate all chapters into one manuscript
import glob

files = [
    "docs/front-matter/*.md",
    "docs/chapters/*.md",
    "docs/appendices/*.md",
    "docs/back-matter/*.md"
]

with open("build/full-manuscript.md", "w") as out:
    for pattern in files:
        for f in sorted(glob.glob(pattern)):
            out.write(open(f).read() + "\n\n")
