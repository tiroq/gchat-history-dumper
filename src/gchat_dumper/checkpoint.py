import json
import os
from typing import Dict


def load_checkpoint(path: str) -> Dict[str, str]:
    """Load checkpoint (per-space last seen timestamp) from JSON file.

    Returns {} if file does not exist or is invalid.
    """
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_checkpoint(path: str, data: Dict[str, str]) -> None:
    """Save checkpoint atomically."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
    os.replace(tmp, path)
