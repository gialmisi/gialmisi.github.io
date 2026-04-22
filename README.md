# gialmisi.github.io

Personal academic homepage and CV for Giovanni Misitano, built with MkDocs Material and a Jinja2-templated LaTeX CV.

## Project structure

```
├── data/                  # YAML data files (shared by website, CV, and publication list)
├── website/               # MkDocs page sources (Markdown + Jinja2 macros)
├── macros/main.py         # MkDocs macros plugin: load_data / load_data_for
├── mkdocs.yml             # MkDocs configuration
├── lib/build_utils.py     # Shared LaTeX/YAML utilities for build scripts
├── cv/
│   ├── build_cv.py        # Builds cv/output/cv.tex from data/ and the template
│   ├── cv_template.tex    # Jinja2 LaTeX template (TENK/RCF format)
│   └── output/            # Generated .tex and .pdf
├── publications/
│   ├── build_publications.py   # Builds the RCF publication list from data/
│   ├── publications_template.tex  # Jinja2 LaTeX template (RCF format)
│   └── output/            # Generated .tex and .pdf
├── justfile               # Build recipes
└── pyproject.toml         # Python dependencies (managed with uv)
```

## Prerequisites

- [uv](https://docs.astral.sh/uv/) for Python dependency management
- A LaTeX distribution with `pdflatex` (e.g., TeX Live) for PDF compilation
- [just](https://github.com/casey/just) command runner (optional, for convenient build commands)

Install dependencies:

```bash
uv sync
# or
just sync
```

## Website

### Local preview

```bash
just serve
# or
uv run mkdocs serve
```

This starts a local server at `http://127.0.0.1:8000` with live reload.

### Deploy

```bash
just deploy
# or
uv run mkdocs gh-deploy --remote-branch main
```

This builds the site and pushes the static output to the `main` branch, which GitHub Pages serves. The `work` branch is the source branch.

## CV

### Build

```bash
just cv
```

Or manually:

```bash
uv run python cv/build_cv.py
cd cv/output && pdflatex cv.tex && pdflatex cv.tex
```

The first command renders the Jinja2 template into `cv/output/cv.tex`. The second compiles it to PDF (run twice for correct page references in the header).

## List of Publications

Generates a publication list PDF following the [Research Council of Finland guidelines](https://www.aka.fi/en/research-funding/apply-for-funding/how-to-apply-for-funding/az-index-of-application-guidelines/list-of-publications/), with publications classified by Ministry of Education categories (A-I).

### Build

```bash
just publications
# or with a specific year:
just publications 2026
```

Or manually:

```bash
uv run python publications/build_publications.py --year 2026
cd publications/output && pdflatex publications_RCF2026_Misitano.tex && pdflatex publications_RCF2026_Misitano.tex
```

### Build both CV and publication list

```bash
just docs
```

## Updating content

All content lives in YAML files under `data/`. Both the website and CV read from the same data files, filtered by the `include` field on each entry.

### The `include` field

Each entry in a YAML data file has an `include` list that controls where it appears:

- `include: [website]` — website only
- `include: [cv]` — CV only
- `include: [website, cv]` — both

If `include` is omitted, the entry appears in both website and CV by default.

### The `rcf_category` field

Any entry (in *any* YAML file under `data/`) that carries an `rcf_category` field is picked up by the publication list build, regardless of where it lives. This lets non-publication items (open-source software under `research.yaml` `outputs`, audiovisual tutorials under `disseminations.yaml`, etc.) also appear in the RCF list.

An entry with `rcf_category` must also provide `authors`, `title`, `journal`, and `year` — the build fails loudly if any are missing.

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
| `publications.yaml` | Peer-reviewed publications (with `rcf_category` for the publication list) |
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
  rcf_category: "A1"
  include: [website, cv]
```

The `rcf_category` field classifies the entry for the RCF publication list (A1 = journal article, A3 = book chapter, A4 = conference proceedings, G1/G2/G5 = theses, I1 = audiovisual, I2 = ICT application, etc.). See `publications/build_publications.py` for the full list of subcategory codes.

### Optional CV sections

Three CV sections only appear when their data files contain entries: **Other education and expertise**, **Career breaks**, and **Other merits**. Each file contains a commented example showing the expected format.

After editing data files, rebuild the website and/or CV as described above.
