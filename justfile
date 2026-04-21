# Build and serve the website and generate documents from YAML data.

# Install Python dependencies
sync:
    uv sync

# Start local website preview with live reload
serve:
    uv run mkdocs serve

# Deploy website to GitHub Pages (main branch)
deploy:
    uv run mkdocs gh-deploy --remote-branch main

# Build the CV PDF
cv:
    uv run python cv/build_cv.py
    cd cv/output && pdflatex -interaction=nonstopmode cv.tex && pdflatex -interaction=nonstopmode cv.tex

# Build the RCF publication list PDF (pass year as argument, defaults to current year)
publications year="":
    #!/usr/bin/env bash
    set -euo pipefail
    uv run python publications/build_publications.py {{ if year != "" { "--year " + year } else { "" } }}
    cd publications/output
    texfile=$(ls publications_RCF*.tex | head -1)
    pdflatex -interaction=nonstopmode "$texfile"
    pdflatex -interaction=nonstopmode "$texfile"

# Build both CV and publication list
docs: cv publications
