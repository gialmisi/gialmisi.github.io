# gialmisi.github.io

Personal academic homepage and CV for Giovanni Misitano, built with MkDocs Material and a Jinja2-templated LaTeX CV.

## Project structure

```
├── data/                  # YAML data files (shared by website and CV)
├── website/               # MkDocs page sources (Markdown + Jinja2 macros)
├── macros/main.py         # MkDocs macros plugin: load_data / load_data_for
├── mkdocs.yml             # MkDocs configuration
├── cv/
│   ├── build_cv.py        # Builds cv/output/cv.tex from data/ and the template
│   ├── cv_template.tex    # Jinja2 LaTeX template (TENK/RCF format)
│   └── output/            # Generated .tex and .pdf
└── pyproject.toml         # Python dependencies (managed with uv)
```

## Prerequisites

- [uv](https://docs.astral.sh/uv/) for Python dependency management
- A LaTeX distribution with `pdflatex` (e.g., TeX Live) for CV compilation

Install dependencies:

```bash
uv sync
```

## Website

### Local preview

```bash
uv run mkdocs serve
```

This starts a local server at `http://127.0.0.1:8000` with live reload.

### Deploy

```bash
uv run mkdocs gh-deploy --remote-branch main
```

This builds the site and pushes the static output to the `main` branch, which GitHub Pages serves. The `work` branch is the source branch.

## CV

### Build

```bash
uv run python cv/build_cv.py
cd cv/output && pdflatex cv.tex
```

The first command renders the Jinja2 template into `cv/output/cv.tex`. The second compiles it to PDF.

## Updating content

All content lives in YAML files under `data/`. Both the website and CV read from the same data files, filtered by the `include` field on each entry.

### The `include` field

Each entry in a YAML data file has an `include` list that controls where it appears:

- `include: [website]` — website only
- `include: [cv]` — CV only
- `include: [website, cv]` — both

If `include` is omitted, the entry appears in both by default.

### Data files

| File | Contents |
|---|---|
| `personal.yaml` | Name, ORCID, languages |
| `education.yaml` | Degrees |
| `other_education.yaml` | Other education and expertise (optional, CV only) |
| `research.yaml` | Positions, research visits, projects, outputs |
| `teaching.yaml` | Teaching experience |
| `supervision.yaml` | Thesis supervision |
| `activities.yaml` | Positions of trust, rewards, funding |
| `publications.yaml` | Peer-reviewed publications |
| `manuscripts.yaml` | Manuscripts under review |
| `disseminations.yaml` | Invited talks, conferences, tutorials |
| `career_breaks.yaml` | Career breaks (optional, CV only) |
| `other_merits.yaml` | Other merits (optional, CV only) |

### Adding a new entry

Edit the relevant YAML file and add an entry following the existing format. For example, to add a publication:

```yaml
- authors: "A. Author, B. Author"
  title: "Paper title"
  journal: "Journal Name"
  year: "2026"
  include: [website, cv]
```

### Optional CV sections

Three CV sections only appear when their data files contain entries: **Other education and expertise**, **Career breaks**, and **Other merits**. Each file contains a commented example showing the expected format.

After editing data files, rebuild the website and/or CV as described above.
