"""Build RCF publication list from YAML data files."""

import argparse
import sys
from collections import OrderedDict
from datetime import date
from pathlib import Path

# Ensure project root is on the path for lib imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import jinja2

from lib.build_utils import DATA_DIR, latex_escape, load_yaml

TEMPLATE_PATH = Path(__file__).resolve().parent / "publications_template.tex"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"

REQUIRED_FIELDS = ("authors", "title", "journal", "year")

# Source: Finnish national publication type classification (Julkaisutyyppiluokitus)
# maintained by CSC. Codes and English labels taken from:
# http://uri.suomi.fi/codelist/research/Julkaisutyyppiluokitus
RCF_CATEGORIES = OrderedDict([
    ("A", "Peer-reviewed scientific articles"),
    ("B", "Non-refereed scientific articles"),
    ("C", "Scientific books (monographs)"),
    ("D", "Publications intended for professional communities"),
    ("E", "Publications intended for the general public"),
    ("F", "Public artistic and design activities"),
    ("G", "Theses"),
    ("H", "Patents and innovation announcements"),
    ("I", "Audiovisual publications and ICT applications"),
])

RCF_SUBCATEGORIES = OrderedDict([
    ("A1", "Journal article (refereed), original research"),
    ("A2", "Review article, Literature review, Systematic review"),
    ("A3", "Book section, Chapters in research books"),
    ("A4", "Article in conference proceedings"),
    ("B1", "Non-refereed journal articles"),
    ("B2", "Book section"),
    ("B3", "Article in conference proceedings (non-peer-reviewed)"),
    ("C1", "Scientific book"),
    ("C2", "Edited book, compilation, conference proceedings or special issue of a journal"),
    ("D1", "Article in a trade journal"),
    ("D2", "Article in a professional research book (incl. an introduction by the editor)"),
    ("D3", "Article in professional conference proceedings"),
    ("D4", "Published development or research report or study"),
    ("D5", "Textbook, professional manual or guide"),
    ("D6", "Edited professional book"),
    ("E1", "Popularised article, newspaper article"),
    ("E2", "Popularised monograph"),
    ("E3", "Edited popular book"),
    ("F1", "Published independent work of art or performance"),
    ("F2", "Partial implementation of a work of art or performance"),
    ("F3", "Artistic part of a non-artistic publication"),
    ("G1", "Polytechnic thesis, Bachelor's thesis"),
    ("G2", "Master's thesis, polytechnic Master's thesis"),
    ("G3", "Licentiate thesis"),
    ("G4", "Doctoral dissertation (monograph)"),
    ("G5", "Doctoral dissertation (articles)"),
    ("H1", "Granted patent"),
    ("H2", "Invention announcement"),
    ("I1", "Audiovisual publications"),
    ("I2", "ICT applications"),
])


def collect_rcf_entries(obj):
    """Recursively walk a loaded YAML structure and collect dicts with 'rcf_category'.

    A dict carrying 'rcf_category' is treated as a leaf — we do not recurse into
    it. This lets any entry in any data file opt into the publication list.
    """
    entries = []
    if isinstance(obj, dict):
        if "rcf_category" in obj:
            entries.append(obj)
        else:
            for v in obj.values():
                entries.extend(collect_rcf_entries(v))
    elif isinstance(obj, list):
        for item in obj:
            entries.extend(collect_rcf_entries(item))
    return entries


def load_rcf_entries():
    """Load all YAML files in the data directory and collect RCF-tagged entries."""
    entries = []
    for yaml_file in sorted(DATA_DIR.glob("*.yaml")):
        data = load_yaml(yaml_file.name)
        entries.extend(collect_rcf_entries(data))
    return entries


def validate_entries(entries):
    """Ensure every RCF-tagged entry has the fields required for rendering."""
    errors = []
    for entry in entries:
        missing = [f for f in REQUIRED_FIELDS if not entry.get(f)]
        if missing:
            errors.append(
                f"Entry tagged rcf_category={entry['rcf_category']!r} "
                f"is missing required field(s) {missing}: {entry}"
            )
        sub = entry["rcf_category"]
        if sub not in RCF_SUBCATEGORIES:
            errors.append(
                f"Entry has unknown rcf_category={sub!r} (expected one of "
                f"{sorted(RCF_SUBCATEGORIES)}): {entry}"
            )
    if errors:
        raise ValueError("Invalid RCF entries:\n  - " + "\n  - ".join(errors))


def group_publications(publications):
    """Group publications by main RCF category and subcategory.

    Returns an OrderedDict like:
        {
            "A": {
                "name": "Peer-reviewed scientific articles",
                "subcategories": [
                    {"code": "A1", "name": "...", "publications": [...]},
                    ...
                ],
            },
            ...
        }
    Only categories and subcategories with at least one publication are included.
    Publications within a subcategory are sorted by year, descending.
    """
    by_subcode = {}
    for pub in publications:
        code = pub.get("rcf_category", "A1")
        by_subcode.setdefault(code, []).append(pub)
    for code in by_subcode:
        by_subcode[code].sort(key=lambda p: str(p.get("year", "0")), reverse=True)

    result = OrderedDict()
    for cat_letter, cat_name in RCF_CATEGORIES.items():
        subcats = []
        for sub_code, sub_name in RCF_SUBCATEGORIES.items():
            if sub_code.startswith(cat_letter) and sub_code in by_subcode:
                subcats.append({
                    "code": sub_code,
                    "name": sub_name,
                    "publications": by_subcode[sub_code],
                })
        if subcats:
            result[cat_letter] = {
                "name": cat_name,
                "subcategories": subcats,
            }
    return result


def build_publications(rcf_year=None):
    """Build the publication list by rendering the Jinja2 LaTeX template with YAML data."""
    personal = load_yaml("personal.yaml")

    publications = load_rcf_entries()
    validate_entries(publications)
    grouped = group_publications(publications)

    if rcf_year is None:
        rcf_year = date.today().year

    surname = personal["name"].split(",")[0].strip()

    # Set up Jinja2 with LaTeX-friendly delimiters
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATE_PATH.parent),
        block_start_string="((*",
        block_end_string="*))",
        variable_start_string="(((",
        variable_end_string=")))",
        comment_start_string="((#",
        comment_end_string="#))",
        autoescape=False,
    )

    env.filters["latex_escape"] = latex_escape

    template = env.get_template("publications_template.tex")

    # Escape all string values in the data
    def escape_data(obj):
        if isinstance(obj, str):
            return latex_escape(obj)
        elif isinstance(obj, list):
            return [escape_data(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: escape_data(v) for k, v in obj.items()}
        return obj

    escaped_personal = escape_data(personal)
    escaped_grouped = escape_data(grouped)

    output = template.render(
        personal=escaped_personal,
        grouped=escaped_grouped,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_filename = f"publications_RCF{rcf_year}_{surname}"
    output_file = OUTPUT_DIR / f"{output_filename}.tex"
    output_file.write_text(output)
    print(f"Publication list generated: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build RCF publication list PDF.")
    parser.add_argument(
        "--year",
        type=int,
        default=None,
        help="RCF application year (defaults to current year)",
    )
    args = parser.parse_args()
    build_publications(rcf_year=args.year)
