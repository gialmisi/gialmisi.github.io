"""Build CV from YAML data files using the RCF LaTeX template."""

import re
import sys
from pathlib import Path

# Ensure project root is on the path for lib imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import jinja2

from lib.build_utils import DATA_DIR, latex_escape, latex_escape_keep_urls, load_yaml

TEMPLATE_PATH = Path(__file__).resolve().parent / "cv_template.tex"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"


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
    data["leadership"] = filter_for_cv(research.get("leadership", []))
    data["open_science"] = filter_for_cv(research.get("open_science", []))
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
    data["conferences_organized"] = filter_for_cv(activities.get("conferences_organized", []))
    data["editorial_roles"] = filter_for_cv(activities.get("editorial_roles", []))
    data["peer_reviews"] = filter_for_cv(activities.get("peer_reviews", []))

    teaching = load_yaml("teaching.yaml")
    data["teachings"] = filter_for_cv(teaching.get("teachings", []))

    publications = load_yaml("publications.yaml")
    data["publications"] = filter_for_cv(publications.get("publications", []))
    data["publications_total"] = len(data["publications"])
    data["publications_oa_total"] = sum(
        1 for p in data["publications"] if p.get("open_access")
    )

    disseminations = load_yaml("disseminations.yaml")
    data["invitations"] = filter_for_cv(disseminations.get("invitations", []))
    data["conferences"] = filter_for_cv(disseminations.get("conferences", []))
    data["tutorials"] = filter_for_cv(disseminations.get("tutorials", []))
    data["media"] = filter_for_cv(disseminations.get("media", []))

    supervision = load_yaml("supervision.yaml")
    data["supervisions"] = filter_for_cv(supervision.get("supervisions", []))
    doctoral = [s for s in data["supervisions"] if "doctoral" in s.get("type", "").lower()]
    masters = [s for s in data["supervisions"] if "master" in s.get("type", "").lower()]
    data["doctoral_ongoing_count"] = sum(
        1 for s in doctoral if "ongoing" in str(s.get("period", "")).lower()
    )
    data["doctoral_completed_count"] = len(doctoral) - data["doctoral_ongoing_count"]
    data["masters_completed_count"] = sum(
        1 for s in masters if "ongoing" not in str(s.get("period", "")).lower()
    )

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

    # Keys whose values are URLs and must remain valid inside \href{}.
    # Inside \href{URL}{...}, only %, #, and \ need escaping; underscores etc. must stay raw.
    URL_KEYS = {"doi", "open_access", "uri", "url", "slides", "poster", "recording", "link"}

    def escape_url(url: str) -> str:
        return url.replace("\\", r"\\").replace("%", r"\%").replace("#", r"\#")

    # Escape all string values in the data
    def escape_data(obj, key=None):
        if isinstance(obj, str):
            if key in URL_KEYS:
                return escape_url(obj)
            return latex_escape(obj)
        elif isinstance(obj, list):
            return [escape_data(item, key=key) for item in obj]
        elif isinstance(obj, dict):
            return {k: escape_data(v, key=k) for k, v in obj.items()}
        return obj

    escaped_data = escape_data(data)

    output = template.render(**escaped_data)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / "cv.tex"
    output_file.write_text(output)
    print(f"CV generated: {output_file}")


if __name__ == "__main__":
    build_cv()
