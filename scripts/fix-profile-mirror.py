#!/usr/bin/env python3
"""Make the archiso profile use the verified Frankfurt mirror for Multilib."""
from pathlib import Path
import re
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: fix-profile-mirror.py /path/to/profile/pacman.conf")

conf = Path(sys.argv[1])
if not conf.is_file():
    raise SystemExit(f"archiso profile pacman.conf not found: {conf}")

text = conf.read_text(encoding="utf-8")
mirror = "Server = https://frankfurt.mirror.pkgbuild.com/$repo/os/$arch"
lines = text.splitlines()

# Ensure an active Multilib repository exists and put the verified mirror first.
matches = [i for i, line in enumerate(lines) if line.strip() == "[multilib]"]
if not matches:
    raise SystemExit("archiso profile pacman.conf has no active [multilib] repository")

start = matches[0]
end = next((i for i in range(start + 1, len(lines)) if re.match(r"^\s*\[[^]]+\]\s*$", lines[i])), len(lines))
section = lines[start + 1:end]
section = [line for line in section if not (
    line.strip().startswith("Server") and "frankfurt.mirror.pkgbuild.com" in line
)]
lines[start + 1:end] = [mirror] + section
conf.write_text("\n".join(lines) + "\n", encoding="utf-8")

print(f"Configured Frankfurt Tier-1 mirror in [multilib] of {conf}")
