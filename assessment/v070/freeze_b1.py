"""Copy the baseline and the two reviewed H01 files into an immutable trial input."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parent / "alps-assessment-improvements"
CHANGED = ("skills/design-agent-work-system/SKILL.md",
           "skills/design-agent-work-system/references/locales/ja/SKILL.md")


def main():
    changes = subprocess.check_output(["git", "diff", "--name-only"], cwd=WORKTREE, text=True).splitlines()
    untracked = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], cwd=WORKTREE, text=True).splitlines()
    if set(changes) != set(CHANGED) or untracked:
        raise SystemExit("Unexpected candidate diff: inspect before freezing")
    destination = ROOT / "frozen/candidate-B1"
    shutil.copytree(ROOT / "frozen/alps", destination, symlinks=True)
    for relative in CHANGED:
        shutil.copy2(WORKTREE / relative, destination / relative)
    hashes = {}
    for path in sorted(destination.rglob("*")):
        if path.is_symlink():
            data, mode = str(path.readlink()).encode(), "120000"
        elif path.is_file():
            data = path.read_bytes()
            mode = "100755" if path.stat().st_mode & 0o111 else "100644"
        else:
            continue
        hashes[path.relative_to(destination).as_posix()] = {
            "sha256": hashlib.sha256(data).hexdigest(), "mode": mode}
    (ROOT / "candidate-B1-hashes.json").write_text(json.dumps(hashes, indent=2) + "\n")
    patch = subprocess.check_output(["git", "diff", "--", *CHANGED], cwd=WORKTREE, text=True)
    (ROOT / "candidate-B1.patch").write_text(patch, encoding="utf-8")
    print(f"Frozen B1: {len(hashes)} files/links, exactly two source-file edits")


if __name__ == "__main__":
    main()
