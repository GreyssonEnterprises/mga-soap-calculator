"""
YAML-backed seed data loader (CI-07).

Single source of truth for the oil and additive seed catalogs is
``app/data/seed-data.yaml``. This module exposes the parsed Python
representation as ``OIL_SEED_DATA`` and ``ADDITIVE_SEED_DATA`` so existing
importers (``scripts/seed_data.py``, unit tests) keep working unchanged.

Shale and Jackie maintain the YAML file directly when the ingredient catalog
changes. Putting the data in a single YAML file (rather than one file per
oil) keeps edits, diffs, and pull-request review simple for non-technical
owners.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

SEED_FILE_PATH: Path = Path(__file__).resolve().parent / "seed-data.yaml"


def load_seed_data(path: Path | None = None) -> dict[str, list[dict[str, Any]]]:
    """
    Load the seed catalog from YAML.

    Returns a dict with ``oils`` and ``additives`` keys, each mapping to a
    list of records ready to pass into the corresponding SQLAlchemy model
    constructor. A missing or empty top-level key is returned as an empty
    list so callers never hit ``KeyError``.
    """
    source = path if path is not None else SEED_FILE_PATH
    with source.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    if not isinstance(data, dict):
        raise ValueError(
            f"Seed file {source} must contain a top-level mapping (got {type(data).__name__})"
        )

    return {
        "oils": list(data.get("oils", []) or []),
        "additives": list(data.get("additives", []) or []),
    }


_DATA = load_seed_data()

OIL_SEED_DATA: list[dict[str, Any]] = _DATA["oils"]
ADDITIVE_SEED_DATA: list[dict[str, Any]] = _DATA["additives"]


__all__ = [
    "ADDITIVE_SEED_DATA",
    "OIL_SEED_DATA",
    "SEED_FILE_PATH",
    "load_seed_data",
]
