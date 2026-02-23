"""Build CV from YAML data files using the RCF LaTeX template."""

import re
from pathlib import Path

import jinja2
import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
TEMPLATE_PATH = Path(__file__).resolve().parent / "cv_template.tex"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def latex_escape(text: str) -> str:
    """Escape LaTeX special characters in text."""
    if not isinstance(text, str):
        return text
    # Order matters: ampersand first so we don't double-escape
    replacements = [
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def latex_escape_keep_urls(text: str) -> str:
    """Escape LaTeX special characters but preserve \\href{}{} commands."""
    if not isinstance(text, str):
        return text
    # Find href patterns and protect them
    href_pattern = re.compile(r"\\href\{[^}]*\}\{[^}]*\}")
    parts = href_pattern.split(text)
    hrefs = href_pattern.findall(text)

    escaped_parts = [latex_escape(p) for p in parts]

    result = escaped_parts[0]
    for i, href in enumerate(hrefs):
        result += href + escaped_parts[i + 1]
    return result


def load_yaml(filename: str) -> dict:
    """Load a YAML file from the data directory."""
    filepath = DATA_DIR / filename
    with open(filepath) as f:
        return yaml.safe_load(f)


def filter_for_cv(items):
    """Filter a list of items, keeping only those with 'cv' in their include field."""
    return [item for item in items if "cv" in item.get("include", ["website", "cv"])]


def load_all_data() -> dict:
    """Load all YAML data files and flatten into a single context dict."""
    data = {}

    personal = load_yaml("personal.yaml")
    data["personal"] = personal
    data["languages"] = personal.get("languages", [])

    education = load_yaml("education.yaml")
    data["educations"] = filter_for_cv(education.get("educations", []))

    research = load_yaml("research.yaml")
    positions = filter_for_cv(research.get("positions", []))
    visits = filter_for_cv(research.get("visits", []))
    # Normalize visits to look like positions so they can be merged
    for visit in visits:
        visit["position"] = "Research visit"
        visit["organization"] = f"{visit['institution']}, {visit['location']}"
    # Merge and sort by most recent first
    def _sort_key(item):
        period = str(item.get("period", ""))
        if "ongoing" in period.lower():
            return -9999
        years = re.findall(r"\d{4}", period)
        return -int(max(years)) if years else 0
    data["positions"] = sorted(positions + visits, key=_sort_key)
    data["projects"] = filter_for_cv(research.get("projects", []))
    data["outputs"] = filter_for_cv(research.get("outputs", []))

    activities = load_yaml("activities.yaml")
    data["activity_positions"] = filter_for_cv(activities.get("positions", []))
    data["rewards"] = filter_for_cv(activities.get("rewards", []))
    data["fundings"] = filter_for_cv(activities.get("fundings", []))

    teaching = load_yaml("teaching.yaml")
    data["teachings"] = filter_for_cv(teaching.get("teachings", []))

    publications = load_yaml("publications.yaml")
    data["publications"] = filter_for_cv(publications.get("publications", []))

    disseminations = load_yaml("disseminations.yaml")
    data["invitations"] = filter_for_cv(disseminations.get("invitations", []))
    data["conferences"] = filter_for_cv(disseminations.get("conferences", []))
    data["tutorials"] = filter_for_cv(disseminations.get("tutorials", []))

    supervision = load_yaml("supervision.yaml")
    data["supervisions"] = filter_for_cv(supervision.get("supervisions", []))

    manuscripts = load_yaml("manuscripts.yaml")
    data["manuscripts"] = filter_for_cv(manuscripts.get("manuscripts", []))

    other_education = load_yaml("other_education.yaml")
    data["other_education"] = filter_for_cv(other_education.get("other_education", []))

    career_breaks = load_yaml("career_breaks.yaml")
    data["career_breaks"] = filter_for_cv(career_breaks.get("career_breaks", []))

    other_merits = load_yaml("other_merits.yaml")
    data["other_merits"] = filter_for_cv(other_merits.get("other_merits", []))

    return data


def build_cv():
    """Build the CV by rendering the Jinja2 LaTeX template with YAML data."""
    data = load_all_data()

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

    env.filters["trim"] = lambda s: s.strip() if isinstance(s, str) else s
    env.filters["latex_escape"] = latex_escape

    template = env.get_template("cv_template.tex")

    # Escape all string values in the data
    def escape_data(obj):
        if isinstance(obj, str):
            return latex_escape(obj)
        elif isinstance(obj, list):
            return [escape_data(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: escape_data(v) for k, v in obj.items()}
        return obj

    escaped_data = escape_data(data)

    output = template.render(**escaped_data)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "cv.tex"
    output_file.write_text(output)
    print(f"CV generated: {output_file}")


if __name__ == "__main__":
    build_cv()
