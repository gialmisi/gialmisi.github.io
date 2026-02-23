import yaml
from pathlib import Path


def _filter_data(obj, target):
    """Recursively filter data: keep list items whose 'include' contains target."""
    if isinstance(obj, list):
        filtered = []
        for item in obj:
            if isinstance(item, dict) and "include" in item:
                if target in item["include"]:
                    filtered.append(_filter_data(item, target))
            else:
                filtered.append(_filter_data(item, target))
        return filtered
    elif isinstance(obj, dict):
        return {k: _filter_data(v, target) for k, v in obj.items()}
    return obj


def define_env(env):
    @env.macro
    def load_data(filename):
        data_path = Path(env.project_dir) / "data" / filename
        with open(data_path, "r") as f:
            return yaml.safe_load(f)

    @env.macro
    def load_data_for(filename, target="website"):
        data_path = Path(env.project_dir) / "data" / filename
        with open(data_path, "r") as f:
            raw = yaml.safe_load(f)
        return _filter_data(raw, target)
