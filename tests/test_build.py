import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_macros_module():
    spec = importlib.util.spec_from_file_location(
        "macros_main", PROJECT_ROOT / "macros" / "main.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["macros_main"] = module
    spec.loader.exec_module(module)
    return module


def _make_env():
    captured = {}

    def macro(func):
        captured[func.__name__] = func
        return func

    env = SimpleNamespace(project_dir=str(PROJECT_ROOT), macro=macro)
    module = _load_macros_module()
    module.define_env(env)
    return captured


def test_properdocs_build_succeeds(project_root):
    site = project_root / "site"
    if site.exists():
        shutil.rmtree(site)
    result = subprocess.run(
        ["uv", "run", "properdocs", "build"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"properdocs build failed\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


@pytest.mark.parametrize(
    "page",
    [
        "index.html",
        "publications/index.html",
        "research/index.html",
        "activities/index.html",
        "education/index.html",
        "dissemination/index.html",
    ],
)
def test_site_has_all_pages(site_dir, page):
    assert (site_dir / page).exists(), f"missing rendered page: {page}"


def test_publications_rendered_correctly(site_dir):
    html = (site_dir / "publications" / "index.html").read_text()
    assert "load_data_for" not in html, (
        "raw Jinja2 macro call found in rendered HTML — macros plugin is not running"
    )
    assert "Misitano" in html, "expected author name 'Misitano' not present in publications page"


def test_research_rendered_correctly(site_dir):
    html = (site_dir / "research" / "index.html").read_text()
    assert "DESIDES" in html, "expected research project 'DESIDES' not present in research page"


def test_index_has_icons(site_dir):
    html = (site_dir / "index.html").read_text()
    assert "svg" in html, "expected SVG (emoji/icons) in rendered index"


def test_slides_present_in_output(site_dir):
    slides_dir = site_dir / "data" / "slides"
    assert slides_dir.is_dir(), f"missing slides directory: {slides_dir}"
    pdfs = list(slides_dir.glob("*.pdf"))
    assert pdfs, "expected at least one .pdf in site/data/slides/"


def test_assets_present_in_output(site_dir):
    assert (site_dir / "assets" / "giovanni.jpg").exists()


def test_load_data_returns_valid_data():
    macros = _make_env()
    data = macros["load_data"]("personal.yaml")
    assert isinstance(data, dict)
    assert "name" in data


def test_load_data_for_filters_correctly():
    macros = _make_env()
    data = macros["load_data_for"]("publications.yaml", "website")
    assert "publications" in data
    for entry in data["publications"]:
        assert "include" in entry
        assert "website" in entry["include"]
