#!/usr/bin/env python3
"""Third NovaOS RC3 hotfix: drop an unavailable optional 32-bit MPEG codec."""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
target = "lib32-mpg123"
files = [
    root / "packages/novaos-live.x86_64",
    root / "packages/novaos-installed.txt",
]
removed = 0
for path in files:
    if not path.exists():
        raise SystemExit(f"required package manifest missing: {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    kept = [line for line in lines if line.strip() != target]
    removed += len(lines) - len(kept)
    if len(kept) != len(lines):
        path.write_text("\n".join(kept) + "\n", encoding="utf-8")

print(f"Removed unavailable optional {target} from {removed} package manifest entries.")
print("Wine, Winetricks and the other 32-bit runtime packages remain enabled.")
