import shutil
import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def project_root():
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def site_dir(project_root):
    site = project_root / "site"
    if site.exists():
        shutil.rmtree(site)
    result = subprocess.run(
        ["uv", "run", "properdocs", "build"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.fail(
            f"properdocs build failed (rc={result.returncode})\n"
            f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}"
        )
    return site
