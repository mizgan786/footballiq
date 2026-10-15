"""
defaults.py

Small static lookups used to fill in optional prediction inputs that the
frontend form doesn't collect. Precomputed once from the training data
(see the one-off command in the project notes) - not recomputed at runtime.
"""

import json
import os

_HEIGHT_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "models", "height_defaults_by_subposition.json")
with open(_HEIGHT_PATH) as f:
    HEIGHT_DEFAULTS_BY_SUBPOSITION = json.load(f)


def default_height(sub_position: str) -> float:
    return HEIGHT_DEFAULTS_BY_SUBPOSITION.get(sub_position, 180.0)
