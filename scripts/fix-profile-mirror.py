#!/usr/bin/env python3
"""Configure the archiso profile mirror and preserve NovaOS os-release safely."""
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

def section_bounds(name):
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

# Add NoExtract in [options] so pacman keeps the NovaOS file already staged
# in airootfs instead of reporting a conflict with filesystem's own os-release.
bounds = section_bounds("options")
if bounds is None:
    raise SystemExit("archiso profile pacman.conf has no [options] section")
start, end = bounds
options = lines[start + 1:end]
options = [
    line for line in options
    if not (line.strip().startswith("NoExtract") and "usr/lib/os-release" in line)
]
options.append("NoExtract = usr/lib/os-release")
lines[start + 1:end] = options

# Use the same current mirror directly for the multilib repository in this
# profile, because mkarchiso uses this file rather than the container default.
bounds = section_bounds("multilib")
if bounds is None:
    raise SystemExit("archiso profile pacman.conf has no active [multilib] repository")
start, end = bounds
section = lines[start + 1:end]
section = [
    line for line in section
    if not (line.strip().startswith("Server") and "frankfurt.mirror.pkgbuild.com" in line)
]
lines[start + 1:end] = [mirror] + section

conf.write_text("\n".join(lines) + "\n", encoding="utf-8")

os_release = conf.parent / "airootfs/usr/lib/os-release"
if os_release.exists():
    print(f"Preserving NovaOS os-release via pacman NoExtract: {os_release}")
else:
    print(f"Warning: no staged usr/lib/os-release found at {os_release}")

print(f"Configured Frankfurt mirror and NoExtract in {conf}")
