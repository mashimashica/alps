"""Freeze an explicitly reviewed candidate diff for separate creator trials."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parent / "alps-assessment-improvements"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("identity")
    parser.add_argument("changed_paths", nargs="+")
    args = parser.parse_args()
    if not re.fullmatch(r"B[2-3][a-z]?", args.identity):
        raise SystemExit("Use an explicit bounded-development candidate identity")
    actual = subprocess.check_output(["git", "diff", "--name-only"], cwd=WORKTREE, text=True).splitlines()
    untracked = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], cwd=WORKTREE, text=True).splitlines()
    if set(actual) != set(args.changed_paths) or untracked:
        raise SystemExit("Unexpected candidate diff: inspect it before freezing")
    for relative in args.changed_paths:
        if not (WORKTREE / relative).is_file() or not (ROOT / "frozen/alps" / relative).is_file():
            raise SystemExit("This reviewed replacement freeze expects existing source files")
    target = ROOT / "frozen" / ("candidate-" + args.identity)
    shutil.copytree(ROOT / "frozen/alps", target, symlinks=True)
    for relative in args.changed_paths:
        shutil.copy2(WORKTREE / relative, target / relative)
    hashes = {}
    for path in sorted(target.rglob("*")):
        if path.is_symlink():
            data, mode = str(path.readlink()).encode(), "120000"
        elif path.is_file():
            data = path.read_bytes()
            mode = "100755" if path.stat().st_mode & 0o111 else "100644"
        else:
            continue
        hashes[path.relative_to(target).as_posix()] = {"sha256": hashlib.sha256(data).hexdigest(), "mode": mode}
    (ROOT / f"candidate-{args.identity}-hashes.json").write_text(json.dumps(hashes, indent=2) + "\n")
    patch = subprocess.check_output(["git", "diff", "--", *args.changed_paths], cwd=WORKTREE, text=True)
    (ROOT / f"candidate-{args.identity}.patch").write_text(patch, encoding="utf-8")
    print(f"Frozen {args.identity}: {len(hashes)} files/links; {len(actual)} reviewed source edits")


if __name__ == "__main__":
    main()
