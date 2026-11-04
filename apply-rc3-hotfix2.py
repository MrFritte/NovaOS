#!/usr/bin/env python3
"""Second NovaOS RC3 hotfix: runtime pacman conf parser and GTK2 package selection."""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()

# The official pacman.conf contains commented file:// examples. Only active
# server directives are build artifacts; comments must not trigger the guard.
p = root / "scripts/make-runtime-pacman-conf.py"
s = p.read_text(encoding="utf-8")
old = "if 'file://' in result or '[novaos-local]' in result:\n    raise SystemExit('build-only local repository leaked into runtime pacman.conf')"
new = """active_lines = [
    line.strip() for line in out
    if line.strip() and not line.lstrip().startswith('#')
]
has_local_section = any(line == '[novaos-local]' for line in active_lines)
has_file_server = any(
    line.lower().startswith('server') and 'file://' in line.lower()
    for line in active_lines
)
if has_local_section or has_file_server:
    raise SystemExit('build-only local repository leaked into runtime pacman.conf')"""
if s.count(old) != 1:
    raise SystemExit("runtime pacman-conf guard pattern not found exactly once")
p.write_text(s.replace(old, new, 1), encoding="utf-8")

# makepkg creates both gtk2 and gtk2-debug. Never select the debug split
# package as the runtime dependency delivered to the ISO and target install.
p = root / "scripts/build-extra-packages.sh"
s = p.read_text(encoding="utf-8")
old = """GTK2_PKG="$(find "$GTK2_DIR" -maxdepth 1 -type f -name 'gtk2-*.pkg.tar.zst' -print -quit)"
[[ -s "$GTK2_PKG" ]] || { echo 'gtk2 AUR package was not created.' >&2; exit 1; }
pacman -U --noconfirm "$GTK2_PKG"
cp -f "$GTK2_PKG" "$REPO/""" + '"' # closing quote retained in exact shell line
new = """GTK2_PKG="$(find "$GTK2_DIR" -maxdepth 1 -type f -name 'gtk2-[0-9]*.pkg.tar.zst' -print -quit)"
[[ -s "$GTK2_PKG" ]] || { echo 'gtk2 runtime package was not created (only gtk2-debug may have been built).' >&2; exit 1; }
pacman -U --noconfirm "$GTK2_PKG"
cp -f "$GTK2_PKG" "$REPO/""" + '"'
if s.count(old) != 1:
    raise SystemExit("GTK2 package selection block not found exactly once")
p.write_text(s.replace(old, new, 1), encoding="utf-8")

print("Applied runtime pacman.conf and GTK2 runtime-package fixes.")
