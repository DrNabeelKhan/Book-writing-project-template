#!/bin/bash
python3 tools/consolidate.py

pandoc build/full-manuscript.md \
  --from markdown \
  --template tools/templates/latex-template.tex \
  --output build/full-manuscript.pdf \
  --metadata-file config/metadata.yaml
