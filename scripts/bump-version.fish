#!/usr/bin/env fish
#
# bump-version.fish — compute today's CalVer and update version sources.
#
# Two forms are kept in sync:
#   * V_DISPLAY (user-facing / git tag / image tag):  2026.4.18, 2026.4.18-1, ...
#   * V_PEP440  (pyproject.toml / uv / pip):          2026.4.18, 2026.4.18.1, ...
#
# The script:
#   1. Computes the CalVer date prefix for today (Y.M.D, no zero padding)
#   2. Finds existing `v<prefix>` and `v<prefix>-N` git tags, picks next N
#   3. Writes both forms to app/_version.py and the PEP 440 form to pyproject.toml
#   4. Prints the values so the caller can `git tag v$V_DISPLAY` etc.
#
# Use: scripts/bump-version.fish [--dry-run]
#
# Must be run from inside the repo.

set -l repo_root (git rev-parse --show-toplevel 2>/dev/null)
if test -z "$repo_root"
    echo "error: not inside a git working tree" >&2
    exit 1
end
cd $repo_root

set -l dry_run 0
if contains -- --dry-run $argv
    set dry_run 1
end

# Today's date prefix — no zero padding on month/day.
set -l y (date +%Y)
set -l m (date +%-m)
set -l d (date +%-d)
set -l prefix "$y.$m.$d"

# Find existing same-day tags (git returns non-zero when no match; suppress).
set -l existing_tags (git tag -l "v$prefix" "v$prefix-*" 2>/dev/null)
set -l suffix ""
if test -n "$existing_tags"
    set -l max_n -1
    for t in $existing_tags
        if test "$t" = "v$prefix"
            if test $max_n -lt 0
                set max_n 0
            end
        else
            set -l n (string replace -r "^v$prefix-" "" -- $t)
            if string match -qr '^[0-9]+$' $n
                if test $n -gt $max_n
                    set max_n $n
                end
            end
        end
    end
    set -l next_n (math $max_n + 1)
    set suffix "-$next_n"
end

set -l v_display "$prefix$suffix"
set -l v_pep440 "$prefix"
if test -n "$suffix"
    set v_pep440 "$prefix"(string replace -- '-' '.' $suffix)
end

echo "Next release:"
echo "  VERSION (display) = $v_display"
echo "  VERSION_PEP440    = $v_pep440"
echo "  git tag           = v$v_display"

if test $dry_run -eq 1
    echo "(--dry-run: no files modified)"
    exit 0
end

# Update app/_version.py
printf '"""Single source of truth for the application version.

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

VERSION = "%s"
VERSION_PEP440 = "%s"
' $v_display $v_pep440 > app/_version.py

# Update pyproject.toml (PEP 440 form) via an inline python rewrite so we
# don't depend on sed's BSD/GNU behavior across macOS and Linux.
env V_PEP="$v_pep440" python3 -c "
import os, pathlib, re, sys
p = pathlib.Path('pyproject.toml')
txt = p.read_text()
new_version = os.environ['V_PEP']
new, n = re.subn(r'^version = \"[^\"]+\"', f'version = \"{new_version}\"', txt, count=1, flags=re.M)
if n == 0:
    sys.exit('error: could not find project.version in pyproject.toml')
if new != txt:
    p.write_text(new)
"
or exit 1

if type -q uv
    uv lock --quiet
end

echo ""
echo "Updated:"
echo "  app/_version.py"
echo "  pyproject.toml"
echo "  uv.lock (via uv lock)"
echo ""
echo "Next steps:"
echo "  git add app/_version.py pyproject.toml uv.lock"
echo "  git commit -m 'chore(release): bump to $v_display'"
echo "  git tag -a v$v_display -m 'Release $v_display'"
echo "  git push && git push origin v$v_display"
