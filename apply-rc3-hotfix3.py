#!/usr/bin/env python3
"""Third NovaOS RC3 hotfix: use the current package set and keep Wine's 32-bit audio codec."""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
target = "lib32-mpg123"
files = [
    root / "packages/novaos-live.x86_64",
    root / "packages/novaos-installed.txt",
]

restored = 0
for path in files:
    if not path.exists():
        raise SystemExit(f"required package manifest missing: {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    if target not in [line.strip() for line in lines]:
        lines.append(target)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        restored += 1

print(f"Ensured {target} is present in both live and installed package manifests (restored {restored}).")
