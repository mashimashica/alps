"""Hash and export this assessment's ordinary evidence for direct Git API saves.

This helper does not call an external API or decide whether a trial succeeded.
It is assessment-only, not part of ALPS distribution.
"""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def files():
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if any(part in {".git", ".local", "__pycache__"} for part in relative.parts):
            continue
        if path.is_file() or path.is_symlink():
            yield path, relative


def frozen_files():
    for path, relative in files():
        if relative.parts[0] != "frozen":
            continue
        if relative.parts[:3] == ("frozen", "skill-creator", "assets"):
            continue
        yield path, relative


def content(path):
    return str(path.readlink()).encode() if path.is_symlink() else path.read_bytes()


def freeze():
    manifest = ROOT / "frozen-hashes.sha256"
    if manifest.exists():
        raise SystemExit("frozen-hashes.sha256 already exists; use verify")
    manifest.write_text("".join(f"{hashlib.sha256(content(p)).hexdigest()}  {r.as_posix()}\n" for p, r in frozen_files()), encoding="utf-8")
    print(f"Recorded {len(manifest.read_text().splitlines())} frozen input hashes")


def verify():
    manifest = ROOT / "frozen-hashes.sha256"
    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        actual = hashlib.sha256(content(ROOT / relative)).hexdigest()
        if actual != expected:
            raise SystemExit(f"Frozen input changed: {relative}")


def export(offset=0, limit=None):
    verify()
    entries = []
    for path, relative in files():
        if relative.parts[:2] == ("frozen", "alps"):
            continue
        if relative.parts[:3] == ("frozen", "skill-creator", "assets"):
            continue
        try:
            value = content(path).decode("utf-8")
        except UnicodeDecodeError:
            raise SystemExit(f"Non-text evidence needs an explicit direct storage route: {relative}")
        entries.append({"path": "assessment/v070/" + relative.as_posix(), "mode": "120000" if path.is_symlink() else "100644", "type": "blob", "content": value})
    selected = entries[offset:] if limit is None else entries[offset:offset+limit]
    print(json.dumps(selected, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("freeze", "verify", "export"))
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    operation = args.operation
    if operation == "freeze":
        freeze()
    elif operation == "verify":
        verify()
        print("Frozen input hashes verified")
    else:
        export(args.offset, args.limit)
