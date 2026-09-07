"""Preserve the reviewed public creator inputs before the main comparison."""

import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
target = ROOT / "frozen/main-cases"
if target.exists():
    raise SystemExit("Public main cases already frozen; preserve that snapshot")
sources = {f"S{i:02}": ROOT / ("cases" if i in (1, 5, 10) else "main-cases") / f"S{i:02}"
           for i in range(1, 13)}
for name, source in sources.items():
    if not (source / "brief.md").is_file():
        raise SystemExit(f"Missing reviewed public input: {name}")
target.mkdir(parents=True)
hashes = {}
for name, source in sources.items():
    shutil.copytree(source, target / name, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
for path in sorted(target.rglob("*")):
    if path.is_file():
        hashes[path.relative_to(target).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
(ROOT / "main-case-hashes.json").write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
print(f"Frozen twelve reviewed public case families, {len(hashes)} files; no consumer cases included")
