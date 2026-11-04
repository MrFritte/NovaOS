#!/usr/bin/env python3
"""Second NovaOS RC3 hotfix: runtime pacman conf guard and GTK2 package selection."""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()

def patch(path, old, new, label):
    s = path.read_text(encoding="utf-8")
    n = s.count(old)
    if n != 1:
        raise SystemExit(label + ": expected exactly one match, found " + str(n))
    path.write_text(s.replace(old, new, 1), encoding="utf-8")

# The official pacman.conf contains commented file:// examples. Only active
# server directives are build artifacts; comments must not trigger the guard.
p = root / "scripts/make-runtime-pacman-conf.py"
patch(
    p,
    "if 'file://' in result or '[novaos-local]' in result:\n    raise SystemExit('build-only local repository leaked into runtime pacman.conf')",
    """active_lines = [
    line.strip() for line in out
    if line.strip() and not line.lstrip().startswith('#')
]
has_local_section = any(line == '[novaos-local]' for line in active_lines)
has_file_server = any(
    line.lower().startswith('server') and 'file://' in line.lower()
    for line in active_lines
)
if has_local_section or has_file_server:
    raise SystemExit('build-only local repository leaked into runtime pacman.conf')""",
    "runtime pacman.conf guard",
)

# makepkg creates gtk2 and gtk2-debug. Select only the real runtime archive;
# the broad gtk2-*.pkg glob incorrectly chose the debug split package.
p = root / "scripts/build-extra-packages.sh"
patch(
    p,
    """GTK2_PKG="$(find "$GTK2_DIR" -maxdepth 1 -type f -name 'gtk2-*.pkg.tar.zst' -print -quit)"
[[ -s "$GTK2_PKG" ]] || { echo 'gtk2 AUR package was not created.' >&2; exit 1; }""",
    """GTK2_PKG="$(find "$GTK2_DIR" -maxdepth 1 -type f -name 'gtk2-[0-9]*.pkg.tar.zst' -print -quit)"
[[ -s "$GTK2_PKG" ]] || { echo 'gtk2 runtime package was not created (only gtk2-debug may have been built).' >&2; exit 1; }""",
    "GTK2 runtime package selection",
)
print("Applied runtime pacman.conf and GTK2 runtime-package fixes.")
