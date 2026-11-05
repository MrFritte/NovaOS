#!/usr/bin/env python3
"""Third NovaOS RC3 hotfix: omit an optional multilib audio package unavailable on the build mirror."""
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
        continue
    lines = path.read_text(encoding="utf-8").splitlines()
    kept = [line for line in lines if line.strip() != target]
    removed += len(lines) - len(kept)
    if len(kept) != len(lines):
        path.write_text("\n".join(kept) + "\n", encoding="utf-8")

if removed == 0:
    raise SystemExit("optional multilib package not found in either NovaOS package manifest")

print(f"Removed optional {target} from {removed} NovaOS package manifest entry/entries.")
print("Wine remains enabled; the unavailable optional 32-bit MPEG audio codec is omitted.")
