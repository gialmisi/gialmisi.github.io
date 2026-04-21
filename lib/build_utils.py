"""Shared utilities for building LaTeX documents from YAML data."""

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


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
    r"""Escape LaTeX special characters but preserve \href{}{} commands."""
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
