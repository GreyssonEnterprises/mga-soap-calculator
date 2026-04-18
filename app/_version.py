"""Single source of truth for the application version.

Two forms are kept in sync by `scripts/bump-version.fish`:

* `VERSION` — the user-facing / git-tag / image-tag form. Uses a dash for
  same-day re-releases: ``2026.4.18``, ``2026.4.18-1``, ``2026.4.18-2``.
* `VERSION_PEP440` — the Python packaging form. Dashes are not valid PEP 440
  separators, so sub-releases collapse to a fourth numeric segment:
  ``2026.4.18``, ``2026.4.18.1``, ``2026.4.18.2``. This is what
  ``pyproject.toml`` carries.

Both forms always share the same date prefix. Do not edit by hand; run
``scripts/bump-version.fish`` instead.
"""

VERSION = "2026.4.18"
VERSION_PEP440 = "2026.4.18"
