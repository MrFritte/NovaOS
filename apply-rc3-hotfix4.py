#!/usr/bin/env python3
"""Insert profile-mirror, os-release and package-resolution fixes before mkarchiso."""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
build = root / "scripts/build-iso.sh"
helper = root / "scripts/fix-profile-mirror.py"

if not build.is_file():
    raise SystemExit(f"missing build script: {build}")
if not helper.is_file():
    raise SystemExit(f"missing mirror helper: {helper}")

text = build.read_text(encoding="utf-8")
marker = "# NOVAOS_PROFILE_MIRROR_FIX"
if marker in text:
    raise SystemExit("profile mirror fix marker already present; refusing a duplicate insertion")

lines = text.splitlines()
candidates = [
    i for i, line in enumerate(lines)
    if "mkarchiso" in line
    and not line.lstrip().startswith("#")
    and "command -v" not in line
]
if not candidates:
    raise SystemExit("could not locate mkarchiso invocation in scripts/build-iso.sh")

idx = candidates[-1]
insertion = [
    marker,
    'PROFILE_PACMAN_CONF="/workspace/build/profile/pacman.conf"',
    'python3 "/workspace/scripts/fix-profile-mirror.py" "$PROFILE_PACMAN_CONF"',
    'echo "Checking live-image Multilib package resolution..."',
    'pacman --config "$PROFILE_PACMAN_CONF" -Syy --noconfirm',
    'pacman --config "$PROFILE_PACMAN_CONF" -Sp --print-format "%r/%n" lib32-alsa-lib',
]
lines[idx:idx] = insertion
build.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("Inserted profile mirror sync and lib32-alsa-lib preflight before mkarchiso.")
