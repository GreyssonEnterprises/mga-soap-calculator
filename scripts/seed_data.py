"""
Backward-compatible re-export of the seed catalog (CI-07).

The canonical seed data now lives in ``app/data/seed-data.yaml`` and is
loaded by ``app.data.seed_loader``. This module re-exports the Python-level
lists so existing callers (unit tests, the seeding entrypoint) keep working
unchanged.

To change seed values, edit ``app/data/seed-data.yaml`` directly — not this
file.
"""

from app.data.seed_loader import ADDITIVE_SEED_DATA, OIL_SEED_DATA

__all__ = ["ADDITIVE_SEED_DATA", "OIL_SEED_DATA"]
