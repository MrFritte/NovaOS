#!/usr/bin/env python3
"""Fix archiso profile mirror and avoid staging a duplicate /usr/lib/os-release."""
from pathlib import Path
import re
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: fix-profile-mirror.py /path/to/profile/pacman.conf")

conf = Path(sys.argv[1])
if not conf.is_file():
    raise SystemExit(f"archiso profile pacman.conf not found: {conf}")

lines = conf.read_text(encoding="utf-8").splitlines()
mirror = "Server = https://frankfurt.mirror.pkgbuild.com/$repo/os/$arch"

def bounds(name):
    matches = [i for i, line in enumerate(lines) if line.strip() == f"[{name}]"]
    if not matches:
        return None
    start = matches[0]
    end = next(
        (i for i in range(start + 1, len(lines))
         if re.match(r"^\s*\[[^]]+\]\s*$", lines[i])),
        len(lines),
    )
    return start, end

# mkarchiso copies profile/airootfs before installing the package list.
# The overlay's /usr/lib/os-release collides with the same path supplied by
# Arch's filesystem package. Keep the distro-specific /etc/os-release file
# and let the filesystem package provide its normal /usr/lib/os-release link.
airootfs = conf.parent / "airootfs"
etc_release = airootfs / "etc/os-release"
usr_release = airootfs / "usr/lib/os-release"

if not etc_release.is_file():
    raise SystemExit(f"NovaOS /etc/os-release is missing from profile overlay: {etc_release}")

if usr_release.exists() or usr_release.is_symlink():
    usr_release.unlink()
    print(f"Removed duplicate staged file: {usr_release}")
else:
    print(f"No duplicate staged file found: {usr_release}")

# Ensure a writable archiso profile points at the synchronized Frankfurt mirror.
multilib = bounds("multilib")
if multilib is None:
    raise SystemExit("archiso profile pacman.conf has no active [multilib] repository")
start, end = multilib
section = [
    line for line in lines[start + 1:end]
    if not (line.strip().startswith("Server") and "frankfurt.mirror.pkgbuild.com" in line)
]
lines[start + 1:end] = [mirror] + section

# Do not use NoExtract for os-release: after removing the staged duplicate,
# pacman should install the filesystem package's standard symlink normally.
options = bounds("options")
if options is None:
    raise SystemExit("archiso profile pacman.conf has no [options] section")
start, end = options
section = [
    line for line in lines[start + 1:end]
    if not (line.strip().startswith("NoExtract") and "usr/lib/os-release" in line)
]
lines[start + 1:end] = section

conf.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Configured Frankfurt mirror and clean os-release handling in {conf}")
